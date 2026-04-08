from assistant_app.core.calculations import calcular_juros_compostos, calcular_juros_simples


def test_calcular_juros_simples() -> None:
    resultado = calcular_juros_simples(1000, 2, 6)
    assert resultado["juros"] == 120.0
    assert resultado["montante"] == 1120.0


def test_calcular_juros_compostos() -> None:
    resultado = calcular_juros_compostos(1000, 1, 12)
    assert resultado["juros"] == 126.83
    assert resultado["montante"] == 1126.83
