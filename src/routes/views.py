from fastapi import APIRouter, HTTPException, Response, Header
from starlette.responses import JSONResponse
from src.models.user import User, UserIn, Phone, Signup, Login, Email, Forgot
from bson import ObjectId
import datetime
from src.schemas.user import userEntity, usersEntity
import csv
from twilio.rest import Client
from sendgrid import SendGridAPIClient 
from sendgrid.helpers.mail import Mail
import random
import jwt
import bcrypt
import os
from dotenv import load_dotenv
import json
from pymongo import MongoClient
conn = MongoClient()

app1 = APIRouter()

load_dotenv()

secret_key = os.getenv("SECRET_KEY")



"""ROUTES"""





'''GETTING user details'''


'''GETTING all user records'''

@app1.get('/users')
async def get_all_users():
    a = conn.local.user.find()
    return usersEntity(a)
    

'''GETTING single user record by OBJECT ID'''

@app1.get('/user/{id}')
async def get_one_user(id): 
    a = conn.local.user.find_one({"_id" : ObjectId(id)})
    if a:
        return userEntity(a)
    else:
        raise HTTPException(status_code=404, detail="record_doesn't_exist!")


'''GETTING single user record by phone number'''

@app1.get('/user')
async def get_only_one_user(phone : int): 
    a = conn.local.user.find_one({"phone" : phone})
    if a:
        return userEntity(a)
    else:
        raise HTTPException(status_code=404, detail="record_doesn't_exist!")





'''ADDING user records by making user's phone number and email unique'''


@app1.post('/user')
async def add_user(user : User):
    phone_number = conn.local.user.find_one({"phone" : user.phone})
    email_id = conn.local.user.find_one({"email" : user.email})
    if not phone_number: 
        if not email_id :
                conn.local.user.insert_one(dict(user))
                return {"message" : "data_added_successfully"}
        else:
            raise HTTPException(status_code=404, detail="email_already_exist!")
    else:
        raise HTTPException(status_code=404, detail="phone_already_exist!")





'''UPDATING user records'''


'''UPDATING user's record by OBJECT ID'''

@app1.put('/user/{id}')
async def update_user(id, user : User):
    a = conn.local.user.find_one({"_id" : ObjectId(id)})
    if a:
        conn.local.user.find_one_and_update({"_id" : ObjectId(id)},{"$set" : dict(user)})
        return {"message" : "data_updated_successfully"}
    else:
        raise HTTPException(status_code=404, detail="record_doesn't_exist!")


'''UPDATING user's record by phone number and generating CSV file after performing PUT request'''

@app1.put('/user')
async def update_user(phone : int, details : UserIn):
    user = conn.local.user.find_one({"phone" : phone})
    if user:
        conn.local.user.find_one_and_update({"phone" : phone},{"$set" : dict(details)})
        info = conn.local.user.find_one({"phone" : phone})
        csv_file = "csvfiles/updated_user.csv"  
        with open(csv_file, "w", ) as f:

            csv_writer = csv.writer(f)
            csv_writer.writerow(["_id", "username", "email", "phone"])
            csv_writer.writerow([str(info["_id"]), info["username"], info["email"], info["phone"]])

        return {"message" : "data_updated_successfully"}
    else:
        raise HTTPException(status_code=404, detail="record_doesn't_exist!")





'''DELETING user records'''


'''DELETING  all  user records'''

@app1.delete('/users')
async def delete_all_users():
    conn.local.user.delete_many({})
    return {"message" : "data_deleted"}


'''DELETING single user record by OBJECT ID'''

@app1.delete('/user/{id}')
async def delete_user(id):
    a = conn.local.user.find_one({"_id" : ObjectId(id)})
    if a :
        conn.local.user.find_one_and_delete({"_id" : ObjectId(id)})
        return {"message" : "data_deleted_successfully"}
    else:
        raise HTTPException(status_code=404, detail="record_doesn't_exist!")


'''DELETING single user record by phone number'''

@app1.delete('/user')
async def delete_user(phone : int):
    a = conn.local.user.find_one({"phone" : phone})
    if a :
        conn.local.user.find_one_and_delete({"phone" : phone})
        return {"message" : "data_deleted_successfully"}
    else:
        raise HTTPException(status_code=404, detail="record_doesn't_exist!")






'''GENERATING CSV Files'''



'''DICT-WRITER'''


'''CSV File containing all user's data (all_users.csv)'''

@app1.get("/csv_all")
async def generate_csv():
    users = list(conn.local.user.find())
    csv_file = "csvfiles/all_users.csv"
    with open(csv_file, "w") as f:

        csv_writer = csv.writer(f)
        csv_writer.writerow(["_id", "username", "email", "phone", "password"])
        for user in users:
            csv_writer.writerow([str(user["_id"]), user["username"], user["email"], user["phone"], user["password"]])

    return Response(csv_file, media_type="json/csv")
    

'''CSV File containing single user data (single_user.csv)'''

@app1.get("/csv_single")
async def create_single_user_csv(phone : int):
    user = conn.local.user.find_one({"phone" : phone})
    if user :
        csv_file = "csvfiles/single_user.csv"                                    
        with open(csv_file, "w") as f:


            '''Selected fields will displayed in csv files'''

            # csv_writer = csv.writer(f)
            # csv_writer.writerow(["_id", "username", "email"])
            # csv_writer.writerow([str(user["_id"]), user["username"], user["email"]])


            '''All fields will displayed in csv files'''

            csv_writer = csv.DictWriter(f, fieldnames=["_id","username","email", "phone", "password"])
            csv_writer.writeheader()
            csv_writer.writerow(user)

        return Response(csv_file, media_type="json/csv")
    else : 
        raise HTTPException(status_code=404, detail="record_doesn't_exist!")





'''DICT-READER'''


@app1.get('/dictreader')
async def see(file : str):
    csv_file = f"csvfiles/{file}.csv"
    try: 
        with open(csv_file, "r") as f:
            
                csv_reader = csv.DictReader(f)
                data = []
                for row in csv_reader:
                    data.append(row)
                    
        return data
    except :
        raise HTTPException(status_code=404, detail="file_doesn't_exist!")
   





'''Sign-up route'''



'''Sending OTP to phone number'''

@app1.post('/verify_phone') 
async def otp(phone : Phone):
    phone_number = conn.local.user.find_one({"phone" : phone.phone})
    if not phone_number :
        otp = random.randrange(000000,999999)
        account_sid = os.getenv("ACCOUNT_SID")
        auth_token = os.getenv("AUTH_TOKEN")
        client = Client(account_sid, auth_token)
        message = client.messages.create(
                        body="Hello! Your otp for registration is - " + str(otp),
                        from_="+16086022741",
                        to ='+91' + str(phone.phone)
                    )
        data = {"phone": phone.phone,"otp": otp}
        conn.local.otp.insert_one(dict(data))
        return {"message" : f"OTP_sent_to_{phone.phone}"}
    raise HTTPException(status_code=404, detail = "user_alredy_regitered!")


'''Registering User details by verifying recieved OTP on user's phone number'''

@app1.post('/signup')
async def signup(user : Signup):
    phone_number = conn.local.user.find_one({"phone" : user.phone})
    email_id = conn.local.user.find_one({"email" : user.email})
    if not phone_number: 
        if not email_id :
            phone_otp = conn.local.otp.find_one({"phone" : user.phone})
            if phone_otp : 
                otp = phone_otp.get("otp")


                '''OTP_vrefication'''
                
                if user.otp == otp :     
                    hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())          
                    data = {"username": user.username, "email" : user.email, "phone": user.phone, "password" : hashed_password}
                    conn.local.user.insert_one(dict(data))
                    return {"message" : "OTP_verified!","success": "user_regitered_successfully"}
                
                raise HTTPException(status_code=404, detail="invalid_OTP!")



            else : 
                raise HTTPException(status_code=404, detail="not_recieved_OTP")
        else:
            raise HTTPException(status_code=404, detail="email_already_exist!")
    else:
        raise HTTPException(status_code=404, detail="phone_already_exist!")





'''LOGIN route'''


@app1.post('/login')
async def login(details : Login):
    email_id = conn.local.user.find_one({"email" : details.email})
    if email_id :
        pwd = email_id.get("password")

        if bcrypt.checkpw(details.password.encode(), pwd) :
            payload = {"user_id": details.email, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}
            token = jwt.encode(payload, secret_key, 'HS256')
            return {"message" : "you_are_logged_in_successfully", "token" : token }
       
        
        raise HTTPException(status_code=404, detail="wrong_password!")
     
    raise HTTPException(status_code=404, detail="email_doesn't_exist!")





'''Forgot Password Route'''



'''Sending OTP to user Email ID'''

@app1.post('/verify_mail')
async def otp(email : Email):
    email_id = conn.local.user.find_one({"email" : email.email})

    '''email_verification'''

    if email_id : 
        # email = email_id.get("email")
        otp = random.randrange(000000,999999)
        sg = SendGridAPIClient(os.getenv("SG_API_KEY))
        message = Mail(
                        from_email="kartik.lavkush@unthinkable.co",
                        to_emails= email.email,
                        subject='OTP Verification Code ',
                        html_content = "Your OTP for reset password - " + str(otp)
                        )
        sg.send(message)
        data = {"email": email.email,"otp": otp}
        conn.local.otp.insert_one(dict(data))
        return {"message" : f"OTP_sent_to_{email.email}"}

    raise HTTPException(status_code=404, detail="email_doesn't_exist!")


'''Updating password by verifying recieved OTP on email ID'''

@app1.put('/forgot_password')
async def forgot_password(details : Forgot):
    user = conn.local.user.find_one({"email" : details.email})
    if user:
        email_otp = conn.local.otp.find_one({"email" : details.email}) 
        if email_otp : 
            otp = email_otp.get("otp")

            '''OTP_vrefication'''

            if details.otp == otp :
                hashed_password = bcrypt.hashpw(details.password.encode(), bcrypt.gensalt()) 
                data = {"password" : hashed_password}
                conn.local.user.find_one_and_update({"email" : details.email},{"$set" : dict(data)})
                return {"message" : "OTP_verified!", "success" : "data_updated_successfully"}

            raise HTTPException(status_code=404, detail="invalid_OTP")
        
        
        
        raise HTTPException(status_code=404, detail="not_recieved_OTP")
    else:
        raise HTTPException(status_code=404, detail="record_doesn't_exist!")
