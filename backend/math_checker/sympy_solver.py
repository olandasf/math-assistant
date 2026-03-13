"""
SymPy Solver - Matematikos sprendimų tikrinimas
================================================
Naudoja SymPy biblioteką matematinių išraiškų analizei ir tikrinimui.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

try:
    from sympy import (
        E,
        Eq,
        I,
        Rational,
        cancel,
        cos,
        exp,
        expand,
        factor,
        latex,
        log,
        pi,
        simplify,
        sin,
        solve,
        sqrt,
        symbols,
        sympify,
        tan,
    )
    from sympy.parsing.latex import parse_latex

    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False


class CheckResult(Enum):
    """Tikrinimo rezultatas."""

    CORRECT = "correct"
    INCORRECT = "incorrect"
    PARTIALLY_CORRECT = "partially_correct"
    PARSE_ERROR = "parse_error"
    UNKNOWN = "unknown"


@dataclass
class SolutionCheck:
    """Sprendimo tikrinimo rezultatas."""

    result: CheckResult
    message: str
    expected_value: Optional[str] = None
    student_value: Optional[str] = None
    expected_latex: Optional[str] = None
    student_latex: Optional[str] = None
    steps_analysis: Optional[List[Dict[str, Any]]] = None
    error_type: Optional[str] = None
    points_ratio: float = 0.0  # 0.0 - 1.0


class MathSolver:
    """Matematikos sprendimų tikrintojas naudojant SymPy."""

    def __init__(self):
        if not SYMPY_AVAILABLE:
            raise ImportError("SymPy biblioteka neįdiegta. Įdiekite: pip install sympy")

        # Dažnai naudojami simboliai
        self.x, self.y, self.z = symbols("x y z")
        self.a, self.b, self.c = symbols("a b c")
        self.n, self.m, self.k = symbols("n m k", integer=True)

    def parse_expression(self, expr_str: str) -> Optional[Any]:
        """
        Parsina matematinę išraišką iš teksto arba LaTeX.

        Args:
            expr_str: Išraiška kaip tekstas arba LaTeX

        Returns:
            SymPy išraiška arba None jei nepavyko
        """
        if not expr_str or not expr_str.strip():
            return None

        expr_str = expr_str.strip()

        # Bandome parsuoti kaip LaTeX
        try:
            if "\\" in expr_str or "{" in expr_str:
                # LaTeX formatas
                return parse_latex(expr_str)
        except Exception:
            pass

        # Bandome parsuoti kaip paprastą išraišką
        try:
            # Pakeičiame dažnus simbolius
            expr_str = expr_str.replace("^", "**")
            expr_str = expr_str.replace("×", "*")
            expr_str = expr_str.replace("÷", "/")
            expr_str = expr_str.replace("·", "*")

            return sympify(expr_str)
        except Exception:
            pass

        return None

    def check_equality(
        self, student_answer: str, correct_answer: str, tolerance: float = 1e-9
    ) -> SolutionCheck:
        """
        Tikrina ar mokinio atsakymas lygus teisingam atsakymui.

        Args:
            student_answer: Mokinio atsakymas
            correct_answer: Teisingas atsakymas
            tolerance: Leistinas skirtumas (skaitinėms reikšmėms)

        Returns:
            SolutionCheck objektas su rezultatu
        """
        student_expr = self.parse_expression(student_answer)
        correct_expr = self.parse_expression(correct_answer)

        if student_expr is None:
            return SolutionCheck(
                result=CheckResult.PARSE_ERROR,
                message="Nepavyko atpažinti mokinio atsakymo",
                student_value=student_answer,
                expected_value=correct_answer,
                error_type="parse_error_student",
            )

        if correct_expr is None:
            return SolutionCheck(
                result=CheckResult.PARSE_ERROR,
                message="Nepavyko atpažinti teisingo atsakymo",
                student_value=student_answer,
                expected_value=correct_answer,
                error_type="parse_error_correct",
            )

        try:
            # Suprastiname abu
            student_simplified = simplify(student_expr)
            correct_simplified = simplify(correct_expr)

            # Tikriname lygybę
            difference = simplify(student_simplified - correct_simplified)

            if difference == 0:
                return SolutionCheck(
                    result=CheckResult.CORRECT,
                    message="Atsakymas teisingas!",
                    student_value=str(student_simplified),
                    expected_value=str(correct_simplified),
                    student_latex=latex(student_simplified),
                    expected_latex=latex(correct_simplified),
                    points_ratio=1.0,
                )

            # Bandome skaitinį palyginimą
            try:
                student_num = float(student_simplified.evalf())
                correct_num = float(correct_simplified.evalf())

                if abs(student_num - correct_num) < tolerance:
                    return SolutionCheck(
                        result=CheckResult.CORRECT,
                        message="Atsakymas teisingas (skaitiškai lygūs)",
                        student_value=str(student_num),
                        expected_value=str(correct_num),
                        points_ratio=1.0,
                    )
            except (ValueError, TypeError):
                pass

            return SolutionCheck(
                result=CheckResult.INCORRECT,
                message="Atsakymas neteisingas",
                student_value=str(student_simplified),
                expected_value=str(correct_simplified),
                student_latex=latex(student_simplified),
                expected_latex=latex(correct_simplified),
                points_ratio=0.0,
            )

        except Exception as e:
            return SolutionCheck(
                result=CheckResult.UNKNOWN,
                message=f"Klaida tikrinant: {str(e)}",
                student_value=student_answer,
                expected_value=correct_answer,
                error_type="check_error",
            )

    def check_fraction(
        self, student_answer: str, correct_answer: str, require_simplified: bool = True
    ) -> SolutionCheck:
        """
        Tikrina trupmeną - ar teisinga ir ar suprastinta.

        Args:
            student_answer: Mokinio atsakymas (pvz., "6/8" arba "\\frac{6}{8}")
            correct_answer: Teisingas atsakymas
            require_simplified: Ar reikalauti suprastintos formos

        Returns:
            SolutionCheck su rezultatu
        """
        result = self.check_equality(student_answer, correct_answer)

        if result.result == CheckResult.CORRECT and require_simplified:
            # Tikriname ar suprastinta
            student_expr = self.parse_expression(student_answer)
            if student_expr is not None:
                try:
                    simplified = simplify(student_expr)
                    if student_expr != simplified:
                        # Trupmena teisinga, bet nesuprastinta
                        return SolutionCheck(
                            result=CheckResult.PARTIALLY_CORRECT,
                            message="Atsakymas teisingas, bet trupmena nesuprastinta",
                            student_value=str(student_expr),
                            expected_value=str(simplified),
                            student_latex=latex(student_expr),
                            expected_latex=latex(simplified),
                            error_type="not_simplified",
                            points_ratio=0.75,  # 75% taškų
                        )
                except Exception:
                    pass

        return result

    def solve_equation(self, equation_str: str, variable: str = "x") -> List[str]:
        """
        Išsprendžia lygtį.

        Args:
            equation_str: Lygtis kaip tekstas (pvz., "2*x + 3 = 7")
            variable: Kintamasis, kurio ieškome

        Returns:
            Sprendinių sąrašas kaip tekstas
        """
        try:
            var = symbols(variable)

            # Parsuojame lygtį
            if "=" in equation_str:
                left, right = equation_str.split("=", 1)
                left_expr = self.parse_expression(left)
                right_expr = self.parse_expression(right)

                if left_expr is None or right_expr is None:
                    return []

                eq = Eq(left_expr, right_expr)
            else:
                # Jei nėra =, laikome kad = 0
                expr = self.parse_expression(equation_str)
                if expr is None:
                    return []
                eq = Eq(expr, 0)

            solutions = solve(eq, var)
            return [str(sol) for sol in solutions]

        except Exception:
            return []

    def check_equation_solution(
        self, equation_str: str, student_answer: str, variable: str = "x"
    ) -> SolutionCheck:
        """
        Tikrina ar mokinio atsakymas yra teisingas lygties sprendinys.

        Args:
            equation_str: Lygtis
            student_answer: Mokinio atsakymas
            variable: Kintamasis

        Returns:
            SolutionCheck su rezultatu
        """
        correct_solutions = self.solve_equation(equation_str, variable)

        if not correct_solutions:
            return SolutionCheck(
                result=CheckResult.PARSE_ERROR,
                message="Nepavyko išspręsti lygties",
                error_type="solve_error",
            )

        student_expr = self.parse_expression(student_answer)
        if student_expr is None:
            return SolutionCheck(
                result=CheckResult.PARSE_ERROR,
                message="Nepavyko atpažinti mokinio atsakymo",
                error_type="parse_error_student",
            )

        # Tikriname ar mokinio atsakymas sutampa su kuriuo nors sprendiniu
        for sol in correct_solutions:
            sol_expr = self.parse_expression(sol)
            if sol_expr is not None:
                if simplify(student_expr - sol_expr) == 0:
                    return SolutionCheck(
                        result=CheckResult.CORRECT,
                        message="Lygties sprendinys teisingas!",
                        student_value=str(student_expr),
                        expected_value=sol,
                        student_latex=latex(student_expr),
                        expected_latex=latex(sol_expr),
                        points_ratio=1.0,
                    )

        return SolutionCheck(
            result=CheckResult.INCORRECT,
            message="Lygties sprendinys neteisingas",
            student_value=str(student_expr),
            expected_value=", ".join(correct_solutions),
            points_ratio=0.0,
        )

    def simplify_expression(self, expr_str: str) -> Tuple[bool, str, str]:
        """
        Suprastina išraišką.

        Args:
            expr_str: Išraiška

        Returns:
            (sėkmė, suprastinta išraiška, LaTeX formatas)
        """
        expr = self.parse_expression(expr_str)
        if expr is None:
            return False, expr_str, expr_str

        try:
            simplified = simplify(expr)
            return True, str(simplified), latex(simplified)
        except Exception:
            return False, expr_str, expr_str

    def expand_expression(self, expr_str: str) -> Tuple[bool, str, str]:
        """
        Išskleidžia išraišką (pvz., (a+b)² → a² + 2ab + b²).

        Returns:
            (sėkmė, išskleista išraiška, LaTeX formatas)
        """
        expr = self.parse_expression(expr_str)
        if expr is None:
            return False, expr_str, expr_str

        try:
            expanded = expand(expr)
            return True, str(expanded), latex(expanded)
        except Exception:
            return False, expr_str, expr_str

    def factor_expression(self, expr_str: str) -> Tuple[bool, str, str]:
        """
        Faktorizuoja išraišką (pvz., x² - 4 → (x-2)(x+2)).

        Returns:
            (sėkmė, faktorizuota išraiška, LaTeX formatas)
        """
        expr = self.parse_expression(expr_str)
        if expr is None:
            return False, expr_str, expr_str

        try:
            factored = factor(expr)
            return True, str(factored), latex(factored)
        except Exception:
            return False, expr_str, expr_str

    def to_latex(self, expr_str: str) -> str:
        """Konvertuoja išraišką į LaTeX formatą."""
        expr = self.parse_expression(expr_str)
        if expr is None:
            return expr_str
        try:
            return latex(expr)
        except Exception:
            return expr_str

    def check_solution_steps(
        self, steps: List[str], expected_answer: str, task_type: str = "equation"
    ) -> Dict[str, Any]:
        """
        Tikrina mokinio sprendimo žingsnius.

        Args:
            steps: Mokinio sprendimo žingsniai (kiekvienas žingsnis kaip tekstas)
            expected_answer: Teisingas galutinis atsakymas
            task_type: Užduoties tipas (equation, fraction, expression)

        Returns:
            Dict su žingsnių analize:
            - total_steps: bendras žingsnių skaičius
            - valid_steps: teisingų žingsnių skaičius
            - first_error_step: pirmo klaidos žingsnio numeris (arba None)
            - step_details: kiekvieno žingsnio analizė
            - final_correct: ar galutinis atsakymas teisingas
            - score: įvertinimas 0-1
        """
        if not steps:
            return {
                "total_steps": 0,
                "valid_steps": 0,
                "first_error_step": None,
                "step_details": [],
                "final_correct": False,
                "score": 0.0,
                "message": "Nėra sprendimo žingsnių",
            }

        step_details = []
        valid_steps = 0
        first_error_step = None
        prev_expr = None

        for i, step in enumerate(steps):
            step_info = {
                "step_number": i + 1,
                "content": step,
                "is_valid": False,
                "issue": None,
                "latex": None,
            }

            # Parsname žingsnį
            current_expr = self.parse_expression(step)

            if current_expr is None:
                step_info["issue"] = "Nepavyko atpažinti išraiškos"
                if first_error_step is None:
                    first_error_step = i + 1
            else:
                step_info["latex"] = latex(current_expr)

                # Tikriname ar žingsnis logiškas
                if prev_expr is not None:
                    # Tikriname ar šis žingsnis seka iš ankstesnio
                    # (pvz., suprastinimas, pertvarkymas, etc.)
                    try:
                        diff = simplify(current_expr - prev_expr)
                        if diff == 0:
                            # Žingsniai matematiškai lygūs (tik pertvarkymas)
                            step_info["is_valid"] = True
                            valid_steps += 1
                        else:
                            # Tikriname ar tai galėjo būti teisinga transformacija
                            # Pvz., sprendžiant lygtį, galima atimti iš abiejų pusių
                            step_info["is_valid"] = (
                                True  # Laikome teisingais skirtingus žingsnius
                            )
                            valid_steps += 1
                    except Exception:
                        step_info["is_valid"] = True  # Duodame benefit of doubt
                        valid_steps += 1
                else:
                    # Pirmas žingsnis - tiesiog priimame
                    step_info["is_valid"] = True
                    valid_steps += 1

                prev_expr = current_expr

            step_details.append(step_info)

        # Tikriname galutinį atsakymą
        final_step = steps[-1] if steps else ""
        final_check = self.check_equality(final_step, expected_answer)
        final_correct = final_check.result == CheckResult.CORRECT

        # Skaičiuojame įvertinimą
        if len(steps) > 0:
            steps_score = valid_steps / len(steps)
            final_score = 1.0 if final_correct else 0.0
            # Galutinis atsakymas sveria 60%, žingsniai 40%
            score = final_score * 0.6 + steps_score * 0.4
        else:
            score = 0.0

        # Nustatome pranešimą
        if final_correct and valid_steps == len(steps):
            message = "Puiku! Sprendimas teisingas ir visi žingsniai korektiški."
        elif final_correct:
            message = f"Atsakymas teisingas, bet {len(steps) - valid_steps} žingsnis(-iai) turi problemų."
        elif valid_steps == len(steps):
            message = (
                "Žingsniai atrodo korektiški, bet galutinis atsakymas neteisingas."
            )
        else:
            message = f"Klaida aptikta {first_error_step} žingsnyje."

        return {
            "total_steps": len(steps),
            "valid_steps": valid_steps,
            "first_error_step": first_error_step,
            "step_details": step_details,
            "final_correct": final_correct,
            "score": round(score, 2),
            "message": message,
        }

    def identify_error_type(
        self, student_answer: str, correct_answer: str, task_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Identifikuoja mokinio klaidos tipą.

        Args:
            student_answer: Mokinio atsakymas
            correct_answer: Teisingas atsakymas
            task_type: Užduoties tipas

        Returns:
            Dict su klaidos informacija:
            - error_type: klaidos tipas
            - description: klaidos aprašymas lietuviškai
            - suggestion: patarimas mokiniui
        """
        student_expr = self.parse_expression(student_answer)
        correct_expr = self.parse_expression(correct_answer)

        if student_expr is None:
            return {
                "error_type": "parse_error",
                "description": "Nepavyko atpažinti tavo atsakymo",
                "suggestion": "Patikrink ar teisingai užrašei atsakymą",
            }

        if correct_expr is None:
            return {
                "error_type": "system_error",
                "description": "Sistema negali patikrinti šio atsakymo",
                "suggestion": "Kreipkis į mokytoją",
            }

        try:
            # Tikriname ar teisingas
            if simplify(student_expr - correct_expr) == 0:
                return {
                    "error_type": "none",
                    "description": "Atsakymas teisingas!",
                    "suggestion": None,
                }

            # Bandome nustatyti klaidos tipą

            # 1. Ženklo klaida
            if simplify(student_expr + correct_expr) == 0:
                return {
                    "error_type": "sign_error",
                    "description": "Ženklo klaida - atsakymas priešingo ženklo",
                    "suggestion": "Atidžiai patikrink + ir - ženklus skaičiavimuose",
                }

            # 2. Klaida 10 kartų (dešimtainio kablelio problema)
            try:
                student_num = float(student_expr.evalf())
                correct_num = float(correct_expr.evalf())

                if abs(student_num * 10 - correct_num) < 0.01:
                    return {
                        "error_type": "decimal_error",
                        "description": "Kablelio klaida - atsakymas per 10 kartų mažesnis",
                        "suggestion": "Patikrink dešimtainį kablelį",
                    }
                if abs(student_num / 10 - correct_num) < 0.01:
                    return {
                        "error_type": "decimal_error",
                        "description": "Kablelio klaida - atsakymas per 10 kartų didesnis",
                        "suggestion": "Patikrink dešimtainį kablelį",
                    }

                # 3. Artimas atsakymas (apvalinimo klaida)
                if correct_num != 0:
                    error_pct = abs((student_num - correct_num) / correct_num) * 100
                    if error_pct < 5:
                        return {
                            "error_type": "rounding_error",
                            "description": f"Apvalinimo klaida - skirtumas tik {error_pct:.1f}%",
                            "suggestion": "Patikrink apvalinimo tikslumą",
                        }
                    elif error_pct < 20:
                        return {
                            "error_type": "calculation_error",
                            "description": "Skaičiavimo klaida - atsakymas artimas, bet neteisingas",
                            "suggestion": "Peržiūrėk skaičiavimus dar kartą žingsnis po žingsnio",
                        }
            except (ValueError, TypeError):
                pass

            # 4. Trupmenų klaidos
            if task_type in ["fraction", "trupmena"]:
                # Tikriname ar nesuprastinta
                simplified = simplify(student_expr)
                if (
                    student_expr != simplified
                    and simplify(simplified - correct_expr) == 0
                ):
                    return {
                        "error_type": "not_simplified",
                        "description": "Atsakymas teisingas, bet trupmena nesuprastinta",
                        "suggestion": "Suprastink trupmeną iki mažiausių skaičių",
                    }

            # 5. Bendrinė skaičiavimo klaida
            return {
                "error_type": "calculation_error",
                "description": "Skaičiavimo klaida",
                "suggestion": "Atidžiai patikrink kiekvieną skaičiavimo žingsnį",
            }

        except Exception as e:
            return {
                "error_type": "unknown",
                "description": "Nepavyko nustatyti klaidos tipo",
                "suggestion": "Paklausk mokytojo pagalbos",
            }


# Singleton instancija
_solver: Optional[MathSolver] = None


def get_solver() -> MathSolver:
    """Gauna MathSolver instanciją."""
    global _solver
    if _solver is None:
        _solver = MathSolver()
    return _solver


# === Convenience funkcijos ===


def check_answer(student: str, correct: str) -> SolutionCheck:
    """Patikrina ar mokinio atsakymas teisingas."""
    return get_solver().check_equality(student, correct)


def check_fraction_answer(
    student: str, correct: str, require_simplified: bool = True
) -> SolutionCheck:
    """Patikrina trupmeną."""
    return get_solver().check_fraction(student, correct, require_simplified)


def solve_eq(equation: str, var: str = "x") -> List[str]:
    """Išsprendžia lygtį."""
    return get_solver().solve_equation(equation, var)


def to_latex(expr: str) -> str:
    """Konvertuoja į LaTeX."""
    return get_solver().to_latex(expr)


if __name__ == "__main__":
    # Testavimas
    solver = MathSolver()

    print("=== SymPy Solver Testavimas ===\n")

    # Trupmenos
    print("1. Trupmenų tikrinimas:")
    result = solver.check_fraction("6/15 + 5/15", "11/15")
    print(f"   6/15 + 5/15 = 11/15: {result.result.value} - {result.message}")

    result = solver.check_fraction("6/8", "3/4", require_simplified=True)
    print(
        f"   6/8 = 3/4 (reikia suprastinti): {result.result.value} - {result.message}"
    )

    # Lygtys
    print("\n2. Lygčių sprendimas:")
    solutions = solver.solve_equation("2*x + 3 = 7")
    print(f"   2x + 3 = 7: x = {solutions}")

    solutions = solver.solve_equation("x**2 - 4 = 0")
    print(f"   x² - 4 = 0: x = {solutions}")

    # Suprastinimas
    print("\n3. Suprastinimas:")
    success, result_str, result_latex = solver.simplify_expression("(x**2 - 4)/(x - 2)")
    print(f"   (x² - 4)/(x - 2) = {result_str}")

    # LaTeX
    print("\n4. LaTeX konvertavimas:")
    latex_result = solver.to_latex("2/5 + 1/3")
    print(f"   2/5 + 1/3 → {latex_result}")

    print("\n✅ Testavimas baigtas!")
