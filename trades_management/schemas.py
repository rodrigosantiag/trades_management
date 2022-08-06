from dataclasses import dataclass, field
from datetime import datetime

from serpens.schema import Schema


@dataclass
class BrokerSchema(Schema):
    name: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AccountSchema(Schema):
    type_account: str
    currency: str
    initial_balance: float
    current_balance: float = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        super().__post_init__()

        if self.current_balance is None:
            self.current_balance = self.initial_balance


@dataclass
class StrategySchema(Schema):
    name: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
