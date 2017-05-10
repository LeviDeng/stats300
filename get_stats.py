#coding:utf-8
import pymongo
import time
client=pymongo.MongoClient('localhost',27017)
coll=client['SanBaiHeros']['match_info']
win_stat={}
STARTNO=0
ENDNO=2000000
with open('Heros.txt') as f:
    hero_list=f.readlines()
    #print hero_list[0].decode('utf8')

def get_stats(hero_list):
    for i,h in enumerate(hero_list):
        h=h.strip()
        print time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())+\
              " : [%d/%d] stating hero %s"%(i+1,146,h.decode('utf8'))
        wins=coll.find({"$and":[{"no":{"$gt":STARTNO}},{"no":{"$lte":ENDNO}},\
                {"Match.WinSide.Hero.Name":h},{"Match.MatchType":1},\
                                {"Match.MatchDate":{"$gt":"2017-05-01"}},{"Match.MatchDate":{"$lte":"2017-05-08 00:00:00"}}]}).count()
        lose=coll.find({"$and":[{"no":{"$gt":STARTNO}},{"no":{"$lte":ENDNO}},\
                {"Match.LoseSide.Hero.Name":h},{"Match.MatchType":1}, \
                                {"Match.MatchDate": {"$gt": "2017-05-01"}},
                                {"Match.MatchDate": {"$lte": "2017-05-08 00:00:00"}}]}).count()
        both=coll.find({"$and":[{"no":{"$gt":STARTNO}},{"no":{"$lte":ENDNO}},\
                {"Match.WinSide.Hero.Name":h},{"Match.LoseSide.Hero.Name":h},{"Match.MatchType":1}, \
                                {"Match.MatchDate": {"$gt": "2017-05-01"}},
                                {"Match.MatchDate": {"$lte": "2017-05-08 00:00:00"}}]}).count()
        win_stat[h]=str(wins)+':'+str(lose)+':'+str(both)

#print win_stat
def writeResult():
    with open('result.txt','w') as f:
        for w in win_stat:
            f.write(w+':'+win_stat[w]+'\n')

def statWins():
    with open('winResult_%dw-%dw.txt'%(int(STARTNO/10000),int(ENDNO/10000)), 'w') as w:
        for k,v in win_stat.items():
            list = v.strip().split(':')
            if int(list[0])+int(list[1])-2*int(list[2]) !=0:
                win_p = float((float(list[0]) - float(list[2])) / (float(list[0]) + float(list[1]) - 2 * float(list[2])))
            else:
                win_p = 0
            w.write(k + ':' + str('%0.3f' % win_p) + '\n')

get_stats(hero_list)
statWins()