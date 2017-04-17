#coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import requests,re
from bs4 import BeautifulSoup
from time import sleep
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
DB_NAME='three_handred_heros'
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
                soup=BeautifulSoup(html.text,'lxml')
                trs=soup.find_all('tr')
                if len(trs)==16:
                    match_info = {}
                #datamsg=soup.findAll(attr={'class':'datamsg'})           #类型:战场 人头数:62/51 比赛时间:2017-03-22 22:19:13 比赛用时:41分40秒
                    datamsg=soup.find_all('div',class_='datamsg')[0].text.split(' ')
                    match_info['no']=no
                    match_info['type']=datamsg[0].split(':')[1]
                    #print match_info.info_type
                    if match_info['type']=='战场':        #战场，竞技场数据格式不同，偏移量为4
                        FLAG=-2
                    else:
                        FLAG=2
                    #print FLAG
                    match_info['date']=datamsg[2].split(':')[1]
                    match_info['time']=datamsg[3]
                    playtime=datamsg[4].split(":")[1]
                    playtime_h=re.findall(u"(\d+)小时",playtime)[0] if re.search(u'小时',playtime) else "00"
                    playtime_m=re.findall(u"(\d+)分",playtime)[0] if re.search(u'分',playtime) else "00"
                    playtime_s=re.findall(u"(\d+)秒",playtime)[0] if re.search(u'秒',playtime) else "00"
                    match_info['playtime']=str(playtime_h)+':'+str(playtime_m)+':'+str(playtime_s)
                    #print match_info['playtime']
                    trs.pop(8)
                    trs.pop(0)
                    match_info['player_info']=[]
                    for i in range(len(trs)):
                        try:
                            tds=[ t for t in trs[i].children ]
                        except IndexError:
                            continue
                            #print i,matchid
                        player_info={}
                        player_info['wins']=True if (trs[i].parent.previous_element.previous_element==u"胜利") else False
                        if tds[3].a:
                            player_info['name']=tds[3].a.string.split('(')[0]
                        try:
                            player_info['hero']=tds[3].a.next_element.next_element.next_element.split('(')[0]
                        except Exception,e:
                            #print i,matchid,e
                            loginfo.warning(e)
                        player_info['user_lv']=int(re.findall("lv\.(\d+)",str(tds[3]))[0])
                        player_info['hero_lv']=int(re.findall("lv\.(\d+)",str(tds[3]))[1])
                        kills=tds[5].string.split('/')
                        player_info['kills']=int(kills[0])
                        player_info['dies']=int(kills[1])
                        player_info['helps']=int(kills[1])
                        player_info['resault']=tds[7].string
                        player_info['soldiers']=int(tds[11].string)
                        player_info['skills']=[]
                        player_info['skills'].append(tds[15+FLAG].img['title'])
                        player_info['skills'].append(tds[15+FLAG].img.next_sibling['title'])
                        #print tds[15+FLAG].img['title']
                        player_info['items']=[]
                        items=tds[17+FLAG].find_all('img')
                        if len(items)!=0:
                            for j in range(1,len(items)+1):
                                player_info['items'].append(items[j-1]['title'])
                                #print items[j-1]['title']
                        if FLAG==2:
                            player_info['golds']=tds[13].string
                            try:
                                gain_golds_exps=tds[21].string.split('/')
                                if len(gain_golds_exps) != 0:
                                    player_info['gain_golds']=int(gain_golds_exps[0])
                                    player_info['gain_exp']=int(gain_golds_exps[1])
                            except TypeError:
                                continue
                            player_info['jiecao']=int(tds[23].string)
                            player_info['win_p']=tds[25].string
                        match_info['player_info'].append(player_info)
                    #print type(match_info)
                    return match_info
            else:
                loginfo.warn("id:%d 未获取到比赛信息。"%no)
        except Exception,e:
            logerror.warn(str(e)+"网络连接失败")

    def write_data(self,info):
        no=info['no']
        if not self.coll.find_one({'no':no}):
            try:
                self.coll.insert(info)
                loginfo.info("成功存储比赛信息，id:%d"%no)
                print "id:%d saved"%no
                sleep(TIME_SLEEP)
            except Exception,e:
                logerror.error("\t\t"+str(e)+"存储数据失败,"+"id:%d"%no)

    def run(self,start,end):
        #threads=[]
        for i in range(int(start),int(end)):
            #t=threading.Thread(target=self.stat_match,args=(STARTID+i,))
            #threads.append(t)
            #t.start()
            match_info=self.stat_match(STARTID+i)
            #print match_info.keys()
            try:
                self.write_data(match_info)
            except Exception,e:
                pass
        #sys.exit()


if __name__=='__main__':
    m=MatchStat()
    try:
        TIME_SLEEP=float(sys.argv[3])
    except:
        pass
    m.run(sys.argv[1],sys.argv[2])


