from __future__ import annotations

from compiler.errors import LexicalError
from compiler.tokens import KEYWORDS, Token, TokenType


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.tokens: list[Token] = []

        self.start = 0
        self.current = 0

        self.line = 1
        self.column = 1
        self.token_column = 1

    def tokenize(self) -> list[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.token_column = self.column
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def advance(self) -> str:
        char = self.source[self.current]
        self.current += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def peek(self) -> str:
        if self.is_at_end():
            return "\0"
        return self.source[self.current]

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def match(self, expected: str) -> bool:
        if self.is_at_end():
            return False

        if self.source[self.current] != expected:
            return False

        self.advance()
        return True

    def add_token(self, token_type: TokenType, value: object | None = None) -> None:
        if value is None:
            value = self.source[self.start:self.current]

        self.tokens.append(Token(token_type, value, self.line, self.token_column))

    def scan_token(self) -> None:
        char = self.advance()

        # Whitespace
        if char in (" ", "\r", "\t"):
            return

        if char == "\n":
            return

        # Comments
        if char == "/":
            if self.match("/"):
                self.skip_line_comment()
                return

            self.add_token(TokenType.SLASH)
            return

        # Single-character tokens
        if char == "(":
            self.add_token(TokenType.LEFT_PAREN)
            return

        if char == ")":
            self.add_token(TokenType.RIGHT_PAREN)
            return

        if char == "{":
            self.add_token(TokenType.LEFT_BRACE)
            return

        if char == "}":
            self.add_token(TokenType.RIGHT_BRACE)
            return

        if char == "[":
            self.add_token(TokenType.LEFT_BRACKET)
            return

        if char == "]":
            self.add_token(TokenType.RIGHT_BRACKET)
            return

        if char == ",":
            self.add_token(TokenType.COMMA)
            return

        if char == ".":
            self.add_token(TokenType.DOT)
            return

        if char == ":":
            self.add_token(TokenType.COLON)
            return

        if char == ";":
            self.add_token(TokenType.SEMICOLON)
            return

        if char == "+":
            self.add_token(TokenType.PLUS)
            return

        if char == "-":
            if self.match(">"):
                self.add_token(TokenType.ARROW)
            else:
                self.add_token(TokenType.MINUS)
            return

        if char == "*":
            if self.match("*"):
                self.add_token(TokenType.POWER)
            else:
                self.add_token(TokenType.STAR)
            return

        if char == "%":
            self.add_token(TokenType.PERCENT)
            return

        # One or two character tokens
        if char == "=":
            if self.match("="):
                self.add_token(TokenType.EQUAL_EQUAL)
            else:
                self.add_token(TokenType.EQUAL)
            return

        if char == "!":
            if self.match("="):
                self.add_token(TokenType.BANG_EQUAL)
                return

            raise LexicalError("Unexpected character `!`. Did you mean `!=`?", self.line, self.token_column)

        if char == ">":
            if self.match("="):
                self.add_token(TokenType.GREATER_EQUAL)
            else:
                self.add_token(TokenType.GREATER)
            return

        if char == "<":
            if self.match("="):
                self.add_token(TokenType.LESS_EQUAL)
            else:
                self.add_token(TokenType.LESS)
            return

        # String
        if char == '"':
            self.string()
            return

        # Number
        if char.isdigit():
            self.number()
            return

        # Identifier / keyword
        if self.is_alpha(char):
            self.identifier()
            return

        raise LexicalError(f"Unexpected character `{char}`.", self.line, self.token_column)

    def skip_line_comment(self) -> None:
        while self.peek() != "\n" and not self.is_at_end():
            self.advance()

    def string(self) -> None:
        value = ""

        while self.peek() != '"' and not self.is_at_end():
            char = self.advance()

            if char == "\n":
                raise LexicalError("Unterminated string.", self.line, self.token_column)

            value += char

        if self.is_at_end():
            raise LexicalError("Unterminated string.", self.line, self.token_column)

        # Consume closing quote
        self.advance()

        self.add_token(TokenType.STRING, value)

    def number(self) -> None:
        while self.peek().isdigit():
            self.advance()

        is_float = False

        if self.peek() == "." and self.peek_next().isdigit():
            is_float = True
            self.advance()

            while self.peek().isdigit():
                self.advance()

        text = self.source[self.start:self.current]

        if is_float:
            self.add_token(TokenType.NUMBER, float(text))
        else:
            self.add_token(TokenType.NUMBER, int(text))

    def identifier(self) -> None:
        while self.is_alpha_numeric(self.peek()):
            self.advance()

        text = self.source[self.start:self.current]

        # Special handling for aura.true / aura.false
        if text == "aura" and self.peek() == ".":
            saved_current = self.current
            saved_column = self.column

            self.advance()  # consume dot

            dot_part_start = self.current

            while self.is_alpha_numeric(self.peek()):
                self.advance()

            after_dot = self.source[dot_part_start:self.current]
            full_text = f"aura.{after_dot}"

            if full_text in KEYWORDS:
                self.add_token(KEYWORDS[full_text], full_text)
                return

            self.current = saved_current
            self.column = saved_column

        token_type = KEYWORDS.get(text, TokenType.IDENTIFIER)
        self.add_token(token_type, text)

    def is_alpha(self, char: str) -> bool:
        return char.isalpha() or char == "_"

    def is_alpha_numeric(self, char: str) -> bool:
        return char.isalnum() or char == "_"