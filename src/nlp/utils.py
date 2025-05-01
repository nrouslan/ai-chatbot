def clear_phrase(phrase):
    """Функция простейшей очистки фраз от «мусора»."""
    phrase = phrase.lower()

    alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя- '
    result = ''.join(symbol for symbol in phrase if symbol in alphabet)

    # TODO: Необходимо существенно доработать эту функцию !

    return result.strip()
