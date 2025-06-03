# 🌱 Pachatec - Asistente Virtual Agrónomo con IA

Pachatec es una aplicación web construida con Flask que actúa como un asistente virtual inteligente especializado en brindar recomendaciones agronómicas. Utiliza la API de OpenAI para interpretar consultas sobre cultivos específicos (arroz, cacao, café y plátano) y generar respuestas expertas a partir de una base de datos local en Excel.

---

## 🚀 Características

- Clasificación automática del tipo de cultivo: arroz, café, cacao, plátano u "otro".
- Extracción de características clave desde la pregunta del usuario.
- Generación de respuestas precisas y personalizadas usando `gpt-4o-mini`.
- Lectura y filtrado dinámico de recomendaciones desde archivos `.xlsx`.
- Historial de conversación gestionado por sesión.
- Interfaz web sencilla con `chat.html`.

---

## 📁 Estructura del Proyecto

.
├── app.py # Archivo principal con el servidor Flask
├── db_pachatec.xlsx # Base de datos con hojas para cada cultivo
├── templates/
│ └── chat.html # Interfaz web para la interacción
└── README.md # Documentación del proyecto

yaml
Copiar
Editar

---

## ⚙️ Requisitos

- Python 3.8+
- Flask
- pandas
- openai

Instalación de dependencias:
```bash
pip install flask pandas openai
🔑 Configuración
Crea un archivo .env o exporta la variable de entorno directamente:

bash
Copiar
Editar
export OPEN_KEY='tu_clave_de_api_de_openai'
Asegúrate de tener el archivo db_pachatec.xlsx en el mismo directorio con las siguientes hojas:

BD Arroz

BD Cacao

BD Café

BD Plátano

Cada hoja debe contener las siguientes columnas:

Tipo de problema

Nombre de problema

Fase de desarrollo

Sistema de producción

Nivel de Severidad

Recomendación y Asesoría Agraria

🧠 Flujo de Trabajo
El usuario envía una consulta a través de la interfaz web.

Se clasifica el tipo de cultivo y las características del problema usando GPT.

Si el cultivo es válido y se encuentran suficientes coincidencias en la base de datos, se genera una recomendación personalizada.

Si la información es insuficiente, se solicitan datos complementarios al usuario.

Si el cultivo es desconocido, se da una respuesta general del asistente.

🔄 Endpoints
/
Método: GET
Carga la interfaz web chat.html.

/send_message
Método: POST
Recibe un JSON con el mensaje del usuario. Retorna una respuesta generada por la IA junto con detalles de clasificación y recomendaciones.

Ejemplo de payload:

json
Copiar
Editar
{
  "message": "Mi cultivo de plátano tiene manchas negras en las hojas."
}
Ejemplo de respuesta:

json
Copiar
Editar
{
  "response": "Te recomendamos aplicar...",
  "cultivo_type": "Plátano",
  "caracteristicas_dict": {...},
  "recomendaciones_values": [...],
  "texto_recomendado": "..."
}
💬 Mensajes Personalizados
Advertencia general: sobre la variabilidad de condiciones según la región.

Mensaje limitado: si el cultivo no es arroz, café, cacao o plátano.

Sugerencias adicionales: si se necesita más información del usuario para afinar la respuesta.
