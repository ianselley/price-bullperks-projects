from flask import Flask, request, jsonify
import os

from shared.sheets import SheetBot


app = Flask(__name__)

sheet_bot = SheetBot()
secret_key = os.getenv("SECRET_KEY")


@app.route("/updatePrices", methods=["GET"])
def update_prices():
    token = request.args.get("CLIENT_TOKEN")
    if token == secret_key:
        try:
            dict_of_prices = sheet_bot.update_sheet()
            sheet_bot.logger.log("Prices updated")
        except Exception as e:
            dict_of_prices = str(e)
            sheet_bot.logger.log(str(e))

        return jsonify({"response": dict_of_prices})
    else:
        return jsonify({"message": "Not Found"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
