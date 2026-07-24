function showError(msg) {
  const el = document.getElementById("error-banner");
  el.textContent = msg;
  el.classList.add("show");
}
function hideError() {
  document.getElementById("error-banner").classList.remove("show");
}

document.addEventListener("DOMContentLoaded", () => {
  if (Api.isLoggedIn()) {
    window.location.href = "/dashboard/";
    return;
  }

  const loginForm = document.getElementById("login-form");
  const signupForm = document.getElementById("signup-form");
  const showSignup = document.getElementById("show-signup");
  const showLogin = document.getElementById("show-login");

  if (showSignup) showSignup.addEventListener("click", (e) => {
    e.preventDefault();
    document.getElementById("login-card").style.display = "none";
    document.getElementById("signup-card").style.display = "block";
  });
  if (showLogin) showLogin.addEventListener("click", (e) => {
    e.preventDefault();
    document.getElementById("signup-card").style.display = "none";
    document.getElementById("login-card").style.display = "block";
  });

  if (loginForm) loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideError();
    const username = document.getElementById("login-username").value.trim();
    const password = document.getElementById("login-password").value;
    try {
      const data = await Api.login({ username, password });
      Api.setTokens(data.access, data.refresh);
      window.location.href = "/dashboard/";
    } catch (err) {
      showError("Login failed: " + err.message);
    }
  });

  if (signupForm) signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideError();
    const username = document.getElementById("signup-username").value.trim();
    const email = document.getElementById("signup-email").value.trim();
    const password = document.getElementById("signup-password").value;
    const password_confirm = document.getElementById("signup-password-confirm").value;
    try {
      const data = await Api.register({ username, email, password, password_confirm });
      Api.setTokens(data.access, data.refresh);
      window.location.href = "/dashboard/";
    } catch (err) {
      showError("Sign up failed: " + err.message);
    }
  });
});
