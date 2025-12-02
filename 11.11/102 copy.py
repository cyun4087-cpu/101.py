import requests
import json
import random

from requests.utils import stream_decode_response_unicode

# 尝试导入TTS功能，如果失败则使用空函数
try:
    from xunfei_tts import text_to_speech
    TTS_AVAILABLE = True
except ImportError as e:
    # 如果导入失败，定义一个空函数
    TTS_AVAILABLE = False
    def text_to_speech(text):
        pass  # 不执行任何操作
    print(f"警告: TTS模块导入失败，语音功能将不可用: {e}")
except Exception as e:
    TTS_AVAILABLE = False
    def text_to_speech(text):
        pass
    print(f"警告: TTS模块加载出错，语音功能将不可用: {e}") 

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

    # 禁用代理，直接连接
    response = requests.post(url, headers=headers, json=data, proxies={"http": None, "https": None}, timeout=30)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API调用失败: {response.status_code}, {response.text}")

# 角色列表：每个角色包含名字、特征和背景
characters = [
    {
        "name": "老管家",
        "description": "一个年迈的管家，说话缓慢，总是回忆过去。他声称案发时在整理书房。",
        "clue": "他的袖口有血迹，但他说是整理旧书时划伤的。"
    },
    {
        "name": "女仆小思",
        "description": "年轻的女仆，说话紧张，眼神闪烁。她声称案发时在厨房准备晚餐。",
        "clue": "她手上有一个奇怪的印记，但她说是被热水烫伤的。"
    },
    {
        "name": "神秘访客",
        "description": "一个陌生的访客，说话含糊不清，总是回避问题。他声称是来拜访主人的。",
        "clue": "他的衣服上有泥土，但他无法解释为什么。"
    },
    {
        "name": "园丁老王",
        "description": "老实的园丁，说话直接，看起来很紧张。他声称案发时在花园修剪植物。",
        "clue": "他的工具少了一把，但他不记得放在哪里了。"
    }
]

# 随机选择真凶
true_ghost = random.choice(characters)
ghost_name = true_ghost["name"]

# 游戏开始提示
print("=" * 50)
print("🔍 抓幽灵游戏开始！")
print("=" * 50)
print(f"在一个古老的宅邸中，发生了一起神秘事件。")
print(f"有{len(characters)}个嫌疑人，其中一个是真凶（幽灵附身）。")
print("你可以向任何角色提问，找出真凶！")
print("提示：真凶会撒谎或露出破绽，其他角色会说真话。")
print("当你确定真凶时，可以说：'真凶是XXX'")
print("=" * 50)
print("\n角色列表：")
for i, char in enumerate(characters, 1):
    print(f"{i}. {char['name']} - {char['description']}")
print("=" * 50)

# 游戏主循环
while True:
    user_input = input("\n请输入你的问题或猜测（格式：'问XXX：...' 或 '真凶是XXX'）：")
    
    # 检查是否是猜测真凶
    if "真凶是" in user_input or "凶手是" in user_input:
        # 提取猜测的名字
        guessed_name = None
        for char in characters:
            if char["name"] in user_input:
                guessed_name = char["name"]
                break
        
        if guessed_name:
            # 判断是否正确
            judge_prompt = f"""你是一个游戏裁判。在这个抓幽灵游戏中，真凶是：{ghost_name}。
用户猜测真凶是：{guessed_name}。
如果用户猜对了（{guessed_name} == {ghost_name}），请回复："恭喜！你找到了真凶！游戏结束！"
如果用户猜错了，请回复："不对，继续调查吧。"
只回复判断结果，不要有其他内容。"""
            
            messages = [{"role": "user", "content": judge_prompt}]
            result = call_zhipu_api(messages)
            assistant_reply = result['choices'][0]['message']['content']
            print(f"\n🎯 {assistant_reply}")
            if TTS_AVAILABLE:
                try:
                    text_to_speech(assistant_reply)
                except Exception as e:
                    print(f"TTS播放失败: {e}")
            
            if "恭喜" in assistant_reply or "游戏结束" in assistant_reply:
                print(f"\n真凶就是：{ghost_name}！")
                print(f"线索：{true_ghost['clue']}")
                break
        else:
            print("请明确说出角色的名字，例如：'真凶是老管家'")
    
    else:
        # 普通提问，需要指定角色
        current_character = None
        question = user_input
        
        # 检查用户是否指定了角色
        for char in characters:
            if char["name"] in user_input:
                current_character = char
                # 提取问题部分（去掉角色名）
                question = user_input.replace(f"问{char['name']}：", "").replace(f"问{char['name']}", "").replace(char['name'], "").strip()
                break
        
        if current_character:
            # 构建角色扮演的prompt
            is_ghost = (current_character["name"] == ghost_name)
            role_prompt = f"""你正在扮演角色：{current_character['name']}
角色描述：{current_character['description']}
线索：{current_character['clue']}

重要规则：
- 如果这个角色是真凶（{'是' if is_ghost else '不是'}），真凶会撒谎、回避问题或露出破绽。
- 如果这个角色不是真凶，他会说真话，但可能不知道全部信息。
- 用第一人称回答，保持角色特征。
- 回答要简短，符合角色性格。

用户的问题：{question}
请以{current_character['name']}的身份回答："""
            
            messages = [{"role": "user", "content": role_prompt}]
            result = call_zhipu_api(messages)
            assistant_reply = result['choices'][0]['message']['content']
            print(f"\n{current_character['name']}：{assistant_reply}")
            if TTS_AVAILABLE:
                try:
                    text_to_speech(assistant_reply)
                except Exception as e:
                    print(f"TTS播放失败: {e}")
        else:
            print("请指定要提问的角色，格式：'问XXX：你的问题'")
            print("例如：'问老管家：案发时你在哪里？'")