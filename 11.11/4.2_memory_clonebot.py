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
                        print(f"✓ 已加载角色 '{role_name}' 的记忆: {memory_file} ({len(data) if isinstance(data, list) else 1} 条记录)")
                    else:
                        memory_content = ""
            else:
                print(f"⚠ 记忆文件不存在: {memory_path}")
        except Exception as e:
            print(f"⚠ 加载记忆失败: {e}")
    
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

# 【角色选择】
# 定义AI的角色和性格特征
# 可以修改这里的角色名来选择不同的人物
# 【加载完整角色设定】
# roles() 函数会自动：
# 1. 加载该角色的外部记忆文件
# 2. 获取该角色的基础人格设定
# 3. 整合成一个完整的、结构化的角色 prompt
role_system = roles("YANGxy")

# 【结束对话规则】
# 告诉AI如何识别用户想要结束对话的意图
# Few-Shot Examples：提供具体示例，让模型学习正确的行为
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

# 【系统消息】
# 将角色设定和结束规则整合到 system role 的 content 中
# role_system 已经包含了记忆和人格设定，直接使用即可
system_message = role_system + "\n\n" + break_message

# ========== 对话循环 ==========
# 
# 【重要说明】
# 1. 每次对话都是独立的，不保存任何对话历史
# 2. 只在当前程序运行期间，在内存中维护对话历史
# 3. 程序关闭后，所有对话记录都会丢失
# 4. AI的记忆完全基于初始记忆文件（life_memory.json）

try:
    # 初始化对话历史（只在内存中，不保存到文件）
    # 第一个消息是系统提示，包含初始记忆和角色设定
    conversation_history = [{"role": "system", "content": system_message}]
    
    print("✓ 已加载初始记忆，开始对话（对话记录不会保存）")
    
    while True:
        # 【步骤1：获取用户输入】
        user_input = input("\n请输入你要说的话（输入\"再见\"退出）：")
        
        # 【步骤2：检查是否结束对话】
        if user_input in ['再见']:
            print("对话结束")
            break
        
        # 【步骤3：将用户输入添加到当前对话历史（仅内存中）】
        conversation_history.append({"role": "user", "content": user_input})
        
        # 【步骤4：调用API获取AI回复】
        # 传入完整的对话历史，让AI在当前对话中保持上下文
        # 注意：这些历史只在本次程序运行中有效，不会保存
        result = call_zhipu_api(conversation_history)
        assistant_reply = result['choices'][0]['message']['content']
        
        # 【步骤5：将AI回复添加到当前对话历史（仅内存中）】
        conversation_history.append({"role": "assistant", "content": assistant_reply})
        
        # 【步骤6：显示AI回复】
        # 生成Ascii头像：https://www.ascii-art-generator.org/
        portrait = """
WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWMWWWWWWWWWWWWWWWWW
WWWWWWWWWWWWWWWWWMWWWWWWWWWWNNNNWWWWWWWWWWWWWWWWWW
WWWWWWWWWWWWWWWWWWNXK00000000KKKKXNWNNWWWWWWWWWWWW
WWWWWWWWWWWWWWWNKOxxxxxxxdxxxxOOOO0KKKKXNWWWWWWWWW
WWWWWWWWWWWWNXKOkxxxxo:,'.,c:;colldkkk0XNWWWWNNNNN
WWWWWWWWWWNX0Okkxxoc;'.....,;,;:,',:dk0XNWWWWWWWWW
WWWWWWWWNNNKOxdol:,'''',,,,,;,;;;;;;lkKXWWWWWWWWWW
WWWWWWWNNNNKOdc,','',,'';:::::::;;::ckXWWWWWWWWWWW
WWWWWWWWWNNX0d;'''',,,,;;;:::::::;:ccdKWWWWWWWWWWW
WWNNNNNWNNNXXk;',;;;;;,;;;;:cccllcc:::dXWNNNNNNNXX
NNWNNNWNWNNNNd,',;:;;;:clodkO0000OOxl;cOXKKKKKKK00
XXXXXKKKKKKX0c,;;;,;;:loddxkOO000Okxo;l0KKKKKKKKKK
00KKKKKK00KKOl,,,.,:'.....',;:cdkdl:,;xKXXXXKXXKKK
KKKKKKKXXKXXXOc;::cdd:..      .,l;. .oKXXXXXXXXXXX
XXXXXXXXXXXXXXKOxoodkkko:,'..';dko;:xKXXNNXNNXXXXX
XXXXXXXXXXXXK0KkoloddxO0000kkkOO0OkO0KKK0000KK0000
KKKKKKKXKKKx;.'..;lloxkkOOkkOOOOOkxk0000OOO0000OOO
0K000KK00x:.     .:lcldxxkxxxxdddxO0000KK0OO0000OO
000Okdl;...       ,oolccoddxxxddxOKKKKKK000O000OO0
xoc,..            .,dxdolllllc:lOKKKKKXXKXXXXXXXXX
..                  'ddloodl'  .':cxO0KKXXXXXXXXXX
                    .';;,','..   .',:xKK0KKXXXXXXX
                       ......     .. 'kXKKXXNNXXXX
                 .     ';;:c:.       .lXXXXXXXXXXX
          ..   ..      'oOOOd'        .xXXXXXXXXXX
    ..... ..      ..    'cdOk:.        ,OXXXXXXXXX
           ...    ...     ,xOl.        .:0XXXXXXXX
        ..   ..    ..      'dx,     .   .oKXXXXXXX
      .....         .       .c'     .    .l0XXXXXX
    ..........           .                .;kXXXXX
   ... ..........                           ,OXXXX
       ...............                      'kXKXX
         .....   ....                       'kXKKK
        ....     ..                         .,o0KK
         ..                                   .dKK
                                               :OO
                  ..                           ,dd
                 .;;.                          ,oo
        """
        print(portrait + "\n" + assistant_reply)
        
        # 【步骤7：检查AI回复是否表示结束】
        reply_cleaned = assistant_reply.strip().replace(" ", "").replace("！", "").replace("!", "").replace("，", "").replace(",", "")
        if reply_cleaned == "再见" or (len(reply_cleaned) <= 5 and "再见" in reply_cleaned):
            print("\n对话结束")
            break

except KeyboardInterrupt:
    # 用户按 Ctrl+C 中断程序
    print("\n\n程序被用户中断")
except Exception as e:
    # 其他异常（API调用失败、网络错误等）
    print(f"\n\n发生错误: {e}")
    