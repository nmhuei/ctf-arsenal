<?php
declare(strict_types=1);

require_once __DIR__ . '/../config.php';
require_once __DIR__ . '/../includes/functions.php';
require_once __DIR__ . '/../db.php';
require_once __DIR__ . '/../auth.php';
require_once __DIR__ . '/../upload.php';

header('Content-Type: application/json; charset=UTF-8');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');

$pdo = get_db();

function api_payload(PDO $pdo, bool $ok = true, string $message = ''): array
{
    $user = get_current_user_record($pdo);
    $avatars = [];
    $tones = ['#ff5ab7', '#d9ff43', '#ff804f', '#48d8ff'];
    $accents = ['#6629ff', '#008f7a', '#ff2e72', '#0068ff'];

    if ($user) {
        foreach (get_user_avatars($pdo, (int)$user['id']) as $index => $avatar) {
            $imageFile = preg_replace('#^avatars/#', '', (string)$avatar['file_path']);
            $createdAt = strtotime((string)$avatar['created_at']);
            $avatars[] = [
                'id' => (int)$avatar['id'],
                'name' => (string)$avatar['original_name'],
                'date' => $createdAt ? strtoupper(date('M d, H:i', $createdAt)) : 'ARCHIVED',
                'tone' => $tones[$index % count($tones)],
                'accent' => $accents[$index % count($accents)],
                'image' => '/image.php?file=' . rawurlencode((string)$imageFile),
            ];
        }
    }

    return [
        'ok' => $ok,
        'message' => $message,
        'csrf' => session_status() === PHP_SESSION_ACTIVE ? csrf_token() : '',
        'user' => $user ? [
            'id' => (int)$user['id'],
            'username' => (string)$user['username'],
            'email' => (string)$user['email'],
        ] : null,
        'avatars' => $avatars,
    ];
}

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    echo json_encode(api_payload($pdo), JSON_UNESCAPED_SLASHES);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    header('Allow: GET, POST');
    echo json_encode(api_payload($pdo, false, 'Method not allowed.'), JSON_UNESCAPED_SLASHES);
    exit;
}

$action = sanitize_text($_POST['action'] ?? null);
$result = match ($action) {
    'signup' => register_user($pdo, $_POST),
    'login' => login_user($pdo, $_POST),
    'upload' => process_avatar_upload($pdo, $_FILES, $_POST),
    'logout' => logout_user($_POST),
    default => ['ok' => false, 'message' => 'Unknown action.'],
};

consume_flash();

if (!$result['ok']) {
    http_response_code($action === 'upload' && !is_logged_in() ? 401 : 400);
}

echo json_encode(
    api_payload($pdo, (bool)$result['ok'], (string)$result['message']),
    JSON_UNESCAPED_SLASHES
);
