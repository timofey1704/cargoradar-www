import enum

class PostCreatorType(str, enum.Enum):
    CLIENT = "client"
    EXECUTOR = "executor"