class AppContext:
    """Global runtime context for session/actor/memory state"""
    def __init__(self):
        self.session_id = None
        self.actor_id = None

app_context = AppContext()
