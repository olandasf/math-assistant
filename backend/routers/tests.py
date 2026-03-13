"""
API Router - Kontroliniai darbai.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from schemas.common import MessageResponse
from schemas.task import TaskBulkCreate, TaskCreate, TaskRead
from schemas.test import TestCreate, TestRead, TestUpdate, TestWithDetails
from schemas.variant import VariantCreate, VariantRead, VariantWithTasks
from services.task_service import TaskService
from services.test_generator import get_test_generator
from services.test_service import TestService
from services.variant_service import VariantService
from sqlalchemy.ext.asyncio import AsyncSession

# Curriculum integracijos importai
from utils.curriculum import (
    CURRICULUM_BY_GRADE,
    get_all_topics_for_grade,
    get_topic_by_id,
    get_topics_for_api,
    get_topics_summary,
    search_topics,
)

# Nauja programa iš JSON failų
from utils.curriculum_loader import (
    build_prompt_context,
    get_available_grades,
    get_cumulative_topics,
    get_difficulty_rules_for_subtopics,
    get_grade_topics,
)

from database import get_db

# === Curriculum schemas ===


class SubtopicResponse(BaseModel):
    """Potemės atsakymas."""

    id: str
    name: str
    description: str
    skills: List[str] = []


class TopicResponse(BaseModel):
    """Temos atsakymas."""

    id: str
    name: str
    name_en: str
    content_area: str
    grade_introduced: int
    importance: int
    subtopics: List[SubtopicResponse] = []


class CurriculumSummaryResponse(BaseModel):
    """Apibendrintas curriculum atsakymas."""

    grade: int
    concentre: str
    topic_count: int
    topics_by_area: dict


# === Generavimo schemas ===


class GenerateTestRequest(BaseModel):
    """Užklausa kontrolinio generavimui."""

    topic: Optional[str] = Field(
        default=None,
        description="Matematikos tema (viena)",
        examples=["trupmenos", "lygtys"],
    )
    topics: Optional[List[str]] = Field(
        default=None,
        description="Matematikos temos (kelios)",
        examples=[["trupmenos", "lygtys"]],
    )
    subtopics: Optional[List[str]] = Field(
        default=None,
        description="Pasirinktos potemės (subtopic IDs)",
    )
    use_curriculum: bool = Field(
        default=False,
        description="Ar naudoti programos temas (curriculum)",
    )
    curriculum_context: Optional[str] = Field(
        default=None,
        description="AI kontekstas iš difficulty_rules (generuojamas automatiškai)",
    )
    grade_level: int = Field(..., ge=5, le=12, description="Klasė (5-12)")
    task_count: int = Field(default=5, ge=1, le=20, description="Uždavinių kiekis")
    variant_count: int = Field(default=2, ge=1, le=4, description="Variantų kiekis")
    difficulty: str = Field(
        default="medium", description="Sudėtingumas: easy, medium, hard, mixed"
    )
    include_solutions: bool = Field(default=True, description="Ar generuoti sprendimus")
    save_to_db: bool = Field(default=False, description="Ar išsaugoti į DB")
    class_id: Optional[int] = Field(
        default=None, description="Klasės ID (jei save_to_db=True)"
    )
    use_template_generator: bool = Field(
        default=True,
        description="Ar naudoti šabloninį generatorių (True) ar AI/Gemini (False)",
    )


class GeneratedTaskResponse(BaseModel):
    """Sugeneruotas uždavinys."""

    number: int
    text: str
    answer: str
    answer_latex: str
    points: int
    topic: str
    difficulty: str
    solution_steps: List[str] = []


class GeneratedVariantResponse(BaseModel):
    """Sugeneruotas variantas."""

    variant_name: str
    tasks: List[GeneratedTaskResponse]


class GenerateTestResponse(BaseModel):
    """Atsakymas su sugeneruotu kontroliniu."""

    title: str
    topic: str
    grade_level: int
    total_points: int
    variants: List[GeneratedVariantResponse]
    saved_test_id: Optional[int] = None


router = APIRouter(prefix="/tests", tags=["Kontroliniai"])


# === Programos temos (iš JSON failų, Matematikos programa/) ===


@router.get("/program/topics/{grade}")
async def get_program_topics_by_grade(grade: int) -> Dict[str, Any]:
    """
    Grąžina kumuliatyvias programos temas pagal klasę.

    Pvz.: 7 kl. grąžina 5, 6 ir 7 kl. temas sugrupuotas pagal klasę.
    Kiekviena potemė turi difficulty_rules (EASY/MEDIUM/HARD).

    Args:
        grade: Klasė (5-12)

    Returns:
        {grade: int, available_grades: [int], grades: {5: [topics], 6: [topics], ...}}
    """
    if grade < 5 or grade > 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Palaikoma tik 5-12 klasėms",
        )

    cumulative = get_cumulative_topics(grade)
    available = get_available_grades()

    return {
        "grade": grade,
        "available_grades": available,
        "grades": {str(g): topics for g, topics in cumulative.items()},
    }


@router.get("/program/grades")
async def get_program_available_grades() -> Dict[str, Any]:
    """Grąžina klases, kurioms yra programos duomenys."""
    available = get_available_grades()
    return {"grades": available}


@router.post("/program/difficulty-context")
async def get_difficulty_context(
    subtopic_ids: List[str],
    difficulty: str = "MEDIUM",
    grade: int = 5,
) -> Dict[str, Any]:
    """
    Grąžina sunkumo taisykles pasirinktoms potemėms.

    Naudojama generatoriaus kontekstui paruošti.

    Args:
        subtopic_ids: Potemių ID sąrašas
        difficulty: EASY / MEDIUM / HARD
        grade: Klasė

    Returns:
        {rules: {...}, prompt_context: str}
    """
    rules = get_difficulty_rules_for_subtopics(subtopic_ids, difficulty)
    prompt = build_prompt_context(subtopic_ids, difficulty, grade)

    return {
        "rules": rules,
        "prompt_context": prompt,
    }


# === Curriculum temos (iš Lietuvos BP) ===


@router.get("/curriculum/topics/{grade}", response_model=List[TopicResponse])
async def get_curriculum_topics_by_grade(
    grade: int,
) -> List[TopicResponse]:
    """
    Gauna visas matematikos temas pagal klasę iš Lietuvos bendrosios programos.

    Args:
        grade: Klasė (5-10)

    Returns:
        Temų sąrašas su potemėmis
    """
    if grade < 5 or grade > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Palaikoma tik 5-10 klasėms",
        )

    topics_data = get_topics_for_api(grade)
    return [
        TopicResponse(
            id=t["id"],
            name=t["name"],
            name_en=t["name_en"],
            content_area=t["content_area"],
            grade_introduced=t["grade_introduced"],
            importance=t["importance"],
            subtopics=[
                SubtopicResponse(
                    id=st["id"],
                    name=st["name"],
                    description=st["description"],
                    skills=st.get("skills", []),
                )
                for st in t["subtopics"]
            ],
        )
        for t in topics_data
    ]


@router.get("/curriculum/topics")
async def get_all_curriculum_topics() -> dict:
    """
    Gauna apibendrintą informaciją apie visas klases ir temas.

    Returns:
        Apibendrintas curriculum pagal klases
    """
    summary = get_topics_summary()
    return {"grades": summary}


@router.get("/curriculum/search")
async def search_curriculum_topics(
    query: str = Query(..., description="Paieškos tekstas"),
    grade: Optional[int] = Query(None, description="Klasė (5-10)"),
) -> List[TopicResponse]:
    """
    Ieško temų pagal pavadinimą arba aprašymą.

    Args:
        query: Paieškos tekstas
        grade: Jei nurodyta, ieško tik toje klasėje

    Returns:
        Atitinkančių temų sąrašas
    """
    results = search_topics(query, grade)
    return [
        TopicResponse(
            id=t.id,
            name=t.name_lt,
            name_en=t.name_en,
            content_area=t.content_area.value,
            grade_introduced=t.grade_introduced,
            importance=t.importance,
            subtopics=[
                SubtopicResponse(
                    id=st.id,
                    name=st.name_lt,
                    description=st.description,
                    skills=st.skills,
                )
                for st in t.subtopics
            ],
        )
        for t in results
    ]


@router.get("/curriculum/topic/{topic_id}")
async def get_curriculum_topic_details(topic_id: str) -> dict:
    """
    Gauna detalią temos informaciją pagal ID.

    Args:
        topic_id: Temos ID

    Returns:
        Detali temos informacija
    """
    topic = get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tema '{topic_id}' nerasta",
        )

    return {
        "id": topic.id,
        "name": topic.name_lt,
        "name_en": topic.name_en,
        "content_area": topic.content_area.value,
        "description": topic.description,
        "grade_introduced": topic.grade_introduced,
        "grade_mastery": topic.grade_mastery,
        "grades_available": topic.grades_available,
        "importance": topic.importance,
        "prerequisites": topic.prerequisites,
        "subtopics": [
            {
                "id": st.id,
                "name": st.name_lt,
                "description": st.description,
                "satisfactory_requirements": st.satisfactory_requirements,
                "basic_requirements": st.basic_requirements,
                "advanced_requirements": st.advanced_requirements,
                "example_easy": st.example_easy,
                "example_medium": st.example_medium,
                "example_hard": st.example_hard,
                "skills": st.skills,
                "common_errors": st.common_errors,
            }
            for st in topic.subtopics
        ],
    }


# === Generavimas ===


@router.post("/generate", response_model=GenerateTestResponse)
async def generate_test(
    request: GenerateTestRequest, db: AsyncSession = Depends(get_db)
) -> GenerateTestResponse:
    """
    Generuoti kontrolinį darbą naudojant AI arba šablonus.

    Palaiko du režimus:
    1. Paprastas - topics sąrašas (šabloninis generatorius)
    2. Programos - subtopics su difficulty_rules (AI generatorius su kontekstu)
    """
    from loguru import logger

    # Jei naudojame programos temas - paruošiame kontekstą
    curriculum_ctx = None
    if request.use_curriculum and request.subtopics:
        # Mappiname difficulty
        diff_map = {"easy": "EASY", "medium": "MEDIUM", "hard": "HARD"}
        diff_key = diff_map.get(request.difficulty, "MEDIUM")
        curriculum_ctx = build_prompt_context(
            request.subtopics, diff_key, request.grade_level
        )
        logger.info(
            f"Programos kontekstas paruoštas: {len(request.subtopics)} potemių, "
            f"sunkumas={diff_key}"
        )
    elif request.curriculum_context:
        curriculum_ctx = request.curriculum_context

    # Nustatome temas - prioritetas `topics` masyvui
    topics_list = (
        request.topics if request.topics else ([request.topic] if request.topic else [])
    )

    # Jei temos tuščios bet yra subtopics - naudojame subtopics kaip temas
    if not topics_list and request.subtopics:
        topics_list = request.subtopics

    if not topics_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nurodykite bent vieną temą (topic arba topics)",
        )

    # Sujungiame temas į vieną string'ą display'ui
    topic_display = ", ".join(topics_list)

    logger.info(
        f"Generuojamas kontrolinis: temos={topics_list}, {request.grade_level} kl., "
        f"šabloninis={request.use_template_generator}, curriculum={request.use_curriculum}"
    )

    generator = get_test_generator()

    try:
        generated = await generator.generate_test(
            topic=topic_display,
            topics=topics_list,
            grade_level=request.grade_level,
            task_count=request.task_count,
            variant_count=request.variant_count,
            difficulty=request.difficulty,
            include_solutions=request.include_solutions,
            use_template_generator=request.use_template_generator,
            curriculum_context=curriculum_ctx,  # Naujas parametras
        )
    except Exception as e:
        logger.error(f"Generavimo klaida: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generavimo klaida: {str(e)}",
        )

    saved_test_id = None

    # Išsaugome į DB jei prašoma
    if request.save_to_db and request.class_id:
        try:
            test_service = TestService(db)
            variant_service = VariantService(db)
            task_service = TaskService(db)

            # Sukuriame kontrolinį
            test_data = TestCreate(
                title=generated.title,
                class_id=request.class_id,
                total_points=generated.total_points,
                status="draft",
            )
            test = await test_service.create(test_data)
            saved_test_id = test.id

            # Sukuriame variantus ir užduotis
            for variant in generated.variants:
                variant_obj = await variant_service.create(
                    VariantCreate(name=variant.variant_name, test_id=test.id)
                )

                for task in variant.tasks:
                    await task_service.create(
                        TaskCreate(
                            variant_id=variant_obj.id,
                            number=task.number,
                            text=task.text,
                            correct_answer=task.answer,
                            points=task.points,
                        )
                    )

            logger.info(f"Kontrolinis išsaugotas: ID={saved_test_id}")

        except Exception as e:
            logger.error(f"Išsaugojimo klaida: {e}")
            # Nesustabdome, grąžiname sugeneruotą be išsaugojimo

    # Konvertuojame į response
    variants_response = []
    for v in generated.variants:
        tasks_response = [
            GeneratedTaskResponse(
                number=t.number,
                text=t.text,
                answer=t.answer,
                answer_latex=t.answer_latex,
                points=t.points,
                topic=t.topic,
                difficulty=t.difficulty,
                solution_steps=t.solution_steps,
            )
            for t in v.tasks
        ]
        variants_response.append(
            GeneratedVariantResponse(variant_name=v.variant_name, tasks=tasks_response)
        )

    return GenerateTestResponse(
        title=generated.title,
        topic=generated.topic,
        grade_level=generated.grade_level,
        total_points=generated.total_points,
        variants=variants_response,
        saved_test_id=saved_test_id,
    )


@router.get("/topics", response_model=dict)
async def get_available_topics() -> dict:
    """Gauti galimas temas pagal klases."""
    from services.test_generator import TestGenerator

    return {
        "topics_by_grade": TestGenerator.TOPIC_TEMPLATES,
        "difficulties": ["easy", "medium", "hard", "mixed"],
    }


# === Kontroliniai ===


@router.get("/", response_model=List[TestRead])
async def get_all_tests(
    class_id: int = None,
    school_year_id: int = None,
    status_filter: str = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> List[TestRead]:
    """Gauti visus kontrolinius (galima filtruoti)."""
    service = TestService(db)

    if class_id:
        return await service.get_by_class(class_id)
    elif school_year_id:
        return await service.get_by_school_year(school_year_id)
    elif status_filter:
        return await service.get_by_status(status_filter)
    else:
        return await service.get_all(skip=skip, limit=limit)


@router.get("/{test_id}", response_model=TestRead)
async def get_test(test_id: int, db: AsyncSession = Depends(get_db)) -> TestRead:
    """Gauti kontrolinį pagal ID."""
    service = TestService(db)
    test = await service.get_by_id(test_id)
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Kontrolinis nerastas"
        )
    return test


@router.post("/", response_model=TestRead, status_code=status.HTTP_201_CREATED)
async def create_test(
    data: TestCreate, create_variants: bool = True, db: AsyncSession = Depends(get_db)
) -> TestRead:
    """Sukurti naują kontrolinį (galima automatiškai sukurti variantus I ir II)."""
    service = TestService(db)
    test = await service.create(data)

    if create_variants:
        variant_service = VariantService(db)
        await variant_service.create(VariantCreate(name="I", test_id=test.id))
        await variant_service.create(VariantCreate(name="II", test_id=test.id))

    return test


@router.put("/{test_id}", response_model=TestRead)
async def update_test(
    test_id: int, data: TestUpdate, db: AsyncSession = Depends(get_db)
) -> TestRead:
    """Atnaujinti kontrolinį."""
    service = TestService(db)
    test = await service.update(test_id, data)
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Kontrolinis nerastas"
        )
    return test


@router.post("/{test_id}/status/{new_status}", response_model=TestRead)
async def change_test_status(
    test_id: int, new_status: str, db: AsyncSession = Depends(get_db)
) -> TestRead:
    """Pakeisti kontrolinio statusą."""
    if new_status not in ["draft", "active", "completed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Neteisingas statusas. Galimi: draft, active, completed",
        )

    service = TestService(db)
    test = await service.set_status(test_id, new_status)
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Kontrolinis nerastas"
        )
    return test


@router.delete("/{test_id}", response_model=MessageResponse)
async def delete_test(
    test_id: int, db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """Ištrinti kontrolinį."""
    service = TestService(db)
    success = await service.delete(test_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Kontrolinis nerastas"
        )
    return MessageResponse(message="Kontrolinis ištrintas")


# === Variantai ===


@router.get("/{test_id}/variants", response_model=List[VariantRead])
async def get_test_variants(
    test_id: int, db: AsyncSession = Depends(get_db)
) -> List[VariantRead]:
    """Gauti visus kontrolinio variantus."""
    service = VariantService(db)
    return await service.get_by_test(test_id)


@router.get("/{test_id}/variants/{variant_id}", response_model=VariantWithTasks)
async def get_variant_with_tasks(
    test_id: int, variant_id: int, db: AsyncSession = Depends(get_db)
) -> VariantWithTasks:
    """Gauti variantą su užduotimis."""
    service = VariantService(db)
    variant = await service.get_with_tasks(variant_id)
    if not variant or variant.test_id != test_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Variantas nerastas"
        )

    result = VariantWithTasks.model_validate(variant)
    result.tasks_count = len(variant.tasks)
    return result


@router.post(
    "/{test_id}/variants",
    response_model=VariantRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_variant(
    test_id: int, data: VariantCreate, db: AsyncSession = Depends(get_db)
) -> VariantRead:
    """Sukurti naują variantą."""
    # Užtikrinti, kad test_id sutampa
    data.test_id = test_id
    service = VariantService(db)
    return await service.create(data)


# === Užduotys ===


@router.get("/{test_id}/variants/{variant_id}/tasks", response_model=List[TaskRead])
async def get_variant_tasks(
    test_id: int, variant_id: int, db: AsyncSession = Depends(get_db)
) -> List[TaskRead]:
    """Gauti visas varianto užduotis."""
    service = TaskService(db)
    return await service.get_by_variant(variant_id)


@router.post(
    "/{test_id}/variants/{variant_id}/tasks",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    test_id: int, variant_id: int, data: TaskCreate, db: AsyncSession = Depends(get_db)
) -> TaskRead:
    """Sukurti naują užduotį."""
    data.variant_id = variant_id
    service = TaskService(db)
    return await service.create(data)


@router.post(
    "/{test_id}/variants/{variant_id}/tasks/bulk",
    response_model=List[TaskRead],
    status_code=status.HTTP_201_CREATED,
)
async def bulk_create_tasks(
    test_id: int,
    variant_id: int,
    data: TaskBulkCreate,
    db: AsyncSession = Depends(get_db),
) -> List[TaskRead]:
    """Sukurti daug užduočių vienu metu."""
    data.variant_id = variant_id
    service = TaskService(db)
    return await service.bulk_create(data)


@router.put("/{test_id}/variants/{variant_id}/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    test_id: int,
    variant_id: int,
    task_id: int,
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
) -> TaskRead:
    """Atnaujinti užduotį."""
    from schemas.task import TaskUpdate

    update_data = TaskUpdate(**data.model_dump(exclude={"variant_id"}))
    service = TaskService(db)
    task = await service.update(task_id, update_data)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Užduotis nerasta"
        )
    return task


@router.delete(
    "/{test_id}/variants/{variant_id}/tasks/{task_id}", response_model=MessageResponse
)
async def delete_task(
    test_id: int, variant_id: int, task_id: int, db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """Ištrinti užduotį."""
    service = TaskService(db)
    success = await service.delete(task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Užduotis nerasta"
        )
    return MessageResponse(message="Užduotis ištrinta")
