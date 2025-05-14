from collections import defaultdict, deque

class SessionManager:
    def __init__(self, max_history=20):  # Increased history size
        self.sessions = defaultdict(lambda: {
            "history": deque(maxlen=max_history),
            "context": {
                "last_diagnosis": None,
                "symptoms": None,
                "image_uploaded": False,
                "image_description": None,
                "image_disease_list": [],
                "base64_image": None,
                "chat_bot": None  # Added for Gemini chat instance
            }
        })

    def add_message(self, session_id, role, content):
        """Add a message to the conversation history."""
        self.sessions[session_id]["history"].append({
            "role": role,
            "content": content
        })

    def get_conversation(self, session_id):
        """Return full conversation history."""
        return list(self.sessions[session_id]["history"])

    def clear_session(self, session_id):
        """Reset entire session history + context."""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def update_context(self, session_id, key, value):
        """Update any context variable (e.g., image_uploaded)."""
        self.sessions[session_id]["context"][key] = value

    def get_context(self, session_id, key):
        """Fetch a specific context variable."""
        return self.sessions[session_id]["context"].get(key)

    def get_full_context(self, session_id):
        """Return all session context as a dictionary."""
        return self.sessions[session_id]["context"]

# Singleton instance used across the app
session_manager = SessionManager()

# Legacy compatibility helpers
def add_message(session_id, role, content):
    session_manager.add_message(session_id, role, content)

def get_conversation(session_id):
    return session_manager.get_conversation(session_id)

def clear_session(session_id):
    session_manager.clear_session(session_id)