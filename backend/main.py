from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sped_processor import (
    processar_sped,
    processar_c175
)
import uuid
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/corrigir")
async def corrigir_sped(file: UploadFile = File(...)):
    uid = str(uuid.uuid4())
    entrada = f"/tmp/{uid}.txt"
    saida = f"/tmp/{uid}_corrigido.txt"

    with open(entrada, "wb") as f:
        f.write(await file.read())

    processar_sped(entrada, saida)

    return FileResponse(saida, filename="SPED_corrigido.txt")


@app.post("/consolidar-c175")
async def consolidar_c175_endpoint(file: UploadFile = File(...)):
    uid = str(uuid.uuid4())
    entrada = f"/tmp/{uid}.txt"
    saida = f"/tmp/{uid}_C175.txt"

    with open(entrada, "wb") as f:
        f.write(await file.read())

    processar_c175(entrada, saida)

    return FileResponse(saida, filename="SPED_C175.txt")
