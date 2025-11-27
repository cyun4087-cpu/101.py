import requests
import json

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

# 使用示例
role_system = "你是一个疯狂的小丑。你可以在适当的时候（比如对话自然结束、用户表示要离开、或者你觉得对话已经完成时）回复'再见'来结束对话。"
# 维护对话历史
conversation_history = [
    {"role": "system", "content": role_system}
]

# 多轮对话循环，直到AI回复 '再见' 结束
while True:  # 表示"当条件为真时一直循环"。由于 True 永远为真，这个循环会一直运行，直到遇到 break 才会停止。
    user_input = input("请输入你要说的话：")
    
    # 添加用户消息到对话历史
    conversation_history.append({"role": "user", "content": user_input})
    
    # 调用API
    result = call_zhipu_api(conversation_history)
    ai_response = result['choices'][0]['message']['content']
    
    # 添加AI回复到对话历史
    conversation_history.append({"role": "assistant", "content": ai_response})
    
    # 打印AI回复
    print(ai_response)
    
    # 检测AI是否回复"再见"来结束对话
    if "再见" in ai_response:
        print("对话结束。")
        break