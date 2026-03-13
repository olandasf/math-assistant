"""
Newton API Klientas - Nemokamas matematikos sprendėjas
=======================================================
https://newton.now.sh - atviras API be registracijos ir raktų.
Naudojamas kaip backup kai SymPy neišsprendžia.
"""

from dataclasses import dataclass
from typing import Any, Optional, Union
from urllib.parse import quote

import httpx
from loguru import logger


@dataclass
class NewtonResult:
    """Newton API rezultatas."""

    success: bool
    operation: str
    expression: str
    result: Optional[Union[str, list, float]] = None
    error: Optional[str] = None


class NewtonClient:
    """Newton API klientas matematikos operacijoms."""

    BASE_URL = "https://newton.now.sh/api/v2"
    TIMEOUT = 15.0

    # Palaikomos operacijos
    OPERATIONS = {
        "simplify": "Supaprastinti išraišką",
        "factor": "Faktorizuoti",
        "derive": "Išvestinė",
        "integrate": "Integralas",
        "zeroes": "Rasti šaknis (x=0)",
        "tangent": "Liestinės lygtis",
        "area": "Plotas po kreive",
        "cos": "Kosinusas",
        "sin": "Sinusas",
        "tan": "Tangentas",
        "arccos": "Arkkosinusas",
        "arcsin": "Arksinusas",
        "arctan": "Arktangentas",
        "abs": "Absoliuti reikšmė",
        "log": "Natūrinis logaritmas",
    }

    def __init__(self):
        """Inicializuoja Newton klientą."""
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Gauna arba sukuria HTTP klientą."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.TIMEOUT, follow_redirects=True
            )
        return self._client

    async def close(self):
        """Uždaro HTTP klientą."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def _encode_expression(self, expr: str) -> str:
        """Užkoduoja išraišką URL formatui."""
        # Newton API naudoja URL path, todėl reikia koduoti specialius simbolius
        return quote(expr, safe="")

    async def _call_api(self, operation: str, expression: str) -> NewtonResult:
        """Iškviečia Newton API."""
        if operation not in self.OPERATIONS:
            return NewtonResult(
                success=False,
                operation=operation,
                expression=expression,
                error=f"Nepalaikoma operacija: {operation}",
            )

        encoded_expr = self._encode_expression(expression)
        url = f"{self.BASE_URL}/{operation}/{encoded_expr}"

        try:
            client = await self._get_client()
            response = await client.get(url)

            if response.status_code == 200:
                data = response.json()
                return NewtonResult(
                    success=True,
                    operation=data.get("operation", operation),
                    expression=data.get("expression", expression),
                    result=data.get("result"),
                )
            else:
                return NewtonResult(
                    success=False,
                    operation=operation,
                    expression=expression,
                    error=f"API klaida: {response.status_code}",
                )

        except httpx.TimeoutException:
            logger.warning(f"Newton API timeout: {operation}/{expression}")
            return NewtonResult(
                success=False,
                operation=operation,
                expression=expression,
                error="Timeout - API neatsako",
            )
        except Exception as e:
            logger.error(f"Newton API klaida: {e}")
            return NewtonResult(
                success=False,
                operation=operation,
                expression=expression,
                error=str(e),
            )

    # === Convenience metodai ===

    async def simplify(self, expression: str) -> NewtonResult:
        """Supaprastina matematinę išraišką."""
        return await self._call_api("simplify", expression)

    async def factor(self, expression: str) -> NewtonResult:
        """Faktorizuoja išraišką."""
        return await self._call_api("factor", expression)

    async def derive(self, expression: str) -> NewtonResult:
        """Apskaičiuoja išvestinę."""
        return await self._call_api("derive", expression)

    async def integrate(self, expression: str) -> NewtonResult:
        """Apskaičiuoja integralą."""
        return await self._call_api("integrate", expression)

    async def zeroes(self, expression: str) -> NewtonResult:
        """Randa išraiškos šaknis (kur f(x) = 0)."""
        return await self._call_api("zeroes", expression)

    async def tangent(self, point: float, expression: str) -> NewtonResult:
        """Randa liestinės lygtį taške."""
        # Formatas: tangent/{c}|{expr} pvz. tangent/2|x^2
        combined = f"{point}|{expression}"
        return await self._call_api("tangent", combined)

    async def area(self, start: float, end: float, expression: str) -> NewtonResult:
        """Apskaičiuoja plotą po kreive."""
        # Formatas: area/{start}:{end}|{expr} pvz. area/0:1|x^2
        combined = f"{start}:{end}|{expression}"
        return await self._call_api("area", combined)

    async def cos(self, value: str) -> NewtonResult:
        """Apskaičiuoja kosinusą."""
        return await self._call_api("cos", value)

    async def sin(self, value: str) -> NewtonResult:
        """Apskaičiuoja sinusą."""
        return await self._call_api("sin", value)

    async def log(self, value: str) -> NewtonResult:
        """Apskaičiuoja natūrinį logaritmą."""
        return await self._call_api("log", value)

    # === Aukšto lygio metodai ===

    async def solve_and_verify(self, expression: str, expected_result: str) -> dict:
        """
        Išsprendžia išraišką ir patikrina ar atsakymas teisingas.

        Returns:
            dict: {"correct": bool, "calculated": str, "expected": str}
        """
        # Bandome supaprastinti
        result = await self.simplify(expression)

        if not result.success:
            return {
                "correct": None,
                "calculated": None,
                "expected": expected_result,
                "error": result.error,
            }

        calculated = str(result.result).strip().lower()
        expected = str(expected_result).strip().lower()

        # Normalizuojame (pašaliname tarpus, etc.)
        calculated_norm = calculated.replace(" ", "")
        expected_norm = expected.replace(" ", "")

        return {
            "correct": calculated_norm == expected_norm,
            "calculated": result.result,
            "expected": expected_result,
            "error": None,
        }

    async def get_derivative_steps(self, expression: str) -> dict:
        """
        Gauna išvestinę ir papildomą informaciją.

        Returns:
            dict: {"original": str, "derivative": str, "success": bool}
        """
        result = await self.derive(expression)

        return {
            "original": expression,
            "derivative": result.result if result.success else None,
            "success": result.success,
            "error": result.error,
        }

    async def get_integral_with_bounds(
        self, expression: str, lower: float = None, upper: float = None
    ) -> dict:
        """
        Gauna integralą (apibrėžtinį arba neapibrėžtinį).

        Returns:
            dict: {"expression": str, "integral": str, "definite_value": float|None}
        """
        # Neapibrėžtinis integralas
        result = await self.integrate(expression)

        response = {
            "expression": expression,
            "integral": result.result if result.success else None,
            "definite_value": None,
            "success": result.success,
            "error": result.error,
        }

        # Jei nurodytos ribos, skaičiuojame apibrėžtinį
        if result.success and lower is not None and upper is not None:
            area_result = await self.area(lower, upper, expression)
            if area_result.success:
                response["definite_value"] = area_result.result

        return response


# Singleton instancija
_newton_client: Optional[NewtonClient] = None


def get_newton_client() -> NewtonClient:
    """Gauna Newton klientą (singleton)."""
    global _newton_client
    if _newton_client is None:
        _newton_client = NewtonClient()
    return _newton_client


# === Convenience funkcijos ===


async def simplify(expression: str) -> NewtonResult:
    """Supaprastina išraišką."""
    return await get_newton_client().simplify(expression)


async def derive(expression: str) -> NewtonResult:
    """Apskaičiuoja išvestinę."""
    return await get_newton_client().derive(expression)


async def integrate(expression: str) -> NewtonResult:
    """Apskaičiuoja integralą."""
    return await get_newton_client().integrate(expression)


async def factor(expression: str) -> NewtonResult:
    """Faktorizuoja išraišką."""
    return await get_newton_client().factor(expression)


async def find_roots(expression: str) -> NewtonResult:
    """Randa šaknis."""
    return await get_newton_client().zeroes(expression)
