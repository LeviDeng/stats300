#coding:utf-8

import sys
import requests
from time import sleep
import json
from pymongo import MongoClient
import logging
from multiprocessing import Process, Queue
logformat=logging.Formatter("%(message)s %(asctime)s \
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
TIME_SLEEP=0.1
MONGODB_HOST=27017
DB_NAME='SanBaiHeros'
COLLECTION_NAME='match_info'

class MatchStat():
    client=MongoClient('localhost',MONGODB_HOST)
    coll=client[DB_NAME][COLLECTION_NAME]
    uq=Queue(maxsize=1000)
    dq=Queue(maxsize=1000)
    mq=Queue(maxsize=10)
    def putID(self,uq,start,end):
        for i in range(start,end):
            while not uq.full():
                uq.put(i)

    def collectMatch(self,uq,dq):
        while True:
            while not uq.empty():
                matchid = uq.get_nowait()
                no = int(matchid - STARTID + 1)
                try:
                    html=requests.get(BASE_URL+'api/getmatch?id=%d'%matchid)
                    if html.status_code==200:
                        user=json.loads(html.text)
                        if user['Result'] and user['Result']=='OK' and \
                                        self.coll.find({'no':no}).count()==0:
                            user['matchid']=matchid
                            user['no']=no
                            sleep(TIME_SLEEP)
                            #print user
                            dq.put(user)
                except Exception:
                    uq.put(matchid)

    def putMatch(self,dq,mq):
        list=[]
        while True:
            for i in range(1000):
                list.append(dq.get(True))
            mq.put(list)
            list=[]

    def writeData(self,mq):
        while True:
            list=mq.get()
            i=int(list[0]['no'])
            try:
                self.coll.insert_many(list)
                loginfo.info("Data saved,id:%d"%(i/1000))
            except Exception,e:
                logerror.error("Write data failed,id:%d"%(i/1000)+str(e))
                mq.put(list)

    def run(self,start,end):
        p1=Process(target=self.putID,args=(self.uq,start,end,))
        p2=Process(target=self.collectMatch,args=(self.uq,self.dq,))
        p3=Process(target=self.putMatch,args=(self.dq,self.mq,))
        p4=Process(target=self.writeData,args=(self.mq,))
        pList=[p1,p2,p3,p4]
        for p in pList:
            p.start()
            p.join()


if __name__=='__main__':
    m=MatchStat()
    loginfo.info("-----------------------------------------------")
    try:
        TIME_SLEEP=float(sys.argv[3])
    except:
        pass
    m.run(int(sys.argv[1]),int(sys.argv[2]))