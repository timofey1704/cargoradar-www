class ClientError(Exception):
    """Базовая ошибка домена клиента."""


class ClientNotFoundError(ClientError):
    def __init__(self, client_id: int) -> None:
        self.client_id = client_id
        super().__init__(f"Client {client_id} not found")


class ClientNotLegalError(ClientError):
    def __init__(self, client_id: int) -> None:
        self.client_id = client_id
        super().__init__(f"Client {client_id} is not a legal client")


class DuplicateFieldError(ClientError):
    def __init__(self, field: str) -> None:
        self.field = field
        super().__init__(f"Значение поля '{field}' уже занято")