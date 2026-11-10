from reclamacoes.bootstrap import intervalo_diferenca


def test_previsoes_iguais_dao_diferenca_zero():
    real = ["atraso", "outro", "atraso", "atendimento"] * 10
    prev = ["atraso", "atraso", "atraso", "atendimento"] * 10
    assert intervalo_diferenca(real, prev, prev, n_amostras=50) == (0, 0, 0)


def test_abordagem_perfeita_ganha_com_intervalo_positivo():
    real = ["atraso", "outro"] * 50
    ruim = ["atraso"] * 100
    dif, baixo, alto = intervalo_diferenca(real, real, ruim, n_amostras=200)
    assert dif > 0 and baixo > 0
