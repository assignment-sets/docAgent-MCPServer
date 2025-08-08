# app/dependencies/llm.py

import os
from dotenv import load_dotenv
import logging
from functools import lru_cache
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Set up logger
logger = logging.getLogger(__name__)


@lru_cache
def get_gemini_llm() -> ChatGoogleGenerativeAI:
    try:
        logger.info("[⚙️] Instantiating Gemini LLM...")
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.3,
            timeout=10,
            max_retries=2,
            api_key=os.getenv("GOOGLE_API_KEY"),
        )
        logger.info("[✅] Gemini LLM instance ready.")
        return llm

    except Exception as e:
        logger.exception("[❌] Failed to instantiate Gemini LLM.")
