"""Domain exceptions for redirect service."""


class LinkNotFoundError(Exception):
    def __init__(self, detail: str = "Link not found") -> None:
        super().__init__(detail)
        self.detail = detail


class LinkExpiredError(Exception):
    def __init__(self, detail: str = "Link has expired") -> None:
        super().__init__(detail)
        self.detail = detail
