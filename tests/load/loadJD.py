import asyncio
import os
from pathlib import Path
from typing import Any

import asyncpg

FILE_PATH = Path(r"D:\学习\来自：BT磁力链下载\裤子(1)\1\京东快递解压密码pncldyerk4gqofhp.onion\www_jd_com_12g.txt")
ENV_PATH = Path(__file__).resolve().parents[2] / "src" / ".env"

DB_NAME = "socialworker"
TABLE_NAME = "jingdong"
COLUMNS = ["name", "account", "password_hash", "email", "field5", "field6", "phone"]
BATCH_SIZE = 10000
PROGRESS_STEP = 100000
MAX_ROWS: int | None = None
DRY_RUN = False
ENCODINGS = ("utf-8-sig", "utf-8", "gb18030")


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
            name varchar(80),
            account varchar(100),
            password_hash varchar(100),
            email varchar(120),
            field5 varchar(200),
            field6 varchar(200),
            phone varchar(200)
        )
        """
    )


def clean_value(value: str) -> str | None:
    value = value.strip()
    if not value or value == r"\N":
        return None
    return value


def parse_line(line: str) -> tuple[Any, ...] | None:
    line = line.rstrip("\r\n")
    if not line:
        return None

    if ": " in line:
        index_part, data_part = line.split(": ", 1)
        if index_part.isdigit():
            line = data_part

    values = line.split("---", len(COLUMNS) - 1)
    if len(values) < len(COLUMNS):
        values.extend([None] * (len(COLUMNS) - len(values)))
    elif len(values) > len(COLUMNS):
        raise ValueError(f"字段数量不匹配，期望 {len(COLUMNS)} 个，实际 {len(values)} 个：{line[:300]}")

    return tuple(clean_value(value) if value is not None else None for value in values)


async def insert_batch(conn: asyncpg.Connection, batch: list[tuple[Any, ...]]) -> None:
    await conn.copy_records_to_table(TABLE_NAME, records=batch, columns=COLUMNS)


async def import_with_encoding(file_path: Path, encoding: str) -> None:
    database_url = "" if DRY_RUN else load_database_url()
    conn: asyncpg.Connection | None = None if DRY_RUN else await asyncpg.connect(database_url)
    batch: list[tuple[Any, ...]] = []
    total_count = 0
    insert_count = 0
    bad_count = 0

    try:
        if conn is not None:
            await create_table(conn)

        with file_path.open("r", encoding=encoding) as f:
            for line_no, line in enumerate(f, start=1):
                try:
                    record = parse_line(line)
                except Exception as e:
                    bad_count += 1
                    print(f"无法解析第 {line_no} 行：{e}")
                    raise

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
                        await insert_batch(conn, batch)
                    insert_count += len(batch)
                    batch.clear()
                    print(f"提示：已读取 {total_count} 条，已导入 {insert_count} 条，当前行 {line_no}")

                if total_count % PROGRESS_STEP == 0:
                    print(f"提示：已解析 {total_count} 条")

        if batch:
            if conn is not None:
                await insert_batch(conn, batch)
            insert_count += len(batch)

    finally:
        if conn is not None and not conn.is_closed():
            await conn.close()

    print(f"提示：完成，解析 {total_count} 条，导入 {insert_count} 条，异常 {bad_count} 条")


async def main() -> None:
    if not FILE_PATH.exists():
        raise FileNotFoundError(f"文件不存在：{FILE_PATH}")

    last_error: UnicodeDecodeError | None = None
    for encoding in ENCODINGS:
        try:
            print(f"提示：尝试使用编码 {encoding} 导入 -> {TABLE_NAME}")
            await import_with_encoding(FILE_PATH, encoding)
            return
        except UnicodeDecodeError as e:
            last_error = e

    raise UnicodeDecodeError(
        last_error.encoding,
        last_error.object,
        last_error.start,
        last_error.end,
        f"无法使用这些编码读取文件：{', '.join(ENCODINGS)}",
    )


if __name__ == "__main__":
    asyncio.run(main())