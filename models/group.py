from dataclasses import dataclass, asdict

@dataclass
class Group:
    personA: str
    email: str
    personB: str
    emailB: str
    teamname: str
    address: str
    dish: str    
    phone: str
    guestInfo: str = ""
    cookInfo: str = ""
    cleaning: str = "Nein"
    further: str = ""
    id: int = 0
    coords : tuple[float, float] = (0,0)

    def to_dict(self):
        return asdict(self)
