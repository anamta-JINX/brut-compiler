from __future__ import annotations

from dataclasses import dataclass
from typing import Any


# -------------------------
# Base nodes
# -------------------------

class ASTNode:
    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError


class Statement(ASTNode):
    pass


class Expression(ASTNode):
    pass


# -------------------------
# Program
# -------------------------

@dataclass
class Program(ASTNode):
    statements: list[Statement]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "Program",
            "statements": [statement.to_dict() for statement in self.statements],
        }


# -------------------------
# Statements
# -------------------------

@dataclass
class VarDeclaration(Statement):
    name: str
    value: Expression
    mutable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "VarDeclaration",
            "name": self.name,
            "mutable": self.mutable,
            "value": self.value.to_dict(),
        }


@dataclass
class Assignment(Statement):
    name: str
    value: Expression

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "Assignment",
            "name": self.name,
            "value": self.value.to_dict(),
        }


@dataclass
class ShowStatement(Statement):
    value: Expression

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "ShowStatement",
            "value": self.value.to_dict(),
        }


@dataclass
class AskStatement(Statement):
    prompt: Expression
    variable_name: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "AskStatement",
            "prompt": self.prompt.to_dict(),
            "variable_name": self.variable_name,
        }


@dataclass
class IfStatement(Statement):
    condition: Expression
    then_branch: list[Statement]
    else_branch: list[Statement] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "IfStatement",
            "condition": self.condition.to_dict(),
            "then_branch": [statement.to_dict() for statement in self.then_branch],
            "else_branch": (
                [statement.to_dict() for statement in self.else_branch]
                if self.else_branch is not None
                else None
            ),
        }


@dataclass
class WhileStatement(Statement):
    condition: Expression
    body: list[Statement]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "WhileStatement",
            "condition": self.condition.to_dict(),
            "body": [statement.to_dict() for statement in self.body],
        }


@dataclass
class RepeatStatement(Statement):
    count: Expression
    body: list[Statement]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "RepeatStatement",
            "count": self.count.to_dict(),
            "body": [statement.to_dict() for statement in self.body],
        }


@dataclass
class ExpressionStatement(Statement):
    expression: Expression

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "ExpressionStatement",
            "expression": self.expression.to_dict(),
        }


# -------------------------
# Expressions
# -------------------------

@dataclass
class Literal(Expression):
    value: Any

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "Literal",
            "value": self.value,
        }


@dataclass
class Identifier(Expression):
    name: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "Identifier",
            "name": self.name,
        }


@dataclass
class BinaryExpression(Expression):
    left: Expression
    operator: str
    right: Expression

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "BinaryExpression",
            "left": self.left.to_dict(),
            "operator": self.operator,
            "right": self.right.to_dict(),
        }


@dataclass
class UnaryExpression(Expression):
    operator: str
    right: Expression

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "UnaryExpression",
            "operator": self.operator,
            "right": self.right.to_dict(),
        }


@dataclass
class GroupingExpression(Expression):
    expression: Expression

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "GroupingExpression",
            "expression": self.expression.to_dict(),
        }