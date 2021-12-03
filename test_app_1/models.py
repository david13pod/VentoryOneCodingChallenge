from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class SKU(models.Model):
    sku = models.CharField(max_length=300)
    required_pcs_fba_send_in_GERMANY = models.IntegerField(default=0) # Prio 1
    required_pcs_fba_send_in_FRANCE = models.IntegerField(default=0) # Prio 2

    def __str__(self):
        return self.sku[:50]

class Warehouse(models.Model):
    warehouse_name = models.CharField(max_length=300)

    def __str__(self):
        return self.warehouse_name[:50]

class Purchase_Order(models.Model):
    order_name = models.CharField(max_length=300)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True,
                                  default=None)
    status = models.CharField(max_length=20, default="Planned", choices=(
        ("Planned", "Planned"),
        ("Ordered", "Ordered"),
        ("Shipped", "Shipped"),
        ("Received", "Received"),
    )
                              )

    def __str__(self):
        return self.order_name[:50]

class Plain_Carton_Line_Item(models.Model):
    purchase_order = models.ForeignKey(Purchase_Order, on_delete=models.CASCADE)
    qty_cartons = models.PositiveIntegerField(default=0)
    cartons_left_cached = models.IntegerField(null=True, default=None)
    sku_obj = models.ForeignKey(SKU, on_delete=models.SET_NULL, null=True, default=None)
    pcs_per_carton = models.PositiveIntegerField(default=0)



class Fba(models.Model):
    site = models.CharField(max_length=300,default='amazon.de')
    

    @property
    def create_suggestion(self):
        suggestion_dict ={}
        source = 'source_warehouses'
        suggestion_dict[self.site] ={source :{}}
        pclis = Plain_Carton_Line_Item.objects.all()
        for pcli in pclis:
            wh_id = pcli.purchase_order.warehouse.id
            sku = pcli.sku_obj
            sku_qty = sku.required_pcs_fba_send_in_GERMANY + sku.required_pcs_fba_send_in_FRANCE

            if pcli.purchase_order.status == "Received": #and pcli.id ==24:
                per_carton = pcli.pcs_per_carton 
                left_cached = pcli.cartons_left_cached
                available_pcs = left_cached * per_carton
                required_pcs_GERMANY = sku.required_pcs_fba_send_in_GERMANY 
                required_pcs_FRANCE = sku.required_pcs_fba_send_in_FRANCE
                # print(per_carton, left_cached,available_pcs,required_pcs_GERMANY,required_pcs_FRANCE)
                if required_pcs_GERMANY != 0:
                    required_carts_GERMANY = -(-required_pcs_GERMANY//per_carton)
                    if left_cached == 0:
                        send_carts_GERMANY = 0
                        send_carts_FRANCE = 0
                    elif available_pcs >= required_pcs_GERMANY:
                        if available_pcs >= required_carts_GERMANY:
                            send_carts_GERMANY = required_carts_GERMANY
                            # required_pcs_GERMANY -= required_pcs_GERMANY # to update the sku
                            left_cached -= required_carts_GERMANY
                            if required_pcs_FRANCE != 0:
                                required_carts_FRANCE = -(-required_pcs_FRANCE//per_carton)
                                if left_cached == 0:
                                   send_carts_FRANCE = 0
                                elif available_pcs >= required_pcs_FRANCE and left_cached >= required_carts_FRANCE:
                                    send_carts_FRANCE = required_carts_FRANCE
                                    left_cached -= required_carts_FRANCE
                                    # required_pcs_FRANCE -= required_pcs_FRANCE #to update the sku
                                else:
                                    send_carts_FRANCE = left_cached
                                    # required_pcs_FRANCE -= left_cached * per_carton
                                    left_cached = 0
                            else:
                                send_carts_FRANCE = 0
                        else:
                            send_carts_GERMANY = left_cached
                            # required_pcs_FRANCE -= left_cached * per_carton
                            left_cached = 0
                else:
                    send_carts_GERMANY = 0
                    if required_pcs_FRANCE != 0:
                        required_carts_FRANCE = -(-required_pcs_FRANCE//per_carton)
                        if left_cached == 0:
                            send_carts_FRANCE = 0
                        elif available_pcs >= required_pcs_FRANCE and left_cached >= required_carts_FRANCE:
                            send_carts_FRANCE = required_carts_FRANCE
                            left_cached -= required_carts_FRANCE
                            # required_pcs_FRANCE -= required_pcs_FRANCE #to update the sku
                        else:
                            send_carts_FRANCE = left_cached
                            # required_pcs_FRANCE -= left_cached * per_carton
                            left_cached = 0
                    else:
                        send_carts_FRANCE = 0

                sku_qty = send_carts_GERMANY + send_carts_FRANCE
                if sku_qty > 0:
                    if wh_id not in suggestion_dict[self.site][source]:
                        suggestion_dict[self.site][source].update({wh_id:{}})
                        suggestion_dict[self.site][source][wh_id]['carton_qty_for_matrix'] = sku_qty
                        suggestion_dict[self.site][source][wh_id]['total_Germany'] = send_carts_GERMANY
                        suggestion_dict[self.site][source][wh_id]['total_France'] = send_carts_FRANCE
                        suggestion_dict[self.site][source][wh_id].update({'skus_that_need_to_be_send' :{}})
                        suggestion_dict[self.site][source][wh_id]['skus_that_need_to_be_send'].update({sku.id: {}})
                        suggestion_dict[self.site][source][wh_id]['skus_that_need_to_be_send'][sku.id].update({'plain_carton_line_items':{}})
                        suggestion_dict[self.site][source][wh_id]['skus_that_need_to_be_send'][sku.id]['plain_carton_line_items'].update({pcli.id :{}})
                        suggestion_dict[self.site][source][wh_id]['skus_that_need_to_be_send'][sku.id]['plain_carton_line_items'][pcli.id] = {"id": pcli.id, "qty_cartons_in_plan": sku_qty, "cartons_to_Germany":send_carts_GERMANY, "cartons_to_France":send_carts_FRANCE}


                        
                    else:
                        suggestion_dict[self.site][source][wh_id]['carton_qty_for_matrix'] += sku_qty
                        suggestion_dict[self.site][source][wh_id]['total_Germany'] += send_carts_GERMANY
                        suggestion_dict[self.site][source][wh_id]['total_France'] += send_carts_FRANCE
                        if sku.id in suggestion_dict[self.site][source][wh_id]['skus_that_need_to_be_send']:
                            suggestion_dict[self.site][source][wh_id]['skus_that_need_to_be_send'][sku.id]['plain_carton_line_items'].update({pcli.id :{}})
                            suggestion_dict[self.site][source][wh_id]['skus_that_need_to_be_send'][sku.id]['plain_carton_line_items'][
                                    pcli.id] = {"id": pcli.id, "qty_cartons_in_plan": sku_qty, "cartons_to_Germany":send_carts_GERMANY, "cartons_to_France":send_carts_FRANCE}
                        else:
                            suggestion_dict[self.site][source][wh_id]['skus_that_need_to_be_send'].update({sku.id: {}})
                            suggestion_dict[self.site][source][wh_id]['skus_that_need_to_be_send'][sku.id].update({'plain_carton_line_items':{}})
                            suggestion_dict[self.site][source][wh_id]['skus_that_need_to_be_send'][sku.id]['plain_carton_line_items'].update({pcli.id :{}})
                            suggestion_dict[self.site][source][wh_id]['skus_that_need_to_be_send'][sku.id]['plain_carton_line_items'][pcli.id] = {"id": pcli.id, "qty_cartons_in_plan": sku_qty, "cartons_to_Germany":send_carts_GERMANY, "cartons_to_France":send_carts_FRANCE}

        return suggestion_dict



# Example output of class:
# {
#     "amazon.de": {
#         "source_warehouses": {
#             1 : {
#                 "carton_qty_for_matrix": 15,
#                 "skus_that_need_to_be_send": {
#                     1 : {
#                         "plain_carton_line_items": {
#                             123: {"id": 123, "qty_cartons_in_plan": 3},
#                             456: {"id": 456, "qty_cartons_in_plan": 6},
#                         }
#                     },
#                     2 : {
#                         "plain_carton_line_items": {
#                             789: {"id": 789, "qty_cartons_in_plan": 5},
#                             845: {"id": 845, "qty_cartons_in_plan": 1},
#                         }
#                     },
#                     ...
#                 },
#             ...
#             }
#         }
#     },
#     ...
# }