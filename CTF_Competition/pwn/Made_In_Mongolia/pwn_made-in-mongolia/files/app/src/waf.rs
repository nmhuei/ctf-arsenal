use std::{
    fmt,
    panic::{AssertUnwindSafe, catch_unwind},
};

use sfex_lang::{Expression, Lexer, Parser, Program, Statement};

const BLOCKED_GLOBALS: &[&str] = &[
    "System",
    "File",
    "Data",
    "CSV",
    "Env",
    "HTTP",
    "WebSocket",
    "TCP",
    "UDP",
    "LLM",
];

#[derive(Debug, PartialEq, Eq)]
pub struct Violation {
    line: usize,
    token: String,
    kind: ViolationKind,
}

#[derive(Debug, PartialEq, Eq)]
enum ViolationKind {
    Import,
    UnsafeGlobal,
}

impl fmt::Display for Violation {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self.kind {
            // SFEX records a Use statement's line after consuming its trailing
            // newline, so omit that misleading location from the user message.
            ViolationKind::Import => write!(formatter, "WAF blocked an import."),
            ViolationKind::UnsafeGlobal => write!(
                formatter,
                "WAF blocked unsafe standard-library access `{}` at line {}.",
                self.token, self.line
            ),
        }
    }
}

pub fn inspect(source: &str) -> Result<(), Violation> {
    // Invalid source is safe to pass through: the same parser in the child
    // process will reject it and return SFEX's native diagnostic. Catching
    // unwinds keeps a parser bug from taking down the HTTP process.
    let parsed = catch_unwind(AssertUnwindSafe(|| {
        let tokens = Lexer::new(source).tokenize().ok()?;
        Parser::new(tokens).parse().ok()
    }));

    let Ok(Some(program)) = parsed else {
        return Ok(());
    };

    inspect_program(&program)
}

fn inspect_program(program: &Program) -> Result<(), Violation> {
    inspect_statements(&program.story.body)?;

    for concept in &program.concepts {
        for method in &concept.methods {
            inspect_statements(&method.body)?;
        }
        for observer in concept.when_observers.values() {
            inspect_statements(observer)?;
        }
    }

    for situation in &program.situations {
        for adjustment in &situation.adjustments {
            for method in &adjustment.methods {
                inspect_statements(&method.body)?;
            }
        }
    }

    Ok(())
}

fn inspect_statements(statements: &[Statement]) -> Result<(), Violation> {
    for statement in statements {
        inspect_statement(statement)?;
    }
    Ok(())
}

fn inspect_statement(statement: &Statement) -> Result<(), Violation> {
    match statement {
        Statement::Use { line, .. } => Err(Violation {
            line: *line,
            token: "Use".to_owned(),
            kind: ViolationKind::Import,
        }),
        Statement::Assignment {
            target,
            value,
            line,
        } => {
            inspect_name(target, *line)?;
            inspect_expression(value, *line)
        }
        Statement::Create {
            initial_fields,
            line,
            ..
        } => {
            for (_, value) in initial_fields {
                inspect_expression(value, *line)?;
            }
            Ok(())
        }
        Statement::Set {
            target,
            value,
            line,
        } => {
            inspect_expression(target, *line)?;
            inspect_expression(value, *line)
        }
        Statement::Print { value, line } => inspect_expression(value, *line),
        Statement::SwitchOn { .. }
        | Statement::SwitchOff { .. }
        | Statement::Break { .. }
        | Statement::Continue { .. } => Ok(()),
        Statement::If {
            condition,
            then_body,
            else_body,
            line,
        } => {
            inspect_expression(condition, *line)?;
            inspect_statements(then_body)?;
            if let Some(else_body) = else_body {
                inspect_statements(else_body)?;
            }
            Ok(())
        }
        Statement::When {
            value,
            cases,
            otherwise,
            line,
        } => {
            inspect_expression(value, *line)?;
            for (case, body) in cases {
                inspect_expression(case, *line)?;
                inspect_statements(body)?;
            }
            if let Some(otherwise) = otherwise {
                inspect_statements(otherwise)?;
            }
            Ok(())
        }
        Statement::TryCatch {
            try_body,
            catch_body,
            always_body,
            ..
        } => {
            inspect_statements(try_body)?;
            if let Some(catch_body) = catch_body {
                inspect_statements(catch_body)?;
            }
            if let Some(always_body) = always_body {
                inspect_statements(always_body)?;
            }
            Ok(())
        }
        Statement::RepeatTimes {
            count, body, line, ..
        } => {
            inspect_expression(count, *line)?;
            inspect_statements(body)
        }
        Statement::RepeatWhile {
            condition,
            body,
            line,
        } => {
            inspect_expression(condition, *line)?;
            inspect_statements(body)
        }
        Statement::ForEach {
            iterable,
            body,
            line,
            ..
        } => {
            inspect_expression(iterable, *line)?;
            inspect_statements(body)
        }
        Statement::Return { value, line } => {
            if let Some(value) = value {
                inspect_expression(value, *line)?;
            }
            Ok(())
        }
        Statement::Expression { expr, line } => inspect_expression(expr, *line),
    }
}

fn inspect_expression(expression: &Expression, line: usize) -> Result<(), Violation> {
    match expression {
        Expression::Number(_) | Expression::String(_) | Expression::Boolean(_) => Ok(()),
        Expression::Identifier(name) => inspect_name(name, line),
        Expression::List(items) => {
            for item in items {
                inspect_expression(item, line)?;
            }
            Ok(())
        }
        Expression::Map(entries) => {
            for (_, value) in entries {
                inspect_expression(value, line)?;
            }
            Ok(())
        }
        Expression::BinaryOp { left, right, .. } => {
            inspect_expression(left, line)?;
            inspect_expression(right, line)
        }
        Expression::UnaryOp { operand, .. } => inspect_expression(operand, line),
        Expression::Index { object, index } => {
            inspect_expression(object, line)?;
            inspect_expression(index, line)
        }
        Expression::MemberAccess { object, .. } => inspect_expression(object, line),
        Expression::MethodCall {
            object, arguments, ..
        } => {
            inspect_expression(object, line)?;
            for (_, argument) in arguments {
                inspect_expression(argument, line)?;
            }
            Ok(())
        }
        Expression::FunctionCall { name, arguments } => {
            inspect_name(name, line)?;
            for argument in arguments {
                inspect_expression(argument, line)?;
            }
            Ok(())
        }
        Expression::Call { callee, arguments } => {
            inspect_expression(callee, line)?;
            for argument in arguments {
                inspect_expression(argument, line)?;
            }
            Ok(())
        }
        Expression::DoInBackground { body } => inspect_statements(body),
        Expression::Proceed { arguments } => {
            for argument in arguments {
                inspect_expression(argument, line)?;
            }
            Ok(())
        }
    }
}

fn inspect_name(name: &str, line: usize) -> Result<(), Violation> {
    if let Some(blocked) = BLOCKED_GLOBALS.iter().find(|blocked| name == **blocked) {
        Err(Violation {
            line,
            token: (*blocked).to_owned(),
            kind: ViolationKind::UnsafeGlobal,
        })
    } else {
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn permits_normal_language_features() {
        let source = r#"Story:
    Values is [1, 2, 3]
    Print JSON.Stringify(Values)
"#;
        assert_eq!(inspect(source), Ok(()));
    }

    #[test]
    fn blocks_imports() {
        let violation = inspect("Use models.User\n").unwrap_err();
        assert_eq!(violation.kind, ViolationKind::Import);
    }

    #[test]
    fn blocks_unsafe_globals_and_aliases() {
        for global in BLOCKED_GLOBALS {
            let source = format!("Story:\n    Alias is {global}\n");
            let violation = inspect(&source).unwrap_err();
            assert_eq!(violation.kind, ViolationKind::UnsafeGlobal);
            assert_eq!(violation.token, *global);
        }
    }

    #[test]
    fn permits_names_that_only_differ_from_unsafe_globals_by_case() {
        let source = r#"Story:
    data is 1
    file is data
    env is file
    Print env
"#;
        assert_eq!(inspect(source), Ok(()));
    }

    #[test]
    fn ignores_comments_and_strings_via_sfex_parser() {
        let source = r#"Story:
    # System.Execute("id")
    Print "Use File HTTP TCP"
    Print 'Env.Load(\"secrets\")'
"#;
        assert_eq!(inspect(source), Ok(()));
    }

    #[test]
    fn ignores_triple_quoted_strings_via_sfex_parser() {
        let source = r#"Story:
    Text is """Use modules.Bad
System.Execute("/bin/echo nope")
File.Read("/flag")"""
    Print Text
"#;
        assert_eq!(inspect(source), Ok(()));
    }

    #[test]
    fn traverses_nested_and_background_expressions() {
        let source = r#"Story:
    If True:
        Repeat 1 times:
            Do in background:
                Result is System.Info()
"#;
        assert!(inspect(source).is_err());
    }

    #[test]
    fn lets_original_parser_report_invalid_source() {
        assert_eq!(inspect("Story:\n  !!! System.Execute"), Ok(()));
    }
}
