"""
121AI - Universal AI Orchestration Platform
121XML Standard - Lossless Universal Format

Package: 121ai
Version: 1.0.0
License: Proprietary - 121 Group
Author: 121 Group
"""

__version__ = "1.0.0"
__author__ = "121 Group"
__license__ = "Proprietary"

# Core Engine
from xml121_main_engine import Engine121AI, EngineConfig, EngineSession

# Format Conversion
from xml121_converter import (
    UniversalConverter,
    FormatType,
    FormatConverter,
    SWIFTConverter,
    ISO20022Converter,
    JSONConverter,
    ConversionResult
)

# Content Addressing
from xml121_addresser import (
    ContentAddresser,
    ContentAddress,
    AddressingService,
    AddressingRecord
)

# Compression
from xml121_compressor import (
    CompressionService,
    SparseReferenceCompressor,
    CompressionResult,
    CompressionMetrics
)

# Audit Trail
from xml121_auditor import (
    AuditTrail,
    ComplianceAuditor,
    AuditEvent,
    OperationType,
    AccessLevel
)

# Format Profiles
from xml121_format_profiles import (
    FormatRegistry,
    FormatSpecification,
    FieldDefinition,
    SWIFT_PROFILE,
    ISO20022_PROFILE,
    HL7_PROFILE,
    JSON_PROFILE,
    CSV_PROFILE
)

# Voice Connectors
from xml121_voice_connectors import (
    HybridVoiceConnector,
    VoiceConnector,
    SiriConnector,
    GoogleAssistantConnector,
    AlexaConnector,
    VoicePlatform,
    VoiceIntent,
    VoiceResponse
)

# Database Adapters
from xml121_database_adapters import (
    DatabaseAdapter,
    DatabaseAdapterFactory,
    PostgreSQLAdapter,
    MongoDBAdapter,
    DynamoDBAdapter,
    RedisAdapter,
    ConnectionConfig,
    QueryResult,
    DatabaseType
)

# Agent Orchestrator
from xml121_agent_orchestrator import (
    AgentOrchestrator,
    Agent,
    Task,
    Tool,
    AgentRole,
    TaskPriority,
    TaskStatus,
    ExecutionPlan
)

__all__ = [
    # Core
    "Engine121AI",
    "EngineConfig",
    "EngineSession",

    # Conversion
    "UniversalConverter",
    "FormatType",
    "FormatConverter",
    "SWIFTConverter",
    "ISO20022Converter",
    "JSONConverter",
    "ConversionResult",

    # Addressing
    "ContentAddresser",
    "ContentAddress",
    "AddressingService",
    "AddressingRecord",

    # Compression
    "CompressionService",
    "SparseReferenceCompressor",
    "CompressionResult",
    "CompressionMetrics",

    # Audit
    "AuditTrail",
    "ComplianceAuditor",
    "AuditEvent",
    "OperationType",
    "AccessLevel",

    # Formats
    "FormatRegistry",
    "FormatSpecification",
    "FieldDefinition",
    "SWIFT_PROFILE",
    "ISO20022_PROFILE",
    "HL7_PROFILE",
    "JSON_PROFILE",
    "CSV_PROFILE",

    # Voice
    "HybridVoiceConnector",
    "VoiceConnector",
    "SiriConnector",
    "GoogleAssistantConnector",
    "AlexaConnector",
    "VoicePlatform",
    "VoiceIntent",
    "VoiceResponse",

    # Database
    "DatabaseAdapter",
    "DatabaseAdapterFactory",
    "PostgreSQLAdapter",
    "MongoDBAdapter",
    "DynamoDBAdapter",
    "RedisAdapter",
    "ConnectionConfig",
    "QueryResult",
    "DatabaseType",

    # Orchestration
    "AgentOrchestrator",
    "Agent",
    "Task",
    "Tool",
    "AgentRole",
    "TaskPriority",
    "TaskStatus",
    "ExecutionPlan",
]


def get_version() -> str:
    """Get package version"""
    return __version__


def get_engine(config=None) -> Engine121AI:
    """Create new 121AI engine instance"""
    return Engine121AI(config)
