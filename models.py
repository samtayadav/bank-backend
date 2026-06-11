from pydantic import BaseModel, Field
from typing import Optional


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)


class LoginRequest(BaseModel):
    username: str
    password: str


class Account(BaseModel):
    account_holder: str
    account_number: str
    bank_name: str
    balance: float
    account_type: str
    phone: Optional[str] = None
    email: Optional[str] = None
    branch_name: Optional[str] = None
    ifsc_code: Optional[str] = None

class UpdateAccount(BaseModel):
    account_holder: Optional[str] = None
    bank_name: Optional[str] = None
    balance: Optional[float] = None
    account_type: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    branch_name: Optional[str] = None
    ifsc_code: Optional[str] = None

class TransferRequest(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: float = Field(gt=0)
    note: Optional[str] = None
