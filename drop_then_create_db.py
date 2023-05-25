from project import db, create_app

if __name__ == '__main__':
  app = create_app()
  with app.app_context():
    db.drop_all()
    db.create_all()