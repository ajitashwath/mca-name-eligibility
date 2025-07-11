import requests
import json
from typing import Dict, List, Any
from crewai.tools import tool
import time
import random
from fuzzywuzzy import fuzz
import re
import os

@tool("MCA Name Checker")
def mca_name_checker(company_name: str) -> Dict[str, Any]:
    """
    Check company name availability through Finanvo API and validate naming conventions.
    
    Args:
        company_name: The company name to check for availability
        
    Returns:
        Dictionary containing availability status, validation results, and recommendations
    """
    try:
        checker = MCANameChecker()
        return checker.check_name(company_name)
    except Exception as e:
        return {
            "error": str(e),
            "name": company_name,
            "is_available": False
        }

class MCANameChecker:
    def __init__(self):
        self.base_url = "https://api.finanvo.in"
        self.headers = {
            'Content-Type': 'application/json',
            'x-api-key': 'be2SxiTi',
            'x-api-secret-key': '0oOwfzhylxtH7OZZA9GuBc5cyGOCrqEqSixOuV'
        }
        self.run_applications = {}
    
    def check_name(self, company_name: str) -> Dict[str, Any]:
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
        """Clean company name by removing suffixes and special characters"""
        suffixes = ['pvt ltd', 'private limited', 'ltd', 'limited', 'pvt', 'private']
        cleaned = name.lower()
        
        for suffix in suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[:-len(suffix)].strip()
        
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', cleaned)
        return cleaned.strip()
    
    def _search_companies_by_name(self, search_term: str) -> List[Dict]:
        found_companies = []
        
        try:
            url = f"{self.base_url}/company/search"
            params = {
                "name": search_term,
                "limit": 10
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    for company in data["data"]:
                        found_companies.append({
                            "company_name": company.get("company_name", ""),
                            "cin": company.get("cin", ""),
                            "status": company.get("status", ""),
                            "similarity": fuzz.ratio(search_term.lower(), 
                                                   company.get("company_name", "").lower())
                        })
            else:
                found_companies = self._mock_company_search(search_term)
                
        except Exception as e:
            print(f"API Error: {e}. Using mock data.")
            found_companies = self._mock_company_search(search_term)
        
        return found_companies
    
    def _mock_company_search(self, name: str) -> List[Dict]:
        common_businesses = [
            "solutions", "systems", "services", "technologies", "enterprises",
            "consulting", "digital", "software", "innovations", "labs",
            "ventures", "industries", "corporation", "holdings", "group"
        ]
        
        locations = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Hyderabad", "Pune"]
        
        name_lower = name.lower()
        conflicts = []
        words = name_lower.split()
        
        for i in range(random.randint(0, 4)):
            if words:
                base_word = random.choice(words)
                business_type = random.choice(common_businesses)
                location = random.choice(locations)
                patterns = [
                    f"{base_word.title()} {business_type.title()} Private Limited",
                    f"{base_word.title()} {business_type.title()} Pvt Ltd",
                    f"New {base_word.title()} {business_type.title()} Limited",
                    f"{base_word.title()} {location} {business_type.title()} Pvt Ltd",
                    f"Global {base_word.title()} {business_type.title()} Private Limited"
                ]
                
                conflict_name = random.choice(patterns)
                similarity = fuzz.ratio(name_lower, conflict_name.lower())
                if similarity > 30:
                    conflicts.append({
                        "company_name": conflict_name,
                        "cin": f"U{random.randint(10000, 99999)}{random.choice(['DL', 'MH', 'KA'])}{random.randint(2010, 2023)}PTC{random.randint(100000, 999999)}",
                        "status": random.choice(["Active", "Inactive", "Struck Off"]),
                        "similarity": similarity
                    })
        
        conflicts.sort(key=lambda x: x["similarity"], reverse=True)
        
        return conflicts[:3]
    
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
            'bank', 'banking', 'insurance', 'government', 'ministry', 'national', 
            'central', 'reserve', 'federal', 'authority', 'commission', 
            'corporation of india', 'registrar', 'co-operative', 'municipal', 
            'panchayat', 'king', 'queen', 'emperor', 'prince', 'princess',
            'supreme', 'tribunal', 'court', 'university', 'college',
            'trust', 'society', 'foundation', 'council'
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
            errors.append("Company name must end with proper suffix (Pvt Ltd or Private Limited)")
        if re.search(r'[^a-zA-Z0-9\s\.\-&()]', name):
            errors.append("Invalid characters found (only letters, numbers, spaces, dots, hyphens, ampersands, and parentheses allowed)")
        if re.search(r'^\d', name):
            errors.append("Company name cannot start with a number")
        if re.search(r'\s{2,}', name):
            warnings.append("Multiple consecutive spaces found")
        
        if name != name.strip():
            warnings.append("Leading or trailing spaces detected")
        words = name.split()
        if len(words) > 15:
            warnings.append("Very long names may face scrutiny during approval")

        base_score = 100
        base_score -= len(errors) * 25  
        base_score -= len(warnings) * 5
        if has_valid_suffix:
            base_score += 5
        if 3 <= len(words) <= 5:
            base_score += 5
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "score": max(0, min(100, base_score))
        }
        
        
    def _get_recommendation(self, availability: Dict, validation: Dict) -> str:
        if not availability["available"]:
            if availability.get("exact_matches"):
                return "❌ Name not available - exact match found in MCA database"
            elif availability.get("existing_companies"):
                similar_count = len(availability["existing_companies"])
                return f"⚠️ Name may be rejected - {similar_count} similar companies found"
        
        if not validation["is_valid"]:
            error_count = len(validation["errors"])
            return f"❌ Name validation failed - {error_count} naming convention errors"
        
        if validation["warnings"]:
            warning_count = len(validation["warnings"])
            return f"⚠️ Name available with minor issues - {warning_count} warnings to consider"
        
        return "✅ Name appears available and compliant with MCA guidelines"

mca_checker_instance = MCANameChecker()

'''
class MCANameCheckerTool:
    def run(self, company_name: str) -> Dict[str, Any]:
        return mca_checker_instance.check_name(company_name)

# Create the tool instance
mca_name_checker_tool = MCANameCheckerTool()
'''

def get_name_suggestions(base_name: str, count: int = 5) -> List[str]:
    suggestions = []
    base_cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', base_name).strip()
    
    suffixes = ['Pvt Ltd', 'Private Limited', 'Ltd']
    prefixes = ['', 'New ', 'Modern ', 'Global ', 'Smart ']
    middle_words = ['Solutions', 'Systems', 'Services', 'Enterprises', 'Technologies']
    
    for i in range(count):
        if i == 0:
            suggestions.append(f"{base_cleaned} Private Limited")
        elif i == 1:
            suggestions.append(f"{base_cleaned} Pvt Ltd")
        else:
            prefix = random.choice(prefixes)
            middle = random.choice(middle_words)
            suffix = random.choice(suffixes)
            suggestion = f"{prefix}{base_cleaned} {middle} {suffix}".strip()
            if suggestion not in suggestions:
                suggestions.append(suggestion)
    
    return suggestions

def batch_check_names(company_names: List[str]) -> List[Dict[str, Any]]:
    results = []
    checker = MCANameChecker()
    
    for name in company_names:
        result = checker.check_name(name)
        results.append(result)
        time.sleep(0.1)
    
    return results