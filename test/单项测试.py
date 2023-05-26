import requests
import json

headers = {"Content-Type": "application/json; charset=UTF-8"}
url = "http://127.0.0.1:5000/api"


def use(data):
    response = requests.post(url, data=json.dumps(data), headers=headers).text
    print(response)


data1 = {"table": "staff", "control": "insert",
         "data": {"stfid": "202383200018", "privilege": 4, "worktime": "2021-05-02 11:24:00", "tel": "1145141919",
                  "groupid": "145615"}}
data2 = {"table": "series", "control": "insert", "data": {"groupid": "145615", "name": "测试组"}}
data3 = {"table": "series", "control": "select", "data": ""}
data4 = {"table": "series", "control": "update",
         "data": [{"key": "groupid", "value": "191981", "condition": "where name='测试组'"},
                  {"key": "name", "value": "'小白组'", "condition": "name='恶臭组'"}]}
use(data4)
