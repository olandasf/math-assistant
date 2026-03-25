from typing import List, Dict, Any
from utils.curriculum import Topic, Subtopic

class PromptGeneratorsMixin:
    def _build_curriculum_enhanced_prompt(
        self,
        topic: str,
        grade_level: int,
        task_count: int,
        difficulty: str,
        points_per_task: list,
        include_solutions: bool,
    ) -> str:
        """
        Sukuria AI prompt'ą, praturtintą curriculum.py informacija.

        Args:
            topic: Tema
            grade_level: Klasė
            task_count: Uždavinių kiekis
            difficulty: Sudėtingumas
            points_per_task: Taškai kiekvienam uždaviniui
            include_solutions: Ar įtraukti sprendimus

        Returns:
            Praturtintas prompt'as
        """
        # Gauname informaciją iš curriculum.py
        curriculum_topic = self._get_curriculum_topic_info(topic, grade_level)

        curriculum_context = ""
        if curriculum_topic:
            # Potemės
            subtopic_names = [st.name_lt for st in curriculum_topic.subtopics]
            if subtopic_names:
                curriculum_context += f"\nPOTEMĖS: {', '.join(subtopic_names)}\n"

            # Įgūdžiai
            skills = self._get_skills_for_topic(topic, grade_level)
            if skills:
                curriculum_context += f"VERTINAMI ĮGŪDŽIAI: {', '.join(skills[:10])}\n"

            # Pavyzdžiai
            examples = self._get_examples_for_topic(topic, grade_level, difficulty)
            if examples:
                curriculum_context += f"\nPAVYZDŽIAI IŠ PROGRAMOS:\n"
                for i, ex in enumerate(examples[:5], 1):
                    curriculum_context += f"  {i}. {ex}\n"

            # Dažnos klaidos (naudingos distraktorių generavimui)
            common_errors = self._get_common_errors_for_topic(topic, grade_level)
            if common_errors:
                curriculum_context += (
                    f"\nDAŽNOS MOKINIŲ KLAIDOS (naudok generuojant testų variantus):\n"
                )
                for error in common_errors[:5]:
                    curriculum_context += f"  • {error}\n"

            # Pasiekimų reikalavimai
            level_map = {"easy": "satisfactory", "medium": "basic", "hard": "advanced"}
            requirements = self._get_requirements_for_level(
                topic, grade_level, level_map.get(difficulty, "basic")
            )
            if requirements:
                curriculum_context += f"\nREIKALAVIMAI PAGAL LYGĮ:\n"
                for req in requirements[:5]:
                    curriculum_context += f"  • {req}\n"

        # Standartinis prompt'as + curriculum kontekstas
        difficulty_lt = {
            "easy": "lengvas (patenkinamas lygis)",
            "medium": "vidutinis (pagrindinis lygis)",
            "hard": "sudėtingas (aukštesnysis lygis)",
            "mixed": "mišrus (visi lygiai)",
        }.get(difficulty, "vidutinis")

        difficulty_instructions = ""
        if difficulty == "mixed":
            a_count, b_count = round(task_count * 0.4), round(task_count * 0.4)
            if task_count == 1:
                a_count, b_count = 1, 0
            elif task_count <= 2:
                a_count, b_count = 1, 1
            c_count = task_count - a_count - b_count
            
            difficulty_instructions = f"""
UŽDAVINIŲ SUDĖTINGUMO PASKIRSTYMAS (A/B/C - 40/40/20):
Turi paruošti {task_count} uždavinius tiksliai laikantis šių proporcijų:
• Lygis A (Žinios ir supratimas, lengvi): {a_count} užd.
• Lygis B (Taikymas ir komunikavimas, vidutiniai): {b_count} užd.
• Lygis C (Problemų sprendimas, sunkūs): {c_count} užd.
"""

        names = ", ".join(random.sample(self.NAMES_MALE + self.NAMES_FEMALE, 6))

        return f"""Sukurk {task_count} SKIRTINGUS matematinius uždavinius kontroliniam darbui.

TEMA: {topic.replace('_', ' ')}
KLASĖ: {grade_level}
SUDĖTINGUMAS: {difficulty_lt}
{curriculum_context}
{difficulty_instructions}
⚠️ LABAI SVARBU - ĮVAIROVĖ:
Kiekvienas uždavinys PRIVALO būti KITOKS! Negalima kartoti to paties tipo.

PRIVALOMI REIKALAVIMAI:
1. Bent {max(1, task_count // 2)} uždaviniai turi būti TEKSTINIAI su realiu kontekstu
2. Naudok lietuviškus vardus: {names}
3. Kontekstai: parduotuvė, mokykla, sportas, kelionės, maistas, pinigai, laikas
4. Kiekvienas uždavinys - SKIRTINGAS tipas ir kontekstas
5. Skaičiai turi būti "gražūs" (dalūs, apvalūs rezultatai)
6. Atsakymai - supaprastinti (trupmenos sutrauktos, lygtys išspręstos)

TEKSTO FORMATAVIMAS (KRITIŠKAI SVARBU!):
- Rašyk PAPRASTĄ tekstą su normaliais tarpais tarp žodžių
- Trupmenas rašyk paprastai: 2/3, 1 1/2, 3/4 (NE LaTeX formatu!)
- Mišrias trupmenas rašyk: 2 1/3 (skaičius, tarpas, trupmena)
- Matematinius veiksmus rašyk simboliais: ×, +, -, ÷, =
- NENAUDOK LaTeX sintaksės (\\frac, \\cdot, $...$ ir pan.)
- Tekstas turi būti skaitomas kaip įprasta lietuviška kalba

TAŠKŲ PASKIRSTYMAS: {points_per_task}

{"SPRENDIMO ŽINGSNIAI: Kiekvienam uždaviniui pateik 2-4 aiškius sprendimo žingsnius lietuvių kalba." if include_solutions else ""}

ATSAKYMO FORMATAS (tik JSON, be jokio kito teksto):
{{
  "tasks": [
    {{
      "number": 1,
      "text": "Pilnas uždavinio tekstas lietuviškai (su kontekstu jei tekstinis)",
      "answer": "Teisingas atsakymas",
      "points": {points_per_task[0] if points_per_task else 2},
      "difficulty": "easy|medium|hard",
      "solution_steps": ["Žingsnis 1: ...", "Žingsnis 2: ...", "Atsakymas: ..."],
      "topic_detail": "konkreti potemė"
    }}
  ]
}}"""

    def _build_curriculum_context_prompt(
        self,
        topic: str,
        grade_level: int,
        task_count: int,
        difficulty: str,
        points_per_task: list,
        include_solutions: bool,
        curriculum_context: str,
    ) -> str:
        """
        Sukuria AI prompt'ą naudojant programos kontekstą iš JSON failų.

        curriculum_context jau turi struktūrizuotą informaciją apie temas,
        potemes ir sunkumo lygių aprašymus.
        """
        difficulty_lt = {
            "easy": "lengvas (patenkinamas lygis)",
            "medium": "vidutinis (pagrindinis lygis)",
            "hard": "sudėtingas (aukštesnysis lygis)",
            "mixed": "mišrus (visi lygiai)",
            "vbe": "VBE lygis (brandos egzaminas)",
        }.get(difficulty, "vidutinis")

        difficulty_instructions = ""
        if difficulty == "mixed":
            a_count, b_count = round(task_count * 0.4), round(task_count * 0.4)
            if task_count == 1:
                a_count, b_count = 1, 0
            elif task_count <= 2:
                a_count, b_count = 1, 1
            c_count = task_count - a_count - b_count
            
            difficulty_instructions = f"""
UŽDAVINIŲ SUDĖTINGUMO PASKIRSTYMAS (A/B/C - 40/40/20):
Turi paruošti {task_count} uždavinius tiksliai laikantis šių proporcijų:
• Lygis A (Žinios ir supratimas, lengvi): {a_count} užd.
• Lygis B (Taikymas ir komunikavimas, vidutiniai): {b_count} užd.
• Lygis C (Problemų sprendimas, sunkūs): {c_count} užd.
"""

        names = ", ".join(random.sample(self.NAMES_MALE + self.NAMES_FEMALE, 6))

        points_info = ", ".join(
            f"Nr.{i+1}: {p} tšk." for i, p in enumerate(points_per_task)
        )

        solutions_instruction = ""
        if include_solutions:
            solutions_instruction = """
"solution_steps": ["žingsnis 1", "žingsnis 2", ...] - DETALŪS sprendimo žingsniai"""

        return f"""Sukurk {task_count} SKIRTINGUS matematinius uždavinius kontroliniam darbui.

TEMA: {topic.replace('_', ' ')}
KLASĖ: {grade_level}
SUDĖTINGUMAS: {difficulty_lt}
{difficulty_instructions}
=== PROGRAMOS KONTEKSTAS (IŠ OFICIALIOS MATEMATIKOS PROGRAMOS) ===
{curriculum_context}
=== PROGRAMOS KONTEKSTAS PABAIGA ===

⚠️ LABAI SVARBU - PROGRAMOS KONTEKSTAS:
Aukščiau pateiktas programos kontekstas nurodo TIKSLIAI kokio tipo ir sudėtingumo
uždavinius reikia generuoti. PRIVALAI vadovautis sunkumo lygio aprašymais!

⚠️ LABAI SVARBU - ĮVAIROVĖ:
Kiekvienas uždavinys PRIVALO būti KITOKS! Negalima kartoti to paties tipo.

PRIVALOMI REIKALAVIMAI:
1. Bent {max(1, task_count // 2)} uždaviniai turi būti TEKSTINIAI su realiu kontekstu
2. Naudok lietuviškus vardus: {names}
3. Kontekstai: parduotuvė, mokykla, sportas, kelionės, maistas, pinigai, laikas
4. Kiekvienas uždavinys - SKIRTINGAS tipas ir kontekstas
5. Skaičiai turi būti "gražūs" (dalūs, apvalūs rezultatai)
6. Atsakymai - supaprastinti (trupmenos sutrauktos, lygtys išspręstos)

TEKSTO FORMATAVIMAS (KRITIŠKAI SVARBU!):
- Naudok \\\\( ir \\\\) inlinems formulėms
- Naudok \\\\[ ir \\\\] blokų formulėms
- Trupmenoms: \\\\frac{{a}}{{b}}
- Laipsniams: x^{{2}}
- Šaknims: \\\\sqrt{{x}}
- NEUZMIRŠK: visos matematinės išraiškos PRIVALO būti LaTeX!
- PAVYZDYS: "Jonas nupirko \\\\( 3 \\\\frac{{1}}{{4}} \\\\) kg obuolių"
- BLOGAS pavyzdys: "Jonas nupirko 3 1/4 kg obuolių"

TAŠKŲ PASKIRSTYMAS: {points_info}

ATSAKYMO FORMATAS (JSON):
{{
  "tasks": [
    {{
      "number": 1,
      "text": "Uždavinio tekstas su \\\\( LaTeX \\\\) formulėmis",
      "answer": "atsakymas",
      "answer_latex": "\\\\frac{{1}}{{2}}",{solutions_instruction}
      "points": {points_per_task[0] if points_per_task else 2},
      "difficulty": "{difficulty}",
      "topic_detail": "konkreti potemė iš programos"
    }}
  ]
}}"""

    def _build_standard_prompt(
        self,
        topic: str,
        grade_level: int,
        task_count: int,
        difficulty: str,
        points_per_task: list,
        include_solutions: bool,
    ) -> str:
        """Standartinis prompt'as 5-9 klasėms."""

        difficulty_lt = {
            "easy": "lengvas (patenkinamas lygis)",
            "medium": "vidutinis (pagrindinis lygis)",
            "hard": "sudėtingas (aukštesnysis lygis)",
            "mixed": "mišrus (visi lygiai)",
        }.get(difficulty, "vidutinis")

        difficulty_instructions = ""
        if difficulty == "mixed":
            a_count, b_count = round(task_count * 0.4), round(task_count * 0.4)
            if task_count == 1:
                a_count, b_count = 1, 0
            elif task_count <= 2:
                a_count, b_count = 1, 1
            c_count = task_count - a_count - b_count
            
            difficulty_instructions = f"""
UŽDAVINIŲ SUDĖTINGUMO PASKIRSTYMAS (A/B/C - 40/40/20):
Turi paruošti {task_count} uždavinius tiksliai laikantis šių proporcijų:
• Lygis A (Žinios ir supratimas, lengvi): {a_count} užd.
• Lygis B (Taikymas ir komunikavimas, vidutiniai): {b_count} užd.
• Lygis C (Problemų sprendimas, sunkūs): {c_count} užd.
"""

        # Konkretūs uždavinių tipai pagal temą
        task_types = self._get_task_types_for_topic(topic, grade_level)
        names = ", ".join(random.sample(self.NAMES_MALE + self.NAMES_FEMALE, 6))

        return f"""Sukurk {task_count} SKIRTINGUS matematinius uždavinius kontroliniam darbui.

TEMA: {topic.replace('_', ' ')}
KLASĖ: {grade_level}
SUDĖTINGUMAS: {difficulty_lt}
{difficulty_instructions}

⚠️ LABAI SVARBU - ĮVAIROVĖ:
Kiekvienas uždavinys PRIVALO būti KITOKS! Negalima kartoti to paties tipo.
Maišyk šiuos uždavinių tipus:

{task_types}

PRIVALOMI REIKALAVIMAI:
1. Bent {max(1, task_count // 2)} uždaviniai turi būti TEKSTINIAI su realiu kontekstu
2. Naudok lietuviškus vardus: {names}
3. Kontekstai: parduotuvė, mokykla, sportas, kelionės, maistas, pinigai, laikas
4. Kiekvienas uždavinys - SKIRTINGAS tipas ir kontekstas
5. Skaičiai turi būti "gražūs" (dalūs, apvalūs rezultatai)
6. Atsakymai - supaprastinti (trupmenos sutrauktos, lygtys išspręstos)

TEKSTO FORMATAVIMAS (KRITIŠKAI SVARBU!):
- Rašyk PAPRASTĄ tekstą su normaliais tarpais tarp žodžių
- Trupmenas rašyk paprastai: 2/3, 1 1/2, 3/4 (NE LaTeX formatu!)
- Matematinius veiksmus rašyk simboliais: ×, +, -, ÷, =
- NENAUDOK LaTeX sintaksės (\\frac, \\cdot, $...$ ir pan.)
- Tekstas turi būti skaitomas kaip įprasta lietuviška kalba

TAŠKŲ PASKIRSTYMAS: {points_per_task}

{"SPRENDIMO ŽINGSNIAI: Kiekvienam uždaviniui pateik 2-4 aiškius sprendimo žingsnius lietuvių kalba." if include_solutions else ""}

ATSAKYMO FORMATAS (tik JSON, be jokio kito teksto):
{{
  "tasks": [
    {{
      "number": 1,
      "text": "Pilnas uždavinio tekstas lietuviškai (su kontekstu jei tekstinis)",
      "answer": "Teisingas atsakymas",
      "points": {points_per_task[0] if points_per_task else 2},
      "difficulty": "easy|medium|hard",
      "solution_steps": ["Žingsnis 1: ...", "Žingsnis 2: ...", "Atsakymas: ..."],
      "topic_detail": "konkreti potemė"
    }}
  ]
}}"""

    def _get_task_types_for_topic(self, topic: str, grade_level: int) -> str:
        """Grąžina konkrečius uždavinių tipus pagal temą."""
        topic_lower = topic.lower()

        if "lygt" in topic_lower:
            if grade_level >= 9 or "kvadrat" in topic_lower:
                return """
UŽDAVINIŲ TIPAI (naudok visus!):
1. TEKSTINIS: "Jonas turi x metų. Po 5 metų jo amžius bus dvigubai didesnis nei sesers. Kiek metų Jonui?"
2. GEOMETRINIS: "Stačiakampio plotas 48 cm². Ilgis 2 cm didesnis už plotį. Rask matmenis."
3. JUDĖJIMO: "Du dviratininkai išvyko vienas priešais kitą. Greičiai 15 km/h ir 20 km/h. Po kiek laiko susitiks, jei atstumas 70 km?"
4. DARBO: "Petras darbą atlieka per 6 val., Ona per 4 val. Per kiek laiko atliks kartu?"
5. MIŠINIO: "Sumaišius 30% ir 50% tirpalus gauta 40% tirpalo. Kiek kiekvieno tirpalo?"
6. TIESIOGINĖ LYGTIS: "Išspręsk: 3x² - 12x + 9 = 0" (tik 1-2 tokie!)"""
            else:
                return """
UŽDAVINIŲ TIPAI (naudok visus!):
1. TEKSTINIS: "Petras turėjo keletą obuolių. Davė draugui 5, liko 12. Kiek turėjo?"
2. PIRKIMO: "Sąsiuvinis kainuoja x eurų. 5 sąsiuviniai ir 3 € trintukas kainuoja 13 €. Kiek kainuoja sąsiuvinis?"
3. AMŽIAUS: "Tėvo amžius 4 kartus didesnis už sūnaus. Po 10 metų bus tik 2 kartus didesnis. Kiek metų sūnui?"
4. GEOMETRINIS: "Stačiakampio perimetras 28 cm. Ilgis 4 cm didesnis už plotį. Rask matmenis."
5. GREIČIO: "Dviratis važiuoja 15 km/h. Per kiek laiko nuvažiuos 45 km?"
6. TIESIOGINĖ: "Išspręsk: 2x + 7 = 15" (tik 1 toks!)"""

        elif "trupmen" in topic_lower:
            return """
UŽDAVINIŲ TIPAI (naudok visus!):
1. DALIES RADIMAS: "Klasėje 24 mokiniai. 3/4 jų lanko būrelį. Kiek mokinių lanko būrelį?"
2. RECEPTAS: "Receptui reikia 2/3 kg miltų. Kiek miltų reikės 3 porcijoms?"
3. KELIONĖ: "Turistai nuėjo 2/5 kelio. Liko 12 km. Koks viso kelio ilgis?"
4. LAIKAS: "Filmas trunka 1 1/2 valandos. Praėjo 2/3 filmo. Kiek minučių liko?"
5. PINIGAI: "Ona išleido 1/4 pinigų knygai ir 1/3 saldainiams. Kokią dalį išleido iš viso?"
6. SKAIČIAVIMAS: "Apskaičiuok: 2/3 + 1/4 - 1/6" (tik 1-2 tokie!)"""

        elif "procent" in topic_lower:
            return """
UŽDAVINIŲ TIPAI (naudok visus!):
1. NUOLAIDA: "Prekė kainavo 80 €. Nuolaida 25%. Kokia nauja kaina?"
2. PALŪKANOS: "Į banką įdėta 500 €. Metinės palūkanos 4%. Kiek bus po metų?"
3. PADIDĖJIMAS: "Kaina pakilo 15%. Dabar prekė kainuoja 46 €. Kokia buvo pradinė kaina?"
4. SUDĖTIS: "Klasėje 30 mokinių. 40% berniukų, 60% mergaičių. Kiek berniukų?"
5. MIŠINYS: "Tirpale 200 g druskos, tai sudaro 8% tirpalo. Kiek sveria visas tirpalas?"
6. PALYGINIMAS: "Pirmą dieną pardavė 120 bilietų, antrą - 150. Kiek procentų daugiau antrą dieną?"""

        elif "funkcij" in topic_lower:
            return """
UŽDAVINIŲ TIPAI (naudok visus!):
1. REIKŠMĖS RADIMAS: "Duota f(x) = 2x² - 3x + 1. Rask f(2) ir f(-1)."
2. APIBRĖŽIMO SRITIS: "Rask funkcijos f(x) = √(x-3) apibrėžimo sritį."
3. NULIAI: "Rask funkcijos f(x) = x² - 5x + 6 nulius."
4. TEKSTINIS: "Taksi kaina: 2€ + 0.5€/km. Užrašyk funkciją ir rask kainą už 10 km."
5. GRAFIKAS: "Funkcijos grafikas eina per taškus (0;3) ir (2;7). Rask tiesinės funkcijos formulę."
6. MONOTONINUMAS: "Nustatyk, kuriuose intervaluose funkcija f(x) = x² - 4x didėja, kuriuose mažėja."
7. EKSTREMUMAI: "Rask funkcijos f(x) = -x² + 6x - 5 didžiausią reikšmę." """

        elif "trigonometr" in topic_lower:
            return """
UŽDAVINIŲ TIPAI (naudok visus!):
1. REIKŠMĖS: "Apskaičiuok: sin 60° + cos 30° - tg 45°"
2. TRIKAMPIS: "Stačiakampio trikampio įžambinė 10 cm, vienas kampas 30°. Rask statinių ilgius."
3. TAPATYBĖ: "Įrodyk, kad sin²α + cos²α = 1 naudojant vienetinį apskritimą."
4. LYGTIS: "Išspręsk: 2sin(x) = 1, kai x ∈ [0°; 360°]"
5. AUKŠTIS: "Nuo 50 m aukščio bokšto matymo kampas iki objekto yra 30°. Koks atstumas iki objekto?"
6. PLOTAS: "Trikampio dvi kraštinės 8 cm ir 6 cm, kampas tarp jų 60°. Rask plotą."
7. SUPAPRASTINIMAS: "Supaprastink: (sin α / cos α) · cos α" """

        elif (
            "geometr" in topic_lower
            or "trikamp" in topic_lower
            or "keturk" in topic_lower
        ):
            return """
UŽDAVINIŲ TIPAI (naudok visus!):
1. PLOTAS: "Sodo sklypas stačiakampio formos: 25 m × 40 m. Koks jo plotas?"
2. PERIMETRAS: "Trikampio kraštinės 7 cm, 8 cm ir 9 cm. Rask perimetrą."
3. PITAGORAS: "Stačiakampio trikampio statiniai 6 cm ir 8 cm. Rask įžambinę."
4. APSKRITIMAS: "Apskritimo spindulys 7 cm. Rask plotą ir ilgį (π ≈ 3.14)."
5. SUDĖTINĖ FIGŪRA: "Kambario grindys: stačiakampis 5×4 m su išpjova 1×1 m kampe. Koks plotas?"
6. ERDVINĖ: "Stačiakampio gretasienio matmenys 3×4×5 cm. Rask tūrį ir paviršiaus plotą."
7. PANAŠUMAS: "Du panašūs trikampiai. Pirmojo kraštinė 6 cm, atitinkama antrojo - 9 cm. Koks panašumo koeficientas?" """

        elif "progresij" in topic_lower:
            return """
UŽDAVINIŲ TIPAI (naudok visus!):
1. N-TASIS NARYS: "Aritmetinės progresijos a₁=3, d=4. Rask a₁₀."
2. SUMA: "Rask aritmetinės progresijos 2, 5, 8, ... pirmųjų 20 narių sumą."
3. TEKSTINIS: "Pirmą dieną Petras nubėgo 1 km, kiekvieną kitą - 0.5 km daugiau. Kiek nubėgo per 10 dienų?"
4. GEOMETRINĖ: "Geometrinės progresijos b₁=2, q=3. Rask b₅."
5. PALŪKANOS: "Įdėta 1000 €, kasmet pridedama 10%. Kiek bus po 3 metų?"
6. RADIMAS: "Aritmetinės progresijos a₃=10, a₇=22. Rask a₁ ir d."
7. BEGALINĖ SUMA: "Rask begalinės geometrinės progresijos 1, 1/2, 1/4, ... sumą." """

        elif "logaritm" in topic_lower:
            return """
UŽDAVINIŲ TIPAI (naudok visus!):
1. SKAIČIAVIMAS: "Apskaičiuok: log₂ 8 + log₃ 27"
2. LYGTIS: "Išspręsk: log₂(x+3) = 4"
3. SAVYBĖS: "Supaprastink: log₂ 8 + log₂ 4 - log₂ 2"
4. TEKSTINIS: "Bakterijų skaičius dvigubėja kas valandą. Po kiek valandų bus 1024 kartus daugiau?"
5. RODIKLINĖ: "Išspręsk: 2ˣ = 32"
6. SUDĖTINGESNĖ: "Išspręsk: log₃(x²-1) = 2"
7. PALYGINIMAS: "Kuris didesnis: log₂ 10 ar log₃ 20?" """

        else:
            # Bendras mišrus
            return f"""
UŽDAVINIŲ TIPAI (maišyk įvairius!):
1. TEKSTINIS SU KONTEKSTU: Parduotuvė, mokykla, kelionė, sportas
2. SKAIČIAVIMO: Tiesioginis matematinis veiksmas
3. GEOMETRINIS: Plotas, perimetras, tūris
4. LOGINIS: Palyginimas, įrodymas
5. PRAKTINIS: Pinigai, laikas, greitis, atstumas

Naudok lietuviškus vardus ir realias situacijas!
Klasė: {grade_level}, todėl pritaikyk sudėtingumą."""

    def _build_vbe_style_prompt(
        self,
        topic: str,
        grade_level: int,
        task_count: int,
        difficulty: str,
        points_per_task: list,
        include_solutions: bool,
    ) -> str:
        """VBE stiliaus prompt'as 10-12 klasėms - sudėtingesni uždaviniai."""

        difficulty_lt = {
            "medium": "vidutinis",
            "hard": "sudėtingas",
            "vbe": "VBE lygis (brandos egzaminas)",
            "mixed": "mišrus (visi lygiai)",
        }.get(difficulty, "vidutinis")

        difficulty_instructions = ""
        if difficulty == "mixed":
            a_count, b_count = round(task_count * 0.4), round(task_count * 0.4)
            if task_count == 1:
                a_count, b_count = 1, 0
            elif task_count <= 2:
                a_count, b_count = 1, 1
            c_count = task_count - a_count - b_count
            
            difficulty_instructions = f"""
UŽDAVINIŲ SUDĖTINGUMO PASKIRSTYMAS (A/B/C - 40/40/20):
Turi paruošti {task_count} uždavinius tiksliai laikantis šių proporcijų:
• Lygis A (Žinios ir supratimas, lengvi): {a_count} užd.
• Lygis B (Taikymas ir komunikavimas, vidutiniai): {b_count} užd.
• Lygis C (Problemų sprendimas, sunkūs): {c_count} užd.
"""

        names = ", ".join(random.sample(self.NAMES_MALE + self.NAMES_FEMALE, 5))
        task_types = self._get_task_types_for_topic(topic, grade_level)

        return f"""Sukurk {task_count} SKIRTINGUS VBE (valstybinio brandos egzamino) lygio matematinius uždavinius.

TEMA: {topic.replace('_', ' ')}
KLASĖ: {grade_level}
SUDĖTINGUMAS: {difficulty_lt}
{difficulty_instructions}

⚠️ KRITIŠKAI SVARBU - ĮVAIROVĖ:
Kiekvienas uždavinys PRIVALO būti VISIŠKAI KITOKS!
DRAUDŽIAMA: visi uždaviniai tipo "Išspręsk lygtį: ..."
PRIVALOMA: maišyti tekstinius, grafinius, įrodymo, skaičiavimo uždavinius.

{task_types}

VBE UŽDAVINIŲ FORMATAI (naudok įvairius!):
1. **Daugiadaliai** su a), b), c):
   "Duota funkcija f(x) = x² - 4x + 3.
    a) Raskite funkcijos šaknis.
    b) Nustatykite funkcijos reikšmių sritį.
    c) Nubraižykite funkcijos grafiką."

2. **Tekstiniai su kontekstu**:
   "{random.choice(self.NAMES_MALE)} stato tvorą. Tvoros ilgis 20 m. Vienas stulpas kas 2 m. Kiek stulpų reikia?"

3. **Įrodymo/pagrindimo**:
   "Įrodykite, kad skaičius n² + n visada dalus iš 2."

4. **Optimizavimo**:
   "Stačiakampio perimetras 40 cm. Kokių matmenų stačiakampio plotas didžiausias?"

TAŠKŲ PASKIRSTYMAS: {points_per_task}

PRIVALOMI REIKALAVIMAI:
1. Bent {max(1, task_count // 2)} uždaviniai - TEKSTINIAI arba DAUGIADALIAI
2. Naudok vardus: {names}
3. Realūs kontekstai: ekonomika, fizika, biologija, kasdienybė
4. Kiekvienas uždavinys - SKIRTINGAS tipas
5. Atsakymuose - VISŲ dalių atsakymai (jei daugiadaliai)

{"SPRENDIMO ŽINGSNIAI: Detalūs, 3-5 žingsniai kiekvienam uždaviniui." if include_solutions else ""}

ATSAKYMO FORMATAS (tik JSON):
{{
  "tasks": [
    {{
      "number": 1,
      "text": "Pilnas uždavinio tekstas (su a), b), c) jei daugiadaliai)",
      "answer": "Visi atsakymai: a) ...; b) ...; c) ...",
      "points": {points_per_task[0] if points_per_task else 4},
      "difficulty": "medium|hard|vbe",
      "solution_steps": ["Žingsnis 1", "Žingsnis 2", "Žingsnis 3"],
      "topic_detail": "konkreti potemė"
    }}
  ]
}}"""
