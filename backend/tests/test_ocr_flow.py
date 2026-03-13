"""
Testas OCR srauto tikrinimui - ar visi puslapiai pasiekia frontend.
"""

import re

# Simuliuojame backend OCR rezultatą (20 užduočių su §§§ separatoriumi)
SAMPLE_LATEX = """1a) -52  \\cdot  (-\\frac{3}{13}) = 52  \\cdot  \\frac{3}{13} = \\frac{156}{13} = 12 Ats. 12§§§1b) 23  \\cdot  (-16) = ? Ats. -368§§§2a) \\frac{7}{15}  \\div  (-\\frac{14}{45}) = \\frac{7}{15}  \\cdot  (-\\frac{45}{14}) = -\\frac{3}{2} Ats. -1.5§§§2b) -\\frac{5}{6}  \\div  \\frac{25}{18} = -\\frac{5}{6}  \\cdot  \\frac{18}{25} = -\\frac{3}{5} Ats. -0.6§§§3a) -2.4  \\cdot  (-1.5) = 3.6 Ats. 3.6§§§3b) -4.8  \\div  1.2 = -4 Ats. -4§§§4a) -\\frac{3}{4} + \\frac{5}{6} = -\\frac{9}{12} + \\frac{10}{12} = \\frac{1}{12} Ats. 1/12§§§4b) \\frac{7}{10} - \\frac{3}{5} = \\frac{7}{10} - \\frac{6}{10} = \\frac{1}{10} Ats. 0.1§§§5a) 2.5 + (-3.7) = -1.2 Ats. -1.2§§§5b) -1.8 - (-2.3) = 0.5 Ats. 0.5§§§5c) (-\\frac{1}{2})^3 = -\\frac{1}{8} Ats. -1/8§§§5d) (-2)^4 = 16 Ats. 16§§§5e) -3^2 = -9 Ats. -9§§§6a) Stačiakampio plotis = 4.5 / 4 = 1.125 cm Ats. 1.125§§§6b) Perimetras = (4.5 + 1.125) * 2 = 11.25 cm Ats. 11.25§§§6c) Plotas = 4.5 * 1.125 = 5.0625 cm² Ats. 5.0625§§§7) (45ml + 11ml)  \\cdot  2 = 132ml Ats. 132"""


def test_separator_count():
    """Testas: ar yra teisingas separatorių skaičius"""
    sep_count = SAMPLE_LATEX.count("§§§")
    print(f"Separatorių skaičius: {sep_count}")
    print(f"Užduočių skaičius: {sep_count + 1}")
    # 17 užduočių = 16 separatorių
    assert sep_count == 16, f"Tikėtasi 16 separatorių, gauta {sep_count}"


def test_parse_tasks():
    """Testas: ar visos užduotys teisingai parsuojamos"""
    lines = SAMPLE_LATEX.split("§§§")
    print(f"\nRasta {len(lines)} eilučių:")

    task_ids = []
    for i, line in enumerate(lines):
        line = line.strip()
        # Ieškome task ID
        match = re.match(r"^\s*(\d+[a-z]?)\)", line, re.IGNORECASE)
        if match:
            task_id = match.group(1).lower()
            task_ids.append(task_id)
            print(f"  {i+1}. {task_id}) - {line[:50]}...")
        else:
            print(f"  {i+1}. [NO ID] - {line[:50]}...")

    print(f"\nRasta {len(task_ids)} užduočių ID: {task_ids}")

    # Tikriname ar yra visos užduotys
    expected = [
        "1a",
        "1b",
        "2a",
        "2b",
        "3a",
        "3b",
        "4a",
        "4b",
        "5a",
        "5b",
        "5c",
        "5d",
        "5e",
        "6a",
        "6b",
        "6c",
        "7",
    ]

    missing = set(expected) - set(task_ids)
    extra = set(task_ids) - set(expected)

    if missing:
        print(f"\n❌ TRŪKSTA: {missing}")
    if extra:
        print(f"\n⚠️ PAPILDOMOS: {extra}")

    assert len(task_ids) == 17, f"Tikėtasi 17 užduočių, gauta {len(task_ids)}"


def test_remove_inline_duplicates():
    """Testas: ar remove_inline_duplicates neištrina tikrų užduočių"""

    def remove_inline_duplicates(text: str) -> str:
        """Nauja versija - tikrina tik segmento pradžioje"""
        if not text:
            return text

        segments = text.split("§§§")
        seen_task_ids = set()
        unique_segments = []

        task_id_pattern = re.compile(r"^\s*(\d+[a-z]?)\)", re.IGNORECASE)

        for segment in segments:
            segment = segment.strip()
            if not segment:
                continue

            match = task_id_pattern.match(segment)
            if match:
                task_id = match.group(1).lower()
                if task_id in seen_task_ids:
                    print(f"  Pašalintas dublikatas: {task_id})")
                    continue
                seen_task_ids.add(task_id)

            unique_segments.append(segment)

        return "§§§".join(unique_segments)

    result = remove_inline_duplicates(SAMPLE_LATEX)

    original_count = SAMPLE_LATEX.count("§§§") + 1
    result_count = result.count("§§§") + 1

    print(f"\nOriginalus: {original_count} užduočių")
    print(f"Po valymo: {result_count} užduočių")

    # Tikriname ar 7 užduotis išliko
    assert "7)" in result, "Užduotis 7 buvo pašalinta!"
    assert (
        result_count == original_count
    ), f"Pašalinta {original_count - result_count} užduočių!"


def test_old_buggy_function():
    """Testas: ar sena funkcija klaidingai pašalina 7 užduotį"""

    def old_remove_inline_duplicates(text: str) -> str:
        """SENA BUGGY versija - tikrina visur"""
        if not text:
            return text

        task_pattern = re.compile(r"(\d+[a-z]?)\)", re.IGNORECASE)
        matches = list(task_pattern.finditer(text))

        if len(matches) <= 1:
            return text

        task_occurrences = {}
        for match in matches:
            task_id = match.group(1).lower()
            if task_id not in task_occurrences:
                task_occurrences[task_id] = []
            task_occurrences[task_id].append(match.start())

        # Parodome ką randa
        print("\nSena funkcija randa šiuos 'dublikatus':")
        for task_id, positions in task_occurrences.items():
            if len(positions) > 1:
                print(f"  {task_id}: {len(positions)} kartai pozicijose {positions}")

        return text  # Negrąžiname modifikuoto - tik parodome problemą

    old_remove_inline_duplicates(SAMPLE_LATEX)


if __name__ == "__main__":
    print("=" * 60)
    print("TEST 1: Separatorių skaičius")
    print("=" * 60)
    test_separator_count()

    print("\n" + "=" * 60)
    print("TEST 2: Užduočių parsavimas")
    print("=" * 60)
    test_parse_tasks()

    print("\n" + "=" * 60)
    print("TEST 3: Nauja remove_inline_duplicates funkcija")
    print("=" * 60)
    test_remove_inline_duplicates()

    print("\n" + "=" * 60)
    print("TEST 4: Senos funkcijos problema")
    print("=" * 60)
    test_old_buggy_function()

    print("\n" + "=" * 60)
    print("✅ VISI TESTAI PRAĖJO!")
    print("=" * 60)
