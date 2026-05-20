import httpx
from typing import Tuple

# Бесплатный API словаря (не требует ключа, но архитектура готова под любые API)
DICTIONARY_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"

def format_api_response(data: list) -> str:
    """Парсит JSON и возвращает читаемый текст."""
    if not data:
        return "Нет данных для отображения."
    
    entry = data[0]
    word = entry.get("word", "").capitalize()
    phonetic = entry.get("phonetic", "")
    meanings = entry.get("meanings", [])

    output = f"📖 {word} {phonetic}\n\n"
    
    for meaning in meanings:
        pos = meaning.get("partOfSpeech", "")
        definitions = meaning.get("definitions", [])
        output += f"🔹 {pos}:\n"
        
        # Ограничиваем вывод первыми 2 определениями для компактности
        for i, defn in enumerate(definitions[:2], 1):
            output += f"{i}. {defn.get('definition', '')}\n"
            example = defn.get('example')
            if example:
                output += f"   💡 Пример: {example}\n"
        output += "\n"
        
    return output.strip()

async def fetch_definition(word: str) -> Tuple[bool, str]:
    """
    Отправляет GET-запрос к API, обрабатывает ошибки сети/HTTP,
    возвращает кортеж (успех: bool, сообщение: str).
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{DICTIONARY_API_URL}{word.lower()}")
            
            if response.status_code == 404:
                return False, f"🔍 Слово «{word}» не найдено в английском словаре."
                
            response.raise_for_status() # Вызовет ошибку при 4xx/5xx
            
            data = response.json()
            text = format_api_response(data)
            return True, text
            
    except httpx.RequestError:
        return False, "⚠️ Ошибка сети. Не удалось связаться с API словаря."
    except httpx.HTTPStatusError as e:
        return False, f"❌ Сервер вернул ошибку: {e.response.status_code}. Попробуйте позже."
    except Exception as e:
        return False, f"❌ Неожиданная ошибка: {str(e)}"