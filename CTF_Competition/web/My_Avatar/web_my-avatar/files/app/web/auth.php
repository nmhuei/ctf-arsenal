<?php
declare(strict_types=1);

require_once __DIR__ . '/db.php';
require_once __DIR__ . '/includes/functions.php';

function get_current_user_record(PDO $pdo): ?array
{
    $userId = current_user_id();
    if ($userId === null) {
        return null;
    }

    $stmt = $pdo->prepare('SELECT id, username, email, created_at FROM users WHERE id = :id LIMIT 1');
    $stmt->execute([':id' => $userId]);
    $user = $stmt->fetch();

    return $user ?: null;
}

function get_user_avatars(PDO $pdo, int $userId): array
{
    $stmt = $pdo->prepare('SELECT id, file_path, original_name, created_at FROM avatars WHERE user_id = :uid ORDER BY created_at DESC');
    $stmt->execute([':uid' => $userId]);
    return $stmt->fetchAll();
}

function register_user(PDO $pdo, array $data): array
{
    if (!verify_csrf($data['csrf_token'] ?? null)) {
        return ['ok' => false, 'message' => 'Invalid security token.'];
    }

    $username = sanitize_text($data['username'] ?? null);
    $email = strtolower(sanitize_text($data['email'] ?? null));
    $password = sanitize_text($data['password'] ?? null);
    $confirmPassword = sanitize_text($data['confirm_password'] ?? null);

    if ($username === '' || $email === '' || $password === '' || $confirmPassword === '') {
        return ['ok' => false, 'message' => 'All fields are required.'];
    }

    if (!preg_match('/^[a-zA-Z0-9_]{3,30}$/', $username)) {
        return ['ok' => false, 'message' => 'Username must be 3-30 letters, numbers, or underscores.'];
    }

    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        return ['ok' => false, 'message' => 'Enter a valid email address.'];
    }

    if (strlen($password) < 8) {
        return ['ok' => false, 'message' => 'Password must be at least 8 characters.'];
    }

    if ($password !== $confirmPassword) {
        return ['ok' => false, 'message' => 'Passwords do not match.'];
    }

    try {
        $exists = $pdo->prepare(
            'SELECT id FROM users WHERE username = :username OR email = :email LIMIT 1'
        );
        $exists->execute([
            ':username' => $username,
            ':email' => $email,
        ]);

        if ($exists->fetch()) {
            return ['ok' => false, 'message' => 'Username or email is already registered.'];
        }

        $passwordHash = password_hash($password, PASSWORD_DEFAULT);
        $insert = $pdo->prepare(
            'INSERT INTO users (username, email, password_hash)
             VALUES (:username, :email, :password_hash)'
        );
        $insert->execute([
            ':username' => $username,
            ':email' => $email,
            ':password_hash' => $passwordHash,
        ]);

        $userId = (int)$pdo->lastInsertId();
        session_regenerate_id(true);
        $_SESSION['user_id'] = $userId;
        $_SESSION['username'] = $username;
        $_SESSION['email'] = $email;

        flash('success', 'Account created. Welcome!');
        return ['ok' => true, 'message' => 'Account created successfully.'];
    } catch (Throwable) {
        return ['ok' => false, 'message' => 'Could not create account. Please try again.'];
    }
}

function login_user(PDO $pdo, array $data): array
{
    if (!verify_csrf($data['csrf_token'] ?? null)) {
        return ['ok' => false, 'message' => 'Invalid security token.'];
    }

    $identity = sanitize_text($data['identity'] ?? null);
    $password = sanitize_text($data['password'] ?? null);

    if ($identity === '' || $password === '') {
        return ['ok' => false, 'message' => 'All fields are required.'];
    }

    try {
        $stmt = $pdo->prepare(
            'SELECT id, username, email, password_hash
             FROM users
             WHERE username = :identity OR email = :identity
             LIMIT 1'
        );
        $stmt->execute([':identity' => $identity]);
        $user = $stmt->fetch();

        if (!$user || !password_verify($password, $user['password_hash'])) {
            return ['ok' => false, 'message' => 'Invalid username/email or password.'];
        }

        session_regenerate_id(true);
        $_SESSION['user_id'] = (int)$user['id'];
        $_SESSION['username'] = (string)$user['username'];
        $_SESSION['email'] = (string)$user['email'];
        flash('success', 'Welcome back!');

        return ['ok' => true, 'message' => 'Signed in successfully.'];
    } catch (Throwable) {
        return ['ok' => false, 'message' => 'Could not sign in. Please try again.'];
    }
}

function logout_user(array $data): array
{
    if (!verify_csrf($data['csrf_token'] ?? null)) {
        return ['ok' => false, 'message' => 'Invalid security token.'];
    }

    $_SESSION = [];

    if (ini_get('session.use_cookies')) {
        $params = session_get_cookie_params();
        setcookie(
            session_name(),
            '',
            time() - 42000,
            $params['path'],
            $params['domain'],
            $params['secure'],
            $params['httponly']
        );
    }

    session_destroy();
    flash('success', 'You are signed out.');
    return ['ok' => true, 'message' => 'Signed out.'];
}
