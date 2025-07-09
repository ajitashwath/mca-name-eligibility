# MCA Company Name Checker 🏢
An AI-powered company name availability checker that validates names against the Indian Ministry of Corporate Affairs (MCA) database using the Finanvo API and CrewAI framework.

## Features
- **Real-time MCA Database Check**: Validates company names against live MCA records
- **AI-Powered Analysis**: Uses CrewAI agents for intelligent name research and validation
- **Batch Processing**: Check multiple names simultaneously with progress tracking
- **Smart Alternatives**: Generates 20+ compliant alternative names automatically
- **Compliance Scoring**: Assigns scores (0-100) based on MCA naming conventions
- **Interactive Dashboard**: Streamlit UI with charts and analytics
- **Export Functionality**: Download results as CSV or JSON
- **Search History**: Track and review previous searches

## Architecture

### Core Components
1. **Streamlit App** (`app.py`): Web interface with interactive dashboard
2. **CrewAI Framework** (`crew.py`): Multi-agent system for name processing
3. **MCA Tool** (`custom_tool.py`): Finanvo API integration and validation logic
4. **Main Script** (`main.py`): Command-line interface

### Agent System
- **Name Researcher**: Analyzes original name availability
- **Name Generator**: Creates intelligent alternatives
- **Name Validator**: Ensures compliance with MCA guidelines

## Installation

### Prerequisites
- Python 3.9+
- Streamlit
- CrewAI

### Setup

```bash
# Clone repository
git clone https://github.com/Kartavya-AI/Company-Name-MCA.git
cd Company-Name-MCA

# Set up configuration files
# Create config/agents.yaml and config/tasks.yaml
```

### Required Dependencies

```
streamlit
crewai
pandas
plotly
requests
pysqlite3
fuzzywuzzy
pyyaml
```

## Configuration
### Agent Configuration

Create `config/agents.yaml`:

```yaml
name_researcher:
  role: "Company Name Research Specialist"
  goal: "Research and analyze company name availability"
  backstory: "Expert in MCA database research"
  verbose: true
  allow_delegation: false
  max_iter: 3

name_generator:
  role: "Company Name Generator"
  goal: "Generate compliant alternative names"
  backstory: "Creative naming specialist"
  verbose: true
  allow_delegation: false
  max_iter: 3

name_validator:
  role: "MCA Compliance Validator"
  goal: "Validate names against MCA guidelines"
  backstory: "Legal compliance expert"
  verbose: true
  allow_delegation: false
  max_iter: 3
```

### Task Configuration

Create `config/tasks.yaml`:

```yaml
research_original_name:
  description: "Research the availability of {original_name}"
  expected_output: "Detailed availability report"

generate_alternative_names:
  description: "Generate 20 alternative names based on research"
  expected_output: "List of compliant alternatives"

validate_name_availability:
  description: "Validate all names for MCA compliance"
  expected_output: "Comprehensive validation report"
```

## Usage

### Web Interface

```bash
streamlit run app.py
```

Navigate to `http://localhost:8501` and:

1. Enter your desired company name
2. Choose whether to generate alternatives
3. Click "Check Name" to start analysis
4. View results with scores and recommendations
5. Export data or select approved names

### Command Line

```bash
python main.py "Your Company Name Pvt Ltd"
```

### API Integration

```python
from src.company_mca.tools.custom_tool import mca_name_checker

result = mca_name_checker._run("Tech Solutions Pvt Ltd")
print(result)
```

## Key Features Explained

### Name Validation

The system checks for:

- **Length**: 3-120 characters
- **Prohibited Words**: Bank, Government, Ministry, etc.
- **Valid Suffixes**: Pvt Ltd, Private Limited, Limited
- **Character Restrictions**: No special characters except dots, hyphens
- **Number Restrictions**: Cannot start with numbers

### Scoring System

- **90-100**: Excellent compliance
- **70-89**: Good with minor issues  
- **50-69**: Moderate issues
- **Below 50**: Significant problems

### Alternative Generation

Creates 20 diverse alternatives using:
- Technology terms (Systems, Digital, Tech)
- Service words (Solutions, Consulting, Services)
- Business terms (Enterprises, Industries, Group)
- Modern prefixes (Global, Smart, Neo, Pro)

### Similarity Detection

Uses fuzzy matching to identify:
- Exact matches (>95% similarity)
- Similar companies (>70% similarity)
- Potential conflicts


## API Integration

### Finanvo API

The system integrates with Finanvo's company search API:

```python
# Search endpoint
GET https://api.finanvo.in/company/search
Parameters: name, limit
Headers: x-api-key, x-api-secret-key
```

### Fallback System

If API fails, the system uses intelligent mocking:
- Generates realistic company conflicts
- Maintains similarity scoring
- Provides consistent validation

## Dashboard Features

### Results Analysis

- **Summary Metrics**: Total checked, available count, average score
- **Score Distribution**: Visual charts showing compliance levels
- **Issues Summary**: Common errors and warnings
- **Export Options**: CSV and JSON download

### Search History

- Tracks recent searches
- Shows timestamps and results
- Provides quick access to previous analyses

### Real-time Updates

- Progress bars for batch processing
- Live status indicators
- Instant feedback on selections

## API Response Format

```json
{
  "name": "Tech Solutions Pvt Ltd",
  "cleaned_name": "tech solutions",
  "is_available": true,
  "existing_companies": [],
  "validation": {
    "is_valid": true,
    "errors": [],
    "warnings": [],
    "score": 95
  },
  "recommendation": "✅ Name appears available and compliant"
}
```
