from typing import List

from app.domain.entities.customer import Customer
from app.domain.ports import CustomerRepositoryPort


class ListCustomersService:
    def __init__(self, repo: CustomerRepositoryPort):
        self.repo = repo

    def execute(self) -> List[Customer]:
        return list(self.repo.list_all())
