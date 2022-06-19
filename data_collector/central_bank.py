import requests
from lxml import etree as ET


class CentralBank:

    def USDRUB_value(self, date_req: str = None) -> float:
        """
        :param date_req: date like 02/03/2002 Optional
        :return:
        """
        method_url = 'http://www.cbr.ru/scripts/XML_daily.asp'
        params = {}
        if date_req:
            params['date_req'] = date_req

        response = requests.get(method_url,
                                params=params)
        tree = ET.fromstring(response.content)
        value = float(tree.find('Valute[@ID="R01235"]').find('Value').text.replace(',', '.'))
        return value
