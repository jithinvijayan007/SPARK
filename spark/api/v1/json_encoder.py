from datetime import datetime, date
import json
from uuid import UUID
import enum

# 3rd party imports
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.collections import InstrumentedList


def encode(sqlalchemy_obj) -> dict:
    responseDict = {}

    # Remove invalid fields and just get the column attributes
    columns = [
        x
        for x in dir(sqlalchemy_obj)
        if (not x.startswith("_") and x != "metadata")
    ]
    if 'admin' in columns:
        columns.remove('admin')
    # import pdb;pdb.set_trace()
    for column in columns:
        # if column == "goal_risk_description":
        #     import pdb;pdb.set_trace()
        print("c_name: ", column)
        value = sqlalchemy_obj.__getattribute__(column)

        try:
            json.dumps(value)
            responseDict[column] = value
        except TypeError:
            if isinstance(value, datetime):
                # print(value.strftime("%Y-%m-%d %H:%M:%S"))
                responseDict[column] = value.__str__()
                # responseDict[column] = value.strftime("%Y-%m-%d %H:%M:%S")

            elif isinstance(value, UUID):
                responseDict[column] = value.__str__()
            elif isinstance(value, date):
                responseDict[column] = value.__str__()
            elif isinstance(value, enum.Enum):
                responseDict[column] = str(value).split(".")[1]
            elif isinstance(value, InstrumentedList):
                responseDict[column] = [encode(each_val) for each_val in value]
            else:
                responseDict[column] = None
        except Exception as e:
            print(e)

    return responseDict


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            return encode(obj)
        return json.JSONEncoder.default(self, obj)
