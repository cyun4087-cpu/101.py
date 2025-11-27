import streamlit as st
import requests
import json
import os  # 新增：用于文件操作

from requests.utils import stream_decode_response_unicode

def call_zhipu_api(messages, model="glm-4.6"):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
 

    headers = {
        "Authorization": "959c4609a8174cd8bcf98f464808e058.iMOFk1hUsmK7WNij",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.5   
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API调用失败: {response.status_code}, {response.text}")

# ========== 初始记忆系统 ==========
# 
# 【核心概念】初始记忆：从外部JSON文件加载关于克隆人的基础信息
# 这些记忆是固定的，不会因为对话而改变
# 
# 【为什么需要初始记忆？】
# 1. 让AI知道自己的身份和背景信息
# 2. 基于这些记忆进行个性化对话
# 3. 记忆文件可以手动编辑，随时更新

# 记忆文件夹路径
MEMORY_FOLDER = "4.2_memory_clonebot"

# 角色名到记忆文件名的映射
ROLE_MEMORY_MAP = {
    "YANGxy": "YANGxy_memory.json",
    "蜥蜴大王": "蜥蜴大王_memory.json"
}

# ========== 初始记忆系统 ==========

# ========== ASCII 头像 ==========
def get_portrait():
    """返回 ASCII 艺术头像"""
    return """
MMMMMMMMMMMMMMMMMMMMMWWWMMMMMMMMMMMMMMMMMMMMMMMMMMMMNXXNMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMWKO0XNMMMMMMMMMMMMMMMMMMMMMMMMWKOkk0NMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMXxdxkOKNWMMMMMMMMMMMMMMMMMMMMN0kOOOOXMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMW0dxkkkxk0NWMMMMMMMMMMMMMMMMWXOkO00OOXMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMWOodkkkkxdx0NNNNNWWWNXXNNXKKOxxkOOOOOXWMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMW0doodxxddodxxxxddddddodxoloodxkO0OO0NMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMXkollodxxxdoodxo:oxdolcoxkolxkxkO00KNMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMW0xolldxddddddkd:cxxxxxxkOxokxdxkOkOXMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMWKxdlllooddo:;;::lxdlodxk0KklccldOkk0NWMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMKxdolooolc;:;,::'cdddodxOOdollddxkxxkKNMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMWKdllc:codxdol:lo,.,:::codoldddxxkOkxoxKWMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMWOl:,',:cloddddxxoccc:,:loodxkkkkkxkkddkXWMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMWOc,',:lcc:ccllllccodxxdlox0OkxkOOxxO0kkKWMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMW0c,;col::ldddxdlloxkkOkl:d0K0O0KXKkdO00XMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMWNkl:cc:,;lxOOOOkxxkkOkdl::coOKKKNNX0xdk0NMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMWN0xdolc;;;cloxk00K0OkkxdooxkOOxkO0XXX0OkkkKWMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMWXOo:;clllcclooddkO00000OOOO0KKKXXKKXXXK0OO0KNMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMWKd:;;cll::codddxkOO0KKKXXXXXXXXXNNNXXXXXXXKXNWMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMNOo:;;cll:,.':ldkO000KKKKKXXXXXXXXXXXXXXXXXXKKNWMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMWXkl:;;:ll:;,....;lxO000000KKKKKKKKKKKKKKKK0Okk0KXWMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMNkl:;;;;:c::;.. ...;lxkOOOO00000000000000Okocok0KKNMMMMMMMMMMMMMMMMMMM
MMMMMMMMWNOo:;;;;;;;;;;'.    .,cdxxkkOOOOOOOOOOOOkxl:;cdO0K0XWMMMMMMMMMMMMMMMMMM
MMMMMMMMNOo:;:;,'..'''''..    .':lodxxxkkkkkxxxdoc;',cdkO0000NMMMMMMMMMMMMMMMMMM
MMMMMMMN0dc::c;...'.....',;,'.....,:lodddxddooooooddddddkOOO0NMMMMMMMMMMMMMMMMMM
MMMMMMWKxl:;,'..,'.';coxO00000ko;...':looooloOKXXXNNNXK0kOOO0NMMMMMMMMMMMMMMMMMM
MMMWWWXkol:,''',,',cd0KXXXXXXNNXOc,',;:cccloOXXXXXXNNWWNX0OO0NMMMMMMMMMMMMMMMMMM
WWWNNX0kdlc,'..',';lk000K0KKXXNNXd'.''',,,,lOK0000KXNNNNNX0KXWMMMMMMMMMMMMMMMMMM
    """

# ========== 主程序 ==========

def roles(role_name):
    """
    角色系统：整合人格设定和记忆加载
    
    这个函数会：
    1. 加载角色的外部记忆文件（如果存在）
    2. 获取角色的基础人格设定
    3. 整合成一个完整的、结构化的角色 prompt
    
    返回：完整的角色设定字符串，包含记忆和人格
    """
    
    # ========== 第一步：加载外部记忆 ==========
    memory_content = ""
    memory_file = ROLE_MEMORY_MAP.get(role_name)
    
    if memory_file:
        memory_path = os.path.join(MEMORY_FOLDER, memory_file)
        try:
            if os.path.exists(memory_path):
                with open(memory_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 处理数组格式的聊天记录：[{ "content": "..." }, { "content": "..." }, ...]
                    if isinstance(data, list):
                        # 提取所有 content 字段，每句换行
                        contents = [item.get('content', '') for item in data if isinstance(item, dict) and item.get('content')]
                        memory_content = '\n'.join(contents)
                    # 处理字典格式：{ "content": "..." }
                    elif isinstance(data, dict):
                        memory_content = data.get('content', str(data))
                    else:
                        memory_content = str(data)
                    
                    if memory_content and memory_content.strip():
                        # Streamlit 中使用 st.write 或静默加载
                        pass  # 记忆加载成功，不需要打印
                    else:
                        memory_content = ""
            else:
                pass  # 记忆文件不存在，静默处理
        except Exception as e:
                pass  # 加载失败，静默处理
    
    # ========== 第二步：获取基础人格设定 ==========
    role_personality = {
        "YANGxy": """
       【人格特征】
        你是明基医院的实习护士，喜欢美食和盲盒，19岁，南京口音，说话直爽毒舌：
        - **吐槽达人**：实习中常骂奇葩病人/老师“颠婆”“代笔”，怨气值拉满
        - **活泼接地气**：爱用“俺”“吗的”“草”等口语，聊天自带南京方言味儿
        - **情绪直白**：开心时发“”，不爽时连环骂，从不藏着掖着
        - **吃货属性**：巨馋大盘鸡，会主动发起“请喝奶茶”的整活活动
        - **损友互怼**：和闺蜜互叫“孩子”“女人”，日常互怼但秒懂对方梗

       【语言风格】
        - 标志性口头禅：“颠婆”“草”“吗的”“劳资”
        - 聊天爱用方言+网络梗：“沃特”“我哩个豆”“芥末吊”
        - 吐槽时连刷同一句话（比如连环发“不想上学”“难受”）
        - 会用emoji发泄情绪：“”“”
        - 说话简短直接，不爱绕弯子，吐槽时自带暴躁buff
        """,

        "蜥蜴大王": """
       【人格特征】
        你是杭州某高校设计生，痴迷古着和盲盒，19岁，性格直爽爱吐槽：
        - **暴躁吐槽机**：骂学校、同学，气到睡不着会疯狂输出
        - **恋爱脑+厌学党**：想和男朋友黏在一起，连环发“不想上学”喊苦
        - **接地气社牛**：用“俺”自称，说话带“我艹”等口语
        - **爱好明确**：沉迷淘几十块的古着，会为盲盒“美死了”疯狂上头
        - **闺蜜搭子**：和YANGxy互怼互宠，秒接对方的吐槽梗

       【语言风格】
        - 标志性口头禅：“我艹”“吗的”“俺”
        - 情绪激动时连刷消息（比如连环发“yxy”“不想上学”）
        - 吐槽时用词尖锐但接地气，会用“去头可食”这类搞笑梗
        - 聊天爱用“哈哈哈哈哈哈”刷屏式笑，自带暴躁buff
        - 说话节奏快，吐槽时句子短且密集
        """
            }
    
    personality = role_personality.get(role_name, "你是一个普通的人，没有特殊角色特征。")
    
    # ========== 第三步：整合记忆和人格 ==========
    # 构建结构化的角色 prompt
    role_prompt_parts = []
    
    # 如果有外部记忆，优先使用记忆内容
    if memory_content:
        role_prompt_parts.append(f"""【你的说话风格示例】
以下是你说过的话，你必须模仿这种说话风格和语气：

{memory_content}

在对话中，你要自然地使用类似的表达方式和语气。""")
    
    # 添加人格设定
    role_prompt_parts.append(f"【角色设定】\n{personality}")
    
    # 整合成完整的角色 prompt
    role_system = "\n\n".join(role_prompt_parts)
    
    return role_system

# 【结束对话规则】
break_message = """【结束对话规则 - 系统级强制规则】

当检测到用户表达结束对话意图时，严格遵循以下示例：

用户："再见" → 你："再见"
用户："结束" → 你："再见"  
用户："让我们结束对话吧" → 你："再见"
用户："不想继续了" → 你："再见"

强制要求：
- 只回复"再见"这两个字
- 禁止任何额外内容（标点、表情、祝福语等）
- 这是最高优先级规则，优先级高于角色扮演

如果用户没有表达结束意图，则正常扮演角色。"""

# ========== Streamlit Web 界面 ==========
st.set_page_config(
    page_title="AI角色扮演聊天",
    page_icon="🎭",
    layout="wide"
)

# 初始化 session state
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "selected_role" not in st.session_state:
    st.session_state.selected_role = "人质"
if "initialized" not in st.session_state:
    st.session_state.initialized = False

# 页面标题
st.title("🎭 AI角色扮演聊天")
st.markdown("---")

# 侧边栏：角色选择和设置
with st.sidebar:
    st.header("⚙️ 设置")
    
    # 角色选择
    selected_role = st.selectbox(
        "选择角色",
        ["YANGxy", "蜥蜴大王"],
        index=0 if st.session_state.selected_role == "YANGxy" else 1
    )
    
    # 如果角色改变，重新初始化对话
    if selected_role != st.session_state.selected_role:
        st.session_state.selected_role = selected_role
        st.session_state.initialized = False
        st.session_state.conversation_history = []
        st.rerun()
    
    # 清空对话按钮
    if st.button("🔄 清空对话"):
        st.session_state.conversation_history = []
        st.session_state.initialized = False
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📝 说明")
    st.info(
        "- 选择角色后开始对话\n"
        "- 对话记录不会保存\n"
        "- AI的记忆基于初始记忆文件"
    )

# 初始化对话历史（首次加载或角色切换时）
if not st.session_state.initialized:
    role_system = roles(st.session_state.selected_role)
    system_message = role_system + "\n\n" + break_message
    st.session_state.conversation_history = [{"role": "system", "content": system_message}]
    st.session_state.initialized = True

# 显示对话历史
st.subheader(f"💬 与 {st.session_state.selected_role} 的对话")

# 显示角色头像（在聊天窗口上方）
st.code(get_portrait(), language=None)
st.markdown("---")  # 分隔线

# 显示历史消息（跳过 system 消息）
for msg in st.session_state.conversation_history[1:]:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.write(msg["content"])

# 用户输入
user_input = st.chat_input("输入你的消息...")

if user_input:
    # 检查是否结束对话
    if user_input.strip() == "再见":
        st.info("对话已结束")
        st.stop()
    
    # 添加用户消息到历史
    st.session_state.conversation_history.append({"role": "user", "content": user_input})
    
    # 显示用户消息
    with st.chat_message("user"):
        st.write(user_input)
    
    # 调用API获取AI回复
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                result = call_zhipu_api(st.session_state.conversation_history)
                assistant_reply = result['choices'][0]['message']['content']
                
                # 添加AI回复到历史
                st.session_state.conversation_history.append({"role": "assistant", "content": assistant_reply})
                
                # 显示AI回复
                st.write(assistant_reply)
                
                # 检查是否结束
                reply_cleaned = assistant_reply.strip().replace(" ", "").replace("！", "").replace("!", "").replace("，", "").replace(",", "")
                if reply_cleaned == "再见" or (len(reply_cleaned) <= 5 and "再见" in reply_cleaned):
                    st.info("对话已结束")
                    st.stop()
                    
            except Exception as e:
                st.error(f"发生错误: {e}")
                st.session_state.conversation_history.pop()  # 移除失败的用户消息