# LAB 09 — Tuần 15: Thiết kế & QoS

> 📘 **Lý thuyết:** [Module-09](Module-09-Architecture-va-QoS.md) —
> đọc **Phần 1** và **Phần 2 mục §3 (campus), §7 (SD-WAN), §8 (SD-Access), §9 (QoS)** trước khi làm.
>
> ⏱️ **Thời gian:** ~3 giờ · 💾 **RAM:** 1 GB — nhẹ nhất repo · 🧰 **Cần:** giấy bút + 2× vIOS

---

## ⭐ Module "học bằng đầu" — Domain 1.0 không có mục nào bắt cấu hình

Toàn bộ Domain 1.0 dùng từ *Explain · Analyze · Differentiate · Describe*.
Nên lab ở đây chủ yếu là **lab-trên-giấy** — đúng dạng câu hỏi của đề.

| LAB | Nội dung | Cần gì | Bắt buộc? |
|---|---|---|:---:|
| **A** | ⭐⭐ **Chọn thiết kế** — 10 tình huống | Giấy bút | ⭐⭐ **Có** |
| **B** | QoS trên EVE-NG (MQC, LLQ, shaping) | 2× vIOS | ⭐⭐ **Có** |
| **C** | ⭐⭐ **Điền bảng thành phần SD-WAN / SD-Access** | Giấy bút | ⭐⭐ **Có** |
| **D** | Nhìn DNA Center & vManage thật | DevNet Sandbox | Nên |

> ⭐ **LAB C là bài đáng làm nhất.** Điền được bảng 4 thành phần SD-WAN và 5 fabric role
> SD-Access **từ trí nhớ** là bạn đã nắm phần lớn câu hỏi của mục 1.4 và 1.5.

---

## ⚠️ Đọc trước khi bắt đầu

| Điều cần biết | Chi tiết |
|---|---|
| **Viết đáp án TRƯỚC khi mở gợi ý** | LAB A và C chỉ có giá trị nếu bạn tự làm trước |
| **LAB B: đổi DSCP sang ToS** | `ping ... tos <n>` nhận **ToS**, không phải DSCP. ⭐ `ToS = DSCP × 4` (EF 46 → 184) |
| 🔴 **Đừng cố dựng SD-WAN on-prem** | vManage + vSmart + vBond + 2 vEdge = **20+ GB RAM**. Máy bạn không kham nổi, **và đề không hỏi cấu hình** |
| **Sandbox là môi trường dùng chung** | ⭐ Chỉ **XEM**, đừng đổi cấu hình |

---

