from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.gemini_service import gemini_service
import json

router = APIRouter()

@router.post("/analyze-donation")
async def analyze_donation(
    bill_file: UploadFile = File(...),
    charity_file: UploadFile = File(...)
):
    """
    Upload a bill image and a charity proof image to analyze them using Gemini.
    """
    try:
        bill_content = await bill_file.read()
        charity_content = await charity_file.read()

        # Basic validation (optional: check mime types)
        
        result_json_str = await gemini_service.analyze_donation_proof(bill_content, charity_content)
        
        # Try to parse JSON to ensure it's valid, or return raw string if parsing fails
        try:
            result = json.loads(result_json_str)
            return result
        except json.JSONDecodeError:
            return {"raw_response": result_json_str}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
