import os
import time
import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

const = {'base_dir': os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))}

load_dotenv()

github_token = os.getenv('GH_TOKEN')

os.environ['GH_TOKEN'] = github_token


def get_news_urls(main_url: str, pages: int = 1) -> list:
    '''
    Função que recebe a URL da página de notícias do jornal O Eco e a quantidade de páginas a serem percorridas para coletar os links das notícias.

    Args:
    main_url (str): URL da página de notícias do jornal O Eco.
    pages (int): Quantidade de páginas a serem percorridas para coletar os links das notícias.

    Returns:
    all_urls (list): Lista com os links das notícias coletadas.
    '''
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    driver = webdriver.Firefox(service=Service(
        GeckoDriverManager().install()), options=options)

    driver.get(main_url)
    all_urls = []

    for _ in range(pages):
        try:

            news_elements = driver.find_elements(
                By.XPATH, '//h2[@class="h4 mb-3"]/a')
            for news_element in news_elements:
                url = news_element.get_attribute('href')
                if url:
                    all_urls.append(url)

            next_button = driver.find_element(
                By.XPATH, '//a[@class="btn text-secondary"][i[@class="fas fa-long-arrow-alt-right ml-1"]]'
            )
            next_button.click()
            time.sleep(2)
        except Exception as e:
            print(f"No more pages or an error occurred: {e}")
            break

    driver.quit()
    return all_urls


def scrape_news_content(url: str) -> dict:
    '''
    Função que recebe a URL de uma notícia do jornal O Eco e coleta o título, subtítulo, autor, data de publicação e conteúdo da notícia.

    Args:
    url (str): URL da notícia do jornal O Eco.

    Returns:
    dict: Dicionário com o título, subtítulo, autor, data de publicação e conteúdo da notícia.
    '''
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    driver = webdriver.Firefox(service=Service(
        GeckoDriverManager().install()), options=options)

    driver.get(url)

    title = driver.find_element(By.XPATH, '//h1').text
    try:
        subtitle = driver.find_element(
            By.XPATH, '//p[@class="lead font-italic mb-5"]').text
    except:
        subtitle = None
    try:
        author = driver.find_element(
            By.XPATH, '//meta[@name="author"]').get_attribute('content')
    except:
        author = None
    try:
        publish_date = driver.find_element(
            By.XPATH, '//meta[@property="article:published_time"]').get_attribute('content')
    except:
        publish_date = None

    content = ''
    for tag in driver.find_elements(By.XPATH, '//div[@class="article"]//p'):
        content += tag.text

    driver.quit()
    return {
        'title': title,
        'subtitle': subtitle,
        'author': author,
        'publish_date': publish_date,
        'content': content
    }


def scrape_concurrent(urls: list, num_threads=5) -> list:
    '''
    Função que recebe uma lista de URLs de notícias do jornal O Eco e coleta o título, subtítulo, autor, data de publicação e conteúdo de cada notícia de forma concorrente.

    Args:
    urls (list): Lista com as URLs das notícias do jornal O Eco.

    Returns:
    results (list): Lista com os dicionários contendo o título, subtítulo, autor, data de publicação e conteúdo de cada notícia.
    '''
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        results = list(executor.map(scrape_news_content, urls))
    return results


def main_scrape_process(main_url: str) -> list:
    '''
    Função que executa o processo de coleta de notícias do jornal O Eco, coletando os links das notícias e em seguida coletando o título, subtítulo, autor, data de publicação e conteúdo de cada notícia.

    Args:
    main_url (str): URL da página de notícias do jornal O Eco.

    Returns:
    all_results (list): Lista com os dicionários contendo o título, subtítulo, autor, data de publicação e conteúdo de cada notícia.
    '''
    urls = get_news_urls(main_url)

    with ProcessPoolExecutor() as executor:
        all_results = list(executor.map(
            scrape_concurrent, [urls], chunksize=1))

    return all_results


def save_results_to_csv(results: list, filename='news_results.csv') -> None:
    '''
    Função que recebe a lista de dicionários com os resultados da coleta de notícias e salva em um arquivo CSV.

    Args:
    results (list): Lista com os dicionários contendo o título, subtítulo, autor, data de publicação e conteúdo de cada notícia.
    filename (str): Nome do arquivo CSV a ser salvo.

    Returns:
    None
    '''
    if results:

        df = pd.DataFrame(results)

        df.to_csv(os.path.join(
            const['base_dir'], 'Sample_Data', 'Processed', filename), index=False)
        print(f"Results saved to {filename}")
    else:
        print("No results to save.")


if __name__ == "__main__":
    main_url = 'https://oeco.org.br/category/noticias/'
    results = main_scrape_process(main_url)
    save_results_to_csv(results[0])
