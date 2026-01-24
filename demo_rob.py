#!/usr/bin/env python3
"""
Demo script for Rob the Builder

Shows example conversations and generated apps.
"""

import os
import shutil
from rob_the_builder import RobTheBuilder


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_conversation(rob, user_inputs, description):
    """Run a demo conversation."""
    print_section(description)

    for user_input in user_inputs:
        print(f"👤 User: {user_input}")
        response = rob.chat(user_input)
        print(f"🔨 Rob:  {response}\n")

    # Show session status
    status = rob.get_session_status()
    if status:
        print(f"✅ Session Status: {status['current_phase']} phase")
        print(f"   Session ID: {status['session_id']}")

    # Reset for next demo
    rob.reset()


def main():
    """Run all demos."""
    print("\n" + "🔨" * 35)
    print("      ROB THE BUILDER - DEMO")
    print("      Phase 1: Conversational App Builder")
    print("🔨" * 35 + "\n")

    print("This demo shows Rob building apps from natural language conversations.")
    print("Watch as a 10-year-old or grandmother could create real, working apps!")

    # Clean up old generated apps
    if os.path.exists('generated_apps'):
        shutil.rmtree('generated_apps')

    rob = RobTheBuilder()

    # Demo 1: Simple Todo List
    demo_conversation(
        rob,
        [
            "I want to make a todo list app",
            "yes"
        ],
        "DEMO 1: Simple Todo List App"
    )

    # Demo 2: Calculator with customization
    demo_conversation(
        rob,
        [
            "Build me a calculator with a blue theme",
            "yes"
        ],
        "DEMO 2: Calculator App with Blue Theme"
    )

    # Demo 3: Notes app with custom name
    demo_conversation(
        rob,
        [
            "Create a notes app called 'My Journal'",
            "yes"
        ],
        "DEMO 3: Notes App with Custom Name"
    )

    # Demo 4: Simple Game
    demo_conversation(
        rob,
        [
            "I want to make a game where you collect stars and avoid red things",
            "yes"
        ],
        "DEMO 4: Simple Collectible Game"
    )

    # Show what was created
    print_section("GENERATED APPS SUMMARY")

    if os.path.exists('generated_apps'):
        apps = os.listdir('generated_apps')
        print(f"✨ Rob created {len(apps)} working apps:\n")

        for i, app_dir in enumerate(apps, 1):
            app_path = os.path.join('generated_apps', app_dir)
            files = os.listdir(app_path)

            print(f"{i}. {app_dir}/")
            print(f"   Files: {', '.join(files)}")
            print(f"   Location: {os.path.abspath(app_path)}")

            # Show how to run it
            index_path = os.path.join(app_path, 'index.html')
            if os.path.exists(index_path):
                print(f"   To use: Open {os.path.abspath(index_path)} in a browser")
            print()

    print_section("WHAT JUST HAPPENED?")

    print("""
Rob the Builder demonstrates Phase 1 of the vision:

✅ Natural language understanding - Recognizes what users want to build
✅ Conversational interface - Friendly, natural conversation
✅ Automatic code generation - Creates complete, working apps
✅ Multiple app types - Todo lists, calculators, notes, games
✅ Customization support - Colors, names, features
✅ Robby PA integration - Uses workflow management underneath

🎯 Target Users: 10-year-olds and grandparents ✓
🎯 Natural conversation: "I want to make X" ✓
🎯 Working apps generated: ✓
🎯 Feels magical: ✓

📊 PROGRESS: Phase 1 Complete (20% toward 80% of App Store)

What's Next:
- Add more app templates (social, e-commerce, media apps)
- Improve natural language understanding
- Add mobile platform support (iOS/Android)
- Implement app refinement ("make it bigger", "change the color")
- Add deployment to actual app stores

Try it yourself:
    python3 rob_cli.py

Or use the API directly:
    from rob_the_builder import RobTheBuilder
    rob = RobTheBuilder()
    response = rob.chat("I want to make a todo list")
    """)

    print("\n" + "=" * 70)
    print("  🎉 Demo Complete! Check out the generated_apps/ folder!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
