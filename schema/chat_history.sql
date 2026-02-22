CREATE TABLE chat_messages (
    id UUID PRIMARY KEY,

    user_id UUID NOT NULL,
    user_query TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);