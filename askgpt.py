import sys
import yaml
from openai import OpenAI

TEMPERATURE = 0.7
DEFAULT_MODEL = "gpt-4"
EXIT_COMMANDS = ("salir", "exit", "quit")

def cargar_config(path="config.yaml"):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print("⚠️  Archivo config.yaml no encontrado.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error al cargar la configuración: {e}")
        sys.exit(1)

def preguntar_a_gpt(pregunta, client, modelo):
    try:
        respuesta = client.chat.completions.create(
            model=modelo,
            messages=[{"role": "user", "content": pregunta}],
            temperature=TEMPERATURE
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"❌ Error en la consulta a GPT:\n{e}"

def modo_interactivo(client, modelo):
    print("💬 Asistente GPT — Escribí 'salir' para terminar.\n")
    while True:
        pregunta = input(">> ")
        if pregunta.lower() in EXIT_COMMANDS:
            break
        respuesta = preguntar_a_gpt(pregunta, client, modelo)
        print(f"\n{respuesta}\n")

def main():
    config = cargar_config()
    client = OpenAI(api_key=config.get("openai_api_key"))
    modelo = config.get("model", DEFAULT_MODEL)
    
    if len(sys.argv) > 1:
        print(preguntar_a_gpt(" ".join(sys.argv[1:]), client, modelo))
    else:
        modo_interactivo(client, modelo)

if __name__ == "__main__":
    main()
