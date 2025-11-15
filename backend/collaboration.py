"""
Real-time collaboration service using Socket.IO for MemeCraft Pro
Handles:
- Real-time canvas updates
- In-editor commenting
- User presence tracking
- Collaborative editing
"""
import socketio
import logging
from typing import Dict, Set
from datetime import datetime

logger = logging.getLogger(__name__)

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=True
)

# Track active sessions and users
active_sessions: Dict[str, Set[str]] = {}  # meme_id -> set of user_ids
user_sessions: Dict[str, str] = {}  # sid -> user_id

@sio.event
async def connect(sid, environ, auth):
    """Handle client connection"""
    logger.info(f"Client connected: {sid}")
    return True

@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {sid}")
    
    # Remove user from active sessions
    if sid in user_sessions:
        user_id = user_sessions[sid]
        
        # Remove from all meme sessions
        for meme_id, users in active_sessions.items():
            if user_id in users:
                users.discard(user_id)
                await sio.emit(
                    'user-left',
                    {
                        'user_id': user_id,
                        'meme_id': meme_id,
                        'active_users': len(users)
                    },
                    room=meme_id
                )
        
        del user_sessions[sid]

@sio.event
async def join_meme(sid, data):
    """
    Join a meme editing session
    data: {
        'meme_id': str,
        'user_id': str,
        'username': str
    }
    """
    try:
        meme_id = data.get('meme_id')
        user_id = data.get('user_id')
        username = data.get('username', 'Anonymous')
        
        if not meme_id or not user_id:
            await sio.emit('error', {'message': 'Missing meme_id or user_id'}, to=sid)
            return
        
        # Add user to session tracking
        user_sessions[sid] = user_id
        
        # Add to meme session
        if meme_id not in active_sessions:
            active_sessions[meme_id] = set()
        active_sessions[meme_id].add(user_id)
        
        # Join Socket.IO room
        await sio.enter_room(sid, meme_id)
        
        # Notify others in the room
        await sio.emit(
            'user-joined',
            {
                'user_id': user_id,
                'username': username,
                'meme_id': meme_id,
                'active_users': len(active_sessions[meme_id])
            },
            room=meme_id,
            skip_sid=sid
        )
        
        # Send confirmation to joining user
        await sio.emit(
            'joined',
            {
                'meme_id': meme_id,
                'active_users': len(active_sessions[meme_id]),
                'user_ids': list(active_sessions[meme_id])
            },
            to=sid
        )
        
        logger.info(f"User {user_id} joined meme {meme_id}")
        
    except Exception as e:
        logger.error(f"Error in join_meme: {str(e)}")
        await sio.emit('error', {'message': str(e)}, to=sid)

@sio.event
async def leave_meme(sid, data):
    """
    Leave a meme editing session
    data: {
        'meme_id': str
    }
    """
    try:
        meme_id = data.get('meme_id')
        
        if not meme_id or sid not in user_sessions:
            return
        
        user_id = user_sessions[sid]
        
        # Remove from meme session
        if meme_id in active_sessions:
            active_sessions[meme_id].discard(user_id)
            
            # Leave Socket.IO room
            await sio.leave_room(sid, meme_id)
            
            # Notify others
            await sio.emit(
                'user-left',
                {
                    'user_id': user_id,
                    'meme_id': meme_id,
                    'active_users': len(active_sessions[meme_id])
                },
                room=meme_id
            )
        
        logger.info(f"User {user_id} left meme {meme_id}")
        
    except Exception as e:
        logger.error(f"Error in leave_meme: {str(e)}")

@sio.event
async def canvas_update(sid, data):
    """
    Broadcast canvas updates to all users in the meme session
    data: {
        'meme_id': str,
        'canvas_data': dict,  # Fabric.js canvas JSON
        'user_id': str
    }
    """
    try:
        meme_id = data.get('meme_id')
        canvas_data = data.get('canvas_data')
        user_id = data.get('user_id')
        
        if not meme_id or not canvas_data:
            await sio.emit('error', {'message': 'Missing meme_id or canvas_data'}, to=sid)
            return
        
        # Broadcast to all users in the room except sender
        await sio.emit(
            'canvas-updated',
            {
                'meme_id': meme_id,
                'canvas_data': canvas_data,
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat()
            },
            room=meme_id,
            skip_sid=sid
        )
        
    except Exception as e:
        logger.error(f"Error in canvas_update: {str(e)}")
        await sio.emit('error', {'message': str(e)}, to=sid)

@sio.event
async def add_comment(sid, data):
    """
    Add a comment to the meme
    data: {
        'meme_id': str,
        'user_id': str,
        'username': str,
        'text': str,
        'position': {'x': int, 'y': int}  # Position on canvas
    }
    """
    try:
        meme_id = data.get('meme_id')
        user_id = data.get('user_id')
        username = data.get('username')
        text = data.get('text')
        position = data.get('position', {'x': 0, 'y': 0})
        
        if not all([meme_id, user_id, text]):
            await sio.emit('error', {'message': 'Missing required fields'}, to=sid)
            return
        
        comment_data = {
            'id': f"{user_id}_{datetime.utcnow().timestamp()}",
            'meme_id': meme_id,
            'user_id': user_id,
            'username': username,
            'text': text,
            'position': position,
            'timestamp': datetime.utcnow().isoformat(),
            'resolved': False
        }
        
        # Broadcast new comment to all users in the room
        await sio.emit(
            'new-comment',
            comment_data,
            room=meme_id
        )
        
        logger.info(f"Comment added by {user_id} on meme {meme_id}")
        
    except Exception as e:
        logger.error(f"Error in add_comment: {str(e)}")
        await sio.emit('error', {'message': str(e)}, to=sid)

@sio.event
async def resolve_comment(sid, data):
    """
    Resolve a comment
    data: {
        'meme_id': str,
        'comment_id': str,
        'user_id': str
    }
    """
    try:
        meme_id = data.get('meme_id')
        comment_id = data.get('comment_id')
        user_id = data.get('user_id')
        
        if not all([meme_id, comment_id]):
            await sio.emit('error', {'message': 'Missing required fields'}, to=sid)
            return
        
        # Broadcast comment resolution to all users
        await sio.emit(
            'comment-resolved',
            {
                'meme_id': meme_id,
                'comment_id': comment_id,
                'resolved_by': user_id,
                'timestamp': datetime.utcnow().isoformat()
            },
            room=meme_id
        )
        
    except Exception as e:
        logger.error(f"Error in resolve_comment: {str(e)}")
        await sio.emit('error', {'message': str(e)}, to=sid)

@sio.event
async def cursor_move(sid, data):
    """
    Broadcast cursor position to show where other users are working
    data: {
        'meme_id': str,
        'user_id': str,
        'username': str,
        'position': {'x': int, 'y': int}
    }
    """
    try:
        meme_id = data.get('meme_id')
        
        if not meme_id:
            return
        
        # Broadcast cursor position to others (throttled on client side)
        await sio.emit(
            'cursor-moved',
            {
                'user_id': data.get('user_id'),
                'username': data.get('username'),
                'position': data.get('position')
            },
            room=meme_id,
            skip_sid=sid
        )
        
    except Exception as e:
        logger.error(f"Error in cursor_move: {str(e)}")

# Function to get active users for a meme
def get_active_users(meme_id: str) -> int:
    """Get count of active users for a meme"""
    return len(active_sessions.get(meme_id, set()))

# Create ASGI app
app = socketio.ASGIApp(sio)
