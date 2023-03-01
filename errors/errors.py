class ImproperlyConfigured(Exception):
    """Raises when a environment variable is missing."""

    def __init__(self, variable_name: str, *args, **kwargs):
        self.variable_name = variable_name
        self.message = f"Set the {variable_name} environment variable."
        super().__init__(self.message, *args, **kwargs)
