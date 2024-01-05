from utilities.choices import ChoiceSet

class PMSType(ChoiceSet):
    """
    List of PMS type
    """
    MICROS_OPERA = 'micros_opera'
    MICROS_WINPAC = 'micros_winpac'
    FIAS = 'fias'
    NOMADIX_PMS_REDIRECTOR = 'nomadix_pms_redirector'
    VINHMS = 'vinhms'

    CHOICES = (
        (MICROS_OPERA, 'Micros Opera'),
        (MICROS_WINPAC, 'Micros WinPac'),
        (FIAS, 'FIAS'),
        (NOMADIX_PMS_REDIRECTOR, 'Nomadix PMS Redirector'),
        (VINHMS, 'VinHMS'),
    )
    
class PMSMessage(ChoiceSet):
    
    ANY = 'any'
    GI = 'GI'
    GO = 'GO'
    GC = 'GC'
    
    CHOICES = (
        (ANY, 'Any'),
        (GI, 'Guest In'),
        (GO, 'Guest Out'),
        (GC, 'Guest Change'),
    )