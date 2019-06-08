# -*- coding:utf-8 -*-

from mahjong_project.server.common.logger import LogConfig

log_type = "console"
logger = LogConfig(log_type).getLogger()


class HandleRequest(object):
    u"""该类主要抽象处理发送消息给客户端。"""

    def __init__(self, table):
        self.table = table

    def register_user(self, msg, player):
        send_msg = "register " + msg
        self.send_message(player["connect_socket"], send_msg)

    def login(self, msg, player):
        send_msg = "login " + msg
        self.send_message(player["connect_socket"], send_msg)

    def get_board_to_check(self, msg, player, table, board):
        send_msg = "wait_discard"

        for temp_player in table:
            if player == temp_player:
                send_msg = "get_" + msg + " %s" % board

            self.send_message(temp_player["connect_socket"], send_msg)

    def discard_board_to_check(self, msg, player, board):
        send_msg = "discard_" + msg + " %s" % board
        self.send_message(player["connect_socket"], send_msg)

    def wait_prepare(self):
        msg = "wait_other_prepare"

        for player in self.table:
            if "connect_socket" in player and "status" in player:
                if player["status"] == 0:
                    msg = "please_prepare"

                self.send_message(player["connect_socket"], msg)

    def distribute_board(self):
        msg = "distribute_board "

        for player in self.table:
            if "connect_socket" in player:
                msg += str(player["board_list"])
                self.send_message(player["connect_socket"], msg)

    def send_message(self, connfd, msg):
        connfd.send(msg.encode())
