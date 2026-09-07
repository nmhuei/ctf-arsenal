import { PassThrough } from "node:stream";
import { renderToPipeableStream } from "react-dom/server.node";

globalThis.__webpack_require__ = function (id) {
  if (id !== "chal:gadget") throw Error("bad import");
  return {
    lmao: (arr) => {
      const [fn, thiz, ...args] = [...arr];
      if (typeof fn !== "function") throw new Error("bad fn");
      return Reflect.apply(fn, thiz, args);
    },
  };
};

const { createFromReadableStream } =
  await import("react-server-dom-webpack/client.node");

const jail = async (flight) => {
  const bytes = new TextEncoder().encode(flight);

  const stream = new ReadableStream({
    start(controller) {
      controller.enqueue(bytes);
      controller.close();
    },
  });

  const model = await createFromReadableStream(stream, {
    serverConsumerManifest: {
      moduleMap: null,
      moduleLoading: null,
      serverModuleMap: null,
    },
  });

  const output = new PassThrough();
  output.setEncoding("utf8");

  let html = "";

  output.on("data", (chunk) => {
    html += chunk;
  });

  const finished = new Promise((resolve, reject) => {
    output.on("end", resolve);
    output.on("error", reject);
  });

  const { pipe } = renderToPipeableStream(model, {
    onAllReady() {
      pipe(output);
    },
  });

  await finished;

  return html;
};

export default jail;

