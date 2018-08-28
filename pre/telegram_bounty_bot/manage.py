from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
import config
from db import db

#setting up with sqlite
app = Flask(__name__)
app.config.from_object(config.ProductionConfig)

# add flask plugins here
db.app = app

db.init_app(app)
migrate = Migrate(app, db, directory=config.ProductionConfig.MIGRATION_DIR)

#manager manages all
manager = Manager(app)
manager.add_command('db', MigrateCommand)
def main():
    manager.run()

if __name__ == '__main__':
    main()