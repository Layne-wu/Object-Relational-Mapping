#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:Wwl

import pymysql

import time
class Field:
    # 创建字段所包含的信息
    def __init__(self, name, column_type, pri_key=False, increment=False, default=None):
        self.name = name
        self.column_type = column_type
        self.pri_key = pri_key
        self.increment = increment
        self.default = default


class Mymetaclass(type):
    def __init__(self, class_name, class_bases, class_dic):
        table_name = class_name  # 将类名作为表名
        columns = []
        for k, field in class_dic.items():
            if isinstance(field, Field):
                fs = '%s %s' % (field.name, field.column_type)
                if field.pri_key:
                    fs += 'primary key'
                    self.pri_key = field.name
                if field.increment:
                    fs += 'auto_increment'
                if field.default != None:
                    if isinstance(field.default, int):
                        fs += 'default %s' % field.default
                    elif isinstance(field.default, str):
                        fs += 'default %s' % field.default
                    else:
                        raise TypeError('默认值必须是字符串或整型')
                columns.append(fs)
        columns = ','.join(columns)
        # 生成最终的sql语句
        sql = 'create table %s(%s)' % (table_name, columns)
        olddb = OldDB()
        olddb.conn.execute(sql)
        print(sql)

class OldDBSingle(type):
    instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance == None:
            obj = object.__new__(cls)
            obj.__init__(*args,**kwargs)
            cls.instance = obj
        return cls.instance


class OldDB(metaclass= OldDBSingle):
    '''创建一个工具类 专门负责 增删改查 创建工具对象的时候就自动连接'''

    def __init__(self):
        self.conn = Connection()

    def save(self, obj):
        column = []
        values = []
        for k, v in obj.__dict__.items():
            column.append(k)
            values.append(v)
        # 拼接要插入的字段名
        column = ','.join(column)
        # 拼接一堆 %s %s %s %s
        fmt = ['%s' for i in values]
        fmt = ','.join(fmt)

        sql = 'insert into %s(%s) values(%s)' % (obj.__class__.__name__, column, fmt)
        print(sql)
        self.conn.execute(sql, values)

    def delete(self, obj):
        table_name = obj.__class__.__name__


        sql = 'delete from %s where %s = %s' % (table_name,obj.__class__.pri_key, obj.id)
        self.conn.execute(sql)
        print(sql)

    def update(self, obj):

        "name = %s,size = %s,author = %s"
        cs = []
        vs = []
        for k, v in obj.__dict__.items():
            c = '%s = ' % k
            c += '%s'
            cs.append(c)
            vs.append(v)
        cs = ','.join(cs)
        print(cs)

        sql = 'update %s set %s where %s = %s' % (obj.__class__.__name__, cs,obj.__class__.pri_key, obj.id)
        self.conn.execute(sql, tuple(vs))

    # 通过表名和主键值 来从数据库获取一个对象
    def get(self, cls, id):
        sql = 'select * from %s where %s = %s' % (cls.__name__,cls.__class__.pri_key, id)
        res = self.conn.select(sql)
        if not res: return
        obj = object.__new__(cls)
        for k, v in res[0].items():
            obj.__dict__[k] = v

        return obj

    def select_many(self,cls,condition=None,limit=None):
        """
        要查哪个表，条件是什么，limit 要查几条
        :return:
        """
        table_name= cls.__name__

        sql = 'select * from %s'%(table_name)
        if condition:
            sql += ' where %s'%condition
        if limit:
            sql += ' limit %s %s'%(limit[0],limit[1])
        #执行sql 防止sql注入
        res = self.conn.select(sql)
        if not res:return
        #将字典转成对象存储到列表中
        objs=[]
        for dic in res:
            obj = object.__new__(cls)
            for k,v in dic.items():
                obj.__dict__[k] = v
            objs.append(obj)
        return objs








class Connection:
    # 创建链接对象时，就自动连接数据库，并获取一个游标
    def __init__(self,max_connect = 10,retry_time):
        self.pool = []
        self.rerty_time = retry_time
        try:
            for i in range(max_connect):
                coon = pymysql.connect(
                    host='127.0.0.1',
                    user='root',
                    password='leilei',
                    database='ormtest',
                    charset = 'utf8',
                    autocommit=True
                )
                self.pool.append(coon)
            # 获取游标
            # self.cursor = coon.cursor(pymysql.cursors.DictCursor)
        except Exception as e:
            print('连接失败', e)
        print('连接数据库成功')

    # 不应该将连接直接暴露给外界 封装起来 开放一个接口
    # 适用于增 删 改的接口
    def execute(self, sql, args=None,is_select=False):
        # if not self.pool:
        #     time.sleep(0.2)
        #     return self.execute(sql,args)
        while True:
            if not self.pool:
                print('没有可用连接')
                time.sleep(0.2)
            else:
                break
        conn = self.pool.pop()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        affect_row = cursor.execute(sql, args)
        self.pool.append(conn)
        #判断要查询还是要修改
        if is_select:
            return cursor.fetchall()
        return affect_row

    # 适用于查询的接口
    def select(self, sql, args=None):
        return self.execute(sql,args,is_select=True)

