with open('result.txt') as r:
    with open('winResult.txt','w') as w:
        for i in r:
            list=i.strip().split(':')
            win_p=float((float(list[1])-float(list[3]))/(float(list[1])+float(list[2])-2*float(list[3])))
            w.write(list[0]+':'+'%0.3f'%win_p+'\n')
