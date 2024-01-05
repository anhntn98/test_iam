import logging
from django.contrib import admin, messages
from django.contrib.admin.options import csrf_protect_m
from constance.admin import ConstanceAdmin, Config, settings

from utilities.database import get_setting
from utilities.utils import strtobool
from .choices import PMSType
from .models import GuestData

logger = logging.getLogger(__name__)


@admin.register(GuestData)
class GuestDataAdmin(admin.ModelAdmin):
    list_display = ["reservation_id", "room", "current_account"]
    search_fields = ["reservation_id", "current_account"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False


class MyConstanceAdmin(ConstanceAdmin):
    hidden_fields = []

    def get_changelist_form(self, request):
        form = super().get_changelist_form(request)
        keys = list(form.__dict__.keys())
        # logger.debug("Keys: {}".format(keys))
        for field in keys:
            if field in self.hidden_fields:
                del form[field]

        return form

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        settings.CONFIG = settings.CONFIG.copy()
        settings.CONFIG_FIELDSETS = settings.CONFIG_FIELDSETS.copy()

        current_pms = get_setting("PMS_TYPE")
        if current_pms == PMSType.NOMADIX_PMS_REDIRECTOR:
            self.hidden_fields + ["PMS_IP", "PMS_PORT"]

        promo = strtobool(get_setting("PROMOTE"))

        for key in list(settings.CONFIG.keys()):
            if current_pms != PMSType.VINHMS and key.startswith("VINHMS_"):
                self.hidden_fields.append(key)
            if not promo and key.startswith("PROMOTE_"):
                self.hidden_fields.append(key)
        settings.CONFIG = {
            k: v for k, v in settings.CONFIG.items() if k not in self.hidden_fields
        }

        for key in list(settings.CONFIG_FIELDSETS.keys()):
            if isinstance(settings.CONFIG_FIELDSETS, dict):
                fieldset_items = settings.CONFIG_FIELDSETS.items()
            else:
                fieldset_items = settings.CONFIG_FIELDSETS
            for fieldset_name, fieldset in fieldset_items:
                if isinstance(fieldset, dict):
                    if "fields" in fieldset:
                        fieldset["fields"] = [
                            _ for _ in fieldset["fields"] if _ not in self.hidden_fields
                        ]
                else:
                    settings.CONFIG_FIELDSETS[fieldset_name] = [
                        _ for _ in fieldset if _ not in self.hidden_fields
                    ]
        return super().changelist_view(request, extra_context)


admin.site.unregister([Config])
admin.site.register([Config], MyConstanceAdmin)
