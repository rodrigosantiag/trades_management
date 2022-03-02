import unittest
from datetime import datetime
from uuid import uuid4

from pony.orm.core import db_session

from entities import Broker, User
from tests.fixtures.fixtures import create_sample_user


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
        uid = str(self.broker.uid)

        result = Broker.get_by_uid(uid)

        self.assertIsInstance(result, Broker)
        self.assertEqual(result.id, self.broker.id)
        self.assertEqual(result.name, self.broker.name)
        self.assertIsInstance(result.user, User)
        self.assertEqual(result.user.id, self.broker.user.id)
