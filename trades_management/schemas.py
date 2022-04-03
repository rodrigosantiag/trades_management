from dataclasses import dataclass, field
from datetime import datetime

from serpens.schema import Schema


@dataclass
class BrokerSchema(Schema):
    name: str
    user_id: int = None
    uid: str = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
