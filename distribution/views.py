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

from datetime import datetime, timedelta

from django.http import Http404
from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework import permissions, generics
from rest_framework.settings import api_settings
from rest_framework_csv.renderers import CSVRenderer

from distribution.models import Vpnuser, OutlineUser, Issue
from distribution.serializers import (
    VpnuserSerializer,
    OutlineuserSerializer,
    IssueSerializer)


class VpnuserView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to CRUD VPN user
    """
    queryset = Vpnuser.objects.all()
    serializer_class = VpnuserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Override get_object to include Create in the view
        """
        if self.request.method == 'PUT':
            return None
        if self.request.method == 'GET':
            username = self.kwargs.get('username', None)
        else:
            username = self.request.data.get('username', None)
        return get_object_or_404(Vpnuser, username=username)

    def perform_destroy(self, instance):
        """
        Override perform_destroy to mark the user to be deleted
        instead of deleting it.
        We also ban the user so they can't use the system.
        """
        if hasattr(settings, 'PROFILE_DELETE_DELAY'):
            days = settings.PROFILE_DELETE_DELAY
        else:
            days = 7
        instance.banned = True
        instance.delete_date = datetime.now() + timedelta(days=days)
        instance.save()


class VpnuserCSVRenderer(CSVRenderer):
    """
    CSV Renderer for VPN Users
    """
    results_field = 'results'
    header = [
        'username',
        'channel',
        'reputation',
        'delete_date',
        'banned',
        'outline_key']

    def render(self, data, media_type=None, renderer_context=None):
        if not isinstance(data, list):
            data = data.get(self.results_field, [])
        return super(VpnuserCSVRenderer, self) \
            .render(data, media_type, renderer_context)


class VpnuserList(generics.ListAPIView):
    """
    List of all VPN users in both CSV and JSON
    """
    serializer_class = VpnuserSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = (VpnuserCSVRenderer, ) + \
        tuple(api_settings.DEFAULT_RENDERER_CLASSES)

    def get_queryset(self):
        """
        Optionally restricts the returned users list,
        by filtering against a `banned` query parameter in the URL.
        """
        queryset = Vpnuser.objects.all()
        banned = self.request.query_params.get('banned', None)
        if banned in ['True', 'False']:
            queryset = queryset.filter(banned=banned)
        return queryset


class OutlineUserView(generics.RetrieveUpdateAPIView):
    """
    View to Retrieve and Create Outline users
    """
    queryset = OutlineUser.objects.all()
    serializer_class = OutlineuserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Override get_object to include Create in the view
        """
        if self.request.method == 'PUT':
            return None
        elif self.request.method == 'GET':
            user = self.kwargs.get('user', None)
        try:
            ouser = OutlineUser.objects.filter(user__username=user).last()
        except OutlineUser.DoesNotExist:
            raise Http404
        return ouser


class OutlineuserCSVRenderer(CSVRenderer):
    results_field = 'results'
    header = ['user', 'server', 'outline_key', 'reputation', 'transfer', 'user_issue']

    def render(self, data, media_type=None, renderer_context=None):
        if not isinstance(data, list):
            data = data.get(self.results_field, [])
        return super(OutlineuserCSVRenderer, self).render(data, media_type, renderer_context)


class OutlineUserList(generics.ListCreateAPIView):
    """
    List of all Outline users in both CSV and JSON
    """

    queryset = OutlineUser.objects.all()
    serializer_class = OutlineuserSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = (OutlineuserCSVRenderer, ) + \
        tuple(api_settings.DEFAULT_RENDERER_CLASSES)

    def get_queryset(self):
        """
        Optionally restricts the returned users list,
        by filtering against a `blocked` query parameter in the URL,
        which shows only blocked keys

        if user_issue is None then user hasn't reported the server blocked
        """
        queryset = OutlineUser.objects.exclude(user__isnull=True)
        blocked = self.request.query_params.get('blocked', None)
        if blocked is not None:
            if blocked.lower() == 'true':
                blocked = True
            elif blocked.lower() == 'false':
                blocked = False
            else:
                return queryset
            queryset = queryset.filter(user_issue__isnull=not blocked)
        return queryset


class IssueList(generics.ListAPIView):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [permissions.IsAuthenticated]
