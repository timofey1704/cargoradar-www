import enum


class OAuthProvider(str, enum.Enum):
    apple = "apple"
    google = "google"