from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import re

#validator for mac address
def is_valid_mac(value):
    #regex for allowed mac addresses
    allowed = re.compile(r"""
                         (
                             ^([0-9A-Z]{2}[:-]){5}([0-9A-Z]{2})*?
                         )
                         """,
                         re.VERBOSE|re.IGNORECASE)
    #checks if input matches regex
    if allowed.match(value) is None:
        #Crafts and presents error message
        msg = "Sorry the mac "+ value +" must be in the following format 00:00:00:00:00:00."
        raise ValidationError(_(msg))