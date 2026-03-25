"""11-12 klasės uždavinių generatoriai (VBE)."""
import math
import random

from services.problem_bank.common import (
    Difficulty, MathProblem,
    random_name,
)

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


