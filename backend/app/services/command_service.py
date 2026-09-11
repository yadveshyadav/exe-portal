from datetime import datetime, timezone
from app.extensions import db
from app.models.command import Command, CommandResult
from app.models.device import Device
from app.services.realtime_service import RealtimeService

ALLOWED_COMMAND_TYPES = {
    "SYNC",
    "REFRESH_CONFIGURATION",
    "HEALTH_CHECK",
    "CHECK_VERSION"
}

class CommandService:
    """Manages safe administrative commands dispatched to Windows agents."""

    @classmethod
    def dispatch_command(
        cls,
        company_id: str,
        device_id: str,
        command_type: str,
        parameters: dict = None,
        created_by: str = None
    ):
        if command_type not in ALLOWED_COMMAND_TYPES:
            raise ValueError(f"Command type '{command_type}' is not permitted. Allowed commands: {', '.join(ALLOWED_COMMAND_TYPES)}")

        device = Device.query.filter_by(id=device_id, company_id=company_id).first()
        if not device:
            raise ValueError("Target device not found")

        command = Command(
            company_id=company_id,
            device_id=device_id,
            command_type=command_type,
            parameters=parameters or {},
            status="PENDING",
            created_by=created_by
        )
        db.session.add(command)
        db.session.commit()

        # Emit to agent channel/room
        RealtimeService.broadcast_command_update(
            company_id=company_id,
            command_data={
                "command_id": command.id,
                "device_id": device_id,
                "device_uid": device.device_uid,
                "command_type": command_type,
                "parameters": parameters or {},
                "status": "PENDING"
            }
        )
        return command

    @classmethod
    def record_command_result(
        cls,
        command_id: str,
        device_id: str,
        exit_code: int,
        result_payload: dict = None,
        error_message: str = None
    ):
        command = Command.query.filter_by(id=command_id, device_id=device_id).first()
        if not command:
            return None

        command.status = "EXECUTED" if exit_code == 0 else "FAILED"
        command.executed_at = datetime.now(timezone.utc)

        result = CommandResult(
            command_id=command.id,
            device_id=device_id,
            exit_code=exit_code,
            result_payload=result_payload or {},
            error_message=error_message
        )
        db.session.add(result)
        db.session.commit()
        return command
