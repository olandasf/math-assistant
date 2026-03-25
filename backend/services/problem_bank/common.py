"""
Matematinių uždavinių bankas ir šabloninis generatorius
========================================================
Generuoja matematiniu būdu teisingus uždavinius su garantuotais atsakymais.
Nereikia AI - viskas skaičiuojama algoritmiškai.
"""

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import List


class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# =============================================================================
# LIETUVIŲ KALBOS LINKSNIAI
# =============================================================================

# Linksniai: V-vardininkas, K-kilmininkas, N-naudininkas, G-galininkas
# Vardai su linksniais: (vardininkas, kilmininkas, galininkas)
NAMES_MALE_DECLINED = [
    ("Petras", "Petro", "Petrą"),
    ("Jonas", "Jono", "Joną"),
    ("Matas", "Mato", "Matą"),
    ("Lukas", "Luko", "Luką"),
    ("Tomas", "Tomo", "Tomą"),
    ("Mantas", "Manto", "Mantą"),
    ("Domas", "Domo", "Domą"),
    ("Rokas", "Roko", "Roką"),
    ("Paulius", "Pauliaus", "Paulių"),
    ("Karolis", "Karolio", "Karolį"),
    ("Andrius", "Andriaus", "Andrių"),
    ("Mindaugas", "Mindaugo", "Mindaugą"),
    ("Vytautas", "Vytauto", "Vytautą"),
    ("Gediminas", "Gedimino", "Gediminą"),
    ("Algirdas", "Algirdo", "Algirdą"),
    ("Kęstutis", "Kęstučio", "Kęstutį"),
    ("Rytis", "Ryčio", "Rytį"),
    ("Aurimas", "Aurimo", "Aurimą"),
]

NAMES_FEMALE_DECLINED = [
    ("Ona", "Onos", "Oną"),
    ("Emilija", "Emilijos", "Emiliją"),
    ("Gabija", "Gabijos", "Gabiją"),
    ("Austėja", "Austėjos", "Austėją"),
    ("Greta", "Gretos", "Gretą"),
    ("Ieva", "Ievos", "Ievą"),
    ("Kotryna", "Kotrynos", "Kotryną"),
    ("Miglė", "Miglės", "Miglę"),
    ("Ugnė", "Ugnės", "Ugnę"),
    ("Liepa", "Liepos", "Liepą"),
    ("Rūta", "Rūtos", "Rūtą"),
    ("Aistė", "Aistės", "Aistę"),
    ("Simona", "Simonos", "Simoną"),
    ("Justina", "Justinos", "Justiną"),
    ("Eglė", "Eglės", "Eglę"),
    ("Monika", "Monikos", "Moniką"),
    ("Laura", "Lauros", "Laurą"),
    ("Kristina", "Kristinos", "Kristiną"),
]


@dataclass
class DeclinedName:
    """Vardas su linksniais."""

    nom: str  # Vardininkas (kas?)
    gen: str  # Kilmininkas (ko?)
    acc: str  # Galininkas (ką?)
    is_male: bool


def get_male_name() -> DeclinedName:
    """Grąžina atsitiktinį vyrišką vardą su linksniais."""
    nom, gen, acc = random.choice(NAMES_MALE_DECLINED)
    return DeclinedName(nom, gen, acc, True)


def get_female_name() -> DeclinedName:
    """Grąžina atsitiktinį moterišką vardą su linksniais."""
    nom, gen, acc = random.choice(NAMES_FEMALE_DECLINED)
    return DeclinedName(nom, gen, acc, False)


def get_random_name() -> DeclinedName:
    """Grąžina atsitiktinį vardą su linksniais."""
    if random.choice([True, False]):
        return get_male_name()
    return get_female_name()


def get_two_names() -> tuple[DeclinedName, DeclinedName]:
    """Grąžina du skirtingus vardus."""
    name1 = get_male_name()
    name2 = get_female_name()
    return (name1, name2)


# Daiktavardžiai su linksniais: (vns_vard, vns_kilm, vns_gal, dgs_vard, dgs_kilm)
ITEMS_DECLINED = {
    "sąsiuvinis": (
        "sąsiuvinis",
        "sąsiuvinio",
        "sąsiuvinį",
        "sąsiuviniai",
        "sąsiuvinių",
    ),
    "pieštukas": ("pieštukas", "pieštuko", "pieštuką", "pieštukai", "pieštukų"),
    "knyga": ("knyga", "knygos", "knygą", "knygos", "knygų"),
    "žaislas": ("žaislas", "žaislo", "žaislą", "žaislai", "žaislų"),
    "obuolys": ("obuolys", "obuolio", "obuolį", "obuoliai", "obuolių"),
    "saldainis": ("saldainis", "saldainio", "saldainį", "saldainiai", "saldainių"),
}


def get_item_form(item_key: str, count: int = 1, case: str = "nom") -> str:
    """
    Grąžina daiktavardį teisingame linksnyje ir skaičiuje.

    Args:
        item_key: Raktas iš ITEMS_DECLINED
        count: Kiekis (nulemia vienaskaitą/daugiskaitą)
        case: "nom" (vardininkas), "gen" (kilmininkas), "acc" (galininkas)
    """
    if item_key not in ITEMS_DECLINED:
        return item_key

    forms = ITEMS_DECLINED[item_key]
    # vns_vard, vns_kilm, vns_gal, dgs_vard, dgs_kilm

    if count == 1:
        if case == "nom":
            return forms[0]
        elif case == "gen":
            return forms[1]
        elif case == "acc":
            return forms[2]
    else:
        if case == "gen":
            return forms[4]
        else:
            return forms[3]

    return forms[0]


# =============================================================================
# SKAITVARDŽIŲ LINKSNIAVIMAS
# =============================================================================

# Daiktavardžiai su visomis formomis pagal skaičių
# Formatas: {raktas: (vns_vard, vns_kilm, dgs_kilm_2_9, dgs_kilm_10_20, dgs_vard)}
# Taisyklė: 1 -> vns_vard, 2-9 paskutinis -> dgs_kilm_2_9, 10-20 arba X0 -> dgs_kilm_10_20
NOUNS_BY_NUMBER = {
    "puslapis": ("puslapis", "puslapio", "puslapiai", "puslapių", "puslapiai"),
    "keleivis": ("keleivis", "keleivio", "keleiviai", "keleivių", "keleiviai"),
    "saldainis": ("saldainis", "saldainio", "saldainiai", "saldainių", "saldainiai"),
    "obuolys": ("obuolys", "obuolio", "obuoliai", "obuolių", "obuoliai"),
    "knyga": ("knyga", "knygos", "knygos", "knygų", "knygos"),
    "euras": ("euras", "euro", "eurai", "eurų", "eurai"),
    "centas": ("centas", "cento", "centai", "centų", "centai"),
    "metras": ("metras", "metro", "metrai", "metrų", "metrai"),
    "kilometras": ("kilometras", "kilometro", "kilometrai", "kilometrų", "kilometrai"),
    "kilogramas": ("kilogramas", "kilogramo", "kilogramai", "kilogramų", "kilogramai"),
    "litras": ("litras", "litro", "litrai", "litrų", "litrai"),
    "valanda": ("valanda", "valandos", "valandos", "valandų", "valandos"),
    "minutė": ("minutė", "minutės", "minutės", "minučių", "minutės"),
    "diena": ("diena", "dienos", "dienos", "dienų", "dienos"),
    "metai": ("metai", "metų", "metai", "metų", "metai"),  # Tik daugiskaita
    "mokinys": ("mokinys", "mokinio", "mokiniai", "mokinių", "mokiniai"),
    "darbininkas": (
        "darbininkas",
        "darbininko",
        "darbininkai",
        "darbininkų",
        "darbininkai",
    ),
    "žmogus": ("žmogus", "žmogaus", "žmonės", "žmonių", "žmonės"),
    "vaikas": ("vaikas", "vaiko", "vaikai", "vaikų", "vaikai"),
    "suolas": ("suolas", "suolo", "suolai", "suolų", "suolai"),
    "dėžė": ("dėžė", "dėžės", "dėžės", "dėžių", "dėžės"),
    "krepšelis": ("krepšelis", "krepšelio", "krepšeliai", "krepšelių", "krepšeliai"),
    "prekė": ("prekė", "prekės", "prekės", "prekių", "prekės"),
    "grybas": ("grybas", "grybo", "grybai", "grybų", "grybai"),
    "bulvė": ("bulvė", "bulvės", "bulvės", "bulvių", "bulvės"),
    "eilė": ("eilė", "eilės", "eilės", "eilių", "eilės"),
}


def skaitvardis(n: int, noun: str, case: str = "gen") -> str:
    """
    Sulinksniuoja daiktavardį pagal skaičių.

    Lietuvių kalbos taisyklės:
    - 1 -> vienaskaita vardininkas: "1 puslapis"
    - 2-9 (paskutinis sk.) -> daugiskaita: "2 puslapiai", "25 puslapiai"
    - 10-20 arba baigiasi 0 -> kilmininkas dgs: "10 puslapių", "20 puslapių"
    - 21-29, 31-39... -> kaip 1-9: "21 puslapis", "22 puslapiai"

    Args:
        n: Skaičius
        noun: Daiktavardžio raktas (pvz., "puslapis")
        case: "nom" arba "gen" (kilmininkas - numatytasis)

    Returns:
        Teisingai sulinksniuota frazė, pvz. "10 puslapių"
    """
    if noun not in NOUNS_BY_NUMBER:
        return f"{n} {noun}"

    forms = NOUNS_BY_NUMBER[noun]
    # (vns_vard, vns_kilm, dgs_vard_2_9, dgs_kilm_10_20, dgs_vard)

    abs_n = abs(n)
    last_digit = abs_n % 10
    last_two = abs_n % 100

    # Specialūs atvejai: 10-20
    if 10 <= last_two <= 20:
        return f"{n} {forms[3]}"  # dgs kilmininkas: "15 puslapių"

    # Paskutinis skaitmuo
    if last_digit == 1:
        return f"{n} {forms[0]}"  # vns vardininkas: "1 puslapis", "21 puslapis"
    elif 2 <= last_digit <= 9:
        return f"{n} {forms[2]}"  # dgs vardininkas: "2 puslapiai", "25 puslapiai"
    else:  # last_digit == 0
        return f"{n} {forms[3]}"  # dgs kilmininkas: "10 puslapių", "100 puslapių"


def daiktavardis_kilm(noun: str, count: int = 1) -> str:
    """Grąžina daiktavardį kilmininke (ko?)."""
    if noun not in NOUNS_BY_NUMBER:
        return noun
    forms = NOUNS_BY_NUMBER[noun]
    if count == 1:
        return forms[1]  # vns kilmininkas
    return forms[3]  # dgs kilmininkas


# =============================================================================
# KONTEKSTINIAI RIBOJIMAI (realūs skaičiai)
# =============================================================================

# Maksimalūs realistiški skaičiai pagal kontekstą
CONTEXT_LIMITS = {
    "autobusas": {"min": 10, "max": 80},  # Autobuse max 80 keleivių
    "klase": {"min": 15, "max": 35},  # Klasėje 15-35 mokiniai
    "grupe": {"min": 5, "max": 20},  # Grupėje 5-20 žmonių
    "seima": {"min": 2, "max": 8},  # Šeimoje 2-8 žmonės
    "knyga": {"min": 50, "max": 500},  # Knygoje 50-500 puslapių
    "saldainiai_vaikas": {"min": 5, "max": 50},  # Vaikas turi 5-50 saldainių
    "obuoliai": {"min": 3, "max": 30},  # Realus obuolių kiekis
    "pinigai_vaikas": {"min": 5, "max": 100},  # Vaiko kišenpinigiai
    "pinigai_suaugęs": {"min": 50, "max": 2000},  # Suaugusio išlaidos
    "atlyginimas": {"min": 800, "max": 3000},  # Atlyginimas Lietuvoje
    "atstumas_pėsčias": {"min": 1, "max": 20},  # Pėsčiomis km
    "atstumas_auto": {"min": 10, "max": 500},  # Automobiliu km
    "greitis_pescias": {"min": 4, "max": 6},  # Pėsčiojo greitis km/h
    "greitis_dviratis": {"min": 15, "max": 25},  # Dviračio greitis km/h
    "greitis_auto": {"min": 50, "max": 120},  # Auto greitis km/h
    "laikas_valandos": {"min": 1, "max": 12},  # Laiko trukmė valandomis
    "laikas_minutes": {"min": 5, "max": 60},  # Laiko trukmė minutėmis
    "amzius_vaikas": {"min": 6, "max": 18},  # Vaiko amžius
    "amzius_suauges": {"min": 25, "max": 65},  # Suaugusio amžius
}


def random_in_context(context: str, difficulty: Difficulty = Difficulty.MEDIUM) -> int:
    """
    Grąžina atsitiktinį skaičių pagal kontekstą ir sunkumą.

    Args:
        context: Konteksto raktas iš CONTEXT_LIMITS
        difficulty: Sunkumo lygis (didina/mažina skaičius)
    """
    if context not in CONTEXT_LIMITS:
        # Fallback - bendri skaičiai
        if difficulty == Difficulty.EASY:
            return random.randint(5, 20)
        elif difficulty == Difficulty.MEDIUM:
            return random.randint(20, 100)
        else:
            return random.randint(100, 500)

    limits = CONTEXT_LIMITS[context]
    min_val = limits["min"]
    max_val = limits["max"]

    # Koreguoti pagal sunkumą
    if difficulty == Difficulty.EASY:
        # Mažesni, "gražūs" skaičiai
        max_val = min_val + (max_val - min_val) // 3
        # Stengtis gauti skaičius, kurie dalinasi iš 5 arba 10
        candidates = [x for x in range(min_val, max_val + 1) if x % 5 == 0]
        if candidates:
            return random.choice(candidates)
    elif difficulty == Difficulty.HARD:
        # Didesni skaičiai
        min_val = min_val + (max_val - min_val) // 2

    return random.randint(min_val, max_val)


@dataclass
class MathProblem:
    """Sugeneruotas matematinis uždavinys."""

    text: str
    answer: str
    answer_numeric: float | int | None = None
    solution_steps: List[str] = field(default_factory=list)
    topic: str = ""
    subtopic: str = ""
    grade_level: int = 6
    difficulty: Difficulty = Difficulty.MEDIUM
    points: int = 2


# Seni vardai atgaliniam suderinamumui (naudokite get_random_name() vietoje)
NAMES_MALE = [n[0] for n in NAMES_MALE_DECLINED]
NAMES_FEMALE = [n[0] for n in NAMES_FEMALE_DECLINED]


def random_name() -> str:
    """DEPRECATED: Naudokite get_random_name() su linksniais."""
    return get_random_name().nom


def male_name() -> str:
    """DEPRECATED: Naudokite get_male_name() su linksniais."""
    return get_male_name().nom


def female_name() -> str:
    """DEPRECATED: Naudokite get_female_name() su linksniais."""
    return get_female_name().nom


# =============================================================================
# 5-6 KLASĖ: NATŪRALIEJI SKAIČIAI, TRUPMENOS, PROCENTAI
# =============================================================================
