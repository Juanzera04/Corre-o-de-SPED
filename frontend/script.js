const BASE_URL = "https://SEU-BACKEND.onrender.com";

async function enviarPis() {
  const f = document.getElementById("filePis").files[0];
  if (!f) return alert("Selecione um arquivo");

  const fd = new FormData();
  fd.append("file", f);

  const r = await fetch(`${BASE_URL}/api/pis-cofins`, {
    method: "POST",
    body: fd
  });

  baixar(r, "SPED_PISCOFINS.txt");
}

async function enviarC175() {
  const f = document.getElementById("fileC175").files[0];
  if (!f) return alert("Selecione um arquivo");

  const fd = new FormData();
  fd.append("file", f);

  const r = await fetch(`${BASE_URL}/api/consolidar-c175`, {
    method: "POST",
    body: fd
  });

  baixar(r, "SPED_C175.txt");
}

async function baixar(response, nome) {
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = nome;
  a.click();
  URL.revokeObjectURL(url);
}
