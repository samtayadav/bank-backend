from fastapi import APIRouter, Depends, HTTPException

from models import Account, UpdateAccount
from security import get_current_user
from services import account_service
from services.exceptions import AccountNotFoundError

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("")
async def create_account(account: Account, current_user: dict = Depends(get_current_user)):
    account_id = await account_service.create_account(account, current_user)
    return {"id": account_id, "message": "Account created!"}


@router.get("")
async def get_accounts(current_user: dict = Depends(get_current_user)):
    return await account_service.get_accounts(current_user)


@router.put("/{account_id}")
async def update_account(
    account_id: str,
    data: UpdateAccount,
    current_user: dict = Depends(get_current_user),
):
    try:
        await account_service.update_account(account_id, data, current_user)
    except AccountNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Account not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"message": "Updated!"}


@router.delete("/{account_id}")
async def delete_account(account_id: str, current_user: dict = Depends(get_current_user)):
    try:
        await account_service.delete_account(account_id, current_user)
    except AccountNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Account not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"message": "Deleted!"}
