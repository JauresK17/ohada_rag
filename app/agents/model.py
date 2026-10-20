from app.config import settings 
from openai import OpenAI 
import logfire 

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.OPENROUTER_API_KEY,
)

def appeler_llm(prompt:str)->str:
    with logfire.span("Appel LLM"):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role":"user","content":prompt}]
            )
            texte = response.choices[0].message.content
            logfire.info("Reponse LLM recue ")
            return texte 
        except Exception as e :
             logfire.error(f"Echec appel LLM : {e}")
             raise 

