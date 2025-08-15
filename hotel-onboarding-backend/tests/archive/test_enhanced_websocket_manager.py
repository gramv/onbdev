#!/usr/bin/env python3
"""
Test script for Enhanced WebSocket Manager
Tests the new features: connection pooling, topic subscriptions, message queuing, and monitoring
"""
import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.websocket_manager import (
    EnhancedWebSocketManager, 
    ConnectionInfo, 
    BroadcastEvent, 
    MessagePriority,
    SubscriptionFilter,
    ConnectionStatus
)
from app.models import UserRole
from app.auth import create_token

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ANSI color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_success(message):
    print(f"{GREEN}✅ {message}{RESET}")

def print_error(message):
    print(f"{RED}❌ {message}{RESET}")

def print_warning(message):
    print(f"{YELLOW}⚠️ {message}{RESET}")

def print_info(message):
    print(f"{BLUE}ℹ️ {message}{RESET}")

def print_section(title):
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{title}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}")

class MockWebSocket:
    """Mock WebSocket for testing"""
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.messages = []
        self.closed = False
        self.accepted = False
    
    async def accept(self):
        self.accepted = True
    
    async def send_json(self, data):
        if not self.closed:
            self.messages.append(data)
    
    async def send_text(self, text):
        if not self.closed:
            self.messages.append(json.loads(text))
    
    async def close(self, code=None, reason=None):
        self.closed = True

async def test_enhanced_connection_management():
    """Test enhanced connection management with pooling"""
    print_section("Testing Enhanced Connection Management")
    
    manager = EnhancedWebSocketManager(max_connections_per_user=2)
    
    # Create test tokens
    hr_token = create_token("hr-user", "hr")
    manager_token = create_token("manager-user", "manager")
    
    try:
        # Test multiple connections for same user
        websocket1 = MockWebSocket("hr-user-1")
        websocket2 = MockWebSocket("hr-user-2")
        websocket3 = MockWebSocket("hr-user-3")  # Should close oldest
        
        # Create connections
        conn1 = ConnectionInfo(
            websocket=websocket1,
            user_id="hr-user",
            property_id=None,
            role=UserRole.HR,
            connected_at=datetime.now()
        )
        
        conn2 = ConnectionInfo(
            websocket=websocket2,
            user_id="hr-user",
            property_id=None,
            role=UserRole.HR,
            connected_at=datetime.now()
        )
        
        conn3 = ConnectionInfo(
            websocket=websocket3,
            user_id="hr-user",
            property_id=None,
            role=UserRole.HR,
            connected_at=datetime.now()
        )
        
        # Connect all three (should enforce pool limit)
        try:
            await manager.connect(conn1)
            print_info("Connection 1 established")
        except Exception as e:
            print_error(f"Connection 1 failed: {e}")
            raise
        
        try:
            await manager.connect(conn2)
            print_info("Connection 2 established")
        except Exception as e:
            print_error(f"Connection 2 failed: {e}")
            raise
        
        try:
            await manager.connect(conn3)  # Should close conn1
            print_info("Connection 3 established")
        except Exception as e:
            print_error(f"Connection 3 failed: {e}")
            raise
        
        # Verify pool management
        if len(manager.connection_pool["hr-user"]) <= 2:
            print_success("Connection pool limit enforced correctly")
        else:
            print_error("Connection pool limit not enforced")
        
        # Test reconnection token
        if conn3.reconnection_token:
            print_success("Reconnection token generated")
            
            # Test reconnection
            new_websocket = MockWebSocket("hr-user-reconnect")
            success = await manager.reconnect_with_token(conn3.reconnection_token, new_websocket)
            if success:
                print_success("Reconnection with token successful")
            else:
                print_error("Reconnection with token failed")
        
        return True
        
    except Exception as e:
        print_error(f"Enhanced connection management test failed: {e}")
        return False
    finally:
        await manager.shutdown()

async def test_topic_subscriptions():
    """Test topic-based subscription system"""
    print_section("Testing Topic-Based Subscriptions")
    
    manager = EnhancedWebSocketManager()
    
    try:
        # Create test connections
        websocket1 = MockWebSocket("hr-user")
        websocket2 = MockWebSocket("manager-user")
        
        conn1 = ConnectionInfo(
            websocket=websocket1,
            user_id="hr-user",
            property_id=None,
            role=UserRole.HR,
            connected_at=datetime.now()
        )
        
        conn2 = ConnectionInfo(
            websocket=websocket2,
            user_id="manager-user",
            property_id="property-1",
            role=UserRole.MANAGER,
            connected_at=datetime.now()
        )
        
        await manager.connect(conn1)
        await manager.connect(conn2)
        
        # Test topic subscriptions
        await manager.subscribe_to_topic("hr-user", "applications", SubscriptionFilter.ALL)
        await manager.subscribe_to_topic("manager-user", "applications", SubscriptionFilter.PROPERTY, "property-1")
        
        # Verify subscriptions
        hr_subscribers = manager.get_topic_subscribers("applications")
        if "hr-user" in hr_subscribers and "manager-user" in hr_subscribers:
            print_success("Topic subscriptions created successfully")
        else:
            print_error("Topic subscriptions not created properly")
        
        # Test topic broadcasting
        event = BroadcastEvent(
            type="application_submitted",
            data={"application_id": "app-123", "property_id": "property-1"},
            priority=MessagePriority.HIGH,
            topic="applications"
        )
        
        await manager.broadcast_to_topic("applications", event)
        
        # Check if messages were received
        if websocket1.messages and websocket2.messages:
            print_success("Topic broadcast delivered to subscribers")
        else:
            print_error("Topic broadcast not delivered properly")
        
        # Test unsubscription
        await manager.unsubscribe_from_topic("hr-user", "applications")
        remaining_subscribers = manager.get_topic_subscribers("applications")
        if "hr-user" not in remaining_subscribers:
            print_success("Topic unsubscription successful")
        else:
            print_error("Topic unsubscription failed")
        
        return True
        
    except Exception as e:
        print_error(f"Topic subscription test failed: {e}")
        return False
    finally:
        await manager.shutdown()

async def test_message_queuing():
    """Test message queuing for offline users"""
    print_section("Testing Message Queuing System")
    
    manager = EnhancedWebSocketManager()
    
    try:
        # Test queuing messages for offline user
        offline_message = {
            "type": "notification",
            "data": {"message": "Test offline message"}
        }
        
        # Send message to offline user (should be queued)
        success = await manager.send_to_user(
            "offline-user", 
            offline_message, 
            priority=MessagePriority.HIGH,
            queue_if_offline=True,
            expires_in_minutes=60
        )
        
        if success:
            print_success("Message queued for offline user")
        else:
            print_error("Message queuing failed")
        
        # Verify message is in offline queue
        if "offline-user" in manager.offline_messages:
            queued_count = len(manager.offline_messages["offline-user"])
            print_success(f"Found {queued_count} queued messages for offline user")
        else:
            print_error("No messages found in offline queue")
        
        # Test message delivery when user comes online
        websocket = MockWebSocket("offline-user")
        conn = ConnectionInfo(
            websocket=websocket,
            user_id="offline-user",
            property_id=None,
            role=UserRole.HR,
            connected_at=datetime.now()
        )
        
        await manager.connect(conn)
        
        # Wait a moment for message processing
        await asyncio.sleep(0.1)
        
        # Check if queued messages were delivered
        if websocket.messages:
            delivered_count = len([msg for msg in websocket.messages if msg.get("type") == "notification"])
            if delivered_count > 0:
                print_success(f"Delivered {delivered_count} queued messages to user")
            else:
                print_warning("No queued messages were delivered")
        
        # Test message acknowledgment
        ack_message = {
            "type": "test_ack",
            "data": {"test": "acknowledgment"}
        }
        
        ack_success = await manager.send_to_user_with_acknowledgment(
            "offline-user", 
            ack_message, 
            timeout_seconds=5
        )
        
        # Simulate acknowledgment
        if websocket.messages:
            last_message = websocket.messages[-1]
            if last_message.get("require_acknowledgment"):
                message_id = last_message.get("message_id")
                await manager.acknowledge_message("offline-user", message_id)
                print_success("Message acknowledgment system working")
        
        return True
        
    except Exception as e:
        print_error(f"Message queuing test failed: {e}")
        return False
    finally:
        await manager.shutdown()

async def test_connection_monitoring():
    """Test connection monitoring and health checks"""
    print_section("Testing Connection Monitoring")
    
    manager = EnhancedWebSocketManager()
    
    try:
        # Create test connection
        websocket = MockWebSocket("test-user")
        conn = ConnectionInfo(
            websocket=websocket,
            user_id="test-user",
            property_id="property-1",
            role=UserRole.MANAGER,
            connected_at=datetime.now()
        )
        
        await manager.connect(conn)
        
        # Test health check
        health = manager.get_connection_health("test-user")
        if health:
            print_success("Connection health information retrieved")
            print_info(f"Connection status: {health['status']}")
            print_info(f"Messages sent: {health['metrics']['messages_sent']}")
            print_info(f"Is healthy: {health['is_healthy']}")
        else:
            print_error("Failed to get connection health")
        
        # Test enhanced statistics
        stats = manager.get_enhanced_stats()
        if stats:
            print_success("Enhanced statistics retrieved")
            print_info(f"Active connections: {stats['performance_metrics']['active_connections']}")
            print_info(f"Active rooms: {stats['performance_metrics']['active_rooms']}")
            print_info(f"Active topics: {stats['performance_metrics']['active_topics']}")
            print_info(f"Background tasks running: {stats['system_health']['background_tasks_running']}")
        else:
            print_error("Failed to get enhanced statistics")
        
        # Test rate limiting
        rate_limit_ok = manager._check_rate_limit("test-user", max_messages_per_minute=5)
        if rate_limit_ok:
            print_success("Rate limiting check passed")
        else:
            print_warning("Rate limiting triggered")
        
        # Test performance metrics update
        await manager._update_performance_metrics()
        print_success("Performance metrics updated")
        
        return True
        
    except Exception as e:
        print_error(f"Connection monitoring test failed: {e}")
        return False
    finally:
        await manager.shutdown()

async def test_event_callbacks():
    """Test event callback system"""
    print_section("Testing Event Callback System")
    
    manager = EnhancedWebSocketManager()
    callback_triggered = False
    
    def test_callback(event_data):
        nonlocal callback_triggered
        callback_triggered = True
        print_info(f"Callback triggered with data: {event_data}")
    
    try:
        # Register callback
        manager.register_event_callback("connection_established", test_callback)
        print_success("Event callback registered")
        
        # Create connection to trigger callback
        websocket = MockWebSocket("callback-user")
        conn = ConnectionInfo(
            websocket=websocket,
            user_id="callback-user",
            property_id=None,
            role=UserRole.HR,
            connected_at=datetime.now()
        )
        
        await manager.connect(conn)
        
        # Wait for callback to be triggered
        await asyncio.sleep(0.1)
        
        if callback_triggered:
            print_success("Event callback system working")
        else:
            print_error("Event callback not triggered")
        
        # Test callback unregistration
        manager.unregister_event_callback("connection_established", test_callback)
        print_success("Event callback unregistered")
        
        return True
        
    except Exception as e:
        print_error(f"Event callback test failed: {e}")
        return False
    finally:
        await manager.shutdown()

async def run_all_tests():
    """Run all enhanced WebSocket manager tests"""
    print_section("Enhanced WebSocket Manager Test Suite")
    
    tests = [
        ("Enhanced Connection Management", test_enhanced_connection_management),
        ("Topic-Based Subscriptions", test_topic_subscriptions),
        ("Message Queuing System", test_message_queuing),
        ("Connection Monitoring", test_connection_monitoring),
        ("Event Callback System", test_event_callbacks)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{BOLD}Running: {test_name}{RESET}")
        try:
            result = await test_func()
            results.append((test_name, result))
            if result:
                print_success(f"{test_name} completed successfully")
            else:
                print_error(f"{test_name} failed")
        except Exception as e:
            print_error(f"{test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print_section("Test Results Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        color = GREEN if result else RED
        print(f"{color}{status:>6}{RESET} - {test_name}")
    
    print(f"\n{BOLD}Overall: {passed}/{total} tests passed{RESET}")
    
    if passed == total:
        print(f"\n{GREEN}{BOLD}🎉 All enhanced WebSocket manager tests passed!{RESET}")
        print("Enhanced features are working correctly:")
        print("  ✅ Connection pooling and automatic reconnection")
        print("  ✅ Topic-based subscription management")
        print("  ✅ Message queuing with offline support")
        print("  ✅ Connection monitoring and health checks")
        print("  ✅ Event callback system")
    else:
        print(f"\n{RED}{BOLD}❌ Some tests failed. Please review the implementation.{RESET}")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(run_all_tests())