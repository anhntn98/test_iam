import logging
from functools import wraps

from django.conf import settings
from django.http import HttpResponse
from asgiref.sync import sync_to_async

from gateway.models import Gateway
from utilities.utils import get_client_ip
from utilities.database import get_setting

logger = logging.getLogger(__name__)

def ip_allow_post_2_pms(func):
    """
    If the client ip is in settings.ALLOWED_HOSTS, or is PMS_IP, or is in Gateway, then return the
    function. Otherwise, return 401
    
    :param func: The function to be decorated
    :return: A function
    """
    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        # Check if client ip is allowed to post to PMS
        # If not, return 401
        try:
            client_ip = get_client_ip(request)
        except:
            logger.warning('Cannot get client ip')
            return HttpResponse('401 Unauthorized', status=401)
        # Step by step check for reducing database query
        # IP in settings.ALLOWED_HOSTS
        allowed_ips = settings.ALLOWED_HOSTS
        if client_ip in allowed_ips: return func(request, *args, **kwargs)
        # IP is PMS_IP
        pms_ip = await sync_to_async(get_setting)(key='PMS_IP')
        if pms_ip and pms_ip == client_ip: return func(request, *args, **kwargs)
        # IP is in Gateway
        if await Gateway.objects.filter(ip_address=client_ip).afirst():
            return func(request, *args, **kwargs)
        
        logger.warning('Client ip %s is not allowed to post to PMS' % client_ip)
        return HttpResponse('401 Unauthorized', status=401)
        
    return wrapper