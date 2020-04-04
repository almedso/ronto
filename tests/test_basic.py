
import ronto
import unittest


class BasicTestCase(unittest.TestCase):
    """ Basic test cases """

    def test_basic(self):
        """ check True is True """
        self.assertTrue(True)

    def test_version(self):
        """ check ronto exposes a version attribute """
        self.assertTrue(hasattr(ronto, "__version__"))
        self.assertIsInstance(ronto.__version__, str)


if __name__ == "__main__":
    unittest.main()
