"""
Epoch Manager
Manages epoch progression and qualification for the Syntheverse blockchain.
"""

from typing import Dict, Optional, List
from enum import Enum
from datetime import datetime

from .blockchain import Epoch
from .contracts.synth_token import SYNTHToken


class EpochManager:
    """
    Manages epoch transitions and qualification rules.
    Each epoch opens only after the previous epoch achieves minimum resonance density.
    """
    
    # Minimum resonance density required to unlock next epoch
    EPOCH_UNLOCK_THRESHOLDS = {
        Epoch.FOUNDER: 0,  # Founder epoch starts immediately
        Epoch.PIONEER: 1_000_000,  # 1M coherence density units
        Epoch.COMMUNITY: 2_000_000,  # 2M coherence density units
        Epoch.ECOSYSTEM: 3_000_000,  # 3M coherence density units
    }
    
    def __init__(self, synth_token: SYNTHToken):
        """
        Initialize epoch manager.
        
        Args:
            synth_token: SYNTH token contract instance
        """
        self.synth_token = synth_token
        self.epoch_history: List[Dict] = []
    
    def get_current_epoch(self) -> Epoch:
        """Get current active epoch."""
        return self.synth_token.current_epoch
    
    def can_unlock_epoch(self, epoch: Epoch) -> bool:
        """
        Check if an epoch can be unlocked based on coherence density.
        
        Args:
            epoch: Epoch to check
        
        Returns:
            True if epoch can be unlocked
        """
        total_coherence = self.synth_token.total_coherence_density
        threshold = self.EPOCH_UNLOCK_THRESHOLDS.get(epoch, float('inf'))
        
        return total_coherence >= threshold
    
    def check_epoch_transitions(self) -> Optional[Epoch]:
        """
        Check if any epoch transitions should occur based on current state.
        
        Returns:
            New epoch if transition should occur, None otherwise
        """
        epoch_order = [Epoch.FOUNDER, Epoch.PIONEER, Epoch.COMMUNITY, Epoch.ECOSYSTEM]
        current_epoch = self.synth_token.current_epoch
        
        try:
            current_index = epoch_order.index(current_epoch)
            
            # Check if we can progress to next epoch
            for i in range(current_index + 1, len(epoch_order)):
                next_epoch = epoch_order[i]
                if self.can_unlock_epoch(next_epoch):
                    if not self.synth_token.epoch_progression.get(next_epoch, False):
                        return next_epoch
                else:
                    break  # Can't progress further
            
            return None
        except ValueError:
            return None
    
    def transition_to_epoch(self, epoch: Epoch) -> bool:
        """
        Transition to a new epoch.
        
        Args:
            epoch: Target epoch
        
        Returns:
            True if transition successful
        """
        if not self.can_unlock_epoch(epoch):
            return False
        
        success = self.synth_token.transition_epoch(epoch)
        
        if success:
            # Record epoch transition
            transition_record = {
                "epoch": epoch.value,
                "timestamp": datetime.now().isoformat(),
                "coherence_density": self.synth_token.total_coherence_density,
                "founder_halving_count": self.synth_token.founder_halving_count,
            }
            self.epoch_history.append(transition_record)
        
        return success
    
    def auto_transition(self) -> Optional[Epoch]:
        """
        Automatically transition to next epoch if conditions are met.
        
        Returns:
            New epoch if transition occurred, None otherwise
        """
        next_epoch = self.check_epoch_transitions()
        if next_epoch:
            if self.transition_to_epoch(next_epoch):
                return next_epoch
        return None
    
    def get_epoch_info(self, epoch: Epoch) -> Dict:
        """
        Get information about a specific epoch.
        
        Args:
            epoch: Epoch to query
        
        Returns:
            Epoch information dictionary
        """
        return {
            "epoch": epoch.value,
            "is_active": self.synth_token.current_epoch == epoch,
            "is_unlocked": self.synth_token.epoch_progression.get(epoch, False),
            "balance": self.synth_token.get_epoch_balance(epoch),
            "threshold": self.EPOCH_UNLOCK_THRESHOLDS.get(epoch, 0),
            "can_unlock": self.can_unlock_epoch(epoch),
            "distribution_percent": SYNTHToken.EPOCH_DISTRIBUTION.get(epoch, 0.0) * 100,
        }
    
    def get_all_epochs_info(self) -> Dict:
        """Get information about all epochs."""
        return {
            epoch.value: self.get_epoch_info(epoch)
            for epoch in Epoch
        }
    
    def get_transition_history(self) -> list:
        """Get history of epoch transitions."""
        return self.epoch_history.copy()
