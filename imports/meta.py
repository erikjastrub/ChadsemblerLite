class namespace(type):
    """Metaclass which makes every method found in a class a static method"""

    def __new__(self, identifier: str, methods: tuple[type], attributes: dict[str, object]):

        static_methods: list[type] = []

        for m in methods:

            static_methods.append( staticmethod(m) )

        return type(identifier, tuple(static_methods), attributes)
