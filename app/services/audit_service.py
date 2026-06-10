from sqlalchemy.orm import Session
from app.models.audit import Audit

def log_audit_event(
    db: Session,
    action: str,
    user_id: int | None = None,
    email: str | None = None,
    details: dict | None = None,
    ip_address: str | None = None
):
    try:
        audit = Audit(
            user_id=user_id,
            email=email,
            action=action,
            details=details,
            ip_address=ip_address
        )
        db.add(audit)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Failed to log audit event: {e}")
