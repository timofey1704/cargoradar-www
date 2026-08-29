import enum

class ExecutorTypes(str, enum.Enum):
    carrier = "carrier" # перевозчик + аренда спец техники
    supplier = "supplier" # поставщик запчастей
    service = "service" # СТО
    towtruck = "towtruck" # эвакуатор