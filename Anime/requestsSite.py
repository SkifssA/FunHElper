import requests
from bs4 import BeautifulSoup
from .requestSQL import *
import re
from .workByKeys import *



def getTitle(soup):
    """Возвращает название аниме"""
    w = ''
    for i in soup.find_all(class_='anime-title'):
        w += i.find('h1').text
    return w


def getRating(soup):
    """Возвращает рейтинг аниме"""
    for i in soup.find_all(class_='rating-value'):
        return float(i.text.replace(',', '.'))


def getLinked(soup):
    """Возвращает список связных аниме"""
    for i in soup.find_all(id='video-watch2'):
        w = []
        for j in i.find_all(
                class_='seasons-item col-6 col-sm-4 col-md-4 col-lg-3 mb-3'):
            a = j.find('a')
            url = a.get('href')
            url = url[:url.rfind('-')] + '-a' + url[url.rfind('-') + 1:]
            w.append((url, a.text.strip(),
                      j.find(class_='seasons-item-info text-gray-dark-5 small'
                             ).text.strip()))
        return w


def getEpisodeCount(soup):
    w = 0 
    """Возвращает кол-во серий аниме"""
    pattern = re.compile(r'^\d+(/\d+)?$')  # ^ и $ обеспечивают точное совпадение всей строки
    # Поиск всех элементов, содержащих нужный текст
    matching_elements = soup.find_all(text=pattern)
    for i in matching_elements:
        w = i.strip() if (x :=
                             i.strip()).find('/') == -1 else x.split('/')[1]
    return int(w)


def getReleased(soup):
    """Возвращает завершено ли аниме"""
    for i in soup.find_all('a', attrs={'title': 'Вышел'}):
        return 1
    return 0


def getGenreId(soup):
    """Возвращает id жанра аниме"""
    w = []
    for i in soup.find_all(class_='col-6 col-sm-8 mb-1 overflow-h')[0]:
        if (i.text.strip() != ','):
            genre = getGenge(i.text.strip())
            if genre != []:
                w.append(genre[0][0])
            else:
                w.append(setGenre(i.text.strip()))
    return w

def getImage(soup, title):
    for i in soup.find_all('img', attrs={'title': title}):
        urlImg = i.get('src')
        begin = urlImg.rfind('/')+1
        return urlImg[begin:]

def registerAnime(data):
    if (x := getAnumeIDByUrl(data['url'])) != []:
        uploadAnime(anime_id=x[0][0], **data)
        return x[0][0]
    else:
        idv =  setAnime(**data)
        for i in data['genre_id']:
            plusAnimeGenre(idv, i)
        return idv


def requisites(url, parent_id=None, What=None, isPush=False):
    headers = {
        "Accept":
        "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru,en;q=0.9",
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 YaBrowser/24.12.0.0 Safari/537.36",
        "Referer": "https://yandex.ru/"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Проверка статуса ответа
        html = response.text
    except requests.exceptions.ProxyError as e:
        return f"Proxy error: {e}"
    except requests.exceptions.RequestException as e:
        return f"Request error: {e}"

    # Создаем объект BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(html, 'html.parser')
    title = getTitle(soup)
    data = {
        'url': url,
        'parent_id': parent_id,
        'whatIsIt': What,
        'genre_id': getGenreId(soup),
        'released': getReleased(soup),
        'title': title,
        'episode_count': getEpisodeCount(soup),
        'rating': getRating(soup),
        'linked': getLinked(soup),
        'idImage': getImage(soup, title)
    }

    if isPush and data['released']:
        for i in subscriptions:
            send_web_push(i, "Аниме вышло полностью",
                          data['title'], f"https://imgos.info/media/cache/thumbs_120x120/upload/anime/images/{data['idImage']}")
    
    idSelf = registerAnime(data)
    for i in data['linked']:
        if i[2] not in ['Изначальная история', 'Предыстория']:
            requisites(i[0], idSelf, i[2])
