from project import db, create_app
from project.models import User

def assign_role(email, role):
    user = User.query.filter_by(email=email).first()
    if user:
        user.role = role
        db.session.commit()

#set the user's role based on email
if __name__ == '__main__':
  email = 'testadmin1@gmail.com'
  app = create_app()
  with app.app_context():
    db.create_all()
    assign_role(email, 'admin')
    print('Admin role assigned to ' + email)