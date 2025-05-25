import sys
import yaml
import openai
from openai import OpenAI

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

def preguntar_a_gpt(pregunta, config):
    client = OpenAI(api_key=config.get("openai_api_key"))
    modelo = config.get("model", "gpt-4")

    try:
        respuesta = client.chat.completions.create(
            model=modelo,
            messages=[{"role": "user", "content": pregunta}],
            temperature=0.7
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"❌ Error en la consulta a GPT:\n{e}"

def modo_interactivo(config):
    print("💬 Asistente GPT — Escribí 'salir' para terminar.\n")
    while True:
        pregunta = input(">> ")
        if pregunta.lower() in ["salir", "exit", "quit"]:
            break
        respuesta = preguntar_a_gpt(pregunta, config)
        print(f"\n{respuesta}\n")

def main():
    config = cargar_config()
    if len(sys.argv) > 1:
        pregunta = " ".join(sys.argv[1:])
        print(preguntar_a_gpt(pregunta, config))
    else:
        modo_interactivo(config)

if __name__ == "__main__":
    main()
