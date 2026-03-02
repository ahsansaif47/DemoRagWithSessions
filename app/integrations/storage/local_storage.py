
async def store_file_chunks(file, file_path: str):
    with open(file_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            buffer.write(chunk)

    await file.close()


# TODO: Use this function to save images in document service layer
def save_image(image_path: str, image_bytes: bytes):
    with open(image_path, "wb") as f:
        f.write(image_bytes)
