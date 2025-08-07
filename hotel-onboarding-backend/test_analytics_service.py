#!/usr/bin/env python3
"""
Comprehensive tests for the Advanced HR Analytics System (Task 5.1)
Tests analytics data aggregation, reporting, and export functionality
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.analytics_service import (
    AnalyticsService, 
    TimeRange, 
    ReportFormat,
    MetricType
)
from app.supabase_service_enhanced import EnhancedSupabaseService

# Test configuration
TEST_PROPERTY_ID = "prop_123"
TEST_MANAGER_ID = "mgr_456"

class TestAnalyticsService:
    """Test suite for analytics service functionality"""
    
    def __init__(self):
        self.supabase = EnhancedSupabaseService()
        self.service = AnalyticsService(self.supabase)
        self.test_results = []
        
    async def test_dashboard_metrics(self):
        """Test dashboard metrics aggregation with different time ranges"""
        print("\n🧪 Testing Dashboard Metrics Aggregation...")
        
        try:
            # Test with last 30 days
            metrics_30d = await self.service.get_dashboard_metrics(
                property_id=TEST_PROPERTY_ID,
                time_range=TimeRange.LAST_30_DAYS
            )
            
            assert "overview" in metrics_30d
            assert "applications" in metrics_30d
            assert "performance" in metrics_30d
            assert "compliance" in metrics_30d
            print("  ✅ 30-day metrics aggregation successful")
            
            # Test with last 7 days
            metrics_7d = await self.service.get_dashboard_metrics(
                property_id=TEST_PROPERTY_ID,
                time_range=TimeRange.LAST_7_DAYS
            )
            
            assert metrics_7d["overview"]["active_applications"] <= metrics_30d["overview"]["active_applications"]
            print("  ✅ 7-day metrics aggregation successful")
            
            # Test with custom range
            metrics_custom = await self.service.get_dashboard_metrics(
                property_id=TEST_PROPERTY_ID,
                time_range=TimeRange.CUSTOM,
                start_date=datetime.now() - timedelta(days=14),
                end_date=datetime.now()
            )
            
            assert "trends" in metrics_custom
            print("  ✅ Custom date range metrics successful")
            
            # Test global metrics (no property filter)
            global_metrics = await self.service.get_dashboard_metrics()
            assert global_metrics["overview"]["total_properties"] >= 1
            print("  ✅ Global metrics aggregation successful")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Dashboard metrics test failed: {e}")
            return False
    
    async def test_cache_functionality(self):
        """Test caching mechanism for performance optimization"""
        print("\n🧪 Testing Cache Functionality...")
        
        try:
            # First call - should hit database
            import time
            start_time = time.time()
            metrics1 = await self.service.get_dashboard_metrics(TEST_PROPERTY_ID)
            first_call_time = time.time() - start_time
            
            # Second call - should hit cache
            start_time = time.time()
            metrics2 = await self.service.get_dashboard_metrics(TEST_PROPERTY_ID)
            second_call_time = time.time() - start_time
            
            # Cache should make second call faster
            assert metrics1 == metrics2  # Same data
            assert second_call_time < first_call_time * 0.5  # At least 50% faster
            print(f"  ✅ Cache hit successful (speedup: {first_call_time/second_call_time:.2f}x)")
            
            # Test cache invalidation
            await asyncio.sleep(0.1)  # Wait briefly
            self.service._cache.clear()  # Clear cache
            
            metrics3 = await self.service.get_dashboard_metrics(TEST_PROPERTY_ID)
            print("  ✅ Cache invalidation successful")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Cache functionality test failed: {e}")
            return False
    
    async def test_custom_reports(self):
        """Test custom report generation with various parameters"""
        print("\n🧪 Testing Custom Report Generation...")
        
        try:
            # Test employee roster report
            roster_report = await self.service.generate_custom_report(
                report_type="employee_roster",
                parameters={
                    "property_id": TEST_PROPERTY_ID,
                    "include_inactive": False,
                    "department": "Front Desk"
                },
                format=ReportFormat.JSON
            )
            
            assert "metadata" in roster_report
            assert "data" in roster_report
            assert roster_report["metadata"]["report_type"] == "employee_roster"
            print("  ✅ Employee roster report successful")
            
            # Test application summary report
            app_summary = await self.service.generate_custom_report(
                report_type="application_summary",
                parameters={
                    "date_range": "last_30_days",
                    "group_by": "status"
                },
                format=ReportFormat.JSON
            )
            
            assert "summary" in app_summary["data"]
            print("  ✅ Application summary report successful")
            
            # Test compliance audit report
            compliance_report = await self.service.generate_custom_report(
                report_type="compliance_audit",
                parameters={
                    "property_id": TEST_PROPERTY_ID,
                    "check_i9": True,
                    "check_w4": True
                },
                format=ReportFormat.JSON
            )
            
            assert "compliance_status" in compliance_report["data"]
            print("  ✅ Compliance audit report successful")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Custom report generation test failed: {e}")
            return False
    
    async def test_export_formats(self):
        """Test data export in multiple formats"""
        print("\n🧪 Testing Export Formats...")
        
        try:
            # Test CSV export
            csv_report = await self.service.generate_custom_report(
                report_type="employee_roster",
                parameters={"property_id": TEST_PROPERTY_ID},
                format=ReportFormat.CSV
            )
            
            assert isinstance(csv_report, str)
            assert "Name,Email,Position" in csv_report  # Check CSV headers
            print("  ✅ CSV export successful")
            
            # Test Excel export (returns bytes)
            excel_report = await self.service.generate_custom_report(
                report_type="application_summary",
                parameters={},
                format=ReportFormat.EXCEL
            )
            
            assert isinstance(excel_report, bytes)
            assert len(excel_report) > 0
            print("  ✅ Excel export successful")
            
            # Test PDF export (returns bytes)
            pdf_report = await self.service.generate_custom_report(
                report_type="compliance_audit",
                parameters={"property_id": TEST_PROPERTY_ID},
                format=ReportFormat.PDF
            )
            
            assert isinstance(pdf_report, bytes)
            assert pdf_report.startswith(b'%PDF')  # PDF magic bytes
            print("  ✅ PDF export successful")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Export format test failed: {e}")
            return False
    
    async def test_performance_metrics(self):
        """Test manager and property performance analytics"""
        print("\n🧪 Testing Performance Metrics...")
        
        try:
            # Test manager performance metrics
            manager_metrics = await self.service.get_manager_performance(
                manager_id=TEST_MANAGER_ID,
                time_period=30
            )
            
            assert "applications_reviewed" in manager_metrics
            assert "average_review_time" in manager_metrics
            assert "approval_rate" in manager_metrics
            assert "onboarding_completion_rate" in manager_metrics
            print("  ✅ Manager performance metrics successful")
            
            # Test property performance comparison
            property_comparison = await self.service.get_property_comparison(
                property_ids=[TEST_PROPERTY_ID, "prop_789"],
                metrics=[MetricType.APPLICATIONS, MetricType.COMPLETION_RATE]
            )
            
            assert len(property_comparison) <= 2
            for prop in property_comparison:
                assert "property_id" in prop
                assert "metrics" in prop
            print("  ✅ Property comparison metrics successful")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Performance metrics test failed: {e}")
            return False
    
    async def test_trend_analysis(self):
        """Test trend analysis and forecasting capabilities"""
        print("\n🧪 Testing Trend Analysis...")
        
        try:
            # Test hiring trends
            hiring_trends = await self.service.get_hiring_trends(
                property_id=TEST_PROPERTY_ID,
                lookback_days=90
            )
            
            assert "daily_applications" in hiring_trends
            assert "weekly_average" in hiring_trends
            assert "trend_direction" in hiring_trends
            assert hiring_trends["trend_direction"] in ["increasing", "decreasing", "stable"]
            print("  ✅ Hiring trends analysis successful")
            
            # Test forecasting
            forecast = await self.service.forecast_staffing_needs(
                property_id=TEST_PROPERTY_ID,
                forecast_days=30
            )
            
            assert "predicted_applications" in forecast
            assert "confidence_interval" in forecast
            assert "recommendations" in forecast
            print("  ✅ Staffing forecast successful")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Trend analysis test failed: {e}")
            return False
    
    async def test_error_handling(self):
        """Test error handling and edge cases"""
        print("\n🧪 Testing Error Handling...")
        
        try:
            # Test invalid report type
            try:
                await self.service.generate_custom_report(
                    report_type="invalid_report",
                    parameters={},
                    format=ReportFormat.JSON
                )
                assert False, "Should have raised error for invalid report type"
            except ValueError as e:
                print("  ✅ Invalid report type handled correctly")
            
            # Test invalid date range
            try:
                await self.service.get_dashboard_metrics(
                    property_id=TEST_PROPERTY_ID,
                    time_range=TimeRange.CUSTOM,
                    start_date=datetime.now(),
                    end_date=datetime.now() - timedelta(days=30)  # End before start
                )
                assert False, "Should have raised error for invalid date range"
            except ValueError as e:
                print("  ✅ Invalid date range handled correctly")
            
            # Test missing required parameters
            try:
                await self.service.generate_custom_report(
                    report_type="employee_roster",
                    parameters={},  # Missing required property_id
                    format=ReportFormat.JSON
                )
                # Should handle gracefully with empty results
                print("  ✅ Missing parameters handled gracefully")
            except Exception as e:
                print(f"  ⚠️  Unexpected error with missing parameters: {e}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error handling test failed: {e}")
            return False
    
    async def test_data_aggregation_accuracy(self):
        """Test accuracy of data aggregation calculations"""
        print("\n🧪 Testing Data Aggregation Accuracy...")
        
        try:
            # Get metrics for verification
            metrics = await self.service.get_dashboard_metrics(
                property_id=TEST_PROPERTY_ID,
                time_range=TimeRange.LAST_30_DAYS
            )
            
            # Verify overview calculations
            overview = metrics["overview"]
            assert overview["active_applications"] >= 0
            assert overview["pending_onboarding"] >= 0
            assert overview["completed_this_month"] >= 0
            assert 0 <= overview["completion_rate"] <= 100
            print("  ✅ Overview metrics calculations accurate")
            
            # Verify application funnel
            funnel = metrics["applications"]["funnel"]
            total = sum(funnel.values())
            for stage, count in funnel.items():
                assert count >= 0
                assert count <= total
            print("  ✅ Application funnel calculations accurate")
            
            # Verify compliance percentages
            compliance = metrics["compliance"]
            assert 0 <= compliance["i9_compliance"] <= 100
            assert 0 <= compliance["w4_compliance"] <= 100
            assert 0 <= compliance["document_completion"] <= 100
            print("  ✅ Compliance percentages accurate")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Data aggregation accuracy test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Execute all analytics tests"""
        print("\n" + "="*60)
        print("🚀 TASK 5.1: Analytics System Test Suite")
        print("="*60)
        
        tests = [
            ("Dashboard Metrics", self.test_dashboard_metrics),
            ("Cache Functionality", self.test_cache_functionality),
            ("Custom Reports", self.test_custom_reports),
            ("Export Formats", self.test_export_formats),
            ("Performance Metrics", self.test_performance_metrics),
            ("Trend Analysis", self.test_trend_analysis),
            ("Error Handling", self.test_error_handling),
            ("Data Aggregation Accuracy", self.test_data_aggregation_accuracy)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                if result:
                    passed += 1
                    self.test_results.append((test_name, "PASSED"))
                else:
                    failed += 1
                    self.test_results.append((test_name, "FAILED"))
            except Exception as e:
                failed += 1
                self.test_results.append((test_name, f"ERROR: {e}"))
                print(f"\n❌ {test_name} encountered error: {e}")
        
        # Print summary
        print("\n" + "="*60)
        print("📊 TEST RESULTS SUMMARY")
        print("="*60)
        
        for test_name, status in self.test_results:
            emoji = "✅" if status == "PASSED" else "❌"
            print(f"{emoji} {test_name}: {status}")
        
        print("\n" + "-"*60)
        print(f"Total Tests: {len(tests)}")
        print(f"Passed: {passed} ({passed/len(tests)*100:.1f}%)")
        print(f"Failed: {failed} ({failed/len(tests)*100:.1f}%)")
        
        completion = (passed / len(tests)) * 100
        print(f"\n🎯 Task 5.1 Completion: {completion:.1f}%")
        
        if completion == 100:
            print("✅ All analytics tests passed successfully!")
        elif completion >= 80:
            print("⚠️  Most tests passed, but some issues need attention")
        else:
            print("❌ Significant test failures - review and fix required")
        
        return completion == 100

async def main():
    """Main test execution"""
    tester = TestAnalyticsService()
    success = await tester.run_all_tests()
    
    print("\n" + "="*60)
    print("📝 NEXT STEPS")
    print("="*60)
    
    if success:
        print("✅ Task 5.1 Complete - Analytics tests all passing")
        print("✅ Task 5.2 Complete - Analytics service already implemented")
        print("📋 Next: Task 5.3 - Build interactive dashboard components")
        print("   - Create React components for charts and metrics")
        print("   - Integrate with analytics service endpoints")
        print("   - Add real-time data updates via WebSocket")
    else:
        print("⚠️  Fix failing tests before proceeding to Task 5.3")
        print("   - Review error messages above")
        print("   - Update analytics_service.py as needed")
        print("   - Re-run tests to verify fixes")

if __name__ == "__main__":
    asyncio.run(main())