"""
GDPR Anonymizer - Mokinio duomenų anonimizavimas prieš siunčiant į išorines API.
"""

import hashlib
from dataclasses import dataclass
from typing import Any


@dataclass
class AnonymizedData:
    """Anonimizuoti duomenys su galimybe atkurti."""

    original: str
    anonymized: str
    token: str


class Anonymizer:
    """
    Anonimizuoja mokinio duomenis prieš siunčiant į išorines API.
    Palaiko de-anonimizavimą grąžintam tekstui.
    """

    def __init__(self, salt: str = "math_teacher_2026"):
        self.salt = salt
        self._mappings: dict[str, AnonymizedData] = {}
        self._token_counter = 0

    def _generate_token(self, prefix: str = "STUDENT") -> str:
        """Generuoja unikalų tokeną."""
        self._token_counter += 1
        return f"[{prefix}_{self._token_counter:04d}]"

    def _hash_value(self, value: str) -> str:
        """Sukuria hash reikšmę identifikavimui."""
        return hashlib.md5(f"{value}{self.salt}".encode()).hexdigest()[:8]

    def anonymize_name(self, name: str) -> str:
        """Anonimizuoja vardą/pavardę."""
        if not name:
            return name

        hash_key = self._hash_value(name)

        if hash_key in self._mappings:
            return self._mappings[hash_key].anonymized

        token = self._generate_token("VARDAS")
        data = AnonymizedData(original=name, anonymized=token, token=hash_key)
        self._mappings[hash_key] = data

        return token

    def anonymize_student_code(self, code: str) -> str:
        """Anonimizuoja mokinio kodą."""
        if not code:
            return code

        hash_key = self._hash_value(code)

        if hash_key in self._mappings:
            return self._mappings[hash_key].anonymized

        token = self._generate_token("KODAS")
        data = AnonymizedData(original=code, anonymized=token, token=hash_key)
        self._mappings[hash_key] = data

        return token

    def anonymize_class(self, class_name: str) -> str:
        """Anonimizuoja klasės pavadinimą."""
        if not class_name:
            return class_name

        hash_key = self._hash_value(f"class_{class_name}")

        if hash_key in self._mappings:
            return self._mappings[hash_key].anonymized

        token = self._generate_token("KLASE")
        data = AnonymizedData(original=class_name, anonymized=token, token=hash_key)
        self._mappings[hash_key] = data

        return token

    def anonymize_text(self, text: str, names: list[str] | None = None) -> str:
        """
        Anonimizuoja tekstą - pakeičia vardus tokenais.

        Args:
            text: Tekstas su vardais
            names: Sąrašas vardų kuriuos reikia anonimizuoti

        Returns:
            Anonimizuotas tekstas
        """
        if not text:
            return text

        result = text

        if names:
            for name in names:
                if name and name in result:
                    token = self.anonymize_name(name)
                    result = result.replace(name, token)

        return result

    def deanonymize_text(self, text: str) -> str:
        """
        Atkuria originalius vardus iš tokenų.

        Args:
            text: Anonimizuotas tekstas su tokenais

        Returns:
            Tekstas su originaliais vardais
        """
        if not text:
            return text

        result = text

        for data in self._mappings.values():
            if data.anonymized in result:
                result = result.replace(data.anonymized, data.original)

        return result

    def anonymize_dict(
        self, data: dict[str, Any], fields_to_anonymize: list[str]
    ) -> dict[str, Any]:
        """
        Anonimizuoja nurodytus laukus žodyne.

        Args:
            data: Žodynas su duomenimis
            fields_to_anonymize: Laukų sąrašas kuriuos reikia anonimizuoti

        Returns:
            Žodynas su anonimizuotais laukais
        """
        result = data.copy()

        for field in fields_to_anonymize:
            if field in result and result[field]:
                if field in ("first_name", "last_name", "name"):
                    result[field] = self.anonymize_name(result[field])
                elif field == "student_code":
                    result[field] = self.anonymize_student_code(result[field])
                elif field == "class_name":
                    result[field] = self.anonymize_class(result[field])
                else:
                    result[field] = self.anonymize_name(result[field])

        return result

    def get_mappings(self) -> dict[str, AnonymizedData]:
        """Grąžina visus anonimizavimo susiejimus."""
        return self._mappings.copy()

    def clear_mappings(self) -> None:
        """Išvalo visus susiejimus."""
        self._mappings.clear()
        self._token_counter = 0


# === Convenience functions ===

_default_anonymizer: Anonymizer | None = None


def get_anonymizer() -> Anonymizer:
    """Grąžina globalų anonymizer instance."""
    global _default_anonymizer
    if _default_anonymizer is None:
        _default_anonymizer = Anonymizer()
    return _default_anonymizer


def anonymize_for_api(
    text: str, student_name: str | None = None, class_name: str | None = None
) -> str:
    """
    Paruošia tekstą siuntimui į išorinę API.

    Args:
        text: Tekstas paruošimui
        student_name: Mokinio vardas (bus anonimizuotas)
        class_name: Klasės pavadinimas (bus anonimizuotas)

    Returns:
        Anonimizuotas tekstas
    """
    anonymizer = get_anonymizer()

    names_to_anonymize = []
    if student_name:
        names_to_anonymize.append(student_name)
        # Jei pilnas vardas, pabandyk ir atskiras dalis
        parts = student_name.split()
        names_to_anonymize.extend(parts)

    result = anonymizer.anonymize_text(text, names_to_anonymize)

    if class_name:
        result = result.replace(class_name, anonymizer.anonymize_class(class_name))

    return result


def deanonymize_response(text: str) -> str:
    """
    Atkuria originalius duomenis API atsakyme.

    Args:
        text: API atsakymo tekstas su tokenais

    Returns:
        Tekstas su atkurtais originaliais duomenimis
    """
    anonymizer = get_anonymizer()
    return anonymizer.deanonymize_text(text)


def reset_anonymizer() -> None:
    """Išvalo globalų anonymizer (naudoti po sesijos)."""
    global _default_anonymizer
    if _default_anonymizer:
        _default_anonymizer.clear_mappings()
