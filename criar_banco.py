from app_imediagram import database, app

with app.app_context():
    database.create_all()