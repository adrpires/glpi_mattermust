# Script para inicializar o repositório Git
# Uso: .\init-repo.ps1 -RepositoryUrl "https://github.com/seu-usuario/glpi-webhook.git"

param(
    [string]$RepositoryUrl = ""
)

Write-Host "🚀 Inicializando repositório GLPI Webhook..." -ForegroundColor Green

# Verifica se Git está instalado
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Git não está instalado. Por favor, instale Git primeiro." -ForegroundColor Red
    exit 1
}

# Inicializa o repositório local
if (Test-Path ".git") {
    Write-Host "✅ Repositório Git já existe" -ForegroundColor Yellow
} else {
    Write-Host "📝 Inicializando novo repositório Git..." -ForegroundColor Cyan
    git init
    git config user.name "Seu Nome"
    git config user.email "seu-email@example.com"
}

# Adiciona os arquivos
Write-Host "📦 Adicionando arquivos..." -ForegroundColor Cyan
git add .

# Cria o primeiro commit
Write-Host "💾 Criando primeiro commit..." -ForegroundColor Cyan
git commit -m "Initial commit: GLPI Webhook intermediary with Docker support"

# Configura o remote se a URL foi fornecida
if ($RepositoryUrl) {
    Write-Host "🔗 Configurando remote repository..." -ForegroundColor Cyan
    git remote add origin $RepositoryUrl
    Write-Host "✅ Remote adicionado: $RepositoryUrl" -ForegroundColor Green
    Write-Host "Próximo passo: git push -u origin main" -ForegroundColor Yellow
} else {
    Write-Host "⚠️  Nenhuma URL de repositório foi fornecida." -ForegroundColor Yellow
    Write-Host "Para adicionar um remoto depois, execute:" -ForegroundColor Cyan
    Write-Host "git remote add origin <URL_DO_REPOSITORIO>" -ForegroundColor Cyan
}

Write-Host "✅ Repositório inicializado com sucesso!" -ForegroundColor Green
git status
