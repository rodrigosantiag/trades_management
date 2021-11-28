import unittest

import helpers


class TestHelpers(unittest.TestCase):
    def test_pass_test(self):
        result = helpers.pass_test()

        self.assertTrue(result)
