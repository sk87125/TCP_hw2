from getpass import getpass
import os
seperator=":"
user={'name':'passwd'}
filename="/home/kj/account.txt"
#if none account.txt , new one
if not os.path.exists(filename):
    f = open('account.txt','w')
    f.close()
else:
    fileIN = open(filename,"r")
    id = raw_input("Account : ")
    line = fileIN.readline()
    while line:
        line=line.strip()
        solu=line.split(seperator)
        user.update({solu[0]:solu[1]})
        line=fileIN.readline()
        print user
    if id in user:
        pw = getpass(prompt="Password : ")
        if user.get(id) == pw:
            print("u got it")
        else:
            print("u are wrong")
#if none user,new one in txt
    else:
        print "NEW A ACCOUNT?"
        f=open('account.txt','a')
        pw = getpass(prompt="Password : ")
        entry_text = "%s:%s"%(id,pw)
        f.write(entry_text+"\n")
        f.close()
