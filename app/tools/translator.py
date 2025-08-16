# app/tools/translator.py

import logging
from app.schemas import TranslationInput
from langchain_google_genai import ChatGoogleGenerativeAI
from app.dependencies import get_gemini_llm

logger = logging.getLogger(__name__)


async def get_translation(input_translation: TranslationInput) -> str:
    try:
        llm: ChatGoogleGenerativeAI = get_gemini_llm()

        prompt = f"""You are a translation assistant.

Task:
Translate the text below from {input_translation.input_language} to {input_translation.output_language}.

Guidelines:
- Provide a meaning-based translation; adapt idioms and figurative language naturally.
- If profanity appears, convey the intent politely without using profanity yourself.
- If the stated source language seems wrong or unclear, auto-detect and translate from the actual language instead.
- If you cannot detect the source or target language, state that you cannot perform the translation in english.
- Use your best judgment to capture the intended meaning.

Output:
- ONLY the translated text — no explanations, comments, or extra words.

Text:
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
