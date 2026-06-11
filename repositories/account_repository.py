from bson import ObjectId
from bson.errors import InvalidId

from database import collection


def _to_object_id(account_id: str) -> ObjectId:
    try:
        return ObjectId(account_id)
    except InvalidId as exc:
        raise ValueError("Invalid account id") from exc


def _serialize_account(account: dict) -> dict:
    account["_id"] = str(account["_id"])
    return account


async def get_account_by_id(account_id: str, session=None) -> dict | None:
    account = await collection.find_one({"_id": _to_object_id(account_id)}, session=session)
    if not account:
        return None
    return _serialize_account(account)


async def get_owned_account_by_id(account_id: str, owner_user_id: str, session=None) -> dict | None:
    account = await collection.find_one(
        {"_id": _to_object_id(account_id), "owner_user_id": owner_user_id},
        session=session,
    )
    if not account:
        return None
    return _serialize_account(account)


async def create_account(account_data: dict, owner_user_id: str) -> str:
    account_data["owner_user_id"] = owner_user_id
    result = await collection.insert_one(account_data)
    return str(result.inserted_id)


async def get_accounts(owner_user_id: str, limit: int = 100) -> list[dict]:
    accounts = await collection.find({"owner_user_id": owner_user_id}).to_list(limit)
    return [_serialize_account(account) for account in accounts]


async def update_account(account_id: str, account_data: dict, owner_user_id: str) -> int:
    result = await collection.update_one(
        {"_id": _to_object_id(account_id), "owner_user_id": owner_user_id},
        {"$set": account_data},
    )
    return result.matched_count


async def delete_account(account_id: str, owner_user_id: str) -> int:
    result = await collection.delete_one(
        {"_id": _to_object_id(account_id), "owner_user_id": owner_user_id}
    )
    return result.deleted_count


async def increment_balance(account_id: str, amount: float, session=None) -> int:
    result = await collection.update_one(
        {"_id": _to_object_id(account_id)},
        {"$inc": {"balance": amount}},
        session=session,
    )
    return result.matched_count


async def debit_balance_if_sufficient(account_id: str, amount: float, session=None) -> int:
    result = await collection.update_one(
        {"_id": _to_object_id(account_id), "balance": {"$gte": amount}},
        {"$inc": {"balance": -amount}},
        session=session,
    )
    return result.matched_count
