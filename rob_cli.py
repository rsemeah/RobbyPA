#!/usr/bin/env python3
"""
Rob the Builder - Command Line Interface

A friendly conversational interface for building apps.
"""

import sys
from rob_the_builder import RobTheBuilder


def print_header():
    """Print welcome header."""
    print("\n" + "=" * 60)
    print("🔨  ROB THE BUILDER  🔨")
    print("=" * 60)
    print("\nHi! I'm Rob, and I can help you build apps!")
    print("Just tell me what you want to create in your own words.")
    print("\nExamples:")
    print("  • 'I want to make a todo list app'")
    print("  • 'Build me a calculator'")
    print("  • 'Create a notes app called My Journal'")
    print("  • 'Make a game where I collect stars'")
    print("\nType 'quit' or 'exit' to leave anytime.")
    print("=" * 60 + "\n")


def format_response(response: str) -> str:
    """Format Rob's response with nice formatting."""
    return f"\n🔨 Rob: {response}\n"


def get_user_input() -> str:
    """Get input from user with friendly prompt."""
    try:
        return input("You: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n\nGoodbye! Happy building! 👋\n")
        sys.exit(0)


def main():
    """Main CLI loop."""
    print_header()

    # Initialize Rob
    rob = RobTheBuilder()

    # Conversation loop
    while True:
        user_input = get_user_input()

        # Handle empty input
        if not user_input:
            continue

        # Handle quit commands
        if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
            print(format_response("Goodbye! Hope to see you again soon! Happy building! 👋"))
            break

        # Handle help
        if user_input.lower() in ['help', '?']:
            print(format_response(
                "Just tell me what you want to build! For example:\n"
                "  • 'I want a todo list app'\n"
                "  • 'Build a calculator'\n"
                "  • 'Make a notes app'\n"
                "  • 'Create a game'\n\n"
                "I'll ask questions if I need more details!"
            ))
            continue

        # Handle status check
        if user_input.lower() in ['status', 'show status']:
            status = rob.get_session_status()
            if status:
                print(format_response(
                    f"Current session status:\n"
                    f"  Phase: {status['current_phase']}\n"
                    f"  Next action: {status['next_action']}\n"
                ))
            else:
                print(format_response("No active session. Tell me what you want to build!"))
            continue

        # Handle reset
        if user_input.lower() in ['reset', 'start over', 'new']:
            rob.reset()
            print(format_response("Okay, let's start fresh! What would you like to build?"))
            continue

        # Send to Rob and get response
        try:
            response = rob.chat(user_input)
            print(format_response(response))
        except Exception as e:
            print(format_response(
                f"Oops! I encountered an error: {str(e)}\n\n"
                "Let's try again. What would you like to build?"
            ))
            rob.reset()


if __name__ == "__main__":
    main()
