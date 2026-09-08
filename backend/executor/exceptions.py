class ExecutorError(Exception):
    """Базовая ошибка домена исполнителя."""


class ExecutorNotFoundError(ExecutorError):
    def __init__(self, executor_id: int) -> None:
        self.executor_id = executor_id
        super().__init__(f"Executor {executor_id} not found")


class ExecutorTypeMismatchError(ExecutorError):
    def __init__(self, executor_id: int, expected: str) -> None:
        self.executor_id = executor_id
        self.expected = expected
        super().__init__(f"Executor {executor_id} is not of type '{expected}'")


class DuplicateFieldError(ExecutorError):
    def __init__(self, field: str) -> None:
        self.field = field
        super().__init__(f"Значение поля '{field}' уже занято")