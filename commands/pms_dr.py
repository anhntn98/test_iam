import requests

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from utilities.database import get_setting
from gateway.models import Gateway, GATEWAYTYPE
from pms.choices import PMSType


class Command(BaseCommand):
    help = "Create PMS Client Connect. (This command can be run at any time.) "

    def handle(self, *args, **options):

        self.stdout.write("\nStart request retranfer from PMS...\n")
        if options['verbosity']:
            
            PMS_HOST = get_setting(key='PMS_IP')
            PMS_PORT = get_setting(key='PMS_PORT')
            PMS_TYPE = get_setting(key='PMS_TYPE')
            
            self.stdout.write("Checking PMS Settings")
            match PMS_TYPE:
                case PMSType.NOMADIX_PMS_REDIRECTOR:
                    self.stdout.write("NomadiX PMS Redirector host is set.")
                    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                    DA= "DA" + timezone.now().strftime("%y%m%d")
                    TI= "TI" + timezone.now().strftime("%H%M%S")
                    xmldata = '<USG COMMAND="PMS_PENDING_TRANSACTION" VERSION="1.0"><P_TRANSACTION><TRANSACTION_ID>12345</TRANSACTION_ID><DATA>DR|{}|{}|</DATA></P_TRANSACTION></USG>'.format(DA, TI)
                    self.stdout.write("[*] Getting Nomadix API settings")
                    gateways = Gateway.objects.filter(enabled=True, type=GATEWAYTYPE.NOMADIX)
                    if gateways:
                        gw = gateways.first()
                        self.stdout.write("\tGateway: {}".format(gw.name))
                        url = "http://{}/pmsRedirector/v1/pendingTransaction".format(gw.ip_address, gw.xml_port)
                        try:
                            response = requests.request("POST", url, data=xmldata, headers=headers)
                        except Exception as e:
                            self.stdout.write("\tError: {}".format(e), self.style.ERROR)
                        else:
                            self.stdout.write("\tResponse: {}".format(response.text))
                    else:
                        self.stdout.write("\tNo Nomadix Gateway found.", self.style.ERROR)
                
            
            

                
                