from typing import Dict


def calcular_juros_simples(capital: float, taxa_percentual: float, tempo: int) -> Dict[str, float]:
    taxa = taxa_percentual / 100
    juros = capital * taxa * tempo
    montante = capital + juros
    return {
        "capital": capital,
        "taxa_percentual": taxa_percentual,
        "tempo": tempo,
        "juros": round(juros, 2),
        "montante": round(montante, 2),
    }


def calcular_juros_compostos(capital: float, taxa_percentual: float, tempo: int) -> Dict[str, float]:
    taxa = taxa_percentual / 100
    montante = capital * ((1 + taxa) ** tempo)
    juros = montante - capital
    return {
        "capital": capital,
        "taxa_percentual": taxa_percentual,
        "tempo": tempo,
        "juros": round(juros, 2),
        "montante": round(montante, 2),
    }
