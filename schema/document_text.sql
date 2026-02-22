CREATE TABLE document_texts (
    id UUID PRIMARY KEY,

    file_id UUID NOT NULL,
    page_number INT NOT NULL,

    content TEXT NOT NULL,
    embedding VECTOR(768), -- adjust to your model

    created_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,

    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
);