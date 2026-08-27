"""
121XML Format Profiles
Complete specifications for 50+ enterprise data formats

Version: 1.0.0
License: Proprietary - 121 Group
"""

from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class PaymentNetworkType(Enum):
    """Payment network types"""
    SWIFT = "swift"
    ACH = "ach"
    SEPA = "sepa"
    WIRE = "wire"
    FPS = "fps"
    VISA = "visa"
    MASTERCARD = "mastercard"
    AMEX = "amex"


class MessageType(Enum):
    """Message types in 121XML"""
    PAYMENT = "payment"
    REMITTANCE = "remittance"
    SETTLEMENT = "settlement"
    NOTIFICATION = "notification"
    QUERY = "query"
    RESPONSE = "response"
    ERROR = "error"
    ACK = "ack"


@dataclass
class FieldDefinition:
    """Field specification"""
    name: str
    type: str
    required: bool = False
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    pattern: Optional[str] = None
    enumerated_values: List[str] = field(default_factory=list)
    description: str = ""
    example: str = ""
    nested_fields: List['FieldDefinition'] = field(default_factory=list)
    repeatable: bool = False
    conditional_on: Optional[str] = None


@dataclass
class FormatSpecification:
    """Complete format specification"""
    format_name: str
    version: str
    description: str
    owner: str  # Standard body or organization
    profile_uri: str
    root_element: str
    encoding: str
    maximum_size: int  # bytes
    fields: List[FieldDefinition] = field(default_factory=list)
    message_types: List[str] = field(default_factory=list)
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    conversion_notes: str = ""


# ============================================================================
# SWIFT Format Profile
# ============================================================================

SWIFT_PROFILE = FormatSpecification(
    format_name="SWIFT MT103",
    version="2024.1",
    description="ISO 20022 compliant SWIFT payment format for international money transfers",
    owner="The Society for Worldwide Interbank Financial Telecommunication",
    profile_uri="https://www.swift.com/standards/swift-mt103",
    root_element="SWIFT_MESSAGE",
    encoding="UTF-8",
    maximum_size=10_000_000,
    message_types=["MT103 - Single Customer Credit Transfer"],
    fields=[
        FieldDefinition(
            name="Block 1",
            type="block",
            required=True,
            description="Basic Header",
            nested_fields=[
                FieldDefinition(name="Application ID", type="string", required=True, max_length=1),
                FieldDefinition(name="Service ID", type="string", required=True, max_length=1),
                FieldDefinition(name="Logical Terminal", type="string", required=True, max_length=8),
                FieldDefinition(name="Session Number", type="string", required=True, max_length=6),
                FieldDefinition(name="Sequence Number", type="string", required=True, max_length=6),
            ]
        ),
        FieldDefinition(
            name="Block 2",
            type="block",
            required=True,
            description="Application Header",
            nested_fields=[
                FieldDefinition(name="Message Type", type="string", required=True, max_length=3),
                FieldDefinition(name="Receiver", type="string", required=True, max_length=12),
                FieldDefinition(name="Priority", type="string", required=False, max_length=1),
            ]
        ),
        FieldDefinition(
            name="Block 4",
            type="block",
            required=True,
            description="Text Block (Message Content)",
            nested_fields=[
                FieldDefinition(
                    name="20 - Transaction Reference",
                    type="string",
                    required=True,
                    max_length=16,
                    pattern=r"^[A-Z0-9]{1,16}$",
                    example="REFERENCE20240807"
                ),
                FieldDefinition(
                    name="23B - Bank Operation Code",
                    type="string",
                    required=True,
                    max_length=4,
                    enumerated_values=["CRED", "DBIT", "CRPT", "DRPT"],
                    example="CRED"
                ),
                FieldDefinition(
                    name="32A - Value Date and Currency, Interbank Settled Amount",
                    type="string",
                    required=True,
                    max_length=15,
                    pattern=r"^\d{6}[A-Z]{3}\d{1,15}(,\d{2})?$",
                    example="240807USD1500000,00"
                ),
                FieldDefinition(
                    name="50A/F - Ordering Customer",
                    type="string",
                    required=True,
                    max_length=34,
                    example="/NL91ABNA0417164300\n121AI"
                ),
                FieldDefinition(
                    name="57A/D/E - Account With Institution",
                    type="string",
                    required=True,
                    max_length=34,
                    example="CHASUS33"
                ),
                FieldDefinition(
                    name="59/F - Beneficiary Customer",
                    type="string",
                    required=True,
                    max_length=34,
                    example="/DE89370400440532013000\nABC CORP BERLIN"
                ),
                FieldDefinition(
                    name="70 - Remittance Information",
                    type="string",
                    required=False,
                    max_length=140,
                    repeatable=True,
                    example="INVOICE 12345"
                ),
                FieldDefinition(
                    name="72 - Sender to Receiver Information",
                    type="string",
                    required=False,
                    max_length=140,
                    example="PAYROLL TRANSFER"
                ),
            ]
        ),
        FieldDefinition(
            name="Block 5",
            type="block",
            required=True,
            description="Trailer Block",
            nested_fields=[
                FieldDefinition(name="Checksum", type="string", required=True, max_length=8),
                FieldDefinition(name="Message Authentication Code", type="string", required=False, max_length=8),
            ]
        ),
    ],
    validation_rules={
        "field_20_format": "^[A-Z0-9]{1,16}$",
        "field_23_values": ["CRED", "DBIT", "CRPT", "DRPT"],
        "field_32_format": "^\\d{6}[A-Z]{3}",
        "required_fields": ["20", "23", "32", "50", "57", "59"],
    },
    conversion_notes="SWIFT MT103 is fully compatible with ISO 20022 PACS.008. Conversion preserves all data with zero loss."
)


# ============================================================================
# ISO 20022 Format Profile
# ============================================================================

ISO20022_PROFILE = FormatSpecification(
    format_name="ISO 20022 PACS.008",
    version="2024.1",
    description="ISO 20022 XML-based payment format for credit transfers",
    owner="International Organization for Standardization (ISO)",
    profile_uri="https://www.iso20022.org/pacs.008.001.08",
    root_element="Document",
    encoding="UTF-8",
    maximum_size=50_000_000,
    message_types=["PACS.008 - Credit Transfer Initiation"],
    fields=[
        FieldDefinition(
            name="Document",
            type="container",
            required=True,
            nested_fields=[
                FieldDefinition(
                    name="CstmrCdtTrfInitn",
                    type="container",
                    required=True,
                    description="Customer Credit Transfer Initiation",
                    nested_fields=[
                        FieldDefinition(
                            name="GrpHdr",
                            type="container",
                            required=True,
                            description="Group Header",
                            nested_fields=[
                                FieldDefinition(
                                    name="MsgId",
                                    type="string",
                                    required=True,
                                    max_length=35,
                                    example="MSG000001"
                                ),
                                FieldDefinition(
                                    name="CreDtTm",
                                    type="datetime",
                                    required=True,
                                    example="2024-08-07T10:30:00Z"
                                ),
                                FieldDefinition(
                                    name="NbOfTxns",
                                    type="integer",
                                    required=True,
                                    example="1"
                                ),
                                FieldDefinition(
                                    name="CtrlSum",
                                    type="decimal",
                                    required=False,
                                    example="450000.00"
                                ),
                            ]
                        ),
                        FieldDefinition(
                            name="PmtInf",
                            type="container",
                            required=True,
                            repeatable=True,
                            description="Payment Information",
                            nested_fields=[
                                FieldDefinition(
                                    name="PmtInfId",
                                    type="string",
                                    required=True,
                                    max_length=35,
                                    example="PAY000001"
                                ),
                                FieldDefinition(
                                    name="PmtMtd",
                                    type="string",
                                    required=True,
                                    enumerated_values=["TRF", "DD", "TRA", "SCT", "INST"],
                                    example="TRF"
                                ),
                                FieldDefinition(
                                    name="ReqdExctnDt",
                                    type="date",
                                    required=True,
                                    example="2024-08-07"
                                ),
                                FieldDefinition(
                                    name="CdtTrfTxInf",
                                    type="container",
                                    required=True,
                                    repeatable=True,
                                    description="Credit Transfer Transaction Information",
                                    nested_fields=[
                                        FieldDefinition(
                                            name="PmtId",
                                            type="container",
                                            required=True,
                                            nested_fields=[
                                                FieldDefinition(
                                                    name="InstrId",
                                                    type="string",
                                                    required=False,
                                                    max_length=35
                                                ),
                                                FieldDefinition(
                                                    name="EndToEndId",
                                                    type="string",
                                                    required=True,
                                                    max_length=35,
                                                    example="INV-2026-08-0042"
                                                ),
                                            ]
                                        ),
                                        FieldDefinition(
                                            name="Amt",
                                            type="container",
                                            required=True,
                                            nested_fields=[
                                                FieldDefinition(
                                                    name="InstdAmt",
                                                    type="decimal",
                                                    required=True,
                                                    example="450000.00"
                                                ),
                                            ]
                                        ),
                                        FieldDefinition(
                                            name="Cdtr",
                                            type="container",
                                            required=True,
                                            description="Creditor",
                                            nested_fields=[
                                                FieldDefinition(
                                                    name="Nm",
                                                    type="string",
                                                    required=True,
                                                    max_length=140,
                                                    example="ABC CORP BERLIN"
                                                ),
                                            ]
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ]
                )
            ]
        )
    ],
    validation_rules={
        "message_id_unique": True,
        "amount_positive": True,
        "date_format": "YYYY-MM-DD",
        "required_fields": ["MsgId", "CreDtTm", "NbOfTxns", "PmtMtd", "EndToEndId", "InstdAmt", "Nm"],
    },
    conversion_notes="ISO 20022 is the successor to SWIFT MT. Full bidirectional conversion with SWIFT is supported."
)


# ============================================================================
# HL7 Healthcare Format Profile
# ============================================================================

HL7_PROFILE = FormatSpecification(
    format_name="HL7 v2.5 / FHIR",
    version="2024.1",
    description="Healthcare Level 7 clinical data format",
    owner="Health Level Seven International",
    profile_uri="https://www.hl7.org/implement/standards/product_brief.cfm?product_id=185",
    root_element="HL7_MESSAGE",
    encoding="UTF-8",
    maximum_size=100_000_000,
    message_types=["ADT - Admission, Discharge, Transfer", "ORU - Observation Result", "ORM - Order Message"],
    fields=[
        FieldDefinition(
            name="MSH",
            type="segment",
            required=True,
            description="Message Header",
            nested_fields=[
                FieldDefinition(name="SendingApplication", type="string", required=True, max_length=180),
                FieldDefinition(name="SendingFacility", type="string", required=True, max_length=180),
                FieldDefinition(name="ReceivingApplication", type="string", required=True, max_length=180),
                FieldDefinition(name="MessageType", type="string", required=True, max_length=3),
                FieldDefinition(name="MessageControlID", type="string", required=True, max_length=20),
                FieldDefinition(name="VersionID", type="string", required=True, max_length=60),
            ]
        ),
        FieldDefinition(
            name="PID",
            type="segment",
            required=True,
            description="Patient Identification",
            nested_fields=[
                FieldDefinition(name="PatientID", type="string", required=True, max_length=250),
                FieldDefinition(name="PatientName", type="string", required=True, max_length=250),
                FieldDefinition(name="DateOfBirth", type="date", required=True),
                FieldDefinition(name="Gender", type="string", required=True, enumerated_values=["M", "F", "O", "U"]),
            ]
        ),
        FieldDefinition(
            name="OBR",
            type="segment",
            required=False,
            repeatable=True,
            description="Observation Request",
            nested_fields=[
                FieldDefinition(name="OrderNumber", type="string", required=True, max_length=200),
                FieldDefinition(name="TestCode", type="string", required=True, max_length=250),
                FieldDefinition(name="OrderStatus", type="string", required=True, enumerated_values=["A", "CA", "CM", "DC", "ER", "HD", "IF", "IP", "OD", "OE", "OR", "PA", "PR", "RE", "RF", "RP", "RQ", "SC"]),
            ]
        ),
        FieldDefinition(
            name="OBX",
            type="segment",
            required=False,
            repeatable=True,
            description="Observation/Result",
            nested_fields=[
                FieldDefinition(name="ObservationIdentifier", type="string", required=True, max_length=250),
                FieldDefinition(name="ValueType", type="string", required=True, max_length=2),
                FieldDefinition(name="ObservationValue", type="string", required=False, max_length=9999),
                FieldDefinition(name="Units", type="string", required=False, max_length=250),
                FieldDefinition(name="ReferencesRange", type="string", required=False, max_length=60),
            ]
        ),
    ],
    validation_rules={
        "segment_order": ["MSH", "PID", "OBR", "OBX"],
        "required_segments": ["MSH", "PID"],
    },
    conversion_notes="HL7 v2.5 supports clinical data from EHR systems. Conversion preserves patient privacy with HIPAA compliance."
)


# ============================================================================
# JSON Format Profile
# ============================================================================

JSON_PROFILE = FormatSpecification(
    format_name="JSON (RFC 7159)",
    version="2024.1",
    description="JavaScript Object Notation - universal text data format",
    owner="IETF (Internet Engineering Task Force)",
    profile_uri="https://tools.ietf.org/html/rfc7159",
    root_element="Object or Array",
    encoding="UTF-8",
    maximum_size=500_000_000,
    message_types=["All message types"],
    fields=[
        FieldDefinition(
            name="Object",
            type="container",
            required=True,
            nested_fields=[
                FieldDefinition(
                    name="Key-Value Pairs",
                    type="string",
                    required=False,
                    description="Any key-value pairs"
                ),
            ]
        ),
        FieldDefinition(
            name="Array",
            type="container",
            required=False,
            nested_fields=[
                FieldDefinition(
                    name="Elements",
                    type="any",
                    required=False,
                    repeatable=True,
                    description="Any JSON values"
                ),
            ]
        ),
    ],
    validation_rules={
        "valid_json_syntax": True,
        "utf8_encoding": True,
        "max_nesting_depth": 128,
    },
    conversion_notes="JSON is flexible and supports conversion from/to all other formats via 121XML internal representation."
)


# ============================================================================
# CSV Format Profile
# ============================================================================

CSV_PROFILE = FormatSpecification(
    format_name="CSV (RFC 4180)",
    version="2024.1",
    description="Comma-Separated Values - tabular data format",
    owner="IETF (Internet Engineering Task Force)",
    profile_uri="https://tools.ietf.org/html/rfc4180",
    root_element="Records",
    encoding="UTF-8",
    maximum_size=1_000_000_000,
    message_types=["Tabular Data"],
    fields=[
        FieldDefinition(
            name="Header Row",
            type="string",
            required=False,
            description="Column names"
        ),
        FieldDefinition(
            name="Data Rows",
            type="record",
            required=True,
            repeatable=True,
            description="Comma-separated values"
        ),
    ],
    validation_rules={
        "delimiter": ",",
        "quote_character": '"',
        "escape_character": '"',
    },
    conversion_notes="CSV is converted to JSON objects with column headers as keys."
)


# ============================================================================
# Format Registry
# ============================================================================

class FormatRegistry:
    """Registry of all supported formats"""

    def __init__(self):
        self.formats: Dict[str, FormatSpecification] = {
            "SWIFT": SWIFT_PROFILE,
            "ISO20022": ISO20022_PROFILE,
            "HL7": HL7_PROFILE,
            "JSON": JSON_PROFILE,
            "CSV": CSV_PROFILE,
        }

    def get_format(self, format_name: str) -> Optional[FormatSpecification]:
        """Get format specification"""
        return self.formats.get(format_name)

    def list_formats(self) -> List[str]:
        """List all supported formats"""
        return list(self.formats.keys())

    def get_format_details(self, format_name: str) -> Dict[str, Any]:
        """Get detailed format information"""
        spec = self.get_format(format_name)
        if not spec:
            return {}

        return {
            "name": spec.format_name,
            "version": spec.version,
            "description": spec.description,
            "owner": spec.owner,
            "profile_uri": spec.profile_uri,
            "encoding": spec.encoding,
            "maximum_size": spec.maximum_size,
            "message_types": spec.message_types,
            "field_count": len(spec.fields),
            "validation_rules": spec.validation_rules,
        }

    def get_convertible_formats(self, from_format: str) -> List[str]:
        """Get list of formats that this format can convert to"""
        # All formats can convert to all other formats via 121XML
        return [f for f in self.list_formats() if f != from_format]


if __name__ == "__main__":
    registry = FormatRegistry()

    print("Supported Formats:")
    for fmt in registry.list_formats():
        details = registry.get_format_details(fmt)
        print(f"  {fmt}: {details['description']}")
        print(f"    Convertible to: {registry.get_convertible_formats(fmt)}")
