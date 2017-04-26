import pymongo
client=pymongo.MongoClient('localhost',27017)
coll=client['SanBaiHeros']['match_info']
win_stat={}
for i in range(50000):
    if coll.find({'no':i}).count()!=0:
        user=coll.find({'no':i})[0]
        for w in user["Match"]["WinSide"]:
            hero=w['Hero']['Name']
            if hero:
                if win_stat.has_key(hero):
                    win_stat[hero] += 1
                else:
                    win_stat[hero] = 1

print win_stat