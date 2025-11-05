document.addEventListener("DOMContentLoaded", () => {
    const runBtn = document.getElementById("runBtn");
    const cancelBtn = document.getElementById("cancelBtn");
    const avisosContainer = document.getElementById("avisosContainer");
    const avisosContent = document.getElementById("avisosContent");
    const cancelSection = document.getElementById("cancelSection");
    const pathInput = document.getElementById("pathInput");

    runBtn.addEventListener("click", () => {
        const path = pathInput.value.trim();

        if (!path) {
            alert("Por favor, insira o caminho de rede antes de executar.");
            return;
        }

        avisosContainer.style.display = "block";
        cancelSection.style.display = "block";

        avisosContent.innerHTML = `
            <li><i class="fa-solid fa-spinner fa-spin me-2"></i>
                Executando automação no caminho: <b>${path}</b>
            </li>
        `;
    });

    cancelBtn.addEventListener("click", () => {
        avisosContent.innerHTML += `
            <li><i class="fa-solid fa-stop-circle me-2 text-danger"></i>
                Processo cancelado pelo usuário.
            </li>
        `;
        cancelSection.style.display = "none";
    });
});
