import pandas as pd
import gspread


class GoogleConnection:

    def __init__(self):
        self.SHEET_ID = '1VUP_vAtZeFFqNCMwgWZVS8KJhHW0J79u1fYLVFjFiqw'

    def open_spreadsheet(self, sample_spreadsheet_id: str):
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        gc = gspread.service_account('KanalServiceGoogle.json', scopes)

        gc = gc.open_by_key(sample_spreadsheet_id)
        return gc

    def read_sheet(self, sheet_name):
        """

        :param sheet_id: ID таблицы в Google
        :param sheet_name: Название листа в таблице
        :return:
        """
        gc = self.open_spreadsheet(self.SHEET_ID)
        values = gc.worksheet(sheet_name).get_all_values()

        df = pd.DataFrame(values)
        df.columns = df.iloc[0]
        df.drop(df.index[0], inplace=True)
        df['стоимость,$'] = df['стоимость,$'].astype(int)

        return df

