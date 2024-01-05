import uuid
from django.db import models

from accesscontrol.models import Account

class BasePMS(models.Model):
    """
    Base model for all PMS record.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    record = models.TextField(max_length=1000, null=True, blank=True,editable=False)
    created_time  = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        abstract = True

class GuestData(models.Model):
    """Store guest data from PMS system
    Mapping Guest ID to IAM account
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reservation_id  = models.IntegerField()
    room = models.CharField(max_length=50)
    current_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True)
 
    def __str__(self):
        return str(self.reservation_id)

    class Meta:
        db_table = 'iam_pms_guest_data'
        verbose_name = 'Guest Data'
        
class SendQueue(BasePMS):
    """
    Store PMS records to be sent to PMS system.
    """
 
    def __str__(self):
        return str(self.record)

    class Meta:
        db_table = 'iam_pms_send_queue'
        verbose_name = 'Send Queue Record'