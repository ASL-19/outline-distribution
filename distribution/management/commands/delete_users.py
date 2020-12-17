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

from distribution.models import Vpnuser
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Delete users after an specified waiting period'

    def add_arguments(self, parser):
        parser.add_argument(
            'days',
            type=int,
            help='Number of days to wait before deleting a profile')

    def handle(self, *args, **options):
        days = options['days']

        target_date = timezone.now() - timezone.timedelta(days=days)
        users = Vpnuser.objects.filter(delete_date__lte=target_date)
        count = users.count()
        try:
            users.delete()
            self.stdout.write(self.style.SUCCESS(
                'Successfully deleted {} users'.format(count)))
        except Exception as exc:
            self.stdout.write(self.style.ERROR(
                'Error during deleting users {}'.format(str(exc))))
