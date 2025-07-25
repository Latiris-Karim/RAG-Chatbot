#  RAG API 

> **Build the future of conversational AI with enterprise-grade security, seamless payments, and powerful chat capabilities.**

A production-ready RESTful API that combines **Retrieval Augmented Generation (RAG)** with modern authentication, subscription management, and real-time chat functionality. Perfect for building AI-powered chat applications, customer support systems, or knowledge bases.


### 🔐 **Enterprise Security First**
- **JWT Token Pair Authentication** - Secure access & refresh token system
- **Multi-provider Auth** - Local accounts + OAuth integration ready
- **Email verification** with secure code generation
- **Password reset** flows with expiring tokens

### 💳 **Revenue-Ready**
- **Stripe Integration** - Complete subscription lifecycle management
- **Flexible billing** with automatic renewals and cancellation handling
- **Usage tracking** and subscription status monitoring

### 💬 **Powerful Chat Experience**
- **Multi-room chat** - Organize conversations by topic or user
- **Message persistence** - Never lose important conversations
- **Role-based messaging** - Support for different message types (user, assistant, system)


### 📊 **Production Monitoring**
- **User activity tracking** - Monitor engagement and usage patterns
- **Audit trails** - Complete visibility into user actions
- **Scalable architecture** - PostgreSQL backend with optimized queries

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client App    │◄──►│    RAG API       │◄──►│   PostgreSQL    │
│                 │    │                  │    │                 │
│ • Angular       │    │ • JWT Auth       │    │ • User Data     │    
                  │    │ • Chat Rooms     │    │ • Messages      │
│                 │    │ • Subscriptions  │    │ • Subscriptions │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Stripe API     │
                       │                  │
                       │ • Payments       │
                       │ • Subscriptions  │
                       │ • Webhooks       │
                       └──────────────────┘
```

## 🎯 Perfect For

- **🤖 AI Chat Applications** - Customer support, virtual assistants, educational tools
- **📚 Knowledge Management** - Internal wikis, documentation systems, Q&A platforms  
- **🔬 Research Platforms** - Document analysis and information retrieval systems


## 🔧 Core Features

### Authentication & Security
- **Secure Registration/Login** with email verification
- **JWT refresh token rotation** for enhanced security
- **Password reset** with time-limited tokens
- **Multi-provider authentication** support

### Testing
- Test Coverage Areas:
- Every endpoint properly rejects unauthorized requests

### Chat Management
- **Create unlimited chat rooms** per user
- **Persistent message history** with sender tracking
- **Bulk operations** and efficient querying

### Subscription System
- **Stripe-powered billing** with webhook support
- **Automatic subscription management** (renewals, cancellations)


### User Management
- **Activity tracking** for analytics and monitoring
- **Account management** (email changes, profile updates)


## 📚 Documentation Deep Dive

### 🗄️ Database Schema
Explore our carefully crafted PostgreSQL schema that powers everything:

- **[📋 Complete SQL Schema](./documentation/database_schema.md)** - Tables, relationships, and constraints
- **User Management** - Secure user data with OAuth support
- **Chat Architecture** - Scalable message storage and room organization  
- **Billing Integration** - Stripe subscription tracking and management
- **Security Features** - Token storage and user activity monitoring

### 🛣️ API Endpoints
Comprehensive API documentation covering all endpoints:

- **[📖 API Documentation](./documentation/ragapi_endpoints.md)** - Complete endpoint reference
- **Authentication flows** - Registration, login, token refresh
- **Chat operations** - Room management, messaging, history
- **Subscription handling** - Billing webhooks, status updates
- **User management** - Profile updates, admin operations


### **Developer Experience**
Clear documentation, consistent API patterns, and helpful error messages make integration a breeze. Get up and running in minutes, not hours.

### **Business Ready**
From day one, you have everything needed to monetize your application. Stripe integration, user management, and subscription handling are ready.

### **RAG-Optimized**
While flexible enough for any chat application, the schema and endpoints are specifically designed to support Retrieval Augmented Generation workflows with document context and conversation history.


