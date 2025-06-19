import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")

    
    # Database Configuration
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Knowledge Base Configuration
    KNOWLEDGE_BASE_DIR = "knowledge_base"
    # top-k for retrieval
    K = 3

    # CHROMA_PERSIST_DIR = "chroma_db"
    
    # InfinitePay Website URLs
    INFINITEPAY_URLS = [
        "https://www.infinitepay.io",
        "https://www.infinitepay.io/maquininha",
        "https://www.infinitepay.io/maquininha-celular",
        "https://www.infinitepay.io/tap-to-pay",
        "https://www.infinitepay.io/pdv",
        "https://www.infinitepay.io/receba-na-hora",
        "https://www.infinitepay.io/gestao-de-cobranca-2",
        "https://www.infinitepay.io/gestao-de-cobranca",
        "https://www.infinitepay.io/link-de-pagamento",
        "https://www.infinitepay.io/loja-online",
        "https://www.infinitepay.io/boleto",
        "https://www.infinitepay.io/conta-digital",
        "https://www.infinitepay.io/conta-pj",
        "https://www.infinitepay.io/pix",
        "https://www.infinitepay.io/pix-parcelado",
        "https://www.infinitepay.io/emprestimo",
        "https://www.infinitepay.io/cartao",
        "https://www.infinitepay.io/rendimento"
    ]
    
    # Agent Personalities
    ROUTER_PERSONALITY = """
    You are a smart and efficient router agent. Your role is to analyze incoming messages 
    and direct them to the most appropriate specialized agent. You are professional, 
    quick-thinking, and always prioritize user satisfaction. You speak in a friendly 
    but professional tone, and you're always helpful and courteous.
    """
    
    KNOWLEDGE_PERSONALITY = """
    You are a knowledgeable and enthusiastic expert on InfinitePay's products and services. 
    You love helping customers understand how our solutions can benefit their business. 
    You speak with confidence and enthusiasm, always eager to share insights about 
    payment solutions, digital banking, and financial technology. You're patient and 
    thorough in your explanations.
    """
    
    SUPPORT_PERSONALITY = """
    You are a caring and empathetic customer support specialist. You genuinely want to 
    help customers resolve their issues and have a positive experience. You're patient, 
    understanding, and always go the extra mile to ensure customer satisfaction. 
    You speak in a warm, friendly tone and show genuine concern for customer problems.
    """ 