# -*- coding: utf-8 -*-
import os
from flask import Flask, Response
from flask import send_from_directory
from flask_cors import CORS
from flask_caching import Cache
# App
from app.utils.env_constants import ENV_CONTEXT, CACHE_IN_SECONDS
from app.utils import response_json
from app.modules.crawler import YahooStocks

if ENV_CONTEXT in os.environ:
    CACHE_IN_SECONDS = int(os.environ[CACHE_IN_SECONDS])
else:
    CACHE_IN_SECONDS = (60 * 3) + 13

# -------------------- #
# Flask Initialization #
# -------------------- #
conf = {
    "DEBUG": True,
    "CACHE_TYPE": "simple",
    "CACHE_DEFAULT_TIMEOUT": CACHE_IN_SECONDS
}

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_mapping(conf)
CORS(app, resources={r"/*": {"origins": "*"}})
cache = Cache(app)


# ---------- #
# Get Stocks #
# ---------- #
@app.route("/stocks-regions/", methods=["GET"])
@cache.cached()
def get_regions_list():
    return YahooStocks(None).get_regions_list()


@app.route("/stocks/<region>", methods=["GET"])
@cache.cached()
def get_stocks_by_region(region):
    return YahooStocks(region).get_stocks_by_region()


# ------------ #
# HEALTH CHECK #
# ------------ #
@app.route('/', methods=["GET"])
@app.route('/health', methods=["GET"])
def health():
    return Response({'ok': True}), 200


# -------- #
# Fav Icon #
# -------- #
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')


# -------------- #
# Error Handling #
# -------------- #
@app.errorhandler(404)
def page_not_found(e):
    error = {"error": 404, "message": str(e)}
    return response_json(error), 404


@app.errorhandler(500)
def internal_server_error(e):
    error = {"error": 500, "message": str(e)}
    return response_json(error), 500


if __name__ == "__main__":
    try:
        cache.init_app(app)
        app.run("0.0.0.0", port=5000)
    except Exception as ex:
        print(ex)
