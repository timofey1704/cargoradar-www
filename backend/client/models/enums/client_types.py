import enum

class ClientTypes(str, enum.Enum):
    individual = "individual" # физ лицо
    legal = "legal" # юр лицо
    