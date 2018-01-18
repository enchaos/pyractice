import requests
from bs4 import BeautifulSoup
import csv

soup_cache = {}
header_flag = False

def get_soup(url):
    global soup_cache
    if url not in soup_cache:
        proxies = {
            "http": "http://proxyserver:8080/",
            "https": "http://proxyserver:8080/",
        }
        r = requests.get(url, proxies=proxies)
        soup = BeautifulSoup(r.text, 'lxml')
        soup_cache[url] = soup

    return soup_cache[url]


def make_url(district='all', room='all', page='1'):

    dists = {
        'all': '',
        'tianhe': 'tianhe/',
        'yuexiu': 'yuexiu/',
        'liwan': 'liwan/',
        'haizhu': 'haizhu/',
        'panyu': 'panyu/',
        'baiyun': 'baiyun/',
        'huangpu': 'huangpugz/',
        'conghua': 'conghua/',
        'zengcheng': 'zengcheng/',
        'huadu': 'huadu/',
        'nansha': 'nansha/',
    }

    rooms = {
        'all': '',
        '1': 'l1/',
        '2': 'l2/',
        '3': 'l3/',
        '4': 'l4/',
        '5': 'l5/',
        '6': 'l6/',
    }
    return 'https://gz.lianjia.com/zufang/%s%s%s' % (dists.get(district, ''), '' if page == '1' else 'pg' + page ,rooms.get(room, ''))


def get_house_list(page_url):
    soup = get_soup(page_url)
    div_tags = soup.find_all('div', class_='info-panel')
    houses = [get_house_from_info_panel_div(dt) for dt in div_tags]
    return houses

def get_max_page(page_url):
    soup = get_soup(page_url)
    page_info_s = soup.find('div', class_='page-box house-lst-page-box')['page-data']
    page_info = eval(page_info_s)
    return page_info['totalPage']

def get_house_from_info_panel_div(tag):
    house_attrs = {}
    house_attrs['code'] = tag.parent['data-id']
    house_attrs['abs_url'] = tag.h2.a['href']
    house_attrs['intro'] = tag.h2.a.string
    house_attrs['xiaoqu'] = tag.find('a', class_='laisuzhou').span.string.strip()
    house_attrs['xiaoqu_url'] = tag.find('a', class_='laisuzhou')['href']
    house_attrs['zone'] = tag.find('span', class_='zone').span.string.strip()
    house_attrs['meters'] = tag.find('span', class_='meters').string.strip()
    house_attrs['towards'] = tag.find('span', class_='meters').next_sibling.string

    house_attrs['region'] = tag.find('div', class_='con').a.string
    house_attrs['region_url'] = tag.find('div', class_='con').a['href']
    house_attrs['floor'] = tag.find('div', class_='con').contents[2]
    house_attrs['year'] = tag.find('div', class_='con').contents[4] if len(tag.find('div', class_='con').contents) > 4 else 'no'
    house_attrs['trans'] = tag.find('span', class_='fang-subway-ex').span.string.strip() if tag.find('span', class_='fang-subway-ex') else 'none'
    house_attrs['haskey-ex'] = tag.find('span', class_='haskey-ex').span.string.strip() if tag.find('span', class_='haskey-ex') else 'none'
    house_attrs['decoration-ex'] = tag.find('span', class_='decoration-ex').span.string.strip() if tag.find('span', class_='decoration-ex') else '一般装修'
    house_attrs['price'] = tag.find('div', class_='price').span.string.strip()
    house_attrs['price_update'] = tag.find('div', class_='price-pre').string.strip()
    house_attrs['visited_total'] = tag.find('div', class_='square').div.span.string.strip()
    return house_attrs

def get_and_save(url, csvfile):
    houses = get_house_list(url)
    # 'utf-8' encoding will cause error due to BOM, utf_8_sig is fine. Or with "csvfile.write(codecs.BOM_UTF8)"
    with open(csvfile, 'a', newline='', encoding='utf_8_sig') as cf:
        fieldnames = ['code', 'abs_url', 'intro', 'xiaoqu', 'xiaoqu_url', 'zone', 'meters', 'towards', 'region', 'region_url', 'floor', 'year', 'trans', 'haskey-ex', 'decoration-ex', 'price', 'price_update', 'visited_total']
        writer = csv.DictWriter(cf, fieldnames=fieldnames)
        global header_flag
        if not header_flag:
             writer.writeheader()
             header_flag = True
        writer.writerows(houses)


def process(district, bedrooms, csvfile):
    # process first page
    start_url = make_url(district, bedrooms, '1')
    get_and_save(start_url, csvfile)

    # get total page number from first page
    max_page = get_max_page(start_url)

    print('Page [%s] got and saved. 1/%s' % (start_url, max_page))

    # process left pages
    for i in range(2, int(max_page)+1):
        url = make_url(district, bedrooms, str(i))
        get_and_save(url, csvfile)
        print('Page [%s] got and saved. %s/%s' % (url, i, max_page))

    print('All %s bedrooms houses in %s are save.' % (bedrooms, district))


def main():
    # process('yuexiu', '2', 'gz.csv')
    # process('yuexiu', '3', 'gz.csv')
    # process('haizhu', '2', 'gz.csv')
    # process('haizhu', '3', 'gz.csv')
    # process('tianhe', '2', 'gz.csv')
    process('tianhe', '3', 'gz.csv')


if __name__ == '__main__':
    main()
