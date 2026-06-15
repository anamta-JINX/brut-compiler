from compiler.lexer import Lexer


source = '''
show("hello");
mut running = aura.true;

while running {
    ask("Enter choice") -> choice;

    if choice == 0 {
        show("bye");
        running = aura.false;
    };
};
'''

lexer = Lexer(source)
tokens = lexer.tokenize()

for token in tokens:
    print(token)