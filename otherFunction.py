from externModel import BaseInfo, BaseTarget, CheckIn, Department, Interview, Mark, Series, Staff
from logger import mylog as log

table_mapping = {
    "baseinfo": BaseInfo,
    "basetarget": BaseTarget,
    "checkin": CheckIn,
    "department": Department,
    "interview": Interview,
    "mark": Mark,
    "series": Series,
    "staff": Staff
}


def insert_splitter(table: str):
    _table = table.lower()
    res = table_mapping.get(_table,None)
    if res is None:
        log.error(f"INSERT SPLITER :: Table {_table} not found")
        raise ValueError(f"STOP :: Table {_table} not found")
    return res
