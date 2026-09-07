# Super Safe Restaurant CLI

Rust CLI for storing restaurant entries in an MDBX database using
[libmdbx-rs](https://github.com/vorot93/libmdbx-rs).

## Usage

```bash
cargo run -- add "Sushi Place" "Open late"
```

Use `--db-path` to change where the MDBX database directory is stored.