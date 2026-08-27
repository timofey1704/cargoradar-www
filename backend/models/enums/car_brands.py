import enum

class CarBrands(str, enum.Enum):
    all = "all"
    abarth = "abarth"
    acura = "acura"
    aiways = "aiways"
    alfa_romeo = "alfa_romeo"
    alpine = "alpine"
    aston_martin = "aston_martin"
    audi = "audi"
    baic = "baic"
    bentley = "bentley"
    bestune = "bestune"
    bmw = "bmw"
    byd = "byd"
    cadillac = "cadillac"
    changan = "changan"
    chery = "chery"
    chevrolet = "chevrolet"
    chrysler = "chrysler"
    citroen = "citroen"
    cupra = "cupra"
    dacia = "dacia"
    daewoo = "daewoo"
    daihatsu = "daihatsu"
    dodge = "dodge"
    dongfeng = "dongfeng"
    ds = "ds"
    exeed = "exeed"
    ferrari = "ferrari"
    fiat = "fiat"
    fisker = "fisker"
    ford = "ford"
    gac = "gac"
    geely = "geely"
    genesis = "genesis"
    gmc = "gmc"
    great_wall = "great_wall"
    haval = "haval"
    honda = "honda"
    hongqi = "hongqi"
    hummer = "hummer"
    hyundai = "hyundai"
    infiniti = "infiniti"
    isuzu = "isuzu"
    iveco = "iveco"
    jac = "jac"
    jaguar = "jaguar"
    jeep = "jeep"
    jetour = "jetour"
    kia = "kia"
    koenigsegg = "koenigsegg"
    lada = "lada"
    lamborghini = "lamborghini"
    lancia = "lancia"
    land_rover = "land_rover"
    leapmotor = "leapmotor"
    lexus = "lexus"
    lifan = "lifan"
    lincoln = "lincoln"
    lotus = "lotus"
    lucid = "lucid"
    lynk_and_co = "lynk_and_co"
    maserati = "maserati"
    maybach = "maybach"
    mazda = "mazda"
    mclaren = "mclaren"
    mercedes = "mercedes"
    mg = "mg"
    mini = "mini"
    mitsubishi = "mitsubishi"
    nio = "nio"
    nissan = "nissan"
    opel = "opel"
    pagani = "pagani"
    peugeot = "peugeot"
    polestar = "polestar"
    porsche = "porsche"
    ram = "ram"
    renault = "renault"
    rivian = "rivian"
    rolls_royce = "rolls_royce"
    rover = "rover"
    saab = "saab"
    seat = "seat"
    skoda = "skoda"
    smart = "smart"
    ssangyong = "ssangyong"
    subaru = "subaru"
    suzuki = "suzuki"
    tata = "tata"
    tesla = "tesla"
    toyota = "toyota"
    vinfast = "vinfast"
    volkswagen = "volkswagen"
    volvo = "volvo"
    voyah = "voyah"
    xpeng = "xpeng"
    zeekr = "zeekr"
    
CAR_BRAND_NAMES: dict[CarBrands, str] = {
    CarBrands.all: "Все марки",
    CarBrands.abarth: "Abarth",
    CarBrands.acura: "Acura",
    CarBrands.aiways: "Aiways",
    CarBrands.alfa_romeo: "Alfa Romeo",
    CarBrands.alpine: "Alpine",
    CarBrands.aston_martin: "Aston Martin",
    CarBrands.audi: "Audi",
    CarBrands.baic: "BAIC",
    CarBrands.bentley: "Bentley",
    CarBrands.bestune: "Bestune",
    CarBrands.bmw: "BMW",
    CarBrands.byd: "BYD",
    CarBrands.cadillac: "Cadillac",
    CarBrands.changan: "Changan",
    CarBrands.chery: "Chery",
    CarBrands.chevrolet: "Chevrolet",
    CarBrands.chrysler: "Chrysler",
    CarBrands.citroen: "Citroën",
    CarBrands.cupra: "CUPRA",
    CarBrands.dacia: "Dacia",
    CarBrands.daewoo: "Daewoo",
    CarBrands.daihatsu: "Daihatsu",
    CarBrands.dodge: "Dodge",
    CarBrands.dongfeng: "Dongfeng",
    CarBrands.ds: "DS Automobiles",
    CarBrands.exeed: "EXEED",
    CarBrands.ferrari: "Ferrari",
    CarBrands.fiat: "Fiat",
    CarBrands.fisker: "Fisker",
    CarBrands.ford: "Ford",
    CarBrands.gac: "GAC",
    CarBrands.geely: "Geely",
    CarBrands.genesis: "Genesis",
    CarBrands.gmc: "GMC",
    CarBrands.great_wall: "Great Wall",
    CarBrands.haval: "Haval",
    CarBrands.honda: "Honda",
    CarBrands.hongqi: "Hongqi",
    CarBrands.hummer: "Hummer",
    CarBrands.hyundai: "Hyundai",
    CarBrands.infiniti: "Infiniti",
    CarBrands.isuzu: "Isuzu",
    CarBrands.iveco: "Iveco",
    CarBrands.jac: "JAC",
    CarBrands.jaguar: "Jaguar",
    CarBrands.jeep: "Jeep",
    CarBrands.jetour: "Jetour",
    CarBrands.kia: "Kia",
    CarBrands.koenigsegg: "Koenigsegg",
    CarBrands.lada: "Lada",
    CarBrands.lamborghini: "Lamborghini",
    CarBrands.lancia: "Lancia",
    CarBrands.land_rover: "Land Rover",
    CarBrands.leapmotor: "Leapmotor",
    CarBrands.lexus: "Lexus",
    CarBrands.lifan: "Lifan",
    CarBrands.lincoln: "Lincoln",
    CarBrands.lotus: "Lotus",
    CarBrands.lucid: "Lucid",
    CarBrands.lynk_and_co: "Lynk & Co",
    CarBrands.maserati: "Maserati",
    CarBrands.maybach: "Maybach",
    CarBrands.mazda: "Mazda",
    CarBrands.mclaren: "McLaren",
    CarBrands.mercedes: "Mercedes-Benz",
    CarBrands.mg: "MG",
    CarBrands.mini: "MINI",
    CarBrands.mitsubishi: "Mitsubishi",
    CarBrands.nio: "NIO",
    CarBrands.nissan: "Nissan",
    CarBrands.opel: "Opel",
    CarBrands.pagani: "Pagani",
    CarBrands.peugeot: "Peugeot",
    CarBrands.polestar: "Polestar",
    CarBrands.porsche: "Porsche",
    CarBrands.ram: "RAM",
    CarBrands.renault: "Renault",
    CarBrands.rivian: "Rivian",
    CarBrands.rolls_royce: "Rolls-Royce",
    CarBrands.rover: "Rover",
    CarBrands.saab: "Saab",
    CarBrands.seat: "SEAT",
    CarBrands.skoda: "Škoda",
    CarBrands.smart: "smart",
    CarBrands.ssangyong: "SsangYong",
    CarBrands.subaru: "Subaru",
    CarBrands.suzuki: "Suzuki",
    CarBrands.tata: "Tata",
    CarBrands.tesla: "Tesla",
    CarBrands.toyota: "Toyota",
    CarBrands.vinfast: "VinFast",
    CarBrands.volkswagen: "Volkswagen",
    CarBrands.volvo: "Volvo",
    CarBrands.voyah: "VOYAH",
    CarBrands.xpeng: "XPENG",
    CarBrands.zeekr: "ZEEKR",
}

def get_car_brand_name(brand: CarBrands) -> str:
    return CAR_BRAND_NAMES.get(
        brand,
        brand.value.replace("_", " ").title(),
    )