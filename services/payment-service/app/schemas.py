from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


PaymentMode = Literal["success", "failure", "timeout", "random"]
PaymentStatus = Literal["authorized", "declined", "timeout_simulated"]


class PaymentModeUpdate(BaseModel):
    mode: PaymentMode


class PaymentAuthorizeRequest(BaseModel):
    order_id: str
    amount: Decimal = Field(gt=0)
    currency: Literal["USD"] = "USD"


class PaymentResponse(BaseModel):
    payment_id: str
    order_id: str
    status: PaymentStatus
    amount: Decimal
    currency: Literal["USD"]


class PaymentModeResponse(BaseModel):
    mode: PaymentMode
