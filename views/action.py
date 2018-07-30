#!/usr/bin/env python
#coding:utf8
import datetime
import json
import os
import sys

import MySQLdb
import urllib2

from db import mysql
from conf import param


class ZabbixApi(object):

    def __init__(self,username="sijie",password="sijie",server="http://127.0.0.1/api_jsonrpc.php",host_list='/etc/work_server_config',db_host="",db_username="",db_password=""):
        self.username = username
        self.password = password
        self.server = server
        self.list = host_list
        self.db_host = db_host
        self.db_username = db_username
        self.db_passwprd = db_password
        self.log = self.log()
        self.db = self.db()
        self.header = {"Content-Type": "application/json"}
        self.token = self.login_token()
        self.init()

    def init(self):
        self.insertgroupsql = "insert into pull.groups(groupid,groupname) values(%s,'%s');"
        self.inserthostsql = "insert into pull.hosts(hostid,ip,hostname,groupid) values(%s,,'%s','%s','%s')"
        self.getgroupidsql = "select groupid from pull.groups where groupname = '%s'"
        self.insertusergroupsql = "insert into pull.usergroup(usergroupid,usergroupname) values(%s,'%s')"
        self.gethostidsql = "select hostid from pull.hosts where hostname='%s'"
        self.getusergroupidsql = "select usergroupid from pull.hosts where hostname=%s"
        self.insertmediaid = "insert into pull.mediatype(mediaid,typeid,medianame) values(%s,%s,'%s')"
        self.getmediaidsql = "select mediatypeid,type from pull.mediatype where description=%s"
        self.insertusersql = "insert into pull.user(userid,username,password,media) values(%s,'%s','%s','%s')"
        self.getuseridsql = "select id from pull.user where username='%s'"
        self.gethostgroupsql = "select groupid from pull.host from where hostname ='%s'"

    def _reponse(self,data):
        request = urllib2.Request(self.server,data)
        for key in self.header:
            request.add_header(key, self.header[key])
        try:
            result = urllib2.urlopen(request)
        except urllib2.URLError as e:
            print "Failed, Please Check :", e.code
            sys.exit(10)
        return result

    def log(self):
        f = open("./action.log","w+")
        return f

    def logger(self,msg):
        nowTime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log.write("%s: %s\n" %(nowTime,msg))
        self.log.flush()

    def login_token(self):
        data = json.dumps(param.param['user']['login']) % (self.username, self.password)
        result =self._reponse(data)
        response = json.loads(result.read())
        result.close()
        return response['result']


    def db(self):
        return mysql.Mysql()

    ### 这里有待优化，例如 json.dumps(param.param['user']['login']) %(self.username,self.password)这样的形式
    def create_host(self,hostname,ip,groupids=[],templateid=10001):
        if self.get_host(hostname) != 0:
            return
        if self.get_host(hostname) != 2:
            if  self.get_groupid(hostname):
                groupids_str = [str(item for item in groupids)]
                groupids_str += self.get_groupid(hostname)
                param.param['host']['update']['auth']=self.token
                param.param['host']['update']['params']['groups']['groupid'] = groupids_str
                param.param["host"]["update"]["params"]["hostid"] =  self.get_host(hostname)
                d = param.param["host"]["update"]
            return None
        else:
            param.param['host']['create']['params']['host']=hostname
            param.param['host']['create']['params']['interfaces'][0]['ip']=ip
            length = len(groupids)
            if length <=0:
                return False
            groupids_str =  [str(item) for item in groupids]
            param.param['host']['create']['params']['groups']['groupid'] = groupids_str
            param.param['host']['create']['params']['templates'][0]['templateid'] = templateid
            param.param['host']['create']['auth']=self.token
            d = param.param["host"]["create"]
        data = json.dumps(d)
        try:
            result = json.loads(self._reponse(data))["result"]
            if result.has_key("hostids"):
                self.db.insertOne(self.inserthostsql,[result['hostids']["0"],ip,hostname,json.dumps(groupids_str)])
                self.logger("successful create group %s,groupid is %s" % (hostname,ip, str(result["hostids"][0])))
        except Exception,e:
            self.logger(e.message)
            self.logger("failed to create host %s" %(hostname))


    def create_group(self,groupname):
        if self.get_groupid(groupname) != 0:
            return
        param.param["hostgroup"]["create"]["params"]["name"] = groupname
        param.param["hostgroup"]["create"]["auth"] = self.token
        data = json.dumps(param.param["hostgroup"]["create"])
        try:
            result = json.loads(self._reponse(data))["result"]
            if result.has_key("groupids"):
                #if self.get_groupid(result["groupids"][0]):
                self.db.insertOne(self.insertgroupsql,[result["groupids"][0]],groupname)
                self.logger("successful create group %s,groupid is %s" %(groupname,str(result["groupids"][0])))
        except Exception,e:
            self.logger(e.message)
            self.logger("failed to create group %s" %(groupname))

##userinfo格式：{'username':'username','password':'password','groups':['dsq','biz'],'media':[{'mediatypeid':1,'sendto':'xxxx'}]}
    def bind_user_group(self,userinfo):
        username = userinfo["username"]
        if self.get_userid(username) != 0:
            return
        param.param["user"]["create"]["auth"] = self.token
        param.param["user"]["createa"]["params"]["alias"] = userinfo["username"]
        param.param["user"]["create"]["params"]["passwd"] = userinfo["password"]
        length = len(userinfo["groups"])
        temp = []
        for i in range(length):
            groupid = self.get_groupid(userinfo['groups'][i])
            temp.append({"usrgrpid":groupid})
        param.param["user"]["create"]["params"]["usrgrps"] = temp
        temp = []
        usermedialist = []
        #这里对用户信息进行判断，得出有哪些传输媒介，然后给出对应的[{mediatype,sendto}],这里进行扩展编写
        medialist = userinfo["media"]
        for i in range(len(medialist)):
            usermedialist.append(medialist[i]["mediatypeid"])
            temp.append({"mediatypeid":medialist[i]["mediatypeid"],"sendto":medialist[i]["sendto"],"active":0,"severity":63,"period":"1-7,00:00-24:00"})
        try:
            data = param.param["user"]["create"]
            result = json.loads(self._reponse(data))["result"]
            userid = result["userids"][0]
            self.db.insertOne(self.insertusersql,[userid,username,param.param["user"]["create"]["params"]["passwd"],json.dumps(usermedialist)])
        except Exception,e:
            self.logger(e.message)

    def get_host_group(self,hostname):
        try:
            result = self.db.getOne(self.gethostgroupsql,hostname)
            return json.loads(result[0]['groupid'])
        except Exception,e:
            self.logger(e.message)
            return None

    def get_userid(self,username):
        try:
            result = self.db.getOne(self.getuseridsql,username)
            return result[0]["id"]
        except Exception,e:
            self.logger(e.message)

    def get_groupid(self,groupname):
        try:
            result = self.db.getOne(self.getgroupidsql,groupname)
            return result[0]["groupid"]
        except Exception,e:
            self.logger(e.message)
            return 0

    def get_host(self,hostname):
        try:
            result = self.db.getOne(self.gethostidsql,hostname)
            try:
                hostid = result[0]["hostid"]
                return int(hostid)
            except Exception,e:
                return 2
        except Exception,e:
            self.logger(e.message)
            return 0

    def get_usergroupid(self,usergroupname):
        try:
            result = self.db.getOne(self.gethostidsql,usergroupname)
            return result[0]["usergroupid"]
        except Exception,e:
            self.logger(e.message)
            return 0

    def get_media_id(self,description):
        try:
            result = self.db.getOne(self.getmediaidsql,description)
            return result[0]["mediatypeid"]
        except Exception,e:
            self.logger(e.message)
            return 0

    def create_usergroup(self,groupname):
        usergroupid= self.get_usergroupid(groupname)
        if usergroupid == 0:
            self.logger("usergroup: %s not exists")
        param.param["usergroup"]["create"]["params"]["rights"]["id"] = usergroupid
        param.param["usergroup"]["create"]["params"]["name"] = groupname
        param.param['host']['create']['auth']=self.token
        data = json.dumps(param.param["hostgroup"]["create"])
        try:
            result = json.loads(self._reponse(data))["result"]
            self.db.insertOne(self.insertusergroupsql,[result["groupids"][0]],groupname)
        except Exception,e:
            self.logger(e.message)



    def create_media(self):
        param.param["mediatype"]["get"]["auth"] = self.token
        try:
            data = param.param["mediatype"]["get"]
            result = json.loads(self._reponse(data))["result"]
            for item in result:
                self.db.insertOne(self.insertusergroupsql,[item["mediatypeid"],item["type"],item["description"]])
        except Exception,e:
            self.logger(e.message)




if __name__ == "__main__":
    zabbix = ZabbixApi(server="https://xxxxx/api_jsonrpc.php",db_username="logstash",db_password="logstash",db_host="xxxx")
    zabbix.diff_ip()
    zabbix.remove_unavaiable_host()
