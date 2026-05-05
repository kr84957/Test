import os
import tempfile
import unittest

from payroll.auth import AuthService


class TestAuthService(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        self.tmp.close()
        self.auth = AuthService(self.tmp.name)

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_register_and_auth(self):
        self.auth.register("tester", "VeryStrong8")
        self.assertTrue(self.auth.authenticate("tester", "VeryStrong8"))
        self.assertFalse(self.auth.authenticate("tester", "wrongpass"))

    def test_duplicate_user(self):
        self.auth.register("tester", "VeryStrong8")
        with self.assertRaises(ValueError):
            self.auth.register("tester", "VeryStrong8")


if __name__ == "__main__":
    unittest.main()
