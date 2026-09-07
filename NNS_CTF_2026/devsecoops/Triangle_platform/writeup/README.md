# Phân Tích & Tư Duy Giải Bài: Triangle platform (devsecoops)

---

## 1. Mô Hình Kiến Trúc & Bề Mặt Tấn Công (Mental Model)

Thử thách mô phỏng một nền tảng điện toán đám mây PaaS (Platform as a Service) chạy trên Kubernetes, cho phép người dùng triển khai các trang tĩnh (static sites) thông qua hai Custom Resource Definition (CRD): `Site` và `Domain`.

Hệ thống được thiết kế theo mô hình đa người thuê (Multi-tenancy):
- **Phía Người Dùng (Attacker)**: Được cấp quyền trong namespace `tenant-a` với ServiceAccount `console`. Quyền của `console` bị giới hạn nghiêm ngặt (chỉ được tạo và quản lý `Site`, không được can thiệp vào `Secret`, `Pod` hay các namespace khác).
- **Mục Tiêu Nhạy Cảm**: Nằm ở namespace hệ thống `triangle-origins`, chứa Secret `origin-acme-invoices.sites.triangle.tld` lưu trữ chuỗi bí mật `FLAG`. Namespace `tenant-b` sở hữu domain hợp pháp `acme-invoices.sites.triangle.tld`.
- **Cơ Chế Kiểm Soát & Điều Phối**:
  1. **Kyverno Admission Controller**: Đóng vai trò tường lửa chính sách (Policy Enforcement), chặn đứng người dùng thông thường kích hoạt các integration nhạy cảm (đặc biệt là `edge`).
  2. **Triangle Operator**: Viết bằng ngôn ngữ Go (`controller-runtime`), lắng nghe các sự kiện tạo/sửa `Site` và `Domain` để render ConfigMap, Deployment và Service tương ứng.

**Mục tiêu bài toán**: Leo thang đặc quyền từ một người thuê bị cô lập (`tenant-a`), đánh lừa bộ điều khiển để trích xuất Secret nhạy cảm từ namespace hệ thống `triangle-origins`.

---

## 2. Chuỗi Lỗ Hổng Đa Tầng (The Multi-Stage Flaws)

Để đánh sập hoàn toàn ranh giới cách ly của hệ thống, ta cần kết hợp 4 điểm yếu thiết kế phân bổ ở các tầng khác nhau:

```text
[Kyverno Policy Check]
       │ (1. YAML Parser Differential: <<: *allowed qua mặt Kyverno)
       ▼
[Go Operator Reconciliation]
       │ (Nhận diện integration "edge" hợp lệ)
       ▼
[Pod Projected Token]
       │ (2. Audience Escalation: target: null cấp Token cho Cluster API)
       ▼
[K8s ServiceAccount Elevation]
       │ (Tạo Secret token cho tri-registry-sync để có quyền ghi Domain)
       ▼
[Domain Controller Logic]
       │ (3. Host Case Desync: "ACME-..." qua mặt contested() nhưng match Secret)
       ▼
[Origin Secret Sync & Nginx Serve]
       │ (4. Operator copy Secret sang tenant-a -> Mount /var/run/origin -> Đọc FLAG)
       ▼
[FLAG EXFILTRATED]
```

---

### Lỗ Hổng 1: Sai Lệch Phân Tích Cú Pháp YAML (YAML Parser Differential)
- **Bản chất**: Kyverno và Go Operator sử dụng hai thư viện phân tích cú pháp YAML hoàn toàn khác nhau:
  - Kyverno sử dụng `sigs.k8s.io/yaml` (go-yaml v2), rồi chuyển đổi cấu trúc YAML sang JSON để xác thực.
  - Triangle Operator viết bằng Go sử dụng `gopkg.in/yaml.v3` và giữ các `yaml.Node` để giải mã cấu hình sau đó.
- **Điểm mù**:
  - Chính sách Kyverno cấm trường `integrations` chứa phần tử mang tên `edge`.
  - Khi ta khai báo một cấu trúc lồng ghép sử dụng merge key:
    - Định nghĩa một anchor hợp lệ: `allowed: &allowed integrations: [forms]`.
    - Khai báo tường minh: `integrations: [edge]`.
    - Chèn merge key ngay sau: `<<: *allowed`.
  - Bộ parser của Kyverno khi chuyển đổi sang JSON bị ghi đè key, chỉ nhìn thấy `integrations: [forms]` nên cho phép tài nguyên đi qua.
  - Bộ parser `yaml.v3` của Go Operator lại ưu tiên giá trị được định nghĩa tường minh trên cùng một cấp, giữ nguyên `integrations: [edge]`.
- **Hệ quả**: Ta kích hoạt thành công ServiceAccount `tri-edge` trên Pod mà không bị Kyverno phát hiện.

---

### Lỗ Hổng 2: Leo Thang Đặc Quyền Token API Server (`target: null`)
- **Bản chất**: Cấu hình trang cho phép khai báo trường `target` để chỉ định đối tượng phục vụ (`Audience`) cho Projected ServiceAccount Token gắn vào container.
- **Điểm mù**:
  - Khi người dùng cung cấp một chuỗi ký tự, token sinh ra bị giới hạn audience cho dịch vụ đó.
  - Khi người dùng cung cấp giá trị rỗng/null (`target: null`), toán tử Go bỏ qua thiết lập audience.
  - Theo cơ chế mặc định của Kubernetes TokenRequest API, một token không yêu cầu audience cụ thể sẽ được gán mặc định audience của Kubernetes API Server trong cụm.
- **Hệ quả**: Token được mount tại `/var/run/triangle/token` trong container `tri-edge` có khả năng xác thực trực tiếp và gọi các API quản trị nội bộ của Kubernetes.

---

### Lỗ Hổng 3: Bất Đối Xứng Chuẩn Hóa Host (Domain Case Desync)
- **Bản chất**: Hệ thống hỗ trợ sao chép cấu hình gốc (Origin Config) từ Secret thuộc namespace `triangle-origins` sang namespace của trang nếu trang đó sở hữu tên miền tương ứng.
- **Điểm mù**:
  - Hàm kiểm tra tranh chấp tên miền `contested()` trong Operator kiểm tra xem tên miền đã bị chiếm giữ bởi người khác chưa bằng cách so sánh trực tiếp hai chuỗi thô:
    $$c_1.\text{host} == c_2.\text{host}$$
  - Trong khi đó, hàm đồng bộ Secret `syncOriginConfig()` lại sử dụng hàm chuẩn hóa `canonicalHost()` để chuyển host về chữ thường (`strings.ToLower`, đồng thời cắt dấu chấm cuối).
  - Tên miền hợp pháp của tổ chức khác là `acme-invoices.sites.triangle.tld` (không có dấu chấm cuối).
  - CRD không bắt buộc host phải là chữ thường. Nếu ta đăng ký `ACME-invoices.sites.triangle.tld`:
    - Hàm `contested()` so sánh chuỗi thô nên không thấy trùng với host chữ thường của tenant-b.
    - Hàm `syncOriginConfig()` chuyển về chữ thường, tìm thấy Secret nguồn `origin-acme-invoices.sites.triangle.tld` trong namespace hệ thống và sao chép thẳng toàn bộ nội dung sang namespace `tenant-a` dưới tên `<site-name>-origin`.

---

### Lỗ Hổng 4: Trích Xuất Secret Qua File Server Nginx
- **Bản chất**: Khi một trang có Secret cấu hình gốc gắn kèm, Operator tự động mount Secret này vào đường dẫn hệ thống `/var/run/origin` bên trong container Nginx.
- **Điểm mù**:
  - Secret `origin-acme-invoices.sites.triangle.tld` chứa key có tên `FLAG`.
  - Cấu hình trang cho phép người dùng tùy biến thư mục gốc (`root`) và tệp chỉ mục (`index`) của Nginx.
  - Chỉ cần cập nhật cấu hình Nginx trỏ `root: /var/run/origin` và `index: FLAG`, toàn bộ nội dung Flag bí mật sẽ được phơi bày trực tiếp qua Service HTTP Proxy của Kubernetes.

---

## 3. Luồng Tư Duy Khai Thác (The Attack Flow)

Luồng tư duy thực hiện tuần tự qua 5 bước logic:

1. **Khởi tạo Site vượt rào (Bypass Policy & Spawn Privileged Pod):**
   - Tạo một tài nguyên `Site` trong `tenant-a` với cấu hình YAML lợi dụng parser differential giữa Kyverno và Go `yaml.v3`.
   - Thiết lập `target: null` và trỏ thư mục Nginx tới `/var/run/triangle` với file index `token`.
   - Chờ Deployment khởi tạo hoàn tất, sau đó đọc nội dung token của `tri-edge` thông qua Kubernetes Service Proxy.

2. **Leo thang quyền ghi Domain (Registry Token Elevation):**
   - ServiceAccount `tri-edge` có quyền tạo Secret loại ServiceAccountToken trong namespace `triangle-system`.
   - Sử dụng token `tri-edge` gửi request tạo Secret gắn với ServiceAccount `tri-registry-sync` (tài khoản có quyền ghi CRD `Domain` trên phạm vi toàn cụm).
   - Đọc ngược lại token vừa được controller sinh ra trong Secret.

3. **Chiếm dụng bí mật tên miền (Case-Variant Domain Hijacking):**
   - Sử dụng token của `tri-registry-sync` để tạo một tài nguyên `Domain` mới liên kết với Site của ta.
   - Thiết lập host dạng chữ hoa: `ACME-invoices.sites.triangle.tld`.
   - Operator phát hiện domain mới, kiểm tra `contested()` thấy hợp lệ, chuẩn hóa host khi tra cứu, rồi tự động nhân bản Secret chứa flag từ `triangle-origins` sang Secret `<site-name>-origin` trong namespace `tenant-a`.

4. **Khai thác tệp dữ liệu đã mount (Exfiltrate Flag):**
   - Patch cấu hình `Site` chuyển Nginx sang trỏ tới thư mục `/var/run/origin` và index `FLAG`.
   - Gửi yêu cầu HTTP GET thông qua Kubernetes Service Proxy tại cổng 80 tới endpoint `/proxy/FLAG`.
   - Bắt trọn vẹn nội dung cờ trả về trong phần thân phản hồi.

---

## 4. Flag & Ý Nghĩa Thiết Kế

- **Flag thu được**:
  ```text
  NNS{MiNN_be5t3_veNN,_I_tH1Nk_that_I_migHt_h4V3_4_kyVern0_aDd1ct10N_Bu7_somehoW_tH3r3_1s_No_W4Y_t0_35c4pe_7H3_yam1_FUCk3RY}
  ```

- **Bài học & Khuyến nghị DevSecOps**:
  - **Sự nguy hiểm của Parser Differential**: Không bao giờ sử dụng hai bộ thư viện phân tích cú pháp khác nhau giữa thành phần kiểm soát chính sách (Admission Webhook) và thành phần thực thi nghiệp vụ (Operator/Controller). Khi có sự sai lệch trong việc xử lý các tính năng mở rộng của YAML (như anchors, merge keys), chính sách bảo vệ hoàn toàn bị vô hiệu hóa.
  - **Cẩn trọng với Projected Token Audience**: Khi triển khai tính năng cấp ServiceAccount Token tự động, luôn bắt buộc kiểm tra và giới hạn chặt chẽ danh sách Audience cho phép, tuyệt đối không cho phép giá trị rỗng/null rơi về Audience mặc định của cụm.
  - **Chuẩn hóa dữ liệu đầu vào (Input Canonicalization) đồng nhất**: Mọi thao tác kiểm tra tính duy nhất (Uniqueness/Contention check) và thao tác tra cứu tài nguyên (Resource lookup) phải luôn thực thi trên cùng một dạng chuẩn hóa (Canonical form) của dữ liệu.
