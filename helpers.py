"""
helpers.py — Calculation and Utility Functions

Pure utility functions with calculation logic using @lru_cache.
"""

from functools import lru_cache
from typing import Dict, List, Any
from data import ELECTION_TIMELINE, VOTER_DOCUMENTS

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

@lru_cache(maxsize=64)
def calculate_days_until(target_date_str: str) -> int:
    """
    Calculate the number of days until a specific date (Mocked implementation for demo).
    
    Args:
        target_date_str (str): The target date string.
        
    Returns:
        int: Number of days remaining.
    """
    # In a real app, parse the string with datetime. For this demo, return a dummy positive value.
    return 15

def get_document_checklist(checked_ids: List[str]) -> Dict[str, Any]:
    """
    Calculate checklist completion and missing documents for an individual voter.
    
    Args:
        checked_ids (list): List of document IDs the voter claims to have.
        
    Returns:
        dict: Completion percentage and missing core documents.
    """
    if not isinstance(checked_ids, list):
        return {"percentage": 0, "status": "No documents provided"}
        
    # Valid documents set
    all_doc_ids = {doc["id"] for doc in VOTER_DOCUMENTS}
    
    # Voter needs EXACTLY one of any of internal valid ids to vote, but EPIC is heavily recommended
    valid_checked = [cid for cid in checked_ids if cid in all_doc_ids]
    
    has_epic = "epic" in valid_checked
    has_any_valid = len(valid_checked) > 0
    
    if has_epic:
        percentage = 100
        message = "You are fully prepared! You have the primary EPIC card."
    elif has_any_valid:
        percentage = 80
        message = "You have an alternative valid ID. Ensure you know your booth."
    else:
        percentage = 0
        message = "You need at least one valid photo ID document to vote."
        
    return {
        "percentage": percentage,
        "message": message,
        "has_epic": has_epic,
        "provided_docs": valid_checked
    }
