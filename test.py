#coding:utf-8
import pymongo
cli=pymongo.MongoClient('localhost',27017)
coll=cli['SanBaiHeros']['match_info']
with open('Heros.txt') as f:
    list=f.readlines()

for i in range(10000):
    if coll.find({'no':i}).count()!=0:
        for n in coll.find({'no': i})[0]['Match']['WinSide']:
            if n['Hero']['Name'] not in list:
                list.append(n['Hero']['Name'])

with open('Heros.txt','w+') as f:
    for l in list:
        f.write(l.encode('utf-8')+'\n')
