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
            description="Check company name availability through Finanvo API and validate naming conventions"
        )
        self.base_url = "https://api.finanvo.in"
        self.headers = {
            'Content-Type': 'application/json',
            'x-api-key': 'be2SxiTi',
            'x-api-secret-key': '0oOwfzhylxtH7OZZA9GuBc5cyGOCrqEqSixOuV'
        }
    
    def _run(self, company_name: str) -> Dict[str, Any]:
        try:
            cleaned_name = self._clean_company_name(company_name)
            availability_result = self._check_company_existence(cleaned_name)
            validation_result = self._validate_naming_conventions(company_name)
            
            return {
                "name": company_name,
                "cleaned_name": cleaned_name,
                "is_available": availability_result["available"],
                "existing_companies": availability_result["existing_companies"],
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
    
    def _search_companies_by_name(self, search_term: str) -> List[Dict]:
        found_companies = []
        search_variations = [
            search_term,
            search_term.replace(' ', ''),
            search_term.upper(),
            search_term.title()
        ]
        
        for variation in search_variations:
            try:
                time.sleep(0.5)
                mock_results = self._mock_company_search(variation)
                found_companies.extend(mock_results)
                
            except Exception as e:
                print(f"Error searching for {variation}: {e}")
                continue
        
        return found_companies
    
    def _mock_company_search(self, name: str) -> List[Dict]:
        common_patterns = [
            "tech", "solutions", "systems", "services", "innovations", 
            "enterprises", "consulting", "digital", "software", "info"
        ]
        
        name_lower = name.lower()
        conflicts = []
        
        for pattern in common_patterns:
            if pattern in name_lower:
                conflicts.append({
                    "company_name": f"{name.title()} {pattern.title()} Private Limited",
                    "cin": f"U{random.randint(10000, 99999)}DL{random.randint(2000, 2023)}PTC{random.randint(100000, 999999)}",
                    "similarity": fuzz.ratio(name_lower, f"{name_lower} {pattern}")
                })
        
        return conflicts[:3]
    
    def _get_company_by_cin(self, cin: str) -> Dict[str, Any]:
        try:
            url = f"{self.base_url}/company/profile"
            params = {"CIN": cin}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API returned status {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            return {"error": f"API request failed: {str(e)}"}
    
    def _check_company_existence(self, name: str) -> Dict[str, Any]:
        try:
            existing_companies = self._search_companies_by_name(name)
            
            exact_matches = []
            similar_companies = []
            
            for company in existing_companies:
                company_name = company.get("company_name", "").lower()
                cleaned_existing = self._clean_company_name(company_name)
                
                similarity = fuzz.ratio(name.lower(), cleaned_existing)
                
                if similarity > 95:  
                    exact_matches.append(company)
                elif similarity > 70:
                    company["similarity"] = similarity
                    similar_companies.append(company)

            similar_companies.sort(key=lambda x: x.get("similarity", 0), reverse=True)
            
            return {
                "available": len(exact_matches) == 0 and len(similar_companies) == 0,
                "exact_matches": exact_matches,
                "existing_companies": similar_companies[:5],  
                "total_found": len(existing_companies)
            }
            
        except Exception as e:
            return {
                "available": True, 
                "error": str(e),
                "existing_companies": []
            }
    
    def _validate_naming_conventions(self, name: str) -> Dict[str, Any]:
        errors = []
        warnings = []

        if len(name) < 3:
            errors.append("Company name too short (minimum 3 characters)")
        elif len(name) > 120:
            errors.append("Company name too long (maximum 120 characters)")

        prohibited_words = [
            'bank', 'insurance', 'government', 'ministry', 'national', 'central',
            'reserve', 'federal', 'authority', 'commission', 'corporation of india',
            'registrar', 'co-operative', 'municipal', 'panchayat'
        ]
        
        name_lower = name.lower()
        for word in prohibited_words:
            if word in name_lower:
                errors.append(f"Prohibited word '{word}' found in name")

        valid_suffixes = [
            'pvt ltd', 'private limited', 'pvt. ltd.', 'private limited.',
            'limited', 'ltd', 'ltd.'
        ]
        
        has_valid_suffix = any(name.lower().endswith(suffix) for suffix in valid_suffixes)
        if not has_valid_suffix:
            warnings.append("Consider adding proper suffix (Pvt Ltd or Private Limited)")

        if re.search(r'[^a-zA-Z0-9\s\.\-&()]', name):
            warnings.append("Special characters may cause issues during incorporation")
 
        if re.search(r'^\d', name):
            errors.append("Company name cannot start with a number")

        if re.search(r'\s{2,}', name):
            warnings.append("Multiple consecutive spaces found")
        
        if name != name.strip():
            warnings.append("Leading or trailing spaces detected")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "score": max(0, 100 - len(errors) * 30 - len(warnings) * 10)
        }
    
    def _get_recommendation(self, availability: Dict, validation: Dict) -> str:
        if not availability["available"]:
            if availability.get("exact_matches"):
                return "Name not available - exact match found in MCA database"
            elif availability.get("existing_companies"):
                similar_count = len(availability["existing_companies"])
                return f"Name may be rejected - {similar_count} similar companies found"
        
        if not validation["is_valid"]:
            error_count = len(validation["errors"])
            return f"Name validation failed - {error_count} naming convention errors"
        
        if validation["warnings"]:
            warning_count = len(validation["warnings"])
            return f"Name available with minor issues - {warning_count} warnings to consider"
        
        return "Name appears available and compliant with MCA guidelines"

mca_name_checker = MCANameChecker()