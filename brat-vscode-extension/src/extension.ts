import * as vscode from "vscode";

let diagnosticCollection: vscode.DiagnosticCollection;

export function activate(context: vscode.ExtensionContext) {
    diagnosticCollection = vscode.languages.createDiagnosticCollection("brat");

    const runCommand = vscode.commands.registerCommand("brat.runFile", async () => {
        await runBratFile(context, "--run");
    });

    const checkCommand = vscode.commands.registerCommand("brat.checkFile", async () => {
        await runBratFile(context, "--check --json");
    });

    context.subscriptions.push(
        runCommand,
        checkCommand,
        diagnosticCollection
    );
}

export function deactivate() {
    if (diagnosticCollection) {
        diagnosticCollection.dispose();
    }
}

function getActiveBratDocument(): vscode.TextDocument | undefined {
    const editor = vscode.window.activeTextEditor;

    if (!editor) {
        vscode.window.showErrorMessage("No active file is open.");
        return undefined;
    }

    const document = editor.document;

    if (document.languageId !== "brat" && !document.fileName.endsWith(".brt")) {
        vscode.window.showErrorMessage("This is not a BRAT .brt file.");
        return undefined;
    }

    return document;
}

function getPythonPath(): string {
    const config = vscode.workspace.getConfiguration("brat");
    return config.get<string>("pythonPath") || "python";
}

function getCompilerModule(): string {
    const config = vscode.workspace.getConfiguration("brat");
    return config.get<string>("compilerModule") || "compiler.main";
}

function quote(value: string): string {
    return `"${value.replace(/"/g, '\\"')}"`;
}

async function runBratFile(context: vscode.ExtensionContext, mode: string) {
    const document = getActiveBratDocument();

    if (!document) {
        return;
    }

    if (document.isDirty) {
        await document.save();
    }

    const pythonPath = getPythonPath();
    const compilerModule = getCompilerModule();
    const filePath = document.fileName;

    const runtimeRoot = context.asAbsolutePath("brut-runtime");

    const terminal = vscode.window.createTerminal({
        name: "BRUT Compiler",
        cwd: runtimeRoot
    });

    terminal.show();

    const command = `${pythonPath} -m ${compilerModule} ${quote(filePath)} ${mode}`;

    terminal.sendText(
        `Clear-Host; Write-Host "BRUT Compiler" -ForegroundColor Cyan; Write-Host "Running your BRAT file..." -ForegroundColor Green; ${command}`
    );
}