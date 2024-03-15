import requests
import csv
from time import sleep
from datetime import datetime
from config import CRYPTO_CURRENCY, FIAT_CURRENCY, STAKING_CSV_FILE, OUTPUT_CSV_FILE, WAITING_TIME


def get_historical_rates(crypto, fiat, date):
    url = f'https://api.coingecko.com/api/v3/coins/{crypto}/history'
    params = {'date': date, 'localization': 'false'}
    response = requests.get(url, params=params)
    data = response.json()
    try:
        return data['market_data']['current_price'][fiat]
    except:
        print(data)


def csv_reader(file):
    csv_array = []
    with open(file) as csvfile:
        csv_reader_object = csv.reader(csvfile, delimiter=',')
        for row in csv_reader_object:
            csv_array.append(row)
        return csv_array


def csv_writer(fields, array):
    with open(OUTPUT_CSV_FILE, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)
        csvwriter.writerows(array)


def convert_date(date):
    input_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    input_date = datetime.strptime(date, input_format)
    output_format = "%d-%m-%Y"
    output_date = input_date.strftime(output_format)
    return output_date


def calculate_fiat_price(crypto, rate):
    fiat = crypto * rate
    return fiat


stake_array = csv_reader(STAKING_CSV_FILE)
output_array = []

for index, row in enumerate(stake_array):
    totalRows = len(stake_array)
    if row[0] == 'mint':
        date = convert_date(row[3])
        rate = get_historical_rates(CRYPTO_CURRENCY, FIAT_CURRENCY, date)
        output_array.append([date, row[1], rate, calculate_fiat_price(float(row[1]), rate)])
        print(str(index) + " of " + str(totalRows) + " rows. Remaining time: " +
              str(round((totalRows - index) / 2 * WAITING_TIME / 60, 1)) + " minutes")
        print(output_array[-1])
        # waiting time so that not too many api requests are sent per minute. (Maximum 5 per minute)
        sleep(WAITING_TIME)

csv_writer(['date', 'VRSC', 'rate', 'EUR'], output_array)