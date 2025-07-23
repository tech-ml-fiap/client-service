from __future__ import annotations
from dataclasses import dataclass
import re

_DIGITS_RE = re.compile(r"\D+")


def _calc_digit(seq: str) -> str:
    soma = sum(int(d) * (len(seq) + 1 - i) for i, d in enumerate(seq))
    resto = soma % 11
    return "0" if resto < 2 else str(11 - resto)


@dataclass(frozen=True, slots=True)
class CPF:
    """CPF sempre armazenado como 11 dígitos."""

    value: str

    def __post_init__(self) -> None:
        digits = _DIGITS_RE.sub("", self.value)
        object.__setattr__(self, "value", digits)

        if len(digits) != 11 or not digits.isdigit():
            raise ValueError("CPF inválido (tamanho)")
        if digits == digits[0] * 11:
            raise ValueError("CPF inválido (sequência repetida)")
        if digits[-2:] != _calc_digit(digits[:9]) + _calc_digit(digits[:10]):
            raise ValueError("CPF inválido (dígitos verificadores)")

    def formatted(self) -> str:
        v = self.value
        return f"{v[:3]}.{v[3:6]}.{v[6:9]}-{v[9:]}"

    def __str__(self) -> str:
        return self.formatted()
