<?php
declare(strict_types=1);

require_once __DIR__ . '/../config.php';
require_once __DIR__ . '/../includes/functions.php';
require_once __DIR__ . '/../db.php';
require_once __DIR__ . '/../auth.php';
require_once __DIR__ . '/../upload.php';

$pdo = get_db();
$user = get_current_user_record($pdo);

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = sanitize_text($_POST['action'] ?? null);

    $result = ['ok' => false, 'message' => 'Unknown action.'];

    if ($action === 'signup') {
        $result = register_user($pdo, $_POST);
        if (!$result['ok']) {
            flash('error', $result['message']);
        }
        redirect($result['ok'] ? '?action=dashboard' : '?action=register');
    }

    if ($action === 'login') {
        $result = login_user($pdo, $_POST);
        if (!$result['ok']) {
            flash('error', $result['message']);
        }
        redirect($result['ok'] ? '?action=dashboard' : '?action=login');
    }

    if ($action === 'upload') {
        $result = process_avatar_upload($pdo, $_FILES, $_POST);
        if (!$result['ok']) {
            flash('error', $result['message']);
        }
        redirect('?action=dashboard');
    }

    if ($action === 'logout') {
        $result = logout_user($_POST);
        if (!$result['ok']) {
            flash('error', $result['message']);
        }
        redirect('?action=login');
    }

    flash('error', $result['message']);
    redirect('?action=dashboard');
}

$action = sanitize_text($_GET['action'] ?? null);
if ($action === '') {
    $action = $user ? 'dashboard' : 'login';
}

if (in_array($action, ['login', 'register'], true) && $user) {
    redirect('?action=dashboard');
}

if ($action === 'dashboard' && !$user) {
    flash('error', 'Sign in to access your dashboard.');
    redirect('?action=login');
}

if (!in_array($action, ['login', 'register', 'dashboard'], true)) {
    $action = 'login';
}

$flash = consume_flash();
$avatars = [];
if ($action === 'dashboard' && $user) {
    $avatars = get_user_avatars($pdo, (int)$user['id']);
}
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MyAvatar — Identity Foundry</title>
    <meta name="color-scheme" content="dark">
    <link rel="stylesheet" href="/style.php">
</head>
<body>
    <div class="runway" aria-hidden="true"></div>
    <div class="solids" aria-hidden="true">
        <div class="solid solid-a">
            <span class="face f1"></span><span class="face f2"></span><span class="face f3"></span>
            <span class="face f4"></span><span class="face f5"></span><span class="face f6"></span>
        </div>
        <div class="solid solid-b">
            <span class="face f1"></span><span class="face f2"></span><span class="face f3"></span>
            <span class="face f4"></span><span class="face f5"></span><span class="face f6"></span>
        </div>
        <div class="solid solid-c">
            <span class="face f1"></span><span class="face f2"></span><span class="face f3"></span>
            <span class="face f4"></span><span class="face f5"></span><span class="face f6"></span>
        </div>
    </div>

    <div class="wrap">
        <header class="header">
            <p class="eyebrow">Identity Foundry</p>
            <h1 class="wordmark" data-text="MyAvatar">MyAvatar</h1>
            <p class="tagline">Upload an image and get it back <strong>watermarked</strong>, minted into your own collection of avatars.</p>
        </header>

        <?php if ($flash): ?>
            <div class="flash flash-<?php echo h($flash['type']); ?>">
                <?php echo h((string)$flash['message']); ?>
            </div>
        <?php endif; ?>

        <?php if ($action === 'dashboard'): ?>
            <section class="panel">
                <div class="topline">
                    <p>Signed in as <strong><?php echo h((string)$user['username']); ?></strong></p>
                    <form method="post" action="">
                        <?php echo csrf_field(); ?>
                        <input type="hidden" name="action" value="logout">
                        <button type="submit" class="btn btn-danger">Sign out</button>
                    </form>
                </div>

                <h2>Upload avatar</h2>
                <form class="upload-form" method="post" action="" enctype="multipart/form-data">
                    <?php echo csrf_field(); ?>
                    <input type="hidden" name="action" value="upload">
                    <label for="avatar">AVIF image, up to 5 MB</label>
                    <input id="avatar" name="avatar" type="file" accept="image/avif,.avif" required>
                    <button class="btn" type="submit">Upload</button>
                </form>

                <h2>Your collection</h2>
                <?php if (!$avatars): ?>
                    <div class="empty">
                        <strong>Nothing minted yet</strong>
                        <p class="muted">Upload an AVIF above to add your first avatar.</p>
                    </div>
                <?php else: ?>
                    <div class="avatar-grid">
                        <?php foreach ($avatars as $avatar): ?>
                            <?php $imageFile = preg_replace('#^avatars/#', '', (string)$avatar['file_path']); ?>
                            <article class="avatar-item">
                                <img src="<?php echo h('/image.php?file=' . rawurlencode((string)$imageFile)); ?>" alt="Avatar">
                                <p><?php echo h((string)$avatar['original_name']); ?></p>
                            </article>
                        <?php endforeach; ?>
                    </div>
                <?php endif; ?>
            </section>
        <?php endif; ?>

        <?php if ($action === 'login'): ?>
            <section class="panel panel-auth">
                <h2>Sign in</h2>
                <form method="post" action="">
                    <?php echo csrf_field(); ?>
                    <input type="hidden" name="action" value="login">
                    <label for="identity">Username or email</label>
                    <input id="identity" name="identity" type="text" autocomplete="username" required>
                    <label for="login-password">Password</label>
                    <input id="login-password" name="password" type="password" autocomplete="current-password" required>
                    <button class="btn" type="submit">Sign in</button>
                </form>
                <p class="muted switch">New here? <a href="?action=register">Create an account</a></p>
            </section>
        <?php endif; ?>

        <?php if ($action === 'register'): ?>
            <section class="panel panel-auth">
                <h2>Create account</h2>
                <form method="post" action="">
                    <?php echo csrf_field(); ?>
                    <input type="hidden" name="action" value="signup">
                    <label for="username">Username</label>
                    <input id="username" name="username" type="text" autocomplete="username" required>
                    <label for="email">Email</label>
                    <input id="email" name="email" type="email" autocomplete="email" required>
                    <label for="password">Password, at least 8 characters</label>
                    <input id="password" name="password" type="password" autocomplete="new-password" required>
                    <label for="confirm_password">Confirm password</label>
                    <input id="confirm_password" name="confirm_password" type="password" autocomplete="new-password" required>
                    <button class="btn" type="submit">Create account</button>
                </form>
                <p class="muted switch">Already have an account? <a href="?action=login">Sign in</a></p>
            </section>
        <?php endif; ?>
    </div>

    <script>
    (function () {
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
        if (window.matchMedia('(max-width: 720px)').matches) return;

        var scene = document.querySelector('.wrap');
        var cards = document.querySelectorAll('.avatar-item');
        var frame = 0;

        function clamp(n) { return n < -1 ? -1 : (n > 1 ? 1 : n); }

        function onMove(e) {
            if (frame) return;
            frame = requestAnimationFrame(function () {
                frame = 0;
                var px = (e.clientX / window.innerWidth) * 2 - 1;
                var py = (e.clientY / window.innerHeight) * 2 - 1;
                scene.style.setProperty('--px', px.toFixed(3));
                scene.style.setProperty('--py', py.toFixed(3));

                cards.forEach(function (card) {
                    var r = card.getBoundingClientRect();
                    card.style.setProperty('--cx', clamp(((e.clientX - r.left) / r.width) * 2 - 1).toFixed(3));
                    card.style.setProperty('--cy', clamp(((e.clientY - r.top) / r.height) * 2 - 1).toFixed(3));
                });
            });
        }

        window.addEventListener('pointermove', onMove, { passive: true });
    })();
    </script>
</body>
</html>
