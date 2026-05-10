from pydantic import BaseModel
from typing import Optional

class Account(BaseModel):
    account_holder: str
    account_number: str
    bank_name: str
    balance: float
    account_type: str

class UpdateAccount(BaseModel):
    account_holder: Optional[str] = None
    bank_name: Optional[str] = None
    balance: Optional[float] = None
    account_type: Optional[str] = None