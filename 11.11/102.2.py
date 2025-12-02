import random

# 随机选择答案
target_number = random.randint(1, 50)

print("数字猜测游戏开始！")
print("我会随机选择一个1-50之间的整数，你有5次猜测机会。\n")

# 游戏主循环
min_range, max_range = 1, 50
guessed_numbers = []
round_count = 0

while round_count < 5:
    round_count += 1
    remaining = 6 - round_count
    
    # 获取用户输入
    try:
        guessed_number = int(input(f"【第{round_count}回合，剩余{remaining}次机会】请输入数字（1-50）："))
        if not 1 <= guessed_number <= 50:
            print("❌ 请输入1-50之间的整数！")
            round_count -= 1
            continue
    except ValueError:
        print("❌ 请输入有效数字！")
        round_count -= 1
        continue
    
    # 检查重复
    if guessed_number in guessed_numbers:
        print(f"❌ 你已经猜过{guessed_number}了！")
        round_count -= 1
        continue
    
    guessed_numbers.append(guessed_number)
    
    # 判断结果
    if guessed_number == target_number:
        print(f"\n🎉 恭喜！答案就是：{target_number}！你用了{round_count}回合。")
        break
    
    # 更新范围
    if guessed_number < target_number:
        min_range = max(min_range, guessed_number + 1)
        hint = "太小了"
    else:
        max_range = min(max_range, guessed_number - 1)
        hint = "太大了"
    
    print(f"💡 {hint}，答案在{min_range}-{max_range}之间")

# 游戏结束
if guessed_numbers and guessed_numbers[-1] != target_number:
    print(f"\n游戏结束！正确答案是：{target_number}")
    print(f"你猜过的数字：{guessed_numbers}")
