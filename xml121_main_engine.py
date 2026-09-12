# © 2026 121 Solutions USA. All rights reserved.
#
# The trademarks 121XQ, 121XML, and 121MetaVerse are the exclusive
# property of 121 Solutions USA.
#
# Unauthorized use, reproduction, or distribution of this material,
# including any proprietary designs, software, or documentation, is
# strictly prohibited without prior written permission from 121 Solutions USA.
"""
121AI - Main Engine
Core orchestration engine integrating all 121XML components

Version: 1.0.0
License: Proprietary - 121 Group
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

# Import all components
from xml121_converter import UniversalConverter, FormatType
from xml121_addresser import AddressingService, ContentAddress
from xml121_auditor import AuditTrail, ComplianceAuditor, OperationType, AccessLevel
from xml121_compressor import CompressionService
from xml121_format_profiles import FormatRegistry
from xml121_voice_connectors import HybridVoiceConnector, VoicePlatform
from xml121_database_adapters import DatabaseAdapterFactory, DatabaseType, ConnectionConfig
from xml121_agent_orchestrator import AgentOrchestrator, Task, TaskPriority


@dataclass
class EngineConfig:
    """121AI Engine configuration"""
    organization_id: str = "121"
    enable_compression: bool = True
    enable_addressing: bool = True
    enable_auditing: bool = True
    enable_voice: bool = True
    compression_level: int = 7  # 1-10
    max_message_size: int = 100_000_000  # bytes
    audit_retention_days: int = 365
    enable_gdpr_compliance: bool = True
    enable_hipaa_compliance: bool = False
    enable_soc2_compliance: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EngineSession:
    """Active engine session"""
    session_id: str = ""
    user_id: str = ""
    start_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_activity: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    message_count: int = 0
    token_count: int = 0
    compression_savings: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class Engine121AI:
    """Core 121AI Engine - Universal AI Orchestration Platform"""

    def __init__(self, config: Optional[EngineConfig] = None):
        """Initialize 121AI Engine"""
        self.config = config or EngineConfig()
        self.session = EngineSession()

        # Initialize components
        self.converter = UniversalConverter()
        self.addressing_service = AddressingService()
        self.audit_trail = AuditTrail(self.config.organization_id)
        self.compliance_auditor = ComplianceAuditor(self.audit_trail)
        self.compression_service = CompressionService()
        self.format_registry = FormatRegistry()
        self.voice_connector = HybridVoiceConnector()
        self.orchestrator = AgentOrchestrator()

        # Initialize logging
        self.event_log: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, List[float]] = {
            "conversion_time_ms": [],
            "compression_ratio": [],
            "addressing_time_ms": [],
            "voice_latency_ms": []
        }

        # Startup logging
        self.audit_trail.log_event(
            operation=OperationType.CREATE,
            actor="system",
            resource="engine_121ai",
            action="startup",
            metadata={"version": "1.0.0", "config": str(self.config)}
        )

    def process_message(
        self,
        content: str,
        source_format: Optional[FormatType] = None,
        target_format: FormatType = FormatType.INTERNAL_121,
        user_id: str = "",
        compress: bool = True,
        address: bool = True,
        audit: bool = True
    ) -> Dict[str, Any]:
        """
        Main message processing pipeline

        1. Detect/validate format
        2. Convert to internal 121XML
        3. Compress (if enabled)
        4. Address (if enabled)
        5. Audit (if enabled)
        6. Return result
        """

        import time
        start_time = time.time()

        result = {
            "success": True,
            "message_id": "",
            "stage_results": {},
            "metrics": {
                "total_time_ms": 0,
                "original_size": len(content),
                "compressed_size": 0,
                "compression_ratio": 0.0,
                "compression_savings": 0.0
            },
            "addresses": {},
            "audit_events": [],
            "warnings": [],
            "errors": []
        }

        try:
            # Stage 1: Format Detection & Conversion
            stage1_start = time.time()

            conversion_result = self.converter.convert(
                content,
                source_format=source_format,
                target_format=target_format,
                validate=True
            )

            if not conversion_result.success:
                result["success"] = False
                result["errors"] = conversion_result.errors
                return result

            converted_data = conversion_result.output
            result["stage_results"]["conversion"] = {
                "source_format": source_format.value if source_format else "auto-detected",
                "target_format": target_format.value,
                "data_loss_percent": conversion_result.data_loss,
                "warnings": conversion_result.warnings,
                "time_ms": (time.time() - stage1_start) * 1000
            }

            # Stage 2: Compression (if enabled)
            if compress and self.config.enable_compression:
                stage2_start = time.time()

                compressed_data, metrics = self.compression_service.compress_and_store(
                    converted_data,
                    aggressiveness=self.config.compression_level
                )

                result["stage_results"]["compression"] = {
                    "original_size": metrics.original_size_bytes,
                    "compressed_size": metrics.compressed_size_bytes,
                    "ratio": metrics.compression_ratio,
                    "token_savings": metrics.token_savings_percent,
                    "time_ms": (time.time() - stage2_start) * 1000
                }

                result["metrics"]["compressed_size"] = metrics.compressed_size_bytes
                result["metrics"]["compression_ratio"] = metrics.compression_ratio
                result["metrics"]["compression_savings"] = metrics.token_savings_percent

                # Use compressed for next stages
                data_to_address = compressed_data
            else:
                data_to_address = converted_data

            # Stage 3: Content Addressing (if enabled)
            if address and self.config.enable_addressing:
                stage3_start = time.time()

                address_record = self.addressing_service.addresser.create_addressing_record(
                    data_to_address,
                    content_type="application/json",
                    metadata={"source_format": source_format.value if source_format else "unknown"}
                )

                result["addresses"] = {
                    "content_address": address_record.address.address_uri,
                    "hash": address_record.address.hash_value,
                    "verified": address_record.verified,
                    "size_bytes": address_record.address.size_bytes
                }

                result["stage_results"]["addressing"] = {
                    "address": address_record.address.address_uri,
                    "verified": address_record.verified,
                    "time_ms": (time.time() - stage3_start) * 1000
                }

                result["message_id"] = address_record.address.hash_value[:16]

            # Stage 4: Auditing (if enabled)
            if audit and self.config.enable_auditing:
                stage4_start = time.time()

                audit_event = self.audit_trail.log_event(
                    operation=OperationType.CONVERT,
                    actor=user_id or "system",
                    resource=source_format.value if source_format else "unknown",
                    action=f"convert_to_{target_format.value}",
                    access_level=AccessLevel.INTERNAL,
                    metadata={
                        "message_id": result["message_id"],
                        "source_format": source_format.value if source_format else "auto",
                        "target_format": target_format.value,
                        "compressed": compress and self.config.enable_compression,
                        "addressed": address and self.config.enable_addressing
                    }
                )

                result["stage_results"]["auditing"] = {
                    "event_id": audit_event.event_id,
                    "time_ms": (time.time() - stage4_start) * 1000
                }

                result["audit_events"].append(audit_event.event_id)

            # Final metrics
            result["metrics"]["total_time_ms"] = (time.time() - start_time) * 1000

            # Update session
            self.session.message_count += 1
            self.session.token_count += len(converted_data.split())
            if "compression_savings" in result["metrics"]:
                self.session.compression_savings += result["metrics"]["compression_savings"]
            self.session.last_activity = datetime.utcnow().isoformat()

            return result

        except Exception as e:
            result["success"] = False
            result["errors"].append(f"Engine error: {str(e)}")

            self.audit_trail.log_event(
                operation=OperationType.CREATE,
                actor=user_id or "system",
                resource="engine",
                action="error",
                status="failure",
                error_message=str(e)
            )

            return result

    def voice_query(
        self,
        text: str,
        platform: VoicePlatform,
        session_id: str,
        user_id: str = ""
    ) -> Dict[str, Any]:
        """Process voice query through hybrid connector"""

        response = self.voice_connector.process_cross_platform(
            text=text,
            platform=platform,
            session_id=session_id,
            context={"user_id": user_id}
        )

        self.audit_trail.log_event(
            operation=OperationType.ACCESS,
            actor=user_id or "system",
            resource=f"voice_{platform.value}",
            action="query",
            metadata={"query": text[:100], "platform": platform.value}
        )

        return {
            "response": response.text,
            "spoken_response": response.spoken_text or response.text,
            "platform": platform.value,
            "confidence": response.confidence,
            "followup_prompt": response.followup_prompt
        }

    def execute_task(
        self,
        task: Task,
        user_id: str = ""
    ) -> Dict[str, Any]:
        """Execute task through agent orchestrator"""

        # Log task submission
        self.audit_trail.log_event(
            operation=OperationType.CREATE,
            actor=user_id or "system",
            resource="task",
            action="submit",
            metadata={"task_id": task.task_id, "description": task.description}
        )

        # Route through orchestrator
        result = self.orchestrator.route_to_agents(task)

        return result

    def get_compliance_report(self) -> Dict[str, Any]:
        """Generate compliance report"""

        report = self.compliance_auditor.generate_compliance_report()

        self.audit_trail.log_event(
            operation=OperationType.READ,
            actor="system",
            resource="compliance",
            action="report_generated",
            metadata={"gdpr_compliant": report["gdpr"]["compliant"]}
        )

        return report

    def get_session_summary(self) -> Dict[str, Any]:
        """Get current session summary"""

        return {
            "session_id": self.session.session_id,
            "start_time": self.session.start_time,
            "duration_seconds": (
                datetime.fromisoformat(self.session.last_activity) -
                datetime.fromisoformat(self.session.start_time)
            ).total_seconds(),
            "messages_processed": self.session.message_count,
            "tokens_processed": self.session.token_count,
            "compression_savings_percent": self.session.compression_savings / self.session.message_count if self.session.message_count > 0 else 0,
            "audit_events": len(self.audit_trail.events),
            "agent_stats": self.orchestrator.get_statistics()
        }

    def get_engine_statistics(self) -> Dict[str, Any]:
        """Get engine statistics"""

        return {
            "config": {
                "organization_id": self.config.organization_id,
                "compression_enabled": self.config.enable_compression,
                "addressing_enabled": self.config.enable_addressing,
                "auditing_enabled": self.config.enable_auditing,
                "voice_enabled": self.config.enable_voice
            },
            "session": self.get_session_summary(),
            "converters": {
                "supported_formats": self.converter.get_supported_formats(),
                "conversions": len(self.converter.conversion_history)
            },
            "compression": self.compression_service.get_statistics(),
            "audit": self.audit_trail._compute_statistics(),
            "compliance": self.get_compliance_report()
        }

    def shutdown(self, user_id: str = ""):
        """Graceful shutdown"""

        self.audit_trail.log_event(
            operation=OperationType.CREATE,
            actor=user_id or "system",
            resource="engine_121ai",
            action="shutdown",
            metadata={
                "messages_processed": self.session.message_count,
                "total_compression_savings": self.session.compression_savings
            }
        )

        # Seal logs
        self.audit_trail.seal_log()

        return {
            "status": "shutdown_complete",
            "session_summary": self.get_session_summary()
        }


if __name__ == "__main__":
    # Example usage
    config = EngineConfig(
        organization_id="121AI",
        enable_compression=True,
        enable_addressing=True,
        enable_auditing=True,
        compression_level=7
    )

    engine = Engine121AI(config)

    # Process a SWIFT message
    swift_data = """{1:F01CHASUS33AXXX1234567890}{2:I103DEUTDEFF200703042150}{4:
:20:REFERENCE20240807
:23B:CRED
:32A:240807USD1500000,00
:50A:/NL91ABNA0417164300
121AI
:57A:CHASUS33
:59:/DE89370400440532013000
ABC CORP BERLIN
:70:INVOICE 12345
:72:PAYROLL TRANSFER
-}"""

    result = engine.process_message(
        swift_data,
        source_format=FormatType.SWIFT,
        target_format=FormatType.INTERNAL_121,
        user_id="user@121.us",
        compress=True,
        address=True,
        audit=True
    )

    print(f"Processing successful: {result['success']}")
    print(f"Message ID: {result['message_id']}")
    print(f"Compression savings: {result['metrics']['compression_savings']:.1f}%")
    print(f"Total time: {result['metrics']['total_time_ms']:.2f}ms")

    # Get statistics
    stats = engine.get_engine_statistics()
    print(f"\nEngine Statistics:")
    print(f"  Supported formats: {stats['converters']['supported_formats']}")
    print(f"  Audit events: {stats['audit']['total_events']}")

    # Shutdown
    shutdown_result = engine.shutdown()
    print(f"\nShutdown: {shutdown_result['status']}")
