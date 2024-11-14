OPEN_KEY = "sk-AI51AIYblTdgE7gR6IR68WjCW1cgWi1QTju1xYeKSqT3BlbkFJsvN7jKXJxu3ulYUgXy3TX69Ec02LhXisbQ6mVcqLgA"
from flask import Flask, request, render_template, session, jsonify
import uuid
import openai
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuración de la API de OpenAI
client = openai.OpenAI(api_key=OPEN_KEY)

# Cargar el archivo Excel y hojas específicas
archivo_excel = 'db_pachatec.xlsx'
hojas_excel = pd.read_excel(archivo_excel, sheet_name=None)
db_hojas = ["BD Arroz", "BD Cacao", "BD Café", "BD Plátano"]
columnas_parametros = ["Tipo de problema", "Nombre de problema", "Fase de desarrollo", "Sistema de producción",
                       "Nivel de Severidad"]
umbral_parametros = 4
sistema_identidad = "Eres Pachatec, un asistente virtual con inteligencia artificial capaz de dar consejos útiles solo del sector agrónomo en un máximo de 250 palabras."

texto_para_listas = "Recuerda , que la prevención y el monitoreo constante son fundamentales para un eficaz control y manejo de tu cultivo. Nuestras recomendaciones pueden variar según la región en la que te encuentres. Por ello, te sugerimos buscar asesoramiento agronómico local para obtener consejos específicos y adaptados a tu ubicación. ¡Te deseamos mucho éxito y una excelente producción!"
texto_chatgpt = "Es importante recordar que, por el momento, sólo contamos con recomendaciones especializadas para solución de problemas y cuidados de los cultivos de café, cacao, arroz y plátano . ¡Mantente atento a las actualizaciones y mejoras continuas que estamos implementando para servirte mejor!"


# Definir el historial de conversaciones como un diccionario global
conversation_histories = {}


def generate_conversation_id():
    # Genera un ID único para cada conversación
    return str(uuid.uuid4())


def get_response(system_prompt, user_prompt, conversation_id=None):
    """Función para obtener respuesta de OpenAI y gestionar el historial."""
    if conversation_id not in conversation_histories:
        conversation_histories[conversation_id] = []
    conversation_history = conversation_histories[conversation_id]
    # Si es la primera interacción, añadir el mensaje del sistema
    if len(conversation_history) == 0:
        conversation_history.append({"role": "system", "content": system_prompt})
    # Añadir la pregunta del usuario al historial
    conversation_history.append({"role": "user", "content": user_prompt})
    # Obtener la respuesta de OpenAI
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation_history,
        temperature=0,
        max_tokens=600
    )

    # Extraer la respuesta
    response_content = completion.choices[0].message.content

    # Añadir la respuesta al historial
    conversation_history.append({"role": "assistant", "content": response_content})

    # Guardar el historial actualizado
    conversation_histories[conversation_id] = conversation_history

    return response_content, conversation_id

# Función para clasificar el tipo de cultivo
def classify_cultivo(user_prompt):
    classification_prompt = (
        "Clasifica el siguiente mensaje en uno de los siguientes cultivos: "
        "Arroz, Café, Cacao, Plátano, Otro. Responde solo con la palabra correspondiente. "
        f"Mensaje: {user_prompt}"
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": classification_prompt}],
        temperature=0,
        max_tokens=5  # Aumentado para permitir palabras completas
    )

    return completion.choices[0].message.content.strip()

def classify_param(user_prompt):

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_prompt}],
        temperature=0,
        max_tokens=30  # Aumentado para permitir palabras completas
    )
    return completion.choices[0].message.content.strip()


@app.route('/')
def index():
    if 'conversation_id' not in session:
        session['conversation_id'] = generate_conversation_id()
    return render_template('chat.html')


@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.json.get("message")
    conversation_id = session['conversation_id']

    # Clasificar el tipo de cultivo
    cultivo_type = classify_cultivo(user_message)
    caracteristicas_dict = {}  # Inicializar para el caso en que no se detecte un cultivo específico
    recomendaciones_values = []  # Inicializar lista para almacenar recomendaciones
    texto_recomendado = ""  # Inicializar variable para texto recomendado

    # Obtener información de la hoja de cálculo si el tipo de cultivo es conocido
    if cultivo_type != "Otro" and f"BD {cultivo_type}" in db_hojas:
        hoja = "BD " + cultivo_type
        dict_columna = {col: hojas_excel[hoja][col].unique().tolist() for col in columnas_parametros}

        # Construir el prompt para clasificar características
        system_prompt = sistema_identidad
        user_prompt = f'''Clasifica las características de la pregunta según cada elemento, si no corresponde asigna el valor de "Otro", dar como respuesta solo los valores asignados separados por coma:
            Pregunta: {user_message}
            Tipo de problema: {dict_columna["Tipo de problema"]}
            Nombre de problema(Relaciona también nombres coloquiales): {dict_columna["Nombre de problema"]}
            Fase de desarrollo: {dict_columna["Fase de desarrollo"]}
            Sistema de producción: {dict_columna["Sistema de producción"]}
            Nivel de Severidad(Relaciona el tiempo, mientras más temprano será menos severo, identifica palabras como recientemente, recien, ultimamente, acabo de, y similares): {dict_columna["Nivel de Severidad"]}'''

        Clasif = classify_param(user_prompt)
        print(Clasif)
        valores = Clasif.split(", ")
        caracteristicas_dict = {
            "Tipo de problema": valores[0],
            "Nombre de problema": valores[1],
            "Fase de desarrollo": valores[2],
            "Sistema de producción": valores[3],
            "Nivel de Severidad": valores[4]
        }

        # Filtrar características relevantes
        filtered_dict = {key: value for key, value in caracteristicas_dict.items() if
                         value not in ['Otro', 'N.A', 'N.a']}
        try:
            if filtered_dict["Tipo de problema"] == "Nutrición":
                filtered_dict["Nivel de Severidad"] = "N.a"
        except KeyError:
            pass

        # Filtrar la base de datos por características
        num_caracteristicas = len(filtered_dict)
        df = hojas_excel[hoja]

        if num_caracteristicas >= umbral_parametros:
            for key, value in filtered_dict.items():
                df = df[df[key] == value]

            # Obtener recomendaciones y texto recomendado
            recomendaciones_values = df['Recomendación y Asesoría Agraria'].values.tolist() if not df.empty else []
            texto_recomendado = "-".join(recomendaciones_values) if recomendaciones_values else ""

            # Construir la respuesta final
            system_prompt = sistema_identidad
            user_prompt = f'''Responde de la siguiente forma: Da una respuesta con tus conocimientos avanzados de agrónomo experto para la pregunta y compléntala (en parrafos posteriores) con la información del texto recomendado siempre y cuando no entre en contradiccion con la recomendación de los parráfos previos. Siempre que sea posible trata de de dar recomendaciones precisas (dosis de pesticidas, fungicidad, nutrientes, etc) siempre que la pregunta lo permita.      pregunta: {user_message}
                Texto recomendado: {texto_recomendado}'''
            respuesta_gpt, conversation_id = get_response(system_prompt, user_prompt, conversation_id)
            respuesta_gpt = respuesta_gpt + f" \n \n Recuerda , que la prevención y el monitoreo constante son fundamentales para un eficaz control y manejo de tu cultivo. Nuestras recomendaciones pueden variar según la región en la que te encuentres. Por ello, te sugerimos buscar asesoramiento agronómico local para obtener consejos específicos y adaptados a tu ubicación. ¡Te deseamos mucho éxito y una excelente producción!"



        elif(caracteristicas_dict["Nombre de problema"] != "Otro"):

            system_prompt = sistema_identidad
            user_prompt = f'''Responde de la siguiente forma: Da una respuesta con tus conocimientos avanzados de agrónomo experto para la pregunta y compléntala (en parrafos posteriores) con la información del texto recomendado siempre y cuando no entre en contradiccion con la recomendación de los parráfos previos. Siempre que sea posible trata de de dar recomendaciones precisas (dosis de pesticidas, fungicidad, nutrientes, etc) siempre que la pregunta lo permita.    pregunta: {user_message}
                            Texto recomendado: {texto_recomendado}'''
            respuesta_gpt, conversation_id = get_response(system_prompt, user_prompt, conversation_id)

            #respuesta_gpt = respuesta_gpt+" \n \n Hemos detectado que hay similitud en nuestra base de datos, si deseas profundizar puedes preguntar, especificando los siguientes campos"

            df = hojas_excel["BD " + cultivo_type]

            actual_columns = list(filtered_dict.keys())

            df_p = df.copy()
            for key, value in filtered_dict.items():
                df_p = df_p[df_p[key] == value]
            print(df_p)
            # Obtener las columnas que no están en filtered_dict pero sí en columnas_parametros
            columns_to_check = [col for col in columnas_parametros if col not in filtered_dict]

            # Crear un diccionario con los valores únicos de cada columna que no está en filtered_dict pero sí en columnas_parametros
            unique_values = {col: df_p[col].unique().tolist() for col in columns_to_check if col in df_p.columns}
            #print(unique_values)
            output_html = "<h2>Puedes complementar con la siguiente información:</h2><ul>"
            for col, values in unique_values.items():
                output_html += f"<li>Para <b>{col}</b>, puedes seleccionar entre:<ul>"
                for value in values:
                    output_html += f"<li>{value}</li>"
                output_html += "</ul></li>"

            respuesta_gpt = respuesta_gpt+f" \n \n Para ofrecerte una recomendación más específica, es importante comprender mejor tu situación agrícola. Para ello, necesitamos conocer algunos detalles adicionales de tu cultivo y/o problema (o consulta): {output_html}"


            agg = f" \n Puede complementar tu pregunta: <b><i>{user_message}</i></b> añadiendo información complementaria a los campos faltante para tener una respuesta más personalizada."
            respuesta_gpt = respuesta_gpt + agg
            print(filtered_dict)


    else:
        # Respuesta cuando el cultivo es "Otro" o no se encuentra en la base de datos
        system_prompt = sistema_identidad
        user_prompt = f'''Da una respuesta a la pregunta con tus conocimientos expertos. Siempre que sea posible trata de de dar recomendaciones precisas (dosis de pesticidas, fungicidad, nutrientes, etc) siempre que la pregunta lo permita y lo requiera.                     
                                                                pregunta: {user_message} '''
        respuesta_gpt, conversation_id = get_response(system_prompt, user_prompt, conversation_id)
        respuesta_gpt = respuesta_gpt + " \n "+ texto_chatgpt

    return jsonify({
        "response": respuesta_gpt,
        "cultivo_type": cultivo_type,
        "caracteristicas_dict": caracteristicas_dict,
        "recomendaciones_values": recomendaciones_values,
        "texto_recomendado": texto_recomendado
    })


if __name__ == '__main__':
    app.run(debug=True)