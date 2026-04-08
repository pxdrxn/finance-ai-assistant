import unicodedata


DISCLAIMER = (
    "\n\nAviso: esta resposta tem caráter exclusivamente educativo e informativo. "
    "Ela não constitui recomendação, consultoria ou aconselhamento de investimento."
)


def normalizar_texto(texto: str) -> str:
    texto_normalizado = unicodedata.normalize("NFKD", texto)
    texto_sem_acentos = "".join(char for char in texto_normalizado if not unicodedata.combining(char))
    return texto_sem_acentos.lower().strip()
