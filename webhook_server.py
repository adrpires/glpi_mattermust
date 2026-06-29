#!/usr/bin/env python3
from flask import Flask, request
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

# Configuração - lê das variáveis de ambiente
MATTERMOST_API_URL = os.getenv('MATTERMOST_API_URL', 'http://192.168.1.10:8065/api/v4')
MATTERMOST_TOKEN = os.getenv('MATTERMOST_TOKEN', 'seu_token_aqui')
MATTERMOST_USERNAME = os.getenv('MATTERMOST_USERNAME', 'apires')

# Headers para autenticação
HEADERS = {
    'Authorization': f'Bearer {MATTERMOST_TOKEN}',
    'Content-Type': 'application/json'
}

@app.route('/webhook/glpi', methods=['POST'])
def glpi_webhook():
    try:
        data = request.get_json()
        print(f"Dados recebidos do GLPI: {json.dumps(data, indent=2)}")

        # Formata a mensagem para o Mattermost
        message = format_message(data)

        # Envia DM via API do Mattermost
        success = send_dm(MATTERMOST_USERNAME, message)

        if success:
            print(f"✅ Mensagem enviada ao Mattermost com sucesso")
            return {'status': 'success'}, 200
        else:
            print(f"❌ Erro ao enviar ao Mattermost")
            return {'status': 'error', 'message': 'Falha ao enviar mensagem'}, 500

    except Exception as e:
        print(f"❌ Erro no webhook: {str(e)}")
        return {'status': 'error', 'message': str(e)}, 500

def get_user_id(username):
    """Obtém o ID do usuário pelo username"""
    try:
        url = f"{MATTERMOST_API_URL}/users/username/{username}"
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            return response.json()['id']
        else:
            print(f"❌ Erro ao buscar usuário: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erro ao obter ID do usuário: {str(e)}")
        return None

def send_dm(username, message):
    """Envia uma mensagem direta via API do Mattermost"""
    try:
        # Obtém o ID do usuário
        user_id = get_user_id(username)
        if not user_id:
            return False

        # Cria um canal direto
        url = f"{MATTERMOST_API_URL}/channels/direct"
        response = requests.post(
            url,
            headers=HEADERS,
            json={'user_id': user_id},
            timeout=5
        )

        if response.status_code not in [200, 201]:
            print(f"❌ Erro ao criar canal direto: {response.status_code} - {response.text}")
            return False

        channel_id = response.json()['id']

        # Envia a mensagem
        url = f"{MATTERMOST_API_URL}/posts"
        response = requests.post(
            url,
            headers=HEADERS,
            json={
                'channel_id': channel_id,
                'message': message
            },
            timeout=5
        )

        if response.status_code == 201:
            print(f"✅ Mensagem enviada para {username}")
            return True
        else:
            print(f"❌ Erro ao enviar mensagem: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Erro ao enviar DM: {str(e)}")
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
    print("📡 URL da API: " + MATTERMOST_API_URL)
    print("🏥 Health check: http://localhost:5000/health")
    app.run(host='0.0.0.0', port=5000, debug=True)
