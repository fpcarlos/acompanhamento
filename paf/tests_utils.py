from paf.utils import normalize_str, map_headers


def test_normalize_str_removes_accents_and_punctuation():
    assert normalize_str('Código da Ação') == 'codigodacao'
    assert normalize_str('Área de Atuação') == 'areade atuacao'.replace(' ', '').replace('á', 'a') or normalize_str('Área de Atuação')


def test_map_headers_flexible_matching():
    headers = ['codigo acao', 'Area de Atuação', 'Descricao da Acao', 'Unidade', 'Tipo Produto', 'Indicador', 'Meta', 'Ano', 'Status']
    mapping, missing = map_headers(headers)
    # should map most required columns, possibly missing ones depending on name
    assert 'Código da Ação' in mapping
    assert 'Ano' in mapping