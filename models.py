#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:Wwl
from old_db import Mymetaclass,Field

class User(metaclass=Mymetaclass):
    id = Field('id','int',pri_key=True,increment=True)
    name = Field('name','char(20)')
    password = Field("password","char(20)",default="xxxxx")
    vip = Field("vip","tinyint",default=0)
    locked = Field("locked","tinyint",default=1)
    def __init__(self,name,password,vip,locked):
        self.nam = name
        self.password = password
        self.vip = vip
        self.locked = locked


class Movie(metaclass=Mymetaclass):
    id = Field("id", "int", pri_key=True, increment=True)
    name = Field("name", "char(20)")
    author = Field("author", "char(20)")
    isvip = Field("isvip", "tinyint", default=0)
    size = Field("size", "char(20)")
    path = Field("path", "varchar(100)")

    def __init__(self,name,author,size,path,isvip=0):
        self.name = name
        self.author = author
        self.size = size
        self.path = path
        self.isvip = isvip