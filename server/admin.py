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
from .models import OutlineServer


@admin.register(OutlineServer)
class OutlineServerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'ipv4', 'user_src',
                    'level', 'active')
    list_display_links = ('id', 'name')
    list_filter = ['user_src', 'level', 'active']
    empty_value_display = 'unknown'
    list_per_page = 10
    list_max_show_all = 100
    search_fields = ['name', 'ipv4']
