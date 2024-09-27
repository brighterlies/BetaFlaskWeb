import os
from flask import Flask, render_template, request, session
from dotenv import load_dotenv
from openai import OpenAI

# Lee los valores de configuración desde el archivo .env
load_dotenv()

app = Flask(__name__)

# Establece la contraseña confidencial para las sesiones
app.secret_key = os.getenv('SECRET_KEY', 'tu_clave_secreta')

# Accede con tu clave API de OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@app.route('/', methods=['GET', 'POST'])
def home():
    # Si no existe un historial de la conversación, créalo
    if 'conversation' not in session:
        session['conversation'] = []
    
    if request.method == 'POST':
        text = request.form['textarea']

        # Realiza una solicitud a la API de OpenAI para obtener la respuesta generada por ChatGPT
        answer = chatgpt_response(text)

        # Registra la pregunta hecha por el usuario y la respuesta entregada por ChatGPT en el historial
        session['conversation'].append({"role": "Tu", "content": text})
        session['conversation'].append({"role": "ChatGPT", "content": answer})
        session.modified = True  
        # Se encaga de mantener el historial de la conversacion actualizado

    return render_template('index.html', conversation=session['conversation'])

def chatgpt_response(text):
    try:
        # Envía una petición a la interfaz de programación de aplicaciones (API) de OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=session['conversation'] + [{"role": "Tu", "content": text}
            ]
        )
        # Recupera la respuesta generada por el modelo
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/reset', methods=['POST'])
def reset_conversation():
    # Reestablece el historial de la conversación
    session.pop('conversation', None)
    return render_template('index.html', conversation=[])

if __name__ == '__main__':
    app.run(debug=True)

