import unittest
from datetime import datetime
from uuid import uuid4

from pony.orm.core import db_session

from entities import Broker, User, Account, Strategy, Trade
from tests.fixtures.fixtures import (
    create_sample_user,
    create_sample_broker,
    create_sample_account,
    create_sample_strategy,
)


class TestBroker(unittest.TestCase):
    @classmethod
    @db_session
    def setUpClass(cls):
        cls.user = create_sample_user()

        cls.broker = Broker(
            uid=uuid4(),
            name="Test Broker",
            user=cls.user,
            created_at=datetime(2022, 2, 1, 0, 0, 0),
            updated_at=datetime(2022, 2, 1, 0, 0, 0),
        )

    @classmethod
    @db_session
    def tearDownClass(cls):
        Broker.select().delete()
        User.select().delete()

    def test_get_broker_by_uuid(self):
        uid = self.broker.uid

        result = Broker.get_by_uid(uid)

        self.assertIsInstance(result, Broker)
        self.assertEqual(result.id, self.broker.id)
        self.assertEqual(result.name, self.broker.name)
        self.assertIsInstance(result.user, User)
        self.assertEqual(result.user.id, self.broker.user.id)

    def test_get_broker_get_by_uid_with_no_result(self):
        result = Broker.get_by_uid(uuid4())

        self.assertIsNone(result)


class TestAccount(unittest.TestCase):
    @classmethod
    @db_session
    def setUpClass(cls):
        cls.broker = create_sample_broker()

        cls.account = Account(
            uid=uuid4(),
            type_account="R",
            currency="USD",
            initial_balance=100.0,
            current_balance=200.0,
            broker=cls.broker,
            user=cls.broker.user,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @classmethod
    @db_session
    def tearDownClass(cls):
        Account.select().delete()
        Broker.select().delete()
        User.select().delete()

    def test_account_get_by_uid(self):
        uid = self.account.uid
        result = Account.get_by_uid(uid)

        self.assertIsInstance(result, Account)
        self.assertEqual(result.id, self.account.id)
        self.assertEqual(result.type_account, "R")
        self.assertEqual(result.currency, "USD")
        self.assertEqual(result.initial_balance, 100.0)
        self.assertEqual(result.current_balance, 200.0)
        self.assertIsInstance(result.broker, Broker)
        self.assertEqual(result.broker.id, self.account.broker.id)
        self.assertIsInstance(result.user, User)
        self.assertEqual(result.user.id, self.account.user.id)

    def test_account_get_by_uid_with_no_result(self):
        result = Account.get_by_uid(uuid4())

        self.assertIsNone(result)


class TestStrategy(unittest.TestCase):
    @classmethod
    @db_session
    def setUpClass(cls):
        cls.user = create_sample_user()

        cls.strategy = Strategy(
            uid=uuid4(),
            name="Test Strategy",
            user=cls.user,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @classmethod
    @db_session
    def tearDownClass(cls):
        Strategy.select().delete()
        User.select().delete()

    def test_get_strategy_by_uuid(self):
        uid = self.strategy.uid

        result = Strategy.get_by_uid(uid)

        self.assertIsInstance(result, Strategy)
        self.assertEqual(result.id, self.strategy.id)
        self.assertEqual(result.name, "Test Strategy")
        self.assertIsInstance(result.user, User)
        self.assertEqual(result.user.id, self.user.id)

    def test_get_strategy_by_uuid_with_no_result(self):
        result = Strategy.get_by_uid(uuid4())

        self.assertIsNone(result)


class TestTrade(unittest.TestCase):
    @classmethod
    @db_session
    def setUpClass(cls):
        cls.account = create_sample_account()

        cls.strategy = create_sample_strategy()

        cls.strategy.user = cls.account.user

        cls.trade = Trade(
            uid=uuid4(),
            value=100.0,
            profit=80.0,
            result=True,
            result_balance=80.0,
            type_trade="T",
            user=cls.account.user,
            account=cls.account,
            strategy=cls.strategy,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @classmethod
    @db_session
    def tearDownClass(cls):
        Trade.select().delete()
        Strategy.select().delete()
        Account.select().delete()
        Broker.select().delete()
        User.select().delete()

    def test_trade_get_by_uid(self):
        uid = self.trade.uid
        result = Trade.get_by_uid(uid)

        self.assertIsInstance(result, Trade)
        self.assertEqual(result.id, self.trade.id)
        self.assertEqual(result.value, 100.0)
        self.assertEqual(result.profit, 80.0)
        self.assertTrue(result.result)
        self.assertEqual(result.result_balance, 80.0)
        self.assertEqual(result.type_trade, "T")
        self.assertIsInstance(result.account, Account)
        self.assertEqual(result.account.id, self.account.id)
        self.assertIsInstance(result.user, User)
        self.assertEqual(result.user.id, self.account.user.id)
        self.assertIsInstance(result.strategy, Strategy)
        self.assertEqual(result.strategy.id, self.strategy.id)

    def test_trade_get_by_uid_with_no_result(self):
        result = Trade.get_by_uid(uuid4())

        self.assertIsNone(result)
