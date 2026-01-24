"""
Tests for Rob the Builder Phase 1 functionality
"""

import os
import shutil
import pytest
from rob_the_builder import (
    RobTheBuilder,
    IntentRecognizer,
    TodoListTemplate,
    CalculatorTemplate,
    NotesTemplate,
    SimpleGameTemplate,
    get_template,
    CodeGenerator
)


class TestIntentRecognition:
    """Test intent recognition from natural language."""

    def setup_method(self):
        self.recognizer = IntentRecognizer()

    def test_recognize_todo_app(self):
        intent = self.recognizer.recognize("I want to make a todo list app")
        assert intent.app_type == 'todo'
        assert intent.confidence > 0.5

    def test_recognize_calculator(self):
        intent = self.recognizer.recognize("Build me a calculator")
        assert intent.app_type == 'calculator'

    def test_recognize_notes_app(self):
        intent = self.recognizer.recognize("Create a notes app")
        assert intent.app_type == 'notes'

    def test_recognize_game(self):
        intent = self.recognizer.recognize("I want to make a game where I collect stars")
        assert intent.app_type == 'game'

    def test_extract_color(self):
        intent = self.recognizer.recognize("Make a blue calculator")
        assert 'color' in intent.customizations
        assert intent.customizations['color'] == 'blue'

    def test_extract_name(self):
        intent = self.recognizer.recognize("Create a notes app called 'My Diary'")
        assert 'name' in intent.customizations
        assert intent.customizations['name'] == 'My Diary'

    def test_detect_features(self):
        intent = self.recognizer.recognize("Todo list with search and delete")
        assert 'search' in intent.features
        assert 'delete' in intent.features


class TestAppTemplates:
    """Test app templates."""

    def test_todo_template(self):
        template = TodoListTemplate(name="My Tasks")
        assert template.name == "My Tasks"
        assert 'add_task' in template.default_features()
        assert 'text_input' in template.required_components()

        spec = template.to_spec()
        assert spec.app_type == 'todolist'
        assert spec.name == "My Tasks"

    def test_calculator_template(self):
        template = CalculatorTemplate()
        assert template.name == "Calculator"
        assert 'add' in template.default_features()
        assert 'number_buttons' in template.required_components()

    def test_notes_template(self):
        template = NotesTemplate()
        assert template.name == "My Notes"
        assert 'create_note' in template.default_features()

    def test_game_template(self):
        template = SimpleGameTemplate(customizations={'name': 'Star Collector'})
        assert template.name == 'Star Collector'
        assert 'player_movement' in template.default_features()

    def test_get_template_by_type(self):
        template = get_template('todo')
        assert isinstance(template, TodoListTemplate)

        template = get_template('calculator')
        assert isinstance(template, CalculatorTemplate)


class TestCodeGeneration:
    """Test code generation."""

    def setup_method(self):
        self.generator = CodeGenerator()

    def test_generate_todo_app(self):
        template = TodoListTemplate(name="Test Tasks")
        spec = template.to_spec()

        files = self.generator.generate(spec)

        assert 'index.html' in files
        assert 'style.css' in files
        assert 'app.js' in files
        assert 'README.md' in files

        # Check content
        assert 'Test Tasks' in files['index.html']
        assert 'localStorage' in files['app.js']  # Should save tasks

    def test_generate_calculator_app(self):
        template = CalculatorTemplate()
        spec = template.to_spec()

        files = self.generator.generate(spec)

        assert 'index.html' in files
        assert 'style.css' in files
        assert 'app.js' in files

        # Check for calculator functionality
        assert 'calculate' in files['app.js']
        assert 'operator' in files['app.js']

    def test_generate_notes_app(self):
        template = NotesTemplate()
        spec = template.to_spec()

        files = self.generator.generate(spec)

        assert 'index.html' in files
        assert 'localStorage' in files['app.js']  # Should persist notes

    def test_generate_game(self):
        template = SimpleGameTemplate()
        spec = template.to_spec()

        files = self.generator.generate(spec)

        assert 'index.html' in files
        assert 'canvas' in files['app.js']  # Games use canvas
        assert 'score' in files['app.js']

    def test_color_customization(self):
        template = TodoListTemplate(customizations={'color': 'red'})
        spec = template.to_spec()

        files = self.generator.generate(spec)

        # Red color should appear in CSS
        assert 'e74c3c' in files['style.css']  # Red hex code


class TestConversationalInterface:
    """Test the conversational interface."""

    def setup_method(self):
        self.rob = RobTheBuilder()
        # Clean up test output
        if os.path.exists('generated_apps'):
            shutil.rmtree('generated_apps')

    def teardown_method(self):
        # Clean up test output
        if os.path.exists('generated_apps'):
            shutil.rmtree('generated_apps')

    def test_initial_conversation(self):
        response = self.rob.chat("I want to make a todo list")
        assert "todo" in response.lower() or "task" in response.lower()
        assert self.rob.context.current_intent is not None
        assert self.rob.context.current_intent.app_type == 'todo'

    def test_full_build_flow(self):
        # Request an app
        response1 = self.rob.chat("Build me a calculator")
        assert "calculator" in response1.lower()

        # Confirm
        response2 = self.rob.chat("yes")
        assert "ready" in response2.lower() or "complete" in response2.lower()

        # Check that files were created
        assert self.rob.context.output_directory is not None
        assert os.path.exists(self.rob.context.output_directory)

        # Check files exist
        output_dir = self.rob.context.output_directory
        assert os.path.exists(os.path.join(output_dir, 'index.html'))
        assert os.path.exists(os.path.join(output_dir, 'style.css'))
        assert os.path.exists(os.path.join(output_dir, 'app.js'))

    def test_rejection_flow(self):
        response1 = self.rob.chat("Make a notes app")
        assert "notes" in response1.lower()

        # Say no
        response2 = self.rob.chat("no")
        assert "what would you like" in response2.lower()

    def test_session_integration(self):
        # Build an app
        self.rob.chat("I want a calculator")
        self.rob.chat("yes")

        # Check Robby PA session
        status = self.rob.get_session_status()
        assert status is not None
        assert status['current_phase'] == 'SHIP'  # Should be complete

    def test_reset(self):
        self.rob.chat("Build a todo list")
        assert self.rob.context.current_intent is not None

        self.rob.reset()
        assert self.rob.context.current_intent is None
        assert self.rob.context.session_id is None


class TestEndToEnd:
    """End-to-end integration tests."""

    def setup_method(self):
        if os.path.exists('generated_apps'):
            shutil.rmtree('generated_apps')

    def teardown_method(self):
        if os.path.exists('generated_apps'):
            shutil.rmtree('generated_apps')

    def test_build_all_app_types(self):
        """Test building each app type."""
        rob = RobTheBuilder()

        app_requests = [
            ("Build a todo list", "todo"),
            ("Make a calculator", "calculator"),
            ("Create a notes app", "notes"),
            ("Build a game", "game"),
        ]

        built_apps = []

        for request, expected_type in app_requests:
            rob.reset()
            response1 = rob.chat(request)
            assert expected_type in response1.lower()

            response2 = rob.chat("yes")
            assert "ready" in response2.lower()

            # Verify output
            assert rob.context.output_directory is not None
            assert os.path.exists(rob.context.output_directory)

            built_apps.append(rob.context.output_directory)

        # Verify all apps were created
        assert len(built_apps) == 4
        assert all(os.path.exists(app) for app in built_apps)

    def test_customized_app(self):
        """Test building an app with customizations."""
        rob = RobTheBuilder()

        response1 = rob.chat("Create a blue calculator called 'Math Helper'")
        assert "Math Helper" in response1
        assert "blue" in response1.lower()

        response2 = rob.chat("yes")

        # Check the generated files
        output_dir = rob.context.output_directory
        with open(os.path.join(output_dir, 'index.html'), 'r') as f:
            html = f.read()
            assert 'Math Helper' in html


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
