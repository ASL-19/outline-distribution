# Copyright 2020 ASL19 Organization
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from rest_framework import serializers
from distribution.models import USER_CHANNEL_CHOICES
from server.models import OutlineServer
from preference.models import Region
from preference.serializers import RegionSerializer


class OutlineServerSerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=128,
        allow_blank=False)
    # ToDo: support ipv6
    ipv4 = serializers.IPAddressField(protocol="IPv4")
    provider = serializers.CharField(required=False)
    cost = serializers.FloatField(required=False)
    user_src = serializers.ChoiceField(choices=USER_CHANNEL_CHOICES, required=False)
    api_url = serializers.CharField()
    api_cert = serializers.CharField()
    prometheus_port = serializers.IntegerField(required=False)
    active = serializers.BooleanField(required=False)
    is_blocked = serializers.BooleanField(required=False)
    region = RegionSerializer(required=False, read_only=True, many=True)

    def create(self, validated_data):
        """
        Create and return a new Vpnuser instance, given the validated data.
        """
        try:
            region = validated_data.pop('region')
            region = Region.objects.get(name=region)
        except Exception:
            region = None
        outline_server = OutlineServer.objects.create(
            **validated_data)
        if region:
            outline_server.region.add(region)
            outline_server.save()
        return outline_server
