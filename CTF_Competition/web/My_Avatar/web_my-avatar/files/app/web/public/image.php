<?php
declare(strict_types=1);

require_once __DIR__ . '/../config.php';
require_once __DIR__ . '/../includes/functions.php';
require_once __DIR__ . '/../db.php';

function redirect_avatar_read_failure(string $flashCode): never
{
    header('Cache-Control: no-store');
    header('Location: /?flash=' . rawurlencode($flashCode), true, 303);
    exit;
}

$requested = isset($_GET['file']) ? (string)$_GET['file'] : '';
$userId = current_user_id();

if ($userId === null) {
    redirect_avatar_read_failure('sign-in-required');
}

$stmt = get_db()->prepare(
    'SELECT id, file_path
     FROM avatars
     WHERE user_id = :user_id AND file_path = :file_path
     LIMIT 1'
);
$stmt->execute([
    ':user_id' => $userId,
    ':file_path' => 'avatars/' . ltrim($requested, '/'),
]);
$avatar = $stmt->fetch();

if (!$avatar) {
    redirect_avatar_read_failure('avatar-unavailable');
}

$storedFile = preg_replace('#^avatars/#', '', (string)$avatar['file_path']);
$avatarRoot = realpath(AVATAR_DIR);
$imagePath = is_string($storedFile) && $storedFile !== ''
    ? realpath(AVATAR_DIR . DIRECTORY_SEPARATOR . $storedFile)
    : false;

if (
    $avatarRoot === false
    || $imagePath === false
    || !is_file($imagePath)
    || !str_starts_with($imagePath, $avatarRoot . DIRECTORY_SEPARATOR)
) {
    redirect_avatar_read_failure('avatar-unavailable');
}

$mime = (new finfo(FILEINFO_MIME_TYPE))->file($imagePath);
if (!is_string($mime) || !str_starts_with($mime, 'image/')) {
    redirect_avatar_read_failure('avatar-unavailable');
}

header('Content-Type: ' . $mime);
header('Cache-Control: no-store');

include $imagePath;
