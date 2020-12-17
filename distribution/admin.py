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

from django.contrib import admin
from distribution.models import Vpnuser, Issue, OutlineUser


@admin.register(OutlineUser)
class OutlineUserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'user_channel',
        'created_date',
        'updated_date')
    list_display_links = ('id', 'user')
    list_filter = [
        'user__username',
        'user__channel']
    empty_value_display = 'unknown'
    list_per_page = 10
    list_max_show_all = 100
    search_fields = ['user__username']

    def user_channel(self, obj):
        return obj.user.channel

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(user__isnull=True)


@admin.register(Vpnuser)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'channel',
        'created_date',
        'delete_date')
    list_display_links = ('id', 'username')
    list_filter = ['channel']
    empty_value_display = 'unknown'
    list_per_page = 10
    list_max_show_all = 100
    search_fields = ['username']


admin.site.register(Issue)
