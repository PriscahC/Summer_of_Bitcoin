"""
Simple Blockchain Implementation
Day 1: Bitcoin Introduction

This is a basic blockchain to demonstrate the core concepts:
- Blocks containing transactions
- Hashing for digital signatures
- Linking blocks together (the "chain")
- Transaction verification

Author: Learning Journey
Date: 2026-02-17
"""

import hashlib
import json
from time import time
from typing import List, Dict, Any


class Transaction:
    """Represents a Bitcoin transaction"""
    
    def __init__(self, sender: str, receiver: str, amount: float):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary format"""
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'timestamp': self.timestamp
        }
    
    def __repr__(self):
        return f"Transaction({self.sender} -> {self.receiver}: {self.amount} BTC)"


class Block:
    """
    Represents a block in the blockchain
    
    Each block contains:
    - index: Position in the chain
    - transactions: List of transactions
    - timestamp: When block was created
    - previous_hash: Hash of previous block (creates the "chain")
    - nonce: Number used for mining
    """
    
    def __init__(self, index: int, transactions: List[Transaction], 
                 previous_hash: str):
        self.index = index
        self.transactions = transactions
        self.timestamp = time()
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.compute_hash()
    
    def compute_hash(self) -> str:
        """
        Create a digital signature (hash) of the block
        
        This is like creating a unique fingerprint of the block.
        Any change to the block will result in a completely different hash.
        """
        block_data = {
            'index': self.index,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }
        
        # Convert to JSON string and create SHA-256 hash
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def __repr__(self):
        return f"Block(#{self.index}, Txs: {len(self.transactions)}, Hash: {self.hash[:8]}...)"


class Blockchain:
    """
    Simple blockchain implementation
    
    Demonstrates:
    - Chain of blocks
    - Transaction verification
    - Block linking through hashes
    """
    
    def __init__(self):
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        
        # Create genesis block (the first block)
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the first block in the blockchain"""
        genesis_block = Block(
            index=0,
            transactions=[],
            previous_hash="0"
        )
        self.chain.append(genesis_block)
        print(f"✅ Genesis block created: {genesis_block.hash}")
    
    def get_latest_block(self) -> Block:
        """Get the most recent block in the chain"""
        return self.chain[-1]
    
    def add_transaction(self, transaction: Transaction) -> bool:
        """
        Add a transaction to pending transactions
        
        In a real blockchain, this would verify:
        - Digital signature is valid
        - Sender has enough balance
        - Transaction hasn't been spent before (no double-spending)
        """
        # Simple validation: sender and receiver must be different
        if transaction.sender == transaction.receiver:
            print("❌ Invalid transaction: sender and receiver are the same")
            return False
        
        if transaction.amount <= 0:
            print("❌ Invalid transaction: amount must be positive")
            return False
        
        self.pending_transactions.append(transaction)
        print(f"✅ Transaction added: {transaction}")
        return True
    
    def mine_pending_transactions(self, miner_address: str):
        """
        Mine pending transactions into a new block
        
        In real Bitcoin:
        - Miners compete to solve a computational puzzle
        - Winner gets to add the block and receives a reward
        - This process secures the network
        """
        if not self.pending_transactions:
            print("⚠️  No transactions to mine")
            return
        
        # Create new block with pending transactions
        new_block = Block(
            index=len(self.chain),
            transactions=self.pending_transactions,
            previous_hash=self.get_latest_block().hash
        )
        
        # Add mining reward transaction
        reward_tx = Transaction(
            sender="NETWORK",
            receiver=miner_address,
            amount=6.25  # Current Bitcoin mining reward
        )
        new_block.transactions.append(reward_tx)
        
        # Recalculate hash with reward included
        new_block.hash = new_block.compute_hash()
        
        # Add block to chain
        self.chain.append(new_block)
        print(f"⛏️  Block #{new_block.index} mined by {miner_address}")
        print(f"   Hash: {new_block.hash}")
        print(f"   Transactions: {len(new_block.transactions)}")
        
        # Clear pending transactions
        self.pending_transactions = []
    
    def is_chain_valid(self) -> bool:
        """
        Verify the integrity of the blockchain
        
        Checks:
        1. Each block's hash is correct
        2. Each block links to the previous block correctly
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check if current block's hash is valid
            if current_block.hash != current_block.compute_hash():
                print(f"❌ Block #{i} has invalid hash")
                return False
            
            # Check if current block links to previous block
            if current_block.previous_hash != previous_block.hash:
                print(f"❌ Block #{i} doesn't link to previous block")
                return False
        
        print("✅ Blockchain is valid!")
        return True
    
    def get_balance(self, address: str) -> float:
        """Calculate the balance of an address"""
        balance = 0
        
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address:
                    balance -= tx.amount
                if tx.receiver == address:
                    balance += tx.amount
        
        return balance
    
    def display_chain(self):
        """Display the entire blockchain"""
        print("\n" + "="*60)
        print("BLOCKCHAIN")
        print("="*60)
        
        for block in self.chain:
            print(f"\nBlock #{block.index}")
            print(f"  Timestamp: {block.timestamp}")
            print(f"  Previous Hash: {block.previous_hash[:8]}...")
            print(f"  Hash: {block.hash[:8]}...")
            print(f"  Transactions ({len(block.transactions)}):")
            for tx in block.transactions:
                print(f"    - {tx}")
        
        print("\n" + "="*60 + "\n")


def main():
    """
    Demo of a simple blockchain
    """
    print("\n🚀 Simple Blockchain Demo - Day 1\n")
    
    # Create blockchain
    blockchain = Blockchain()
    
    # Create some transactions
    tx1 = Transaction("Alice", "Bob", 5.0)
    tx2 = Transaction("Bob", "Charlie", 2.0)
    tx3 = Transaction("Charlie", "Alice", 1.5)
    
    # Add transactions
    blockchain.add_transaction(tx1)
    blockchain.add_transaction(tx2)
    blockchain.add_transaction(tx3)
    
    print("\n--- Mining Block 1 ---")
    blockchain.mine_pending_transactions("Miner1")
    
    # Add more transactions
    tx4 = Transaction("Alice", "Charlie", 3.0)
    tx5 = Transaction("Bob", "Alice", 1.0)
    
    blockchain.add_transaction(tx4)
    blockchain.add_transaction(tx5)
    
    print("\n--- Mining Block 2 ---")
    blockchain.mine_pending_transactions("Miner2")
    
    # Display the blockchain
    blockchain.display_chain()
    
    # Check balances
    print("💰 Account Balances:")
    for person in ["Alice", "Bob", "Charlie", "Miner1", "Miner2"]:
        balance = blockchain.get_balance(person)
        print(f"   {person}: {balance:.2f} BTC")
    
    # Verify blockchain integrity
    print("\n🔍 Verifying blockchain...")
    blockchain.is_chain_valid()
    
    # Attempt to tamper with blockchain
    print("\n🔨 Attempting to tamper with Block #1...")
    blockchain.chain[1].transactions[0].amount = 100.0
    blockchain.is_chain_valid()


if __name__ == "__main__":
    main()
      
