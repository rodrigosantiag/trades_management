from datetime import datetime
from uuid import uuid4

from pony.orm.core import db_session

from entities import User, Broker


@db_session
def create_sample_user():
    return User(
        uid=uuid4(),
        encrypted_password="test123",
        confirmed_at=datetime(2021, 1, 1, 0, 0, 0),
        name="John Doe",
        email="foo@bar.com",
        risk=7,
        created_at=datetime(1970, 1, 1, 0, 0, 0),
        updated_at=datetime(1970, 1, 1, 0, 0, 0),
    )


@db_session
def create_sample_broker():
    return Broker(
        uid=uuid4(),
        name="Test Broker",
        user=create_sample_user(),
        created_at=datetime(2022, 2, 1, 0, 0, 0),
        updated_at=datetime(2022, 2, 1, 0, 0, 0),
    )
