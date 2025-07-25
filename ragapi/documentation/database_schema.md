# Database Schema Documentation

```mermaid
    users {
        int id PK
        varchar email UK
        varchar password_hash
        timestamp created_at
        timestamp updated_at
        varchar role
        varchar code
        boolean verified
        varchar customer_id
        varchar reset_token
        timestamp reset_token_expiry
        varchar new_email
        varchar new_email_code
        varchar auth_provider
    }

    chat_rooms {
        int id PK
        int user_id FK
        timestamp created_at
        varchar title
    }

    messages {
        int id PK
        int chat_room_id FK
        int sender_id FK
        text msg
        varchar role
        timestamp created_at
    }

    refresh_tokens {
        varchar token_hash PK
        int user_id FK
        timestamp expires_at
        timestamp created_at
    }

    subscriptions {
        int id PK
        int user_id FK
        subscription_status status
        varchar stripe_subscription_id UK
        timestamp current_period_start
        timestamp current_period_end
        boolean auto_renew
        timestamp created_at
        timestamp updated_at
        timestamp cancelled_at
    }

    user_activity {
        int id PK
        int user_id FK
        timestamp created_at
    }
```

## Table Descriptions

### users
Core user authentication and profile table.
- Primary authentication via email/password or OAuth providers
- Supports email verification and password reset workflows
- Stripe customer integration for billing

### chat_rooms
User-owned chat sessions or conversations.
- Each user can have multiple chat rooms
- Soft deletion supported via CASCADE on user deletion

### messages
Individual messages within chat rooms.
- Supports both user and system/AI messages via `role` field
- `sender_id` can be NULL for system messages
- Cascading deletion when chat room is deleted

### refresh_tokens
JWT refresh token storage for session management.
- Hashed tokens for security
- Automatic cleanup via expiration timestamps

### subscriptions
Stripe subscription management.
- Tracks billing periods and auto-renewal settings
- Supports subscription cancellation tracking

### user_activity
User engagement tracking.
- Simple activity logging for analytics
- Cascading deletion maintains data integrity

## Key Relationships

- **Users → Chat Rooms**: One-to-many (users can have multiple chat sessions)
- **Chat Rooms → Messages**: One-to-many (each chat room contains multiple messages)
- **Users → Messages**: One-to-many (users can send messages, but sender_id can be NULL for system messages)
- **Users → Subscriptions**: One-to-many (users can have subscription history)
- **Users → Refresh Tokens**: One-to-many (multiple active sessions)

## Indexes

- `idx_subscriptions_user_id` - Optimizes subscription queries by user

## Custom Types

- `subscription_status` - Enum type for subscription states (active, cancelled, etc.)

---

## Raw SQL Schema

```sql
CREATE TABLE IF NOT EXISTS public.chat_rooms
(
    id serial NOT NULL,
    user_id integer NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    title character varying(255) COLLATE pg_catalog."default",
    CONSTRAINT chat_rooms_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.messages
(
    id serial NOT NULL,
    chat_room_id integer NOT NULL,
    sender_id integer,
    msg text COLLATE pg_catalog."default" NOT NULL,
    role character varying(10) COLLATE pg_catalog."default" NOT NULL,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT messages_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.refresh_tokens
(
    token_hash character varying(64) COLLATE pg_catalog."default" NOT NULL,
    user_id integer NOT NULL,
    expires_at timestamp without time zone NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    CONSTRAINT refresh_tokens_pkey PRIMARY KEY (token_hash)
);

CREATE TABLE IF NOT EXISTS public.subscriptions
(
    id serial NOT NULL,
    user_id integer NOT NULL,
    status subscription_status NOT NULL DEFAULT 'active'::subscription_status,
    stripe_subscription_id character varying(255) COLLATE pg_catalog."default" NOT NULL,
    current_period_start timestamp without time zone NOT NULL,
    current_period_end timestamp without time zone NOT NULL,
    auto_renew boolean NOT NULL DEFAULT true,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cancelled_at timestamp without time zone,
    CONSTRAINT subscriptions_pkey PRIMARY KEY (id),
    CONSTRAINT subscriptions_stripe_subscription_id_key UNIQUE (stripe_subscription_id)
);

CREATE TABLE IF NOT EXISTS public.user_activity
(
    id serial NOT NULL,
    user_id integer NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    CONSTRAINT user_activity_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.users
(
    id serial NOT NULL,
    email character varying(255) COLLATE pg_catalog."default" NOT NULL,
    password_hash character varying(255) COLLATE pg_catalog."default" NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    role character varying(50) COLLATE pg_catalog."default" NOT NULL DEFAULT 'user'::character varying,
    code character varying(6) COLLATE pg_catalog."default",
    verified boolean DEFAULT false,
    customer_id character varying(255) COLLATE pg_catalog."default",
    reset_token character varying(255) COLLATE pg_catalog."default",
    reset_token_expiry timestamp without time zone,
    new_email character varying(255) COLLATE pg_catalog."default",
    new_email_code character varying(255) COLLATE pg_catalog."default",
    auth_provider character varying(50) COLLATE pg_catalog."default" NOT NULL DEFAULT 'local'::character varying,
    CONSTRAINT users_pkey PRIMARY KEY (id),
    CONSTRAINT users_email_key UNIQUE (email)
);

-- Foreign Key Constraints
ALTER TABLE IF EXISTS public.chat_rooms
    ADD CONSTRAINT chat_rooms_user_id_fkey FOREIGN KEY (user_id)
    REFERENCES public.users (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE CASCADE;

ALTER TABLE IF EXISTS public.messages
    ADD CONSTRAINT fk_messages_chatroom FOREIGN KEY (chat_room_id)
    REFERENCES public.chat_rooms (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE CASCADE;

ALTER TABLE IF EXISTS public.messages
    ADD CONSTRAINT messages_sender_id_fkey FOREIGN KEY (sender_id)
    REFERENCES public.users (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE SET NULL;

ALTER TABLE IF EXISTS public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_user_id_fkey FOREIGN KEY (user_id)
    REFERENCES public.users (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.subscriptions
    ADD CONSTRAINT fk_user_id FOREIGN KEY (user_id)
    REFERENCES public.users (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE CASCADE;

ALTER TABLE IF EXISTS public.user_activity
    ADD CONSTRAINT user_activity_user_id_fkey FOREIGN KEY (user_id)
    REFERENCES public.users (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE CASCADE;

-- Indexes
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id
    ON public.subscriptions(user_id);
```
