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

MATTERMOST_HEADERS = {
    'Authorization': f'Bearer {MATTERMOST_TOKEN}',
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

    item = data.get('item', {})
    parent_item = data.get('parent_item', {})

    # Verifica se é um comentário (ITILFollowup) ou solução (ITILSolution)
    # Se tem 'items_id' no item, significa que é um acompanhamento/comentário do ticket pai
    is_followup = 'items_id' in item and parent_item

    if is_followup:
        # É um comentário ou solução
        ticket_id = parent_item.get('id', item.get('items_id', 'N/A'))
        title = parent_item.get('name', 'Sem título')
        status = parent_item.get('status', {})
        status_name = status.get('name') if isinstance(status, dict) else status or 'N/A'
        category = parent_item.get('category', {})
        category_name = category.get('name') if isinstance(category, dict) else category or 'N/A'
        user_recipient = parent_item.get('user_recipient', {})
        user_name = user_recipient.get('name') if isinstance(user_recipient, dict) else user_recipient or 'N/A'

        # Extrai o usuário que fez o comentário
        user = item.get('user', {})
        comment_user = user.get('name') if isinstance(user, dict) else user or 'N/A'

        # Conteúdo do comentário/solução
        content_html = item.get('content', '')
        content = limpar_html(content_html)[:300]

        # Determina se é solução ou acompanhamento
        request_type = item.get('request_type', {})
        request_type_name = request_type.get('name') if isinstance(request_type, dict) else request_type or ''

        if 'Solução' in str(request_type_name) or 'solution' in str(item.get('itemtype', '')).lower():
            event_display = '✅ Solução Adicionada'
        else:
            event_display = '💬 Novo Acompanhamento'

        # Formata a mensagem
        message = f"""@{user_name}

**{event_display}**
- **Nº Chamado:** #{ticket_id}
- **Título:** {title}
- **Status:** {status_name}
- **Categoria:** {category_name}
- **Por:** {comment_user}
- **Acompanhamento:** {content}
- **Data:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"""

        return message

    else:
        # É um ticket normal (criação ou atualização)
        event_type = data.get('event', 'Evento').capitalize()

        # Mapeia nomes de eventos
        event_names = {
            'new': '🆕 Novo Chamado',
            'update': '✏️ Chamado Atualizado',
            'solved': '✅ Chamado Resolvido',
            'closed': '🔒 Chamado Fechado'
        }
        event_display = event_names.get(data.get('event'), f'📋 {event_type}')

        # Extrai informações
        ticket_id = item.get('id', 'N/A')
        title = item.get('name', 'Sem título')

        status = item.get('status', {})
        status_name = status.get('name') if isinstance(status, dict) else status or 'N/A'

        category = item.get('category', {})
        category_name = category.get('name') if isinstance(category, dict) else category or 'N/A'

        # Descrição/Conteúdo
        content_html = item.get('content', '')
        content = limpar_html(content_html)[:200]

        # Usuario
        user_recipient = item.get('user_recipient', {})
        user_name = user_recipient.get('name') if isinstance(user_recipient, dict) else user_recipient or 'N/A'

        # Formata a mensagem
        message = f"""@{user_name}

**{event_display}**
- **Nº Chamado:** #{ticket_id}
- **Título:** {title}
- **Status:** {status_name}
- **Categoria:** {category_name}
- **Descrição:** {content}
- **Data:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"""

        return message

@app.route('/health', methods=['GET'])
def health():
    """Verifica se o serviço está funcionando"""
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    print("🚀 Iniciando servidor de webhook GLPI...")
    print("📡 Mattermost API URL: " + MATTERMOST_API_URL)
    print("📺 Canal ID: " + MATTERMOST_CHANNEL_ID)
    print("🏥 Health check: http://localhost:5000/health")
    app.run(host='0.0.0.0', port=5000, debug=True)
