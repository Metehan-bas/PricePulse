const supabaseUrl = "https://xuufcosqqtjmpccuwegz.supabase.co";
const supabaseKey = "sb_publishable_68Rb1G2CbCW1Oyv6m8bOBg_9e3yfo51";

const supabaseClient = window.supabase.createClient(supabaseUrl, supabaseKey);

const form = document.getElementById("registerForm");

if (form) {
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const firstName = document.getElementById("firstName").value.trim();
        const lastName = document.getElementById("lastName").value.trim();
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;
        const confirmPassword = document.getElementById("confirmPassword").value;

        if (password !== confirmPassword) {
            alert("Şifreler eşleşmiyor.");
            return;
        }

        const { data, error } = await supabaseClient.auth.signUp({ email, password });

        if (error) {
            console.error(error);
            alert(error.message);
            return;
        }

        const { error: insertError } = await supabaseClient
            .from("Members")
            .insert([{ id: data.user.id, name: firstName, surname: lastName, mail: email }]);

        if (insertError) {
            console.error(insertError);
            alert(insertError.message);
            return;
        }

        alert("Kayıt başarılı!");
        window.location.href = "/login";
    });
}
