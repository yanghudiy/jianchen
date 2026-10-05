import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Sankey

# 1. 读取你合并去重完的终极干净关系表 (rhetoric_final_edges.csv)
df = pd.read_csv("jianchen_final.csv")

# 2. 核心统计：计算每一卷中，各个修辞词汇出现的次数（频数统计）
# 这一步让 Python 自动帮你数清每个词被史官用了多少次，作为桑基图水流的粗细权重（value）
# 注：桑基图不允许 source==target 的自环（如「佞幸」既是卷名又是某人物的修辞词），
#     这种自环没有流向意义，必须过滤掉，否则 echarts 会抛 dataIndex 错误。
df = df[df['Category'].astype(str).str.strip() != df['Target'].astype(str).str.strip()].copy()
counts_df = df.groupby(['Category', 'Target']).size().reset_index(name='value')

# 3. 构建桑基图需要的节点列表 (Nodes)
# 包括左侧的三个大类（卷名）和右侧的所有修辞词汇
nodes = []
nodes_set = set()

# 放入左侧卷名节点
for cat in counts_df['Category'].unique():
    nodes.append({"name": str(cat).strip()})
    nodes_set.add(str(cat).strip())

# 放入右侧修辞词汇节点
for tgt in counts_df['Target'].unique():
    name = str(tgt).strip()
    if name not in nodes_set:
        nodes.append({"name": name})
        nodes_set.add(name)

# 4. 构建水流连线 (Links)
links = []
for _, row in counts_df.iterrows():
    links.append({
        "source": str(row['Category']).strip(),
        "target": str(row['Target']).strip(),
        "value": int(row['value']) # 水流粗细完美对应词频统计次数
    })

# 5. 调用 pyecharts 桑基图引擎进行高颜值渲染
sankey = (
    Sankey(init_opts=opts.InitOpts(width="100%", height="900px", page_title="明史修辞流向桑基图"))
    .add(
        series_name="",
        nodes=nodes,
        links=links,
        # 强迫症专属排版参数：调整左右间距，防止文字和水流挤在一起
        pos_left="10%",
        pos_right="15%",
        node_width=20,     # 条块的宽度
        node_gap=15,       # 条块之间的上下间距
        orient="horizontal",
        label_opts=opts.LabelOpts(position="right", font_size=12),
        # 鼠标悬停在水流或词汇上时，自动弹窗显示该词被具体统计了多少次
        tooltip_opts=opts.TooltipOpts(trigger="item", trigger_on="mousemove")
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(
            title="《明史》奸臣/佞幸/盗贼卷──史官惯用修辞频数统计与派系流向桑基图", 
            subtitle="水流粗细严格对应修辞词汇在各卷传主身上的复现频次统计",
            pos_left="center"
        )
    )
    .render("明史修辞流向桑基图.html") # 一键渲染导出为独立的 HTML 网页文件
)

# 6. 把 CDN 引用替换为本地 echarts，保证 file:// 直接双击也能打开
import os, re
html_path = "明史修辞流向桑基图.html"
os.makedirs("assets", exist_ok=True)
if not os.path.exists("assets/echarts.min.js"):
    import urllib.request
    urllib.request.urlretrieve(
        "https://assets.pyecharts.org/assets/v6/echarts.min.js",
        "assets/echarts.min.js",
    )
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()
html = re.sub(
    r'src="https://assets\.pyecharts\.org/assets/v6/echarts\.min\.js"',
    'src="assets/echarts.min.js"',
    html,
)
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print("\n🎉 【词频统计桑基图绘制完成！】")
print("完美的成果已成功导出为：明史修辞流向桑基图.html")
print("请在你的本地文件夹中直接双击打开该网页，即可开启最直观的修辞交叉分布探索！")
