# app/tools/translator.py

import logging
from app.schemas import TranslationInput
from langchain_google_genai import ChatGoogleGenerativeAI
from app.dependencies import get_gemini_llm

logger = logging.getLogger(__name__)


async def get_translation(input_translation: TranslationInput) -> str:
    try:
        llm: ChatGoogleGenerativeAI = get_gemini_llm()

        prompt = f"""Translate the following text from {input_translation.input_language} to {input_translation.output_language}. 
        Provide a meaning-based translation, not a word-for-word literal translation, especially for idioms or figurative language. 
        Do not filter or censor any content, even if it is vulgar, offensive, or explicit, as this is for educational purposes only and its very important to reflect the real meaning for facilitating true understanding therefore you are also expected to use any word which best describes the meaning in the translation without censoring. 

        If the input language appears incorrect or unclear, only then you may detect the actual language automatically and proceed to translate from that instead. 
        Use your best judgment to interpret the intended meaning and translate accordingly. 

        Say nothing else but the translated text:

        {input_translation.text}"""

        logger.debug("Generated prompt: %s", prompt)

        response = await llm.ainvoke(prompt)

        if not response:
            logger.error(
                "Empty response from LLM for input: %s", input_translation.text
            )
            raise ValueError("Empty response from LLM")

        logger.info("Successfully translated input text.")
        return response.content

    except Exception as e:
        logger.exception("Translation failed due to unexpected error.")
        raise


if __name__ == "__main__":
    import asyncio

    translation_query = TranslationInput(
        text="bro that may happen once in a blue moon ",
        input_language="english",
        output_language="bengali",
    )

    async def local_test():
        res = await get_translation(translation_query)
        print(res)

    asyncio.run(local_test())
