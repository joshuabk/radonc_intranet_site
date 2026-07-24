from django.db.models import Prefetch
from django.shortcuts import render

from .models import Link, LinkCategory


def link_hub(request):
    categories = LinkCategory.objects.prefetch_related(
        Prefetch("links", queryset=Link.objects.filter(is_active=True))
    )
    return render(request, "linkhub/hub.html", {"categories": categories})
