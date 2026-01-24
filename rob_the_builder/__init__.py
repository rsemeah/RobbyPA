"""
Rob the Builder - Conversational App Builder for Robby PA

Phase 1: Foundation
- Natural conversation interface for non-technical users
- Basic app templates (todo list, calculator, notes)
- Code generation for simple web/mobile apps
- Integration with Robby PA workflow system
"""

from .conversational_interface import RobTheBuilder
from .intent_recognition import IntentRecognizer
from .app_templates import AppTemplate, TodoListTemplate, CalculatorTemplate, NotesTemplate, SimpleGameTemplate, get_template
from .code_generator import CodeGenerator

__all__ = [
    'RobTheBuilder',
    'IntentRecognizer',
    'AppTemplate',
    'TodoListTemplate',
    'CalculatorTemplate',
    'NotesTemplate',
    'SimpleGameTemplate',
    'get_template',
    'CodeGenerator',
]
