cd C:\Users\HP\Desktop\BRUT

Write-Host "Preparing BRUT VS Code extension..." -ForegroundColor Cyan

Remove-Item -Recurse -Force brat-vscode-extension\brut-runtime -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force brat-vscode-extension\brut-runtime | Out-Null

Copy-Item -Recurse -Force compiler brat-vscode-extension\brut-runtime\compiler
New-Item -ItemType Directory -Force brat-vscode-extension\brut-runtime\generated | Out-Null

cd brat-vscode-extension

Write-Host "Cleaning old VSIX files..." -ForegroundColor Yellow
Remove-Item -Force *.vsix -ErrorAction SilentlyContinue

Write-Host "Installing VSCE if needed..." -ForegroundColor Green
npm install --save-dev @vscode/vsce

Write-Host "Compiling extension..." -ForegroundColor Green
npm run compile

if ($LASTEXITCODE -ne 0) {
    Write-Host "Compile failed. Stopping build." -ForegroundColor Red
    cd ..
    Remove-Item -Recurse -Force brat-vscode-extension\brut-runtime -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "Packaging VSIX..." -ForegroundColor Green
npx vsce package --allow-missing-repository

if ($LASTEXITCODE -ne 0) {
    Write-Host "VSIX packaging failed. No file was created." -ForegroundColor Red
    cd ..
    Remove-Item -Recurse -Force brat-vscode-extension\brut-runtime -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "Renaming VSIX file..." -ForegroundColor Green
$vsixFile = Get-ChildItem -Filter "*.vsix" | Select-Object -First 1

if ($null -eq $vsixFile) {
    Write-Host "No VSIX file found to rename." -ForegroundColor Red
    cd ..
    Remove-Item -Recurse -Force brat-vscode-extension\brut-runtime -ErrorAction SilentlyContinue
    exit 1
}

Rename-Item -Path $vsixFile.Name -NewName "brut-compiler.vsix"

cd ..

Write-Host "Cleaning temporary brut-runtime folder..." -ForegroundColor Yellow
Remove-Item -Recurse -Force brat-vscode-extension\brut-runtime -ErrorAction SilentlyContinue

Write-Host "Done. Your VSIX file is:" -ForegroundColor Cyan
Write-Host "C:\Users\HP\Desktop\BRUT\brat-vscode-extension\brut-compiler.vsix" -ForegroundColor Cyan