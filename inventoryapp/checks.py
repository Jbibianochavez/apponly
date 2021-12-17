import re

class maccheck():
    
    def is_valid_mac(value):
        #regex for allowed mac addresses
        allowed = re.compile(r"""
                         (
                             ^([0-9A-Z]{2}[:-]){5}([0-9A-Z]{2})$
                         )
                         """,
                         re.VERBOSE|re.IGNORECASE)
        #checks if input matches regex
        if allowed.match(value) is None:
            #Crafts and presents error message
            msg = "Sorry the mac "+ value +" must be in the following format 00:00:00:00:00:00."
            return msg
        else:
            return value

class jscheck():        
    def checkforjs(value):
        BLACKLIST = ['`', ']', '[', '{', '}','(',')','<','>']
        #initializes our check value
        checkval = 0
        for val in BLACKLIST:
            #checks if value in the list is in the value sent in from the previous method
            if val in value:
                #if present set value to 1 and return
                msg = "Sorry, "+ value + " contained invalid characters."
                return msg
            else:
                continue
        return value
