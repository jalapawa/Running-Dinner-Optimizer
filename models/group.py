from dataclasses import dataclass

@dataclass
class Group:
    personA: str
    email: str
    personB: str
    teamname: str
    address: str
    dish: str    
    phone: str
    guestInfo: str = ""
    cookInfo: str = ""
    cleaning: str = "Nein"
    further: str = ""