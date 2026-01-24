"""
Intent Recognition for Rob the Builder

Understands natural language requests and maps them to app templates and features.
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Intent:
    """Recognized intent from user input."""
    app_type: str  # 'todo', 'calculator', 'notes', 'game', etc.
    features: List[str]  # Requested features
    customizations: Dict[str, str]  # Colors, names, etc.
    confidence: float  # 0-1 confidence score


class IntentRecognizer:
    """Recognizes user intent from natural language."""

    # App type patterns
    APP_PATTERNS = {
        'todo': [
            r'todo', r'task', r'checklist', r'to-do', r'to do',
            r'things to do', r'reminder', r'list of tasks'
        ],
        'calculator': [
            r'calculator', r'calc', r'math', r'calculate',
            r'do math', r'add numbers', r'subtract', r'multiply'
        ],
        'notes': [
            r'notes?', r'note.?taking', r'write down', r'jot down',
            r'memo', r'diary', r'journal', r'keep track of'
        ],
        'game': [
            r'game', r'play', r'fun', r'collect', r'avoid',
            r'catch', r'puzzle', r'adventure'
        ],
    }

    # Feature patterns
    FEATURE_PATTERNS = {
        'save': [r'save', r'store', r'remember', r'keep', r'persist'],
        'share': [r'share', r'send', r'export', r'email'],
        'color': [r'color', r'theme', r'style', r'look', r'appearance'],
        'search': [r'search', r'find', r'filter', r'look for'],
        'sort': [r'sort', r'organize', r'order', r'arrange'],
        'delete': [r'delete', r'remove', r'clear', r'erase'],
        'edit': [r'edit', r'change', r'modify', r'update'],
    }

    # Color extraction
    COLORS = [
        'red', 'blue', 'green', 'yellow', 'purple', 'pink',
        'orange', 'black', 'white', 'gray', 'brown', 'cyan',
        'magenta', 'teal', 'lime', 'navy', 'maroon'
    ]

    def recognize(self, user_input: str) -> Intent:
        """
        Recognize intent from user input.

        Args:
            user_input: Natural language from user

        Returns:
            Intent object with recognized information
        """
        text = user_input.lower()

        # Detect app type
        app_type = self._detect_app_type(text)

        # Detect features
        features = self._detect_features(text)

        # Extract customizations
        customizations = self._extract_customizations(text)

        # Calculate confidence
        confidence = self._calculate_confidence(app_type, features, text)

        return Intent(
            app_type=app_type,
            features=features,
            customizations=customizations,
            confidence=confidence
        )

    def _detect_app_type(self, text: str) -> str:
        """Detect which type of app the user wants."""
        scores = {}

        for app_type, patterns in self.APP_PATTERNS.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    score += 1
            if score > 0:
                scores[app_type] = score

        if not scores:
            # Default to notes if unclear
            return 'notes'

        # Return app type with highest score
        return max(scores.items(), key=lambda x: x[1])[0]

    def _detect_features(self, text: str) -> List[str]:
        """Detect requested features."""
        features = []

        for feature, patterns in self.FEATURE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    features.append(feature)
                    break

        return features

    def _extract_customizations(self, text: str) -> Dict[str, str]:
        """Extract customization preferences."""
        customizations = {}

        # Extract colors
        for color in self.COLORS:
            if color in text:
                customizations['color'] = color
                break

        # Extract app name (quoted text or "called X" pattern)
        name_match = re.search(r'["\']([^"\']+)["\']', text)
        if name_match:
            customizations['name'] = name_match.group(1)
        else:
            called_match = re.search(r'called\s+(\w+)', text, re.IGNORECASE)
            if called_match:
                customizations['name'] = called_match.group(1)

        return customizations

    def _calculate_confidence(self, app_type: str, features: List[str], text: str) -> float:
        """Calculate confidence score."""
        confidence = 0.6  # Base confidence (higher default)

        # Increase confidence if we found patterns
        if any(re.search(pattern, text, re.IGNORECASE)
               for pattern in self.APP_PATTERNS.get(app_type, [])):
            confidence += 0.3

        # Increase confidence if features were detected
        if features:
            confidence += 0.1

        # Cap at 1.0
        return min(confidence, 1.0)

    def ask_clarifying_question(self, intent: Intent) -> Optional[str]:
        """
        Generate a clarifying question if confidence is low.

        Args:
            intent: Recognized intent

        Returns:
            Question string or None if no clarification needed
        """
        if intent.confidence < 0.6:
            return f"I think you want to build a {intent.app_type} app. Is that right?"

        if intent.app_type == 'game' and not intent.customizations:
            return "What kind of game would you like? Can you describe it?"

        return None
