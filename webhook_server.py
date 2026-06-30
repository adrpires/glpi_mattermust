#!/usr/bin/env python3
from flask import Flask, request
import requests
import json
import os
import sys
import logging
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

HEADERS = {
    'Authorization': f'Bearer {MATTERMOST_TOKEN}',
    'Content-Type': 'application/json'
}

@app.route('/webhook/glpi', methods=['POST'])
def glpi_webhook():
    try:
        data = request.get_json()
        print(f"\n📨 ===== DADOS COMPLETOS DO GLPI =====")
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
        print(f"🔐 Headers: {HEADERS}")
        print(f"📺 Canal ID: {channel_id}")

        response = requests.post(
            url,
            headers=HEADERS,
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

def format_message(data):
    """Formata os dados do GLPI em uma mensagem legível"""

    # Tenta extrair informações do GLPI
    ticket_id = data.get('id') or data.get('ticket_id') or 'N/A'
    title = data.get('name') or data.get('title') or 'Sem título'
    status = data.get('status') or 'N/A'
    priority = data.get('priority') or 'N/A'
    category = data.get('category') or 'N/A'
    requester = data.get('requester') or data.get('requester_name') or 'N/A'
    event_type = data.get('event_type') or data.get('action') or 'Evento'

    # Formata a mensagem
    message = f"""**🎫 Notificação GLPI - {event_type}**
- **ID:** {ticket_id}
- **Título:** {title}
- **Status:** {status}
- **Prioridade:** {priority}
- **Categoria:** {category}
- **Requerente:** {requester}
- **Data:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"""

    return message

@app.route('/health', methods=['GET'])
def health():
    """Verifica se o serviço está funcionando"""
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    print("🚀 Iniciando servidor de webhook GLPI...")
    print("📡 API URL: " + MATTERMOST_API_URL)
    print("📺 Canal ID: " + MATTERMOST_CHANNEL_ID)
    print("🏥 Health check: http://localhost:5000/health")
    app.run(host='0.0.0.0', port=5000, debug=True)
