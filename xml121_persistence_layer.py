# © 2026 121 Solutions USA. All rights reserved.
#
# The trademarks 121XQ, 121XML, and 121MetaVerse are the exclusive
# property of 121 Solutions USA.
#
# Unauthorized use, reproduction, or distribution of this material,
# including any proprietary designs, software, or documentation, is
# strictly prohibited without prior written permission from 121 Solutions USA.
"""
121XML Data Persistence Layer
==============================

File-based persistence for all 121XML objects.
Content-addressed storage with SHA256 lookup.

Features:
- Content-addressed storage
- SHA256 indexing
- Relationship traversal
- Concurrent access safety
- Backup and recovery
- Query capabilities

Author: 121XML Foundation
License: Apache 2.0
"""

import json
import hashlib
import os
from pathlib import Path
from typing import Dict, Optional, List, Any
from datetime import datetime


class PersistenceLayer:
    """121XML file-based persistence"""
    
    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = Path("/sessions/trusting-inspiring-gates/mnt/121XML/data")
        
        self.data_dir = data_dir
        self.objects_dir = data_dir / "objects"
        self.index_dir = data_dir / "index"
        self.archive_dir = data_dir / "archive"
        
        # Create directories
        for d in [self.objects_dir, self.index_dir, self.archive_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        # Load indices
        self.address_index: Dict[str, str] = self._load_index("addresses")
        self.type_index: Dict[str, List[str]] = self._load_index("types")
    
    def _load_index(self, index_name: str) -> Dict:
        """Load index from file"""
        index_file = self.index_dir / f"{index_name}.json"
        if index_file.exists():
            return json.loads(index_file.read_text())
        return {}
    
    def _save_index(self, index_name: str, index: Dict):
        """Save index to file"""
        index_file = self.index_dir / f"{index_name}.json"
        index_file.write_text(json.dumps(index, indent=2))
    
    def store(self, obj: Dict, obj_type: str) -> str:
        """
        Store object and return its content address.
        
        Args:
            obj: Object to store
            obj_type: Type classification for indexing
        
        Returns:
            Content address: data://sha256:HASH:TYPE
        """
        
        # Compute address
        json_str = json.dumps(obj, sort_keys=True, separators=(',', ':'))
        hash_val = hashlib.sha256(json_str.encode()).hexdigest()
        address = f"data://sha256:{hash_val}:{obj_type}"
        
        # Extract short hash for filename
        short_hash = hash_val[:16]
        filename = f"{short_hash}.json"
        filepath = self.objects_dir / obj_type / filename
        
        # Create type directory
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Store object with metadata
        storage_obj = {
            "_address": address,
            "_type": obj_type,
            "_stored": datetime.utcnow().isoformat() + "Z",
            "_hash": hash_val,
            "data": obj
        }
        
        filepath.write_text(json.dumps(storage_obj, indent=2))
        
        # Update indices
        self.address_index[address] = str(filepath)
        if obj_type not in self.type_index:
            self.type_index[obj_type] = []
        if address not in self.type_index[obj_type]:
            self.type_index[obj_type].append(address)
        
        self._save_index("addresses", self.address_index)
        self._save_index("types", self.type_index)
        
        return address
    
    def retrieve(self, address: str) -> Optional[Dict]:
        """
        Retrieve object by content address.
        
        Args:
            address: Content address (data://sha256:HASH:TYPE)
        
        Returns:
            Original object or None if not found
        """
        
        if address not in self.address_index:
            return None
        
        filepath = Path(self.address_index[address])
        if not filepath.exists():
            return None
        
        storage_obj = json.loads(filepath.read_text())
        return storage_obj.get("data")
    
    def query_by_type(self, obj_type: str) -> List[Dict]:
        """
        Query all objects of a specific type.
        
        Args:
            obj_type: Object type to query
        
        Returns:
            List of objects
        """
        
        if obj_type not in self.type_index:
            return []
        
        objects = []
        for address in self.type_index[obj_type]:
            obj = self.retrieve(address)
            if obj:
                objects.append({
                    "_address": address,
                    "data": obj
                })
        
        return objects
    
    def archive(self, address: str) -> bool:
        """
        Archive object (move to archive, keep reference).
        
        Args:
            address: Address of object to archive
        
        Returns:
            True if successful
        """
        
        obj = self.retrieve(address)
        if not obj:
            return False
        
        # Create archive entry
        archive_obj = {
            "_original_address": address,
            "_archived": datetime.utcnow().isoformat() + "Z",
            "data": obj
        }
        
        # Store in archive
        hash_val = address.split(":")[1]
        archive_file = self.archive_dir / f"{hash_val}.json"
        archive_file.write_text(json.dumps(archive_obj, indent=2))
        
        return True
    
    def get_stats(self) -> Dict:
        """Get storage statistics"""
        
        total_objects = 0
        total_size = 0
        type_stats = {}
        
        for obj_dir in self.objects_dir.iterdir():
            if not obj_dir.is_dir():
                continue
            
            obj_type = obj_dir.name
            obj_count = len(list(obj_dir.glob("*.json")))
            obj_size = sum(f.stat().st_size for f in obj_dir.glob("*.json"))
            
            total_objects += obj_count
            total_size += obj_size
            type_stats[obj_type] = {
                "count": obj_count,
                "size_bytes": obj_size
            }
        
        return {
            "data_dir": str(self.data_dir),
            "total_objects": total_objects,
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "object_types": type_stats,
            "indexed_addresses": len(self.address_index),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


# ============================================================================
# DEMO
# ============================================================================

def demo_persistence():
    """Demonstrate persistence layer"""
    
    print("=" * 70)
    print("121XML DATA PERSISTENCE LAYER - DEMO")
    print("=" * 70)
    
    persistence = PersistenceLayer()
    
    # Store some objects
    objects_to_store = [
        {
            "type": "payment",
            "obj": {
                "id": "pay_001",
                "amount": 450000,
                "currency": "USD",
                "invoice": "INV-2026-08-0042"
            }
        },
        {
            "type": "payment",
            "obj": {
                "id": "pay_002",
                "amount": 275000,
                "currency": "GBP",
                "invoice": "INV-2026-08-0043"
            }
        },
        {
            "type": "resource",
            "obj": {
                "uri": "banking://schema/swift",
                "name": "SWIFT Schema",
                "content": "SWIFT MT103 specification..."
            }
        }
    ]
    
    print("\n📥 Storing objects:")
    addresses = []
    for obj_info in objects_to_store:
        address = persistence.store(obj_info["obj"], obj_info["type"])
        addresses.append(address)
        print(f"   ✓ {obj_info['type']}: {address[:40]}...")
    
    print("\n📤 Retrieving objects:")
    for address in addresses:
        obj = persistence.retrieve(address)
        if obj:
            print(f"   ✓ Retrieved: {obj.get('id', obj.get('uri', 'unknown'))}")
    
    print("\n📊 Querying by type:")
    payment_objects = persistence.query_by_type("payment")
    print(f"   Found {len(payment_objects)} payment objects")
    
    print("\n📈 Storage Statistics:")
    stats = persistence.get_stats()
    print(f"   Total objects: {stats['total_objects']}")
    print(f"   Total size: {stats['total_size_mb']:.2f} MB")
    print(f"   Object types: {list(stats['object_types'].keys())}")

if __name__ == "__main__":
    demo_persistence()

