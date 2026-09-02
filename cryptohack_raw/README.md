# CryptoHack Challenge Downloader

Downloader nay dung CloakBrowser de mo cac trang challenge cua CryptoHack, luu de bai va tai cac file dinh kem ve may.

## Cai dat

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Lan dau chay, CloakBrowser se tu tai Chromium binary rieng cua no.

## Chay

```bash
python download_cryptohack.py
```

Mac dinh output nam trong `cryptohack_challenges/`, cau truc:

```text
cryptohack_challenges/
  index.json
  general/
    category.json
    encoding/
      ascii/
        statement.html
        statement.md
        metadata.json
        files/
```

Mot vai tuy chon huu ich:

```bash
python download_cryptohack.py --output out --headed
python download_cryptohack.py --limit-categories 1 --limit-challenges 3
python download_cryptohack.py --delay 0.7
python download_cryptohack.py --headed --login-wait
```

Neu muon dung session da login, chay `--headed --login-wait`, dang nhap trong cua so browser, roi quay lai terminal bam Enter. Script van tai duoc de bai cong khai khi khong login.

## Quan ly flag da solve

Dung `manage_flags.py` de xem bai nao solved/chua solved va luu flag offline. Script doc dataset trong `cryptohack_challenges/` va luu trang thai rieng vao `cryptohack_flags.json`.

```bash
python manage_flags.py stats
python manage_flags.py stats --category aes
python manage_flags.py list --category aes --status unsolved
python manage_flags.py list --status solved --show-flag
python manage_flags.py set aes0 'crypto{...}' --note 'ghi chu cach giai'
python manage_flags.py unset aes0 --clear-flag
python manage_flags.py show aes0
```

Tham so challenge co the la key day du, `data_challenge` nhu `aes0`, title, hoac mot substring duy nhat.

## Dang ky/dang nhap va submit flag len CryptoHack

Dung `cryptohack_account.py` de tao session account CryptoHack. Tool se mo browser cho ban tu dang ky/dang nhap, sau do luu cookie/session vao `.cryptohack_session.json`.

```bash
python cryptohack_account.py register
python cryptohack_account.py login
python cryptohack_account.py check
```

Submit mot flag truc tiep:

```bash
python cryptohack_account.py submit aes0 'crypto{...}'
```

Hoac luu flag vao state local truoc, roi submit bang account da login:

```bash
python manage_flags.py set aes0 'crypto{...}'
python cryptohack_account.py submit aes0
```

Submit tat ca flag da luu local:

```bash
python cryptohack_account.py submit-solved --yes
```

Mac dinh tool chi thao tac tren mot session/account trong `.cryptohack_session.json`. Neu muon tach account, dung `--session path/to/session.json`.

## Nen moi challenge thanh zip

Tao file zip theo ten challenge ngay trong moi thu muc challenge, gom de bai va file dinh kem:

```bash
python package_challenges.py
```

Vi du `great-snakes/great-snakes.zip`. Moi zip gom `README.txt`, `statement.md`, `statement.html`, `metadata.json`, va `files/` neu challenge co attachment.

Neu muon gom zip ra mot thu muc rieng:

```bash
python package_challenges.py --output cryptohack_challenges/_zips
```
