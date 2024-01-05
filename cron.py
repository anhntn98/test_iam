import logging
from urllib.parse import urlencode
from QoS.models import Room
import requests

from pms.types.VinHMS import CiHMS_Token, save_token_to_cache, get_token_from_cache
from pms.types.VinHMS.utils import json_to_room_data, get_setting
from utilities.database import set_cache

# logger = logging.getLogger(__name__) # pms....
logger = logging.getLogger('cron')

def get_token_schedule():
    """Cronjob to query token every 8 hours"""
    logger.debug("------Start querying token from cron------")
    token_api = 'https://identity.prod.hulk.cloudhms.io/connect/token'
    
    for i in range(1, 3):
        logger.debug("Attempt {} to query token api".format(i))
        payload = {
            'client_id': get_setting('VINHMS_CLIENT_ID'),
            'client_secret': get_setting('VINHMS_CLIENT_SECRET'),
            'organization_id': get_setting('VINHMS_ORGANIZATION_ID'),
            'grant_type': 'client_credentials',
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        logger.debug("Start querying get token API...")
        try:
            response = requests.post(
                token_api, data=urlencode(payload), headers=headers)
        except Exception as err:
            logger.debug("Error while calling api from {}:  {}".format(__name__, err))
            continue
        
        logger.debug("Querying get token API complete")
        
        if response.status_code == 200:
            _token = CiHMS_Token(**response.json())
            logger.debug("Token querying success.")
            save_token_to_cache(_token)
            break
        else:
            logger.warning('Cannot get token from CiHMS in attempt number {}'.format(i))
            
    logger.debug("------End querying token from cron------\n")

def get_room_schedule():
    logger.debug("------Start querying room from cron------")
    rooms = Room.objects.all()
    room_info_api = 'https://premium-api.product.cloudhms.io/common-trd/v1/ops-front-office/melia/inhouse-guest'
    token = get_token_from_cache()
    if token:
        logger.debug("Found token in cache.")
       
        for room in rooms:    
            headers = {
                'Authorization': 'Bearer ' + token.access_token
            }
            data = {
                "propertyId": get_setting('VINHMS_PROPERTYID'),
                "roomNumber": room.name,
            }
            for i in range(1, 3):
                logger.debug("Attempt {} to query room api of room {}".format(i, room.name))
                
                try:
                    logger.debug("Start querying get room api of room {}...".format(room.name))
                    response = requests.get(room_info_api +
                                            '?' + urlencode(data), headers=headers)
                    logger.debug(response.json())
                    logger.debug("Querying get room API complete!")
                except Exception as err:
                    logger.debug("Error while calling api from {}:  {}".format(__name__, err))
                    continue
                
                if response.status_code == 200:
                    guest_list = json_to_room_data(response.json())
                    # if guest_list:
                    cache_key = "HMS_ROOM_" + room.name
                    set_cache(cache_key, guest_list)
                    logger.debug("Querying room success.")
                    break
                else:
                    if response.json()['message'] == 'Unauthorized':
                        logger.debug("WRONG TOKEN")
                        continue
                    logger.debug(response.json())
        
    logger.debug("------End querying room from cron------\n")
    