"""9-10 klasės uždavinių generatoriai."""
import math
import random

from services.problem_bank.common import (
    Difficulty, MathProblem,
    random_name,
)

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


