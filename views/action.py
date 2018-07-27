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
        self.inserthostsql = "insert into pull.hosts(hostid,hostname,groupid) values(%s,'%s',%s)"
        self.getgroupidsql = "select groupid from pull.groups where groupname = '%s'"
        self.insertusergroupsql = "insert into pull.usergroup(usergroupid,usergroupname) values(%s,'%s')"
        self.gethostidsql = "select hostid from pull.hosts where hostname=%s"
        self.getusergroupidsql = "select usergroupid from pull.hosts where hostname=%s"

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
        if self.get_host(hostname) !=0:
            return
        param.param['host']['create']['params']['host']=hostname
        param.param['host']['create']['params']['interfaces'][0]['ip']=ip
        length = len(groupids)
        if length <=0:
            return False
        for i in range(length):
            param.param['host']['create']['params']['groups'][i]['groupid'] = groupids[i]
        param.param['host']['create']['params']['templates'][0]['templateid'] = templateid
        param.param['host']['create']['auth']=self.token
        data = json.dumps(param.param["host"]["create"])
        try:
            result = json.loads(self._reponse(data))["result"]
            if result.has_key("hostids"):
                for i in range(length):
                    self.db.insertOne(self.inserthostsql,[result['hostids']["0"],hostname,groupids[i]])
                    self.logger("successful create group %s,groupid is %s" % (hostname, str(result["hostids"][0])))
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

    def bind_user_group(self):
        pass

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
            return result[0]["hostid"]
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





if __name__ == "__main__":
    zabbix = ZabbixApi(server="https://xxxxx/api_jsonrpc.php",db_username="logstash",db_password="logstash",db_host="xxxx")
    zabbix.diff_ip()
    zabbix.remove_unavaiable_host()
