async function searchProduct() {

    const product = document.getElementById("product").value.trim();

    if (!product) {
        alert("Lütfen bir ürün adı gir.");
        return;
    }

    document.getElementById("results").innerHTML =
        "<p class='text-gray-400'>Ürünler aranıyor...</p>";

    try {

        const response = await fetch("/search", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                product: product
            })

        });

        const data = await response.json();

        let html = "";

        function createCards(title, items) {

            html += `
                <h2 class="text-2xl font-bold mt-8 mb-4">${title}</h2>
            `;

            if (!items.length) {

                html += `
                    <p class="text-gray-400">Sonuç bulunamadı.</p>
                `;

                return;
            }

            items.forEach(item => {

                html += `
                    <div class="bg-slate-800 p-5 rounded-xl mb-4">

                        <h3 class="font-bold text-lg">
                            ${item.ad}
                        </h3>

                        <p class="text-green-400 mt-2">
                            ${item.fiyat}
                        </p>

                        <p class="text-gray-400">
                            ${item.site}
                        </p>

                    </div>
                `;

            });

        }

        createCards("Trendyol", data.trendyol);
        createCards("Hepsiburada", data.hepsiburada);
        createCards("Amazon", data.amazon);

        document.getElementById("results").innerHTML = html;

    }

    catch (err) {

        console.error(err);

        document.getElementById("results").innerHTML =
            "<p class='text-red-500'>Bir hata oluştu.</p>";

    }

}