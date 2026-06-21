import os
import logging
import requests
from dotenv import load_dotenv
from supabase import create_client, Client

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()

# Credenciais
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ZAPI_INSTANCE = os.getenv("ZAPI_INSTANCE")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")


def conectar_supabase() -> Client:
    """Inicializa e retorna o cliente do Supabase."""
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        logging.error(f"Erro ao conectar com Supabase: {e}")
        raise


def buscar_contatos(supabase: Client, limite: int = 3) -> list:
    """Busca os contatos cadastrados na tabela do Supabase."""
    try:
        logging.info("Buscando contatos no Supabase...")
        resposta = supabase.table("contatos").select("*").limit(limite).execute()
        return resposta.data
    except Exception as e:
        logging.error(f"Erro ao buscar contatos: {e}")
        return []


def enviar_mensagem_whatsapp(nome: str, telefone: str):
    """Envia a mensagem via Z-API para o contato específico."""
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text"
    mensagem = f"Olá, {nome} tudo bem com você?"

    payload = {
        "phone": telefone,
        "message": mensagem
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()  # Lança exceção se o HTTP status for de erro (4xx, 5xx)
        logging.info(f"Mensagem enviada com sucesso para {nome} ({telefone})!")
    except requests.exceptions.RequestException as e:
        logging.error(f"Falha ao enviar mensagem para {nome} ({telefone}). Erro: {e}")


def main():
    # Validação de variáveis de ambiente
    if not all([SUPABASE_URL, SUPABASE_KEY, ZAPI_INSTANCE, ZAPI_TOKEN]):
        logging.error("Faltam variáveis de ambiente. Verifique seu arquivo .env.")
        return

    supabase = conectar_supabase()
    contatos = buscar_contatos(supabase)

    if not contatos:
        logging.warning("Nenhum contato encontrado no banco de dados.")
        return

    logging.info(f"Encontrado(s) {len(contatos)} contato(s). Iniciando envios...")

    for contato in contatos:
        nome = contato.get("nome_contato")
        telefone = contato.get("telefone")

        if nome and telefone:
            enviar_mensagem_whatsapp(nome, telefone)
        else:
            logging.warning(f"Contato ignorado (dados incompletos): {contato}")


if __name__ == "__main__":
    main()