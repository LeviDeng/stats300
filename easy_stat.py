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
    uq=Queue(maxsize=10)
    dq=Queue(maxsize=2)
    mq=Queue(maxsize=2)
    end=0
    last_valid_no=0
    def putID(self,uq,start,end):
        for i in range(start,end):
            uq.put(i,True)
            #print i

    def putID_forever(self,uq,start):
        while True:
            uq.put(start,True)
            start += 1

    def collectMatch(self,uq,dq):
        client = MongoClient('localhost', MONGODB_HOST)
        coll = client[DB_NAME][COLLECTION_NAME]
        while True:
            while not uq.empty():
                no = int(uq.get()+1)
                print no
                matchid = int(no + STARTID - 1)
                if coll.find({'no':no}).count()==0:
                    try:
                        html=requests.get(BASE_URL+'api/getmatch?id=%d'%matchid)
                        if html.status_code==200:
                            user=json.loads(html.text)
                            if user['Result'] and user['Result']=='OK':
                                user['matchid']=matchid
                                user['no']=no
                                #print user
                                dq.put(user,True)
                                sleep(TIME_SLEEP)
                            elif html.text.strip()=="sql: no rows in result set" \
                                    and no>self.last_valid_no:
                               uq.put(no)
                               sleep(1)
                        #sleep(0.1)
                    except Exception:
                        uq.put(no)
            #if self.end==1:
                #break

    def insertMatch(self,dq):
        client = MongoClient('localhost', MONGODB_HOST)
        coll = client[DB_NAME][COLLECTION_NAME]
        while True:
            match=dq.get(True)
            try:
                coll.insert_one(match)
                self.last_valid_no=match['no']
                loginfo.info("Data saved,id:%d" % (match['no']))
            except Exception,e:
                logerror.error("Write data failed,id:%d" % (match['no']) + str(e))
                dq.put(match,True)

    def putMatch(self,dq,mq):
        list=[]
        while True:
            for i in range(1000):
                try:
                    list.append(dq.get(True,timeout=1000))
                except:
                    break
            mq.put(list)
            list=[]
            #if self.end==1:
                #break

    def writeData(self,mq):
        client = MongoClient('localhost', MONGODB_HOST)
        coll = client[DB_NAME][COLLECTION_NAME]
        while True:
            try:
                list=mq.get(True,timeout=1000)
                i=int(list[0]['no'])
                try:
                    coll.insert_many(list)
                    loginfo.info("Data saved,id:%d,lastid:%d"%(i/1000,list[-1]))
                except Exception,e:
                    logerror.error("Write data failed,id:%d"%(i/1000)+str(e))
                    mq.put(list)
            except:
                #self.end=1
                #break
                pass

    def run(self,list):
        if len(list)==1:
            p1 = Process(target=self.putID_forever, args=(self.uq, list[0],))
        elif len(list)==2:
            p1 = Process(target=self.putID,args=(self.uq,list[0],list[1],))
        p2 = Process(target=self.collectMatch,args=(self.uq,self.dq,))
        p3 = Process(target=self.insertMatch,args=(self.dq,))
        #p4 = Process(target=self.insertData,args=(self.mq,))
        #pList=[p1,p2,p3,p4]
        p1.start()
        p2.start()
        p3.start()
        p1.join()
        p2.join()
        p3.join()

if __name__=='__main__':
    m=MatchStat()
    loginfo.info("-----------------------------------------------")
    try:
        TIME_SLEEP=float(sys.argv[3])
    except:
        pass
    if len(sys.argv)==3:
        argvs=[int(sys.argv[1]),int(sys.argv[2])]
    elif len(sys.argv)==2:
        argvs=[int(sys.argv[1])]
    else:
        print "Usage: python %s  startno  [endno]  [time_split]"%(sys.argv[0])
        sys.exit(0)
    m.run(argvs)