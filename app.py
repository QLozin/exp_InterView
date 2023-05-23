from flask import Flask, request, jsonify
from logger import mylog as log
from SQL.mainSQL import SQL
from model import ReceiveBaseInfo,MessageGen,DeleteMessage

app = Flask(__name__)
mysql = SQL(passwd="mysql@root", dbname="experiment")


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/test', methods=['POST'])
def get_json():
    data = request.get_json()
    log.info(f"Receive Test Data::{data}")
    return 'You Have Been Connected To Us!'


@app.route('/insert/baseinfo', methods=['POST'])
def insert_baseinfo():
    receive = request.get_json()
    log.info(f"收到数据::{receive}")
    try:
        data = ReceiveBaseInfo(**receive)
        log.info(f"成功解析数据::{data}")
    except Exception as e:
        log.error(e)
        return 'failed'
    res:MessageGen = mysql.insert(data.table, data.data.dict())
    return jsonify(res.dict())

@app.route('/insert',methods=['POST'])
def general_insert():
    """
    通用插入方法，JSON格式应该为{"table":table_name,"data":{...}}
    :return:
    """
    receive = request.get_json()
    log.info(f"收到数据::{receive}")
    res:MessageGen = mysql.insert(receive['table'],receive['data'])
    return jsonify(res.dict())

@app.route('/delete', methods=['POST'])
def delete():
    receive = request.get_json()
    log.info(f"收到数据::{receive}")
    print(receive)
    try:
        data = DeleteMessage(**receive)
        log.info(f"成功解析数据::{data}")
    except Exception as e:
        log.error(e)
        return 'failed'
    res:MessageGen = mysql.delete(data.table, data.condition)
    return jsonify(res.dict())

@app.route('/update', methods=['POST'])
def update():
    receive = request.get_json()
    table = receive['table']
    key = receive['data']['key']
    value = receive['data']['value']
    condition = receive['data']['condition']
    log.info(f"收到数据::UPDATE {table} SET {key} = {value} WHERE {condition}")
    res:MessageGen = mysql.update(table,key,value,condition)
    return jsonify(res.dict())

@app.route('/select',methods=['POST'])
def select():
    receive = request.get_json()
    log.info(f"收到数据::{receive}")
    try:
        table = receive['table']
        condition = receive['condition']
        column = receive['column']
        limit = receive.get('limit',100)
    except KeyError as keyerr:
        log.error(f"Can Not Found Key::{keyerr}")
        return 'failed'
    res:MessageGen = mysql.select(table,condition,column,limit)
    return jsonify(res.dict())

@app.errorhandler(OSError)
def handle_os_error(e):
    data = MessageGen.false_load(["OSError", str(e)])
    log.error(f"Get Critical Error!\n::{data}")
    response = jsonify(data.dict())
    response.status_code = 500
    return response


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8086)
