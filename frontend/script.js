const API_BASE = "https://SEU-BACKEND.onrender.com";

// ===============================
// PIS / COFINS
// ===============================
async function enviarPisCofins() {

  const input = document.getElementById("fileInputPis");
  if (!input.files.length) {
    alert("Selecione um arquivo SPED");
    return;
  }

  const formData = new FormData();
  formData.append("file", input.files[0]);

  const response = await fetch(`${API_BASE}/corrigir`, {
    method: "POST",
    body: formData
  });

  if (!response.ok) {
    alert("Erro ao processar o arquivo");
    return;
  }

  baixarArquivo(response, "SPED_PISCOFINS.txt");
}

// ===============================
// CONSOLIDAR C175
// ===============================
async function enviarC175() {

  const input = document.getElementById("fileInputC175");
  if (!input.files.length) {
    alert("Selecione um arquivo SPED");
    return;
  }

  const formData = new FormData();
  formData.append("file", input.files[0]);

  const response = await fetch(`${API_BASE}/consolidar-c175`, {
    method: "POST",
    body: formData
  });

  if (!response.ok) {
    alert("Erro ao processar o arquivo");
    return;
  }

  baixarArquivo(response, "SPED_C175.txt");
}

// ===============================
// DOWNLOAD
// ===============================
async function baixarArquivo(response, nomeArquivo) {
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = nomeArquivo;
  document.body.appendChild(a);
  a.click();

  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}
