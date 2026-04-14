class UserRepository():
    def __init__(self, db):
        self.db = db

    def get_by_id(self, user_id: int):
        from src.models.user_model import User

        return self.db.get(User, user_id)

    def get_by_username(self, username: str):
        from src.models.user_model import User

        return self.db.query(User).filter(User.username == username).first()

    def create_user(self, username: str, password_hash: str):
        from src.models.user_model import User

        user = User(username=username, password_hash=password_hash)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(self, user):
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user):
        self.db.delete(user)
        self.db.commit()