use libmdbx::{Database, DatabaseOptions, NoWriteMap, TableFlags, WriteFlags};
use std::{env, error::Error, fs, path::Path};

fn open_database(path: &Path) -> Result<Database<NoWriteMap>, Box<dyn Error>> {
    fs::create_dir_all(path)?;
    let options = DatabaseOptions {
        max_tables: Some(2),
        ..Default::default()
    };
    Ok(Database::open_with_options(path, options)?)
}

fn add_restaurant(path: &Path, name: &str, info: &str) -> Result<(), Box<dyn Error>> {
    let db = open_database(path)?;
    let txn = db.begin_rw_txn()?;
    let table = txn.create_table(Some("restaurants"), TableFlags::empty())?;

    txn.put(&table, name.as_bytes(), info.as_bytes(), WriteFlags::UPSERT)?;
    txn.commit()?;
    Ok(())
}

#[cfg(test)]
fn get_restaurant(path: &Path, name: &str) -> Result<Option<String>, Box<dyn Error>> {
    let db = open_database(path)?;
    let txn = db.begin_ro_txn()?;
    let table = txn.open_table(Some("restaurants"))?;
    let data = txn.get::<Vec<u8>>(&table, name.as_bytes())?;
    Ok(data.map(|raw| String::from_utf8_lossy(&raw).into_owned()))
}

fn main() -> Result<(), Box<dyn Error>> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: {} add <name> <info> [--db-path <path>]", args[0]);
        std::process::exit(1);
    }

    let db_path = args
        .iter()
        .position(|a| a == "--db-path")
        .and_then(|i| args.get(i + 1))
        .map(|s| s.as_str())
        .unwrap_or("./restaurant-db");

    match args[1].as_str() {
        "add" => {
            if args.len() < 4 {
                eprintln!("Usage: {} add <name> <info>", args[0]);
                std::process::exit(1);
            }
            let name = &args[2];
            let info = &args[3];
            add_restaurant(Path::new(db_path), name, info)?;
            println!("Saved restaurant \"{name}\"");
        }
        other => {
            eprintln!("Unknown command: {other}");
            std::process::exit(1);
        }
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;

    #[test]
    fn add_restaurant_persists_name_and_info() {
        let dir = tempdir().expect("create temp dir");
        let db_path = dir.path().join("db");

        add_restaurant(&db_path, "Sushi Place", "Open late").expect("add restaurant");
        let stored = get_restaurant(&db_path, "Sushi Place")
            .expect("load restaurant")
            .expect("record present");

        assert_eq!(stored, "Open late");
    }
}
