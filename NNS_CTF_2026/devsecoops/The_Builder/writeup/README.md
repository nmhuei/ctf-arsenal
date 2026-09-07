# Phân Tích & Tư Duy Giải Bài: The Builder (devsecoops)

---

## 1. Mô Hình Kiến Trúc & Bề Mặt Tấn Công (Mental Model)

Thử thách triển khai một dịch vụ tự động dựng trang web tĩnh (Site Builder CI/CD Pipeline):
- **Web Interface / API**: Cung cấp endpoint `POST /api/builds` nhận các trường `location` (đường dẫn lưu trữ) và `content` (nội dung trang tĩnh). Sau khi gửi, server sinh mã `build-id` và cho phép theo dõi log qua `GET /builds/<id>`.
- **Hệ Thống Dựng Tự Động (Docker / BuildKit)**:
  - Dựa trên dữ liệu người dùng, hệ thống sinh ra một `Dockerfile` đa tầng (Multi-stage build):
    - **Stage 1 (`theme`)**: Chạy từ image base của Debian, gắn bí mật build qua cờ `--mount=type=secret,id=flag` và sao chép bí mật vào `/flag.txt`. Ranh giới bảo mật dự kiến: secret chỉ tồn tại tạm thời trong stage này và không được truyền vào image cuối.
    - **Stage 2 (`contentN`)**: Nhập nội dung từng trang thông qua `FROM pageN AS contentN`. Tên `pageN` tương ứng với image có tag `pages:<sha256(content)[:12]>`.
    - **Stage 3 (`site`)**: Khởi tạo web server Nginx và thực hiện `COPY --from=contentN /page /usr/share/nginx/html/<location>`.
- **Private Docker Registry v2**:
  - Hệ thống tích hợp một Docker Registry nội bộ để lưu trữ các layer trung gian (`pages`) và image thành phẩm cuối cùng (`sites/<build-id>:latest`).

**Mục tiêu bài toán**: Phá vỡ ranh giới cách ly giữa các stage trong quy trình Multi-stage build của Docker để đánh cắp `/flag.txt` từ stage bí mật `theme`.

---

## 2. Bản Chất Lỗ Hổng & Điểm Mù Thiết Kế (Vulnerability Analysis)

Mô hình bảo vệ của hệ thống sụp đổ do sự kết hợp của 3 điểm yếu chí mạng:

```text
[Attacker]
    │
    │ (1. Đẩy trước OCI image chứa OnBuild trigger vào Registry)
    ▼
[Unauthenticated Registry v2]  ==> Lưu pages:<hash> với trigger:
                                   ONBUILD COPY --from=theme /flag.txt /page
    ▲
    │ (2. Gửi request build với content có cùng mã hash)
[Builder Pipeline]
    │
    ├── Stage 1: FROM debian AS theme (Gắn secret /flag.txt)
    │
    ├── Stage 2: FROM page0 (Kích hoạt ONBUILD trigger!)
    │            ==> Copy trộm /flag.txt từ stage theme vào /page!
    │
    └── Stage 3: FROM nginx AS site
                 ==> COPY --from=content0 /page ... (Đưa flag vào image cuối)
    │
    ▼
[Sites Registry Layer] ===> Attacker tải layer về giải nén đọc FLAG
```

---

### Lỗ Hổng 1: Docker Registry Hoàn Toàn Không Xác Thực (Unauthenticated Registry v2)
- Cổng dịch vụ Docker Registry v2 được mở công khai mà không yêu cầu bất kỳ cơ chế xác thực nào (Anonymous Read/Write).
- Bất kỳ ai cũng có quyền đẩy blob (tệp nén layer, tệp json cấu hình) và ký gửi manifest (`PUT /v2/<repo>/manifests/<tag>`) lên bất kỳ kho lưu trữ nào, kể cả kho lưu trữ hệ thống `pages`.

### Lỗ Hổng 2: Tính Xác Định Của Tag (Deterministic Hash Tagging)
- Tag của image chứa nội dung trang được tính toán bằng công thức:
  $$\text{tag} = \text{sha256}(\text{content})[:12]$$
- Do công thức hoàn toàn minh bạch và có tính xác định (deterministic), kẻ tấn công có thể chọn trước một chuỗi nội dung tùy ý (ví dụ: `x`), tính toán trước mã hash (ví dụ: `2d711642b726`), và chủ động đưa image độc hại lên registry trước khi kích hoạt tiến trình build trên server.
- Khi BuildKit thực hiện lệnh `FROM page0 AS content0`, nó tìm kiếm tag `pages:2d711642b726`. Do tag này đã tồn tại sẵn trên registry, BuildKit sẽ kéo image độc hại về sử dụng thay vì tự sinh mới.

### Lỗ Hổng 3: Khai Thác Chỉ Thị BuildKit ONBUILD (ONBUILD Trigger Hijacking)
- Trong định dạng OCI/Docker image, chỉ thị `ONBUILD` cho phép lưu các lệnh build vào metadata cấu hình của image (`container_config.OnBuild`). Các lệnh này không thực thi khi image được build lần đầu, mà sẽ **tự động được kích hoạt khi image đó đóng vai trò là Base Image (`FROM`) trong một lượt build khác**.
- Điểm mấu chốt: Trong cùng một tệp `Dockerfile`, các stage phía sau hoàn toàn có quyền tham chiếu ngược lại tài nguyên của các stage phía trước thông qua cờ `--from=<stage_name>`.
- Kẻ tấn công tạo ra một image `pages:2d711642b726` với metadata chứa trigger:
  ```json
  {"config": {"OnBuild": ["COPY --from=theme /flag.txt /page"]}}
  ```
- Khi BuildKit xử lý chỉ thị `FROM page0 AS content0`:
  1. BuildKit nhận diện được trigger `ONBUILD` kế thừa từ `page0`.
  2. Trigger được kích hoạt ngay lập tức trong ngữ cảnh của `Dockerfile`. Vì stage `theme` đã hoàn tất ở ngay trước đó và có chứa `/flag.txt`, lệnh sao chép thực hiện thành công và ghi đè `/flag.txt` vào tệp `/page` của `content0`.
  3. Đến stage cuối `site`, lệnh tiêu chuẩn `COPY --from=content0 /page /usr/share/nginx/html/...` sẽ đưa toàn bộ nội dung `/flag.txt` vào tệp phục vụ của web server và đóng gói vào image cuối cùng!

---

## 3. Luồng Tư Duy Khai Thác (The Attack Flow)

Luồng tấn công được thực hiện theo 4 bước bài bản:

1. **Chuẩn bị Payload OCI Image & Tính Hash:**
   - Chọn một chuỗi nội dung tĩnh đơn giản (ví dụ: `x`).
   - Tính toán 12 ký tự hex đầu của mã băm SHA-256 để xác định tag mục tiêu trên registry.
   - Xây dựng một OCI image hợp lệ gồm một layer chứa tệp giả lập `/page`, và đặc biệt tiêm cấu hình `OnBuild` với chỉ thị `COPY --from=theme /flag.txt /page`.

2. **Đầu độc Registry (Pre-seeding the Cache):**
   - Kết nối tới Docker Registry v2 của mục tiêu.
   - Khởi tạo phiên upload blob, đẩy layer dữ liệu tar.gz và tệp config JSON lên registry.
   - Đẩy OCI manifest liên kết config và layer vào repository `pages` với tag vừa tính toán.

3. **Kích hoạt Quy Trình Build:**
   - Gửi yêu cầu HTTP POST tới `/api/builds` với `content` trùng khớp với chuỗi đã chọn ở bước 1.
   - Hệ thống tiến hành build, kéo image `pages` đã bị đầu độc, kích hoạt trigger `ONBUILD` để trích xuất file bí mật từ stage `theme`, và đẩy image hoàn thiện lên kho lưu trữ `sites/<build-id>:latest`.

4. **Kéo Layer & Thu Hoạch Flag:**
   - Truy vấn registry để lấy manifest của image `sites/<build-id>:latest`.
   - Tải về các layer của image thành phẩm.
   - Giải nén các layer tarball cục bộ và tìm kiếm định dạng cờ `NNS{...}` nằm trong tệp tin được xuất ra.

---

## 4. Flag & Ý Nghĩa Thiết Kế

- **Flag thu được**:
  ```text
  NNS{who_tHough7_7h47_7his_tRi663R_w45_a_go0D_iD3a??_We1l_anyW4y5_Y0u_DiD_it}
  ```

- **Bài học & Khuyến nghị DevSecOps**:
  - **Kiểm soát truy cập Registry**: Docker Registry trong môi trường CI/CD bắt buộc phải cấu hình xác thực chặt chẽ (mTLS, Token-based Auth) và phân quyền chi tiết (RBAC). Tuyệt đối không cho phép quyền ghi ẩn danh (Anonymous Push).
  - **Nguy cơ tiềm ẩn từ ONBUILD**: Trình biên dịch Dockerfile cần vô hiệu hóa hoặc lọc bỏ các chỉ thị `ONBUILD` khi sử dụng các base image không rõ nguồn gốc hoặc do người dùng kiểm soát.
  - **Tính bất biến của Artifact**: Không bao giờ đặt niềm tin vào các image tag có thể dự đoán được (Deterministic tags). Cần áp dụng xác thực mã băm nội dung thực tế (Immutable Content Digest / Content Addressable Storage) thay vì chỉ tin cậy vào tên tag.
