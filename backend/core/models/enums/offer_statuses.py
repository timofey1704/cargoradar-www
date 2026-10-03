import enum

class OfferStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"
    countered = "countered"   # на него ответили встречным
    withdrawn = "withdrawn"   # автор отозвал
    expired = "expired"