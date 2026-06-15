from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from compiler.codegen_python import PythonCodeGenerator
from compiler.errors import BratError, LexicalError, ParserError, SemanticError
from compiler.lexer import Lexer
from compiler.parser import Parser


def print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def get_error_code(error: Exception) -> str:
    if isinstance(error, LexicalError):
        return "BRAT_LEX_002"

    if isinstance(error, ParserError):
        return "BRAT_PARSE_003"

    if isinstance(error, SemanticError):
        return "BRAT_SEMANTIC_004"

    if isinstance(error, BratError):
        return "BRAT_ERROR_005"

    return "BRUT_COMPILER_001"


def is_missing_syntax_error(message: str) -> bool:
    lowered = message.lower()

    syntax_words = [
        "expected",
        "semicolon",
        "`;`",
        "missing",
        "after",
        "before",
        "syntax",
        "brace",
        "paren",
        "parenthesis",
        "}",
        "{",
        ")",
        "(",
    ]

    return any(word in lowered for word in syntax_words)


def is_semicolon_error(message: str) -> bool:
    lowered = message.lower()
    return "`;`" in lowered or "semicolon" in lowered


def is_repeat_error(message: str) -> bool:
    lowered = message.lower()
    return "repeat" in lowered or "times" in lowered or "`times`" in lowered


def get_fix_suggestion(message: str) -> str:
    lowered = message.lower()

    if "`;`" in lowered or "semicolon" in lowered:
        return "You probably forgot a semicolon `;`, shawty."

    if "`times`" in lowered or "times" in lowered:
        return "Use repeat like this: repeat 5 times { show(\"hi\"); };"

    if "`}`" in lowered or "right_brace" in lowered:
        return "Close your block with `}` and then add `;` after the block."

    if "`{`" in lowered or "left_brace" in lowered:
        return "Open the block with `{` after your condition or loop statement."

    if "`)`" in lowered or "right_paren" in lowered:
        return "Close your brackets properly with `)`."

    if "`(`" in lowered or "left_paren" in lowered:
        return "Open your function call with `(`."

    if "expected expression" in lowered:
        return "BRAT expected a value, variable, number, string, or expression here."

    return "Check the syntax near this line and fix the BRAT statement."


def get_roast_line(error_code: str, message: str) -> str:
    if is_semicolon_error(message):
        return "You probably forgot a semicolon `;`, shawty."

    if is_missing_syntax_error(message):
        return "This is not a bug. This is a cry for help."

    if error_code.startswith("BRAT_LEX"):
        return "it couldn't pass the vibe check"

    if error_code.startswith("BRAT_PARSE"):
        return "Bestie, this is not giving."

    if error_code.startswith("BRAT_SEMANTIC"):
        return "Bruh… it couldn't pass the vibe check."

    if error_code.startswith("BRUT_COMPILER"):
        return "This is not a bug. This is a cry for help."

    return "Fix it, fineshyt. BRAT is watching 👀"


def error_payload(
    message: str,
    line: int = 1,
    column: int = 1,
    error_code: str = "BRAT_ERROR_001",
) -> dict[str, Any]:
    return {
        "success": False,
        "error_intro": f"BRAT had a breakdown at line {line} 💀",
        "vibe": get_roast_line(error_code, message),
        "errors": [
            {
                "line": line,
                "column": column,
                "code": error_code,
                "message": message,
                "fix": get_fix_suggestion(message),
            }
        ],
    }


def print_brat_error(message: str, line: int, column: int, error_code: str) -> None:
    roast_line = get_roast_line(error_code, message)
    fix = get_fix_suggestion(message)

    print(f"BRAT had a breakdown at line {line} 💀")
    print(roast_line)
    print()
    print(f"Error Code : {error_code}")
    print(f"Line       : {line}")
    print(f"Column     : {column}")
    print(f"Issue      : {message}")

    if fix != roast_line:
        print(f"Fix        : {fix}")

    print()
    print("Fix it, fineshyt. BRAT is watching 👀")


def print_compiler_error(message: str) -> None:
    print("BRAT had a breakdown at line 1 💀")
    print("This is not a bug. This is a cry for help.")
    print()
    print("Error Code : BRUT_COMPILER_001")
    print("Line       : 1")
    print("Column     : 1")
    print(f"Issue      : {message}")
    print("Fix        : Check the compiler setup or the generated Python output.")
    print()
    print("Fix it, fineshyt. BRAT is watching 👀")


def read_source(source_path: Path) -> str:
    return source_path.read_text(encoding="utf-8")


def tokenize_source(source: str):
    lexer = Lexer(source)
    return lexer.tokenize()


def parse_source(source: str):
    tokens = tokenize_source(source)
    parser = Parser(tokens)
    return parser.parse()


def compile_to_python(source_path: Path) -> str:
    source = read_source(source_path)
    program = parse_source(source)

    generator = PythonCodeGenerator()
    return generator.generate(program)


def check_file(source_path: Path) -> dict[str, Any]:
    compile_to_python(source_path)
    return {
        "success": True,
        "errors": [],
    }


def write_generated_python(source_path: Path, python_code: str) -> Path:
    generated_dir = Path("generated")
    generated_dir.mkdir(exist_ok=True)

    output_path = generated_dir / f"{source_path.stem}_generated.py"
    output_path.write_text(python_code, encoding="utf-8")

    return output_path


def run_file(source_path: Path) -> int:
    python_code = compile_to_python(source_path)
    output_path = write_generated_python(source_path, python_code)

    result = subprocess.run(
        [sys.executable, str(output_path)],
        text=True,
    )

    return result.returncode


def main() -> None:
    arg_parser = argparse.ArgumentParser(description="BRUT Compiler for BRAT language")

    arg_parser.add_argument("file", help="Path to .brt file")

    arg_parser.add_argument("--tokens", action="store_true", help="Print tokens")
    arg_parser.add_argument("--ast", action="store_true", help="Print AST")
    arg_parser.add_argument("--python", action="store_true", help="Print generated Python code")
    arg_parser.add_argument("--check", action="store_true", help="Check file for compiler errors")
    arg_parser.add_argument("--run", action="store_true", help="Run BRAT file")
    arg_parser.add_argument("--json", action="store_true", help="Output JSON where supported")

    args = arg_parser.parse_args()

    source_path = Path(args.file)

    if not source_path.exists():
        message = f"File not found: {source_path}"
        payload = error_payload(
            message=message,
            line=1,
            column=1,
            error_code="BRAT_FILE_404",
        )

        if args.json:
            print_json(payload)
        else:
            print_brat_error(
                message=message,
                line=1,
                column=1,
                error_code="BRAT_FILE_404",
            )

        sys.exit(1)

    try:
        source = read_source(source_path)

        if args.tokens:
            tokens = tokenize_source(source)
            token_data = [token.to_dict() for token in tokens]

            if args.json:
                print_json(token_data)
            else:
                for token in tokens:
                    print(token)

            return

        if args.ast:
            program = parse_source(source)

            if args.json:
                print_json(program.to_dict())
            else:
                print_json(program.to_dict())

            return

        if args.python:
            python_code = compile_to_python(source_path)
            print(python_code)
            return

        if args.check:
            payload = check_file(source_path)

            if args.json:
                print_json(payload)
            else:
                print("BRAT check passed.")

            return

        if args.run:
            exit_code = run_file(source_path)
            sys.exit(exit_code)

        print("BRUT is ready.")
        print("Use one of these:")
        print("  --tokens")
        print("  --ast")
        print("  --python")
        print("  --check")
        print("  --run")

    except (LexicalError, ParserError, SemanticError, BratError) as error:
        message = getattr(error, "message", str(error))
        line = getattr(error, "line", 1)
        column = getattr(error, "column", 1)
        error_code = get_error_code(error)

        payload = error_payload(
            message=message,
            line=line,
            column=column,
            error_code=error_code,
        )

        if args.json:
            print_json(payload)
        else:
            print_brat_error(
                message=message,
                line=line,
                column=column,
                error_code=error_code,
            )

        sys.exit(1)

    except Exception as error:
        message = str(error)

        payload = error_payload(
            message=message,
            line=1,
            column=1,
            error_code="BRUT_COMPILER_001",
        )

        if args.json:
            print_json(payload)
        else:
            print_compiler_error(message)

        sys.exit(1)


if __name__ == "__main__":
    main()