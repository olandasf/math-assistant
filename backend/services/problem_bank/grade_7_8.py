"""7-8 klasės uždavinių generatoriai."""
import random

from services.problem_bank.common import (
    Difficulty, MathProblem,
    random_name, get_male_name, get_female_name,
)


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
