# -*- coding:utf -*-

import random
import copy

from mahjong_project.server.common.logger import LogConfig

log_type = "console"
logger = LogConfig(log_type).getLogger()


class Table(object):
	u"""该类主要抽象牌桌的行为，该类在整个流程只实例化一次。
		该类的方法对应玩家的动作，因此玩家在牌桌上的每个动作都需要一个处理函数。
	"""

	# 记录所有桌的信息
	all_table_info = list()

	def check_table(self, player, table):
		if player not in table:
			logger.error(u"房间出现未知异常，请重新连接！")
			raise Exception(u"房间出现未知异常，请重新连接！")

		if len(table) != 5:
			logger.error(u"房间出现未知异常，请重新连接！")
			raise Exception(u"房间出现未知异常，请重新连接！")

	def create_table(self, player):
		u"""若玩家点击创建房间，则创建一桌游戏，此时需要等待满四人；
		    若都是加入房间的形式的话，那么就需要判断满四人才创建一桌。
		"""
		new_table = list()
		new_table.append(player)
		self.all_table_info.append(new_table)

		return new_table

	def join_table(self, player):
		u"""加入房间."""
		for table in self.all_table_info:
			if len(table) < 4:
				table.append(player)

				return table

		# 游戏队列中都满员，需要创建房间
		return self.create_table(player)

	def quit_table(self, player, table):
		u"""退出房间."""
		if not table or player not in table:
			logger.error(u"玩家(%s)未加入到房间，不允许退出房间！" % player["nick_name"])
			return

		if len(table) == 5:
			logger.error(u"游戏中，不允许退出房间")

		table.remove(player)

	def start(self, table):
		u"""开始游戏."""
		# 摇筛子
		index = random.randrange(4)
		logger.info(u"随机庄家为：%s" % table[index]["nick_name"])
		self.distribute_board(table)
		# 将正在出牌的人记录在牌桌的最后一个元素中
		table[-1]["index"] = index
		board = table[-1]["board_list"].pop(0)
		# 给筛子摇中的人(庄家)多发一张
		table[index]["board_list"].append(board)

	def distribute_board(self, table):
		u"""发牌."""
		# 生成牌堆
		board_factory = BoardFactory()
		board_list = board_factory.gen_board_list()
		# 发牌给每个玩家
		for i in range(4):
			table[i]["board_list"] = list()
			for j in range(len(board_list)):
				if len(table[i]["board_list"]) >= 13:
					logger.info(u"玩家(%s)的手牌为：%s" %
								(table[i]["nick_name"], table[i]["board_list"]))
					break

				board = board_list.pop(j)
				table[i]["board_list"].append(board)

		# 将剩余的牌加入到第五个元素
		table_board = dict()
		table_board["board_list"] = board_list
		table.append(table_board)

	def get_one_board(self, player, table, handle_request_obj):
		u"""玩家摸牌."""
		self.check_table(player, table)
		# 抽牌
		board = table[-1].pop(0)
		# 在将摸的牌加入牌堆之前去判断
		self.check_board(board, table, handle_request_obj, check_player=player)

	def discard_one_board(self, player, table, disused_board, handle_request_obj):
		u"""玩家出牌."""
		self.check_table(player, table)
		# 废弃牌堆
		player["board_list"].remove(disused_board)
		# 记录废弃牌，显示在桌面
		player["disused_board_list"].append(disused_board)
		self.check_board(disused_board, table, handle_request_obj, exclude_player=player)

	def check_board(self, disused_board, table, handle_request_obj,
					check_player=None, exclude_player=None):
		u"""检查玩家是否能碰、杠、胡牌."""
		check_board = CheckMahjongBoard()

		# 判断出需要检查的玩家
		if check_player:
			msg = check_board.check(disused_board, check_player)
			handle_request_obj.get_board_to_check(msg, check_player, table, disused_board)
		elif exclude_player:
			for player in table:
				if player == exclude_player:
					continue

				msg = check_board.check(disused_board, player)
				handle_request_obj.discard_board_to_check(msg, player, disused_board)

	def judge_next_player(self):
		u"""判定下一个出牌玩家."""
		pass

	def is_all_prepared(self, table):
		u"""所有玩家是否都点击准备."""
		# 记录是否存在玩家没准备
		flag = False

		if len(table) < 4:
			logger.info(u"同桌玩家数量不够，请等待其他玩家连接！")
			return

		for player in table:
			if player["status"] == 0:
				flag = True

		# 四个玩家都准备好了
		if not flag:
			logger.info(u"同桌玩家均已经准备好，开始发牌！")
			self.start(table)

			return table

		logger.info(u"还有玩家未准备，请的等待该玩家准备！")


class BoardFactory(object):
	u"""该类主要抽象生成牌堆."""

	def __init__(self):
		pass

	def gen_board_list(self):
		u"""生成一桌的牌堆."""
		board_list = list()

		for i in range(4):
			for j in range(11, 20):
				# 万
				board_list.append(str(j))
			for j in range(21, 30):
				# 条
				board_list.append(str(j))
			for j in range(31, 40):
				# 筒
				board_list.append(str(j))
			for j in range(41, 44):
				# 中，发，白板
				board_list.append(str(j))

		# 打乱牌堆顺序
		random.shuffle(board_list)
		logger.info(u"生成的乱序牌堆为：%s" % str(board_list))

		return board_list


class CheckMahjongBoard(object):

	def __init__(self):
		pass

	def _is_seven_pairs(self, board, board_list):
		u"""七对胡牌."""
		board_list.append(board)
		board_list.sort()

		if len(board_list) != 14:
			return False

		# 去重之后直接判断相同的牌的数量
		for temp_board in set(board_list):
			if board_list.count(temp_board) not in [2, 4]:
				return False

		return True

	def _is_common_win(self, board, board_list):
		u"""常规胡牌."""
		board_list.append(board)
		board_list.sort()

		# 判断牌数是否正确
		if len(board_list) % 3 != 2:
			logger.info(u"胡牌失败，牌数不正确！")
			return False

		# 记录相同的牌
		same_list = list()
		for temp_board in set(board_list):
			if board_list.count(temp_board) >= 2:
				same_list.append(temp_board)

		if not same_list:
			return False

		origin_board_list = copy.deepcopy(board_list)
		divide_board_list = list()
		for temp_board in same_list:
			# 先分组多余两张牌的牌
			board_list.remove(temp_board)
			board_list.remove(temp_board)
			divide_board_list.append((temp_board, temp_board))

			for i in range(len(board_list) // 3):
				if board_list.count(board_list[0]) == 3:
					divide_board_list.append((board_list[0],) * 3)
					board_list = board_list[3:]
				elif board_list[0]+1 in board_list and board_list[0]+2 in board_list:
					# 此处不能用index来判断，因为可能存在 1，222，3 的情况
					divide_board_list.append((board_list[0], board_list[0]+1, board_list[0]+2))
					board_list.remove(board_list[0])
					board_list.remove(board_list[0]+1)
					board_list.remove(board_list[0]+2)
				else:
					# 当前的一张牌可能是分离列表中的第三张，需要重置
					board_list = copy.deepcopy(origin_board_list)
					divide_board_list = list()
					break
			else:
				return True
		else:
			return False

	def is_win(self, count_same_board, board, player):
		u"""是否可以胡牌."""
		board_list = player["board_list"]

		if count_same_board == 0:
			# 只能是3,3,3,3,2胡牌
			flag = self._is_common_win(board, board_list)
		elif count_same_board == 1:
			# 能3,3,3,3,2胡牌，也能七对胡牌
			# 优先去判断是否能七对
			flag = False
			flag1 = self._is_seven_pairs(board, board_list)
			flag2 = self._is_common_win(board, board_list)

			if flag1 or flag2:
				flag = True
		elif count_same_board == 2:
			# 只能3,3,3,3,2胡牌
			flag = self._is_common_win(board, board_list)
		elif count_same_board == 3:
			# 只能七对胡牌
			flag = self._is_seven_pairs(board, board_list)
		else:
			logger.error(u"玩家(%s)的手牌不正确！" % player["nick_name"])
			flag = False

		return flag

	def check(self, board, player):
		logger.info(u"检查玩家(%s)手牌是否能碰、杠、胡" % player["nick_name"])
		# 先去查看该玩家的手牌中有几张该牌
		count_same_board = player["board_list"].count(board)

		# 先去判断是否能胡牌
		flag = self.is_win(count_same_board, board, player)

		# 再根据有几张相同的手牌去判断是否可以碰或杠
		if count_same_board <= 1:
			msg = "pass"
			if flag:
				logger.info(u"玩家(%s)可以胡牌！" % player["nick_name"])
				msg = "win"
		elif count_same_board == 2:
			logger.info(u"玩家(%s)可以碰牌！" % player["nick_name"])
			msg = "double_board"

			if flag:
				logger.info(u"玩家(%s)可以胡牌！" % player["nick_name"])
				msg = "win_and_double_board"
		elif count_same_board == 3:
			logger.info(u"玩家(%s)可以碰牌！" % player["nick_name"])
			msg = "triple_board"

			if flag:
				logger.info(u"玩家(%s)可以胡牌！" % player["nick_name"])
				msg = "win_and_triple_board"
		else:
			logger.error(u"玩家(%s)的手牌不正确！" % player["nick_name"])
			msg = "error"

		return msg
