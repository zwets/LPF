from unittest import TestCase

class TestStrings(TestCase):
    def test_upper(self):
        self.assertEqual("spam".upper(), "SPAM")