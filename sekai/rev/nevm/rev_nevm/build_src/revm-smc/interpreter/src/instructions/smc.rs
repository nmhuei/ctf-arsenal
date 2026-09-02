use crate::{
    interpreter::analysis::to_analysed,
    primitives::{Bytecode, Bytes},
    Host, InstructionResult, Interpreter,
};

pub fn decrypt_smc<H: Host + ?Sized>(interpreter: &mut Interpreter, _host: &mut H) {
    gas!(interpreter, 3);
    pop!(interpreter, len, start, key);
    let len = as_usize_or_fail!(interpreter, len);
    let start = as_usize_or_fail!(interpreter, start);

    let code = interpreter.contract.bytecode.original_byte_slice();
    let Some(end) = len.checked_next_multiple_of(32).map(|n| start.saturating_add(n)) else {
        interpreter.instruction_result = InstructionResult::OutOfOffset;
        return;
    };
    if end > code.len() {
        interpreter.instruction_result = InstructionResult::OutOfOffset;
        return;
    }

    let key = key.to_be_bytes::<32>();
    let mut runtime: Vec<u8> = code[start..end]
        .iter()
        .enumerate()
        .map(|(i, b)| b ^ key[i % 32])
        .collect();
    runtime.truncate(len);

    interpreter.contract.bytecode = to_analysed(Bytecode::new_legacy(Bytes::from(runtime)));
    interpreter.bytecode = interpreter.contract.bytecode.bytecode().clone();
    interpreter.instruction_pointer = interpreter.bytecode.as_ptr();
}
