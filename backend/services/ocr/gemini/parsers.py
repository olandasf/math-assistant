"""Gemini Vision OCR parsers and utilities."""
import json
import re
from loguru import logger
from typing import Optional


def clean_lithuanian_text(text: str) -> str:
    """Sutvarko sulūžusias lietuviškas raides ir šiukšles."""
    if not text:
        return ""

    # 1. Sutvarkom varneles ir nosines
    text = re.sub(r"c\s*[ˇv̌]", "č", text, flags=re.IGNORECASE)
    text = re.sub(r"s\s*[ˇv̌]", "š", text, flags=re.IGNORECASE)
    text = re.sub(r"z\s*[ˇv̌]", "ž", text, flags=re.IGNORECASE)
    text = re.sub(r"a\s*[˛̨]", "ą", text, flags=re.IGNORECASE)
    text = re.sub(r"e\s*[˛̨]", "ę", text, flags=re.IGNORECASE)
    text = re.sub(r"i\s*[˛̨]", "į", text, flags=re.IGNORECASE)
    text = re.sub(r"u\s*[˛̨]", "ų", text, flags=re.IGNORECASE)

    # 2. Specifinės teksto šiukšlės
    text = text.replace("Skaic ių", "Skaičių")
    text = text.replace("Skaic̆ių", "Skaičių")
    text = text.replace("skaič ių", "skaičių")
    text = text.replace("prieš ingą", "priešingą")
    text = text.replace("atvirkš tinį", "atvirkštinį")
    text = text.replace("Stač iakampio", "Stačiakampio")
    text = text.replace("Apskaič iuokite", "Apskaičiuokite")

    # 3. Svarbus pataisymas: [Mokinysnepateike˙sprendimo]
    text = text.replace("˙", "")
    text = text.replace("[Mokinysnepateiksprendimo]", "[Nėra sprendimo]")
    text = text.replace("[Mokinysnepateikesprendimo]", "[Nėra sprendimo]")
    text = re.sub(
        r"\[Mokinys\s*nepateik[eė]?\s*sprendimo\]",
        "[Nėra sprendimo]",
        text,
        flags=re.IGNORECASE,
    )

    # 4. Trupmenų sutvarkymas: 4 1/2 -> 4½
    text = text.replace(" 1/2", "½").replace(" 1/4", "¼").replace(" 3/4", "¾")

    # 5. Laipsnių sutvarkymas
    text = text.replace("^2", "²").replace("^3", "³")

    # 6. Minusų sutvarkymas
    text = text.replace(" - ", " – ")

    return text.strip()


def remove_inline_content_duplicates(text: str) -> str:
    """Pašalina inline turinio dublikatus iš student_work."""
    if not text or len(text) < 10:
        return text

    def normalize_for_comparison(s: str) -> str:
        s = s.replace("·", "*").replace("×", "*").replace("⋅", "*")
        s = s.replace("÷", "/").replace(":", "/")
        s = s.replace("−", "-").replace("–", "-")
        s = re.sub(r"\s+", "", s)
        return s.lower()

    normalized = normalize_for_comparison(text)
    text_len = len(normalized)

    for split_point in range(text_len // 2 - 5, text_len // 2 + 10):
        if split_point <= 0 or split_point >= text_len:
            continue

        first_half = normalized[:split_point]
        second_half = normalized[split_point:]

        min_len = min(len(first_half), len(second_half))
        if min_len < 5:
            continue

        common_start = 0
        for i in range(min(20, min_len)):
            if first_half[i] == second_half[i]:
                common_start = i + 1
            else:
                break

        if common_start >= 10:
            for i in range(len(text) // 2 - 10, len(text) // 2 + 20):
                if i <= 0 or i >= len(text):
                    continue

                first_part = text[:i]
                second_part = text[i:]

                first_norm = normalize_for_comparison(first_part)
                second_norm = normalize_for_comparison(second_part)

                if len(second_norm) >= 10 and len(first_norm) >= 10:
                    if first_norm[:10] == second_norm[:10]:
                        logger.info(f"🗑️ Pašalintas turinio dublikatas: '{text[i:i+30]}...'")
                        return first_part.strip()

    return text


def to_latex(text: str) -> str:
    """Konvertuoja ASCII matematiką į LaTeX."""
    if not text:
        return ""

    latex = text

    latex = latex.replace("·", r"\cdot ").replace("⋅", r"\cdot ").replace("*", r"\cdot ")
    latex = latex.replace("×", r"\times ")
    latex = latex.replace("÷", r"\div ")
    latex = latex.replace("–", "-").replace("−", "-")
    latex = latex.replace("½", "1/2").replace("¼", "1/4").replace("¾", "3/4")

    latex = re.sub(r"(\d+)\s+([1-9])/([1-9]+)", r"\1\frac{\2}{\3}", latex)
    latex = re.sub(r"([1-9])/([1-9]+)", r"\frac{\1}{\2}", latex)

    latex = latex.replace("²", "^2").replace("³", "^3")
    latex = re.sub(r"\^(\d+)", r"^{\1}", latex)
    latex = latex.replace("pi", r"\pi")

    latex = re.sub(r"(?<!\\)sqrt\(([^)]+)\)", r"\sqrt{\1}", latex)
    latex = latex.replace("sqrt", r"\sqrt")
    latex = latex.replace("<=", r"\le ").replace(">=", r"\ge ")
    latex = latex.replace("!=", r"\neq ")
    latex = latex.replace("...", r"\dots ")

    return latex.strip()


def remove_duplicate_tasks(latex_text: str) -> str:
    """Pašalina dublikuotas užduotis iš LaTeX teksto."""
    if not latex_text:
        return latex_text

    tasks = latex_text.split("§§§")
    unique_tasks = []
    seen_prefixes = set()

    for task in tasks:
        task = task.strip()
        if not task:
            continue

        match = re.match(r"^(\[conf:[\d.]+\]\s*\d+[a-z]?\))", task, re.IGNORECASE)
        if match:
            prefix = match.group(1).lower()
            if prefix not in seen_prefixes:
                seen_prefixes.add(prefix)
                unique_tasks.append(task)
            else:
                logger.info(f"🗑️ Pašalintas LaTeX dublikatas: {prefix}")
        else:
            if task not in unique_tasks:
                unique_tasks.append(task)

    return "§§§".join(unique_tasks)


def parse_response(response: str) -> tuple[str, Optional[str], bool]:
    """Išparsuoja Gemini atsakymą į tekstą ir LaTeX su post-processing valymu."""
    if not response:
        return "", None, False

    text = response
    latex = None
    is_math = False

    try:
        json_match = re.search(r"```json\s*(.*?)\s*```", response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        elif response.strip().startswith("{"):
            json_str = response.strip()
        elif "tasks" in response and "{" in response:
            start_idx = response.find("{")
            json_str = response[start_idx:].strip() if start_idx != -1 else None
        else:
            json_str = None

        if json_str:
            data = json.loads(json_str)
            tasks = data.get("tasks", [])

            if tasks:
                seen_numbers = set()
                unique_tasks = []
                for task in tasks:
                    raw_num = task.get("number", "")
                    num = re.sub(r"[\s\)\(\.\,]", "", str(raw_num)).lower().strip()
                    if num and num not in seen_numbers:
                        seen_numbers.add(num)
                        unique_tasks.append(task)
                    elif not num:
                        unique_tasks.append(task)

                tasks = unique_tasks

                text_lines = []
                latex_lines = []

                for task in tasks:
                    num = task.get("number", "").strip()
                    solution = task.get("student_work") or task.get("solution", "")
                    answer = task.get("final_answer") or task.get("answer")
                    question_text = task.get("question_text")
                    confidence = task.get("confidence", 0.5)

                    if solution == "?" or solution == "":
                        solution = "[Mokinys nepateikė sprendimo]"
                    else:
                        solution = clean_lithuanian_text(solution)
                        solution = remove_inline_content_duplicates(solution)

                    if question_text:
                        question_text = clean_lithuanian_text(question_text)

                    if question_text:
                        if answer:
                            task_text = f"{num}) {question_text} | {solution} Ats. {answer}"
                        else:
                            task_text = f"{num}) {question_text} | {solution}"
                    else:
                        if answer:
                            task_text = f"{num}) {solution} Ats. {answer}"
                        else:
                            task_text = f"{num}) {solution}"
                    text_lines.append(task_text)

                    latex_solution = to_latex(solution)
                    conf_prefix = f"[conf:{confidence:.2f}]"
                    if answer and "Ats" not in solution:
                        latex_line = f"{conf_prefix}{num}) {latex_solution} Ats. {answer}"
                    else:
                        latex_line = f"{conf_prefix}{num}) {latex_solution}"
                    latex_lines.append(latex_line)

                text = "\n".join(text_lines)
                latex = "§§§".join(latex_lines)
                is_math = True

                latex = remove_duplicate_tasks(latex)

                logger.info(f"JSON parsuotas: {len(tasks)} užduočių, latex separatorius: §§§")
                return text, latex, is_math

    except Exception as e:
        logger.debug(f"JSON parsavimas nepavyko: {e}")

    math_indicators = ["=", "+", "-", "×", "÷", "*", "/"]
    is_math = any(ind in response for ind in math_indicators)
    return text, None, is_math
