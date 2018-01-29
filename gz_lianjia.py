import requests
from bs4 import BeautifulSoup
import csv

soup_cache = {}

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

def make_url(xiaoqu, district, criteria, page):
    dists = {
        # 'all': '',
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
    base_url = 'https://gz.lianjia.com/'
    base_url += 'xiaoqu/' if xiaoqu else 'zufang/'
    base_url += dists.get(district, '')
    if page != '1':
        base_url += criteria + 'pg' + page + '/'
    else:
        if criteria != '':
            base_url += criteria + '/'
    return base_url

def make_searching_criteria(xiaoqu, acceptable_year, area, room_number):
    years = {
        '<5': 'y1',
        '<10': 'y2',
        '<15': 'y3',
        '<20': 'y4',
        '>20': 'y5',
    }
    areas = {
        '80-100': 'ra4',
        '100-120': 'ra5',
        '120-144': 'ra6',
        '>144': 'ra7',
    }
    rooms = {
        '1': 'l1',
        '2': 'l2',
        '3': 'l3',
        '4': 'l4',
        '5': 'l5',
        '6': 'l6',
    }

    if xiaoqu:
        return years.get(acceptable_year, '')
    else:
        return areas.get(area, '') + rooms.get(room_number, '')

def get_max_page(url):
    soup = get_soup(url)
    page_info_s = soup.find('div', class_='page-box house-lst-page-box')['page-data']
    page_info = eval(page_info_s)
    return page_info['totalPage']

def get_house_list(url):
    soup = get_soup(url)
    div_tags = soup.find_all('div', class_='info-panel')
    houses = [get_house_from_info_panel_div(dt) for dt in div_tags]
    return houses

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

def get_xiaoqu_list(url):
    soup = get_soup(url)
    li_tags = soup.find_all('li', class_='clear xiaoquListItem')
    xiaoqu_list = [get_xiaoqu_from_li(lt) for lt in li_tags]
    return xiaoqu_list

def get_xiaoqu_from_li(tag):
    xiaoqu_attrs = {}
    xiaoqu_attrs['name'] = tag.find('div', class_='title').a.string
    xiaoqu_attrs['xiaoqu_url'] = tag.find('div', class_='title').a['href']
    xiaoqu_attrs['in_rent'] = tag.find('span', class_='cutLine').next_sibling.string
    if not xiaoqu_attrs['in_rent'].startswith('0'):
        xiaoqu_attrs['rent_url'] = tag.find('span', class_='cutLine').next_sibling['href']
    else:
        xiaoqu_attrs['rent_url'] = ''
    xiaoqu_attrs['region'] = tag.find('a', class_='district').string
    xiaoqu_attrs['region_url'] = tag.find('a', class_='district')['href']
    xiaoqu_attrs['sub_region'] = tag.find('a', class_='bizcircle').string
    xiaoqu_attrs['sub_region_url'] = tag.find('a', class_='bizcircle')['href']
    xiaoqu_attrs['trans'] = tag.find('div', class_='tagList').span.string if tag.find('div', class_='tagList').span else 'No Info'
    return xiaoqu_attrs

def save_to_csv(csvfile, results):
    # 'utf-8' encoding will cause error due to BOM, utf_8_sig is fine. Or with "csvfile.write(codecs.BOM_UTF8)"
    with open(csvfile, 'w', newline='', encoding='utf_8_sig') as cf:
        writer = csv.DictWriter(cf, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)

def collect_houses(district, bedrooms, csvfile):
    # process first page
    cr = make_searching_criteria(False, '', '100-120', bedrooms)
    start_url = make_url(False, district, cr, '1')
    houses = get_house_list(start_url)

    # get total page number from first page
    max_page = get_max_page(start_url)

    print('House Page [%s] got. 1/%s' % (start_url, max_page))

    # process left pages
    for i in range(2, int(max_page)+1):
        url = make_url(False, district, cr, str(i))
        houses += get_house_list(url)
        print('House Page [%s] got. %s/%s' % (url, i, max_page))

    save_to_csv(csvfile, houses)
    print('All %s bedrooms houses in %s are save.' % (bedrooms, district))

def collect_xiaoqu(district, csvfile, year):
    cr = make_searching_criteria(True, year, '', '')
    start_url = make_url(True, district, cr, '1')
    xiaoqu_list = get_xiaoqu_list(start_url)

    max_page = get_max_page(start_url)
    print('Xiaoqu Page [%s] got. 1/%s' % (start_url, max_page))

    for i in range(2, int(max_page)+1):
        url = make_url(True, district, cr, str(i))
        xiaoqu_list += get_xiaoqu_list(url)
        print('Xiaoqu Page [%s] got. %s/%s' % (url, i, max_page))

    save_to_csv(csvfile, xiaoqu_list)
    print('Xiaoqu got and saved.')

def main():
    collect_houses('tianhe', '3', 'tianhe_3_bedrooms.csv')
    collect_xiaoqu('tianhe', 'tianhe_xiaoqu_2008.csv', '<10')


if __name__ == '__main__':
    main()
