from fastapi import FastAPI
import os
import traceback

from app.sheets import SheetBot

app = FastAPI()

sheet_bot = SheetBot()
secret_key = os.getenv("SECRET_KEY")


@app.get("/updatePrices")
def update_prices(CLIENT_TOKEN: str = ""):
    if CLIENT_TOKEN == secret_key:
        try:
            response = sheet_bot.update_sheet()
            sheet_bot.logger.log("Prices updated")
        except Exception as e:
            print(traceback.format_exc())
            response = str(e)
            sheet_bot.logger.log(response)

        return {"response": response}
    else:
        return {"message": "Not Found"}

