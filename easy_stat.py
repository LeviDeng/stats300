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
    def stat_match(self,matchid):
        no = int(matchid - STARTID + 1)
        try:
            html=requests.get(BASE_URL+'match.html?id=%d'%matchid)
            if html.status_code==200:
                user=json.loads(html.text)
                if user['Result'] and user['Resault']=='OK':
                    try:
                        self.coll.insert_one(user)
                        sleep(TIME_SLEEP)
                    except Exception,e:
                        logerror.error("Write data failed,matchid:%d,id:%d"%(matchid,matchid-STARTID))
            else:
                loginfo.warn("Get data failed!matchid:%d,id:%d"%(matchid,matchid-STARTID))
        except Exception,e:
            loginfo.warn("unable to get match:%d,id:%d"%(matchid,matchid-STARTID))

if __name__=='__main__':
    m=MatchStat()
    try:
        TIME_SLEEP=float(sys.argv[3])
    except:
        pass
    for i in range(int(sys.argv[1]),int(sys.argv[2])):
        m.stat_match(i+STARTID)