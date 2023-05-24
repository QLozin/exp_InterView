import sqlite3 as sqli
import configparser as config
from pathlib import Path
from ..logger import mylog as log


class ConfigWeb(object):
    def __init__(self, conf_path='./default.conf') -> None:
        self.config = ConfigWeb._initialize(conf_path)
        self.conn = self.sql_database_initialize()
        self.cursor = self.conn.cursor()

    @staticmethod
    def _initialize(conf_path):
        default_dict = {"path": "default.sql", "db": "flask_db", "table": "user"}
        setting = config.ConfigParser()
        setting["DEFAULT"] = default_dict
        setting.read(conf_path, encoding='utf-8')
        log.info("Initialize config file success.")
        log.debug(f"检查配置文件内容:{setting}")
        return setting

    def sql_database_initialize(self):
        sql_path = self.config['SQL']['path']
        if not Path(sql_path).is_file():
            log.warning(f"SQL文件不存在:{sql_path}")
        return sqli.connect(sql_path)


    def cursor(self,cursor, statement: str):
        flag = "INSERT" in statement or "UPDATE" in statement or "DELETE" in statement
        try:
            self.cursor.execute(statement)
            cursor.commit()
            return True
        except Exception as e:
            log.error(f"SQL执行失败::{e}")
            self.conn.rollback()
            log.warning(f"SQL执行失败，回滚")
            return False
    def create(self):
        self.cursor.execute(f'CREATE DATABASE IF NOT EXISTS `flask_db`')
        self.cursor.execute('USE `user`')
        self.cursor.execute('CREATE ')


if __name__ == '__main__':
    conf = config.ConfigParser()
    conf.read('./default.conf', encoding='utf-8')
    print(conf['SQL'])
