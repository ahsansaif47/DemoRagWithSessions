CREATE TABLE files (
    id UUID PRIMARY KEY,

    user_id UUID NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size BIGINT,

    created_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT fk_user
        FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);