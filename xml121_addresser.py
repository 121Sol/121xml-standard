"""
121XML Content Addressing System
SHA256-based immutable addressing for perfect data reconstruction

Version: 1.0.0
License: Proprietary - 121 Group
"""

import hashlib
import json
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
import base64


@dataclass
class ContentAddress:
    """Content-addressed reference"""
    hash_type: str = "sha256"
    hash_value: str = ""
    content_type: str = ""
    size_bytes: int = 0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def address_uri(self) -> str:
        """Generate content:// URI"""
        return f"content://{self.hash_type}:{self.hash_value}"

    @property
    def data_uri(self) -> str:
        """Generate data:// URI"""
        return f"data://{self.hash_type}:{self.hash_value}:{self.content_type}"


@dataclass
class AddressingRecord:
    """Record of content addressing operation"""
    address: ContentAddress
    original_hash: str = ""
    transformation_chain: List[str] = field(default_factory=list)
    verified: bool = False
    verification_timestamp: str = ""
    archive_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContentAddresser:
    """Universal content addressing system"""

    def __init__(self, hash_algorithm: str = "sha256"):
        self.hash_algorithm = hash_algorithm
        self.addressing_index: Dict[str, AddressingRecord] = {}
        self.reverse_index: Dict[str, List[str]] = {}  # Hash -> [addresses]
        self.verification_log: List[Dict[str, Any]] = []

    def address_content(
        self,
        content: Any,
        content_type: str = "application/json",
        metadata: Optional[Dict[str, Any]] = None
    ) -> ContentAddress:
        """Generate content address for data"""

        # Normalize content for consistent hashing
        normalized = self._normalize_content(content)
        content_bytes = normalized.encode("utf-8")

        # Generate hash
        hash_value = hashlib.sha256(content_bytes).hexdigest()

        # Create address
        address = ContentAddress(
            hash_type=self.hash_algorithm,
            hash_value=hash_value,
            content_type=content_type,
            size_bytes=len(content_bytes),
            metadata=metadata or {}
        )

        return address

    def verify_content(
        self,
        content: Any,
        address: ContentAddress
    ) -> Tuple[bool, str]:
        """Verify content matches its address"""

        normalized = self._normalize_content(content)
        content_bytes = normalized.encode("utf-8")
        computed_hash = hashlib.sha256(content_bytes).hexdigest()

        verified = computed_hash == address.hash_value

        verification_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "address": address.hash_value,
            "computed_hash": computed_hash,
            "verified": verified,
            "content_size": len(content_bytes)
        }
        self.verification_log.append(verification_record)

        return verified, computed_hash

    def create_addressing_record(
        self,
        content: Any,
        content_type: str = "application/json",
        transformation_chain: Optional[List[str]] = None,
        archive_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AddressingRecord:
        """Create complete addressing record"""

        address = self.address_content(content, content_type, metadata)
        verified, original_hash = self.verify_content(content, address)

        record = AddressingRecord(
            address=address,
            original_hash=original_hash,
            transformation_chain=transformation_chain or [],
            verified=verified,
            verification_timestamp=datetime.utcnow().isoformat() if verified else "",
            archive_path=archive_path,
            metadata=metadata or {}
        )

        # Store in index
        self.addressing_index[address.hash_value] = record

        # Maintain reverse index
        if address.hash_value not in self.reverse_index:
            self.reverse_index[address.hash_value] = []
        self.reverse_index[address.hash_value].append(address.address_uri)

        return record

    def batch_address(
        self,
        content_items: List[Tuple[Any, str]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[AddressingRecord]:
        """Address multiple content items"""

        records = []
        for content, content_type in content_items:
            record = self.create_addressing_record(
                content,
                content_type,
                metadata=metadata
            )
            records.append(record)

        return records

    def build_merkle_tree(
        self,
        content_list: List[Any]
    ) -> Dict[str, Any]:
        """Build Merkle tree for batch verification"""

        if not content_list:
            return {"root": None, "tree": [], "height": 0}

        # Address all items
        addresses = [
            self.address_content(item).hash_value
            for item in content_list
        ]

        # Build tree bottom-up
        tree_levels = [addresses]
        current_level = addresses

        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                if i + 1 < len(current_level):
                    combined = current_level[i] + current_level[i + 1]
                else:
                    combined = current_level[i]

                parent_hash = hashlib.sha256(combined.encode()).hexdigest()
                next_level.append(parent_hash)

            tree_levels.append(next_level)
            current_level = next_level

        root = current_level[0] if current_level else None

        return {
            "root": root,
            "tree": tree_levels,
            "height": len(tree_levels),
            "leaf_count": len(addresses),
            "verified": all(self.addressing_index.get(addr, {}).verified for addr in addresses)
        }

    def create_hash_chain(
        self,
        content_sequence: List[Any]
    ) -> List[Dict[str, Any]]:
        """Create hash chain for sequence verification (tamper-evident)"""

        chain = []
        previous_hash = None

        for i, content in enumerate(content_sequence):
            address = self.address_content(content)

            # Chain link includes previous hash
            link_data = {
                "sequence": i,
                "content_hash": address.hash_value,
                "previous_hash": previous_hash,
                "timestamp": datetime.utcnow().isoformat(),
                "link_hash": self._compute_link_hash(
                    address.hash_value,
                    previous_hash,
                    i
                )
            }

            chain.append(link_data)
            previous_hash = link_data["link_hash"]

        return chain

    def verify_hash_chain(
        self,
        chain: List[Dict[str, Any]]
    ) -> Tuple[bool, List[str]]:
        """Verify hash chain integrity"""

        errors = []

        if not chain:
            return True, []

        for i, link in enumerate(chain):
            # Verify link hash
            computed_link_hash = self._compute_link_hash(
                link["content_hash"],
                link["previous_hash"],
                link["sequence"]
            )

            if computed_link_hash != link["link_hash"]:
                errors.append(f"Chain link {i} verification failed")

            # Verify sequence
            if link["sequence"] != i:
                errors.append(f"Chain link {i} sequence mismatch")

            # Verify previous hash matches
            if i > 0:
                prev_link_hash = chain[i - 1]["link_hash"]
                if link["previous_hash"] != prev_link_hash:
                    errors.append(f"Chain link {i} previous hash mismatch")

        return len(errors) == 0, errors

    def create_proof_of_inclusion(
        self,
        item_hash: str,
        merkle_tree: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create proof that item is in Merkle tree"""

        tree_levels = merkle_tree.get("tree", [])
        if not tree_levels:
            return {"valid": False, "proof": [], "root": None}

        # Find item in tree
        leaf_level = tree_levels[0]
        if item_hash not in leaf_level:
            return {"valid": False, "proof": [], "root": None}

        item_index = leaf_level.index(item_hash)

        # Build proof path
        proof = []
        index = item_index

        for level_idx in range(len(tree_levels) - 1):
            current_level = tree_levels[level_idx]
            sibling_index = index ^ 1  # XOR to get sibling

            if sibling_index < len(current_level):
                sibling_hash = current_level[sibling_index]
                proof.append({
                    "level": level_idx,
                    "position": index,
                    "sibling": sibling_hash,
                    "direction": "left" if index % 2 == 0 else "right"
                })

            index = index // 2

        return {
            "valid": True,
            "proof": proof,
            "root": merkle_tree.get("root"),
            "item_hash": item_hash,
            "leaf_index": item_index
        }

    def get_address_history(self, content_hash: str) -> Optional[AddressingRecord]:
        """Retrieve address history"""
        return self.addressing_index.get(content_hash)

    def export_index(self) -> Dict[str, Any]:
        """Export addressing index"""
        return {
            "addressing_index": {
                hash_val: asdict(record)
                for hash_val, record in self.addressing_index.items()
            },
            "reverse_index": self.reverse_index,
            "verification_log": self.verification_log,
            "statistics": {
                "total_addresses": len(self.addressing_index),
                "total_verifications": len(self.verification_log),
                "successful_verifications": sum(
                    1 for v in self.verification_log if v.get("verified")
                )
            }
        }

    def _normalize_content(self, content: Any) -> str:
        """Normalize content for consistent hashing"""

        if isinstance(content, str):
            return content
        elif isinstance(content, dict):
            # Sort keys for deterministic hashing
            return json.dumps(content, sort_keys=True, separators=(",", ":"))
        elif isinstance(content, (list, tuple)):
            return json.dumps(list(content), separators=(",", ":"))
        else:
            return json.dumps(content, default=str)

    def _compute_link_hash(
        self,
        content_hash: str,
        previous_hash: Optional[str],
        sequence: int
    ) -> str:
        """Compute hash for chain link"""

        link_data = f"{sequence}:{previous_hash or 'genesis'}:{content_hash}"
        return hashlib.sha256(link_data.encode()).hexdigest()


class AddressingService:
    """High-level addressing service"""

    def __init__(self):
        self.addresser = ContentAddresser()
        self.archives: Dict[str, Dict[str, Any]] = {}

    def archive_with_address(
        self,
        content: Any,
        content_type: str = "application/json",
        archive_name: Optional[str] = None,
        archive_path: Optional[str] = None
    ) -> Tuple[ContentAddress, str]:
        """Archive content and return address"""

        record = self.addresser.create_addressing_record(
            content,
            content_type,
            archive_path=archive_path
        )

        # Store in archives
        if archive_name is None:
            archive_name = record.address.hash_value[:16]

        self.archives[archive_name] = {
            "address": record.address,
            "record": record,
            "archived_at": datetime.utcnow().isoformat(),
            "archive_path": archive_path
        }

        return record.address, archive_name

    def retrieve_archived(self, archive_name: str) -> Optional[Any]:
        """Retrieve archived content by name"""
        return self.archives.get(archive_name)

    def list_archives(self) -> List[Dict[str, Any]]:
        """List all archives"""
        return [
            {
                "name": name,
                "hash": archive["address"].hash_value[:16],
                "type": archive["address"].content_type,
                "size": archive["address"].size_bytes,
                "archived_at": archive["archived_at"]
            }
            for name, archive in self.archives.items()
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """Get addressing statistics"""
        export = self.addresser.export_index()
        return {
            "total_archives": len(self.archives),
            "addresser_stats": export.get("statistics", {}),
            "verification_rate": (
                export["statistics"]["successful_verifications"] /
                export["statistics"]["total_verifications"]
                if export["statistics"]["total_verifications"] > 0
                else 0
            )
        }


if __name__ == "__main__":
    # Example usage
    addresser = ContentAddresser()

    # Address content
    test_data = {"transaction": "INV-2026-08-0042", "amount": 450000.00}
    address = addresser.address_content(test_data, "application/json")

    print(f"Content Address: {address.address_uri}")
    print(f"Hash: {address.hash_value}")
    print(f"Size: {address.size_bytes} bytes")

    # Verify content
    verified, hash_val = addresser.verify_content(test_data, address)
    print(f"Verification: {verified}")

    # Create Merkle tree
    batch = [
        {"id": 1, "amount": 100},
        {"id": 2, "amount": 200},
        {"id": 3, "amount": 300},
    ]

    tree = addresser.build_merkle_tree(batch)
    print(f"\nMerkle Tree Root: {tree['root']}")
    print(f"Tree Height: {tree['height']}")

    # Create hash chain
    sequence = ["event1", "event2", "event3"]
    chain = addresser.create_hash_chain(sequence)
    print(f"\nHash Chain Created: {len(chain)} links")
    valid, errors = addresser.verify_hash_chain(chain)
    print(f"Chain Valid: {valid}")
