def should_exit_by_user(user_input):
    """判断用户是否想要结束对话，返回 True/False"""
    exit_words = ['再见', '退出', '结束', 'bye', 'exit']
    return user_input.strip() in exit_words


def should_exit_by_ai(ai_reply):
    """判断AI的回复是否表示要结束对话，返回 True/False"""
    reply_cleaned = (
        ai_reply.strip()
        .replace(" ", "")
        .replace("！", "")
        .replace("!", "")
        .replace("，", "")
        .replace(",", "")
    )

    if reply_cleaned == "再见" or (len(reply_cleaned) <= 5 and "再见" in reply_cleaned):
        return True
    return False