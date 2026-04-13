from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "transaction_type",
        "transaction_amount",
        "transaction_date",
        "get_user",
    )
    list_filter = ("transaction_type", "transaction_date")
    search_fields = ("title", "description")

    def get_user(self, obj):
        return obj.account.user

    get_user.short_description = "user"
