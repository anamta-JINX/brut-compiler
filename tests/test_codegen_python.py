from compiler.codegen_python import PythonCodeGenerator
from compiler.lexer import Lexer
from compiler.parser import Parser


source = '''
show("BRAT codegen is working");

let x = 2 + 3 * 4;
mut running = aura.true;

if x > 10 {
    show("x is bigger than 10");
    show(x);
}
else {
    show("x is small");
};

while running {
    show("loop runs once");
    running = aura.false;
};
'''

lexer = Lexer(source)
tokens = lexer.tokenize()

parser = Parser(tokens)
program = parser.parse()

generator = PythonCodeGenerator()
python_code = generator.generate(program)

print("========== GENERATED PYTHON ==========")
print(python_code)

print("========== PROGRAM OUTPUT ==========")
exec(python_code)