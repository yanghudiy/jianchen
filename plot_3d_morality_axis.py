# -*- coding: utf-8 -*-
"""
正负道德情感烈度与褒贬极性数轴 —— 全息交互 3D 网页。
读取 analysis_result.csv，将几率比权重非线性映射为
道德褒贬极性指数（忠臣 +1~+5，奸臣 -5~-1），
圆柱双螺旋布局，Z=0 零点参考面，生成独立交互 HTML。

运行前请先安装依赖：
    pip install pandas plotly numpy

运行：
    python plot_3d_morality_axis.py

输出：
    ./analysis_morality_axis.html
"""

import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------------------------------------
# 路径与配置
# ----------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "analysis_result.csv")
OUT_HTML = os.path.join(BASE_DIR, "analysis_morality_axis.html")

# 学术级配色
COLOR_LOYAL = "#2b5c8f"
COLOR_TRAITOR = "#b83b3b"

# 圆柱半径 & 总词数
RADIUS = 5.0
TOTAL_WORDS = 30

CJK_FONT = "Noto Sans SC, PingFang SC, Microsoft YaHei, sans-serif"


# ----------------------------------------------------------------------
# 读取 CSV
# ----------------------------------------------------------------------
def read_result(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8")
    df.columns = [c.strip() for c in df.columns]
    return df


# ----------------------------------------------------------------------
# 道德褒贬极性指数计算
# ----------------------------------------------------------------------
def compute_morality_index(sub: pd.DataFrame) -> pd.DataFrame:
    """
    忠臣特征 → 正区间 [+1.0, +5.0]
    奸臣特征 → 负区间 [-5.0, -1.0]
    使用 log1p 压缩后做 min-max 线性缩放到目标区间。
    """
    sub = sub.copy()
    sub["OR_log"] = np.log1p(sub["几率比权重"].astype(float))

    loyal_mask = sub["群体标签"].str.contains("忠")
    traitor_mask = sub["群体标签"].str.contains("奸")

    # 忠臣：[+1, +5]
    if loyal_mask.any():
        lvals = sub.loc[loyal_mask, "OR_log"]
        lmin, lmax = lvals.min(), lvals.max()
        if lmax > lmin:
            scaled = (lvals - lmin) / (lmax - lmin)  # 0~1
        else:
            scaled = pd.Series(0.5, index=lvals.index)
        sub.loc[loyal_mask, "道德褒贬极性指数"] = 1.0 + scaled * 4.0  # +1~+5

    # 奸臣：[-5, -1]
    if traitor_mask.any():
        tvals = sub.loc[traitor_mask, "OR_log"]
        tmin, tmax = tvals.min(), tvals.max()
        if tmax > tmin:
            scaled = (tvals - tmin) / (tmax - tmin)
        else:
            scaled = pd.Series(0.5, index=tvals.index)
        sub.loc[traitor_mask, "道德褒贬极性指数"] = -(1.0 + scaled * 4.0)  # -1~-5

    return sub


# ----------------------------------------------------------------------
# 全息三维散点图
# ----------------------------------------------------------------------
def plot(df: pd.DataFrame):
    df = df.copy()
    df["群体标签"] = df["群体标签"].astype(str)

    loyal = df[df["群体标签"].str.contains("忠")].sort_values(
        "几率比权重", ascending=False).head(15)
    traitor = df[df["群体标签"].str.contains("奸")].sort_values(
        "几率比权重", ascending=False).head(15)
    sub = pd.concat([loyal, traitor], ignore_index=True)

    # —— 道德褒贬极性指数 ——
    sub = compute_morality_index(sub)

    # —— 圆柱双螺旋布局 ——
    sub = sub.sort_values("几率比权重", ascending=False).reset_index(drop=True)
    sub["排名"] = np.arange(1, len(sub) + 1)
    sub["theta"] = (sub["排名"] / TOTAL_WORDS) * 2.0 * np.pi
    sub["X_helix"] = RADIUS * np.cos(sub["theta"])
    sub["Y_helix"] = RADIUS * np.sin(sub["theta"])

    fig = px.scatter_3d(
        sub,
        x="X_helix",
        y="Y_helix",
        z="道德褒贬极性指数",
        color="群体标签",
        text="词语",
        custom_data=["奸臣组频数", "忠臣组频数", "几率比权重",
                     "道德褒贬极性指数"],
        color_discrete_map={
            "忠臣特征": COLOR_LOYAL,
            "奸臣特征": COLOR_TRAITOR,
        },
        title="<b>《明史》忠臣 vs 奸臣 正负道德褒贬极性全息投影</b>",
    )

    # —— 全白浮窗 ——
    hover_tpl = (
        "<b style='font-size:16px'>【词语】：%{text}</b><br>"
        "━━━━━━━━━━━━━━━━<br>"
        "奸臣文本频数：<b>%{customdata[0]}</b><br>"
        "忠臣文本频数：<b>%{customdata[1]}</b><br>"
        "原始几率比权重(OR)：<b>%{customdata[2]:.4f}</b><br>"
        "━━━━━━━━━━━━━━━━<br>"
        "<span style='color:white;'>"
        "道德褒贬极性指数：<b>%{customdata[3]:+.2f}</b>"
        "</span>"
        "<extra></extra>"
    )

    fig.update_traces(
        marker=dict(size=6, line=dict(width=0.4, color="#444")),
        textposition="top center",
        textfont=dict(size=11, color="#222", family=CJK_FONT),
        hovertemplate=hover_tpl,
        hoverlabel=dict(
            font=dict(color="white", size=12),
            bordercolor="black",
        ),
        selector=dict(type="scatter3d"),
    )

    # —— 立体零点平面（道德中性分界线） ——
    z_plane_x = np.array([-RADIUS, RADIUS, RADIUS, -RADIUS])
    z_plane_y = np.array([-RADIUS, -RADIUS, RADIUS, RADIUS])
    z_plane_z = np.array([0, 0, 0, 0])
    fig.add_trace(go.Mesh3d(
        x=z_plane_x, y=z_plane_y, z=z_plane_z,
        color="lightgray", opacity=0.12,
        alphahull=0,
        hoverinfo="skip",
        showlegend=False,
    ))

    # —— 坐标轴命名 ——
    fig.update_layout(
        scene=dict(
            xaxis=dict(title=dict(text="圆柱面 X 坐标 (cosθ)"),
                       backgroundcolor="rgba(245,245,250,0.9)",
                       gridcolor="#cccccc", showbackground=True),
            yaxis=dict(title=dict(text="圆柱面 Y 坐标 (sinθ)"),
                       backgroundcolor="rgba(245,245,250,0.9)",
                       gridcolor="#cccccc", showbackground=True),
            zaxis=dict(title=dict(text="道德褒贬极性指数 (-5 到 +5)"),
                       backgroundcolor="rgba(245,245,250,0.9)",
                       gridcolor="#cccccc", showbackground=True,
                       zeroline=True, zerolinewidth=2,
                       zerolinecolor="rgba(120,120,120,0.6)"),
            camera=dict(eye=dict(x=1.4, y=1.4, z=1.1)),
            aspectmode="cube",
        ),
        legend=dict(title=dict(text="群体标签"),
                    font=dict(family=CJK_FONT, size=12)),
        title_font=dict(family=CJK_FONT, size=18),
        margin=dict(l=0, r=0, t=80, b=0),
    )

    fig.write_html(OUT_HTML, include_plotlyjs="cdn")


# ----------------------------------------------------------------------
# 主流程
# ----------------------------------------------------------------------
def main():
    df = read_result(CSV_PATH)
    plot(df)


if __name__ == "__main__":
    main()
