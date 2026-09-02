<?php
declare(strict_types=1);

define('APP_ROOT', dirname(__FILE__));
define('DATA_DIR', APP_ROOT . DIRECTORY_SEPARATOR . 'data');
define('DB_PATH', DATA_DIR . DIRECTORY_SEPARATOR . 'myavatar.sqlite');

define('PUBLIC_DIR', APP_ROOT . DIRECTORY_SEPARATOR . 'public');
define('UPLOAD_TMP_DIR', PUBLIC_DIR . DIRECTORY_SEPARATOR . 'uploads');
define('AVATAR_DIR', PUBLIC_DIR . DIRECTORY_SEPARATOR . 'avatars');
define('AVATAR_VALIDATOR_PATH', '/usr/local/bin/avatar-validator');

define('MAX_AVATAR_SIZE', 5 * 1024 * 1024);
define('MAX_AVATAR_WIDTH', 512);
define('MAX_AVATAR_HEIGHT', 512);
define('MIN_AVATAR_WIDTH', 64);
define('MIN_AVATAR_HEIGHT', 64);

define('WATERMARK_TEXT', 'MyAvatar App');
define('WATERMARK_MARGIN', 14);
define('WATERMARK_ALPHA', 60);

$isSecureRequest = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off')
    || (isset($_SERVER['SERVER_PORT']) && $_SERVER['SERVER_PORT'] === '443');

if (PHP_VERSION_ID >= 70300) {
    session_set_cookie_params([
        'lifetime' => 0,
        'path' => '/',
        'httponly' => true,
        'samesite' => 'Lax',
        'secure' => $isSecureRequest,
    ]);
} else {
    session_set_cookie_params(0, '/; samesite=Lax', '', $isSecureRequest, true);
}

if (session_status() !== PHP_SESSION_ACTIVE) {
    session_start();
}

foreach ([DATA_DIR, UPLOAD_TMP_DIR, AVATAR_DIR] as $directory) {
    if (!is_dir($directory)) {
        mkdir($directory, 0755, true);
    }
}
