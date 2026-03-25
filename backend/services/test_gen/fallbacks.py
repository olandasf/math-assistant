import random
import math
from typing import List, Dict, Any
from services.test_gen.models import GeneratedTask
from services.math_problem_bank import Difficulty, MathProblemGenerator

class FallbackGeneratorsMixin:
    def _distribute_points_mixed(self, task_count: int) -> list[int]:
        """Paskirsto taškus mišriam sudėtingumui (A/B/C - 40/40/20)."""
        points = []
        a_count = round(task_count * 0.4)
        b_count = round(task_count * 0.4)
        if task_count == 1:
            a_count, b_count = 1, 0
        elif task_count <= 2:
            a_count, b_count = 1, 1
            
        for i in range(task_count):
            if i < a_count:
                points.append(random.randint(1, 2))  # A (Žinios ir supratimas)
            elif i < a_count + b_count:
                points.append(random.randint(2, 3))  # B (Taikymas / Komunikavimas)
            else:
                points.append(random.randint(3, 5))  # C (Problemų sprendimas)
        return points

    def _generate_fallback_tasks(
        self,
        topic: str,
        grade_level: int,
        task_count: int,
        difficulty: str,
        points_per_task: list,
    ) -> list[GeneratedTask]:
        """Generuoja uždavinius be AI (fallback) pagal temą."""
        tasks = []
        topic_lower = topic.lower()

        for i in range(task_count):
            points = points_per_task[i] if i < len(points_per_task) else 2

            # Generuojame pagal temą
            if "trupmen" in topic_lower or "fraction" in topic_lower:
                task_data = self._generate_fraction_task(grade_level, difficulty, i + 1)
            elif "procent" in topic_lower or "percent" in topic_lower:
                task_data = self._generate_percent_task(grade_level, difficulty, i + 1)
            elif "lygt" in topic_lower or "equation" in topic_lower:
                task_data = self._generate_equation_task(grade_level, difficulty, i + 1)
            elif "geometr" in topic_lower:
                task_data = self._generate_geometry_task(grade_level, difficulty, i + 1)
            elif "funkcij" in topic_lower or "function" in topic_lower:
                # Įvairūs funkcijų uždaviniai
                func_types = [
                    self._generate_function_task,
                    self._generate_function_domain_task,
                    self._generate_function_zeros_task,
                ]
                task_func = random.choice(func_types)
                task_data = task_func(grade_level, difficulty, i + 1)
            elif "trigonometr" in topic_lower:
                task_data = self._generate_trig_task(grade_level, difficulty, i + 1)
            elif "logaritm" in topic_lower:
                task_data = self._generate_log_task(grade_level, difficulty, i + 1)
            elif "išvestin" in topic_lower or "derivative" in topic_lower:
                task_data = self._generate_derivative_task(
                    grade_level, difficulty, i + 1
                )
            elif "progresij" in topic_lower:
                task_data = self._generate_progression_task(
                    grade_level, difficulty, i + 1
                )
            else:
                # Default: mišrūs uždaviniai pagal klasę
                task_data = self._generate_mixed_task(grade_level, difficulty, i + 1)

            text = task_data["text"]
            answer = task_data["answer"]

            tasks.append(
                GeneratedTask(
                    number=i + 1,
                    text=text,
                    answer=str(answer),
                    answer_latex=str(answer),
                    points=points,
                    topic=topic,
                    difficulty=difficulty if difficulty != "mixed" else "medium",
                    solution_steps=[f"{text} = {answer}"],
                )
            )

        return tasks

    def _generate_arithmetic_task(
        self, grade_level: int, difficulty: str, num: int
    ) -> dict:
        """Generuoja aritmetikos uždavinį su kontekstu."""
        if difficulty == "easy":
            a, b = random.randint(1, 20), random.randint(1, 20)
        elif difficulty == "hard":
            a, b = random.randint(50, 200), random.randint(10, 100)
        else:
            a, b = random.randint(10, 100), random.randint(5, 50)

        # Pasirenkame vardą
        name = random.choice(self.NAMES_MALE + self.NAMES_FEMALE)

        # Tekstiniai uždaviniai su kontekstu
        templates_add = [
            (
                f"{name} turėjo {a} obuolių. Draugas davė dar {b} obuolių. Kiek obuolių dabar turi {name}?",
                a + b,
            ),
            (
                f"Parduotuvėje buvo {a} knygų. Atvežė dar {b} knygas. Kiek knygų dabar parduotuvėje?",
                a + b,
            ),
            (
                f"Autobuse važiavo {a} keleivių. Stotelėje įlipo dar {b}. Kiek keleivių dabar autobuse?",
                a + b,
            ),
            (
                f"{name} surinko {a} grybų, o jo draugas - {b} grybų. Kiek grybų jie surinko kartu?",
                a + b,
            ),
        ]

        templates_sub = [
            (
                f"{name} turėjo {max(a,b)} saldainių. Suvalgė {min(a,b)}. Kiek saldainių liko?",
                abs(a - b),
            ),
            (
                f"Bibliotekoje buvo {max(a,b)} knygų. Išdavė {min(a,b)}. Kiek knygų liko?",
                abs(a - b),
            ),
            (
                f"Autobuse važiavo {max(a,b)} keleivių. Stotelėje išlipo {min(a,b)}. Kiek keleivių liko?",
                abs(a - b),
            ),
        ]

        templates_mul = [
            (
                f"{name} nupirko {min(a,12)} sąsiuvinius po {min(b,15)} ct. Kiek sumokėjo centų?",
                min(a, 12) * min(b, 15),
            ),
            (
                f"Klasėje yra {min(a,6)} eilės po {min(b,8)} suolus. Kiek suolų klasėje?",
                min(a, 6) * min(b, 8),
            ),
            (
                f"Viename dėžutėje yra {min(a,10)} pieštukų. Kiek pieštukų yra {min(b,5)} dėžutėse?",
                min(a, 10) * min(b, 5),
            ),
            (
                f"{name} važiavo {min(a,4)} valandas greičiu {min(b,60)} km/h. Kokį atstumą nuvažiavo?",
                min(a, 4) * min(b, 60),
            ),
        ]

        templates_div = []
        # Dalyba - užtikriname kad dalinasi be liekanos
        for divisor in [2, 3, 4, 5, 6, 8, 10]:
            dividend = divisor * random.randint(2, 20)
            templates_div.extend(
                [
                    (
                        f"{name} turi {dividend} saldainių. Nori padalinti po lygiai {divisor} draugams. Po kiek saldainių gaus kiekvienas?",
                        dividend // divisor,
                    ),
                    (
                        f"Mokykloje yra {dividend} mokinių. Jie suskirstyti į {divisor} klases po lygiai. Kiek mokinių kiekvienoje klasėje?",
                        dividend // divisor,
                    ),
                ]
            )

        # Pasirenkame atsitiktinį šabloną
        all_templates = templates_add + templates_sub + templates_mul
        if templates_div:
            all_templates.extend(
                random.sample(templates_div, min(2, len(templates_div)))
            )

        text, answer = random.choice(all_templates)
        return {"text": text, "answer": answer}

    def _generate_fraction_task(
        self, grade_level: int, difficulty: str, num: int
    ) -> dict:
        """Generuoja trupmenų uždavinį su kontekstu."""
        from fractions import Fraction

        name = random.choice(self.NAMES_MALE + self.NAMES_FEMALE)

        if difficulty == "easy":
            a, b = random.randint(1, 4), random.randint(2, 5)
            c, d = random.randint(1, 4), random.randint(2, 5)
        else:
            a, b = random.randint(1, 8), random.randint(2, 10)
            c, d = random.randint(1, 8), random.randint(2, 10)

        # Užtikriname kad trupmenos yra mažesnės už 1
        if a >= b:
            a = b - 1
        if c >= d:
            c = d - 1

        # Tekstiniai uždaviniai su trupmenomis
        templates = [
            (
                f"{name} suvalgė {a}/{b} pyrago. Kokia pyrago dalis liko?",
                Fraction(b - a, b),
            ),
            (
                f"Pirmą dieną {name} perskaitė {a}/{b} knygos, antrą dieną - {c}/{d} knygos. Kokią dalį knygos perskaitė per abi dienas?",
                Fraction(a, b) + Fraction(c, d),
            ),
            (
                f"Baseinas užpildytas {a}/{b} vandens. Kokią dalį dar reikia pripilti, kad būtų pilnas?",
                Fraction(b - a, b),
            ),
            (
                f"{name} turi {a}/{b} kg obuolių ir {c}/{d} kg kriaušių. Kiek kilogramų vaisių iš viso?",
                Fraction(a, b) + Fraction(c, d),
            ),
            (
                f"Iš {a}/{b} litro pieno {name} išgėrė {c}/{d} litro. Kiek pieno liko?",
                abs(Fraction(a, b) - Fraction(c, d)),
            ),
            (
                f"Stačiakampio ilgis yra {a}/{b} m, o plotis - {c}/{d} m. Koks stačiakampio perimetras?",
                2 * (Fraction(a, b) + Fraction(c, d)),
            ),
        ]

        text, result = random.choice(templates)

        # Supaprastinta forma
        if result.denominator == 1:
            answer = str(result.numerator)
        else:
            answer = f"{result.numerator}/{result.denominator}"

        return {"text": text, "answer": answer}

    def _generate_percent_task(
        self, grade_level: int, difficulty: str, num: int
    ) -> dict:
        """Generuoja procentų uždavinį su kontekstu."""
        name = random.choice(self.NAMES_MALE + self.NAMES_FEMALE)
        base = random.choice([50, 100, 150, 200, 250, 300, 400, 500])
        percent = random.choice([10, 20, 25, 30, 40, 50, 75])
        part = base * percent // 100

        templates = [
            (
                f"{name} turėjo {base} eurų. Išleido {percent}% pinigų. Kiek eurų išleido?",
                part,
            ),
            (
                f"Parduotuvėje prekė kainuoja {base} eurų. Nuolaida - {percent}%. Kokia nuolaidos suma?",
                part,
            ),
            (
                f"Klasėje yra {base} mokinių. {percent}% mokinių lanko būrelį. Kiek mokinių lanko būrelį?",
                part,
            ),
            (
                f"{name} perskaitė {part} puslapių iš {base} puslapių knygos. Kiek procentų knygos perskaitė?",
                percent,
            ),
        ]

        if difficulty in ["medium", "hard"]:
            templates.extend(
                [
                    (
                        f"Po {percent}% nuolaidos prekė kainuoja {base - part} eurų. Kokia buvo pradinė kaina?",
                        base,
                    ),
                    (
                        f"{name} gavo {percent}% didesnį atlyginimą. Dabar gauna {base + part} eurų. Koks buvo pradinis atlyginimas?",
                        base,
                    ),
                ]
            )

        template = random.choice(templates)
        return {"text": template[0], "answer": template[1]}

    def _generate_equation_task(
        self, grade_level: int, difficulty: str, num: int
    ) -> dict:
        """Generuoja lygčių uždavinį su kontekstu."""
        name = random.choice(self.NAMES_MALE + self.NAMES_FEMALE)

        if difficulty == "easy" or grade_level <= 6:
            # Paprastos lygtys su tekstiniu kontekstu
            a = random.randint(2, 10)
            x = random.randint(1, 15)
            b = a + x

            templates = [
                (
                    f"{name} turėjo keletą saldainių. Gavęs dar {a}, jis turi {b} saldainių. Kiek saldainių turėjo iš pradžių? (Sudaryk lygtį ir išspręsk)",
                    x,
                ),
                (f"Skaičius, padaugintas iš {a}, lygus {a * x}. Koks tai skaičius?", x),
                (
                    f"{name} amžius, padidinus {a} metais, bus {b} metai. Kiek metų {name} dabar?",
                    x,
                ),
                (f"Išspręsk lygtį: x + {a} = {b}", x),
            ]
            text, answer = random.choice(templates)

        elif difficulty == "hard" or grade_level >= 9:
            # Kvadratinė lygtis
            x1 = random.randint(-5, 5)
            x2 = random.randint(-5, 5)
            a = 1
            b = -(x1 + x2)
            c = x1 * x2

            eq = f"x² "
            if b >= 0:
                eq += f"+ {b}x "
            else:
                eq += f"- {-b}x "
            if c >= 0:
                eq += f"+ {c} = 0"
            else:
                eq += f"- {-c} = 0"

            text = f"Išspręsk lygtį: {eq}"
            if x1 == x2:
                answer = f"x = {x1}"
            else:
                answer = f"x₁ = {min(x1, x2)}, x₂ = {max(x1, x2)}"
        else:
            # Tiesinė lygtis su kontekstu
            a = random.randint(2, 8)
            x = random.randint(1, 10)
            b = random.randint(1, 20)
            c = a * x + b

            templates = [
                (
                    f"{name} nupirko {a} vienodus sąsiuvinius ir dar vieną už {b} ct. Iš viso sumokėjo {c} ct. Kiek kainavo vienas sąsiuvinis?",
                    x,
                ),
                (f"Išspręsk lygtį: {a}x + {b} = {c}", x),
                (
                    f"Trikampio perimetras yra {c} cm. Dvi kraštinės yra po {a} cm, o trečioji - x cm. Rask x.",
                    c - 2 * a,
                ),
            ]
            text, answer = random.choice(templates)

        return {"text": text, "answer": answer}

    def _generate_geometry_task(
        self, grade_level: int, difficulty: str, num: int
    ) -> dict:
        """Generuoja geometrijos uždavinį."""
        shapes = ["stačiakampis", "kvadratas", "trikampis", "apskritimas"]
        shape = random.choice(shapes)

        if shape == "stačiakampis":
            a = random.randint(3, 15)
            b = random.randint(3, 15)
            calc_type = random.choice(["plotas", "perimetras"])
            if calc_type == "plotas":
                text = f"Stačiakampio kraštinės yra {a} cm ir {b} cm. Rask plotą."
                answer = f"{a * b} cm²"
            else:
                text = f"Stačiakampio kraštinės yra {a} cm ir {b} cm. Rask perimetrą."
                answer = f"{2 * (a + b)} cm"
        elif shape == "kvadratas":
            a = random.randint(2, 12)
            calc_type = random.choice(["plotas", "perimetras"])
            if calc_type == "plotas":
                text = f"Kvadrato kraštinė yra {a} cm. Rask plotą."
                answer = f"{a * a} cm²"
            else:
                text = f"Kvadrato kraštinė yra {a} cm. Rask perimetrą."
                answer = f"{4 * a} cm"
        elif shape == "trikampis":
            a = random.randint(4, 12)
            h = random.randint(3, 10)
            text = f"Trikampio pagrindas yra {a} cm, aukštinė - {h} cm. Rask plotą."
            answer = f"{a * h / 2} cm²"
        else:  # apskritimas
            r = random.randint(2, 10)
            calc_type = random.choice(["plotas", "ilgis"])
            if calc_type == "plotas":
                text = f"Apskritimo spindulys yra {r} cm. Rask plotą (π ≈ 3.14)."
                answer = f"{round(3.14 * r * r, 2)} cm²"
            else:
                text = (
                    f"Apskritimo spindulys yra {r} cm. Rask apskritimo ilgį (π ≈ 3.14)."
                )
                answer = f"{round(2 * 3.14 * r, 2)} cm"

        return {"text": text, "answer": answer}

    def _generate_function_task(
        self, grade_level: int, difficulty: str, num: int
    ) -> dict:
        """Generuoja funkcijų uždavinį."""
        a = random.randint(1, 5)
        b = random.randint(-10, 10)
        x = random.randint(-5, 5)

        if grade_level <= 8 or difficulty == "easy":
            # Tiesinė funkcija
            y = a * x + b
            sign = "+" if b >= 0 else "-"
            text = f"Duota funkcija f(x) = {a}x {sign} {abs(b)}. Rask f({x})."
            answer = y
        else:
            # Kvadratinė funkcija
            c = random.randint(-5, 5)
            y = a * x * x + b * x + c
            text = f"Duota funkcija f(x) = {a}x² + {b}x + {c}. Rask f({x})."
            answer = y

        return {"text": text, "answer": answer}

    def _generate_function_domain_task(
        self, grade_level: int, difficulty: str, num: int
    ) -> dict:
        """Generuoja funkcijos apibrėžimo srities uždavinį."""
        task_types = [
            # Šaknis
            (
                f"Rask funkcijos f(x) = √(x - {random.randint(1,10)}) apibrėžimo sritį.",
                f"x ≥ {random.randint(1,10)}",
            ),
            (
                f"Rask funkcijos f(x) = √({random.randint(2,8)} - x) apibrėžimo sritį.",
                f"x ≤ {random.randint(2,8)}",
            ),
            # Trupmena
            (
                f"Rask funkcijos f(x) = 1/(x - {random.randint(1,5)}) apibrėžimo sritį.",
                f"x ≠ {random.randint(1,5)}",
            ),
            (
                f"Rask funkcijos f(x) = (x + 1)/(x² - {random.randint(1,4)**2}) apibrėžimo sritį.",
                f"x ≠ ±{random.randint(1,4)}",
            ),
        ]
        text, answer = random.choice(task_types)
        return {"text": text, "answer": answer}

    def _generate_function_zeros_task(
        self, grade_level: int, difficulty: str, num: int
    ) -> dict:
        """Generuoja funkcijos nulių radimo uždavinį."""
        a = random.randint(1, 5)
        b = random.randint(-10, 10)

        if grade_level <= 8 or difficulty == "easy":
            # Tiesinė funkcija
            if a != 0:
                zero = -b / a
                sign = "+" if b >= 0 else "-"
                text = f"Rask funkcijos f(x) = {a}x {sign} {abs(b)} nulį (šaknį)."
                answer = f"x = {zero}" if zero == int(zero) else f"x = {-b}/{a}"
            else:
                text = f"Rask funkcijos f(x) = {b} nulį."
                answer = "Nulių nėra" if b != 0 else "Visi x"
        else:
            # Kvadratinė funkcija
            x1 = random.randint(-5, 5)
            x2 = random.randint(-5, 5)
            # f(x) = (x - x1)(x - x2) = x² - (x1+x2)x + x1*x2
            b_coef = -(x1 + x2)
            c_coef = x1 * x2
            sign_b = "+" if b_coef >= 0 else "-"
            sign_c = "+" if c_coef >= 0 else "-"
            text = f"Rask funkcijos f(x) = x² {sign_b} {abs(b_coef)}x {sign_c} {abs(c_coef)} nulius."
            if x1 == x2:
                answer = f"x = {x1}"
            else:
                answer = f"x₁ = {min(x1, x2)}, x₂ = {max(x1, x2)}"

        return {"text": text, "answer": answer}

    def _generate_progression_task(
        self, grade_level: int, difficulty: str, num: int
    ) -> dict:
        """Generuoja progresijų uždavinį."""
        prog_type = random.choice(["arithmetic", "geometric"])

        if prog_type == "arithmetic":
            a1 = random.randint(1, 10)
            d = random.randint(1, 5)
            n = random.randint(5, 10)

            task_types = [
                (
                    f"Aritmetinės progresijos pirmasis narys a₁ = {a1}, skirtumas d = {d}. Rask {n}-ąjį narį.",
                    a1 + (n - 1) * d,
                ),
                (
                    f"Aritmetinės progresijos a₁ = {a1}, d = {d}. Rask pirmųjų {n} narių sumą.",
                    n * (2 * a1 + (n - 1) * d) // 2,
                ),
                (
                    f"Aritmetinė progresija: {a1}, {a1+d}, {a1+2*d}, ... Koks yra {n}-asis narys?",
                    a1 + (n - 1) * d,
                ),
            ]
        else:
            a1 = random.randint(1, 5)
            q = random.randint(2, 3)
            n = random.randint(4, 6)

            task_types = [
                (
                    f"Geometrinės progresijos pirmasis narys b₁ = {a1}, vardiklis q = {q}. Rask {n}-ąjį narį.",
                    a1 * (q ** (n - 1)),
                ),
                (
                    f"Geometrinė progresija: {a1}, {a1*q}, {a1*q*q}, ... Koks yra {n}-asis narys?",
                    a1 * (q ** (n - 1)),
                ),
            ]

        text, answer = random.choice(task_types)
        return {"text": text, "answer": answer}

    def _generate_mixed_task(self, grade_level: int, difficulty: str, num: int) -> dict:
        """Generuoja mišrų uždavinį pagal klasę."""
        # Pasirenkame uždavinio tipą pagal klasę
        if grade_level <= 6:
            generators = [
                self._generate_arithmetic_task,
                self._generate_fraction_task,
                self._generate_percent_task,
            ]
        elif grade_level <= 8:
            generators = [
                self._generate_arithmetic_task,
                self._generate_equation_task,
                self._generate_geometry_task,
                self._generate_percent_task,
            ]
        else:
            generators = [
                self._generate_equation_task,
                self._generate_geometry_task,
                self._generate_function_task,
                self._generate_function_zeros_task,
                self._generate_progression_task,
            ]

        generator = random.choice(generators)
        return generator(grade_level, difficulty, num)

    def _generate_trig_task(self, grade_level: int, difficulty: str, num: int) -> dict:
        """Generuoja trigonometrijos uždavinį."""
        angles = [
            (30, "1/2", "√3/2"),
            (45, "√2/2", "√2/2"),
            (60, "√3/2", "1/2"),
            (90, "1", "0"),
            (0, "0", "1"),
        ]
        angle, sin_val, cos_val = random.choice(angles)

        func = random.choice(["sin", "cos"])
        if func == "sin":
            text = f"Rask sin {angle}°"
            answer = sin_val
        else:
            text = f"Rask cos {angle}°"
            answer = cos_val

        return {"text": text, "answer": answer}

    def _generate_log_task(self, grade_level: int, difficulty: str, num: int) -> dict:
        """Generuoja logaritmų uždavinį."""
        bases = [2, 3, 5, 10]
        base = random.choice(bases)

        # Generuojame taip, kad atsakymas būtų sveikas skaičius
        exp = random.randint(1, 4)
        arg = base**exp

        text = f"Rask log₍{base}₎{arg}"
        answer = exp

        return {"text": text, "answer": answer}

    def _generate_derivative_task(
        self, grade_level: int, difficulty: str, num: int
    ) -> dict:
        """Generuoja išvestinių uždavinį."""
        a = random.randint(1, 5)
        n = random.randint(2, 4)

        if difficulty == "easy":
            text = f"Rask funkcijos f(x) = {a}x^{n} išvestinę"
            answer = f"{a * n}x^{n - 1}"
        else:
            b = random.randint(1, 10)
            text = f"Rask funkcijos f(x) = {a}x^{n} + {b}x išvestinę"
            answer = f"{a * n}x^{n - 1} + {b}"

        return {"text": text, "answer": answer}
