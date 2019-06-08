# -*- coding:utf-8 -*-

u"""
    主要实现服务端。
"""

import sys
from socket import *

from mahjong_project.server.main.player import Player
from mahjong_project.server.common.utils import create_thread
from mahjong_project.server.common.logger import LogConfig

log_type = "console"
logger = LogConfig(log_type).getLogger()


class MahjongServer(object):

    def __init__(self):
        self.init_env()

    def init_env(self):
        # TODO: 此处需要 ssl 建立私密连接
        # 创建套接字
        sockfd = socket()
        sockfd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sockfd.bind(('0.0.0.0', 5297))
        sockfd.listen(10)

        # 等待连接
        self.wait_connect(sockfd)

    def wait_connect(self, sockfd):
        while True:
            logger.info("Waiting for connect ...")

            try:
                connfd, addr = sockfd.accept()
            except KeyboardInterrupt:
                sockfd.close()
                sys.exit("exit(1)")
            except Exception as e:
                logger.error(e)
                continue

            logger.info("Connect ip: %s" % addr[0])
            # 每个玩家连接服务器后，创建一个玩家实例
            player = Player(connfd, addr)
            create_thread(player.work_on)
