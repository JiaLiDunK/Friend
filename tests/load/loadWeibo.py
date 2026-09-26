import asyncio
import os
from pathlib import Path

import asyncpg

FILE_PATH = r"D:\学习\来自：BT磁力链下载\裤子(1)\微博五亿2019.txt"
ENV_PATH = Path(__file__).resolve().parents[2] / "src" / ".env"

DB_NAME = "socialworker"
TABLE_NAME = "weibo"
COLUMNS = ["phone", "uid"]

BATCH_SIZE = 100000
PROGRESS_STEP = 1000000
SKIP_HEADER = True
SKIP_LINES = 171982540
MAX_RETRIES = 10
RETRY_DELAY = 10
DRY_RUN = True


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


def parse_line(line: str) -> tuple[tuple[int, int] | None, str]:
    parts = line.strip().split()

    if len(parts) != 2:
        return None, f"字段数为 {len(parts)}"

    phone, uid = parts

    if not phone.isdigit():
        return None, "phone 非数字"

    if not uid.isdigit():
        return None, "uid 非数字"

    return (int(phone), int(uid)), ""


async def insert_batch(
    conn: asyncpg.Connection,
    batch: list[tuple[int, int]],
    database_url: str,
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

            conn = await asyncpg.connect(database_url)

    return conn


async def main() -> None:
    database_url = "" if DRY_RUN else load_database_url()
    conn: asyncpg.Connection | None = None if DRY_RUN else await asyncpg.connect(database_url)

    total_count = 0
    insert_count = 0
    bad_count = 0
    batch: list[tuple[int, int]] = []

    print(f"提示：开始导入授权数据到 {TABLE_NAME}")
    if DRY_RUN:
        print(f"提示：当前为调试模式，不会写入数据库，从第 {SKIP_LINES + 1} 行开始检查")

    try:
        with open(FILE_PATH, "r", encoding="utf-8", errors="ignore") as f:
            for line_no, line in enumerate(f, start=1):
                if line_no <= SKIP_LINES:
                    continue

                if SKIP_HEADER and line_no == 1:
                    continue

                raw = line.strip()
                if not raw:
                    continue

                total_count += 1

                record, reason = parse_line(raw)
                if record is None:
                    bad_count += 1
                    print(f"无法解析第 {line_no} 行：{reason}")
                    print(f"原始内容：{raw!r}")
                    raise RuntimeError(f"导入中断：第 {line_no} 行无法解析，原因：{reason}")
                else:
                    batch.append(record)

                if len(batch) >= BATCH_SIZE:
                    if not DRY_RUN:
                        conn = await insert_batch(conn, batch, database_url)
                    insert_count += len(batch)
                    batch.clear()

                if line_no % PROGRESS_STEP == 0:
                    print(f"提示：已读取 {line_no} 行，已导入 {insert_count} 条，异常 {bad_count} 条")

        if batch:
            if not DRY_RUN:
                conn = await insert_batch(conn, batch, database_url)
            insert_count += len(batch)

    finally:
        if conn is not None and not conn.is_closed():
            await conn.close()

    print(f"提示：完成，总读取 {total_count} 条，导入 {insert_count} 条，异常 {bad_count} 条")


if __name__ == "__main__":
    asyncio.run(main())