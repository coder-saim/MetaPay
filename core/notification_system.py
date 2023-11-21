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


