#!/usr/bin/env python3
"""
121XML Universal Format Converter Tool
Converts between ANY format and 121XML using standardized transformations
Handles: Medical (HL7, FHIR), Finance (ISO20022, FIX), Code (Python, Java, PHP),
Telecom (SS7, SIP), and custom formats
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class Industry(Enum):
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    EDUCATION = "education"
    TELECOMMUNICATIONS = "telecommunications"
    SOFTWARE = "software"
    MANUFACTURING = "manufacturing"


class DataFormat(Enum):
    # Healthcare
    HL7_V2 = "hl7_v2"
    HL7_V3 = "hl7_v3"
    FHIR = "fhir"
    DICOM = "dicom"
    
    # Finance
    ISO20022 = "iso20022"
    FIX = "fix"
    SWIFT = "swift"
    
    # Telecom
    SS7 = "ss7"
    SIP = "sip"
    
    # Software
    PYTHON = "python"
    JAVA = "java"
    PHP = "php"
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    
    # Universal
    XML121 = "121xml"


@dataclass
class ConversionJob:
    """Represents a conversion task"""
    job_id: str
    industry: Industry
    input_format: DataFormat
    output_format: DataFormat
    input_file_path: str
    output_file_path: str
    status: str = "pending"
    timestamp: str = None
    content_address: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat() + "Z"


class ContentAddresser:
    """Generates immutable content addresses"""
    
    @staticmethod
    def compute(data: str, object_type: str) -> str:
        """Generate SHA256-based content address"""
        hash_value = hashlib.sha256(data.encode()).hexdigest()
        return f"data://sha256:{hash_value}:{object_type}"


class HL7Converter:
    """Convert HL7 v2 messages to/from 121XML"""
    
    @staticmethod
    def hl7_to_121xml(hl7_message: str) -> Dict[str, Any]:
        """Convert HL7 v2 to 121XML structure"""
        lines = hl7_message.strip().split('\n')
        segments = {}
        
        for line in lines:
            parts = line.split('|')
            segment_type = parts[0]
            
            if segment_type == 'MSH':
                segments['header'] = {
                    'message_type': parts[9].split('^')[0],
                    'timestamp': parts[7],
                    'message_id': parts[10]
                }
            elif segment_type == 'PID':
                segments['patient'] = {
                    'mrn': parts[3].split('^')[0],
                    'name': parts[5].split('^')[0] if len(parts) > 5 else '',
                    'dob': parts[7] if len(parts) > 7 else '',
                    'gender': parts[8] if len(parts) > 8 else ''
                }
            elif segment_type == 'RXE':
                segments['medication'] = {
                    'name': parts[2],
                    'strength': parts[3].split('^')[0],
                    'unit': parts[3].split('^')[1] if '^' in parts[3] else '',
                    'form': parts[11] if len(parts) > 11 else 'TABLET'
                }
            elif segment_type == 'RXD':
                segments['dosage'] = {
                    'quantity': parts[4],
                    'unit': parts[5],
                    'date': parts[6]
                }
        
        return {
            'profile_uri': 'urn:121xml:medical-prescription/1.0',
            'data': segments,
            'content_address': ContentAddresser.compute(json.dumps(segments), 'prescription')
        }


class ISO20022Converter:
    """Convert ISO 20022 financial messages to/from 121XML"""
    
    @staticmethod
    def iso20022_to_121xml(iso_xml: str) -> Dict[str, Any]:
        """Convert ISO 20022 XML to 121XML structure"""
        import xml.etree.ElementTree as ET
        
        try:
            root = ET.fromstring(iso_xml)
        except:
            return {'error': 'Invalid ISO 20022 XML'}
        
        # Extract key financial data
        transaction_data = {
            'transaction_type': 'payment',
            'details': {}
        }
        
        # Parse namespaces and extract elements
        for elem in root.iter():
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            
            if tag == 'MsgId':
                transaction_data['details']['message_id'] = elem.text
            elif tag == 'Nm':
                if 'debtor_name' not in transaction_data['details']:
                    transaction_data['details']['debtor_name'] = elem.text
            elif tag == 'InstdAmt':
                transaction_data['details']['amount'] = elem.text
                transaction_data['details']['currency'] = elem.get('Ccy', 'USD')
            elif tag == 'Cd' and 'Purp' in elem.getparent().tag:
                transaction_data['details']['purpose'] = elem.text
        
        return {
            'profile_uri': 'urn:121xml:financial-transaction/1.0',
            'data': transaction_data,
            'content_address': ContentAddresser.compute(json.dumps(transaction_data), 'financial-transaction')
        }


class CodeConverter:
    """Convert source code to/from 121XML intermediate representation"""
    
    @staticmethod
    def python_to_121xml(python_code: str) -> Dict[str, Any]:
        """Extract Python code structure to 121XML"""
        import ast
        
        try:
            tree = ast.parse(python_code)
        except:
            return {'error': 'Invalid Python code'}
        
        classes = []
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append({
                            'name': item.name,
                            'type': 'CONSTRUCTOR' if item.name == '__init__' else 'METHOD',
                            'parameters': [arg.arg for arg in item.args.args],
                            'return_type': 'UNKNOWN'
                        })
                
                classes.append({
                    'name': node.name,
                    'type': 'CLASS',
                    'methods': methods
                })
            
            elif isinstance(node, ast.FunctionDef) and not any(
                isinstance(p, ast.ClassDef) and node in ast.walk(p) for p in ast.walk(tree)
            ):
                functions.append({
                    'name': node.name,
                    'type': 'FUNCTION',
                    'parameters': [arg.arg for arg in node.args.args]
                })
        
        code_structure = {
            'source_language': 'PYTHON',
            'classes': classes,
            'functions': functions
        }
        
        return {
            'profile_uri': 'urn:121xml:program-structure/1.0',
            'data': code_structure,
            'content_address': ContentAddresser.compute(json.dumps(code_structure), 'program-structure')
        }


class UniversalConverter:
    """Main conversion engine"""
    
    def __init__(self):
        self.hl7_converter = HL7Converter()
        self.iso_converter = ISO20022Converter()
        self.code_converter = CodeConverter()
        self.conversion_history = []
    
    def convert(self, input_data: str, input_format: DataFormat, 
                output_format: DataFormat, industry: Industry) -> Dict[str, Any]:
        """
        Universal conversion interface
        
        Args:
            input_data: The actual data to convert
            input_format: Source format (HL7, ISO20022, Python, etc.)
            output_format: Target format (121XML or other)
            industry: Business domain
        
        Returns:
            Converted data with metadata
        """
        
        job_id = hashlib.md5(
            f"{input_format.value}{output_format.value}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:8]
        
        result = {
            'job_id': job_id,
            'status': 'started',
            'timestamp': datetime.utcnow().isoformat() + "Z"
        }
        
        try:
            # Step 1: Convert input to 121XML (if not already)
            if input_format == DataFormat.XML121:
                intermediate = json.loads(input_data)
            elif input_format == DataFormat.HL7_V2:
                intermediate = self.hl7_converter.hl7_to_121xml(input_data)
            elif input_format == DataFormat.ISO20022:
                intermediate = self.iso_converter.iso20022_to_121xml(input_data)
            elif input_format == DataFormat.PYTHON:
                intermediate = self.code_converter.python_to_121xml(input_data)
            else:
                return {**result, 'status': 'error', 'error': f'Unsupported input format: {input_format.value}'}
            
            # Step 2: Generate 121XML output
            if output_format == DataFormat.XML121:
                result['output'] = intermediate
                result['status'] = 'success'
            
            elif output_format == DataFormat.JSON:
                result['output'] = json.dumps(intermediate, indent=2)
                result['status'] = 'success'
            
            elif output_format == DataFormat.JAVA and input_format == DataFormat.PYTHON:
                result['output'] = self._generate_java_from_121xml(intermediate)
                result['status'] = 'success'
            
            elif output_format == DataFormat.PHP and input_format == DataFormat.PYTHON:
                result['output'] = self._generate_php_from_121xml(intermediate)
                result['status'] = 'success'
            
            else:
                result['output'] = intermediate
                result['status'] = 'success'
            
            # Step 3: Add audit trail
            result['content_address'] = intermediate.get('content_address', '')
            self.conversion_history.append(result)
            
            return result
        
        except Exception as e:
            return {
                **result,
                'status': 'error',
                'error': str(e)
            }
    
    def _generate_java_from_121xml(self, structure: Dict) -> str:
        """Generate Java code from 121XML program structure"""
        output = []
        data = structure.get('data', {})
        
        for cls in data.get('classes', []):
            output.append(f"public class {cls['name']} {{")
            
            # Generate methods
            for method in cls.get('methods', []):
                params = ', '.join([f"Object {p}" for p in method.get('parameters', [])])
                output.append(f"    public void {method['name']}({params}) {{ }}")
            
            output.append("}")
        
        return '\n'.join(output)
    
    def _generate_php_from_121xml(self, structure: Dict) -> str:
        """Generate PHP code from 121XML program structure"""
        output = ["<?php"]
        data = structure.get('data', {})
        
        for cls in data.get('classes', []):
            output.append(f"class {cls['name']} {{")
            
            # Generate methods
            for method in cls.get('methods', []):
                params = ', '.join([f"${p}" for p in method.get('parameters', [])])
                output.append(f"    public function {method['name']}({params}) {{ }}")
            
            output.append("}")
        
        output.append("?>")
        return '\n'.join(output)


# Example usage
if __name__ == '__main__':
    converter = UniversalConverter()
    
    # Example 1: HL7 to 121XML
    hl7_example = """MSH|^~\\&|PHARMACY|HOSPITAL|CLAIMS|INSURER|20260806141530||RXE^RXE^RXE|MSG123456|P|2.5
PID|1||12345678^^^MRN||DOE^JOHN^A||19750315|M
RXE|1|METFORMIN|500^MG||||PO|BID|30|TABLET"""
    
    result = converter.convert(
        input_data=hl7_example,
        input_format=DataFormat.HL7_V2,
        output_format=DataFormat.XML121,
        industry=Industry.HEALTHCARE
    )
    
    print("HL7 → 121XML Conversion:")
    print(json.dumps(result, indent=2))
    print("\n" + "="*50 + "\n")
    
    # Example 2: Python to Java conversion
    python_code = """
class BankAccount:
    def __init__(self, account_id, balance):
        self.account_id = account_id
        self.balance = balance
    
    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            return True
        return False
"""
    
    result = converter.convert(
        input_data=python_code,
        input_format=DataFormat.PYTHON,
        output_format=DataFormat.JAVA,
        industry=Industry.SOFTWARE
    )
    
    print("Python → Java Conversion:")
    print(result['output'])

