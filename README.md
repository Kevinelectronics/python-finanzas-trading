# python-finanzas-trading
Curso gratuito y público de Python para Finanzas y Trading Algorítmico, disponible en YouTube y Udemy. Aprende desde cero a usar Python para analizar datos financieros reales, consumir APIs, crear visualizaciones, dashboards, informes en Excel y dar tus primeros pasos en trading algorítmico.
=======
Python para Finanzas y Trading Algorítmico desde Cero

Este repositorio contiene el código del curso Python para Finanzas y Trading Algorítmico desde Cero.
Aprenderás paso a paso a usar Python para:

Extraer datos financieros desde APIs

Analizar datos con pandas y DataFrames

Crear métricas financieras

Visualizar datos y dashboards

Generar informes en Excel

Construir prototipos de bots de trading y alertas

(Opcional) Generar insights con IA

El objetivo es que cualquier persona, incluso sin experiencia previa, pueda seguir el curso y ejecutar el código sin problemas.

1️⃣ Requisitos previos

Antes de empezar necesitas tener instalado:

Python 3.9 o superior
👉 https://www.python.org/downloads/

Git
👉 https://git-scm.com/downloads

Para comprobar que todo está correcto:

python --version
git --version

2️⃣ Clonar el repositorio

Abre una terminal (PowerShell en Windows o Terminal en Mac/Linux) y ejecuta:

git clone https://github.com/TU_USUARIO/TU_REPO.git


Entra en la carpeta del proyecto:

cd TU_REPO

3️⃣ Crear entorno virtual (MUY IMPORTANTE)
🔹 Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1


Si ves el prefijo (.venv) en la terminal, todo va bien.

🔹 Mac / Linux
python3 -m venv .venv
source .venv/bin/activate

4️⃣ Instalar librerías necesarias

Con el entorno virtual activado, ejecuta:

pip install -r requirements.txt


Si todo va bien, verás cómo se instalan pandas, requests, matplotlib, etc.

5️⃣ Configurar variables de entorno (API Keys)
1. Crear el archivo .env
Windows
copy .env.example .env

Mac / Linux
cp .env.example .env

2. Editar el archivo .env

Abre .env con un editor de texto y rellena tus claves:

FMP_API_KEY=tu_api_key_de_fmp
OPENAI_API_KEY=tu_api_key_de_openai
TELEGRAM_BOT_TOKEN=tu_token_de_telegram
TELEGRAM_CHAT_ID=tu_chat_id


📌 Nunca subas este archivo a GitHub.

6️⃣ Estructura del proyecto
data/
 └─ raw/                → CSV de ejemplo (datos históricos)
outputs/
 └─ excel/              → Excel generados automáticamente
src/
 └─ lessons/            → Scripts del curso (por orden)

7️⃣ Ejecutar los scripts (por orden del curso)

⚠️ Ejecuta siempre los scripts desde la raíz del proyecto.

🔹 Clase 1 – Introducción a Python y APIs financieras
python src/lessons/script_clase1.py

🔹 Clase 2 – DataFrames y análisis con pandas
python src/lessons/script_clase_2_df.py

🔹 Clase 3 – Visualización de datos financieros
python src/lessons/script3_visualizacion.py

🔹 Clase 4 – Dashboards financieros
python src/lessons/script4_dashboard.py

🔹 Clase 5 – Bot de trading y automatización
python src/lessons/tradin_bot_script5.py

🔹 Clase Extra – Generación de insights con IA (opcional)
python src/lessons/insights_with_chatgpt.py

8️⃣ Dónde se guardan los resultados

📊 Archivos Excel → outputs/excel/

📁 Datos CSV → data/raw/

📈 Gráficos y dashboards → se muestran en pantalla o se guardan automáticamente

9️⃣ Errores comunes y soluciones rápidas
❌ Error: ModuleNotFoundError

👉 Asegúrate de haber activado el entorno virtual:

.\.venv\Scripts\Activate.ps1


o

source .venv/bin/activate

❌ Error 401 / API Key incorrecta

👉 Revisa que:

El archivo .env existe

La API Key es correcta

No hay espacios extra en el .env

❌ El script no encuentra archivos

👉 Ejecuta siempre los comandos desde la carpeta raíz del proyecto, no desde src.

🔟 Recomendaciones finales

Ejecuta los scripts en el orden del curso

Lee el código mientras se ejecuta

Modifica parámetros y experimenta

No tengas miedo a romper cosas (para eso está el entorno virtual 😉)
