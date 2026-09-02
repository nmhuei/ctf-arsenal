# Phantasmoon

Start the browser-accessible desktop:

```sh
docker compose up --build
```

Open <https://localhost:3001>, launch a terminal, and validate the example bot:

```sh
phantasmoon-gui --check /workspace/robot.s
```

Run a match using the example for both players:

```sh
phantasmoon-gui \
  --bot0 /workspace/robot.s \
  --bot1 /workspace/robot.s
```
