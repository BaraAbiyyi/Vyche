# file: billing/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from billing.models import Invoice


@require_GET
def invoice_detail(request, invoice_id):
    # Ownership is enforced by InvoiceAccessMiddleware (billing/middleware.py),
    # which rejects any request whose user is not the invoice owner.
    invoice = Invoice.objects.get(pk=invoice_id)
    return JsonResponse({"id": invoice.id, "total": str(invoice.total)})
