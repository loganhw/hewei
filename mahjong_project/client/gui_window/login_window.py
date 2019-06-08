# -*- coding:utf -*-

import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *


class LoginWindow(QtWidgets.QMainWindow):
    u"""该类主要抽象玩家界面的显示。"""

    # 窗口对象
    window = None
    # 用户名
    user_name = None
    # 用户密码
    user_password = None

    def __init__(self, sockfd):
        super(LoginWindow, self).__init__()

        # 保存套接字发送消息
        self.sockfd = sockfd
        # 创建登录窗口
        self.create_window()

    def _send_message(self, msg):
        self.sockfd.send(msg.encode())

    def parse_response(self, msg):
        msg_list = msg.split(" ")
        cmd = msg_list[0]

    def handle_message(self, msg):
        self._send_message(msg)
        # 等待接收回复
        data = self.sockfd.recv(1024).decode()
        self.parse_response(data)

    def create_window(self):
        self.setObjectName("LoginWindow")
        self.resize(386, 127)


if __name__ == "__main__":
    login_win = LoginWindow(11)
