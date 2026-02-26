from fastapi import UploadFile


async def store_file_chunks(upload_file: UploadFile, file_path: str):
    with open(file_path, "wb") as buffer:
        while chunk := await upload_file.read(1024 * 1024):
            buffer.write(chunk)

    await upload_file.close()


# TODO: Use this function to save images in document service layer
def save_image(image_path: str, image_bytes: bytes):
    with open(image_path, "wb") as f:
        f.write(image_bytes)
