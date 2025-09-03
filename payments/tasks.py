from celery import shared_task
from django.conf import settings
from .models import PaymentGatewayTransaction


@shared_task
def check_payment_status(txn_id: int) -> str:
    """Check payment status via provider API.

    This task simulates a call to the provider. In a real implementation,
    you would use the provider's API and authentication credentials from
    settings (e.g., settings.CLICK_SECRET_KEY).
    """
    txn = PaymentGatewayTransaction.objects.get(pk=txn_id)
    # TODO: implement provider-specific API call.
    txn.status = "paid"
    txn.save(update_fields=["status"])
    return txn.status
