# -*- coding:utf -*-

u"""
    本项目主要实现简单四人在线麻将功能。麻将中有碰牌、杠牌、胡牌操作。
"""

from mahjong_project.server.server import MahjongServer
from mahjong_project.server.common.logger import LogConfig

log_type = "console"
logger = LogConfig(log_type).getLogger()


def main():
    logger.info(u"开启服务器！")
    MahjongServer()


if __name__ == "__main__":
    main()
