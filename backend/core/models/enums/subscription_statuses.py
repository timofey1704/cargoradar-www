import enum

class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"          # действует прямо сейчас
    EXPIRED = "expired"        # срок вышел, не продлили/не оплатили вовремя
    CANCELLED = "cancelled"    # пользователь сам отменил (действует до subscription_end)
    SUSPENDED = "suspended"    # заблокирована администрацией за нарушение
    
class SubscriptionSource(str, enum.Enum):
    TRIAL_GRANT = "trial_grant" # бесплатная пробная подписка, выданная при регистрации
    PURCHASE = "purchase"       # оплаченная подписка