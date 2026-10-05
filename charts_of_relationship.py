import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Graph

# 1. 读取你刚刚合并去重完的终极干净关系表
# 请确保你的文件名是 rhetoric_final_edges.csv
df = pd.read_csv("jianchen_final.csv")

nodes = []
edges = []
nodes_set = set()

# 2. 定义三卷专属的强迫症学术配色体系（高雅色调）
category_colors = {
    "奸臣": "#E41A1C",  # 猩红（批判性）
    "佞幸": "#377EB8",  # 靛蓝（依附性）
    "盗贼": "#4DAF4A"   # 草绿（破坏性）
}

# 3. 提取所有传主节点
for _, row in df.iterrows():
    source = str(row['Source']).strip()
    target = str(row['Target']).strip()
    category = str(row['Category']).strip()
    
    # 填充传主节点（大圆点，代表历史人物）
    if source not in nodes_set:
        nodes.append({
            "name": source,
            "symbolSize": 25,  # 传主人物放大显示
            "itemStyle": {"color": category_colors.get(category, "#999999")},
            "category": category
        })
        nodes_set.add(source)
        
    # 填充修辞词汇节点（小圆点，代表书写修辞）
    if target not in nodes_set:
        nodes.append({
            "name": target,
            "symbolSize": 12,  # 修辞词汇小点显示
            "itemStyle": {"color": "#666666"}, # 修辞词默认深灰
            "category": "修辞词汇"
        })
        nodes_set.add(target)

    # 4. 构建网状关系的连线（边）
    edges.append({"source": source, "target": target})

# 5. 调用 pyecharts 力导向动态网络图引擎进行渲染
categories = [
    {"name": "奸臣"},
    {"name": "佞幸"},
    {"name": "盗贼"},
    {"name": "修辞词汇"},
]
category_color_map = {
    "奸臣": "#E41A1C",
    "佞幸": "#377EB8",
    "盗贼": "#4DAF4A",
    "修辞词汇": "#666666",
}

# 给每个节点补上 category 索引，并让 itemStyle 颜色由分类决定
cat_index = {c["name"]: i for i, c in enumerate(categories)}
for n in nodes:
    n["category"] = n["category"] if n["category"] in cat_index else "修辞词汇"
    n["symbol"] = "circle"

c = (
    Graph(init_opts=opts.InitOpts(width="100%", height="800px", page_title="明史三卷史官修辞知识图谱"))
    .add(
        "",
        nodes,
        edges,
        categories=categories,
        repulsion=1500,  # 节点之间的弹开排斥力，数值越大图谱越舒展
        is_draggable=True,  # 允许用鼠标随意拖拽节点
        edge_label=opts.LabelOpts(is_show=False),
        label_opts=opts.LabelOpts(position="right", is_show=True), # 节点旁边显示文字
        itemstyle_opts=opts.ItemStyleOpts(color=None),  # 让 echarts 按 categories 着色
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(title="《明史》奸臣/佞幸/盗贼卷──史官书写修辞网络知识图谱", subtitle="基于数字人文词典映射与二元关系配对研究"),
        legend_opts=opts.LegendOpts(is_show=True, orient="vertical", pos_left="2%", pos_top="10%")
    )
    .render("明史修辞知识图谱.html") # 一键渲染导出为独立的 HTML 网页文件
)

# 6. 把 CDN 引用替换为本地 echarts，保证 file:// 直接双击也能打开
import os, re
html_path = "明史修辞知识图谱.html"
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

print("\n🎉 【终极大功告成！】网页动态知识图谱已完美生成！")
print("请在你的本地文件夹中，直接双击打开【明史修辞知识图谱.html】网页文件，即可开启沉浸式学术探索！")
