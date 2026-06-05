from datetime import datetime
from decimal import Decimal
from typing import Literal

import pytest
from pydantic import BaseModel, EmailStr


pytestmark = pytest.mark.contract


class UserResponseContract(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    status: Literal["active", "blocked", "deleted"]
    created_at: datetime


class ProductResponseContract(BaseModel):
    id: str
    name: str
    description: str
    price: Decimal
    currency: Literal["USD"]
    stock: int
    status: Literal["active", "archived"]
    created_at: datetime
    updated_at: datetime


class OrderEventContract(BaseModel):
    event_type: Literal["order.created", "order.paid", "order.cancelled"]
    event_id: str
    order_id: str
    user_id: str
    occurred_at: datetime


def test_user_contract_consumed_by_order_service(create_user):
    user = create_user()

    validated = UserResponseContract.model_validate(user)

    assert validated.status == "active"


def test_product_contract_consumed_by_order_service(create_product):
    product = create_product(stock=4)

    validated = ProductResponseContract.model_validate(product)

    assert validated.currency == "USD"
    assert validated.stock == 4


def test_order_event_contract_shape():
    event = OrderEventContract.model_validate(
        {
            "event_type": "order.paid",
            "event_id": "11111111-1111-1111-1111-111111111111",
            "order_id": "22222222-2222-2222-2222-222222222222",
            "user_id": "33333333-3333-3333-3333-333333333333",
            "occurred_at": "2026-01-01T00:00:00Z",
        }
    )

    assert event.event_type == "order.paid"
