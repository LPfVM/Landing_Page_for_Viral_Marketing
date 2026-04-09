from .models import Transaction


class TransactionService:
    @staticmethod
    def create_transaction(user, data):
        return Transaction.objects.create(**data)
