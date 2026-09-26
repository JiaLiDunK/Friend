import asyncio
import os
from pathlib import Path
from typing import Any

import asyncpg

FILE_PATH = Path(r"D:\学习\来自：BT磁力链下载\裤子(1)\1\shunfeng\script.sql")
ENV_PATH = Path(__file__).resolve().parents[2] / "src" / ".env"

DB_NAME = "socialworker"
TABLE_NAME = "shunfeng"
COLUMNS = ["name", "phone", "province", "city", "dist", "addr"]
ENCODING = "utf-16"
BATCH_SIZE = 10000
PROGRESS_STEP = 100000
MAX_ROWS: int | None = None
DRY_RUN = False


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


async def create_table(conn: asyncpg.Connection) -> None:
    await conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            name varchar(40),
            phone varchar(15),
            province varchar(30),
            city varchar(30),
            dist varchar(40),
            addr varchar(200)
        )
        """
    )


def parse_sql_value(value: str) -> str | None:
    value = value.strip()
    if value.upper() == "NULL":
        return None
    if value.startswith("N'") and value.endswith("'"):
        return value[2:-1].replace("''", "'")
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    return value


def split_values(values: str) -> list[str]:
    result: list[str] = []
    current: list[str] = []
    in_string = False
    index = 0

    while index < len(values):
        char = values[index]
        if char == "'":
            current.append(char)
            if in_string and index + 1 < len(values) and values[index + 1] == "'":
                current.append(values[index + 1])
                index += 2
                continue
            in_string = not in_string
        elif char == "," and not in_string:
            result.append("".join(current).strip())
            current.clear()
        else:
            current.append(char)
        index += 1

    result.append("".join(current).strip())
    return result


def parse_insert_line(line: str) -> tuple[Any, ...] | None:
    upper_line = line.upper()
    if "INSERT" not in upper_line or "VALUES" not in upper_line:
        return None

    values_start = upper_line.find("VALUES")
    left = line.find("(", values_start)
    right = line.rfind(")")
    if left == -1 or right == -1 or right <= left:
        return None

    values = split_values(line[left + 1:right])
    if len(values) != len(COLUMNS):
        raise ValueError(f"字段数量不匹配，期望 {len(COLUMNS)} 个，实际 {len(values)} 个：{line[:300]}")

    return tuple(parse_sql_value(value) for value in values)


async def main() -> None:
    if not FILE_PATH.exists():
        raise FileNotFoundError(f"文件不存在：{FILE_PATH}")

    database_url = "" if DRY_RUN else load_database_url()
    conn: asyncpg.Connection | None = None if DRY_RUN else await asyncpg.connect(database_url)
    batch: list[tuple[Any, ...]] = []
    total_count = 0
    insert_count = 0

    try:
        if conn is not None:
            await create_table(conn)

        with FILE_PATH.open("r", encoding=ENCODING) as f:
            for line_no, line in enumerate(f, start=1):
                record = parse_insert_line(line)
                if record is None:
                    continue

                total_count += 1
                batch.append(record)

                if DRY_RUN and total_count <= 10:
                    print(dict(zip(COLUMNS, record)))

                if MAX_ROWS is not None and total_count >= MAX_ROWS:
                    break

                if len(batch) >= BATCH_SIZE:
                    if conn is not None:
                        await conn.copy_records_to_table(TABLE_NAME, records=batch, columns=COLUMNS)
                    insert_count += len(batch)
                    batch.clear()
                    print(f"提示：已读取 {total_count} 条，已导入 {insert_count} 条，当前行 {line_no}")

                if total_count % PROGRESS_STEP == 0:
                    print(f"提示：已解析 {total_count} 条")

        if batch:
            if conn is not None:
                await conn.copy_records_to_table(TABLE_NAME, records=batch, columns=COLUMNS)
            insert_count += len(batch)

    finally:
        if conn is not None and not conn.is_closed():
            await conn.close()

    print(f"提示：完成，解析 {total_count} 条，导入 {insert_count} 条")


if __name__ == "__main__":
    asyncio.run(main())