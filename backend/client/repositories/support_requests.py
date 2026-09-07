from core.repositories.support_requests_repository import BaseSupportRequestRepository


class ClientSupportRequestRepository(BaseSupportRequestRepository):
    owner_field = "client_id"