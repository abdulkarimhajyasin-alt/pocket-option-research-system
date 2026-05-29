document.addEventListener("submit", (event) => {
  const form = event.target;
  if (!form.matches(".action-card")) {
    return;
  }
  const button = form.querySelector("button");
  if (button) {
    button.disabled = true;
    button.textContent = "Running";
  }
});
