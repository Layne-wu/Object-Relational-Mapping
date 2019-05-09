#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:Wwl
import pymysql


class Mysql:
    __instance = None

    def __init__(self):
        self.conn = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='leilei',
            database='youku',
            charset='utf8',
            autocommit=True
        )
        self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)  # 将列表配成字典

    def close_db(self):
        self.cursor.close()
        self.conn.close()

    def select(self, sql, args):  # 查询方法
        self.cursor.execute(sql, args)
        res = self.cursor.fetchall()
        return res

    def extcute(self, sql, args):  # 更新 保存 的方法 执行update 和 insert 语句
        try:
            self.cursor.execute(sql, args)
            affected = self.cursor.rowcount  # 影响的行数 并返回
        except BaseException as e:
            print(e)

            return affected

    @classmethod
    def singleton(cls):  # 单例模式
        if not cls.__instance:
            cls.__instance = cls()
        return cls.__instance


if __name__ == '__main__':
    ms = Mysql()
    re = ms.select('select * from user where id = %s', 1)
    print(re)
