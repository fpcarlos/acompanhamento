import csv
from openpyxl import load_workbook
from io import TextIOWrapper

REQUIRED_COLUMNS = [
    'Código da Ação',
    'Área de Atuação',
    'Descrição da Ação',
    'Unidade Técnica Responsável',
    'Tipo de Produto / Instrumento',
    'Indicador',
    'Meta',
    'Ano',
    'Status',
]


def read_table_from_file(file_obj):
    """Read CSV or XLSX into list of dicts (header row expected).

    Returns (rows, errors) where rows is a list of dict and errors is a list of strings.
    """
    fname = getattr(file_obj, 'name', '')
    if fname.lower().endswith('.csv'):
        # Decode bytes to text
        text = TextIOWrapper(file_obj.file, encoding='utf-8') if hasattr(file_obj, 'file') else TextIOWrapper(file_obj, encoding='utf-8')
        reader = csv.DictReader(text)
        rows = list(reader)
        return rows, []

    if fname.lower().endswith('.xlsx'):
        wb = load_workbook(file_obj, read_only=True)
        ws = wb.active
        rows = []
        headers = [cell.value for cell in next(ws.rows)]
        for r in ws.iter_rows(min_row=2, values_only=True):
            row = {headers[i]: r[i] for i in range(len(headers))}
            rows.append(row)
        return rows, []

    return [], [f'Unsupported file type: {fname}']


def validate_columns(headers):
    missing = [c for c in REQUIRED_COLUMNS if c not in headers]
    return missing
