from dotenv import dotenv_values

config = dotenv_values("./config/.env")


IS_DEV = bool(int(config.get("IS_DEV", "0")))

DB_HOST = config["DB_HOST"]
DB_NAME = config["DB_NAME"]
DB_USER = config["DB_USER"]
DB_PASSWORD = config["DB_PASSWORD"]

WEB_SERVER_PORT = int(config["WEB_SERVER_PORT"])

WEB_SERVER_SECRET = config["WEB_SERVER_SECRET"]
