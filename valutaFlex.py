import requests
from requests.exceptions import ConnectionError
import os
import sys
import time
import datetime
import pprint
from bs4 import BeautifulSoup
from typing import Union,List


class ValutaFlex():
    def __init__(self):
        self.valute = None
        self.IMPOSTA_VALUTE()

    
    def IMPOSTA_VALUTE(self):
        try :
            target = [
                'XOF','XAF','USD','CAD','CDF','CHF','EGP','DZD',
                'GBP','GMD','GNF','JPY','KMF','LBP','MAD','ZWL','EUR'
                ]
            link = 'http://currencylayer.com/currencies'
            respons = requests.get(link)
            #ottiene le valute disponibili presenti nella tabella
            table = BeautifulSoup(respons.content,'html.parser')
            rows = [row.find_all('td') for row in table.find_all('tr')]
            column0 = [i[0].get_text() for i in rows if i!=[] and ''.join(i[0].get_text()) in target ]
            column1 = [i[1].get_text() for i in rows if i !=[] and ''.join(i[0].get_text()) in target]
            # print(sorted(list(zip(column0,column1))))
            self.valute = dict(list(zip(column0,column1)))
            return {'STATUS':True}
        except ConnectionError as e:
            return {'STATUS':False}
        except requests.exceptions.ReadTimeout:
            return False

    def GET_CURRNCIES(self):
        return self.valute
    
    def converti(self,From:str,to:str,value:Union[float,int]=None):
        try:
            #fai una request
            base_url = 'http://api.currencylayer.com/'
            api_end = f'convert?access_key=52056f2e1d87e8bc1ffbed1383d76c4d&from={From}&to={to}&amount={value}'
            send_req = requests.get(base_url+api_end)
            respons = send_req.json()
            return [respons['result'],respons['success']]
            
           
        except ConnectionError as e:
            return False
        except requests.exceptions.ReadTimeout:
            return False

        


# obj = ValutaFlex()
# print(obj.converti('USD','EUR',200))
