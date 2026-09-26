from pathlib import Path
import re
from collections import Counter

FILE_PATH = Path(r"D:\学习\来自：BT磁力链下载\裤子(1)\1\shunfeng\script.sql")
ENCODING = "utf-16"

CREATE_RE = re.compile(r"CREATE\s+TABLE\s+\[dbo\]\.\[([^\]]+)\]", re.IGNORECASE)
INSERT_RE = re.compile(r"INSERT\s+\[dbo\]\.\[([^\]]+)\]", re.IGNORECASE)

create_tables = Counter()
insert_tables = Counter()

with FILE_PATH.open("r", encoding=ENCODING) as f:
    for line_no, line in enumerate(f, start=1):
        create_match = CREATE_RE.search(line)
        if create_match:
            create_tables[create_match.group(1)] += 1

        insert_match = INSERT_RE.search(line)
        if insert_match:
            insert_tables[insert_match.group(1)] += 1

print("CREATE TABLE：")
for table, count in create_tables.items():
    print(table, count)

print("\nINSERT：")
for table, count in insert_tables.items():
    print(table, count)