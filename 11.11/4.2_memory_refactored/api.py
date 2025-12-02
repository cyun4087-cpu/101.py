import requests

from requests.utils import stream_decode_response_unicode  # noqa: F401


def call_zhipu_api(messages, model="glm-4.6"):
    """调用智谱API获取AI回复"""
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    headers = {
        "Authorization": "959c4609a8174cd8bcf98f464808e058.iMOFk1hUsmK7WNij",
        "Content-Type": "application/json",
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.5,
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(f"API调用失败: {response.status_code}, {response.text}")

    return response.json()
