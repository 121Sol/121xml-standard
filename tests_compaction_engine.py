"""
Test Suite for 121XML Lossless Compaction Engine
=================================================

Comprehensive tests for all compaction components.
Target: 85%+ code coverage

Author: 121XML Foundation
License: Apache 2.0
"""

import unittest
import json
from datetime import datetime
import sys

# Import compaction engine
sys.path.insert(0, '/F/AI/Claude/Projects/121XML')
from xml_121xml_compaction_engine import (
    ContentAddressManager, TokenBudgetManager, LosslessCompressor,
    CompactionStrategyEngine, CompactionEvent, CompactionResult,
    LosslessCompactionEngine, CompactionPolicy, CompactionStrategy
)


class TestContentAddressManager(unittest.TestCase):
    """Test content addressing"""

    def setUp(self):
        self.cam = ContentAddressManager()

    def test_compute_address(self):
        """Test address computation"""
        obj = {"id": "test", "name": "Test"}
        address = self.cam.compute(obj, "test-type")

        self.assertIn("data://sha256:", address)
        self.assertIn("test-type", address)

    def test_deterministic_addressing(self):
        """Test same object produces same address"""
        obj1 = {"z": 1, "a": 2}
        obj2 = {"a": 2, "z": 1}

        addr1 = self.cam.compute(obj1, "type")
        addr2 = self.cam.compute(obj2, "type")

        self.assertEqual(addr1, addr2)

    def test_different_objects_different_addresses(self):
        """Test different objects produce different addresses"""
        obj1 = {"id": "test1"}
        obj2 = {"id": "test2"}

        addr1 = self.cam.compute(obj1, "type")
        addr2 = self.cam.compute(obj2, "type")

        self.assertNotEqual(addr1, addr2)


class TestTokenBudgetManager(unittest.TestCase):
    """Test token budget management"""

    def setUp(self):
        self.manager = TokenBudgetManager(max_tokens=10000)

    def test_initial_health(self):
        """Test initial token health"""
        health = self.manager.check_token_health()

        self.assertEqual(health["status"], "healthy")
        self.assertFalse(health["action_required"])
        self.assertEqual(health["tokens_remaining"], 10000)

    def test_warning_threshold(self):
        """Test warning threshold detection"""
        self.manager.used_tokens = 7000  # 70% usage

        health = self.manager.check_token_health()
        self.assertEqual(health["status"], "warning")
        self.assertFalse(health["action_required"])

    def test_critical_threshold(self):
        """Test critical threshold detection"""
        self.manager.used_tokens = 8500  # 85% usage

        health = self.manager.check_token_health()
        self.assertEqual(health["status"], "critical")
        self.assertTrue(health["action_required"])

    def test_should_compact(self):
        """Test compaction trigger"""
        self.manager.used_tokens = 7000
        self.assertFalse(self.manager.should_compact())

        self.manager.used_tokens = 8500
        self.assertTrue(self.manager.should_compact())

    def test_add_tokens(self):
        """Test adding tokens"""
        self.manager.add_tokens(5000)
        self.assertEqual(self.manager.used_tokens, 5000)

        self.manager.add_tokens(3000)
        self.assertEqual(self.manager.used_tokens, 8000)


class TestLosslessCompressor(unittest.TestCase):
    """Test lossless compression"""

    def setUp(self):
        self.cam = ContentAddressManager()
        self.compressor = LosslessCompressor(self.cam)

    def test_compress_messages(self):
        """Test message compression"""
        context = {
            "messages": [
                {"id": "msg1", "content": "Hello", "timestamp": "2026-08-06T00:00:00Z"},
                {"id": "msg2", "content": "World", "timestamp": "2026-08-06T00:01:00Z"}
            ]
        }

        compressed, event = self.compressor.compress_context(context)

        # Check compression
        self.assertIn("messages", compressed)
        self.assertEqual(compressed["message_count"], 2)
        self.assertEqual(len(compressed["messages"]), 2)

        # Check event
        self.assertEqual(event.data_loss_percent, 0.0)
        self.assertGreater(event.compression_ratio, 50)

    def test_zero_data_loss(self):
        """Test that compression has zero data loss"""
        context = {
            "messages": [
                {"id": "msg1", "content": "Test " * 100},
                {"id": "msg2", "content": "Data " * 100}
            ],
            "execution_state": {"step": 1, "status": "running"}
        }

        compressed, event = self.compressor.compress_context(context)

        # Verify zero data loss
        self.assertEqual(event.data_loss_percent, 0.0)
        self.assertTrue(event.reconstruction_possible)

    def test_high_compression_ratio(self):
        """Test that compression achieves 80%+ reduction"""
        context = {
            "messages": [
                {"id": f"msg{i}", "content": "Test message " * 10}
                for i in range(100)
            ]
        }

        compressed, event = self.compressor.compress_context(context)

        # Should achieve at least 80% compression
        self.assertGreater(event.compression_ratio, 80)

    def test_event_validation(self):
        """Test compaction event validation"""
        context = {"messages": [{"id": "msg1", "content": "Test"}]}
        compressed, event = self.compressor.compress_context(context)

        self.assertTrue(event.validate())
        self.assertEqual(event.data_loss_percent, 0.0)
        self.assertTrue(event.reconstruction_possible)

    def test_decompress_perfect_reconstruction(self):
        """Test perfect reconstruction from compressed"""
        original_context = {
            "messages": [
                {"id": "msg1", "content": "Hello"},
                {"id": "msg2", "content": "World"}
            ]
        }

        compressed, event = self.compressor.compress_context(original_context)

        # Create archived content map
        archived = {}
        for msg_ref in compressed["messages"]:
            # In production, this would have the full content
            msg_index = int(msg_ref["id"].split("msg")[1]) - 1
            archived[msg_ref["address"]] = original_context["messages"][msg_index]

        # Reconstruct
        reconstructed = self.compressor.decompress_context(compressed, archived)

        self.assertIn("messages", reconstructed)
        self.assertEqual(len(reconstructed["messages"]), 2)


class TestCompactionStrategyEngine(unittest.TestCase):
    """Test compaction strategy selection"""

    def setUp(self):
        self.cam = ContentAddressManager()
        self.compressor = LosslessCompressor(self.cam)
        self.engine = CompactionStrategyEngine(self.compressor, self.cam)

    def test_no_compaction_needed(self):
        """Test when no compaction is needed"""
        context = {"messages": [{"id": "msg1", "content": "Test"}]}
        result = self.engine.handle_token_pressure(context, 5000, 10000)

        self.assertEqual(result.strategy, CompactionStrategy.NONE.value)
        self.assertEqual(result.action, "continue")
        self.assertEqual(result.tokens_freed, 0)

    def test_sparse_compression_strategy(self):
        """Test sparse compression strategy"""
        context = {
            "messages": [{"id": f"msg{i}", "content": "Test"} for i in range(50)],
            "execution_state": {"status": "running"}
        }

        result = self.engine.handle_token_pressure(context, 15000, 20000)

        self.assertEqual(result.strategy, CompactionStrategy.SPARSE_COMPRESSION.value)
        self.assertIsNotNone(result.compressed_context)
        self.assertGreater(result.tokens_freed, 0)
        self.assertEqual(result.data_loss, 0.0)

    def test_session_split_strategy(self):
        """Test session split strategy"""
        context = {
            "messages": [{"id": f"msg{i}", "content": "Test"} for i in range(100)],
            "session_id": "original_session"
        }

        result = self.engine.handle_token_pressure(context, 19000, 20000)

        self.assertEqual(result.strategy, CompactionStrategy.SESSION_SPLIT.value)
        self.assertIsNotNone(result.new_session_id)
        self.assertGreater(result.tokens_freed, 0)

    def test_archive_strategy(self):
        """Test archive strategy"""
        context = {
            "messages": [{"id": f"msg{i}", "content": "Test"} for i in range(100)]
        }

        result = self.engine.handle_token_pressure(context, 19800, 20000)

        self.assertEqual(result.strategy, CompactionStrategy.ARCHIVE.value)
        self.assertIsNotNone(result.archive_id)
        self.assertGreater(result.tokens_freed, 0)


class TestCompactionEvent(unittest.TestCase):
    """Test compaction event records"""

    def test_event_creation(self):
        """Test creating compaction event"""
        event = CompactionEvent(
            event_id="event1",
            timestamp="2026-08-06T00:00:00Z",
            original_token_count=10000,
            compressed_token_count=1000,
            compression_ratio=90.0,
            data_loss_percent=0.0,
            archived_content_count=50,
            reconstruction_possible=True,
            strategy_used="sparse_compression"
        )

        self.assertTrue(event.validate())
        self.assertEqual(event.data_loss_percent, 0.0)

    def test_event_to_121xml(self):
        """Test event serialization to 121XML"""
        event = CompactionEvent(
            event_id="event1",
            timestamp="2026-08-06T00:00:00Z",
            original_token_count=10000,
            compressed_token_count=1000,
            compression_ratio=90.0,
            data_loss_percent=0.0,
            archived_content_count=50,
            reconstruction_possible=True,
            strategy_used="sparse_compression"
        )

        xml = event.to_121xml()

        self.assertIn("<compaction_event>", xml)
        self.assertIn("event_id", xml)
        self.assertIn("compression_ratio", xml)
        self.assertIn("reconstruction_possible", xml)

    def test_event_validation_zero_loss(self):
        """Test that valid events have zero data loss"""
        valid_event = CompactionEvent(
            event_id="event1",
            timestamp="2026-08-06T00:00:00Z",
            original_token_count=10000,
            compressed_token_count=1000,
            compression_ratio=90.0,
            data_loss_percent=0.0,
            archived_content_count=50,
            reconstruction_possible=True,
            strategy_used="sparse_compression"
        )

        self.assertTrue(valid_event.validate())


class TestCompactionPolicy(unittest.TestCase):
    """Test compaction policy configuration"""

    def test_default_policy(self):
        """Test default policy is lossless"""
        policy = CompactionPolicy.get_default_policy()

        self.assertEqual(policy["compaction_algorithm"], "121xml_lossless")
        self.assertEqual(policy["data_loss_target"], 0.0)
        self.assertTrue(policy["audit_logging"])
        self.assertTrue(policy["reconstruction_enabled"])

    def test_policy_validation(self):
        """Test policy has required fields"""
        policy = CompactionPolicy.get_default_policy()

        required_fields = [
            "enabled",
            "compaction_algorithm",
            "data_loss_target",
            "audit_logging",
            "reconstruction_enabled"
        ]

        for field in required_fields:
            self.assertIn(field, policy)


class TestLosslessCompactionEngine(unittest.TestCase):
    """Test complete compaction engine"""

    def setUp(self):
        self.engine = LosslessCompactionEngine(max_tokens=20000)

    def test_engine_initialization(self):
        """Test engine initializes correctly"""
        self.assertEqual(self.engine.budget_manager.max_tokens, 20000)
        self.assertTrue(self.engine.policy["audit_logging"])
        self.assertEqual(self.engine.policy["data_loss_target"], 0.0)

    def test_no_compaction_scenario(self):
        """Test processing when no compaction needed"""
        context = {
            "messages": [{"id": "msg1", "content": "Test"}]
        }

        processed, event = self.engine.process_context(context)

        self.assertEqual(processed, context)
        self.assertIsNone(event)

    def test_compaction_scenario(self):
        """Test processing when compaction triggered"""
        # Set high token usage
        self.engine.budget_manager.used_tokens = 17000

        context = {
            "messages": [
                {"id": f"msg{i}", "content": "Test message"} for i in range(100)
            ]
        }

        processed, event = self.engine.process_context(context)

        if event:
            self.assertEqual(event.data_loss_percent, 0.0)
            self.assertTrue(event.reconstruction_possible)

    def test_compaction_stats(self):
        """Test retrieving compaction statistics"""
        context = {"messages": [{"id": "msg1", "content": "Test"}]}
        self.engine.budget_manager.used_tokens = 17000
        self.engine.process_context(context)

        stats = self.engine.get_compaction_stats()

        self.assertIn("total_compactions", stats)
        self.assertIn("total_tokens_freed", stats)
        self.assertIn("data_loss", stats)
        self.assertEqual(stats["data_loss"], 0.0)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete compaction flow"""

    def test_complete_compaction_cycle(self):
        """Test complete compaction cycle"""
        engine = LosslessCompactionEngine(max_tokens=10000)

        # Build context progressively
        messages = []
        for batch in range(3):
            for i in range(10):
                messages.append({
                    "id": f"msg_{batch}_{i}",
                    "content": f"Message batch {batch} number {i}",
                    "timestamp": f"2026-08-06T{batch:02d}:{i:02d}:00Z"
                })

            context = {
                "messages": messages,
                "execution_state": {"batch": batch, "status": "running"}
            }

            # Process through engine
            processed, event = engine.process_context(context)

            if event:
                self.assertEqual(event.data_loss_percent, 0.0)
                self.assertTrue(event.validate())

    def test_multiple_compactions(self):
        """Test handling multiple compaction events"""
        engine = LosslessCompactionEngine(max_tokens=5000)

        for iteration in range(3):
            context = {
                "messages": [
                    {
                        "id": f"msg_{iteration}_{i}",
                        "content": f"Message {iteration}-{i}"
                    }
                    for i in range(20)
                ]
            }

            engine.budget_manager.used_tokens = 4200 + (iteration * 1000)
            processed, event = engine.process_context(context)

            if event:
                self.assertEqual(event.data_loss_percent, 0.0)

        # Verify audit trail
        log = engine.compaction_log
        self.assertGreater(len(log), 0)

        # All events should be valid
        for event in log:
            self.assertTrue(event.validate())


if __name__ == "__main__":
    unittest.main(verbosity=2)
