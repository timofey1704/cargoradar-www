import enum

class MessageType(str, enum.Enum):
    text = "text"
    media = "media"
    offer = "offer"      # карточка оффера в ленте
    system = "system"    # «оффер принят», «заказ передан в работу»