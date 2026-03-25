"""
Geometry Checker - Geometrijos uždavinių tikrinimas
===================================================
Tikrina geometrijos uždavinius: plotai, perimetrai, tūriai.
"""

import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Union

try:
    pass

    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False


class GeometryShape(Enum):
    """Geometrinės figūros."""

    # 2D figūros
    SQUARE = "square"
    RECTANGLE = "rectangle"
    TRIANGLE = "triangle"
    CIRCLE = "circle"
    PARALLELOGRAM = "parallelogram"
    TRAPEZOID = "trapezoid"
    RHOMBUS = "rhombus"

    # 3D figūros
    CUBE = "cube"
    CUBOID = "cuboid"  # Stačiakampis gretasienis
    CYLINDER = "cylinder"
    CONE = "cone"
    SPHERE = "sphere"
    PYRAMID = "pyramid"
    PRISM = "prism"


class CalculationType(Enum):
    """Skaičiavimo tipas."""

    AREA = "area"
    PERIMETER = "perimeter"
    VOLUME = "volume"
    SURFACE_AREA = "surface_area"
    DIAGONAL = "diagonal"
    HEIGHT = "height"
    RADIUS = "radius"
    SIDE = "side"


@dataclass
class GeometryResult:
    """Geometrijos skaičiavimo rezultatas."""

    is_correct: bool
    message: str
    expected_value: Union[float, str]
    student_value: Union[float, str]
    expected_formula: Optional[str] = None
    error_percentage: float = 0.0
    hint: Optional[str] = None


class GeometryChecker:
    """Geometrijos uždavinių tikrintojas."""

    def __init__(self, tolerance: float = 0.01):
        """
        Args:
            tolerance: Leistinas procentinis skirtumas (0.01 = 1%)
        """
        self.tolerance = tolerance

        # Formulių žinynas lietuvių kalba
        self.formulas = {
            # 2D plotai
            (GeometryShape.SQUARE, CalculationType.AREA): {
                "formula": "a²",
                "description": "Kvadrato plotas = kraštinė²",
                "params": ["a"],
            },
            (GeometryShape.RECTANGLE, CalculationType.AREA): {
                "formula": "a × b",
                "description": "Stačiakampio plotas = ilgis × plotis",
                "params": ["a", "b"],
            },
            (GeometryShape.TRIANGLE, CalculationType.AREA): {
                "formula": "½ × a × h",
                "description": "Trikampio plotas = ½ × pagrindas × aukštis",
                "params": ["a", "h"],
            },
            (GeometryShape.CIRCLE, CalculationType.AREA): {
                "formula": "π × r²",
                "description": "Apskritimo plotas = π × spindulys²",
                "params": ["r"],
            },
            (GeometryShape.PARALLELOGRAM, CalculationType.AREA): {
                "formula": "a × h",
                "description": "Lygiagretainio plotas = pagrindas × aukštis",
                "params": ["a", "h"],
            },
            (GeometryShape.TRAPEZOID, CalculationType.AREA): {
                "formula": "½ × (a + b) × h",
                "description": "Trapecijos plotas = ½ × (viršutinė + apatinė) × aukštis",
                "params": ["a", "b", "h"],
            },
            (GeometryShape.RHOMBUS, CalculationType.AREA): {
                "formula": "½ × d₁ × d₂",
                "description": "Rombo plotas = ½ × pirmoji įstrižainė × antroji įstrižainė",
                "params": ["d1", "d2"],
            },
            # 2D perimetrai
            (GeometryShape.SQUARE, CalculationType.PERIMETER): {
                "formula": "4 × a",
                "description": "Kvadrato perimetras = 4 × kraštinė",
                "params": ["a"],
            },
            (GeometryShape.RECTANGLE, CalculationType.PERIMETER): {
                "formula": "2 × (a + b)",
                "description": "Stačiakampio perimetras = 2 × (ilgis + plotis)",
                "params": ["a", "b"],
            },
            (GeometryShape.TRIANGLE, CalculationType.PERIMETER): {
                "formula": "a + b + c",
                "description": "Trikampio perimetras = suma visų kraštinių",
                "params": ["a", "b", "c"],
            },
            (GeometryShape.CIRCLE, CalculationType.PERIMETER): {
                "formula": "2 × π × r",
                "description": "Apskritimo ilgis = 2 × π × spindulys",
                "params": ["r"],
            },
            # 3D tūriai
            (GeometryShape.CUBE, CalculationType.VOLUME): {
                "formula": "a³",
                "description": "Kubo tūris = kraštinė³",
                "params": ["a"],
            },
            (GeometryShape.CUBOID, CalculationType.VOLUME): {
                "formula": "a × b × c",
                "description": "Stačiakampio gretasienio tūris = ilgis × plotis × aukštis",
                "params": ["a", "b", "c"],
            },
            (GeometryShape.CYLINDER, CalculationType.VOLUME): {
                "formula": "π × r² × h",
                "description": "Cilindro tūris = π × spindulys² × aukštis",
                "params": ["r", "h"],
            },
            (GeometryShape.CONE, CalculationType.VOLUME): {
                "formula": "⅓ × π × r² × h",
                "description": "Kūgio tūris = ⅓ × π × spindulys² × aukštis",
                "params": ["r", "h"],
            },
            (GeometryShape.SPHERE, CalculationType.VOLUME): {
                "formula": "⁴⁄₃ × π × r³",
                "description": "Rutulio tūris = ⁴⁄₃ × π × spindulys³",
                "params": ["r"],
            },
            (GeometryShape.PYRAMID, CalculationType.VOLUME): {
                "formula": "⅓ × S × h",
                "description": "Piramidės tūris = ⅓ × pagrindo plotas × aukštis",
                "params": ["S", "h"],
            },
            (GeometryShape.PRISM, CalculationType.VOLUME): {
                "formula": "S × h",
                "description": "Prizmės tūris = pagrindo plotas × aukštis",
                "params": ["S", "h"],
            },
            # 3D paviršiaus plotai
            (GeometryShape.CUBE, CalculationType.SURFACE_AREA): {
                "formula": "6 × a²",
                "description": "Kubo paviršiaus plotas = 6 × kraštinė²",
                "params": ["a"],
            },
            (GeometryShape.CUBOID, CalculationType.SURFACE_AREA): {
                "formula": "2 × (ab + bc + ac)",
                "description": "Stačiakampio gretasienio paviršiaus plotas",
                "params": ["a", "b", "c"],
            },
            (GeometryShape.SPHERE, CalculationType.SURFACE_AREA): {
                "formula": "4 × π × r²",
                "description": "Rutulio paviršiaus plotas = 4 × π × spindulys²",
                "params": ["r"],
            },
            (GeometryShape.CYLINDER, CalculationType.SURFACE_AREA): {
                "formula": "2πr² + 2πrh",
                "description": "Cilindro paviršiaus plotas (su pagrindais)",
                "params": ["r", "h"],
            },
        }

    # ==================== 2D PLOTAI ====================

    def area_square(self, a: float) -> float:
        """Kvadrato plotas."""
        return a**2

    def area_rectangle(self, a: float, b: float) -> float:
        """Stačiakampio plotas."""
        return a * b

    def area_triangle(self, base: float, height: float) -> float:
        """Trikampio plotas."""
        return 0.5 * base * height

    def area_triangle_heron(self, a: float, b: float, c: float) -> float:
        """Trikampio plotas pagal Herono formulę."""
        s = (a + b + c) / 2  # pusperimetris
        return math.sqrt(s * (s - a) * (s - b) * (s - c))

    def area_circle(self, r: float) -> float:
        """Apskritimo plotas."""
        return math.pi * r**2

    def area_parallelogram(self, base: float, height: float) -> float:
        """Lygiagretainio plotas."""
        return base * height

    def area_trapezoid(self, a: float, b: float, h: float) -> float:
        """Trapecijos plotas."""
        return 0.5 * (a + b) * h

    def area_rhombus(self, d1: float, d2: float) -> float:
        """Rombo plotas."""
        return 0.5 * d1 * d2

    # ==================== 2D PERIMETRAI ====================

    def perimeter_square(self, a: float) -> float:
        """Kvadrato perimetras."""
        return 4 * a

    def perimeter_rectangle(self, a: float, b: float) -> float:
        """Stačiakampio perimetras."""
        return 2 * (a + b)

    def perimeter_triangle(self, a: float, b: float, c: float) -> float:
        """Trikampio perimetras."""
        return a + b + c

    def perimeter_circle(self, r: float) -> float:
        """Apskritimo ilgis."""
        return 2 * math.pi * r

    # ==================== 3D TŪRIAI ====================

    def volume_cube(self, a: float) -> float:
        """Kubo tūris."""
        return a**3

    def volume_cuboid(self, a: float, b: float, c: float) -> float:
        """Stačiakampio gretasienio tūris."""
        return a * b * c

    def volume_cylinder(self, r: float, h: float) -> float:
        """Cilindro tūris."""
        return math.pi * r**2 * h

    def volume_cone(self, r: float, h: float) -> float:
        """Kūgio tūris."""
        return (1 / 3) * math.pi * r**2 * h

    def volume_sphere(self, r: float) -> float:
        """Rutulio tūris."""
        return (4 / 3) * math.pi * r**3

    def volume_pyramid(self, base_area: float, h: float) -> float:
        """Piramidės tūris."""
        return (1 / 3) * base_area * h

    def volume_prism(self, base_area: float, h: float) -> float:
        """Prizmės tūris."""
        return base_area * h

    # ==================== 3D PAVIRŠIAUS PLOTAI ====================

    def surface_area_cube(self, a: float) -> float:
        """Kubo paviršiaus plotas."""
        return 6 * a**2

    def surface_area_cuboid(self, a: float, b: float, c: float) -> float:
        """Stačiakampio gretasienio paviršiaus plotas."""
        return 2 * (a * b + b * c + a * c)

    def surface_area_sphere(self, r: float) -> float:
        """Rutulio paviršiaus plotas."""
        return 4 * math.pi * r**2

    def surface_area_cylinder(self, r: float, h: float) -> float:
        """Cilindro paviršiaus plotas (su pagrindais)."""
        return 2 * math.pi * r**2 + 2 * math.pi * r * h

    # ==================== PAGALBINĖS FUNKCIJOS ====================

    def diagonal_square(self, a: float) -> float:
        """Kvadrato įstrižainė."""
        return a * math.sqrt(2)

    def diagonal_rectangle(self, a: float, b: float) -> float:
        """Stačiakampio įstrižainė."""
        return math.sqrt(a**2 + b**2)

    def diagonal_cube(self, a: float) -> float:
        """Kubo erdvinė įstrižainė."""
        return a * math.sqrt(3)

    def diagonal_cuboid(self, a: float, b: float, c: float) -> float:
        """Stačiakampio gretasienio erdvinė įstrižainė."""
        return math.sqrt(a**2 + b**2 + c**2)

    # ==================== TIKRINIMO METODAI ====================

    def check_answer(
        self,
        student_answer: Union[float, str],
        expected: float,
        shape: GeometryShape,
        calc_type: CalculationType,
    ) -> GeometryResult:
        """
        Tikrina ar mokinio atsakymas teisingas.

        Args:
            student_answer: Mokinio atsakymas
            expected: Tikėtinas teisingas atsakymas
            shape: Geometrinė figūra
            calc_type: Skaičiavimo tipas

        Returns:
            GeometryResult su tikrinimo rezultatu
        """
        # Konvertuojame mokinio atsakymą į skaičių
        try:
            if isinstance(student_answer, str):
                # Pašaliname vienetų žymėjimus
                cleaned = student_answer.strip()
                cleaned = cleaned.replace("cm²", "").replace("m²", "")
                cleaned = cleaned.replace("cm³", "").replace("m³", "")
                cleaned = cleaned.replace("cm", "").replace("m", "")
                cleaned = cleaned.replace(",", ".")  # Lietuviška kablelis
                cleaned = cleaned.strip()

                # Jei yra π, bandome interpretuoti
                if "π" in cleaned or "pi" in cleaned.lower():
                    cleaned = cleaned.replace("π", str(math.pi))
                    cleaned = cleaned.replace("Pi", str(math.pi))
                    cleaned = cleaned.replace("PI", str(math.pi))

                student_value = float(eval(cleaned))
            else:
                student_value = float(student_answer)
        except (ValueError, SyntaxError) as e:
            return GeometryResult(
                is_correct=False,
                message=f"Nepavyko atpažinti atsakymo: {student_answer}",
                expected_value=expected,
                student_value=student_answer,
                error_percentage=100.0,
            )

        # Skaičiuojame procentinį skirtumą
        if expected != 0:
            error_pct = abs((student_value - expected) / expected) * 100
        else:
            error_pct = abs(student_value) * 100 if student_value != 0 else 0

        # Gauname formulę
        formula_info = self.formulas.get((shape, calc_type), {})
        expected_formula = formula_info.get("formula")
        description = formula_info.get("description")

        # Tikriname ar atsakymas teisingas
        is_correct = error_pct <= (self.tolerance * 100)

        if is_correct:
            message = "Teisingai! ✓"
            hint = None
        else:
            if error_pct < 5:
                message = "Beveik teisingai. Patikrinkite apvalinimą."
                hint = f"Tikslus atsakymas: {expected:.4f}"
            elif error_pct < 20:
                message = "Artimas, bet neteisingas. Patikrinkite skaičiavimus."
                hint = description
            else:
                message = "Neteisingai. Patikrinkite formulę ir skaičiavimus."
                hint = f"Formulė: {expected_formula}. {description}"

        return GeometryResult(
            is_correct=is_correct,
            message=message,
            expected_value=round(expected, 4),
            student_value=round(student_value, 4),
            expected_formula=expected_formula,
            error_percentage=round(error_pct, 2),
            hint=hint,
        )

    def calculate_and_check(
        self,
        shape: GeometryShape,
        calc_type: CalculationType,
        student_answer: Union[float, str],
        **params,
    ) -> GeometryResult:
        """
        Apskaičiuoja teisingą atsakymą ir patikrina mokinio atsakymą.

        Args:
            shape: Geometrinė figūra
            calc_type: Skaičiavimo tipas (plotas, perimetras, tūris)
            student_answer: Mokinio atsakymas
            **params: Figūros parametrai (a, b, r, h ir t.t.)

        Returns:
            GeometryResult su tikrinimo rezultatu
        """
        # Apskaičiuojame teisingą atsakymą
        try:
            expected = self._calculate(shape, calc_type, **params)
        except Exception as e:
            return GeometryResult(
                is_correct=False,
                message=f"Klaida skaičiuojant: {str(e)}",
                expected_value="?",
                student_value=student_answer,
                error_percentage=100.0,
            )

        return self.check_answer(student_answer, expected, shape, calc_type)

    def _calculate(
        self,
        shape: GeometryShape,
        calc_type: CalculationType,
        **params,
    ) -> float:
        """Apskaičiuoja geometrinę reikšmę."""

        # 2D plotai
        if calc_type == CalculationType.AREA:
            if shape == GeometryShape.SQUARE:
                return self.area_square(params["a"])
            elif shape == GeometryShape.RECTANGLE:
                return self.area_rectangle(params["a"], params["b"])
            elif shape == GeometryShape.TRIANGLE:
                if "c" in params:  # Herono formulė
                    return self.area_triangle_heron(
                        params["a"], params["b"], params["c"]
                    )
                return self.area_triangle(params.get("base", params["a"]), params["h"])
            elif shape == GeometryShape.CIRCLE:
                return self.area_circle(params["r"])
            elif shape == GeometryShape.PARALLELOGRAM:
                return self.area_parallelogram(params["a"], params["h"])
            elif shape == GeometryShape.TRAPEZOID:
                return self.area_trapezoid(params["a"], params["b"], params["h"])
            elif shape == GeometryShape.RHOMBUS:
                return self.area_rhombus(params["d1"], params["d2"])

        # 2D perimetrai
        elif calc_type == CalculationType.PERIMETER:
            if shape == GeometryShape.SQUARE:
                return self.perimeter_square(params["a"])
            elif shape == GeometryShape.RECTANGLE:
                return self.perimeter_rectangle(params["a"], params["b"])
            elif shape == GeometryShape.TRIANGLE:
                return self.perimeter_triangle(params["a"], params["b"], params["c"])
            elif shape == GeometryShape.CIRCLE:
                return self.perimeter_circle(params["r"])

        # 3D tūriai
        elif calc_type == CalculationType.VOLUME:
            if shape == GeometryShape.CUBE:
                return self.volume_cube(params["a"])
            elif shape == GeometryShape.CUBOID:
                return self.volume_cuboid(params["a"], params["b"], params["c"])
            elif shape == GeometryShape.CYLINDER:
                return self.volume_cylinder(params["r"], params["h"])
            elif shape == GeometryShape.CONE:
                return self.volume_cone(params["r"], params["h"])
            elif shape == GeometryShape.SPHERE:
                return self.volume_sphere(params["r"])
            elif shape == GeometryShape.PYRAMID:
                return self.volume_pyramid(params["S"], params["h"])
            elif shape == GeometryShape.PRISM:
                return self.volume_prism(params["S"], params["h"])

        # 3D paviršiaus plotai
        elif calc_type == CalculationType.SURFACE_AREA:
            if shape == GeometryShape.CUBE:
                return self.surface_area_cube(params["a"])
            elif shape == GeometryShape.CUBOID:
                return self.surface_area_cuboid(params["a"], params["b"], params["c"])
            elif shape == GeometryShape.SPHERE:
                return self.surface_area_sphere(params["r"])
            elif shape == GeometryShape.CYLINDER:
                return self.surface_area_cylinder(params["r"], params["h"])

        # Įstrižainės
        elif calc_type == CalculationType.DIAGONAL:
            if shape == GeometryShape.SQUARE:
                return self.diagonal_square(params["a"])
            elif shape == GeometryShape.RECTANGLE:
                return self.diagonal_rectangle(params["a"], params["b"])
            elif shape == GeometryShape.CUBE:
                return self.diagonal_cube(params["a"])
            elif shape == GeometryShape.CUBOID:
                return self.diagonal_cuboid(params["a"], params["b"], params["c"])

        raise ValueError(f"Nepalaiko: {shape.value} {calc_type.value}")

    def get_formula(
        self,
        shape: GeometryShape,
        calc_type: CalculationType,
    ) -> Dict[str, str]:
        """Gauna formulę ir aprašymą."""
        return self.formulas.get(
            (shape, calc_type),
            {"formula": "Nežinoma", "description": "Formulė nerasta", "params": []},
        )


# Convenience funkcijos tiesiogiam naudojimui
def check_area(
    shape: str,
    student_answer: Union[float, str],
    **params,
) -> GeometryResult:
    """
    Patogi funkcija ploto tikrinimui.

    Pavyzdys:
        result = check_area("rectangle", 24, a=6, b=4)
    """
    checker = GeometryChecker()
    shape_enum = GeometryShape(shape)
    return checker.calculate_and_check(
        shape_enum, CalculationType.AREA, student_answer, **params
    )


def check_perimeter(
    shape: str,
    student_answer: Union[float, str],
    **params,
) -> GeometryResult:
    """Patogi funkcija perimetro tikrinimui."""
    checker = GeometryChecker()
    shape_enum = GeometryShape(shape)
    return checker.calculate_and_check(
        shape_enum, CalculationType.PERIMETER, student_answer, **params
    )


def check_volume(
    shape: str,
    student_answer: Union[float, str],
    **params,
) -> GeometryResult:
    """Patogi funkcija tūrio tikrinimui."""
    checker = GeometryChecker()
    shape_enum = GeometryShape(shape)
    return checker.calculate_and_check(
        shape_enum, CalculationType.VOLUME, student_answer, **params
    )


# Testavimui
if __name__ == "__main__":
    checker = GeometryChecker()

    print("=== Geometrijos tikrintojas ===\n")

    # Stačiakampio plotas
    result = check_area("rectangle", 24, a=6, b=4)
    print(f"Stačiakampis 6×4, atsakymas 24: {result.is_correct} - {result.message}")

    result = check_area("rectangle", 25, a=6, b=4)
    print(f"Stačiakampis 6×4, atsakymas 25: {result.is_correct} - {result.message}")

    # Apskritimo plotas
    result = check_area("circle", "3.14", r=1)
    print(f"Apskritimas r=1, atsakymas 3.14: {result.is_correct} - {result.message}")

    result = check_area("circle", "π", r=1)
    print(f"Apskritimas r=1, atsakymas π: {result.is_correct} - {result.message}")

    # Kubo tūris
    result = check_volume("cube", 27, a=3)
    print(f"Kubas a=3, atsakymas 27: {result.is_correct} - {result.message}")

    # Formulės
    formula = checker.get_formula(GeometryShape.TRAPEZOID, CalculationType.AREA)
    print(f"\nTrapecijos ploto formulė: {formula['formula']}")
    print(f"Aprašymas: {formula['description']}")
