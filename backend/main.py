# main.py

from fastapi import FastAPI
from sped_processor import processar_sped, processar_c175

app = FastAPI()


@app.post("/corrigir")
def corrigir_sped(dados: list):
    resultado = processar_sped(dados)
    return {"resultado": resultado}


@app.post("/consolidar-c175")
def consolidar(dados: list):
    resultado = processar_c175(dados)
    return {"resultado": resultado}
