# app/tools/text_summarizer.py

import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from app.dependencies import get_gemini_llm
from app.schemas import SummarizeInput

logger = logging.getLogger(__name__)


async def summarize_text(input_data: SummarizeInput) -> str:
    try:
        llm: ChatGoogleGenerativeAI = get_gemini_llm()
        prompt = f"Summarize this text:\n\n{input_data.text}"
        logger.debug("Generated prompt: %s", prompt)

        response = await llm.ainvoke(prompt)

        if not response:
            logger.error("Empty response from LLM for input: %s", input_data.text)
            raise ValueError("Empty response from LLM")

        logger.info("Successfully summarized input text.")
        return response.content

    except Exception as e:
        logger.exception("Summarization failed due to unexpected error.")
        raise Exception(f"Summarization failed: {str(e)}")
