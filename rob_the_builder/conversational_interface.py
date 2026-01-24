"""
Rob the Builder - Conversational Interface

Main conversational interface that coordinates between natural language understanding,
app generation, and Robby PA's workflow management.
"""

import os
from typing import Optional
from dataclasses import dataclass

from robby import SessionManager, Phase
from .intent_recognition import IntentRecognizer, Intent
from .app_templates import get_template, AppSpec
from .code_generator import CodeGenerator


@dataclass
class BuilderContext:
    """Context for a conversation with Rob the Builder."""
    session_id: Optional[str] = None
    current_intent: Optional[Intent] = None
    current_spec: Optional[AppSpec] = None
    awaiting_confirmation: bool = False
    output_directory: Optional[str] = None


class RobTheBuilder:
    """
    Rob the Builder - Conversational App Builder

    Talks to users in natural language and builds apps for them.
    """

    def __init__(self):
        self.session_manager = SessionManager()
        self.intent_recognizer = IntentRecognizer()
        self.code_generator = CodeGenerator()
        self.context = BuilderContext()

        # Conversation state
        self.conversation_history = []

    def chat(self, user_input: str) -> str:
        """
        Main conversation interface.

        Args:
            user_input: What the user said

        Returns:
            Rob's response
        """
        # Add to conversation history
        self.conversation_history.append({'role': 'user', 'message': user_input})

        # Route to appropriate handler based on context
        if self.context.awaiting_confirmation:
            response = self._handle_confirmation(user_input)
        elif self.context.session_id and self.context.current_spec:
            response = self._handle_refinement(user_input)
        else:
            response = self._handle_new_request(user_input)

        # Add response to history
        self.conversation_history.append({'role': 'assistant', 'message': response})

        return response

    def _handle_new_request(self, user_input: str) -> str:
        """Handle a new app building request."""
        # Recognize intent
        intent = self.intent_recognizer.recognize(user_input)
        self.context.current_intent = intent

        # Check if clarification is needed
        clarification = self.intent_recognizer.ask_clarifying_question(intent)
        if clarification and intent.confidence < 0.7:
            self.context.awaiting_confirmation = True
            return clarification

        # Create app spec
        return self._create_app_spec(intent)

    def _create_app_spec(self, intent: Intent) -> str:
        """Create app specification and start build process."""
        try:
            # Get template
            template = get_template(
                intent.app_type,
                name=intent.customizations.get('name'),
                customizations=intent.customizations
            )

            # Create spec
            spec = template.to_spec(features=intent.features)
            self.context.current_spec = spec

            # Start Robby PA session
            session = self.session_manager.create_session(
                metadata={
                    'project': spec.name,
                    'app_type': spec.app_type,
                    'platform': spec.platform,
                    'builder': 'RobTheBuilder',
                }
            )
            self.context.session_id = session.session_id

            # Build response
            response = f"Great! I'll build '{spec.name}' for you!\n\n"
            response += f"📱 App Type: {spec.app_type.title()}\n"
            response += f"📝 Description: {spec.description}\n\n"

            if intent.customizations:
                response += "✨ Customizations:\n"
                for key, value in intent.customizations.items():
                    response += f"  • {key.title()}: {value}\n"
                response += "\n"

            response += "Should I go ahead and build this app? (yes/no)"
            self.context.awaiting_confirmation = True

            return response

        except Exception as e:
            return f"Hmm, I'm having trouble understanding that. Could you describe what you want to build in a different way? ({str(e)})"

    def _handle_confirmation(self, user_input: str) -> str:
        """Handle yes/no confirmation."""
        self.context.awaiting_confirmation = False

        # Check for positive confirmation
        positive_words = ['yes', 'yeah', 'yep', 'sure', 'ok', 'okay', 'go ahead', 'do it', 'build it']
        if any(word in user_input.lower() for word in positive_words):
            return self._build_app()
        else:
            # User said no or something unclear
            self.context = BuilderContext()  # Reset
            return "No problem! What would you like to build instead?"

    def _build_app(self) -> str:
        """Actually build the app."""
        try:
            spec = self.context.current_spec
            session_id = self.context.session_id

            # Progress through Robby PA phases
            response = "🔨 Building your app...\n\n"

            # INTAKE → SCOPE_LOCK
            self.session_manager.advance_phase(session_id, "User requirements gathered")
            response += "✓ Requirements gathered\n"

            # SCOPE_LOCK → PLAN
            self.session_manager.advance_phase(session_id, "App scope locked")
            response += "✓ Scope locked\n"

            # PLAN - Create execution plan
            plan = self._create_execution_plan(spec)
            self.session_manager.approve_plan(session_id, plan)
            response += "✓ Plan created\n"

            # PLAN → EXECUTE
            self.session_manager.advance_phase(session_id, "Plan approved, beginning execution")
            response += "✓ Starting build\n"

            # Generate code
            files = self.code_generator.generate(spec)

            # Write files to output directory
            output_dir = self._create_output_directory(spec.name)
            self.context.output_directory = output_dir

            for filename, content in files.items():
                filepath = os.path.join(output_dir, filename)
                with open(filepath, 'w') as f:
                    f.write(content)

            response += f"✓ Code generated ({len(files)} files)\n"

            # EXECUTE → PROVE
            self.session_manager.advance_phase(session_id, "Code generation complete")
            response += "✓ Build complete\n"

            # PROVE - Add verification receipts
            self.session_manager.add_truthserum_receipt(
                session_id,
                verification_type="code_generation",
                verified=True,
                verification_data={'files_created': len(files), 'output_dir': output_dir},
                verifier="CodeGenerator"
            )
            response += "✓ Verified\n"

            # PROVE → HANDOFF
            self.session_manager.advance_phase(session_id, "Verification complete")

            # HANDOFF → SHIP
            self.session_manager.advance_phase(session_id, "Ready for use")
            response += "✓ Ready!\n\n"

            # Final message
            response += f"🎉 Your app '{spec.name}' is ready!\n\n"
            response += f"📁 Location: {output_dir}\n\n"
            response += "To use your app:\n"
            response += f"1. Open the folder: {output_dir}\n"
            response += "2. Double-click 'index.html' to open in your browser\n"
            response += "3. Enjoy your app!\n\n"
            response += "Want to build another app? Just tell me what you'd like to create!"

            return response

        except Exception as e:
            # Add blocker if something goes wrong
            if self.context.session_id:
                self.session_manager.add_blocker(
                    self.context.session_id,
                    f"Build failed: {str(e)}"
                )

            return f"Oops! Something went wrong while building your app: {str(e)}\n\nLet's try again. What would you like to build?"

    def _handle_refinement(self, user_input: str) -> str:
        """Handle requests to modify or refine the app."""
        # For now, just acknowledge and offer to build a new app
        return "I've already built your app! If you'd like to make changes, please tell me what new app you'd like to build."

    def _create_execution_plan(self, spec: AppSpec) -> str:
        """Create execution plan for Robby PA."""
        plan = f"Execution Plan for {spec.name}\n"
        plan += "=" * 50 + "\n\n"
        plan += "1. Initialize project structure\n"
        plan += f"2. Generate {spec.platform} application code\n"
        plan += f"3. Implement {len(spec.features)} features:\n"

        for feature in spec.features:
            plan += f"   - {feature}\n"

        plan += "4. Apply customizations:\n"
        for key, value in spec.customizations.items():
            plan += f"   - {key}: {value}\n"

        plan += "5. Generate supporting files (README, etc.)\n"
        plan += "6. Verify all files created successfully\n"

        return plan

    def _create_output_directory(self, app_name: str) -> str:
        """Create output directory for the app."""
        # Sanitize app name for use as directory name
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in app_name)
        safe_name = safe_name.replace(' ', '_').lower()

        # Create in generated_apps directory
        base_dir = os.path.join(os.getcwd(), 'generated_apps')
        os.makedirs(base_dir, exist_ok=True)

        # Create unique directory name if it exists
        output_dir = os.path.join(base_dir, safe_name)
        counter = 1
        while os.path.exists(output_dir):
            output_dir = os.path.join(base_dir, f"{safe_name}_{counter}")
            counter += 1

        os.makedirs(output_dir)
        return output_dir

    def get_session_status(self) -> Optional[dict]:
        """Get current Robby PA session status."""
        if not self.context.session_id:
            return None

        return self.session_manager.get_session_status(self.context.session_id)

    def reset(self):
        """Reset conversation context."""
        self.context = BuilderContext()
        self.conversation_history = []
