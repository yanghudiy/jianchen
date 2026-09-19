import jieba
from collections import Counter
import re

print("【🚀本地系統提示】: 正在啟動【明史雙組25詞擴容版】演算法...")

# 1. 注入強規制語義詞網，確保核心行為詞不被切碎
core_words = ['力諫', '死節', '抗疏', '專權', '弄權', '結黨', '納賄', '進讒', '構陷', '篡逆']
for word in core_words:
    jieba.add_word(word, freq=50000)

# 2. AI 精細化雜質黑名單（僅精準剔除人名簡稱、冷門人名、地理與中性時間噪點）
ai_filtered_blacklist = {
    '延儒', '體仁', '大鋮', '士英', '迎祥', '世蕃', '謙益', '嚴嵩', '馮銓', '廣微', 
    '惟庸', '承疇', '呈秀', '良玉', '維華', '慎言', '莊烈帝', '魯生', '真人', '客氏',
    '陝西', '中外', '大喜', '白金', '帝益', '道行', '論死', '我兵', '薄城', '民兵',
    '之', '乎', '者', '也', '矣', '焉', '而', '其', '以', '於', '則', '何', '如', '此',
    '帝', '曰', '人', '官', '書', '中', '年', '月', '日', '時', '事', '後', '前', '至', '自'
}

# 嚴格清洗非漢字字符（標點、數字等）
punctuation_clean = re.compile(r'[^\u4e00-\u9fa5]')

def process_file_expanded(filepath):
    print(f"【📊系統提示】: 正在流式掃描文本: {filepath}")
    counter = Counter()
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        while True:
            chunk = f.read(500)
            if not chunk:
                break
            raw_words = jieba.cut(chunk.strip())
            for word in raw_words:
                w = punctuation_clean.sub('', word).strip()
                if len(w) < 2 or w in ai_filtered_blacklist:
                    continue
                counter[w] += 1
    return counter

try:
    # 🚨 這裡已經徹底移除了 is_jianchen 篩選網，允許名詞與動詞自然並存
    jian_counts = process_file_expanded('./jianchen.txt')
    zhong_counts = process_file_expanded('./zhongchen.txt')
except Exception as e:
    print(f"【⚠️本地錯誤】: 讀取文件失敗。錯誤: {e}")
    exit()

print("【💡系統提示】: 開始計算幾率比 (Odds Ratio)...")
total_jian = sum(jian_counts.values())
total_zhong = sum(zhong_counts.values())
all_words = set(jian_counts.keys()).union(set(zhong_counts.keys()))
results = []

for word in all_words:
    f_jian = jian_counts.get(word, 0)
    f_zhong = zhong_counts.get(word, 0)
    p_jian = (f_jian + 0.5) / (total_jian + 1.0)
    p_zhong = (f_zhong + 0.5) / (total_zhong + 1.0)
    results.append({
        'word': word, 'f_jian': f_jian, 'f_zhong': f_zhong,
        'or_jian': p_jian / p_zhong, 'or_zhong': p_zhong / p_jian
    })

# 🚨 【核心擴容點】：兩組各取前 25 個最顯著的特徵詞（總共 50 個詞）
top_jian = sorted(results, key=lambda x: x['or_jian'], reverse=True)[:25]
top_zhong = sorted(results, key=lambda x: x['or_zhong'], reverse=True)[:25]

print("【📝系統提示】: 正在寫入 `./analysis_result.csv`...")
with open('./analysis_result.csv', 'w', encoding='utf-8') as f:
    f.write("詞語,奸臣組頻數,忠臣組頻數,幾率比權重,群體標籤\n")
    for item in top_jian:
        f.write(f"{item['word']},{item['f_jian']},{item['f_zhong']},{item['or_jian']:.4f},奸臣特徵\n")
    for item in top_zhong:
        f.write(f"{item['word']},{item['f_jian']},{item['f_zhong']},{item['or_zhong']:.4f},忠臣特徵\n")

print("【🎉大功告成】: 25 詞擴容並存版數據已成功落盤至 `./analysis_result.csv`！")
