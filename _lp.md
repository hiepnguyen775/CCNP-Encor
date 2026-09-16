## 🧪 PHẦN 3 — NHÌN THẤY NÓ

> ### 👉 **[LAB 10 — Tuần 16: Hardening · AAA · ACL · CoPP · 802.1X](Module-10-LAB.md)**

| LAB | Nội dung | Ví von ở Phần 1 | Cơ chế ở Phần 2 |
|---|---|---|---|
| **A** | Password type · SSH · `login block-for` | — | §3 |
| **B** | 🔴 ⭐⭐ **AAA + FALLBACK** *(lab quan trọng nhất)* | §2.1 thẻ nhân viên · §2.2 nhân sự không bắt máy | §4 |
| **C** | ACL nâng cao · ⭐ **bẫy IPv6 giết NDP** | — | §5 |
| **D** | ⭐⭐ **CoPP — đo trước, siết sau** | §2.3 thư ký gác cửa bộ não | §6 |
| **E–I** | 🚀 802.1X · uRPF · VACL · DHCP Snooping · wireless | §2.4 bảo vệ giữ cửa | §7–§10 |

> ⭐ **Ba lab "cố ý phá" đáng làm nhất:**
>
> 1. ⭐ **Giải ngược chuỗi password type 7** bằng công cụ online — mất 2 phút, nhớ cả đời
> 2. 🔴 ⭐⭐ **Bỏ `local` khỏi method list → tự khóa mình → sửa bằng phiên SSH thứ hai**
> 3. 🔴 ⭐⭐ **Áp `deny ipv6 any any` → IPv6 chết sạch** vì NDP bị chặn
>
> Ba bài này dạy bạn nhiều hơn 20 trang lý thuyết.
