from app.extensions import db
from app.models.agent import Agent
from app.models.device import Device
from app.models.company import Company
from app.services.realtime_service import RealtimeService
from app.services.audit_service import AuditService

class AgentService:
    @staticmethod
    def get_agents_overview(company_id: str):
        devices = Device.query.filter_by(company_id=company_id, is_active=True).all()
        results = []
        for dev in devices:
            if dev.agent:
                agent_dict = dev.agent.to_dict()
                agent_dict["hostname"] = dev.hostname
                agent_dict["employee_name"] = dev.employee.full_name if dev.employee else "Unassigned"
                agent_dict["status"] = dev.status
                results.append(agent_dict)
        return results

    @staticmethod
    def get_agent_config(company_id: str, device_id: str = None):
        company = Company.query.filter_by(id=company_id).first()
        default_config = {
            "server_url": "http://192.168.1.253:5000",
            "server_ip": "192.168.1.253",
            "server_port": 5000,
            "heartbeat_interval_seconds": 30,
            "idle_threshold_seconds": 300,
            "reconnect_interval_seconds": 15,
            "event_batch_size": 20,
            "log_retention_days": 90,
        }
        if company and company.settings and "agent_config" in company.settings:
            default_config.update(company.settings["agent_config"])
        return default_config

    @staticmethod
    def push_configuration(company_id: str, device_id: str, config_data: dict):
        company = Company.query.filter_by(id=company_id).first()
        if not company:
            return None, "Company not found"

        device = (
            Device.query.filter_by(id=device_id, company_id=company_id, is_active=True).first()
            if device_id and device_id != "global"
            else None
        )

        current_settings = dict(company.settings or {})
        agent_config = dict(current_settings.get("agent_config", {}))

        if "server_ip" in config_data and config_data["server_ip"]:
            agent_config["server_ip"] = str(config_data["server_ip"]).strip()
        if "server_port" in config_data and config_data["server_port"]:
            agent_config["server_port"] = int(config_data["server_port"])

        if "server_url" in config_data and config_data["server_url"]:
            agent_config["server_url"] = str(config_data["server_url"]).strip().rstrip("/")
        elif "server_ip" in agent_config and "server_port" in agent_config:
            agent_config["server_url"] = f"http://{agent_config['server_ip']}:{agent_config['server_port']}"

        if "heartbeat_interval_seconds" in config_data and config_data["heartbeat_interval_seconds"]:
            agent_config["heartbeat_interval_seconds"] = int(config_data["heartbeat_interval_seconds"])
        elif "heartbeat_interval" in config_data and config_data["heartbeat_interval"]:
            agent_config["heartbeat_interval_seconds"] = int(config_data["heartbeat_interval"])

        if "idle_threshold_seconds" in config_data and config_data["idle_threshold_seconds"]:
            agent_config["idle_threshold_seconds"] = int(config_data["idle_threshold_seconds"])
        elif "idle_threshold" in config_data and config_data["idle_threshold"]:
            agent_config["idle_threshold_seconds"] = int(config_data["idle_threshold"])

        if "reconnect_interval_seconds" in config_data and config_data["reconnect_interval_seconds"]:
            agent_config["reconnect_interval_seconds"] = int(config_data["reconnect_interval_seconds"])
        elif "reconnect_interval" in config_data and config_data["reconnect_interval"]:
            agent_config["reconnect_interval_seconds"] = int(config_data["reconnect_interval"])

        current_settings["agent_config"] = agent_config
        company.settings = current_settings
        db.session.commit()

        # Emit configuration update to device & portal clients
        RealtimeService.emit_to_company(
            company_id=company_id,
            event_type="CONFIGURATION_UPDATED",
            data={
                "device_id": device.id if device else "all",
                "device_uid": device.device_uid if device else "all",
                "configuration": agent_config,
            },
        )

        AuditService.log_action(
            action="AGENT_CONFIGURATION_PUSHED",
            resource_type="agent",
            resource_id=device.id if device else company_id,
            after_value=agent_config,
            company_id=company_id,
        )
        return {"status": "dispatched", "device_id": device_id, "configuration": agent_config}, None

