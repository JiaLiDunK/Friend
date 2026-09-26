import asyncio
import os
from pathlib import Path

import asyncpg

FILE_PATH = r"C:\jieya\6.9更新总库.txt"
ENV_PATH = Path(__file__).resolve().parents[2] / "src" / ".env"
DB_NAME = "socialworker"
TABLE_NAME = "qq"
COLUMNS = ["qq", "phone"]
BATCH_SIZE = 100000
PROGRESS_STEP = 1000000
SKIP_LINES = 19000000
MAX_RETRIES = 10
RETRY_DELAY = 10
DRY_RUN = False
ONLY_ABNORMAL = True
BAD_SAMPLE_LIMIT = 20
BAD_LINES_PATH = r"C:\jieya\bad_lines.txt"


def normalize_url(url: str) -> str:
    url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
    return url.rsplit("/", 1)[0] + "/" + DB_NAME


def load_database_url() -> str:
    database_url = os.getenv("DATABASE_PG_URL")
    if database_url:
        return normalize_url(database_url)

    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("DATABASE_PG_URL="):
                value = line.split("=", 1)[1].strip().strip("'").strip('"')
                return normalize_url(value)

    raise RuntimeError("未找到 DATABASE_PG_URL，请检查 src/.env")


async def insert_batch(
    conn: asyncpg.Connection, batch: list[tuple[int, int]], database_url: str
) -> asyncpg.Connection:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            await conn.copy_records_to_table(TABLE_NAME, records=batch, columns=COLUMNS)
            return conn
        except (asyncpg.PostgresConnectionError, asyncpg.InterfaceError, OSError) as e:
            if attempt == MAX_RETRIES:
                raise
            print(f"提示：连接中断（{e}），{RETRY_DELAY} 秒后第 {attempt} 次重连")
            await asyncio.sleep(RETRY_DELAY)
            try:
                await conn.close()
            except Exception:
                pass
            try:
                conn = await asyncpg.connect(database_url)
            except OSError as ce:
                print(f"提示：重连失败（{ce}），稍后再试")
    return conn


def parse_line(line: str) -> tuple[list[tuple[int, int]], str]:
    parts = [p.strip() for p in line.split("----")]
    parts = [p for p in parts if p]
    if len(parts) < 2:
        return [], f"字段数为{len(parts)}"
    phone = parts[-1]
    if not phone.isdigit():
        return [], "phone非数字"
    qqs = list(dict.fromkeys(parts[:-1]))
    if any(not q.isdigit() for q in qqs):
        return [], "qq非数字"
    return [(int(q), int(phone)) for q in qqs], ""


async def main() -> None:
    database_url = "" if DRY_RUN else load_database_url()
    conn: asyncpg.Connection | None = None if DRY_RUN else await asyncpg.connect(database_url)
    mode = "复查（不导入）" if DRY_RUN else f"导入 -> {TABLE_NAME}"
    if ONLY_ABNORMAL:
        mode += "（仅异常行）"
    label = "合法" if DRY_RUN else "已插入"
    print(f"提示：开始{mode} {FILE_PATH}，从第 {SKIP_LINES + 1} 行开始")

    total_count = 0
    insert_count = 0
    abnormal_count = 0
    bad_count = 0
    last_committed_line = SKIP_LINES
    batch: list[tuple[int, int]] = []
    bad_file = open(BAD_LINES_PATH, "w", encoding="utf-8")

    try:
        with open(FILE_PATH, "r", encoding="utf-8", errors="ignore") as f:
            for line_no, line in enumerate(f, start=1):
                if line_no <= SKIP_LINES:
                    continue

                total_count += 1
                raw = line.rstrip("\r\n")
                line = line.strip()

                records, reason = parse_line(line)
                if not records:
                    bad_count += 1
                    bad_file.write(f"{line_no}\t{reason}\t{raw!r}\n")
                    if bad_count <= BAD_SAMPLE_LIMIT:
                        print(f"无法解析#{bad_count} 第 {line_no} 行 [{reason}]：{raw!r}")
                    continue

                if line.count("----") == 1:
                    if ONLY_ABNORMAL:
                        continue
                else:
                    abnormal_count += 1

                batch.extend(records)

                if len(batch) >= BATCH_SIZE:
                    if not DRY_RUN:
                        conn = await insert_batch(conn, batch, database_url)
                    insert_count += len(batch)
                    last_committed_line = line_no
                    batch.clear()

                if line_no % PROGRESS_STEP == 0:
                    print(f"提示：已读取 {line_no} 行，{label} {insert_count} 条，异常行 {abnormal_count} 行，无法解析 {bad_count} 行")

        if batch:
            if not DRY_RUN:
                conn = await insert_batch(conn, batch, database_url)
            insert_count += len(batch)

    except Exception as e:
        print(f"提示：{mode}中断，{label} {insert_count} 条，可将 SKIP_LINES 设为 {last_committed_line} 后重跑。错误：{e}")
        raise
    finally:
        bad_file.close()
        if conn is not None and not conn.is_closed():
            await conn.close()

    print(f"提示：{mode}完成，总读取 {total_count} 行，{label} {insert_count} 条，异常行 {abnormal_count} 行，无法解析 {bad_count} 行")
    print(f"提示：无法解析的行已写入 {BAD_LINES_PATH}")


if __name__ == "__main__":
    print("开始")
    asyncio.run(main())
    print("结束")