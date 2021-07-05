from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import NLP


driver = webdriver.Chrome('C:\Program Files (x86)\chromedriver.exe')
pre = 'https://en.wikipedia.org'

ROOT = '/wiki/France'

def element_exists(elem, tag):
    try:
        elem.find_element_by_tag_name(tag)
    except NoSuchElementException:
        return False
    return True

def crawl(depth, page=ROOT):
    nodes_dict = dict()
    a_tags = list()
    href_dict = dict()
    predicted_objs = list()
    first_paragraph = None
    cur_page = page
    for i in range(depth):
        driver.get(pre + cur_page)
        paragraphs = driver.find_elements_by_tag_name('p')

        for paragraph in paragraphs:
            if element_exists(paragraph, 'b'):
                first_paragraph = paragraph
                break

        if first_paragraph == None or not element_exists(first_paragraph, 'a'):
            print('REACHED TERMINAL PAGE')
            return None

        predicted_objs = NLP.parse_clause(first_paragraph.text)[2]

        a_tags = first_paragraph.find_elements_by_tag_name('a')
        for a_tag in a_tags:
            # print(a_tag.text)
            cur_href = a_tag.get_attribute('href')
            if 'cite' not in cur_href:
                href_dict[a_tag.text] = cur_href

        data = list()
        for a_txt in href_dict:
            for obj in predicted_objs:
                if obj.lower() in a_txt.lower() or a_txt.lower() in obj.lower():
                    href_txt = href_dict[a_txt]
                    data.append(href_txt[href_txt.find('g/')+1:])

        nodes_dict[cur_page] = data
        cur_page = data[0]

    return nodes_dict

def close_driver():
    driver.quit()