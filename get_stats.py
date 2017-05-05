import pymongo
client=pymongo.MongoClient('localhost',27017)
coll=client['SanBaiHeros']['match_info']
win_stat={}
with open('Heros.txt') as f:
    hero_list=f.readlines()
for h in hero_list:
    h=h.strip()
    print "stating hero %s"%h
    wins=coll.find({"Match.WinSide.Hero.Name":h,"Match.MatchType":1,\
                    "$where":"this.no > 900000"}).count()
    lose=coll.find({"Match.LoseSide.Hero.Name":h,"Match.MatchType":1,\
                    "$where":"this.no > 900000"}).count()
    both=coll.find({'Match.WinSide.Hero.Name':h,'Match.LoseSide.Hero.Name':h,\
                            'Match.MatchType':1,"$where":"this.no > 900000"}).count()
    win_stat[h]=str(wins)+':'+str(lose)+':'+str(both)

#print win_stat
def writeResult():
    with open('result.txt','w') as f:
        for w in win_stat:
            f.write(w+':'+win_stat[w]+'\n')

def statWins():
    with open('winResult.txt', 'w') as w:
        for k,v in win_stat.items():
            list = v.strip().split(':')
            win_p = float(
                (float(list[1]) - float(list[3])) / (float(list[1]) + float(list[2]) - 2 * float(list[3])))
            w.write(k + ':' + '%0.3f' % win_p + '\n')

statWins()