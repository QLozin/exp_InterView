# normal modules

import pymysql as mysql
from json import dumps
from typing import Union
# customer modules
from logger import mylog as log
from model import MessageGen


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
        self.hstname = hstname
        self.usrname = usrname
        self.dbname = dbname
        self.passwd = passwd
        self.connect = None
        self.spprt = Support()
        self.connection(test_model=0)

    def connection(self, test_model: int = 1):
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
            return self.spprt.message(True, 1, "SQL connection established", {})
        except Exception as e:
            log.warning(f"SQL connection failed: {e}")
            self.connect = None
            return self.spprt.message(False, 0, "SQL connection failed", {})

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
                    return MessageGen.false_load({"code": "1001", "msg": "SQL has not connected"})
                cursor = self.connect.cursor()
                log.debug("Get Cursor Successfully")
                try:
                    log.debug(f"Running Function {func.__name__}")
                    result = func(cursr=cursor, *args, **kwargs)
                    if commit:
                        self.connect.commit()
                    cursor.close()
                    log.success(f"SQL Operate success")
                    return MessageGen.true_load([True, "0001", "SQL Statement Finished", {"result": result}])
                except Exception as e:
                    if commit:
                        self.connect.rollback()
                    log.error(f"SQL Operate failed: {e}")
                    return MessageGen.false_load([False, "1002", f"Execution Err:: {e}", {"result": 0}])

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
        cursr.execute(f"DELETE FROM {target_table} WHERE {condition}")
        return None

    @staticmethod
    def _update(target_table: str, key_name: str, value, condition: str, cursr=None):
        cursr.execute(f"UPDATE {target_table} SET {key_name} = {value} WHERE {condition}")
        return None

    @staticmethod
    def _select(target_table: str, condition: str, col: Union[list, tuple, str] = '*', limit: int = 0, cursr=None):
        column_name = col if isinstance(col, str) else ','.join(col)
        log.debug(f"SELECT {column_name} FROM {target_table} WHERE {condition} LIMIT {limit}")
        cursr.execute(f"SELECT {column_name} FROM {target_table} WHERE {condition} LIMIT {limit}")
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
        log.debug(f"SQL delete: {target_table} {condition}")
        # res = self._delete(target_table, condition)
        res = self._generation_operation(commit=1)(self._delete)(target_table, condition)
        log.debug(f"delete 返回值为 {res}")
        return res

    def update(self, target_table: str, key_name: str, value, condition: str):
        """
        更新记录\n
        :param target_table: 表名
        :param key_name: 列名
        :param value: 值
        :param condition: 条件
        :return: 在修饰器中返回Json{"status": bool, "code": int, "msg": str, "data": dict}
        """
        log.debug(f"SQL Statement:: UPDATE {target_table} SET {key_name} = {value} WHERE {condition}")
        # res = self._update(target_table, key_name, value, condition)
        res = self._generation_operation(commit=1)(self._update)(target_table, key_name, value, condition)
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
        log.debug(f"SQL select: {target_table} {condition} {col} {limit}")
        # res = self._select(target_table, condition, col, limit)
        res = self._generation_operation(commit=0)(self._select)(target_table, condition, col, limit)
        log.debug(f"select 返回值为 {res}")
        return res


if __name__ == '__main__':
    test = SQL(passwd="mysql@root")
    test.insert("test", {"name": "test", "age": 18})
