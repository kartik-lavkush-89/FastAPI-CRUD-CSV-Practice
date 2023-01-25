from fastapi import APIRouter, HTTPException, requests, Response
from src.models.user import User, UserIn
from bson import ObjectId
from datetime import datetime
from src.schemas.user import userEntity, usersEntity
import csv
import json
from pymongo import MongoClient
conn = MongoClient()

app1 = APIRouter()


"""ROUTES"""





'''GETTING user details'''


'''GETTING all user records'''

@app1.get('/users')
async def get_all_users():
    print (conn.local.user.find())
    return usersEntity(conn.local.user.find())
    

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
    with open(csv_file, "w", newline="") as f:

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
        with open(csv_file, "w", ) as f:


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
    csv_file = "csvfiles/{}.csv".format(file)
    try: 
        with open(csv_file, "r") as f:
            
                csv_reader = csv.DictReader(f)
                data = []
                for row in csv_reader:
                    data.append(row)
                    
        return data
    except :
        raise HTTPException(status_code=404, detail="file_doesn't_exist!")
   