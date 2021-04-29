from .models import NetworkClass
from rest_framework import serializers

class NetworkClassSerializers(serializers.ModelSerializer):
    class Meta:
        model = NetworkClass
        fields = (
            'index', 'src_ip', 'src_port','dst_ip', 'dst_port', 'timestamp', 'class_field'
        )