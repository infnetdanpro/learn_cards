from googletrans import Translator


def translate(original_word: str, source_lang: str='ru', dest_lang: str='sr') -> str:
    translator = Translator()
    result = translator.translate(original_word, src=source_lang, dest=dest_lang)
    return result.text
