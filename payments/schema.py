import strawberry
import strawberry_django
from decimal import Decimal
from typing import List
from django.contrib.auth import get_user_model

from projects.schema import UserType
from .models import Wallet, Transaction, PaymentGatewayTransaction
from .tasks import check_payment_status
from notifications.tasks import send_system_notification, dispatch_notification


@strawberry_django.type(Wallet)
class WalletType:
    id: strawberry.auto
    user: UserType
    balance: strawberry.auto


@strawberry_django.type(Transaction)
class TransactionType:
    id: strawberry.auto
    wallet: WalletType
    amount: strawberry.auto
    type: strawberry.auto
    status: strawberry.auto
    created_at: strawberry.auto


@strawberry_django.type(PaymentGatewayTransaction)
class PaymentGatewayTransactionType:
    id: strawberry.auto
    wallet: WalletType
    provider: strawberry.auto
    amount: strawberry.auto
    status: strawberry.auto
    provider_txn_id: strawberry.auto
    created_at: strawberry.auto


@strawberry.type
class Query:
    @strawberry.field
    def wallet(self, info) -> WalletType:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required")
        return user.wallet

    @strawberry.field
    def transactions(self, info) -> List[TransactionType]:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required")
        return list(user.wallet.transactions.order_by("-created_at"))

    @strawberry.field
    def payment_transactions(self, info) -> List[PaymentGatewayTransactionType]:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required")
        return list(user.wallet.gateway_transactions.order_by("-created_at"))


@strawberry.type
class Mutation:
    @strawberry.mutation
    def deposit(self, info, amount: Decimal) -> WalletType:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required")
        wallet = user.wallet
        wallet.balance += amount
        wallet.save()
        Transaction.objects.create(wallet=wallet, amount=amount, type="deposit")
        return wallet

    @strawberry.mutation
    def withdraw(self, info, amount: Decimal) -> WalletType:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required")
        wallet = user.wallet
        if wallet.balance < amount:
            raise Exception("Insufficient funds")
        wallet.balance -= amount
        wallet.save()
        Transaction.objects.create(wallet=wallet, amount=amount, type="withdraw")
        return wallet

    @strawberry.mutation
    def initiate_payment(self, info, provider: str, amount: Decimal) -> str:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required")
        wallet = user.wallet
        valid_providers = dict(PaymentGatewayTransaction._meta.get_field("provider").choices)
        if provider not in valid_providers:
            raise Exception("Unsupported provider")
        txn = PaymentGatewayTransaction.objects.create(
            wallet=wallet, provider=provider, amount=amount
        )
        # In real life, call provider API to get payment URL or form.
        payment_url = f"https://{provider}.example.com/pay/{txn.id}"
        try:
            check_payment_status.delay(txn.id)
        except Exception:
            check_payment_status.apply(args=[txn.id])
        return payment_url

    @strawberry.mutation
    def transfer(self, info, to_user_id: int, amount: Decimal) -> WalletType:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required")
        if user.id == to_user_id:
            raise Exception("Cannot transfer to yourself")
        wallet = user.wallet
        if wallet.balance < amount:
            raise Exception("Insufficient funds")
        User = get_user_model()
        to_user = User.objects.get(pk=to_user_id)
        to_wallet = to_user.wallet
        wallet.balance -= amount
        wallet.save()
        to_wallet.balance += amount
        to_wallet.save()
        Transaction.objects.create(wallet=wallet, amount=amount, type="transfer")
        Transaction.objects.create(wallet=to_wallet, amount=amount, type="transfer")
        dispatch_notification(send_system_notification, to_user.id, 'Payment Received', f'You received {amount} from {user.username}')
        return wallet
