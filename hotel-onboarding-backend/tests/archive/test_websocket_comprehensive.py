#!/usr/bin/env python3
"""
Comprehensive WebSocket Tests for Task 3: Real-Time Dashboard Infrastructure
Tests all WebSocket functionality including authentication, connection management,
room subscriptions, broadcasting, and error handling.
"""

import asyncio
import json
import pytest
from typing import Dict, Any, List
from datetime import datetime, timedelta
import jwt
import websockets
from unittest.mock import Mock, patch, AsyncMock
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.websocket_manager import WebSocketManager, ConnectionInfo, BroadcastEvent
from app.models import UserRole
from app.auth import create_token, decode_token

# Test configuration
TEST_WS_URL = "ws://localhost:8000/ws/dashboard"
TEST_JWT_SECRET = "hotel-onboarding-super-secret-key-2025"

class TestWebSocketManager:
    """Test WebSocket Manager functionality"""
    
    @pytest.fixture
    def manager(self):
        """Create WebSocket manager instance"""
        return WebSocketManager()
    
    @pytest.fixture
    def hr_token(self):
        """Create HR user token"""
        return create_token(user_id="hr-123", role="hr")
    
    @pytest.fixture
    def manager_token(self):
        """Create manager user token"""
        return create_token(user_id="mgr-456", role="manager")
    
    @pytest.mark.asyncio
    async def test_connection_management(self, manager):
        """Test WebSocket connection add/remove"""
        # Create mock WebSocket
        mock_ws = AsyncMock()
        mock_ws.send = AsyncMock()
        
        # Test adding connection
        connection_id = await manager.add_connection(
            websocket=mock_ws,
            user_id="user-123",
            role=UserRole.HR,
            property_id=None
        )
        
        assert connection_id is not None
        assert connection_id in manager.connections
        assert manager.connections[connection_id].user_id == "user-123"
        assert manager.connections[connection_id].role == UserRole.HR
        
        # Test removing connection
        await manager.remove_connection(connection_id)
        assert connection_id not in manager.connections
    
    @pytest.mark.asyncio
    async def test_room_subscriptions(self, manager):
        """Test room subscription functionality"""
        mock_ws = AsyncMock()
        
        # Add connection
        connection_id = await manager.add_connection(
            websocket=mock_ws,
            user_id="user-123",
            role=UserRole.MANAGER,
            property_id="prop-456"
        )
        
        # Test automatic room subscription for manager
        assert "property:prop-456" in manager.rooms
        assert connection_id in manager.rooms["property:prop-456"]
        
        # Test manual room subscription
        await manager.subscribe_to_room(connection_id, "custom-room")
        assert "custom-room" in manager.rooms
        assert connection_id in manager.rooms["custom-room"]
        
        # Test unsubscribe
        await manager.unsubscribe_from_room(connection_id, "custom-room")
        assert connection_id not in manager.rooms.get("custom-room", set())
    
    @pytest.mark.asyncio
    async def test_broadcast_to_room(self, manager):
        """Test broadcasting messages to rooms"""
        # Create multiple connections
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()
        mock_ws3 = AsyncMock()
        
        conn1 = await manager.add_connection(mock_ws1, "user-1", UserRole.HR, None)
        conn2 = await manager.add_connection(mock_ws2, "user-2", UserRole.MANAGER, "prop-1")
        conn3 = await manager.add_connection(mock_ws3, "user-3", UserRole.MANAGER, "prop-1")
        
        # Subscribe HR to global room
        await manager.subscribe_to_room(conn1, "global")
        
        # Broadcast to property room
        event = BroadcastEvent(
            event_type="application_submitted",
            room="property:prop-1",
            data={"application_id": "app-123"},
            sender_id="system"
        )
        
        await manager.broadcast_to_room(event)
        
        # Verify only property managers received the message
        mock_ws1.send.assert_not_called()
        assert mock_ws2.send.called
        assert mock_ws3.send.called
    
    @pytest.mark.asyncio
    async def test_broadcast_to_user(self, manager):
        """Test direct user messaging"""
        mock_ws = AsyncMock()
        
        conn_id = await manager.add_connection(mock_ws, "user-123", UserRole.HR, None)
        
        # Send direct message
        await manager.broadcast_to_user(
            user_id="user-123",
            event_type="notification",
            data={"message": "Test notification"}
        )
        
        # Verify message was sent
        mock_ws.send.assert_called_once()
        sent_data = json.loads(mock_ws.send.call_args[0][0])
        assert sent_data["type"] == "notification"
        assert sent_data["data"]["message"] == "Test notification"
    
    @pytest.mark.asyncio
    async def test_connection_cleanup_on_disconnect(self, manager):
        """Test proper cleanup when connection drops"""
        mock_ws = AsyncMock()
        
        # Add connection and subscribe to rooms
        conn_id = await manager.add_connection(mock_ws, "user-123", UserRole.MANAGER, "prop-1")
        await manager.subscribe_to_room(conn_id, "custom-room")
        
        # Verify subscriptions
        assert conn_id in manager.rooms["property:prop-1"]
        assert conn_id in manager.rooms["custom-room"]
        
        # Remove connection
        await manager.remove_connection(conn_id)
        
        # Verify cleanup
        assert conn_id not in manager.connections
        assert conn_id not in manager.rooms.get("property:prop-1", set())
        assert conn_id not in manager.rooms.get("custom-room", set())


class TestWebSocketAuthentication:
    """Test WebSocket authentication and authorization"""
    
    @pytest.mark.asyncio
    async def test_valid_token_authentication(self):
        """Test successful authentication with valid token"""
        # Create valid token
        token = create_token(user_id="user-123", role="hr")
        
        # Decode and verify
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user-123"
        assert payload["role"] == "hr"
    
    @pytest.mark.asyncio
    async def test_expired_token_rejection(self):
        """Test rejection of expired tokens"""
        # Create expired token
        token = create_token(
            user_id="user-123", 
            role="hr",
            expires_delta=timedelta(seconds=-1)
        )
        
        # Verify rejection
        payload = decode_token(token)
        assert payload is None
    
    @pytest.mark.asyncio
    async def test_invalid_token_rejection(self):
        """Test rejection of invalid tokens"""
        # Create invalid token
        invalid_token = "invalid.token.here"
        
        # Verify rejection
        payload = decode_token(invalid_token)
        assert payload is None
    
    @pytest.mark.asyncio
    async def test_role_based_room_access(self):
        """Test role-based room subscription restrictions"""
        manager = WebSocketManager()
        
        # HR user should access global room
        hr_ws = AsyncMock()
        hr_conn = await manager.add_connection(hr_ws, "hr-user", UserRole.HR, None)
        
        can_subscribe = await manager.can_subscribe_to_room(hr_conn, "global")
        assert can_subscribe is True
        
        # Manager should not access other property rooms
        mgr_ws = AsyncMock()
        mgr_conn = await manager.add_connection(mgr_ws, "mgr-user", UserRole.MANAGER, "prop-1")
        
        can_subscribe = await manager.can_subscribe_to_room(mgr_conn, "property:prop-2")
        assert can_subscribe is False
        
        # Manager should access own property room
        can_subscribe = await manager.can_subscribe_to_room(mgr_conn, "property:prop-1")
        assert can_subscribe is True


class TestWebSocketIntegration:
    """Integration tests for WebSocket functionality"""
    
    @pytest.mark.asyncio
    async def test_full_connection_lifecycle(self):
        """Test complete WebSocket connection lifecycle"""
        manager = WebSocketManager()
        mock_ws = AsyncMock()
        
        # 1. Connect
        conn_id = await manager.add_connection(
            websocket=mock_ws,
            user_id="user-123",
            role=UserRole.HR,
            property_id=None
        )
        assert conn_id in manager.connections
        
        # 2. Subscribe to rooms
        await manager.subscribe_to_room(conn_id, "global")
        await manager.subscribe_to_room(conn_id, "notifications")
        
        # 3. Receive messages
        test_event = BroadcastEvent(
            event_type="system_alert",
            room="global",
            data={"alert": "System maintenance"},
            sender_id="system"
        )
        await manager.broadcast_to_room(test_event)
        
        # 4. Send heartbeat
        await manager.send_heartbeat(conn_id)
        
        # 5. Handle errors gracefully
        mock_ws.send.side_effect = Exception("Connection lost")
        await manager.broadcast_to_user("user-123", "test", {})
        
        # 6. Disconnect
        await manager.remove_connection(conn_id)
        assert conn_id not in manager.connections
    
    @pytest.mark.asyncio
    async def test_concurrent_connections(self):
        """Test handling multiple concurrent connections"""
        manager = WebSocketManager()
        connections = []
        
        # Create 100 concurrent connections
        for i in range(100):
            mock_ws = AsyncMock()
            conn_id = await manager.add_connection(
                websocket=mock_ws,
                user_id=f"user-{i}",
                role=UserRole.MANAGER if i % 2 == 0 else UserRole.HR,
                property_id=f"prop-{i % 5}" if i % 2 == 0 else None
            )
            connections.append(conn_id)
        
        # Verify all connections registered
        assert len(manager.connections) == 100
        
        # Broadcast to all
        event = BroadcastEvent(
            event_type="system_broadcast",
            room="global",
            data={"message": "Test broadcast"},
            sender_id="system"
        )
        
        # Subscribe all to global
        for conn_id in connections:
            await manager.subscribe_to_room(conn_id, "global")
        
        await manager.broadcast_to_room(event)
        
        # Clean up all connections
        for conn_id in connections:
            await manager.remove_connection(conn_id)
        
        assert len(manager.connections) == 0
    
    @pytest.mark.asyncio
    async def test_reconnection_handling(self):
        """Test automatic reconnection handling"""
        manager = WebSocketManager()
        
        # Initial connection
        mock_ws1 = AsyncMock()
        conn_id1 = await manager.add_connection(
            websocket=mock_ws1,
            user_id="user-123",
            role=UserRole.HR,
            property_id=None
        )
        
        # Simulate disconnect
        await manager.remove_connection(conn_id1)
        
        # Reconnect with same user
        mock_ws2 = AsyncMock()
        conn_id2 = await manager.add_connection(
            websocket=mock_ws2,
            user_id="user-123",
            role=UserRole.HR,
            property_id=None
        )
        
        # Verify new connection established
        assert conn_id1 != conn_id2
        assert conn_id2 in manager.connections
        assert manager.connections[conn_id2].user_id == "user-123"


class TestWebSocketErrorHandling:
    """Test error handling and fallback mechanisms"""
    
    @pytest.mark.asyncio
    async def test_connection_error_handling(self):
        """Test handling of connection errors"""
        manager = WebSocketManager()
        mock_ws = AsyncMock()
        
        # Simulate send failure
        mock_ws.send.side_effect = websockets.exceptions.ConnectionClosed(None, None)
        
        conn_id = await manager.add_connection(mock_ws, "user-123", UserRole.HR, None)
        
        # Try to send message (should handle error gracefully)
        await manager.send_to_connection(
            conn_id,
            {"type": "test", "data": {}}
        )
        
        # Connection should be removed after error
        assert conn_id not in manager.connections
    
    @pytest.mark.asyncio
    async def test_invalid_room_subscription(self):
        """Test handling of invalid room subscriptions"""
        manager = WebSocketManager()
        mock_ws = AsyncMock()
        
        conn_id = await manager.add_connection(
            websocket=mock_ws,
            user_id="mgr-123",
            role=UserRole.MANAGER,
            property_id="prop-1"
        )
        
        # Try to subscribe to unauthorized room
        result = await manager.subscribe_to_room(conn_id, "property:prop-999")
        
        # Should be rejected
        assert result is False
        assert conn_id not in manager.rooms.get("property:prop-999", set())
    
    @pytest.mark.asyncio
    async def test_broadcast_error_recovery(self):
        """Test recovery from broadcast errors"""
        manager = WebSocketManager()
        
        # Create connections with one failing
        good_ws = AsyncMock()
        bad_ws = AsyncMock()
        bad_ws.send.side_effect = Exception("Connection error")
        
        good_conn = await manager.add_connection(good_ws, "user-1", UserRole.HR, None)
        bad_conn = await manager.add_connection(bad_ws, "user-2", UserRole.HR, None)
        
        # Subscribe both to global
        await manager.subscribe_to_room(good_conn, "global")
        await manager.subscribe_to_room(bad_conn, "global")
        
        # Broadcast (should not fail despite one bad connection)
        event = BroadcastEvent(
            event_type="test",
            room="global",
            data={"test": "data"},
            sender_id="system"
        )
        
        await manager.broadcast_to_room(event)
        
        # Good connection should receive message
        good_ws.send.assert_called()
        # Bad connection should be removed
        assert bad_conn not in manager.connections


class TestWebSocketStats:
    """Test WebSocket statistics and monitoring"""
    
    @pytest.mark.asyncio
    async def test_connection_statistics(self):
        """Test gathering connection statistics"""
        manager = WebSocketManager()
        
        # Create various connections
        for i in range(5):
            mock_ws = AsyncMock()
            await manager.add_connection(
                websocket=mock_ws,
                user_id=f"hr-{i}",
                role=UserRole.HR,
                property_id=None
            )
        
        for i in range(10):
            mock_ws = AsyncMock()
            await manager.add_connection(
                websocket=mock_ws,
                user_id=f"mgr-{i}",
                role=UserRole.MANAGER,
                property_id=f"prop-{i % 3}"
            )
        
        stats = await manager.get_connection_stats()
        
        assert stats["total_connections"] == 15
        assert stats["connections_by_role"]["hr"] == 5
        assert stats["connections_by_role"]["manager"] == 10
        assert len(stats["rooms"]) > 0
    
    @pytest.mark.asyncio
    async def test_room_statistics(self):
        """Test room subscription statistics"""
        manager = WebSocketManager()
        
        # Create connections and subscriptions
        for i in range(10):
            mock_ws = AsyncMock()
            conn_id = await manager.add_connection(
                websocket=mock_ws,
                user_id=f"user-{i}",
                role=UserRole.HR,
                property_id=None
            )
            await manager.subscribe_to_room(conn_id, "global")
            if i % 2 == 0:
                await manager.subscribe_to_room(conn_id, "notifications")
        
        stats = await manager.get_room_stats()
        
        assert stats["global"]["subscriber_count"] == 10
        assert stats["notifications"]["subscriber_count"] == 5


# Run tests
if __name__ == "__main__":
    print("Running Comprehensive WebSocket Tests for Task 3")
    print("=" * 60)
    
    # Run with pytest if available
    try:
        import pytest
        pytest.main([__file__, "-v", "--tb=short"])
    except ImportError:
        print("pytest not installed. Install with: pip install pytest pytest-asyncio")
        print("\nRunning basic tests without pytest...")
        
        # Basic test runner without pytest
        async def run_basic_tests():
            manager = WebSocketManager()
            
            # Test 1: Connection management
            print("✓ Testing connection management...")
            mock_ws = AsyncMock()
            conn_id = await manager.add_connection(mock_ws, "test-user", UserRole.HR, None)
            assert conn_id in manager.connections
            await manager.remove_connection(conn_id)
            assert conn_id not in manager.connections
            print("  ✅ Connection management works")
            
            # Test 2: Room subscriptions
            print("✓ Testing room subscriptions...")
            conn_id = await manager.add_connection(mock_ws, "test-user", UserRole.HR, None)
            await manager.subscribe_to_room(conn_id, "test-room")
            assert conn_id in manager.rooms.get("test-room", set())
            print("  ✅ Room subscriptions work")
            
            # Test 3: Broadcasting
            print("✓ Testing broadcasting...")
            event = BroadcastEvent(
                event_type="test",
                room="test-room",
                data={"test": "data"},
                sender_id="system"
            )
            await manager.broadcast_to_room(event)
            print("  ✅ Broadcasting works")
            
            print("\n✅ All basic tests passed!")
        
        asyncio.run(run_basic_tests())