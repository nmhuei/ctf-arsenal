function notFound(req, res) {
  res.status(404).render("errors/error", {
    title: "Not found",
    status: 404,
    message: "That page drifted out of signal range.",
  });
}

function errorHandler(error, req, res, _next) {
  if (!error.status || error.status >= 500) {
    console.error(error);
  }

  if (error.code === "LIMIT_FILE_SIZE") {
    return res.status(400).render("errors/error", {
      title: "Upload too large",
      status: 400,
      message: "Images must be 5 MB or smaller.",
    });
  }

  res.status(error.status || 500).render("errors/error", {
    title: error.status === 403 ? "Access denied" : "System error",
    status: error.status || 500,
    message:
      error.expose && error.message
        ? error.message
        : "Tagger hit an unexpected glitch. Please try again.",
  });
}

module.exports = { errorHandler, notFound };
