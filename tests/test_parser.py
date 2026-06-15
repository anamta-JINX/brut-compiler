import json

from compiler.lexer import Lexer
from compiler.parser import Parser


source = '''
show("BRAT parser is working");

mut running = aura.true;

while running {
    ask("Enter choice") -> choice;

    if choice == 0 {
        show("bye");
        running = aura.false;
    }
    else {
        show("still running");
    };
};
'''

lexer = Lexer(source)
tokens = lexer.tokenize()

parser = Parser(tokens)
program = parser.parse()

print(json.dumps(program.to_dict(), indent=2))