from dataclasses import dataclass, field
from datetime import datetime
from typing import Union, List

from serpens.schema import Schema

import enums


@dataclass
class ErrorResponse(Schema):
    type: enums.ErrorCode
    errors: list

    @classmethod
    def create(cls, code: enums.ErrorCode, messages: Union[List[str], str, None] = None):
        pass


@dataclass
class BrokerSchema(Schema):
    name: str
    user_id: int = None
    uid: str = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AccountSchema(Schema):
    type_account: str
    currency: str
    initial_balance: float
    broker_id: int
    user_id: int
    current_balance: float = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
