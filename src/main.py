
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import requests, json
from jsonpath import *
import time

def extract_page(url):
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--start-maximized')  # 浏览器最大化
    chrome_options.add_argument('--no-sandbox')

    wd = webdriver.Chrome(r'C:\Tools\Webdriver\chromedriver.exe', chrome_options=chrome_options)


    wd.get(url)
        
    # wd.find_element(By.XPATH, '//*[@id="show-more-btn"]/span').click()
    records = {}
    records['author_first'] = wd.find_element(By.XPATH, '//*[@id="author-group"]/a[1]').text
    records['author_corres'] = wd.find_element(By.XPATH, '//*[@id="author-group"]/a[2]').text
    records['title'] = wd.find_element(By.XPATH, '//*[@id="screen-reader-main-title"]/span').text
    records['pub_time'] = wd.find_element(By.XPATH, '//*[@id="publication-title"]/a').text
    records['journal'] = wd.find_element(By.XPATH, '//*[@id="publication-title"]/a').text
    records['abstract'] = wd.find_element(By.XPATH, '//*[@id="as005"]').text
    
    # Cited by (XX)
    records['cited'] = (wd.find_element(By.XPATH, '//*[@id="citing-articles-header"]/h2').text).isdigit()
    
    # records['source'] = wd.find_element(By.XPATH, '//*[@id="author-group"]/dl/dd').text

    return records

# connected with notion and read Database
def notion_readDatabase(databaseID, headers):
    readurl = f"https://api.notion.com/v1/databases/{databaseID}/query"
    res = requests.request("POST", readurl, headers=headers)
    # Alarm
    if res.status_code == 200:
        print('connect success')
    else:
        print(res)
    
    data=res.json()
    
    with open('./db.json', 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False)
    

def notion_get_target(target):
    with open('./db.json','r',encoding='utf8')as fp:
        data = json.load(fp)

    # Statistics
    pgsID = jsonpath(data, '$.results.*.id')
    # print(pgsID)

    target_list = []
    
    for it in range(len(pgsID)):
        key = jsonpath(data, f"$.results[{it}]..properties.doi.rich_text..text.content")
        # print(key)
        # If not find return False
        if key:
            target_dict = {}
            target_dict['doi'] = key
            target_dict['id'] = pgsID[it]
            target_list.append(target_dict)
            
    # print(target_list)
    return target_list


# %% [markdown]
# body = {
#      'properties':{
#           '我是number（这里对应你database的属性名称）':{'type': 'number', 'number': int(数据)},
#           '我是title':{
#                 'id': 'title', 'type': 'title', 
#                 'title': [{'type': 'text', 'text': {'content': str(数据)}, 'plain_text': str(数据)}]
#             },
#           '我是select': {'type': 'select', 'select': {'name': str(数据)}},
#           '我是date': {'type': 'date', 'date': {'start': str(数据), 'end': None}},
#           '我是Text': {'type': 'rich_text', 'rich_text': [{'type': 'text', 'text': {'content': str(数据)},  'plain_text': str(数据)}]},
#           '我是multi_select': {'type': 'multi_select', 'multi_select': [{'name': str(数据)}, {'name': str(数据)}]}
#           '我是checkbox':{'type': 'checkbox', 'checkbox': bool(数据)}
#      }
# }


def notion_update(pageID, headers, update_data, dataType, prName='title'):
    print('entre success')

    updateurl = f"https://api.notion.com/v1/pages/{pageID}"

    if dataType is 'title':
        body = {
        'properties':{
            f'{prName}':{
                'id': 'title', 'type': 'title', 
                'title': [{'type': 'text', 'text': {'content': f'{update_data}'}, 'plain_text': f'{update_data}'}]
                }
            }
        }
    
    elif dataType is 'date':
        body = {
        'properties':{
            f'{prName}':{
                'type': 'date', 'date': {'start': f'{update_data}', 'end': None}
                }
            }
        }
    elif dataType is 'select':
        body = {
        'properties':{
            f'{prName}':{
                'type': 'select', 'select': {'name': f'{update_data}'}
                }
            }
        }
    elif dataType is 'text':
        body = {
        'properties':{
            f'{prName}': {
                'type': 'rich_text', 
                'rich_text': [{'type': 'text', 'text': {'content': f'{update_data}'}, 'plain_text': f'{update_data}'}]
                }
            }
        }
    elif dataType is 'multi_select':
        body = {
        'properties':{
            f'{prName}': {
                'type': 'multi_select', 'multi_select': [{'name': f'{update_data}'}, {'name': f'{update_data}'}]
                }
            }
        }
    elif dataType is 'number':
        body = {
        'properties':{
             f'{prName}': {
                'type': 'number', 'number': f'{update_data}'
                }
            }
        }
    elif dataType is 'checkbox':
        body = {
        'properties':{
            f'{prName}':{
                'type': 'checkbox', 'checkbox': f'{update_data}' # bool型
                }
            }
        }
    res = requests.request("PATCH", updateurl, headers=headers, json=body)

    # Alarm
    if res.status_code == 200:
        print('update success')
    else:
        print(res)
    

def notion_read_doi(databaseID, headers):
    readurl = f"https://api.notion.com/v1/databases/{databaseID}/query"
    res = requests.request("POST", readurl, headers=headers)
    if res.status_code == 200:
        print('connect success')
    else:
        print('ERROR! '+ res.text())
    data = []
    json.dump(res.json(), data, ensure_ascii=False)
    values = data['results']['properties']['doi']
    print(values)

def str_list(list):
    string = str(list)[2:-2]
    return string

# %% [markdown]
# token:secret_i3GD70ce5R0G4Pm18dIGGUi2yH6zXqgJuyigCnjy5j5

# %%
# parameters
doi = 'https://doi.org/10.1016/j.seta.2022.102102'

token = 'secret_i3GD70ce5R0G4Pm18dIGGUi2yH6zXqgJuyigCnjy5j5'

databaseID = '798067dde4c643adb0fc9e3b63b8f8a4'

testdbID = '222bdad0c90d4f228ca81df2a66a45be'
testpgID = '54b2f836-34bb-4c1f-9245-d9cc5af2a2f9'

headers = {
    "Authorization": "Bearer " + token,
    "Notion-Version": "2022-02-22",
    "Accept": "application/json",
    "Content-Type": "application/json",
}
target_name = 'doi'

# %%
if __name__=='__main__':
    # Step 1 Connect DataBase
    notion_readDatabase(testdbID, headers)
    
    DBlist = notion_get_target(target_name)

    # Step 2 Extract Info and Update
    num = 0
    for it in DBlist:
        # Navigate through doi
        it_doi = str_list(it['doi'])
        records = extract_page(it_doi)
        it_title = str(records['title'])
        it_pgID = str(it['id'])
        
        notion_update(it_pgID, headers, it_title, 'title')
        time.sleep(3)
    





