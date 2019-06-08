# -*- coding:utf -*-

u"""
    本项目主要实现简单四人在线麻将功能。麻将中有碰牌、杠牌、胡牌操作。
"""

from mahjong_project.client.client import MahjongClient
from client.gui_window.login_window import LoginWindow


class Play(object):

    def __init__(self):
        # 连接服务器
        client = MahjongClient()
        self.sockfd = client.sockfd
        LoginWindow(self.sockfd)

    def work_on(self):
        pass


if __name__ == "__main__":
    play = Play()
