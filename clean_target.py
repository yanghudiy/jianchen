import csv
import re

INPUT = "rhetoric_final_edges.csv"
OUTPUT = "jianchen_final.csv"

with open(INPUT, newline="", encoding="utf-8") as f:
    rows = list(csv.reader(f))

header, data = rows[0], rows[1:]
target_idx = header.index("Target")

for r in data:
    raw = r[target_idx]
    # 去掉所有引号，只保留汉字
    cleaned = re.sub(r'["""]+', "", raw)
    r[target_idx] = cleaned

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(header)
    w.writerows(data)

print(f"Done -> {OUTPUT}")