from enum import Enum

class Gender(Enum):
    MALE = 1
    FEMALE = 2
    OTHERS = 3

class Role(Enum):
    ENDUSER = 1
    ADMIN = 2

class Size(Enum):
    S = 1
    M = 2
    L = 3
    XL = 4
    XXL = 5
    
class Status(Enum):
    PENDING = 1
    PROCESSING = 2
    SHIPPED = 3
    DELIVERED = 4
    CANCELLED = 5

class Color(Enum):
    RED = 1
    BLUE = 2
    GREEN = 3
    BLACK = 4


class PaymentStatus(Enum):
    PENDING = 1
    SUCCESS = 2
    FAILED = 3
    CANCELLED = 4
    
class PayMethods(Enum):
    CARD = 1
    UPI = 2
    NETBANKING = 3
    
class Banks(Enum):
    STATE_BANK_OF_INDIA = 1
    BANDHAN_BANK = 2
    BARODA_BANK = 3
    AIRTEL_PAYMENTS_BANK = 4
    CENTRAL_BANK_OF_INDIA = 5
    
    


    