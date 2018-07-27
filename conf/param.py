#coding:utf8



import collections

param = collections.OrderedDict()

param = {
     "user":
         {"login":{
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": "%s",
                "password": "%s"
            },
            "id": 0
          },
            "create":{
                "jsonrpc":"2.0",
                "method":"user.create",
                "params":{
                    "alias":"%s",
                    "passwd":"%s",
                    "usergrps":[
                        {
                            "usrgrpid":"%s"
                        }
                    ],
                    "user_medias":[
                        {
                            "mediatypeid":"%s",
                            "active": 0,
                            "sendto":"%s",
                            "severity": 63,
                            "period": "1-7,00:00-24:00"
                        }
                    ]
                }
            }
         },
     "host":{
         "create":{
        "jsonrpc": "2.0",
        "method": "host.create",
        "params": {
            "host": "%s",
            "interfaces": [
               {
                "type": 1,
                "main": 1,
                "useip": 1,
                "ip": "%s",
                "dns": "",
                "port": "10050"
                }
             ],
           "groups": [
               {
                   "groupid": "%s"
                }
             ],
            "templates": [
                {
                   "templateid": "%s"
               }
            ]
            },
            "auth": "%s",
            "id": 1
            },
        "get":{
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "output": "extend",
                "filter": {
                "ip": "%s"
            }
        },
        "auth": "%s",
        "id": 1
        },
     "delete":{
        "jsonrpc": "2.0",
        "method": "host.delete",
        "params": [
            "%s"
        ],
        "auth": "%s",
        "id": 1
     }
     },
    "hostinterface":{
        "get":{
            "jsonrpc": "2.0",
            "method": "hostinterface.get",
            "params": {
                "output": "extend",
            },
            "auth": "%s",
            "id": 1
        }
    },
    "hostgroup":{
        "create":{
            "jsonrpc":"2.0",
            "method":"hostgroup.create",
            "params":{
                "name":"%s"
            },
            "auth":"%s",
            "id":1
        }
    },
    "usergroup":{
        "create":{
            "jsonrpc":"2.0",
            "method":"usergroup.create",
            "params":{
                "name":"%s",
                "rights":{
                    "permission":"0",
                    "id":"%s"
                }
            },
            "auth":"%s",
            "id":1
        }
    }
}