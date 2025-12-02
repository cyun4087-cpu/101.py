import json
import os

def load_memory(file_path):
    """从JSON文件加载对话历史，返回对话历史列表"""
    if not file_path:
        return []

    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_memory(file_path, data):
    """保存对话历史到JSON文件"""
    if not file_path:
        return

    directory = os.path.dirname(file_path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

