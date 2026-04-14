class LogRepository():
    def __init__(self, db):
        self.db = db

    def get_by_id(self, log_id: int):
        from src.models.log_model import Log

        return self.db.get(Log, log_id)

    def list_by_user_id(self, user_id: int, offset: int = 0, limit: int = 10):
        from src.models.log_model import Log

        return (
            self.db.query(Log)
            .filter(Log.user_id == user_id)
            .order_by(Log.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def list_all(self, offset: int = 0, limit: int = 10):
        from src.models.log_model import Log

        return (
            self.db.query(Log)
            .order_by(Log.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def count_by_user_id(self, user_id: int) -> int:
        from src.models.log_model import Log

        return self.db.query(Log).filter(Log.user_id == user_id).count()

    def count_all(self) -> int:
        from src.models.log_model import Log

        return self.db.query(Log).count()

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