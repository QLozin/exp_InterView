import requests
import json

headers = {"Content-Type": "application/json; charset=UTF-8"}
url = "http://127.0.0.1:5000/api"


def use(data):
    response = requests.post(url, data=json.dumps(data), headers=headers).text
    print(response)


select_pool = [{"table": "baseinfo", "control": "select", "data": {"condition": "", "column": "*", "limit": "10"}}]
insert_pool = [{"table": "baseinfo", "control": "insert",
                "data": {"stdid": "202183210099", "name": "张全蛋", "sex": "男", "tel": "123456789012"}}]
delete_pool = [{"table": "baseinfo", "control": "delete", "data": {"condition": "where name='张全蛋'"}},
               {"table": "baseinfo", "control": "delete", "data": {"condition": "name='张全蛋'"}}]
update_pool = [{"table": "baseinfo", "control": "update","data":{"key":"name","value":"'中黄'","condition":"where name='大黄'"}},
               {"table":"baseinfo","control":"update","data":[{"key":"name","value":"'大黄'","condition":"where name='中黄'"}]}]
all_pool = []
all_pool.extend(select_pool)
all_pool.extend(insert_pool)
all_pool.extend(delete_pool)
all_pool.extend(update_pool)
for re in all_pool:
    use(re)
