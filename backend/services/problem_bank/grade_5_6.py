"""5-6 klasės uždavinių generatoriai."""
import math
import random
from fractions import Fraction

from services.problem_bank.common import (
    Difficulty, MathProblem, DeclinedName,
    random_name, male_name, female_name,
    get_random_name, get_male_name, get_female_name, get_two_names,
    random_in_context, get_item_form, skaitvardis, daiktavardis_kilm,
    NAMES_MALE, NAMES_FEMALE,
)

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


