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


class CargoRequestNotFoundError(ClientError):
    """Заявки нет либо она принадлежит другому клиенту."""

    def __init__(self, request_id: int) -> None:
        self.request_id = request_id
        super().__init__(f"Cargo request {request_id} not found")


class CargoRequestNotEditableError(ClientError):
    """Заявку нельзя править: перевозчик уже взял её в работу или она закрыта."""

    def __init__(self, request_id: int, status: str) -> None:
        self.request_id = request_id
        self.status = status
        super().__init__(
            f"Cargo request {request_id} cannot be edited in status '{status}'"
        )


class CargoRequestNotDeletableError(ClientError):
    """Заявку нельзя удалить: она в работе или уже выполнена."""

    def __init__(self, request_id: int, status: str) -> None:
        self.request_id = request_id
        self.status = status
        super().__init__(
            f"Cargo request {request_id} cannot be deleted in status '{status}'"
        )