"""
Math Checker Router - Matematikos tikrinimo API
==============================================
Endpointai matematikos sprendimų tikrinimui ir paaiškinimams.
"""

from math_checker.wolfram_client import get_wolfram_client
from math_checker.geometry_checker import (
    CalculationType,
    GeometryChecker,
    GeometryShape,
)
from typing import List, Optional

from ai.gemini_client import GeminiClient, get_gemini_client
from fastapi import APIRouter, HTTPException
from loguru import logger
from math_checker.sympy_solver import MathSolver, to_latex


from fastapi import APIRouter
from .schemas import *
from .services import *

router = APIRouter(prefix="/math", tags=["math"])


@router.get("/status")
async def get_math_status():
    """
    Gauti matematikos tikrinimo sistemos statusą.
    """
    # SymPy visada veikia
    sympy_status = True

    # Gemini reikia patikrinti
    gemini_client = get_gemini_client()
    gemini_status = gemini_client.is_configured

    return {
        "sympy": {"available": sympy_status, "version": "1.x"},
        "gemini": {
            "available": gemini_status,
            "model": gemini_client.model if gemini_status else None,
        },
    }


@router.post("/check", response_model=CheckAnswerResponse)
async def check_math_answer(request: CheckAnswerRequest):
    """
    Patikrinti mokinio matematikos atsakymą.

    Palaikomi tipai:
    - equation: lygtys (2x + 5 = 11)
    - fraction: trupmenos (2/3, 3/4)
    - expression: išraiškos (2x + 3)
    """
    try:
        solver = MathSolver()

        # Tikrinti pagal tipą arba automatiškai
        if request.task_type == "fraction":
            result = solver.check_fraction(
                request.student_answer, request.correct_answer
            )
        elif request.task_type == "equation":
            result = solver.check_equation_solution(
                "x",  # default kintamasis
                request.student_answer,
                request.correct_answer,
            )
        else:
            # Bendrinis tikrinimas
            result = solver.check_equality(
                request.student_answer, request.correct_answer
            )

        # LaTeX versijos
        student_latex = to_latex(request.student_answer)
        correct_latex = to_latex(request.correct_answer)

        return CheckAnswerResponse(
            is_correct=result.result,
            message=result.message,
            student_value=result.student_value,
            expected_value=result.expected_value,
            student_latex=student_latex,
            correct_latex=correct_latex,
        )

    except Exception as e:
        logger.error(f"Klaida tikrinant atsakymą: {str(e)}")
        return CheckAnswerResponse(
            is_correct=False,
            message=f"Nepavyko patikrinti: {str(e)}",
            student_value=request.student_answer,
            expected_value=request.correct_answer,
        )


@router.post("/solve", response_model=SolveEquationResponse)
async def solve_equation(request: SolveEquationRequest):
    """
    Išspręsti lygtį.

    Pvz: "2x + 5 = 11" → ["3"]
    """
    try:
        solver = MathSolver()
        solutions = solver.solve_equation(request.equation, request.variable)

        if solutions:
            # Konvertuojame sprendinius į LaTeX
            solutions_latex = [to_latex(s) for s in solutions]

            return SolveEquationResponse(
                success=True,
                solutions=solutions,
                solutions_latex=solutions_latex,
                message=f"Lygtis išspręsta: {request.variable} = {', '.join(solutions)}",
            )
        else:
            return SolveEquationResponse(
                success=False,
                solutions=[],
                solutions_latex=[],
                message="Sprendinių nerasta",
            )

    except Exception as e:
        logger.error(f"Klaida sprendžiant lygtį: {str(e)}")
        return SolveEquationResponse(
            success=False,
            solutions=[],
            solutions_latex=[],
            message=f"Nepavyko išspręsti: {str(e)}",
        )


@router.post("/simplify", response_model=SimplifyResponse)
async def simplify_expression(request: SimplifyRequest):
    """
    Suprastinti matematinę išraišką.
    """
    try:
        solver = MathSolver()

        # Parse ir suprastinti
        expr = solver.parse_expression(request.expression)
        from sympy import simplify

        simplified = simplify(expr)

        return SimplifyResponse(
            success=True,
            simplified=str(simplified),
            simplified_latex=to_latex(str(simplified)),
            original_latex=to_latex(request.expression),
        )

    except Exception as e:
        logger.error(f"Klaida suprastinant: {str(e)}")
        return SimplifyResponse(
            success=False,
            simplified=request.expression,
            simplified_latex=to_latex(request.expression),
            original_latex=to_latex(request.expression),
        )


@router.post("/check-steps", response_model=CheckStepsResponse)
async def check_solution_steps(request: CheckStepsRequest):
    """
    Tikrinti mokinio sprendimo tarpinius žingsnius.

    Analizuoja kiekvieną žingsnį ir nustato, kur įvyko klaida.
    """
    try:
        solver = MathSolver()
        result = solver.check_solution_steps(
            steps=request.steps,
            expected_answer=request.expected_answer,
            task_type=request.task_type,
        )

        # Konvertuojame į StepDetail objektus
        step_details = []
        for step in result["step_details"]:
            step_details.append(
                StepDetail(
                    step_number=step["step_number"],
                    content=step["content"],
                    is_valid=step["is_valid"],
                    issue=step.get("issue"),
                    latex=step.get("latex"),
                )
            )

        return CheckStepsResponse(
            total_steps=result["total_steps"],
            valid_steps=result["valid_steps"],
            first_error_step=result.get("first_error_step"),
            step_details=step_details,
            final_correct=result["final_correct"],
            score=result["score"],
            message=result["message"],
        )

    except Exception as e:
        logger.error(f"Klaida tikrinant žingsnius: {str(e)}")
        return CheckStepsResponse(
            total_steps=len(request.steps),
            valid_steps=0,
            first_error_step=1,
            step_details=[],
            final_correct=False,
            score=0.0,
            message=f"Nepavyko patikrinti: {str(e)}",
        )


@router.post("/identify-error", response_model=IdentifyErrorResponse)
async def identify_error_type(request: IdentifyErrorRequest):
    """
    Identifikuoti klaidos tipą pagal mokinio ir teisingą atsakymą.

    Grąžina klaidos tipą su paaiškinimu lietuvių kalba.
    """
    try:
        solver = MathSolver()
        result = solver.identify_error_type(
            student_answer=request.student_answer,
            correct_answer=request.correct_answer,
            task_type=request.task_type,
        )

        return IdentifyErrorResponse(
            error_type=result["error_type"],
            description=result["description"],
            suggestion=result.get("suggestion"),
        )

    except Exception as e:
        logger.error(f"Klaida identifikuojant klaidos tipą: {str(e)}")
        return IdentifyErrorResponse(
            error_type="unknown",
            description=f"Nepavyko identifikuoti klaidos: {str(e)}",
            suggestion=None,
        )


@router.post("/explain-error", response_model=ExplainErrorResponse)
async def explain_math_error(request: ExplainErrorRequest):
    """
    Gauti AI paaiškinimą mokinio klaidai.

    Naudoja Gemini 2.5 Pro lietuvių kalba.
    """
    client = get_gemini_client()

    if not client.is_configured:
        return ExplainErrorResponse(
            success=False,
            explanation="AI paaiškinimai neprieinami - Gemini API raktas nenustatytas.",
            suggestions=[],
            error="API raktas nenustatytas. Eikite į Nustatymai → API raktai.",
        )

    try:
        result = await client.explain_math_error(
            problem=request.task_text,
            student_answer=request.student_answer,
            correct_answer=request.correct_answer,
            grade_level=request.grade_level,
        )

        return ExplainErrorResponse(
            success=result.success,
            explanation=result.explanation,
            suggestions=result.suggestions or [],
            error=result.error_type,
        )

    except Exception as e:
        logger.error(f"Klaida gaunant paaiškinimą: {str(e)}")
        return ExplainErrorResponse(
            success=False,
            explanation="Nepavyko gauti paaiškinimo.",
            suggestions=[],
            error=str(e),
        )


@router.post("/alternative-solutions", response_model=AlternativeSolutionsResponse)
async def get_alternative_solutions(request: AlternativeSolutionsRequest):
    """
    Gauti alternatyvius uždavinio sprendimo būdus.

    Grąžina 2-3 skirtingus būdus, kaip galima išspręsti tą patį uždavinį.
    Naudinga mokymosi tikslams - mokinys gali matyti skirtingus metodus.
    """
    client = get_gemini_client()

    if not client.is_configured:
        return AlternativeSolutionsResponse(
            success=False,
            solutions="",
            error="Gemini API raktas nenustatytas. Eikite į Nustatymai → API raktai.",
        )

    try:
        result = await client.generate_alternative_solutions(
            problem=request.problem,
            correct_answer=request.correct_answer,
            grade_level=request.grade_level,
            num_solutions=request.num_solutions,
        )

        if not result.success:
            return AlternativeSolutionsResponse(
                success=False,
                solutions="",
                error=result.error_type or "Nepavyko sugeneruoti sprendimų",
            )

        return AlternativeSolutionsResponse(
            success=True,
            solutions=result.explanation,
        )

    except Exception as e:
        logger.error(f"Klaida generuojant alternatyvius sprendimus: {str(e)}")
        return AlternativeSolutionsResponse(
            success=False,
            solutions="",
            error=str(e),
        )


@router.post("/analyze-steps", response_model=AnalyzeStepsResponse)
async def analyze_solution_steps(request: AnalyzeStepsRequest):
    """
    Analizuoti mokinio sprendimo žingsnius.
    """
    client = get_gemini_client()

    if not client.is_configured:
        return AnalyzeStepsResponse(
            success=False,
            analysis="AI analizė neprieinami.",
            issues=[],
            is_correct=False,
        )

    try:
        # Formuojame student_solution iš žingsnių
        student_solution = "\n".join(
            [f"{i+1}. {step}" for i, step in enumerate(request.steps)]
        )
        student_solution += f"\nGalutinis atsakymas: {request.final_answer}"

        result = await client.analyze_solution_steps(
            problem=request.task_text,
            student_solution=student_solution,
        )

        # Nustatyti ar teisingas pagal analizę
        is_correct = (
            "teisingai" in result.explanation.lower() and not result.suggestions
        )

        return AnalyzeStepsResponse(
            success=result.success,
            analysis=result.explanation,
            issues=result.suggestions,
            is_correct=is_correct,
        )

    except Exception as e:
        logger.error(f"Klaida analizuojant žingsnius: {str(e)}")
        return AnalyzeStepsResponse(
            success=False,
            analysis="Nepavyko atlikti analizės.",
            issues=[],
            is_correct=False,
        )


@router.post("/to-latex")
async def convert_to_latex(expression: str):
    """
    Konvertuoti išraišką į LaTeX formatą.
    """
    try:
        latex = to_latex(expression)
        return {"success": True, "original": expression, "latex": latex}
    except Exception as e:
        return {
            "success": False,
            "original": expression,
            "latex": expression,
            "error": str(e),
        }


@router.post("/batch-check")
async def batch_check_answers(answers: List[CheckAnswerRequest]):
    """
    Patikrinti kelis atsakymus vienu metu.
    """
    results = []
    solver = MathSolver()

    for answer in answers:
        try:
            result = solver.check_equality(answer.student_answer, answer.correct_answer)
            results.append(
                {
                    "is_correct": result.result,
                    "message": result.message,
                    "student_answer": answer.student_answer,
                    "correct_answer": answer.correct_answer,
                }
            )
        except Exception as e:
            results.append(
                {
                    "is_correct": False,
                    "message": f"Klaida: {str(e)}",
                    "student_answer": answer.student_answer,
                    "correct_answer": answer.correct_answer,
                }
            )

    correct_count = sum(1 for r in results if r["is_correct"])

    return {
        "results": results,
        "summary": {
            "total": len(results),
            "correct": correct_count,
            "incorrect": len(results) - correct_count,
            "percentage": (correct_count / len(results) * 100) if results else 0,
        },
    }


# === Geometrijos tikrinimas ===


@router.post("/geometry/check", response_model=GeometryCheckResponse)
async def check_geometry_answer(request: GeometryCheckRequest):
    """
    Patikrinti geometrijos atsakymą.

    Palaikomos figūros:
    - 2D: square, rectangle, triangle, circle, parallelogram, trapezoid, rhombus
    - 3D: cube, cuboid, cylinder, cone, sphere, pyramid, prism

    Skaičiavimo tipai:
    - area: plotas
    - perimeter: perimetras
    - volume: tūris
    - surface_area: paviršiaus plotas

    Pavyzdys:
    ```
    {
        "shape": "rectangle",
        "calculation_type": "area",
        "student_answer": "24",
        "params": {"a": 6, "b": 4}
    }
    ```
    """
    try:
        checker = GeometryChecker()

        # Konvertuojame string į enum
        try:
            shape = GeometryShape(request.shape.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Nežinoma figūra: {request.shape}. Palaikomos: {[s.value for s in GeometryShape]}",
            )

        try:
            calc_type = CalculationType(request.calculation_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Nežinomas skaičiavimo tipas: {request.calculation_type}. Palaikomi: {[c.value for c in CalculationType]}",
            )

        # Tikriname
        result = checker.calculate_and_check(
            shape=shape,
            calc_type=calc_type,
            student_answer=request.student_answer,
            **request.params,
        )

        return GeometryCheckResponse(
            is_correct=result.is_correct,
            message=result.message,
            expected_value=(
                float(result.expected_value)
                if isinstance(result.expected_value, (int, float))
                else 0
            ),
            student_value=(
                float(result.student_value)
                if isinstance(result.student_value, (int, float))
                else 0
            ),
            expected_formula=result.expected_formula,
            error_percentage=result.error_percentage,
            hint=result.hint,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Klaida tikrinant geometriją: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Klaida: {str(e)}")


@router.get(
    "/geometry/formula/{shape}/{calc_type}", response_model=GeometryFormulaResponse
)
async def get_geometry_formula(shape: str, calc_type: str):
    """
    Gauti geometrijos formulę.

    Pvz: /math/geometry/formula/rectangle/area
    """
    try:
        checker = GeometryChecker()

        try:
            shape_enum = GeometryShape(shape.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Nežinoma figūra: {shape}",
            )

        try:
            calc_enum = CalculationType(calc_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Nežinomas skaičiavimo tipas: {calc_type}",
            )

        formula = checker.get_formula(shape_enum, calc_enum)

        return GeometryFormulaResponse(
            formula=formula.get("formula", "Nežinoma"),
            description=formula.get("description", ""),
            params=formula.get("params", []),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Klaida gaunant formulę: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Klaida: {str(e)}")


# === Pilno darbo tikrinimas ===


@router.post("/check-full-work", response_model=FullWorkCheckResponse)
async def check_full_work(request: FullWorkCheckRequest):
    """
    Patikrinti pilną mokinio darbą.

    Priima LaTeX su sprendimais ir užduočių sąrašą,
    grąžina kiekvienos užduoties tikrinimo rezultatus.
    """
    logger.info(f"Tikrinamas pilnas darbas, užduočių: {len(request.tasks)}")

    solver = MathSolver()
    task_results = []
    total_points = 0.0
    max_points = 0.0

    # Išparsuojame LaTeX - ieškome atsakymų
    latex_content = request.latex_content

    for task_def in request.tasks:
        max_points += task_def.max_points

        # Bandome rasti mokinio atsakymą LaTeX
        student_answer = extract_answer_from_latex(latex_content, task_def.task_number)

        if student_answer is None:
            # Neradome atsakymo
            task_results.append(
                TaskResult(
                    task_number=task_def.task_number,
                    student_answer=None,
                    expected_answer=task_def.expected_answer,
                    is_correct=False,
                    points_earned=0,
                    max_points=task_def.max_points,
                    error_type="missing",
                    error_description="Atsakymas nerastas",
                )
            )
            continue

        try:
            # Tikrinimui naudojame MathSolver
            check_result = solver.check_equality(
                student_answer, task_def.expected_answer
            )

            is_correct = check_result.result
            points_earned = task_def.max_points if is_correct else 0

            # Jei neteisinga - analizuojame klaidą
            error_type = None
            error_desc = None
            suggestion = None

            if not is_correct:
                error_info = analyze_error(
                    student_answer, task_def.expected_answer, task_def.task_type
                )
                error_type = error_info.get("type", "calculation")
                error_desc = error_info.get("description", "Skaičiavimo klaida")
                suggestion = error_info.get("suggestion")

                # Daliniai taškai už teisingą metodą
                if "teisingas_metodas" in check_result.message.lower():
                    points_earned = task_def.max_points * 0.5

            total_points += points_earned

            task_results.append(
                TaskResult(
                    task_number=task_def.task_number,
                    student_answer=student_answer,
                    expected_answer=task_def.expected_answer,
                    is_correct=is_correct,
                    points_earned=points_earned,
                    max_points=task_def.max_points,
                    error_type=error_type,
                    error_description=error_desc,
                    suggestion=suggestion,
                )
            )

        except Exception as e:
            logger.error(f"Klaida tikrinant {task_def.task_number}: {e}")
            task_results.append(
                TaskResult(
                    task_number=task_def.task_number,
                    student_answer=student_answer,
                    expected_answer=task_def.expected_answer,
                    is_correct=False,
                    points_earned=0,
                    max_points=task_def.max_points,
                    error_type="system",
                    error_description=f"Sistemos klaida: {str(e)}",
                )
            )

    percentage = (total_points / max_points * 100) if max_points > 0 else 0
    correct_count = sum(1 for r in task_results if r.is_correct)

    summary = f"Teisingai: {correct_count}/{len(task_results)}, Taškai: {total_points}/{max_points} ({percentage:.0f}%)"

    return FullWorkCheckResponse(
        success=True,
        total_points=total_points,
        max_points=max_points,
        percentage=percentage,
        task_results=task_results,
        summary=summary,
    )


def extract_answer_from_latex(latex: str, task_number: str) -> Optional[str]:
    """
    Išgauti mokinio atsakymą iš LaTeX pagal užduoties numerį.

    Palaikomi formatai:
    - "1a) 3 * 18 = 54"
    - "1a. 3 * 18 = 54"
    - "a) 3 * 18 = 54" (kai task_number="1a", ieškome "a)" sekcijoje "1.")
    - "ats. 54" arba "atsakymas: 54"
    - LaTeX: "\\textbf{1.} ... a)\\ ... = 54"
    """
    import re

    task_num = task_number.lower().strip()

    # Bandome išskaidyti į sekcijos numerį ir sub-užduoties raidę
    # Pvz. "1a" -> section="1", letter="a"
    # Pvz. "2" -> section="2", letter=None
    section_match = re.match(r"(\d+)([a-z])?", task_num)
    if not section_match:
        return None

    section_num = section_match.group(1)
    letter = section_match.group(2)  # Gali būti None

    # ====== Strategija 1: Ieškome tiesiogiai visame LaTeX ======
    patterns_direct = []

    if letter:
        # "1a) ... = 54" arba "1a. ... = 54"
        patterns_direct.append(
            rf"{section_num}\s*{letter}\s*[\)\.\:]?\s*[^=\n]*?=\s*([\d\.,\-\+/\*\s]+)"
        )
        # "a) ... = 54" (tik raidė, bet po sekcijos numerio)
        patterns_direct.append(
            rf"(?:{section_num}[\.\:\)].*?)?{letter}\s*[\)\.\:]?\s*[^=\n]*?=\s*([\d\.,\-\+/\*\s]+)"
        )
    else:
        # Tiesiog numeris: "1. ... = 54" arba "1) ... = 54"
        patterns_direct.append(
            rf"\b{section_num}\s*[\)\.\:]?\s*[^=\n]*?=\s*([\d\.,\-\+/\*\s]+)"
        )

    # ====== Strategija 2: LaTeX formatas su \textbf arba sekcijomis ======
    # Pirmiausia bandome rasti sekciją, tada ieškome joje
    section_patterns = [
        rf"\\textbf\{{{section_num}\.\}}(.*?)(?=\\textbf\{{\d+\.\}}|$)",  # \textbf{1.}...
        rf"(?:^|\n)\s*{section_num}[\.\)]\s*(.*?)(?=(?:^|\n)\s*\d+[\.\)]|$)",  # 1. ... arba 1) ...
    ]

    for sec_pattern in section_patterns:
        sec_match = re.search(sec_pattern, latex, re.IGNORECASE | re.DOTALL)
        if sec_match:
            section_content = sec_match.group(1)

            if letter:
                # Ieškome raidės sekcijoje
                letter_patterns = [
                    rf"{letter}\s*[\)\.\:]?\s*[^=\n]*?=\s*([\d\.,\-\+/\*\s]+)",
                    rf"{letter}\s*[\)\.\:]\s*.*?ats\.?\s*([\d\.,\-\+/\*\s]+)",
                ]
                for lp in letter_patterns:
                    lmatch = re.search(lp, section_content, re.IGNORECASE)
                    if lmatch:
                        return _clean_answer(lmatch.group(1))
            else:
                # Jei nėra raidės, imame pirmą = po sekcijos
                simple_match = re.search(r"=\s*([\d\.,\-\+/\*\s]+)", section_content)
                if simple_match:
                    return _clean_answer(simple_match.group(1))

    # ====== Strategija 3: Tiesioginiai pattern'ai ======
    for pattern in patterns_direct:
        match = re.search(pattern, latex, re.IGNORECASE | re.MULTILINE)
        if match:
            return _clean_answer(match.group(1))

    # ====== Strategija 4: "ats." formatas ======
    if letter:
        ats_pattern = rf"{section_num}\s*{letter}[^\n]*?(?:ats\.?|atsakymas:?)\s*([\d\.,\-\+/\*\s]+)"
    else:
        ats_pattern = rf"\b{section_num}[\)\.\:]?[^\n]*?(?:ats\.?|atsakymas:?)\s*([\d\.,\-\+/\*\s]+)"

    ats_match = re.search(ats_pattern, latex, re.IGNORECASE)
    if ats_match:
        return _clean_answer(ats_match.group(1))

    return None


def _clean_answer(answer: str) -> str:
    """
    Išvalo atsakymą - pašalina matavimo vienetus ir nereikalingus simbolius.
    """
    import re

    answer = answer.strip()

    # Pašaliname LaTeX simbolius
    answer = answer.replace("\\", "").replace("{", "").replace("}", "")
    answer = answer.replace("\\cdot", "*").replace("\\times", "*")

    # Pašaliname matavimo vienetus
    answer = re.sub(
        r"\s*(km|m|cm|mm|l|ml|kg|g|mg|h|val|min|sek|s|lt|eur|€|%)\s*$",
        "",
        answer,
        flags=re.IGNORECASE,
    )

    # Pašaliname skliaustus pabaigoje
    answer = re.sub(r"[\(\)\[\]]+$", "", answer)

    # Pašaliname tarpus
    answer = answer.strip()

    # Jei liko tik skaičiai ir operatoriai, grąžiname
    if re.match(r"^[\d\.,\-\+/\*\s]+$", answer):
        return answer.strip()

    return answer.strip()


def analyze_error(student: str, expected: str, task_type: str) -> dict:
    """
    Analizuoti klaidos tipą ir pateikti išsamų paaiškinimą lietuvių kalba.

    Klaidų tipai:
    - digit_swap: Skaitmenų sukeitimo klaida (54 vietoj 45)
    - decimal: Kablelio klaida (10x skirtumas)
    - sign: Ženklo klaida (-5 vietoj 5)
    - rounding: Apvalinimo klaida (artimas atsakymas)
    - arithmetic: Aritmetikos klaida (sudėtis, atimtis, daugyba, dalyba)
    - calculation: Bendrinė skaičiavimo klaida
    - format: Netinkamas formatas
    """
    try:
        # Normalizuojame įvestį
        student_clean = student.replace(",", ".").replace(" ", "").strip()
        expected_clean = expected.replace(",", ".").replace(" ", "").strip()

        student_val = float(student_clean)
        expected_val = float(expected_clean)

        diff = abs(student_val - expected_val)

        # ===== 1. Ženklo klaida =====
        if student_val == -expected_val:
            return {
                "type": "sign",
                "description": "Ženklo klaida - atsakymas priešingo ženklo",
                "suggestion": "Atidžiai patikrink + ir - ženklus. Teisingas atsakymas: "
                + expected,
            }

        # ===== 2. Skaitmenų sukeitimo klaida =====
        try:
            student_int = int(abs(student_val))
            expected_int = int(abs(expected_val))
            if len(str(student_int)) == len(str(expected_int)) >= 2:
                if str(student_int)[::-1] == str(expected_int):
                    return {
                        "type": "digit_swap",
                        "description": f"Skaitmenų sukeitimo klaida: parašei {student}, o turėjo būti {expected}",
                        "suggestion": "Atidžiai patikrink skaitmenis ir jų tvarką",
                    }
                # Ar tik vienas skaitmuo sukeistas?
                diff_count = sum(
                    a != b for a, b in zip(str(student_int), str(expected_int))
                )
                if diff_count == 2:
                    return {
                        "type": "digit_swap",
                        "description": f"Atrodo, kad du skaitmenys sukeisti vietomis",
                        "suggestion": f"Teisingas atsakymas: {expected}. Patikrink ar teisingai perrašei",
                    }
        except (ValueError, TypeError):
            pass

        # ===== 3. Kablelio/10x klaida =====
        if expected_val != 0:
            ratio = student_val / expected_val
            if abs(ratio - 10) < 0.01:
                return {
                    "type": "decimal",
                    "description": "Atsakymas 10 kartų per didelis",
                    "suggestion": f"Patikrink kablelio vietą. Teisingas atsakymas: {expected}",
                }
            if abs(ratio - 0.1) < 0.01:
                return {
                    "type": "decimal",
                    "description": "Atsakymas 10 kartų per mažas",
                    "suggestion": f"Patikrink kablelio vietą. Teisingas atsakymas: {expected}",
                }
            if abs(ratio - 100) < 0.01:
                return {
                    "type": "decimal",
                    "description": "Atsakymas 100 kartų per didelis",
                    "suggestion": f"Patikrink skaičiavimus su dešimtainiais. Teisingas atsakymas: {expected}",
                }
            if abs(ratio - 0.01) < 0.001:
                return {
                    "type": "decimal",
                    "description": "Atsakymas 100 kartų per mažas",
                    "suggestion": f"Patikrink skaičiavimus su dešimtainiais. Teisingas atsakymas: {expected}",
                }

        # ===== 4. Apvalinimo klaida (artimas atsakymas) =====
        if expected_val != 0:
            error_pct = abs(diff / expected_val) * 100
            if error_pct < 2:
                return {
                    "type": "rounding",
                    "description": f"Labai artimas atsakymas (skirtumas tik {error_pct:.1f}%)",
                    "suggestion": f"Atsakymas beveik teisingas! Tikslus atsakymas: {expected}",
                }
            if error_pct < 5:
                return {
                    "type": "rounding",
                    "description": f"Artimas atsakymas, bet yra apvalinimo klaida",
                    "suggestion": f"Patikrink apvalinimą. Teisingas atsakymas: {expected}",
                }

        # ===== 5. Aritmetikos klaida (pagal task_type) =====
        if task_type in ["addition", "sudėtis"]:
            return {
                "type": "arithmetic",
                "description": f"Sudėties klaida: {student} ≠ {expected}",
                "suggestion": f"Patikrink ar teisingai sudėjai. Teisingas atsakymas: {expected}",
            }
        if task_type in ["subtraction", "atimtis"]:
            return {
                "type": "arithmetic",
                "description": f"Atimties klaida: {student} ≠ {expected}",
                "suggestion": f"Patikrink ar teisingai atėmei. Teisingas atsakymas: {expected}",
            }
        if task_type in ["multiplication", "daugyba"]:
            return {
                "type": "arithmetic",
                "description": f"Daugybos klaida: {student} ≠ {expected}",
                "suggestion": f"Patikrink daugybos lentelę. Teisingas atsakymas: {expected}",
            }
        if task_type in ["division", "dalyba"]:
            return {
                "type": "arithmetic",
                "description": f"Dalybos klaida: {student} ≠ {expected}",
                "suggestion": f"Patikrink dalybą. Teisingas atsakymas: {expected}",
            }

        # ===== 6. Bendrinė skaičiavimo klaida =====
        return {
            "type": "calculation",
            "description": f"Skaičiavimo klaida: {student} ≠ {expected}",
            "suggestion": f"Teisingas atsakymas: {expected}. Patikrink skaičiavimus žingsnis po žingsnio.",
        }

    except ValueError:
        return {
            "type": "format",
            "description": "Netinkamas atsakymo formatas",
            "suggestion": "Įsitikink, kad atsakymas yra skaičius be papildomų simbolių",
        }


@router.get("/geometry/shapes")
async def list_geometry_shapes():
    """
    Gauti visų palaikomų figūrų sąrašą.
    """
    return {
        "2d_shapes": [
            {"value": "square", "label": "Kvadratas"},
            {"value": "rectangle", "label": "Stačiakampis"},
            {"value": "triangle", "label": "Trikampis"},
            {"value": "circle", "label": "Apskritimas"},
            {"value": "parallelogram", "label": "Lygiagretainis"},
            {"value": "trapezoid", "label": "Trapecija"},
            {"value": "rhombus", "label": "Rombas"},
        ],
        "3d_shapes": [
            {"value": "cube", "label": "Kubas"},
            {"value": "cuboid", "label": "Stačiakampis gretasienis"},
            {"value": "cylinder", "label": "Cilindras"},
            {"value": "cone", "label": "Kūgis"},
            {"value": "sphere", "label": "Rutulys"},
            {"value": "pyramid", "label": "Piramidė"},
            {"value": "prism", "label": "Prizmė"},
        ],
        "calculation_types": [
            {"value": "area", "label": "Plotas"},
            {"value": "perimeter", "label": "Perimetras"},
            {"value": "volume", "label": "Tūris"},
            {"value": "surface_area", "label": "Paviršiaus plotas"},
        ],
    }


# === AUTOMATINIS TIKRINIMAS BE IŠ ANKSTO NUSTATYTŲ ATSAKYMŲ ===


@router.post("/check-auto", response_model=AutoCheckResponse)
async def check_auto(request: AutoCheckRequest):
    """
    Automatiškai patikrinti mokinio darbą BE iš anksto nustatytų atsakymų.

    Sistema:
    1. Išparsuoja LaTeX ir randa užduotis
    2. Nustato matematinius veiksmus
    3. Pati apskaičiuoja teisingus atsakymus
    4. Palygina su mokinio atsakymais
    """
    logger.info(f"Automatinis tikrinimas, klasė: {request.grade_level}")

    # DEBUG: Log incoming LaTeX
    latex_len = len(request.latex_content) if request.latex_content else 0
    sep_count = request.latex_content.count("§§§") if request.latex_content else 0
    logger.info(f"📥 check-auto: latex_length={latex_len}, separator_count={sep_count}")
    if request.latex_content:
        logger.debug(f"📥 check-auto first 300 chars: {request.latex_content[:300]}")
        logger.debug(f"📥 check-auto last 300 chars: {request.latex_content[-300:]}")

    solver = MathSolver()
    task_results = []

    try:
        # 1. Parsuojame LaTeX ir randame užduotis
        parsed_tasks = parse_latex_tasks(request.latex_content)
        logger.info(f"Rasta {len(parsed_tasks)} užduočių")

        # DEBUG: Log parsed task IDs
        task_ids = [t.get("id", "?") for t in parsed_tasks]
        logger.info(f"📋 Parsed task IDs: {task_ids}")

        if not parsed_tasks:
            # Bandome su Gemini AI
            gemini = get_gemini_client()
            if gemini:
                ai_result = await analyze_work_with_ai(
                    gemini, request.latex_content, request.grade_level
                )
                if ai_result:
                    return ai_result

            return AutoCheckResponse(
                success=False,
                task_results=[],
                total_tasks=0,
                correct_count=0,
                incorrect_count=0,
                unknown_count=0,
                summary="Nerasta jokių užduočių. Patikrinkite ar OCR teisingai atpažino tekstą.",
            )

        correct_count = 0
        incorrect_count = 0
        unknown_count = 0

        for task in parsed_tasks:
            task_id = task["id"]
            student_solution = task.get("solution", "")
            student_answer = task.get("answer", "")

            # 1. Bandome patys apskaičiuoti su SymPy
            try:
                (
                    calculated,
                    is_correct,
                    error_desc,
                    suggestion,
                    error_analysis,
                    solution_methods,
                ) = check_calculation(solver, student_solution, student_answer)

                logger.info(
                    f"Task {task_id}: check_calculation returned is_correct={is_correct}, solution_methods={len(solution_methods) if solution_methods else 0}"
                )
            except Exception as calc_error:
                logger.error(
                    f"Task {task_id}: check_calculation exception: {calc_error}"
                )
                calculated = None
                is_correct = None
                error_desc = str(calc_error)
                suggestion = None
                error_analysis = None
                solution_methods = []

            # 2. Jei SymPy nepavyko - bandome WolframAlpha
            if is_correct is None and student_solution:
                import re

                # Ištraukiame išraišką prieš = ženklą
                expr_match = re.search(
                    r"^([\d\s+\-*/().×·÷:]+)\s*=", student_solution.strip()
                )
                if expr_match:
                    expression = expr_match.group(1).strip()
                    expression = (
                        expression.replace("×", "*")
                        .replace("·", "*")
                        .replace("÷", "/")
                        .replace(":", "/")
                    )

                    wolfram_calc, wolfram_correct, wolfram_error, wolfram_sugg = (
                        await check_with_wolfram(expression, student_answer)
                    )

                    if wolfram_correct is not None:
                        calculated = wolfram_calc
                        is_correct = wolfram_correct
                        error_desc = wolfram_error
                        suggestion = wolfram_sugg
                        logger.info(f"WolframAlpha patikrintas {task_id}: {is_correct}")

            if is_correct is None:
                unknown_count += 1
            elif is_correct:
                correct_count += 1
            else:
                incorrect_count += 1

            # Konvertuojame error_analysis ir solution_methods į Pydantic modelius
            error_analysis_model = None
            if error_analysis:
                error_analysis_model = ErrorAnalysis(
                    error_type=error_analysis.get("error_type", "calculation"),
                    error_location=error_analysis.get("error_location", ""),
                    what_went_wrong=error_analysis.get("what_went_wrong", ""),
                    why_wrong=error_analysis.get("why_wrong", ""),
                    how_to_fix=error_analysis.get("how_to_fix", ""),
                )

            solution_methods_models = []
            if solution_methods:
                logger.debug(
                    f"Task {task_id}: solution_methods count = {len(solution_methods)}"
                )
                for method in solution_methods:
                    steps = [
                        SolutionStep(
                            step_number=s.get("step_number", 0),
                            description=s.get("description", ""),
                            expression=s.get("expression", ""),
                            result=s.get("result"),
                        )
                        for s in method.get("steps", [])
                    ]
                    solution_methods_models.append(
                        SolutionMethod(
                            method_name=method.get("method_name", ""),
                            steps=steps,
                            final_answer=method.get("final_answer", ""),
                        )
                    )
                logger.debug(
                    f"Task {task_id}: solution_methods_models count = {len(solution_methods_models)}"
                )
            else:
                logger.debug(f"Task {task_id}: solution_methods is empty or None")

            task_results.append(
                AutoTaskResult(
                    task_id=task_id,
                    task_text=task.get("text", ""),
                    student_solution=student_solution,
                    student_answer=student_answer,
                    calculated_answer=calculated,
                    is_correct=is_correct,
                    error_description=error_desc,
                    error_analysis=error_analysis_model,
                    solution_methods=solution_methods_models,
                    suggestion=suggestion,
                    confidence=task.get("confidence", 0.5),  # OCR confidence
                )
            )

        # === AI PAAIŠKINIMŲ GENERAVIMAS ===
        # Generuojame išsamius paaiškinimus neteisingoms IR neatsakytoms užduotims naudojant Gemini Pro
        import asyncio

        async def generate_ai_explanation_for_task(
            task_result: AutoTaskResult,
            original_task_text: str,
        ) -> AutoTaskResult:
            """Generuoja AI paaiškinimą vienai užduočiai."""
            # Tik neteisingoms arba neatsakytoms užduotims
            if task_result.is_correct == True:
                return task_result

            try:
                gemini = get_gemini_client()
                if not gemini or not gemini.is_configured:
                    return task_result

                # Nustatome ar mokinys pateikė atsakymą
                has_student_answer = bool(
                    task_result.student_answer
                    and task_result.student_answer.strip()
                    and task_result.student_answer.strip() not in ["?", ""]
                )

                # Problema - naudojame originalų užduoties tekstą jei nėra sprendimo
                # Išvalome "[Nėra sprendimo]" iš teksto
                student_sol = task_result.student_solution or ""
                if "[Nėra sprendimo]" in student_sol:
                    student_sol = ""  # Ignoruojame nes tai ne tikras sprendimas

                problem_text = (
                    student_sol
                    or original_task_text
                    or task_result.task_text
                    or f"Užduotis {task_result.task_id}"
                )

                logger.debug(
                    f"AI paaiškinimas {task_result.task_id}: problem='{problem_text[:50]}...', no_answer={not has_student_answer}"
                )

                result = await gemini.generate_detailed_solution_with_thinking(
                    problem=problem_text,
                    student_answer=(
                        task_result.student_answer if has_student_answer else None
                    ),
                    correct_answer=task_result.calculated_answer,
                    is_correct=task_result.is_correct == True,
                    grade_level=request.grade_level,
                    no_student_answer=not has_student_answer,
                )

                if result.success and result.explanation:
                    # Pridedame AI paaiškinimą prie suggestion
                    task_result.suggestion = result.explanation
                    logger.info(
                        f"✅ AI paaiškinimas sugeneruotas užduočiai {task_result.task_id}"
                    )
                else:
                    logger.warning(
                        f"⚠️ AI paaiškinimas nepavyko {task_result.task_id}: {result.error_type}"
                    )

            except Exception as e:
                logger.warning(
                    f"AI paaiškinimo generavimas nepavyko {task_result.task_id}: {e}"
                )

            return task_result

        # Sukuriame žodyną su originaliais užduočių tekstais
        task_id_to_text = {
            task["id"]: task.get("text", task.get("solution", ""))
            for task in parsed_tasks
        }

        # Generuojame paaiškinimus tik NETEISINGOMS užduotims
        # Taip pat pridedame neatsakytas užduotis kur yra užduoties tekstas
        tasks_needing_explanation = []
        for t in task_results:
            if t.is_correct == False:
                # Neteisinga - reikia paaiškinimo
                tasks_needing_explanation.append(t)
            elif t.is_correct is None:
                # Neatsakyta/nepatikrinta - patikriname ar yra užduoties duomenų
                has_task_data = bool(
                    t.task_text
                    or t.student_solution
                    or task_id_to_text.get(t.task_id, "")
                )
                if has_task_data:
                    tasks_needing_explanation.append(t)
                    logger.debug(
                        f"Pridėta neatsakyta užduotis {t.task_id} paaiškinimui"
                    )

        logger.info(
            f"📊 Užduočių reikalaujančių paaiškinimo: {len(tasks_needing_explanation)} (iš {len([t for t in task_results if t.is_correct != True])} neteisingų/unknown)"
        )

        # Limituojame iki 5 užduočių
        tasks_to_explain = tasks_needing_explanation[:5]

        if tasks_to_explain:
            logger.info(
                f"🧠 Generuojami AI paaiškinimai {len(tasks_to_explain)} užduotims (iš {len(tasks_needing_explanation)} reikalaujančių)..."
            )

            # Lygiagretus generavimas su timeout (60 sek max)
            try:
                updated_tasks = await asyncio.wait_for(
                    asyncio.gather(
                        *[
                            generate_ai_explanation_for_task(
                                t, task_id_to_text.get(t.task_id, "")
                            )
                            for t in tasks_to_explain
                        ],
                        return_exceptions=True,
                    ),
                    timeout=60.0,  # 60 sekundžių timeout
                )
            except asyncio.TimeoutError:
                logger.warning(
                    "⏱️ AI paaiškinimų generavimas užtruko per ilgai, praleidžiama"
                )
                updated_tasks = []

            # Loguojame rezultatus
            for i, result in enumerate(updated_tasks):
                if isinstance(result, Exception):
                    logger.error(f"❌ AI paaiškinimo klaida užduočiai {i}: {result}")
                elif isinstance(result, AutoTaskResult):
                    if result.suggestion:
                        logger.info(f"✅ AI paaiškinimas gautas: {result.task_id}")
                    else:
                        logger.warning(f"⚠️ AI paaiškinimas tuščias: {result.task_id}")

            # Atnaujiname task_results su AI paaiškinimais
            if updated_tasks:
                task_id_to_updated = {
                    t.task_id: t for t in updated_tasks if isinstance(t, AutoTaskResult)
                }

                task_results = [
                    (
                        task_id_to_updated.get(t.task_id, t)
                        if t.task_id in task_id_to_updated
                        else t
                    )
                    for t in task_results
                ]

        total = len(task_results)
        summary = f"Patikrinta {total} užduočių: ✅ {correct_count} teisingai, ❌ {incorrect_count} neteisingai"
        if unknown_count > 0:
            summary += f", ❓ {unknown_count} negalėjome patikrinti"

        return AutoCheckResponse(
            success=True,
            task_results=task_results,
            total_tasks=total,
            correct_count=correct_count,
            incorrect_count=incorrect_count,
            unknown_count=unknown_count,
            summary=summary,
        )

    except Exception as e:
        logger.error(f"Automatinio tikrinimo klaida: {e}")

        # Fallback: Bandome su Gemini AI
        gemini = get_gemini_client()
        if gemini:
            try:
                ai_result = await analyze_work_with_ai(
                    gemini, request.latex_content, request.grade_level
                )
                if ai_result:
                    return ai_result
            except Exception as ai_error:
                logger.error(f"AI analizės klaida: {ai_error}")

        return AutoCheckResponse(
            success=False,
            task_results=[],
            total_tasks=0,
            correct_count=0,
            incorrect_count=0,
            unknown_count=0,
            summary=f"Tikrinimo klaida: {str(e)}",
        )


# === Išsamus paaiškinimas su Thinking režimu ===


@router.post("/detailed-explanation", response_model=DetailedExplanationResponse)
async def get_detailed_explanation(request: DetailedExplanationRequest):
    """
    Gauti išsamų uždavinio paaiškinimą su Gemini Pro Thinking režimu.

    Naudoja gemini-3-pro-preview su thinking_budget kad AI galėtų
    "pagalvoti" prieš atsakant - tai duoda kokybiškesnius paaiškinimus.

    Grąžina:
    - Jei teisingas: paaiškinimą kodėl teisinga + alternatyvius sprendimo būdus
    - Jei neteisingas: klaidos analizę + teisingą sprendimą + patarimus
    """
    logger.info(
        f"📚 Generuojamas išsamus paaiškinimas: is_correct={request.is_correct}, "
        f"problem={request.problem[:50]}..."
    )

    gemini = get_gemini_client()

    if not gemini or not gemini.is_configured:
        return DetailedExplanationResponse(
            success=False,
            explanation="",
            error="Gemini API nesukonfigūruotas",
        )

    try:
        result = await gemini.generate_detailed_solution_with_thinking(
            problem=request.problem,
            student_answer=request.student_answer,
            correct_answer=request.correct_answer,
            is_correct=request.is_correct,
            grade_level=request.grade_level,
        )

        if result.success:
            logger.info(
                f"✅ Išsamus paaiškinimas sugeneruotas: {len(result.explanation)} simbolių"
            )
            return DetailedExplanationResponse(
                success=True,
                explanation=result.explanation,
            )
        else:
            return DetailedExplanationResponse(
                success=False,
                explanation="",
                error=result.error_type or "Nepavyko sugeneruoti paaiškinimo",
            )

    except Exception as e:
        logger.error(f"Išsamaus paaiškinimo klaida: {e}")
        return DetailedExplanationResponse(
            success=False,
            explanation="",
            error=str(e),
        )


def parse_latex_tasks(latex: str) -> List[dict]:
    """
    Išparsuoja LaTeX turinį ir grąžina užduočių sąrašą.

    Palaikomi formatai:
    - "1. a) 3*18=54 ats. 54"
    - "a) 3*18=54 ats. 54 b) 51:3=17 ats. 17"
    - "\\textbf{1.} a)\\ 3 \\cdot 18 = 54"
    - "1a) 3*18=54"
    - Eilutėmis atskirti: "a) ...\nb) ..."
    - Su §§§ separatoriumi: "1a) ... §§§ 1b) ... §§§ 2a) ..."
    - Tik raidės be skaičių: "c) ..." → priskiriama paskutiniam žinomam numeriui
    """
    import re

    tasks = []
    last_task_number = "5"  # Default jei randame tik raides be skaičių

    # === PIRMA: Tikriname ar yra §§§ separatorius ===
    if "§§§" in latex:
        logger.info(
            "parse_latex_tasks: rastas §§§ separatorius, naudojame naują logiką"
        )
        lines = latex.split("§§§")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Ištraukiame confidence jei yra [conf:0.85] pradžioje
            confidence = 0.5  # Default
            conf_match = re.match(r"^\[conf:(\d+\.?\d*)\](.*)", line)
            if conf_match:
                confidence = float(conf_match.group(1))
                line = conf_match.group(2).strip()

            # Normalizuojame šią eilutę
            normalized_line = line
            normalized_line = re.sub(r"\\textbf\{([^}]*)\}", r"\1", normalized_line)
            normalized_line = re.sub(r"\\mathbf\{([^}]*)\}", r"\1", normalized_line)
            normalized_line = re.sub(r"\\cdot", "*", normalized_line)
            normalized_line = re.sub(r"\\times", "*", normalized_line)
            normalized_line = re.sub(r"\\div", "/", normalized_line)
            normalized_line = re.sub(
                r"\\frac\{([^}]*)\}\{([^}]*)\}", r"\1/\2", normalized_line
            )
            normalized_line = re.sub(r"\\quad", " ", normalized_line)
            normalized_line = re.sub(r"\\;", " ", normalized_line)
            normalized_line = re.sub(r"\\text\{([^}]*)\}", r"\1", normalized_line)
            normalized_line = re.sub(r"\\boxed\{([^}]*)\}", r"\1", normalized_line)
            normalized_line = re.sub(r"\\\s*", " ", normalized_line)

            # Ieškome užduoties ID: "1a)", "1b)", "2a)", "6)", "7)" ir pan.
            id_match = re.match(
                r"^\s*(\d+[a-z]?)\s*\)\s*(.*)",
                normalized_line,
                re.IGNORECASE | re.DOTALL,
            )

            if id_match:
                task_id = id_match.group(1).lower()
                content = id_match.group(2).strip()

                # Išsaugome paskutinį užduoties numerį (be raidės)
                num_match = re.match(r"(\d+)", task_id)
                if num_match:
                    last_task_number = num_match.group(1)
            else:
                # Bandome rasti TIK raidę be skaičiaus: "c)", "d)", "e)"
                letter_only_match = re.match(
                    r"^\s*([a-z])\s*\)\s*(.*)",
                    normalized_line,
                    re.IGNORECASE | re.DOTALL,
                )
                if letter_only_match:
                    letter = letter_only_match.group(1).lower()
                    content = letter_only_match.group(2).strip()
                    # Priskiriame paskutinį žinomą numerį
                    task_id = f"{last_task_number}{letter}"
                    logger.info(
                        f"§§§ parser: rasta tik raidė '{letter})', priskirta kaip '{task_id}'"
                    )
                else:
                    # Jei neradome ID, bandome kaip paprastą tekstą
                    logger.debug(
                        f"§§§ parser: nerastas ID eilutėje: {normalized_line[:50]}..."
                    )
                    continue

            # Ieškome atsakymo
            answer = ""
            # Pirmiausia bandome rasti "Ats. X" arba "?Ats. X" formatą
            answer_match = re.search(
                r"(?:\?)?(?:ats\.?|atsakymas:?)\s*[=:]?\s*([-]?\d[\d.,/\-]*)",
                content,
                re.IGNORECASE,
            )
            if answer_match:
                answer = answer_match.group(1).strip().rstrip(".,")
            else:
                # Jei nėra "ats.", imame paskutinį skaičių po = ženklo
                # Bet ignoruojame jei po = yra tik "?"
                eq_match = re.search(r"=\s*([-]?\d[\d.,/\-]+)\s*$", content)
                if eq_match:
                    answer = eq_match.group(1).strip().rstrip(".,")
                else:
                    # Bandome rasti bet kokį skaičių po = ženklo (ne ?)
                    eq_match2 = re.search(r"=\s*\??\s*([-]?\d[\d.,/\-]+)", content)
                    if eq_match2:
                        answer = eq_match2.group(1).strip().rstrip(".,")

            tasks.append(
                {
                    "id": task_id,
                    "text": "",
                    "solution": content,
                    "answer": answer,
                    "original_latex": line,  # Saugome originalų LaTeX
                    "confidence": confidence,  # OCR pasitikėjimo lygis
                }
            )
            logger.info(
                f"§§§ parser: rasta užduotis {task_id}, answer={answer}, confidence={confidence}"
            )

        if tasks:
            # Pašaliname dublikatus pagal task_id (paliekame pirmą)
            seen_ids = set()
            unique_tasks = []
            for task in tasks:
                if task["id"] not in seen_ids:
                    seen_ids.add(task["id"])
                    unique_tasks.append(task)
                else:
                    logger.debug(f"§§§ parser: pašalintas dublikatas {task['id']}")

            logger.info(
                f"parse_latex_tasks: rasta {len(unique_tasks)} unikalių užduočių (§§§ separator, prieš: {len(tasks)})"
            )
            return unique_tasks

    # Normalizuojame LaTeX - pašaliname LaTeX komandas
    normalized = latex
    normalized = re.sub(r"\\textbf\{(\d+)\.\}", r"\1.", normalized)
    normalized = re.sub(r"\\cdot", "*", normalized)
    normalized = re.sub(r"\\times", "*", normalized)
    normalized = re.sub(r"\\div", "/", normalized)
    normalized = re.sub(r"\\\s*", " ", normalized)  # \\ -> space
    normalized = re.sub(r"\\text\{([^}]*)\}", r"\1", normalized)

    logger.debug(f"Normalized LaTeX: {normalized[:200]}...")

    # === Strategija 1: Ieškome "1a) ... 1b) ... 2a) ..." formatu ===
    # Pattern: skaičius + raidė + ) + turinys iki kito skaičius+raidė+) arba eilutės pabaigos
    full_id_pattern = r"(\d+[a-z])\s*\)\s*(.*?)(?=\s*\d+[a-z]\s*\)|$)"
    full_matches = re.findall(full_id_pattern, normalized, re.IGNORECASE | re.DOTALL)

    logger.debug(f"Full ID matches found: {len(full_matches)}")

    if full_matches:
        for task_id, content in full_matches:
            content = content.strip()
            if not content:
                continue

            # Ieškome atsakymo
            answer = ""
            answer_match = re.search(
                r"(?:ats\.?|atsakymas:?)\s*[=:]?\s*([-]?\d[\d.,/\-]*)",
                content,
                re.IGNORECASE,
            )
            if answer_match:
                answer = answer_match.group(1).strip().rstrip(".,")
            else:
                # Jei nėra "ats.", imame paskutinį skaičių po = ženklo
                eq_match = re.search(r"=\s*([-]?\d[\d.,/\-]*)\s*$", content)
                if eq_match:
                    answer = eq_match.group(1).strip().rstrip(".,")

            tasks.append(
                {
                    "id": task_id.lower(),
                    "text": "",
                    "solution": content,
                    "answer": answer,
                }
            )
            logger.debug(f"Rasta užduotis {task_id}: answer={answer}")

        if tasks:
            logger.info(
                f"parse_latex_tasks: rasta {len(tasks)} užduočių (full ID format)"
            )
            return tasks

    # === Strategija 2: Ieškome "a) ... b) ... c) ..." inline formatu ===
    # Naudojame lookahead kad rastume kiekvieną raidę su skliaustu
    # Pattern: raidė + ) + turinys iki kitos raidės su ) arba eilutės pabaigos
    letter_pattern = r"([a-z])\s*\)\s*(.*?)(?=\s+[a-z]\s*\)|$)"
    letter_matches = re.findall(letter_pattern, normalized, re.IGNORECASE)

    logger.debug(f"Letter matches found: {len(letter_matches)}")

    if letter_matches:
        current_section = "1"  # Default sekcija

        # Bandome rasti sekcijos numerį prieš raides
        section_match = re.search(
            r"(\d+)\s*[.):]\s*(?=[a-z]\s*\))", normalized, re.IGNORECASE
        )
        if section_match:
            current_section = section_match.group(1)

        for letter, content in letter_matches:
            task_id = f"{current_section}{letter.lower()}"
            content = content.strip()

            if not content:
                continue

            # Ieškome atsakymo
            answer = ""
            # Formatas: "ats. 54" arba "ats 54" arba "atsakymas: 54" arba "Ats. 54 km"
            # Skaičius turi prasidėti skaitmeniu, ne tašku
            answer_match = re.search(
                r"(?:ats\.?|atsakymas:?)\s*[=:]?\s*(\d[\d.,/\-]*)",
                content,
                re.IGNORECASE,
            )
            if answer_match:
                answer = answer_match.group(1).strip().rstrip(".,")
            else:
                # Jei nėra "ats.", imame paskutinį skaičių po = ženklo
                eq_match = re.search(r"=\s*(\d[\d.,]*)\s*(?:\([^)]*\))?\s*$", content)
                if eq_match:
                    answer = eq_match.group(1).strip().rstrip(".,")
                else:
                    # Bandome rasti bet kokį skaičių po = ženklo
                    eq_match2 = re.search(r"=\s*(\d[\d.,]*)", content)
                    if eq_match2:
                        answer = eq_match2.group(1).strip().rstrip(".,")

            tasks.append(
                {
                    "id": task_id,
                    "text": "",
                    "solution": content,
                    "answer": answer,
                }
            )
            logger.debug(f"Rasta užduotis {task_id}: answer={answer}")

    # === Strategija 2: Eilutėmis atskirti formatai ===
    if not tasks:
        # Skaidome į eilutes ir ieškome "a)", "b)", "1.", "2." ir pan.
        lines = normalized.split("\n")
        current_section = "1"

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Tikriname ar tai sekcijos pradžia: "1." arba "2."
            section_start = re.match(r"^(\d+)\s*[.):]", line)
            if section_start:
                current_section = section_start.group(1)
                # Pašaliname sekcijos numerį iš eilutės
                line = re.sub(r"^\d+\s*[.):]\s*", "", line)

            # Ieškome raidės: "a)" arba "b)"
            letter_match = re.match(r"^([a-z])\s*\)\s*(.*)", line, re.IGNORECASE)
            if letter_match:
                letter = letter_match.group(1).lower()
                content = letter_match.group(2).strip()
                task_id = f"{current_section}{letter}"

                # Ieškome atsakymo
                answer = ""
                answer_match = re.search(
                    r"(?:ats\.?|atsakymas:?)\s*[=:]?\s*(\d[\d.,/\-]*)",
                    content,
                    re.IGNORECASE,
                )
                if answer_match:
                    answer = answer_match.group(1).strip().rstrip(".,")
                else:
                    eq_match = re.search(
                        r"=\s*(\d[\d.,]*)\s*(?:\([^)]*\))?\s*$", content
                    )
                    if eq_match:
                        answer = eq_match.group(1).strip().rstrip(".,")
                    else:
                        eq_match2 = re.search(r"=\s*(\d[\d.,]*)", content)
                        if eq_match2:
                            answer = eq_match2.group(1).strip().rstrip(".,")

                if content:
                    tasks.append(
                        {
                            "id": task_id,
                            "text": "",
                            "solution": content,
                            "answer": answer,
                        }
                    )

    # === Strategija 3: Tik numeruotos užduotys be raidžių ===
    if not tasks:
        pattern_simple = r"(?:^|\n)\s*(\d+)\s*[.)]\s*(.*?)(?=(?:\n\s*\d+\s*[.)]|$))"
        matches = re.findall(pattern_simple, normalized, re.DOTALL)

        for match in matches:
            task_num, content = match
            content = content.strip()

            if not content:
                continue

            answer_match = re.search(
                r"(?:ats\.?|atsakymas:?)\s*[=:]?\s*(\d[\d.,/\-]*)",
                content,
                re.IGNORECASE,
            )
            answer = answer_match.group(1).rstrip(".,") if answer_match else ""

            tasks.append(
                {
                    "id": str(task_num),
                    "text": "",
                    "solution": content,
                    "answer": answer.strip() if answer else "",
                }
            )

    # === Strategija 4: Ieškome bet kokių skaičiavimų su = ženklu ===
    if not tasks:
        # Paskutinė viltis - ieškome visų "X op Y = Z" formatų
        calc_pattern = r"([\d.,]+\s*[+\-*/×·÷:]\s*[\d.,]+\s*=\s*[\d.,]+)"
        calc_matches = re.findall(calc_pattern, normalized)

        for idx, calc in enumerate(calc_matches, 1):
            # Ištraukiame atsakymą (po = ženklo)
            eq_match = re.search(r"=\s*([\d.,]+)", calc)
            answer = eq_match.group(1) if eq_match else ""

            tasks.append(
                {
                    "id": str(idx),
                    "text": "",
                    "solution": calc.strip(),
                    "answer": answer,
                }
            )

    logger.info(f"parse_latex_tasks: rasta {len(tasks)} užduočių")
    return tasks


def generate_solution_methods(
    operation: str, a: float, b: float, result: float
) -> List[dict]:
    """
    Generuoja kelis sprendimo būdus su žingsniais.
    """
    methods = []

    a_int = int(a) if a == int(a) else a
    b_int = int(b) if b == int(b) else b
    result_int = int(result) if result == int(result) else result

    if operation == "multiply":
        # Metodas 1: Tiesioginis dauginimas
        methods.append(
            {
                "method_name": "Tiesioginis dauginimas",
                "steps": [
                    {
                        "step_number": 1,
                        "description": "Užrašome daugybos veiksmą",
                        "expression": f"{a_int} × {b_int}",
                        "result": None,
                    },
                    {
                        "step_number": 2,
                        "description": "Atliekame daugybą",
                        "expression": f"{a_int} × {b_int} = {result_int}",
                        "result": str(result_int),
                    },
                ],
                "final_answer": str(result_int),
            }
        )

        # Metodas 2: Skaidymas (jei tinka)
        if b >= 10 and b == int(b):
            b1 = int(b // 10) * 10
            b2 = int(b % 10)
            if b2 > 0:
                part1 = a * b1
                part2 = a * b2
                methods.append(
                    {
                        "method_name": "Skaidymas į dalis",
                        "steps": [
                            {
                                "step_number": 1,
                                "description": f"Išskaidome {b_int} į {b1} + {b2}",
                                "expression": f"{b_int} = {b1} + {b2}",
                                "result": None,
                            },
                            {
                                "step_number": 2,
                                "description": f"Dauginame {a_int} iš {b1}",
                                "expression": f"{a_int} × {b1} = {int(part1)}",
                                "result": str(int(part1)),
                            },
                            {
                                "step_number": 3,
                                "description": f"Dauginame {a_int} iš {b2}",
                                "expression": f"{a_int} × {b2} = {int(part2)}",
                                "result": str(int(part2)),
                            },
                            {
                                "step_number": 4,
                                "description": "Sudedame rezultatus",
                                "expression": f"{int(part1)} + {int(part2)} = {result_int}",
                                "result": str(result_int),
                            },
                        ],
                        "final_answer": str(result_int),
                    }
                )

        # Metodas 3: Stulpeliu (jei didesni skaičiai)
        if a >= 10 or b >= 10:
            methods.append(
                {
                    "method_name": "Daugyba stulpeliu",
                    "steps": [
                        {
                            "step_number": 1,
                            "description": "Užrašome skaičius stulpeliu",
                            "expression": f"  {a_int}\n× {b_int}\n────",
                            "result": None,
                        },
                        {
                            "step_number": 2,
                            "description": "Dauginame kiekvieną skaitmenį",
                            "expression": f"Atliekame daugybą žingsnis po žingsnio",
                            "result": None,
                        },
                        {
                            "step_number": 3,
                            "description": "Gauname rezultatą",
                            "expression": f"= {result_int}",
                            "result": str(result_int),
                        },
                    ],
                    "final_answer": str(result_int),
                }
            )

    elif operation == "divide":
        # Metodas 1: Tiesioginis dalijimas
        methods.append(
            {
                "method_name": "Tiesioginis dalijimas",
                "steps": [
                    {
                        "step_number": 1,
                        "description": "Užrašome dalybos veiksmą",
                        "expression": f"{a_int} ÷ {b_int}",
                        "result": None,
                    },
                    {
                        "step_number": 2,
                        "description": "Atliekame dalybą",
                        "expression": f"{a_int} ÷ {b_int} = {result_int}",
                        "result": str(result_int),
                    },
                ],
                "final_answer": str(result_int),
            }
        )

        # Metodas 2: Per daugybą (patikrinimas)
        methods.append(
            {
                "method_name": "Patikrinimas per daugybą",
                "steps": [
                    {
                        "step_number": 1,
                        "description": "Klausiame: kiek kartų telpa?",
                        "expression": f"{b_int} × ? = {a_int}",
                        "result": None,
                    },
                    {
                        "step_number": 2,
                        "description": f"Randame: {b_int} × {result_int} = {a_int}",
                        "expression": f"{b_int} × {result_int} = {a_int}",
                        "result": str(result_int),
                    },
                    {
                        "step_number": 3,
                        "description": "Atsakymas",
                        "expression": f"{a_int} ÷ {b_int} = {result_int}",
                        "result": str(result_int),
                    },
                ],
                "final_answer": str(result_int),
            }
        )

        # Metodas 3: Dalijimas dalimis (jei didelis skaičius)
        if a >= 100:
            methods.append(
                {
                    "method_name": "Dalijimas kampu",
                    "steps": [
                        {
                            "step_number": 1,
                            "description": "Užrašome dalybą kampu",
                            "expression": f"{a_int} | {b_int}",
                            "result": None,
                        },
                        {
                            "step_number": 2,
                            "description": "Daliname žingsnis po žingsnio",
                            "expression": "Imame skaitmenis iš kairės",
                            "result": None,
                        },
                        {
                            "step_number": 3,
                            "description": "Gauname rezultatą",
                            "expression": f"= {result_int}",
                            "result": str(result_int),
                        },
                    ],
                    "final_answer": str(result_int),
                }
            )

    elif operation == "add":
        methods.append(
            {
                "method_name": "Tiesioginis sudėjimas",
                "steps": [
                    {
                        "step_number": 1,
                        "description": "Užrašome sudėties veiksmą",
                        "expression": f"{a_int} + {b_int}",
                        "result": None,
                    },
                    {
                        "step_number": 2,
                        "description": "Atliekame sudėtį",
                        "expression": f"{a_int} + {b_int} = {result_int}",
                        "result": str(result_int),
                    },
                ],
                "final_answer": str(result_int),
            }
        )

    elif operation == "subtract":
        methods.append(
            {
                "method_name": "Tiesioginis atimtis",
                "steps": [
                    {
                        "step_number": 1,
                        "description": "Užrašome atimties veiksmą",
                        "expression": f"{a_int} - {b_int}",
                        "result": None,
                    },
                    {
                        "step_number": 2,
                        "description": "Atliekame atimtį",
                        "expression": f"{a_int} - {b_int} = {result_int}",
                        "result": str(result_int),
                    },
                ],
                "final_answer": str(result_int),
            }
        )

    return methods


def generate_error_analysis(
    operation: str, a: float, b: float, student_val: float, correct_val: float
) -> dict:
    """
    Generuoja detalią klaidos analizę.
    """
    a_int = int(a) if a == int(a) else a
    b_int = int(b) if b == int(b) else b
    student_int = int(student_val) if student_val == int(student_val) else student_val
    correct_int = int(correct_val) if correct_val == int(correct_val) else correct_val

    op_names = {
        "multiply": ("daugybos", "×", "dauginti"),
        "divide": ("dalybos", "÷", "dalinti"),
        "add": ("sudėties", "+", "sudėti"),
        "subtract": ("atimties", "-", "atimti"),
    }

    op_name, op_symbol, op_verb = op_names.get(
        operation, ("skaičiavimo", "?", "skaičiuoti")
    )

    # Analizuojame klaidos tipą
    error_type = "calculation"
    what_went_wrong = (
        f"Mokinio atsakymas {student_int} nesutampa su teisingu atsakymu {correct_int}"
    )
    why_wrong = f"Atliekant {op_name} veiksmą {a_int} {op_symbol} {b_int}, gauname {correct_int}, ne {student_int}"

    # Bandome nustatyti konkretesnę klaidos priežastį
    abs(correct_val - student_val)
    ratio = student_val / correct_val if correct_val != 0 else 0

    if abs(ratio - 10) < 0.01 or abs(ratio - 0.1) < 0.01:
        error_type = "decimal_place"
        what_went_wrong = (
            f"Kablelio (dešimtainės dalies) klaida - atsakymas skiriasi 10 kartų"
        )
        why_wrong = f"Tikėtina, kad buvo pamirštas arba pridėtas papildomas nulis"
    elif str(int(student_val))[::-1] == str(int(correct_val)) and len(
        str(int(student_val))
    ) == len(str(int(correct_val))):
        error_type = "digit_swap"
        what_went_wrong = f"Skaitmenys sukeisti vietomis"
        why_wrong = (
            f"Atsakymas {student_int} yra {correct_int} su sukeistais skaitmenimis"
        )
    elif operation == "multiply" and student_val == a + b:
        error_type = "wrong_operation"
        what_went_wrong = f"Vietoj daugybos atlikta sudėtis"
        why_wrong = f"{a_int} + {b_int} = {int(a+b)}, bet reikėjo {a_int} × {b_int} = {correct_int}"
    elif operation == "divide" and student_val == a - b:
        error_type = "wrong_operation"
        what_went_wrong = f"Vietoj dalybos atlikta atimtis"
        why_wrong = f"{a_int} - {b_int} = {int(a-b)}, bet reikėjo {a_int} ÷ {b_int} = {correct_int}"

    how_to_fix = f"Patikrink {op_name} veiksmą dar kartą. {a_int} {op_symbol} {b_int} = {correct_int}"

    return {
        "error_type": error_type,
        "error_location": f"Veiksmas: {a_int} {op_symbol} {b_int}",
        "what_went_wrong": what_went_wrong,
        "why_wrong": why_wrong,
        "how_to_fix": how_to_fix,
    }


def check_calculation(solver: MathSolver, solution: str, student_answer: str) -> tuple:
    """
    Patikrina ar mokinio skaičiavimas teisingas.
    Naudoja SymPy sympify() kaip pagrindinį tikrintoją - supranta bet kokią matematinę išraišką.

    Returns:
        (calculated_answer, is_correct, error_description, suggestion, error_analysis, solution_methods)
    """
    import re

    from sympy import SympifyError, sympify

    # Jei nėra atsakymo, bandome bent apskaičiuoti teisingą atsakymą
    if not student_answer or student_answer.strip() in ["?", ""]:
        # Bandome ištraukti išraišką ir apskaičiuoti
        if solution:
            # Pašaliname "?" ir "Ats." iš solution
            clean_sol = re.sub(
                r"\?+\s*(?:Ats\.?|atsakymas:?)?", "", solution, flags=re.IGNORECASE
            )
            clean_sol = re.sub(
                r"(?:Ats\.?|atsakymas:?)\s*\?*", "", clean_sol, flags=re.IGNORECASE
            )

            # Ieškome išraiškos (viskas prieš = arba visa eilutė)
            expr_match = re.search(r"^([\d\s+\-*/().,×·÷:]+)", clean_sol.strip())
            if expr_match:
                expr_str = expr_match.group(1).strip()
                expr_str = (
                    expr_str.replace("×", "*")
                    .replace("·", "*")
                    .replace("÷", "/")
                    .replace(":", "/")
                    .replace(",", ".")
                )
                expr_str = re.sub(r"\s+", "", expr_str)

                try:
                    calculated = float(sympify(expr_str))
                    calc_str = str(
                        int(calculated)
                        if calculated == int(calculated)
                        else round(calculated, 4)
                    )
                    return (
                        calc_str,
                        None,  # Nežinome ar teisinga - mokinys nepateikė atsakymo
                        "Mokinys nepateikė atsakymo",
                        f"Teisingas atsakymas turėtų būti: {calc_str}",
                        None,
                        [
                            {
                                "method_name": "Apskaičiuotas atsakymas",
                                "steps": [
                                    {
                                        "step_number": 1,
                                        "description": f"Išraiška: {expr_str}",
                                        "expression": expr_str,
                                        "result": None,
                                    },
                                    {
                                        "step_number": 2,
                                        "description": "Rezultatas",
                                        "expression": f"= {calc_str}",
                                        "result": calc_str,
                                    },
                                ],
                                "final_answer": calc_str,
                            }
                        ],
                    )
                except (SympifyError, ValueError, TypeError):
                    pass

        return None, None, "Atsakymas nerastas", "Pateikite galutinį atsakymą", None, []

    try:
        # Bandome konvertuoti atsakymą į skaičių
        # Palaikome trupmenas kaip "-1/2"
        answer_str = student_answer.replace(",", ".").replace(" ", "")
        if "/" in answer_str and not any(c.isalpha() for c in answer_str):
            # Trupmena - apskaičiuojame
            try:
                student_val = float(sympify(answer_str))
            except (SympifyError, ValueError, TypeError):
                student_val = float(answer_str.split("/")[0]) / float(
                    answer_str.split("/")[1]
                )
        else:
            student_val = float(answer_str)
    except (ValueError, ZeroDivisionError):
        return (
            None,
            None,
            "Neteisingas atsakymo formatas",
            "Atsakymas turi būti skaičius",
            None,
            [],
        )

    try:
        # === UNIVERSALUS TIKRINIMAS SU SYMPIFY ===
        # Ieškome išraiškos = rezultatas formatu
        # Palaiko: 2+3+4=9, 10*5=50, (2+3)*4=20, 100-50+25=75, 23*(-16)=-368, ir t.t.

        # Pirmiausia pašaliname "?Ats." ir panašius pattern'us iš solution
        clean_solution = solution
        clean_solution = re.sub(
            r"\?+\s*(?:Ats\.?|atsakymas:?)", " = ", clean_solution, flags=re.IGNORECASE
        )
        clean_solution = re.sub(
            r"(?:Ats\.?|atsakymas:?)\s*", " = ", clean_solution, flags=re.IGNORECASE
        )
        # Pašaliname dvigubus = ženklus
        clean_solution = re.sub(r"=\s*=", "=", clean_solution)

        # Regex palaiko neigiamus skaičius sklaustuose: (-16), (-3/13)
        expr_match = re.search(
            r"([\d\s+\-*/().,×·÷:]+)\s*=\s*([-]?[\d.,/]+)", clean_solution
        )
        if expr_match:
            expr_str = expr_match.group(1).strip()

            # Konvertuojame simbolius į Python operatorius
            expr_str = (
                expr_str.replace("×", "*")
                .replace("·", "*")
                .replace("÷", "/")
                .replace(":", "/")
                .replace(",", ".")
            )

            # Pašaliname tarpus bet palikame struktūrą
            expr_str = re.sub(r"\s+", "", expr_str)

            # Pašaliname tuščius simbolius ir validuojame
            if not expr_str or not any(c.isdigit() for c in expr_str):
                return None, None, None, None, None, []

            try:
                # SymPy sympify supranta bet kokią matematinę išraišką
                calculated = float(sympify(expr_str))
                calc_str = str(
                    int(calculated)
                    if calculated == int(calculated)
                    else round(calculated, 6)
                )

                # Nustatome operacijos tipą sprendimo būdams
                solution_methods = []
                error_analysis = None

                # Analizuojame išraišką sprendimo būdams
                numbers = re.findall(r"[\d.]+", expr_str)
                operators = re.findall(r"[+\-*/]", expr_str)

                if len(numbers) >= 2 and len(operators) >= 1:
                    nums = [float(n) for n in numbers]

                    # Jei tik vienas operatorius - generuojame detalius sprendimo būdus
                    if len(operators) == 1:
                        op = operators[0]
                        a, b = nums[0], nums[1]
                        op_type = {
                            "+": "add",
                            "-": "subtract",
                            "*": "multiply",
                            "/": "divide",
                        }.get(op)
                        if op_type:
                            solution_methods = generate_solution_methods(
                                op_type, a, b, calculated
                            )
                            if abs(calculated - student_val) >= 0.001:
                                error_analysis = generate_error_analysis(
                                    op_type, a, b, student_val, calculated
                                )

                    # Kelių operacijų išraiška - paprastas metodas
                    elif len(operators) > 1:
                        # Nustatome dominuojantį operatorių
                        if all(op == "+" for op in operators):
                            solution_methods = [
                                {
                                    "method_name": "Nuosekli sudėtis",
                                    "steps": [
                                        {
                                            "step_number": i + 1,
                                            "description": f"Skaičius: {n}",
                                            "expression": str(n),
                                            "result": None,
                                        }
                                        for i, n in enumerate(nums)
                                    ]
                                    + [
                                        {
                                            "step_number": len(nums) + 1,
                                            "description": "Galutinis rezultatas",
                                            "expression": f"= {calc_str}",
                                            "result": calc_str,
                                        }
                                    ],
                                    "final_answer": calc_str,
                                }
                            ]
                        elif all(op == "-" for op in operators):
                            solution_methods = [
                                {
                                    "method_name": "Nuosekli atimtis",
                                    "steps": [
                                        {
                                            "step_number": 1,
                                            "description": f"Pradinis skaičius: {nums[0]}",
                                            "expression": str(nums[0]),
                                            "result": None,
                                        }
                                    ]
                                    + [
                                        {
                                            "step_number": i + 2,
                                            "description": f"Atimame {n}",
                                            "expression": f"- {n}",
                                            "result": None,
                                        }
                                        for i, n in enumerate(nums[1:])
                                    ]
                                    + [
                                        {
                                            "step_number": len(nums) + 1,
                                            "description": "Galutinis rezultatas",
                                            "expression": f"= {calc_str}",
                                            "result": calc_str,
                                        }
                                    ],
                                    "final_answer": calc_str,
                                }
                            ]
                        else:
                            # Mišri išraiška
                            solution_methods = [
                                {
                                    "method_name": "Mišrūs veiksmai",
                                    "steps": [
                                        {
                                            "step_number": 1,
                                            "description": f"Išraiška: {expr_str}",
                                            "expression": expr_str,
                                            "result": None,
                                        },
                                        {
                                            "step_number": 2,
                                            "description": "Galutinis rezultatas",
                                            "expression": f"= {calc_str}",
                                            "result": calc_str,
                                        },
                                    ],
                                    "final_answer": calc_str,
                                }
                            ]

                # Tikriname ar atsakymas teisingas
                if abs(calculated - student_val) < 0.001:
                    return (calc_str, True, None, None, None, solution_methods)
                else:
                    # Formatuojame klaidos pranešimą
                    student_str = str(
                        int(student_val)
                        if student_val == int(student_val)
                        else student_val
                    )
                    return (
                        calc_str,
                        False,
                        f"Skaičiavimo klaida: {expr_str} = {calc_str}, ne {student_str}",
                        f"Patikrink skaičiavimus. Teisingas rezultatas: {calc_str}",
                        error_analysis,
                        solution_methods,
                    )

            except (SympifyError, ValueError, TypeError) as e:
                logger.debug(f"SymPy nepavyko apdoroti: {expr_str}, klaida: {e}")

        # === FALLBACK: SENAS REGEX METODAS ===
        # Jei sympify neveikia, bandome senus regex

        # Daugyba
        calc_match = re.search(
            r"([\d.,]+)\s*[*×·]\s*([\d.,]+)\s*=\s*([\d.,]+)", solution
        )
        if calc_match:
            a, b, result = calc_match.groups()
            a = float(a.replace(",", "."))
            b = float(b.replace(",", "."))
            calculated = a * b

            student_val = float(student_answer.replace(",", ".").replace(" ", ""))
            calc_str = str(
                int(calculated) if calculated == int(calculated) else calculated
            )

            # VISADA generuojame sprendimo būdus (ir teisingo, ir neteisingo atsakymo atveju)
            solution_methods = generate_solution_methods("multiply", a, b, calculated)

            if abs(calculated - student_val) < 0.001:
                return (calc_str, True, None, None, None, solution_methods)
            else:
                error_analysis = generate_error_analysis(
                    "multiply", a, b, student_val, calculated
                )
                return (
                    calc_str,
                    False,
                    f"Daugybos klaida: {int(a) if a == int(a) else a} × {int(b) if b == int(b) else b} = {calc_str}, ne {int(student_val) if student_val == int(student_val) else student_val}",
                    f"Patikrink daugybos veiksmą. Teisingas rezultatas: {calc_str}",
                    error_analysis,
                    solution_methods,
                )

        # Dalyba
        calc_match = re.search(
            r"([\d.,]+)\s*[:/÷]\s*([\d.,]+)\s*=\s*([\d.,]+)", solution
        )
        if calc_match:
            a, b, result = calc_match.groups()
            a = float(a.replace(",", "."))
            b = float(b.replace(",", "."))
            if b != 0:
                calculated = a / b

                student_val = float(student_answer.replace(",", ".").replace(" ", ""))
                calc_str = str(
                    int(calculated) if calculated == int(calculated) else calculated
                )

                # VISADA generuojame sprendimo būdus
                solution_methods = generate_solution_methods("divide", a, b, calculated)

                if abs(calculated - student_val) < 0.001:
                    return (calc_str, True, None, None, None, solution_methods)
                else:
                    error_analysis = generate_error_analysis(
                        "divide", a, b, student_val, calculated
                    )
                    return (
                        calc_str,
                        False,
                        f"Dalybos klaida: {int(a) if a == int(a) else a} ÷ {int(b) if b == int(b) else b} = {calc_str}, ne {int(student_val) if student_val == int(student_val) else student_val}",
                        f"Patikrink dalybos veiksmą. Teisingas rezultatas: {calc_str}",
                        error_analysis,
                        solution_methods,
                    )

        # Sudėtis - palaikome kelis skaičius (pvz. 110 + 100 + 130 = 340)
        # Pirmiausia bandome rasti visą išraišką su keliais +
        multi_add_match = re.search(
            r"([\d.,]+(?:\s*\+\s*[\d.,]+)+)\s*=\s*([\d.,]+)", solution
        )
        if multi_add_match:
            expr_str = multi_add_match.group(1)
            multi_add_match.group(2)

            # Išskaidome išraišką į skaičius
            numbers = re.findall(r"[\d.,]+", expr_str)
            if numbers:
                calculated = sum(float(n.replace(",", ".")) for n in numbers)
                student_val = float(student_answer.replace(",", ".").replace(" ", ""))
                calc_str = str(
                    int(calculated) if calculated == int(calculated) else calculated
                )

                # Generuojame sprendimo būdus tik jei 2 skaičiai
                if len(numbers) == 2:
                    a, b = float(numbers[0].replace(",", ".")), float(
                        numbers[1].replace(",", ".")
                    )
                    solution_methods = generate_solution_methods(
                        "add", a, b, calculated
                    )
                else:
                    # Kelių skaičių sudėtis - paprastas metodas
                    solution_methods = [
                        {
                            "method_name": "Nuosekli sudėtis",
                            "steps": [
                                {
                                    "step_number": i + 1,
                                    "description": f"Pridedame {n}",
                                    "expression": f"+ {n}",
                                    "result": None,
                                }
                                for i, n in enumerate(numbers)
                            ]
                            + [
                                {
                                    "step_number": len(numbers) + 1,
                                    "description": "Galutinis rezultatas",
                                    "expression": f"= {calc_str}",
                                    "result": calc_str,
                                }
                            ],
                            "final_answer": calc_str,
                        }
                    ]

                if abs(calculated - student_val) < 0.001:
                    return (calc_str, True, None, None, None, solution_methods)
                else:
                    nums_str = " + ".join(
                        str(
                            int(float(n.replace(",", ".")))
                            if float(n.replace(",", "."))
                            == int(float(n.replace(",", ".")))
                            else n
                        )
                        for n in numbers
                    )
                    error_analysis = (
                        generate_error_analysis(
                            "add",
                            float(numbers[0].replace(",", ".")),
                            float(numbers[-1].replace(",", ".")),
                            student_val,
                            calculated,
                        )
                        if len(numbers) == 2
                        else None
                    )
                    return (
                        calc_str,
                        False,
                        f"Sudėties klaida: {nums_str} = {calc_str}, ne {int(student_val) if student_val == int(student_val) else student_val}",
                        f"Patikrink sudėties veiksmą. Teisingas rezultatas: {calc_str}",
                        error_analysis,
                        solution_methods,
                    )

        # Atimtis        # Atimtis
        calc_match = re.search(r"([\d.,]+)\s*-\s*([\d.,]+)\s*=\s*([\d.,]+)", solution)
        if calc_match:
            a, b, result = calc_match.groups()
            a = float(a.replace(",", "."))
            b = float(b.replace(",", "."))
            calculated = a - b

            student_val = float(student_answer.replace(",", ".").replace(" ", ""))
            calc_str = str(
                int(calculated) if calculated == int(calculated) else calculated
            )

            # VISADA generuojame sprendimo būdus
            solution_methods = generate_solution_methods("subtract", a, b, calculated)

            if abs(calculated - student_val) < 0.001:
                return (calc_str, True, None, None, None, solution_methods)
            else:
                error_analysis = generate_error_analysis(
                    "subtract", a, b, student_val, calculated
                )
                return (
                    calc_str,
                    False,
                    f"Atimties klaida: {int(a) if a == int(a) else a} - {int(b) if b == int(b) else b} = {calc_str}, ne {int(student_val) if student_val == int(student_val) else student_val}",
                    f"Patikrink atimties veiksmą. Teisingas rezultatas: {calc_str}",
                    error_analysis,
                    solution_methods,
                )

        # Negalime patikrinti
        return None, None, None, None, None, []

    except Exception as e:
        logger.debug(f"Skaičiavimo tikrinimo klaida: {e}")
        return None, None, None, None, None, []


async def analyze_work_with_ai(
    gemini: GeminiClient, latex_content: str, grade_level: int
) -> Optional[AutoCheckResponse]:
    """
    Analizuoja mokinio darbą su Gemini AI.
    """


async def check_with_wolfram(expression: str, student_answer: str) -> tuple:
    """
    Patikrina skaičiavimą su WolframAlpha API.

    Returns:
        (calculated_answer, is_correct, error_description, suggestion)
    """
    from math_checker.wolfram_client import get_wolfram_client

    client = get_wolfram_client()
    if not client.is_configured:
        return None, None, None, None

    try:
        # Apskaičiuojame su Wolfram
        result = await client.calculate(expression)

        if not result.success:
            return None, None, None, None

        calculated = result.result
        calculated_num = result.result_numeric

        if calculated_num is not None:
            # Bandome paversti mokinio atsakymą į skaičių
            try:
                student_num = float(student_answer.replace(",", ".").replace(" ", ""))

                # Lyginame
                if abs(calculated_num - student_num) < 0.001:
                    return str(calculated_num), True, None, None
                else:
                    return (
                        str(calculated_num),
                        False,
                        f"Skaičiavimo klaida: rezultatas turėtų būti {calculated_num}, ne {student_num}",
                        f"WolframAlpha: teisingas rezultatas yra {calculated_num}",
                    )
            except ValueError:
                pass

        # Tekstinis palyginimas
        if calculated:
            if calculated.lower().replace(" ", "") == student_answer.lower().replace(
                " ", ""
            ):
                return calculated, True, None, None

        return calculated, None, None, None

    except Exception as e:
        logger.debug(f"WolframAlpha klaida: {e}")
        return None, None, None, None


# Originali analyze_work_with_ai funkcija
async def _analyze_work_with_ai(
    gemini: GeminiClient, latex_content: str, grade_level: int
) -> Optional[AutoCheckResponse]:
    prompt = f"""Esi matematikos mokytojo asistentas. Analizuok šį {grade_level} klasės mokinio darbą.

MOKINIO DARBAS (OCR atpažintas):
{latex_content}

UŽDUOTIS:
1. Rask visas užduotis ir jų sprendimus
2. Patikrink kiekvieną skaičiavimą
3. Nurodyk klaidas ir paaiškink jas lietuviškai

ATSAKYK JSON formatu:
{{
    "tasks": [
        {{
            "task_id": "1a",
            "student_solution": "3 * 18 = 54",
            "student_answer": "54",
            "calculated_answer": "54",
            "is_correct": true,
            "error_description": null,
            "suggestion": null
        }},
        {{
            "task_id": "1b",
            "student_solution": "51 : 3 = 16",
            "student_answer": "16",
            "calculated_answer": "17",
            "is_correct": false,
            "error_description": "Dalybos klaida: 51 ÷ 3 = 17, ne 16",
            "suggestion": "Patikrink dalybos veiksmą"
        }}
    ],
    "summary": "Trumpa santrauka lietuviškai"
}}

Atsakyk TIK JSON, be papildomo teksto."""

    try:
        import json

        response = await gemini.generate_async(prompt)

        if not response:
            return None

        # Išvalome JSON
        json_str = response.strip()
        if json_str.startswith("```"):
            json_str = json_str.split("```")[1]
            if json_str.startswith("json"):
                json_str = json_str[4:]
        json_str = json_str.strip()

        data = json.loads(json_str)

        tasks_data = data.get("tasks", [])
        task_results = []
        correct_count = 0
        incorrect_count = 0
        unknown_count = 0

        for t in tasks_data:
            is_correct = t.get("is_correct")
            if is_correct is True:
                correct_count += 1
            elif is_correct is False:
                incorrect_count += 1
            else:
                unknown_count += 1

            task_results.append(
                AutoTaskResult(
                    task_id=t.get("task_id", "?"),
                    task_text="",
                    student_solution=t.get("student_solution", ""),
                    student_answer=t.get("student_answer", ""),
                    calculated_answer=t.get("calculated_answer"),
                    is_correct=is_correct,
                    error_description=t.get("error_description"),
                    suggestion=t.get("suggestion"),
                    confidence=0.8,
                )
            )

        return AutoCheckResponse(
            success=True,
            task_results=task_results,
            total_tasks=len(task_results),
            correct_count=correct_count,
            incorrect_count=incorrect_count,
            unknown_count=unknown_count,
            summary=data.get(
                "summary",
                f"AI analizė: {correct_count} teisingai, {incorrect_count} neteisingai",
            ),
            ai_analysis=data.get("summary"),
        )

    except Exception as e:
        logger.error(f"AI analizės klaida: {e}")
        return None


# === WolframAlpha endpointai ===


@router.get("/wolfram/status")
async def get_wolfram_status():
    """
    Gauti WolframAlpha API statusą.
    """
    client = get_wolfram_client()
    return {
        "configured": client.is_configured,
        "message": (
            "WolframAlpha API sukonfigūruotas"
            if client.is_configured
            else "WolframAlpha API raktas nenustatytas"
        ),
    }


@router.post("/wolfram/calculate", response_model=WolframResponse)
async def wolfram_calculate(request: WolframCalculateRequest):
    """
    Apskaičiuoti išraišką su WolframAlpha.

    Pvz: "3*18", "sqrt(144)", "2^10", "sin(45 degrees)"
    """
    client = get_wolfram_client()

    if not client.is_configured:
        return WolframResponse(
            success=False,
            query=request.expression,
            error="WolframAlpha API raktas nenustatytas. Eikite į Nustatymai → API raktai.",
        )

    result = await client.calculate(request.expression)

    return WolframResponse(
        success=result.success,
        query=result.query,
        result=result.result,
        result_numeric=result.result_numeric,
        error=result.error,
    )


@router.post("/wolfram/solve", response_model=WolframResponse)
async def wolfram_solve(request: WolframSolveRequest):
    """
    Išspręsti lygtį su WolframAlpha.

    Pvz: "x^2-4=0", "2x+5=11", "x^3-8=0"
    """
    client = get_wolfram_client()

    if not client.is_configured:
        return WolframResponse(
            success=False,
            query=request.equation,
            error="WolframAlpha API raktas nenustatytas",
        )

    result = await client.solve_equation(request.equation)

    return WolframResponse(
        success=result.success,
        query=result.query,
        result=result.result,
        result_numeric=result.result_numeric,
        error=result.error,
    )


@router.post("/wolfram/check")
async def wolfram_check_answer(request: WolframCheckRequest):
    """
    Patikrinti mokinio atsakymą su WolframAlpha.

    Apskaičiuoja abi reikšmes ir palygina.
    """
    client = get_wolfram_client()

    if not client.is_configured:
        return {
            "success": False,
            "is_correct": None,
            "error": "WolframAlpha API raktas nenustatytas",
        }

    try:
        is_correct = await client.check_equality(
            request.student_answer, request.correct_answer
        )

        return {
            "success": True,
            "is_correct": is_correct,
            "student_answer": request.student_answer,
            "correct_answer": request.correct_answer,
            "message": "Teisingai!" if is_correct else "Neteisingai",
        }
    except Exception as e:
        logger.error(f"WolframAlpha tikrinimo klaida: {e}")
        return {"success": False, "is_correct": None, "error": str(e)}
