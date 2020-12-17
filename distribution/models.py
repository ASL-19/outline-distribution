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

from django.db import models
from server.models import OutlineServer


USER_CHANNEL_CHOICES = (
    ('TG', 'Telegram'),
    ('EM', 'Email'),
    ('SG', 'Signal'),
    ('NA', 'Unknown')
)


class DatedMixin(models.Model):
    class Meta:
        ordering = ['-id']
        abstract = True

    created_date = models.DateTimeField(
        auto_now_add=True)
    updated_date = models.DateTimeField(
        auto_now=True)


class Issue(DatedMixin):
    """
    Model definition for Issues reported by users
    """
    title = models.CharField(
        max_length=128)
    description = models.CharField(
        max_length=256)

    def __str__(self):
        return self.title


class Vpnuser(DatedMixin):
    """
    Model definition for Vpn Users
    """

    username = models.CharField(
        max_length=256,
        blank=False,
        unique=True)
    channel = models.CharField(
        choices=USER_CHANNEL_CHOICES,
        max_length=2,
        default='NA')
    reputation = models.IntegerField(
        default=0)
    delete_date = models.DateTimeField(
        null=True,
        blank=True)
    banned = models.BooleanField(
        default=False)

    def __str__(self):
        return self.username


class OutlineUser(DatedMixin):
    """
    Model definition for OutlineUser.
    """
    user = models.ForeignKey(
        Vpnuser,
        null=True,
        blank=True,
        related_name='outline_keys',
        on_delete=models.SET_NULL)
    server = models.ForeignKey(
        OutlineServer,
        on_delete=models.PROTECT)
    outline_key_id = models.IntegerField()
    outline_key = models.CharField(
        max_length=512)
    reputation = models.IntegerField(
        default=0)
    transfer = models.FloatField(
        null=True,
        blank=True)
    user_issue = models.ForeignKey(
        Issue,
        null=True,
        blank=True,
        on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'OutlineUser'
        verbose_name_plural = 'OutlineUsers'

    def __str__(self):
        return self.outline_key
