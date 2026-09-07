function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

export function validateArchive(archive) {
  if (!isObject(archive) || !isObject(archive.manifest) || !Array.isArray(archive.memories)) {
    throw new Error("Archive requires manifest and memories.");
  }
  if (typeof archive.manifest.name !== "string" || archive.manifest.name.length < 1 || archive.manifest.name.length > 60) {
    throw new Error("Invalid manifest name.");
  }
  if (!Array.isArray(archive.manifest.capabilities) || archive.manifest.capabilities.some((capability) => capability !== "memory.search")) {
    throw new Error("Manifest requests an unsupported capability.");
  }
  if (archive.memories.length > 12 || archive.memories.some((memory) => !isObject(memory) || typeof memory.text !== "string" || memory.text.length > 1200)) {
    throw new Error("Invalid episodic memory.");
  }
}

export function restoreArchive(archive) {
  validateArchive(archive);
  return {
    id: crypto.randomUUID(),
    manifest: archive.manifest,
    memories: archive.memories
  };
}
