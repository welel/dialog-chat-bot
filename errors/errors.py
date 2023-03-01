class ImproperlyConfigured(Exception):
    """Raises when a environment variable is missing."""

    def __init__(self, variable_name: str, *args, **kwargs):
        self.variable_name = variable_name
        self.message = f"Set the {variable_name} environment variable."
        super().__init__(self.message, *args, **kwargs)


class NoSuchResource(Exception):
    """Raises when `RecourceManager` is a missing given resource."""

    def __init__(self, resource_name: str, *args, **kwargs):
        self.resource_name = resource_name
        self.message = f"Resource with name {resource_name} is missing."
        super().__init__(self.message, *args, **kwargs)
