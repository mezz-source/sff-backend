class LogRepository():
    def __init__(self, db):
        self.db = db

    def get_by_id(self, log_id: int):
        from src.models.log_model import Log

        return self.db.get(Log, log_id)

    def list_by_user_id(self, user_id: int):
        from src.models.log_model import Log

        return (
            self.db.query(Log)
            .filter(Log.user_id == user_id)
            .order_by(Log.created_at.desc())
            .all()
        )

    def create_log(self, user_id: int, message: str):
        from src.models.log_model import Log

        log = Log(user_id=user_id, message=message)
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def update_log(self, log):
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log