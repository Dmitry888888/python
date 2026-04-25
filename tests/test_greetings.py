import unittest
from utils.greetings import greet


class TestGreetings(unittest.TestCase):
    """Test the greet function."""

    def test_greet_normal(self):
        self.assertEqual(greet("Alice"), "Hello, Alice! Welcome to Python programming.")

    def test_greet_empty(self):
        self.assertEqual(greet(""), "Hello, ! Welcome to Python programming.")

    def test_greet_whitespace(self):
        self.assertEqual(greet("  "), "Hello,   ! Welcome to Python programming.")


if __name__ == "__main__":
    unittest.main()