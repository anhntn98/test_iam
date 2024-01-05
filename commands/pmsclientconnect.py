from datetime import timedelta
from importlib import import_module

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from utilities.database import get_setting
from pms.choices import PMSType


class Command(BaseCommand):
    help = "Create PMS Client Connect. (This command can be run at any time.) "

    def handle(self, *args, **options):

        if options['verbosity']:
            
            PMS_HOST = get_setting(key='PMS_IP')
            PMS_PORT = get_setting(key='PMS_PORT')
            PMS_TYPE = get_setting(key='PMS_TYPE')
            
            if PMS_TYPE == PMSType.NOMADIX_PMS_REDIRECTOR:
                raise CommandError("!!NomadiX PMS Redirector does not need PMS Client Connect.")
            
            self.stdout.write("[*] Start PMS Client Connect")
            if not all([PMS_HOST, PMS_PORT]):
               raise CommandError("    PMS Client Connect host or port is not set.")
            

                
                