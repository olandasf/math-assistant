"""
Math Checker Router - Matematikos tikrinimo API
==============================================
Endpointai matematikos sprendimų tikrinimui ir paaiškinimams.
"""

from typing import List, Optional

from ai.gemini_client import GeminiClient, get_gemini_client
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from math_checker.sympy_solver import MathSolver, check_answer, solve_eq, to_latex
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db


from .schemas import *

