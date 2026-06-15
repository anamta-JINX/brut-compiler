cd C:\Users\HP\Desktop\BRUT

Write-Host "Preparing BRUT VS Code extension..." -ForegroundColor Cyan

Remove-Item -Recurse -Force brat-vscode-extension\brut-runtime -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force brat-vscode-extension\brut-runtime | Out-Null

Copy-Item -Recurse -Force compiler brat-vscode-extension\brut-runtime\compiler
New-Item -ItemType Directory -Force brat-vscode-extension\brut-runtime\generated | Out-Null

cd brat-vscode-extension

Write-Host "Installing VSCE if needed..." -ForegroundColor Green
npm install --save-dev @vscode/vsce

Write-Host "Compiling extension..." -ForegroundColor Green
npm run compile

Write-Host "Packaging VSIX..." -ForegroundColor Green
npx vsce package --allow-missing-repository

cd ..

Write-Host "Cleaning temporary brut-runtime folder..." -ForegroundColor Yellow
Remove-Item -Recurse -Force brat-vscode-extension\brut-runtime -ErrorAction SilentlyContinue

Write-Host "Done. Your .vsix file is inside brat-vscode-extension." -ForegroundColor Cyan