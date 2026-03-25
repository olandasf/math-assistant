"""Papildomos temos: stereometrija, tikimybės, kombinatorika, vektoriai."""
import random
from fractions import Fraction

from services.problem_bank.common import (
    Difficulty, MathProblem,
    random_name,
)


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

        Fraction(p_num, p_denom)
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
