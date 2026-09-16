# LAB 08 — Tuần 14: VRF · GRE · IPsec

> 📘 **Lý thuyết:** [Module-08](Module-08-Virtualization-va-Overlay.md) —
> đọc **Phần 1** và **Phần 2 mục §4 (VRF), §5 (GRE), §6–7 (IPsec)** trước khi làm.
>
> ⏱️ **Thời gian:** ~5 giờ · 💾 **RAM:** 2 GB *(hoặc ~7 GB nếu phải dùng CSR1000v cho crypto)*
> · 🧰 **Cần:** EVE-NG + 3× vIOS

---

## Lab này trả lời 6 câu hỏi

| # | Câu hỏi | Bước |
|:---:|---|:---:|
| 1 | Hai interface **cùng một IP** trên một router — làm sao được? | 1 |
| 2 | Vì sao gán VRF xong thì **IP biến mất**? | 1 |
| 3 | Vì sao `ping <ip>` **không bao giờ** tới host trong VRF? | 1 |
| 4 | Gói đi qua Internet mà ISP **không biết** mạng nội bộ — bằng cách nào? | 2 |
| 5 | Tunnel lên rồi xuống liên tục — vì sao, và sửa thế nào? | 3 |
| 6 | Bắt gói trước/sau khi bật IPsec — khác nhau thế nào? | 5, §11.5 |

> ⭐ **Bước 3 (tái hiện recursive routing) là bước giá trị nhất.**
> Lab hỏng dạy nhiều hơn lab chạy — bạn sẽ thấy tunnel flapping thật và hiểu vì sao.

---

## ⚠️ Đọc trước khi bắt đầu

| Điều cần biết | Chi tiết |
|---|---|
| ⚠️ **Kiểm tra crypto TRƯỚC** | Gõ `crypto isakmp policy 10` trên R1. Báo `% Invalid input` thì image thiếu `securityk9` — đổi R1/R2 sang **CSR1000v**, hoặc bỏ bước 5 và đọc kỹ cấu hình |
| ⭐ **VRF: gán VRF TRƯỚC, đặt IP SAU** | Làm ngược thì IP bị xóa. Trên thiết bị thật, nếu đang SSH qua chính interface đó thì **mất kết nối** |
| ⭐ **Ping trong VRF phải gõ `vrf`** | `ping vrf KHACH-A <ip>` — quên là dùng bảng global, không bao giờ tới |
| **Bước 3 và 6 là cố ý phá** | Làm xong nhớ sửa lại |
| **Lỗi > 15 phút** | Ghi vào [`SO-TAY-LOI.md`](SO-TAY-LOI.md) |

---

