from datetime import datetime, timedelta, date
from data_collector.google_connection import GoogleConnection
from data_collector.central_bank import CentralBank
import time
from sqlalchemy import create_engine, inspect
import pandas as pd
from telebot import TeleBot

BOT_TOKEN = '5232297700:AAH_xfABa7PHL4WDgRytlhERBJYAXeNsbgE'

google_client = GoogleConnection()
CB_client = CentralBank()
bot = TeleBot(BOT_TOKEN)


def update_df(base_df: pd.DataFrame, new_df: pd.DataFrame) -> pd.DataFrame:
    """
    Function for updating data in dataframe from sql
    :param base_df: pd.DataFrame from SQL
    :param new_df: pd.DataFrame from google
    :return: updated DataFrame
    """
    columns = ['№', 'заказ №', 'стоимость,$', 'стоимость в руб.', 'срок поставки']
    for order in base_df['заказ №'].values:
        if order not in new_df['заказ №'].values:
            base_df.drop(base_df.loc[base_df['заказ №'] == order].index, inplace=True)
    for values in new_df[columns].values:
        order_id = values[1]
        if order_id not in base_df['заказ №'].values:
            base_df = pd.concat([base_df, pd.DataFrame([values], columns=columns)], )
        else:
            base_df.loc[base_df['заказ №'] == order_id, columns] = values
    return base_df


prev_update = datetime.now() - timedelta(minutes=2)
if __name__ == '__main__':
    while True:
        if datetime.now() - prev_update > timedelta(minutes=1):
            engine = create_engine('postgresql://alex:kanalservice@postgresbd:5432/kanalservicedb')
            inspector = inspect(engine)
            # read SQL
            tables = inspector.get_table_names()
            print(tables)
            if 'orders' in tables:
                with engine.connect() as connection:
                    base_df = pd.read_sql_table('orders', connection)
            else:
                base_df = None

            # read Google table
            df = google_client.read_sheet('KanalSevice')
            USD_value = CB_client.USDRUB_value()
            df['стоимость в руб.'] = list(map(lambda x: round(x, 2), df['стоимость,$'] * USD_value))

            # update pandas dataframe
            if base_df is None:
                base_df = df
            else:
                base_df = update_df(base_df, df)
            if 'уведомление отправлено' not in base_df.columns.values:
                base_df['уведомление отправлено'] = None

            # send messages
            updates = bot.get_updates()
            users = set([update.message.from_user.id for update in updates])
            for [order_id, delivery_date, message_sent] in base_df[
                ['заказ №', 'срок поставки', 'уведомление отправлено']].values:
                [day, month, year] = map(int, delivery_date.split('.'))
                delivery_date = date(year, month, day)
                if datetime.now().date() > delivery_date and (message_sent is None or pd.isna(message_sent)):
                    base_df.loc[
                        base_df['заказ №'] == order_id, 'уведомление отправлено'] = datetime.now().date().isoformat()
                    for user in users:
                        bot.send_message(user, f'Прошел срок доставки по заказу {order_id}, '
                                               f'Срок доставки {delivery_date.isoformat()}')

            # update SQLBase
            with engine.begin() as connection:
                base_df.to_sql('orders', connection, index=False, if_exists='replace')
                print('updated')
            prev_update = datetime.now()
            print('-------------------------')

        time.sleep(30)
