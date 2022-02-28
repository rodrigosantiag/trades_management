from serpens import envvars

APPNAME = "trades-management"
VERSION = "0.1.0"

DATABASE_URL = envvars.get("DATABASE_URL")
