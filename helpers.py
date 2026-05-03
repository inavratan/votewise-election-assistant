"""
helpers.py — Calculation and Utility Functions

Pure utility functions with calculation logic using @lru_cache.
"""

from functools import lru_cache
from typing import Dict, List, Any
from data import ELECTION_TIMELINE, VOTER_DOCUMENTS
from datetime import datetime

__all__ = [
    "check_voter_eligibility",
    "get_election_phase_info",
    "calculate_days_until",
    "get_document_checklist"
]

@lru_cache(maxsize=128)
def check_voter_eligibility(age: int, is_citizen: bool, is_resident: bool) -> Dict[str, Any]:
    """
    Check if a person is eligible to vote based on Indian election rules.
    
    Args:
        age (int): The age of the person.
        is_citizen (bool): Whether the person is an Indian citizen.
        is_resident (bool): Whether the person is ordinarily resident in an Indian constituency.
        
    Returns:
        dict: A dictionary indicating 'eligible' status and a 'reason' message.
    """
    if not is_citizen:
        return {"eligible": False, "reason": "You must be an Indian citizen to vote."}
    
    if age < 18:
        return {"eligible": False, "reason": "You must be at least 18 years old to vote."}
        
    if not is_resident:
        # Note: NRIs can register, but must comply with specific rules (Form 6A). 
        # For this basic check, we'll mark it as a special case.
        return {"eligible": True, "reason": "As an NRI, you must submit Form 6A to register."}
        
    return {"eligible": True, "reason": "You are fully eligible to register and vote!"}

@lru_cache(maxsize=32)
def get_election_phase_info(phase_id: str) -> Dict[str, Any]:
    """
    Retrieve specific information for an election phase.
    
    Args:
        phase_id (str): The ID of the election phase.
        
    Returns:
        dict: The phase dictionary or an empty dict if not found.
    """
    for phase_data in ELECTION_TIMELINE:
        if phase_data["id"] == phase_id:
            return phase_data
    return {}

@lru_cache(maxsize=128)
def calculate_days_until(target_date_str: str) -> int:
    """
    Calculate the number of days until a target date.
    
    Args:
        target_date_str (str): Target date in 'YYYY-MM-DD' format.
        
    Returns:
        int: Number of days remaining. Negative if past. 0 if invalid format.
    """
    try:
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d")
        delta = target_date - datetime.now()
        return delta.days
    except (ValueError, TypeError):
        return 0

@lru_cache(maxsize=128)
def get_document_checklist(checked_tuple: tuple) -> dict:
    """
    Calculate checklist completion percentage and missing primary documents.
    Accepts tuple to allow caching.
    
    Args:
        checked_tuple (tuple): Tuple of indices for checked documents.
        
    Returns:
        dict: Completion data with percentage and missing document names.
    """
    from data import VOTER_DOCUMENTS
    total = len(VOTER_DOCUMENTS)
    if total == 0:
        return {"percentage": 0, "missing": []}
    
    checked_count = len(checked_tuple)
    percentage = int((checked_count / total) * 100)
    missing = [doc for i, doc in enumerate(VOTER_DOCUMENTS) if i not in checked_tuple]
    
    return {"percentage": percentage, "missing": missing}
