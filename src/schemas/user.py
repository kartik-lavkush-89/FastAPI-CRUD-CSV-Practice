from pydantic import validator
import datetime

"""SCHEMAS"""


'''SCHEMA for returning single user data record'''

def userEntity(item) -> dict:
    return {
        "id" : str(item["_id"]),
        "username" : item["username"],
        "email" : item["email"],
        "phone" : item["phone"],
        # "password" : item["password"],
        
    }

@validator("date_created")
def convert_date_created_to_datetime(cls, value):
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")



'''SCHEMA for returning multiple user data records'''

def usersEntity(entity) -> list:
    return [userEntity(item) for item in entity]
    