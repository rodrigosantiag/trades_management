from datetime import datetime
from typing import Union
from uuid import UUID, uuid4

from pony.orm.core import PrimaryKey, Required, Optional, Set, db_session
from serpens import database

import settings

db = database.Database()


class Broker(db.Entity):
    _table_ = "brokers"

    id = PrimaryKey(int, auto=True)
    uid = Required(UUID, default=uuid4)
    name = Required(str)
    user = Required(lambda: User, column="user_id")
    accounts = Set(lambda: Account)
    created_at = Required(datetime, default=datetime.utcnow)
    updated_at = Required(datetime, default=datetime.utcnow)

    @staticmethod
    @db_session
    def get_by_uid(uid: UUID) -> Union["Broker", None]:
        return Broker.get(uid=uid)


class Account(db.Entity):
    _table_ = "accounts"

    id = PrimaryKey(int, auto=True)
    uid = Required(UUID, default=uuid4)
    type_account = Optional(str, nullable=True)
    currency = Optional(str, nullable=True)
    initial_balance = Optional(float, nullable=True)
    current_balance = Optional(float, nullable=True)
    broker = Required(Broker, column="broker_id")
    user = Required(lambda: User, column="user_id")
    trades = Set(lambda: Trade)
    created_at = Required(datetime, default=datetime.utcnow)
    updated_at = Required(datetime, default=datetime.utcnow)

    @staticmethod
    @db_session
    def get_by_uid(uid: UUID) -> Union["Account", None]:
        return Account.get(uid=uid)


class Strategy(db.Entity):
    _table_ = "strategies"

    id = PrimaryKey(int, auto=True)
    uid = Required(UUID, default=uuid4)
    name = Optional(str, nullable=True)
    user = Required(lambda: User, column="user_id")
    trades = Set(lambda: Trade)
    created_at = Required(datetime, default=datetime.utcnow)
    updated_at = Required(datetime, default=datetime.utcnow)

    @staticmethod
    @db_session
    def get_by_uid(uid: UUID) -> Union["Strategy", None]:
        return Strategy.get(uid=uid)


class Trade(db.Entity):
    _table_ = "trades"

    id = PrimaryKey(int, auto=True)
    uid = Required(UUID, default=uuid4)
    value = Optional(float, nullable=True)
    profit = Optional(float, nullable=True)
    result = Optional(bool, nullable=True)
    result_balance = Optional(float, nullable=True)
    type_trade = Optional(str, nullable=True)
    account = Required(Account, column="account_id")
    user = Required(lambda: User, column="user_id")
    strategy = Required(Strategy, column="strategy_id")
    created_at = Required(datetime, default=datetime.utcnow)
    updated_at = Required(datetime, default=datetime.utcnow)

    @staticmethod
    @db_session
    def get_by_uid(uid: UUID) -> Union["Trade", None]:
        return Trade.get(uid=uid)


class User(db.Entity):
    _table_ = "users"

    id = PrimaryKey(int, auto=True)
    uid = Required(UUID, default=uuid4)
    encrypted_password = Required(str)
    confirmed_at = Optional(datetime, nullable=True)
    unconfirmed_email = Optional(str, nullable=True)
    name = Optional(str, nullable=True)
    email = Optional(str, nullable=True)
    risk = Optional(int, nullable=True)
    brokers = Set(Broker)
    accounts = Set(Account)
    strategies = Set(Strategy)
    trades = Set(Trade)
    created_at = Required(datetime, default=datetime.utcnow)
    updated_at = Required(datetime, default=datetime.utcnow)


if settings.DATABASE_URL:  # pragma: no cover
    db.bind(mapping=True)
