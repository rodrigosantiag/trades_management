import os

from serpens import testgres

from entities import db


testgres.setup(db)

os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
