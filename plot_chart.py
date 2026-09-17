# -*- coding: utf-8 -*-
"""
读取 analysis_result.csv，绘制忠臣 vs 奸臣 特征词几率比对比水平条形图（学术级）。
================================================================
运行前请先安装依赖：
    pip install matplotlib pandas requests

运行：
    python plot_chart.py

输出：
    ./analysis_chart.png  （DPI=300 高清静默落盘）
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
OUT_PNG = os.path.join(BASE_DIR, "analysis_chart.png")
FONT_PATH = os.path.join(BASE_DIR, "NotoSansSC-Regular.otf")

# 思源黑体（Noto Sans SC）多备选直链——任一直链下载成功即可
FONT_URLS = [
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
    # 标准化列名（防止 BOM / 空白）
    df.columns = [c.strip() for c in df.columns]
    return df


# ----------------------------------------------------------------------
# 3. 学术级水平条形图（1x2 双面板对比）
# ----------------------------------------------------------------------
def plot(df: pd.DataFrame, font_path: str):
    fp = fm.FontProperties(fname=font_path)
    plt.rcParams["axes.unicode_minus"] = False

    # 分组：忠臣 / 奸臣
    loyal = df[df["群体标签"].str.contains("忠")].copy()
    traitor = df[df["群体标签"].str.contains("奸")].copy()

    # Y 轴降序：权重最高在最上方 → barh 需 ascending=True（自下而上）
    loyal = loyal.sort_values("几率比权重", ascending=True).tail(15)
    traitor = traitor.sort_values("几率比权重", ascending=True).tail(15)

    fig, axes = plt.subplots(1, 2, figsize=(16, 9))
    plt.subplots_adjust(left=0.10, right=0.96, top=0.90, bottom=0.08, wspace=0.45)

    # —— 左：忠臣（深蓝） ——
    ax = axes[0]
    ax.barh(loyal["词语"], loyal["几率比权重"],
            color=COLOR_LOYAL, edgecolor="#1d3a5f", height=0.65)
    xmax = loyal["几率比权重"].max()
    for i, (v, fz) in enumerate(zip(loyal["几率比权重"], loyal["忠臣组频数"])):
        ax.text(v + xmax * 0.012, i, f"{v:.2f} (n={fz})",
                va="center", ha="left", fontproperties=fp, fontsize=9, color="#333")
    ax.set_title("忠臣特征词  Top 15\n（几率比高 → 忠臣独有）",
                 fontproperties=fp, fontsize=14, fontweight="bold")
    ax.set_xlabel("Odds Ratio", fontproperties=fp, fontsize=11)
    ax.set_ylabel("特征词语", fontproperties=fp, fontsize=11)
    ax.set_yticklabels(loyal["词语"], fontproperties=fp, fontsize=11)
    ax.axvline(0, color="gray", lw=0.6, ls="-")
    ax.grid(axis="x", ls="--", alpha=0.35)
    ax.set_xlim(0, xmax * 1.18)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    # —— 右：奸臣（深红） ——
    ax = axes[1]
    ax.barh(traitor["词语"], traitor["几率比权重"],
            color=COLOR_TRAITOR, edgecolor="#7a2424", height=0.65)
    xmax = traitor["几率比权重"].max()
    for i, (v, fz) in enumerate(zip(traitor["几率比权重"], traitor["奸臣组频数"])):
        ax.text(v + xmax * 0.012, i, f"{v:.2f} (n={fz})",
                va="center", ha="left", fontproperties=fp, fontsize=9, color="#333")
    ax.set_title("奸臣特征词  Top 15\n（几率比高 → 奸臣独有）",
                 fontproperties=fp, fontsize=14, fontweight="bold")
    ax.set_xlabel("Odds Ratio", fontproperties=fp, fontsize=11)
    ax.set_ylabel("特征词语", fontproperties=fp, fontsize=11)
    ax.set_yticklabels(traitor["词语"], fontproperties=fp, fontsize=11)
    ax.axvline(0, color="gray", lw=0.6, ls="-")
    ax.grid(axis="x", ls="--", alpha=0.35)
    ax.set_xlim(0, xmax * 1.18)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    # 总标题
    fig.suptitle("《明史》忠臣 vs 奸臣  特征词几率比（Odds Ratio）对比",
                 fontproperties=fp, fontsize=16, fontweight="bold")

    plt.tight_layout(rect=[0, 0, 1, 0.95])
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
