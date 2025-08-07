#!/usr/bin/env python3
"""
Basic WebSocket functionality test
Tests the WebSocket implementation without external dependencies
"""
import asyncio
import sys
import os
import unittest
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.websocket_manager import (
    WebSocketManager, 
    ConnectionInfo, 
    BroadcastEvent, 
    WebSocketRoom
)
from app.models import UserRole


class MockWebSocket:
    """Mock WebSocket for testing"""
    def __init__(self):
        self.messages = []
        self.closed = False
        self.close_code = None
        self.close_reason = None
    
    async def accept(self):
        pass
    
    async def send_json(self, data):
        self.messages.append(data)
    
    async def send_text(self, text):
        self.messages.append(text)
    
    async def close(self, code=1000, reason=""):
        self.closed = True
        self.close_code = code
        self.close_reason = reason


async def test_websocket_manager_basic():
    """Test basic WebSocket manager functionality"""
    print("Testing WebSocket Manager basic functionality...")
    
    # Create WebSocket manager
    manager = WebSocketManager()
    
    # Test connection
    mock_ws = MockWebSocket()
    connection = ConnectionInfo(
        websocket=mock_ws,
        user_id="test-user-1",
        property_id="test-property-1",
        role=UserRole.HR,
        connected_at=datetime.now()
    )
    
    await manager.connect(connection)
    
    # Check connection was registered
    assert manager.is_connected("test-user-1"), "User should be connected"
    assert manager.get_connection_count() == 1, "Connection count should be 1"
    
    print("✅ Connection test passed")
    
    # Test room subscription
    await manager.subscribe_to_room("test-user-1", "global")
    
    # Check room was created and user added
    assert "global" in manager.rooms, "Global room should exist"
    assert "test-user-1" in manager.rooms["global"].members, "User should be in global room"
    
    print("✅ Room subscription test passed")
    
    # Test event broadcasting
    event = BroadcastEvent(
        type="test_event",
        data={"message": "Test broadcast"}
    )
    
    await manager.broadcast_to_room("global", event)
    
    # Check message was sent
    assert len(mock_ws.messages) >= 2, "Should have received welcome and broadcast messages"
    
    # Find the test event message
    test_message = None
    for msg in mock_ws.messages:
        if isinstance(msg, dict) and msg.get("type") == "test_event":
            test_message = msg
            break
    
    assert test_message is not None, "Should have received test event"
    assert test_message["data"]["message"] == "Test broadcast", "Message content should match"
    
    print("✅ Event broadcasting test passed")
    
    # Test disconnection
    await manager.disconnect("test-user-1")
    
    assert not manager.is_connected("test-user-1"), "User should be disconnected"
    assert manager.get_connection_count() == 0, "Connection count should be 0"
    assert mock_ws.closed, "WebSocket should be closed"
    
    print("✅ Disconnection test passed")
    
    print("🎉 All WebSocket Manager tests passed!")


async def test_websocket_room_management():
    """Test WebSocket room management"""
    print("Testing WebSocket room management...")
    
    manager = WebSocketManager()
    
    # Create test connections
    connections = []
    for i in range(3):
        mock_ws = MockWebSocket()
        connection = ConnectionInfo(
            websocket=mock_ws,
            user_id=f"user-{i}",
            property_id="test-property",
            role=UserRole.MANAGER if i < 2 else UserRole.HR,
            connected_at=datetime.now()
        )
        connections.append((connection, mock_ws))
        await manager.connect(connection)
    
    # Subscribe users to rooms
    await manager.subscribe_to_room("user-0", "property-test-property")
    await manager.subscribe_to_room("user-1", "property-test-property")
    await manager.subscribe_to_room("user-2", "global")  # HR user
    
    # Test room membership
    assert len(manager.rooms["property-test-property"].members) == 2, "Property room should have 2 members"
    assert len(manager.rooms["global"].members) == 1, "Global room should have 1 member"
    
    print("✅ Room membership test passed")
    
    # Test broadcasting to property room
    event = BroadcastEvent(
        type="property_event",
        data={"property_id": "test-property", "message": "Property update"}
    )
    
    await manager.broadcast_to_room("property-test-property", event)
    
    # Check only property room members received the message
    property_users_received = 0
    for i in range(2):  # First two users are in property room
        _, mock_ws = connections[i]
        for msg in mock_ws.messages:
            if isinstance(msg, dict) and msg.get("type") == "property_event":
                property_users_received += 1
                break
    
    assert property_users_received == 2, "Both property room members should receive the message"
    
    # Check HR user didn't receive property-specific message
    _, hr_ws = connections[2]
    hr_received_property_msg = any(
        isinstance(msg, dict) and msg.get("type") == "property_event" 
        for msg in hr_ws.messages
    )
    assert not hr_received_property_msg, "HR user should not receive property-specific message"
    
    print("✅ Room broadcasting test passed")
    
    # Cleanup
    for connection, _ in connections:
        await manager.disconnect(connection.user_id)
    
    print("🎉 All room management tests passed!")


async def test_authentication_simulation():
    """Test authentication simulation (without actual JWT)"""
    print("Testing WebSocket authentication simulation...")
    
    manager = WebSocketManager()
    mock_ws = MockWebSocket()
    
    # Simulate authentication data
    auth_data = {
        "user_id": "test-user",
        "role": UserRole.HR,
        "property_id": "test-property"
    }
    
    # Create connection with auth data
    connection = ConnectionInfo(
        websocket=mock_ws,
        user_id=auth_data["user_id"],
        property_id=auth_data["property_id"],
        role=auth_data["role"],
        connected_at=datetime.now()
    )
    
    await manager.connect(connection)
    
    # Test role-based room access
    # HR should be able to access global room
    try:
        await manager.subscribe_to_room("test-user", "global")
        print("✅ HR user can access global room")
    except PermissionError:
        assert False, "HR user should be able to access global room"
    
    # Cleanup
    await manager.disconnect("test-user")
    
    print("🎉 Authentication simulation test passed!")


async def main():
    """Run all tests"""
    print("🚀 Starting WebSocket functionality tests...")
    print("=" * 50)
    
    try:
        await test_websocket_manager_basic()
        print()
        await test_websocket_room_management()
        print()
        await test_authentication_simulation()
        
        print("=" * 50)
        print("🎉 ALL WEBSOCKET TESTS PASSED! 🎉")
        print("The WebSocket infrastructure is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    # Run tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)