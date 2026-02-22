CREATE TABLE document_images (
    id UUID PRIMARY KEY,

    file_id UUID NOT NULL,
    page_number INT NOT NULL,

    image_path TEXT NOT NULL,
    embedding VECTOR(768),

    created_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,

    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
);