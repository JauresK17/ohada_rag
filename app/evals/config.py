from langchain_openai import ChatOpenAI
from langchain_mistralai import MistralAIEmbeddings
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from app.config import settings

#1LLM juge via Openrouter 
llm_juge = ChatOpenAI(
    model = "anthropic/claude-sonnet-5",
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.OPENROUTER_API_KEY
)

#2. Embeddings Mistral 
embeddings = MistralAIEmbeddings(
    model="mistral-embed",
    api_key=settings.MISTRAL_API_KEY
)

llm_ragas = LangchainLLMWrapper(llm_juge)
emb_ragas = LangchainEmbeddingsWrapper(embeddings)