const sitesAPI = "/apis/triangle.io/v1/namespaces/tenant-a/sites";
const domainOf = (name) => `${name}.sites.triangle.tld`;
const previewOf = (name) => `/api/v1/namespaces/tenant-a/services/${name}:80/proxy/`;

const el = {
    sites: document.getElementById("sites"),
    editor: document.getElementById("editor"),
    name: document.getElementById("name"),
    domain: document.getElementById("domain"),
    content: document.getElementById("content"),
    log: document.getElementById("log"),
};

function say(text, kind) {
    el.log.hidden = false;
    el.log.dataset.kind = kind;
    el.log.textContent = text;
}

async function call(path, options) {
    const res = await fetch(path, options);
    const body = res.status === 204 ? null : await res.json();
    if (!res.ok) {
        throw new Error(body?.message ?? `${res.status} ${res.statusText}`);
    }
    return body;
}

function node(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
}

function siteYAML(form) {
    const integrations = [...form.querySelectorAll("input[name=integration]:checked")]
        .map((box) => box.value);

    const lines = ["target:", `  plane: ${form.plane.value}`];
    if (integrations.length) {
        lines.push("integrations:", ...integrations.map((name) => `  - ${name}`));
    }
    lines.push("server:", `  root: ${form.root.value}`, `  index: ${form.index.value}`);

    const page = form.content.value.replace(/\s+$/, "");
    if (page) {
        lines.push("content: |", ...page.split("\n").map((line) => `  ${line}`));
    }
    lines.push("");
    return lines.join("\n");
}

const varsCache = new Map();

async function configVars(name) {
    const res = await fetch(`/internal/v1/domains?host=${encodeURIComponent(domainOf(name))}`);
    if (!res.ok) {
        return {unavailable: res.status};
    }
    return {env: (await res.json()).env ?? []};
}

function renderVars(target, name) {
    if (!varsCache.has(name)) {
        varsCache.set(name, configVars(name));
    }
    varsCache.get(name).then(({env, unavailable}) => {
        if (unavailable) {
            target.dataset.kind = "error";
            target.textContent = `unavailable · ${unavailable}`;
            return;
        }
        target.replaceChildren(...env.map((variable) => {
            const row = node("span", "var", variable);
            row.append(node("em", null, "•".repeat(12)));
            return row;
        }));
    });
}

function card(item) {
    const name = item.metadata.name;
    const phase = item.status?.phase ?? "Pending";

    const title = node("span", "site-name", name);

    const state = node("span", "phase", phase);
    state.dataset.phase = phase;

    const view = node("a", "button", "View site");
    view.href = previewOf(name);
    view.target = "_blank";
    view.rel = "noreferrer";

    const remove = node("button", "ghost", "Delete");
    remove.type = "button";
    remove.addEventListener("click", async () => {
        try {
            await call(`${sitesAPI}/${name}`, {method: "DELETE"});
            say(`Deleted ${name}.`, "info");
        } catch (err) {
            say(err.message, "error");
        }
        refresh();
    });

    const values = node("dd");
    renderVars(values, name);

    const vars = node("dl", "vars");
    vars.append(node("dt", null, "Config vars"), values);

    const head = node("div", "site-head");
    head.append(title, state);

    const actions = node("div", "site-actions");
    actions.append(view, remove);

    const box = node("article", "site");
    box.append(
        head,
        node("p", "domain", domainOf(name)),
        node("p", "message", item.status?.message ?? ""),
        vars,
        actions,
    );
    return box;
}

let shown = "";

function render(list) {
    const state = JSON.stringify(list.items.map((item) => [
        item.metadata.name,
        item.status?.phase,
        item.status?.message,
    ]));
    if (state === shown) return;
    shown = state;

    if (!list.items.length) {
        el.sites.replaceChildren(node("p", "empty", "No sites yet."));
        return;
    }
    el.sites.replaceChildren(...list.items.map(card));
}

async function refresh() {
    try {
        render(await call(sitesAPI));
    } catch (err) {
        say(err.message, "error");
    }
}

el.content.value = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>My shop</title>
</head>
<body>
<h1>My shop</h1>
<p>Opening soon.</p>
</body>
</html>
`;

el.name.addEventListener("input", () => {
    el.domain.textContent = el.name.value || "site";
});

el.editor.addEventListener("submit", async (event) => {
    event.preventDefault();
    const name = el.name.value.trim();
    const body = {
        apiVersion: "triangle.io/v1",
        kind: "Site",
        metadata: {name},
        spec: {siteYAML: siteYAML(el.editor)},
    };
    try {
        const current = await fetch(`${sitesAPI}/${name}`);
        if (current.ok) {
            body.metadata.resourceVersion = (await current.json()).metadata.resourceVersion;
            await call(`${sitesAPI}/${name}`, {
                method: "PUT",
                headers: {"content-type": "application/json"},
                body: JSON.stringify(body),
            });
            say(`Updated ${name}.`, "info");
        } else {
            await call(sitesAPI, {
                method: "POST",
                headers: {"content-type": "application/json"},
                body: JSON.stringify(body),
            });
            say(`Deployed ${name}.`, "info");
        }
    } catch (err) {
        say(err.message, "error");
    }
    varsCache.delete(name);
    shown = "";
    refresh();
});

refresh();
setInterval(refresh, 5000);
