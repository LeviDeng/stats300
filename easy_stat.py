#coding:utf-8

import sys
import requests
from time import sleep
import json
from pymongo import MongoClient
import logging
logformat=logging.Formatter("%(message)s %(asctime)s %(filename)s[line:%(lineno)d] \
                     %(levelname)s ")
loginfo=logging.getLogger('info')
loginfo.setLevel(logging.INFO)
logerror=logging.getLogger('error')
finfo=logging.FileHandler('info.log')
ferror=logging.FileHandler('error.log')
finfo.setFormatter(logformat)
ferror.setFormatter(logformat)
loginfo.addHandler(finfo)
logerror.addHandler(ferror)

BASE_URL="http://300report.jumpw.com/"
STARTID=72008655
TIME_SLEEP=2
MONGODB_HOST=27017
DB_NAME='SanBaiHeros'
COLLECTION_NAME='match_info'

class MatchStat():
    client=MongoClient('localhost',MONGODB_HOST)
    db=client[DB_NAME]
    coll=db[COLLECTION_NAME]
    def collect_match(self,matchid):
        no = int(matchid - STARTID + 1)
        try:
            html=requests.get(BASE_URL+'api/getmatch?id=%d'%matchid)
            if html.status_code==200:
                user=json.loads(html.text)
                if user['Result'] and user['Result']=='OK': #and self.coll.find({'matchid':matchid}).count()==0:
                    user['matchid']=matchid
                    user['no']=no
                    #sleep(TIME_SLEEP)
                    #print user
                    return user
        except Exception,e:
            loginfo.warn("unable to get match:%d,id:%d"%(matchid,matchid-STARTID)+str(e))

    def stat_match(self,start,end):
        list=[]
        j=0
        for i in range(start,end):
            if j<1000:
                try:
                    user=self.collect_match(i+STARTID)
                    if user:
                        list.append(user)
                        j += 1
                    else:
                        pass
                except Exception:
                    pass
            else:
                try:
                    self.coll.insert_many(list)
                    loginfo.info("Data saved,id:%d"%(i/1000))
                except Exception,e:
                    logerror.error("Write data failed,id:%d"%(i/1000)+str(e))
                j=0
                list=[]
        try:
            self.coll.insert_many(list)
        except Exception, e:
            logerror.error("Write data failed,id:%d" % (i/1000)+str(e))

if __name__=='__main__':
    m=MatchStat()
    loginfo.info("-----------------------------------------------")
    try:
        TIME_SLEEP=float(sys.argv[3])
    except:
        pass
    m.stat_match(int(sys.argv[1]),int(sys.argv[2]))