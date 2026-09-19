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

# 数学建模：构建正负道德情感极性轴（Z轴：-5 到 +5）
max_or = final_df['几率比权重'].max()
min_or = final_df['几率比权重'].min()

z_scores = []
for idx, row in final_df.iterrows():
    norm_or = 1.0 + 4.0 * (row['几率比权重'] - min_or) / (max_or - min_or + 1e-5)
    # 兼容繁体字和简体字的标签判断
    is_zhong = "忠" in row['群体标签']
    z_val = norm_or if is_zhong else -norm_or
    z_scores.append(z_val)
final_df['道德极性指数'] = z_scores
final_df['规范化群体标签'] = final_df['群体标签'].apply(lambda x: '忠臣特征' if '忠' in x else '奸臣特征')

# 让三轴比例更均衡：进一步拉开螺旋间距，避免 50 个词点过于拥挤，视觉上更清晰
final_df = final_df.sort_values(by='道德极性指数', ascending=False).reset_index(drop=True)
angles = np.linspace(0, 2 * np.pi, len(final_df), endpoint=False)
spiral_radius = 6.8
final_df['X_helix'] = spiral_radius * np.cos(angles)
final_df['Y_helix'] = spiral_radius * np.sin(angles)

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
    x=np.linspace(-7, 7, 2), y=np.linspace(-7, 7, 2), z=np.zeros((2, 2)),
    opacity=0.1, showscale=False, colorscale=[[0, '#888888'], [1, '#888888']], hoverinfo='skip'
))

fig.update_layout(
    title=dict(
        text='《明史》奸臣、忠臣情感特征25词及程度分布',
        x=0.5,
        xanchor='center',
        font=dict(size=24, color='#1f2937')
    ),
    scene=dict(
        xaxis=dict(title='X: 空间舒展轴', showticklabels=False, range=[-7.5, 7.5]),
        yaxis=dict(title='Y: 空间舒展轴', showticklabels=False, range=[-7.5, 7.5]),
        zaxis=dict(
            title='Z: 道德褒贬极性指数 (-8 到 +8)',
            range=[-8.8, 8.8],
            tickmode='array',
            tickvals=[-8, -6, -4, -2, 0, 2, 4, 6, 8],
            showbackground=True,
            backgroundcolor='rgba(245, 245, 245, 0.8)',
            gridcolor='rgba(90, 90, 90, 0.25)',
            zerolinecolor='rgba(200, 60, 60, 0.8)',
            zerolinewidth=2,
            tickfont=dict(color='#374151')
        ),
        camera=dict(eye=dict(x=2.2, y=1.8, z=1.0)),
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
