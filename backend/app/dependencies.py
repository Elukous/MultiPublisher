from app.platforms.registry import registry


def get_registry():
    """Dependency that provides the platform registry."""
    return registry
