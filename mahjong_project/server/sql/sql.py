# -*- coding:utf-8 -*-

from pymysql import *

from mahjong_project.server.common.logger import LogConfig

log_type = "console"
logger = LogConfig(log_type).getLogger()


class SqlServer(object):

    # 创建游标对象
    cursor = None
    # 创建连接对象
    connect = None

    def __init__(self, user="root", password="root", db='mahjong',
                 host="localhost", port=3306, charset="utf8"):
        self.user = user
        self.password = password
        self.db = db
        self.host = host
        self.port = port
        self.charset = charset

    def connect_sql(self):
        u"""和数据库创建连接，建立游标."""
        self.connect = connect(user=self.user,
                               passwd=self.password,
                               db=self.db,
                               host=self.host,
                               port=self.port,
                               charset=self.charset
                               )

        # 创建游标
        self.cursor = self.connect.cursor()

    def close(self):
        u"""关闭连接，关闭游标."""
        self.cursor.close()
        self.connect.close()

    def _execute_sql(self, sql, args):
        u"""执行 sql 语句."""
        # 执行 sql 语句之前创建连接
        self.connect_sql()
        # 执行 sql 语句
        self.cursor.execute(sql, args)
        self.connect.commit()
        self.close()

    def insert_into_sql(self, user_name, password, nick_name):
        u"""数据库插入信息操作."""
        try:
            sql = "insert into user(user_name, password, nick_name) values(%s, %s, %s);"
            self._execute_sql(sql, (user_name, password, nick_name))
        except Exception as e:
            logger.error(u"插入记录到数据库失败，详细见：%s" % e)
            raise Exception(u"插入记录到数据库失败！")

    def select_from_sql(self, user_name, password):
        u"""对数据库进行查询操作."""
        try:
            sql = "select * from user where user_name = %s and password = %s;"
            self._execute_sql(sql, (user_name, password))
            data = self.cursor.fetchall()
        except Exception as e:
            logger.error(u"查询数据库记录失败，详细见：%s" % e)
            raise Exception(u"插入记录到数据库失败！")

        return data  # ((1, 'hewei', '123123', '被淹死的鱼', 1),)
