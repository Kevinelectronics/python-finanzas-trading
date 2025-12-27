from dotenv import load_dotenv
from openai import OpenAI
import os
os.environ.pop("SSLKEYLOGFILE", None)
load_dotenv()

from openai import OpenAI

# PEGA AQUÍ TU API KEY (una sola línea, sin espacios)
OPENAI_API_KEY = "YOUR_API_KEY"

def main():
    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Reply only with the word OK"}
        ],
        temperature=0
    )

    print("Respuesta de OpenAI:")
    print(response.choices[0].message.content)

if __name__ == "__main__":
    main()
