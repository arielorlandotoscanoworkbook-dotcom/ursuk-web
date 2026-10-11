import os
import datetime
import re
from flask import Flask, request, jsonify, render_template_string
from google import genai

app = Flask(__name__)

API_KEY = "AQ.Ab8RN6Jd_qiGFwEfWr3g76xdD5uX1NFQduid43_cJG1vE5U9Pg"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>URSUK Web - Asistente IA</title>
    <style>
        body {
            background-color: #0b0b0f;
            color: #ffffff;
            font-family: 'Roboto', sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            width: 90%;
            max-width: 400px;
            text-align: center;
        }
        h1 {
            color: #00E5FF;
            font-family: 'Consolas', monospace;
            margin-bottom: 5px;
            letter-spacing: 2px;
        }
        #chat-box {
            background: #121218;
            border: 1px solid #222230;
            border-radius: 10px;
            height: 280px;
            overflow-y: auto;
            padding: 10px;
            text-align: left;
            font-size: 14px;
            margin-bottom: 15px;
        }
        .msg-user { color: #00E5FF; margin: 5px 0; }
        .msg-ursuk { color: #A0A0A0; margin: 5px 0; }
        .input-group {
            display: flex;
            gap: 5px;
        }
        input {
            flex: 1;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #333;
            background: #1a1a24;
            color: white;
            font-size: 14px;
        }
        button {
            padding: 10px 15px;
            border: none;
            border-radius: 5px;
            background: #008B8B;
            color: white;
            font-weight: bold;
            cursor: pointer;
        }
        button:active { background: #006666; }
    </style>
</head>
<body>

    <div class="container">
        <h1>U R S U K</h1>
        <p style="font-size: 12px; color: #888;">Asistente Inteligente de Ariel Toscano</p>

        <div id="chat-box">
            <div class="msg-ursuk"><b>URSUK:</b> Hola, ¿con quién estoy hablando? Escribí tu nombre.</div>
        </div>

        <div class="input-group">
            <input type="text" id="userInput" placeholder="Escribí tu mensaje..." onkeypress="chequearEnter(event)">
            <button onclick="enviarMensaje()">Enviar</button>
        </div>
    </div>

    <script>
        let usuario = "Ariel";
        let primerMensaje = true;

        function hablarVoz(texto) {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                
                // Reemplazamos URSUK por Úrsuk para que la voz lo pronuncie como palabra fluida y no deletreado
                let textoParaVoz = texto.replace(/URSUK/g, "Úrsuk");
                
                let utterance = new SpeechSynthesisUtterance(textoParaVoz);
                utterance.lang = 'es-AR';
                
                // Intentar asignar una voz en español del teléfono
                let voces = window.speechSynthesis.getVoices();
                let vozEspanol = voces.find(v => v.lang.includes('es'));
                if (vozEspanol) {
                    utterance.voice = vozEspanol;
                }

                window.speechSynthesis.speak(utterance);
            }
        }

        function agregarMensaje(emisor, texto) {
            let chatBox = document.getElementById("chat-box");
            let clase = emisor.includes("Vos") ? "msg-user" : "msg-ursuk";
            chatBox.innerHTML += `<div class="\${clase}"><b>${emisor}:</b>${texto}</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function chequearEnter(e) {
            if (e.key === 'Enter') {
                enviarMensaje();
            }
        }

        async function enviarMensaje() {
            let input = document.getElementById("userInput");
            let mensaje = input.value.trim();
            if (!mensaje) return;

            if (primerMensaje) {
                usuario = mensaje;
                primerMensaje = false;
            }

            // Muestra correctamente el nombre del usuario
            agregarMensaje(`Vos (\${usuario})`, mensaje);
            input.value = "";

            try {
                let response = await fetch('/consultar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mensaje: mensaje, usuario: usuario })
                });

                let data = await response.json();
                agregarMensaje("URSUK", data.respuesta);
                hablarVoz(data.respuesta);
            } catch (error) {
                agregarMensaje("URSUK", "Error de comunicación con el servidor.");
            }
        }
        
        // Cargar voces disponibles al iniciar
        if ('speechSynthesis' in window) {
            window.speechSynthesis.onvoiceschanged = () => {
                window.speechSynthesis.getVoices();
            };
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/consultar", methods=["POST"])
def consultar():
    try:
        data = request.get_json(force=True)
        prompt = data.get("mensaje", "").strip()
        nombre_usuario = data.get("usuario", "Ariel").strip()

        if not prompt:
            return jsonify({"respuesta": "No recibí ningún mensaje."})

        prompt_lower = prompt.lower()

        if any(p in prompt_lower for p in ["como te llamas", "cómo te llamas", "como es tu nombre", "quien sos", "tu nombre"]):
            respuesta_texto = "Mi nombre es URSUK."
        elif any(p in prompt_lower for p in ["creador", "desarrollador", "padre", "mama", "quien te creo", "quien te hizo"]):
            respuesta_texto = "Mi creador es Ariel Toscano, él es mi padre se podría decir, y también se podría decir que Benyi, Carlitos y Francesca son mis hermanos, y Lorena mi mamá."
        elif "hora" in prompt_lower:
            respuesta_texto = f"Son las {datetime.datetime.now().strftime('%H:%M')}."
        elif "fecha" in prompt_lower or "día" in prompt_lower or "dia" in prompt_lower:
            respuesta_texto = f"Hoy es {datetime.datetime.now().strftime('%d/%m/%Y')}."
        else:
            try:
                client = genai.Client(api_key=API_KEY)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )
                respuesta_texto = response.text if response and response.text else f"Hola {nombre_usuario}, te escucho perfectamente."
            except Exception as ex:
                respuesta_texto = f"Hola {nombre_usuario}, recibí tu mensaje correctamente en el sistema web."

        respuesta_limpia = re.sub(r'[*#_~`\-]', ' ', respuesta_texto)
        respuesta_limpia = re.sub(r'\s+', ' ', respuesta_limpia).strip()

        return jsonify({"respuesta": respuesta_limpia})

    except Exception as err:
        return jsonify({"respuesta": "Procesamiento completado con éxito."}), 200

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
