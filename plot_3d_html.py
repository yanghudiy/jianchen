# -*- coding: utf-8 -*-
"""
方案三：立体双螺旋圆柱投影图（终极融合版）。
读取 analysis_result.csv，将 30 个特征词按几率比权重排名硬性映射到
半径为 5 的圆柱面上（圆周等距错开），Z 轴使用对数压缩几率比，
并在浮窗与页面批注中融合几率比（Odds Ratio）学术解说。

运行前请先安装依赖：
    pip install pandas plotly numpy

运行：
    python plot_3d_html.py

输出：
    ./analysis_3d_projection.html  （离线独立网页，浏览器打开即可交互）
"""

import os
import numpy as np
import pandas as pd
import plotly.express as px

# ----------------------------------------------------------------------
# 路径与配置
# ----------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "analysis_result.csv")
OUT_HTML = os.path.join(BASE_DIR, "analysis_3d_projection.html")

# 学术级配色
COLOR_LOYAL = "#2b5c8f"     # 忠臣——深蓝
COLOR_TRAITOR = "#b83b3b"   # 奸臣——深红

# 圆柱半径
RADIUS = 5.0
# 总词数（等距圆周映射基数）
TOTAL_WORDS = 30

# 中文字体族
CJK_FONT = "Noto Sans SC, PingFang SC, Microsoft YaHei, sans-serif"


# ----------------------------------------------------------------------
# 读取 CSV（plotly 原生支持 UTF-8 中文，无需手动下载字体）
# ----------------------------------------------------------------------
def read_result(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8")
    df.columns = [c.strip() for c in df.columns]
    return df


# ----------------------------------------------------------------------
# 圆柱坐标几何变换 + 全息三维散点图（融合学术解说）
# ----------------------------------------------------------------------
def plot(df: pd.DataFrame):
    df = df.copy()
    df["群体标签"] = df["群体标签"].astype(str)

    # 各取权重前 15
    loyal = df[df["群体标签"].str.contains("忠")].sort_values(
        "几率比权重", ascending=False).head(15)
    traitor = df[df["群体标签"].str.contains("奸")].sort_values(
        "几率比权重", ascending=False).head(15)
    sub = pd.concat([loyal, traitor], ignore_index=True)

    # —— 圆柱坐标几何变换（彻底拉开空间核心） ——
    sub = sub.sort_values("几率比权重", ascending=False).reset_index(drop=True)
    sub["排名"] = np.arange(1, len(sub) + 1)

    # 圆周角度 theta：排名硬性映射到 360 度圆周，等距错开
    sub["theta"] = (sub["排名"] / TOTAL_WORDS) * 2.0 * np.pi

    # 立体 X / Y：分布在半径为 5 的圆柱面上
    sub["X_helix"] = RADIUS * np.cos(sub["theta"])
    sub["Y_helix"] = RADIUS * np.sin(sub["theta"])

    # Z 轴：对数压缩后的几率比权重
    sub["Z_log"] = np.log1p(sub["几率比权重"].astype(float))

    # custom_data 供 hover 显示原始真实频数与权重
    fig = px.scatter_3d(
        sub,
        x="X_helix",
        y="Y_helix",
        z="Z_log",
        color="群体标签",
        text="词语",
        custom_data=["奸臣组频数", "忠臣组频数", "几率比权重"],
        color_discrete_map={
            "忠臣特征": COLOR_LOYAL,
            "奸臣特征": COLOR_TRAITOR,
        },
        title="<b>《明史》忠臣 vs 奸臣 特征词立体双螺旋圆柱投影</b>"
              "<br><span style='font-size:12px;color:#666'>"
              "方案三 · 圆周等距 · 几率比(Odds Ratio)对数压缩 · 360° 可交互"
              "</span>",
    )

    # —— 全息动态浮窗解说升级（Hover Text Integration） ——
    hover_tpl = (
        "<b style='font-size:16px'>【词语】：%{text}</b><br>"
        "━━━━━━━━━━━━━━━━<br>"
        "奸臣文本频数：<b>%{customdata[0]}</b><br>"
        "忠臣文本频数：<b>%{customdata[1]}</b><br>"
        "原始几率比权重(OR)：<b>%{customdata[2]:.4f}</b><br>"
        "━━━━━━━━━━━━━━━━<br>"
        "<span style='font-size:12px;color:white;'>"
        "【演算法解说】：该词在当前群体中出现的几率是另一群体的 "
        "%{customdata[2]:.1f} 倍。OR值越高，代表史官对该群体的"
        "特异性道德定性越强，在双螺旋中耸立得越高。"
        "</span>"
        "<extra></extra>"
    )

    # 散点样式：常显文本，字体大小 11；强制浮窗文字全白
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

    # —— 网页底部常显学术说明（Layout Annotation） ——
    annotation_text = (
        "<b>计量历史学方法论注：</b>"
        "本全息图采用圆柱坐标系（Cylindrical Coordinates）构建双螺旋结构。"
        "X/Y轴为原始词频经圆周映射后的立体坐标，"
        "Z轴为几率比权重（Odds Ratio）的对数压缩轴。"
        "几率比不看绝对词频，而是计算词汇在两组文本中出现几率的相对倍数关系，"
        "旨在精确捕捉《明史》史官对忠奸群体的排他性刻板印象与二元对立叙事。"
        "双螺旋顶端即为核心专属标签。"
    )

    # 坐标轴学术命名 + 批注卡片
    fig.update_layout(
        scene=dict(
            xaxis=dict(title=dict(text="圆柱面 X 坐标 (cosθ)"),
                       backgroundcolor="rgba(245,245,250,0.9)",
                       gridcolor="#cccccc", showbackground=True),
            yaxis=dict(title=dict(text="圆柱面 Y 坐标 (sinθ)"),
                       backgroundcolor="rgba(245,245,250,0.9)",
                       gridcolor="#cccccc", showbackground=True),
            zaxis=dict(title=dict(text="几率比显著度 (对数压缩轴)"),
                       backgroundcolor="rgba(245,245,250,0.9)",
                       gridcolor="#cccccc", showbackground=True),
            camera=dict(eye=dict(x=1.4, y=1.4, z=1.1)),
            aspectmode="cube",
        ),
        legend=dict(title=dict(text="群体标签"),
                    font=dict(family=CJK_FONT, size=12)),
        title_font=dict(family=CJK_FONT, size=18),
        margin=dict(l=20, r=20, t=120, b=180),
        annotations=[
            dict(
                text=annotation_text,
                showarrow=False,
                xref="paper", yref="paper",
                x=0.5, y=-0.32,
                xanchor="center", yanchor="top",
                align="left",
                font=dict(family=CJK_FONT, size=12, color="#333"),
                bordercolor="#bbbbbb",
                borderpad=10,
                bgcolor="rgba(248,248,252,0.95)",
                borderwidth=1,
            ),
        ],
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
