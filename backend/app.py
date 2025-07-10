from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS 
import google.generativeai as genai
from PIL import Image
import io
import os

API_KEY = os.getenv("API_KEY")

app = Flask(
    __name__,
    static_folder="../frontend",
    static_url_path=""
)
CORS(app, origins="*")

# Inicializar Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Criar chat com memória
chat = model.start_chat(history=[])

# Contexto do assistente gastronômico
contexto_base = (
    "Você é um assistente virtual especializado em gastronomia. "
    "Ajude usuários com receitas, técnicas culinárias, dicas de preparo, substituições de ingredientes, "
    "harmonização de pratos com bebidas, culinária brasileira e internacional. "
    "Divida a resposta em parágrafos sempre que for possível. "
    "Seja simpático, claro e **responda de forma resumida, mas eficiente**."
)

@app.route("/")
def home():
    return send_from_directory(app.static_folder, "chatbot.html")

@app.route("/reset", methods=["POST"])
def reset_conversa():
    global chat
    chat = model.start_chat(history=[])
    return jsonify({"status": "conversa resetada"})

@app.route("/chat", methods=["POST"])
def chat_route():
    try:
        text = request.form.get("text")
        image_file = request.files.get("image")

        if not text and not image_file:
            return jsonify({"erro": "Nenhum conteúdo enviado."}), 400

        parts = [contexto_base]
        if text:
            parts.append(text)

        if image_file:
            try:
                image_bytes = image_file.read()
                image = Image.open(io.BytesIO(image_bytes))
                parts.append(image)
            except Exception as img_error:
                return jsonify({"erro": f"Erro ao processar imagem: {str(img_error)}"}), 400

        # Enviar mensagem mantendo o histórico
        response = chat.send_message(parts)

        if hasattr(response, "text"):
            return jsonify({"resposta": response.text})
        else:
            return jsonify({"erro": "Resposta vazia."}), 500

    except Exception as e:
        print("Erro geral no /chat:", e)
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
