import asyncio
import os
from pathlib import Path
from typing import Any

import asyncpg
import pandas as pd

ROOT_DIR = Path(r"C:\jieya\户籍数据1.03GB公安专用")
ENV_PATH = Path(__file__).resolve().parents[2] / "src" / ".env"

DB_NAME = "socialworker"
TABLE_NAME = "census"
COLUMNS = ["statistics_period", "code", "birthday", "sex", "number", "name", "phone", "address"]
SOURCE_COLUMNS = ["统计时间", "编码编号", "出生日期", "性别", "身份证", "名字", "手机号", "地址"]
DEFAULT_VALUES = {
    "统计时间": None,
    "编码编号": None,
    "出生日期": None,
    "性别": 2,
    "身份证": None,
    "名字": None,
    "手机号": None,
    "地址": None,
}

BATCH_SIZE = 10000
PROGRESS_STEP = 100000
SKIP_ROWS = 0
MAX_ROWS: int | None = None
MAX_RETRIES = 10
RETRY_DELAY = 10
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


def clean_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def parse_text(value: Any) -> str | None:
    value = clean_value(value)
    if value is None:
        return None

    if isinstance(value, float) and value.is_integer():
        value = int(value)

    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    return text or None


def parse_datetime(value: Any) -> Any:
    value = clean_value(value)
    if value is None:
        return None
    return pd.to_datetime(value, errors="coerce").to_pydatetime() if not pd.isna(pd.to_datetime(value, errors="coerce")) else None


def parse_sex(value: Any) -> int | None:
    value = clean_value(value)
    if value is None:
        return 2

    value = str(value).strip()
    if value in ("男", "1", "1.0"):
        return 1
    if value in ("女", "0", "0.0"):
        return 0
    if value in ("未知", "2", "2.0"):
        return 2
    return 2


def parse_phone(value: Any) -> str | None:
    value = clean_value(value)
    if value is None:
        return None

    if isinstance(value, float) and value.is_integer():
        value = int(value)

    phone = str(value).strip()
    if phone.endswith(".0"):
        phone = phone[:-2]

    return phone if phone.isdigit() else None


def parse_row(row: pd.Series) -> tuple[Any, ...]:
    return (
        parse_datetime(row["统计时间"]),
        parse_text(row["编码编号"]),
        parse_datetime(row["出生日期"]),
        parse_sex(row["性别"]),
        parse_text(row["身份证"]),
        parse_text(row["名字"]),
        parse_text(row["手机号"]),
        parse_text(row["地址"]),
    )


def fill_missing_columns(df: pd.DataFrame, file_path: Path) -> pd.DataFrame:
    missing_columns = [column for column in SOURCE_COLUMNS if column not in df.columns]
    if missing_columns:
        print(f"提示：文件 {file_path} 缺少列 {missing_columns}，已使用默认值")

    for column in missing_columns:
        df[column] = DEFAULT_VALUES[column]

    return df[SOURCE_COLUMNS]


async def insert_batch(
    conn: asyncpg.Connection,
    batch: list[tuple[Any, ...]],
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
    batch: list[tuple[Any, ...]] = []

    mode = "调试检查" if DRY_RUN else f"导入 -> {TABLE_NAME}"
    xlsx_files = sorted(path for path in ROOT_DIR.rglob("*.xlsx") if not path.name.startswith("~$"))
    print(f"提示：开始{mode} {ROOT_DIR}，共发现 {len(xlsx_files)} 个 xlsx 文件")
    if DRY_RUN:
        print("提示：当前为调试模式，不会写入数据库")

    try:
        for file_index, file_path in enumerate(xlsx_files, start=1):
            print(f"提示：开始处理第 {file_index}/{len(xlsx_files)} 个文件：{file_path}")
            df = pd.read_excel(file_path, skiprows=range(1, SKIP_ROWS + 1), nrows=MAX_ROWS)
            df = fill_missing_columns(df, file_path)
            print(f"提示：当前文件已读取到内存，准备处理 {len(df)} 条数据")

            file_count = 0
            file_insert_count = 0

            for index, row in df.iterrows():
                row_no = SKIP_ROWS + index + 2
                total_count += 1
                file_count += 1

                try:
                    record = parse_row(row)
                except Exception as e:
                    bad_count += 1
                    print(f"无法解析文件 {file_path} 第 {row_no} 行：{e}")
                    print(f"原始内容：{row.to_dict()}")
                    raise

                batch.append(record)

                if DRY_RUN and total_count <= 10:
                    print(dict(zip(COLUMNS, record)))

                if len(batch) >= BATCH_SIZE:
                    current_batch_size = len(batch)
                    if not DRY_RUN:
                        conn = await insert_batch(conn, batch, database_url)
                    insert_count += current_batch_size
                    file_insert_count += current_batch_size
                    print(f"提示：本批处理 {current_batch_size} 条，当前文件累计处理 {file_insert_count} 条，总累计处理 {insert_count} 条")
                    batch.clear()

                if total_count % PROGRESS_STEP == 0:
                    print(f"提示：已读取 {total_count} 条，已处理 {insert_count} 条，异常 {bad_count} 条")

            print(f"提示：文件处理完成：{file_path}，读取 {file_count} 条，已批量提交 {file_insert_count} 条，待提交 {len(batch)} 条")

        if batch:
            current_batch_size = len(batch)
            if not DRY_RUN:
                conn = await insert_batch(conn, batch, database_url)
            insert_count += current_batch_size
            print(f"提示：最后一批处理 {current_batch_size} 条，累计处理 {insert_count} 条")

    finally:
        if conn is not None and not conn.is_closed():
            await conn.close()

    print(f"提示：完成，总读取 {total_count} 条，处理 {insert_count} 条，异常 {bad_count} 条")


if __name__ == "__main__":
    asyncio.run(main())