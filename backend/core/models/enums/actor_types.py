import enum


class ActorType(str, enum.Enum):
    """Тип участника чата.

    ``system`` используется только для автора системных сообщений
    (в офферах и вложениях этот тип запрещён CheckConstraint-ом).
    """

    client = "client"
    executor = "executor"
    system = "system"