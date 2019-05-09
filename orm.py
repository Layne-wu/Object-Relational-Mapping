# #!/usr/bin/env python
# # -*- coding:utf-8 -*-
# # Author:Wwl
#
# """
# orm 简易版的思路：
# 1、定义一个基类 来表示一个表的每一个字段
# 2、定义两个 来继承这个基类，不同的数据类型
# 3、 把程序当中的类 对应到数据库 当中的表 把对应关系做好
#  表的名字，哪个键是主键，表有一堆列，，用类模拟出来，在类里加东西 来表示。
# 4、写了一个基类，让所有与数据库对应的  来继承这个基类 modles这个基类
# 对象实例化的时候 可以在类里传值，点操作。每个类里都要有一个堆东西（包括主键，名字，一堆属性）
# 用元类 拦截类的创建，把这一堆东西放进去。方法：重写了__new__方法，拦截它。
#
# """
import Mysql_singleton


class Field:  # 一个列是对象 对象里面有它的名字，是不是主键，数据类型
    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default


class StringField(Field):  # char 类型 varchar 类型
    def __init__(self, name=None, column_type='varchar(200)', primary_key=False, default=None):
        super().__init__(name, column_type, primary_key, default)


class IntegerField(Field):  # int类型
    def __init__(self, name=None, column_type='int', primary_key=False, default=0):
        super().__init__(name, column_type, primary_key, default)


class ModlesMetaclass(type):
    def __new__(cls, name, bases, attrs):

        if name == 'Modles':
            return type.__new__(cls, name, bases, attrs)
        table_name = attrs.get('table_name', None)
        # table_name=attrs['table_name']

        primary_key = None
        mappings = dict()
        for k, v in attrs.items():
            if isinstance(v, Field):  # v 是不是Field的对象
                mappings[k] = v
                if v.primary_key:

                    # 找到主键
                    if primary_key:
                        raise TypeError('主键重复：%s' % k)
                    primary_key = k

        for k in mappings.keys():
            attrs.pop(k)

        if not primary_key:
            raise TypeError('没有主键')
        attrs['table_name'] = table_name
        attrs['primary_key'] = primary_key
        attrs['mappings'] = mappings
        return type.__new__(cls, name, bases, attrs)
    # def __new__(cls, name, bases, attrs):  # name 就是user（类的名字）
    #     if name == 'Models':  # 当他是基类的时候，基类的创建过程，如果是继承基类的类 就进行拦截
    #         return type.__new__(cls, name, bases, attrs)
    #
    #     table_name = attrs.get('table_name', None)
    #     # table_name = attrs['table_name'] 这个没有的话，就报错 闪退了
    #     if not table_name:
    #         table_name = name  # 拿到表名
    #     primary_key = None
    #     # print(primary_key)
    #     mappings = dict()
    #     for k, v in attrs.items():  # for 循环干了两件事：1 把列取出来放到字典里，2、找到主键给了primary key
    #         if isinstance(v, Field):  # 判断v 是不是 Field 的对象 过滤掉一些比如__doc__的参数，因为不需要
    #             mappings[k] = v  # v 是对象
    #             if v.primary_key:  # 找到主键，v 就是 IntegerField('id',primary_key=True,default=0) 的一个对象，不是str类型了
    #                 if primary_key:
    #                     raise TypeError('主键重复：%s' % k)
    #                 primary_key = k
    #                 print(primary_key, 'iii')  # v.name 就是 id，表的主键就是id了
    #
    #     for k in mappings.keys():
    #         attrs.pop(k)
    #
    #     # 生成一个空对象
    #     print(primary_key, '-----')
    #
    #     if not primary_key:
    #         raise TypeError('没有主键')
    #     attrs['table_name'] = table_name
    #     attrs['primary_key'] = primary_key
    #     attrs['mappings'] = mappings
    #     # 类实例化出来，带着我们想要的一堆东西
    #     return type.__new__(cls, name, bases, attrs)


class Modles(dict, metaclass=ModlesMetaclass):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __setattr__(self, key, value):  # self 字典对象,给属性赋值的时候，会走__setattr__
        self[key] = value

    def __getattr__(self, item):  # user.name 先去user对象里找name属性，有的话直接返回，没有就走__getattr__
        try:
            return self[item]
        except TypeError:
            raise ('没有该属性')

    @classmethod
    def select_one(cls, **kwargs):  # 查一条
        key = list(kwargs.keys())[0]
        value = kwargs[key]
        # select * from user where id = %s
        sql = 'select * from %s where %s = ?' % (cls.table_name, key)
        sql = sql.replace('?', '%s')
        ms = Mysql_singleton.Mysql().singleton()  # 单例模式
        re = ms.select(sql, value)
        if re:
            # attrs = {'name':'123,'password':123}
            # user(**attrs)
            # 相当于 User(name = '123',password = 123)
            return cls(**re[0])  # **re 就是打散了
        else:
            return

    @classmethod
    def select_all_many(cls, **kwargs):  # 查多条
        ms = Mysql_singleton.Mysql().singleton()
        if kwargs:
            key = list(kwargs.keys())[0]
            value = kwargs[key]
            # select * from user where id = %s
            sql = 'select * from %s where %s = ?' % (cls.table_name, key)
            sql = sql.replace('?', '%s')
            re = ms.select(sql, value)
        else:
            sql = 'select * from %s' % cls.table_name
            re = ms.select(sql, None)

        return [cls(**r) for r in re]  # 返回一个装有多个对象的列表,列表推导式

    def update(self):  # 不需要传参数
        ms = Mysql_singleton.Mysql().singleton()
        # update user set = 'wwl' password = '123' where id = 1
        filed = []
        pr_key = []
        args = []
        # mappings = {id:inter的对象 name：strfil的对象  password：strfil的对象}
        # user： 1，table_name 2 primary_key 3 mappings #类的属性
        #        4 name = '123'  5 id =1 6 password = '123' # 自己的属性
        for k, v in self.mapping.items():
            if v.primary_key:
                pr_key = getattr(self, v.name, None)

                # pr_key = getattr(user,id,None) 拿到1
            else:
                filed.append(v.name + '=?')
                args.append(getattr(self, v.name, None))

                # pr_key = getattr(user,name,None) 拿到123

        sql = 'update %s set %s where %s = %s' % (self.table_name, ','.join(filed), self.primary_key, pr_key)
        sql = sql.replace('?', '%s')
        ms.extcute(sql, args)

    def save(self):
        ms = Mysql_singleton.Mysql().singleton()
        # insert into user(name,password) values(?,?)
        field = []
        values = []
        args = []
        for k, v in self.mappings.items():
            field.append(v.name)
            values.append('?')  # 有几个就放几个问号
            args.append(getattr(self, v.name, None))
        sql = 'insert into %s(%s) valuses(%s)' % (self.table_name, ','.join(field), ','.join(values))
        sql = sql.replace('?', '%s')
        ms.extcute(sql, args)


class User(Modles):
    table_name = 'user'
    id = IntegerField('id', primary_key=True, default=0)  # k就是id，v就是一个实例化出来的对象
    password = StringField('password')


class Notic(Modles):
    table_name = 'notice'
    id = IntegerField('id',primary_key=True)
    name = StringField('name')
    content = StringField('content')
    user_id = IntegerField('user_id')



if __name__ == '__main__':
    # user = User.select_one(id=1)  # 对象关系映射的查询
    # print(user.name)
    # notice_list = Notic.select_all_many()
    # print(notice_list)
    # notice = Notic.select_one(id=1)
    # notice.name='我改了'
    # notice.update()
    # notice = Notic(name='123', content='测试没有id', user_id=1)  # 如果不删除的话，对象属性和类属性就会冲突，我只要对象属性，类属性都不要
    # notice.save()
    user=User()
    user.name = 'name'
    user['id'] =1
    print(user.name)



# import Mysql_singleton
#
#
# class Fileld:
#     def __init__(self, name, column_type, primary_key, default):
#         self.name = name
#         self.column_type = column_type
#         self.primary_key = primary_key
#         self.default = default
#
#
# class StringFileld(Fileld):
#     def __init__(self, name=None, column_type='varchar(200)', primary_key=False, default=None):
#         super().__init__(name, column_type, primary_key, default)
#
#
# class IntegerFileld(Fileld):
#     def __init__(self, name=None, column_type='int', primary_key=False, default=0):
#         super().__init__(name, column_type, primary_key, default)
#
#
# class ModlesMetaclass(type):
#     def __new__(cls, name, bases, attrs):
#
#         if name == 'Modles':
#             return type.__new__(cls, name, bases, attrs)
#         table_name = attrs.get('table_name', None)
#         # table_name=attrs['table_name']
#
#         primary_key = None
#         mappings = dict()
#         for k, v in attrs.items():
#             if isinstance(v, Fileld):  # v 是不是Field的对象
#                 mappings[k] = v
#                 if v.primary_key:
#
#                     # 找到主键
#                     if primary_key:
#                         raise TypeError('主键重复：%s' % k)
#                     primary_key = k
#
#         for k in mappings.keys():
#             attrs.pop(k)
#
#         if not primary_key:
#             raise TypeError('没有主键')
#         attrs['table_name'] = table_name
#         attrs['primary_key'] = primary_key
#         attrs['mappings'] = mappings
#         return type.__new__(cls, name, bases, attrs)
# #
#
# class Modles(dict, metaclass=ModlesMetaclass):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#
#     def __setattr__(self, key, value):
#
#         self[key] = value
#
#     def __getattr__(self, item):
#         try:
#             return self[item]
#         except TypeError:
#             raise ('没有该属性')
#
#     @classmethod
#     def select_one(cls, **kwargs):
#         # 只查一条
#         key = list(kwargs.keys())[0]
#         value = kwargs[key]
#         # select * from user where id=%s
#         sql = 'select * from %s where %s=?' % (cls.table_name, key)
#         #
#         sql = sql.replace('?', '%s')
#         ms = Mysql_singleton.Mysql().singleton()
#         re = ms.select(sql, value)
#         if re:
#             # attrs={'name':'123','password':123}
#             # u=User(**attrs)
#             # 相当于 User(name='123',password=123)
#             u = cls(**re[0])
#             return u
#         else:
#             return
#
#     @classmethod
#     def select_many(cls, **kwargs):
#         ms = Mysql_singleton.Mysql().singleton()
#         if kwargs:
#             key = list(kwargs.keys())[0]
#             value = kwargs[key]
#             sql = 'select * from %s where %s=?' % (cls.table_name, key)
#             #
#             sql = sql.replace('?', '%s')
#
#             re = ms.select(sql, value)
#         else:
#             sql = 'select * from %s' % (cls.table_name)
#             re = ms.select(sql)
#
#         if re:
#             lis_obj = [cls(**r) for r in re]
#             return lis_obj
#         else:
#             return
#
    # def update(self):
    #     ms = Mysql_singleton.Mysql().singleton()
    #     # update user set name=?,password=? where id=1
    #
    #     filed = []
    #     pr = None
    #     args = []
    #     for k, v in self.mappings.items():
    #
    #         if v.primary_key:
    #             pr = getattr(self, v.name, None)
    #         else:
    #             filed.append(v.name + '=?')
    #             args.append(getattr(self, v.name, v.default))
    #
    #     sql = 'update %s set %s where %s =%s' % (self.table_name, ','.join(filed), self.primary_key, pr)
    #     # 'update user set name=?,password =? where id =1'
    #     sql = sql.replace('?', '%s')
    #     ms.extcute(sql, args)
#
#     def save(self):
#         ms = Mysql_singleton.Mysql().singleton()
#         # insert into user (name,passwword) values (?,?)
#         filed = []
#         values = []
#         args = []
#         for k, v in self.mappings.items():
#             if not v.primary_key:
#                 filed.append(v.name)
#                 values.append('?')
#                 args.append(getattr(self, v.name, v.default))
#         sql = 'insert into %s (%s) VALUES (%s)' % (self.table_name, ','.join(filed), ','.join(values))
#         sql = sql.replace('?', '%s')
#         ms.extcute(sql, args)
#
#
# class User(Modles):
#     table_name = 'user'
#     id = IntegerFileld('id', primary_key=True, default=0)
#     name = StringFileld('name')
#     password = StringFileld('password')
#
# class Notic(Modles):
#     table_name = 'notice'
#     id = IntegerFileld('id', primary_key=True)
#     name = StringFileld('name')
#     content = StringFileld('content')
#     user_id = IntegerFileld('user_id')
#
#
# if __name__ == '__main__':
#     user = User.select_one(id=1)
#
#     print(user.name)
    # notice_list=Notic.select_many()
    #
    # print(notice_list)
    # notice.name='我改了'
    # notice.update()
    # notice = Notic(name='123', content='测试没有id', user_id=1)
    # notice.save()
