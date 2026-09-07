import enum


class SupportRequestTypes(str, enum.Enum):
   SOLUTION = "solution"         # предложение по логике / доработке
   ERROR = "error"               # сведения об ошибке в рамках приложения 
   
class RequestStatuses(str, enum.Enum):
   NEW = "new"                   # новая заявка
   IN_PROGRESS = "in_progress"   # в обработке администратором
   NEEDS_INFO = "needs_info"     # суппорт связался с клиентом, уточняет данные
   RESOLVED = "resolved"         # заявка успешно решена
   REJECTED = "rejected"         # заявка отклонена