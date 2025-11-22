from server import app, db, Admin

def init_db():
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if admin exists
        admin = Admin.query.filter_by(college_id='C-123').first()
        if not admin:
            # Create default admin
            admin = Admin(
                college_id='C-123',
                admin_name='Admin',
                college_name='Test College',
                admin_password='admin123'
            )
            db.session.add(admin)
            db.session.commit()
            print("Default admin account created!")

if __name__ == '__main__':
    init_db()