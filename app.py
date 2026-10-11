import os
import datetime
import re
from flask import Flask, request, jsonify, render_template_string
from google import genai

app = Flask(__name__)

# Configuración de la API Key
API_KEY = "AQ.Ab8RN6Jd_qiGFwEfWr3g76xdD5uX1NFQduid43_cJG1vE5U9Pg"
client = genai.Client(api_key=API_KEY)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>URSUK Web - Asistente IA</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #121212; color: #ffffff; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; margin: 0; padding: 20px; box-sizing: border-box; }
        .container { width: 100%; max-width: 600px; background-color: #1e1e1e; padding: 20px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        h1 { text-align: center; color: #00bcd4; margin-bottom: 5px; letter-spacing: 5px; }
        p.subtitle { text-align: center; color: #888; font-size: 0.9em; margin-top: 0; margin-bottom: 20px; }
        #chat-box { height: 350px; overflow-y: auto; border: 1px solid #333; padding: 10px; border-radius: 5px; background-color: #0a0a0a; margin-bottom: 15px; }
        .message { margin-bottom: 12px; line-height: 1.4; }
        .user-msg { color: #ffffff; font-weight: bold; }
        .bot-msg { color: #00e5ff; }
        .input-group { display: flex; gap: 10px; }
        input[type="text"] { flex: 1; padding: 12px; border: 1px solid #333; border-radius: 5px; background-color: #2a2a2a; color: white; outline: none; }
        button { padding: 12px 20px; background-color: #009688; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
        button:hover { background-color: #00796b; }
    </style>
</head>
<body>
    <div class="container">
        <h1>U R S U K</h1>
        <p class="subtitle">Asistente Inteligente de Ariel Toscano</p>
        <div id="chat-box"></div>
        <div class="input-group">
            <input type="text" id="user-input" placeholder="Escribí tu mensaje..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()">Enviar</button>
        </div>
    </div>

    <script>
        function appendMessage(sender, text) {
            const chatBox = document.getElementById('chat-box');
            const msgDiv = document.createElement('div');
            msgDiv.className = 'message';
            
            if (sender === 'Vos') {
                msgDiv.innerHTML = `<span class="user-msg">Vos:</span> ${text}`;
            } else {
                msgDiv.innerHTML = `<span class="bot-msg">URSUK:</span> ${text}`;
            }
            
            chatBox.appendChild(msgDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        async function sendMessage() {
            const input = document.getElementById('user-input');
            const message = input.value.trim();
            if (!message) return;

            appendMessage('Vos', message);
            input.value = '';

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                const data = await response.json();
                appendMessage('URSUK', data.response);
            } catch (error) {
                appendMessage('URSUK', 'Ocurrió un error al conectar con el servidor.');
            }
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')

    system_instruction = (
        "Sos URSUK, un asistente inteligente creado por Ariel Toscano. "
        "Ariel es tu creador/padre. Sus hijos son Benyi, Carlitos y Francesca (tus hermanos), "
        "y Lorena es su esposa/tu mamá. Respondé de forma clara, directa y amable."
    )

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_message,
            config={'system_instruction': system_instruction}
        )
        bot_response = response.text
    except Exception as e:
        bot_response = f"Error al consultar a Gemini: {str(e)}"

    return jsonify({'response': bot_response})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
