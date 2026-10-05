import pandas as pd

# 1. 读取 CSV 文件
df = pd.read_csv("rhetoric_v3.csv")
df_clean = df[['传主', '所属奸臣类型', '传主特征']]

relationships = []

# 2. 整合后的单层循环拦截
for current_idx, (index, row) in enumerate(df_clean.iterrows()):
    
    excel_row_number = current_idx + 2  # 计算出在 Excel 中的物理行号
    name = str(row['传主']).strip()
    
    # 【最终纯净版拦截】：只保留数字指定和空行跳过两种条件
    if (excel_row_number in [2, 22, 36]) or (name in ["nan", "无"]):
        print(f"--- ⚠️ 【过滤拦截】已跳过不相关或空行：物理行号 {[2, 22, 36]} (传主: {name}) ---")
        continue

    # 3. 只有通过上面两种筛选的纯净传主行，才会来到这里进行修辞拆解
    rhetoric_text = str(row['传主特征'])
    category = str(row['所属奸臣类型']).strip()
    
    # 将同一格里用逗号隔开的多组修辞拆开，与传主进行一对一咬合绑定
    words = [w.strip() for w in rhetoric_text.replace("，", ",").split(",") if w.strip()]
    
    for word in words:
        relationships.append({
            "Source": name,
            "Target": word,
            "Category": category
        })

# 4. 导出最终成果表
result_df = pd.DataFrame(relationships)
result_df.to_csv("rhetoric_final_edges.csv", index=False, encoding="utf-8-sig")
print("\n🎉 【处理完成】成果已成功导出为 rhetoric_final_edges.csv！")
