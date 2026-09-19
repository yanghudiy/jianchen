import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

print("【🚀本地系统提示】: 正在构建【位置硬绑定・50词全息双螺旋】图...")

# 读取 25 词扩容版的数据结果
try:
    final_df = pd.read_csv('./analysis_result.csv')
except FileNotFoundError:
    print("【⚠️错误】: 请先运行 history_analysis.py 生成基础数据！")
    exit()

# 🚨 【终极修复点】：彻底抛弃字符名字匹配，改用绝对位置绑定
# 无论第一列叫什么，强行改叫 '词语'；第四列强行叫 '几率比权重'；第五列强行叫 '群体标签'
if len(final_df.columns) >= 5:
    final_df.columns.values[0] = '词语'
    final_df.columns.values[1] = '奸臣组频数'
    final_df.columns.values[2] = '忠臣组频数'
    final_df.columns.values[3] = '几率比权重'
    final_df.columns.values[4] = '群体标签'
else:
    # 极端防错：如果列数不足，强行补充
    print("【⚠️警告】: CSV文件数据列数不足，正在强行修正...")
    final_df.columns = ['词语', '奸臣组频数', '忠臣组频数', '几率比权重', '群体标签'][:len(final_df.columns)]

# 强制将几率比权重转为数字类型，防止字符串格式干扰计算
final_df['几率比权重'] = pd.to_numeric(final_df['几率比权重'], errors='coerce').fillna(1.0)
final_df['群体标签'] = final_df['群体标签'].astype(str).str.strip()
final_df['规范化群体标签'] = final_df['群体标签'].replace({'奸臣特徵': '奸臣特征', '忠臣特徵': '忠臣特征'})

# 数学建模：构建正负道德情感极性轴（Z轴：-5 到 +5）
# 🚨 【Z轴去重补丁】：按组内几率比权重排名生成唯一高度，避免同权词在Z轴重叠遮挡
final_df = final_df.sort_values(by='几率比权重', ascending=False).reset_index(drop=True)

z_scores = []
for label in ['忠', '奸']:
    mask = final_df['群体标签'].str.contains(label)
    sub = final_df[mask].sort_values(by='几率比权重', ascending=False)
    n = len(sub)
    # 每个词在组内获得唯一排名高度：忠臣 +1.0~+5.0，奸臣 -1.0~-5.0
    for rank, idx in enumerate(sub.index):
        frac = (n - 1 - rank) / (n - 1) if n > 1 else 0.5  # 权重越高→越靠近极值
        if label == '忠':
            z_val = 6.0 + 24.0 * frac
        else:
            z_val = -(6.0 + 24.0 * frac)
        z_scores.append((idx, z_val))

# 写回原 df（按原始索引对齐）
idx_to_z = dict(z_scores)
final_df['道德极性指数'] = final_df.index.map(lambda i: idx_to_z[i])

# 🚨 【附加微调补丁】：将圆柱半径从 6 扩大到 8，在水平方向上也进一步拉开词与词的距离
final_df = final_df.sort_values(by='道德极性指数', ascending=False).reset_index(drop=True)
angles = np.linspace(0, 2 * np.pi, len(final_df), endpoint=False)
final_df['X_helix'] = 50 * np.cos(angles)  # 半径放大到 50，给标签留足空间
final_df['Y_helix'] = 50 * np.sin(angles)  # 半径放大到 50，给标签留足空间


# 绘制纯净版全息 3D 图
fig = px.scatter_3d(
    final_df, x='X_helix', y='Y_helix', z='道德极性指数',
    text='词语', color='规范化群体标签',
    color_discrete_map={'忠臣特征': '#2b5c8f', '奸臣特征': '#b83b3b'},
    hover_data={'X_helix': False, 'Y_helix': False, '道德极性指数': ':.2f', '几率比权重': ':.2f'}
)

# 视觉美化与全白浮窗样式强设定
fig.update_traces(
    marker=dict(size=5.5, opacity=0.9),
    textposition='top center',
    textfont=dict(size=17, family='Microsoft YaHei, SimHei, sans-serif'),
    hovertemplate="<b>【特征词】：%{text}</b><br>群体归属：%{customdata}<br>道德褒贬指数：%{z:.2f}<br>原始几率比：%{customdata:.2f}<br><i>【全息解说】：正值代表史官的道德褒扬，负值代表道德谴责。</i><extra></extra>",
    hoverlabel=dict(font=dict(color='white', size=12)) # 强制浮窗文字全白
)

# 增加 Z=0 处的半透明灰色中性道德参考面
fig.add_trace(go.Surface(
    x=np.linspace(-52, 52, 2), y=np.linspace(-52, 52, 2), z=np.zeros((2, 2)),
    opacity=0.1, showscale=False, colorscale=[[0, '#888888'], [1, '#888888']], hoverinfo='skip'
))

fig.update_layout(
    title=dict(
        text='《明史》奸臣、忠臣特征25词及程度分布',
        x=0.5,
        xanchor='center',
        font=dict(size=24, color='#1f2937')
    ),
    scene=dict(
        xaxis=dict(
            title='X: 空间舒展轴', showticklabels=False, range=[-55, 55],
            showbackground=True, backgroundcolor='rgba(245, 245, 245, 0.8)',
            gridcolor='rgba(90, 90, 90, 0.25)', zerolinecolor='rgba(60, 120, 200, 0.8)',
            zerolinewidth=2, showgrid=True, showline=True
        ),
        yaxis=dict(
            title='Y: 空间舒展轴', showticklabels=False, range=[-55, 55],
            showbackground=True, backgroundcolor='rgba(245, 245, 245, 0.8)',
            gridcolor='rgba(90, 90, 90, 0.25)', zerolinecolor='rgba(60, 120, 200, 0.8)',
            zerolinewidth=2, showgrid=True, showline=True
        ),
        zaxis=dict(
            title='Z: 道德褒贬极性指数 (-30 到 +30)',
            range=[-32, 32],
            tickmode='array',
            tickvals=[-30, -24, -18, -12, -6, 0, 6, 12, 18, 24, 30],
            showbackground=True,
            backgroundcolor='rgba(245, 245, 245, 0.8)',
            gridcolor='rgba(90, 90, 90, 0.25)',
            zerolinecolor='rgba(200, 60, 60, 0.8)',
            zerolinewidth=2,
            tickfont=dict(color='#374151')
        ),
        camera=dict(eye=dict(x=1.5, y=1.5, z=1.2)),
        aspectmode='manual',
        aspectratio=dict(x=1.0, y=1.0, z=1.0)
    ),
    margin=dict(l=12, r=12, b=12, t=60),
    legend=dict(title_text='史官道德叙事判定', yanchor="top", y=0.95, xanchor="left", x=0.05),
    width=1500,
    height=1100
)

output_path = './analysis_morality_axis.html'
fig.write_html(output_path)
print(f"【🎉大功告成】: 50词独立全息网页已成功生成！请查看: {output_path}")
