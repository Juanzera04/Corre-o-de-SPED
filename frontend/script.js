const API = "https://SEU-BACKEND.onrender.com";

function processarPisCofins(inputId) {
    const input = document.getElementById(inputId);
    if (!input.files.length) {
        alert("Selecione um arquivo");
        return;
    }

    const form = new FormData();
    form.append("file", input.files[0]);

    fetch(`${API}/corrigir`, {
        method: "POST",
        body: form
    })
    .then(r => r.blob())
    .then(b => download(b, "SPED_corrigido.txt"))
    .catch(e => alert(e));
}

function processarC175(inputId) {
    const input = document.getElementById(inputId);
    if (!input.files.length) {
        alert("Selecione um arquivo");
        return;
    }

    const form = new FormData();
    form.append("file", input.files[0]);

    fetch(`${API}/consolidar-c175`, {
        method: "POST",
        body: form
    })
    .then(r => r.blob())
    .then(b => download(b, "SPED_C175.txt"))
    .catch(e => alert(e));
}

function download(blob, nome) {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = nome;
    a.click();
    URL.revokeObjectURL(a.href);
}
