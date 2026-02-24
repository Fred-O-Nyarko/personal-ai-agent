from app.core.container import get_container

def get_event_bus():
    return get_container().event_bus

def get_llm_client():
    return get_container().llm_client

def get_tool_registry():
    return get_container().tool_registry


def get_agent_service():
    return get_container().agent_service


def get_thread_service():
    return get_container().thread_service