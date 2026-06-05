from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


OrderStatus = Literal["created", "paid", "payment_failed", "cancelled"]


class OrderItemCreate(BaseModel):
    product_id: str
    quantity: int = Field(ge=1)


class OrderCreate(BaseModel):
    user_id: str
    items: list[OrderItemCreate] = Field(min_length=1)


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: str
    quantity: int
    unit_price: Decimal


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    items: list[OrderItemResponse]
    total_amount: Decimal
    currency: Literal["USD"]
    status: OrderStatus
    created_at: datetime
    updated_at: datetime


class UserContract(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    status: Literal["active", "blocked", "deleted"]
    created_at: datetime


class ProductContract(BaseModel):
    id: str
    name: str
    description: str
    price: Decimal
    currency: Literal["USD"]
    stock: int
    status: Literal["active", "archived"]
    created_at: datetime
    updated_at: datetime


class PaymentAuthorizeRequest(BaseModel):
    order_id: str
    amount: Decimal
    currency: Literal["USD"] = "USD"


class PaymentContract(BaseModel):
    payment_id: str
    order_id: str
    status: Literal["authorized", "declined", "timeout_simulated"]
    amount: Decimal
    currency: Literal["USD"]


class OrderEventPayload(BaseModel):
    event_type: Literal["order.created", "order.paid", "order.cancelled"]
    event_id: str
    order_id: str
    user_id: str
    occurred_at: datetime
