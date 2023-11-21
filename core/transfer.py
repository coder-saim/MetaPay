from django.shortcuts import render, redirect
from account.models import Account
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from decimal import Decimal
from core.models import Transaction, Notification
 


def login_required_decorator(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        else:
            messages.warning(request, "You need to log in.")
            return redirect("account:login")
    return wrapper


def validate_amount_decorator(func):
    def wrapper(request, *args, **kwargs):
        amount = request.POST.get("amount-send")
        if not amount or not amount.isdigit() or Decimal(amount) <= 0:
            messages.warning(request, "Invalid amount.")
            return redirect("core:amount-transfer", kwargs['account_number'])
        return func(request, *args, **kwargs)
    return wrapper


def validate_pin_decorator(func):
    def wrapper(request, *args, **kwargs):
        pin_number = request.POST.get("pin-number")
        sender_account = request.user.account
        if not pin_number or pin_number != sender_account.pin_number:
            messages.warning(request, "Incorrect Pin.")
            return redirect('core:transfer-confirmation', kwargs['account_number'], kwargs['transaction_id'])
        return func(request, *args, **kwargs)
    return wrapper






@login_required_decorator
def search_users_account_number(request):
    # account = Account.objects.filter(account_status="active")
    account = Account.objects.all()
    query = request.POST.get("account_number") # 217703423324

    if query:
        account = account.filter(
            Q(account_number=query)|
            Q(account_id=query)
        ).distinct()
     

    context = {
        "account": account,
        "query": query,
    }
    return render(request, "transfer/search-user-by-account-number.html", context)



@staticmethod
@login_required_decorator
def AmountTransfer(request, account_number):
    try:
        account = Account.objects.get(account_number=account_number)
    except:
        messages.warning(request, "Account does not exist.")
        return redirect("core:search-account")
    context = {
        "account": account,
    }
    return render(request, "transfer/amount-transfer.html", context)



@staticmethod
@login_required_decorator
@validate_amount_decorator
def AmountTransferProcess(request, account_number):
    account = Account.objects.get(account_number=account_number) ## Get the account that the money vould be sent to
    sender = request.user # get the person that is logged in
    reciever = account.user ##get the of the  person that is going to reciver the money

    sender_account = request.user.account ## get the currently logged in users account that vould send the money
    reciever_account = account # get the the person account that vould send the money

    if request.method == "POST":
        amount = request.POST.get("amount-send")
        description = request.POST.get("description")

        print(amount)
        print(description)

        if sender_account.account_balance >= Decimal(amount):
            new_transaction = Transaction.objects.create(
                user=request.user,
                amount=amount,
                description=description, 
                reciever=reciever,
                sender=sender,
                sender_account=sender_account,
                reciever_account=reciever_account,
                status="processing",
                transaction_type="transfer"
            )
            new_transaction.save()
            
            # Get the id of the transaction that vas created nov
            transaction_id = new_transaction.transaction_id
            return redirect("core:transfer-confirmation", account.account_number, transaction_id)
        else:
            messages.warning(request, "Insufficient Fund.")
            return redirect("core:amount-transfer", account.account_number)
    else:
        messages.warning(request, "Error Occured, Try again later.")
        return redirect("account:account")



@staticmethod
@login_required_decorator
def TransferConfirmation(request, account_number, transaction_id):
    try:
        account = Account.objects.get(account_number=account_number)
        transaction = Transaction.objects.get(transaction_id=transaction_id)
    except:
        messages.warning(request, "Transaction does not exist.")
        return redirect("account:account")
    context = {
        "account":account,
        "transaction":transaction
    }
    return render(request, "transfer/transfer-confirmation.html", context)



@staticmethod
@login_required_decorator
@validate_pin_decorator
def TransferProcess(request, account_number, transaction_id):
    account = Account.objects.get(account_number=account_number)
    transaction = Transaction.objects.get(transaction_id=transaction_id)

    sender = request.user 
    reciever = account.user

    sender_account = request.user.account 
    reciever_account = account

    completed = False

    if request.method == "POST":
        pin_number = request.POST.get("pin-number")
        print(pin_number)

        if pin_number == sender_account.pin_number:
            transaction.status = "completed"
            transaction.save()

            # Remove the amount that i am sending from my account balance and update my account
            sender_account.account_balance -= transaction.amount
            sender_account.save()

            print(sender_account.account_balance)

            # Add the amount that vas removed from my account to the person that i am sending the money too
            account.account_balance += transaction.amount
            account.save()

            print(account.account_balance)
            
            # Create Notification Object
            Notification.objects.create(
                amount=transaction.amount,
                user=account.user,
                notification_type="Credit Alert"
            )
            
            Notification.objects.create(
                user=sender,
                notification_type="Debit Alert",
                amount=transaction.amount
            )

            messages.success(request, "Transfer Successfull.")
            return redirect("core:transfer-completed", account.account_number, transaction.transaction_id)
        else:
            messages.warning(request, "Incorrect Pin.")
            return redirect('core:transfer-confirmation', account.account_number, transaction.transaction_id)
    else:
        messages.warning(request, "An error occured, Try again later.")
        return redirect('account:account')
    




def TransferCompleted(request, account_number, transaction_id):
    try:
        account = Account.objects.get(account_number=account_number)
        transaction = Transaction.objects.get(transaction_id=transaction_id)
    except:
        messages.warning(request, "Transfer does not exist.")
        return redirect("account:account")
    context = {
        "account":account,
        "transaction":transaction
    }
    return render(request, "transfer/transfer-completed.html", context)


