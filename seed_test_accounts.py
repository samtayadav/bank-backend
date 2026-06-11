import asyncio

from bson import ObjectId

from database import collection, users_collection
from security import _hash_password

DEMO_USERS = [
    {
        "_id": ObjectId("6a1000000000000000000001"),
        "username": "demo1",
        "password": "password1",
    },
    {
        "_id": ObjectId("6a1000000000000000000002"),
        "username": "demo2",
        "password": "password2",
    },
]


TEST_ACCOUNTS = [
    {
        "account_holder": "Aarav Sharma",
        "account_number": "1001001001",
        "bank_name": "State Bank of India",
        "balance": 24500.75,
        "account_type": "savings",
        "phone": "9876543210",
        "email": "aarav.sharma@example.com",
        "branch_name": "Delhi Main",
        "ifsc_code": "SBIN0001234",
    },
    {
        "account_holder": "Priya Patel",
        "account_number": "1001001002",
        "bank_name": "HDFC Bank",
        "balance": 58210.0,
        "account_type": "current",
        "phone": "9876543211",
        "email": "priya.patel@example.com",
        "branch_name": "Ahmedabad CG Road",
        "ifsc_code": "HDFC0000456",
    },
    {
        "account_holder": "Rohan Gupta",
        "account_number": "1001001003",
        "bank_name": "ICICI Bank",
        "balance": 15780.5,
        "account_type": "savings",
        "phone": "9876543212",
        "email": "rohan.gupta@example.com",
        "branch_name": "Mumbai Andheri",
        "ifsc_code": "ICIC0000789",
    },
    {
        "account_holder": "Sneha Iyer",
        "account_number": "1001001004",
        "bank_name": "Axis Bank",
        "balance": 74000.25,
        "account_type": "fixed",
        "phone": "9876543213",
        "email": "sneha.iyer@example.com",
        "branch_name": "Chennai T Nagar",
        "ifsc_code": "UTIB0000123",
    },
    {
        "account_holder": "Vikram Singh",
        "account_number": "1001001005",
        "bank_name": "Punjab National Bank",
        "balance": 9800.0,
        "account_type": "recurring",
        "phone": "9876543214",
        "email": "vikram.singh@example.com",
        "branch_name": "Jaipur MI Road",
        "ifsc_code": "PUNB0002345",
    },
    {
        "account_holder": "Neha Verma",
        "account_number": "1001001006",
        "bank_name": "Kotak Mahindra Bank",
        "balance": 32650.9,
        "account_type": "savings",
        "phone": "9876543215",
        "email": "neha.verma@example.com",
        "branch_name": "Pune Camp",
        "ifsc_code": "KKBK0000567",
    },
    {
        "account_holder": "Arjun Reddy",
        "account_number": "1001001007",
        "bank_name": "Canara Bank",
        "balance": 45120.4,
        "account_type": "current",
        "phone": "9876543216",
        "email": "arjun.reddy@example.com",
        "branch_name": "Hyderabad Banjara Hills",
        "ifsc_code": "CNRB0000987",
    },
    {
        "account_holder": "Kavya Nair",
        "account_number": "1001001008",
        "bank_name": "Bank of Baroda",
        "balance": 12100.0,
        "account_type": "savings",
        "phone": "9876543217",
        "email": "kavya.nair@example.com",
        "branch_name": "Kochi MG Road",
        "ifsc_code": "BARB0MGROAD",
    },
    {
        "account_holder": "Manish Kumar",
        "account_number": "1001001009",
        "bank_name": "Union Bank of India",
        "balance": 66750.6,
        "account_type": "fixed",
        "phone": "9876543218",
        "email": "manish.kumar@example.com",
        "branch_name": "Lucknow Hazratganj",
        "ifsc_code": "UBIN0003456",
    },
    {
        "account_holder": "Meera Joshi",
        "account_number": "1001001010",
        "bank_name": "IDFC FIRST Bank",
        "balance": 21990.35,
        "account_type": "recurring",
        "phone": "9876543219",
        "email": "meera.joshi@example.com",
        "branch_name": "Bengaluru Indiranagar",
        "ifsc_code": "IDFB0080123",
    },
]


async def main():
    upserted = 0
    modified = 0

    for user in DEMO_USERS:
        await users_collection.update_one(
            {"username": user["username"]},
            {
                "$setOnInsert": {
                    "_id": user["_id"],
                    "username": user["username"],
                    "password_hash": _hash_password(user["password"]),
                }
            },
            upsert=True,
        )

    for index, account in enumerate(TEST_ACCOUNTS):
        owner = DEMO_USERS[index % len(DEMO_USERS)]
        account["owner_user_id"] = str(owner["_id"])
        result = await collection.update_one(
            {"account_number": account["account_number"]},
            {"$set": account},
            upsert=True,
        )
        upserted += 1 if result.upserted_id else 0
        modified += result.modified_count

    total = await collection.count_documents({})
    print(f"Seed complete: {upserted} inserted, {modified} updated, {total} total accounts.")
    print("Demo logins: demo1/password1 and demo2/password2")


if __name__ == "__main__":
    asyncio.run(main())
