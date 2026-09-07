function escapeMarkup(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function serializeAttributes(attributes) {
  if (
    !attributes ||
    typeof attributes !== "object" ||
    Array.isArray(attributes)
  ) {
    return "";
  }

  return Object.entries(attributes)
    .filter(
      ([name, value]) =>
        /^[a-z]+$/.test(name) && /^[a-zA-Z0-9,. =]*$/.test(String(value))
    )
    .map(([name, value]) => ` ${name}="${escapeMarkup(value)}"`)
    .join("");
}

function safeImageSource(value) {
  const source = String(value || "").trim();
  if (
    /^data:image\/(?:png|jpeg|gif|webp);base64,[a-zA-Z0-9+/]+={0,2}$/.test(
      source
    )
  ) {
    return source;
  }
  return "";
}

function messageMarkup(message) {
  const storedTag = String(message.tagName || "message");
  const fallbackTag = message.type === "image" ? "img" : "message";
  const tagName = /^[a-z][^a-zA-Z \t\\\/<>"'&#]*$/.test(storedTag)
    ? storedTag
    : fallbackTag;
  const attributes = { ...(message.attributes || {}) };

  if (message.type === "image") {
    delete attributes.src;
    return `<img${serializeAttributes(attributes)} class="message-image" src="${escapeMarkup(safeImageSource(message.content))}" alt="Shared image">`;
  }

  // `message` is the storage-level name for the standard paragraph element.
  const renderedTag = tagName === "message" ? "p" : tagName;
  return `<${renderedTag}${serializeAttributes(attributes)}>${escapeMarkup(message.content)}</${renderedTag}>`;
}

module.exports = { messageMarkup };
