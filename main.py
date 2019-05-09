#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:Wwl
from old_db import OldDB
from models import Movie
olddb = OldDB()
m1 = Movie('毒液','歪果仁','3GB','movies/毒液.MKV')
olddb.save(m1)


obj = olddb.get(Movie,2)
print(obj.size)


obj.name = '黄金傻仔'
# olddb.delete(obj)

# olddb.delete(obj)

# m = Movie("妈妈再爱我一次","一群中国人","200MB","妈妈再爱我一次.mp4")
# olddb.save(m)
#
# m2 = olddb.get(Movie,5)
# print(m2.name)
#
# m2.name = "妈妈再爱我两次"
# olddb.update(m2)
#
# olddb.delete(m2)

