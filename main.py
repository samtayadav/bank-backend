from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
from database import collection
from models import Account, UpdateAccount

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def fix_id(doc):
    doc["_id"] = str(doc["_id"])
    return doc

@app.get("/")
async def root():
    return {"message": "Bank API Working!"}

@app.post("/accounts")
async def create_account(account: Account):
    result = await collection.insert_one(account.dict())
    return {"id": str(result.inserted_id), "message": "Account created!"}

@app.get("/accounts")
async def get_accounts():
    accounts = await collection.find().to_list(100)
    return [fix_id(a) for a in accounts]

@app.put("/accounts/{id}")
async def update_account(id: str, data: UpdateAccount):
    await collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": data.dict(exclude_none=True)}
    )
    return {"message": "Updated!"}

@app.delete("/accounts/{id}")
async def delete_account(id: str):
    await collection.delete_one({"_id": ObjectId(id)})
    return {"message": "Deleted!"}