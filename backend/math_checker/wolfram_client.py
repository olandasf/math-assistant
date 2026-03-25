"""
WolframAlpha API Klientas - Sudėtingų matematikos uždavinių sprendimas
======================================================================
https://products.wolframalpha.com/api/

WolframAlpha yra galingiausias matematikos variklis - sprendžia:
- Sudėtingas lygtis ir sistemas
- Diferencialines lygtis
- Integralus
- Ribas
- Trigonometrines funkcijas
- Žodžių uždavinius
"""

from dataclasses import dataclass
from typing import Optional

import httpx
from loguru import logger


@dataclass
class WolframResult:
    """WolframAlpha API rezultatas."""

    success: bool
    query: str
    result: Optional[str] = None
    result_numeric: Optional[float] = None
    steps: Optional[str] = None  # Sprendimo žingsniai (jei yra)
    pods: Optional[list] = None  # Visos atsakymo sekcijos
    error: Optional[str] = None


class WolframClient:
    """WolframAlpha API klientas sudėtingiems skaičiavimams."""

    BASE_URL = "https://api.wolframalpha.com/v2"
    SHORT_ANSWERS_URL = "https://api.wolframalpha.com/v1/result"
    TIMEOUT = 30.0  # Wolfram gali būti lėtas

    def __init__(self, app_id: Optional[str] = None):
        """
        Inicializuoja WolframAlpha klientą.

        Args:
            app_id: WolframAlpha App ID (gaunamas iš developer.wolframalpha.com)
        """
        self.app_id = app_id
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def is_configured(self) -> bool:
        """Ar konfigūruotas su API raktu."""
        return bool(self.app_id)

    def configure(self, app_id: str):
        """Nustatyti API raktą."""
        self.app_id = app_id
        logger.info("WolframAlpha API sukonfigūruotas")

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

    async def get_short_answer(self, query: str) -> WolframResult:
        """
        Gauti trumpą atsakymą (Short Answers API).

        Greitesnis ir paprastesnis būdas gauti tik atsakymą.
        Pvz: "2+2" -> "4", "solve x^2-4=0" -> "x = -2 or x = 2"
        """
        if not self.is_configured:
            return WolframResult(
                success=False,
                query=query,
                error="WolframAlpha API raktas nenustatytas",
            )

        try:
            client = await self._get_client()
            response = await client.get(
                self.SHORT_ANSWERS_URL,
                params={
                    "appid": self.app_id,
                    "i": query,
                    "units": "metric",
                },
            )

            if response.status_code == 200:
                result_text = response.text.strip()

                # Bandome konvertuoti į skaičių
                result_numeric = None
                try:
                    # Pašaliname tarpus ir kablelius
                    clean = result_text.replace(" ", "").replace(",", ".")
                    result_numeric = float(clean)
                except (ValueError, TypeError):
                    pass

                return WolframResult(
                    success=True,
                    query=query,
                    result=result_text,
                    result_numeric=result_numeric,
                )
            elif response.status_code == 501:
                return WolframResult(
                    success=False,
                    query=query,
                    error="WolframAlpha nesupranta šios užklausos",
                )
            else:
                return WolframResult(
                    success=False,
                    query=query,
                    error=f"API klaida: {response.status_code}",
                )

        except httpx.TimeoutException:
            logger.warning(f"WolframAlpha timeout: {query}")
            return WolframResult(
                success=False,
                query=query,
                error="Užklausa per ilgai užtruko",
            )
        except Exception as e:
            logger.error(f"WolframAlpha klaida: {e}")
            return WolframResult(
                success=False,
                query=query,
                error=str(e),
            )

    async def query_full(
        self, query: str, include_steps: bool = False
    ) -> WolframResult:
        """
        Pilna WolframAlpha užklausa (Full Results API).

        Grąžina visas atsakymo sekcijas (pods) su detaliais paaiškinimais.

        Args:
            query: Matematikos užklausa
            include_steps: Ar įtraukti sprendimo žingsnius (reikia Pro)
        """
        if not self.is_configured:
            return WolframResult(
                success=False,
                query=query,
                error="WolframAlpha API raktas nenustatytas",
            )

        try:
            client = await self._get_client()

            params = {
                "appid": self.app_id,
                "input": query,
                "format": "plaintext",
                "output": "json",
                "units": "metric",
            }

            if include_steps:
                params["podstate"] = "Step-by-step solution"

            response = await client.get(
                f"{self.BASE_URL}/query",
                params=params,
            )

            if response.status_code != 200:
                return WolframResult(
                    success=False,
                    query=query,
                    error=f"API klaida: {response.status_code}",
                )

            data = response.json()
            queryresult = data.get("queryresult", {})

            if not queryresult.get("success"):
                return WolframResult(
                    success=False,
                    query=query,
                    error=queryresult.get("error", {}).get("msg", "Nežinoma klaida"),
                )

            # Ištraukiame pods
            pods = queryresult.get("pods", [])

            # Ieškome pagrindinio rezultato
            result = None
            result_numeric = None
            steps = None

            for pod in pods:
                pod_id = pod.get("id", "")
                subpods = pod.get("subpods", [])

                # Pagrindinis rezultatas
                if pod_id in [
                    "Result",
                    "Solution",
                    "Solutions",
                    "NumericalAnswer",
                    "DecimalApproximation",
                ]:
                    for subpod in subpods:
                        plaintext = subpod.get("plaintext", "")
                        if plaintext:
                            result = plaintext
                            # Bandome gauti skaičių
                            try:
                                clean = plaintext.replace(" ", "").replace(",", ".")
                                # Pašaliname vienetus ir tekstą
                                import re

                                numbers = re.findall(r"[-+]?\d*\.?\d+", clean)
                                if numbers:
                                    result_numeric = float(numbers[0])
                            except (ValueError, TypeError):
                                pass
                            break
                    if result:
                        break

                # Sprendimo žingsniai
                if "step" in pod_id.lower():
                    for subpod in subpods:
                        plaintext = subpod.get("plaintext", "")
                        if plaintext:
                            steps = plaintext
                            break

            # Jei neradome "Result", imame pirmą pod su tekstu
            if not result:
                for pod in pods:
                    if pod.get("id") != "Input":
                        for subpod in pod.get("subpods", []):
                            plaintext = subpod.get("plaintext", "")
                            if plaintext:
                                result = plaintext
                                break
                        if result:
                            break

            return WolframResult(
                success=True,
                query=query,
                result=result,
                result_numeric=result_numeric,
                steps=steps,
                pods=[{"id": p.get("id"), "title": p.get("title")} for p in pods],
            )

        except httpx.TimeoutException:
            logger.warning(f"WolframAlpha timeout: {query}")
            return WolframResult(
                success=False,
                query=query,
                error="Užklausa per ilgai užtruko",
            )
        except Exception as e:
            logger.error(f"WolframAlpha klaida: {e}")
            return WolframResult(
                success=False,
                query=query,
                error=str(e),
            )

    async def calculate(self, expression: str) -> WolframResult:
        """
        Apskaičiuoti matematinę išraišką.

        Pvz: "3*18", "sqrt(144)", "2^10"
        """
        return await self.get_short_answer(expression)

    async def solve_equation(self, equation: str) -> WolframResult:
        """
        Išspręsti lygtį.

        Pvz: "x^2-4=0", "2x+5=11"
        """
        query = f"solve {equation}"
        return await self.get_short_answer(query)

    async def simplify(self, expression: str) -> WolframResult:
        """
        Supaprastinti išraišką.

        Pvz: "2x+3x", "(x+1)^2"
        """
        query = f"simplify {expression}"
        return await self.get_short_answer(query)

    async def derivative(self, expression: str, variable: str = "x") -> WolframResult:
        """
        Apskaičiuoti išvestinę.

        Pvz: "x^3", "sin(x)"
        """
        query = f"derivative of {expression} with respect to {variable}"
        return await self.get_short_answer(query)

    async def integrate(self, expression: str, variable: str = "x") -> WolframResult:
        """
        Apskaičiuoti integralą.

        Pvz: "x^2", "1/x"
        """
        query = f"integrate {expression} with respect to {variable}"
        return await self.get_short_answer(query)

    async def check_equality(self, expr1: str, expr2: str) -> bool:
        """
        Patikrinti ar dvi išraiškos lygios.

        Args:
            expr1: Pirma išraiška (mokinio atsakymas)
            expr2: Antra išraiška (teisingas atsakymas)

        Returns:
            True jei lygios, False jei ne
        """
        # Bandome abi reikšmes apskaičiuoti ir palyginti
        result1 = await self.calculate(expr1)
        result2 = await self.calculate(expr2)

        if result1.success and result2.success:
            # Jei turime skaitines reikšmes - lyginam jas
            if (
                result1.result_numeric is not None
                and result2.result_numeric is not None
            ):
                # Leistina paklaida
                tolerance = 1e-9
                return abs(result1.result_numeric - result2.result_numeric) < tolerance

            # Lyginam tekstines reikšmes
            if result1.result and result2.result:
                # Normalizuojame
                r1 = result1.result.lower().replace(" ", "")
                r2 = result2.result.lower().replace(" ", "")
                return r1 == r2

        return False


# Globalus klientas
_wolfram_client: Optional[WolframClient] = None


def get_wolfram_client() -> WolframClient:
    """Gauti globalų WolframAlpha klientą."""
    global _wolfram_client
    if _wolfram_client is None:
        _wolfram_client = WolframClient()
    return _wolfram_client


def configure_wolfram(app_id: str):
    """Konfigūruoti WolframAlpha su API raktu."""
    client = get_wolfram_client()
    client.configure(app_id)
