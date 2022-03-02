from datetime import datetime
from uuid import UUID, uuid4

from pony.orm.core import PrimaryKey, Required, Optional
from serpens import database

import settings

db = database.Database()


class User(db.Entity):
    _table_ = "users"

    id = PrimaryKey(int, auto=True)
    uid = Required(UUID, default=uuid4)
    encrypted_password = Required(str)
    confirmed_at = Optional(str, nullable=True)
    unconfirmed_email = Optional(str, nullable=True)
    name = Optional(str, nullable=True)
    email = Optional(str, nullable=True)
    risk = Optional(int, nullable=True)
    created_at = Required(datetime, default=datetime.utcnow)
    updated_at = Required(datetime, default=datetime.utcnow)


if settings.DATABASE_URL:  # pragma: no cover
    db.bind(mapping=True)
