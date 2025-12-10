from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sped_processor import processar_sped
import uuid

app = FastAPI()

# --- CORS LIBERADO ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # se quiser, posso limitar ao domínio do Render
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
