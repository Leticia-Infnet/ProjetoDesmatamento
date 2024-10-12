import os
import pandas as pd

const = {'base_dir': os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))}


def normalize_terrabrasilis(file_name: str) -> None:
    '''
    Função para normalizar os dados provenientes do TerraBrasilis e salvar em um novo arquivo csv.

    Args:
    file_name: str - Nome do arquivo csv a ser normalizado.

    Returns:
    None
    '''

    df = pd.read_csv(os.path.join(
        const['base_dir'], 'Sample_Data', 'Raw', file_name), sep=';')

    df['area km²'] = round(
        df['area km²'].str.replace('.', '').str.replace(',', '.').astype(float), 2)

    df.sort_values(by='year', ascending=True, inplace=True)

    df.to_csv(os.path.join(
        const['base_dir'], 'Sample_Data', 'Processed', file_name), index=False)


if __name__ == '__main__':
    normalize_terrabrasilis('incremento_mata_atlantica.csv')
