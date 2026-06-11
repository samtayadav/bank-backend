from bson import ObjectId
from bson.errors import InvalidId

from database import db

transfer_collection = db.transfer_requests


def _to_object_id(transfer_id: str) -> ObjectId:
    try:
        return ObjectId(transfer_id)
    except InvalidId as exc:
        raise ValueError("Invalid transfer id") from exc


def _serialize_transfer(transfer: dict) -> dict:
    transfer["_id"] = str(transfer["_id"])
    return transfer


async def create_transfer(transfer_data: dict) -> str:
    result = await transfer_collection.insert_one(transfer_data)
    return str(result.inserted_id)


async def get_transfer_by_id(transfer_id: str, session=None) -> dict | None:
    transfer = await transfer_collection.find_one(
        {"_id": _to_object_id(transfer_id)},
        session=session,
    )
    if not transfer:
        return None
    return _serialize_transfer(transfer)


async def get_transfers(status: str | None = None, limit: int = 100) -> list[dict]:
    query = {"status": status} if status else {}
    transfers = await transfer_collection.find(query).sort("created_at", -1).to_list(limit)
    return [_serialize_transfer(transfer) for transfer in transfers]


async def get_user_transfers(
    user_id: str,
    status: str | None = None,
    limit: int = 100,
) -> list[dict]:
    query = {
        "$or": [
            {"from_owner_user_id": user_id},
            {"to_owner_user_id": user_id},
        ]
    }
    if status:
        query["status"] = status

    transfers = await transfer_collection.find(query).sort("created_at", -1).to_list(limit)
    return [_serialize_transfer(transfer) for transfer in transfers]


async def update_transfer_status(
    transfer_id: str,
    status: str,
    status_data: dict,
    session=None,
) -> int:
    result = await transfer_collection.update_one(
        {"_id": _to_object_id(transfer_id)},
        {"$set": {"status": status, **status_data}},
        session=session,
    )
    return result.matched_count
