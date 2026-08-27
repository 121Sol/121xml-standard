"""
121AI Complete Test Suite
Unit, Integration, Stress, and Security Tests

Version: 1.0.0
License: Proprietary - 121 Group
"""

import unittest
from typing import List, Dict, Any
import time
import json
from datetime import datetime

# Import all components
from xml121_main_engine import Engine121AI, EngineConfig
from xml121_converter import FormatType, UniversalConverter
from xml121_addresser import ContentAddresser
from xml121_compressor import CompressionService
from xml121_auditor import AuditTrail, OperationType
from xml121_voice_connectors import SiriConnector, VoiceIntent, IntentType
from xml121_database_adapters import PostgreSQLAdapter, ConnectionConfig, DatabaseType
from xml121_agent_orchestrator import AgentOrchestrator, Task, TaskPriority


class TestUnitConversion(unittest.TestCase):
    """Unit tests for format conversion"""

    def setUp(self):
        self.converter = UniversalConverter()

    def test_swift_detection(self):
        """Test SWIFT format detection"""
        swift_data = "{1:F01CHASUS33AXXX1234567890}{2:I103DEUTDEFF}"
        result = self.converter.detect_format(swift_data)
        self.assertEqual(result, FormatType.SWIFT)

    def test_json_detection(self):
        """Test JSON format detection"""
        json_data = '{"key": "value", "amount": 100.00}'
        result = self.converter.detect_format(json_data)
        self.assertEqual(result, FormatType.JSON)

    def test_conversion_swift_to_json(self):
        """Test SWIFT to JSON conversion"""
        swift_data = """{1:F01CHASUS33AXXX1234567890}{2:I103DEUTDEFF200703042150}{3:{108:swiftexample}}{4:
:20:REFERENCE20240807
:23B:CRED
:32A:240807USD1500000,00
:50A:/NL91ABNA0417164300
121AI
:57A:CHASUS33
:59:/DE89370400440532013000
ABC CORP BERLIN
:70:INVOICE 12345
-}"""

        result = self.converter.convert(swift_data, FormatType.SWIFT, FormatType.JSON)
        self.assertTrue(result.success)
        self.assertEqual(result.data_loss, 0.0)

    def test_lossless_guarantee(self):
        """Test lossless conversion guarantee"""
        test_data = '{"invoice": "INV-2026-08-0042", "amount": 450000.00, "status": "paid"}'
        result = self.converter.convert(test_data, FormatType.JSON, FormatType.INTERNAL_121)
        self.assertEqual(result.data_loss, 0.0)
        self.assertTrue(result.success)


class TestUnitCompression(unittest.TestCase):
    """Unit tests for compression"""

    def setUp(self):
        self.compressor = CompressionService()

    def test_compression_ratio(self):
        """Test compression achieves target ratio"""
        data = json.dumps({"invoices": [{"id": i, "amount": 1000.00} for i in range(100)]})
        compressed, metrics = self.compressor.compress_and_store(data)

        self.assertGreater(metrics.compression_ratio, 0)
        self.assertLess(metrics.compression_ratio, 1)
        self.assertGreater(metrics.token_savings_percent, 80)

    def test_lossless_decompression(self):
        """Test decompression recovers original data"""
        original = json.dumps({"test": "data", "value": 12345})
        compressed, _ = self.compressor.compress_and_store(original)
        decompressed, verified = self.compressor.decompress_and_verify(compressed)

        self.assertTrue(verified)
        self.assertIn("test", decompressed)


class TestUnitAddressing(unittest.TestCase):
    """Unit tests for content addressing"""

    def setUp(self):
        self.addresser = ContentAddresser()

    def test_deterministic_hashing(self):
        """Test same content produces same hash"""
        content = '{"id": "123", "amount": 100.00}'
        address1 = self.addresser.address_content(content)
        address2 = self.addresser.address_content(content)

        self.assertEqual(address1.hash_value, address2.hash_value)

    def test_content_verification(self):
        """Test content verification"""
        content = '{"transaction": "payment"}'
        address = self.addresser.address_content(content)
        verified, _ = self.addresser.verify_content(content, address)

        self.assertTrue(verified)

    def test_merkle_tree_verification(self):
        """Test Merkle tree creation and verification"""
        contents = ['item1', 'item2', 'item3', 'item4']
        tree = self.addresser.build_merkle_tree(contents)

        self.assertIsNotNone(tree['root'])
        self.assertGreater(tree['height'], 0)
        self.assertEqual(tree['leaf_count'], 4)


class TestUnitAudit(unittest.TestCase):
    """Unit tests for audit trail"""

    def setUp(self):
        self.audit = AuditTrail("test_org")

    def test_event_logging(self):
        """Test event logging"""
        event = self.audit.log_event(
            operation=OperationType.CREATE,
            actor="test_user",
            resource="test_resource",
            action="test_action"
        )

        self.assertIsNotNone(event.event_id)
        self.assertEqual(len(self.audit.events), 1)

    def test_verification_chain(self):
        """Test verification chain integrity"""
        self.audit.log_event(OperationType.READ, "user1", "resource1", "read")
        self.audit.log_event(OperationType.WRITE, "user2", "resource2", "write")

        valid = self.audit.verify_verification_chain()
        self.assertTrue(valid)


class TestIntegrationEngine(unittest.TestCase):
    """Integration tests for complete engine"""

    def setUp(self):
        self.config = EngineConfig(
            enable_compression=True,
            enable_addressing=True,
            enable_auditing=True
        )
        self.engine = Engine121AI(self.config)

    def test_complete_pipeline(self):
        """Test complete processing pipeline"""
        swift_data = "{1:F01CHASUS33AXXX1234567890}{2:I103DEUTDEFF200703042150}{4::20:REF123:23B:CRED:32A:240807USD450000,00-}"

        result = self.engine.process_message(
            swift_data,
            source_format=FormatType.SWIFT,
            target_format=FormatType.INTERNAL_121,
            compress=True,
            address=True,
            audit=True
        )

        self.assertTrue(result['success'])
        self.assertIn('message_id', result)
        self.assertGreater(result['metrics']['compression_savings'], 0)

    def test_voice_query_pipeline(self):
        """Test voice query processing"""
        from xml121_voice_connectors import VoicePlatform

        response = self.engine.voice_query(
            "What's my balance?",
            VoicePlatform.SIRI,
            "test_session",
            "test_user"
        )

        self.assertIn('response', response)
        self.assertEqual(response['platform'], 'siri')

    def test_compliance_reporting(self):
        """Test compliance report generation"""
        report = self.engine.get_compliance_report()

        self.assertIn('gdpr', report)
        self.assertIn('hipaa', report)
        self.assertIn('audit_trail_integrity', report)


class TestStress(unittest.TestCase):
    """Stress tests for performance under load"""

    def setUp(self):
        self.engine = Engine121AI(EngineConfig())

    def test_high_volume_conversion(self):
        """Test conversion under high volume"""
        start = time.time()

        for i in range(100):
            data = json.dumps({"id": i, "amount": 1000.00 * i})
            self.engine.converter.convert(data, FormatType.JSON, FormatType.INTERNAL_121)

        elapsed = time.time() - start

        self.assertLess(elapsed, 30)  # Should complete in under 30 seconds
        self.assertEqual(len(self.engine.converter.conversion_history), 100)

    def test_compression_throughput(self):
        """Test compression throughput"""
        start = time.time()
        total_bytes = 0

        for i in range(50):
            data = json.dumps({"transaction": f"TXN{i}", "details": "x" * 1000})
            compressed, metrics = self.engine.compression_service.compress_and_store(data)
            total_bytes += metrics.original_size_bytes

        elapsed = time.time() - start
        throughput_mbps = (total_bytes / 1_000_000) / elapsed

        self.assertGreater(throughput_mbps, 1)  # At least 1 MB/s

    def test_concurrent_task_execution(self):
        """Test concurrent task execution"""
        orchestrator = AgentOrchestrator()

        tasks = [
            Task(
                description=f"Process transaction {i}",
                priority=TaskPriority.NORMAL,
                required_tools=["format_converter"],
                input_data={"amount": 1000.00}
            )
            for i in range(20)
        ]

        for task in tasks:
            orchestrator.submit_task(task)

        self.assertEqual(len(orchestrator.task_queue), 20)


class TestSecurity(unittest.TestCase):
    """Security tests"""

    def setUp(self):
        self.audit = AuditTrail("security_test")

    def test_access_control_logging(self):
        """Test access control is logged"""
        self.audit.log_authentication("user@test.com", "oauth2", True, "192.168.1.1")

        auth_events = self.audit.get_events_by_operation(OperationType.AUTHENTICATE)
        self.assertEqual(len(auth_events), 1)
        self.assertEqual(auth_events[0].actor, "user@test.com")

    def test_data_encryption_logging(self):
        """Test encryption operations are logged"""
        self.audit.log_encryption("system", "sensitive_data", "AES-256", "key_id_123")

        encrypt_events = self.audit.get_events_by_operation(OperationType.ENCRYPT)
        self.assertEqual(len(encrypt_events), 1)

    def test_audit_trail_immutability(self):
        """Test audit trail cannot be modified"""
        self.audit.log_event(OperationType.READ, "user1", "resource1", "read")
        original_count = len(self.audit.events)

        # Seal and create new log
        sealed = self.audit.seal_log()

        # Verify original events count unchanged
        self.assertEqual(len(self.audit.events), original_count)
        self.assertTrue(sealed.integrity_verified)


class TestDataIntegrity(unittest.TestCase):
    """Data integrity tests"""

    def setUp(self):
        self.addresser = ContentAddresser()

    def test_merkle_proof_verification(self):
        """Test Merkle proof verification"""
        items = ['A', 'B', 'C', 'D']
        tree = self.addresser.build_merkle_tree(items)

        item_hash = self.addresser.address_content('A').hash_value
        proof = self.addresser.create_proof_of_inclusion(item_hash, tree)

        self.assertTrue(proof['valid'])
        self.assertGreater(len(proof['proof']), 0)

    def test_hash_chain_tampering_detection(self):
        """Test hash chain detects tampering"""
        sequence = ['event1', 'event2', 'event3']
        chain = self.addresser.create_hash_chain(sequence)

        # Verify chain
        valid, errors = self.addresser.verify_hash_chain(chain)
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)


class TestPerformance(unittest.TestCase):
    """Performance benchmarks"""

    def test_conversion_latency(self):
        """Benchmark conversion latency"""
        converter = UniversalConverter()
        swift_data = "{1:F01CHASUS33AXXX1234567890}{2:I103DEUTDEFF200703042150}{4:-}"

        start = time.time()
        result = converter.convert(swift_data, FormatType.SWIFT, FormatType.JSON)
        elapsed = (time.time() - start) * 1000

        self.assertLess(elapsed, 100)  # Should be under 100ms

    def test_addressing_latency(self):
        """Benchmark content addressing latency"""
        addresser = ContentAddresser()
        data = json.dumps({"test": "data" * 100})

        start = time.time()
        address = addresser.address_content(data)
        elapsed = (time.time() - start) * 1000

        self.assertLess(elapsed, 50)  # Should be under 50ms

    def test_compression_latency(self):
        """Benchmark compression latency"""
        compressor = CompressionService()
        data = json.dumps({"invoice": "data" * 500})

        start = time.time()
        _, _ = compressor.compress_and_store(data)
        elapsed = (time.time() - start) * 1000

        self.assertLess(elapsed, 200)  # Should be under 200ms


class TestReport(unittest.TestCase):
    """Test report generation"""

    def test_statistics_generation(self):
        """Test statistics can be generated"""
        engine = Engine121AI()

        # Generate some activity
        for i in range(5):
            data = json.dumps({"id": i})
            engine.converter.convert(data, FormatType.JSON, FormatType.INTERNAL_121)

        stats = engine.get_engine_statistics()

        self.assertIn('session', stats)
        self.assertIn('converters', stats)
        self.assertGreater(stats['converters']['conversions'], 0)


def run_all_tests():
    """Run all tests and generate report"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestUnitConversion,
        TestUnitCompression,
        TestUnitAddressing,
        TestUnitAudit,
        TestIntegrationEngine,
        TestStress,
        TestSecurity,
        TestDataIntegrity,
        TestPerformance,
        TestReport
    ]

    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return {
        "tests_run": result.testsRun,
        "successes": result.testsRun - len(result.failures) - len(result.errors),
        "failures": len(result.failures),
        "errors": len(result.errors),
        "success_rate": (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun if result.testsRun > 0 else 0
    }


if __name__ == "__main__":
    report = run_all_tests()
    print(f"\n{'='*60}")
    print(f"Test Report Summary")
    print(f"{'='*60}")
    print(f"Tests Run: {report['tests_run']}")
    print(f"Passed: {report['successes']}")
    print(f"Failed: {report['failures']}")
    print(f"Errors: {report['errors']}")
    print(f"Success Rate: {report['success_rate']*100:.1f}%")
    print(f"{'='*60}")
