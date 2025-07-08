'''
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
sys.modules["sqlite3.dbapi2"] = sys.modules["pysqlite3.dbapi2"]
'''
import sys
import os
from crew import CompanyMcaCrew
import json

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py 'Company Name'")
        sys.exit(1)
    
    original_name = sys.argv[1]
    
    print(f"Checking availability for: {original_name}")
    print("=" * 50)
    
    try:
        crew = CompanyMcaCrew()
        result = crew.run_crew(original_name)
        print("\nResults:")
        print(result)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()