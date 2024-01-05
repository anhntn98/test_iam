# -*- coding: utf-8 -*-
from functools import wraps
import re
import logging
import asyncio
from lxml import etree
from datetime import datetime, timedelta

from django.http import HttpResponse
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync, sync_to_async

from QoS.models import Room, Plan
from history.models import RoomHistory, ExpiredAccount
from accesscontrol.models import Account, Vip
from accesscontrol.choices import ACCOUNTTYPE, ACCOUNTSTATUS

from .decorators import ip_allow_post_2_pms
from .choices import PMSType
from .models import GuestData

logger = logging.getLogger(__name__)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

def async_csrf_exempt(view_func):
    """Mark a view function as being exempt from the CSRF view protection."""
    # view_func.csrf_exempt = True would also work, but decorators are nicer
    # if they don't have side effects, so return a new function.

    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)

    async def wrapped_view_async(*args, **kwargs):
        resp = await view_func(*args, **kwargs)
        resp.csrf_exempt = True
        return resp

    wrapped_view.csrf_exempt = True
    return wraps(view_func)(wrapped_view_async if asyncio.iscoroutinefunction(view_func) else wrapped_view)


@ip_allow_post_2_pms
@csrf_exempt
def pms(request, pms_type=PMSType.MICROS_OPERA):
    """
    Receive message from PMS and update account information
    """
    logger.debug('Received message %s' % (request.body))
    try:
        asyncio.create_task(process_pms_request(pms_type, request.body))
    except Exception as e:
        logger.error('Cannot process PMS request: {}'.format(e))

    return HttpResponse('')

async def process_pms_request(pms_type, body):
    """
    """
    try:
        doc = etree.XML(body)
    except Exception as err:
        logger.warning('Nomadix reponse XML error: {}'.format(err))
    else:
        command = doc.get('COMMAND')
        data = doc.findtext('DATA')
        try:
            data = str(data).strip()
        except:
            pass
        logger.debug('XML data %s' % (data))
        if data:
            await sync_to_async(process_pms_message)(pms_type, command, data)

def process_pms_message(pms_type, command, data):
    """
    Process message from PMS and update account information
    """
    match pms_type:
        case _:
            from pms.record import OperaRecord as Record

    match command:
        case 'PMS_UNSOLICITED_RESPONSE' | 'PMS_TRANSACTION_RESPONSE':
            """aaa"""
            record = Record(data)
            if not record.is_valid():
                logger.info('Invalid record: {}'.format(record))
                return

            match record.type:
                case 'DS':
                    logger.info('PMS - Database Resync started')
                    return
                case 'DE':
                    logger.info('PMS - Database Resync ended')
                    return

            # All message must have room number
            RN, GN, GV, GID = record.RN, record.GN, record.GV, record.GID

            GT = record.GT
            if GT:
                # Remove title from name
                GN = GN.replace(' {}'.format(GT.lower()), '')
            # Clean up name
            lastname = None if not GN else GN.lower().replace(
                '\'', '').split('|')[0].split(' ')[0]
            account_name = RN + '.' + lastname if lastname else None

            # Create room with sync DR message
            room, created = Room.objects.get_or_create(name=RN)
            if created:
                logger.debug('Recipe GI message with virtual room igore')
            else:
                logger.debug('Room {} found'.format(RN))
            vip = cal_vip(GV)

            msg = 'Room {} checkin with account {}'.format(room.name, lastname)
            logger.debug(msg)
            RoomHistory.objects.create(room_name=room.name, status=room.status, log=msg)
            room.status = 1
            room.save()

            # Different message type
            match record.type:
                case 'GI':
                    """Guest In Message"""
                    DA = 0
                    try:
                        DA = cal_date(record.GA, record.GD)
                    except:
                        pass
                    logger.debug(
                        'Guest {} checkin room {} in {} days'.format(GN, RN, DA))

                    guest, created = GuestData.objects.get_or_create(reservation_id=GID)

                    account, created = Account.objects.get_or_create(username=account_name, type=ACCOUNTTYPE.POSTPAID)
                    if created:
                        logger.debug(
                            'Account {} not found create new account'.format(account_name))
                        account.duration_time = 1440*int(DA)
                        account.countdown = True
                        account.room = room
                    # update password, lastname
                    account.password = lastname
                    account.vip = vip
                    account.save()
                    guest.room = str(room)
                    guest.current_account = account
                    guest.save()

                case 'GO':
                    """Guest Out Message"""
                    logger.debug('Guest Out')
                    for acc in Account.objects.filter(room__name=RN):
                        if str(acc.username) == str(acc.room):
                            # bypass acc parent
                            continue
                        logger.debug(
                            'Checkout room {} move Account {} to history'.format(RN, acc.username))
                        #ExpiredAccount.objects.create(username=acc.username, data=model_to_dict(acc), description='Guest checkout')
                        acc.delete()

                case 'GC' | 'GM':
                    """Guest Change Message"""
                    DA = 0
                    try:
                        DA = cal_date(record.GA, record.GD)
                        logger.debug("DA: {}".format(DA))
                    except:
                        pass
                    logger.debug('Guest {} change infomation.'.format(GN))
                    logger.debug("GID: {}".format(GID))
                    guest, created = GuestData.objects.get_or_create(reservation_id=GID)
                    #note. the previous command not run completely
                    logger.debug("guest: {}".format(guest))
                    account = guest.current_account
                    logger.debug(account)
                    if not account:
                        logger.debug('guest {}'.format(guest.reservation_id))
                        RO = record.RO
                        if RO:
                            old_account_name = RO + "." + lastname if lastname else None
                            try:
                                account = Account.objects.get(username=old_account_name, type=ACCOUNTTYPE.POSTPAID)
                            except:
                                pass
                            else:
                                logger.debug(
                                    'Account {} found'.format(old_account_name))
                        if not account:
                            account, created = Account.objects.get_or_create(username=account_name, type=ACCOUNTTYPE.POSTPAID)
                            if created:
                                logger.debug(
                                    'Account {} not found create new account'.format(account_name))
                                account.countdown = True
                                account.room = room
                    # handle if account is null. todo
                    if GN:
                        account.username = account_name
                    logger.debug(account.pk)
                    #guest.current_account = account.pk (account.pk is integer)
                    guest.room = str(room)
                    if account.room.name != RN:
                        """
                        Guest move to another room
                        GC|G#21380470|RN118|GSN|DA140806|RO111|GSN|TI153352|
                        """
                        try:
                            account = Account.objects.get(username=account_name, type=ACCOUNTTYPE.POSTPAID)
                        except:
                            account.room = room
                            account.username = account_name
                        logger.debug(
                            'Change session current account to {}'.format(account.username))
                        guest.room = room.name
                    guest.current_account = account
                    guest.save()
                    # update password, lastname
                    account.duration_time = 1440*int(DA)
                    account.password = lastname
                    account.vip = vip
                    account.save()

            RE_PL = re.search(r'^PL\|(.*)', data)

        case 'PMS_UNSOLICITED_RESPONSE1':
            # GI|DA130624|TI151815|RN335|
            # GO|DA130624|TI151820|RN340|
            record = Record(data)

            # Record donot have reservation_id
            RN = record.RN
            try:
                room = Room.objects.get(name=RN)
            except:
                rm = Room(name=RN)
                match record.type:
                    case 'GI':
                        rm.status = 1
                    case 'GO':
                        rm.status = 0
                rm.save()
                Account.objects.create(username=RN, password=RN, countdown=True, type=ACCOUNTTYPE.POSTPAID, room=rm)
            else:
                pass
    logger.debug('Finish process message')
    return

def cal_date(GA, GD):
    """
    Caculate date between arival and destination
    Example: #GA140731|GD140801
    """
    delta = datetime.strptime(GD, "%y%m%d") - datetime.strptime(GA, "%y%m%d")
    days = delta.days
    if days <= 0:
        days = 1
    return days + 1


def cal_vip(GV):
    """
    return vip object with high priority
    """
    if not GV:
        return None
    vip_code = 1000000
    vips = Vip.objects.all()

    for vip in vips:
        rx = r'\b(?=\w){0}\b(?!\w)'.format(vip.name)
        if re.search(rx, GV, re.IGNORECASE):
            logger.debug('Match vip %s with priority %s' % (GV, vip.priority))
            if int(vip.priority) <= int(vip_code):
                vip_code = vip.priority

    logger.debug('Cal gv %s with vip priority %s' % (GV, vip_code))
    try:
        result = Vip.objects.get(priority=vip_code)
    except:
        result = None

    return result

