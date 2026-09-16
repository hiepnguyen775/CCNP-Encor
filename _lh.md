# LAB 10 — Tuần 16: Hardening · AAA · ACL · CoPP · 802.1X

> 📘 **Lý thuyết:** [Module-10](Module-10-Security.md) —
> đọc **Phần 1** và **Phần 2 mục §3 (hardening), §4 (AAA), §5 (ACL), §6 (CoPP)** trước khi làm.
>
> ⏱️ **Thời gian:** ~7 giờ · 💾 **RAM:** 1.8 GB · 🧰 **Cần:** EVE-NG + 2× vIOS + 1× vIOS-L2

---

## ⭐ Không có RADIUS server vẫn lab được 80%

| Nội dung | Cần server? | Cách lab |
|---|:---:|---|
| Password type, SSH, hardening | ❌ | Lab đầy đủ |
| ⭐⭐ **AAA + fallback** | ❌ | ⭐ **Trỏ vào IP không tồn tại** → server "chết" → quan sát fallback sang `local`.<br>⭐ **Đây chính là điểm đề hỏi!** |
| ACL nâng cao, uRPF, VACL | ❌ | Lab đầy đủ |
| CoPP | ❌ | Lab đầy đủ |
| ⭐ 802.1X | ⚠️ | Quan sát `Unauthorized` + tái hiện **Critical VLAN** khi RADIUS chết |

> ⭐ **Lab "server chết → fallback" còn giá trị hơn lab "đăng nhập thành công"** —
> vì đề hỏi đúng cái tình huống hỏng.

---

## 🔴 CẢNH BÁO AN TOÀN — đọc trước khi gõ

| Việc | Vì sao nguy hiểm |
|---|---|
| 🔴 ⭐⭐ **TẠO USER LOCAL TRƯỚC khi gõ `aaa new-model`** | Thiếu bước này là **tự khóa mình ra khỏi router** |
| 🔴 ⭐⭐ **GIỮ MỘT PHIÊN SSH THỨ HAI đang mở** | Nếu hỏng thì còn đường sửa. LAB B **cố ý** cho bạn tự khóa mình một lần |
| ⭐ **`test aaa` TRƯỚC khi logout** | Đừng logout rồi mới biết |
| 🔴 **CoPP: bắt đầu `exceed-action transmit`** | Siết ngay là **tự đánh sập OSPF/SSH của chính mình** |

---

