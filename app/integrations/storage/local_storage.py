from fastapi import UploadFile


async def store_file_chunks(upload_file: UploadFile, file_path: str):
    with open(file_path, "wb") as buffer:
        while chunk := await upload_file.read(1024*1024):
            buffer.write(chunk)

    await upload_file.close()







