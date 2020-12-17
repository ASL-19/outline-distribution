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

from django.urls import path, include, re_path
from distribution import views


urlpatterns = [
    re_path(r'user/(?P<username>.+)$', views.VpnuserView.as_view()),
    re_path(r'user$', views.VpnuserView.as_view()),
    path('outline', views.OutlineUserView.as_view()),
    re_path(r'outline/(?P<user>\w+)$', views.OutlineUserView.as_view()),
    path('users', views.VpnuserList.as_view()),
    path('listoutlineusers', views.OutlineUserList.as_view()),
    path('issues', views.IssueList.as_view()),
]

urlpatterns = [path('distribution/', include(urlpatterns))]
