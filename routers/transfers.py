from fastapi import APIRouter, Depends, HTTPException, Query

from models import TransferRequest
from security import get_current_user
from services import transfer_service
from services.exceptions import (
    AccountNotFoundError,
    InsufficientBalanceError,
    InvalidTransferError,
    PermissionDeniedError,
    TransferNotFoundError,
)

router = APIRouter(prefix="/transfers", tags=["transfers"])


@router.post("")
async def create_transfer_request(
    transfer: TransferRequest,
    current_user: dict = Depends(get_current_user),
):
    try:
        transfer_id = await transfer_service.create_transfer_request(transfer, current_user)
    except AccountNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Account not found") from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=403, detail="You cannot transfer from this account") from exc
    except InvalidTransferError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"id": transfer_id, "message": "Transfer request created!"}


@router.get("")
async def get_transfers(
    status: str | None = Query(default=None),
    current_user: dict = Depends(get_current_user),
):
    try:
        return await transfer_service.get_transfers(current_user, status=status)
    except InvalidTransferError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{transfer_id}/approve")
async def approve_transfer(transfer_id: str, current_user: dict = Depends(get_current_user)):
    try:
        await transfer_service.approve_transfer(transfer_id, current_user)
    except TransferNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Transfer request not found") from exc
    except AccountNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Account not found") from exc
    except InsufficientBalanceError as exc:
        raise HTTPException(status_code=409, detail="Insufficient balance") from exc
    except InvalidTransferError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=403, detail="You cannot approve this transfer") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"message": "Transfer approved!"}


@router.post("/{transfer_id}/reject")
async def reject_transfer(transfer_id: str, current_user: dict = Depends(get_current_user)):
    try:
        await transfer_service.reject_transfer(transfer_id, current_user)
    except TransferNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Transfer request not found") from exc
    except InvalidTransferError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=403, detail="You cannot reject this transfer") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"message": "Transfer rejected!"}
