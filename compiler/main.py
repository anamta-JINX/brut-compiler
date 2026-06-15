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


def error_payload(message: str, line: int = 1, column: int = 1) -> dict[str, Any]:
    return {
        "success": False,
        "errors": [
            {
                "line": line,
                "column": column,
                "message": message,
            }
        ],
    }


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
        payload = error_payload(f"File not found: {source_path}")

        if args.json:
            print_json(payload)
        else:
            print(f"Error: File not found: {source_path}")

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
        payload = error_payload(
            getattr(error, "message", str(error)),
            getattr(error, "line", 1),
            getattr(error, "column", 1),
        )

        if args.json:
            print_json(payload)
        else:
            print(f"BRAT Error at line {payload['errors'][0]['line']}: {payload['errors'][0]['message']}")

        sys.exit(1)

    except Exception as error:
        payload = error_payload(str(error))

        if args.json:
            print_json(payload)
        else:
            print(f"Compiler Error: {error}")

        sys.exit(1)


if __name__ == "__main__":
    main()