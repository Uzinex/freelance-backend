from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseNotAllowed
from django.conf import settings
import json

from .models import PaymentGatewayTransaction


@csrf_exempt
def payment_callback(request, provider):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    signature = request.headers.get("X-Signature")
    secret = {
        "click": settings.CLICK_SECRET_KEY,
        "payme": settings.PAYME_SECRET_KEY,
        "stripe": settings.STRIPE_SECRET_KEY,
    }.get(provider)

    if not secret or signature != secret:
        return HttpResponseForbidden("Invalid signature")

    data = json.loads(request.body or "{}")
    txn_id = data.get("txn_id")
    provider_txn_id = data.get("provider_txn_id")
    status = data.get("status")

    try:
        txn = PaymentGatewayTransaction.objects.get(pk=txn_id, provider=provider)
    except PaymentGatewayTransaction.DoesNotExist:
        return JsonResponse({"detail": "Transaction not found"}, status=404)

    if provider_txn_id:
        txn.provider_txn_id = provider_txn_id
    if status:
        txn.status = status
    txn.save(update_fields=["provider_txn_id", "status"])

    return JsonResponse({"success": True})
