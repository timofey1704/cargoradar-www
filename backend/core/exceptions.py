"""Доменные ошибки чата: роуты превращают их в HTTP-ответы (как client.exceptions)."""


class ChatError(Exception):
    """Базовая ошибка домена чата."""


class ConversationNotFoundError(ChatError):
    """Беседы нет либо текущий пользователь не её участник (404 без подсказок)."""

    def __init__(self, conversation_id: int) -> None:
        self.conversation_id = conversation_id
        super().__init__(f"Conversation {conversation_id} not found")


class MessageEmptyError(ChatError):
    """Текстовое сообщение пустое или состоит только из пробелов (422)."""


class MessageTooLongError(ChatError):
    """Текст длиннее `settings.chat_max_message_length` (422)."""

    def __init__(self, limit: int) -> None:
        self.limit = limit
        super().__init__(f"Message longer than {limit} characters")


class AttachmentsMissingError(ChatError):
    """`type=media` без единого attachment_id (422)."""


class AttachmentLimitError(ChatError):
    """Вложений в одном сообщении больше `settings.chat_max_attachments` (422)."""

    def __init__(self, limit: int) -> None:
        self.limit = limit
        super().__init__(f"More than {limit} attachments per message")


class AttachmentNotFoundError(ChatError):
    """Вложения нет — оно удалено или принадлежит кому-то другому (404)."""

    def __init__(self, attachment_id: int) -> None:
        self.attachment_id = attachment_id
        super().__init__(f"Attachment {attachment_id} not found")


class AttachmentNotAvailableError(ChatError):
    """Вложение уже привязано к чужому сообщению (409)."""

    def __init__(self, attachment_id: int) -> None:
        self.attachment_id = attachment_id
        super().__init__(f"Attachment {attachment_id} is already attached")


class AttachmentTooLargeError(ChatError):
    """Файл больше `settings.chat_max_file_bytes` (413)."""

    def __init__(self, size: int, limit: int) -> None:
        self.size = size
        self.limit = limit
        super().__init__(f"File of {size} bytes exceeds limit of {limit} bytes")


class AttachmentUnsupportedError(ChatError):
    """Тип файла вне белого списка (415): расширение, content_type или сигнатура."""
