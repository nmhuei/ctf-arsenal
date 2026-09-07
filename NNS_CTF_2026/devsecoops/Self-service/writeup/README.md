# Phân Tích & Tư Duy Giải Bài: Self-service (devsecoops)

---

## 1. Mô Hình Kiến Trúc & Giả Định Ban Đầu (Mental Model)

Khi bước vào bài toán, ta nhận được một tài khoản nhân viên hợp đồng (`contractor`):
- **User**: `ereid:Summer2026`
- **Cổng vào**: SSH over TLS tới máy nhảy trung gian (`jump`).

Từ máy `jump`, tiến hành quan sát sơ đồ mạng nội bộ (`/etc/hosts`) và phân tích ranh giới:
1. **`jump`**: Máy trạm trung gian (Debian). Cấu hình SSHD (`/etc/ssh/sshd_config.d/20-role.conf`) chỉ định rõ ràng: `DenyUsers ops`. Nghĩa là tài khoản dịch vụ vận hành `ops` tuyệt đối không được phép đăng nhập vào máy này.
2. **`dir`**: Máy chủ LDAP (`ldap://dir:3389`), giữ cơ sở dữ liệu xác thực tập trung cho toàn bộ tổ chức `dc=corp,dc=nns`.
3. **`srv2`**: Máy chủ dịch vụ đích. Khảo sát thông tin người dùng cho thấy:
   `ops:*:5010:5000:Operations service account (backup/restore on srv2):/home/ops:/bin/bash`
   -> `srv2` chính là máy đích mà chỉ tài khoản `ops` mới có quyền truy cập, và flag nằm tại `/home/ops/flag.txt` trên máy này.

**Mục tiêu tối hậu:** Đăng nhập vào `srv2` dưới danh nghĩa `ops`.  
**Nút thắt:** Ta không có mật khẩu của `ops`, và mật khẩu ban đầu của `ereid` không có quyền trên `srv2`.

---

## 2. Dò Xét Ranh Giới Phòng Thủ & Phân Tích ACI (Access Control Instructions)

Vì LDAP đóng vai trò trung tâm điều khiển danh tính và xác thực, toàn bộ chìa khóa của bài toán nằm ở các chỉ thị kiểm soát truy cập (ACI) trên OpenLDAP/389ds.

Bằng cách dump toàn bộ thuộc tính `aci`, ta bóc tách được các quy tắc bảo mật cốt lõi:

* **ACI 1 (Chuyển đổi nhân viên hợp đồng)**:
  `target_from = "ou=contractors", target_to = "ou=staff", allow (moddn) groupdn = "cn=onboarding-agents"`
  -> Người dùng thuộc `cn=onboarding-agents` có quyền chuyển đối tượng từ đơn vị nhân sự tạm thời sang biên chế chính thức (`ou=staff`). `ereid` đang nằm trong nhóm này.

* **ACI 2 (Sửa đổi thuộc tính định danh - Naming Attribute)**:
  `targetattr = "uid", targattrfilters = "add=uid:(!(uid=ops)), del=uid:(!(uid=ops))", allow (write) groupdn = "cn=onboarding-agents"`
  -> Nhóm `onboarding-agents` được cấp quyền ghi đè thuộc tính `uid` trên các đối tượng. Tác giả đã đặt một bộ lọc phòng thủ: *Không được phép gán hoặc xoá giá trị `uid=ops`*.

* **ACI 3 (Cấp quyền Helpdesk reset mật khẩu tài khoản dịch vụ)**:
  Trên entry `uid=ops,ou=staff,dc=corp,dc=nns`:
  `targetattr = "userPassword", allow (write) groupdn = "cn=helpdesk,ou=groups,dc=corp,dc=nns"`
  -> Chỉ có thành viên của nhóm `cn=helpdesk` mới được quyền đổi mật khẩu cho `ops`.

---

## 3. Lỗ Hổng Tư Duy Của Người Quản Trị & Điểm Gãy Bảo Mật

### A. Ranh giới giả tạo: "Blacklist" thay vì "Whitelist"
Người quản trị hệ thống đã nhận thức được rủi ro nếu `onboarding-agents` đổi tên tài khoản thành `ops`, nên đã thiết lập bộ lọc: `(!(uid=ops))`.  
Tuy nhiên, đây là tư duy **Blacklist điển hình**: họ chỉ chặn đúng tên `ops`, nhưng lại bỏ ngỏ việc đổi tên thành bất kỳ danh tính nào khác trong công ty.

### B. Vấn đề Stale Reference trong mô hình Group tĩnh (`groupOfNames`)
Kiểm tra cấu trúc của nhóm `cn=helpdesk`:
```text
dn: cn=helpdesk,ou=groups,dc=corp,dc=nns
objectClass: groupOfNames
member: uid=agrant,ou=staff,dc=corp,dc=nns
member: uid=cnovak,ou=staff,dc=corp,dc=nns
member: uid=pdelgado,ou=staff,dc=corp,dc=nns
```
- Nhóm `cn=helpdesk` sử dụng thuộc tính `member` lưu trữ dưới dạng **chuỗi DN tuyệt đối** (`Distinguished Name`).
- Trong hệ thống LDAP không bật cơ chế toàn vẹn tham chiếu tự động (Referential Integrity Plugin), nếu đối tượng `uid=agrant,ou=staff,...` bị đổi tên RDN (thành `uid=agrant-old`), giá trị `member: uid=agrant,ou=staff,...` trong nhóm `helpdesk` **vẫn tồn tại nguyên vẹn** (trở thành một con trỏ lơ lửng - Dangling / Stale DN).
- Lúc này, bất kỳ đối tượng nào xuất hiện và sở hữu lại đúng DN `uid=agrant,ou=staff,dc=corp,dc=nns` sẽ ngay lập tức được hệ thống phân quyền coi là thành viên hợp lệ của `cn=helpdesk`.

---

## 4. Xây Dựng Chuỗi Khai Thác Logic (The Attack Path)

Từ các nhận định trên, ta thiết lập luồng tấn công gồm 4 chặng:

```
[ereid:Contractor] 
       │ (Sử dụng quyền onboarding-agents)
       ▼
[Chuyển ereid sang ou=staff]
       │
       ▼
[Đổi tên agrant -> agrant-retired]  ──>  Giải phóng vị trí DN "uid=agrant,ou=staff,..."
       │
       ▼
[Đổi tên ereid -> agrant]          ──>  Chiếm vị trí DN "uid=agrant", giữ nguyên mật khẩu "Summer2026"
       │
       ▼
[Xác thực danh tính mới]          ──>  Được hệ thống công nhận là Helpdesk Member
       │
       ▼
[Reset mật khẩu ops]              ──>  Gán mật khẩu ta kiểm soát cho tài khoản ops
       │
       ▼
[SSH sang srv2 với ops]           ──>  Lấy Flag tại /home/ops/flag.txt
```

1. **Bước 1: Chuyển vùng đối tượng**  
   Dùng quyền `onboarding-agents`, thực hiện `moddn` chuyển `ereid` từ `ou=contractors` sang `ou=staff`. Cập nhật `loginShell` sang `/bin/bash` thông qua cơ chế tự phục vụ (`Self-service directory updates`).

2. **Bước 2: Hoán vị RDN (DN Hijacking)**  
   - Do ACI cho phép sửa `uid` ngoại trừ `ops`, ta đổi tên nhân viên Helpdesk thật (`agrant`) sang một tên tạm thời (`agrant-retired`). DN `uid=agrant,ou=staff,dc=corp,dc=nns` được trả về trạng thái trống.
   - Tiếp tục đổi tên tài khoản của ta (`ereid`) thành `agrant`. Bây giờ, ta chính là chủ sở hữu của entry `uid=agrant,ou=staff,dc=corp,dc=nns` với mật khẩu đã biết (`Summer2026`).

3. **Bước 3: Thực thi quyền hạn Helpdesk**  
   Liên kết (bind) vào LDAP dưới danh nghĩa `agrant:Summer2026`. Vì DN này có tên trong danh sách thành viên của `cn=helpdesk`, ta thực hiện lệnh sửa đổi `userPassword` trên entry `uid=ops,ou=staff,dc=corp,dc=nns`, đặt lại thành một mật khẩu mới.

4. **Bước 4: Vượt ranh giới mạng nội bộ**  
   Từ máy `jump`, mở phiên SSH tới máy chủ `srv2` bằng user `ops` cùng mật khẩu vừa thiết lập, sau đó đọc nội dung file flag.

---

## 5. Flag & Ý Nghĩa Thiết Kế

- **Flag thu được**:
  ```text
  NNS{a_JoB_7i71e_is_Not_4n_acCes5_contr0l_BoundarY_4nD_aPP4rently_theR3_are_4ctU41_oRgs_7H47_D0_57uPid_5hi7_1iK3_7h15}
  ```

- **Bài học bảo mật**:
  1. **Job title không phải là ranh giới bảo mật**: Hệ thống không nên dựa vào các thuộc tính nhân sự hoặc quyền tự quản lý định danh để ngầm định quyền truy cập đặc quyền.
  2. **Nguy cơ của dangling DN trong LDAP**: Nhóm quyền tĩnh (`groupOfNames`) khi kết hợp với quyền di chuyển/đổi tên đối tượng (`moddn`) mà không có Referential Integrity sẽ mở ra kỹ thuật chiếm quyền định danh (DN Takeover).
  3. **Hạn chế của Blacklist filter**: Việc chỉ ngăn chặn `uid=ops` tạo ra ảo tưởng về an toàn, trong khi kẻ tấn công hoàn toàn có thể đi đường vòng qua tài khoản Helpdesk để đạt cùng mục đích.


