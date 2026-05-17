from sqlalchemy.orm import Session

from app.models.projekt import Projekt


class ProjektService:
    def create(self, db: Session, name: str) -> Projekt:
        projekt = Projekt(name=name)
        db.add(projekt)
        db.commit()
        db.refresh(projekt)
        return projekt

    def list_all(self, db: Session) -> list[Projekt]:
        return db.query(Projekt).order_by(Projekt.created_at.desc()).all()
