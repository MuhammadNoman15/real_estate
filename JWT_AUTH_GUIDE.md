# JWT Authentication Guide

## Overview
Your application now has complete JWT (JSON Web Token) authentication with login, logout, and protected endpoints.

## Setup

### 1. Update your `.env` file
Add these JWT configuration variables:
```env
JWT_SECRET_KEY=your-secret-key-here-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Important:** Generate a secure secret key using:
```bash
openssl rand -hex 32
```

## API Endpoints

### 1. Register a New User
**POST** `/register`

**Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "confirm_password": "SecurePass123"
}
```

**Response:**
```json
{
  "message": "User registered successfully"
}
```

---

### 2. Login
**POST** `/login`

**Body:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  }
}
```

**Save the `access_token`** - you'll need it for authenticated requests!

---

### 3. Logout
**POST** `/logout`

**Headers:**
```
Authorization: Bearer <your_access_token>
```

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

The token is now blacklisted and cannot be used again.

---

### 4. Get Current User Info (Protected Endpoint)
**GET** `/me`

**Headers:**
```
Authorization: Bearer <your_access_token>
```

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2024-01-15T10:30:00"
}
```

---

## How to Protect Your Endpoints

To make any endpoint require authentication, add the `get_current_user` dependency:

```python
@app.post("/my-protected-endpoint")
async def my_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # current_user is automatically available
    # Only authenticated users can access this
    return {"message": f"Hello {current_user.username}!"}
```

## Testing with Postman/Thunder Client

### 1. Login Flow:
1. **Register** a user via `/register`
2. **Login** via `/login` → Copy the `access_token`
3. For protected endpoints:
   - Add header: `Authorization: Bearer <paste_token_here>`

### 2. Logout Flow:
1. Call `/logout` with the token in the header
2. The token is now blacklisted
3. Future requests with that token will return `401 Unauthorized`

## Testing with cURL

### Register:
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "confirm_password": "password123"
  }'
```

### Login:
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Get Current User (Protected):
```bash
curl -X GET http://localhost:8000/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Logout:
```bash
curl -X POST http://localhost:8000/logout \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## How It Works

### 1. **Login**
- User sends email/password
- Server verifies credentials
- Server creates a JWT token with:
  - User email (`sub`)
  - User ID
  - Expiration time (default: 30 minutes)
- Token is returned to client

### 2. **Authenticated Requests**
- Client includes token in `Authorization: Bearer <token>` header
- Server verifies token signature
- Server checks if token is blacklisted
- Server extracts user info from token
- Request proceeds with user context

### 3. **Logout**
- Client sends token in header
- Server adds token to `token_blacklist` table
- Token can no longer be used
- Token expires naturally after its expiration time

## Database Tables

### `users`
- `id` - Primary key
- `username` - Unique username
- `email` - Unique email
- `hashed_password` - Bcrypt hashed password
- `created_at` - Account creation timestamp

### `token_blacklist`
- `id` - Primary key
- `token` - The blacklisted JWT token
- `blacklisted_at` - When token was blacklisted
- `expires_at` - When token naturally expires

## Security Features

✅ **Password Hashing** - Passwords stored as bcrypt hashes  
✅ **JWT Tokens** - Stateless authentication  
✅ **Token Expiration** - Tokens automatically expire  
✅ **Token Blacklisting** - Logout invalidates tokens  
✅ **Secure Headers** - Bearer token authentication  
✅ **Protected Endpoints** - Easy to add authentication to any endpoint  

## Example: Protecting the Chat Endpoint

To make the `/chat` endpoint require authentication:

```python
@app.post("/chat")
async def chat_with_ai(
    query: dict,
    current_user: User = Depends(get_current_user)  # Add this line
):
    user_query = query.get("query")
    
    if not user_query:
        raise HTTPException(status_code=400, detail="No query provided")
    
    # Now you have access to current_user
    print(f"User {current_user.username} asked: {user_query}")
    
    api_response = await determine_api_action(user_query)
    return api_response
```

## Next Steps

1. ✅ Update your `.env` file with JWT configuration
2. ✅ Test the authentication flow
3. 🔄 Decide which endpoints need authentication
4. 🔄 Add `current_user: User = Depends(get_current_user)` to protected endpoints
5. 🔄 Consider adding refresh tokens for longer sessions (optional)

## Troubleshooting

### "Invalid authentication credentials"
- Token may be expired (30 min default)
- Token may be blacklisted (logged out)
- Token may be malformed
- JWT_SECRET_KEY may have changed

### "User not found"
- Token is valid but user was deleted from database

### Migration Issues
If you had existing users before adding JWT:
```bash
# Run migrations
alembic revision --autogenerate -m "add_jwt_support"
alembic upgrade head
```

---

**Your authentication system is now complete!** 🎉

