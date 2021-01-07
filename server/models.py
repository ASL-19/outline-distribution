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

from django.core.exceptions import ValidationError
from django.db import models

from preference.models import Region


USER_SRC_CHOICES = (
    ('TG', 'Telegram'),
    ('EM', 'Email'),
    ('SG', 'Signal'),
    ('NA', 'Unknows')
)


class ServerQuerySet(models.QuerySet):
    """
    Costomized Query Sets
    """

    def active(self):
        return self.filter(active=True)

    def inactive(self):
        return self.filter(active=False)

    def blocked(self):
        return self.filter(is_blocked=True)

    def not_blocked(self):
        return self.filter(is_blocked=False)

    def distributing(self):
        return self.filter(is_distributing=True)

    def not_distributing(self):
        return self.filter(is_distributing=False)


class Server(models.Model):
    """
    Server information
    """
    class Meta:
        abstract = True

    name = models.CharField(
        max_length=128,
        unique=True)

    ipv4 = models.GenericIPAddressField(
        null=True,
        blank=True)

    ipv6 = models.GenericIPAddressField(
        null=True,
        blank=True)

    provider = models.CharField(
        max_length=128,
        null=True,
        blank=True)

    cost = models.FloatField(
        null=True,
        blank=True)

    user_src = models.CharField(
        choices=USER_SRC_CHOICES,
        max_length=2,
        default='NA')

    reputation = models.IntegerField(
        default=0)

    level = models.IntegerField(
        default=0)

    active = models.BooleanField(
        default=False)

    alert = models.BooleanField(
        default=False)

    user_count = models.IntegerField(
        default=0)

    is_blocked = models.BooleanField(
        default=False)

    is_distributing = models.BooleanField(
        default=True)

    objects = ServerQuerySet.as_manager()

    region = models.ManyToManyField(
        Region,
        blank=True)

    def clean(self):
        if self.ipv4 or self.ipv6:
            return
        raise ValidationError('Either IPv4 or IPv6 should be provided')

    def __str__(self):
        return self.ipv4 if self.ipv4 else self.ipv6


class OutlineServer(Server):
    """
    Outline VPN servers
    """
    api_url = models.TextField(
        null=True,
        blank=True)
    api_cert = models.TextField(
        null=True,
        blank=True)
    prometheus_port = models.IntegerField(
        default=900)
