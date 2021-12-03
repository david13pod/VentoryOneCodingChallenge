import json

from django.http import HttpResponse
from django.shortcuts import render

from test_app_1.models import *


def index(request):
    return render(request, 'test_page.html')


def ajax_get_table_data(request):
    response_dict = []
    action = request.POST.get('action', '')


    if action == "dt_sugg_fba_send_ins":
        suggestions=Fba.objects.get(site='amazon.de')
        suggest_dict=suggestions.create_suggestion
        suggest_warehouse_keys=suggest_dict["amazon.de"]["source_warehouses"].keys()
        warehouses = Warehouse.objects.all()
        for wh in warehouses:
            if wh.id in suggest_warehouse_keys:
                response_dict.append({
                    "warehouse_id": wh.id,
                    "warehouse": wh.warehouse_name,
                    "amazon_de": suggest_dict["amazon.de"]["source_warehouses"][wh.id]['total_Germany'],
                    "amazon_fr": suggest_dict["amazon.de"]["source_warehouses"][wh.id]['total_France'],

                })

    return HttpResponse(json.dumps({"data": response_dict}), content_type='application/json')