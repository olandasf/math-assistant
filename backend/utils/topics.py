"""
Matematikos temų konstantos ir pagalbinės funkcijos.
Naudojama užduočių žymėjimui pagal temą.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Topic:
    """Matematikos tema."""

    id: str
    name_lt: str
    name_en: str
    category: str
    grade_levels: List[int]  # Klasės, kurioms taikoma


# Temų kategorijos
TOPIC_CATEGORIES = {
    "arithmetic": "Aritmetika",
    "algebra": "Algebra",
    "geometry": "Geometrija",
    "statistics": "Statistika ir tikimybės",
    "other": "Kita",
}

# Visos matematikos temos
TOPICS: Dict[str, Topic] = {
    # Aritmetika
    "natural_numbers": Topic(
        id="natural_numbers",
        name_lt="Natūralieji skaičiai",
        name_en="Natural numbers",
        category="arithmetic",
        grade_levels=[5, 6],
    ),
    "integers": Topic(
        id="integers",
        name_lt="Sveikieji skaičiai",
        name_en="Integers",
        category="arithmetic",
        grade_levels=[6, 7],
    ),
    "fractions": Topic(
        id="fractions",
        name_lt="Trupmenos",
        name_en="Fractions",
        category="arithmetic",
        grade_levels=[5, 6, 7],
    ),
    "decimals": Topic(
        id="decimals",
        name_lt="Dešimtainės trupmenos",
        name_en="Decimals",
        category="arithmetic",
        grade_levels=[5, 6],
    ),
    "percentages": Topic(
        id="percentages",
        name_lt="Procentai",
        name_en="Percentages",
        category="arithmetic",
        grade_levels=[6, 7, 8],
    ),
    "ratios": Topic(
        id="ratios",
        name_lt="Santykiai ir proporcijos",
        name_en="Ratios and proportions",
        category="arithmetic",
        grade_levels=[6, 7, 8],
    ),
    "powers": Topic(
        id="powers",
        name_lt="Laipsniai",
        name_en="Powers",
        category="arithmetic",
        grade_levels=[7, 8],
    ),
    "roots": Topic(
        id="roots",
        name_lt="Šaknys",
        name_en="Roots",
        category="arithmetic",
        grade_levels=[8],
    ),
    # Algebra
    "expressions": Topic(
        id="expressions",
        name_lt="Reiškiniai",
        name_en="Expressions",
        category="algebra",
        grade_levels=[6, 7, 8],
    ),
    "linear_equations": Topic(
        id="linear_equations",
        name_lt="Tiesinės lygtys",
        name_en="Linear equations",
        category="algebra",
        grade_levels=[6, 7, 8],
    ),
    "quadratic_equations": Topic(
        id="quadratic_equations",
        name_lt="Kvadratinės lygtys",
        name_en="Quadratic equations",
        category="algebra",
        grade_levels=[8, 10],
    ),
    "inequalities": Topic(
        id="inequalities",
        name_lt="Nelygybės",
        name_en="Inequalities",
        category="algebra",
        grade_levels=[7, 8],
    ),
    "equation_systems": Topic(
        id="equation_systems",
        name_lt="Lygčių sistemos",
        name_en="Systems of equations",
        category="algebra",
        grade_levels=[8, 10],
    ),
    "functions": Topic(
        id="functions",
        name_lt="Funkcijos",
        name_en="Functions",
        category="algebra",
        grade_levels=[8, 10],
    ),
    "sequences": Topic(
        id="sequences",
        name_lt="Sekos",
        name_en="Sequences",
        category="algebra",
        grade_levels=[8, 10],
    ),
    "polynomials": Topic(
        id="polynomials",
        name_lt="Daugianariai",
        name_en="Polynomials",
        category="algebra",
        grade_levels=[7, 8],
    ),
    # Geometrija
    "basic_shapes": Topic(
        id="basic_shapes",
        name_lt="Pagrindinės figūros",
        name_en="Basic shapes",
        category="geometry",
        grade_levels=[5, 6],
    ),
    "angles": Topic(
        id="angles",
        name_lt="Kampai",
        name_en="Angles",
        category="geometry",
        grade_levels=[5, 6, 7],
    ),
    "triangles": Topic(
        id="triangles",
        name_lt="Trikampiai",
        name_en="Triangles",
        category="geometry",
        grade_levels=[6, 7, 8],
    ),
    "quadrilaterals": Topic(
        id="quadrilaterals",
        name_lt="Keturkampiai",
        name_en="Quadrilaterals",
        category="geometry",
        grade_levels=[6, 7, 8],
    ),
    "circles": Topic(
        id="circles",
        name_lt="Apskritimai",
        name_en="Circles",
        category="geometry",
        grade_levels=[6, 7, 8],
    ),
    "perimeter_area": Topic(
        id="perimeter_area",
        name_lt="Perimetras ir plotas",
        name_en="Perimeter and area",
        category="geometry",
        grade_levels=[5, 6, 7, 8],
    ),
    "volume": Topic(
        id="volume",
        name_lt="Tūris",
        name_en="Volume",
        category="geometry",
        grade_levels=[6, 7, 8],
    ),
    "coordinate_geometry": Topic(
        id="coordinate_geometry",
        name_lt="Koordinatės",
        name_en="Coordinate geometry",
        category="geometry",
        grade_levels=[7, 8],
    ),
    "transformations": Topic(
        id="transformations",
        name_lt="Transformacijos",
        name_en="Transformations",
        category="geometry",
        grade_levels=[7, 8],
    ),
    "pythagorean": Topic(
        id="pythagorean",
        name_lt="Pitagoro teorema",
        name_en="Pythagorean theorem",
        category="geometry",
        grade_levels=[8],
    ),
    # Statistika ir tikimybės
    "data_analysis": Topic(
        id="data_analysis",
        name_lt="Duomenų analizė",
        name_en="Data analysis",
        category="statistics",
        grade_levels=[5, 6, 7, 8],
    ),
    "mean_median": Topic(
        id="mean_median",
        name_lt="Vidurkis ir mediana",
        name_en="Mean and median",
        category="statistics",
        grade_levels=[6, 7, 8],
    ),
    "probability": Topic(
        id="probability",
        name_lt="Tikimybės",
        name_en="Probability",
        category="statistics",
        grade_levels=[7, 8],
    ),
    "graphs_charts": Topic(
        id="graphs_charts",
        name_lt="Grafikai ir diagramos",
        name_en="Graphs and charts",
        category="statistics",
        grade_levels=[5, 6, 7, 8],
    ),
    # Kita
    "word_problems": Topic(
        id="word_problems",
        name_lt="Tekstiniai uždaviniai",
        name_en="Word problems",
        category="other",
        grade_levels=[5, 6, 7, 8],
    ),
    "units_conversion": Topic(
        id="units_conversion",
        name_lt="Matų vienetai",
        name_en="Units and conversion",
        category="other",
        grade_levels=[5, 6, 7],
    ),
    "money": Topic(
        id="money",
        name_lt="Pinigai ir sąskaitos",
        name_en="Money",
        category="other",
        grade_levels=[5, 6],
    ),
    "time": Topic(
        id="time",
        name_lt="Laikas",
        name_en="Time",
        category="other",
        grade_levels=[5, 6],
    ),
    # === VBE TEMOS (9-12 klasės) ===
    # Trigonometrija
    "trigonometry_basics": Topic(
        id="trigonometry_basics",
        name_lt="Trigonometrijos pagrindai",
        name_en="Trigonometry basics",
        category="algebra",
        grade_levels=[9, 10],
    ),
    "trigonometry_unit_circle": Topic(
        id="trigonometry_unit_circle",
        name_lt="Vienetinis apskritimas",
        name_en="Unit circle",
        category="algebra",
        grade_levels=[10, 11],
    ),
    "trigonometry_identities": Topic(
        id="trigonometry_identities",
        name_lt="Trigonometrinės tapatybės",
        name_en="Trigonometric identities",
        category="algebra",
        grade_levels=[10, 11, 12],
    ),
    "trigonometry_equations": Topic(
        id="trigonometry_equations",
        name_lt="Trigonometrinės lygtys",
        name_en="Trigonometric equations",
        category="algebra",
        grade_levels=[10, 11, 12],
    ),
    # Logaritmai
    "logarithms_basics": Topic(
        id="logarithms_basics",
        name_lt="Logaritmų pagrindai",
        name_en="Logarithm basics",
        category="algebra",
        grade_levels=[10, 11],
    ),
    "logarithms_properties": Topic(
        id="logarithms_properties",
        name_lt="Logaritmų savybės",
        name_en="Logarithm properties",
        category="algebra",
        grade_levels=[10, 11, 12],
    ),
    "logarithmic_equations": Topic(
        id="logarithmic_equations",
        name_lt="Logaritminės lygtys",
        name_en="Logarithmic equations",
        category="algebra",
        grade_levels=[10, 11, 12],
    ),
    "exponential_equations": Topic(
        id="exponential_equations",
        name_lt="Rodiklinės lygtys",
        name_en="Exponential equations",
        category="algebra",
        grade_levels=[10, 11, 12],
    ),
    # Išvestinės ir integralai
    "derivatives_basics": Topic(
        id="derivatives_basics",
        name_lt="Išvestinės pagrindai",
        name_en="Derivative basics",
        category="algebra",
        grade_levels=[11, 12],
    ),
    "derivatives_rules": Topic(
        id="derivatives_rules",
        name_lt="Išvestinių taisyklės",
        name_en="Derivative rules",
        category="algebra",
        grade_levels=[11, 12],
    ),
    "derivatives_applications": Topic(
        id="derivatives_applications",
        name_lt="Išvestinių taikymas",
        name_en="Derivative applications",
        category="algebra",
        grade_levels=[11, 12],
    ),
    "integrals_basics": Topic(
        id="integrals_basics",
        name_lt="Integralų pagrindai",
        name_en="Integral basics",
        category="algebra",
        grade_levels=[12],
    ),
    # Vektoriai
    "vectors_basics": Topic(
        id="vectors_basics",
        name_lt="Vektorių pagrindai",
        name_en="Vector basics",
        category="geometry",
        grade_levels=[10, 11],
    ),
    "vectors_operations": Topic(
        id="vectors_operations",
        name_lt="Vektorių veiksmai",
        name_en="Vector operations",
        category="geometry",
        grade_levels=[10, 11, 12],
    ),
    "vectors_scalar_product": Topic(
        id="vectors_scalar_product",
        name_lt="Skaliarinė sandauga",
        name_en="Scalar product",
        category="geometry",
        grade_levels=[10, 11, 12],
    ),
    # Stereometrija
    "stereometry_prism": Topic(
        id="stereometry_prism",
        name_lt="Prizmė",
        name_en="Prism",
        category="geometry",
        grade_levels=[10, 11],
    ),
    "stereometry_pyramid": Topic(
        id="stereometry_pyramid",
        name_lt="Piramidė",
        name_en="Pyramid",
        category="geometry",
        grade_levels=[10, 11, 12],
    ),
    "stereometry_cone": Topic(
        id="stereometry_cone",
        name_lt="Kūgis",
        name_en="Cone",
        category="geometry",
        grade_levels=[10, 11, 12],
    ),
    "stereometry_cylinder": Topic(
        id="stereometry_cylinder",
        name_lt="Cilindras",
        name_en="Cylinder",
        category="geometry",
        grade_levels=[10, 11],
    ),
    "stereometry_sphere": Topic(
        id="stereometry_sphere",
        name_lt="Rutulys",
        name_en="Sphere",
        category="geometry",
        grade_levels=[10, 11, 12],
    ),
    # Kombinatorika ir tikimybės (VBE)
    "combinatorics": Topic(
        id="combinatorics",
        name_lt="Kombinatorika",
        name_en="Combinatorics",
        category="statistics",
        grade_levels=[10, 11, 12],
    ),
    "permutations": Topic(
        id="permutations",
        name_lt="Kėliniai",
        name_en="Permutations",
        category="statistics",
        grade_levels=[10, 11, 12],
    ),
    "combinations": Topic(
        id="combinations",
        name_lt="Deriniai",
        name_en="Combinations",
        category="statistics",
        grade_levels=[10, 11, 12],
    ),
    "probability_advanced": Topic(
        id="probability_advanced",
        name_lt="Tikimybių teorija",
        name_en="Probability theory",
        category="statistics",
        grade_levels=[10, 11, 12],
    ),
    # Progresijos
    "arithmetic_progression": Topic(
        id="arithmetic_progression",
        name_lt="Aritmetinė progresija",
        name_en="Arithmetic progression",
        category="algebra",
        grade_levels=[9, 10, 11],
    ),
    "geometric_progression": Topic(
        id="geometric_progression",
        name_lt="Geometrinė progresija",
        name_en="Geometric progression",
        category="algebra",
        grade_levels=[9, 10, 11],
    ),
    # Kitos VBE temos
    "irrational_equations": Topic(
        id="irrational_equations",
        name_lt="Iracionaliosios lygtys",
        name_en="Irrational equations",
        category="algebra",
        grade_levels=[10, 11],
    ),
    "absolute_value": Topic(
        id="absolute_value",
        name_lt="Modulis",
        name_en="Absolute value",
        category="algebra",
        grade_levels=[9, 10],
    ),
    "function_analysis": Topic(
        id="function_analysis",
        name_lt="Funkcijų tyrimas",
        name_en="Function analysis",
        category="algebra",
        grade_levels=[11, 12],
    ),
}


def get_topic(topic_id: str) -> Optional[Topic]:
    """Gauti temą pagal ID."""
    return TOPICS.get(topic_id)


def get_topic_name(topic_id: str, lang: str = "lt") -> str:
    """Gauti temos pavadinimą pagal kalbą."""
    topic = TOPICS.get(topic_id)
    if not topic:
        return topic_id
    return topic.name_lt if lang == "lt" else topic.name_en


def get_topics_by_category(category: str) -> List[Topic]:
    """Gauti visas temas pagal kategoriją."""
    return [t for t in TOPICS.values() if t.category == category]


def get_topics_by_grade(grade: int) -> List[Topic]:
    """Gauti temas pagal klasę."""
    return [t for t in TOPICS.values() if grade in t.grade_levels]


def get_all_topics_list() -> List[Dict]:
    """Gauti visų temų sąrašą (API atsakymui)."""
    return [
        {
            "id": t.id,
            "name": t.name_lt,
            "name_en": t.name_en,
            "category": t.category,
            "category_name": TOPIC_CATEGORIES.get(t.category, t.category),
            "grade_levels": t.grade_levels,
        }
        for t in TOPICS.values()
    ]


def get_topics_grouped() -> Dict[str, List[Dict]]:
    """Gauti temas sugrupuotas pagal kategorijas."""
    result = {}
    for category_id, category_name in TOPIC_CATEGORIES.items():
        topics = get_topics_by_category(category_id)
        if topics:
            result[category_id] = {
                "name": category_name,
                "topics": [
                    {
                        "id": t.id,
                        "name": t.name_lt,
                        "grade_levels": t.grade_levels,
                    }
                    for t in topics
                ],
            }
    return result
