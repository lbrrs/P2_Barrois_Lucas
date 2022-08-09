import requests
from bs4 import BeautifulSoup
import csv
import re
import urllib.request


def extract_category_data(url):
    reponse = requests.get(url)
    soup = BeautifulSoup(reponse.content, 'html.parser')

    category = soup.find("ul", class_='nav')

    extract_category = dict()

    for link in category.findAll('a'):
        tmp = link.get('href').replace('catalogue/category/books/', '')
        tmp = tmp.replace('/index.html', '')
        tmp = re.sub('_\w*', '', tmp)
        if tmp != 'catalogue/category/books':
            extract_category[tmp] = 'http://books.toscrape.com/' + link.get('href')
        '''
        if len(extract_category) >= 2:
            break
        '''

    print(extract_category)

    return extract_category


def extract_book_link(data):
    print("=========================")
    p = dict()
    for key, links in data.items():
        p[key] = list()
        reponse = requests.get(links)
        soup = BeautifulSoup(reponse.content, 'html.parser')
        for link in soup.findAll('h3'):
            link = link.next
            l = link.attrs['href']
            '''print('http://books.toscrape.com/catalogue/' + l.replace('../', ''))'''
            p[key].append('http://books.toscrape.com/catalogue/' + l.replace('../', ''))

    return p


def extract_book_data(book):
    book_data = dict()

    for key, links in book.items():
        book_data[key] = list()
        for link in links:

            reponse = requests.get(link)
            soup = BeautifulSoup(reponse.content, 'html.parser')

            title = soup.title.string.strip()
            img = soup.img
            image_link = img["src"].replace('../../', 'http://books.toscrape.com/')
            price = soup.find("p", class_="price_color").text[1:]
            stock = soup.find("p", class_="instock").text.strip()

            th = soup.find_all("th")
            th_textes = []
            for characteristic in th:
                th_textes.append(characteristic.string)

            td = soup.find_all("td")
            td_textes = []
            for data in td:
                td_textes.append(data.string)

            stars = soup.find("p", class_="Three")

            description = soup.find_all("p")
            p_texte = []
            for texte in description:
                p_texte.append(texte.string)

            universal_product_code = td_textes[0]

            price_including_tax = td_textes[2]
            price_excluding_tax = td_textes[3]
            number_available = td_textes[5]
            '''
            print(title)
            print(img["src"].replace('../../', 'http://books.toscrape.com/'))
            print(price)
            print(stock)
            print(th_textes)
            print(td_textes)
            print(stars)
            print(p_texte[3])
            '''
            if price_excluding_tax is not None:
                price_excluding_tax = str(price_excluding_tax)
            if stars is not None:
                stars = stars.attrs['class'][1]
            if p_texte[3] is None:
                p_texte[3] = ""
            if stars is None:
                stars = "No review"
            book_data[key].append(
                [key, link, title, image_link, price_including_tax, price_excluding_tax, stock, p_texte[3],
                 stars, universal_product_code])

    return book_data


#download image from url
def download_image(image_link, filename):
    name = "./images" + str(filename)
    image_url = image_link
    if name.find(".jpg") == -1:
        name = name + ".jpg"
# calling urlretrieve function to get resource
    urllib.request.urlretrieve(image_url, name)



def main(book_data):
    # boucle cat
    filename = 1
    for b in book_data:
        key = b
        csvfile = open(f"./csv/{key}.csv", 'w', encoding='UTF8', newline='')
        header = ['category', 'product_page_url', 'title', 'image_url', 'price_including_tax',
                  'price_excluding_tax',
                  'number_available', 'product_description', 'review_rating', 'universal_product_code']
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(header)

        for links in book_data[b]:
            csv_writer.writerow(links)
            download_image(links[3], filename)
            filename += 1


url = "http://books.toscrape.com/index.html"
url_category = "http://books.toscrape.com/catalogue/category/books_1/index.html"
book = 'http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'

data = extract_category_data(url)
url_book = extract_book_link(data)
book_data = extract_book_data(url_book)
main(book_data)
