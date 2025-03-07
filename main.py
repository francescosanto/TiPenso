import firebase_admin
from firebase_admin import credentials, auth
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import sqlite3
from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

app = FastAPI()

class LoginRequest(BaseModel):
    token: str  # Token ID ricevuto da Firebase Authentication

@app.post("/login/")
async def login(request: LoginRequest):
    try:
        decoded_token = auth.verify_id_token(request.token)
        return {"uid": decoded_token["uid"], "email": decoded_token.get("email")}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")


class DevicePairRequest(BaseModel):
    device1: str
    device2: str

@app.post("/pair_devices/")
async def pair_devices(request: DevicePairRequest):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO device_pairs (device1, device2) VALUES (?, ?)", 
                   (request.device1, request.device2))
    conn.commit()
    conn.close()
    return {"message": "Devices paired successfully"}

# 🔥 Inserisci la tua Firebase Server Key qui 🔥
FCM_SERVER_KEY = "BKmmkLxRJawGGDqcLnE_g8JSHX20RSWFKXhEz9wIGZNL_PVlZTTnW8qyZRVZ-qOVNHQeuTyFmyi2jDmXeyblAKk"

class NotificationRequest(BaseModel):
    token: str  # Il token del dispositivo che riceve la notifica
    title: str
    body: str

@app.post("/send_notification/")
async def send_notification(request: NotificationRequest):
    headers = {
        "Authorization": f"key={FCM_SERVER_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "to": request.token,
        "notification": {
            "title": request.title,
            "body": request.body
        }
    }
    response = requests.post("https://fcm.googleapis.com/fcm/send", json=data, headers=headers)
    return response.json()

