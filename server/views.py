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

from django.shortcuts import get_object_or_404
from rest_framework import permissions
from server.models import OutlineServer
from server.serializers import OutlineServerSerializer
from rest_framework import generics


class OutlineServerView(generics.RetrieveUpdateAPIView):
    queryset = OutlineServer.objects.filter(active=True).all()
    serializer_class = OutlineServerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Override get_object to include Create in the view
        """
        if self.request.method == 'PUT':
            return None
        if self.request.method == 'GET':
            pk = self.kwargs.get('pk', None)
        else:
            pk = self.request.data.get('pk', None)
        return get_object_or_404(OutlineServer, pk=pk)
