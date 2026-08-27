"""
121XML Audit Trail System
Immutable logging of all operations with cryptographic verification

Version: 1.0.0
License: Proprietary - 121 Group
"""

import json
import hashlib
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import uuid


class OperationType(Enum):
    """Types of operations tracked"""
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    CONVERT = "convert"
    COMPRESS = "compress"
    ADDRESS = "address"
    VERIFY = "verify"
    ARCHIVE = "archive"
    ACCESS = "access"
    AUTHENTICATE = "authenticate"
    AUTHORIZE = "authorize"
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"


class AccessLevel(Enum):
    """Data access levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"


@dataclass
class AuditEvent:
    """Single audit event"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    operation: OperationType = OperationType.READ
    actor: str = ""  # User, service, or system performing operation
    resource: str = ""  # What was accessed/modified
    action: str = ""  # Specific action taken
    status: str = "success"  # success, failure, partial
    result: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""
    access_level: AccessLevel = AccessLevel.INTERNAL
    source_ip: str = ""
    user_agent: str = ""
    request_id: str = ""
    parent_event_id: Optional[str] = None
    related_events: List[str] = field(default_factory=list)
    data_inputs: Dict[str, Any] = field(default_factory=dict)
    data_outputs: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    event_hash: str = ""  # Cryptographic hash of event


@dataclass
class AuditLog:
    """Complete audit log with chain verification"""
    log_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    events: List[AuditEvent] = field(default_factory=list)
    log_hash: str = ""
    previous_log_hash: str = ""
    integrity_verified: bool = False


class AuditTrail:
    """Maintains immutable audit trail"""

    def __init__(self, organization_id: str = "121"):
        self.organization_id = organization_id
        self.events: List[AuditEvent] = []
        self.logs: List[AuditLog] = []
        self.current_log = AuditLog()
        self.logs.append(self.current_log)
        self.event_index: Dict[str, AuditEvent] = {}
        self.actor_index: Dict[str, List[str]] = {}  # Actor -> event IDs
        self.resource_index: Dict[str, List[str]] = {}  # Resource -> event IDs
        self.verification_chain: List[str] = []  # Hash chain for verification

    def log_event(
        self,
        operation: OperationType,
        actor: str,
        resource: str,
        action: str = "",
        status: str = "success",
        access_level: AccessLevel = AccessLevel.INTERNAL,
        result: Optional[Dict[str, Any]] = None,
        error_message: str = "",
        source_ip: str = "",
        user_agent: str = "",
        request_id: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """Log an operation"""

        event = AuditEvent(
            operation=operation,
            actor=actor,
            resource=resource,
            action=action,
            status=status,
            access_level=access_level,
            result=result or {},
            error_message=error_message,
            source_ip=source_ip,
            user_agent=user_agent,
            request_id=request_id,
            metadata=metadata or {}
        )

        # Compute event hash
        event_data = {
            "timestamp": event.timestamp,
            "operation": event.operation.value,
            "actor": event.actor,
            "resource": event.resource,
            "action": event.action,
            "status": event.status
        }
        event.event_hash = hashlib.sha256(
            json.dumps(event_data, sort_keys=True).encode()
        ).hexdigest()

        # Add to current log
        self.current_log.events.append(event)
        self.events.append(event)
        self.event_index[event.event_id] = event

        # Update indexes
        if actor not in self.actor_index:
            self.actor_index[actor] = []
        self.actor_index[actor].append(event.event_id)

        if resource not in self.resource_index:
            self.resource_index[resource] = []
        self.resource_index[resource].append(event.event_id)

        # Add to verification chain
        chain_data = f"{len(self.verification_chain)}:{event.event_hash}"
        if self.verification_chain:
            chain_data = f"{self.verification_chain[-1][:16]}:{chain_data}"
        chain_hash = hashlib.sha256(chain_data.encode()).hexdigest()
        self.verification_chain.append(chain_hash)

        return event

    def log_data_access(
        self,
        actor: str,
        resource: str,
        access_type: str,  # read, write, delete
        success: bool,
        access_level: AccessLevel = AccessLevel.INTERNAL
    ) -> AuditEvent:
        """Log data access operation"""

        return self.log_event(
            operation=OperationType.ACCESS,
            actor=actor,
            resource=resource,
            action=f"data_{access_type}",
            status="success" if success else "failure",
            access_level=access_level,
            metadata={"access_type": access_type}
        )

    def log_authentication(
        self,
        actor: str,
        method: str,
        success: bool,
        source_ip: str = "",
        error_message: str = ""
    ) -> AuditEvent:
        """Log authentication attempt"""

        return self.log_event(
            operation=OperationType.AUTHENTICATE,
            actor=actor,
            resource="authentication_service",
            action=f"login_{method}",
            status="success" if success else "failure",
            source_ip=source_ip,
            error_message=error_message,
            metadata={"method": method}
        )

    def log_authorization(
        self,
        actor: str,
        resource: str,
        permission: str,
        granted: bool,
        reason: str = ""
    ) -> AuditEvent:
        """Log authorization decision"""

        return self.log_event(
            operation=OperationType.AUTHORIZE,
            actor=actor,
            resource=resource,
            action=permission,
            status="success" if granted else "failure",
            metadata={"granted": granted, "reason": reason}
        )

    def log_conversion(
        self,
        actor: str,
        source_format: str,
        target_format: str,
        record_count: int = 0,
        success: bool = True,
        error_message: str = ""
    ) -> AuditEvent:
        """Log format conversion"""

        return self.log_event(
            operation=OperationType.CONVERT,
            actor=actor,
            resource=f"{source_format}_to_{target_format}",
            action="format_conversion",
            status="success" if success else "failure",
            error_message=error_message,
            metadata={"source_format": source_format, "target_format": target_format, "record_count": record_count}
        )

    def log_encryption(
        self,
        actor: str,
        resource: str,
        algorithm: str,
        key_id: str,
        success: bool = True
    ) -> AuditEvent:
        """Log encryption operation"""

        return self.log_event(
            operation=OperationType.ENCRYPT,
            actor=actor,
            resource=resource,
            action="encrypt",
            status="success" if success else "failure",
            metadata={"algorithm": algorithm, "key_id": key_id}
        )

    def log_archival(
        self,
        actor: str,
        resource: str,
        archive_path: str,
        content_hash: str,
        success: bool = True
    ) -> AuditEvent:
        """Log archival operation"""

        return self.log_event(
            operation=OperationType.ARCHIVE,
            actor=actor,
            resource=resource,
            action="archive",
            status="success" if success else "failure",
            metadata={"archive_path": archive_path, "content_hash": content_hash}
        )

    def get_actor_events(self, actor: str) -> List[AuditEvent]:
        """Get all events for an actor"""
        event_ids = self.actor_index.get(actor, [])
        return [self.event_index[eid] for eid in event_ids if eid in self.event_index]

    def get_resource_events(self, resource: str) -> List[AuditEvent]:
        """Get all events for a resource"""
        event_ids = self.resource_index.get(resource, [])
        return [self.event_index[eid] for eid in event_ids if eid in self.event_index]

    def get_events_by_operation(self, operation: OperationType) -> List[AuditEvent]:
        """Get all events of a specific operation type"""
        return [e for e in self.events if e.operation == operation]

    def get_events_by_status(self, status: str) -> List[AuditEvent]:
        """Get all events with specific status"""
        return [e for e in self.events if e.status == status]

    def get_events_by_access_level(self, access_level: AccessLevel) -> List[AuditEvent]:
        """Get all events with specific access level"""
        return [e for e in self.events if e.access_level == access_level]

    def get_events_by_date_range(
        self,
        start_date: str,
        end_date: str
    ) -> List[AuditEvent]:
        """Get events within date range (ISO format)"""
        return [
            e for e in self.events
            if start_date <= e.timestamp <= end_date
        ]

    def seal_log(self) -> AuditLog:
        """Seal current log and create new one"""

        # Compute log hash
        log_data = json.dumps(
            [asdict(e) for e in self.current_log.events],
            sort_keys=True,
            default=str
        )
        self.current_log.log_hash = hashlib.sha256(log_data.encode()).hexdigest()

        # Link to previous log
        if len(self.logs) > 1:
            self.current_log.previous_log_hash = self.logs[-2].log_hash

        # Verify integrity
        self.current_log.integrity_verified = self.verify_log_integrity(self.current_log)

        # Create new log
        new_log = AuditLog()
        self.logs.append(new_log)
        self.current_log = new_log

        return self.logs[-2]

    def verify_log_integrity(self, log: AuditLog) -> bool:
        """Verify log integrity"""

        if not log.events:
            return True

        # Recompute log hash
        log_data = json.dumps(
            [asdict(e) for e in log.events],
            sort_keys=True,
            default=str
        )
        computed_hash = hashlib.sha256(log_data.encode()).hexdigest()

        return computed_hash == log.log_hash

    def verify_verification_chain(self) -> bool:
        """Verify event verification chain"""

        if not self.verification_chain:
            return True

        for i, chain_hash in enumerate(self.verification_chain):
            if i == 0:
                continue

            # Recompute previous link
            event = self.events[i - 1]
            chain_data = f"{self.verification_chain[i - 2][:16]}:{i - 1}:{event.event_hash}"
            expected_hash = hashlib.sha256(chain_data.encode()).hexdigest()

            if expected_hash != self.verification_chain[i]:
                return False

        return True

    def export_audit_trail(
        self,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """Export audit trail data"""

        export = {
            "organization_id": self.organization_id,
            "exported_at": datetime.utcnow().isoformat(),
            "total_events": len(self.events),
            "total_logs": len(self.logs),
            "chain_verified": self.verify_verification_chain(),
            "events": [],
            "statistics": self._compute_statistics()
        }

        if include_details:
            export["events"] = [asdict(e) for e in self.events]
            export["logs"] = [
                {
                    "log_id": log.log_id,
                    "created_at": log.created_at,
                    "event_count": len(log.events),
                    "log_hash": log.log_hash,
                    "integrity_verified": log.integrity_verified
                }
                for log in self.logs
            ]

        return export

    def _compute_statistics(self) -> Dict[str, Any]:
        """Compute audit trail statistics"""

        return {
            "total_events": len(self.events),
            "by_operation": {
                op.value: len(self.get_events_by_operation(op))
                for op in OperationType
            },
            "by_status": {
                status: len(self.get_events_by_status(status))
                for status in ["success", "failure", "partial"]
            },
            "by_access_level": {
                level.value: len(self.get_events_by_access_level(level))
                for level in AccessLevel
            },
            "total_actors": len(self.actor_index),
            "total_resources": len(self.resource_index),
            "failure_count": len(self.get_events_by_status("failure"))
        }


class ComplianceAuditor:
    """Compliance-focused auditing (GDPR, HIPAA, SOC2)"""

    def __init__(self, audit_trail: AuditTrail):
        self.audit_trail = audit_trail
        self.policies: Dict[str, Dict[str, Any]] = self._init_policies()

    def _init_policies(self) -> Dict[str, Dict[str, Any]]:
        """Initialize compliance policies"""
        return {
            "gdpr": {
                "data_retention_days": 365,
                "requires_consent": True,
                "right_to_deletion": True,
                "data_portability": True
            },
            "hipaa": {
                "access_logging": True,
                "encryption_required": True,
                "audit_retention_years": 6,
                "breach_notification_required": True
            },
            "soc2": {
                "logical_access_controls": True,
                "physical_access_controls": True,
                "monitoring_and_alerts": True,
                "annual_review_required": True
            }
        }

    def audit_gdpr_compliance(self) -> Dict[str, Any]:
        """Check GDPR compliance"""
        results = {
            "compliant": True,
            "checks": {},
            "issues": []
        }

        # Check data access logging
        access_events = self.audit_trail.get_events_by_operation(OperationType.ACCESS)
        results["checks"]["access_logged"] = len(access_events) > 0

        # Check deletion capability
        delete_events = self.audit_trail.get_events_by_operation(OperationType.DELETE)
        results["checks"]["deletion_capability"] = len(delete_events) >= 0

        # Check data retention
        retention_days = self.policies["gdpr"]["data_retention_days"]
        old_events = [
            e for e in self.audit_trail.events
            if (datetime.fromisoformat(e.timestamp) - datetime.utcnow()).days > retention_days
        ]
        if old_events:
            results["issues"].append(f"Found {len(old_events)} events exceeding retention period")
            results["compliant"] = False

        return results

    def audit_hipaa_compliance(self) -> Dict[str, Any]:
        """Check HIPAA compliance"""
        results = {
            "compliant": True,
            "checks": {},
            "issues": []
        }

        # Check encryption
        encrypt_events = self.audit_trail.get_events_by_operation(OperationType.ENCRYPT)
        results["checks"]["encryption_in_use"] = len(encrypt_events) > 0

        # Check audit trail retention (6 years)
        retention_years = self.policies["hipaa"]["audit_retention_years"]
        old_events = [
            e for e in self.audit_trail.events
            if (datetime.fromisoformat(e.timestamp) - datetime.utcnow()).days > retention_years * 365
        ]
        if old_events:
            results["issues"].append(f"Audit logs older than {retention_years} years should be archived")

        # Check access controls
        auth_events = self.audit_trail.get_events_by_operation(OperationType.AUTHENTICATE)
        results["checks"]["access_controls"] = len(auth_events) > 0

        return results

    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "gdpr": self.audit_gdpr_compliance(),
            "hipaa": self.audit_hipaa_compliance(),
            "audit_trail_integrity": self.audit_trail.verify_verification_chain(),
            "total_events": len(self.audit_trail.events)
        }


if __name__ == "__main__":
    # Example usage
    trail = AuditTrail("121AI")

    # Log various operations
    trail.log_authentication("user1@121.us", "oauth2", True, "192.168.1.1")
    trail.log_data_access("user1@121.us", "/api/invoices", "read", True)
    trail.log_conversion("system", "SWIFT", "ISO20022", 100)
    trail.log_archival("system", "invoice_12345", "/archive/2024/08", "sha256:abc123")

    # Get statistics
    stats = trail.events[0]
    print(f"Total Events: {len(trail.events)}")
    print(f"First Event: {stats.operation.value}")

    # Verify chain
    chain_valid = trail.verify_verification_chain()
    print(f"Chain Valid: {chain_valid}")

    # Check compliance
    auditor = ComplianceAuditor(trail)
    report = auditor.generate_compliance_report()
    print(f"GDPR Compliant: {report['gdpr']['compliant']}")
