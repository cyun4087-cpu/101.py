from api import call_zhipu_api
from roles import get_break_rules


def chat_once(history, user_input, role_prompt):
    """进行一次对话交互，返回AI的回复内容"""
    # 添加用户消息
    history.append({"role": "user", "content": user_input})

    # 构造调用消息：重新拼接system提示，保证规则最新
    system_message = role_prompt + "\n\n" + get_break_rules()
    api_messages = [{"role": "system", "content": system_message}] + history[1:]

    result = call_zhipu_api(api_messages)
    reply = result["choices"][0]["message"]["content"]

    history.append({"role": "assistant", "content": reply})
    return reply
