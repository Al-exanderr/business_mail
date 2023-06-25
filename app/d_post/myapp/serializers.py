from rest_framework import serializers, renderers
from rest_framework.renderers import JSONRenderer
from .models import Abonents


class AbonentsSerializer(serializers.Serializer):
    fio = serializers.CharField(max_length=255)
    address = serializers.CharField(max_length=255)
    doc_number = serializers.CharField(max_length=255)
    # made_date
    # inspector
    # notification
    record_creation_date = serializers.DateField()
    # возвр id. Надо reg_number:
    reg_nmbr = serializers.IntegerField(source='reg_id.reg_number')
    # fns


# renger data to json
json_render_for_our_data = renderers.JSONRenderer()
