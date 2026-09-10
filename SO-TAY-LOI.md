# SỔ TAY LỖI — của riêng bạn

> **Quy tắc:** mỗi lần bạn mất **> 15 phút** vì một lỗi → ghi vào đây. Không ghi khi vừa sửa xong
> thì sau 2 tuần bạn sẽ mắc lại đúng lỗi đó.
>
> Cuối 20 tuần, đây là file **giá trị nhất** trong repo — vì nó viết bằng đúng những chỗ *bạn* hay sai,
> không phải chỗ người khác hay sai. Trước khi thi, đọc lại file này thay vì đọc lại sách.

---

## Cách ghi (copy khối này xuống mỗi lần)

```markdown
### [Ngày] — [Tiêu đề ngắn gọn]

- **Module / LAB:** 
- **Triệu chứng:** (mô tả đúng cái bạn nhìn thấy, kèm output nếu có)
- **Tôi đã nghĩ sai rằng:** (quan trọng nhất — ghi lại suy nghĩ sai của mình)
- **Nguyên nhân thật:** 
- **Lệnh tìm ra nó:** 
- **Cách sửa:** 
- **Mất bao lâu:** 
- **Bài học 1 câu:** 
```

---

## Ví dụ mẫu (xóa khi bạn có mục thật)

### 2026-09-10 — Node EVE-NG không boot

- **Module / LAB:** Module-00, LAB-00
- **Triệu chứng:** Icon router chuyển xanh 2 giây rồi về xám. Console mở ra trống trơn.
- **Tôi đã nghĩ sai rằng:** image bị lỗi, tải lại image mất 1 tiếng vô ích.
- **Nguyên nhân thật:** chưa tick *Virtualize Intel VT-x/EPT* trong VMware settings.
- **Lệnh tìm ra nó:** `tail -50 /opt/unetlab/data/Logs/unl_wrapper.txt` → báo lỗi KVM không khả dụng.
- **Cách sửa:** Shutdown VM → Settings → Processors → tick VT-x/EPT → power on.
- **Mất bao lâu:** 1 giờ 20 phút
- **Bài học 1 câu:** Node không boot → kiểm tra VT-x/EPT **trước** khi nghi ngờ image.

---

## Bảng tổng hợp — cập nhật mỗi tuần

| Ngày | Lỗi | Module | Mất bao lâu | Đã mắc lại? |
|---|---|---|:---:|:---:|
| 2026-09-10 | Node không boot (VT-x/EPT) | M00 | 1h20 | ☐ |
|  |  |  |  |  |

---

## 🔥 Danh sách "lỗi tôi mắc ≥ 2 lần" — đọc trước mỗi buổi lab

> Khi một lỗi xuất hiện lần thứ hai, chuyển nó lên đây. Đây là điểm yếu thật của bạn.

| Lỗi | Số lần mắc | Cách phòng |
|---|:---:|---|
|  |  |  |

---

## 📌 Checklist tự phòng lỗi — thêm dòng khi phát hiện thói quen xấu của mình

| # | Trước khi báo "lab lỗi", tôi phải kiểm tra | ✅ |
|:---:|---|:---:|
| 1 | `show ip interface brief` — interface có `up/up` chưa? | ☐ |
| 2 | Đã `no shutdown` chưa? | ☐ |
| 3 | IP/mask có đúng subnet không? | ☐ |
| 4 | (Switch) VLAN có tồn tại trên **cả hai** switch? | ☐ |
| 5 | Đã `write memory` chưa? | ☐ |
| 6 | Có ACL nào đang chặn? (`show ip int Gi0/0 \| inc access`) | ☐ |
| 7 | Có route tới đích chưa? (`show ip route <đích>`) | ☐ |
| 8 | Debug cũ đã tắt chưa? (`undebug all`) | ☐ |
