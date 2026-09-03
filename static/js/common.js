document.addEventListener("DOMContentLoaded", () => {
    const girisYapildiMi = localStorage.getItem("loggedIn") === "true";
    const authButtons = document.getElementById("authButtons");

    if (girisYapildiMi && authButtons) {
        authButtons.classList.add("hidden");

        const header = document.querySelector("header");

        const container = document.createElement("div");
        container.className = "flex items-center gap-3";

        const userBox = document.createElement("div");
        userBox.innerHTML = `
            <button class="bg-tranparent-600 px-5 py-3 rounded-xl border border-slate-500" onclick="cikisYap()">
                Çıkış Yap
            </button>
        `;

        const DashboardBtn = document.createElement("div");
        DashboardBtn.innerHTML = `
            <button id="dashboardBtn" class="bg-violet-600 px-5 py-3 rounded-xl border border-slate-700">
                <a href="/dashboard">Dashboard</a>
            </button>
        `;

        container.appendChild(DashboardBtn);
        container.appendChild(userBox);
        header.appendChild(container);
    }
});

function cikisYap() {
    localStorage.removeItem("loggedIn");
    window.location.reload();
}