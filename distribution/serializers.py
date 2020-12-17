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

import random
import logging

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import APIException
from outline_api import (
    Manager as OutlineManager,
    get_key_datatransfer)

from distribution.models import Vpnuser, OutlineUser, USER_CHANNEL_CHOICES, Issue
from lp_server.reputation import ReputationSystem
from server.models import OutlineServer

logger = logging.getLogger(__name__)


class NotAcceptable(APIException):
    """
    Custom Error to represent Unacceptable API calls
    """
    status_code = 406
    default_detail = 'Not Acceptable, try again later.'
    default_code = 'not_acceptable'


class VpnuserSerializer(serializers.Serializer):
    """
    Serializer for VPN Users
    """
    id = serializers.IntegerField(
        read_only=True)
    username = serializers.CharField(
        required=True,
        max_length=256,
        allow_blank=False,
        validators=[UniqueValidator(queryset=Vpnuser.objects.all())])
    channel = serializers.ChoiceField(
        choices=USER_CHANNEL_CHOICES,
        required=True)
    reputation = serializers.IntegerField(
        required=False,
        default=0)
    banned = serializers.BooleanField(
        required=False,
        default=False)
    outline_key = serializers.SerializerMethodField()

    def create(self, validated_data):
        """
        Create and return a new Vpnuser instance, given the validated data.
        """
        try:
            user = Vpnuser.objects.create(**validated_data)
        except Exception as exc:
            logger.error('Error in adding VPN user {}'.format(str(exc)))
            raise serializers.ValidationError("The User cannot be created.")

        return user

    def update(self, instance, validated_data):
        """
        Update and return an existing Vpnuser instance, given the validated data.
        """
        instance.username = validated_data.get(
            'username',
            instance.username)
        instance.channel = validated_data.get(
            'channel',
            instance.channel)
        instance.reputation = validated_data.get(
            'reputation',
            instance.reputation)
        instance.banned = validated_data.get(
            'banned',
            instance.banned)

        instance.save()
        return instance

    def get_outline_key(self, user):
        """
        Populate Outline Key
        """
        try:
            outline_user = user.outline_keys.latest('updated_date')
            return outline_user.outline_key
        except Exception as exc:
            logger.error(exc)
            return ''


class OutlineuserSerializer(serializers.Serializer):
    """
    Serializer for Outline User
    """
    id = serializers.IntegerField(
        read_only=True)
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username')
    server = serializers.PrimaryKeyRelatedField(
        read_only=True)
    outline_key_id = serializers.IntegerField(
        required=False)
    outline_key = serializers.CharField(
        required=False,
        max_length=256)
    reputation = serializers.IntegerField(
        default=0)
    transfer = serializers.FloatField(
        required=False)
    user_issue = serializers.PrimaryKeyRelatedField(
        read_only=True,
        required=False)
    user = serializers.CharField()

    def remove_lastkey(self, user, user_issue):
        """
        Remove users last key from the Outline Server and
        update its data
        """
        if user_issue:
            try:
                user_issue = Issue.objects.get(id=user_issue)
            except Issue.DoesNotExist:
                logger.error('Invalid issue specified!')
                user_issue = None

        last_key = OutlineUser.objects.filter(user=user).last()
        if last_key:
            try:
                transfer = get_key_datatransfer(
                    host=last_key.server.ipv4,
                    port=last_key.server.prometheus_port,
                    key=str(last_key.outline_key_id),
                    duration="30d"
                )
            except Exception as exc:
                logger.error('Error in getting data transfer {}'.format(str(exc)))
                transfer = None

            last_key.user_issue = user_issue
            last_key.transfer = transfer
            last_key.save()
            try:
                previous_manager = OutlineManager(
                    apiurl=last_key.server.api_url,
                    apicrt=last_key.server.api_cert)
                previous_manager.delete(last_key.outline_key_id)
            except Exception as exc:
                logger.error(exc)

    def get_server(self, user, level):
        """
        Get a server based on user's level and channel
        """
        last_keys = OutlineUser.objects.filter(user=user).all()
        last_servers = list(set([last_key.server.id for last_key in last_keys]))

        servers = OutlineServer.objects.filter(
            active=True,
            is_distributing=True,
            level=level,
            user_src=user.channel).exclude(id__in=last_servers)
        count = servers.count()
        if count > 1:
            server = servers[random.randint(0, count - 1)]
        else:
            server = servers.first()
        return server

    def create(self, validated_data):
        """
        Create and return a new OutlineUser instance, given the validated data.
        """
        user = validated_data.pop('user')
        try:
            user = Vpnuser.objects.get(username=user)
        except Vpnuser.DoesNotExist:
            raise NotAcceptable('User does not exist')

        if user.banned:
            logger.error('User {} is banned'.format(user))
            raise NotAcceptable('User is banned')

        level = ReputationSystem.server_level(user.reputation)
        server = self.get_server(user, level)
        if server is None:
            logger.error('Unable to find a new server for user {}'.format(str(user.id)))
            raise NotAcceptable('No server found for user {}'.format(str(user.id)))

        try:
            manager = OutlineManager(apiurl=server.api_url, apicrt=server.api_cert)
            new_key = manager.new()
        except Exception as exc:
            logger.error('Error getting new key from server {} (Error: {})'.format(server.id, exc))
            raise NotAcceptable('Outline server error')

        try:
            validated_data["outline_key_id"] = new_key['id']
            validated_data["outline_key"] = new_key['accessUrl']
        except KeyError as exc:
            logger.error(exc)
            raise NotAcceptable('Outline key creation error')

        user_issue_id = validated_data.pop('user_issue', None)
        validated_data.pop('transfer', None)
        self.remove_lastkey(user, user_issue_id)
        new_rep = ReputationSystem.after_new_key(user.reputation)
        if new_rep != user.reputation:
            user.reputation = new_rep
            user.save()

        return OutlineUser.objects.create(
            **validated_data, user=user, server=server)


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = '__all__'
