<?php
declare(strict_types=1);

require_once __DIR__ . '/db.php';
require_once __DIR__ . '/includes/functions.php';

function avatar_passes_decode_limits(string $path): bool
{
    $process = @proc_open(
        [AVATAR_VALIDATOR_PATH, $path],
        [
            0 => ['file', '/dev/null', 'r'],
            1 => ['file', '/dev/null', 'w'],
            2 => ['file', '/dev/null', 'w'],
        ],
        $pipes
    );

    return is_resource($process) && proc_close($process) === 0;
}

function process_avatar_upload(PDO $pdo, array $files, array $post): array
{
    $userId = current_user_id();
    if ($userId === null) {
        return ['ok' => false, 'message' => 'Sign in is required to upload avatars.'];
    }

    if (!verify_csrf($post['csrf_token'] ?? null)) {
        return ['ok' => false, 'message' => 'Invalid security token.'];
    }

    if (!isset($files['avatar'])) {
        return ['ok' => false, 'message' => 'No file was uploaded.'];
    }

    $upload = $files['avatar'];
    if (!is_array($upload) || !isset($upload['error'], $upload['tmp_name'], $upload['size'], $upload['name'])) {
        return ['ok' => false, 'message' => 'Invalid upload payload.'];
    }

    if ((int)$upload['error'] !== UPLOAD_ERR_OK) {
        return ['ok' => false, 'message' => 'Upload failed.'];
    }

    if ((int)$upload['size'] > MAX_AVATAR_SIZE) {
        return ['ok' => false, 'message' => 'File is larger than 5 MB limit.'];
    }

    if (!is_uploaded_file($upload['tmp_name'])) {
        return ['ok' => false, 'message' => 'File source is invalid.'];
    }

    $imageInfo = @getimagesize($upload['tmp_name']);
    if ($imageInfo === false) {
        return ['ok' => false, 'message' => 'Only image files can be uploaded.'];
    }

    $mime = (string)($imageInfo['mime'] ?? '');

    if ($mime !== 'image/avif') {
        return ['ok' => false, 'message' => 'Only AVIF images are accepted.'];
    }

    if (!function_exists('imagecreatefromavif') || !function_exists('imageavif')) {
        return ['ok' => false, 'message' => 'AVIF image processing is unavailable.'];
    }

    if (!avatar_passes_decode_limits($upload['tmp_name'])) {
        return ['ok' => false, 'message' => 'Could not read image.'];
    }

    $loader = 'imagecreatefromavif';
    $saver = 'imageavif';

    try {
        $source = $loader($upload['tmp_name']);
        if (!$source instanceof GdImage && !is_resource($source)) {
            return ['ok' => false, 'message' => 'Could not read image.'];
        }

        $width = imagesx($source);
        $height = imagesy($source);

        if ($width < MIN_AVATAR_WIDTH || $height < MIN_AVATAR_HEIGHT) {
            imagedestroy($source);
            return ['ok' => false, 'message' => 'Image must be at least 64x64 pixels.'];
        }

        if ($width > MAX_AVATAR_WIDTH || $height > MAX_AVATAR_HEIGHT) {
            imagedestroy($source);
            return ['ok' => false, 'message' => 'Image dimensions must not exceed 512x512 pixels.'];
        }

        $text = WATERMARK_TEXT;
        $font = 5;
        $fontWidth = imagefontwidth($font);
        $textLength = strlen($text);
        $textWidth = $fontWidth * $textLength;
        $textHeight = imagefontheight(5);
        $x = max(WATERMARK_MARGIN, $width - $textWidth - WATERMARK_MARGIN);
        $y = max(WATERMARK_MARGIN, $height - $textHeight - WATERMARK_MARGIN);

        $gradientStart = [random_int(0, 255), random_int(0, 255), random_int(0, 255)];
        $gradientEnd = [random_int(0, 255), random_int(0, 255), random_int(0, 255)];

        for ($i = 0; $i < $textLength; $i++) {
            $ratio = $textLength > 1 ? $i / ($textLength - 1) : 0;
            $textColor = imagecolorallocatealpha(
                $source,
                (int)round($gradientStart[0] + (($gradientEnd[0] - $gradientStart[0]) * $ratio)),
                (int)round($gradientStart[1] + (($gradientEnd[1] - $gradientStart[1]) * $ratio)),
                (int)round($gradientStart[2] + (($gradientEnd[2] - $gradientStart[2]) * $ratio)),
                WATERMARK_ALPHA
            );

            imagestring($source, $font, $x + ($fontWidth * $i), $y, $text[$i], $textColor);
        }

        $userDir = AVATAR_DIR . DIRECTORY_SEPARATOR . $userId;
        if (!is_dir($userDir)) {
            mkdir($userDir, 0755, true);
        }

        $filename = bin2hex(random_bytes(16)) . '.avif';
        $relativePath = 'avatars/' . $userId . '/' . $filename;
        $absolutePath = AVATAR_DIR . DIRECTORY_SEPARATOR . $userId . DIRECTORY_SEPARATOR . $filename;

        $saved = $saver($source, $absolutePath, 85);

        if (!$saved) {
            imagedestroy($source);
            return ['ok' => false, 'message' => 'Could not save image.'];
        }

        imagedestroy($source);

        $insert = $pdo->prepare(
            'INSERT INTO avatars (user_id, file_path, original_name)
             VALUES (:user_id, :file_path, :original_name)'
        );
        $insert->execute([
            ':user_id' => $userId,
            ':file_path' => $relativePath,
            ':original_name' => sanitize_text($upload['name']),
        ]);

        flash('success', 'Avatar uploaded and watermarked.');
        return ['ok' => true, 'message' => 'Avatar uploaded.'];
    } catch (Throwable) {
        return ['ok' => false, 'message' => 'Could not process upload.'];
    }
}
