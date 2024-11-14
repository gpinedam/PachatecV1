OPEN_KEY = "sk-AI51AIYblTdgE7gR6IR68WjCW1cgWi1QTju1xYeKSqT3BlbkFJsvN7jKXJxu3ulYUgXy3TX69Ec02LhXisbQ6mVcqLgA"

from openai import OpenAI
import pandas as pd
import time


archivo_excel = 'db_pachatec.xlsx'
hojas_excel = pd.read_excel(archivo_excel, sheet_name=None)

client = OpenAI(api_key=OPEN_KEY)

columnas_parametros = ["Tipo de problema", "Nombre de problema", "Fase de desarrollo", "Sistema de producción", "Nivel de Severidad"]
columnas_respuestas = ["Tipo de Recomendación", "Recomendación y Asesoría Agraria"]
db_hojas = ["BD Arroz", "BD Cacao", "BD Café", "BD Plátano"]
db_cultivos = ["Arroz", "Cacao", "Café", "Plátano"]
db_sugerencia = "Recomendación y Asesoría Agraria"

sistema_identidad="Eres Pachatec, un Asesor Agrario Virtual que da consejos útiles en menos de 250 palabras y siempre respondes en el mismo idioma en que eres preguntado. Cuando se pregunte sobre temas no relacionados a agricultura, cultivos o información relacionada no respondas."
#Texto recomendacion
texto_para_listas = "Nuestras recomendaciones pueden variar según la región en la que te encuentres. Por ello, te sugerimos buscar asesoramiento agronómico local para obtener consejos específicos y adaptados a tu ubicación. ¡Te deseamos mucho éxito y una excelente producción!"
texto_chatgpt = "Es importante recordar que, por el momento, sólo contamos con recomendaciones especializadas para solución de problemas y cuidados de los cultivos de café, cacao, arroz y plátano . ¡Mantente atento a las actualizaciones y mejoras continuas que estamos implementando para servirte mejor!"
texto_pre_listas = "Para ofrecerte una recomendación más específica, es importante comprender mejor tu situación agrícola. Para ello, necesitamos conocer algunos detalles adicionales de tu cultivo y/o problema (o consulta):"
#Umbral de parámetros
umbral_parametros = 4
# bloque gpt
def get_response(system_prompt, user_prompt):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0,
        max_tokens=600
    )
    return completion.choices[0].message.content

#Clasificador
def obtener_cultivo(pregunta):
    system_prompt = "Eres un chatbot experto agrícola"
    user_prompt = f'''Clasifica el tipo de cultivo en triple backticks como Arroz, Cacao, Café, Plátano y Otro. Da la respuesta en una sola palabra:
                        {pregunta}'''
    return get_response(system_prompt, user_prompt)

def obtener_listas(cultivo):
    hoja = "BD " + cultivo
    dict_columna = {}
    for columna in columnas_parametros:
        lista_columna = hojas_excel[hoja][columna].unique().tolist()
        dict_columna[columna] = lista_columna
    return dict_columna

def string_to_dictionary(valor_string):
    valores = valor_string.split(", ")
    dictionarie = {
        "Tipo de problema": valores[0],
        "Nombre de problema": valores[1],
        "Fase de desarrollo": valores[2],
        "Sistema de producción": valores[3],
        "Nivel de Severidad": valores[4]
    }
    return (dictionarie)


def mostrar_listas(df, list_dict, columna):
    this_list = list(list_dict.keys())
    if columna not in this_list:
        df_p = df[columna]
        print(f"Selecciona {columna}: ")
        lista_opciones = df_p.unique().tolist()

        for i in range(len(lista_opciones)):
            print(f"{i + 1}. {lista_opciones[i]}")

        valor_p = input("Ingrese el número de la lista: ")
        valor = lista_opciones[int(valor_p) - 1]
        print(f"Se seleccionó: {valor}\n")
    else:
        if list_dict[columna] in df[columna].unique().tolist():
            valor = list_dict[columna]
            print(f"El valor de {columna} es: {valor}\n")
        else:
            df_p = df[columna]
            print(f"Selecciona {columna}: ")
            lista_opciones = df_p.unique().tolist()

            for i in range(len(lista_opciones)):
                print(f"{i + 1}. {lista_opciones[i]}")

            valor_p = input("Ingrese el número de la lista: ")
            valor = lista_opciones[int(valor_p) - 1]
            print(f"Se seleccionó: {valor}\n")
    df_final = df[df[columna] == valor]
    return df_final, valor

pregunta = input("Cuál es tu pegunta: ")
time_start = time.time()
tipo_cultivo = obtener_cultivo(pregunta)
print(f"Se reconoció el tipo de cultivo: {tipo_cultivo}")

if tipo_cultivo != "Otro":
    #CONDICION 1: PARA CUANDO EL CULTIVO SEA ARROZ, PLATANO, CAFE O CACAO
    listas_cultivos = obtener_listas(tipo_cultivo)
    # #Obtiene un dictionary para el cultivo detectado, tiene todos los items para cada columna
    #print(listas_cultivos)

    # #Defino cada columna a una variable
    tipo_problema = (listas_cultivos["Tipo de problema"])
    nombre_problema = (listas_cultivos["Nombre de problema"])
    fase = (listas_cultivos["Fase de desarrollo"])
    sist_prod = (listas_cultivos["Sistema de producción"])
    severidad = (listas_cultivos["Nivel de Severidad"])

    # Descubre los paramatros de la pregunta, le paso las columnas
    system_prompt = "Eres un sistema de clasificacion experto agrícola"
    user_prompt = f'''Clasifica las características de la pregunta según cada elemento, si no corresponde asigna el valor de "Otro", dar como respuesta solo los valores asignados separados por coma:
                            Pregunta: {pregunta}
                            Tipo de problema: {tipo_problema}
                            Nombre de problema(Relaciona también nombres coloquiales): {nombre_problema}
                            Fase de desarrollo (relaciona datos de la pregunta, como si el cultivo ya da fruto a su fase actual): {fase}
                            Sistema de producción: {sist_prod}
                            Nivel de Severidad(Relaciona el momento de identificacion del insecto o enfermedad. Mientras más temprano se haya identificado será menos severo, identifica palabras como acabo de, hace unos días, recientemente): {severidad}'''

    Clasif = get_response(system_prompt, user_prompt)

    # # Convierto la respuesta a un dictionary
    caracteristicas_dict = string_to_dictionary(Clasif)
    print(caracteristicas_dict)

    # # Elimino los key para cuando su valor sea Otro, N.a o N.A
    filtered_dict = {key: value for key, value in caracteristicas_dict.items() if value not in ['Otro', 'N.A', 'N.a']}
    #print(f"filtered_dict: {filtered_dict}")
    #No hay campos para Nutrición en nivel de severidad, pasa a ser N.a para no asignarle un nivel de severidad
    try:
        if filtered_dict["Tipo de problema"] == "Nutrición":
            filtered_dict["Nivel de Severidad"] = "N.a"
    except:
        None

    #print(f"filtered_dict_2: {filtered_dict}")
    num_caracteristicas = len(filtered_dict)

    #IMPRIMIR COMO MÉTRICA
    print(f"Se encontraron {num_caracteristicas}, las caracteristicas son: {Clasif}")

    if num_caracteristicas >= umbral_parametros:
        #CONDICION 2
        df = hojas_excel["BD " + tipo_cultivo]
        for key, value in filtered_dict.items():
            df = df[df[key] == value]

        #print(df)
        if not df['Recomendación y Asesoría Agraria'].empty:
            #texto_recomendado = df['Recomendación y Asesoría Agraria'].sample().values[0]
            texto_recomendado = "-".join(df['Recomendación y Asesoría Agraria'].values)
        else:
            texto_recomendado = ""

        #resultado = "-".join(df['Recomendación y Asesoría Agraria'].values)
        #print(resultado)
        #print(f"Texto seleccionado: {texto_recomendado}")

        system_prompt = sistema_identidad
        user_prompt = f'''Responde de la siguiente forma: Da una respuesta con tus conocimientos avanzados de agrónomo experto para la pregunta y complétala (en parrafos posteriores) con la información del texto recomendado siempre y cuando no entre en contradiccion con la recomendación de los parráfos previos. Siempre que sea posible trata de dar recomendaciones precisas (dosis de pesticidas, fungicidad, nutrientes, etc) siempre que la pregunta lo permita.                     
                                        pregunta: {pregunta}
                                        Texto recomendado: {texto_recomendado}'''
        respuesta_gpt = get_response(system_prompt, user_prompt)

        transcurso_tiempo = time.time() - time_start
        print(f"Tiempo hasta respuesta: {transcurso_tiempo}")

        print(respuesta_gpt + "\n")
        print(texto_para_listas)

    elif (caracteristicas_dict["Nombre de problema"] != "Otro"):
        #CONDICION 3: LISTAS
        system_prompt = sistema_identidad
        user_prompt = pregunta
        respuesta_gpt = get_response(system_prompt, user_prompt)

        print(respuesta_gpt)
        list_dict = [key for key in caracteristicas_dict if key not in filtered_dict]
        print(f"Elementos identificados: {filtered_dict}")
        print(texto_pre_listas)
        print("Parece que tenemos información relacionada a tu pregunta en nuestra base de datos personal, te invito a completar tu pregunta con esta información")

        hoja = "BD " + tipo_cultivo
        #secuencia: Tipo de problema, Nombre de problema, Fase de desarrollo, Sistema de producción,
                  # Nivel de severidad, Tipo de Recomendación, Recomendación y Asesoría Agraria
        todas_columnas = ["Tipo de problema", "Nombre de problema", "Fase de desarrollo", "Sistema de producción", "Nivel de Severidad"]
        lista_existente = list(filtered_dict.keys())
        columnas_agregadas = []

        #df, valor = mostrar_listas(df, list_dict, columna)
        # # # BUCLE PARA RESPUESTAS CON LISTAS.

        df = hojas_excel["BD " + tipo_cultivo]
        list_dict = filtered_dict
        for each_column in todas_columnas:
            this_list = list(list_dict.keys())
            # Se comienza con los key que no se detectaron
            if each_column not in this_list:
                # busca la columna en el df
                df_p = df[each_column]

                print(f"Selecciona {each_column}: ")
                lista_opciones = df_p.unique().tolist()

                for i in range(len(lista_opciones)):
                    print(f"{i + 1}. {lista_opciones[i]}")

                valor_p = input("Ingrese el número de la lista: ")
                valor = lista_opciones[int(valor_p) - 1]
                print(f"Se seleccionó: {valor}\n")
            # Si el key sí fue detectado(en el dict de caracteristicas)
            else:
                # Si el parámetro encontrado existge en la serie de lista hasta el momento, si no, pide su lista
                if list_dict[each_column] in df[each_column].unique().tolist():
                    valor = list_dict[each_column]
                    print(f"El valor de {each_column} es: {valor}\n")
                else:
                    df_p = df[each_column]
                    print(f"Selecciona {each_column}: ")
                    lista_opciones = df_p.unique().tolist()

                    for i in range(len(lista_opciones)):
                        print(f"{i + 1}. {lista_opciones[i]}")

                    valor_p = input("Ingrese el número de la lista: ")
                    valor = lista_opciones[int(valor_p) - 1]
                    print(f"Se seleccionó: {valor}\n")

            df = df[df[each_column] == valor]

        texto_recomendado = df["Recomendación y Asesoría Agraria"].sample().values[0]

        system_prompt = sistema_identidad
        user_prompt = f'''Responde de la siguiente forma: Da una respuesta con tus conocimientos avanzados de agrónomo experto para la pregunta y compléntala (en parrafos posteriores) con la información del texto recomendado siempre y cuando no entre en contradiccion con la recomendación de los parráfos previos. Siempre que sea posible trata de de dar recomendaciones precisas (dosis de pesticidas, fungicidad, nutrientes, etc) siempre que la pregunta lo permita.                     
                                                pregunta: {pregunta}
                                                Texto recomendado: {texto_recomendado}'''


        respuesta_gpt = get_response(system_prompt, user_prompt)
        print(respuesta_gpt)
        print(texto_para_listas)
        transcurso_tiempo = time.time() - time_start
        print(f"Tiempo hasta respuesta: {transcurso_tiempo}")
    else:
        system_prompt = sistema_identidad
        user_prompt = f'''Da una respuesta a la pregunta con tus conocimientos expertos. Siempre que sea posible trata de de dar recomendaciones precisas (dosis de pesticidas, fungicidad, nutrientes, etc) siempre que la pregunta lo requiera.                      
                                                    pregunta: {pregunta}'''
        respuesta_gpt = get_response(system_prompt, user_prompt)
        print(respuesta_gpt)
        print(texto_para_listas)
        transcurso_tiempo = time.time() - time_start
        print(f"Tiempo hasta respuesta: {transcurso_tiempo}")
else:
    #CONDICION 4
    system_prompt = sistema_identidad
    user_prompt = f'''Da una respuesta a la pregunta con tus conocimientos expertos. Siempre que sea posible trata de de dar recomendaciones precisas (dosis de pesticidas, fungicidad, nutrientes, etc) siempre que la pregunta lo permita y lo requiera.                     
                                            pregunta: {pregunta}'''
    respuesta_gpt = get_response(system_prompt, user_prompt)
    print(respuesta_gpt)
    print(texto_chatgpt)
    transcurso_tiempo = time.time() - time_start
    print(f"Tiempo hasta respuesta: {transcurso_tiempo}")