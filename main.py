#!/usr/bin/env python3
"""
Main script that uses a function from another file and folder.

This script demonstrates:
- Importing a custom function from a module in a subdirectory
- User input and string formatting
- Basic arithmetic operations

Example:
    Run the script and enter your name when prompted.
    Then input two numbers to see the results of basic math operations.
"""

from utils.greetings import greet


def main():
    """Main function to run the script."""
    name = input("Enter your name: ")
    message = greet(name)
    print(message)

    # Simple calculation example
    print("\nLet's do a quick calculation:")
    num1 = float(input("Enter first number: "))
    num2 = float(input("Enter second number: "))

    print(f"{num1} + {num2} = {num1 + num2}")
    print(f"{num1} - {num2} = {num1 - num2}")
    print(f"{num1} * {num2} = {num1 * num2}")
    if num2 != 0:
        print(f"{num1} / {num2} = {num1 / num2}")
    else:
        print("Cannot divide by zero!")


if __name__ == "__main__":
    main()