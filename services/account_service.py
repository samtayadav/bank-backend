from models import Account, UpdateAccount
from repositories import account_repository
from services.exceptions import AccountNotFoundError


async def create_account(account: Account, current_user: dict) -> str:
    return await account_repository.create_account(account.model_dump(), current_user["_id"])


async def get_accounts(current_user: dict) -> list[dict]:
    return await account_repository.get_accounts(current_user["_id"])


async def update_account(account_id: str, data: UpdateAccount, current_user: dict) -> None:
    account_data = data.model_dump(exclude_none=True)
    matched_count = await account_repository.update_account(
        account_id,
        account_data,
        current_user["_id"],
    )
    if matched_count == 0:
        raise AccountNotFoundError


async def delete_account(account_id: str, current_user: dict) -> None:
    deleted_count = await account_repository.delete_account(account_id, current_user["_id"])
    if deleted_count == 0:
        raise AccountNotFoundError
