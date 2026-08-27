import enum

class VehicleTypes(str, enum.Enum):
    truck = "truck"
    special_equipment = "special_equipment"
    towtruck = "towtruck"
    
class CarTypes(str, enum.Enum):
    sedan = "sedan"
    hatchback = "hatchback"
    coupe = "coupe"
    convertible = "convertible"
    suv = "suv"
    crossover = "crossover"
    minivan = "minivan"
    van = "van"
    pickup = "pickup"
    
CarTypesNames: dict[CarTypes, str] = {
    CarTypes.sedan: "Седан",
    CarTypes.hatchback: "Хэтчбек",
    CarTypes.coupe: "Купе",
    CarTypes.convertible: "Кабриолет",
    CarTypes.suv: "Внедорожник",
    CarTypes.crossover: "Кроссовер",
    CarTypes.minivan: "Минивэн",
    CarTypes.van: "Фургон",
    CarTypes.pickup: "Пикап",
}