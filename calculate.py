import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'WenQuanYi Micro Hei']
plt.rcParams['axes.unicode_minus'] = False
print("正在读取 curve_design.xlsx ...")
df = pd.read_excel('curve_design.xlsx', sheet_name=0)
exp_needed = df['最终经验'].tolist() 
print(f"读取成功，共 {len(exp_needed)} 级数据")
print(f"1级升2级需要: {exp_needed[0]} 经验")
print(f"89级升90级需要: {exp_needed[-1]} 经验")

def simulate(daily_exp, name, max_days=365):
    level = 1           # 当前等级
    current_exp = 0     # 当前等级已获得的经验
    history = []        # 记录每天的等级
    
    for day in range(1, max_days + 1):
        current_exp += daily_exp
        
        # 检查是否可以升级（可能一天升多级）
        while level < 90 and current_exp >= exp_needed[level-1]:
            current_exp -= exp_needed[level-1]
            level += 1
            history.append({'day': day, 'level': level-1})
            
            if level == 90:
                break
        
        # 记录每天的等级（用于后续分析）
        history.append({'day': day, 'level': level})
        
        if level == 90:
            print(f"{name} 在第 {day} 天满级！")
            break
    
    # 转换为DataFrame
    df_result = pd.DataFrame(history)
    return df_result

players = [
    {"name": "零氪党", "daily_exp": 3000},      # 每天3000经验
    {"name": "月卡党", "daily_exp": 6000},      # 每天6000经验
    {"name": "双月卡党", "daily_exp": 8000},    # 每天8000经验
]

results = {}
for player in players:
    print(f"\n正在模拟 {player['name']} ...")
    df = simulate(player["daily_exp"], player["name"])
    results[player["name"]] = df
    filename = f"{player['name']}_升级记录.csv"
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"已保存: {filename}")

plt.figure(figsize=(12, 7))
colors = ['blue', 'green', 'red']
for i, (name, df) in enumerate(results.items()):
    daily_level = df.drop_duplicates(subset=['day'], keep='last')
    plt.plot(daily_level['day'], daily_level['level'], 
             label=name, color=colors[i], linewidth=2, marker='', alpha=0.8)

plt.xlabel('天数', fontsize=12)
plt.ylabel('等级', fontsize=12)
plt.title('不同付费玩家升级曲线对比', fontsize=14)
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.ylim(0, 95)
plt.xlim(0, 200)

# 标注软卡点区间（60-80级）
plt.axhspan(60, 80, alpha=0.2, color='orange', label='软卡点区间(60-80级)')
plt.text(5, 70, '软卡点区间\n60-80级', fontsize=10, color='orange', alpha=0.7)

plt.tight_layout()
plt.savefig('升级曲线对比图.png', dpi=150, bbox_inches='tight')
print("\n 图表已保存: 升级曲线对比图.png")
plt.show()

# ========== 6. 分析各等级停留天数 ==========
print("\n" + "="*50)
print("各等级平均停留天数分析：")
print("="*50)

stay_analysis = {}
for name, df in results.items():
    # 计算每个等级停留了多少天
    level_stay = {}
    prev_day = 0
    prev_level = 1
    
    for _, row in df.iterrows():
        if row['level'] != prev_level:
            days_stayed = row['day'] - prev_day
            level_stay[prev_level] = days_stayed
            prev_day = row['day']
            prev_level = row['level']
    
    stay_analysis[name] = level_stay
    
    print(f"\n【{name}】")
    # 输出关键等级的停留天数
    for level in [30, 50, 60, 70, 80]:
        if level in level_stay:
            print(f"  停留在 {level} 级: {level_stay[level]} 天")
    # 计算60-80级总停留时间
    stay_60_80 = sum(level_stay.get(l, 0) for l in range(60, 81))
    total_days = df['day'].max()
    if total_days > 0:
        ratio = stay_60_80 / total_days * 100
        print(f"  60-80级总停留: {stay_60_80} 天 (占总升级时间 {ratio:.1f}%)")

# ========== 7. 生成停留天数热力图数据 ==========
# 为后续热力图准备数据
heatmap_data = []
for name in players:
    name_key = name["name"]
    if name_key in stay_analysis:
        level_stays = []
        for level in range(1, 91):
            level_stays.append(stay_analysis[name_key].get(level, 0))
        heatmap_data.append(level_stays)

# 保存热力图数据
heatmap_df = pd.DataFrame(heatmap_data, 
                           index=[p["name"] for p in players],
                           columns=[f"Lv{i}" for i in range(1, 91)])
heatmap_df.to_csv('停留天数_热力图数据.csv', encoding='utf-8-sig')
print("\n   停留天数数据已保存: 停留天数_热力图数据.csv")

print("\n   模拟完成！生成的文件：")
print("   - 各玩家_升级记录.csv (详细升级日志)")
print("   - 升级曲线对比图.png (升级曲线图)")
print("   - 停留天数_热力图数据.csv (各等级停留天数)")
