from django.db.models import Q
from django.shortcuts import render

from .models import ServiceContact


#user: superuser  pass:radoncintra

def contact_list(request):
    q = (request.GET.get("q") or "").strip()
    contacts = ServiceContact.objects.filter(is_active=True).prefetch_related("locations")
    if q:
        contacts = contacts.filter(
            Q(name__icontains=q) | Q(organization__icontains=q)
            | Q(systems__icontains=q) | Q(notes__icontains=q)
        )
    return render(request, "contacts/list.html", {"contacts": contacts, "q": q})
