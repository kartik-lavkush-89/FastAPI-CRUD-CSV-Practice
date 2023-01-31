"""PYDATNIC  MODELS"""

from pydantic import BaseModel

'''Models for CRUD operations'''

class User(BaseModel):
    username : str
    email : str
    phone : int
    password : str
    
class UserIn(BaseModel):
    username : str
    email : str
    password : str


'''Models for Login and SignUp'''

#base model for sending OTP to phone number
class Phone(BaseModel):
    phone : int

class Signup(BaseModel):
    username : str
    email : str
    phone : int
    otp : int
    password : str

class Login(BaseModel):
    email : str
    password : str
    
#base model for sending OTP to email ID    
class Email(BaseModel):
    email : str

class Forgot(BaseModel):
    email : str
    password : str
    otp : int
