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
    ShowStatement,
    Statement,
    UnaryExpression,
    VarDeclaration,
    WhileStatement,
)
from compiler.errors import ParserError
from compiler.tokens import Token, TokenType


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> Program:
        statements: list[Statement] = []

        while not self.is_at_end():
            statements.append(self.declaration())

        return Program(statements)

    # -------------------------
    # Declarations / statements
    # -------------------------

    def declaration(self) -> Statement:
        if self.match(TokenType.LET):
            return self.var_declaration(mutable=False)

        if self.match(TokenType.MUT):
            return self.var_declaration(mutable=True)

        return self.statement()

    def var_declaration(self, mutable: bool) -> Statement:
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name.")
        self.consume(TokenType.EQUAL, "Expected `=` after variable name.")

        value = self.expression()

        self.consume(TokenType.SEMICOLON, "Expected `;` after variable declaration.")

        return VarDeclaration(
            name=str(name.value),
            value=value,
            mutable=mutable,
        )

    def statement(self) -> Statement:
        if self.match(TokenType.SHOW):
            return self.show_statement()

        if self.match(TokenType.SAY):
            return self.show_statement()

        if self.match(TokenType.ASK):
            return self.ask_statement()

        if self.match(TokenType.IF):
            return self.if_statement()

        if self.match(TokenType.WHILE):
            return self.while_statement()

        if self.check(TokenType.IDENTIFIER) and self.check_next(TokenType.EQUAL):
            return self.assignment_statement()

        return self.expression_statement()

    def show_statement(self) -> Statement:
        self.consume(TokenType.LEFT_PAREN, "Expected `(` after show/say.")

        value = self.expression()

        self.consume(TokenType.RIGHT_PAREN, "Expected `)` after show/say value.")
        self.consume(TokenType.SEMICOLON, "Expected `;` after show/say statement.")

        return ShowStatement(value=value)

    def ask_statement(self) -> Statement:
        self.consume(TokenType.LEFT_PAREN, "Expected `(` after ask.")

        prompt = self.expression()

        self.consume(TokenType.RIGHT_PAREN, "Expected `)` after ask prompt.")
        self.consume(TokenType.ARROW, "Expected `->` after ask prompt.")

        variable = self.consume(TokenType.IDENTIFIER, "Expected variable name after `->`.")

        self.consume(TokenType.SEMICOLON, "Expected `;` after ask statement.")

        return AskStatement(
            prompt=prompt,
            variable_name=str(variable.value),
        )

    def assignment_statement(self) -> Statement:
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name.")
        self.consume(TokenType.EQUAL, "Expected `=` in assignment.")

        value = self.expression()

        self.consume(TokenType.SEMICOLON, "Expected `;` after assignment.")

        return Assignment(
            name=str(name.value),
            value=value,
        )

    def if_statement(self) -> Statement:
        condition = self.expression()

        self.consume(TokenType.LEFT_BRACE, "Expected `{` after if condition.")

        then_branch = self.block_statements()

        self.consume(TokenType.RIGHT_BRACE, "Expected `}` after if block.")

        else_branch: list[Statement] | None = None

        if self.match(TokenType.ELSE):
            self.consume(TokenType.LEFT_BRACE, "Expected `{` after else.")

            else_branch = self.block_statements()

            self.consume(TokenType.RIGHT_BRACE, "Expected `}` after else block.")

        self.consume(TokenType.SEMICOLON, "Expected `;` after if/else block.")

        return IfStatement(
            condition=condition,
            then_branch=then_branch,
            else_branch=else_branch,
        )

    def while_statement(self) -> Statement:
        condition = self.expression()

        self.consume(TokenType.LEFT_BRACE, "Expected `{` after while condition.")

        body = self.block_statements()

        self.consume(TokenType.RIGHT_BRACE, "Expected `}` after while block.")
        self.consume(TokenType.SEMICOLON, "Expected `;` after while block.")

        return WhileStatement(
            condition=condition,
            body=body,
        )

    def block_statements(self) -> list[Statement]:
        statements: list[Statement] = []

        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())

        return statements

    def expression_statement(self) -> Statement:
        expr = self.expression()

        self.consume(TokenType.SEMICOLON, "Expected `;` after expression.")

        return ExpressionStatement(expression=expr)

    # -------------------------
    # Expressions
    # -------------------------

    def expression(self) -> Expression:
        return self.or_expression()

    def or_expression(self) -> Expression:
        expr = self.and_expression()

        while self.match(TokenType.OR):
            operator = str(self.previous().value)
            right = self.and_expression()
            expr = BinaryExpression(expr, operator, right)

        return expr

    def and_expression(self) -> Expression:
        expr = self.equality()

        while self.match(TokenType.AND):
            operator = str(self.previous().value)
            right = self.equality()
            expr = BinaryExpression(expr, operator, right)

        return expr

    def equality(self) -> Expression:
        expr = self.comparison()

        while self.match(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
            operator = str(self.previous().value)
            right = self.comparison()
            expr = BinaryExpression(expr, operator, right)

        return expr

    def comparison(self) -> Expression:
        expr = self.term()

        while self.match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = str(self.previous().value)
            right = self.term()
            expr = BinaryExpression(expr, operator, right)

        return expr

    def term(self) -> Expression:
        expr = self.factor()

        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = str(self.previous().value)
            right = self.factor()
            expr = BinaryExpression(expr, operator, right)

        return expr

    def factor(self) -> Expression:
        expr = self.power()

        while self.match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            operator = str(self.previous().value)
            right = self.power()
            expr = BinaryExpression(expr, operator, right)

        return expr

    def power(self) -> Expression:
        expr = self.unary()

        if self.match(TokenType.POWER):
            operator = str(self.previous().value)
            right = self.power()
            expr = BinaryExpression(expr, operator, right)

        return expr

    def unary(self) -> Expression:
        if self.match(TokenType.NOT, TokenType.MINUS):
            operator = str(self.previous().value)
            right = self.unary()
            return UnaryExpression(operator, right)

        return self.primary()

    def primary(self) -> Expression:
        if self.match(TokenType.NUMBER):
            return Literal(self.previous().value)

        if self.match(TokenType.STRING):
            return Literal(self.previous().value)

        if self.match(TokenType.AURA_TRUE):
            return Literal(True)

        if self.match(TokenType.AURA_FALSE):
            return Literal(False)

        if self.match(TokenType.NULL):
            return Literal(None)

        if self.match(TokenType.ANY):
            return Literal(None)

        if self.match(TokenType.IDENTIFIER):
            return Identifier(str(self.previous().value))

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected `)` after expression.")
            return GroupingExpression(expr)

        token = self.peek()
        raise ParserError(
            f"Expected expression, got `{token.value}`.",
            token.line,
            token.column,
        )

    # -------------------------
    # Helpers
    # -------------------------

    def match(self, *types: TokenType) -> bool:
        for token_type in types:
            if self.check(token_type):
                self.advance()
                return True

        return False

    def consume(self, token_type: TokenType, message: str) -> Token:
        if self.check(token_type):
            return self.advance()

        token = self.peek()
        raise ParserError(message, token.line, token.column)

    def check(self, token_type: TokenType) -> bool:
        if self.is_at_end():
            return False

        return self.peek().type == token_type

    def check_next(self, token_type: TokenType) -> bool:
        if self.current + 1 >= len(self.tokens):
            return False

        return self.tokens[self.current + 1].type == token_type

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1

        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]