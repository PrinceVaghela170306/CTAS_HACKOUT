#!/usr/bin/env python3
"""
Supabase Authentication Integration Test Suite

This script tests the Supabase authentication integration to ensure
all components are working correctly before going live.

Usage:
    python test_supabase_auth.py [--verbose] [--test-user-email=test@example.com]
"""

import asyncio
import argparse
import sys
import json
import requests
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.supabase import get_supabase_client, verify_supabase_token, get_user_data, create_user_data, update_user_data
from app.core.config import settings


class SupabaseAuthTester:
    def __init__(self, verbose: bool = False, test_email: str = "test@example.com"):
        self.verbose = verbose
        self.test_email = test_email
        self.test_password = "TestPassword123!"
        self.supabase = get_supabase_client()
        self.test_results = []
        self.created_user_id = None
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp"""
        if self.verbose or level in ["ERROR", "SUCCESS", "FAIL"]:
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"[{timestamp}] {level}: {message}")
    
    def add_test_result(self, test_name: str, success: bool, message: str = ""):
        """Add test result to results list"""
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
        status = "✅ PASS" if success else "❌ FAIL"
        self.log(f"{status} {test_name}: {message}", "SUCCESS" if success else "FAIL")
    
    def test_supabase_connection(self) -> bool:
        """Test basic Supabase connection"""
        try:
            # Test if we can connect to Supabase
            response = self.supabase.auth.admin.list_users(page=1, per_page=1)
            
            if hasattr(response, 'error') and response.error:
                self.add_test_result("Supabase Connection", False, f"Connection failed: {response.error}")
                return False
            
            self.add_test_result("Supabase Connection", True, "Successfully connected to Supabase")
            return True
            
        except Exception as e:
            self.add_test_result("Supabase Connection", False, f"Exception: {str(e)}")
            return False
    
    def test_configuration(self) -> bool:
        """Test Supabase configuration"""
        config_issues = []
        
        if not settings.SUPABASE_URL:
            config_issues.append("SUPABASE_URL not set")
        elif not settings.SUPABASE_URL.startswith('https://'):
            config_issues.append("SUPABASE_URL should start with https://")
            
        if not settings.SUPABASE_KEY:
            config_issues.append("SUPABASE_KEY not set")
            
        if not settings.SUPABASE_ANON_KEY:
            config_issues.append("SUPABASE_ANON_KEY not set")
        
        if config_issues:
            self.add_test_result("Configuration", False, "; ".join(config_issues))
            return False
        
        self.add_test_result("Configuration", True, "All required configuration values are set")
        return True
    
    def test_user_creation(self) -> bool:
        """Test creating a user in Supabase"""
        try:
            # First, try to delete the test user if it exists
            self.cleanup_test_user()
            
            user_data = {
                'email': self.test_email,
                'password': self.test_password,
                'email_confirm': True,
                'user_metadata': {
                    'full_name': 'Test User',
                    'phone_number': '+1234567890',
                    'test_user': True
                }
            }
            
            response = self.supabase.auth.admin.create_user(user_data)
            
            if hasattr(response, 'error') and response.error:
                self.add_test_result("User Creation", False, f"Failed to create user: {response.error}")
                return False
            
            self.created_user_id = response.user.id
            self.add_test_result("User Creation", True, f"Created test user with ID: {self.created_user_id}")
            return True
            
        except Exception as e:
            self.add_test_result("User Creation", False, f"Exception: {str(e)}")
            return False
    
    def test_user_authentication(self) -> Optional[str]:
        """Test user authentication and token generation"""
        try:
            response = self.supabase.auth.sign_in_with_password({
                'email': self.test_email,
                'password': self.test_password
            })
            
            if hasattr(response, 'error') and response.error:
                self.add_test_result("User Authentication", False, f"Sign in failed: {response.error}")
                return None
            
            if not response.session or not response.session.access_token:
                self.add_test_result("User Authentication", False, "No access token received")
                return None
            
            access_token = response.session.access_token
            self.add_test_result("User Authentication", True, "Successfully authenticated and received token")
            return access_token
            
        except Exception as e:
            self.add_test_result("User Authentication", False, f"Exception: {str(e)}")
            return None
    
    def test_token_verification(self, access_token: str) -> bool:
        """Test token verification functionality"""
        try:
            user_data = verify_supabase_token(access_token)
            
            if not user_data:
                self.add_test_result("Token Verification", False, "Token verification returned None")
                return False
            
            if user_data.get('email') != self.test_email:
                self.add_test_result("Token Verification", False, f"Email mismatch: expected {self.test_email}, got {user_data.get('email')}")
                return False
            
            self.add_test_result("Token Verification", True, "Token verified successfully")
            return True
            
        except Exception as e:
            self.add_test_result("Token Verification", False, f"Exception: {str(e)}")
            return False
    
    def test_backend_user_operations(self) -> bool:
        """Test backend user CRUD operations"""
        if not self.created_user_id:
            self.add_test_result("Backend User Operations", False, "No test user ID available")
            return False
        
        try:
            # Test get user data
            user_data = get_user_data(self.created_user_id)
            if not user_data:
                # User doesn't exist in backend, try to create
                test_user_data = {
                    'id': self.created_user_id,
                    'email': self.test_email,
                    'full_name': 'Test User',
                    'phone_number': '+1234567890'
                }
                
                created_user = create_user_data(test_user_data)
                if not created_user:
                    self.add_test_result("Backend User Operations", False, "Failed to create user in backend")
                    return False
                
                self.log("Created user in backend database", "INFO")
            
            # Test update user data
            update_data = {'full_name': 'Updated Test User'}
            updated_user = update_user_data(self.created_user_id, update_data)
            
            if not updated_user:
                self.add_test_result("Backend User Operations", False, "Failed to update user data")
                return False
            
            self.add_test_result("Backend User Operations", True, "All backend user operations successful")
            return True
            
        except Exception as e:
            self.add_test_result("Backend User Operations", False, f"Exception: {str(e)}")
            return False
    
    def test_api_endpoints(self) -> bool:
        """Test API endpoints with Supabase authentication"""
        try:
            # Get access token
            access_token = self.test_user_authentication()
            if not access_token:
                self.add_test_result("API Endpoints", False, "No access token for API testing")
                return False
            
            base_url = "http://localhost:8000"  # Adjust if needed
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Test health check endpoint
            response = requests.get(f"{base_url}/supabase-auth/health", headers=headers)
            if response.status_code != 200:
                self.add_test_result("API Endpoints", False, f"Health check failed: {response.status_code}")
                return False
            
            # Test profile endpoint
            response = requests.get(f"{base_url}/supabase-auth/profile", headers=headers)
            if response.status_code != 200:
                self.add_test_result("API Endpoints", False, f"Profile endpoint failed: {response.status_code}")
                return False
            
            # Test profile update
            update_data = {'full_name': 'API Test User'}
            response = requests.put(f"{base_url}/supabase-auth/profile", 
                                  headers=headers, 
                                  json=update_data)
            if response.status_code != 200:
                self.add_test_result("API Endpoints", False, f"Profile update failed: {response.status_code}")
                return False
            
            self.add_test_result("API Endpoints", True, "All API endpoints working correctly")
            return True
            
        except requests.exceptions.ConnectionError:
            self.add_test_result("API Endpoints", False, "Cannot connect to backend server. Is it running on localhost:8000?")
            return False
        except Exception as e:
            self.add_test_result("API Endpoints", False, f"Exception: {str(e)}")
            return False
    
    def cleanup_test_user(self):
        """Clean up test user after testing"""
        try:
            if self.created_user_id:
                self.supabase.auth.admin.delete_user(self.created_user_id)
                self.log(f"Cleaned up test user: {self.created_user_id}", "INFO")
            else:
                # Try to find and delete by email
                response = self.supabase.auth.admin.list_users()
                if hasattr(response, 'users'):
                    for user in response.users:
                        if user.email == self.test_email:
                            self.supabase.auth.admin.delete_user(user.id)
                            self.log(f"Cleaned up test user by email: {user.id}", "INFO")
                            break
        except Exception as e:
            self.log(f"Failed to cleanup test user: {str(e)}", "ERROR")
    
    def run_all_tests(self) -> bool:
        """Run all tests and return overall success"""
        self.log("Starting Supabase Authentication Integration Tests", "INFO")
        self.log("=" * 60, "INFO")
        
        tests = [
            ("Configuration", self.test_configuration),
            ("Supabase Connection", self.test_supabase_connection),
            ("User Creation", self.test_user_creation),
            ("User Authentication", lambda: self.test_user_authentication() is not None),
            ("Token Verification", lambda: self.test_token_verification(self.test_user_authentication() or "")),
            ("Backend User Operations", self.test_backend_user_operations),
            ("API Endpoints", self.test_api_endpoints)
        ]
        
        all_passed = True
        
        for test_name, test_func in tests:
            try:
                if not test_func():
                    all_passed = False
            except Exception as e:
                self.add_test_result(test_name, False, f"Unexpected error: {str(e)}")
                all_passed = False
        
        # Cleanup
        self.cleanup_test_user()
        
        # Print summary
        self.print_summary()
        
        return all_passed
    
    def print_summary(self):
        """Print test summary"""
        self.log("=" * 60, "INFO")
        self.log("TEST SUMMARY", "INFO")
        self.log("=" * 60, "INFO")
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        self.log(f"Tests passed: {passed}/{total}", "INFO")
        
        if passed == total:
            self.log("🎉 All tests passed! Supabase authentication is ready.", "SUCCESS")
        else:
            self.log("❌ Some tests failed. Please review the issues above.", "FAIL")
            
        # Print failed tests
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            self.log("\nFailed Tests:", "ERROR")
            for test in failed_tests:
                self.log(f"  - {test['test']}: {test['message']}", "ERROR")
    
    def export_results(self, filename: str = "supabase_test_results.json"):
        """Export test results to JSON file"""
        with open(filename, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'test_email': self.test_email,
                'results': self.test_results
            }, f, indent=2)
        
        self.log(f"Test results exported to {filename}", "INFO")


def main():
    parser = argparse.ArgumentParser(description='Test Supabase Authentication Integration')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--test-user-email', default='test@example.com', help='Email for test user')
    parser.add_argument('--export-results', help='Export results to JSON file')
    
    args = parser.parse_args()
    
    tester = SupabaseAuthTester(verbose=args.verbose, test_email=args.test_user_email)
    
    success = tester.run_all_tests()
    
    if args.export_results:
        tester.export_results(args.export_results)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()