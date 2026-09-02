use std::{env, fs, process::exit};

use revm::{
    db::{CacheDB, EmptyDB},
    primitives::{alloy_primitives::keccak256, Address, ExecutionResult, Output, SpecId, TransactTo},
    Evm,
};

const FLAG_BLOB: [u8; 64] = [
    0x77, 0x1b, 0x62, 0x6a, 0x88, 0xdb, 0xb7, 0x6c, 0x07, 0x28, 0xe2, 0x9a, 0x97, 0xb0, 0xb8, 0xc5,
    0x10, 0xb9, 0x83, 0x48, 0x5a, 0x5e, 0x0a, 0x73, 0x29, 0x0a, 0xe9, 0x1c, 0xad, 0xbd, 0xb6, 0x68,
    0x17, 0xfa, 0xa9, 0xf0, 0xa5, 0x5d, 0xd2, 0x77, 0x2c, 0x5a, 0xe3, 0xae, 0x2d, 0xc8, 0xb1, 0xba,
    0x34, 0x88, 0xa1, 0xf2, 0x9b, 0x32, 0x3e, 0x7b, 0x64, 0x42, 0xd1, 0x15, 0x70, 0x5f, 0xc2, 0x4a,
];

const TARGETS: [[u8; 16]; 4] = [
    [0xba, 0x93, 0x83, 0xce, 0xdc, 0xe8, 0x6c, 0x2f, 0xed, 0x64, 0x8b, 0x9d, 0x17, 0x2e, 0xa2, 0x16],
    [0xe7, 0x8b, 0x91, 0xff, 0x62, 0x00, 0x51, 0x74, 0x67, 0xb1, 0xe5, 0x5a, 0x85, 0xa4, 0x47, 0x42],
    [0xcc, 0x07, 0xfb, 0x3d, 0x22, 0x16, 0xfc, 0x7b, 0x0a, 0xec, 0xa4, 0xd3, 0xcc, 0xed, 0x20, 0x95],
    [0xfe, 0x18, 0x15, 0x27, 0x0a, 0x53, 0x9c, 0xc1, 0x15, 0x5e, 0x32, 0x0b, 0x92, 0xae, 0xf3, 0x97],
];

const SENDER: Address = Address::new([
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0xc0, 0xde,
]);

fn unhex(s: &str) -> Vec<u8> {
    let s = s.trim();
    hex::decode(s.strip_prefix("0x").unwrap_or(s)).expect("invalid hex")
}

fn transact(db: &mut CacheDB<EmptyDB>, to: TransactTo, data: Vec<u8>) -> ExecutionResult {
    Evm::builder()
        .with_db(db)
        .with_spec_id(SpecId::CANCUN)
        .modify_cfg_env(|c| c.limit_contract_code_size = Some(usize::MAX))
        .modify_tx_env(|tx| {
            tx.caller = SENDER;
            tx.transact_to = to;
            tx.data = data.into();
            tx.gas_limit = u64::MAX;
        })
        .build()
        .transact_commit()
        .expect("evm execution failed")
}

fn run_contract(code: Vec<u8>, calldata: Vec<u8>) -> Vec<u8> {
    let mut db = CacheDB::new(EmptyDB::default());
    let addr = match transact(&mut db, TransactTo::Create, code) {
        ExecutionResult::Success {
            output: Output::Create(_, Some(a)),
            ..
        } => a,
        other => panic!("deploy failed: {other:?}"),
    };
    match transact(&mut db, TransactTo::Call(addr), calldata) {
        ExecutionResult::Success {
            output: Output::Call(out),
            ..
        } => out.to_vec(),
        other => panic!("call failed: {other:?}"),
    }
}

fn oracle(bytecode_path: &str, calldata: &str) {
    let code = fs::read(bytecode_path).expect("read bytecode");
    let out = run_contract(code, unhex(calldata));
    println!("0x{}", hex::encode(out));
}

fn solve(plaintexts: &[String]) {
    let dir = env::var("NEVM_DIR").unwrap_or_else(|_| ".".into());
    let mut packed = Vec::with_capacity(64);
    let mut correct = true;

    for (i, pt) in plaintexts.iter().enumerate() {
        let n = i + 1;
        let pt = unhex(pt);
        assert_eq!(pt.len(), 16, "plaintext {n} must be 16 bytes");
        packed.extend_from_slice(&pt);

        let code = fs::read(format!("{dir}/challenge_{n}.bin")).expect("read challenge");
        let mut calldata = vec![0u8; 36];
        calldata[20..].copy_from_slice(&pt);

        if run_contract(code, calldata)[..16] == TARGETS[i] {
            eprintln!("contract {n}: ok");
        } else {
            eprintln!("contract {n}: wrong");
            correct = false;
        }
    }

    if !correct {
        exit(1);
    }

    let key0 = keccak256(&packed);
    let key1 = keccak256(key0);
    let mut flag = [0u8; 64];
    for i in 0..32 {
        flag[i] = key0[i] ^ FLAG_BLOB[i];
        flag[32 + i] = key1[i] ^ FLAG_BLOB[32 + i];
    }
    println!("{}", String::from_utf8_lossy(&flag));
}

fn print_targets() {
    for (i, t) in TARGETS.iter().enumerate() {
        println!("target_{} = {}", i + 1, hex::encode(t));
    }
}

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();
    match args.as_slice() {
        [cmd, pts @ ..] if cmd == "solve" && pts.len() == 4 => solve(pts),
        [bytecode, calldata] => oracle(bytecode, calldata),
        [] => print_targets(),
        _ => {
            eprintln!("usage: nevm-runner                          # print the 4 targets");
            eprintln!("       nevm-runner <bytecode> <calldata>    # query a contract");
            eprintln!("       nevm-runner solve <pt1> <pt2> <pt3> <pt4>");
            exit(1);
        }
    }
}
