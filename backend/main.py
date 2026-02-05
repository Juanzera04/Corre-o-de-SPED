from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sped_processor import (
    processar_sped,
    processar_c175
)
import uuid
import os
import tempfile

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return JSONResponse(
        content={
            "status": "online", 
            "message": "SPED Processor API",
            "endpoints": {
                "corrigir": "/corrigir",
                "consolidar-c175": "/consolidar-c175"
            }
        }
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/corrigir")
async def corrigir_sped(file: UploadFile = File(...)):
    try:
        uid = str(uuid.uuid4())
        entrada = f"/tmp/{uid}.txt"
        saida = f"/tmp/{uid}_corrigido.txt"

        # Lê o conteúdo do arquivo
        content = await file.read()
        
        # Salva no arquivo temporário
        with open(entrada, "wb") as f:
            f.write(content)

        # Processa o arquivo
        processar_sped(entrada, saida)

        # Verifica se o arquivo de saída foi criado
        if not os.path.exists(saida):
            raise HTTPException(status_code=500, detail="Arquivo de saída não criado")

        return FileResponse(
            saida, 
            filename="SPED_corrigido.txt",
            media_type="text/plain"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar: {str(e)}")

@app.post("/consolidar-c175")
async def consolidar_c175_endpoint(file: UploadFile = File(...)):
    try:
        uid = str(uuid.uuid4())
        entrada = f"/tmp/{uid}.txt"
        saida = f"/tmp/{uid}_C175.txt"

        with open(entrada, "wb") as f:
            f.write(await file.read())

        processar_c175(entrada, saida)

        if not os.path.exists(saida):
            raise HTTPException(status_code=500, detail="Arquivo de saída não criado")

        return FileResponse(
            saida, 
            filename="SPED_C175.txt",
            media_type="text/plain"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar C175: {str(e)}")