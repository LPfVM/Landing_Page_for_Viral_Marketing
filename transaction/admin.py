from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "transaction_type",
        "transaction_amount",
        "transaction_date",
        "user",
    )
    list_filter = ("transaction_type", "transaction_date")
    search_fields = ("title", "description")
