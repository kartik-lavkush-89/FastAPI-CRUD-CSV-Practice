"""PYDATNIC  MODELS"""

from pydantic import BaseModel

class User(BaseModel):
    username : str
    email : str
    phone : int
    password : str
    
class UserIn(BaseModel):
    username : str
    email : str
    password : str
    
