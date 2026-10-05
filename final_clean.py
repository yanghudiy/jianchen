import pandas as pd

# 1. 读取你刚刚剔除完杂质、但还含有重复词的 CSV 文件
# 请将 "your_cleaned_output.csv" 替换为你本地文件的真实名称
input_file = "rhetoric_final_edges.csv" 
df = pd.read_csv(input_file)

# 打印去重前的状态，方便强迫症核对
initial_rows = len(df)
print(f"--- 📊 正在处理：{input_file} ---")
print(f"合并前，表格当前共有关系数: {initial_rows} 条")

# 2. 【核心合并去重指令】
# 依据 'Source'(传主) 和 'Target'(史官修辞) 这两列的组合进行排查
# 只要同一个传主身上出现了相同的词，只保留第一个（first），其余重复的合并删去
df_merged = df.drop_duplicates(subset=['Source', 'Target'], keep='first')

# 3. 导出合并去重后的终极学术成果表
output_file = "rhetoric_final_edges.csv"
df_merged.to_csv(output_file, index=False, encoding="utf-8-sig")

# 4. 打印合并结果
final_rows = len(df_merged)
removed_rows = initial_rows - final_rows
print(f"\n🎉 【传主重复特征词合并完成！】")
print(f"共发现并合并了 {removed_rows} 条在传主身上重复复现的修辞词。")
print(f"合并后，最终纯净关系数: {final_rows} 条")
print(f"完美的去重成果已成功导出为：{output_file}")
