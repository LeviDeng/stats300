#coding:utf-8
import pymongo
client=pymongo.MongoClient('localhost',27017)
coll=client['SanBaiHeros']['match_info']
win_stat={}
STARTNO=900000
ENDNO=1000001
with open('Heros.txt') as f:
    hero_list=f.readlines()
    #print hero_list[0].decode('utf8')

def get_stats(hero_list):
    for h in hero_list:
        h=h.strip()
        print "stating hero %s"%h.decode('utf8')
        wins=coll.find({"$where":"this.no > %d && this.no < %d"%(STARTNO,ENDNO),\
                        "Match.WinSide.Hero.Name":h,"Match.MatchType":1}).count()
        lose=coll.find({"$where":"this.no > %d && this.no < %d"%(STARTNO,ENDNO),\
                        "Match.LoseSide.Hero.Name":h,"Match.MatchType":1,}).count()
        both=coll.find({"$where":"this.no > %d && this.no < %d"%(STARTNO,ENDNO),'\
        Match.WinSide.Hero.Name':h,'Match.LoseSide.Hero.Name':h}).count()
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
            win_p = float(
                (float(list[1]) - float(list[3])) / (float(list[1]) + float(list[2]) - 2 * float(list[3])))
            w.write(k + ':' + '%0.3f' % win_p + '\n')

get_stats(hero_list)
statWins()