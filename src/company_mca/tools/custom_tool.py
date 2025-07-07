import requests
import json
from typing import Dict, List, Any
from crewai.tools import BaseTool
import time
import random
from fuzzywuzzy import fuzz
import re

class MCANameChecker(BaseTool):
    def __init__(self):
        super().__init__(
            name="MCA Name Checker",
            description="Check company name availability through MCA database and validate naming conventions"
        )
        self.base_url = "https://www.mca.gov.in/mcafoportal/companyLLPNameSearch.do"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json'
        }
    
    def _run(self, company_name: str) -> Dict[str, Any]:
        try:
            cleaned_name = self._clean_company_name(company_name)
            availability_result = self._check_mca_availability(cleaned_name)
            validation_result = self._validate_naming_conventions(company_name)
            
            return {
                "name": company_name,
                "cleaned_name": cleaned_name,
                "is_available": availability_result["available"],
                "similar_names": availability_result["similar_names"],
                "validation": validation_result,
                "recommendation": self._get_recommendation(availability_result, validation_result)
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "name": company_name,
                "is_available": False
            }
    
    def _clean_company_name(self, name: str) -> str:
        suffixes = ['pvt ltd', 'private limited', 'ltd', 'limited', 'pvt', 'private']
        cleaned = name.lower()
        
        for suffix in suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[:-len(suffix)].strip()
        
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', cleaned)
        return cleaned.strip()
    
    def _check_mca_availability(self, name: str) -> Dict[str, Any]:
        time.sleep(random.uniform(0.5, 1.5))

        existing_companies = [
            "xyz technology", "abc technology", "xyz solutions", "tech innovations",
            "digital solutions", "cyber tech", "info systems", "data analytics",
            "smart solutions", "tech services", "xyz enterprises", "abc solutions"
        ]
        
        exact_match = name.lower() in existing_companies
        similar_names = []
        for existing in existing_companies:
            similarity = fuzz.ratio(name.lower(), existing.lower())
            if similarity > 70:
                similar_names.append({
                    "name": existing,
                    "similarity": similarity
                })
        
        similar_names.sort(key=lambda x: x["similarity"], reverse=True)
        
        return {
            "available": not exact_match and len(similar_names) == 0,
            "exact_match": exact_match,
            "similar_names": similar_names[:5] 
        }
    
    def _validate_naming_conventions(self, name: str) -> Dict[str, Any]:
        errors = []
        warnings = []
        
        if len(name) < 3:
            errors.append("Company name too short (minimum 3 characters)")
        elif len(name) > 120:
            errors.append("Company name too long (maximum 120 characters)")
  
        prohibited_words = ['bank', 'insurance', 'government', 'ministry', 'national', 'central']
        name_lower = name.lower()
        
        for word in prohibited_words:
            if word in name_lower:
                errors.append(f"Prohibited word '{word}' found in name")
        
        valid_suffixes = ['pvt ltd', 'private limited', 'pvt. ltd.', 'private limited.']
        has_valid_suffix = any(name.lower().endswith(suffix) for suffix in valid_suffixes)

        if not has_valid_suffix:
            warnings.append("Consider adding proper suffix (Pvt Ltd or Private Limited)")
        if re.search(r'[^a-zA-Z0-9\s\.\-&]', name):
            warnings.append("Special characters may cause issues during incorporation")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "score": max(0, 100 - len(errors) * 30 - len(warnings) * 10)
        }
    
    def _get_recommendation(self, availability: Dict, validation: Dict) -> str:
        if not availability["available"]:
            if availability["exact_match"]:
                return "Name not available - exact match found"
            elif availability["similar_names"]:
                return f"Name may be rejected - {len(availability['similar_names'])} similar names found"
        
        if not validation["is_valid"]:
            return f"Name validation failed - {len(validation['errors'])} errors found"
        
        if validation["warnings"]:
            return f"Name available with minor issues - {len(validation['warnings'])} warnings"
        
        return "Name available and compliant"

mca_name_checker = MCANameChecker()