import unittest
from unittest.mock import patch
from io import StringIO
import sys

# We'll import main but avoid running it on import
import main


class TestMainScript(unittest.TestCase):
    """Test the main script using mocked input/output."""

    @patch('builtins.input', side_effect=['Bob', '5.0', '2.0'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_full_calculation(self, mock_stdout, mock_input):
        """Simulate full interaction and check output."""
        main.main()

        output = mock_stdout.getvalue()

        # Check greeting
        self.assertIn("Hello, Bob! Welcome to Python programming.", output)

        # Check calculations
        self.assertIn("5.0 + 2.0 = 7.0", output)
        self.assertIn("5.0 - 2.0 = 3.0", output)
        self.assertIn("5.0 * 2.0 = 10.0", output)
        self.assertIn("5.0 / 2.0 = 2.5", output)

    @patch('builtins.input', side_effect=['Charlie', '10', '0'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_division_by_zero(self, mock_stdout, mock_input):
        """Ensure division by zero is handled."""
        main.main()

        output = mock_stdout.getvalue()
        self.assertIn("Cannot divide by zero!", output)


if __name__ == "__main__":
    unittest.main()