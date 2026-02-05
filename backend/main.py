from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sped_processor import processar_sped, consolidar_c175
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# PIS / COFINS
# ===============================

@app.post("/corrigir")
async def corrigir_sped(file: UploadFile = File(...)):

    uid = str(uuid.uuid4())
    entrada = f"/tmp/{uid}.txt"
    saida = f"/tmp/{uid}_corrigido.txt"

    with open(entrada, "wb") as f:
        f.write(await file.read())

    processar_sped(entrada, saida)

    return FileResponse(
        saida,
        filename="SPED_PISCOFINS.txt",
        media_type="text/plain"
    )

# ===============================
# CONSOLIDAR C175
# ===============================

@app.post("/consolidar-c175")
async def consolidar(file: UploadFile = File(...)):

    uid = str(uuid.uuid4())
    entrada = f"/tmp/{uid}.txt"
    saida = f"/tmp/{uid}_c175.txt"

    with open(entrada, "wb") as f:
        f.write(await file.read())

    consolidar_c175(entrada, saida)

    return FileResponse(
        saida,
        filename="SPED_C175.txt",
        media_type="text/plain"
    )
