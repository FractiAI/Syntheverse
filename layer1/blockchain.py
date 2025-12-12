"""
Syntheverse Layer 1 Blockchain
Core blockchain implementation with Proof-of-Discovery consensus.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
import json
from enum import Enum


class TransactionType(Enum):
    """Transaction types in the Syntheverse blockchain."""
    POD_SUBMISSION = "pod_submission"
    POD_EVALUATION = "pod_evaluation"
    TOKEN_ALLOCATION = "token_allocation"
    EPOCH_TRANSITION = "epoch_transition"
    TIER_ASSIGNMENT = "tier_assignment"


class ContributionTier(Enum):
    """Contribution tiers for different types of discoveries."""
    GOLD = "gold"  # Scientific contributions
    SILVER = "silver"  # Tech contributions
    COPPER = "copper"  # Alignment contributions


class Epoch(Enum):
    """Epoch types for token distribution."""
    FOUNDER = "founder"
    PIONEER = "pioneer"
    COMMUNITY = "community"
    ECOSYSTEM = "ecosystem"


class Transaction:
    """Represents a transaction on the Syntheverse blockchain."""
    
    def __init__(
        self,
        tx_type: TransactionType,
        data: Dict[str, Any],
        sender: str,
        timestamp: Optional[datetime] = None
    ):
        """
        Initialize a transaction.
        
        Args:
            tx_type: Type of transaction
            data: Transaction data
            sender: Address/ID of transaction sender
            timestamp: Transaction timestamp (defaults to now)
        """
        self.tx_type = tx_type
        self.data = data
        self.sender = sender
        self.timestamp = timestamp or datetime.now()
        self.hash = self._calculate_hash()
    
    def _calculate_hash(self) -> str:
        """Calculate transaction hash."""
        tx_data = {
            "type": self.tx_type.value,
            "data": self.data,
            "sender": self.sender,
            "timestamp": self.timestamp.isoformat(),
        }
        tx_string = json.dumps(tx_data, sort_keys=True, default=str)
        return hashlib.sha256(tx_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary."""
        return {
            "hash": self.hash,
            "type": self.tx_type.value,
            "data": self.data,
            "sender": self.sender,
            "timestamp": self.timestamp.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Transaction":
        """Create transaction from dictionary."""
        tx = cls(
            tx_type=TransactionType(data["type"]),
            data=data["data"],
            sender=data["sender"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )
        tx.hash = data["hash"]
        return tx


class Block:
    """Represents a block in the Syntheverse blockchain."""
    
    def __init__(
        self,
        index: int,
        transactions: List[Transaction],
        previous_hash: str,
        timestamp: Optional[datetime] = None,
        validator: Optional[str] = None,
        pod_score: float = 0.0
    ):
        """
        Initialize a block.
        
        Args:
            index: Block index/height
            transactions: List of transactions in the block
            previous_hash: Hash of previous block
            timestamp: Block timestamp (defaults to now)
            validator: Address/ID of block validator
            pod_score: Proof-of-Discovery score for this block
        """
        self.index = index
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = timestamp or datetime.now()
        self.validator = validator
        self.pod_score = pod_score
        self.nonce = 0
        self.hash = self._calculate_hash()
    
    def _calculate_hash(self) -> str:
        """Calculate block hash."""
        block_data = {
            "index": self.index,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp.isoformat(),
            "validator": self.validator,
            "pod_score": self.pod_score,
            "nonce": self.nonce,
        }
        block_string = json.dumps(block_data, sort_keys=True, default=str)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int = 1):
        """
        Mine block by finding nonce that satisfies difficulty.
        
        Args:
            difficulty: Number of leading zeros required in hash
        """
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self._calculate_hash()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary."""
        return {
            "index": self.index,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp.isoformat(),
            "validator": self.validator,
            "pod_score": self.pod_score,
            "nonce": self.nonce,
            "hash": self.hash,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Block":
        """Create block from dictionary."""
        transactions = [Transaction.from_dict(tx) for tx in data["transactions"]]
        block = cls(
            index=data["index"],
            transactions=transactions,
            previous_hash=data["previous_hash"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            validator=data.get("validator"),
            pod_score=data.get("pod_score", 0.0)
        )
        block.nonce = data["nonce"]
        block.hash = data["hash"]
        return block


class Blockchain:
    """Syntheverse blockchain implementation."""
    
    def __init__(self, difficulty: int = 1):
        """
        Initialize blockchain.
        
        Args:
            difficulty: Mining difficulty (number of leading zeros)
        """
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.difficulty = difficulty
        self._create_genesis_block()
    
    def _create_genesis_block(self):
        """Create the genesis block."""
        genesis = Block(
            index=0,
            transactions=[],
            previous_hash="0" * 64,
            timestamp=datetime.now(),
            validator="genesis",
            pod_score=0.0
        )
        genesis.mine_block(self.difficulty)
        self.chain.append(genesis)
    
    def get_latest_block(self) -> Block:
        """Get the latest block in the chain."""
        return self.chain[-1]
    
    def add_transaction(self, transaction: Transaction) -> bool:
        """
        Add transaction to pending pool.
        
        Args:
            transaction: Transaction to add
        
        Returns:
            True if added successfully
        """
        self.pending_transactions.append(transaction)
        return True
    
    def mine_pending_transactions(self, validator: str, pod_score: float = 0.0) -> Block:
        """
        Mine pending transactions into a new block.
        
        Args:
            validator: Address/ID of validator
            pod_score: Proof-of-Discovery score for this block
        
        Returns:
            Newly mined block
        """
        if not self.pending_transactions:
            raise ValueError("No pending transactions to mine")
        
        block = Block(
            index=len(self.chain),
            transactions=self.pending_transactions.copy(),
            previous_hash=self.get_latest_block().hash,
            validator=validator,
            pod_score=pod_score
        )
        
        block.mine_block(self.difficulty)
        self.chain.append(block)
        self.pending_transactions = []
        
        return block
    
    def is_chain_valid(self) -> bool:
        """
        Validate the entire blockchain.
        
        Returns:
            True if chain is valid
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check block hash
            if current_block.hash != current_block._calculate_hash():
                return False
            
            # Check previous hash link
            if current_block.previous_hash != previous_block.hash:
                return False
            
            # Check difficulty
            if current_block.hash[:self.difficulty] != "0" * self.difficulty:
                return False
        
        return True
    
    def get_chain_length(self) -> int:
        """Get the length of the blockchain."""
        return len(self.chain)
    
    def get_block_by_index(self, index: int) -> Optional[Block]:
        """Get block by index."""
        if 0 <= index < len(self.chain):
            return self.chain[index]
        return None
    
    def get_transactions_by_type(self, tx_type: TransactionType) -> List[Transaction]:
        """Get all transactions of a specific type from the chain."""
        transactions = []
        for block in self.chain:
            for tx in block.transactions:
                if tx.tx_type == tx_type:
                    transactions.append(tx)
        return transactions
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert blockchain to dictionary."""
        return {
            "chain": [block.to_dict() for block in self.chain],
            "pending_transactions": [tx.to_dict() for tx in self.pending_transactions],
            "difficulty": self.difficulty,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Blockchain":
        """Create blockchain from dictionary."""
        blockchain = cls(difficulty=data.get("difficulty", 1))
        blockchain.chain = [Block.from_dict(block_data) for block_data in data["chain"]]
        blockchain.pending_transactions = [
            Transaction.from_dict(tx_data) for tx_data in data.get("pending_transactions", [])
        ]
        return blockchain

