import sys
import os
import time
import yaml
from openai import OpenAI

# Configuración global
TEMPERATURE = 0.7
DEFAULT_MODEL = "gpt-4"
EXIT_COMMANDS = ("salir", "exit", "quit", "/exit")

def cargar_config(path="config.yaml"):
    """Carga la configuración desde un archivo YAML"""
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
    """Envía una pregunta a GPT y retorna la respuesta"""
    try:
        respuesta = client.chat.completions.create(
            model=modelo,
            messages=[{"role": "user", "content": pregunta}],
            temperature=TEMPERATURE
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"❌ Error en la consulta a GPT:\n{e}"

def limpiar_entrada(pregunta):
    """Limpia la entrada del usuario removiendo espacios en blanco"""
    return pregunta.strip()

def procesar_comando_especial(comando):
    """
    Procesa comandos especiales del sistema
    Retorna:
    - True: comando procesado, continuar
    - False: comando de salida, terminar
    - None: no es comando especial
    """
    if comando == "/clear":
        # Limpiar consola (Windows: cls, Unix: clear)
        os.system('cls' if os.name == 'nt' else 'clear')
        return True
    elif comando == "/help":
        # Mostrar ayuda de comandos disponibles
        print("📋 Comandos disponibles:")
        print("  /clear - Limpiar consola")
        print("  /exit  - Salir del programa")
        print("  /help  - Mostrar esta ayuda")
        print("  salir, exit, quit - Salir del programa\n")
        return True
    elif comando == "/exit":
        # Comando de salida
        return False
    return None

def modo_interactivo(client, modelo):
    """Modo interactivo principal con mejoras de usabilidad"""
    # Mensaje de bienvenida amigable
    print("🤖 ¡Hola! Soy tu asistente GPT.")
    print("💬 Podés hacerme cualquier pregunta — Escribí 'salir' o '/help' para ver comandos.\n")
    
    while True:
        pregunta = input(">> ")
        # Limpiar entrada del usuario
        pregunta = limpiar_entrada(pregunta)
        
        # Procesar comandos especiales (/clear, /help, /exit)
        if pregunta.startswith('/'):
            resultado = procesar_comando_especial(pregunta)
            if resultado is False:
                break  # Salir del programa
            elif resultado is True:
                continue  # Comando procesado, continuar
        
        # Verificar comandos de salida tradicionales
        if pregunta.lower() in EXIT_COMMANDS:
            break
        
        # Ignorar entradas vacías
        if not pregunta:
            continue
        
        # Medir tiempo de respuesta de GPT
        inicio = time.time()
        respuesta = preguntar_a_gpt(pregunta, client, modelo)
        tiempo_transcurrido = time.time() - inicio
        
        # Mostrar respuesta y tiempo
        print(f"\n{respuesta}\n")
        print(f"⏱️  Tiempo de respuesta: {tiempo_transcurrido:.2f}s\n")
        
        # Guardar conversación en archivo
        with open("conversacion.txt", "a", encoding="utf-8") as file:
            file.write(f"Usuario: {pregunta}\n")
            file.write(f"GPT: {respuesta}\n\n")

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
