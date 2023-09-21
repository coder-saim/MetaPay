from django.urls import path
from core import transfer, views


app_name = "core"

urlpatterns = [
    path("", views.index, name="index"),
    path("search-account/", transfer.search_users_account_number, name="search-account"),
]