import functools
import json
from collections import defaultdict
from decimal import Decimal
from typing import Dict, List

from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.db.models import Q
from django.views import generic
from .models import Document, DocumentDifference, DocumentEntry, Difference
# Create your views here.


class DocumentView(generic.ListView):
    model = Document


class DEView(generic.ListView):
    model = DocumentEntry


class DDView(generic.ListView):
    model = DocumentDifference


class ResultView(generic.TemplateView):
    template_name = "accounting_difference/result.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = []
        for d in Difference.objects.all().filter(primary=None):
            table = []
            m = Decimal(0)
            for sd in Difference.objects.all().filter(primary=d):
                amount = Decimal(0)
                for dd in DocumentDifference.objects.all().filter(difference_sec=sd):
                    amount += dd.amount
                m += amount
                if sd.code[-1] != '0' or m != Decimal(0):
                    table.append([sd.name+'\t\t', str(amount)])
            table.insert(0, [d.name+'\t\t', str(m)])
            context['form'].extend(table)
        return context
