#!/usr/bin/env python3
"""
Main script that uses a function from another file and folder.
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