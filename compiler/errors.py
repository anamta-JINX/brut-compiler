from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BratError(Exception):
    message: str
    line: int = 1
    column: int = 1

    def __str__(self) -> str:
        return f"{self.message} at line {self.line}, column {self.column}"


class LexicalError(BratError):
    pass


class ParserError(BratError):
    pass


class SemanticError(BratError):
    pass