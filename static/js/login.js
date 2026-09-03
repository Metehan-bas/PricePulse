const supabaseUrl = "https://xuufcosqqtjmpccuwegz.supabase.co";
const supabaseKey = "sb_publishable_68Rb1G2CbCW1Oyv6m8bOBg_9e3yfo51";

const supabaseClient = window.supabase.createClient(
    supabaseUrl,
    supabaseKey
);

const form = document.getElementById("loginForm");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    let girisYapildiMi = false;

    const { data, error } = await supabaseClient.auth.signInWithPassword({
        email: email,
        password: password
    });

    if (error) {
        console.error(error);
        alert(error.message);
        return;
    }

    girisYapildiMi = true;
    localStorage.setItem("loggedIn", "true");
    alert("Giriş başarılı!");
    window.location.href = "/";
});