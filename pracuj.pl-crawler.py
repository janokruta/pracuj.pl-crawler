__author__ = 'Jan Okruta'
__email__ = 'jan.okruta@gmail.com'
__license__ = 'GPL'

import os
import requests
import shutil
import time

from bs4 import BeautifulSoup
from requests_html import HTMLSession

locations = {
    'cala polska': '0',
    'dolnoslaskie': '1',
    'kujawsko-pomorskie': '2',
    'lubelskie': '3',
    'lubuskie': '4',
    'lodzkie': '5',
    'malopolskie': '6',
    'mazowieckie': '7',
    'opolskie': '8',
    'pomorskie': '9',
    'podkarpackie': '10',
    'podlaskie': '11',
    'swietokrzyskie': '12',
    'slaskie': '13',
    'warminsko-mazurskie': '14',
    'wielkopolskie': '15',
    'zachodniopomorskie': '16'
}

ltrPL = "ŻÓŁĆĘŚĄŹŃżółćęśąźń"
ltrnoPL = "ZOLCESAZNzolcesazn"


def offers_spider(kw, loc):
    number_of_pages = 1
    offers_count = 0
    page = 1
    while page <= number_of_pages:
        print('Szukam ofert...')
        url = 'https://www.pracuj.pl/praca/' + kw + ';kw/a;r,' + locations[loc] + '/?pn=' + str(page)
        session = HTMLSession()
        r = session.get(url)
        r.html.render()
        offers_links = [[a.absolute_links.pop(), a.text] for a in r.html.find('.offer-details__title-link')[:-3] if a.absolute_links]
        for link in offers_links:
            offers_count += 1
            get_offer(link[0], link[1], offers_count)
        print(f'Przeszukałem {page}. stronę.', end=' ')

        # sprawdzenie, czy istnieje nastepna strona
        paginators = [li.text for li in r.html.find('.pagination_element-page')]
        if paginators and page < int(paginators[-1]):
            number_of_pages += 1
        page += 1
    print_result(page, offers_count)


def get_offer(offer_link, title, i):
    page_code = requests.get(offer_link).text
    soup = BeautifulSoup(page_code, 'html.parser')
    title = title.translate(str.maketrans(ltrPL, ltrnoPL)).replace('/', ' ').replace('\ '[0], ' ').replace('|', ' ')
    filename = f'{i}) {title.strip()}.html'
    offer_file = open(offers_dir + '/' + filename, 'w')
    offer_code = f"{soup.head.style}{soup.find(id='offCont')}"
    try:
        offer_file.write(offer_code)
    except UnicodeEncodeError:
        offer_file.write(str(offer_code.encode('utf8')))
    offer_file.close()


def print_result(p, o):
    p -= 1
    if p > 1:
        toprint = f'\n\nPrzeszukałem wszystkie {p} stron'
        if 1 < p % 10 < 5 and not 11 < p < 15:
            toprint += 'y'
        toprint += '.'
        print(toprint)
    if o > 1:
        toprint = f'Przygotowałem {o} ofert'
        if 1 < o % 10 < 5 and not 11 < o < 15:
            toprint += 'y'
        print(toprint + ". Znajdziesz je w folderze 'oferty'.")
    elif o == 1:
        print("Przygotowałem 1 ofertę. Znajdziesz ją w folderze 'oferty'.")
    else:
        print('Nie znaleziono ofert.')


if __name__ == '__main__':
    kw_input = input('Słowo kluczowe, stanowisko, firma: ')
    keyword = kw_input.strip().lower().translate(str.maketrans(ltrPL, ltrnoPL))

    loc_input = input('Województwo (domyślnie cała Polska): ')
    location = loc_input.strip().lower().translate(str.maketrans(ltrPL, ltrnoPL)) or 'cala polska'
    while location not in locations:
        print('Wprowadź poprawne województwo lub pozostaw puste pole aby wyświetlić ogłoszenia z całej Polski')
        location = input('Województwo (domyślnie cała Polska): ').strip().lower().translate(str.maketrans(ltrPL, ltrnoPL)) or 'cala polska'
    print()

    offers_dir = 'oferty/' + keyword + ' ' + location
    if os.path.exists(offers_dir):
        shutil.rmtree(offers_dir)
    os.makedirs(offers_dir)

    offers_spider(keyword, location)

    time.sleep(60)
