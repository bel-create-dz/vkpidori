from abc import ABC, abstractmethod
from uuid import uuid4



class AccountFrozenError(Exception):
    pass

class AccountClosedError(Exception):
    pass

class InvalidOperationError(ValueError):
    pass

class InsufficientFundsError(Exception):
    pass


class AbstractAccount(ABC):
    _used_ids = set()


    def __init__(self, profile_data, balance, account_status, uuid = None ):
        if uuid is None:
            uuid = uuid4().hex[:8]
            while uuid in self._used_ids:
                uuid = uuid4().hex[:8]
        else:
            if not isinstance(uuid, str) or not uuid.strip():
                raise ValueError("Строка не должна быть пустой")
            uuid = uuid.strip()
            if uuid in self._used_ids:
                raise ValueError("Даннный номер уже занят")

        self._uuid = uuid
        self.profile_data = profile_data
        self._account_status = account_status
        self._balance = balance
        self._used_ids.add(uuid)


    @property
    def uuid(self):
        return self._uuid

    @abstractmethod
    def deposit(self, amount):
        pass

    @abstractmethod
    def withdraw(self, amount):
        pass

    @abstractmethod
    def get_account_info(self):
        pass



class BankAccount(AbstractAccount):
    ALLOWWED_CURRENCY = ("USD", "EUR", "RUB", "CNY", "KZT")
    ACCOUNT_STATUS = ("FROZEN", "CLOSED", "ACTIVE")
    def __init__(self, profile_data, balance, account_status, currency, uuid = None,):
        if not isinstance(profile_data, str) or not profile_data.strip():
            raise ValueError("Имя владельца должно быть непустой строкой")
        if account_status not in self.ACCOUNT_STATUS:
            raise ValueError("Unknown account status")

        if currency not in BankAccount.ALLOWWED_CURRENCY:
            raise ValueError("Доступные валюты: USD, EUR, RUB, CNY, KZT")
        if type(balance) not in ( int, float ):
            raise ValueError("Баланс должен быть числом")
        if not(0 <= balance < float('inf')):
            raise ValueError("Баланс должен быть конечным числом от нуля")

        super().__init__(profile_data, balance, account_status, uuid=uuid)
        self.currency = currency

    def _check_operation(self, operation):
        if self._account_status == "FROZEN":
            raise AccountFrozenError("Аккаунт заморожен")
        if self._account_status == "CLOSED":
            raise AccountClosedError("Аккаунт закрыт")
        if self._account_status != "ACTIVE":
            raise ValueError("Неизвестный статус")
        if type(operation) not in (int, float) or not (0 < operation < float("inf")):
            raise InvalidOperationError("Сумма операции должна быть положительным конечным числом")

    def deposit(self, amount):
        self._check_operation(amount)
        new_balance = self._balance + amount
        if new_balance == float('inf'):
            raise ValueError("Недопустимый баланс")
        else:
            self._balance = new_balance


    def withdraw(self, amount):
        self._check_operation(amount)
        if self._balance < amount:
            raise InsufficientFundsError("Недостаточно средств")
        else:
            self._balance -= amount


    def get_account_info(self):
        return {
            "Profile": self.profile_data,
            "AccountStatus": self._account_status,
            "Balance": self._balance,
            "Currency": self.currency,
            "uuid": self._uuid,
        }

    def __str__(self):
        return (
            f"{type(self).__name__} | {self.profile_data} | "
            f"№ ****{self.uuid[-4:]} | {self._account_status} | "
            f"{self._balance} {self.currency}"
        )

frozen_test_account = BankAccount("user_0",1000, "FROZEN", "USD")

try:
    frozen_test_account.deposit(100)
except AccountFrozenError as error:
    print(f"Пополнение отклонено: {error}")

print(f"Баланс после попытки: {frozen_test_account.get_account_info()['Balance']} USD")

active_test_account = BankAccount("user_1", 1888, "ACTIVE", "USD")

active_test_account.deposit(100)
print(active_test_account.get_account_info()['Balance'], "USD")
active_test_account.withdraw(100)
print(active_test_account.get_account_info()['Balance'], "USD")











