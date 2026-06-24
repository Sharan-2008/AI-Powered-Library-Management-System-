import mysql.connector
import matplotlib.pyplot as plt

# Connect to the database
conn = mysql.connector.connect(
    host='localhost',
    user='root',     
    password='p@ssword'  
)

import db
import cli


def run():
    db.init_db()
    cli.main()


if __name__ == "__main__":
    run()