"""
Announcements endpoints for the High School Management System API
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime
from bson import ObjectId

from ..database import announcements_collection

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)


@router.get("/")
def get_active_announcements() -> List[Dict[str, Any]]:
    """Get all active announcements (not expired and within start date)"""
    now = datetime.utcnow().isoformat() + "Z"
    
    announcements = list(announcements_collection.find({
        "$and": [
            {"expiration_date": {"$gte": now}},
            {
                "$or": [
                    {"start_date": None},
                    {"start_date": {"$lte": now}}
                ]
            }
        ]
    }).sort("_id", -1))
    
    # Convert ObjectId to string for JSON serialization
    for announcement in announcements:
        announcement["_id"] = str(announcement["_id"])
    
    return announcements


@router.get("/all")
def get_all_announcements() -> List[Dict[str, Any]]:
    """Get all announcements (for admin management)"""
    announcements = list(announcements_collection.find().sort("_id", -1))
    
    # Convert ObjectId to string for JSON serialization
    for announcement in announcements:
        announcement["_id"] = str(announcement["_id"])
    
    return announcements


@router.post("/")
def create_announcement(
    message: str,
    expiration_date: str,
    start_date: Optional[str] = None,
    created_by: str = "system"
) -> Dict[str, Any]:
    """Create a new announcement"""
    announcement = {
        "message": message,
        "start_date": start_date,
        "expiration_date": expiration_date,
        "created_by": created_by,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    
    result = announcements_collection.insert_one(announcement)
    announcement["_id"] = str(result.inserted_id)
    
    return announcement


@router.put("/{announcement_id}")
def update_announcement(
    announcement_id: str,
    message: str,
    expiration_date: str,
    start_date: Optional[str] = None
) -> Dict[str, Any]:
    """Update an existing announcement"""
    try:
        obj_id = ObjectId(announcement_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid announcement ID")
    
    updated_announcement = {
        "message": message,
        "start_date": start_date,
        "expiration_date": expiration_date
    }
    
    result = announcements_collection.find_one_and_update(
        {"_id": obj_id},
        {"$set": updated_announcement},
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    result["_id"] = str(result["_id"])
    return result


@router.delete("/{announcement_id}")
def delete_announcement(announcement_id: str) -> Dict[str, str]:
    """Delete an announcement"""
    try:
        obj_id = ObjectId(announcement_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid announcement ID")
    
    result = announcements_collection.delete_one({"_id": obj_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    return {"message": "Announcement deleted successfully"}
