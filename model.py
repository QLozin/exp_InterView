from pydantic import BaseModel, constr, StrictInt
from typing import Union
from externModel import BaseInfo
class Message(BaseModel):
    status: Union[int, bool] = 1
    code: int = -1
    msg: str = ""
    data: dict = {}

    @classmethod
    def loading(cls, data: Union[list, dict]):
        if isinstance(data, list) and len(data) == 4:
            return cls(status=data[0], code=data[1], msg=data[2], data=data[3])
        elif isinstance(data, dict):
            return cls.parse_obj(data)
        else:
            raise TypeError("Data Error")


class MessageGen(Message):
    """
    通用消息器，有true_load和false_load两个方法，分别返回成功和失败的消息\n
    """
    status: Union[bool, int] = 1
    code: int = 1

    @staticmethod
    def _inner(data: Union[list, dict], _bool: Union[bool, int] = 1):
        _bool = 1 if _bool else 0
        if isinstance(data, list):
            if len(data) == 4:
                return MessageGen.loading([_bool, data[1], data[2], data[3]])
            elif len(data) == 3:
                return MessageGen.loading([_bool, data[0], data[1], data[2]])
            elif len(data) == 2:
                return MessageGen.loading([_bool, 1, data[0], data[1]])
            else:
                raise TypeError("Data Length Error")
        elif isinstance(data, dict):
            data["status"] = _bool
            return MessageGen.parse_obj(data)
        else:
            raise TypeError("Data Error")

    @classmethod
    def true_load(cls, data: Union[list, dict, str]):
        """
        成功消息\n
        :param data: 消息体，字典|字符串，列表最长为4
        :return: BaseModel
        """
        if isinstance(data, str):
            return cls._inner([data, {}], 1)
        return cls._inner(data, 1)

    @classmethod
    def false_load(cls, data: Union[list, dict, str]):
        """
        失败消息\n
        :param data: 消息体，字典|字符串，列表最长为4
        :return: BaseModel
        """
        if isinstance(data, str):
            return cls._inner([data, {}], 0)
        return cls._inner(data, 0)


class _BaseInfo(BaseModel):
    """
    该方法已经被externalModel里的BaseInfo取代
    """
    stdid: constr(min_length=12, max_length=12)
    name: constr(max_length=24)
    sex: constr(max_length=6)
    tel: constr(max_length=12)
    mail: constr(max_length=24)


class ReceiveBaseInfo(BaseModel):
    table: str
    data: BaseInfo


class DeleteMessage(BaseModel):
    table: str
    condition: str


class SQLMessage(BaseModel):
    hstname: str = "127.0.0.1"
    usrname: str = "root"
    dbname: str = "test"
    passwd: str = ""
    port: int = 3306


class GeneralMessage(BaseModel):
    table: str
    #control: constr(regex="[SELECT,DELETE,UPDATE,INSERT]") = "Any"
    #token: constr(min_length=32, max_length=32) = "root"
    multiple: StrictInt = 0
    data: dict


