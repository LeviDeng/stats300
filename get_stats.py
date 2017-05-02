import pymongo
client=pymongo.MongoClient('localhost',27017)
coll=client['SanBaiHeros']['match_info']
win_stat={}
with open('Heros.txt') as f:
    hero_list=f.readlines()
for h in hero_list:
    h=h.strip()
    wins=coll.find({'$and':[{'Match.WinSide.Hero.Name':h},{'Match.MatchType':1}]}).count()
    lose=coll.find({'$and':[{'Match.LoseSide.Hero.Name':h},{'Match.MatchType':1}]}).count()
    both=coll.find({'$and':[{'Match.WinSide.Hero.Name':h},{'Match.LoseSide.Hero.Name':h},\
                            {'Match.MatchType':1}]}).count()
    win_stat[h]=str(wins)+':'+str(lose)+':'+str(both)

#print win_stat
with open('result.txt','w') as f:
    for w in win_stat:
        f.write(w+':'+win_stat[w]+'\n')
