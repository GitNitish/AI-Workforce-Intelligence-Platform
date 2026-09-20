from typing import Any

from sqlalchemy.orm import Session

from app.models.entities import AuditEvent


def create_audit_event(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    result: str = "success",
    user_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> AuditEvent:
    audit_event = AuditEvent(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        result=result,
        event_metadata=metadata,
    )

    db.add(audit_event)
    db.flush()

    return audit_event