from pms.choices import PMSType

__all__ = ['PMS_IP', 'PMS_TYPE', 'PMS_PORT', 'VINHMS_CLIENT_ID', 'VINHMS_CLIENT_SECRET', 'VINHMS_ORGANIZATION_ID', 'VINHMS_PROPERTYID']

PMS_IP = ('', '(Optional) PMS IP (for PMS integration only)', str)
PMS_TYPE = (PMSType.NOMADIX_PMS_REDIRECTOR, '(Optional) PMS TYPE (micros_opera, fias, nomadix_pms_redirector, etc...)', 'pms_type_select')
PMS_PORT = (5000, '(Optional) PMS Port (for PMS integration only)', int)


VINHMS_CLIENT_ID = ('', 'Client ID of the hotel management system', str)
VINHMS_CLIENT_SECRET = ('', 'Client secret of the hotel management system', str)
VINHMS_ORGANIZATION_ID = ('', 'Organization ID of the hotel management system', str)
VINHMS_PROPERTYID = ('', 'Property ID of the hotel management system', str)