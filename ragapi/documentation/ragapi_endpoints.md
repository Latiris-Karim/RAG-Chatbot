# RAG API Endpoints Documentation

## Chat Endpoints (`/chat`)

### `POST /chat/create`
Creates a new chatroom for the authenticated user.
- **Authentication:** Required (JWT token)
- **Request Body:** None
- **Response:** Chatroom creation confirmation
- **Notes:** Each user can create multiple chatrooms

### `POST /chat/send`
Sends a message to a specific chatroom and gets AI response.
- **Authentication:** Required (JWT token)
- **Request Body:**
  ```json
  {
    "txt": "string",
    "chatroom_id": "integer"
  }
  ```
- **Response:** AI-generated response
- **Rate Limiting:** 
  - Free users: Limited queries per time period
  - Premium users: Unlimited
- **Access Control:** User must have access to the specified chatroom
- **Notes:** 
  - Saves both user message and AI response to chat history
  - Uses RAG pipeline for response generation
  - Includes response time logging

### `GET /chat/get_chatrooms`
Retrieves all chatrooms belonging to the authenticated user.
- **Authentication:** Required (JWT token)
- **Request Body:** None
- **Response:** List of user's chatrooms
- **Notes:** Only returns chatrooms owned by the current user

### `GET /chat/get_msgs`
Retrieves all messages from a specific chatroom.
- **Authentication:** Required (JWT token)
- **Query Parameters:** `chatroom_id` (required)
- **Response:** List of messages in the chatroom
- **Access Control:** User must have access to the specified chatroom
- **Error Response:** 403 if access denied or chatroom doesn't exist

---

## Settings Endpoints (`/settings`)

### `GET /settings/display`
Displays current user information/settings.
- **Authentication:** Required (JWT token)
- **Request Body:** None
- **Response:** User information object

### `POST /settings/change_pw`
Changes password for logged-in user.
- **Authentication:** Required (JWT token)
- **Request Body:**
  ```json
  {
    "pw": "string"
  }
  ```
- **Response:** Password change confirmation

### `POST /settings/request_pw_change`
Initiates password reset process (Step 1 - sends reset email).
- **Authentication:** Not required
- **Request Body:**
  ```json
  {
    "email": "string"
  }
  ```
- **Response:** Password reset request confirmation
- **Notes:** Sends password reset email with token

### `POST /settings/change_forgotten_pw`
Completes password reset using token from Step 1 (Step 2).
- **Authentication:** Not required
- **Request Body:**
  ```json
  {
    "token": "string",
    "pw": "string"
  }
  ```
- **Response:** Password reset confirmation
- **Notes:** Validates reset token before changing password

### `POST /settings/change_email_request`
Initiates email change process (Step 1).
- **Authentication:** Required (JWT token)
- **Request Body:**
  ```json
  {
    "newEmail": "string"
  }
  ```
- **Response:** Email change request confirmation
- **Notes:** Sends verification code to new email

### `POST /settings/change_email`
Completes email change using verification code (Step 2).
- **Authentication:** Required (JWT token)
- **Request Body:**
  ```json
  {
    "code": "string"
  }
  ```
- **Response:** Email change confirmation

### `POST /settings/delete_account`
Permanently deletes user account.
- **Authentication:** Required (JWT token)
- **Request Body:** None
- **Response:** Account deletion confirmation
- **⚠️ Warning:** This action is irreversible

---

## User Authentication Endpoints (`/user`)

### `POST /user/register`
Registers a new user account.
- **Authentication:** Not required
- **Request Body:**
  ```json
  {
    "email": "string",
    "pw": "string"
  }
  ```
- **Response:** Registration confirmation
- **Notes:** Triggers email verification process

### `POST /user/login`
Authenticates user and returns tokens.
- **Authentication:** Not required
- **Request Body:**
  ```json
  {
    "email": "string",
    "pw": "string"
  }
  ```
- **Response:** JWT access token and refresh token
- **Notes:** Tokens should be stored securely on client side

### `POST /user/verify_code`
Verifies email with confirmation code.
- **Authentication:** Not required
- **Request Body:**
  ```json
  {
    "code": "string",
    "email": "string"
  }
  ```
- **Response:** Email verification confirmation

### `POST /user/logout`
Invalidates user session/token.
- **Authentication:** Required (Bearer token in header)
- **Request Body:** None
- **Response:** Logout confirmation
- **Notes:** Token will be blacklisted

### `POST /user/refresh`
Refreshes access token using refresh token.
- **Authentication:** Not required (uses refresh token)
- **Request Body:**
  ```json
  {
    "refresh_token": "string"
  }
  ```
- **Response:** New access token and refresh token pair
- **Notes:** Update both tokens in client storage

---

## Subscription Endpoints (`/subscribtion`)

### `POST /subscribtion/create-customer`
Creates a Stripe customer for the user.
- **Authentication:** Required (JWT token)
- **Request Body:**
  ```json
  {
    "email": "string"
  }
  ```
- **Response:** Stripe customer object
- **Notes:** One customer per user; returns message if customer already exists

### `POST /subscribtion/create-subscription`
Creates a new subscription for the customer.
- **Authentication:** Required (JWT token)
- **Request Body:**
  ```json
  {
    "priceId": "string"
  }
  ```
- **Response:** 
  ```json
  {
    "subscriptionId": "string",
    "clientSecret": "string"
  }
  ```
- **Prerequisites:** Customer must exist (call create-customer first)
- **Notes:** Returns clientSecret for frontend payment completion

### `POST /subscribtion/cancel-subscription`
Cancels an active subscription.
- **Authentication:** Required (JWT token)
- **Request Body:**
  ```json
  {
    "subscriptionId": "string"
  }
  ```
- **Response:** Cancellation confirmation

### `GET /subscribtion/subscriptions`
Lists all subscriptions for the user.
- **Authentication:** Required (JWT token)
- **Request Body:** None
- **Response:** List of user's subscriptions with billing info
- **Error Response:** 404 if customer not found

---

## Webhook Endpoints

### `POST /webhook`
Handles Stripe webhook events for subscription management.
- **Authentication:** Stripe webhook signature verification
- **Request Body:** Stripe webhook payload
- **Supported Events:**
  - `invoice.payment_succeeded`: Processes successful payments
  - `invoice.payment_failed`: Handles failed payments
  - `invoice.finalized`: Logs invoice finalization
  - `customer.subscription.deleted`: Processes subscription cancellations
- **Notes:** 
  - Sends email notifications for subscription events
  - Prevents duplicate subscriptions
  - Updates internal subscription database

---

## Authentication Notes

- **JWT Tokens:** Most endpoints require JWT token in Authorization header
- **Rate Limiting:** Free users have usage limits on chat endpoints
- **Access Control:** Users can only access their own resources
- **Token Management:** Use refresh endpoint to maintain session

## Error Handling

- **400:** Bad Request (invalid data)
- **401:** Unauthorized (invalid/missing token)
- **403:** Forbidden (access denied)
- **404:** Not Found (resource doesn't exist)
- **500:** Internal Server Error

## Security Features

- Password hashing
- JWT token authentication
- Webhook signature verification
- Email verification
- Rate limiting for free users
- Access control validation
