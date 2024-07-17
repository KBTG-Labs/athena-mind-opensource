from abc import ABC, abstractmethod
from typing import Generic, TypeVar

TDomainEntity = TypeVar('TDomainEntity')
TDalEntity = TypeVar('TDalEntity')


class IDataMapper(ABC, Generic[TDomainEntity, TDalEntity]):
    @abstractmethod
    def to_domain_entity(self, dal_entity: TDalEntity) -> TDomainEntity:
        raise NotImplementedError

    @abstractmethod
    def to_dal_entity(self, domain_entity: TDomainEntity) -> TDalEntity:
        raise NotImplementedError
