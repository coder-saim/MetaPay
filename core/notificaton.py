from core.models import Notification

class OldNotificationModel:
    def create_notification(self, user, notification_type, amount=None):
        Notification.objects.create(
            user=user,
            notification_type=notification_type,
            amount=amount,
        )

class NewNotificationAdapter:
    def __init__(self, old_notification):
        self.old_notification = old_notification

    def send_payment_request_notification(self, user, amount):
        self.old_notification.create_notification(
            user=user,
            notification_type="Sent Payment Request",
            amount=amount,
        )

    def receive_payment_request_notification(self, user, amount):
        self.old_notification.create_notification(
            user=user,
            notification_type="Received Payment Request",
            amount=amount,
        )

    def withdrew_credit_card_funds_notification(self, user, amount):
        self.old_notification.create_notification(
            user=user,
            notification_type="Withdrew Credit Card Funds",
            amount=amount,
        )

    def deleted_credit_card_notification(self, user):
        self.old_notification.create_notification(
            user=user,
            notification_type="Deleted Credit Card",
        )

    def funded_credit_card_notification(self, user, amount):
        self.old_notification.create_notification(
            user=user,
            notification_type="Funded Credit Card",
            amount=amount,
        )

old_notification = OldNotificationModel()
adapter = NewNotificationAdapter(old_notification)

# adapter.send_payment_request_notification(request.user, transaction.amount)
# adapter.receive_payment_request_notification(account.user, transaction.amount)
# adapter.withdrew_credit_card_funds_notification(request.user, amount)
# adapter.deleted_credit_card_notification(request.user)
# adapter.funded_credit_card_notification(request.user, amount)



from abc import ABC, abstractmethod
from decimal import Decimal
from django.contrib import messages
from django.shortcuts import redirect
from core.models import Notification
from account.models import Account
from core.models import CreditCard

class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

class WithdrawFundCommand(Command):
    def __init__(self, account, credit_card, amount):
        self.account = account
        self.credit_card = credit_card
        self.amount = amount

    def execute(self):
        if self.credit_card.amount >= Decimal(self.amount) and self.credit_card.amount != 0.00:
            self.account.account_balance += Decimal(self.amount)
            self.account.save()

            self.credit_card.amount -= Decimal(self.amount)
            self.credit_card.save()

            Notification.objects.create(
                user=self.account.user,
                amount=self.amount,
                notification_type="Withdrew Credit Card Funds"
            )

            messages.success(self.request, "Withdrawal Successful")
            return redirect("core:card-detail", self.credit_card.card_id)
        elif self.credit_card.amount == 0.00:
            messages.warning(self.request, "Insufficient Funds")
            return redirect("core:card-detail", self.credit_card.card_id)
        else:
            messages.warning(self.request, "Insufficient Funds")
            return redirect("core:card-detail", self.credit_card.card_id)

class DeleteCardCommand(Command):
    def __init__(self, credit_card, request):
        self.credit_card = credit_card
        self.request = request

    def execute(self):
        account = self.credit_card.user.account

        if self.credit_card.amount > 0:
            account.account_balance += self.credit_card.amount
            account.save()

        Notification.objects.create(
            user=self.credit_card.user,
            notification_type="Deleted Credit Card"
        )

        self.credit_card.delete()
        messages.success(self.request, "Card Deleted Successfully")
        return redirect("account:dashboard")

class FundCreditCardCommand(Command):
    def __init__(self, account, credit_card, amount, request):
        self.account = account
        self.credit_card = credit_card
        self.amount = amount
        self.request = request

    def execute(self):
        if Decimal(self.amount) <= self.account.account_balance:
            self.account.account_balance -= Decimal(self.amount)
            self.account.save()

            self.credit_card.amount += Decimal(self.amount)
            self.credit_card.save()

            Notification.objects.create(
                amount=self.amount,
                user=self.account.user,
                notification_type="Funded Credit Card"
            )

            messages.success(self.request, "Funding Successful")
            return redirect("core:card-detail", self.credit_card.card_id)
        else:
            messages.warning(self.request, "Insufficient Funds")
            return redirect("core:card-detail", self.credit_card.card_id)

class CommandInvoker:
    def __init__(self, command):
        self.command = command

    def execute(self):
        return self.command.execute()


# withdraw_command = WithdrawFundCommand(account, credit_card, amount)
# withdraw_invoker = CommandInvoker(withdraw_command)
# withdraw_invoker.execute()

