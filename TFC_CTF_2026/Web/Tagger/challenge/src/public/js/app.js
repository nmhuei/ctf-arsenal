const messages = document.querySelector("#messages");
if (messages) {
  messages.scrollTop = messages.scrollHeight;
}

const imageInput = document.querySelector("#image-input");
const fileName = document.querySelector("#file-name");
if (imageInput && fileName) {
  imageInput.addEventListener("change", () => {
    fileName.textContent = imageInput.files[0] ? imageInput.files[0].name : "";
  });
}

document.querySelectorAll(".flash").forEach((flash) => {
  window.setTimeout(() => flash.classList.add("flash-fade"), 4500);
});
