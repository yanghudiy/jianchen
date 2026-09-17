import jieba
from collections import Counter

print("【🚀系统提示】: 正在初始化【分批流式切块版】配置...")

dirty_words = {
    '体仁', '大英', '温体仁', '严嵩', '魏忠贤', '客氏', '王振', '刘瑾', '汪直', '江彬', 
    '钱宁', '严世蕃', '周延儒', '马士英', '阮大铖', '帝', '曰', '人', '官', '书', 
    '太祖', '成祖', '朝', '廷', '明', '洪武', '永乐', '嘉靖', '万历', '天启', '崇祯',
    '之', '乎', '者', '也', '矣', '焉', '而', '其', '以', '于', '则', '何', '如', '此',
    '中', '年', '月', '日', '时', '事', '后', '前', '至', '自', '因', '遂', '乃', '即',
    # 繁体适配：同名同义繁体形态一并进行清洗
    '體仁', '大英', '溫體仁', '嚴嵩', '魏忠賢', '客氏', '王振', '劉瑾', '汪直', '江彬',
    '錢寧', '嚴世蕃', '周延儒', '馬士英', '阮大鋮', '帝', '曰', '人', '官', '書',
    '太祖', '成祖', '朝', '廷', '明', '洪武', '永樂', '嘉靖', '萬曆', '天啟', '崇禎',
    '於', '則', '為', '時', '後', '從', '與', '乃',
    # 上一次执行遗留、无法洗干净的 dirty words（简体 + 繁体 双形态）
    # 人名片段（人名残缺形态）
    '惟庸', '馮銓', '冯铨', '嚴嵩', '严嵩', '廣微', '广微', '承疇', '承畴', '良玉',
    '延儒', '大鋮', '大铖', '士英', '迎祥', '文華', '文华', '世蕃', '魯生', '鲁生',
    '謙益', '谦益', '維華', '维华', '呈秀',
    # 官职 / 头衔 / 机构
    '太師', '太师', '太傅', '太常', '言官', '訓導', '训导', '貢生', '贡生',
    '鄉官', '乡官', '上官', '校尉',
    # 常见行为 / 状态词（描述性噪声）
    '帝益', '白金', '道行', '論死', '论死', '大罵', '大骂',
    '城破', '城陷', '被執', '被执', '支解', '自焚', '共守', '並死', '并死',
    '抗節', '抗节', '贈光祿', '赠光禄', '舉於鄉', '举于乡',
}

def clean_and_count_safe(filepath):
    print(f"【📊系统提示】: 正在极速流式读取文本: {filepath}")
    counter = Counter()
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        # 核心改进：限制每次只读取 300 个字的小片段，绝不让 jieba 计算超大拓扑图
        while True:
            chunk = f.read(300)
            if not chunk:
                break
                
            # 分批处理小片段，速度会提升成百上千倍
            raw_words = jieba.cut(chunk.strip())
            for word in raw_words:
                if len(word) < 2 or word in dirty_words:
                    continue
                counter[word] += 1
                
    print(f"   -> {filepath} 过滤与分词计数成功！")
    return counter

# 执行极速安全分词
try:
    jian_counts = clean_and_count_safe('./明史奸臣、流贼.txt')
    zhong_counts = clean_and_count_safe('./明史忠义.txt')
except Exception as e:
    print(f"【⚠️报错】: 读取文件失败。错误: {e}")
    exit()

print("【💡系统提示】: 开始线性计算几率比 (Odds Ratio)...")
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

# 顽固人名黑名单，在最后的特征提取中直接硬性拦截（简体 + 繁体双形态）
stubborn_names = {
    '崔呈秀', '冯铨', '馮銓', '周延儒', '陈演', '陳演', '谢升', '謝升',
    '魏广微', '魏廣微', '顾秉谦', '顧秉謙', '温体仁', '溫體仁', '张大英', '張大英',
    '霍轁', '夏言', '严世蕃', '嚴世蕃', '徐阶', '徐階', '高拱', '张居正', '張居正',
    '申时行', '申時行', '王锡爵', '王錫爵', '沈一贯', '沈一貫',
    '严嵩', '嚴嵩', '胡惟庸', '胡惟庸', '洪承畴', '洪承疇', '左良玉', '左良玉',
} 

top_jian = []
sorted_jian = sorted(results, key=lambda x: x['or_jian'], reverse=True)
for item in sorted_jian:
    if len(top_jian) >= 15:
        break
    if item['word'] in stubborn_names:
        continue
    top_jian.append(item)

top_zhong = []
sorted_zhong = sorted(results, key=lambda x: x['or_zhong'], reverse=True)
for item in sorted_zhong:
    if len(top_zhong) >= 15:
        break
    if item['word'] in stubborn_names:
        continue
    top_zhong.append(item)

print("【📝系统提示】: 正在写入 ./analysis_result.csv...")
with open('./analysis_result.csv', 'w', encoding='utf-8') as f:
    f.write("词语,奸臣组频数,忠臣组频数,几率比权重,群体标签\n")
    for item in top_jian:
        f.write(f"{item['word']},{item['f_jian']},{item['f_zhong']},{item['or_jian']:.4f},奸臣特征\n")
    for item in top_zhong:
        f.write(f"{item['word']},{item['f_jian']},{item['f_zhong']},{item['or_zhong']:.4f},忠臣特征\n")

print("【🎉大功告成】: 脚本已完美运行结束！请立刻查看 `./analysis_result.csv` 文件！")