from pydantic import BaseModel,constr,StrictInt
from datetime import datetime
email_str = "^[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$"
class BaseInfo(BaseModel):
    stdid : constr(min_length=12, max_length=12)
    name : constr(max_length=24)
    sex : constr(max_length=2)
    tel : constr(max_length=12)
    mail : constr(max_length=24) = None

class BaseTarget(BaseModel):
    stdid : constr(min_length=12, max_length=12)
    f_target : constr(max_length=12)
    s_target : constr(max_length=12) = None
    t_target : constr(max_length=12) = None

class CheckIn(BaseModel):
    stdid : constr(min_length=12, max_length=12)
    checkTime : datetime = None
    expectTime : datetime = datetime.now()
    remarks : str = ""

class Department(BaseModel):
    dpid : constr(max_length=6,min_length=6)
    dpname : constr(max_length=12)
    recruit : StrictInt = 20
    manager : constr(min_length=12,max_length=12) = None

class Interview(BaseModel):
    stdid : constr(min_length=12, max_length=12)
    group : constr(min_length=6,max_length=6)
    startTime : datetime = None
    endTime : datetime = None

class Mark(BaseModel):
    stdid : constr(min_length=12, max_length=12)
    reviews : str = ""
    grade : float = -1.0
    mhr : constr(min_length=12,max_length=12)
    shr : constr(min_length=12,max_length=12)

class Series(BaseModel):
    groupid : constr(max_length=6)
    name : str

class Staff(BaseModel):
    stfid : constr(min_length=12, max_length=12)
    privilege : StrictInt = 4
    worktime : datetime = None
    tel : constr(max_length=12)
    group : constr(max_length=6)