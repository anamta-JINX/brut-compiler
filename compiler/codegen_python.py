from __future__ import annotations

from compiler.ast_nodes import (
    Assignment,
    AskStatement,
    BinaryExpression,
    Expression,
    ExpressionStatement,
    GroupingExpression,
    Identifier,
    IfStatement,
    Literal,
    Program,
    RepeatStatement,
    ShowStatement,
    Statement,
    UnaryExpression,
    VarDeclaration,
    WhileStatement,
)


class PythonCodeGenerator:
    def __init__(self):
        self.lines: list[str] = []
        self.indent_level = 0
        self.repeat_counter = 0

    def generate(self, program: Program) -> str:
        self.lines = []
        self.indent_level = 0
        self.repeat_counter = 0

        self.emit_runtime_helpers()

        for statement in program.statements:
            self.generate_statement(statement)

        return "\n".join(self.lines) + "\n"

    # -------------------------
    # Runtime helper
    # -------------------------

    def emit_runtime_helpers(self) -> None:
        self.emit("def _brat_input(prompt):")
        self.indent_level += 1
        self.emit("value = input(str(prompt) + ': ')")
        self.emit("try:")
        self.indent_level += 1
        self.emit("if '.' in value:")
        self.indent_level += 1
        self.emit("return float(value)")
        self.indent_level -= 1
        self.emit("return int(value)")
        self.indent_level -= 1
        self.emit("except ValueError:")
        self.indent_level += 1
        self.emit("return value")
        self.indent_level -= 1
        self.indent_level -= 1
        self.emit("")

    # -------------------------
    # Statements
    # -------------------------

    def generate_statement(self, statement: Statement) -> None:
        if isinstance(statement, VarDeclaration):
            self.generate_var_declaration(statement)
            return

        if isinstance(statement, Assignment):
            self.generate_assignment(statement)
            return

        if isinstance(statement, ShowStatement):
            self.generate_show_statement(statement)
            return

        if isinstance(statement, AskStatement):
            self.generate_ask_statement(statement)
            return

        if isinstance(statement, IfStatement):
            self.generate_if_statement(statement)
            return

        if isinstance(statement, WhileStatement):
            self.generate_while_statement(statement)
            return

        if isinstance(statement, RepeatStatement):
            self.generate_repeat_statement(statement)
            return

        if isinstance(statement, ExpressionStatement):
            self.emit(self.generate_expression(statement.expression))
            return

        raise Exception(f"Unsupported statement type: {type(statement).__name__}")

    def generate_var_declaration(self, statement: VarDeclaration) -> None:
        value = self.generate_expression(statement.value)
        self.emit(f"{statement.name} = {value}")

    def generate_assignment(self, statement: Assignment) -> None:
        value = self.generate_expression(statement.value)
        self.emit(f"{statement.name} = {value}")

    def generate_show_statement(self, statement: ShowStatement) -> None:
        value = self.generate_expression(statement.value)
        self.emit(f"print({value})")

    def generate_ask_statement(self, statement: AskStatement) -> None:
        prompt = self.generate_expression(statement.prompt)
        self.emit(f"{statement.variable_name} = _brat_input({prompt})")

    def generate_if_statement(self, statement: IfStatement) -> None:
        condition = self.generate_expression(statement.condition)

        self.emit(f"if {condition}:")
        self.indent_level += 1

        if statement.then_branch:
            for body_statement in statement.then_branch:
                self.generate_statement(body_statement)
        else:
            self.emit("pass")

        self.indent_level -= 1

        if statement.else_branch is not None:
            self.emit("else:")
            self.indent_level += 1

            if statement.else_branch:
                for body_statement in statement.else_branch:
                    self.generate_statement(body_statement)
            else:
                self.emit("pass")

            self.indent_level -= 1

    def generate_while_statement(self, statement: WhileStatement) -> None:
        condition = self.generate_expression(statement.condition)

        self.emit(f"while {condition}:")
        self.indent_level += 1

        if statement.body:
            for body_statement in statement.body:
                self.generate_statement(body_statement)
        else:
            self.emit("pass")

        self.indent_level -= 1

    def generate_repeat_statement(self, statement: RepeatStatement) -> None:
        loop_var = f"_brat_repeat_{self.repeat_counter}"
        self.repeat_counter += 1

        count = self.generate_expression(statement.count)

        self.emit(f"for {loop_var} in range(int({count})):")
        self.indent_level += 1

        if statement.body:
            for body_statement in statement.body:
                self.generate_statement(body_statement)
        else:
            self.emit("pass")

        self.indent_level -= 1

    # -------------------------
    # Expressions
    # -------------------------

    def generate_expression(self, expression: Expression) -> str:
        if isinstance(expression, Literal):
            return self.generate_literal(expression)

        if isinstance(expression, Identifier):
            return expression.name

        if isinstance(expression, BinaryExpression):
            left = self.generate_expression(expression.left)
            right = self.generate_expression(expression.right)
            operator = self.map_operator(expression.operator)
            return f"({left} {operator} {right})"

        if isinstance(expression, UnaryExpression):
            right = self.generate_expression(expression.right)
            operator = self.map_operator(expression.operator)
            return f"({operator} {right})"

        if isinstance(expression, GroupingExpression):
            inner = self.generate_expression(expression.expression)
            return f"({inner})"

        raise Exception(f"Unsupported expression type: {type(expression).__name__}")

    def generate_literal(self, expression: Literal) -> str:
        value = expression.value

        if isinstance(value, str):
            return repr(value)

        if value is True:
            return "True"

        if value is False:
            return "False"

        if value is None:
            return "None"

        return str(value)

    def map_operator(self, operator: str) -> str:
        operators = {
            "+": "+",
            "-": "-",
            "*": "*",
            "/": "/",
            "%": "%",
            "**": "**",
            "==": "==",
            "!=": "!=",
            ">": ">",
            ">=": ">=",
            "<": "<",
            "<=": "<=",
            "and": "and",
            "or": "or",
            "not": "not",
        }

        if operator not in operators:
            raise Exception(f"Unsupported operator: {operator}")

        return operators[operator]

    # -------------------------
    # Helper
    # -------------------------

    def emit(self, line: str) -> None:
        self.lines.append("    " * self.indent_level + line)