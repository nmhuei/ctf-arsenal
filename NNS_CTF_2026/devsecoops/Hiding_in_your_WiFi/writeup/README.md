# Phân Tích & Tư Duy Giải Bài: Hiding in your WiFi (devsecoops)

---

## 1. Bối Cảnh & Mô Hình Mạng (Mental Model)

Đề bài đặt ta vào một phân đoạn mạng nội bộ (Layer 2 / Broadcast Domain):
- **Ta (Attacker)**: `10.10.10.66`
- **Mục tiêu 1 (Web Server)**: `10.10.10.10` (chạy HTTP port 80)
- **Mục tiêu 2 (Client)**: `10.10.10.20`
- **Môi trường**: Shell Linux có sẵn các công cụ `arpspoof`, `tcpdump`.

**Đặc tính then chốt của bài toán**:
1. Server (`10.10.10.10`) chỉ phục vụ và trả lời client (`10.10.10.20`), áp dụng cơ chế lọc IP (IP Whitelisting / Firewall). Mọi kết nối trực tiếp từ `10.10.10.66` tới Server đều bị từ chối hoặc bỏ qua.
2. Client liên tục thực hiện truy vấn HTTP lấy dữ liệu bí mật từ Server theo chu kỳ.
3. Mạng là mạng chia sẻ (Switched Network), các máy giao tiếp qua Switch ảo. Mặc định trên Switched Network, card mạng của `.66` ở chế độ thông thường sẽ không nhìn thấy Unicast traffic giữa `.10` và `.20`.

**Mục tiêu**: Bắt được gói tin HTTP Response từ Server gửi về cho Client để đọc Flag mà không bị ảnh hưởng bởi traffic rác / honeypot.

---

## 2. Bản Chất Giao Thức & Lỗ Hổng Thiết Kế (The Protocol Flaw)

Mạng cục bộ (Ethernet/WiFi) hoạt động ở hai tầng địa chỉ:
- **Tầng 3 (Network Layer)**: Định tuyến theo địa chỉ IP (`10.10.10.x`).
- **Tầng 2 (Data Link Layer)**: Chuyển phát khung tin thực tế dựa vào địa chỉ MAC phần cứng.

Giao thức **ARP (Address Resolution Protocol)** chịu trách nhiệm phân giải IP sang MAC. Tuy nhiên, ARP có điểm yếu thiết kế nguyên thủy:
- **Không có cơ chế xác thực (Stateless & Trust-based)**: Một thiết bị sẽ tự động cập nhật bảng nhớ tạm (ARP Cache) bất cứ khi nào nó nhận được bản tin ARP Reply, ngay cả khi nó không hề gửi yêu cầu ARP Request trước đó (Gratuitous ARP / Unsolicited ARP Reply).
- **Không có ranh giới tin cậy giữa các thiết bị chung mạng**: Bất kỳ máy nào trong cùng subnet đều có thể tự xưng là chủ sở hữu của bất kỳ địa chỉ IP nào trong subnet đó.

---

## 3. Luồng Tư Duy Khai Thác (The Attack Flow)

Để đưa ta vào vị trí "Người đứng giữa" (Man-in-the-Middle - MitM) giữa Client và Server, tư duy thực hiện gồm 3 giai đoạn:

```text
[Client 10.10.10.20]  <=== Giao tiếp bình thường ===>  [Server 10.10.10.10]
           ▲                                                   ▲
           │          [Attacker 10.10.10.66]                   │
           │           (Bật IP Forwarding)                     │
           │                    ▲                              │
           └──── ARP Poison ────┴──── ARP Poison ──────────────┘
           "Server MAC là CỦA TÔI"   "Client MAC là CỦA TÔI"
```

### Bước 1: Đánh Lừa Bảng ARP (Bidirectional ARP Poisoning)
- Ta gửi liên tục các bản tin ARP giả mạo tới Client: *"Địa chỉ IP `10.10.10.10` đang có địa chỉ MAC của `.66`"*.
- Đồng thời gửi các bản tin ARP giả mạo tới Server: *"Địa chỉ IP `10.10.10.20` đang có địa chỉ MAC của `.66`"*.
- Khi cả hai máy cập nhật bảng ARP Cache bị nhiễm độc:
  - Mọi gói tin Client muốn gửi tới Server sẽ được switch chuyển thẳng tới card mạng của ta.
  - Mọi gói tin Server trả lời cho Client cũng được chuyển thẳng tới card mạng của ta.
  - Nhân Linux của ta (với IP Forwarding) sẽ chuyển tiếp gói tin đến đích thật để kết nối HTTP không bị đứt đoạn.

### Bước 2: Lọc Bắt Gói Tin Mục Tiêu (Focused Packet Filtering)
Trong môi trường mạng có thể tồn tại nhiều luồng nhiễu, broadcast hoặc bẫy mật khẩu / honeypot:
- Ta không bắt toàn bộ traffic vô tội vạ.
- Luồng tư duy chỉ tập trung vào gói tin chứa dữ liệu nhạy cảm nhất: **HTTP Response từ Server trả về cho Client**.
- Thiết lập bộ lọc bắt gói chính xác:
  - `Source IP = 10.10.10.10`
  - `Destination IP = 10.10.10.20`
  - `Source Port = 80` (HTTP)
  - Giải mã nội dung payload dạng ASCII/text.

### Bước 3: Thu Hoạch & Phục Hồi Mạng
- Khi Client gửi yêu cầu và Server phản hồi gói tin HTTP chứa nội dung Flag, bộ lắng nghe bắt trọn phần Body.
- Dừng ngay lập tức quá trình đầu độc ARP để trả lại trạng thái định tuyến bình thường cho mạng (tránh làm tê liệt kết nối).

---

## 4. Flag & Ý Nghĩa Thiết Kế

- **Flag thu được**:
  ```text
  NNS{sw17ch3D_n3tW0RK5_still_tRU5t_aRP_so_K3ep_y0Ur_deviC3s_53Parate}
  ```

- **Ý nghĩa & Bài học**:
  - *"Switched networks still trust ARP, so keep your devices separate"*: Rất nhiều quản trị viên lầm tưởng rằng việc sử dụng Switch hoặc mạng WiFi bảo mật sẽ ngăn chặn được việc nghe lén (Sniffing) giữa các máy trạm.
  - Trên thực tế, ARP Spoofing vẫn đánh sập hoàn toàn ranh giới này nếu mạng không triển khai các biện pháp phòng vệ Layer 2 như:
    - **DAI (Dynamic ARP Inspection)**
    - **Port Security / MAC Binding**
    - **Client Isolation / Private VLAN (PVLAN)** trên hệ thống WiFi.

