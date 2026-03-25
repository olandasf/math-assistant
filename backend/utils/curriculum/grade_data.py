"""
Konkretūs ugdymo programos duomenys klasėms (5-10 kl.).
"""
from typing import Dict
from utils.curriculum.models import (
    Topic, Subtopic, ContentArea, Competency, GradeCurriculum
)

# =============================================================================
# 5 KLASĖ - TURINIO SRITYS
# =============================================================================
# PASTABA: Pagal NŠA Bendrąją programą (5-6 kl. koncentras, pirmieji metai)
# SVARBU: 5 klasėje NENAUDOTI neigiamų skaičių ir trupmenų su skirtingais vardikliais!

GRADE_5_TOPICS = [
    # --- SKAIČIAI IR SKAIČIAVIMAI ---
    Topic(
        id="naturalieji_skaiciai_5",
        name_lt="Natūralieji skaičiai ir veiksmai",
        name_en="Natural Numbers and Operations",
        content_area=ContentArea.NUMBERS,
        grade_introduced=5,
        grade_mastery=5,
        grades_available=[5, 6, 7, 8],
        description="Veiksmai su natūraliaisiais skaičiais (iki milijono), apvalinimas",
        importance=5,
        prerequisites=[],
        subtopics=[
            Subtopic(
                id="natural_ops_5",
                name_lt="Veiksmai su natūraliaisiais skaičiais",
                name_en="Operations with natural numbers",
                description="Sudėtis, atimtis, daugyba, dalyba su natūraliaisiais skaičiais",
                satisfactory_requirements=[
                    "Sudėtis ir atimtis stulpeliu (be perėjimo per skyrių)",
                    "Skaito ir rašo skaičius iki 1000",
                ],
                basic_requirements=[
                    "Daugyba ir dalyba (iš vienaženklio/dviženklio)",
                    "Veiksmų tvarka su skliaustais",
                    "Sudėtis ir atimtis su perėjimu per skyrių",
                ],
                advanced_requirements=[
                    "Tekstiniai uždaviniai su keliais veiksmais",
                    "Lygties sudarymas pagal tekstą",
                    "Reiškiniai su skliaustais ir 3+ nariais",
                ],
                example_easy="345 + 120 = ?",
                example_medium="123 × 3 = ? arba 45 × 23 = ?",
                example_hard="Autobuse buvo 45, išlipo 12, įlipo 5. Kiek liko?",
                skills=["sudėtis", "atimtis", "daugyba", "dalyba", "veiksmų_tvarka"],
                common_errors=[
                    "Veiksmų tvarkos klaidos (pvz., sudėtis prieš daugybą)",
                    "Skliaustų ignoravimas",
                    "Perėjimo per dešimtis klaidos (skolinimasis)",
                ],
                distractor_logic="Generuoti atsakymus su veiksmų tvarkos klaidomis",
                competencies=[Competency.COGNITIVE],
            ),
            Subtopic(
                id="rounding_5",
                name_lt="Apvalinimas ir dideli skaičiai",
                name_en="Rounding and large numbers",
                description="Skaičių iki milijono skaitymas, rašymas, apvalinimas",
                satisfactory_requirements=[
                    "Skaito ir rašo skaičius iki milijono",
                    "Nustato skaitmens poziciją skaičiuje",
                ],
                basic_requirements=[
                    "Apvalina iki nurodyto skyriaus (dešimčių, šimtų)",
                    "Lygina skaičius naudodamas >, <, = ženklus",
                ],
                advanced_requirements=[
                    "Įvertina sumą/skirtumą 'iš akies' (apytikslis skaičiavimas)",
                    "Sprendžia uždavinius su dideliais skaičiais",
                ],
                example_easy="Parašyk skaičių: trys tūkstančiai penki šimtai",
                example_medium="Apvalinti 3 456 iki šimtų",
                example_hard="Įvertink: 498 + 312 ≈ ?",
                skills=["skaitymas", "rašymas", "apvalinimas", "lyginimas"],
                common_errors=[
                    "Apvalinimo kryptis (kada didinti, kada mažinti)",
                    "Skyriaus pozicijos klaidos",
                ],
                distractor_logic="Pateikti neteisingai apvalintą atsakymą",
                competencies=[Competency.COGNITIVE],
            ),
        ],
    ),
    # --- DEŠIMTAINĖS TRUPMENOS (Pagrindinė 5 kl. tema) ---
    Topic(
        id="desimtaines_trupmenos_5",
        name_lt="Dešimtainės trupmenos",
        name_en="Decimal Fractions",
        content_area=ContentArea.NUMBERS,
        grade_introduced=5,
        grade_mastery=6,
        grades_available=[5, 6, 7, 8],
        description="Dešimtainių trupmenų skaitymas, lyginimas ir veiksmai (svarbiausia 5 kl. tema)",
        importance=5,
        prerequisites=["naturalieji_skaiciai_5"],
        subtopics=[
            Subtopic(
                id="decimal_structure_5",
                name_lt="Dešimtainių trupmenų skaitymas ir lyginimas",
                name_en="Reading and comparing decimals",
                description="Dešimtainių trupmenų samprata ir palyginimas",
                satisfactory_requirements=[
                    "Palyginti dvi trupmenas (pvz. 2,5 ir 2,05)",
                    "Skaito ir rašo dešimtaines trupmenas",
                ],
                basic_requirements=[
                    "Surikiuoti trupmenas didėjimo tvarka",
                    "Supranta dešimtainės trupmenos vietą skaičių tiesėje",
                ],
                advanced_requirements=[
                    "Verčia paprastąsias trupmenas (1/2, 1/4, 1/5) dešimtainėmis",
                ],
                example_easy="Palygink: 2,5 ir 2,05",
                example_medium="Surikiuok: 3,5; 3,15; 3,51",
                example_hard="Paversk 3/4 dešimtaine trupmena",
                skills=["dešimtainės_skaitymas", "dešimtainės_lyginimas"],
                common_errors=[
                    "2,5 ir 2,05 painiojimas (mano, kad 2,05 > 2,5)",
                    "Skaitmenų skaičiaus po kablelio ignoravimas",
                ],
                distractor_logic="Pateikti atsakymą ignoruojant nulius",
                competencies=[Competency.COGNITIVE],
            ),
            Subtopic(
                id="decimal_ops_5",
                name_lt="Veiksmai su dešimtainėmis trupmenomis",
                name_en="Decimal operations",
                description="Sudėtis, atimtis, daugyba ir dalyba su dešimtainėmis",
                satisfactory_requirements=[
                    "Sudėtis ir atimtis (kablelis po kableliu)",
                    "Sudėtis, kai skaitmenų skaičius po kablelio vienodas",
                ],
                basic_requirements=[
                    "Daugyba ir dalyba iš natūraliojo skaičiaus",
                    "Atimtis iš sveikojo skaičiaus (nulių prirašymas)",
                ],
                advanced_requirements=[
                    "Dalyba iš dešimtainės trupmenos",
                    "Tekstiniai uždaviniai (pinigai, svoris)",
                    "Daugyba iš dešimtainės trupmenos",
                ],
                example_easy="2,5 + 1,3 = ?",
                example_medium="10 - 2,45 = ?",
                example_hard="1,5 × 0,4 = ?",
                skills=[
                    "dešimtainių_sudėtis",
                    "dešimtainių_atimtis",
                    "dešimtainių_daugyba",
                ],
                common_errors=[
                    "Kablelio pozicijos klaida",
                    "Nulių prirašymo pamiršimas",
                ],
                distractor_logic="Pateikti atsakymą su neteisingai padėtu kableliu",
                competencies=[Competency.COGNITIVE],
            ),
        ],
    ),
    # --- PAPRASTOSIOS TRUPMENOS (Įvadas - TIK SU VIENODAIS VARDIKLIAIS!) ---
    Topic(
        id="paprastosios_trupmenos_5",
        name_lt="Paprastosios trupmenos (Įvadas)",
        name_en="Introduction to Fractions",
        content_area=ContentArea.NUMBERS,
        grade_introduced=5,
        grade_mastery=6,
        grades_available=[5, 6, 7, 8],
        description="Trupmenos supratimas, veiksmai TIK su vienodais vardikliais",
        importance=4,
        prerequisites=["naturalieji_skaiciai_5"],
        subtopics=[
            Subtopic(
                id="fraction_concept_5",
                name_lt="Trupmenos supratimas ir vaizdavimas",
                name_en="Understanding fractions",
                description="Kas yra trupmena, skaitiklis, vardiklis, vaizdavimas",
                satisfactory_requirements=[
                    "Nuspalvinti dalį figūros pagal trupmeną",
                    "Supranta trupmenos prasmę kaip sveikojo dalį",
                ],
                basic_requirements=[
                    "Mišrieji skaičiai ir netaisyklingosios trupmenos",
                    "Užrašo trupmeną pagal paveikslą",
                ],
                advanced_requirements=[
                    "Verčia tarp paprastųjų ir mišriųjų trupmenų",
                    "Randa dalį nuo skaičiaus",
                ],
                example_easy="Nuspalvink 2/4 apskritimo",
                example_medium="Paversk 7/4 mišriąja trupmena",
                example_hard="Rask 1/4 nuo 20",
                skills=["trupmenos_samprata", "vaizdavimas", "vertimas"],
                common_errors=[
                    "Skaitiklio ir vardiklio sumaišymas",
                    "Mišriosios trupmenos vertimo klaidos",
                ],
                distractor_logic="Sukeisti skaitiklį ir vardiklį",
                competencies=[Competency.COGNITIVE],
            ),
            Subtopic(
                id="fraction_same_denom_5",
                name_lt="Veiksmai su vienodais vardikliais",
                name_en="Operations with same denominator",
                description="Sudėtis ir atimtis TIK kai vardikliai vienodi",
                satisfactory_requirements=[
                    "Sudėtis/Atimtis kai vardikliai vienodi (be sveikųjų)",
                    "2/5 + 1/5 = ?",
                ],
                basic_requirements=[
                    "Mišriųjų skaičių sudėtis (vienodi vardikliai)",
                    "Supaprastina rezultatą",
                ],
                advanced_requirements=[
                    "Tekstinis uždavinys: 'Suvalgė 2/7 torto, kiek liko?'",
                    "Daugiaveiksmiai uždaviniai su vienodais vardikliais",
                ],
                example_easy="2/5 + 1/5 = ?",
                example_medium="1 2/7 + 3/7 = ?",
                example_hard="Petras suvalgė 2/7 pyrago, o Jonas 3/7. Kiek pyrago liko?",
                skills=["trupmenų_sudėtis", "trupmenų_atimtis"],
                common_errors=[
                    "Vardiklių sudėjimas (pvz., 2/5 + 1/5 = 3/10)",
                    "Rezultato nesupaprastinimas",
                ],
                distractor_logic="Pateikti atsakymą su sudėtais vardikliais",
                competencies=[Competency.COGNITIVE],
            ),
        ],
    ),
    # --- GEOMETRIJOS PRADMENYS ---
    Topic(
        id="geometrija_basic_5",
        name_lt="Geometrijos pradmenys",
        name_en="Geometry Basics",
        content_area=ContentArea.GEOMETRY,
        grade_introduced=5,
        grade_mastery=5,
        grades_available=[5, 6, 7, 8],
        description="Kampai, stačiakampio plotas ir perimetras",
        importance=5,
        prerequisites=["naturalieji_skaiciai_5"],
        subtopics=[
            Subtopic(
                id="angles_5",
                name_lt="Kampai ir jų matavimas",
                name_en="Angles and measurement",
                description="Kampų rūšys ir matavimas matlankiu",
                satisfactory_requirements=[
                    "Atpažinti kampo rūšį (status, smailus, bukas)",
                    "Matuoja kampus matlankiu",
                ],
                basic_requirements=[
                    "Išmatuoti kampą matlankiu (tikslumas 5°)",
                    "Braižo nurodytą kampą",
                ],
                advanced_requirements=[
                    "Apskaičiuoti kampą be matavimo (gretutiniai, kryžminiai)",
                    "Žino, kad ištiestinis kampas = 180°",
                ],
                example_easy="Kokio laipsnio yra status kampas?",
                example_medium="Nubraižyk 45° kampą",
                example_hard="Du kampai sudaro ištiestinį kampą. Vienas jų 35°. Koks kitas?",
                skills=["kampų_matavimas", "kampų_rūšys", "matlankis"],
                common_errors=[
                    "Kampų rūšių painiojimas",
                    "Matlankio skaitymo klaidos",
                ],
                distractor_logic="Pateikti papildomą kampą vietoj gretutinio",
                competencies=[Competency.COGNITIVE],
            ),
            Subtopic(
                id="perimeter_area_5",
                name_lt="Stačiakampio plotas ir perimetras",
                name_en="Rectangle area and perimeter",
                description="Formulės P=2(a+b), S=a×b (TIK sveiki skaičiai)",
                satisfactory_requirements=[
                    "Pagal formulę P=2(a+b), S=a×b (sveiki skaičiai)",
                    "Apskaičiuoja plotą ir perimetrą",
                ],
                basic_requirements=[
                    "Atvirkštinis: duotas plotas, rasti kraštinę",
                    "Kvadrato P=4a, S=a²",
                ],
                advanced_requirements=[
                    "Sudėtinės figūros plotas (padalijant į stačiakampius)",
                    "Tekstiniai uždaviniai su perimetru/plotu",
                ],
                example_easy="a=5, b=4. Rask S ir P.",
                example_medium="Kiek tvoros reikia aptverti 20×30m sklypą?",
                example_hard="Plotas 40, ilgis 8. Koks plotis?",
                skills=["perimetras", "plotas", "formulės"],
                common_errors=[
                    "Perimetro ir ploto sumaišymas",
                    "Matų vienetų klaidos (m ir m²)",
                ],
                distractor_logic="Pateikti perimetrą vietoj ploto",
                competencies=[Competency.COGNITIVE],
            ),
        ],
    ),
    # --- LYGTYS IR RAIDINIAI REIŠKINIAI ---
    Topic(
        id="lygtys_basic_5",
        name_lt="Raidiniai reiškiniai ir lygtys",
        name_en="Algebraic Expressions and Equations",
        content_area=ContentArea.ALGEBRA,
        grade_introduced=5,
        grade_mastery=6,
        grades_available=[5, 6, 7, 8],
        description="Paprastosios lygtys su natūraliaisiais skaičiais",
        importance=5,
        prerequisites=["naturalieji_skaiciai_5"],
        subtopics=[
            Subtopic(
                id="simple_equations_5",
                name_lt="Paprastosios lygtys",
                name_en="Simple equations",
                description="Lygtys tipo x+a=b, a-x=b, ax=b (TIK natūralieji skaičiai)",
                satisfactory_requirements=[
                    "Rasti x: x + 15 = 30 (nežinomasis - dėmuo)",
                ],
                basic_requirements=[
                    "Rasti x: 2x + 5 = 15 (su natūraliaisiais)",
                    "Nežinomasis - turinys/mažinys: 50 - x = 20",
                ],
                advanced_requirements=[
                    "Sudaryti lygtį pagal tekstą ('Galvoju skaičių...')",
                    "Sprendžia lygtis ir atlieka patikrą",
                ],
                example_easy="x + 15 = 40",
                example_medium="50 - x = 20",
                example_hard="Galvoju skaičių, atimu 10 ir gaunu 5. Koks skaičius?",
                skills=["lygčių_sprendimas", "atvirkštiniai_veiksmai"],
                common_errors=[
                    "Atvirkštinio veiksmo pasirinkimo klaidos",
                    "a - x = b tipo lygčių sprendimo klaidos",
                ],
                distractor_logic="Taikyti neteisingą atvirkštinį veiksmą",
                competencies=[Competency.COGNITIVE],
            ),
        ],
    ),
]


# =============================================================================
# 6 KLASĖ - TURINIO SRITYS
# =============================================================================

GRADE_6_TOPICS = [
    # --- SKAIČIAI IR SKAIČIAVIMAI ---
    Topic(
        id="fractions_operations_6",
        name_lt="Veiksmai su trupmenomis",
        name_en="Fraction Operations",
        content_area=ContentArea.NUMBERS,
        grade_introduced=6,
        grade_mastery=7,
        grades_available=[6, 7, 8],
        description="Visi veiksmai su paprastosiomis trupmenomis",
        importance=5,
        prerequisites=["fractions_intro_5"],
        subtopics=[
            Subtopic(
                id="frac_common_denom",
                name_lt="Bendras vardiklis",
                name_en="Common denominator",
                description="Trupmenų bendravardiklinimas",
                satisfactory_requirements=[
                    "Randa bendrą vardiklį dviem trupmenoms (paprastais atvejais)",
                ],
                basic_requirements=[
                    "Randa MBK kaip bendrą vardiklį",
                    "Bendravardiklina 2-3 trupmenas",
                ],
                advanced_requirements=[
                    "Efektyviai randa mažiausią bendrą vardiklį",
                    "Bendravardiklina trupmenas su dideliais vardikliais",
                ],
                example_easy="Rask bendrą vardiklį: 1/2 ir 1/4",
                example_medium="Bendravardiklink: 2/3 ir 3/4",
                example_hard="Bendravardiklink: 5/6, 3/8 ir 7/12",
                skills=["bendras_vardiklis", "mbk"],
            ),
            Subtopic(
                id="frac_add_sub_6",
                name_lt="Trupmenų sudėtis ir atimtis",
                name_en="Addition and subtraction of fractions",
                description="Sudėtis ir atimtis su skirtingais vardikliais",
                satisfactory_requirements=[
                    "Sudeda trupmenas su skirtingais vardikliais (paprastais atvejais)",
                ],
                basic_requirements=[
                    "Atlieka sudėtį ir atimtį su bet kokiais vardikliais",
                    "Supaprastina rezultatą",
                    "Dirba su mišriosiomis trupmenomis",
                ],
                advanced_requirements=[
                    "Sprendžia daugiaveiksmius reiškinius",
                    "Sprendžia tekstinius uždavinius",
                ],
                example_easy="1/2 + 1/4 = ?",
                example_medium="2/3 - 1/4 + 1/6 = ?",
                example_hard="3 1/2 - 1 2/3 + 2 1/4 = ?",
                skills=["trupmenų_sudėtis", "trupmenų_atimtis", "mišriosios"],
            ),
            Subtopic(
                id="frac_mult_div_6",
                name_lt="Trupmenų daugyba ir dalyba",
                name_en="Multiplication and division of fractions",
                description="Trupmenos daugybos ir dalybos veiksmai",
                satisfactory_requirements=[
                    "Daugina trupmeną iš natūraliojo skaičiaus",
                ],
                basic_requirements=[
                    "Daugina ir dalija trupmenas",
                    "Taiko atvirkštinės trupmenos sąvoką",
                    "Supaprastina prieš dauginant",
                ],
                advanced_requirements=[
                    "Sprendžia sudėtingus reiškinius su visais veiksmais",
                    "Taiko veiksmų su trupmenomis savybes",
                ],
                example_easy="2/3 × 6 = ?",
                example_medium="3/4 × 2/5 = ?",
                example_hard="(2/3 + 1/4) ÷ (1/2 - 1/6) = ?",
                skills=["trupmenų_daugyba", "trupmenų_dalyba", "atvirkštinė"],
            ),
        ],
    ),
    Topic(
        id="decimals_operations_6",
        name_lt="Veiksmai su dešimtainėmis trupmenomis",
        name_en="Decimal Operations",
        content_area=ContentArea.NUMBERS,
        grade_introduced=6,
        grade_mastery=6,
        grades_available=[6, 7, 8],
        description="Visi veiksmai su dešimtainėmis trupmenomis",
        importance=5,
        prerequisites=["decimals_5"],
        subtopics=[
            Subtopic(
                id="dec_mult_6",
                name_lt="Dešimtainių daugyba",
                name_en="Decimal multiplication",
                description="Dešimtainių trupmenų daugyba",
                satisfactory_requirements=[
                    "Daugina dešimtainę iš 10, 100, 1000",
                    "Daugina dešimtainę iš natūraliojo skaičiaus",
                ],
                basic_requirements=[
                    "Daugina dvi dešimtaines trupmenas",
                    "Teisingai deda kablelį rezultate",
                ],
                advanced_requirements=[
                    "Vertina atsakymo pagrįstumą",
                    "Sprendžia tekstinius uždavinius",
                ],
                example_easy="2,5 × 10 = ?",
                example_medium="3,4 × 2,5 = ?",
                example_hard="1 m² kainuoja 12,50 €. Kiek kainuos 3,6 m²?",
                skills=["dešimtainių_daugyba", "kablelio_padėtis"],
            ),
            Subtopic(
                id="dec_div_6",
                name_lt="Dešimtainių dalyba",
                name_en="Decimal division",
                description="Dešimtainių trupmenų dalyba",
                satisfactory_requirements=[
                    "Dalija dešimtainę iš 10, 100, 1000",
                    "Dalija dešimtainę iš natūraliojo skaičiaus",
                ],
                basic_requirements=[
                    "Dalija dvi dešimtaines trupmenas",
                    "Supranta periodinių dešimtainių sąvoką",
                ],
                advanced_requirements=[
                    "Apvalina dalybos rezultatą iki nurodyto tikslumo",
                    "Sprendžia tekstinius uždavinius",
                ],
                example_easy="4,8 ÷ 4 = ?",
                example_medium="7,5 ÷ 2,5 = ?",
                example_hard="15 kg kainuoja 22,50 €. Kiek kainuoja 1 kg?",
                skills=["dešimtainių_dalyba", "periodinės_trupmenos"],
            ),
        ],
    ),
    Topic(
        id="percentages_6",
        name_lt="Procentai",
        name_en="Percentages",
        content_area=ContentArea.NUMBERS,
        grade_introduced=6,
        grade_mastery=7,
        grades_available=[6, 7, 8, 9, 10],
        description="Procento sąvoka, skaičiavimai su procentais",
        importance=5,
        prerequisites=["fractions_operations_6", "decimals_operations_6"],
        subtopics=[
            Subtopic(
                id="perc_concept",
                name_lt="Procento sąvoka",
                name_en="Percentage concept",
                description="Kas yra procentas, ryšys su trupmenomis",
                satisfactory_requirements=[
                    "Supranta, kad 1% = 1/100",
                    "Verčia paprastus procentus trupmenomis ir atvirkščiai",
                ],
                basic_requirements=[
                    "Verčia bet kokius procentus trupmenomis ir dešimtainėmis",
                    "Atpažįsta procentus diagramose",
                ],
                advanced_requirements=[
                    "Taiko procentus įvairiose situacijose",
                    "Lygina procentus, trupmenas, dešimtaines",
                ],
                example_easy="Užrašyk 50% trupmena",
                example_medium="Paversk 3/4 procentais",
                example_hard="Kas daugiau: 0,7 ar 65%?",
                skills=["procentų_samprata", "vertimas"],
            ),
            Subtopic(
                id="perc_find_part",
                name_lt="Procento dalies radimas",
                name_en="Finding percentage of a number",
                description="X% nuo skaičiaus radimas",
                satisfactory_requirements=[
                    "Randa 10%, 25%, 50% nuo skaičiaus",
                ],
                basic_requirements=[
                    "Randa bet kokį procentą nuo skaičiaus",
                    "Sprendžia nuolaidos, palūkanų uždavinius",
                ],
                advanced_requirements=[
                    "Sprendžia sudėtingus praktinius uždavinius",
                    "Apskaičiuoja galutinę kainą su keliomis nuolaidomis",
                ],
                example_easy="Rask 25% nuo 80",
                example_medium="Prekė kainuoja 60 €. Nuolaida 15%. Kokia nauja kaina?",
                example_hard="Prekei taikoma 20% nuolaida, o lojalumo kortelei dar 10%. Pradinė kaina 100 €.",
                skills=["procentų_radimas", "nuolaidos", "palūkanos"],
            ),
            Subtopic(
                id="perc_find_whole",
                name_lt="Skaičiaus radimas pagal procentus",
                name_en="Finding the whole from percentage",
                description="Jei X% = skaičius, rasti visą skaičių",
                satisfactory_requirements=[
                    "Randa skaičių, kai žinoma 50%, 25%",
                ],
                basic_requirements=[
                    "Randa skaičių pagal bet kokį procentą",
                    "Sprendžia tekstinius uždavinius",
                ],
                advanced_requirements=[
                    "Sprendžia sudėtingus procentų uždavinius",
                    "Randa pradinę kainą pagal galutinę ir nuolaidą",
                ],
                example_easy="20% skaičiaus yra 10. Koks skaičius?",
                example_medium="Po 30% nuolaidos prekė kainuoja 35 €. Kokia pradinė kaina?",
                example_hard="Banke per metus suma padidėjo 8% ir tapo 540 €. Kokia buvo pradinė suma?",
                skills=["skaičiaus_radimas", "atvirkštiniai_procentai"],
            ),
        ],
    ),
    Topic(
        id="integers_6",
        name_lt="Sveikieji skaičiai",
        name_en="Integers",
        content_area=ContentArea.NUMBERS,
        grade_introduced=6,
        grade_mastery=7,
        grades_available=[6, 7, 8],
        description="Teigiami ir neigiami skaičiai, veiksmai su jais",
        importance=5,
        prerequisites=["natural_numbers_5"],
        subtopics=[
            Subtopic(
                id="int_concept",
                name_lt="Sveikųjų skaičių sąvoka",
                name_en="Integer concept",
                description="Teigiami ir neigiami skaičiai, modulis",
                satisfactory_requirements=[
                    "Atpažįsta teigiamus ir neigiamus skaičius",
                    "Žymi skaičius skaičių tiesėje",
                ],
                basic_requirements=[
                    "Lygina sveikuosius skaičius",
                    "Randa skaičiaus modulį",
                    "Supranta priešingų skaičių sąvoką",
                ],
                advanced_requirements=[
                    "Taiko sveikuosius skaičius praktinėse situacijose",
                    "Sprendžia uždavinius su temperatūra, skolom",
                ],
                example_easy="Kuris didesnis: -3 ar -5?",
                example_medium="Rask |-7|",
                example_hard="Temperatūra nuo -8°C pakilo 15°C. Kokia dabar?",
                skills=["sveikieji_skaičiai", "modulis", "skaičių_tiesė"],
            ),
            Subtopic(
                id="int_operations",
                name_lt="Veiksmai su sveikaisiais skaičiais",
                name_en="Operations with integers",
                description="Sudėtis, atimtis, daugyba, dalyba",
                satisfactory_requirements=[
                    "Sudeda ir atima skaičius su vienodais ženklais",
                ],
                basic_requirements=[
                    "Atlieka visus veiksmus su sveikaisiais skaičiais",
                    "Taiko ženklų taisykles daugyboje ir dalyboje",
                ],
                advanced_requirements=[
                    "Sprendžia daugiaveiksmius reiškinius",
                    "Taiko veiksmų savybes",
                ],
                example_easy="(-5) + (-3) = ?",
                example_medium="(-8) × (-3) = ?",
                example_hard="(-12) ÷ 4 + (-5) × (-2) = ?",
                skills=["sveikųjų_sudėtis", "sveikųjų_daugyba", "ženklų_taisyklės"],
            ),
        ],
    ),
    # --- ALGEBRA (6 klasė) ---
    Topic(
        id="equations_6",
        name_lt="Tiesinės lygtys",
        name_en="Linear Equations",
        content_area=ContentArea.ALGEBRA,
        grade_introduced=6,
        grade_mastery=7,
        grades_available=[6, 7, 8],
        description="Tiesinių lygčių sprendimas",
        importance=5,
        prerequisites=["expressions_intro_5", "equations_intro_5", "integers_6"],
        subtopics=[
            Subtopic(
                id="eq_linear_6",
                name_lt="Lygtys su vienu nežinomuoju",
                name_en="Equations with one unknown",
                description="Lygtys ax + b = c",
                satisfactory_requirements=[
                    "Sprendžia lygtis ax + b = c, kai a, b, c natūralūs",
                ],
                basic_requirements=[
                    "Sprendžia lygtis su sveikaisiais skaičiais",
                    "Sprendžia lygtis su skliaustais",
                    "Atlieka patikrą",
                ],
                advanced_requirements=[
                    "Sprendžia sudėtingesnes lygtis",
                    "Sudaro lygtis pagal tekstines sąlygas",
                ],
                example_easy="2x + 5 = 11, rask x",
                example_medium="3(x - 2) = 15, rask x",
                example_hard="4x - 3 = 2x + 9, rask x",
                skills=["lygčių_sprendimas", "skliaustų_atskleidimas"],
            ),
        ],
    ),
    Topic(
        id="ratios_6",
        name_lt="Santykiai ir proporcijos",
        name_en="Ratios and Proportions",
        content_area=ContentArea.ALGEBRA,
        grade_introduced=6,
        grade_mastery=7,
        grades_available=[6, 7, 8],
        description="Santykis, proporcija, proporcingumas",
        importance=5,
        prerequisites=["fractions_operations_6"],
        subtopics=[
            Subtopic(
                id="ratio_concept",
                name_lt="Santykis",
                name_en="Ratio",
                description="Santykio sąvoka, supaprastinimas",
                satisfactory_requirements=[
                    "Supranta santykio prasmę",
                    "Užrašo santykį a:b",
                ],
                basic_requirements=[
                    "Supaprastina santykius",
                    "Dalija skaičių santykiu",
                ],
                advanced_requirements=[
                    "Sprendžia sudėtingus padalijimo uždavinius",
                    "Randa proporcingas dalis",
                ],
                example_easy="Užrašyk santykį: 6 berniukai ir 4 mergaitės",
                example_medium="Supaprastink 12:18",
                example_hard="Padalink 120 santykiu 3:2:1",
                skills=["santykiai", "supaprastinimas", "padalijimas"],
            ),
            Subtopic(
                id="proportion_6",
                name_lt="Proporcija",
                name_en="Proportion",
                description="Proporcijos sąvoka, pagrindinė savybė",
                satisfactory_requirements=[
                    "Atpažįsta proporciją",
                    "Žino proporcijos pagrindinę savybę",
                ],
                basic_requirements=[
                    "Randa nežinomą proporcijos narį",
                    "Tikrina ar santykiai sudaro proporciją",
                ],
                advanced_requirements=[
                    "Sudaro proporcijas tekstiniuose uždaviniuose",
                    "Sprendžia sudėtingus proporcijų uždavinius",
                ],
                example_easy="2:3 = 4:x, rask x",
                example_medium="Jei 5 kg kainuoja 15 €, kiek kainuos 8 kg?",
                example_hard="Žemėlapio mastelis 1:50000. Koks tikras atstumas, jei žemėlapyje 3 cm?",
                skills=["proporcija", "mastelis", "nežinomo_radimas"],
            ),
        ],
    ),
    # --- GEOMETRIJA (6 klasė) ---
    Topic(
        id="triangles_6",
        name_lt="Trikampiai",
        name_en="Triangles",
        content_area=ContentArea.GEOMETRY,
        grade_introduced=6,
        grade_mastery=7,
        grades_available=[6, 7, 8],
        description="Trikampių klasifikacija, savybės, plotas",
        importance=5,
        prerequisites=["geometry_basics_5", "rectangles_squares_5"],
        subtopics=[
            Subtopic(
                id="tri_types",
                name_lt="Trikampių rūšys",
                name_en="Types of triangles",
                description="Klasifikacija pagal kraštines ir kampus",
                satisfactory_requirements=[
                    "Skiria lygiašonį, lygiakraštį, įvairiakraštį trikampius",
                    "Skiria smailųjį, statųjį, bukąjį trikampius",
                ],
                basic_requirements=[
                    "Klasifikuoja trikampį pagal jo savybes",
                    "Žino trikampio kampų sumą (180°)",
                ],
                advanced_requirements=[
                    "Sprendžia uždavinius su trikampių savybėmis",
                    "Randa nežinomus kampus",
                ],
                example_easy="Kokio tipo trikampis, jei visos kraštinės lygios?",
                example_medium="Rask trečią trikampio kampą, jei du kampai yra 50° ir 70°",
                example_hard="Lygiašonio trikampio viršūnės kampas 40°. Rask pamato kampus.",
                skills=["trikampių_klasifikacija", "kampų_suma"],
            ),
            Subtopic(
                id="tri_area",
                name_lt="Trikampio plotas",
                name_en="Triangle area",
                description="Trikampio ploto skaičiavimas",
                satisfactory_requirements=[
                    "Žino trikampio ploto formulę S = ah/2",
                ],
                basic_requirements=[
                    "Taiko formulę praktiškai",
                    "Randa aukštinę arba pagrindą pagal plotą",
                ],
                advanced_requirements=[
                    "Sprendžia sudėtingus ploto uždavinius",
                    "Randa sudėtinių figūrų plotus",
                ],
                example_easy="Trikampio pagrindas 8 cm, aukštinė 5 cm. Rask plotą.",
                example_medium="Trikampio plotas 24 cm². Pagrindas 8 cm. Rask aukštinę.",
                example_hard="Stačiojo trikampio statiniai 6 cm ir 8 cm. Rask plotą ir įžambinę.",
                skills=["trikampio_plotas", "aukštinė"],
            ),
        ],
    ),
    Topic(
        id="circles_6",
        name_lt="Apskritimas",
        name_en="Circle",
        content_area=ContentArea.GEOMETRY,
        grade_introduced=6,
        grade_mastery=7,
        grades_available=[6, 7, 8],
        description="Apskritimo elementai, ilgis, plotas",
        importance=4,
        prerequisites=["rectangles_squares_5"],
        subtopics=[
            Subtopic(
                id="circle_elements",
                name_lt="Apskritimo elementai",
                name_en="Circle elements",
                description="Centras, spindulys, skersmuo, lankas, chorda",
                satisfactory_requirements=[
                    "Žino spindulio ir skersmens sąvokas",
                    "Braižo apskritimą pagal spindulį",
                ],
                basic_requirements=[
                    "Atpažįsta visus apskritimo elementus",
                    "Taiko ryšį d = 2r",
                ],
                advanced_requirements=[
                    "Sprendžia uždavinius su apskritimo elementais",
                ],
                example_easy="Apskritimo spindulys 5 cm. Koks skersmuo?",
                example_medium="Nubraižyk apskritimą su r = 3 cm ir pažymėk chordą",
                example_hard="Apskritimo skersmuo 10 cm. Koks ilgiausios chordos ilgis?",
                skills=["apskritimo_elementai", "spindulys", "skersmuo"],
            ),
            Subtopic(
                id="circle_circumference",
                name_lt="Apskritimo ilgis",
                name_en="Circumference",
                description="Apskritimo ilgio skaičiavimas C = 2πr",
                satisfactory_requirements=[
                    "Žino formulę C = 2πr arba C = πd",
                ],
                basic_requirements=[
                    "Apskaičiuoja apskritimo ilgį",
                    "Naudoja π ≈ 3,14",
                ],
                advanced_requirements=[
                    "Randa spindulį pagal ilgį",
                    "Sprendžia praktinius uždavinius",
                ],
                example_easy="Apskritimo spindulys 7 cm. Rask ilgį (π ≈ 3,14).",
                example_medium="Rato skersmuo 50 cm. Kiek metrų nuvažiuos per 10 apsisukimų?",
                example_hard="Apskritimo ilgis 31,4 cm. Rask spindulį.",
                skills=["apskritimo_ilgis", "formulė"],
            ),
            Subtopic(
                id="circle_area",
                name_lt="Skritulio plotas",
                name_en="Circle area",
                description="Skritulio ploto skaičiavimas S = πr²",
                satisfactory_requirements=[
                    "Žino formulę S = πr²",
                ],
                basic_requirements=[
                    "Apskaičiuoja skritulio plotą",
                    "Sprendžia tekstinius uždavinius",
                ],
                advanced_requirements=[
                    "Randa spindulį pagal plotą",
                    "Skaičiuoja žiedo plotą",
                ],
                example_easy="Skritulio spindulys 5 cm. Rask plotą (π ≈ 3,14).",
                example_medium="Picos skersmuo 30 cm. Koks picos plotas?",
                example_hard="Žiedas: išorinis r = 10 cm, vidinis r = 6 cm. Rask plotą.",
                skills=["skritulio_plotas", "žiedas"],
            ),
        ],
    ),
    # --- STATISTIKA (6 klasė) ---
    Topic(
        id="statistics_6",
        name_lt="Duomenų charakteristikos",
        name_en="Data Characteristics",
        content_area=ContentArea.STATISTICS,
        grade_introduced=6,
        grade_mastery=7,
        grades_available=[6, 7, 8],
        description="Vidurkis, mediana, moda, imtis",
        importance=4,
        prerequisites=["data_basics_5"],
        subtopics=[
            Subtopic(
                id="mean_6",
                name_lt="Aritmetinis vidurkis",
                name_en="Arithmetic mean",
                description="Vidurkio skaičiavimas ir interpretavimas",
                satisfactory_requirements=[
                    "Apskaičiuoja vidurkį iš kelių skaičių",
                ],
                basic_requirements=[
                    "Apskaičiuoja vidurkį iš didesnio duomenų rinkinio",
                    "Interpretuoja vidurkio prasmę",
                ],
                advanced_requirements=[
                    "Sprendžia atvirkštinius uždavinius",
                    "Analizuoja vidurkio pokytį",
                ],
                example_easy="Rask vidurkį: 5, 7, 9, 11",
                example_medium="Mokinys gavo 8, 9, 7, 10, ?. Vidurkis turi būti 8,6. Koks paskutinis pažymys?",
                example_hard="5 skaičių vidurkis 12. Pridėjus 6-ą skaičių vidurkis tampa 11. Koks 6-asis?",
                skills=["vidurkis", "atvirkštinis_uždavinys"],
            ),
            Subtopic(
                id="median_mode_6",
                name_lt="Mediana ir moda",
                name_en="Median and mode",
                description="Medianos ir modos radimas",
                satisfactory_requirements=[
                    "Randa modą duomenų rinkinyje",
                ],
                basic_requirements=[
                    "Randa medianą sutvarkytame duomenų rinkinyje",
                    "Skiria vidurkio, medianos, modos sąvokas",
                ],
                advanced_requirements=[
                    "Pasirenka tinkamiausią charakteristiką duomenims",
                    "Kritiškai vertina duomenis",
                ],
                example_easy="Rask modą: 3, 5, 5, 7, 5, 9, 3",
                example_medium="Rask medianą: 12, 5, 8, 3, 15, 7, 9",
                example_hard="Kuri charakteristika tinkamesnė algoms: 2000, 2100, 2050, 15000, 2200?",
                skills=["mediana", "moda", "duomenų_analizė"],
            ),
        ],
    ),
]


# =============================================================================
# 7 KLASĖ - TURINIO SRITYS
# =============================================================================

GRADE_7_TOPICS = [
    # --- SKAIČIAI IR SKAIČIAVIMAI ---
    Topic(
        id="powers_7",
        name_lt="Laipsniai su natūraliuoju rodikliu",
        name_en="Powers with Natural Exponents",
        content_area=ContentArea.NUMBERS,
        grade_introduced=7,
        grade_mastery=8,
        grades_available=[7, 8, 9, 10],
        description="Laipsnio sąvoka, veiksmų taisyklės",
        importance=5,
        prerequisites=["natural_numbers_5", "integers_6"],
        subtopics=[
            Subtopic(
                id="pow_concept",
                name_lt="Laipsnio sąvoka",
                name_en="Power concept",
                description="Laipsnis, pagrindas, rodiklis",
                satisfactory_requirements=[
                    "Supranta laipsnio prasmę kaip pasikartojančią daugybą",
                    "Apskaičiuoja paprastus laipsnius",
                ],
                basic_requirements=[
                    "Apskaičiuoja laipsnius su neigiamais pagrindais",
                    "Žino, kad a⁰ = 1 ir a¹ = a",
                ],
                advanced_requirements=[
                    "Taiko laipsnius įvairiose situacijose",
                    "Sprendžia uždavinius su laipsniais",
                ],
                example_easy="Apskaičiuok: 2⁴",
                example_medium="Apskaičiuok: (-3)³",
                example_hard="Rask n, jei 2ⁿ = 32",
                skills=["laipsnis", "rodiklis", "pagrindas"],
            ),
            Subtopic(
                id="pow_rules",
                name_lt="Veiksmų su laipsniais taisyklės",
                name_en="Rules for operations with powers",
                description="Laipsnių daugyba, dalyba, kėlimas laipsniu",
                satisfactory_requirements=[
                    "Žino, kad aᵐ × aⁿ = aᵐ⁺ⁿ",
                ],
                basic_requirements=[
                    "Taiko visas pagrindines taisykles",
                    "Supaprastina reiškinius su laipsniais",
                ],
                advanced_requirements=[
                    "Sprendžia sudėtingesnius reiškinius",
                    "Taiko taisykles atvirkščia tvarka",
                ],
                example_easy="Supaprastink: 2³ × 2⁴",
                example_medium="Supaprastink: (a²)³ × a⁵",
                example_hard="Supaprastink: (2³ × 4²) ÷ 8",
                skills=["laipsnių_daugyba", "laipsnių_dalyba", "kėlimas_laipsniu"],
            ),
        ],
    ),
    Topic(
        id="rational_numbers_7",
        name_lt="Racionalieji skaičiai",
        name_en="Rational Numbers",
        content_area=ContentArea.NUMBERS,
        grade_introduced=7,
        grade_mastery=8,
        grades_available=[7, 8, 9, 10],
        description="Racionalieji skaičiai, veiksmai su jais",
        importance=5,
        prerequisites=["fractions_operations_6", "integers_6"],
        subtopics=[
            Subtopic(
                id="rat_operations",
                name_lt="Veiksmai su racionaliaisiais skaičiais",
                name_en="Operations with rational numbers",
                description="Visi veiksmai su teigiamomis ir neigiamomis trupmenomis",
                satisfactory_requirements=[
                    "Atlieka paprastus veiksmus su racionaliaisiais skaičiais",
                ],
                basic_requirements=[
                    "Atlieka visus veiksmus",
                    "Sprendžia reiškinius su keliais veiksmais",
                ],
                advanced_requirements=[
                    "Sprendžia sudėtingus daugiaveiksmius reiškinius",
                    "Optimizuoja skaičiavimus",
                ],
                example_easy="(-2/3) + (1/2) = ?",
                example_medium="(-3/4) × (2/5) + (1/2) = ?",
                example_hard="[(−2/3)² − (1/2)] ÷ (−1/6) = ?",
                skills=["racionalieji_skaičiai", "veiksmų_tvarka"],
            ),
        ],
    ),
    # --- ALGEBRA (7 klasė) ---
    Topic(
        id="algebraic_expressions_7",
        name_lt="Algebriniai reiškiniai",
        name_en="Algebraic Expressions",
        content_area=ContentArea.ALGEBRA,
        grade_introduced=7,
        grade_mastery=8,
        grades_available=[7, 8, 9, 10],
        description="Reiškiniai su kintamaisiais, pertvarkymas",
        importance=5,
        prerequisites=["expressions_intro_5", "powers_7"],
        subtopics=[
            Subtopic(
                id="expr_operations",
                name_lt="Veiksmai su reiškiniais",
                name_en="Operations with expressions",
                description="Reiškinių sudėtis, atimtis, daugyba",
                satisfactory_requirements=[
                    "Surenka panašius narius",
                    "Sudeda ir atima paprastus reiškinius",
                ],
                basic_requirements=[
                    "Daugina reiškinį iš skaičiaus",
                    "Atskleidžia skliaustus",
                    "Taiko sutrumpintos daugybos formules: (a+b)², (a-b)²",
                ],
                advanced_requirements=[
                    "Taiko visas sutrumpintos daugybos formules",
                    "Išskaido dauginamaisiais",
                ],
                example_easy="Supaprastink: 3x + 5x - 2x",
                example_medium="Išskleisk: 2(3x - 5) + 4x",
                example_hard="Išskleisk: (2x + 3)²",
                skills=["panašūs_nariai", "skliaustų_atskleidimas", "formulės"],
            ),
            Subtopic(
                id="expr_factoring",
                name_lt="Išskaidymas dauginamaisiais",
                name_en="Factoring",
                description="Bendro dauginamojo iškėlimas, grupavimas",
                satisfactory_requirements=[
                    "Iškelia bendrą dauginamąjį",
                ],
                basic_requirements=[
                    "Taiko sutrumpintos daugybos formules skaidymui",
                    "Skaido grupavimo būdu",
                ],
                advanced_requirements=[
                    "Skaido sudėtingesnius reiškinius",
                    "Renkasi tinkamiausią metodą",
                ],
                example_easy="Iškelk: 6x + 9",
                example_medium="Išskaidyk: x² - 9",
                example_hard="Išskaidyk: x² - 5x + 6",
                skills=["bendro_dauginamojo_iškėlimas", "formulės", "grupavimas"],
            ),
        ],
    ),
    Topic(
        id="linear_equations_7",
        name_lt="Tiesinės lygtys ir nelygybės",
        name_en="Linear Equations and Inequalities",
        content_area=ContentArea.ALGEBRA,
        grade_introduced=7,
        grade_mastery=8,
        grades_available=[7, 8, 9, 10],
        description="Sudėtingesnės tiesinės lygtys, nelygybės",
        importance=5,
        prerequisites=["equations_6", "algebraic_expressions_7"],
        subtopics=[
            Subtopic(
                id="eq_complex_7",
                name_lt="Sudėtingesnės tiesinės lygtys",
                name_en="More complex linear equations",
                description="Lygtys su skliaustais, trupmeninės lygtys",
                satisfactory_requirements=[
                    "Sprendžia lygtis su skliaustais",
                ],
                basic_requirements=[
                    "Sprendžia lygtis su kintamuoju abiejose pusėse",
                    "Sprendžia trupmenines lygtis (paprastesnes)",
                ],
                advanced_requirements=[
                    "Sprendžia sudėtingas trupmenines lygtis",
                    "Analizuoja lygčių sprendinių egzistavimą",
                ],
                example_easy="3(x - 2) = 2(x + 1)",
                example_medium="(x + 1)/2 = (2x - 3)/3",
                example_hard="(2x - 1)/3 - (x + 2)/4 = 1",
                skills=["lygtys_su_skliaustais", "trupmeninės_lygtys"],
                common_errors=[
                    "Skliaustų atidaromo klaidos (ypač su minusu prieš)",
                    "Lygties pušių sumaišymas perkeliant narius",
                    "Ženklo keitimo pamiršimas perkeliant",
                    "Trupmeninių lygčių vardiklių nepatikrinimas (dalyba iš 0)",
                ],
                distractor_logic="Pateikti atsakymą su ženklo klaida",
                competencies=[Competency.COGNITIVE],
            ),
            Subtopic(
                id="ineq_7",
                name_lt="Tiesinės nelygybės",
                name_en="Linear inequalities",
                description="Nelygybių sprendimas ir atvaizdavimas",
                satisfactory_requirements=[
                    "Supranta nelygybės prasmę",
                    "Sprendžia paprastas nelygybes",
                ],
                basic_requirements=[
                    "Sprendžia sudėtingesnes nelygybes",
                    "Atvaizduoja sprendinių aibę skaičių tiesėje",
                ],
                advanced_requirements=[
                    "Sprendžia dvigubas nelygybes",
                    "Užrašo sprendinių aibę intervalais",
                ],
                example_easy="2x + 3 > 7, rask x",
                example_medium="3x - 5 ≤ 2x + 4, rask x ir atvaizduok",
                example_hard="-2 < 3x + 1 ≤ 10, rask x",
                skills=["nelygybės", "intervalai", "skaičių_tiesė"],
                common_errors=[
                    "Ženklo nepakeitimas dalinant iš neigiamo skaičiaus",
                    "Intervalo ribos painiojimas (atviras/uždaras)",
                    "Dvigubų nelygybių sprendimo klaidos",
                ],
                distractor_logic="Pateikti intervalą su nekeista nelygybe dalinant iš -1",
                competencies=[Competency.COGNITIVE],
            ),
        ],
    ),
    Topic(
        id="word_problems_7",
        name_lt="Tekstiniai uždaviniai",
        name_en="Word Problems",
        content_area=ContentArea.ALGEBRA,
        grade_introduced=7,
        grade_mastery=8,
        grades_available=[7, 8, 9, 10],
        description="Tekstinių uždavinių sprendimas lygčių pagalba",
        importance=5,
        prerequisites=["linear_equations_7", "ratios_6"],
        subtopics=[
            Subtopic(
                id="wp_motion",
                name_lt="Judėjimo uždaviniai",
                name_en="Motion problems",
                description="Greitis, laikas, atstumas",
                satisfactory_requirements=[
                    "Taiko formulę s = v × t",
                    "Sprendžia paprastus judėjimo uždavinius",
                ],
                basic_requirements=[
                    "Sprendžia uždavinius su dviem objektais",
                    "Supranta sąvokas: priešpriešinis, pasivijimo judėjimas",
                ],
                advanced_requirements=[
                    "Sprendžia sudėtingus judėjimo uždavinius",
                    "Analizuoja grafinę judėjimo interpretaciją",
                ],
                example_easy="Automobilis važiuoja 60 km/h. Per kiek laiko nuvažiuos 180 km?",
                example_medium="Du dviratininkai išvyko vienas prieš kitą. Greičiai 15 km/h ir 20 km/h. Atstumas 70 km. Po kiek laiko susitiks?",
                example_hard="Automobilis aplenkia dviratininką. Automobilio greitis 60 km/h, dviratininko 20 km/h. Pradinė distancija 20 km. Po kiek laiko aplenkis?",
                skills=["greitis", "laikas", "atstumas", "judėjimo_tipai"],
            ),
            Subtopic(
                id="wp_work",
                name_lt="Darbo uždaviniai",
                name_en="Work problems",
                description="Bendro darbo uždaviniai",
                satisfactory_requirements=[
                    "Supranta darbo našumo sąvoką",
                ],
                basic_requirements=[
                    "Sprendžia paprastus bendro darbo uždavinius",
                ],
                advanced_requirements=[
                    "Sprendžia sudėtingus darbo uždavinius su pertraukomis",
                ],
                example_easy="Petras darbą atlieka per 6 val. Kokią dalį atlieka per 1 val.?",
                example_medium="Petras darbą atlieka per 6 val., Jonas per 4 val. Per kiek laiko atliks kartu?",
                example_hard="Pirmas darbininkas darbą atlieka per 10 val. Po 2 val. prisijungė antras. Kartu baigė po 3 val. Per kiek laiko antrasis dirbtų vienas?",
                skills=["darbo_uždaviniai", "našumas"],
            ),
        ],
    ),
    # --- GEOMETRIJA (7 klasė) ---
    Topic(
        id="quadrilaterals_7",
        name_lt="Keturkampiai",
        name_en="Quadrilaterals",
        content_area=ContentArea.GEOMETRY,
        grade_introduced=7,
        grade_mastery=8,
        grades_available=[7, 8, 9, 10],
        description="Keturkampių rūšys, savybės, plotai",
        importance=5,
        prerequisites=["rectangles_squares_5", "triangles_6"],
        subtopics=[
            Subtopic(
                id="quad_types",
                name_lt="Keturkampių rūšys",
                name_en="Types of quadrilaterals",
                description="Lygiagretainis, rombas, trapecija",
                satisfactory_requirements=[
                    "Atpažįsta pagrindinius keturkampius",
                    "Žino stačiakampio ir kvadrato savybes",
                ],
                basic_requirements=[
                    "Žino lygiagrėtainio, rombo, trapecijos savybes",
                    "Klasifikuoja keturkampius",
                ],
                advanced_requirements=[
                    "Įrodo keturkampių savybes",
                    "Taiko savybes uždaviniuose",
                ],
                example_easy="Kokio tipo keturkampis turi 4 lygias kraštines ir stačius kampus?",
                example_medium="Lygiagrėtainio priešingi kampai lygūs 60° ir 120°. Kodėl?",
                example_hard="Įrodyk, kad rombo įstrižainės statmenos viena kitai",
                skills=["keturkampiai", "savybės", "klasifikacija"],
            ),
            Subtopic(
                id="quad_area",
                name_lt="Keturkampių plotai",
                name_en="Areas of quadrilaterals",
                description="Lygiagrėtainio, rombo, trapecijos plotų formulės",
                satisfactory_requirements=[
                    "Žino lygiagrėtainio ploto formulę S = ah",
                ],
                basic_requirements=[
                    "Taiko rombo ploto formulę S = d₁d₂/2",
                    "Taiko trapecijos ploto formulę S = (a+b)h/2",
                ],
                advanced_requirements=[
                    "Sprendžia sudėtingus ploto uždavinius",
                    "Randa nežinomus dydžius pagal plotą",
                ],
                example_easy="Lygiagrėtainio pagrindas 8 cm, aukštinė 5 cm. Rask plotą.",
                example_medium="Rombo įstrižainės 6 cm ir 8 cm. Rask plotą.",
                example_hard="Trapecijos pagrindai 10 cm ir 6 cm. Plotas 40 cm². Rask aukštinę.",
                skills=["lygiagrėtainio_plotas", "rombo_plotas", "trapecijos_plotas"],
            ),
        ],
    ),
    Topic(
        id="pythagorean_intro_7",
        name_lt="Pitagoro teorema (įvadas)",
        name_en="Introduction to Pythagorean Theorem",
        content_area=ContentArea.GEOMETRY,
        grade_introduced=7,
        grade_mastery=8,
        grades_available=[7, 8, 9, 10],
        description="Pitagoro teorema ir jos taikymas",
        importance=5,
        prerequisites=["triangles_6", "powers_7"],
        subtopics=[
            Subtopic(
                id="pyth_theorem",
                name_lt="Pitagoro teorema",
                name_en="Pythagorean theorem",
                description="Stačiakampio trikampio savybė c² = a² + b²",
                satisfactory_requirements=[
                    "Žino Pitagoro teoremos formulę",
                    "Patikrina ar skaičiai sudaro Pitagoro trejetą",
                ],
                basic_requirements=[
                    "Randa įžambinę pagal statinius",
                    "Randa statinį pagal įžambinę ir kitą statinį",
                ],
                advanced_requirements=[
                    "Taiko teoremą sudėtingesnėse figūrose",
                    "Sprendžia praktinius uždavinius",
                ],
                example_easy="Ar 3, 4, 5 sudaro Pitagoro trejetą?",
                example_medium="Statiniai 6 cm ir 8 cm. Rask įžambinę.",
                example_hard="Kopėčios 5 m ilgio atremiamos į sieną. Kojų atstumas nuo sienos 3 m. Kokiame aukštyje?",
                skills=["pitagoro_teorema", "stačiakampis_trikampis"],
                common_errors=[
                    "Formulės taikymas ne stačiakampiui trikampiui",
                    "Įžambinės ir statinio sumašymas (c ≠ a + b)",
                    "Pamirštama ištraukti šaknį (c² = 25, tai c = 25 o ne 5)",
                    "Šaknies iš neigiamo skaičiaus (kai statinys > įžambinė)",
                ],
                distractor_logic="Pateikti c² reikšmę vietoj c",
                competencies=[Competency.COGNITIVE, Competency.CREATIVE],
            ),
        ],
    ),
    # --- STATISTIKA (7 klasė) ---
    Topic(
        id="probability_intro_7",
        name_lt="Tikimybių įvadas",
        name_en="Introduction to Probability",
        content_area=ContentArea.STATISTICS,
        grade_introduced=7,
        grade_mastery=8,
        grades_available=[7, 8, 9, 10],
        description="Tikimybės sąvoka, paprastas skaičiavimas",
        importance=4,
        prerequisites=["fractions_operations_6"],
        subtopics=[
            Subtopic(
                id="prob_concept",
                name_lt="Tikimybės sąvoka",
                name_en="Probability concept",
                description="Atsitiktinis įvykis, tikimybė",
                satisfactory_requirements=[
                    "Supranta tikimybės prasmę",
                    "Skiria neįmanomus, būtinus, atsitiktinius įvykius",
                ],
                basic_requirements=[
                    "Apskaičiuoja paprastą tikimybę P = m/n",
                    "Taiko tikimybę praktinėse situacijose",
                ],
                advanced_requirements=[
                    "Sprendžia sudėtingesnius tikimybių uždavinius",
                ],
                example_easy="Kokia tikimybė išmesti lyginį skaičių metant kauliuką?",
                example_medium="Dėžėje 3 raudoni ir 5 mėlyni kamuoliukai. Kokia tikimybė ištraukti raudoną?",
                example_hard="Kokia tikimybė ištraukti tūzą iš 52 kortų kaladės?",
                skills=["tikimybė", "palankūs_atvejai"],
                common_errors=[
                    "Pamirštama skaičiuoti visus įmanomus atvejus",
                    "Tikimybė > 1 (negalima)",
                    "Sudėtinių įvykių tikimybių sudėjimas vietoj dauginimo",
                ],
                distractor_logic="Pateikti tikimybę su neteisingu vardįliu",
                competencies=[Competency.COGNITIVE, Competency.CIVIC],
            ),
        ],
    ),
]


# =============================================================================
# 8 KLASĖ - TURINIO SRITYS
# =============================================================================

GRADE_8_TOPICS = [
    # --- SKAIČIAI IR SKAIČIAVIMAI ---
    Topic(
        id="roots_8",
        name_lt="Šaknys",
        name_en="Roots",
        content_area=ContentArea.NUMBERS,
        grade_introduced=8,
        grade_mastery=9,
        grades_available=[8, 9, 10],
        description="Kvadratinė šaknis, kubinė šaknis",
        importance=5,
        prerequisites=["powers_7"],
        subtopics=[
            Subtopic(
                id="sqrt_concept",
                name_lt="Kvadratinė šaknis",
                name_en="Square root",
                description="Šaknies sąvoka, savybės, traukimas",
                satisfactory_requirements=[
                    "Supranta šaknies sąvoką",
                    "Traukia šaknį iš pilnų kvadratų",
                ],
                basic_requirements=[
                    "Žino šaknies savybes",
                    "Supaprastina šaknies reiškinius",
                    "Traukia dauginamąjį iš po šaknies",
                ],
                advanced_requirements=[
                    "Atlieka veiksmus su šaknimis",
                    "Racionalina vardiklį",
                ],
                example_easy="√64 = ?",
                example_medium="Supaprastink: √50",
                example_hard="Racionalink vardiklį: 3/√2",
                skills=["kvadratinė_šaknis", "savybės", "racionalizavimas"],
            ),
        ],
    ),
    Topic(
        id="standard_form_8",
        name_lt="Standartinis skaičiaus pavidalas",
        name_en="Scientific Notation",
        content_area=ContentArea.NUMBERS,
        grade_introduced=8,
        grade_mastery=8,
        grades_available=[8, 9, 10],
        description="Labai didelių ir labai mažų skaičių užrašymas",
        importance=4,
        prerequisites=["powers_7"],
        subtopics=[
            Subtopic(
                id="sci_notation",
                name_lt="Standartinis pavidalas",
                name_en="Scientific notation",
                description="Skaičiaus užrašymas a × 10ⁿ",
                satisfactory_requirements=[
                    "Užrašo didelius skaičius standartiniu pavidalu",
                ],
                basic_requirements=[
                    "Užrašo mažus skaičius standartiniu pavidalu",
                    "Konvertuoja atgal į įprastą formą",
                ],
                advanced_requirements=[
                    "Atlieka veiksmus su standartinio pavidalo skaičiais",
                ],
                example_easy="Užrašyk standartiniu pavidalu: 5 600 000",
                example_medium="Užrašyk standartiniu pavidalu: 0,00047",
                example_hard="Apskaičiuok: (3 × 10⁴) × (2 × 10⁻²)",
                skills=["standartinis_pavidalas", "dešimties_laipsniai"],
            ),
        ],
    ),
    # --- ALGEBRA (8 klasė) ---
    Topic(
        id="quadratic_equations_8",
        name_lt="Kvadratinės lygtys",
        name_en="Quadratic Equations",
        content_area=ContentArea.ALGEBRA,
        grade_introduced=8,
        grade_mastery=9,
        grades_available=[8, 9, 10],
        description="Kvadratinių lygčių sprendimas",
        importance=5,
        prerequisites=["algebraic_expressions_7", "roots_8"],
        subtopics=[
            Subtopic(
                id="quad_eq_incomplete",
                name_lt="Nepilnosios kvadratinės lygtys",
                name_en="Incomplete quadratic equations",
                description="Lygtys ax² + c = 0 ir ax² + bx = 0",
                satisfactory_requirements=[
                    "Sprendžia lygtis tipo x² = a",
                ],
                basic_requirements=[
                    "Sprendžia lygtis ax² + c = 0",
                    "Sprendžia lygtis ax² + bx = 0 (iškeliant)",
                ],
                advanced_requirements=[
                    "Analizuoja sprendinių skaičių",
                ],
                example_easy="x² = 25",
                example_medium="2x² - 18 = 0",
                example_hard="3x² + 6x = 0",
                skills=["nepilnosios_lygtys"],
            ),
            Subtopic(
                id="quad_eq_full",
                name_lt="Pilnosios kvadratinės lygtys",
                name_en="Complete quadratic equations",
                description="Diskriminantas, sprendimas formule",
                satisfactory_requirements=[
                    "Žino kvadratinės lygties bendrą formą",
                ],
                basic_requirements=[
                    "Apskaičiuoja diskriminantą",
                    "Sprendžia lygtis naudojant formulę",
                ],
                advanced_requirements=[
                    "Analizuoja sprendinių priklausomybę nuo D",
                    "Taiko Vijeto teoremą",
                ],
                example_easy="x² - 5x + 6 = 0, naudok formulę",
                example_medium="2x² + 3x - 2 = 0",
                example_hard="Rask m, jei lygties x² - 4x + m = 0 diskriminantas lygus 0",
                skills=["diskriminantas", "formulė", "vijeto_teorema"],
            ),
        ],
    ),
    Topic(
        id="equation_systems_8",
        name_lt="Tiesinių lygčių sistemos",
        name_en="Systems of Linear Equations",
        content_area=ContentArea.ALGEBRA,
        grade_introduced=8,
        grade_mastery=9,
        grades_available=[8, 9, 10],
        description="Dviejų lygčių su dviem nežinomaisiais sistemos",
        importance=5,
        prerequisites=["linear_equations_7"],
        subtopics=[
            Subtopic(
                id="sys_substitution",
                name_lt="Keitimo būdas",
                name_en="Substitution method",
                description="Sistemos sprendimas keitimo būdu",
                satisfactory_requirements=[
                    "Supranta sistemos sprendinio prasmę",
                ],
                basic_requirements=[
                    "Sprendžia sistemas keitimo būdu",
                ],
                advanced_requirements=[
                    "Pasirenka efektyviausią metodą",
                ],
                example_easy="y = x + 2; x + y = 10",
                example_medium="2x + y = 7; x - y = 2",
                example_hard="3x - 2y = 8; 2x + 3y = 14",
                skills=["keitimo_būdas"],
            ),
            Subtopic(
                id="sys_addition",
                name_lt="Sudėties būdas",
                name_en="Addition method",
                description="Sistemos sprendimas sudėties būdu",
                satisfactory_requirements=[
                    "Supranta sudėties būdo esmę",
                ],
                basic_requirements=[
                    "Sprendžia sistemas sudėties būdu",
                ],
                advanced_requirements=[
                    "Analizuoja sistemų sprendinių skaičių",
                ],
                example_easy="x + y = 5; x - y = 1",
                example_medium="2x + 3y = 12; 3x - 3y = 3",
                example_hard="5x + 2y = 16; 3x + 4y = 18",
                skills=["sudėties_būdas"],
            ),
        ],
    ),
    Topic(
        id="linear_functions_8",
        name_lt="Tiesinė funkcija",
        name_en="Linear Function",
        content_area=ContentArea.ALGEBRA,
        grade_introduced=8,
        grade_mastery=9,
        grades_available=[8, 9, 10],
        description="Tiesinės funkcijos grafikas, savybės",
        importance=5,
        prerequisites=["linear_equations_7"],
        subtopics=[
            Subtopic(
                id="lin_func_graph",
                name_lt="Tiesinės funkcijos grafikas",
                name_en="Graph of linear function",
                description="Funkcija y = kx + b, jos grafikas",
                satisfactory_requirements=[
                    "Braižo tiesinės funkcijos grafiką pagal taškų lentelę",
                ],
                basic_requirements=[
                    "Supranta koeficientų k ir b prasmę",
                    "Nustato funkciją pagal grafiką",
                ],
                advanced_requirements=[
                    "Analizuoja funkcijų savybes",
                    "Sprendžia uždavinius su funkcijomis",
                ],
                example_easy="Nubraižyk y = 2x + 1 grafiką",
                example_medium="Rask funkciją, kurios grafikas eina per taškus (0; 3) ir (2; 7)",
                example_hard="Rask tiesių y = 2x - 1 ir y = -x + 5 susikirtimo tašką",
                skills=["funkcijos_grafikas", "krypties_koeficientas"],
            ),
        ],
    ),
    # --- GEOMETRIJA (8 klasė) ---
    Topic(
        id="similarity_8",
        name_lt="Figūrų panašumas",
        name_en="Similarity of Figures",
        content_area=ContentArea.GEOMETRY,
        grade_introduced=8,
        grade_mastery=9,
        grades_available=[8, 9, 10],
        description="Panašių figūrų savybės",
        importance=5,
        prerequisites=["triangles_6", "ratios_6"],
        subtopics=[
            Subtopic(
                id="similar_triangles",
                name_lt="Panašieji trikampiai",
                name_en="Similar triangles",
                description="Panašumo požymiai, santykiai",
                satisfactory_requirements=[
                    "Supranta panašumo sąvoką",
                ],
                basic_requirements=[
                    "Žino panašumo požymius",
                    "Randa panašumo koeficientą",
                ],
                advanced_requirements=[
                    "Taiko panašumą skaičiavimams",
                    "Sprendžia praktinius uždavinius",
                ],
                example_easy="Ar du trikampiai panašūs, jei jų kampai lygūs?",
                example_medium="Panašių trikampių kraštinės 3 cm ir 6 cm. Koks panašumo koeficientas?",
                example_hard="Medžio šešėlis 6 m. Tuo pat metu 2 m lazda meta 1,5 m šešėlį. Koks medžio aukštis?",
                skills=["panašumas", "panašumo_koeficientas"],
            ),
        ],
    ),
    Topic(
        id="solid_geometry_8",
        name_lt="Erdvinės figūros",
        name_en="Solid Geometry",
        content_area=ContentArea.GEOMETRY,
        grade_introduced=8,
        grade_mastery=9,
        grades_available=[8, 9, 10],
        description="Prizmė, piramidė, tūris ir paviršiaus plotas",
        importance=5,
        prerequisites=["rectangles_squares_5", "quadrilaterals_7"],
        subtopics=[
            Subtopic(
                id="prism_8",
                name_lt="Prizmė",
                name_en="Prism",
                description="Stačiakampė prizmė, tūris ir paviršiaus plotas",
                satisfactory_requirements=[
                    "Atpažįsta prizmę",
                    "Žino stačiakampės gretasienio tūrio formulę",
                ],
                basic_requirements=[
                    "Skaičiuoja prizmės tūrį ir paviršiaus plotą",
                ],
                advanced_requirements=[
                    "Sprendžia sudėtingus erdvinės geometrijos uždavinius",
                ],
                example_easy="Stačiakampis gretasienis 3×4×5 cm. Rask tūrį.",
                example_medium="Kubo briaunos ilgis 4 cm. Rask paviršiaus plotą.",
                example_hard="Stačiakampės gretasienio tūris 120 cm³. Pagrindo matmenys 4×5 cm. Rask aukštį.",
                skills=["prizmė", "tūris", "paviršiaus_plotas"],
            ),
            Subtopic(
                id="pyramid_8",
                name_lt="Piramidė",
                name_en="Pyramid",
                description="Piramidės tūris",
                satisfactory_requirements=[
                    "Atpažįsta piramidę",
                ],
                basic_requirements=[
                    "Taiko piramidės tūrio formulę V = Sh/3",
                ],
                advanced_requirements=[
                    "Sprendžia sudėtingus piramidės uždavinius",
                ],
                example_easy="Piramidės pagrindo plotas 24 cm², aukštis 9 cm. Rask tūrį.",
                example_medium="Taisyklingos keturkampės piramidės pagrindo kraštinė 6 cm, aukštis 8 cm. Rask tūrį.",
                example_hard="Piramidės tūris 200 cm³. Pagrindo plotas 60 cm². Rask aukštį.",
                skills=["piramidė", "tūris"],
            ),
        ],
    ),
    # --- STATISTIKA (8 klasė) ---
    Topic(
        id="probability_8",
        name_lt="Tikimybės ir kombinatorika",
        name_en="Probability and Combinatorics",
        content_area=ContentArea.STATISTICS,
        grade_introduced=8,
        grade_mastery=9,
        grades_available=[8, 9, 10],
        description="Tikimybių skaičiavimas, kombinatorikos elementai",
        importance=4,
        prerequisites=["probability_intro_7"],
        subtopics=[
            Subtopic(
                id="prob_rules_8",
                name_lt="Tikimybių taisyklės",
                name_en="Probability rules",
                description="Sudėties ir daugybos taisyklės",
                satisfactory_requirements=[
                    "Skaičiuoja paprastą tikimybę",
                ],
                basic_requirements=[
                    "Taiko priešingo įvykio tikimybę",
                    "Skaičiuoja nepriklausomų įvykių tikimybę",
                ],
                advanced_requirements=[
                    "Taiko sudėties ir daugybos taisykles",
                ],
                example_easy="Tikimybė laimėti 1/4. Kokia tikimybė nelaimėti?",
                example_medium="Metami du kauliukai. Kokia tikimybė išmesti du 6?",
                example_hard="Dėžėje 3 raudoni ir 2 mėlyni. Traukiami 2 kamuoliukai. Kokia tikimybė, kad abu raudoni?",
                skills=["tikimybių_taisyklės", "priešingas_įvykis"],
            ),
        ],
    ),
]


# =============================================================================
# 9-10 KLASĖ (I-II GIMNAZIJOS) - TURINIO SRITYS
# =============================================================================

GRADE_9_TOPICS = [
    # Kvadratinė funkcija (išsamus)
    Topic(
        id="quadratic_function_9",
        name_lt="Kvadratinė funkcija",
        name_en="Quadratic Function",
        content_area=ContentArea.ALGEBRA,
        grade_introduced=9,
        grade_mastery=10,
        grades_available=[9, 10],
        description="Funkcija y = ax² + bx + c, jos savybės",
        importance=5,
        prerequisites=["quadratic_equations_8", "linear_functions_8"],
        subtopics=[
            Subtopic(
                id="quad_func_graph",
                name_lt="Kvadratinės funkcijos grafikas",
                name_en="Graph of quadratic function",
                description="Parabolė, viršūnė, ašis, šaknys",
                satisfactory_requirements=[
                    "Braižo parabolę pagal taškų lentelę",
                ],
                basic_requirements=[
                    "Randa viršūnės koordinates",
                    "Nustato funkcijos šaknis",
                ],
                advanced_requirements=[
                    "Analizuoja funkcijos savybes pagal grafiką",
                    "Sprendžia optimizavimo uždavinius",
                ],
                example_easy="Nubraižyk y = x² grafiką",
                example_medium="Rask funkcijos y = x² - 4x + 3 viršūnę ir šaknis",
                example_hard="Stačiakampio perimetras 20 cm. Kokių matmenų jo plotas didžiausias?",
                skills=["parabolė", "viršūnė", "šaknys", "optimizavimas"],
            ),
        ],
    ),
    # Trigonometrija (įvadas)
    Topic(
        id="trigonometry_9",
        name_lt="Trigonometrija",
        name_en="Trigonometry",
        content_area=ContentArea.ALGEBRA,
        grade_introduced=9,
        grade_mastery=10,
        grades_available=[9, 10],
        description="sin, cos, tg stačiakampiame trikampyje",
        importance=5,
        prerequisites=["pythagorean_intro_7", "roots_8"],
        subtopics=[
            Subtopic(
                id="trig_right_triangle",
                name_lt="Trigonometrinės funkcijos stačiakampiame trikampyje",
                name_en="Trigonometric functions in right triangle",
                description="sin α, cos α, tg α apibrėžimai",
                satisfactory_requirements=[
                    "Žino sin, cos, tg apibrėžimus",
                    "Žino standartinių kampų (30°, 45°, 60°) reikšmes",
                ],
                basic_requirements=[
                    "Skaičiuoja nežinomas kraštines naudojant trigonometriją",
                    "Randa kampus pagal trigonometrines funkcijas",
                ],
                advanced_requirements=[
                    "Taiko trigonometriją sudėtingesnėse situacijose",
                    "Sprendžia praktinius matavimo uždavinius",
                ],
                example_easy="sin 30° = ?",
                example_medium="Stačiakampio trikampio įžambinė 10 cm, kampas 30°. Rask priešais esantį statinį.",
                example_hard="Nuo 20 m aukščio bokšto matymo kampas prie objekto yra 60°. Koks atstumas iki objekto?",
                skills=["sin", "cos", "tg", "stačiakampis_trikampis"],
            ),
        ],
    ),
]

GRADE_10_TOPICS = [
    # Trigonometrija (tęsinys)
    Topic(
        id="trigonometry_advanced_10",
        name_lt="Trigonometrija (tęsinys)",
        name_en="Advanced Trigonometry",
        content_area=ContentArea.ALGEBRA,
        grade_introduced=10,
        grade_mastery=10,
        grades_available=[10],
        description="Vienetinis apskritimas, trigonometrinės lygtys",
        importance=5,
        prerequisites=["trigonometry_9"],
        subtopics=[
            Subtopic(
                id="unit_circle",
                name_lt="Vienetinis apskritimas",
                name_en="Unit circle",
                description="Trigonometrinės funkcijos vienetiniame apskritime",
                satisfactory_requirements=[
                    "Supranta vienetinio apskritimo sąvoką",
                ],
                basic_requirements=[
                    "Randa trigonometrinių funkcijų reikšmes bet kokiam kampui",
                    "Taiko redukcijos formules",
                ],
                advanced_requirements=[
                    "Taiko pagrindines trigonometrines tapatybes",
                    "Sprendžia paprastas trigonometrines lygtis",
                ],
                example_easy="sin 120° = ?",
                example_medium="Supaprastink: sin²α + cos²α",
                example_hard="Išspręsk: sin x = 1/2, x ∈ [0°; 360°]",
                skills=["vienetinis_apskritimas", "redukcijos_formulės", "tapatybės"],
            ),
        ],
    ),
    # Progresijos
    Topic(
        id="progressions_10",
        name_lt="Progresijos",
        name_en="Progressions",
        content_area=ContentArea.ALGEBRA,
        grade_introduced=10,
        grade_mastery=10,
        grades_available=[10],
        description="Aritmetinė ir geometrinė progresijos",
        importance=5,
        prerequisites=["linear_functions_8", "powers_7"],
        subtopics=[
            Subtopic(
                id="arithmetic_prog",
                name_lt="Aritmetinė progresija",
                name_en="Arithmetic progression",
                description="n-tasis narys, suma",
                satisfactory_requirements=[
                    "Atpažįsta aritmetinę progresiją",
                    "Randa d ir a₁",
                ],
                basic_requirements=[
                    "Taiko n-tojo nario formulę aₙ = a₁ + (n-1)d",
                    "Skaičiuoja pirmųjų n narių sumą",
                ],
                advanced_requirements=[
                    "Sprendžia sudėtingus progresijų uždavinius",
                ],
                example_easy="3, 7, 11, 15, ... Koks d?",
                example_medium="a₁ = 5, d = 3. Rask a₁₀.",
                example_hard="Rask aritmetinės progresijos 2, 5, 8, ... pirmųjų 20 narių sumą.",
                skills=["aritmetinė_progresija", "n-tasis_narys", "suma"],
            ),
            Subtopic(
                id="geometric_prog",
                name_lt="Geometrinė progresija",
                name_en="Geometric progression",
                description="n-tasis narys, suma",
                satisfactory_requirements=[
                    "Atpažįsta geometrinę progresiją",
                    "Randa q ir b₁",
                ],
                basic_requirements=[
                    "Taiko n-tojo nario formulę bₙ = b₁ × qⁿ⁻¹",
                    "Skaičiuoja pirmųjų n narių sumą",
                ],
                advanced_requirements=[
                    "Sprendžia praktinius progresijų uždavinius (palūkanos)",
                ],
                example_easy="2, 6, 18, 54, ... Koks q?",
                example_medium="b₁ = 3, q = 2. Rask b₆.",
                example_hard="Įdėta 1000 € su 5% metinėmis palūkanomis. Kiek bus po 3 metų?",
                skills=["geometrinė_progresija", "n-tasis_narys", "palūkanos"],
            ),
        ],
    ),
    # Stereometrija (tęsinys)
    Topic(
        id="solid_geometry_10",
        name_lt="Erdvinės figūros (tęsinys)",
        name_en="Advanced Solid Geometry",
        content_area=ContentArea.GEOMETRY,
        grade_introduced=10,
        grade_mastery=10,
        grades_available=[10],
        description="Cilindras, kūgis, rutulys",
        importance=4,
        prerequisites=["solid_geometry_8", "circles_6"],
        subtopics=[
            Subtopic(
                id="cylinder_10",
                name_lt="Cilindras",
                name_en="Cylinder",
                description="Cilindro tūris ir paviršiaus plotas",
                satisfactory_requirements=[
                    "Atpažįsta cilindrą",
                ],
                basic_requirements=[
                    "Skaičiuoja cilindro tūrį V = πr²h",
                    "Skaičiuoja šoninio paviršiaus plotą",
                ],
                advanced_requirements=[
                    "Sprendžia sudėtingus cilindro uždavinius",
                ],
                example_easy="Cilindro r = 3 cm, h = 10 cm. Rask tūrį.",
                example_medium="Cilindro tūris 200π cm³. r = 5 cm. Rask h.",
                example_hard="Vandens stiklinė - cilindras r = 3 cm, h = 10 cm. Kiek litrų telpa?",
                skills=["cilindras", "tūris", "paviršius"],
            ),
            Subtopic(
                id="cone_sphere_10",
                name_lt="Kūgis ir rutulys",
                name_en="Cone and sphere",
                description="Kūgio ir rutulio tūriai",
                satisfactory_requirements=[
                    "Atpažįsta kūgį ir rutulį",
                ],
                basic_requirements=[
                    "Taiko formules V = πr²h/3 ir V = 4πr³/3",
                ],
                advanced_requirements=[
                    "Sprendžia praktinius uždavinius",
                ],
                example_easy="Rutulio r = 3 cm. Rask tūrį.",
                example_medium="Kūgio r = 6 cm, h = 8 cm. Rask tūrį.",
                example_hard="Ledų porcija - pusrutulis r = 3 cm ant kūgio r = 3 cm, h = 12 cm. Rask bendrą tūrį.",
                skills=["kūgis", "rutulys", "tūris"],
            ),
        ],
    ),
]


# =============================================================================
# PAGRINDINĖ STRUKTŪRA
# =============================================================================

# Visos klasės su jų temomis
CURRICULUM_BY_GRADE: Dict[int, GradeCurriculum] = {
    5: GradeCurriculum(
        grade=5,
        topics=GRADE_5_TOPICS,
        concentre_name="5-6 klasių koncentras",
        review_topics=[],
    ),
    6: GradeCurriculum(
        grade=6,
        topics=GRADE_6_TOPICS,
        concentre_name="5-6 klasių koncentras",
        # Atnaujinti topic ID pagal naują 5 klasės struktūrą
        review_topics=[
            "naturalieji_skaiciai_5",
            "paprastosios_trupmenos_5",
            "desimtaines_trupmenos_5",
        ],
    ),
    7: GradeCurriculum(
        grade=7,
        topics=GRADE_7_TOPICS,
        concentre_name="7-8 klasių koncentras",
        review_topics=[
            "fractions_operations_6",
            "percentages_6",
            "integers_6",
            "equations_6",
        ],
    ),
    8: GradeCurriculum(
        grade=8,
        topics=GRADE_8_TOPICS,
        concentre_name="7-8 klasių koncentras",
        review_topics=[
            "powers_7",
            "algebraic_expressions_7",
            "linear_equations_7",
            "quadrilaterals_7",
        ],
    ),
    9: GradeCurriculum(
        grade=9,
        topics=GRADE_9_TOPICS,
        concentre_name="9-10 klasių koncentras (I-II gimn.)",
        review_topics=[
            "quadratic_equations_8",
            "equation_systems_8",
            "linear_functions_8",
        ],
    ),
    10: GradeCurriculum(
        grade=10,
        topics=GRADE_10_TOPICS,
        concentre_name="9-10 klasių koncentras (I-II gimn.)",
        review_topics=["quadratic_function_9", "trigonometry_9"],
    ),
}


# =============================================================================
# PAGALBINĖS FUNKCIJOS
# =============================================================================
