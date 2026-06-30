#!/usr/bin/env python3
from flask import Flask, request
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

# Configuração - lê das variáveis de ambiente
MATTERMOST_WEBHOOK_URL = os.getenv('MATTERMOST_WEBHOOK_URL', 'http://192.168.1.10:8065/hooks/3b5ypip89ig48qmstrbtwmipjw')
MATTERMOST_USERNAME = os.getenv('MATTERMOST_USERNAME', 'apires')

@app.route('/webhook/glpi', methods=['POST'])
def glpi_webhook():
    try:
        data = request.get_json()
        print(f"\n📨 Dados recebidos do GLPI: {json.dumps(data, indent=2)}")

        # Formata a mensagem para o Mattermost
        message = format_message(data, MATTERMOST_USERNAME)
        print(f"📝 Mensagem: {message}")

        # Envia via webhook do Mattermost (form-data)
        print(f"📤 Enviando para Mattermost...")
        payload = {"payload": json.dumps({"text": message})}
        response = requests.post(
            MATTERMOST_WEBHOOK_URL,
            data=payload,
            timeout=5
        )

        if response.status_code == 200:
            print(f"✅ Mensagem enviada ao Mattermost com sucesso")
            return {'status': 'success'}, 200
        else:
            print(f"❌ Erro ao enviar ao Mattermost: {response.status_code} - {response.text}")
            return {'status': 'error', 'message': response.text}, response.status_code

    except Exception as e:
        print(f"❌ Erro no webhook: {str(e)}")
        return {'status': 'error', 'message': str(e)}, 500

def format_message(data, username):
    """Formata os dados do GLPI em uma mensagem legível com mention"""

    # Tenta extrair informações do GLPI
    ticket_id = data.get('id') or data.get('ticket_id') or 'N/A'
    title = data.get('name') or data.get('title') or 'Sem título'
    status = data.get('status') or 'N/A'
    priority = data.get('priority') or 'N/A'
    category = data.get('category') or 'N/A'
    requester = data.get('requester') or data.get('requester_name') or 'N/A'
    event_type = data.get('event_type') or data.get('action') or 'Evento'

    # Formata a mensagem com mention do usuário
    message = f"""@{username}

**🎫 Notificação GLPI - {event_type}**
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
    print("📡 Webhook URL: " + MATTERMOST_WEBHOOK_URL)
    print("👤 Username: " + MATTERMOST_USERNAME)
    print("🏥 Health check: http://localhost:5000/health")
    app.run(host='0.0.0.0', port=5000, debug=True)
