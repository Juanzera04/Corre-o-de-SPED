from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from sped_processor import processar_sped
import uuid
import os

app = FastAPI()

@app.post("/corrigir")
async def corrigir_sped(file: UploadFile = File(...)):
    arquivo_id = str(uuid.uuid4())
    caminho_original = f"/tmp/{arquivo_id}.txt"
    caminho_corrigido = f"/tmp/{arquivo_id}_corrigido.txt"

    with open(caminho_original, "wb") as f:
        f.write(file.file.read())

    processar_sped(caminho_original, caminho_corrigido)

    return FileResponse(
        caminho_corrigido,
        filename="SPED_corrigido.txt",
        media_type="text/plain"
    )
