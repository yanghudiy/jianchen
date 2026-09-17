# -*- coding: utf-8 -*-
"""
方案二（数据内生维度模型）：读取 analysis_result.csv，绘制三维立体投影散点图。
===============================================================
X 轴：奸臣组频数（奸臣叙事中的普遍性）
Y 轴：忠臣组频数（忠臣叙事中的普遍性）
Z 轴：几率比权重（Odds Ratio，词汇的群体特异性显著度）

运行前请先安装依赖：
    pip install matplotlib pandas requests

运行：
    python plot_3d_chart.py

输出：
    ./analysis_3d_projection.png  （DPI=300 高清静默落盘）
"""

import os
import io
import requests
import matplotlib
matplotlib.use("Agg")  # 无 GUI 后端，确保静默落盘
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd

# ----------------------------------------------------------------------
# 路径与配置
# ----------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "analysis_result.csv")
OUT_PNG = os.path.join(BASE_DIR, "analysis_3d_projection.png")
FONT_PATH = os.path.join(BASE_DIR, "NotoSansSC-Regular.otf")

# 思源黑体（Noto Sans SC）多备选直链——任一直链下载成功即可
FONT_URLS = [
    "https://githubusercontent.com",
    "https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/OTF/SimplifiedChinese/NotoSansSC-Regular.otf",
    "https://github.com/googlefonts/noto-cjk/raw/main/Sans/SubsetOTF/SC/NotoSansSC-Regular.otf",
    "https://mirrors.tuna.tsinghua.edu.cn/github-release/notofonts/noto-cjk/Sans/OTF/SimplifiedChinese/NotoSansSC-Regular.otf",
]
# 系统已装 CJK 字体（兜底）
SYSTEM_FONTS = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
]

# 学术级配色
COLOR_LOYAL = "#2b5c8f"     # 忠臣——深蓝
COLOR_TRAITOR = "#b83b3b"   # 奸臣——深红


# ----------------------------------------------------------------------
# 1. 无痕中文字体下载（防乱码核心）
# ----------------------------------------------------------------------
def ensure_font() -> str:
    """优先用已下载字体 → 网络下载 → 系统已装 CJK 字体。"""
    # 1) 本地已存在且体积正常
    if os.path.exists(FONT_PATH) and os.path.getsize(FONT_PATH) > 1_000_000:
        return FONT_PATH
    # 2) 网络下载（多备选直链，依次尝试）
    for url in FONT_URLS:
        try:
            resp = requests.get(url, timeout=60,
                                headers={"User-Agent": "curl/8.0"})
            if resp.status_code == 200 and len(resp.content) > 1_000_000:
                with open(FONT_PATH, "wb") as f:
                    f.write(resp.content)
                return FONT_PATH
        except Exception:
            continue
    # 3) 系统已装字体兜底
    for sf in SYSTEM_FONTS:
        if os.path.exists(sf):
            return sf
    raise RuntimeError("无法获取任何中文字体，图表中文将乱码")


# ----------------------------------------------------------------------
# 2. 读取 CSV
# ----------------------------------------------------------------------
def read_result(path: str) -> pd.DataFrame:
    """
    CSV 列：词语,奸臣组频数,忠臣组频数,几率比权重,群体标签
    群体标签取值：奸臣特征 / 忠臣特征
    """
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]
    return df


# ----------------------------------------------------------------------
# 3. 三维立体投影散点图
# ----------------------------------------------------------------------
def plot(df: pd.DataFrame, font_path: str):
    fp = fm.FontProperties(fname=font_path)
    plt.rcParams["axes.unicode_minus"] = False

    # 分组：忠臣 / 奸臣
    loyal = df[df["群体标签"].str.contains("忠")].copy()
    traitor = df[df["群体标签"].str.contains("奸")].copy()

    # 各取权重前 15
    loyal = loyal.sort_values("几率比权重", ascending=False).head(15)
    traitor = traitor.sort_values("几率比权重", ascending=False).head(15)

    fig = plt.figure(figsize=(14, 11))
    ax = fig.add_subplot(111, projection="3d")

    # —— 忠臣（深蓝圆点） ——
    lx = loyal["奸臣组频数"].values
    ly = loyal["忠臣组频数"].values
    lz = loyal["几率比权重"].values
    ax.scatter(lx, ly, lz, c=COLOR_LOYAL, marker="o", s=60,
               edgecolors="#1d3a5f", linewidths=0.5, label="忠臣特征词")

    # —— 奸臣（深红圆点） ——
    tx = traitor["奸臣组频数"].values
    ty = traitor["忠臣组频数"].values
    tz = traitor["几率比权重"].values
    ax.scatter(tx, ty, tz, c=COLOR_TRAITOR, marker="o", s=60,
               edgecolors="#7a2424", linewidths=0.5, label="奸臣特征词")

    # 计算坐标范围，用于偏移防重叠
    all_x = list(lx) + list(tx)
    all_y = list(ly) + list(ty)
    all_z = list(lz) + list(tz)
    max_x = max(all_x) if all_x else 1
    max_y = max(all_y) if all_y else 1
    max_z = max(all_z) if all_z else 1

    # —— 文字悬浮标签：忠臣 ——
    for x, y, z, word in zip(lx, ly, lz, loyal["词语"].values):
        ax.text(x + max_x * 0.01, y + max_y * 0.01, z + max_z * 0.01,
                word, fontproperties=fp, fontsize=8, color=COLOR_LOYAL)

    # —— 文字悬浮标签：奸臣 ——
    for x, y, z, word in zip(tx, ty, tz, traitor["词语"].values):
        ax.text(x + max_x * 0.01, y + max_y * 0.01, z + max_z * 0.01,
                word, fontproperties=fp, fontsize=8, color=COLOR_TRAITOR)

    # —— 坐标轴中文标签 ——
    ax.set_xlabel("奸臣文本频数", fontproperties=fp, fontsize=12,
                  labelpad=10, color="#333")
    ax.set_ylabel("忠臣文本频数", fontproperties=fp, fontsize=12,
                  labelpad=10, color="#333")
    ax.set_zlabel("几率比权重(Odds Ratio)", fontproperties=fp, fontsize=12,
                  labelpad=10, color="#333")

    # —— 标题与图例 ——
    ax.set_title("《明史》忠臣 vs 奸臣 特征词三维立体投影\n"
                 "（数据内生维度模型：奸臣频数 × 忠臣频数 × 几率比权重）",
                 fontproperties=fp, fontsize=15, fontweight="bold",
                 pad=18, color="#222")

    legend = ax.legend(prop=fp, fontsize=11, loc="upper left",
                       frameon=True, framealpha=0.9)

    # —— 立体背景网格 ——
    ax.grid(True)
    ax.xaxis._axinfo["grid"].update({"color": "#cccccc", "linestyle": "--",
                                     "alpha": 0.45, "linewidth": 0.6})
    ax.yaxis._axinfo["grid"].update({"color": "#cccccc", "linestyle": "--",
                                     "alpha": 0.45, "linewidth": 0.6})
    ax.zaxis._axinfo["grid"].update({"color": "#cccccc", "linestyle": "--",
                                     "alpha": 0.45, "linewidth": 0.6})

    # 设置背景面板为浅色，增强立体感
    ax.xaxis.set_pane_color((0.96, 0.96, 0.98, 1.0))
    ax.yaxis.set_pane_color((0.96, 0.96, 0.98, 1.0))
    ax.zaxis.set_pane_color((0.96, 0.96, 0.98, 1.0))

    # —— 优化 3D 视角 ——
    ax.view_init(elev=20, azim=45)

    # 静默高清落盘
    fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------------------------
# 4. 主流程
# ----------------------------------------------------------------------
def main():
    font_path = ensure_font()
    df = read_result(CSV_PATH)
    plot(df, font_path)


if __name__ == "__main__":
    main()
