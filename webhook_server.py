#!/usr/bin/env python3
from flask import Flask, request
import requests
import json
import os
import sys
import logging
import re
import html
from datetime import datetime

# Força o stdout a ser unbuffered
sys.stdout = sys.stderr = open(sys.stdout.fileno(), 'w', buffering=1, encoding='utf-8')

# Configurar logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format='%(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuração - lê das variáveis de ambiente
MATTERMOST_API_URL = os.getenv('MATTERMOST_API_URL', 'http://192.168.1.10:8065/api/v4')
MATTERMOST_TOKEN = os.getenv('MATTERMOST_TOKEN', 'kr3f8h4iifre3ycfb6kxjmxk3a')
MATTERMOST_CHANNEL_ID = os.getenv('MATTERMOST_CHANNEL_ID', 'g4is7cbng7yg3d8p4o4us1i6re')
GLPI_API_URL = os.getenv('GLPI_API_URL', 'https://glpi.macielvieiracoelho.com.br/api/v4')
GLPI_TOKEN = os.getenv('GLPI_TOKEN', 'kr3f8h4iifre3ycfb6kxjmxk3a')

MATTERMOST_HEADERS = {
    'Authorization': f'Bearer {MATTERMOST_TOKEN}',
    'Content-Type': 'application/json'
}

GLPI_HEADERS = {
    'Authorization': f'Bearer {GLPI_TOKEN}',
    'Content-Type': 'application/json'
}

@app.route('/webhook/glpi', methods=['POST'])
def glpi_webhook():
    try:
        # Tenta todos os formatos possíveis
        print(f"\n📨 ===== INVESTIGANDO PAYLOAD DO GLPI =====")
        print(f"Content-Type: {request.content_type}")
        print(f"URL Args: {request.args.to_dict()}")
        print(f"Headers: {dict(request.headers)}")
        print(f"Raw Data: {request.data}")

        # Tenta JSON primeiro
        if request.is_json:
            data = request.get_json()
        elif request.form:
            data = request.form.to_dict()
        elif request.args:
            data = request.args.to_dict()
        else:
            # Se tudo falhar, tenta parsear o raw data
            try:
                data = json.loads(request.data.decode('utf-8'))
            except:
                data = {}

        print(f"\n📨 ===== DADOS EXTRAÍDOS DO GLPI =====")
        print(json.dumps(data, indent=2))
        print(f"===== FIM DOS DADOS =====")

        # Formata a mensagem para o Mattermost
        message = format_message(data)
        print(f"📝 Mensagem: {message}")

        # Envia para o canal via API
        print(f"📤 Enviando para canal mvc-geral...")
        success = send_to_channel(MATTERMOST_CHANNEL_ID, message)

        if success:
            print(f"✅ Mensagem enviada ao Mattermost com sucesso")
            return {'status': 'success'}, 200
        else:
            print(f"❌ Erro ao enviar ao Mattermost")
            return {'status': 'error', 'message': 'Falha ao enviar mensagem'}, 500

    except Exception as e:
        print(f"❌ Erro no webhook: {str(e)}")
        return {'status': 'error', 'message': str(e)}, 500

def get_latest_comment(ticket_id):
    """Busca o comentário mais recente do GLPI API"""
    try:
        print(f"🔍 Buscando comentários do ticket #{ticket_id} no GLPI...")

        url = f"{GLPI_API_URL}/Ticket/{ticket_id}/ITILFollowup"
        print(f"📤 URL: {url}")

        response = requests.get(
            url,
            headers=GLPI_HEADERS,
            timeout=5
        )

        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            followups = response.json()
            if isinstance(followups, list) and len(followups) > 0:
                # Pega o último comentário (mais recente)
                latest = followups[-1]
                comment_text = latest.get('content', '')
                if comment_text:
                    print(f"✅ Comentário encontrado: {comment_text[:100]}...")
                    return limpar_html(comment_text)

        print(f"⚠️ Nenhum comentário encontrado")
        return None

    except Exception as e:
        print(f"❌ Erro ao buscar comentários: {type(e).__name__}: {str(e)}")
        return None

def send_to_channel(channel_id, message):
    """Envia uma mensagem para um canal via API do Mattermost"""
    try:
        print(f"🔗 Conectando à API: {MATTERMOST_API_URL}")
        print(f"📝 Mensagem: {message[:100]}...")

        url = f"{MATTERMOST_API_URL}/posts"
        print(f"📤 URL: {url}")
        print(f"🔐 Headers: {MATTERMOST_HEADERS}")
        print(f"📺 Canal ID: {channel_id}")

        response = requests.post(
            url,
            headers=MATTERMOST_HEADERS,
            json={
                'channel_id': channel_id,
                'message': message
            },
            timeout=5
        )

        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response: {response.text[:500]}")

        if response.status_code == 201:
            print(f"✅ Mensagem postada no canal com sucesso!")
            return True
        else:
            print(f"❌ Erro ao postar: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ EXCEÇÃO ao enviar para canal: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def limpar_html(html_text):
    """Remove tags HTML e decodifica entidades HTML"""
    if not html_text:
        return ""
    # Decodifica entidades HTML
    text = html.unescape(html_text)
    # Remove tags HTML
    text = re.sub(r'<[^>]+>', '', text)
    # Remove espaços em branco extras
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def format_message(data):
    """Formata os dados do GLPI em uma mensagem legível"""

    # Extrai dados do GLPI (vem dentro de 'item')
    item = data.get('item', {})
    event_type = data.get('event', 'Evento').capitalize()

    # Mapeia nomes de eventos
    event_names = {
        'new': '🆕 Novo Chamado',
        'update': '✏️ Chamado Atualizado',
        'solved': '✅ Chamado Resolvido',
        'closed': '🔒 Chamado Fechado'
    }
    event_display = event_names.get(data.get('event'), f'📋 {event_type}')

    # Extrai informações com suporte a estrutura aninhada
    ticket_id = item.get('id', 'N/A')
    title = item.get('name', 'Sem título')

    # Status, Categoria, etc podem ser dicts ou strings
    status = item.get('status', {})
    status_name = status.get('name') if isinstance(status, dict) else status or 'N/A'

    category = item.get('category', {})
    category_name = category.get('name') if isinstance(category, dict) else category or 'N/A'

    # Descrição/Conteúdo (limpar HTML)
    content_html = item.get('content', '')
    content = limpar_html(content_html)[:200]  # Primeiros 200 caracteres

    # Usuario que criou/recebeu
    user_recipient = item.get('user_recipient', {})
    user_name = user_recipient.get('name') if isinstance(user_recipient, dict) else user_recipient or 'N/A'

    # Formata a mensagem com mention
    message = f"""@{user_name}

**{event_display}**
- **Nº Chamado:** #{ticket_id}
- **Título:** {title}
- **Status:** {status_name}
- **Categoria:** {category_name}
- **Descrição:** {content}
- **Data:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"""

    # Se for uma atualização, tenta buscar comentários
    if data.get('event') == 'update':
        comment = get_latest_comment(ticket_id)
        if comment:
            comment_preview = comment[:200]  # Primeiros 200 caracteres
            message += f"\n\n📝 **Comentário:** {comment_preview}"

    return message

@app.route('/health', methods=['GET'])
def health():
    """Verifica se o serviço está funcionando"""
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    print("🚀 Iniciando servidor de webhook GLPI...")
    print("📡 Mattermost API URL: " + MATTERMOST_API_URL)
    print("📺 Canal ID: " + MATTERMOST_CHANNEL_ID)
    print("🔗 GLPI API URL: " + GLPI_API_URL)
    print("🏥 Health check: http://localhost:5000/health")
    app.run(host='0.0.0.0', port=5000, debug=True)
