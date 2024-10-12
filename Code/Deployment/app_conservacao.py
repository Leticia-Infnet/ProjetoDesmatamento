import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import nltk
import re
import plotly.express as px
from wordcloud import WordCloud
from PIL import Image

const = {'base_dir': os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))}


@st.cache_data
def csv_news_to_df(filename) -> pd.DataFrame:
    '''
    Função que lê o arquivo CSV com os resultados da coleta de notícias e retorna um DataFrame.

    Returns:
    df (pd.DataFrame): DataFrame com os resultados da coleta de notícias.
    '''
    df = pd.read_csv(os.path.join(
        const['base_dir'], 'Sample_Data', 'Processed', filename))
    return df


@st.cache_data
def csv_brasilis_to_df(filename: str) -> pd.DataFrame:
    '''
    Função que lê o arquivo CSV com os resultados da coleta de dados do TerraBrasilis e retorna um DataFrame.

    Args:
    filename (str): Nome do arquivo CSV a ser lido.

    Returns:
    df (pd.DataFrame): DataFrame com os resultados da coleta de dados do TerraBrasilis.
    '''
    df = pd.read_csv(os.path.join(
        const['base_dir'], 'Sample_Data', 'Processed', filename))
    return df


@st.cache_data
def tokenize_text(df: pd.DataFrame) -> str:
    '''
    Função que tokeniza o texto das notícias e retorna uma string com as palavras filtradas.

    Args:
    df (pd.DataFrame): DataFrame com as notícias.

    Returns:
    filtered_words (str): String com as palavras filtradas.
    '''
    nltk.download('stopwords')
    stopwords = set(nltk.corpus.stopwords.words('portuguese'))

    words = [re.sub(r'[^\w\s]|[\d]', '', word.lower().strip())
             for line in df['content']
             for word in line.split()]

    filtered_words = [
        word for word in words if word and word not in stopwords and (len(word) > 3 or word == 'sul')]

    return ' '.join(filtered_words)


def create_line_chart(df: pd.DataFrame) -> None:
    '''
    Função que cria um gráfico de linha com o incremento do desmatamento da Mata Atlântica por UF.

    Args:
    df (pd.DataFrame): DataFrame com os dados do TerraBrasilis.

    Returns:
    None
    '''
    st.markdown('## Incremento do desmatamento da Mata Atlântica por UF')
    st.markdown('''O gráfico abaixo apresenta o incremento do desmatamento da Mata Atlântica por UF ao longo dos anos.
                Os dados foram obtidos a partir do site [TerraBrasilis](https://terrabrasilis.dpi.inpe.br/).''')

    UF = st.multiselect('Selecione as UF:',
                        df['uf'].unique(), default=df['uf'][0])
    df_filtered = df[df['uf'].isin(UF)]
    fig = px.line(df_filtered, x='year',
                  y='area km²',
                  color='uf',
                  markers=True)

    fig.update_layout(title='Incremento do desmatamento da Mata Atlântica por UF',
                      xaxis_title='Ano',
                      yaxis_title='Área (km²)',
                      legend_title='UF')

    fig.update_layout(title=dict(font=dict({'size': 25,
                                            'color': 'black',
                                            })))

    st.plotly_chart(fig)

    csv = df_filtered.to_csv(index=False)
    st.download_button(label='Download dos dados',
                       data=csv,
                       file_name='incremento_mata_atlantica.csv',
                       mime='text/csv')


def create_word_cloud(text: str) -> None:
    '''
    Função que cria uma nuvem de palavras a partir do texto das notícias.

    Args:
    text (str): Texto das notícias.

    Returns:
    None
    '''
    st.markdown('## Nuvem de Palavras:snow_cloud:')
    st.markdown('''A nuvem de palavras abaixo foi gerada a partir do conteúdo das
                notícias do ano de 2024 do site [((o))eco](https://www.oeco.org.br/).''')
    with st.spinner('Aguarde, carregando dados...'):
        frog_mask = np.array(Image.open(
            os.path.join(const['base_dir'], 'Sample_Data', 'Raw', 'frog.png')))

        stopwords = ['brasil', 'ano', 'ainda',
                     'área', 'estado', 'sobre',
                     'segundo', 'projeto', 'disse',
                     'todo', 'outro', 'outra',
                     'apenas', 'pode', 'grande',
                     'desde', 'gente', 'região',
                     'proposta', 'forma', 'além',
                     'toda', 'onde', 'áreas',
                     'processo', 'ações', 'espécie',
                     'país', 'maior', 'pessoa',
                     'município', 'nova', 'cidade',
                     'dado', 'sendo', 'anos',
                     'estudo', 'bioma', 'outras',
                     'podem', 'espécies', 'parte',
                     'acordo', 'então', 'caso',
                     'pessoas', 'porque', 'total',
                     'desse', 'órgão', 'território',
                     'outros', 'trabalho', 'após',
                     'dados', 'milhões', 'número',
                     'animais', 'impacto', 'parque',
                     'contra', 'atividade', 'pesquisadores',
                     'todos', 'medida', 'assim',
                     'municípios', 'ambiental', 'governo',
                     'nacional', 'problema', 'disso',
                     'hectare', 'hectares', 'plano',
                     'política', 'federal', 'proteção',
                     'presidente', 'dessa', 'estados',
                     'empresa', 'cada', 'afirmou',
                     'conta', 'sistema', 'instituto',
                     'durante', 'exemplo', 'dentro',
                     'relação', 'direito', 'afirmou',
                     'brasileiro', 'servidores', 'importante',
                     'pesquisa', 'novo', 'tema']

        wordcloud = WordCloud(width=800,
                              height=400,
                              background_color='white',
                              colormap='Dark2',
                              contour_width=3,
                              stopwords=stopwords,
                              contour_color='green',
                              mask=frog_mask).generate(text)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.set_axis_off()
        st.pyplot(fig)


def app():
    '''
    Função principal que cria a aplicação Streamlit.
    '''
    st.title('Observatório da Conservação:frog:')
    st.markdown('<div style="text-align: justify;">A conservação da biodiversidade e dos recursos naturais é um tema de extrema importância na sociedade atual. Vários ODS estão diretamente relacionados à conservação, como o ODS 13 (Ação contra a mudança global do clima), ODS 14 (Vida na água) e ODS 15 (Vida terrestre). Em vista desse cenário, o Observatório da Conservação foi criado para disponibilizar análises e informações sobre a conservação da biodiversidade e dos recursos naturais no Brasil.</div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(['Nuvem de Palavras', 'Mata Atlântica'])
    with tab1:
        df_news = csv_news_to_df('news_results.csv')
        text = tokenize_text(df_news)
        create_word_cloud(text)
    with tab2:
        df_brasilis = csv_brasilis_to_df(
            'incremento_mata_atlantica.csv')
        create_line_chart(df_brasilis)


if __name__ == '__main__':
    app()
