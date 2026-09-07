import enum

class AdminTypes(str, enum.Enum):
    support = "support" # специалист поддержки
    manager = "manager" # управляющий
    owner = "owner"     # владелец
    