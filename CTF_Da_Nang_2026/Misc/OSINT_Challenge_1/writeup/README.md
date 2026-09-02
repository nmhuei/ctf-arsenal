# OSINT Challenge 1

| Property | Value |
| :--- | :--- |
| **Category** | `Misc` |
| **Points** | `56` |
| **Solves** | 9 |

## 📝 Description

Following the Footprints of Someone Who Was Never There


## 📦 Files & Resources

*No file attachments associated with this challenge.*

## 🚩 Flag & Solution

- [x] Solved

```
flag{19d9cbeb-3d99-43d3-9732-a3fae3ea5860}
```

### Writeup / Notes

1. **Truy vết arXiv**:
   - Truy cập `/arxiv/` trên instance bài thi tìm thấy bài báo của tác giả **Nguyễn Minh Khoa** tại `/arxiv/abs/2605.99847`.
   - Trong thông tin tác giả có liên kết đến profile X (Twitter): `@khoa_neuralnet` (`/x/khoa_neuralnet`).

2. **Truy vết X (Twitter)**:
   - Profile X trỏ đến tài khoản GitHub `minhkhoa-ai` (`/gh/minhkhoa-ai`).
   - Bài đăng trên X nhắc đến ghi chú thử nghiệm được đưa lên Pastebin.

3. **Truy vết GitHub & Pastebin**:
   - Truy cập repository `phantom-gradient-descent` (`/gh/minhkhoa-ai/phantom-gradient-descent`), trong file `README.md` có link dẫn tới Pastebin unlisted: `/p/gg5oggvj`.
   - Trong nội dung Pastebin có trường:
     `master_key_b64 = "ZmxhZ3sxOWQ5Y2JlYi0zZDk5LTQzZDMtOTczMi1hM2ZhZTNlYTU4NjB9"`

4. **Giải mã Flag**:
   - Base64 decode: `flag{19d9cbeb-3d99-43d3-9732-a3fae3ea5860}`.
