"""
Math Checker Router - Matematikos tikrinimo API
==============================================
Endpointai matematikos sprendimų tikrinimui ir paaiškinimams.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class CheckAnswerRequest(BaseModel):
    """Užklausa atsakymo tikrinimui."""

    student_answer: str = Field(..., description="Mokinio atsakymas")
    correct_answer: str = Field(..., description="Teisingas atsakymas")
    task_type: Optional[str] = Field(
        None, description="Užduoties tipas: equation, fraction, expression"
    )


class CheckAnswerResponse(BaseModel):
    """Atsakymo tikrinimo rezultatas."""

    is_correct: bool
    message: str
    student_value: Optional[str] = None
    expected_value: Optional[str] = None
    student_latex: Optional[str] = None
    correct_latex: Optional[str] = None


class SolveEquationRequest(BaseModel):
    """Užklausa lygties sprendimui."""

    equation: str = Field(..., description="Lygtis, pvz. '2x + 5 = 11'")
    variable: str = Field(default="x", description="Kintamasis")


class SolveEquationResponse(BaseModel):
    """Lygties sprendimo rezultatas."""

    success: bool
    solutions: List[str] = []
    solutions_latex: List[str] = []
    message: str


class SimplifyRequest(BaseModel):
    """Užklausa išraiškos suprastinimui."""

    expression: str


class SimplifyResponse(BaseModel):
    """Suprastinimo rezultatas."""

    success: bool
    simplified: str
    simplified_latex: str
    original_latex: str


class ExplainErrorRequest(BaseModel):
    """Užklausa klaidos paaiškinimui."""

    task_text: str = Field(..., description="Užduoties tekstas")
    student_answer: str = Field(..., description="Mokinio atsakymas")
    correct_answer: str = Field(..., description="Teisingas atsakymas")
    grade_level: int = Field(default=6, ge=5, le=10, description="Klasė (5-10)")


class ExplainErrorResponse(BaseModel):
    """Klaidos paaiškinimo rezultatas."""

    success: bool
    explanation: str
    suggestions: List[str] = []
    error: Optional[str] = None


class AnalyzeStepsRequest(BaseModel):
    """Užklausa žingsnių analizei."""

    task_text: str
    steps: List[str]
    final_answer: str


class AnalyzeStepsResponse(BaseModel):
    """Žingsnių analizės rezultatas."""

    success: bool
    analysis: str
    issues: List[str] = []
    is_correct: bool


class CheckStepsRequest(BaseModel):
    """Užklausa tarpinių žingsnių tikrinimui."""

    steps: List[str] = Field(..., description="Mokinio sprendimo žingsniai")
    expected_answer: str = Field(..., description="Teisingas galutinis atsakymas")
    task_type: str = Field(default="equation", description="Užduoties tipas")


class StepDetail(BaseModel):
    """Vieno žingsnio informacija."""

    step_number: int
    content: str
    is_valid: bool
    issue: Optional[str] = None
    latex: Optional[str] = None


class CheckStepsResponse(BaseModel):
    """Žingsnių tikrinimo rezultatas."""

    total_steps: int
    valid_steps: int
    first_error_step: Optional[int] = None
    step_details: List[StepDetail]
    final_correct: bool
    score: float
    message: str


class IdentifyErrorRequest(BaseModel):
    """Užklausa klaidos tipo identifikavimui."""

    student_answer: str = Field(..., description="Mokinio atsakymas")
    correct_answer: str = Field(..., description="Teisingas atsakymas")
    task_type: str = Field(default="general", description="Užduoties tipas")


class IdentifyErrorResponse(BaseModel):
    """Klaidos identifikavimo rezultatas."""

    error_type: str
    description: str
    suggestion: Optional[str] = None


class AlternativeSolutionsRequest(BaseModel):
    """Užklausa alternatyviems sprendimams."""

    problem: str = Field(..., description="Uždavinio tekstas")
    correct_answer: str = Field(..., description="Teisingas atsakymas")
    grade_level: int = Field(default=6, ge=5, le=10, description="Klasė (5-10)")
    num_solutions: int = Field(default=3, ge=1, le=5, description="Sprendimų skaičius")


class AlternativeSolutionsResponse(BaseModel):
    """Alternatyvių sprendimų rezultatas."""

    success: bool
    solutions: str = ""
    error: Optional[str] = None


# === Endpoints ===


class GeometryCheckRequest(BaseModel):
    """Užklausa geometrijos atsakymo tikrinimui."""

    shape: str = Field(
        ...,
        description="Figūros tipas: square, rectangle, triangle, circle, cube, cylinder, etc.",
    )
    calculation_type: str = Field(
        ...,
        description="Skaičiavimo tipas: area, perimeter, volume, surface_area",
    )
    student_answer: str = Field(..., description="Mokinio atsakymas")
    params: dict = Field(
        ...,
        description="Figūros parametrai, pvz. {'a': 5, 'b': 3}",
    )


class GeometryCheckResponse(BaseModel):
    """Geometrijos tikrinimo rezultatas."""

    is_correct: bool
    message: str
    expected_value: float
    student_value: float
    expected_formula: Optional[str] = None
    error_percentage: float = 0.0
    hint: Optional[str] = None


class GeometryFormulaResponse(BaseModel):
    """Geometrijos formulės informacija."""

    formula: str
    description: str
    params: List[str]


class TaskDefinition(BaseModel):
    """Užduoties apibrėžimas tikrinimui."""

    task_number: str = Field(..., description="Užduoties numeris, pvz. '1a', '2b'")
    expected_answer: str = Field(..., description="Teisingas atsakymas")
    max_points: float = Field(default=1.0, description="Maksimalūs taškai")
    task_type: str = Field(default="arithmetic", description="Užduoties tipas")


class FullWorkCheckRequest(BaseModel):
    """Užklausa pilno darbo tikrinimui."""

    latex_content: str = Field(..., description="Pilnas LaTeX su mokinio sprendimais")
    tasks: List[TaskDefinition] = Field(
        ..., description="Užduočių sąrašas su teisingais atsakymais"
    )
    grade_level: int = Field(default=6, ge=5, le=10, description="Klasė")


class TaskResult(BaseModel):
    """Vienos užduoties tikrinimo rezultatas."""

    task_number: str
    student_answer: Optional[str] = None
    expected_answer: str
    is_correct: bool
    points_earned: float
    max_points: float
    error_type: Optional[str] = None
    error_description: Optional[str] = None
    suggestion: Optional[str] = None


class FullWorkCheckResponse(BaseModel):
    """Pilno darbo tikrinimo rezultatas."""

    success: bool
    total_points: float
    max_points: float
    percentage: float
    task_results: List[TaskResult]
    summary: str
    ai_explanation: Optional[str] = None


class AutoCheckRequest(BaseModel):
    """Užklausa automatiniam tikrinimui be iš anksto nustatytų atsakymų."""

    latex_content: str = Field(..., description="OCR atpažintas LaTeX turinys")
    grade_level: int = Field(default=6, ge=5, le=10, description="Klasė (5-10)")
    check_calculations: bool = Field(
        default=True, description="Ar tikrinti skaičiavimus"
    )


class SolutionStep(BaseModel):
    """Vienas sprendimo žingsnis."""

    step_number: int
    description: str  # Žingsnio aprašymas
    expression: str  # Matematinė išraiška
    result: Optional[str] = None  # Žingsnio rezultatas


class SolutionMethod(BaseModel):
    """Vienas sprendimo būdas."""

    method_name: str  # Metodo pavadinimas
    steps: List[SolutionStep]  # Žingsniai
    final_answer: str  # Galutinis atsakymas


class ErrorAnalysis(BaseModel):
    """Detali klaidos analizė."""

    error_type: str  # Klaidos tipas: "calculation", "method", "sign", "order" ir t.t.
    error_location: str  # Kur įvyko klaida
    what_went_wrong: str  # Kas nutiko blogai
    why_wrong: str  # Kodėl tai neteisinga
    how_to_fix: str  # Kaip pataisyti


class AutoTaskResult(BaseModel):
    """Automatiškai aptiktos užduoties rezultatas."""

    task_id: str  # "1a", "1b", "2" ir t.t.
    task_text: str  # Užduoties tekstas jei rastas
    student_solution: str  # Mokinio sprendimas
    student_answer: str  # Galutinis atsakymas
    calculated_answer: Optional[str] = None  # Mūsų apskaičiuotas teisingas atsakymas
    is_correct: Optional[bool] = None  # None jei negalime patikrinti

    # Išplėsta klaidų analizė
    error_description: Optional[str] = None  # Trumpas klaidos aprašymas
    error_analysis: Optional[ErrorAnalysis] = None  # Detali klaidos analizė

    # Teisingi sprendimo būdai
    solution_methods: List[SolutionMethod] = []  # Keli sprendimo variantai

    suggestion: Optional[str] = None  # Patarimas mokiniui
    confidence: float = 0.0  # Pasitikėjimas rezultatu 0-1


class AutoCheckResponse(BaseModel):
    """Automatinio tikrinimo rezultatas."""

    success: bool
    task_results: List[AutoTaskResult]
    total_tasks: int
    correct_count: int
    incorrect_count: int
    unknown_count: int  # Negalėjome patikrinti
    summary: str
    ai_analysis: Optional[str] = None


class DetailedExplanationRequest(BaseModel):
    """Užklausa išsamiam paaiškinimui."""

    problem: str = Field(..., description="Uždavinio tekstas arba išraiška")
    student_answer: str = Field(..., description="Mokinio atsakymas")
    correct_answer: str = Field(..., description="Teisingas atsakymas")
    is_correct: bool = Field(..., description="Ar mokinio atsakymas teisingas")
    grade_level: int = Field(default=6, ge=5, le=10, description="Klasė")


class DetailedExplanationResponse(BaseModel):
    """Išsamaus paaiškinimo rezultatas."""

    success: bool
    explanation: str
    error: Optional[str] = None


class WolframCheckRequest(BaseModel):
    """Užklausa WolframAlpha tikrinimui."""

    student_answer: str = Field(..., description="Mokinio atsakymas")
    correct_answer: str = Field(..., description="Teisingas atsakymas")


class WolframCalculateRequest(BaseModel):
    """Užklausa WolframAlpha skaičiavimui."""

    expression: str = Field(..., description="Matematinė išraiška")


class WolframSolveRequest(BaseModel):
    """Užklausa lygties sprendimui."""

    equation: str = Field(..., description="Lygtis, pvz. 'x^2-4=0'")


class WolframResponse(BaseModel):
    """WolframAlpha atsakymas."""

    success: bool
    query: str
    result: Optional[str] = None
    result_numeric: Optional[float] = None
    error: Optional[str] = None
