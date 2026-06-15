import json

from compiler.ast_nodes import (
    Assignment,
    BinaryExpression,
    Identifier,
    IfStatement,
    Literal,
    Program,
    ShowStatement,
    VarDeclaration,
    WhileStatement,
)


program = Program(
    statements=[
        ShowStatement(
            value=Literal("BRAT AST is working")
        ),
        VarDeclaration(
            name="running",
            value=Literal(True),
            mutable=True,
        ),
        WhileStatement(
            condition=Identifier("running"),
            body=[
                IfStatement(
                    condition=BinaryExpression(
                        left=Identifier("choice"),
                        operator="==",
                        right=Literal(0),
                    ),
                    then_branch=[
                        ShowStatement(Literal("bye")),
                        Assignment(
                            name="running",
                            value=Literal(False),
                        ),
                    ],
                    else_branch=[
                        ShowStatement(Literal("still running")),
                    ],
                )
            ],
        ),
    ]
)

print(json.dumps(program.to_dict(), indent=2))