import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class TweetRequest(BaseModel):
    tweet_url: str
    custom_title: str | None = None

def get_tweet_data(url: str):
    try:
        parts = url.split("/status/")
        if len(parts) < 2:
            raise ValueError("URL de tweet inválida")
        tweet_id = parts[1].split("?")[0].split("/")[0]
        
        api_url = f"https://api.fxtwitter.com/status/{tweet_id}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="No se pudo obtener el tweet")
            
        data = response.json().get("tweet", {})
        return {
            "text": data.get("text", ""),
            "author_name": data.get("author", {}).get("name", "Desconocido"),
            "author_screen_name": data.get("author", {}).get("screen_name", "anonimo"),
            "created_at": data.get("created_at", "")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"status": "Servidor de Tweets funcionando correctamente"}

@app.post("/process-tweet")
async def process_tweet(payload: TweetRequest):
    tweet_info = get_tweet_data(payload.tweet_url)
    
    if payload.custom_title:
        file_name = f"{payload.custom_title}.md"
    else:
        file_name = f"@{tweet_info['author_screen_name']}_tweet.md"
        
    md_content = f"""# Tweet de {tweet_info['author_name']} (@{tweet_info['author_screen_name']})

> {tweet_info['text']}

---
- **Fuente:** {payload.tweet_url}
- **Fecha:** {tweet_info['created_at']}
"""

    return {
        "status": "success",
        "file_name": file_name,
        "content": md_content,
        "message": "Tweet procesado en formato Markdown"
    }
