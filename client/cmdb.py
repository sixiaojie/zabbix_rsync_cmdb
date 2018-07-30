#coding:utf8
import urllib2
import sys,os
import json

class cmdb(object):
    def __init__(self,server,user,password):
        self.header = {"Content-Type": "application/json"}
        self.user = user
        self.password = password
        self.server = server

    def _response(self,url,data):
        request = urllib2.Request(url,data)
        for key in self.header:
            request.add_header(key,self.header[key])
        try:
            result = urllib2.urlopen(request)
        except urllib2.URLError as e:
            print "Failed,please Check:", e.code
            sys.exit(10)
        return result.read()

    def get_token(self):
        data = {"username":self.user,"password":self.password}
        url = self.server+"/auth"
        result = json.loads(self._response(url,json.dumps(data)))
	token = "JWT "+result["access_token"]
        self.header["Authorization"] = token

    def first(self):
        url = self.server+"/v1/biz/first/"
        result = self._response(url,None)
        firstidlist = [item['id'] for item in json.loads(result)['data']]
        return firstidlist

    def second(self,args):
        secondlist=[]
        for fid in args:
            url = self.server+"/v1/biz/first/"+str(fid)+"/"
            result = self._response(url,None)
	    for item in json.loads(result)["data"]["sub_biz"]:
		temp = {}
		user_list = []
		temp["id"] = item["id"]
		temp["name"] = item["name"]
		temp["description"] = item["description"]
		temp["third"] = self.third(item["id"])
		for user in item["principal"]:
		    user_info = {}
		    user_info["id"] = user["id"]
		    user_info["fullname"] = user["fullname"]
		    #user_info["emial"] = user["email"]
		    user_info["phone"] = user["phone"]
		    user_list.append(user_info)
		temp["user"] = user_list
	        secondlist.append(temp)
	print  secondlist

    def third(self,secondid):
	url = self.server+"/v1/biz/second/"+str(secondid)+"/"
	result = self._response(url,None)
	thirdidlist= [item['id'] for item in json.loads(result)['data']['sub_biz']]
	return thirdidlist


###下面可以添加各种告警的媒介。这里得到如何下的结果：{'username':'username',,'groups':['dsq','biz'],'phone':"xxxxx"}
    def produce_correct_userinfo(self,kargs):
        ##kargs = self.second(self.first())
        userinfo = {}
        for item in kargs:
            for user in  item["user"]:
                if not userinfo.has_key(user["id"]):
                    userinfo[user["id"]] = {"username":user["fullname"],"groups":[item["name"]],"phone":user["phone"]}
                else:
                    userinfo[user["id"]]["groups"].append(item["name"])

        print userinfo

if __name__ == "__main__":
    cmdb = cmdb("xxxxxx","xxxx","xxxx")
    cmdb.get_token()
    #cmdb.third(cmdb.second(cmdb.first()))
    cmdb.second(cmdb.first())
