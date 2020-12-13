import pandas as pd
from bs4 import BeautifulSoup
import requests


def get_mid_data(data, feat, feat_idx, uiks, k, tds, idx):
    
    while feat_idx < len(feat):
        for i in range(len(uiks)):
            nobrs = tds[idx + i].find_all('nobr')[0].b
            if k == 'u':
                data[i][feat[feat_idx]] = int(nobrs.contents[0])
            else:
                data[i][feat_idx] = int(nobrs.contents[0])
        
        idx += len(uiks)
        feat_idx += 1
        
    return data, idx
        
                
def get_names(start, end, data, tds):
    
    for td in tds[start:end:3]:
        nobr = td.find_all('nobr')[0]
        data.append(nobr.contents[0])
    
    return data
    
        
def get_elections_data():
    
    path = 'http://notelections.online/region/region/st-petersburg?action=show&root=1&tvd=27820001217417&vrn=27820001217413&region=78&global=&sub_region=78&prver=0&pronetvd=null&vibid=27820001217417&type=222'
    request = requests.get(path)
    
    request = request.content.strip()
    tiks = BeautifulSoup(request, 'html.parser').find_all('a')[8:-3]

    tik_urls = {}
    base_url = 'http://notelections.online'
    
    # get tiks urls
    for tik in tiks:
        tik_name = tik.contents[0]
        tik_url = f"{base_url}{tik.get('href')}"
        tik_urls[tik_name] = tik_url

    data = []


    for tik_name, tik_url in tik_urls.items():
        
        if tik_name == "Цифровые избирательные участки":
            break
            
        # get tik data
        request = requests.get(tik_url)
        
        request = request.content.strip()
        tds = BeautifulSoup(request, 'html.parser').find_all('td')[19:]
        
        # get fields names
        fields = []
        fields = get_names(1, 32, fields, tds)

        # get candidates names
        candidates = []
        candidates = get_names(36, 44, candidates, tds)
        
        # get uiks names
        idx = 45
        uiks_names = []
        a = [0]
        while len(a) == 1:
            a = tds[idx].find_all('nobr')[0].find_all('a')

            if len(a) == 1:
                uiks_names.append(a[0].contents[0])
                idx += 1


        # get uiks data
        uiks_data = [{} for _ in range(len(uiks_names))]
        field_idx = 0
        uiks_data, idx = get_mid_data(uiks_data, fields, field_idx, uiks_names, 'u', tds, idx)
        
        idx += 2
        
        # get candidates data
        candidates_data = [[0 for _ in range(len(candidates))] for _ in range(len(uiks_names))]
        candidate_idx = 0
        candidates_data, idx = get_mid_data(candidates_data, candidates, candidate_idx, uiks_names, '', tds, idx)

        # get our data
        for i in range(len(uiks_names)):
            
            data.append({'tik': tik_name,
                         'uik': uiks_names[i]})
            
            data[-1].update({fields[j]: uiks_data[i][fields[j]]
                             for j in range(len(fields))})
            
            data[-1].update({candidates[j]: candidates_data[i][j]
                             for j in range(len(candidates))})
            
    df = pd.DataFrame(data)
    df.to_csv('data.csv', index=False)


get_elections_data()