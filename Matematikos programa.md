{
  "document_meta": {
    "title": "Lietuvos bendrojo ugdymo mokyklų matematikos išplėstinė programa: Išsami turinio, kompetencijų ir vertinimo architektūros analizė skaitmeninių testavimo sistemų kūrimui",
    "file_source": "Lietuvos bendrojo ugdymo mokyklų matematikos išplėstinė programa.docx",
    "context": "Analizė skirta programinės įrangos architektams ir turinio kūrėjams adaptuoti sistemas pagal atnaujintas bendrąsias programas (BP 2022)."
  },
  "content": [
    {
      "section_id": "1",
      "title": "Įvadas: Ugdymo turinio atnaujinimo paradigma ir technologinė integracija",
      "text_content": "Lietuvos švietimo sistemoje vykstantys pokyčiai žymi posūkį nuo žinių akumuliacijos link kompetencijų ugdymo (ŠMSM įsakymas Nr. V-1269). Skaitmeninės priemonės turi būti adaptyvios ir pedagogiškai validžios. Analizė orientuota į 'išplėstinio' lygmens identifikavimą 5-12 klasėse.",
      "subsections": [
        {
          "subsection_id": "1.1",
          "title": "Kompetencijomis grįsto ugdymo implikacijos testavimo sistemoms",
          "description": "Naujoji programa išskiria šešias bendrąsias kompetencijas. Testų 'meta-duomenys' privalo apimti kompetencijos dedamąją.",
          "competency_matrix": [
            {
              "competency": "Pažinimo",
              "expression": "Kritinis mąstymas, problemų sprendimas, dėsningumų pastebėjimas.",
              "requirement": "Algoritmai turi generuoti ne tik standartines lygtis, bet ir uždavinius su trūkstamais duomenimis arba pertekline informacija."
            },
            {
              "competency": "Skaitmeninė",
              "expression": "Technologijų naudojimas skaičiavimams ir vaizdavimui.",
              "requirement": "Testai turi integruoti interaktyvias skaičiuokles arba reikalauti interpretuoti kompiuteriu gautus grafikus/duomenis."
            },
            {
              "competency": "Kūrybiškumo",
              "expression": "Nestandartinių sprendimo būdų paieška, modeliavimas.",
              "requirement": "'Open-ended' tipo užduotys, vertinamos pagal strategijos pasirinkimą."
            },
            {
              "competency": "Komunikavimo",
              "expression": "Matematinės kalbos vartojimas, argumentavimas.",
              "requirement": "Uždaviniai, kuriuose reikia pasirinkti teisingą paaiškinimą arba sudėlioti įrodymo žingsnius."
            },
            {
              "competency": "Kultūrinė",
              "expression": "Matematikos raida, istorinis kontekstas.",
              "requirement": "Kontekstiniai uždaviniai, susieti su mokslo istorija, architektūra."
            },
            {
              "competency": "Pilietinė",
              "expression": "Duomenų interpretavimas socialiniame kontekste.",
              "requirement": "Statistikos uždaviniai su realiais demografiniais/ekonominiais duomenimis."
            }
          ]
        }
      ]
    },
    {
      "section_id": "2",
      "title": "Vertinimo architektūra ir pasiekimų lygiai",
      "text_content": "Perėjimas prie kriterinio vertinimo. Testai turi būti subalansuoti pagal tris pasiekimų sritis.",
      "subsections": [
        {
          "subsection_id": "2.1",
          "title": "Pasiekimų sričių ir lygių sąveika",
          "areas": [
            {
              "name": "Žinios ir supratimas (Knowledge & Understanding)",
              "weight": "30-40%",
              "logic": "Standartinės procedūros, faktų atpažinimas. Lengvai automatizuojama keičiant skaitines reikšmes."
            },
            {
              "name": "Taikymas (Application)",
              "weight": "40-50%",
              "logic": "Žinomų metodų taikymas pakeistose situacijose. Reikalauja 'šablonų bibliotekos' (tekstiniai scenarijai)."
            },
            {
              "name": "Problemų sprendimas (Problem Solving)",
              "weight": "10-20% (Aukštesniajame iki 30%)",
              "logic": "Naujų strategijų kūrimas, įrodymai. Reikalauja 'kombinatorinio' generavimo (pvz., geometrija + algebra)."
            }
          ]
        },
        {
          "subsection_id": "2.2",
          "title": "Detalizuoti pasiekimų lygiai (1-4)",
          "levels_table": [
            {
              "level_name": "Slenkstinis",
              "score_val": 1,
              "descriptor": "Atpažįsta objektus, vieno žingsnio veiksmai su pagalba.",
              "test_rule": "Tiesioginis klausimas, pasirenkamasis atsakymas, vizualinė pagalba."
            },
            {
              "level_name": "Patenkinamas",
              "score_val": 2,
              "descriptor": "Supranta sąvokas, standartiniai algoritmai, paprasti tekstiniai uždaviniai.",
              "test_rule": "Standartinis uždavinys, 1-2 žingsniai."
            },
            {
              "level_name": "Pagrindinis",
              "score_val": 3,
              "descriptor": "Taikymas naujose situacijose, argumentavimas, analizė.",
              "test_rule": "Kompleksinis uždavinys (3-4 žingsniai), modelio sudarymas."
            },
            {
              "level_name": "Aukštesnysis",
              "score_val": "4+",
              "descriptor": "Abstrakčios sąvokos, nestandartiniai uždaviniai, įrodymai.",
              "test_rule": "'Olimpiadinio' tipo elementai, parametrinės lygtys, optimizavimas."
            }
          ]
        }
      ]
    },
    {
      "section_id": "3",
      "title": "5–6 Klasės: Adaptacija ir aritmetinis pagrindas",
      "text_content": "Latentinė diferenciacija. Fokusas į skaičių teoriją ir loginį mąstymą.",
      "subsections": [
        {
          "subsection_id": "3.1",
          "title": "Skaičiai ir skaičiavimai",
          "topics": [
            {
              "topic": "Natūralieji skaičiai",
              "advanced_focus": "Dalumo požymiai, pirminiai/sudėtiniai skaičiai, DBD/MBK tekstiniuose uždaviniuose.",
              "distractor_logic": "Veiksmų tvarkos klaidos."
            },
            {
              "topic": "Dešimtainės trupmenos",
              "advanced_focus": "Begalinės periodinės trupmenos, kablelio padėtis."
            },
            {
              "topic": "Paprastosios trupmenos",
              "advanced_focus": "Mišrieji skaičiai (netaisyklingos trupmenos vertimas), skirtingi vardikliai."
            }
          ]
        },
        {
          "subsection_id": "3.2",
          "title": "Algebra",
          "topics": [
            {
              "topic": "Raidiniai reiškiniai",
              "task_type": "Reiškinio sudarymas iš teksto."
            },
            {
              "topic": "Lygtys",
              "method": "Remiantis veiksmų tarp skaičių ryšiais (ne narių kilnojimu)."
            }
          ]
        },
        {
          "subsection_id": "3.3",
          "title": "Geometrija ir Matavimai",
          "topics": [
            {
              "topic": "Erdvinis mąstymas",
              "task_type": "Išklotinės lankstymas (mintinis), tūrio vs ploto painiojimas."
            }
          ]
        }
      ]
    },
    {
      "section_id": "4",
      "title": "7–8 Klasės: Algebraizacija ir Dedukcijos pradžia",
      "text_content": "Kritinis etapas atotrūkiui tarp A ir B lygių. Įrodymo uždaviniai, funkcinis mąstymas.",
      "subsections": [
        {
          "subsection_id": "4.1",
          "title": "Realiųjų skaičių aibės plėtra",
          "topics": [
            "Neigiami skaičiai (dvigubas minusas kaip distraktorius)",
            "Iracionalieji skaičiai (šaknys, apytikslis skaičiavimas, veiksmai su šaknimis aukštesniame lygyje)"
          ]
        },
        {
          "subsection_id": "4.2",
          "title": "Algebra: Nuo aritmetikos prie funkcijų",
          "topics": [
            "Tiesinės lygtys (išimtys: neturi sprendinių, be galo daug)",
            "Polinomai ir greitosios daugybos formulės (atvirkštinis taikymas - skaidymas)",
            "Funkcijos (Tiesinė y=kx+b, koeficientų prasmė)"
          ]
        },
        {
          "subsection_id": "4.3",
          "title": "Geometrija: Įrodymų era",
          "topics": [
            "Trikampių lygumo požymiai (KKK - distraktorius)",
            "Keturkampiai (hierarchija)",
            "Pitagoro teorema (taikymas erdvėje ar sudėtingose figūrose)"
          ]
        }
      ]
    },
    {
      "section_id": "5",
      "title": "9–10 Klasės: Pasirengimas PUPP ir Diferenciacijai",
      "text_content": "Diagnostinis ir egzaminacinis režimai. PUPP simuliacija.",
      "subsections": [
        {
          "subsection_id": "5.1",
          "title": "Funkcijos ir Analizės pradmenys",
          "topics": [
            "Kvadratinė funkcija (parabolės savybės, diskriminanto ženklo nustatymas iš grafiko)",
            "Funkcijų transformacijos (stumas vertikaliai/horizontaliai)"
          ]
        },
        {
          "subsection_id": "5.2",
          "title": "Lygtys ir nelygybės",
          "topics": [
            "Kvadratinės lygtys (Vijeto teorema, Bikvadratinės)",
            "Lygčių sistemos (tekstiniai uždaviniai)",
            "Kvadratinės nelygybės (intervalų metodas, ženklo keitimo klaidos)"
          ]
        },
        {
          "subsection_id": "5.3",
          "title": "Trigonometrija ir Geometrija",
          "topics": [
            "Trigonometrija stačiajame trikampyje",
            "Panašumas (plotų santykis k^2)",
            "Apskritimas (centriniai/įbrėžtiniai kampai)",
            "Stereometrija (kūnai, pjūviai)"
          ]
        },
        {
          "subsection_id": "5.4",
          "title": "PUPP Struktūra",
          "pupp_matrix": [
            { "area": "Skaičiai, algebra", "percent": "~40%" },
            { "area": "Geometrija, matavimai", "percent": "~35%" },
            { "area": "Duomenys, tikimybės", "percent": "~25%" }
          ],
          "note": "Būtina formulių lapo integracija."
        }
      ]
    },
    {
      "section_id": "6",
      "title": "Išplėstinis kursas (11–12 klasės): VBE lygmuo",
      "text_content": "Orientuota į STEM. Modulių įvedimas, privaloma planimetrija.",
      "subsections": [
        {
          "subsection_id": "6.2.A",
          "title": "Skaičiai, aibės, logika",
          "topics": "Matematinė logika, kvantoriai, įrodymo metodai (indukcija)."
        },
        {
          "subsection_id": "6.2.B",
          "title": "Funkcijos ir Analizės pradmenys (Calculus)",
          "importance": "40-50% VBE turinio",
          "topics": [
            "Išvestinės (taisyklės, sudėtinės f-jos, geometrinė/fizikinė prasmė, optimizavimas)",
            "Integralinis skaičiavimas (plotai, tūris)",
            "Rodiklinė ir Logaritminė funkcijos (apibrėžimo sritis, pagrindo keitimas)",
            "Trigonometrija (lygtys, sprendinių serijos)"
          ]
        },
        {
          "subsection_id": "6.2.C",
          "title": "Geometrija (Planimetrija ir Stereometrija)",
          "topics": [
            "Planimetrija: Sinusų/Kosinusų teoremos, apskritimai, plotų formulės.",
            "Stereometrija: Dvisieniai kampai, vektoriai erdvėje, briaunainiai."
          ]
        },
        {
          "subsection_id": "6.2.D",
          "title": "Stochastika",
          "topics": [
            "Kombinatorika (Gretiniai, Kėliniai, Deriniai)",
            "Tikimybės (Sąlyginė, Bajeso formulė, Bernulio schema)",
            "Statistika (Atsitiktiniai dydžiai, skirstiniai, normalusis skirstinys)"
          ]
        }
      ]
    },
    {
      "section_id": "7",
      "title": "Techninė specifikacija testų generavimo aplikacijai",
      "subsections": [
        {
          "subsection_id": "7.1",
          "title": "Duomenų modelis (Tagging)",
          "description": "Siūloma JSON struktūra uždaviniui.",
          "example_structure": {
            "id": "MAT-11-ALG-LOG-005",
            "grade": 11,
            "curriculum_type": "advanced",
            "topic_hierarchy": ["Algebra", "Logaritmai", "Logaritminės lygtys"],
            "cognitive_domain": "Problem Solving",
            "difficulty_level": 4,
            "competencies": [],
            "parameters": { "base": [], "argument_type": "quadratic" },
            "common_errors": []
          }
        },
        {
          "subsection_id": "7.2",
          "title": "Distraktorių variklis",
          "requirement": "Simuliuoti mąstymo klaidas (pvz., ženklo klaida, aritmetinė klaida), o ne atsitiktinius skaičius."
        },
        {
          "subsection_id": "7.3",
          "title": "Ilgalaikių planų integracija",
          "requirement": "Generuoti testus pagal standartinį mėnesio planą."
        },
        {
          "subsection_id": "7.4",
          "title": "Adaptyvumas (IRT)",
          "requirement": "Korekciniai takai klystantiems ir 'Mastery' takai pažengusiems."
        }
      ]
    },
    {
      "section_id": "8",
      "title": "Išvados",
      "summary": "Programa yra hierarchinė sistema. Aplikacija turi būti pedagoginis variklis, suprantantis kognityvinę raidą ir klaidų strategijas."
    }
  ]
}