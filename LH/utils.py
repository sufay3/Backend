"""
功能集
"""

from urllib.request import urlopen, Request
import ssl

ssl_context = ssl._create_unverified_context()


def http_fetch(url, data):
    """
    通过http协议获取响应结果
    :param url: url
    :param data: 提交数据
    :return:
    """
    try:
        response = urlopen(url, data, context=ssl_context)
        return response.read()
    except Exception as e:
        print(e.__traceback__)
        return ''
