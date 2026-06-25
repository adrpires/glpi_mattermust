# Webhook Intermediário GLPI → Mattermost

## O que faz?
Este script atua como intermediário entre o GLPI e o Mattermost, recebendo notificações do GLPI e reenviando ao Mattermost em um formato correto.

## 📋 Requisitos

- Docker e Docker Compose (para produção)
- Python 3.14+ (para desenvolvimento local)
- Webhook URL do Mattermost

## 🚀 Execução com Docker (Recomendado)

### 1. Clone o repositório:
```bash
git clone <seu-repositorio> glpi-webhook
cd glpi-webhook
```

### 2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite .env e configure MATTERMOST_WEBHOOK_URL
```

### 3. Execute com Docker Compose:
```bash
docker-compose up -d
```

### 4. Verifique se está rodando:
```bash
curl http://localhost:5000/health
```

## 💻 Execução Local (Desenvolvimento)

### 1. Instale as dependências:
```bash
python -m pip install -r requirements.txt
```

### 2. Execute o servidor:
```bash
python webhook_server.py
```

Você verá:
```
🚀 Iniciando servidor de webhook GLPI...
📡 URL do webhook: http://localhost:5000/webhook/glpi
🏥 Health check: http://localhost:5000/health
```

## ⚙️ Configuração no GLPI

### 1. Se estiver rodando localmente:
- Acesse: **Administração > Configuração > Webhooks**
- Configure a URL como: `http://localhost:5000/webhook/glpi`

### 2. Se estiver rodando em um servidor (produção):
- Use o IP ou domínio do servidor: `http://seu-servidor:5000/webhook/glpi`

## 🧪 Teste

Para testar se o servidor está funcionando:

```bash
curl http://localhost:5000/health
```

Para simular uma notificação do GLPI (PowerShell):

```powershell
$payload = @{
    id = 123
    name = "Teste de Chamado"
    status = "Novo"
    priority = "Média"
    category = "TI"
    requester = "João Silva"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/webhook/glpi" `
  -Method POST `
  -ContentType "application/json" `
  -Body $payload
```

Ou com curl (Linux/Mac):

```bash
curl -X POST http://localhost:5000/webhook/glpi \
  -H "Content-Type: application/json" \
  -d '{
    "id": 123,
    "name": "Teste de Chamado",
    "status": "Novo",
    "priority": "Média",
    "category": "TI",
    "requester": "João Silva"
  }'
```

## 🛠️ Troubleshooting

- Se a porta 5000 já está em uso, edite `docker-compose.yml` e mude para outra porta
- Para ver logs: `docker-compose logs -f`
- Para parar o container: `docker-compose down`
- Verifique se o Mattermost webhook está ativo e a URL está correta

## 📦 Estrutura do Projeto

```
glpi-webhook/
├── webhook_server.py      # Script principal
├── requirements.txt       # Dependências Python
├── Dockerfile             # Configuração Docker
├── docker-compose.yml     # Orquestração Docker
├── .env.example           # Variáveis de ambiente exemplo
├── .gitignore             # Arquivos ignorados pelo Git
└── README.md              # Este arquivo
```

## 📝 Licença

MIT
