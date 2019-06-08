# -*- coding:utf-8 -*-

import sys

from mahjong_project.server.main.table import Table
from mahjong_project.server.main.handle_request import HandleRequest
from mahjong_project.server.sql.sql import SqlServer
from mahjong_project.server.common.logger import LogConfig

log_type = "console"
logger = LogConfig(log_type).getLogger()


class Player(Table):
	u"""该类主要抽象玩家的行为。"""

	# 创建玩家对象，status 代表玩家的状态；0：未准备，1：准备
	# disused_board_list 是出过的牌
	new_player = {"status": 0, "disused_board_list": []}
	# 记录同桌的数据，直接进行传参改变，后续不需要遍历整个列表
	table = None

	def __init__(self, connfd, addr):
		self.connfd = connfd
		self.addr = addr
		self.new_player["addr"] = addr
		self.new_player["connect_socket"] = connfd
		# 实例化发送信息类
		self.handle_request = HandleRequest(self.table)
		# 实例化 sql 类
		self.sql_client = SqlServer()

	def has_double_board(self):
		u"""碰牌."""
		logger.info(u"碰牌！")
		pass

	def has_triple_board(self):
		u"""杠牌."""
		logger.info(u"杠牌！")
		pass

	def pass_board(self):
		u"""过."""
		logger.info(u"过！")
		pass

	def wining(self):
		u"""胡牌."""
		logger.info(u"胡牌！")
		pass

	def register(self, msg_list):
		u"""注册账号."""
		logger.info(u"用户名为：%s 的用户请求注册账号！" % msg_list[1])
		user_name = msg_list[1]
		password = msg_list[2]
		nick_name = msg_list[3]

		if not user_name or not password or not nick_name:
			logger.error(u"注册用户(%s)失败！" % user_name)
			return False

		try:
			self.sql_client.insert_into_sql(user_name, password, nick_name)
		except Exception:
			return False

		return True

	def login(self, msg_list):
		u"""账号登录."""
		logger.info(u"用户名为：%s 的用户请求登录账号！" % msg_list[1])
		user_name = msg_list[1]
		password = msg_list[2]

		if not user_name or not password:
			logger.error(u"注册用户(%s)失败！" % user_name)
			return False

		try:
			data = self.sql_client.select_from_sql(user_name, password)
		except Exception:
			return False

		if not data:
			return False

		# 登录成功记录该用户的信息
		self.new_player["user_name"] = user_name
		self.new_player["nick_name"] = data[0][3]

		return True

	def parse_cmd(self, msg):
		# 此处可以移动到 handle_request 中处理
		cmd_list = msg.split(" ")
		cmd = cmd_list[0]

		# 解析命令
		if cmd == "register":
			# cmd_list = ["register", "user_name", "password"]
			res = self.register(cmd_list)
			msg = "error"
			if res:
				msg = "ok"

			self.handle_request.register_user(msg, self.new_player)
		elif cmd == "login":
			# cmd_list = ["register", "user_name", "password"]
			res = self.login(cmd_list)
			msg = "error"
			if res:
				msg = "ok"

			self.handle_request.login(msg, self.new_player)
		elif cmd == "create_table":
			logger.info(u"%s 创建房间！" % self.new_player["nick_name"])
			self.table = self.create_table(self.new_player)
		elif cmd == "join_table":
			logger.info(u"%s 加入房间！" % self.new_player["nick_name"])
			self.table = self.join_table(self.new_player)
		elif cmd == "quit_table":
			logger.info(u"%s 退出房间！" % self.new_player["nick_name"])
			self.quit_table(self.new_player, self.table)
		elif cmd == "get_one_board":
			logger.info(u"玩家(%s)摸牌！" % self.new_player["nick_name"])
			self.get_one_board(self.new_player, self.table, self.handle_request)
		elif cmd == "discard_one_board":
			disused_board = cmd_list[1]
			self.discard_one_board(self.new_player, self.table, disused_board, self.handle_request)
		elif cmd == "has_triple_board":
			self.has_triple_board()
		elif cmd == "has_triple_board":
			self.has_triple_board()
		elif cmd == "pass_board":
			self.pass_board()
		elif cmd == "prepare":
			logger.info(u"玩家(%s)已准备！" % self.new_player["nick_name"])
			self.new_player["status"] = 1
			data = self.is_all_prepared(self.table)

			if not data:
				# 还有玩家没有准备
				self.handle_request.wait_prepare()
			else:
				# 所有玩家都准备好了，直接发牌
				self.handle_request.distribute_board()
		else:
			logger.info(u"玩家(%s)发送未知命令！" % self.addr[0])

	def work_on(self):
		while True:
			msg = self.connfd.recv(1024).decode()
			if msg == "quit":
				logger.info(u"客户端(%s)退出" % self.addr[0])
				sys.exit(u"客户端退出")

			self.parse_cmd(msg)
