import requests
import json
import random

def call_zhipu_api(messages, model="glm-4.6"):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
 

    headers = {
        "Authorization": "959c4609a8174cd8bcf98f464808e058.iMOFk1hUsmK7WNij",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": 1.0
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API调用失败: {response.status_code}, {response.text}")

# 游戏设置
role_system = ["老虎", "狮子", "豹", "猎豹", "雪豹"]
current_role = random.choice(role_system)

# 系统提示词
game_system = f"""你正在玩"动物猜猜猜"游戏。你的身份是：{current_role}

游戏规则：
1. 用户会通过提问来猜测你是什么动物（可能是：老虎、狮子、豹、猎豹、雪豹中的一种）
2. 你要通过描述自己的外貌特征、生活习性、栖息环境、特殊能力、饮食习惯等特征来暗示，但绝对不能直接说出"{current_role}"这个词
3. 不要直接回答"是"或"否"，而是通过描述动物特征让用户自己判断
4. 不要说"我不是XX"这种直接否定，而是用"我更喜欢..."或"我通常..."来描述
5. 不要提及其他可能的动物选项
6. 当用户准确说出"{current_role}"这个词时，你只回复"再见"来结束游戏
7. 保持神秘感和趣味性，可以用一些有趣的动物特征来暗示，比如特殊的行为、有趣的外貌、独特的能力等
8. 注意：这5种动物都是大型猫科动物，有很多相似之处，但你要通过细节特征来区分，比如体型大小、栖息地、花纹、速度、生活习性等

回答示例：
- 如果你是"老虎"，用户问"你生活在草原上吗？"
  好的回答："我更喜欢生活在森林、草原和湿地等多样化的环境中，我身上有独特的条纹，是独居的动物..."
  坏的回答："不是，我是老虎" 或 "我不在草原，我是老虎"

- 如果你是"猎豹"，用户问"你跑得快吗？"  
  好的回答："我是陆地上跑得最快的动物，短距离内可以达到非常高的速度，但我无法长时间保持高速，而且我身上有独特的黑色泪痕..."
  坏的回答："快，我是猎豹" 或 "我是最快的，我是猎豹"

- 如果你是"雪豹"，用户问"你生活在热带吗？"
  好的回答："我生活在高海拔的寒冷山区，我的毛很厚，有很好的保暖性，而且我身上有独特的斑点，适合在雪地中隐藏..."
  坏的回答："不是热带，我是雪豹"

现在开始游戏，用户会开始提问。保持角色，通过描述动物特征来暗示，不要直接否定或肯定。"""

# 维护对话历史
conversation_history = [
    {"role": "system", "content": game_system}
]

# 多轮对话循环
while True:
    user_input = input("请输入你要说的话：")
    
    # 添加用户消息到历史
    conversation_history.append({"role": "user", "content": user_input})
    
    # 调用API
    result = call_zhipu_api(conversation_history)
    assistant_reply = result['choices'][0]['message']['content']
    
    # 添加助手回复到历史
    conversation_history.append({"role": "assistant", "content": assistant_reply})
    
    # 打印回复
    print(assistant_reply)
    
    # 检查是否猜对（模型回复"再见"）
    if "再见" in assistant_reply:
        print(f"\n游戏结束！正确答案是：{current_role}")
        break