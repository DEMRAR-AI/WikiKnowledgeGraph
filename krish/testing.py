from selenium import webdriver
import NLP


driver = webdriver.Chrome('C:\Program Files (x86)\chromedriver.exe')
pre = 'https://en.wikipedia.org'

ROOT = '/wiki/Horse'

driver.get(pre+ROOT)
fp = None


for p in driver.find_elements_by_tag_name('p'):
    try:
        p.find_element_by_tag_name('b')
        fp = p
        break
    except:
        continue


a_tags = fp.find_elements_by_tag_name('a')
for a in a_tags:
    for obj in NLP.parse_clause(fp.text)[2]:
        if a.text.lower() in obj.lower() or obj.lower() in a.text.lower():
            print(obj, ", ", a.text)