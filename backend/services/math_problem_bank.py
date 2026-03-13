"""
Matematinių uždavinių bankas ir šabloninis generatorius
========================================================
Generuoja matematiniu būdu teisingus uždavinius su garantuotais atsakymais.
Nereikia AI - viskas skaičiuojama algoritmiškai.
"""

import math
import random
from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from typing import Callable, List, Optional


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


class Grade5_6_Generators:
    """5-6 klasės uždavinių generatoriai."""

    # -------------------------------------------------------------------------
    # ARITMETIKA
    # -------------------------------------------------------------------------

    @staticmethod
    def addition_context(difficulty: Difficulty) -> MathProblem:
        """Sudėties uždavinys su kontekstu."""
        name = random_name()

        if difficulty == Difficulty.EASY:
            a, b = random.randint(10, 50), random.randint(10, 50)
        elif difficulty == Difficulty.MEDIUM:
            a, b = random.randint(50, 200), random.randint(50, 200)
        else:
            a, b = random.randint(200, 1000), random.randint(200, 1000)

        result = a + b

        contexts = [
            (
                f"{name} turėjo {a} obuolių. Draugas davė dar {b} obuolių. Kiek obuolių dabar turi {name}?",
                [f"{a} + {b} = {result}", f"Atsakymas: {result} obuolių"],
            ),
            (
                f"Bibliotekoje buvo {a} knygų. Atvežė dar {b} knygas. Kiek knygų dabar bibliotekoje?",
                [f"{a} + {b} = {result}", f"Atsakymas: {result} knygų"],
            ),
            (
                f"Pirmą dieną parduotuvė pardavė {a} prekių, antrą dieną - {b} prekių. Kiek prekių pardavė per abi dienas?",
                [f"{a} + {b} = {result}", f"Atsakymas: {result} prekių"],
            ),
            (
                f"{name} surinko {a} grybų, o draugas - {b} grybų. Kiek grybų jie surinko kartu?",
                [f"{a} + {b} = {result}", f"Atsakymas: {result} grybų"],
            ),
        ]

        text, steps = random.choice(contexts)
        return MathProblem(
            text=text,
            answer=str(result),
            answer_numeric=result,
            solution_steps=steps,
            topic="aritmetika",
            subtopic="sudėtis",
            grade_level=5,
            difficulty=difficulty,
            points=1 if difficulty == Difficulty.EASY else 2,
        )

    @staticmethod
    def subtraction_context(difficulty: Difficulty) -> MathProblem:
        """Atimties uždavinys su kontekstu."""
        person = get_random_name()

        # Skirtingi kontekstai su realistiškais limitais
        context_type = random.choice(["saldainiai", "autobusas", "bulvės"])

        if context_type == "autobusas":
            # Autobuse max 80 keleivių
            a = random_in_context("autobusas", difficulty)
            b = random.randint(5, max(6, a - 5))
        elif context_type == "saldainiai":
            if difficulty == Difficulty.EASY:
                a = random.randint(30, 100)
            elif difficulty == Difficulty.MEDIUM:
                a = random.randint(100, 300)
            else:
                a = random.randint(200, 500)
            b = random.randint(10, max(11, a - 10))
        else:  # bulvės
            a = random_in_context("produktas_kg", difficulty)
            b = random.randint(5, max(6, a - 5))

        result = a - b

        contexts = {
            "saldainiai": (
                f"{person.gen} krepšelyje buvo {skaitvardis(a, 'saldainis')}. Suvalgė {b}. Kiek saldainių liko?",
                [
                    f"{a} - {b} = {result}",
                    f"Atsakymas: {skaitvardis(result, 'saldainis')}",
                ],
            ),
            "autobusas": (
                f"Autobuse važiavo {skaitvardis(a, 'keleivis')}. Stotelėje išlipo {b}. Kiek keleivių liko autobuse?",
                [
                    f"{a} - {b} = {result}",
                    f"Atsakymas: {skaitvardis(result, 'keleivis')}",
                ],
            ),
            "bulvės": (
                f"Ūkininkas turėjo {a} kg bulvių. Pardavė {b} kg. Kiek kilogramų liko?",
                [f"{a} - {b} = {result}", f"Atsakymas: {result} kg"],
            ),
        }

        text, steps = contexts[context_type]
        return MathProblem(
            text=text,
            answer=str(result),
            answer_numeric=result,
            solution_steps=steps,
            topic="aritmetika",
            subtopic="atimtis",
            grade_level=5,
            difficulty=difficulty,
            points=1 if difficulty == Difficulty.EASY else 2,
        )

    @staticmethod
    def multiplication_context(difficulty: Difficulty) -> MathProblem:
        """Daugybos uždavinys su kontekstu."""
        name = random_name()

        if difficulty == Difficulty.EASY:
            a, b = random.randint(2, 10), random.randint(2, 10)
        elif difficulty == Difficulty.MEDIUM:
            a, b = random.randint(5, 20), random.randint(3, 15)
        else:
            a, b = random.randint(10, 50), random.randint(5, 30)

        result = a * b

        contexts = [
            (
                f"{name} nupirko {a} sąsiuvinius po {b} ct. Kiek centų sumokėjo?",
                [f"{a} × {b} = {result}", f"Atsakymas: {result} ct"],
            ),
            (
                f"Klasėje yra {a} eilės po {b} suolus. Kiek suolų klasėje?",
                [f"{a} × {b} = {result}", f"Atsakymas: {result} suolų"],
            ),
            (
                f"Viename dėžutėje yra {b} pieštukų. Kiek pieštukų yra {a} dėžutėse?",
                [f"{a} × {b} = {result}", f"Atsakymas: {result} pieštukų"],
            ),
            (
                f"{name} važiavo {a} valandas greičiu {b} km/h. Kokį atstumą nuvažiavo?",
                [f"{a} × {b} = {result}", f"Atsakymas: {result} km"],
            ),
        ]

        text, steps = random.choice(contexts)
        return MathProblem(
            text=text,
            answer=str(result),
            answer_numeric=result,
            solution_steps=steps,
            topic="aritmetika",
            subtopic="daugyba",
            grade_level=5,
            difficulty=difficulty,
            points=1 if difficulty == Difficulty.EASY else 2,
        )

    @staticmethod
    def division_context(difficulty: Difficulty) -> MathProblem:
        """Dalybos uždavinys su kontekstu (visada dalus be liekanos)."""
        name = random_name()

        if difficulty == Difficulty.EASY:
            divisor = random.randint(2, 10)
            quotient = random.randint(2, 10)
        elif difficulty == Difficulty.MEDIUM:
            divisor = random.randint(3, 15)
            quotient = random.randint(5, 20)
        else:
            divisor = random.randint(5, 25)
            quotient = random.randint(10, 40)

        dividend = divisor * quotient  # Užtikrinam, kad dalus be liekanos

        contexts = [
            (
                f"{name} turi {dividend} saldainių. Nori padalinti po lygiai {divisor} draugams. Po kiek saldainių gaus kiekvienas?",
                [
                    f"{dividend} ÷ {divisor} = {quotient}",
                    f"Atsakymas: po {quotient} saldainius",
                ],
            ),
            (
                f"Mokykloje yra {dividend} mokinių. Jie suskirstyti į {divisor} klases po lygiai. Kiek mokinių kiekvienoje klasėje?",
                [
                    f"{dividend} ÷ {divisor} = {quotient}",
                    f"Atsakymas: {quotient} mokinių",
                ],
            ),
            (
                f"Ūkininkas {dividend} kg obuolių supakavo į dėžes po {divisor} kg. Kiek dėžių prireikė?",
                [
                    f"{dividend} ÷ {divisor} = {quotient}",
                    f"Atsakymas: {quotient} dėžių",
                ],
            ),
        ]

        text, steps = random.choice(contexts)
        return MathProblem(
            text=text,
            answer=str(quotient),
            answer_numeric=quotient,
            solution_steps=steps,
            topic="aritmetika",
            subtopic="dalyba",
            grade_level=5,
            difficulty=difficulty,
            points=1 if difficulty == Difficulty.EASY else 2,
        )

    @staticmethod
    def division_with_remainder(difficulty: Difficulty) -> MathProblem:
        """Dalyba su liekana."""
        name = random_name()

        if difficulty == Difficulty.EASY:
            divisor = random.randint(3, 7)
            quotient = random.randint(3, 10)
            remainder = random.randint(1, divisor - 1)
        else:
            divisor = random.randint(5, 15)
            quotient = random.randint(5, 20)
            remainder = random.randint(1, divisor - 1)

        dividend = divisor * quotient + remainder

        text = f"{name} turi {dividend} obuolių. Nori sudėti į krepšelius po {divisor}. Kiek krepšelių prireiks ir kiek obuolių liks?"
        steps = [
            f"{dividend} ÷ {divisor} = {quotient} (liekana {remainder})",
            f"Atsakymas: {quotient} krepšeliai ir {remainder} obuoliai liks",
        ]

        return MathProblem(
            text=text,
            answer=f"{quotient} krepš., liekana {remainder}",
            solution_steps=steps,
            topic="aritmetika",
            subtopic="dalyba su liekana",
            grade_level=5,
            difficulty=difficulty,
            points=2,
        )

    # -------------------------------------------------------------------------
    # TRUPMENOS
    # -------------------------------------------------------------------------

    @staticmethod
    def fraction_part_of_whole(difficulty: Difficulty) -> MathProblem:
        """Dalies radimas iš sveiko skaičiaus."""
        name = random_name()

        # Pasirenkam trupmenas su gražiais rezultatais
        fractions_easy = [(1, 2), (1, 3), (1, 4), (2, 3), (3, 4), (1, 5), (2, 5)]
        fractions_medium = [(1, 6), (5, 6), (2, 7), (3, 8), (5, 8), (4, 9)]

        if difficulty == Difficulty.EASY:
            num, denom = random.choice(fractions_easy)
            whole = denom * random.randint(2, 8)
        else:
            num, denom = random.choice(fractions_medium)
            whole = denom * random.randint(3, 12)

        result = whole * num // denom

        contexts = [
            (
                f"Klasėje yra {whole} mokinių. {num}/{denom} jų lanko būrelį. Kiek mokinių lanko būrelį?",
                [
                    f"{whole} × {num}/{denom} = {whole} × {num} ÷ {denom} = {whole * num} ÷ {denom} = {result}",
                    f"Atsakymas: {result} mokinių",
                ],
            ),
            (
                f"{name} turėjo {whole} eurų. Išleido {num}/{denom} pinigų. Kiek eurų išleido?",
                [f"{whole} × {num}/{denom} = {result}", f"Atsakymas: {result} eurų"],
            ),
            (
                f"Knygoje yra {whole} puslapių. {name} perskaitė {num}/{denom} knygos. Kiek puslapių perskaitė?",
                [
                    f"{whole} × {num}/{denom} = {result}",
                    f"Atsakymas: {result} puslapių",
                ],
            ),
        ]

        text, steps = random.choice(contexts)
        return MathProblem(
            text=text,
            answer=str(result),
            answer_numeric=result,
            solution_steps=steps,
            topic="trupmenos",
            subtopic="dalies radimas",
            grade_level=5,
            difficulty=difficulty,
            points=2,
        )

    @staticmethod
    def fraction_find_whole(difficulty: Difficulty) -> MathProblem:
        """Sveiko skaičiaus radimas pagal dalį."""
        name = random_name()

        fractions = [(1, 2), (1, 3), (1, 4), (2, 3), (3, 4), (1, 5), (2, 5), (3, 5)]
        num, denom = random.choice(fractions)

        if difficulty == Difficulty.EASY:
            whole = denom * random.randint(2, 6)
        else:
            whole = denom * random.randint(4, 12)

        part = whole * num // denom

        contexts = [
            (
                f"{name} perskaitė {part} iš visų knygos puslapių, tai sudaro {num}/{denom} visos knygos. Kiek puslapių yra knygoje?",
                [
                    f"Jei {num}/{denom} = {part}, tai 1/{denom} = {part // num}",
                    f"Visa knyga = {part // num} × {denom} = {whole}",
                    f"Atsakymas: {skaitvardis(whole, 'puslapis')}",
                ],
            ),
            (
                f"Turistai nuėjo {part} km, tai sudaro {num}/{denom} viso kelio. Koks viso kelio ilgis?",
                [f"{part} ÷ {num} × {denom} = {whole}", f"Atsakymas: {whole} km"],
            ),
        ]

        text, steps = random.choice(contexts)
        return MathProblem(
            text=text,
            answer=str(whole),
            answer_numeric=whole,
            solution_steps=steps,
            topic="trupmenos",
            subtopic="sveiko radimas",
            grade_level=6,
            difficulty=difficulty,
            points=3,
        )

    @staticmethod
    def fraction_addition(difficulty: Difficulty) -> MathProblem:
        """
        Trupmenų sudėtis.

        SVARBU: 5 klasei (EASY lygis) naudojami TIK vienodi vardikliai!
        Skirtingi vardikliai tik 6+ klasei (MEDIUM, HARD).
        """
        if difficulty == Difficulty.EASY:
            # 5 KLASĖ: TIK vienodi vardikliai!
            denom = random.choice([2, 3, 4, 5, 6, 8])
            num1 = random.randint(1, denom - 2)
            num2 = random.randint(1, denom - num1 - 1)

            result_num = num1 + num2
            result = Fraction(result_num, denom)
            text = f"Apskaičiuok: {num1}/{denom} + {num2}/{denom}"
            steps = [f"{num1}/{denom} + {num2}/{denom} = {result_num}/{denom}"]
            if result_num != result.numerator or denom != result.denominator:
                steps.append(f"= {result.numerator}/{result.denominator}")
            grade = 5

        elif difficulty == Difficulty.MEDIUM:
            # 5 KLASĖ (sunkesnis): Dar vis vienodi vardikliai, bet mišrieji skaičiai
            denom = random.choice([3, 4, 5, 6, 7, 8])
            num1 = random.randint(1, denom - 1)
            num2 = random.randint(1, denom - 1)
            # Mišrusis skaičius: 1 num1/denom + num2/denom
            whole = 1
            total_num = whole * denom + num1 + num2
            result = Fraction(total_num, denom)
            text = f"Apskaičiuok: 1 {num1}/{denom} + {num2}/{denom}"
            steps = [
                f"1 {num1}/{denom} = {denom + num1}/{denom}",
                f"{denom + num1}/{denom} + {num2}/{denom} = {total_num}/{denom}",
            ]
            if result.numerator >= result.denominator:
                whole_part = result.numerator // result.denominator
                remainder = result.numerator % result.denominator
                if remainder > 0:
                    steps.append(f"= {whole_part} {remainder}/{result.denominator}")
            grade = 5  # Vis dar 5 klasė, nes vienodi vardikliai

        else:  # HARD - 6+ klasė
            # 6 KLASĖ: Skirtingi vardikliai
            denom1 = random.choice([2, 3, 4, 5, 6])
            denom2 = random.choice([2, 3, 4, 5, 6])
            while denom1 == denom2:  # Užtikrinam, kad skirtingi
                denom2 = random.choice([2, 3, 4, 5, 6])
            num1 = random.randint(1, denom1 - 1)
            num2 = random.randint(1, denom2 - 1)

            f1 = Fraction(num1, denom1)
            f2 = Fraction(num2, denom2)
            result = f1 + f2
            text = f"Apskaičiuok: {num1}/{denom1} + {num2}/{denom2}"
            common_denom = (denom1 * denom2) // math.gcd(denom1, denom2)
            steps = [
                f"Bendras vardiklis: {common_denom}",
                f"{num1}/{denom1} = {num1 * common_denom // denom1}/{common_denom}",
                f"{num2}/{denom2} = {num2 * common_denom // denom2}/{common_denom}",
                f"Suma = {result.numerator}/{result.denominator}",
            ]
            grade = 6  # Skirtingi vardikliai = 6 klasė

        answer = (
            f"{result.numerator}/{result.denominator}"
            if result.denominator != 1
            else str(result.numerator)
        )

        return MathProblem(
            text=text,
            answer=answer,
            solution_steps=steps,
            topic="trupmenos",
            subtopic="sudėtis",
            grade_level=grade,
            difficulty=difficulty,
            points=2,
        )

    # -------------------------------------------------------------------------
    # PROCENTAI
    # -------------------------------------------------------------------------

    @staticmethod
    def percent_find_part(difficulty: Difficulty) -> MathProblem:
        """Procentų dalies radimas."""
        name = random_name()

        # Pasirenkami "gražūs" procentai ir skaičiai
        percents = [10, 20, 25, 30, 40, 50, 75]
        percent = random.choice(percents)

        if difficulty == Difficulty.EASY:
            base = random.choice([50, 100, 200])
        elif difficulty == Difficulty.MEDIUM:
            base = random.choice([80, 120, 150, 250, 300, 400])
        else:
            base = random.choice([180, 240, 360, 450, 600, 800])

        result = base * percent // 100

        contexts = [
            (
                f"Prekė kainuoja {base} €. Nuolaida {percent}%. Kokia nuolaidos suma?",
                [
                    f"{base} × {percent}% = {base} × {percent}/100 = {result}",
                    f"Atsakymas: {result} €",
                ],
            ),
            (
                f"Klasėje yra {base} mokinių. {percent}% mokinių lanko sporto būrelį. Kiek mokinių lanko būrelį?",
                [f"{base} × {percent}/100 = {result}", f"Atsakymas: {result} mokinių"],
            ),
            (
                f"{name} uždirbo {base} €. Sutaupė {percent}% atlyginimo. Kiek eurų sutaupė?",
                [f"{base} × {percent}/100 = {result}", f"Atsakymas: {result} €"],
            ),
        ]

        text, steps = random.choice(contexts)
        return MathProblem(
            text=text,
            answer=str(result),
            answer_numeric=result,
            solution_steps=steps,
            topic="procentai",
            subtopic="dalies radimas",
            grade_level=6,
            difficulty=difficulty,
            points=2,
        )

    @staticmethod
    def percent_find_whole(difficulty: Difficulty) -> MathProblem:
        """Viso skaičiaus radimas pagal procentus."""
        name = random_name()

        percents = [10, 20, 25, 50]
        percent = random.choice(percents)

        if difficulty == Difficulty.EASY:
            whole = random.choice([100, 200, 400])
        else:
            whole = random.choice([80, 120, 160, 240, 300])

        part = whole * percent // 100

        text = f"{name} išleido {part} €, tai sudaro {percent}% visų pinigų. Kiek pinigų turėjo iš pradžių?"
        steps = [
            f"Jei {percent}% = {part} €",
            f"Tai 1% = {part} ÷ {percent} = {part / percent}",
            f"100% = {part / percent} × 100 = {whole}",
            f"Atsakymas: {whole} €",
        ]

        return MathProblem(
            text=text,
            answer=str(whole),
            answer_numeric=whole,
            solution_steps=steps,
            topic="procentai",
            subtopic="viso radimas",
            grade_level=6,
            difficulty=difficulty,
            points=3,
        )

    @staticmethod
    def percent_discount(difficulty: Difficulty) -> MathProblem:
        """Kainos su nuolaida skaičiavimas."""
        percents = [10, 15, 20, 25, 30, 40, 50]
        percent = random.choice(percents)

        # Pasirenkam kainą, kad nuolaida būtų sveika
        if difficulty == Difficulty.EASY:
            price = random.choice([20, 40, 50, 80, 100])
        else:
            price = random.choice([60, 90, 120, 150, 180, 200, 250])

        discount = price * percent // 100
        final_price = price - discount

        text = (
            f"Prekė kainavo {price} €. Nuolaida {percent}%. Kokia kaina po nuolaidos?"
        )
        steps = [
            f"Nuolaida: {price} × {percent}/100 = {discount} €",
            f"Kaina po nuolaidos: {price} - {discount} = {final_price} €",
            f"Atsakymas: {final_price} €",
        ]

        return MathProblem(
            text=text,
            answer=f"{final_price} €",
            answer_numeric=final_price,
            solution_steps=steps,
            topic="procentai",
            subtopic="nuolaida",
            grade_level=6,
            difficulty=difficulty,
            points=2,
        )

    @staticmethod
    def percent_increase(difficulty: Difficulty) -> MathProblem:
        """Padidėjimo procentais skaičiavimas."""
        person = get_random_name()
        percents = [10, 20, 25, 50]
        percent = random.choice(percents)

        # Naudojame realistiškus atlyginimus
        if difficulty == Difficulty.EASY:
            original = random.choice([1000, 1200, 1500, 2000])
        else:
            original = random.choice([800, 1100, 1350, 1800, 2500])

        increase = original * percent // 100
        final = original + increase

        # Naudojame kilmininką: "Gedimino atlyginimas", ne "Gediminas atlyginimas"
        text = f"{person.gen} atlyginimas buvo {original} €. Jis padidėjo {percent}%. Koks atlyginimas dabar?"
        steps = [
            f"Padidėjimas: {original} × {percent}/100 = {increase} €",
            f"Naujas atlyginimas: {original} + {increase} = {final} €",
            f"Atsakymas: {final} €",
        ]

        return MathProblem(
            text=text,
            answer=f"{final} €",
            answer_numeric=final,
            solution_steps=steps,
            topic="procentai",
            subtopic="padidėjimas",
            grade_level=6,
            difficulty=difficulty,
            points=2,
        )

    # -------------------------------------------------------------------------
    # GEOMETRIJA (5-6 klasė)
    # -------------------------------------------------------------------------

    @staticmethod
    def rectangle_perimeter(difficulty: Difficulty) -> MathProblem:
        """Stačiakampio perimetras."""
        if difficulty == Difficulty.EASY:
            a = random.randint(3, 15)
            b = random.randint(3, 15)
        else:
            a = random.randint(10, 50)
            b = random.randint(10, 50)

        perimeter = 2 * (a + b)

        text = f"Stačiakampio ilgis {a} cm, plotis {b} cm. Apskaičiuok perimetrą."
        steps = [
            f"P = 2 × (a + b)",
            f"P = 2 × ({a} + {b})",
            f"P = 2 × {a + b} = {perimeter} cm",
            f"Atsakymas: {perimeter} cm",
        ]

        return MathProblem(
            text=text,
            answer=f"{perimeter} cm",
            answer_numeric=perimeter,
            solution_steps=steps,
            topic="geometrija",
            subtopic="perimetras",
            grade_level=5,
            difficulty=difficulty,
            points=2,
        )

    @staticmethod
    def rectangle_area(difficulty: Difficulty) -> MathProblem:
        """Stačiakampio plotas."""
        if difficulty == Difficulty.EASY:
            a = random.randint(3, 12)
            b = random.randint(3, 12)
        else:
            a = random.randint(8, 25)
            b = random.randint(8, 25)

        area = a * b

        contexts = [
            f"Stačiakampio ilgis {a} cm, plotis {b} cm. Apskaičiuok plotą.",
            f"Kambario grindys yra stačiakampio formos: {a} m × {b} m. Koks grindų plotas?",
            f"Sodo sklypas yra {a} m ilgio ir {b} m pločio. Koks sklypo plotas?",
        ]

        text = random.choice(contexts)
        unit = "m²" if "m ×" in text or "m ilgio" in text else "cm²"

        steps = [
            f"S = a × b",
            f"S = {a} × {b} = {area} {unit}",
            f"Atsakymas: {area} {unit}",
        ]

        return MathProblem(
            text=text,
            answer=f"{area} {unit}",
            answer_numeric=area,
            solution_steps=steps,
            topic="geometrija",
            subtopic="plotas",
            grade_level=5,
            difficulty=difficulty,
            points=2,
        )

    @staticmethod
    def square_perimeter_area(difficulty: Difficulty) -> MathProblem:
        """Kvadrato perimetras ir plotas."""
        if difficulty == Difficulty.EASY:
            a = random.randint(3, 15)
        else:
            a = random.randint(10, 30)

        perimeter = 4 * a
        area = a * a

        text = f"Kvadrato kraštinė {a} cm. Apskaičiuok perimetrą ir plotą."
        steps = [
            f"Perimetras: P = 4 × a = 4 × {a} = {perimeter} cm",
            f"Plotas: S = a² = {a}² = {area} cm²",
            f"Atsakymas: P = {perimeter} cm, S = {area} cm²",
        ]

        return MathProblem(
            text=text,
            answer=f"P = {perimeter} cm, S = {area} cm²",
            solution_steps=steps,
            topic="geometrija",
            subtopic="kvadratas",
            grade_level=5,
            difficulty=difficulty,
            points=3,
        )

    @staticmethod
    def triangle_area(difficulty: Difficulty) -> MathProblem:
        """Trikampio plotas."""
        # Pasirenkam taip, kad plotas būtų sveikas
        if difficulty == Difficulty.EASY:
            base = random.choice([4, 6, 8, 10, 12])
            height = random.choice([2, 4, 6, 8, 10])
        else:
            base = random.choice([6, 8, 10, 12, 14, 16])
            height = random.choice([5, 7, 9, 11, 13])

        area = base * height // 2

        text = (
            f"Trikampio pagrindas {base} cm, aukštinė {height} cm. Apskaičiuok plotą."
        )
        steps = [
            f"S = (a × h) / 2",
            f"S = ({base} × {height}) / 2",
            f"S = {base * height} / 2 = {area} cm²",
            f"Atsakymas: {area} cm²",
        ]

        return MathProblem(
            text=text,
            answer=f"{area} cm²",
            answer_numeric=area,
            solution_steps=steps,
            topic="geometrija",
            subtopic="trikampio plotas",
            grade_level=6,
            difficulty=difficulty,
            points=2,
        )

    @staticmethod
    def circle_circumference(difficulty: Difficulty) -> MathProblem:
        """Apskritimo ilgis."""
        if difficulty == Difficulty.EASY:
            r = random.choice([5, 7, 10, 14])
        else:
            r = random.choice([3, 6, 8, 11, 15, 21])

        # Naudojam π ≈ 3.14
        circumference = round(2 * 3.14 * r, 2)

        text = f"Apskritimo spindulys {r} cm. Apskaičiuok apskritimo ilgį (π ≈ 3,14)."
        steps = [
            f"C = 2πr",
            f"C = 2 × 3,14 × {r}",
            f"C = {circumference} cm",
            f"Atsakymas: {circumference} cm",
        ]

        return MathProblem(
            text=text,
            answer=f"{circumference} cm",
            answer_numeric=circumference,
            solution_steps=steps,
            topic="geometrija",
            subtopic="apskritimo ilgis",
            grade_level=6,
            difficulty=difficulty,
            points=2,
        )

    # -------------------------------------------------------------------------
    # PAPRASTOS LYGTYS (5 klasė) - TIK natūralieji skaičiai, be neigiamų!
    # -------------------------------------------------------------------------

    @staticmethod
    def simple_equation_addition_5(difficulty: Difficulty) -> MathProblem:
        """
        Paprasta lygtis x + a = b (5 klasė).

        SVARBU: Tik natūralieji skaičiai, jokių neigiamų!
        """
        if difficulty == Difficulty.EASY:
            # x + a = b, kur x, a, b > 0
            x = random.randint(5, 20)
            a = random.randint(5, 20)
            b = x + a
        elif difficulty == Difficulty.MEDIUM:
            x = random.randint(10, 50)
            a = random.randint(10, 50)
            b = x + a
        else:  # HARD
            x = random.randint(20, 100)
            a = random.randint(20, 100)
            b = x + a

        text = f"Išspręsk lygtį: x + {a} = {b}"
        steps = [
            f"x + {a} = {b}",
            f"x = {b} - {a}",
            f"x = {x}",
            f"Patikra: {x} + {a} = {b} ✓",
        ]

        return MathProblem(
            text=text,
            answer=str(x),
            answer_numeric=x,
            solution_steps=steps,
            topic="lygtys",
            subtopic="paprasta lygtis",
            grade_level=5,
            difficulty=difficulty,
            points=2,
        )

    @staticmethod
    def simple_equation_subtraction_5(difficulty: Difficulty) -> MathProblem:
        """
        Paprasta lygtis x - a = b (5 klasė).

        SVARBU: Tik natūralieji skaičiai, x > a, b > 0!
        """
        if difficulty == Difficulty.EASY:
            a = random.randint(5, 15)
            b = random.randint(5, 20)
            x = a + b  # Užtikrinam, kad x - a = b duoda teigiamą
        elif difficulty == Difficulty.MEDIUM:
            a = random.randint(10, 30)
            b = random.randint(10, 40)
            x = a + b
        else:  # HARD
            a = random.randint(20, 50)
            b = random.randint(20, 60)
            x = a + b

        text = f"Išspręsk lygtį: x - {a} = {b}"
        steps = [
            f"x - {a} = {b}",
            f"x = {b} + {a}",
            f"x = {x}",
            f"Patikra: {x} - {a} = {b} ✓",
        ]

        return MathProblem(
            text=text,
            answer=str(x),
            answer_numeric=x,
            solution_steps=steps,
            topic="lygtys",
            subtopic="paprasta lygtis",
            grade_level=5,
            difficulty=difficulty,
            points=2,
        )

    @staticmethod
    def simple_equation_multiplication_5(difficulty: Difficulty) -> MathProblem:
        """
        Paprasta lygtis a * x = b (5 klasė).

        SVARBU: Tik natūralieji skaičiai, b dalijasi iš a!
        """
        if difficulty == Difficulty.EASY:
            a = random.randint(2, 5)
            x = random.randint(2, 10)
        elif difficulty == Difficulty.MEDIUM:
            a = random.randint(3, 8)
            x = random.randint(5, 15)
        else:  # HARD
            a = random.randint(4, 12)
            x = random.randint(8, 20)

        b = a * x  # Užtikrinam, kad dalijasi be liekanos

        text = f"Išspręsk lygtį: {a}x = {b}"
        steps = [
            f"{a}x = {b}",
            f"x = {b} ÷ {a}",
            f"x = {x}",
            f"Patikra: {a} × {x} = {b} ✓",
        ]

        return MathProblem(
            text=text,
            answer=str(x),
            answer_numeric=x,
            solution_steps=steps,
            topic="lygtys",
            subtopic="paprasta lygtis",
            grade_level=5,
            difficulty=difficulty,
            points=2,
        )

    @staticmethod
    def simple_equation_unknown_minuend_5(difficulty: Difficulty) -> MathProblem:
        """
        Lygtis a - x = b (5 klasė) - nežinomasis yra atimamasis.

        SVARBU: Tik natūralieji skaičiai, a > b, x > 0!
        Ši lygtis dažnai klaidina mokinius.
        """
        if difficulty == Difficulty.EASY:
            b = random.randint(5, 15)
            x = random.randint(5, 15)
            a = b + x  # a - x = b, tai a = b + x
        elif difficulty == Difficulty.MEDIUM:
            b = random.randint(10, 30)
            x = random.randint(10, 25)
            a = b + x
        else:  # HARD
            b = random.randint(20, 50)
            x = random.randint(15, 40)
            a = b + x

        text = f"Išspręsk lygtį: {a} - x = {b}"
        steps = [
            f"{a} - x = {b}",
            f"x = {a} - {b}",
            f"x = {x}",
            f"Patikra: {a} - {x} = {b} ✓",
        ]

        return MathProblem(
            text=text,
            answer=str(x),
            answer_numeric=x,
            solution_steps=steps,
            topic="lygtys",
            subtopic="paprasta lygtis",
            grade_level=5,
            difficulty=difficulty,
            points=2,
        )

    @staticmethod
    def equation_word_problem_5(difficulty: Difficulty) -> MathProblem:
        """
        Tekstinis uždavinys su lygtimi (5 klasė).

        SVARBU: Tik natūralieji skaičiai!
        """
        name = get_random_name()

        if difficulty == Difficulty.EASY:
            # Petras galvoja skaičių. Pridėjęs 5, gavo 12. Koks tas skaičius?
            a = random.randint(3, 10)
            result = random.randint(10, 25)
            x = result - a

            text = f"{name.nom} galvoja skaičių. Pridėjęs {a}, gavo {result}. Koks tas skaičius?"
            steps = [
                f"Sudarome lygtį: x + {a} = {result}",
                f"x = {result} - {a}",
                f"x = {x}",
                f"Atsakymas: {name.nom} galvojo skaičių {x}",
            ]

        elif difficulty == Difficulty.MEDIUM:
            # Tėtis dvigubai vyresnis už sūnų. Kartu jiems 45 metai.
            son_age = random.randint(10, 20)
            total = son_age * 3

            text = f"Tėtis dvigubai vyresnis už sūnų. Kartu jiems {total} metų. Kiek metų sūnui?"
            steps = [
                "Tegu sūnaus amžius = x",
                "Tada tėvo amžius = 2x",
                f"x + 2x = {total}",
                f"3x = {total}",
                f"x = {total // 3}",
                f"Atsakymas: Sūnui {son_age} metų",
            ]
            x = son_age

        else:  # HARD
            # Stačiakampio perimetras 30 cm. Ilgis 3 cm didesnis už plotį. Rask kraštines.
            width = random.randint(4, 10)
            diff = random.randint(2, 5)
            length = width + diff
            perimeter = 2 * (length + width)

            text = f"Stačiakampio perimetras {perimeter} cm. Ilgis {diff} cm didesnis už plotį. Rask kraštines."
            steps = [
                "Tegu plotis = x cm",
                f"Tada ilgis = x + {diff} cm",
                f"Perimetras: 2(x + x + {diff}) = {perimeter}",
                f"2(2x + {diff}) = {perimeter}",
                f"4x + {2 * diff} = {perimeter}",
                f"4x = {perimeter - 2 * diff}",
                f"x = {width}",
                f"Atsakymas: plotis = {width} cm, ilgis = {length} cm",
            ]
            x = width

        return MathProblem(
            text=text,
            answer=str(x),
            answer_numeric=x,
            solution_steps=steps,
            topic="lygtys",
            subtopic="tekstinis uždavinys",
            grade_level=5,
            difficulty=difficulty,
            points=3 if difficulty == Difficulty.HARD else 2,
        )


# =============================================================================
# 7-8 KLASĖ: LYGTYS, PROPORCIJOS, FUNKCIJOS
# =============================================================================


class Grade7_8_Generators:
    """7-8 klasės uždavinių generatoriai."""

    # -------------------------------------------------------------------------
    # TIESINĖS LYGTYS
    # -------------------------------------------------------------------------

    @staticmethod
    def linear_equation_simple(difficulty: Difficulty) -> MathProblem:
        """Paprasta tiesinė lygtis ax + b = c."""
        # Pirma pasirenkam atsakymą, tada konstruojam lygtį
        if difficulty == Difficulty.EASY:
            x = random.randint(1, 10)
            a = random.randint(2, 5)
            b = random.randint(1, 20)
        elif difficulty == Difficulty.MEDIUM:
            x = random.randint(-10, 10)
            a = random.randint(2, 8)
            b = random.randint(-20, 20)
        else:
            x = random.randint(-20, 20)
            a = random.randint(2, 12)
            b = random.randint(-50, 50)

        c = a * x + b

        # Formatuojam lygtį
        if b >= 0:
            eq = f"{a}x + {b} = {c}"
        else:
            eq = f"{a}x - {abs(b)} = {c}"

        text = f"Išspręsk lygtį: {eq}"
        steps = [
            f"{eq}",
            f"{a}x = {c} - ({b})" if b >= 0 else f"{a}x = {c} + {abs(b)}",
            f"{a}x = {c - b}",
            f"x = {c - b} ÷ {a}",
            f"x = {x}",
            f"Atsakymas: x = {x}",
        ]

        return MathProblem(
            text=text,
            answer=f"x = {x}",
            answer_numeric=x,
            solution_steps=steps,
            topic="lygtys",
            subtopic="tiesinė lygtis",
            grade_level=7,
            difficulty=difficulty,
            points=2,
        )

    @staticmethod
    def linear_equation_both_sides(difficulty: Difficulty) -> MathProblem:
        """Lygtis su x abiejose pusėse: ax + b = cx + d."""
        x = (
            random.randint(1, 15)
            if difficulty == Difficulty.EASY
            else random.randint(-15, 15)
        )

        a = random.randint(3, 8)
        c = random.randint(1, a - 1)  # c < a, kad x būtų teigiamas koeficientas
        b = random.randint(-20, 20)
        d = (a - c) * x + b

        # Formatuojam
        left = f"{a}x + {b}" if b >= 0 else f"{a}x - {abs(b)}"
        right = f"{c}x + {d}" if d >= 0 else f"{c}x - {abs(d)}"

        text = f"Išspręsk lygtį: {left} = {right}"
        steps = [
            f"{left} = {right}",
            f"{a}x - {c}x = {d} - ({b})",
            f"{a - c}x = {d - b}",
            f"x = {d - b} ÷ {a - c}",
            f"x = {x}",
            f"Atsakymas: x = {x}",
        ]

        return MathProblem(
            text=text,
            answer=f"x = {x}",
            answer_numeric=x,
            solution_steps=steps,
            topic="lygtys",
            subtopic="lygtis su x abiejose pusėse",
            grade_level=7,
            difficulty=difficulty,
            points=3,
        )

    @staticmethod
    def equation_word_problem_age(difficulty: Difficulty) -> MathProblem:
        """Tekstinis uždavinys apie amžių."""
        # Naudojame vardus su linksniais
        person1 = get_male_name()
        person2 = get_female_name()

        # Dabartinis amžius
        if difficulty == Difficulty.EASY:
            age1 = random.randint(8, 15)
            multiplier = random.randint(2, 4)
        else:
            age1 = random.randint(10, 20)
            multiplier = random.randint(2, 5)

        age2 = age1 * multiplier

        # Naudojame galininką (ką?) po "už"
        text = f"{person2.nom} yra {multiplier} kartus vyresnė už {person1.acc}. Kartu jiems {age1 + age2} metai. Kiek metų kiekvienam?"
        steps = [
            f"Tegu {person1.gen} amžius = x",
            f"Tada {person2.gen} amžius = {multiplier}x",
            f"x + {multiplier}x = {age1 + age2}",
            f"{multiplier + 1}x = {age1 + age2}",
            f"x = {age1}",
            f"{person1.nom}: {age1} m., {person2.nom}: {age2} m.",
        ]

        return MathProblem(
            text=text,
            answer=f"{person1.nom}: {age1} m., {person2.nom}: {age2} m.",
            solution_steps=steps,
            topic="lygtys",
            subtopic="amžiaus uždavinys",
            grade_level=7,
            difficulty=difficulty,
            points=3,
        )

    @staticmethod
    def equation_word_problem_purchase(difficulty: Difficulty) -> MathProblem:
        """Tekstinis uždavinys apie pirkimą."""
        name = random_name()

        # Kaina ir kiekis
        if difficulty == Difficulty.EASY:
            price = random.randint(2, 8)
            quantity = random.randint(3, 8)
            extra = random.randint(5, 15)
        else:
            price = random.randint(5, 15)
            quantity = random.randint(4, 10)
            extra = random.randint(10, 30)

        total = price * quantity + extra

        # Teisingi linksniai: (galininkas dgs, vardininkas vns, kilmininkas vns)
        items = random.choice(
            [
                ("sąsiuvinius", "sąsiuvinis", "sąsiuvinio"),
                ("pieštukus", "pieštukas", "pieštuko"),
                ("knygas", "knyga", "knygos"),
                ("žaislus", "žaislas", "žaislo"),
            ]
        )

        text = f"{name} nupirko {quantity} {items[0]} ir dar vieną daiktą už {extra} €. Iš viso sumokėjo {total} €. Kiek kainavo viena {items[1]}?"
        steps = [
            f"Tegu vieno {items[2]} kaina = x",
            f"{quantity}x + {extra} = {total}",
            f"{quantity}x = {total} - {extra}",
            f"{quantity}x = {total - extra}",
            f"x = {price}",
            f"Atsakymas: {price} €",
        ]

        return MathProblem(
            text=text,
            answer=f"{price} €",
            answer_numeric=price,
            solution_steps=steps,
            topic="lygtys",
            subtopic="pirkimo uždavinys",
            grade_level=7,
            difficulty=difficulty,
            points=3,
        )

    @staticmethod
    def equation_word_problem_geometry(difficulty: Difficulty) -> MathProblem:
        """Tekstinis uždavinys su geometrija."""
        # Stačiakampio perimetras
        if difficulty == Difficulty.EASY:
            width = random.randint(5, 15)
            diff = random.randint(2, 8)
        else:
            width = random.randint(10, 25)
            diff = random.randint(5, 15)

        length = width + diff
        perimeter = 2 * (length + width)

        text = f"Stačiakampio perimetras {perimeter} cm. Ilgis {diff} cm didesnis už plotį. Rask stačiakampio matmenis."
        steps = [
            f"Tegu plotis = x, tada ilgis = x + {diff}",
            f"Perimetras: 2(x + x + {diff}) = {perimeter}",
            f"2(2x + {diff}) = {perimeter}",
            f"4x + {2 * diff} = {perimeter}",
            f"4x = {perimeter - 2 * diff}",
            f"x = {width}",
            f"Plotis = {width} cm, ilgis = {length} cm",
        ]

        return MathProblem(
            text=text,
            answer=f"plotis {width} cm, ilgis {length} cm",
            solution_steps=steps,
            topic="lygtys",
            subtopic="geometrijos uždavinys",
            grade_level=7,
            difficulty=difficulty,
            points=4,
        )

    # -------------------------------------------------------------------------
    # PROPORCIJOS IR SANTYKIAI
    # -------------------------------------------------------------------------

    @staticmethod
    def ratio_simple(difficulty: Difficulty) -> MathProblem:
        """Paprastas santykio uždavinys."""
        name = random_name()

        # Santykis a:b
        ratios = [(1, 2), (1, 3), (2, 3), (1, 4), (3, 4), (2, 5), (3, 5)]
        a, b = random.choice(ratios)

        if difficulty == Difficulty.EASY:
            multiplier = random.randint(2, 8)
        else:
            multiplier = random.randint(5, 15)

        total = (a + b) * multiplier
        part1 = a * multiplier
        part2 = b * multiplier

        contexts = [
            (
                f"{name} ir draugas pasidalino {total} obuolių santykiu {a}:{b}. Kiek obuolių gavo kiekvienas?",
                f"{name}: {part1}, draugas: {part2}",
            ),
            (
                f"Mišinys sudarytas iš vandens ir sirupo santykiu {a}:{b}. Kiek kiekvienos medžiagos yra {total} ml mišinio?",
                f"vanduo: {part1} ml, sirupas: {part2} ml",
            ),
        ]

        text, answer = random.choice(contexts)
        steps = [
            f"Santykis {a}:{b}, viso dalių: {a} + {b} = {a + b}",
            f"Viena dalis: {total} ÷ {a + b} = {multiplier}",
            f"Pirma dalis: {a} × {multiplier} = {part1}",
            f"Antra dalis: {b} × {multiplier} = {part2}",
            f"Atsakymas: {answer}",
        ]

        return MathProblem(
            text=text,
            answer=answer,
            solution_steps=steps,
            topic="proporcijos",
            subtopic="santykis",
            grade_level=7,
            difficulty=difficulty,
            points=3,
        )

    @staticmethod
    def proportion_direct(difficulty: Difficulty) -> MathProblem:
        """Tiesioginė proporcija."""
        name = random_name()

        if difficulty == Difficulty.EASY:
            a1 = random.randint(2, 8)
            b1 = random.randint(10, 50)
            a2 = random.randint(3, 12)
        else:
            a1 = random.randint(5, 15)
            b1 = random.randint(20, 100)
            a2 = random.randint(8, 25)

        # b1/a1 = b2/a2 => b2 = b1 * a2 / a1
        # Užtikrinam, kad b2 būtų sveikas
        b1 = (b1 // a1) * a1  # Pakoreguojam b1
        b2 = b1 * a2 // a1

        contexts = [
            (f"Jei {a1} kg obuolių kainuoja {b1} €, kiek kainuos {a2} kg?", f"{b2} €"),
            (
                f"{name} per {a1} valandas nuvažiuoja {b1} km. Kiek nuvažiuos per {a2} valandas tuo pačiu greičiu?",
                f"{b2} km",
            ),
            (
                f"Iš {a1} m audinio pasiuvami {b1} marškiniai. Kiek marškinių pasiuvama iš {a2} m audinio?",
                f"{b2} vnt.",
            ),
        ]

        text, answer = random.choice(contexts)
        steps = [
            f"Tiesioginė proporcija: {a1} → {b1}",
            f"                       {a2} → x",
            f"x = {b1} × {a2} ÷ {a1}",
            f"x = {b1 * a2} ÷ {a1} = {b2}",
            f"Atsakymas: {answer}",
        ]

        return MathProblem(
            text=text,
            answer=answer,
            answer_numeric=b2,
            solution_steps=steps,
            topic="proporcijos",
            subtopic="tiesioginė proporcija",
            grade_level=7,
            difficulty=difficulty,
            points=3,
        )

    @staticmethod
    def proportion_inverse(difficulty: Difficulty) -> MathProblem:
        """Atvirkštinė proporcija."""
        if difficulty == Difficulty.EASY:
            workers1 = random.randint(2, 6)
            days1 = random.randint(4, 12)
            workers2 = random.randint(3, 8)
        else:
            workers1 = random.randint(4, 10)
            days1 = random.randint(6, 20)
            workers2 = random.randint(5, 15)

        # workers1 * days1 = workers2 * days2
        total_work = workers1 * days1
        # Užtikrinam, kad days2 būtų sveikas
        workers2 = total_work // (total_work // workers2)  # Pakoreguojam
        days2 = total_work // workers2

        text = f"{workers1} darbininkai darbą atlieka per {days1} dienų. Per kiek dienų tą patį darbą atliks {workers2} darbininkai?"
        steps = [
            f"Atvirkštinė proporcija: daugiau darbininkų - mažiau dienų",
            f"Bendras darbo kiekis: {workers1} × {days1} = {total_work}",
            f"Dienų skaičius: {total_work} ÷ {workers2} = {days2}",
            f"Atsakymas: {days2} dienų",
        ]

        return MathProblem(
            text=text,
            answer=f"{days2} dienų",
            answer_numeric=days2,
            solution_steps=steps,
            topic="proporcijos",
            subtopic="atvirkštinė proporcija",
            grade_level=7,
            difficulty=difficulty,
            points=3,
        )

    # -------------------------------------------------------------------------
    # FUNKCIJOS (8 klasė)
    # -------------------------------------------------------------------------

    @staticmethod
    def linear_function_value(difficulty: Difficulty) -> MathProblem:
        """Tiesinės funkcijos reikšmės skaičiavimas."""
        if difficulty == Difficulty.EASY:
            a = random.randint(1, 5)
            b = random.randint(-10, 10)
            x = random.randint(-5, 5)
        else:
            a = random.randint(-8, 8)
            while a == 0:
                a = random.randint(-8, 8)
            b = random.randint(-20, 20)
            x = random.randint(-10, 10)

        y = a * x + b

        # Formatuojam funkciją
        if b >= 0:
            func = f"f(x) = {a}x + {b}"
        else:
            func = f"f(x) = {a}x - {abs(b)}"

        text = f"Duota funkcija {func}. Apskaičiuok f({x})."
        steps = [
            f"f({x}) = {a} × ({x}) + ({b})",
            f"f({x}) = {a * x} + ({b})",
            f"f({x}) = {y}",
            f"Atsakymas: f({x}) = {y}",
        ]

        return MathProblem(
            text=text,
            answer=f"f({x}) = {y}",
            answer_numeric=y,
            solution_steps=steps,
            topic="funkcijos",
            subtopic="reikšmės skaičiavimas",
            grade_level=8,
            difficulty=difficulty,
            points=2,
        )

    @staticmethod
    def linear_function_zero(difficulty: Difficulty) -> MathProblem:
        """Tiesinės funkcijos nulio radimas."""
        # Pirma pasirenkam nulį, tada konstruojam funkciją
        if difficulty == Difficulty.EASY:
            x0 = random.randint(1, 8)
            a = random.randint(1, 5)
        else:
            x0 = random.randint(-10, 10)
            a = random.randint(2, 8)

        b = -a * x0  # f(x) = ax + b, kai f(x0) = 0 => b = -a*x0

        if b >= 0:
            func = f"f(x) = {a}x + {b}"
        else:
            func = f"f(x) = {a}x - {abs(b)}"

        text = f"Rask funkcijos {func} nulį (šaknį)."
        steps = [
            f"Funkcijos nulis: f(x) = 0",
            f"{a}x + ({b}) = 0",
            f"{a}x = {-b}",
            f"x = {-b} ÷ {a} = {x0}",
            f"Atsakymas: x = {x0}",
        ]

        return MathProblem(
            text=text,
            answer=f"x = {x0}",
            answer_numeric=x0,
            solution_steps=steps,
            topic="funkcijos",
            subtopic="funkcijos nulis",
            grade_level=8,
            difficulty=difficulty,
            points=2,
        )


# =============================================================================
# 9-10 KLASĖ: KVADRATINĖS LYGTYS, FUNKCIJOS, TRIGONOMETRIJA
# =============================================================================


class Grade9_10_Generators:
    """9-10 klasės uždavinių generatoriai."""

    # -------------------------------------------------------------------------
    # KVADRATINĖS LYGTYS
    # -------------------------------------------------------------------------

    @staticmethod
    def quadratic_equation_simple(difficulty: Difficulty) -> MathProblem:
        """Kvadratinė lygtis x² = a."""
        if difficulty == Difficulty.EASY:
            # Pilni kvadratai
            x = random.randint(2, 10)
        else:
            x = random.randint(5, 15)

        a = x * x

        text = f"Išspręsk lygtį: x² = {a}"
        steps = [
            f"x² = {a}",
            f"x = ±√{a}",
            f"x = ±{x}",
            f"Atsakymas: x₁ = {x}, x₂ = -{x}",
        ]

        return MathProblem(
            text=text,
            answer=f"x₁ = {x}, x₂ = -{x}",
            solution_steps=steps,
            topic="kvadratinės lygtys",
            subtopic="x² = a",
            grade_level=9,
            difficulty=difficulty,
            points=2,
        )

    @staticmethod
    def quadratic_equation_factored(difficulty: Difficulty) -> MathProblem:
        """Kvadratinė lygtis, kurią galima išskaidyti."""
        # Šaknys x1 ir x2
        if difficulty == Difficulty.EASY:
            x1 = random.randint(1, 6)
            x2 = random.randint(1, 6)
        elif difficulty == Difficulty.MEDIUM:
            x1 = random.randint(-8, 8)
            x2 = random.randint(-8, 8)
        else:
            x1 = random.randint(-12, 12)
            x2 = random.randint(-12, 12)

        # (x - x1)(x - x2) = x² - (x1+x2)x + x1*x2
        b = -(x1 + x2)
        c = x1 * x2

        # Formatuojam lygtį
        if b >= 0 and c >= 0:
            eq = f"x² + {b}x + {c} = 0"
        elif b >= 0 and c < 0:
            eq = f"x² + {b}x - {abs(c)} = 0"
        elif b < 0 and c >= 0:
            eq = f"x² - {abs(b)}x + {c} = 0"
        else:
            eq = f"x² - {abs(b)}x - {abs(c)} = 0"

        text = f"Išspręsk lygtį: {eq}"

        D = b * b - 4 * c
        steps = [
            f"a = 1, b = {b}, c = {c}",
            f"D = b² - 4ac = {b}² - 4×1×{c} = {b*b} - {4*c} = {D}",
            f"x = (-b ± √D) / 2a",
            f"x = ({-b} ± √{D}) / 2",
            f"x₁ = ({-b} + {int(D**0.5)}) / 2 = {x1 if x1 >= x2 else x2}",
            f"x₂ = ({-b} - {int(D**0.5)}) / 2 = {x2 if x1 >= x2 else x1}",
        ]

        x_min, x_max = min(x1, x2), max(x1, x2)
        if x1 == x2:
            answer = f"x = {x1}"
        else:
            answer = f"x₁ = {x_min}, x₂ = {x_max}"

        return MathProblem(
            text=text,
            answer=answer,
            solution_steps=steps,
            topic="kvadratinės lygtys",
            subtopic="diskriminantas",
            grade_level=9,
            difficulty=difficulty,
            points=3,
        )

    @staticmethod
    def quadratic_equation_incomplete(difficulty: Difficulty) -> MathProblem:
        """Nepilna kvadratinė lygtis (ax² + bx = 0 arba ax² + c = 0)."""
        eq_type = random.choice(["bx", "c"])

        if eq_type == "bx":
            # ax² + bx = 0 => x(ax + b) = 0
            if difficulty == Difficulty.EASY:
                a = random.randint(1, 3)
                x2 = random.randint(1, 6)
            else:
                a = random.randint(2, 5)
                x2 = random.randint(-8, 8)

            b = -a * x2  # kad x2 būtų šaknis

            if b >= 0:
                eq = f"{a}x² + {b}x = 0"
            else:
                eq = f"{a}x² - {abs(b)}x = 0"

            text = f"Išspręsk lygtį: {eq}"
            steps = [
                f"Iškeliam x: x({a}x + ({b})) = 0",
                f"x = 0 arba {a}x + ({b}) = 0",
                f"x = 0 arba x = {x2}",
                f"Atsakymas: x₁ = 0, x₂ = {x2}",
            ]
            answer = f"x₁ = 0, x₂ = {x2}"
        else:
            # ax² + c = 0 => x² = -c/a
            if difficulty == Difficulty.EASY:
                x = random.randint(2, 8)
                a = 1
            else:
                x = random.randint(3, 10)
                a = random.randint(1, 3)

            c = -a * x * x  # kad x² = x²

            eq = f"{a}x² - {abs(c)} = 0" if a > 1 else f"x² - {abs(c)} = 0"

            text = f"Išspręsk lygtį: {eq}"
            steps = [
                f"{a}x² = {abs(c)}",
                f"x² = {x*x}",
                f"x = ±{x}",
                f"Atsakymas: x₁ = {x}, x₂ = -{x}",
            ]
            answer = f"x₁ = {x}, x₂ = -{x}"

        return MathProblem(
            text=text,
            answer=answer,
            solution_steps=steps,
            topic="kvadratinės lygtys",
            subtopic="nepilna lygtis",
            grade_level=9,
            difficulty=difficulty,
            points=2,
        )

    # -------------------------------------------------------------------------
    # KVADRATINĖ FUNKCIJA
    # -------------------------------------------------------------------------

    @staticmethod
    def quadratic_function_vertex(difficulty: Difficulty) -> MathProblem:
        """Kvadratinės funkcijos viršūnės radimas."""
        if difficulty == Difficulty.EASY:
            a = random.choice([1, -1, 2, -2])
            # Viršūnė su sveikais skaičiais
            xv = random.randint(-5, 5)
            yv = random.randint(-10, 10)
        else:
            a = random.choice([1, -1, 2, -2, 3, -3])
            xv = random.randint(-8, 8)
            yv = random.randint(-15, 15)

        # f(x) = a(x - xv)² + yv = ax² - 2a*xv*x + a*xv² + yv
        b = -2 * a * xv
        c = a * xv * xv + yv

        # Formatuojam
        if b >= 0 and c >= 0:
            func = f"f(x) = {a}x² + {b}x + {c}"
        elif b >= 0 and c < 0:
            func = f"f(x) = {a}x² + {b}x - {abs(c)}"
        elif b < 0 and c >= 0:
            func = f"f(x) = {a}x² - {abs(b)}x + {c}"
        else:
            func = f"f(x) = {a}x² - {abs(b)}x - {abs(c)}"

        text = f"Rask funkcijos {func} viršūnės koordinates."
        steps = [
            f"Viršūnės x koordinatė: xᵥ = -b/(2a) = -{b}/(2×{a}) = {xv}",
            f"Viršūnės y koordinatė: yᵥ = f({xv})",
            f"yᵥ = {a}×{xv}² + ({b})×{xv} + ({c})",
            f"yᵥ = {a * xv * xv} + ({b * xv}) + ({c}) = {yv}",
            f"Atsakymas: V({xv}; {yv})",
        ]

        return MathProblem(
            text=text,
            answer=f"V({xv}; {yv})",
            solution_steps=steps,
            topic="funkcijos",
            subtopic="kvadratinės funkcijos viršūnė",
            grade_level=9,
            difficulty=difficulty,
            points=3,
        )

    # -------------------------------------------------------------------------
    # TRIGONOMETRIJA
    # -------------------------------------------------------------------------

    @staticmethod
    def trig_basic_values(difficulty: Difficulty) -> MathProblem:
        """Pagrindinės trigonometrinės reikšmės."""
        # Standartiniai kampai ir jų reikšmės
        values = {
            0: {"sin": "0", "cos": "1", "tan": "0"},
            30: {"sin": "1/2", "cos": "√3/2", "tan": "√3/3"},
            45: {"sin": "√2/2", "cos": "√2/2", "tan": "1"},
            60: {"sin": "√3/2", "cos": "1/2", "tan": "√3"},
            90: {"sin": "1", "cos": "0", "tan": "neapibrėžtas"},
        }

        if difficulty == Difficulty.EASY:
            angles = [0, 30, 45, 60, 90]
            funcs = ["sin", "cos"]
        else:
            angles = [0, 30, 45, 60, 90]
            funcs = ["sin", "cos", "tan"]

        angle = random.choice(angles)
        func = random.choice(funcs)

        if func == "tan" and angle == 90:
            angle = random.choice([0, 30, 45, 60])

        answer = values[angle][func]

        text = f"Apskaičiuok: {func} {angle}°"
        steps = [f"{func} {angle}° = {answer}", f"Atsakymas: {answer}"]

        return MathProblem(
            text=text,
            answer=answer,
            solution_steps=steps,
            topic="trigonometrija",
            subtopic="pagrindinės reikšmės",
            grade_level=9,
            difficulty=difficulty,
            points=1,
        )

    @staticmethod
    def trig_right_triangle(difficulty: Difficulty) -> MathProblem:
        """Stačiakampio trikampio uždavinys."""
        # Pitagoro trejetas
        triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)]

        if difficulty == Difficulty.EASY:
            a, b, c = random.choice(triples[:2])
            multiplier = random.randint(1, 3)
        else:
            a, b, c = random.choice(triples)
            multiplier = random.randint(1, 4)

        a, b, c = a * multiplier, b * multiplier, c * multiplier

        # Atsitiktinai pasirenkam, ką reikia rasti
        find = random.choice(["hypotenuse", "leg"])

        if find == "hypotenuse":
            text = (
                f"Stačiakampio trikampio statiniai yra {a} cm ir {b} cm. Rask įžambinę."
            )
            steps = [
                f"Pagal Pitagoro teoremą: c² = a² + b²",
                f"c² = {a}² + {b}² = {a*a} + {b*b} = {c*c}",
                f"c = √{c*c} = {c} cm",
                f"Atsakymas: {c} cm",
            ]
            answer = f"{c} cm"
        else:
            text = f"Stačiakampio trikampio įžambinė {c} cm, vienas statinis {a} cm. Rask kitą statinį."
            steps = [
                f"Pagal Pitagoro teoremą: a² + b² = c²",
                f"b² = c² - a² = {c}² - {a}² = {c*c} - {a*a} = {b*b}",
                f"b = √{b*b} = {b} cm",
                f"Atsakymas: {b} cm",
            ]
            answer = f"{b} cm"

        return MathProblem(
            text=text,
            answer=answer,
            solution_steps=steps,
            topic="trigonometrija",
            subtopic="Pitagoro teorema",
            grade_level=9,
            difficulty=difficulty,
            points=3,
        )


# =============================================================================
# 11-12 KLASĖ (VBE): LOGARITMAI, IŠVESTINĖS, PROGRESIJOS
# =============================================================================


class Grade11_12_Generators:
    """11-12 klasės (VBE lygio) uždavinių generatoriai."""

    # -------------------------------------------------------------------------
    # LOGARITMAI
    # -------------------------------------------------------------------------

    @staticmethod
    def logarithm_basic(difficulty: Difficulty) -> MathProblem:
        """Pagrindinis logaritmo skaičiavimas."""
        bases = [2, 3, 5, 10]
        base = random.choice(bases)

        if difficulty == Difficulty.EASY:
            exp = random.randint(1, 4)
        else:
            exp = random.randint(2, 6)

        arg = base**exp

        text = f"Apskaičiuok: log₍{base}₎{arg}"
        steps = [
            f"log₍{base}₎{arg} = x reiškia {base}ˣ = {arg}",
            f"{base}^{exp} = {arg}",
            f"Todėl log₍{base}₎{arg} = {exp}",
            f"Atsakymas: {exp}",
        ]

        return MathProblem(
            text=text,
            answer=str(exp),
            answer_numeric=exp,
            solution_steps=steps,
            topic="logaritmai",
            subtopic="skaičiavimas",
            grade_level=10,
            difficulty=difficulty,
            points=2,
        )

    @staticmethod
    def logarithm_equation(difficulty: Difficulty) -> MathProblem:
        """Logaritminė lygtis."""
        base = random.choice([2, 3, 5, 10])

        if difficulty == Difficulty.EASY:
            result = random.randint(1, 4)
            x = base**result
        else:
            result = random.randint(2, 5)
            x = base**result

        text = f"Išspręsk lygtį: log₍{base}₎x = {result}"
        steps = [
            f"log₍{base}₎x = {result}",
            f"x = {base}^{result}",
            f"x = {x}",
            f"Atsakymas: x = {x}",
        ]

        return MathProblem(
            text=text,
            answer=f"x = {x}",
            answer_numeric=x,
            solution_steps=steps,
            topic="logaritmai",
            subtopic="logaritminė lygtis",
            grade_level=10,
            difficulty=difficulty,
            points=2,
        )

    @staticmethod
    def exponential_equation(difficulty: Difficulty) -> MathProblem:
        """Rodiklinė lygtis."""
        base = random.choice([2, 3, 5])

        if difficulty == Difficulty.EASY:
            x = random.randint(1, 4)
        else:
            x = random.randint(2, 6)

        result = base**x

        text = f"Išspręsk lygtį: {base}ˣ = {result}"
        steps = [
            f"{base}ˣ = {result}",
            f"{base}ˣ = {base}^{x}",
            f"x = {x}",
            f"Atsakymas: x = {x}",
        ]

        return MathProblem(
            text=text,
            answer=f"x = {x}",
            answer_numeric=x,
            solution_steps=steps,
            topic="logaritmai",
            subtopic="rodiklinė lygtis",
            grade_level=10,
            difficulty=difficulty,
            points=2,
        )

    # -------------------------------------------------------------------------
    # IŠVESTINĖS
    # -------------------------------------------------------------------------

    @staticmethod
    def derivative_power(difficulty: Difficulty) -> MathProblem:
        """Laipsnio funkcijos išvestinė."""
        if difficulty == Difficulty.EASY:
            a = random.randint(1, 5)
            n = random.randint(2, 4)
        else:
            a = random.randint(2, 8)
            n = random.randint(3, 6)

        # f(x) = ax^n => f'(x) = a*n*x^(n-1)
        coef = a * n
        new_exp = n - 1

        text = f"Rask funkcijos f(x) = {a}x^{n} išvestinę."

        if new_exp == 1:
            answer = f"f'(x) = {coef}x"
        elif new_exp == 0:
            answer = f"f'(x) = {coef}"
        else:
            answer = f"f'(x) = {coef}x^{new_exp}"

        steps = [
            f"f(x) = {a}x^{n}",
            f"Taikome taisyklę: (xⁿ)' = n·xⁿ⁻¹",
            f"f'(x) = {a} × {n} × x^({n}-1)",
            f"f'(x) = {coef}x^{new_exp}",
            f"Atsakymas: {answer}",
        ]

        return MathProblem(
            text=text,
            answer=answer,
            solution_steps=steps,
            topic="išvestinės",
            subtopic="laipsnio išvestinė",
            grade_level=11,
            difficulty=difficulty,
            points=2,
        )

    @staticmethod
    def derivative_polynomial(difficulty: Difficulty) -> MathProblem:
        """Daugianario išvestinė."""
        if difficulty == Difficulty.EASY:
            a = random.randint(1, 4)
            b = random.randint(1, 6)
            c = random.randint(1, 10)
        else:
            a = random.randint(2, 6)
            b = random.randint(-8, 8)
            c = random.randint(-15, 15)

        # f(x) = ax² + bx + c => f'(x) = 2ax + b

        # Formatuojam funkciją
        if b >= 0 and c >= 0:
            func = f"f(x) = {a}x² + {b}x + {c}"
        elif b >= 0 and c < 0:
            func = f"f(x) = {a}x² + {b}x - {abs(c)}"
        elif b < 0 and c >= 0:
            func = f"f(x) = {a}x² - {abs(b)}x + {c}"
        else:
            func = f"f(x) = {a}x² - {abs(b)}x - {abs(c)}"

        # Išvestinė
        da = 2 * a
        if b >= 0:
            deriv = f"f'(x) = {da}x + {b}"
        else:
            deriv = f"f'(x) = {da}x - {abs(b)}"

        text = f"Rask funkcijos {func} išvestinę."
        steps = [
            f"{func}",
            f"({a}x²)' = {da}x",
            f"({b}x)' = {b}",
            f"({c})' = 0",
            f"Atsakymas: {deriv}",
        ]

        return MathProblem(
            text=text,
            answer=deriv,
            solution_steps=steps,
            topic="išvestinės",
            subtopic="daugianario išvestinė",
            grade_level=11,
            difficulty=difficulty,
            points=3,
        )

    @staticmethod
    def derivative_at_point(difficulty: Difficulty) -> MathProblem:
        """Išvestinės reikšmė taške."""
        if difficulty == Difficulty.EASY:
            a = random.randint(1, 3)
            b = random.randint(-5, 5)
            x0 = random.randint(-3, 3)
        else:
            a = random.randint(2, 5)
            b = random.randint(-10, 10)
            x0 = random.randint(-5, 5)

        # f(x) = ax² + bx => f'(x) = 2ax + b
        deriv_value = 2 * a * x0 + b

        if b >= 0:
            func = f"f(x) = {a}x² + {b}x"
        else:
            func = f"f(x) = {a}x² - {abs(b)}x"

        text = f"Rask funkcijos {func} išvestinės reikšmę taške x = {x0}."
        steps = [
            f"f'(x) = {2*a}x + ({b})",
            f"f'({x0}) = {2*a} × {x0} + ({b})",
            f"f'({x0}) = {2*a*x0} + ({b})",
            f"f'({x0}) = {deriv_value}",
            f"Atsakymas: f'({x0}) = {deriv_value}",
        ]

        return MathProblem(
            text=text,
            answer=f"f'({x0}) = {deriv_value}",
            answer_numeric=deriv_value,
            solution_steps=steps,
            topic="išvestinės",
            subtopic="išvestinė taške",
            grade_level=11,
            difficulty=difficulty,
            points=3,
        )

    # -------------------------------------------------------------------------
    # PROGRESIJOS
    # -------------------------------------------------------------------------

    @staticmethod
    def arithmetic_progression_nth(difficulty: Difficulty) -> MathProblem:
        """Aritmetinės progresijos n-tasis narys."""
        if difficulty == Difficulty.EASY:
            a1 = random.randint(1, 10)
            d = random.randint(1, 5)
            n = random.randint(5, 10)
        else:
            a1 = random.randint(-10, 20)
            d = random.randint(-5, 8)
            n = random.randint(10, 20)

        an = a1 + (n - 1) * d

        text = f"Aritmetinės progresijos a₁ = {a1}, d = {d}. Rask a₍{n}₎."
        steps = [
            f"aₙ = a₁ + (n-1)d",
            f"a₍{n}₎ = {a1} + ({n}-1) × {d}",
            f"a₍{n}₎ = {a1} + {n-1} × {d}",
            f"a₍{n}₎ = {a1} + {(n-1)*d}",
            f"a₍{n}₎ = {an}",
            f"Atsakymas: a₍{n}₎ = {an}",
        ]

        return MathProblem(
            text=text,
            answer=f"a₍{n}₎ = {an}",
            answer_numeric=an,
            solution_steps=steps,
            topic="progresijos",
            subtopic="aritmetinė progresija",
            grade_level=10,
            difficulty=difficulty,
            points=2,
        )

    @staticmethod
    def arithmetic_progression_sum(difficulty: Difficulty) -> MathProblem:
        """Aritmetinės progresijos suma."""
        if difficulty == Difficulty.EASY:
            a1 = random.randint(1, 8)
            d = random.randint(1, 4)
            n = random.randint(5, 10)
        else:
            a1 = random.randint(1, 15)
            d = random.randint(2, 6)
            n = random.randint(10, 20)

        an = a1 + (n - 1) * d
        Sn = n * (a1 + an) // 2

        text = f"Rask aritmetinės progresijos {a1}, {a1+d}, {a1+2*d}, ... pirmųjų {n} narių sumą."
        steps = [
            f"a₁ = {a1}, d = {d}",
            f"aₙ = a₁ + (n-1)d = {a1} + {n-1}×{d} = {an}",
            f"Sₙ = n(a₁ + aₙ)/2",
            f"S₍{n}₎ = {n} × ({a1} + {an}) / 2",
            f"S₍{n}₎ = {n} × {a1 + an} / 2 = {Sn}",
            f"Atsakymas: S₍{n}₎ = {Sn}",
        ]

        return MathProblem(
            text=text,
            answer=f"S₍{n}₎ = {Sn}",
            answer_numeric=Sn,
            solution_steps=steps,
            topic="progresijos",
            subtopic="aritmetinės progresijos suma",
            grade_level=10,
            difficulty=difficulty,
            points=3,
        )

    @staticmethod
    def geometric_progression_nth(difficulty: Difficulty) -> MathProblem:
        """Geometrinės progresijos n-tasis narys."""
        if difficulty == Difficulty.EASY:
            b1 = random.randint(1, 5)
            q = random.randint(2, 3)
            n = random.randint(3, 5)
        else:
            b1 = random.randint(1, 8)
            q = random.randint(2, 4)
            n = random.randint(4, 6)

        bn = b1 * (q ** (n - 1))

        text = f"Geometrinės progresijos b₁ = {b1}, q = {q}. Rask b₍{n}₎."
        steps = [
            f"bₙ = b₁ × qⁿ⁻¹",
            f"b₍{n}₎ = {b1} × {q}^({n}-1)",
            f"b₍{n}₎ = {b1} × {q}^{n-1}",
            f"b₍{n}₎ = {b1} × {q**(n-1)}",
            f"b₍{n}₎ = {bn}",
            f"Atsakymas: b₍{n}₎ = {bn}",
        ]

        return MathProblem(
            text=text,
            answer=f"b₍{n}₎ = {bn}",
            answer_numeric=bn,
            solution_steps=steps,
            topic="progresijos",
            subtopic="geometrinė progresija",
            grade_level=10,
            difficulty=difficulty,
            points=2,
        )


# =============================================================================
# PAPILDOMOS TEMOS: STEREOMETRIJA, TIKIMYBĖS, VEKTORIAI
# (Perkeltos prieš MathProblemGenerator, nes naudojamos GENERATORS žodyne)
# =============================================================================


class AdditionalGenerators:
    """Papildomų temų generatoriai."""

    # -------------------------------------------------------------------------
    # STEREOMETRIJA (Erdvinės figūros)
    # -------------------------------------------------------------------------

    @staticmethod
    def rectangular_prism_volume(difficulty: Difficulty) -> MathProblem:
        """Stačiakampio gretasienio tūris."""
        if difficulty == Difficulty.EASY:
            a = random.randint(2, 8)
            b = random.randint(2, 8)
            c = random.randint(2, 8)
        else:
            a = random.randint(5, 15)
            b = random.randint(5, 15)
            c = random.randint(3, 12)

        volume = a * b * c

        contexts = [
            f"Stačiakampio gretasienio matmenys: {a} cm × {b} cm × {c} cm. Apskaičiuok tūrį.",
            f"Akvariumo matmenys: {a} dm × {b} dm × {c} dm. Koks jo tūris?",
            f"Dėžės ilgis {a} cm, plotis {b} cm, aukštis {c} cm. Rask tūrį.",
        ]

        text = random.choice(contexts)
        unit = "dm³" if "dm" in text else "cm³"

        steps = [
            f"V = a × b × c",
            f"V = {a} × {b} × {c}",
            f"V = {a * b} × {c} = {volume} {unit}",
            f"Atsakymas: {volume} {unit}",
        ]

        return MathProblem(
            text=text,
            answer=f"{volume} {unit}",
            answer_numeric=volume,
            solution_steps=steps,
            topic="stereometrija",
            subtopic="gretasienio tūris",
            grade_level=8,
            difficulty=difficulty,
            points=2,
        )

    @staticmethod
    def rectangular_prism_surface(difficulty: Difficulty) -> MathProblem:
        """Stačiakampio gretasienio paviršiaus plotas."""
        if difficulty == Difficulty.EASY:
            a = random.randint(2, 6)
            b = random.randint(2, 6)
            c = random.randint(2, 6)
        else:
            a = random.randint(4, 12)
            b = random.randint(4, 12)
            c = random.randint(3, 10)

        surface = 2 * (a * b + b * c + a * c)

        text = f"Stačiakampio gretasienio matmenys: {a} cm × {b} cm × {c} cm. Apskaičiuok paviršiaus plotą."
        steps = [
            f"S = 2(ab + bc + ac)",
            f"S = 2({a}×{b} + {b}×{c} + {a}×{c})",
            f"S = 2({a*b} + {b*c} + {a*c})",
            f"S = 2 × {a*b + b*c + a*c} = {surface} cm²",
            f"Atsakymas: {surface} cm²",
        ]

        return MathProblem(
            text=text,
            answer=f"{surface} cm²",
            answer_numeric=surface,
            solution_steps=steps,
            topic="stereometrija",
            subtopic="gretasienio paviršius",
            grade_level=8,
            difficulty=difficulty,
            points=3,
        )

    @staticmethod
    def cube_volume_surface(difficulty: Difficulty) -> MathProblem:
        """Kubo tūris ir paviršiaus plotas."""
        if difficulty == Difficulty.EASY:
            a = random.randint(2, 8)
        else:
            a = random.randint(5, 15)

        volume = a**3
        surface = 6 * a * a

        text = f"Kubo briaunos ilgis {a} cm. Apskaičiuok tūrį ir paviršiaus plotą."
        steps = [
            f"Tūris: V = a³ = {a}³ = {volume} cm³",
            f"Paviršiaus plotas: S = 6a² = 6 × {a}² = 6 × {a*a} = {surface} cm²",
            f"Atsakymas: V = {volume} cm³, S = {surface} cm²",
        ]

        return MathProblem(
            text=text,
            answer=f"V = {volume} cm³, S = {surface} cm²",
            solution_steps=steps,
            topic="stereometrija",
            subtopic="kubas",
            grade_level=8,
            difficulty=difficulty,
            points=3,
        )

    @staticmethod
    def cylinder_volume(difficulty: Difficulty) -> MathProblem:
        """Cilindro tūris."""
        if difficulty == Difficulty.EASY:
            r = random.choice([2, 3, 5, 7])
            h = random.randint(3, 10)
        else:
            r = random.choice([3, 4, 5, 6, 7, 10])
            h = random.randint(5, 15)

        volume = round(3.14 * r * r * h, 2)

        text = f"Cilindro pagrindo spindulys {r} cm, aukštis {h} cm. Apskaičiuok tūrį (π ≈ 3,14)."
        steps = [
            f"V = πr²h",
            f"V = 3,14 × {r}² × {h}",
            f"V = 3,14 × {r*r} × {h}",
            f"V = {volume} cm³",
            f"Atsakymas: {volume} cm³",
        ]

        return MathProblem(
            text=text,
            answer=f"{volume} cm³",
            answer_numeric=volume,
            solution_steps=steps,
            topic="stereometrija",
            subtopic="cilindro tūris",
            grade_level=10,
            difficulty=difficulty,
            points=3,
        )

    @staticmethod
    def cone_volume(difficulty: Difficulty) -> MathProblem:
        """Kūgio tūris."""
        if difficulty == Difficulty.EASY:
            r = random.choice([3, 6, 9])
            h = random.choice([4, 5, 7, 10])
        else:
            r = random.choice([3, 4, 5, 6, 9, 12])
            h = random.choice([5, 8, 10, 12, 15])

        volume = round(3.14 * r * r * h / 3, 2)

        text = f"Kūgio pagrindo spindulys {r} cm, aukštis {h} cm. Apskaičiuok tūrį (π ≈ 3,14)."
        steps = [
            f"V = (1/3)πr²h",
            f"V = (1/3) × 3,14 × {r}² × {h}",
            f"V = (1/3) × 3,14 × {r*r} × {h}",
            f"V = (1/3) × {round(3.14 * r * r * h, 2)}",
            f"V = {volume} cm³",
            f"Atsakymas: {volume} cm³",
        ]

        return MathProblem(
            text=text,
            answer=f"{volume} cm³",
            answer_numeric=volume,
            solution_steps=steps,
            topic="stereometrija",
            subtopic="kūgio tūris",
            grade_level=10,
            difficulty=difficulty,
            points=3,
        )

    @staticmethod
    def sphere_volume(difficulty: Difficulty) -> MathProblem:
        """Rutulio tūris."""
        if difficulty == Difficulty.EASY:
            r = random.choice([3, 6])
        else:
            r = random.choice([3, 6, 9, 12])

        volume = round(4 / 3 * 3.14 * r * r * r, 2)

        text = f"Rutulio spindulys {r} cm. Apskaičiuok tūrį (π ≈ 3,14)."
        steps = [
            f"V = (4/3)πr³",
            f"V = (4/3) × 3,14 × {r}³",
            f"V = (4/3) × 3,14 × {r*r*r}",
            f"V = {volume} cm³",
            f"Atsakymas: {volume} cm³",
        ]

        return MathProblem(
            text=text,
            answer=f"{volume} cm³",
            answer_numeric=volume,
            solution_steps=steps,
            topic="stereometrija",
            subtopic="rutulio tūris",
            grade_level=10,
            difficulty=difficulty,
            points=3,
        )

    @staticmethod
    def pyramid_volume(difficulty: Difficulty) -> MathProblem:
        """Piramidės tūris."""
        if difficulty == Difficulty.EASY:
            a = random.choice([6, 9, 12])
            h = random.choice([4, 5, 8, 10])
        else:
            a = random.choice([6, 8, 10, 12, 15])
            h = random.choice([6, 9, 12, 15])

        base_area = a * a
        volume = base_area * h // 3

        text = f"Taisyklingos keturkampės piramidės pagrindo kraštinė {a} cm, aukštis {h} cm. Apskaičiuok tūrį."
        steps = [
            f"V = (1/3) × S_pagrindo × h",
            f"S_pagrindo = {a}² = {base_area} cm²",
            f"V = (1/3) × {base_area} × {h}",
            f"V = {base_area * h} / 3 = {volume} cm³",
            f"Atsakymas: {volume} cm³",
        ]

        return MathProblem(
            text=text,
            answer=f"{volume} cm³",
            answer_numeric=volume,
            solution_steps=steps,
            topic="stereometrija",
            subtopic="piramidės tūris",
            grade_level=10,
            difficulty=difficulty,
            points=3,
        )

    # -------------------------------------------------------------------------
    # TIKIMYBĖS IR KOMBINATORIKA
    # -------------------------------------------------------------------------

    @staticmethod
    def probability_simple(difficulty: Difficulty) -> MathProblem:
        """Paprasta tikimybė."""
        scenarios = [
            (
                "Dėžėje yra 3 raudoni ir 5 mėlyni kamuoliukai. Kokia tikimybė ištraukti raudoną?",
                3,
                8,
                "3/8",
            ),
            (
                "Dėžėje yra 4 obuoliai ir 6 kriaušės. Kokia tikimybė paimti obuolį?",
                4,
                10,
                "2/5",
            ),
            (
                "Maišelyje 2 balti ir 8 juodi kamuoliukai. Kokia tikimybė ištraukti baltą?",
                2,
                10,
                "1/5",
            ),
            ("Kortų kaladėje 52 kortos. Kokia tikimybė ištraukti tūzą?", 4, 52, "1/13"),
            (
                "Metamas taisyklingas kauliukas. Kokia tikimybė išmesti lyginį skaičių?",
                3,
                6,
                "1/2",
            ),
            (
                "Metamas kauliukas. Kokia tikimybė išmesti skaičių, didesnį už 4?",
                2,
                6,
                "1/3",
            ),
            (
                "Klasėje 12 berniukų ir 18 mergaičių. Atsitiktinai renkamas vienas mokinys. Kokia tikimybė, kad tai berniukas?",
                12,
                30,
                "2/5",
            ),
        ]

        text, favorable, total, answer = random.choice(scenarios)
        prob = Fraction(favorable, total)

        steps = [
            f"Palankių atvejų skaičius: {favorable}",
            f"Visų atvejų skaičius: {total}",
            f"P = {favorable}/{total} = {prob.numerator}/{prob.denominator}",
            f"Atsakymas: {answer}",
        ]

        return MathProblem(
            text=text,
            answer=answer,
            solution_steps=steps,
            topic="tikimybės",
            subtopic="paprasta tikimybė",
            grade_level=8,
            difficulty=difficulty,
            points=2,
        )

    @staticmethod
    def probability_complement(difficulty: Difficulty) -> MathProblem:
        """Priešingo įvykio tikimybė."""
        name = random_name()

        p_num = random.randint(1, 4)
        p_denom = random.choice([5, 6, 8, 10])

        q_num = p_denom - p_num

        p = Fraction(p_num, p_denom)
        q = Fraction(q_num, p_denom)

        text = f"Tikimybė, kad {name} laimės loterijoje, yra {p_num}/{p_denom}. Kokia tikimybė, kad nelaimės?"
        steps = [
            f"P(laimės) = {p_num}/{p_denom}",
            f"P(nelaimės) = 1 - P(laimės)",
            f"P(nelaimės) = 1 - {p_num}/{p_denom} = {p_denom}/{p_denom} - {p_num}/{p_denom}",
            f"P(nelaimės) = {q.numerator}/{q.denominator}",
            f"Atsakymas: {q.numerator}/{q.denominator}",
        ]

        return MathProblem(
            text=text,
            answer=f"{q.numerator}/{q.denominator}",
            solution_steps=steps,
            topic="tikimybės",
            subtopic="priešingas įvykis",
            grade_level=9,
            difficulty=difficulty,
            points=2,
        )

    @staticmethod
    def factorial_simple(difficulty: Difficulty) -> MathProblem:
        """Faktorialas."""
        if difficulty == Difficulty.EASY:
            n = random.randint(3, 5)
        else:
            n = random.randint(4, 7)

        result = 1
        for i in range(1, n + 1):
            result *= i

        text = f"Apskaičiuok: {n}!"

        factors = " × ".join(str(i) for i in range(n, 0, -1))
        steps = [f"{n}! = {factors}", f"{n}! = {result}", f"Atsakymas: {result}"]

        return MathProblem(
            text=text,
            answer=str(result),
            answer_numeric=result,
            solution_steps=steps,
            topic="kombinatorika",
            subtopic="faktorialas",
            grade_level=10,
            difficulty=difficulty,
            points=2,
        )

    @staticmethod
    def permutations_simple(difficulty: Difficulty) -> MathProblem:
        """Kėliniai."""
        if difficulty == Difficulty.EASY:
            n = random.randint(3, 5)
        else:
            n = random.randint(4, 6)

        result = 1
        for i in range(1, n + 1):
            result *= i

        contexts = [
            f"Kiek būdų galima surikiuoti {n} skirtingas knygas lentynoje?",
            f"Kiek skirtingų eilių galima sudaryti iš {n} žmonių?",
            f"Kiek būdų {n} bėgikai gali finišuoti (skirtingomis vietomis)?",
        ]

        text = random.choice(contexts)
        steps = [
            f"Kėlinių skaičius: P_{n} = {n}!",
            f"P_{n} = {' × '.join(str(i) for i in range(n, 0, -1))}",
            f"P_{n} = {result}",
            f"Atsakymas: {result} būdų",
        ]

        return MathProblem(
            text=text,
            answer=f"{result} būdų",
            answer_numeric=result,
            solution_steps=steps,
            topic="kombinatorika",
            subtopic="kėliniai",
            grade_level=10,
            difficulty=difficulty,
            points=3,
        )

    @staticmethod
    def combinations_simple(difficulty: Difficulty) -> MathProblem:
        """Deriniai."""
        if difficulty == Difficulty.EASY:
            n = random.randint(4, 6)
            k = random.randint(2, 3)
        else:
            n = random.randint(5, 8)
            k = random.randint(2, 4)

        def factorial(x):
            r = 1
            for i in range(1, x + 1):
                r *= i
            return r

        result = factorial(n) // (factorial(k) * factorial(n - k))

        contexts = [
            f"Kiek būdų iš {n} mokinių galima išrinkti {k} atstovus?",
            f"Kiek skirtingų {k} kortų kombinacijų galima sudaryti iš {n} kortų?",
            f"Komandoje {n} žaidėjai. Kiek būdų išrinkti {k} žaidėjus startui?",
        ]

        text = random.choice(contexts)
        steps = [
            f"Derinių skaičius: C({n},{k}) = {n}! / ({k}! × {n-k}!)",
            f"C({n},{k}) = {factorial(n)} / ({factorial(k)} × {factorial(n-k)})",
            f"C({n},{k}) = {factorial(n)} / {factorial(k) * factorial(n-k)}",
            f"C({n},{k}) = {result}",
            f"Atsakymas: {result} būdų",
        ]

        return MathProblem(
            text=text,
            answer=f"{result} būdų",
            answer_numeric=result,
            solution_steps=steps,
            topic="kombinatorika",
            subtopic="deriniai",
            grade_level=10,
            difficulty=difficulty,
            points=3,
        )

    # -------------------------------------------------------------------------
    # VEKTORIAI
    # -------------------------------------------------------------------------

    @staticmethod
    def vector_addition(difficulty: Difficulty) -> MathProblem:
        """Vektorių sudėtis."""
        if difficulty == Difficulty.EASY:
            a1, a2 = random.randint(-5, 5), random.randint(-5, 5)
            b1, b2 = random.randint(-5, 5), random.randint(-5, 5)
        else:
            a1, a2 = random.randint(-10, 10), random.randint(-10, 10)
            b1, b2 = random.randint(-10, 10), random.randint(-10, 10)

        c1, c2 = a1 + b1, a2 + b2

        text = f"Duoti vektoriai ā({a1}; {a2}) ir b̄({b1}; {b2}). Rask ā + b̄."
        steps = [
            f"ā + b̄ = ({a1}; {a2}) + ({b1}; {b2})",
            f"ā + b̄ = ({a1} + {b1}; {a2} + {b2})",
            f"ā + b̄ = ({c1}; {c2})",
            f"Atsakymas: ({c1}; {c2})",
        ]

        return MathProblem(
            text=text,
            answer=f"({c1}; {c2})",
            solution_steps=steps,
            topic="vektoriai",
            subtopic="sudėtis",
            grade_level=10,
            difficulty=difficulty,
            points=2,
        )

    @staticmethod
    def vector_subtraction(difficulty: Difficulty) -> MathProblem:
        """Vektorių atimtis."""
        if difficulty == Difficulty.EASY:
            a1, a2 = random.randint(-5, 5), random.randint(-5, 5)
            b1, b2 = random.randint(-5, 5), random.randint(-5, 5)
        else:
            a1, a2 = random.randint(-10, 10), random.randint(-10, 10)
            b1, b2 = random.randint(-10, 10), random.randint(-10, 10)

        c1, c2 = a1 - b1, a2 - b2

        text = f"Duoti vektoriai ā({a1}; {a2}) ir b̄({b1}; {b2}). Rask ā - b̄."
        steps = [
            f"ā - b̄ = ({a1}; {a2}) - ({b1}; {b2})",
            f"ā - b̄ = ({a1} - {b1}; {a2} - {b2})",
            f"ā - b̄ = ({c1}; {c2})",
            f"Atsakymas: ({c1}; {c2})",
        ]

        return MathProblem(
            text=text,
            answer=f"({c1}; {c2})",
            solution_steps=steps,
            topic="vektoriai",
            subtopic="atimtis",
            grade_level=10,
            difficulty=difficulty,
            points=2,
        )

    @staticmethod
    def vector_scalar_multiplication(difficulty: Difficulty) -> MathProblem:
        """Vektoriaus daugyba iš skaičiaus."""
        if difficulty == Difficulty.EASY:
            a1, a2 = random.randint(-5, 5), random.randint(-5, 5)
            k = random.randint(-3, 5)
        else:
            a1, a2 = random.randint(-8, 8), random.randint(-8, 8)
            k = random.randint(-5, 7)

        while k == 0:
            k = random.randint(-5, 5)

        c1, c2 = k * a1, k * a2

        text = f"Duotas vektorius ā({a1}; {a2}). Rask {k}ā."
        steps = [
            f"{k}ā = {k} × ({a1}; {a2})",
            f"{k}ā = ({k} × {a1}; {k} × {a2})",
            f"{k}ā = ({c1}; {c2})",
            f"Atsakymas: ({c1}; {c2})",
        ]

        return MathProblem(
            text=text,
            answer=f"({c1}; {c2})",
            solution_steps=steps,
            topic="vektoriai",
            subtopic="daugyba iš skaičiaus",
            grade_level=10,
            difficulty=difficulty,
            points=2,
        )

    @staticmethod
    def vector_dot_product(difficulty: Difficulty) -> MathProblem:
        """Skaliarinė sandauga."""
        if difficulty == Difficulty.EASY:
            a1, a2 = random.randint(-4, 4), random.randint(-4, 4)
            b1, b2 = random.randint(-4, 4), random.randint(-4, 4)
        else:
            a1, a2 = random.randint(-8, 8), random.randint(-8, 8)
            b1, b2 = random.randint(-8, 8), random.randint(-8, 8)

        dot = a1 * b1 + a2 * b2

        text = f"Duoti vektoriai ā({a1}; {a2}) ir b̄({b1}; {b2}). Rask skaliarinę sandaugą ā · b̄."
        steps = [
            f"ā · b̄ = a₁b₁ + a₂b₂",
            f"ā · b̄ = {a1} × {b1} + {a2} × {b2}",
            f"ā · b̄ = {a1 * b1} + {a2 * b2}",
            f"ā · b̄ = {dot}",
            f"Atsakymas: {dot}",
        ]

        return MathProblem(
            text=text,
            answer=str(dot),
            answer_numeric=dot,
            solution_steps=steps,
            topic="vektoriai",
            subtopic="skaliarinė sandauga",
            grade_level=10,
            difficulty=difficulty,
            points=3,
        )

    @staticmethod
    def vector_length(difficulty: Difficulty) -> MathProblem:
        """Vektoriaus ilgis."""
        pairs = [(3, 4), (5, 12), (8, 6), (0, 5), (4, 0), (6, 8), (5, 0), (0, 7)]
        a1, a2 = random.choice(pairs)

        if random.choice([True, False]):
            a1 = -a1
        if random.choice([True, False]):
            a2 = -a2

        length = int((a1**2 + a2**2) ** 0.5)

        text = f"Rask vektoriaus ā({a1}; {a2}) ilgį."
        steps = [
            f"|ā| = √(a₁² + a₂²)",
            f"|ā| = √({a1}² + {a2}²)",
            f"|ā| = √({a1*a1} + {a2*a2})",
            f"|ā| = √{a1*a1 + a2*a2} = {length}",
            f"Atsakymas: |ā| = {length}",
        ]

        return MathProblem(
            text=text,
            answer=f"|ā| = {length}",
            answer_numeric=length,
            solution_steps=steps,
            topic="vektoriai",
            subtopic="vektoriaus ilgis",
            grade_level=10,
            difficulty=difficulty,
            points=2,
        )

    @staticmethod
    def vector_perpendicular_check(difficulty: Difficulty) -> MathProblem:
        """Patikrinti ar vektoriai statmeni."""
        is_perpendicular = random.choice([True, False])

        if is_perpendicular:
            a1 = random.randint(1, 6)
            a2 = random.randint(1, 6)
            b1, b2 = -a2, a1
            if random.choice([True, False]):
                b1, b2 = a2, -a1
        else:
            a1, a2 = random.randint(-5, 5), random.randint(-5, 5)
            b1, b2 = random.randint(-5, 5), random.randint(-5, 5)
            while a1 * b1 + a2 * b2 == 0:
                b1 = random.randint(-5, 5)

        dot = a1 * b1 + a2 * b2
        answer = "Taip, statmeni" if dot == 0 else "Ne, nestatmeni"

        text = f"Ar vektoriai ā({a1}; {a2}) ir b̄({b1}; {b2}) yra statmeni?"
        steps = [
            f"Vektoriai statmeni, jei ā · b̄ = 0",
            f"ā · b̄ = {a1} × {b1} + {a2} × {b2}",
            f"ā · b̄ = {a1 * b1} + {a2 * b2} = {dot}",
            f"Kadangi {dot} {'= 0' if dot == 0 else '≠ 0'}, vektoriai {'yra' if dot == 0 else 'nėra'} statmeni",
            f"Atsakymas: {answer}",
        ]

        return MathProblem(
            text=text,
            answer=answer,
            solution_steps=steps,
            topic="vektoriai",
            subtopic="statmenumas",
            grade_level=10,
            difficulty=difficulty,
            points=3,
        )


# =============================================================================
# PAGRINDINIS GENERATORIUS
# =============================================================================


class MathProblemGenerator:
    """
    Pagrindinis matematinių uždavinių generatorius.
    Naudoja šablonus ir algoritmus, ne AI.
    """

    # Visų generatorių registras pagal temas ir klases
    GENERATORS = {
        # 5-6 klasė
        "aritmetika": {
            "grades": [5, 6],
            "generators": [
                Grade5_6_Generators.addition_context,
                Grade5_6_Generators.subtraction_context,
                Grade5_6_Generators.multiplication_context,
                Grade5_6_Generators.division_context,
                Grade5_6_Generators.division_with_remainder,
            ],
        },
        "trupmenos": {
            "grades": [5, 6, 7],
            "generators": [
                Grade5_6_Generators.fraction_part_of_whole,
                Grade5_6_Generators.fraction_find_whole,
                Grade5_6_Generators.fraction_addition,
            ],
        },
        "procentai": {
            "grades": [6, 7, 8],
            "generators": [
                Grade5_6_Generators.percent_find_part,
                Grade5_6_Generators.percent_find_whole,
                Grade5_6_Generators.percent_discount,
                Grade5_6_Generators.percent_increase,
            ],
        },
        "geometrija_pagrindai": {
            "grades": [5, 6, 7],
            "generators": [
                Grade5_6_Generators.rectangle_perimeter,
                Grade5_6_Generators.rectangle_area,
                Grade5_6_Generators.square_perimeter_area,
                Grade5_6_Generators.triangle_area,
                Grade5_6_Generators.circle_circumference,
            ],
        },
        # 5 klasė - paprastos lygtys (TIK natūralieji skaičiai!)
        "lygtys_paprastos": {
            "grades": [5, 6],
            "generators": [
                Grade5_6_Generators.simple_equation_addition_5,
                Grade5_6_Generators.simple_equation_subtraction_5,
                Grade5_6_Generators.simple_equation_multiplication_5,
                Grade5_6_Generators.simple_equation_unknown_minuend_5,
                Grade5_6_Generators.equation_word_problem_5,
            ],
        },
        # 7-8 klasė - tiesinės lygtys (su neigiamais)
        "lygtys": {
            "grades": [7, 8],
            "generators": [
                Grade7_8_Generators.linear_equation_simple,
                Grade7_8_Generators.linear_equation_both_sides,
                Grade7_8_Generators.equation_word_problem_age,
                Grade7_8_Generators.equation_word_problem_purchase,
                Grade7_8_Generators.equation_word_problem_geometry,
            ],
        },
        "proporcijos": {
            "grades": [7, 8],
            "generators": [
                Grade7_8_Generators.ratio_simple,
                Grade7_8_Generators.proportion_direct,
                Grade7_8_Generators.proportion_inverse,
            ],
        },
        "funkcijos_pagrindai": {
            "grades": [8, 9],
            "generators": [
                Grade7_8_Generators.linear_function_value,
                Grade7_8_Generators.linear_function_zero,
            ],
        },
        # 9-10 klasė
        "kvadratines_lygtys": {
            "grades": [9, 10],
            "generators": [
                Grade9_10_Generators.quadratic_equation_simple,
                Grade9_10_Generators.quadratic_equation_factored,
                Grade9_10_Generators.quadratic_equation_incomplete,
            ],
        },
        "kvadratine_funkcija": {
            "grades": [9, 10],
            "generators": [
                Grade9_10_Generators.quadratic_function_vertex,
            ],
        },
        "trigonometrija": {
            "grades": [9, 10, 11, 12],
            "generators": [
                Grade9_10_Generators.trig_basic_values,
                Grade9_10_Generators.trig_right_triangle,
            ],
        },
        # 11-12 klasė (VBE)
        "logaritmai": {
            "grades": [10, 11, 12],
            "generators": [
                Grade11_12_Generators.logarithm_basic,
                Grade11_12_Generators.logarithm_equation,
                Grade11_12_Generators.exponential_equation,
            ],
        },
        "isvestines": {
            "grades": [11, 12],
            "generators": [
                Grade11_12_Generators.derivative_power,
                Grade11_12_Generators.derivative_polynomial,
                Grade11_12_Generators.derivative_at_point,
            ],
        },
        "progresijos": {
            "grades": [10, 11, 12],
            "generators": [
                Grade11_12_Generators.arithmetic_progression_nth,
                Grade11_12_Generators.arithmetic_progression_sum,
                Grade11_12_Generators.geometric_progression_nth,
            ],
        },
        # Papildomos temos
        "stereometrija": {
            "grades": [8, 9, 10, 11, 12],
            "generators": [
                AdditionalGenerators.rectangular_prism_volume,
                AdditionalGenerators.rectangular_prism_surface,
                AdditionalGenerators.cube_volume_surface,
                AdditionalGenerators.cylinder_volume,
                AdditionalGenerators.cone_volume,
                AdditionalGenerators.sphere_volume,
                AdditionalGenerators.pyramid_volume,
            ],
        },
        "tikimybes": {
            "grades": [8, 9, 10, 11, 12],
            "generators": [
                AdditionalGenerators.probability_simple,
                AdditionalGenerators.probability_complement,
            ],
        },
        "kombinatorika": {
            "grades": [10, 11, 12],
            "generators": [
                AdditionalGenerators.factorial_simple,
                AdditionalGenerators.permutations_simple,
                AdditionalGenerators.combinations_simple,
            ],
        },
        "vektoriai": {
            "grades": [10, 11, 12],
            "generators": [
                AdditionalGenerators.vector_addition,
                AdditionalGenerators.vector_subtraction,
                AdditionalGenerators.vector_scalar_multiplication,
                AdditionalGenerators.vector_dot_product,
                AdditionalGenerators.vector_length,
                AdditionalGenerators.vector_perpendicular_check,
            ],
        },
    }

    # Temų pavadinimai lietuviškai
    TOPIC_NAMES_LT = {
        "aritmetika": "Aritmetika",
        "trupmenos": "Trupmenos",
        "procentai": "Procentai",
        "geometrija_pagrindai": "Geometrijos pagrindai",
        "lygtys_paprastos": "Paprastos lygtys (5 kl.)",
        "lygtys": "Tiesinės lygtys",
        "proporcijos": "Proporcijos ir santykiai",
        "funkcijos_pagrindai": "Funkcijų pagrindai",
        "kvadratines_lygtys": "Kvadratinės lygtys",
        "kvadratine_funkcija": "Kvadratinė funkcija",
        "trigonometrija": "Trigonometrija",
        "logaritmai": "Logaritmai",
        "isvestines": "Išvestinės",
        "progresijos": "Progresijos",
        "stereometrija": "Stereometrija (erdvinės figūros)",
        "tikimybes": "Tikimybės",
        "kombinatorika": "Kombinatorika",
        "vektoriai": "Vektoriai",
    }

    @classmethod
    def get_topics_for_grade(cls, grade: int) -> List[str]:
        """Grąžina temas, tinkamas nurodytai klasei."""
        topics = []
        for topic_id, topic_data in cls.GENERATORS.items():
            if grade in topic_data["grades"]:
                topics.append(topic_id)
        return topics

    @classmethod
    def generate_problem(
        cls,
        topic: str,
        difficulty: Difficulty = Difficulty.MEDIUM,
        grade: Optional[int] = None,
    ) -> MathProblem:
        """
        Generuoja vieną uždavinį pagal temą ir sudėtingumą.

        Args:
            topic: Temos ID (pvz., "lygtys", "trupmenos")
            difficulty: Sudėtingumo lygis
            grade: Klasė (naudojama filtravimui)

        Returns:
            MathProblem objektas
        """
        if topic not in cls.GENERATORS:
            # Bandome rasti panašią temą
            topic_lower = topic.lower()
            for t in cls.GENERATORS.keys():
                if t in topic_lower or topic_lower in t:
                    topic = t
                    break
            else:
                # Default - aritmetika
                topic = "aritmetika"

        generators = cls.GENERATORS[topic]["generators"]
        generator = random.choice(generators)

        problem = generator(difficulty)

        # Nustatom klasę jei nenurodyta
        if grade:
            problem.grade_level = grade

        return problem

    @classmethod
    def generate_test(
        cls,
        topics: List[str],
        grade: int,
        task_count: int = 5,
        difficulty: str = "medium",
        include_solutions: bool = True,
    ) -> List[MathProblem]:
        """
        Generuoja kontrolinio uždavinius.

        Args:
            topics: Temų sąrašas
            grade: Klasė
            task_count: Uždavinių kiekis
            difficulty: Sudėtingumas ("easy", "medium", "hard", "mixed")
            include_solutions: Ar įtraukti sprendimus

        Returns:
            Uždavinių sąrašas
        """
        problems = []

        # Konvertuojam difficulty
        if difficulty == "easy":
            diff = Difficulty.EASY
        elif difficulty == "hard":
            diff = Difficulty.HARD
        elif difficulty == "mixed":
            diff = None  # Bus pasirinktas atsitiktinai
        else:
            diff = Difficulty.MEDIUM

        # Filtruojam temas pagal klasę
        valid_topics = []
        for t in topics:
            t_lower = (
                t.lower()
                .replace(" ", "_")
                .replace("ė", "e")
                .replace("ų", "u")
                .replace("į", "i")
            )
            for topic_id, topic_data in cls.GENERATORS.items():
                if (topic_id in t_lower or t_lower in topic_id) and grade in topic_data[
                    "grades"
                ]:
                    valid_topics.append(topic_id)
                    break

        if not valid_topics:
            # Jei nėra tinkamų temų, naudojam visas klasei tinkamas
            valid_topics = cls.get_topics_for_grade(grade)

        # Generuojam uždavinius
        for i in range(task_count):
            topic = random.choice(valid_topics) if valid_topics else "aritmetika"

            # Jei mixed - atsitiktinis sudėtingumas
            if diff is None:
                if i < task_count // 3:
                    current_diff = Difficulty.EASY
                elif i < 2 * task_count // 3:
                    current_diff = Difficulty.MEDIUM
                else:
                    current_diff = Difficulty.HARD
            else:
                current_diff = diff

            problem = cls.generate_problem(topic, current_diff, grade)
            problem.number = i + 1

            if not include_solutions:
                problem.solution_steps = []

            problems.append(problem)

        return problems

    @classmethod
    def get_all_topics(cls) -> dict:
        """Grąžina visas temas su pavadinimais."""
        return {
            topic_id: {
                "name": cls.TOPIC_NAMES_LT.get(topic_id, topic_id),
                "grades": data["grades"],
                "generator_count": len(data["generators"]),
            }
            for topic_id, data in cls.GENERATORS.items()
        }


# Singleton
_generator: Optional[MathProblemGenerator] = None


def get_math_problem_generator() -> MathProblemGenerator:
    """Gauna matematinių uždavinių generatorių."""
    global _generator
    if _generator is None:
        _generator = MathProblemGenerator()
    return _generator
