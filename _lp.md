## 🧪 PHẦN 3 — NHÌN THẤY NÓ

> ### 👉 **[LAB 08 — Tuần 14: VRF · GRE · IPsec](Module-08-LAB.md)**

| Bước | Nội dung | Ví von ở Phần 1 | Cơ chế ở Phần 2 |
|:---:|---|---|---|
| 1 | ⭐⭐ **VRF + hai interface trùng IP** | §2.1 nhiều công ty thuê chung tòa nhà | §4 |
| 2 | ⭐ GRE tunnel + OSPF qua tunnel | §2.2 phong bì trong suốt | §5 |
| 3 | 🔴 ⭐⭐ **Tái hiện recursive routing** | §2.3 muốn tới nhà phải đi qua chính nhà đó | §5.3 |
| 4 | ⭐⭐ Tìm MTU thật bằng `ping df-bit` | — | §5.4 |
| 5 | ⭐⭐ **GRE over IPsec** — `QM_IDLE`, encaps/decaps | §2.2 hộp niêm phong | §6–7 |
| 6 | 🔴 ⭐ Cố ý phá IPsec (sai PSK, lệch transform-set) | — | §7.3 |

> ⚠️ **Hai bước quan trọng nhất:**
>
> ⭐ **Bước 1** — bạn sẽ đặt **cùng một IP `10.10.10.1` lên hai interface** và router
> **không báo lỗi**. Đó là lúc VRF thôi là khái niệm và trở thành thứ nhìn thấy được.
>
> ⭐ **Bước 3** — tái hiện `%TUN-5-RECURDOWN` và thấy tunnel flapping thật.
> **Lab hỏng dạy nhiều hơn lab chạy.**
