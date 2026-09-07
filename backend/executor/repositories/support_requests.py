from core.repositories.support_requests_repository import BaseSupportRequestRepository


class ExecutorSupportRequestRepository(BaseSupportRequestRepository):
    owner_field = "executor_id"