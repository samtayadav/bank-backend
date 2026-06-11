from datetime import datetime, timezone

from database import client
from models import TransferRequest
from repositories import account_repository, transfer_repository
from services.exceptions import (
    AccountNotFoundError,
    InsufficientBalanceError,
    InvalidTransferError,
    PermissionDeniedError,
    TransferNotFoundError,
)

VALID_STATUSES = {"pending", "approved", "rejected"}


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def create_transfer_request(transfer: TransferRequest, current_user: dict) -> str:
    if transfer.from_account_id == transfer.to_account_id:
        raise InvalidTransferError("Source and destination accounts must be different")

    from_account = await account_repository.get_owned_account_by_id(
        transfer.from_account_id,
        current_user["_id"],
    )
    to_account = await account_repository.get_account_by_id(transfer.to_account_id)

    if not from_account or not to_account:
        raise AccountNotFoundError

    transfer_data = transfer.model_dump()
    transfer_data.update(
        {
            "status": "pending",
            "from_owner_user_id": from_account["owner_user_id"],
            "to_owner_user_id": to_account.get("owner_user_id"),
            "created_at": _now(),
            "approved_at": None,
            "rejected_at": None,
        }
    )
    return await transfer_repository.create_transfer(transfer_data)


async def get_transfers(current_user: dict, status: str | None = None) -> list[dict]:
    if status and status not in VALID_STATUSES:
        raise InvalidTransferError("Invalid transfer status")
    return await transfer_repository.get_user_transfers(current_user["_id"], status=status)


async def approve_transfer(transfer_id: str, current_user: dict) -> None:
    async with await client.start_session() as session:
        async with session.start_transaction():
            transfer = await transfer_repository.get_transfer_by_id(transfer_id, session=session)
            if not transfer:
                raise TransferNotFoundError

            if transfer["status"] != "pending":
                raise InvalidTransferError("Only pending transfers can be approved")

            if transfer.get("from_owner_user_id") != current_user["_id"]:
                raise PermissionDeniedError

            from_account = await account_repository.get_account_by_id(
                transfer["from_account_id"],
                session=session,
            )
            to_account = await account_repository.get_account_by_id(
                transfer["to_account_id"],
                session=session,
            )

            if not from_account or not to_account:
                raise AccountNotFoundError

            amount = transfer["amount"]
            debited_count = await account_repository.debit_balance_if_sufficient(
                transfer["from_account_id"],
                amount,
                session=session,
            )
            if debited_count == 0:
                raise InsufficientBalanceError

            await account_repository.increment_balance(
                transfer["to_account_id"],
                amount,
                session=session,
            )
            await transfer_repository.update_transfer_status(
                transfer_id,
                "approved",
                {"approved_at": _now()},
                session=session,
            )


async def reject_transfer(transfer_id: str, current_user: dict) -> None:
    transfer = await transfer_repository.get_transfer_by_id(transfer_id)
    if not transfer:
        raise TransferNotFoundError

    if current_user["_id"] not in {
        transfer.get("from_owner_user_id"),
        transfer.get("to_owner_user_id"),
    }:
        raise PermissionDeniedError

    if transfer["status"] != "pending":
        raise InvalidTransferError("Only pending transfers can be rejected")

    await transfer_repository.update_transfer_status(
        transfer_id,
        "rejected",
        {"rejected_at": _now()},
    )
