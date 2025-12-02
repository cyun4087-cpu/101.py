from datetime import datetime

from chat import chat_once
from logic import should_exit_by_ai, should_exit_by_user
from memory import load_memory, save_memory
from roles import get_break_rules, get_role_prompt

# 全局配置
MEMORY_FILE = "conversation_memory.json"
DEFAULT_ROLE = "YANGxy"


def main():
    """主程序入口：初始化对话历史，运行主循环，保存记忆"""
    print("✓ 已加载初始记忆系统")
    print("输入'再见'即可退出\n")

    role_prompt = get_role_prompt(DEFAULT_ROLE)
    system_message = role_prompt + "\n\n" + get_break_rules()

    conversation_history = load_memory(MEMORY_FILE)
    if conversation_history and conversation_history[0].get("role") == "system":
        # 确保系统提示保持最新
        conversation_history[0]["content"] = system_message
    else:
        conversation_history = [{"role": "system", "content": system_message}]

    print(f"当前角色：{DEFAULT_ROLE}，历史消息 {len(conversation_history) - 1} 条")

    while True:
        user_input = input("你：")

        if should_exit_by_user(user_input):
            print("再见！")
            break

        try:
            reply = chat_once(conversation_history, user_input, role_prompt)
            print(f"AI：{reply}\n")

            save_memory(MEMORY_FILE, conversation_history)

            if should_exit_by_ai(reply):
                print("对话结束")
                break

        except Exception as exc:
            print(f"发生错误: {exc}")
            break

    save_memory(MEMORY_FILE, conversation_history)
    print(f"对话记录已保存：{MEMORY_FILE} - {datetime.now()}")


if __name__ == "__main__":
    main()