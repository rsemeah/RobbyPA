"""
App Templates for Rob the Builder

Defines templates for common app types that can be generated.
"""

from abc import ABC, abstractmethod
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class AppSpec:
    """Specification for an app to be generated."""
    app_type: str
    name: str
    description: str
    features: List[str]
    customizations: Dict[str, str]
    platform: str = 'web'  # 'web', 'ios', 'android', 'react-native'


class AppTemplate(ABC):
    """Base class for app templates."""

    def __init__(self, name: str = None, customizations: Dict[str, str] = None):
        self.customizations = customizations or {}
        self.name = name or self.default_name()

    @abstractmethod
    def default_name(self) -> str:
        """Default name for this app type."""
        pass

    @abstractmethod
    def description(self) -> str:
        """Description of what this app does."""
        pass

    @abstractmethod
    def default_features(self) -> List[str]:
        """Default features for this app type."""
        pass

    @abstractmethod
    def required_components(self) -> List[str]:
        """Required UI components for this app."""
        pass

    def to_spec(self, features: List[str] = None) -> AppSpec:
        """Convert template to app specification."""
        return AppSpec(
            app_type=self.__class__.__name__.replace('Template', '').lower(),
            name=self.name,
            description=self.description(),
            features=features or self.default_features(),
            customizations=self.customizations,
            platform='web'
        )


class TodoListTemplate(AppTemplate):
    """Template for todo list / task management apps."""

    def default_name(self) -> str:
        return self.customizations.get('name', 'My Tasks')

    def description(self) -> str:
        return 'A simple todo list app to track your tasks and check them off when complete.'

    def default_features(self) -> List[str]:
        return [
            'add_task',
            'check_off_task',
            'delete_task',
            'save_locally',
            'clear_completed'
        ]

    def required_components(self) -> List[str]:
        return [
            'text_input',      # For new tasks
            'button',          # Add task button
            'list',            # Task list
            'checkbox',        # Check off tasks
            'delete_button',   # Delete individual tasks
        ]


class CalculatorTemplate(AppTemplate):
    """Template for calculator apps."""

    def default_name(self) -> str:
        return self.customizations.get('name', 'Calculator')

    def description(self) -> str:
        return 'A simple calculator for basic math operations: add, subtract, multiply, divide.'

    def default_features(self) -> List[str]:
        return [
            'add',
            'subtract',
            'multiply',
            'divide',
            'clear',
            'backspace',
        ]

    def required_components(self) -> List[str]:
        return [
            'display',         # Shows numbers
            'number_buttons',  # 0-9
            'operator_buttons',# +, -, *, /
            'equals_button',   # =
            'clear_button',    # C
        ]


class NotesTemplate(AppTemplate):
    """Template for note-taking apps."""

    def default_name(self) -> str:
        return self.customizations.get('name', 'My Notes')

    def description(self) -> str:
        return 'A simple note-taking app to write down your thoughts and ideas.'

    def default_features(self) -> List[str]:
        return [
            'create_note',
            'edit_note',
            'delete_note',
            'save_locally',
            'search_notes',
            'list_notes'
        ]

    def required_components(self) -> List[str]:
        return [
            'text_area',       # For writing notes
            'note_list',       # List of saved notes
            'save_button',     # Save current note
            'new_note_button', # Create new note
            'delete_button',   # Delete note
            'search_input',    # Search notes
        ]


class SimpleGameTemplate(AppTemplate):
    """Template for simple games."""

    def default_name(self) -> str:
        return self.customizations.get('name', 'My Game')

    def description(self) -> str:
        game_desc = self.customizations.get('description',
                                           'A simple game where you collect stars and avoid obstacles')
        return game_desc

    def default_features(self) -> List[str]:
        return [
            'player_movement',
            'collectibles',
            'obstacles',
            'score_tracking',
            'game_over',
            'restart'
        ]

    def required_components(self) -> List[str]:
        return [
            'canvas',          # Game area
            'player_sprite',   # Player character
            'collectible_sprites',  # Things to collect
            'obstacle_sprites',     # Things to avoid
            'score_display',   # Show score
            'game_over_screen',# Game over UI
            'start_button',    # Start/restart
        ]


# Template registry
TEMPLATE_REGISTRY = {
    'todo': TodoListTemplate,
    'todolist': TodoListTemplate,
    'calculator': CalculatorTemplate,
    'calc': CalculatorTemplate,
    'notes': NotesTemplate,
    'note': NotesTemplate,
    'game': SimpleGameTemplate,
}


def get_template(app_type: str, name: str = None, customizations: Dict[str, str] = None) -> AppTemplate:
    """
    Get an app template by type.

    Args:
        app_type: Type of app (todo, calculator, notes, game)
        name: Custom name for the app
        customizations: Custom settings

    Returns:
        AppTemplate instance
    """
    template_class = TEMPLATE_REGISTRY.get(app_type.lower())
    if not template_class:
        raise ValueError(f"Unknown app type: {app_type}")

    return template_class(name=name, customizations=customizations)
