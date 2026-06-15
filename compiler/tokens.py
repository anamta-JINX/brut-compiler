from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TokenType(str, Enum):
    # Single-character tokens
    LEFT_PAREN = "LEFT_PAREN"
    RIGHT_PAREN = "RIGHT_PAREN"
    LEFT_BRACE = "LEFT_BRACE"
    RIGHT_BRACE = "RIGHT_BRACE"
    LEFT_BRACKET = "LEFT_BRACKET"
    RIGHT_BRACKET = "RIGHT_BRACKET"
    COMMA = "COMMA"
    DOT = "DOT"
    COLON = "COLON"
    SEMICOLON = "SEMICOLON"

    # Operators
    PLUS = "PLUS"
    MINUS = "MINUS"
    STAR = "STAR"
    SLASH = "SLASH"
    PERCENT = "PERCENT"
    POWER = "POWER"

    EQUAL = "EQUAL"
    EQUAL_EQUAL = "EQUAL_EQUAL"
    BANG_EQUAL = "BANG_EQUAL"

    GREATER = "GREATER"
    GREATER_EQUAL = "GREATER_EQUAL"
    LESS = "LESS"
    LESS_EQUAL = "LESS_EQUAL"

    ARROW = "ARROW"

    # Literals
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING = "STRING"

    # Keywords
    LET = "LET"
    MUT = "MUT"
    FUN = "FUN"
    RETURN = "RETURN"

    IF = "IF"
    ELSE = "ELSE"
    WHILE = "WHILE"
    REPEAT = "REPEAT"
    TIMES = "TIMES"

    LOOP = "LOOP"
    FOREVER = "FOREVER"
    FROM = "FROM"
    TO = "TO"
    IN = "IN"

    SAY = "SAY"
    SHOW = "SHOW"
    ASK = "ASK"

    AND = "AND"
    OR = "OR"
    NOT = "NOT"

    AURA_TRUE = "AURA_TRUE"
    AURA_FALSE = "AURA_FALSE"
    NULL = "NULL"
    ANY = "ANY"

    EOF = "EOF"


KEYWORDS: dict[str, TokenType] = {
    "let": TokenType.LET,
    "mut": TokenType.MUT,
    "fun": TokenType.FUN,
    "return": TokenType.RETURN,

    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "repeat": TokenType.REPEAT,
    "times": TokenType.TIMES,

    "loop": TokenType.LOOP,
    "forever": TokenType.FOREVER,
    "from": TokenType.FROM,
    "to": TokenType.TO,
    "in": TokenType.IN,

    "say": TokenType.SAY,
    "show": TokenType.SHOW,
    "ask": TokenType.ASK,

    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,

    "aura.true": TokenType.AURA_TRUE,
    "aura.false": TokenType.AURA_FALSE,
    "null": TokenType.NULL,
    "any": TokenType.ANY,
}


@dataclass
class Token:
    type: TokenType
    value: object
    line: int
    column: int

    def to_dict(self) -> dict[str, object]:
        return {
            "type": self.type.value,
            "value": self.value,
            "line": self.line,
            "column": self.column,
        }

    def __repr__(self) -> str:
        return (
            f"Token(type={self.type.value}, "
            f"value={self.value!r}, "
            f"line={self.line}, "
            f"column={self.column})"
        )