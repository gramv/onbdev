#!/usr/bin/env python3
"""
Frontend API Analysis
Analyzes frontend code to identify expected API endpoints and data structures
"""

import os
import re
import json
from typing import Dict, List, Set, Any

class FrontendAPIAnalyzer:
    def __init__(self):
        self.frontend_path = "hotel-onboarding-frontend/src"
        self.api_calls = []
        self.expected_endpoints = set()
        self.data_structures = {}
        self.issues = []
        
    def analyze_api_calls(self):
        """Extract API calls from frontend code"""
        print("🔍 Analyzing Frontend API Calls...")
        
        # Common patterns for API calls
        patterns = [
            r'axios\.get\([\'"`]([^\'"`]+)[\'"`]',
            r'axios\.post\([\'"`]([^\'"`]+)[\'"`]',
            r'axios\.put\([\'"`]([^\'"`]+)[\'"`]',
            r'axios\.delete\([\'"`]([^\'"`]+)[\'"`]',
            r'fetch\([\'"`]([^\'"`]+)[\'"`]',
            r'http://127\.0\.0\.1:8000([^\'"`\s]+)',
            r'http://localhost:8000([^\'"`\s]+)',
        ]
        
        for root, dirs, files in os.walk(self.frontend_path):
            for file in files:
                if file.endswith(('.tsx', '.ts', '.js', '.jsx')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        for pattern in patterns:
                            matches = re.findall(pattern, content)
                            for match in matches:
                                # Clean up the endpoint
                                endpoint = match.replace('http://127.0.0.1:8000', '').replace('http://localhost:8000', '')
                                if endpoint.startswith('/'):
                                    self.expected_endpoints.add(endpoint)
                                    self.api_calls.append({
                                        'file': file_path,
                                        'endpoint': endpoint,
                                        'pattern': pattern
                                    })
                                    
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
    
    def analyze_data_structures(self):
        """Analyze expected data structures from TypeScript interfaces"""
        print("📊 Analyzing Expected Data Structures...")
        
        interface_pattern = r'interface\s+(\w+)\s*{([^}]+)}'
        type_pattern = r'type\s+(\w+)\s*=\s*{([^}]+)}'
        
        for root, dirs, files in os.walk(self.frontend_path):
            for file in files:
                if file.endswith(('.tsx', '.ts')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Find interfaces
                        interfaces = re.findall(interface_pattern, content, re.DOTALL)
                        for name, body in interfaces:
                            fields = self._parse_interface_fields(body)
                            self.data_structures[name] = {
                                'type': 'interface',
                                'fields': fields,
                                'file': file_path
                            }
                            
                        # Find type definitions
                        types = re.findall(type_pattern, content, re.DOTALL)
                        for name, body in types:
                            fields = self._parse_interface_fields(body)
                            self.data_structures[name] = {
                                'type': 'type',
                                'fields': fields,
                                'file': file_path
                            }
                            
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
    
    def _parse_interface_fields(self, body: str) -> List[Dict[str, Any]]:
        """Parse interface/type body to extract fields"""
        fields = []
        lines = body.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('//') or line.startswith('*'):
                continue
                
            # Simple field parsing (name: type)
            field_match = re.match(r'(\w+)(\??):\s*([^;,\n]+)', line)
            if field_match:
                name, optional, field_type = field_match.groups()
                fields.append({
                    'name': name,
                    'type': field_type.strip(),
                    'optional': bool(optional)
                })
                
        return fields
    
    def analyze_auth_context(self):
        """Analyze authentication context expectations"""
        print("🔐 Analyzing Authentication Context...")
        
        auth_file = os.path.join(self.frontend_path, 'contexts/AuthContext.tsx')
        if os.path.exists(auth_file):
            with open(auth_file, 'r') as f:
                content = f.read()
                
            # Look for API endpoints in auth context
            auth_endpoints = re.findall(r'`\${API_BASE_URL}([^`]+)`', content)
            for endpoint in auth_endpoints:
                self.expected_endpoints.add(endpoint)
                
            # Look for expected response structure
            login_response_match = re.search(r'interface LoginResponse\s*{([^}]+)}', content, re.DOTALL)
            if login_response_match:
                fields = self._parse_interface_fields(login_response_match.group(1))
                self.data_structures['LoginResponse'] = {
                    'type': 'interface',
                    'fields': fields,
                    'file': auth_file
                }
    
    def analyze_dashboard_components(self):
        """Analyze dashboard component API expectations"""
        print("📋 Analyzing Dashboard Components...")
        
        dashboard_files = [
            'pages/HRDashboard.tsx',
            'pages/ManagerDashboard.tsx',
            'components/dashboard/ApplicationsTab.tsx',
            'components/dashboard/PropertiesTab.tsx',
            'components/dashboard/ManagersTab.tsx',
            'components/dashboard/EmployeesTab.tsx'
        ]
        
        for file_name in dashboard_files:
            file_path = os.path.join(self.frontend_path, file_name)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                # Look for axios calls
                axios_calls = re.findall(r'axios\.(get|post|put|delete)\([\'"`]([^\'"`]+)[\'"`]', content)
                for method, url in axios_calls:
                    endpoint = url.replace('http://127.0.0.1:8000', '').replace('http://localhost:8000', '')
                    if endpoint.startswith('/'):
                        self.expected_endpoints.add(endpoint)
                        
                # Look for response.data usage patterns
                response_patterns = re.findall(r'response\.data\.(\w+)', content)
                for pattern in response_patterns:
                    print(f"  Expected response field: {pattern} in {file_name}")
    
    def compare_with_backend_endpoints(self):
        """Compare frontend expectations with backend reality"""
        print("🔄 Comparing Frontend Expectations with Backend...")
        
        # Read backend main file to extract actual endpoints
        backend_file = "hotel-onboarding-backend/app/main_enhanced.py"
        backend_endpoints = set()
        
        if os.path.exists(backend_file):
            with open(backend_file, 'r') as f:
                content = f.read()
                
            # Extract FastAPI route decorators
            route_patterns = [
                r'@app\.get\([\'"`]([^\'"`]+)[\'"`]',
                r'@app\.post\([\'"`]([^\'"`]+)[\'"`]',
                r'@app\.put\([\'"`]([^\'"`]+)[\'"`]',
                r'@app\.delete\([\'"`]([^\'"`]+)[\'"`]'
            ]
            
            for pattern in route_patterns:
                matches = re.findall(pattern, content)
                backend_endpoints.update(matches)
        
        # Compare
        missing_in_backend = self.expected_endpoints - backend_endpoints
        extra_in_backend = backend_endpoints - self.expected_endpoints
        
        print(f"\n📊 Endpoint Comparison Results:")
        print(f"  Frontend expects: {len(self.expected_endpoints)} endpoints")
        print(f"  Backend provides: {len(backend_endpoints)} endpoints")
        print(f"  Missing in backend: {len(missing_in_backend)}")
        print(f"  Extra in backend: {len(extra_in_backend)}")
        
        if missing_in_backend:
            print(f"\n❌ Missing in Backend:")
            for endpoint in sorted(missing_in_backend):
                print(f"    {endpoint}")
                
        if extra_in_backend:
            print(f"\n➕ Extra in Backend:")
            for endpoint in sorted(extra_in_backend):
                print(f"    {endpoint}")
    
    def analyze_error_handling_patterns(self):
        """Analyze how frontend handles errors"""
        print("⚠️  Analyzing Error Handling Patterns...")
        
        error_patterns = [
            r'catch\s*\([^)]*\)\s*{([^}]+)}',
            r'\.catch\([^)]*\)\s*{([^}]+)}',
            r'error\.response\?\.([^.\s]+)',
            r'axios\.isAxiosError\(([^)]+)\)'
        ]
        
        error_handling_files = []
        
        for root, dirs, files in os.walk(self.frontend_path):
            for file in files:
                if file.endswith(('.tsx', '.ts')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                            
                        has_error_handling = any(re.search(pattern, content) for pattern in error_patterns)
                        if has_error_handling:
                            error_handling_files.append(file_path)
                            
                    except Exception as e:
                        continue
        
        print(f"  Files with error handling: {len(error_handling_files)}")
        
        # Check for consistent error handling
        inconsistent_patterns = []
        for file_path in error_handling_files[:5]:  # Check first 5 files
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Look for different error handling patterns
            if 'error.response?.data?.detail' in content and 'error.message' in content:
                inconsistent_patterns.append(file_path)
                
        if inconsistent_patterns:
            self.issues.append(f"Inconsistent error handling in {len(inconsistent_patterns)} files")
    
    def generate_api_specification(self):
        """Generate API specification based on frontend expectations"""
        print("📝 Generating API Specification...")
        
        spec = {
            "expected_endpoints": sorted(list(self.expected_endpoints)),
            "data_structures": self.data_structures,
            "issues": self.issues,
            "recommendations": [
                "Standardize error response format across all endpoints",
                "Implement consistent pagination for list endpoints", 
                "Add request/response validation",
                "Implement proper HTTP status codes",
                "Add comprehensive API documentation",
                "Implement rate limiting",
                "Add request logging and monitoring",
                "Standardize date/time formats",
                "Implement proper CORS handling",
                "Add API versioning strategy"
            ]
        }
        
        with open('frontend_api_specification.json', 'w') as f:
            json.dump(spec, f, indent=2)
            
        print("✅ API specification saved to frontend_api_specification.json")
    
    def run_analysis(self):
        """Run complete frontend API analysis"""
        print("🚀 Starting Frontend API Analysis...")
        print("=" * 60)
        
        self.analyze_api_calls()
        self.analyze_data_structures()
        self.analyze_auth_context()
        self.analyze_dashboard_components()
        self.compare_with_backend_endpoints()
        self.analyze_error_handling_patterns()
        self.generate_api_specification()
        
        print("\n" + "=" * 60)
        print("📊 FRONTEND API ANALYSIS REPORT")
        print("=" * 60)
        
        print(f"\n📍 EXPECTED ENDPOINTS ({len(self.expected_endpoints)}):")
        for endpoint in sorted(self.expected_endpoints):
            print(f"  {endpoint}")
            
        print(f"\n📋 DATA STRUCTURES ({len(self.data_structures)}):")
        for name, info in self.data_structures.items():
            print(f"  {name} ({info['type']}) - {len(info['fields'])} fields")
            
        print(f"\n❌ ISSUES FOUND ({len(self.issues)}):")
        for issue in self.issues:
            print(f"  {issue}")
            
        print("\n" + "=" * 60)
        print("Analysis Complete!")

if __name__ == "__main__":
    analyzer = FrontendAPIAnalyzer()
    analyzer.run_analysis()