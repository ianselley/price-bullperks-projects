import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from datetime import datetime
import os
from abc import ABC, abstractmethod


class ConnectSheet:

    def __init__(self):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
        self.client = gspread.authorize(creds)

    def get_sheet(self, id: int=0, sheet_name: str="BullPerks"):
        sheet = self.client.open(sheet_name).get_worksheet(id)
        return sheet


class Logger:

    def __init__(self):
        self.sheet = ConnectSheet().get_sheet(1)
        self.sheet_data = self.sheet.get_all_values()

    
    def update_sheet(self, message):
        self.sheet_data.insert(0, [message])
        self.sheet.update("A1", self.sheet_data)


    def log(self, message: str):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"[{now}] => {message}"
        self.update_sheet(message)
        print("\n" + message + "\n")


class Exchange(ABC):

    @abstractmethod
    def get_prices(self):
        pass

    @abstractmethod
    def add_prices_to(self, slugs: dict[str]):
        pass


class CoinMarketCap(Exchange):

    def __init__(self):
        self.url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
        self.headers = {
            'Accepts': 'application/json',
            "X-CMC_PRO_API_KEY": os.getenv("COINMARKETCAP_API_KEY"),
        }


    def fetch_api(self, slugs: dict[str]):
        parameters = {
            "slug": ",".join(slugs),
            "convert": "USD",
            "skip_invalid": True,
        }
        response = requests.get(self.url, params=parameters, headers=self.headers)
        return response.json()


    def get_prices(self, slugs: dict[str]):
        response_json = self.fetch_api(slugs)
        status = response_json["status"]

        while status["error_code"] != 0:
            slug_to_remove = status["error_message"].split('"')[-2]
            del slugs[slug_to_remove]
            response_json = self.fetch_api(slugs)
            status = response_json["status"]

        return response_json


    def add_prices_to(self, slugs: dict[str]):
        response_json = self.get_prices(slugs)
        for coin_data in response_json["data"].values():
            slugs[coin_data["slug"]]["price"] = f'{coin_data["quote"]["USD"]["price"]:,}'

        return slugs


class CoinGecko(Exchange):

    def __init__(self):
        self.url = "https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
        self.headers = {"Accept": "application/json"}


    def get_prices(self, ids: str):
        url = self.url.format(ids=ids)
        response = requests.get(url, headers=self.headers)
        return response.json()


    def add_prices_to(self, slugs: dict[str]):
        response_json = self.get_prices(",".join(slugs.keys()))
        for slug, data in response_json.items():
            slugs[slug]["price"] = f'{data["usd"]:,}'

        return slugs


class SheetBot:

    def __init__(self, exchange: Exchange=CoinGecko(), logger=Logger(), sheet_connector=ConnectSheet):
        self.exchange = exchange
        self.logger = logger
        self.sheet_connector = sheet_connector


    def parse_slug(self, project: str):
        try:
            return project.strip().split(" ")[0]
        except Exception as e:
            self.logger.log(str(e))


    def get_slugs_with_position(self) -> dict[str, dict[str, int]]:
        current_row = self.project_coordinates.row
        slugs = {}

        while self.sheet_data[current_row][self.project_coordinates.col - 1] != "":
            project = self.sheet_data[current_row][self.project_coordinates.col - 1]
            slug = self.parse_slug(project)
            current_row += 1
            slugs[slug.lower()] = {"row": current_row, "col": self.price_coordinates.col}

        return slugs


    def get_slugs(self) -> str:
        slugs_position = self.get_slugs_with_position()
        return ",".join(slugs_position.keys())


    def place_prices(self, slugs: dict[str]):
        for data in slugs.values():
            self.sheet.update_cell(data["row"], data["col"], data.get("price"))


    def check_column_and_price_row(self):
        if self.project_coordinates.row != self.price_coordinates.row:
            error = "'Precio actual' y 'Projecto' no están en la misma fila"
            self.logger.log(error)
            raise Exception(error)


    def update_sheet(self):
        self.sheet = self.sheet_connector().get_sheet()
        self.sheet_data = self.sheet.get_all_values()
        self.project_coordinates = self.sheet.find("Proyecto")
        self.price_coordinates = self.sheet.find("Precio actual")

        self.check_column_and_price_row()

        slugs_position = self.get_slugs_with_position()
        slug_prices = self.exchange.add_prices_to(slugs_position)

        self.place_prices(slug_prices)

        return {slug: data.get("price") for slug, data in slug_prices.items()}
        