# normal modules

import pymysql as mysql
from json import dumps
from typing import Union
# customer modules
from logger import mylog as log
from model import MessageGen
from typing import List


class Support(object):
    def __init__(self) -> None:
        self.__dic = {"code": -2, "msg": "", "data": {}, "status": False}

    def message(self, status: bool = False, code: int = -2, msg: str = "", data: dict = None):
        """
        返回事件状态\n
        :param status: 事件状态，布尔值
        :param code: 事件代码，整数，-2表示无效，0表示失败，1表示成功
        :param msg: 事件信息，字符串
        :param data: 事件数据，字典
        """
        dic_copy = self.__dic.copy()
        dic_copy["code"] = code
        dic_copy["msg"] = msg
        dic_copy["data"] = data if data is not None else {}
        dic_copy["status"] = status
        return dumps(dic_copy)

    def get_dict(self):
        return self.__dic.copy()


class SQL(object):
    def __init__(self, hstname: str = '127.0.0.1', usrname: str = 'root', dbname: str = 'experiment',
                 passwd: str = 'root') -> None:
        """
        初始化SQL连接\n
        :param hstname: 主机地址
        :param usrname: 用户名
        :param dbname: 数据库名
        :param passwd: 密码
        """
        self.lazy = True
        self.hstname = hstname
        self.usrname = usrname
        self.dbname = dbname
        self.passwd = passwd
        self.connect = None
        self.spprt = Support()
        self._connection(test_model=0)

    def _connection(self, test_model: int = 1):
        """
        连接数据库或测试连接数据\n
        :param test_model: 1 - 测试连接   0 - 连接数据库
        :return: Json{"status": bool, "code": int, "msg": str, "data": dict}
        """
        try:
            conn = mysql.connect(host=self.hstname, user=self.usrname, db=self.dbname, password=self.passwd)
            log.info(f"SQL connection established")
            if test_model:
                log.debug(f"Testing SQL connection successfully,connection closed")
                conn.close()
            else:
                self.connect = conn
            return MessageGen.true_load([1, "SQL connection established", {}])
        except Exception as e:
            log.warning(f"SQL connection failed: {e}")
            self.connect = None
            return MessageGen.false_load([0, "SQL connection failed", {}])

    def reconnect(self, hstname: str = '127.0.0.1', usrname: str = 'root', dbname: str = 'experiment',
                  passwd: str = 'root'):
        self.hstname = hstname
        self.usrname = usrname
        self.dbname = dbname
        self.passwd = passwd
        return self._connection(test_model=0)

    @log.catch()
    def _generation_operation(self, commit: Union[int, bool] = 1):
        """
        通用SQL语句装饰器，将SQL语句注入后执行、异常处理、回滚或提交、日志记录\n
        :param commit: 是否使用提交模式，0 - 不回滚也不提交 1 - 提交或回滚
        :return: Json{"status": bool, "code": int, "msg": str, "data": dict}
        """

        def wrapper(func):
            def foo(*args, **kwargs):
                if self.connect is None:
                    log.warning(f"SQL has not connected, But be called")
                    return MessageGen.false_load(
                        {"code": "1001", "msg": "SQL has not connected"}) if self.lazy else False
                cursor = self.connect.cursor()
                log.debug("Get Cursor Successfully")
                try:
                    log.debug(f"Running Function {func.__name__}")
                    result = func(cursr=cursor, *args, **kwargs)
                    if commit:
                        self.connect.commit()
                    cursor.close()
                    log.success(f"SQL Operate success")
                    return MessageGen.true_load(
                        ["0001", "SQL Statement Finished", {"result": result}]) if self.lazy else True
                except Exception as e:
                    if commit:
                        self.connect.rollback()
                    log.critical(f"SQL Operate failed: {e}")
                    return MessageGen.false_load(
                        ["1002", f"Execution Err:: {e}", {"result": 0}]) if self.lazy else False

            return foo

        return wrapper

    @staticmethod
    def _insert(target_table: str, values: Union[tuple, dict], cursr=None):
        middle = ""
        if isinstance(values, dict):
            keys = ','.join(values.keys())
            values = tuple(values.values())
            middle = f"({keys})"
        placeholder = ','.join(['%s'] * len(values))
        log.debug(f"\n==EXECUTING STATEMENT==\nINSERT INTO {target_table} {middle} VALUES ({placeholder})({values},)\n")
        cursr.execute(f"INSERT INTO {target_table} {middle} VALUES ({placeholder})", values)
        return None

    @staticmethod
    def _delete(target_table: str, condition: str, cursr=None):
        _condition = condition.lower()
        if "where" in condition:
            log.warning(f"'where' statement should not in condition")
            _condition=_condition.lower().replace("where", "")
            log.info(f"'where' in condition has been removed :statement: {_condition}")
        log.info(f"Execute DELETE FROM {target_table} WHERE {_condition}")
        cursr.execute(f"DELETE FROM {target_table} WHERE {_condition}")
        return None

    @staticmethod
    def _update(target_table: str, key_name: str, value, condition: str, cursr=None):
        if condition != "" and "where" not in condition.lower():
            log.warning(f"Condition is not empty but not INCLUDE 'where'")
            cursr.execute(f"UPDATE {target_table} SET {key_name} = {value} WHERE {condition}")
        cursr.execute(f"UPDATE {target_table} SET {key_name} = {value} {condition}")
        if cursr.rowcount == 0:
            log.warning(f"Update failed, No record has been changed")
        else:
            log.success(f"Update success, {key_name} = {value} has been changed")
        return None

    @staticmethod
    def _select(target_table: str, condition: str, col: Union[list, tuple, str] = '*', limit: int = 100, cursr=None):
        column_name = col if isinstance(col, str) else ','.join(col)
        log.debug(f"SELECT {column_name} FROM {target_table} {condition} LIMIT {limit}")
        if condition != "" and "where" not in condition.lower():
            log.warning(
                f"\nCondition is not empty but not INCLUDE 'where'\nYou can ONLY read 10 records FOR EACH REQUEST")
            cursr.execute(
                f"SELECT {column_name} FROM {target_table} {condition} LIMIT 10 OFFSET {0 if int(limit) < 0 else limit}")
        else:
            cursr.execute(
                f"SELECT {column_name} FROM {target_table} {condition} LIMIT {100 if int(limit) < 0 else limit}")
        return cursr.fetchall()

    def insert(self, target_table: str, values: Union[tuple, dict]):
        """
        插入记录\n
        :param target_table: 表名
        :param values: 值 - 元组或字典
        :return: 在修饰器中返回Json{"status": bool, "code": int, "msg": str, "data": dict}
        """
        log.debug(f"尝试执行SQL语句::表{target_table}||字段{values}")
        # res = self._insert(target_table, values)
        res = self._generation_operation(commit=1)(self._insert)(target_table, values)
        log.debug(f"insert 返回值为 {res}")
        return res

    def delete(self, target_table: str, condition: str):
        """
        删除记录\n
        :param target_table: 表名
        :param condition: 条件
        :return: 在修饰器中返回Json{"status": bool, "code": int, "msg": str, "data": dict}
        """
        log.debug(f"SQL delete: Try To Delete Table {target_table} Where {condition}")
        # res = self._delete(target_table, condition)
        res = self._generation_operation(commit=1)(self._delete)(target_table, condition)
        log.debug(f"delete 返回值为 {res}")
        return res

    def update(self, target_table: str, key_name: str, value, condition: str, multiple: List[dict] = None):
        """
        更新记录\n
        :param multiple:
        :param target_table: 表名
        :param key_name: 列名
        :param value: 值
        :param condition: 条件
        :return: 在修饰器中返回Json{"status": bool, "code": int, "msg": str, "data": dict}
        """
        log.info(f"SQL Statement:: UPDATE {target_table} SET {key_name} = {value} WHERE {condition}")
        res_mid = self._generation_operation(commit=1)(self._update)
        if multiple is None:
            res = res_mid(target_table, key_name, value, condition)
        else:
            tick = 0
            self.lazy = False
            for sm in multiple:
                if not isinstance(sm, dict):
                    log.error(f"Find a non-dict object in multiple list")
                    continue
                res_bool = res_mid(target_table, sm.get('key', None), sm.get('value', None), sm.get('condition', None))
                if res_bool:
                    tick += 1
            self.lazy = True
            res = MessageGen.true_load("Update ALL Done") if tick == len(multiple) else MessageGen.false_load(
                f"Update {tick} Done {len(multiple) - tick} Failed")
        log.debug(f"UPDATE 返回值为 {res}")
        return res

    def select(self, target_table: str, condition: str, col: str = '*', limit: int = 100):
        """
        查询记录\n
        :param target_table: 表名
        :param condition: 条件
        :param col: 显示的行 - 默认显示全部
        :param limit: 限制的行数 - 默认限制100行
        :return: 在修饰器中返回Json{"status": bool, "code": int, "msg": str, "data": dict}
        """
        log.debug(f"SQL select: TABLE: {target_table} COND: {condition} COL: {col} LIMIT: {limit}")
        # res = self._select(target_table, condition, col, limit)
        res = self._generation_operation(commit=0)(self._select)(target_table, condition, col, limit)
        log.debug(f"select 返回值为 {res}")
        return res


if __name__ == '__main__':
    test = SQL(passwd="mysql@root")
    test.insert("test", {"name": "test", "age": 18})
