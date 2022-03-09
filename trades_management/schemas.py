from dataclasses import dataclass, field
from datetime import datetime

from serpens.schema import Schema


@dataclass
class BrokerSchema(Schema):
    name: str
    # TODO: temporary adds here user_id. In future associate user to broker through authentication
    user_id: int
    uid: str = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
