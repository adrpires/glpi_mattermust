# 🚀 Guia de Deploy - GLPI Webhook

## Pré-requisitos

- [Git](https://git-scm.com) instalado
- Conta no [GitHub](https://github.com), [GitLab](https://gitlab.com) ou outro Git provider
- Docker e Docker Compose (para produção)

## 1️⃣ Criar um novo repositório

### No GitHub:
1. Vá para [github.com/new](https://github.com/new)
2. Crie um repositório público ou privado
3. **Não** inicialize com README, .gitignore ou licença (já temos)
4. Copie a URL do repositório (ex: `https://github.com/seu-usuario/glpi-webhook.git`)

### No GitLab:
1. Vá para [gitlab.com/projects/new](https://gitlab.com/projects/new)
2. Preencha o nome do projeto
3. Deixe vazio (não inicialize)
4. Copie a URL do repositório

---

## 2️⃣ Inicializar e fazer push do código

### Opção A: Usar o script PowerShell (Windows)

```powershell
cd C:\Python\glpi
.\init-repo.ps1 -RepositoryUrl "https://github.com/seu-usuario/glpi-webhook.git"
git push -u origin main
```

### Opção B: Manual (Windows/Linux)

```bash
cd glpi

# Inicializar repositório local
git init
git config user.name "Seu Nome"
git config user.email "seu-email@exemplo.com"

# Adicionar todos os arquivos
git add .

# Primeiro commit
git commit -m "Initial commit: GLPI Webhook intermediary with Docker support"

# Adicionar remote
git remote add origin https://github.com/seu-usuario/glpi-webhook.git

# Fazer push
git branch -M main
git push -u origin main
```

---

## 3️⃣ Testar localmente com Docker

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/glpi-webhook.git
cd glpi-webhook

# Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com sua URL do Mattermost webhook

# Execute com Docker
docker-compose up -d

# Verifique se está rodando
curl http://localhost:5000/health
```

---

## 4️⃣ Deploy em servidor (Linux)

### Via SSH:

```bash
# 1. Conecte ao servidor
ssh usuario@seu-servidor.com

# 2. Clone o repositório
git clone https://github.com/seu-usuario/glpi-webhook.git
cd glpi-webhook

# 3. Configure as variáveis
cp .env.example .env
nano .env  # Edite com sua URL

# 4. Inicie com Docker
docker-compose up -d

# 5. Verifique os logs
docker-compose logs -f
```

---

## 5️⃣ Configurar no GLPI

1. Acesse o GLPI em **Administração > Configuração > Webhooks**
2. Edite os webhooks existentes ou crie novos:
   - **URL:** `http://seu-servidor:5000/webhook/glpi`
   - **Ou se acessar via HTTPS:** `https://seu-servidor:5000/webhook/glpi`

3. Crie um novo chamado de teste para verificar se as notificações chegam

---

## 🔐 Segurança em Produção

### 1. Use variáveis de ambiente:
```bash
# Arquivo .env (nunca faça commit!)
MATTERMOST_WEBHOOK_URL=https://seu-mattermost.com/hooks/xxxxx
FLASK_ENV=production
```

### 2. Configure HTTPS (com Nginx reverse proxy):

```nginx
server {
    listen 443 ssl;
    server_name seu-servidor.com;

    ssl_certificate /etc/letsencrypt/live/seu-servidor.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-servidor.com/privkey.pem;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Use firewall:
```bash
# Abra apenas a porta necessária
sudo ufw allow 443/tcp
sudo ufw allow 80/tcp  # Para renovação de certificado
```

---

## 📊 Monitoramento

### Verifique o status:
```bash
docker-compose ps
```

### Veja os logs:
```bash
docker-compose logs -f glpi-webhook
```

### Limpe e reinicie:
```bash
docker-compose down
docker-compose up -d
```

---

## 🆘 Troubleshooting

### A aplicação não inicia
```bash
docker-compose logs glpi-webhook
# Procure por erros de configuração ou de conexão
```

### Webhook não recebe notificações
1. Verifique a URL no GLPI: `http://seu-servidor:5000/webhook/glpi`
2. Teste a conectividade: `curl http://seu-servidor:5000/health`
3. Verifique os logs: `docker-compose logs -f`
4. Confirme que o Mattermost webhook URL está correta no `.env`

---

## 📝 Changelog

Documente as mudanças em um arquivo `CHANGELOG.md` para rastrear versões.

---

**Sucesso! 🎉**
