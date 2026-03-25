"""
Globalių matematikos temų registras (spiralinis modelis).

Kiekviena potemė gali būti naudojama keliose klasėse (spiral learning).
Uždaviniai žymimi global_area + global_subtopic, o ne konkrečia klase.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class GlobalSubtopic:
    """Globali potemė — mažiausias vienetas temų hierarchijoje."""

    id: str
    title_lt: str
    title_en: str
    grades: List[int]  # Kuriose klasėse pasirodo
    keywords: List[str] = field(default_factory=list)  # Raktiniai žodžiai paieškos


@dataclass
class GlobalArea:
    """Globali sritis — aukščiausias lygis temų hierarchijoje."""

    id: str
    title_lt: str
    title_en: str
    subtopics: Dict[str, GlobalSubtopic]


# === GLOBALIOS SRITYS IR POTEMĖS ===
# Pagal BP 2022 ir mokytojos ilgalaikius planus (PDF)

GLOBAL_AREAS: Dict[str, GlobalArea] = {
    # ─── 1. SKAIČIAI IR SKAIČIAVIMAI ───
    "skaiciai": GlobalArea(
        id="skaiciai",
        title_lt="Skaičiai ir skaičiavimai",
        title_en="Numbers and Calculations",
        subtopics={
            "naturalieji": GlobalSubtopic(
                id="naturalieji",
                title_lt="Natūralieji skaičiai",
                title_en="Natural numbers",
                grades=[5, 6],
                keywords=["natūralieji", "rašymas", "skaitymas", "romėniški"],
            ),
            "sveikieji": GlobalSubtopic(
                id="sveikieji",
                title_lt="Sveikieji skaičiai",
                title_en="Integers",
                grades=[6, 7, 8],
                keywords=["sveikieji", "teigiamieji", "neigiamieji", "priešingas", "aibė", "poaibis"],
            ),
            "trupmenos": GlobalSubtopic(
                id="trupmenos",
                title_lt="Trupmenos ir dešimtainiai skaičiai",
                title_en="Fractions and decimals",
                grades=[5, 6, 7],
                keywords=["trupmenos", "dešimtainiai", "mišrieji", "racionalieji"],
            ),
            "dalumas": GlobalSubtopic(
                id="dalumas",
                title_lt="Dalumas, dalikliai ir kartotiniai",
                title_en="Divisibility, factors and multiples",
                grades=[5, 6],
                keywords=["dalumas", "dalikliai", "kartotiniai", "pirminiai", "MBK", "DBD"],
            ),
            "laipsniai": GlobalSubtopic(
                id="laipsniai",
                title_lt="Laipsniai",
                title_en="Powers",
                grades=[7, 8, 9],
                keywords=["laipsnis", "pagrindas", "rodiklis", "kėlimas"],
            ),
            "saknys": GlobalSubtopic(
                id="saknys",
                title_lt="Šaknys",
                title_en="Roots",
                grades=[8, 9],
                keywords=["šaknis", "kvadratinė", "kubinė", "iracionalieji", "pošaknio"],
            ),
            "realieji_skaiciai": GlobalSubtopic(
                id="realieji_skaiciai",
                title_lt="Realieji skaičiai ir skaičių aibės",
                title_en="Real numbers and number sets",
                grades=[8, 9, 10],
                keywords=["realieji", "iracionalieji", "skaičių aibė", "aibė N", "aibė Z", "aibė Q", "aibė R"],
            ),
            "standartine_israiska": GlobalSubtopic(
                id="standartine_israiska",
                title_lt="Standartinė skaičiaus išraiška",
                title_en="Standard form / Scientific notation",
                grades=[7, 8],
                keywords=["standartinė", "eilė", "10 laipsnis"],
            ),
            "procentai": GlobalSubtopic(
                id="procentai",
                title_lt="Procentai",
                title_en="Percentages",
                grades=[5, 6, 7, 8, 9, 10],
                keywords=["procentai", "procentinis", "nuolaida", "sudėtinės palūkanos"],
            ),
            "veiksmu_tvarka": GlobalSubtopic(
                id="veiksmu_tvarka",
                title_lt="Veiksmų tvarka ir savybės",
                title_en="Order of operations and properties",
                grades=[5, 6, 7],
                keywords=["veiksmų tvarka", "skliaustai", "reiškinys", "dėsniai"],
            ),
        },
    ),
    # ─── 2. ALGEBRA ───
    "algebra": GlobalArea(
        id="algebra",
        title_lt="Algebra",
        title_en="Algebra",
        subtopics={
            "reiskiniai": GlobalSubtopic(
                id="reiskiniai",
                title_lt="Raidiniai ir skaitiniai reiškiniai",
                title_en="Algebraic and numerical expressions",
                grades=[5, 6, 7, 8, 9],
                keywords=["reiškiniai", "raidiniai", "prastinimas", "skliaustai"],
            ),
            "tiesines_lygtys": GlobalSubtopic(
                id="tiesines_lygtys",
                title_lt="Tiesinės lygtys",
                title_en="Linear equations",
                grades=[6, 7, 8, 9],
                keywords=["lygtis", "nežinomasis", "sprendinys", "tiesinė"],
            ),
            "kvadratines_lygtys": GlobalSubtopic(
                id="kvadratines_lygtys",
                title_lt="Kvadratinės lygtys",
                title_en="Quadratic equations",
                grades=[9, 10],
                keywords=["kvadratinė", "diskriminantas"],
            ),
            "nelygybes": GlobalSubtopic(
                id="nelygybes",
                title_lt="Nelygybės",
                title_en="Inequalities",
                grades=[7, 8, 9, 10, 11],
                keywords=["nelygybė", "intervalas", "sprendiniai", "sistema"],
            ),
            "lygtys_sistemos": GlobalSubtopic(
                id="lygtys_sistemos",
                title_lt="Lygčių sistemos",
                title_en="Systems of equations",
                grades=[8, 9, 10],
                keywords=["sistema", "dviejų lygčių", "keitimo", "sudėties"],
            ),
            "proporcijos": GlobalSubtopic(
                id="proporcijos",
                title_lt="Santykiai ir proporcijos",
                title_en="Ratios and proportions",
                grades=[6, 7],
                keywords=["santykis", "proporcija", "proporcingumo koeficientas"],
            ),
            "daugianariai": GlobalSubtopic(
                id="daugianariai",
                title_lt="Daugianariai ir dauginamieji",
                title_en="Polynomials and factoring",
                grades=[8, 9, 10],
                keywords=["daugianaris", "vienanariai", "skaidymas", "dauginamieji"],
            ),
            "sekos": GlobalSubtopic(
                id="sekos",
                title_lt="Dėsningumai ir sekos",
                title_en="Patterns and sequences",
                grades=[5, 6, 8, 9],
                keywords=["seka", "dėsningumas", "n-tasis"],
            ),
        },
    ),
    # ─── 3. GEOMETRIJA ───
    "geometrija": GlobalArea(
        id="geometrija",
        title_lt="Geometrija ir matavimai",
        title_en="Geometry and Measurement",
        subtopics={
            "kampai": GlobalSubtopic(
                id="kampai",
                title_lt="Kampai",
                title_en="Angles",
                grades=[5, 6, 7],
                keywords=["kampas", "smailusis", "statusis", "bukasis", "matlankis"],
            ),
            "trikampiai": GlobalSubtopic(
                id="trikampiai",
                title_lt="Trikampiai",
                title_en="Triangles",
                grades=[6, 7, 8, 9, 10],
                keywords=[
                    "trikampis", "lygumo požymiai", "pusiaukampinė",
                    "pusiaukraštinė", "aukštinė", "kampų suma", "panašumas"
                ],
            ),
            "keturkampiai": GlobalSubtopic(
                id="keturkampiai",
                title_lt="Keturkampiai",
                title_en="Quadrilaterals",
                grades=[7, 8, 9, 10],
                keywords=[
                    "lygiagretainis", "stačiakampis", "rombas",
                    "kvadratas", "trapecija",
                ],
            ),
            "apskritimai": GlobalSubtopic(
                id="apskritimai",
                title_lt="Apskritimai ir skrituliai",
                title_en="Circles",
                grades=[7, 8, 9, 10],
                keywords=["apskritimas", "skritulys", "spindulys", "skersmuo", "π"],
            ),
            "perimetras_plotas": GlobalSubtopic(
                id="perimetras_plotas",
                title_lt="Perimetras ir plotas",
                title_en="Perimeter and area",
                grades=[5, 6, 7, 8, 9, 10],
                keywords=["perimetras", "plotas", "formulė"],
            ),
            "turis": GlobalSubtopic(
                id="turis",
                title_lt="Tūris ir paviršiaus plotas",
                title_en="Volume and surface area",
                grades=[5, 7, 8, 12],
                keywords=["tūris", "gretasienis", "prizmė", "ritinys", "kūgis"],
            ),
            "erdvines_figuros": GlobalSubtopic(
                id="erdvines_figuros",
                title_lt="Erdvinės figūros (Stereometrija)",
                title_en="3D Shapes",
                grades=[7, 8, 12],
                keywords=["prizmė", "piramidė", "ritinys", "kūgis", "apotema", "stereometrija", "suktiniai"],
            ),
            "tieses_lygiagretumas": GlobalSubtopic(
                id="tieses_lygiagretumas",
                title_lt="Tiesės, lygiagretumas, statmenumas",
                title_en="Lines, parallelism, perpendicularity",
                grades=[7, 9, 10],
                keywords=["lygiagrečios", "statmenos", "kirstinė", "atitinkamieji"],
            ),
            "transformacijos": GlobalSubtopic(
                id="transformacijos",
                title_lt="Transformacijos ir simetrija",
                title_en="Transformations and symmetry",
                grades=[5, 6, 7, 9],
                keywords=["simetrija", "postūmis", "posūkis", "atspindys", "lygumas"],
            ),
            "koordinates": GlobalSubtopic(
                id="koordinates",
                title_lt="Koordinatės ir koordinačių plokštuma",
                title_en="Coordinates and coordinate plane",
                grades=[6, 7, 8, 9],
                keywords=["koordinačių", "plokštuma", "ketvirčiai", "taškas"],
            ),
            "matavimo_vienetai": GlobalSubtopic(
                id="matavimo_vienetai",
                title_lt="Matavimo vienetai",
                title_en="Units of measurement",
                grades=[5, 6],
                keywords=["matavimas", "vienetai", "stambinimas", "smulkinimas"],
            ),
            "braizybos_uzdaviniai": GlobalSubtopic(
                id="braizybos_uzdaviniai",
                title_lt="Braižymo uždaviniai",
                title_en="Construction problems",
                grades=[7],
                keywords=["skriestuvas", "liniuotė", "braižymas"],
            ),
            "vektoriai": GlobalSubtopic(
                id="vektoriai",
                title_lt="Vektoriai",
                title_en="Vectors",
                grades=[8, 9, 10, 11, 12],
                keywords=["vektorius", "koordinatės", "skaliarinė sandauga", "kolinearumas", "plokštuma", "erdvė"],
            ),
            "pitagoro_teorema": GlobalSubtopic(
                id="pitagoro_teorema",
                title_lt="Pitagoro teorema",
                title_en="Pythagorean theorem",
                grades=[8, 9, 10],
                keywords=["Pitagoro", "hipotenuzė", "statinis", "stačiasis trikampis"],
            ),
        },
    ),
    # ─── 4. FUNKCIJOS IR MAZGO ANALIZĖ ───
    "funkcijos": GlobalArea(
        id="funkcijos",
        title_lt="Funkcijos ir grafikai",
        title_en="Functions and Graphs",
        subtopics={
            "tiesioginis_proporcingumas": GlobalSubtopic(
                id="tiesioginis_proporcingumas",
                title_lt="Tiesioginis proporcingumas",
                title_en="Direct proportionality",
                grades=[6, 7],
                keywords=["tiesioginis", "proporcingumas", "koeficientas"],
            ),
            "atvirkstinis_proporcingumas": GlobalSubtopic(
                id="atvirkstinis_proporcingumas",
                title_lt="Atvirkštinis proporcingumas",
                title_en="Inverse proportionality",
                grades=[7],
                keywords=["atvirkštinis", "hiperbolė"],
            ),
            "grafikai": GlobalSubtopic(
                id="grafikai",
                title_lt="Grafikai ir priklausomybės",
                title_en="Graphs and dependencies",
                grades=[6, 7, 8, 9, 10],
                keywords=["grafikas", "priklausomas", "nepriklausomas", "kintamasis", "tyrimas"],
            ),
            "tiesine_funkcija": GlobalSubtopic(
                id="tiesine_funkcija",
                title_lt="Tiesinė funkcija",
                title_en="Linear function",
                grades=[8, 9],
                keywords=["tiesinė funkcija", "y = kx + b", "nuolydis"],
            ),
            "kvadratine_funkcija": GlobalSubtopic(
                id="kvadratine_funkcija",
                title_lt="Kvadratinė funkcija",
                title_en="Quadratic function",
                grades=[9, 10],
                keywords=["parabolė", "viršūnė", "šakos"],
            ),
            "laipsniai_logaritmai": GlobalSubtopic(
                id="laipsniai_logaritmai",
                title_lt="Logaritminės ir rodiklinės funkcijos",
                title_en="Logarithmic and exponential functions",
                grades=[11],
                keywords=["logaritmas", "rodiklinė", "laipsniai"],
            ),
            "trigonometrija": GlobalSubtopic(
                id="trigonometrija",
                title_lt="Trigonometrija",
                title_en="Trigonometry",
                grades=[11],
                keywords=["sinusas", "kosinusas", "tangentas", "vienetinis apskritimas", "tapatybės"],
            ),
            "isvestines": GlobalSubtopic(
                id="isvestines",
                title_lt="Išvestinės",
                title_en="Derivatives",
                grades=[12],
                keywords=["išvestinė", "diferenciavimas", "ekstremumai", "optimizavimas"],
            ),
            "integralai": GlobalSubtopic(
                id="integralai",
                title_lt="Integralai",
                title_en="Integrals",
                grades=[12],
                keywords=["integralas", "pirmykštė funkcija", "plotas", "apibrėžtinis"],
            ),
        },
    ),
    # ─── 5. STATISTIKA ───
    "statistika": GlobalArea(
        id="statistika",
        title_lt="Statistika ir duomenų analizė",
        title_en="Statistics and Data Analysis",
        subtopics={
            "duomenu_rinkimas": GlobalSubtopic(
                id="duomenu_rinkimas",
                title_lt="Duomenų rinkimas ir analizė",
                title_en="Data collection and analysis",
                grades=[5, 6, 7, 8, 9, 10, 11, 12],
                keywords=["duomenys", "rinkimas", "analizė", "tyrimas"],
            ),
            "vidurkis_mediana_moda": GlobalSubtopic(
                id="vidurkis_mediana_moda",
                title_lt="Vidurkis, mediana ir moda",
                title_en="Mean, median and mode",
                grades=[6, 7, 8, 9, 10, 11, 12],
                keywords=["vidurkis", "mediana", "moda", "dažnis", "dispersija", "nuokrypis"],
            ),
            "diagramos": GlobalSubtopic(
                id="diagramos",
                title_lt="Diagramos ir grafinis vaizdavimas",
                title_en="Charts and graphical representation",
                grades=[5, 6, 7, 8, 9, 10, 11],
                keywords=["diagrama", "stulpelinė", "skritulinė", "linijinė", "histograma"],
            ),
            "imtis_atranka": GlobalSubtopic(
                id="imtis_atranka",
                title_lt="Imtis ir atranka",
                title_en="Sampling",
                grades=[7, 8, 11],
                keywords=["imtis", "populiacija", "atranka", "reprezentatyvi"],
            ),
            "kvartiliai": GlobalSubtopic(
                id="kvartiliai",
                title_lt="Kvartiliai ir stačiakampė diagrama",
                title_en="Quartiles and box plot",
                grades=[8, 12],
                keywords=["kvartilis", "stačiakampė diagrama", "ūsai", "išskirtys"],
            ),
        },
    ),
    # ─── 6. TIKIMYBĖS IR FINANSAI ───
    "tikimybes": GlobalArea(
        id="tikimybes",
        title_lt="Tikimybės ir finansiniai skaičiavimai",
        title_en="Probability and Financial Calculations",
        subtopics={
            "atsitiktiniai_ivykiai": GlobalSubtopic(
                id="atsitiktiniai_ivykiai",
                title_lt="Atsitiktiniai įvykiai ir tikimybė",
                title_en="Random events and probability",
                grades=[5, 6, 7, 8, 9, 10, 11, 12],
                keywords=["tikimybė", "atsitiktinis", "baigtys", "įvykis", "kombinatorika"],
            ),
            "diskreti_skirstiniai": GlobalSubtopic(
                id="diskreti_skirstiniai",
                title_lt="Diskretieji atsitiktiniai dydžiai",
                title_en="Discrete random variables",
                grades=[12],
                keywords=["atsitiktinis dydis", "skirstinys", "matematinė viltis", "dispersija"],
            ),
            "finansiniai": GlobalSubtopic(
                id="finansiniai",
                title_lt="Finansiniai skaičiavimai",
                title_en="Financial calculations",
                grades=[7, 8, 9, 10],
                keywords=["palūkanos", "biudžetas", "mokesčiai", "sąskaitos"],
            ),
            "judejimo_uzdaviniai": GlobalSubtopic(
                id="judejimo_uzdaviniai",
                title_lt="Judėjimo ir darbo uždaviniai",
                title_en="Motion and work problems",
                grades=[5, 6, 7, 8, 9, 10],
                keywords=["greitis", "laikas", "kelias", "darbo", "tekstiniai"],
            ),
            "matematinis_samprotavimas": GlobalSubtopic(
                id="matematinis_samprotavimas",
                title_lt="Matematinis samprotavimas ir įrodymai",
                title_en="Mathematical reasoning and proofs",
                grades=[9, 10, 11, 12],
                keywords=["samprotavimas", "įrodymas", "prieštaros", "modeliavimas", "teiginiai"],
            ),
        },
    ),
}


# === PAGALBINĖS FUNKCIJOS ===


def get_area(area_id: str) -> Optional[GlobalArea]:
    """Gauti globalią sritį pagal ID."""
    return GLOBAL_AREAS.get(area_id)


def get_subtopic(area_id: str, subtopic_id: str) -> Optional[GlobalSubtopic]:
    """Gauti potemę pagal srities ir potemės ID."""
    area = GLOBAL_AREAS.get(area_id)
    if area:
        return area.subtopics.get(subtopic_id)
    return None


def find_subtopic(subtopic_id: str) -> Optional[tuple]:
    """Rasti potemę bet kurioje srityje. Grąžina (area_id, subtopic)."""
    for area_id, area in GLOBAL_AREAS.items():
        if subtopic_id in area.subtopics:
            return area_id, area.subtopics[subtopic_id]
    return None


def get_subtopics_by_grade(grade: int) -> List[tuple]:
    """Gauti visas potemes, taikomas nurodytai klasei.
    
    Grąžina sąrašą: [(area_id, subtopic_id, subtopic), ...]
    """
    result = []
    for area_id, area in GLOBAL_AREAS.items():
        for sub_id, sub in area.subtopics.items():
            if grade in sub.grades:
                result.append((area_id, sub_id, sub))
    return result


def get_all_areas_list() -> List[Dict]:
    """Gauti visų sričių sąrašą su potemėmis (API atsakymui)."""
    return [
        {
            "id": area.id,
            "title": area.title_lt,
            "title_en": area.title_en,
            "subtopics": [
                {
                    "id": sub.id,
                    "title": sub.title_lt,
                    "title_en": sub.title_en,
                    "grades": sub.grades,
                }
                for sub in area.subtopics.values()
            ],
        }
        for area in GLOBAL_AREAS.values()
    ]


def get_areas_grouped_by_grade(grade: int) -> Dict:
    """Gauti sritis su potemėmis, filtruotas pagal klasę."""
    result = {}
    for area_id, area in GLOBAL_AREAS.items():
        relevant_subs = {
            sub_id: sub
            for sub_id, sub in area.subtopics.items()
            if grade in sub.grades
        }
        if relevant_subs:
            result[area_id] = {
                "title": area.title_lt,
                "subtopics": [
                    {"id": s.id, "title": s.title_lt, "grades": s.grades}
                    for s in relevant_subs.values()
                ],
            }
    return result


# Mapping iš senų topics.py ID → naujus global_topics ID
LEGACY_TOPIC_MAPPING = {
    "natural_numbers": ("skaiciai", "naturalieji"),
    "integers": ("skaiciai", "sveikieji"),
    "fractions": ("skaiciai", "trupmenos"),
    "decimals": ("skaiciai", "trupmenos"),
    "percentages": ("skaiciai", "procentai"),
    "ratios": ("algebra", "proporcijos"),
    "powers": ("skaiciai", "laipsniai"),
    "roots": ("skaiciai", "saknys"),
    "expressions": ("algebra", "reiskiniai"),
    "linear_equations": ("algebra", "tiesines_lygtys"),
    "quadratic_equations": ("algebra", "lygtys_sistemos"),
    "inequalities": ("algebra", "nelygybes"),
    "equation_systems": ("algebra", "lygtys_sistemos"),
    "functions": ("funkcijos", "tiesine_funkcija"),
    "sequences": ("algebra", "sekos"),
    "polynomials": ("algebra", "daugianariai"),
    "basic_shapes": ("geometrija", "perimetras_plotas"),
    "angles": ("geometrija", "kampai"),
    "triangles": ("geometrija", "trikampiai"),
    "quadrilaterals": ("geometrija", "keturkampiai"),
    "circles": ("geometrija", "apskritimai"),
    "perimeter_area": ("geometrija", "perimetras_plotas"),
    "volume": ("geometrija", "turis"),
    "coordinate_geometry": ("geometrija", "koordinates"),
    "transformations": ("geometrija", "transformacijos"),
    "pythagorean": ("geometrija", "trikampiai"),
    "data_analysis": ("statistika", "duomenu_rinkimas"),
    "mean_median": ("statistika", "vidurkis_mediana_moda"),
    "probability": ("tikimybes", "atsitiktiniai_ivykiai"),
    "graphs_charts": ("statistika", "diagramos"),
    "word_problems": ("tikimybes", "judejimo_uzdaviniai"),
    "units_conversion": ("geometrija", "matavimo_vienetai"),
    "money": ("tikimybes", "finansiniai"),
    "time": ("tikimybes", "judejimo_uzdaviniai"),
}


def map_legacy_topic(old_topic_id: str) -> Optional[tuple]:
    """Konvertuoti seną temos ID į naujus (area_id, subtopic_id)."""
    return LEGACY_TOPIC_MAPPING.get(old_topic_id)
