from flask import Flask, request, jsonify
from logger import mylog as log
from SQL.mainSQL import SQL
from model import ReceiveBaseInfo, MessageGen, DeleteMessage, SQLMessage
from otherFunction import insert_splitter
app = Flask(__name__)
mysql = SQL(passwd="mysql@root", dbname="experiment")


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/sql', methods=['POST'])
def web_sql():
    receive = request.get_json()
    log.info(f"收到数据::{receive}")
    try:
        receive_SQL = SQLMessage.parse_obj(receive)
    except Exception as e:
        log.error(e)
        return 'SQL Connected Failed'
    res: MessageGen = mysql.reconnect(**receive_SQL.dict())
    return jsonify(res.dict())


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
    res: MessageGen = mysql.insert(data.table, data.data.dict())
    return jsonify(res.dict())


@app.route('/api', methods=['POST', 'GET'])
def api():
    if request.method != 'POST':
        return "Support POST Method Only"
    receive = request.get_json()
    log.info(f"收到数据::{receive}")
    try:
        model = receive['control'].lower()
        table = receive['table']
        re_data = receive['data'] if isinstance(receive['data'], (dict,list)) else {}
        log.debug(f"检查数据获取状态::{model}*{type(model)}+++{table}*{type(table)}+++{re_data}*{type(re_data)}")
    except KeyError as e:
        log.error(f"Can Not Found Key::{e}")
        return 'Key Not Found Error Occurred'
    except Exception as e:
        log.critical(f"Unknown FATAL Error Occurred::{e}")
        return "Failed"
    if model == "insert":
        log.info(f"Using INSERT Model")
        data_filter = insert_splitter(table).parse_obj(re_data)
        log.success(f"Loading Data Successfully")
        res: MessageGen = mysql.insert(table, data_filter.dict())
    elif model == "delete":
        res: MessageGen = mysql.delete(table, re_data.get('condition', None))
    elif model == "select":
        condition = re_data.get('condition', None)
        column = re_data.get('column', None)
        limit = re_data.get('limit', -1)
        if limit == -1:
            log.warning(f"Value limit Missing, Using Default Value -1")
        if column is None or condition is None:
            log.error(f"ValueError::column or condition is None")
            condition = "" if condition is None else condition
            column = "*" if column is None else column
        res: MessageGen = mysql.select(table, condition, column, limit)
    elif model == "update":
        if isinstance(re_data, list) and len(re_data) >= 1:
            res: MessageGen = mysql.update(table, "", 0, "", re_data)
        else:
            _condition = re_data.get('condition', None)
            if _condition is None:
                log.error(f"condition not should be None")
                return "Failed"
            res: MessageGen = mysql.update(table, re_data.get('key', None), re_data.get('value', None),
                                           _condition)
    else:
        log.error(f"Unknown Model::{model}")
        return 'Unknown Model'
    return jsonify(res.dict())


@app.route('/insert', methods=['POST'])
def general_insert():
    """
    通用插入方法，JSON格式应该为{"table":table_name,"data":{...}}
    :return:
    """
    receive = request.get_json()
    log.info(f"收到数据::{receive}")
    try:
        table = receive['table']
        data = receive['data']
    except KeyError as e:
        log.error(f"Can Not Found Key::{e}")
        return 'Key Not Found Error Occurred'
    except Exception as ue:
        log.critical(f"Critical Unknown Error::{ue}")
        return 'Unknown Error Occurred'
    res: MessageGen = mysql.insert(table, data)
    return jsonify(res.dict())


@app.route('/delete', methods=['POST'])
def delete():
    receive = request.get_json()
    log.info(f"收到数据::{receive}")
    print(receive)
    try:
        data = DeleteMessage(**receive)
        log.info(f"成功解析数据::{data}")
    except KeyError as e:
        log.error(f"Can Not Found Key::{e}")
        return 'Key Not Found Error Occurred'
    except Exception as e:
        log.critical(e)
        return 'Unknown Error Occurred'
    res: MessageGen = mysql.delete(data.table, data.condition)
    return jsonify(res.dict())


@app.route('/update', methods=['POST'])
def update():
    receive = request.get_json()
    try:
        table = receive['table']
        key = receive['data']['key']
        value = receive['data']['value']
        condition = receive['data']['condition']
    except KeyError as e:
        log.error(f"Can Not Found Key::{e}")
        return 'Key Not Found Error Occurred'
    except Exception as e:
        log.critical(e)
        return 'Unknown Error Occurred'
    log.info(f"收到数据::UPDATE {table} SET {key} = {value} WHERE {condition}")
    res: MessageGen = mysql.update(table, key, value, condition)
    return jsonify(res.dict())


@app.route('/select', methods=['POST'])
def select():
    receive = request.get_json()
    log.info(f"收到数据::{receive}")
    try:
        table = receive['table']
        condition = receive['condition']
        column = receive['column']
        limit = receive.get('limit', 100)
    except KeyError as keyerr:
        log.error(f"Can Not Found Key::{keyerr}")
        return 'failed'
    res: MessageGen = mysql.select(table, condition, column, limit)
    return jsonify(res.dict())


@app.errorhandler(OSError)
def handle_os_error(e):
    data = MessageGen.false_load(["OSError", str(e)])
    log.error(f"Get Critical Error!\n::{data}")
    response = jsonify(data.dict())
    response.status_code = 500
    return response


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8086)
