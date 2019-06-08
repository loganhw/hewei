# -*- coding:utf-8 -*-

u"""
    主要实现客户端。
"""

from socket import *


class MahjongClient(object):

    # 保存套接字
    sockfd = None

    def __init__(self):
        self.connect_server()

    def connect_server(self):
        # 创建连接(和服务端进行交互)
        HOST = '192.168.0.114'
        PORT = 5297
        ADDR = (HOST, PORT)
        s = socket()
        s.connect(ADDR)
        self.sockfd = s
        print("Connect server success!")


if __name__ == "__main__":
    MahjongClient()
