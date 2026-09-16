# Module-11 — Network Assurance

> 🧭 **Lộ trình:** [Module-10](Module-10-Security.md) → `[Bạn đang ở đây] Module-11` → Module-12 (Automation & Programmability)
>
> 📊 **Blueprint — Domain 4.0 Network Assurance (10% đề):**
> · ⭐⭐ **4.1 — Diagnose network problems using tools such as debugs, conditional debugs, traceroute, ping, SNMP, and syslog**
> · 🔴 ⭐⭐ **4.2 — CONFIGURE AND VERIFY device monitoring using syslog for remote logging**
> · 🔴 ⭐⭐ **4.3 — CONFIGURE AND VERIFY NetFlow and Flexible NetFlow**
> · 🔴 ⭐⭐ **4.4 — CONFIGURE AND VERIFY SPAN/RSPAN/ERSPAN**
> · 🔴 ⭐⭐ **4.5 — CONFIGURE AND VERIFY IPSLA**
> · 🟡 **4.6 — Describe Cisco DNA Center workflows to apply network configuration, monitoring, and management**
> · 🔴 ⭐ **4.7 — CONFIGURE AND VERIFY NETCONF and RESTCONF** → ⭐ **xem §10, học sâu ở Module-12**
>
> ⏱️ **Tuần 17** · 10 giờ

---

# 📌 TÓM TẮT — đọc 10 phút là nắm khung

## Module này trả lời một câu hỏi duy nhất

> **Mạng đang chạy — làm sao biết nó có KHỎE không, và khi hỏng thì tìm nguyên nhân ở đâu?**

## Năm công cụ = năm GIÁC QUAN khác nhau

```
   ┌──────────────┬────────────────────────┬───────────────────────┐
   │ Syslog       │ Nhật ký                │ "Đã xảy ra chuyện gì?"│
   │ SNMP         │ Bắt mạch định kỳ       │ "Tình trạng hiện giờ?"│
   │ NetFlow      │ Sổ ghi chi tiêu        │ "AI ăn hết băng thông?"│
   │ SPAN         │ Kính hiển vi           │ "Trong gói có gì?"    │
   │ IP SLA       │ Máy đo huyết áp đeo    │ "Chất lượng có đạt?"  │
   └──────────────┴────────────────────────┴───────────────────────┘

   🔴 Chỉ dùng MỘT giác quan là mù.
      Người mới thường chỉ có SNMP rồi ngạc nhiên vì
      "tất cả đèn xanh mà người dùng vẫn kêu"
      — vì SNMP đo THIẾT BỊ, không đo TRẢI NGHIỆM.
```

## 🔴 Điều kiện tiên quyết: NTP

```
   Sai giờ  →  log không đối chiếu được giữa các thiết bị
            →  biểu đồ NetFlow sai thời điểm
            →  one-way delay của IP SLA VÔ NGHĨA
            →  chứng thư 802.1X / AP join hỏng   (M07B, M10)

   ⭐ Ba dòng phải có trên MỌI thiết bị:
        ntp server <ip>
        service timestamps log datetime msec localtime show-timezone
        service sequence-numbers
```

## 7 ý phải nhớ

| # | Ý | Một câu |
|:---:|---|---|
| 1 | 🔴 ⭐⭐ **Syslog: số NHỎ = nghiêm trọng HƠN** | 0 Emergency … 7 Debugging. ⭐ **`logging trap 4` gửi mức 0–4**, không phải "chỉ 4" |
| 2 | ⭐ **Bẫy `%LINK-3` vs `%LINEPROTO-5`** | Cùng sự kiện rút cáp nhưng **khác severity** → `trap 4` thấy interface **down** mà **không thấy nó up lại** |
| 3 | ⭐⭐ **SNMP: agent nghe 161, manager nghe 162** | **Trap** = bắn rồi quên · **Inform** = có ACK, gửi lại · ⭐ **chỉ `authPriv` mới mã hóa** |
| 4 | ⭐⭐ **NetFlow là 7-tuple** | 5-tuple **cộng thêm ToS và input interface**. ⭐ **`match` = KEY định nghĩa flow · `collect` chỉ ghi thêm** |
| 5 | 🔴 ⭐⭐ **`cache timeout active` mặc định 1800s** | Flow dài **không lên collector** trong 30 phút → tưởng mạng rảnh. ⭐ **Đặt 60** |
| 6 | 🔴 ⭐⭐ **Cổng SPAN destination thành "câm"** | Ngừng forward, không STP — nhưng ⭐ **vẫn báo `up/up`**. Thiết bị cắm vào **mất mạng** |
| 7 | 🔴 ⭐⭐ **Quên `ip sla schedule`** | Config trông hoàn hảo nhưng operation **KHÔNG BAO GIỜ CHẠY** |

## Bảng lệnh cốt lõi

| Lệnh | Cho biết gì |
|---|---|
| ⭐ `show logging` | Cấu hình + toàn bộ buffer — **so `Buffer logging` với `Trap logging`** |
| `show snmp user` / `show snmp group` | v3: auth/priv protocol, security level |
| ⭐⭐ `show flow monitor <FM> cache format table` | **Xem toàn bộ flow NGAY TRÊN ROUTER** — không cần collector |
| `show flow monitor <FM> statistics` | ⭐ **`Emergency aged > 0` = cache đầy = số liệu sai** |
| ⭐ `show monitor session all` | SPAN — kiểm tra cổng đích có ai đang dùng không |
| ⭐⭐ `show ip sla statistics <id>` | **Return code** + RTT/jitter/MOS |
| ⭐⭐ `undebug all` *(`u all`)* | **Lệnh cứu hộ — học thuộc trước khi bật bất kỳ debug nào** |

## 🗺️ Bố cục module

| Phần | Tên | Thời gian |
|:---:|---|:---:|
| **1** | 🧠 **CÁI ĐÓ LÀ GÌ** — 6 ví von | 45 phút |
| **2** | ⚙️ **NÓ CHẠY THẾ NÀO** — ⭐ **§3 (thời gian) đọc trước mọi thứ** | 5 giờ |
| **3** | 🧪 **NHÌN THẤY NÓ** — [LAB 11](Module-11-LAB.md), ⭐ **gần như không cần server** | 4 giờ |
| **4** | 🏗️ **TOPO & KIẾN TRÚC** — công cụ nào cho câu hỏi nào | 45 phút |
| **📎** | **PHỤ LỤC** — 🔴 không đọc lần đầu | — |

> 🔴 ⭐⭐ **CẢNH BÁO — Domain 4.0 CHƯA xong sau module này.**
>
> Mục **4.7 (NETCONF & RESTCONF)** thuộc **Domain 4.0 Network Assurance**, không phải
> Domain 6.0 Automation như nhiều người tưởng. Repo này dạy nó ở **Module-12 §3**
> vì nó không thể tách rời YANG.
>
> ⭐ **Đừng tick "xong Domain 4.0" sau module này.** §11 có bản tóm tắt ngắn để bạn không bị hụt.

---

## ⭐ 0. Phạm vi

### 0.1 ⭐⭐ Domain "configure" đậm đặc nhất kỳ thi

> 🔴 ⭐⭐ **Domain 4.0 chỉ chiếm 10% đề nhưng có tới NĂM mục "Configure and verify"** (4.2, 4.3, 4.4, 4.5, 4.7).
> ⭐ **Tỉ lệ cấu-hình/khái-niệm cao nhất trong cả blueprint.**
>
> ⭐ **Tin tốt:** ⭐ **mọi thứ ở đây đều lab được trên EVE-NG, và phần lớn KHÔNG cần server ngoài** —
> xem §1.1. ⭐ **Đây là domain dễ ăn điểm nhất nếu bạn chịu gõ tay.**

| Chủ đề | Blueprint | ⭐ Mức cần đạt | Thời gian |
|---|---|---|---|
| ⭐⭐ **Syslog** | 🔴 **4.2 Configure** | ⭐⭐ **8 severity level** · `logging trap` lọc thế nào · đọc được dòng log | 1.5 giờ |
| ⭐⭐ **SNMP** | ⭐ **4.1** *(chẩn đoán)* | ⭐ **v2c vs v3** · ⭐ **3 security level** · ⭐ **Trap vs Inform** · port 161/162 | 1.5 giờ |
| ⭐⭐ **NetFlow / Flexible NetFlow** | 🔴 **4.3 Configure** | ⭐⭐ **7-tuple** · ⭐⭐ **4 thành phần FNF** · ⭐ **match vs collect** · đọc cache | 2 giờ |
| ⭐⭐ **SPAN / RSPAN / ERSPAN** | 🔴 **4.4 Configure** | ⭐⭐ **Bảng 3 loại** · ⭐ **cổng đích thành "câm"** · RSPAN VLAN · ERSPAN dùng GRE | 1.5 giờ |
| ⭐⭐ **IP SLA** | 🔴 **4.5 Configure** | ⭐ **Loại operation** · ⭐ **Responder dùng khi nào** · ⭐ **ghép với `track`** | 1.5 giờ |
| ⭐⭐ **Debug an toàn & ping/traceroute** | ⭐⭐ **4.1** | ⭐⭐ **Conditional debug** · ⭐ **vì sao `debug all` là tự sát** · extended ping | 1.5 giờ |
| 🟡 **DNA Center Assurance** | 🟡 **4.6 Describe** | ⭐ **Health score · Path Trace · Network Time Travel · Client 360** | 45 phút |
| ⭐ **NETCONF / RESTCONF** | 🔴 **4.7 Configure** | ➡️ ⭐ **Module-12** *(xem cảnh báo §0.2)* | — |

### 0.2 🔴 ⭐⭐ Cảnh báo về mục 4.7 — đọc kỹ, đây là chỗ dễ hụt

> 🔴 ⭐⭐ **NETCONF và RESTCONF nằm ở mục 4.7 — tức là thuộc Domain 4.0 Network Assurance,
> KHÔNG phải Domain 6.0 Automation như hầu hết người học tưởng.**
>
> ⭐ **Vì sao repo này vẫn dạy nó ở Module-12:** NETCONF/RESTCONF **không thể hiểu tách rời YANG**,
> mà YANG lại nằm ở Domain 6.0. ⭐ Tách ra dạy riêng ở đây sẽ khiến bạn học hai lần và hiểu nửa vời.
>
> ⚠️ ⭐⭐ **Nhưng bạn PHẢI biết điều này khi ôn theo domain:** nếu bạn tự chấm *"tôi đã xong Domain 4.0"*
> sau Module-11 → ⭐ **bạn đang thiếu mục 4.7.** ⭐ **Domain 4.0 chỉ thực sự xong sau Module-12 §3.**
>
> ⭐ §10 của module này có **tóm tắt ngắn** để bạn không bị hẫng nếu thi sớm.

### 0.3 ⭐ Bốn mối nối với những gì đã học

| Nối với | Chỗ nào |
|---|---|
| ⭐⭐ **[Module-06B §3](Module-06B-NAT-NTP-Multicast.md)** — NTP | 🔴 ⭐⭐ **Không có NTP thì TOÀN BỘ module này vô nghĩa.** ⭐ Xem §2 |
| ⭐ **[Module-03 §2.6](Module-03-IP-Routing-Nen-tang.md)** + **[Module-06A](Module-06A-FHRP-HSRP-VRRP-GLBP.md)** — IP SLA + track | ⭐ Bạn đã dùng IP SLA để **failover**. ⭐ Ở đây học nó như **công cụ ĐO** |
| ⭐ **[Module-09 §7.8](Module-09-Architecture-va-QoS.md)** — DNA Center | ⭐ **Assurance là workflow thứ tư** bạn đã gặp |
| ⭐ **[Module-08 §4.4](Module-08-Virtualization-va-Overlay.md)** — MTU/GRE | ⭐ **ERSPAN dùng GRE** → cùng vấn đề MTU |

---

## ✅ 1. Chuẩn bị

| Cần có | Chi tiết |
|---|---|
| **Kiến thức trước** | ⭐ **Module-06B §3 (NTP)** · Module-03 (IP SLA + track) · Module-02 (VLAN/trunk — cho RSPAN) · Module-08 §4.4 (MTU — cho ERSPAN) |
| **Lab** | ⭐ **EVE-NG**: `R1`, `R2` (vIOS 512 MB) + `SW1` (vIOS-L2 768 MB) |
| **RAM** | ⭐ **~1.8 GB** ✅ — dùng lại đúng topology Module-10 |
| **Tùy chọn** | Một máy Linux nhỏ làm **syslog server / NetFlow collector** — ⭐ **xem §1.1, phần lớn LAB không cần** |
| **Thời lượng** | 5h lý thuyết · 4h lab · 1h quiz |

### 1.1 ⭐⭐ Không có server ngoài — vẫn lab được gần hết

> ⭐ **Đây là điểm mạnh của Module-11:** ⭐ **hầu hết công cụ giám sát đều có bộ đệm/bộ nhớ NGAY TRÊN
> THIẾT BỊ**, nên bạn xem kết quả tại chỗ mà không cần collector.

| Nội dung | Cần server? | ⭐ Cách lab không cần server |
|---|:---:|---|
| ⭐⭐ **Syslog** | ❌ | ⭐⭐ **`logging buffered` → `show logging`.** ⭐ Thấy đủ severity, timestamp, format |
| ⭐ **SNMP** | ⚠️ Một phần | ⭐ Cấu hình + `show snmp user/group/host`. ⭐ Muốn `snmpwalk` thật thì cần Linux |
| ⭐⭐ **Flexible NetFlow** | ❌ | ⭐⭐ **`show flow monitor <FM> cache` — ⭐ XEM ĐƯỢC TOÀN BỘ FLOW NGAY TRÊN ROUTER.** ⭐ Đây là LAB hay nhất module |
| ⭐⭐ **SPAN** | ❌ | ⭐ Cấu hình + `show monitor session`. ⭐ Và **tái hiện được bẫy "cổng đích thành câm"** |
| ⭐ **RSPAN** | ❌ | ⭐ Lab được với 1 switch (hoặc 2 nếu máy cho phép) |
| ⭐ **ERSPAN** | ⚠️ | 🔴 ⭐ **vIOS thường KHÔNG hỗ trợ.** ⭐ Đọc cấu hình + hiểu cơ chế là đủ (xem §6.4) |
| ⭐⭐ **IP SLA** | ❌ | ⭐⭐ **Lab đầy đủ** — kể cả `udp-jitter` với **Responder trên R2** |
| ⭐⭐ **Debug an toàn** | ❌ | ⭐⭐ **Lab đầy đủ** — conditional debug là kỹ năng thật |
| **DNA Center Assurance** | ❌ | ⭐ **DevNet Sandbox** |

---

## 🧠 PHẦN 1 — CÁI ĐÓ LÀ GÌ

> **Đọc phần này TRƯỚC, đọc một mạch.** Không lệnh, không bảng tra.
>
> Module-11 gom **năm công cụ giám sát** dễ lẫn nhau. Sáu ví von dưới đây cho bạn biết
> **cái nào dùng khi nào** — quan trọng hơn cả việc nhớ cú pháp.
>
> **Tự kiểm tra:** đọc xong mỗi mục, gấp tài liệu lại, nói lại trong 3 câu.

### 2.1 Năm công cụ = năm loại "giác quan"

⭐ Một mạng cũng giống một cơ thể, và bạn cần **nhiều giác quan khác nhau**:

| Công cụ | ⭐ Giác quan | Trả lời |
|---|---|---|
| ⭐ **Syslog** | ⭐ **Nhật ký** | *"Đã xảy ra chuyện gì?"* — **quá khứ** |
| ⭐ **SNMP** | ⭐ **Bắt mạch định kỳ** | *"Tình trạng hiện giờ ra sao?"* — **hiện tại, đều đặn** |
| ⭐ **NetFlow** | ⭐ **Sổ ghi chi tiêu** | *"Tiền (băng thông) đi đâu hết?"* |
| ⭐ **SPAN** | ⭐ **Kính hiển vi** | *"Trong mẫu vật này chính xác có gì?"* |
| ⭐ **IP SLA** | ⭐ **Máy đo huyết áp đeo liên tục** | *"Chất lượng có duy trì được không?"* |

🔴 ⭐ **Chỉ dùng một giác quan là mù.** ⭐ Người mới thường **chỉ có SNMP** rồi ngạc nhiên vì
⭐ *"tất cả đèn xanh mà người dùng vẫn kêu"* — vì ⭐ **SNMP không đo trải nghiệm, nó đo thiết bị.**

### 2.2 Syslog severity: số càng nhỏ, tiếng chuông càng to

⭐ Hình dung một **thang báo động ngược**:
- ⭐ **0 = còi hú toàn nhà máy** (Emergency — cháy rồi)
- ⭐ **3 = chuông báo một phòng** (Error — interface xuống)
- ⭐ **5 = ghi vào sổ trực** (Notification — ai đó vừa sửa config)
- ⭐ **7 = camera ghi hình mọi thứ** (Debugging — cực nhiều dữ liệu)

⭐⭐ **`logging trap 4` = "chỉ gọi tôi khi tiếng chuông TO BẰNG mức 4 trở lên"** →
⭐ nhận 0,1,2,3,4 và ⭐ **bỏ qua 5,6,7.**

🔴 ⭐ **Và đây là lý do bẫy `%LINK-3` / `%LINEPROTO-5` tồn tại:** ⭐ **hai nửa của cùng một sự kiện
lại nằm ở hai bên ngưỡng lọc** → bạn thấy interface **xuống** mà không thấy nó **lên lại**.

### 2.3 NetFlow là hóa đơn điện thoại, SPAN là nghe lén

- ⭐⭐ **NetFlow** = ⭐ **hóa đơn điện thoại chi tiết**: ai gọi ai, lúc mấy giờ, bao lâu, tốn bao nhiêu.
  ⭐ **Rẻ, giữ được cả năm, đủ để biết "ai xài nhiều nhất"** — ⭐ **nhưng không biết họ nói gì.**
- ⭐⭐ **SPAN** = ⭐ **ghi âm cuộc gọi**: biết chính xác từng lời.
  🔴 ⭐ **Nhưng không thể ghi âm mọi cuộc gọi mãi mãi** — quá tốn.

⭐ **Vì thế quy trình thật luôn là:** ⭐ **NetFlow chạy 24/7 để PHÁT HIỆN bất thường** →
⭐ **rồi mới bật SPAN vào đúng chỗ đó để SOI CHI TIẾT.**

### 2.4 `match` vs `collect`: cái gì làm nên "một cuộc gọi riêng biệt"

⭐ Quay lại ẩn dụ hóa đơn:
- ⭐⭐ **`match` (key)** = ⭐ **những thứ định nghĩa "đây là một cuộc gọi khác"**:
  số gọi đi, số nhận, loại cuộc gọi. ⭐ **Đổi một trong số đó = một dòng hóa đơn mới.**
- ⭐ **`collect` (non-key)** = ⭐ **những thứ chỉ ghi thêm vào dòng đó**: thời lượng, số tiền.
  ⭐ **Không tạo ra dòng mới.**

🔴 ⭐⭐ **Hệ quả:** nếu bạn `match` **source port** — mà mỗi lần trình duyệt mở kết nối lại dùng
**một source port ngẫu nhiên khác** → ⭐ **một máy duyệt web tạo ra HÀNG TRĂM dòng hóa đơn.**
⭐ **Cache đầy rất nhanh.** ⭐ **Chỉ match cái gì bạn thật sự cần phân biệt.**

### 2.5 SPAN destination là "cổng đã bị trưng dụng"

⭐ Khi bạn chỉ định một port làm **SPAN destination**, ⭐ **switch trưng dụng nó hoàn toàn**:
- 🔴 ⭐ **Không chuyển traffic bình thường nữa**
- 🔴 ⭐ **Không tham gia STP**
- 🔴 ⭐ **Không học MAC**
- ⭐ **Chỉ làm đúng một việc: phun bản sao ra ngoài**

🔴 ⭐⭐ **Vì thế: cắm nhầm SPAN destination vào port đang có người dùng = người đó MẤT MẠNG ngay lập tức**,
⭐ **và bạn sẽ không nghĩ ra nguyên nhân** vì `show interface` vẫn báo `up/up`.

⭐ **Và bẫy oversubscription:** ⭐ **10 cổng 1 Gbps đổ vào 1 cổng 1 Gbps** → ⭐ **gói bị rơi âm thầm**.
⭐ Bạn mở Wireshark, thấy "traffic có vẻ bình thường" — ⭐ **trong khi 60% đã bị vứt trước khi tới bạn.**

### 2.6 IP SLA: ping là chụp ảnh, IP SLA là camera an ninh

- ⭐ **`ping` thủ công** = ⭐ **chụp một tấm ảnh**. ⭐ Lúc bạn chụp thì mọi thứ ổn —
  🔴 ⭐ **nhưng sự cố xảy ra lúc 3 giờ sáng thì sao?**
- ⭐⭐ **IP SLA** = ⭐ **camera quay liên tục 24/7 và lưu lại thống kê.**
  ⭐ Sáng hôm sau bạn xem `show ip sla statistics` và ⭐ **biết chính xác đêm qua mất bao nhiêu gói, lúc mấy giờ.**

⭐⭐ **Và Responder là "người cầm đồng hồ ở đầu kia"** — ⭐ nhờ có anh ta đóng dấu thời gian,
bạn ⭐ **tách được độ trễ CHIỀU ĐI khỏi độ trễ CHIỀU VỀ.**
🔴 ⭐ **Nhưng hai người phải chỉnh đồng hồ giống nhau (NTP), nếu không con số vô nghĩa.**


---

## ⚙️ PHẦN 2 — NÓ CHẠY THẾ NÀO

> | Phần 1 (ví von) | → | Phần 2 (cơ chế) |
> |---|:---:|---|
> | §2.1 năm giác quan | → | **§4 Syslog · §5 SNMP · §6 NetFlow · §7 SPAN · §8 IP SLA** |
> | §2.2 thang báo động ngược | → | **§4 Syslog severity** ⭐⭐ |
> | §2.3 hóa đơn vs ghi âm · §2.4 dòng hóa đơn nào | → | **§6 NetFlow (`match` vs `collect`)** ⭐⭐ |
> | §2.5 cổng bị trưng dụng | → | **§7 SPAN destination** 🔴 |
> | §2.6 camera an ninh vs chụp ảnh | → | **§8 IP SLA** ⭐⭐ |
>
> 🔴 ⭐⭐ **Đọc §3 (THỜI GIAN) trước mọi thứ khác.** Sai giờ thì cả năm công cụ ở trên
> đều trở thành **rác**: log không đối chiếu được · biểu đồ NetFlow sai thời điểm ·
> one-way delay của IP SLA vô nghĩa.

---

## 📘 3. 🔴 ⭐⭐ NỀN TẢNG: THỜI GIAN — đọc trước mọi thứ khác

> 🔴 ⭐⭐ **Nếu đồng hồ sai, toàn bộ Module-11 trở nên vô dụng.** ⭐ Đây không phải lời nói quá:

| Công cụ | 🔴 Hỏng thế nào khi sai giờ |
|---|---|
| ⭐ **Syslog** | ⭐ **Không đối chiếu được log giữa các thiết bị** → không dựng lại được trình tự sự cố |
| ⭐ **NetFlow** | ⭐ Collector vẽ biểu đồ **sai thời điểm** → tưởng nghẽn lúc 2h sáng mà thật ra là 2h chiều |
| ⭐ **IP SLA** | ⭐ **One-way delay tính SAI hoàn toàn** *(xem §7.4)* |
| ⭐ **SNMP** | Trap tới NMS với timestamp lệch |
| ⭐ **Chứng thư số** | ⭐ **802.1X / AP join / HTTPS đều hỏng** *(Module-07B §3.4, Module-10)* |
| ⭐ **Điều tra sự cố an ninh** | 🔴 ⭐ **Log không có giá trị pháp lý nếu thời gian không tin cậy** |

```
! BA DÒNG PHẢI CÓ TRÊN MỌI THIẾT BỊ — trước khi làm bất cứ gì trong module này
ntp server 10.99.1.5 prefer
ntp server 10.99.1.6
clock timezone ICT 7 0
!
service timestamps log datetime msec localtime show-timezone
service timestamps debug datetime msec localtime show-timezone
service sequence-numbers
```

| Lệnh | ⭐ Vì sao cần |
|---|---|
| ⭐⭐ `service timestamps log datetime msec` | ⭐ **Mặc định log chỉ có `uptime`** (`*Mar 1 00:04:12`) → ⭐ **vô dụng khi đối chiếu nhiều thiết bị.** ⭐ `msec` cần cho sự kiện nhanh (STP, flap) |
| ⭐ `localtime show-timezone` | ⭐ Hiện giờ địa phương + múi giờ → ⭐ **không nhầm khi đọc log lúc 3 giờ sáng** |
| ⭐ `service sequence-numbers` | ⭐ Đánh số thứ tự mỗi dòng log → ⭐ **biết ngay có dòng nào bị MẤT không** |

⭐ **Kiểm chứng:**
```
show clock detail
   14:23:45.123 ICT Thu Sep 10 2026
   Time source is NTP              ← PHẢI có dòng này
   (nếu thấy dấu * trước giờ = CHƯA đồng bộ — Module-06B §3.5)
show ntp status | include synchronized|stratum
```

> ⭐ **Nhắc lại [Module-06B §3.5](Module-06B-NAT-NTP-Multicast.md):** ⭐ **dấu `*` trước giờ = giờ không đáng tin** ·
> ⭐ **`stratum 16` = chưa sync** · ⭐ **`reach 377` = 8/8 gói tốt.**

---

## 📘 4. 🔴 ⭐⭐ SYSLOG (blueprint 4.2 — CONFIGURE AND VERIFY)

### 4.1 ⭐⭐ TÁM MỨC SEVERITY — bảng phải thuộc lòng

| Mức | Tên | ⭐ Nghĩa | Ví dụ thật |
|:---:|---|---|---|
| ⭐ **0** | **Emergency** | ⭐ **Hệ thống KHÔNG DÙNG ĐƯỢC** | Sắp sập nguồn |
| ⭐ **1** | **Alert** | ⭐ **Cần hành động NGAY** | Nhiệt độ vượt ngưỡng nguy hiểm |
| ⭐ **2** | **Critical** | Tình trạng nghiêm trọng | Lỗi phần cứng, quạt hỏng |
| ⭐ **3** | **Error** | Có lỗi | ⭐ `%LINK-3-UPDOWN` — interface xuống |
| ⭐ **4** | **Warning** | Cảnh báo | ⭐ `%SYS-4-CONFIG_RESOLVE_FAILURE` |
| ⭐ **5** | **Notification** | ⭐ **Bình thường nhưng đáng chú ý** | ⭐ `%LINEPROTO-5-UPDOWN` · `%SYS-5-CONFIG_I` (ai đó vừa sửa config) |
| ⭐ **6** | **Informational** | Thông tin | ⭐ `%SEC-6-IPACCESSLOGP` — ACL chặn gói |
| ⭐ **7** | **Debugging** | ⭐ **Output của `debug`** | Rất nhiều, rất nhanh |

> ⭐⭐ **Mẹo nhớ tiếng Anh:** ⭐ **"Every Awesome Cisco Engineer Will Need Ice-cream Daily"**
> = **E**mergency · **A**lert · **C**ritical · **E**rror · **W**arning · **N**otification · **I**nformational · **D**ebugging
>
> 🔴 ⭐⭐ **ĐIỀU QUAN TRỌNG NHẤT: SỐ CÀNG NHỎ = CÀNG NGHIÊM TRỌNG.**
> ⭐ **0 là tệ nhất, 7 là nhẹ nhất.** ⭐ Nhiều người nhớ ngược.

### 4.2 🔴 ⭐⭐ `logging trap <mức>` lọc như thế nào — bẫy đề kinh điển

```
   logging trap 4   →  GỬI ĐI CÁC MỨC 0, 1, 2, 3, VÀ 4
                            (tức là "mức 4 TRỞ XUỐNG SỐ", = nghiêm trọng hơn hoặc bằng)
                            KHÔNG gửi mức 5, 6, 7
```

| Cấu hình | ⭐ Gửi những mức nào | Số lượng log |
|---|---|---|
| `logging trap 0` (emergencies) | Chỉ 0 | Rất ít |
| ⭐ `logging trap 4` (warnings) | ⭐ **0–4** | Vừa phải |
| ⭐ `logging trap 6` (informational) | ⭐ **0–6** | ⭐ **Mặc định cho syslog server** |
| 🔴 `logging trap 7` (debugging) | ⭐ **0–7** | 🔴 ⭐ **Rất nhiều — cẩn thận** |

> 🔴 ⭐⭐ **Câu hỏi đề:** *"`logging trap 4` gửi những severity nào lên server?"*
> ⭐ **Đáp án: 0, 1, 2, 3, 4** — ⭐ **KHÔNG phải "chỉ mức 4"**, ⭐ **cũng KHÔNG phải "4 trở lên (5,6,7)"**.
>
> ⭐ **Cách nhớ:** ⭐ *"Bạn khai báo NGƯỠNG NGHIÊM TRỌNG TỐI THIỂU. Cái gì nghiêm trọng bằng
> hoặc hơn ngưỡng đó thì được gửi."*

### 4.3 ⭐ Năm nơi log có thể đi tới

| Đích | Lệnh | Mức mặc định | ⭐ Ghi chú |
|---|---|:---:|---|
| ⭐ **Console** | `logging console <mức>` | ⭐ **7 (debugging)** | 🔴 ⭐⭐ **Console là ĐỒNG BỘ và CHẬM** — log nhiều **làm treo router**. ⭐ **Nên hạ xuống `warnings`** |
| ⭐ **Monitor (VTY)** | `logging monitor <mức>` | 7 | ⭐ **Phải gõ `terminal monitor`** mới thấy khi SSH |
| ⭐⭐ **Buffer (RAM)** | `logging buffered <bytes> <mức>` | 7 | ⭐⭐ **Nơi bạn xem bằng `show logging`.** ⭐ **Công cụ chính khi lab** |
| ⭐⭐ **Syslog server** | `logging host <ip>` + `logging trap <mức>` | ⭐ **6** | ⭐ **UDP 514** |
| **SNMP trap** | `snmp-server enable traps syslog` | — | Gửi log dạng SNMP trap |

### 4.4 ⭐⭐ Cấu hình đầy đủ

```
! ─── ① Nền thời gian (§2) ───
service timestamps log datetime msec localtime show-timezone
service sequence-numbers

! ─── ② Buffer trên RAM ───
logging buffered 64000 debugging          ! 64 KB, nhận tới mức 7

! ─── ③ GIẢM SPAM CONSOLE — rất quan trọng ───
logging console warnings                  ! chỉ 0–4 ra console
   ! hoặc mạnh tay: no logging console

! ─── ④ VTY ───
logging monitor debugging                   ! nhớ gõ "terminal monitor" khi SSH

! ─── ⑤ SYSLOG SERVER TỪ XA (chính là mục 4.2) ───
logging host 10.99.1.20
   ! (cú pháp mới, chỉ định rõ transport/port:)
   ! logging host 10.99.1.20 transport udp port 514
logging trap informational                ! = mức 6 → gửi 0–6
logging source-interface Loopback0        ! IP nguồn CỐ ĐỊNH — server dễ nhận diện
logging origin-id hostname                  ! nhét tên thiết bị vào mỗi dòng
logging facility local6                     ! để server phân loại

! ─── ⑥ Chống nghẽn khi bão log ───
logging rate-limit 50 except errors         ! tối đa 50 msg/s, trừ lỗi nghiêm trọng
```

> ⭐⭐ **Ba dòng đáng giá nhất trong khối trên:**
> 1. ⭐⭐ **`logging source-interface Loopback0`** — không có nó, thiết bị nhiều interface sẽ gửi log
>    với **IP nguồn thay đổi** → ⭐ **server tưởng là nhiều thiết bị khác nhau.**
> 2. ⭐⭐ **`logging console warnings`** — ⭐ **cứu router khỏi treo** khi có bão log hoặc khi bạn bật debug.
> 3. ⭐ **`service sequence-numbers`** — ⭐ **biết ngay nếu có dòng log bị mất** (UDP 514 không đảm bảo).

### 4.5 ⭐⭐ Đọc một dòng syslog — mổ xẻ từng phần

```
000123: Sep 10 14:23:11.456 ICT: %LINEPROTO-5-UPDOWN: Line protocol on Interface
        GigabitEthernet0/0, changed state to up
└──┬──┘ └──────────┬──────────┘  └────┬────┘└┬┘└──┬──┘  └───────────┬──────────────┘
   │               │                  │      │    │                 │
   │               │                  │      │    │            MÔ TẢ
   │               │                  │      │    └── MNEMONIC (tên sự kiện)
   │               │                  │      └────── SEVERITY (5 = Notification)
   │               │                  └───────────── FACILITY (hệ thống con nào)
   │               └──────────────────────────────── TIMESTAMP (nhờ service timestamps)
   └──────────────────────────────────────────────── SEQUENCE (nhờ service sequence-numbers)
```

⭐⭐ **Định dạng chuẩn:** `%FACILITY-SEVERITY-MNEMONIC: mô tả`

> 🔴 ⭐⭐ **Bẫy hay: cùng một sự kiện "rút cáp" sinh ra HAI dòng log ở HAI severity khác nhau:**
>
> ```
> %LINK-3-UPDOWN: Interface GigabitEthernet0/0, changed state to down
>       └─ ⭐ severity 3 (Error)  — LỚP VẬT LÝ (Layer 1)
>
> %LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/0, changed state to down
>       └─ ⭐ severity 5 (Notification) — GIAO THỨC ĐƯỜNG TRUYỀN (Layer 2)
> ```
> ⭐ **Hệ quả thực tế rất quan trọng:** nếu bạn đặt ⭐ **`logging trap 4`**, bạn sẽ ⭐ **nhận được
> `%LINK-3` nhưng KHÔNG nhận được `%LINEPROTO-5`** → ⭐ **thấy interface down mà không thấy nó up lại.**

⭐ **Vài facility hay gặp:**

| Facility | Nghĩa |
|---|---|
| ⭐ `%LINK` | Trạng thái vật lý interface |
| ⭐ `%LINEPROTO` | Trạng thái line protocol |
| ⭐ `%SYS` | Hệ thống chung — ⭐ `%SYS-5-CONFIG_I` = **ai đó vừa sửa config** |
| ⭐ `%OSPF` / `%BGP` / `%DUAL` | Giao thức định tuyến |
| ⭐ `%SEC` | ⭐ ACL chặn gói (`%SEC-6-IPACCESSLOGP`) |
| ⭐ `%SEC_LOGIN` | ⭐ Đăng nhập thất bại / quiet-mode *(Module-10 §2.4)* |
| ⭐ `%SPANTREE` | STP — ⭐ root change, BPDU Guard |
| ⭐ `%DOT1X` / `%AUTHMGR` / `%MAB` | 802.1X *(Module-10 §6)* |
| ⭐ `%TUN` | ⭐ Tunnel — `%TUN-5-RECURDOWN` *(Module-08 §4.3)* |
| ⭐ `%NAT` | `%NAT-4-ADDR_ALLOC_FAILURE` *(Module-06B)* |

### 4.6 ⭐ Verify syslog

```
show logging                              ! lệnh chính — cấu hình + toàn bộ buffer
show logging | include %LINK|%LINEPROTO     ! lọc theo facility
show logging | include Sep 10 14:           ! lọc theo giờ
show logging count                          ! đếm số message theo facility
clear logging                                ! xóa buffer trước khi tái hiện lỗi
terminal monitor  /  terminal no monitor    ! bật/tắt xem log trên phiên SSH
```

⭐ **Đọc phần đầu của `show logging` — đây là nơi kiểm tra cấu hình:**
```
Syslog logging: enabled (0 messages dropped, 0 flushes, 0 overruns)
    Console logging: level warnings, 45 messages logged      ← mức console
    Monitor logging: level debugging, 0 messages logged
    Buffer logging: level debugging, 312 messages logged     ← buffer
    Trap logging: level informational, 289 message lines logged
        Logging to 10.99.1.20 (udp port 514, audit disabled,
              link up), 289 message lines logged, 0 message lines dropped
```

| Dòng cần soi | ⭐ Ý nghĩa |
|---|---|
| ⭐ `messages dropped` | 🔴 **> 0** = buffer đầy hoặc quá tải → tăng buffer / giảm mức |
| ⭐ `link up` sau IP server | ⭐ Router **tới được** syslog server |
| ⭐ `message lines dropped` | 🔴 **> 0** = không gửi kịp lên server |

---

## 📘 5. ⭐⭐ SNMP (blueprint 4.1)

### 5.1 ⭐ Bốn thành phần

```
   ┌────────────────┐                          ┌─────────────────────┐
   │  MANAGER    │ ── Get/GetNext/GetBulk ──►│  AGENT           │
   │  (NMS: PRTG,   │      UDP 161           │  (router/switch)    │
   │   Zabbix,      │                           │                     │
   │   SolarWinds)  │ ◄──── Response ───────────│  ┌───────────────┐  │
   │                │                           │  │  MIB       │  │
   │                │ ◄─── Trap / Inform ───────│  │ (cây dữ liệu) │  │
   │                │      UDP 162           │  └───────────────┘  │
   └────────────────┘                          └─────────────────────┘
```

| Thành phần | ⭐ Là gì |
|---|---|
| ⭐ **Manager (NMS)** | Máy chủ giám sát — **hỏi** và **nhận cảnh báo** |
| ⭐ **Agent** | Phần mềm trên thiết bị — **trả lời** và **gửi cảnh báo** |
| ⭐ **MIB** | ⭐ **Cây dữ liệu** mô tả những gì đo được (CPU, interface, nhiệt độ…) |
| ⭐ **OID** | ⭐ **Địa chỉ của một mục trong cây MIB** — VD `1.3.6.1.2.1.1.5.0` = sysName |

> ⭐⭐ **Hai port phải nhớ:**
> ⭐ **UDP 161** — **agent lắng nghe** (manager hỏi vào đây)
> ⭐ **UDP 162** — **manager lắng nghe** (trap/inform gửi vào đây)
>
> ⭐ **Mẹo nhớ:** ⭐ **161 là "hỏi đáp bình thường", 162 là "báo động khẩn"** — số lớn hơn cho việc gấp hơn.

### 5.2 ⭐⭐ Các thao tác — và cặp Trap vs Inform

| Thao tác | Ai khởi xướng | ⭐ Ghi chú |
|---|---|---|
| **Get** | Manager | Lấy **một** OID |
| **GetNext** | Manager | Lấy OID **kế tiếp** — dùng để "đi bộ" qua cây (`snmpwalk`) |
| ⭐ **GetBulk** | Manager | ⭐ Lấy **nhiều OID một lần** — ⭐ **chỉ có từ v2c** |
| **Set** | Manager | ⭐ **GHI** giá trị — ⭐ đây là lý do community RW rất nguy hiểm |
| ⭐⭐ **Trap** | ⭐ **Agent** | ⭐⭐ **Bắn đi rồi quên — KHÔNG có xác nhận** |
| ⭐⭐ **Inform** | ⭐ **Agent** | ⭐⭐ **CÓ xác nhận — không nhận được ACK thì GỬI LẠI.** ⭐ Chỉ có từ **v2c** |
| **Response** | Agent | Trả lời cho Get/Set |

> 🔴 ⭐⭐ **Trap vs Inform — câu hỏi đề kinh điển:**
>
> | | ⭐ **Trap** | ⭐ **Inform** |
> |---|---|---|
> | Xác nhận | 🔴 ⭐ **Không** (fire-and-forget) | ⭐ **Có (ACK)** |
> | Mất gói thì sao | 🔴 ⭐ **MẤT LUÔN, không ai biết** | ⭐ **Gửi lại** |
> | Tốn tài nguyên | ⭐ Ít | ⭐ Nhiều hơn (phải giữ trong bộ nhớ chờ ACK) |
> | Có từ phiên bản | v1 | ⭐ **v2c trở lên** |
>
> ⭐ **Chọn:** ⭐ **cảnh báo quan trọng (thiết bị sắp chết) → Inform.**
> ⭐ **Sự kiện thường xuyên, mất một cái không sao → Trap.**

### 5.3 ⭐⭐ v1 vs v2c vs v3 — bảng phải thuộc

| | **v1** | ⭐ **v2c** | ⭐⭐ **v3** |
|---|---|---|---|
| ⭐ **Xác thực** | ⭐ **Community string** | ⭐ **Community string** | ⭐⭐ **Username + mật khẩu (USM)** |
| 🔴 ⭐ **Bảo mật** | 🔴 ⭐ **Plaintext trên đường truyền** | 🔴 ⭐ **Plaintext** | ⭐⭐ **Xác thực + MÃ HÓA** |
| GetBulk | ❌ | ⭐ **Có** | Có |
| Inform | ❌ | ⭐ **Có** | Có |
| Toàn vẹn dữ liệu | ❌ | ❌ | ⭐ **Có** |
| ⭐ Nên dùng | 🔴 Không | ⚠️ Chỉ trong mạng quản trị cách ly | ⭐⭐ **Đây là lựa chọn đúng** |

⭐⭐ **BA MỨC BẢO MẬT CỦA v3 — đề hỏi rất nhiều:**

| Mức | Xác thực | Mã hóa | ⭐ Nghĩa |
|---|:---:|:---:|---|
| ⭐ **noAuthNoPriv** | ❌ | ❌ | Chỉ có username — ⭐ **gần như v2c** |
| ⭐ **authNoPriv** | ✅ **MD5/SHA** | ❌ | ⭐ **Biết chắc ai gửi, nhưng dữ liệu vẫn đọc được** |
| ⭐⭐ **authPriv** | ✅ **MD5/SHA** | ⭐✅ **DES/3DES/AES** | ⭐⭐ **Mức duy nhất nên dùng thật** |

> ⭐ **Mẹo nhớ:** ⭐ **"auth" = xác thực (anh là ai)** · ⭐ **"priv" = privacy = MÃ HÓA (không ai đọc trộm)**.
> ⭐ **`authPriv` = có cả hai.**

### 5.4 ⭐ Cấu hình

```
!═══════ SNMPv2c (chỉ dùng khi buộc phải) ═══════
ip access-list standard ACL-SNMP
 permit 10.99.1.0 0.0.0.255
 deny   any log
!
snmp-server community CTY-Read-0nly RO ACL-SNMP     ! RO + KHÓA BẰNG ACL
   ! TRÁNH community RW nếu không thật sự cần — nó cho phép GHI cấu hình
snmp-server location "DC1 - Rack 12 - U20"
snmp-server contact "netops@cty.local"
snmp-server host 10.99.1.30 version 2c CTY-Read-0nly
snmp-server enable traps snmp linkdown linkup coldstart
snmp-server enable traps config
snmp-server enable traps cpu threshold
snmp-server source-interface informs Loopback0

!═══════ SNMPv3 (nên dùng) ═══════
! ① View — quyết định NHÌN ĐƯỢC phần nào của cây MIB
snmp-server view VIEW-ALL iso included
   ! (hạn chế hơn:  snmp-server view VIEW-IF ifTable included)
!
! ② Group — gắn view + mức bảo mật + ACL
snmp-server group GRP-MONITOR v3 priv read VIEW-ALL access ACL-SNMP
!                                  └┬─┘
!                                   "priv" = yêu cầu authPriv
!
! ③ User — thuộc group, có mật khẩu xác thực và mật khẩu mã hóa
snmp-server user netops GRP-MONITOR v3 auth sha AuthPass2026 priv aes 128 PrivPass2026
!                                        └───┬───┘             └─────┬─────┘
!                                       XÁC THỰC            MÃ HÓA
!
! ④ Đích nhận trap
snmp-server host 10.99.1.30 version 3 priv netops
```

> ⭐⭐ **Thứ tự bắt buộc: VIEW → GROUP → USER.** ⭐ Group tham chiếu view, user tham chiếu group.
> ⭐ Gõ sai thứ tự thì IOS báo lỗi hoặc tạo ra cấu hình không hoạt động.

### 5.5 ⭐ Verify SNMP

```
show snmp                        ! thống kê tổng, số gói vào/ra
show snmp community                ! (v2c — có thể bị ẩn vì lý do bảo mật)
show snmp user                   ! v3: user, engineID, auth/priv protocol
show snmp group                  ! group đang dùng view nào, mức bảo mật gì
show snmp view
show snmp host                   ! đang gửi trap/inform đi đâu
show snmp engineID
debug snmp packet                  ! ⚠️ chỉ lab
```

⭐ **Đọc `show snmp user`:**
```
User name: netops
Engine ID: 800000090300AABBCC001100
storage-type: nonvolatile        active
Authentication Protocol: SHA          ← xác thực
Privacy Protocol: AES128              ← mã hóa → đây là authPriv ✅
Group-name: GRP-MONITOR
```
> ⭐ **Nếu `Privacy Protocol: None`** → ⭐ **user này chỉ ở mức `authNoPriv`**, dữ liệu **không được mã hóa.**

---

## 📘 6. 🔴 ⭐⭐ NETFLOW & FLEXIBLE NETFLOW (blueprint 4.3 — CONFIGURE AND VERIFY)

### 6.1 ⭐⭐ NetFlow là gì — và khác SPAN chỗ nào

> ⭐ **NetFlow ghi lại "AI nói chuyện với AI, bao nhiêu, khi nào"** — ⭐ **metadata**, không phải nội dung.

| | ⭐⭐ **NetFlow** | ⭐⭐ **SPAN** *(§6)* |
|---|---|---|
| Thu thập gì | ⭐ **Tóm tắt luồng** (IP, port, số byte, số gói) | ⭐ **Bản sao TOÀN BỘ gói** |
| Tải lên thiết bị | ⭐ **Nhẹ** | 🔴 ⭐ **Nặng** |
| Băng thông xuất ra | ⭐ **Rất nhỏ** (~1–2% traffic) | 🔴 ⭐ **Bằng đúng traffic được sao chép** |
| Chạy liên tục 24/7? | ⭐ ✅ **Được** | 🔴 ❌ Chỉ bật khi cần |
| ⭐ Trả lời câu hỏi | ⭐⭐ ***"AI đang ăn hết băng thông?"*** · *"Traffic đi đâu?"* | ⭐⭐ ***"Chính xác trong gói tin đó có gì?"*** |
| Xem được nội dung gói | 🔴 ❌ | ✅ Có |

> ⭐⭐ **Câu chốt:** ⭐ **NetFlow = hóa đơn điện thoại** (ai gọi ai, bao lâu, lúc nào — nhưng không nghe được nội dung).
> ⭐ **SPAN = nghe lén cuộc gọi** (nghe được hết, nhưng không thể nghe mọi cuộc mọi lúc).

### 6.2 ⭐⭐ NetFlow truyền thống — 7 trường định nghĩa một FLOW

```
   HAI GÓI THUỘC CÙNG MỘT FLOW khi CẢ BẢY trường sau GIỐNG NHAU:

   ① Source IP address
   ② Destination IP address
   ③ Source port
   ④ Destination port
   ⑤ Layer 3 protocol type       (TCP=6, UDP=17, ICMP=1)
   ⑥ ToS byte  (DSCP)            — trường hay bị quên nhất
   ⑦ Input logical interface

   Khác MỘT trường thôi  →  ĐÃ LÀ FLOW KHÁC
```

> 🔴 ⭐⭐ **Bẫy đề:** *"Kể 7 trường của NetFlow truyền thống."*
> ⭐ Người ta hay quên ⭐ **ToS/DSCP (⑥)** và ⭐ **input interface (⑦)** — chỉ nhớ 5 cái đầu (5-tuple).
> ⭐ **Nhớ: 5-tuple là của FIREWALL. NetFlow là 7-tuple** (thêm **ToS** và **input interface**).

⭐ **Các phiên bản:**

| Phiên bản | Đặc điểm |
|---|---|
| ⭐ **v5** | ⭐ **Cố định, chỉ IPv4** — phổ biến nhất thời cũ, không mở rộng được |
| ⭐⭐ **v9** | ⭐⭐ **Dựa trên TEMPLATE** → linh hoạt, hỗ trợ **IPv6, MPLS, VLAN**. ⭐ **Nền của Flexible NetFlow** |
| ⭐ **IPFIX (v10)** | ⭐ **Chuẩn IETF**, dựa trên v9. RFC 7011 |

### 6.3 ⭐⭐ FLEXIBLE NETFLOW — BỐN THÀNH PHẦN (phần quan trọng nhất §5)

```
   ┌──────────────────┐        ┌────────────────────┐
   │ FLOW RECORD   │        │ FLOW EXPORTER   │
   │ "ĐO CÁI GÌ"      │        │ "GỬI ĐI ĐÂU"       │
   │ · match = KEY    │        │ · destination IP   │
   │ · collect =      │        │ · port, version    │
   │   NON-KEY        │        │ · source interface │
   └────────┬─────────┘        └─────────┬──────────┘
            └────────────┬───────────────┘
                         ▼
              ┌─────────────────────┐
              │ FLOW MONITOR   │  ← ghép record + exporter + CACHE
              └──────────┬──────────┘
                         │  (+ FLOW SAMPLER — tùy chọn, lấy mẫu 1/N gói)
                         ▼
                 ┌───────────────┐
                 │ INTERFACE  │  ip flow monitor <FM> input|output
                 └───────────────┘
```

| # | Thành phần | ⭐ Trả lời câu hỏi |
|:---:|---|---|
| ⭐⭐ **1** | **Flow Record** | ⭐ *"Cái gì tạo nên một flow, và tôi muốn ghi lại thông tin gì?"* |
| ⭐⭐ **2** | **Flow Exporter** | ⭐ *"Gửi dữ liệu về collector nào, bằng giao thức nào?"* |
| ⭐⭐ **3** | **Flow Monitor** | ⭐ *"Ghép record với exporter, và giữ cache ở đâu?"* |
| ⭐ **4** | **Flow Sampler** *(tùy chọn)* | ⭐ *"Link 100 Gbps quá nhanh — lấy mẫu 1 trên N gói thôi"* |

#### 🔴 ⭐⭐ `match` vs `collect` — phân biệt SỐNG CÒN

| | ⭐⭐ **`match`** | ⭐⭐ **`collect`** |
|---|---|---|
| Gọi là | ⭐ **KEY field** | ⭐ **NON-KEY field** |
| Vai trò | ⭐⭐ **ĐỊNH NGHĨA flow** — khác giá trị = **flow KHÁC** | ⭐ **Chỉ ghi lại thêm** — không tạo flow mới |
| Ví dụ | source IP, dest IP, port, protocol | số byte, số gói, timestamp, output interface |

> 🔴 ⭐⭐ **Hệ quả phải hiểu:** ⭐ **thêm một `match` = số flow trong cache có thể TĂNG VỌT.**
>
> ⭐ **Ví dụ:** nếu bạn `match transport source-port`, thì mỗi lần một client mở kết nối mới
> (source port ngẫu nhiên khác nhau) → ⭐ **một flow mới.** ⭐ Một máy duyệt web có thể tạo hàng trăm flow.
>
> 🔴 ⭐ **Cache đầy → flow bị đẩy ra sớm → số liệu sai.** ⭐ **Chỉ `match` những gì thật sự cần phân biệt.**

### 6.4 ⭐⭐ Cấu hình Flexible NetFlow

```
!═══════ ① FLOW RECORD — đo cái gì ═══════
flow record FR-IPV4
 description Ghi nhan luu luong IPv4
 ! ─── KEY FIELDS (match) — định nghĩa flow ───
 match ipv4 source address
 match ipv4 destination address
 match ipv4 protocol
 match transport source-port
 match transport destination-port
 match ipv4 tos
 match interface input
 ! ─── NON-KEY FIELDS (collect) — ghi thêm ───
 collect counter bytes
 collect counter packets
 collect interface output
 collect timestamp sys-uptime first
 collect timestamp sys-uptime last
 collect transport tcp flags

!═══════ ② FLOW EXPORTER — gửi đi đâu ═══════
flow exporter FE-COLLECTOR
 destination 10.99.1.40
 source Loopback0                     ! IP nguồn cố định
 transport udp 2055                   ! port phổ biến (2055, 9995, 9996)
 export-protocol netflow-v9
 template data timeout 60               ! gửi lại template mỗi 60s
 option interface-table                 ! gửi kèm bảng tên interface

!═══════ ③ FLOW MONITOR — ghép lại + cache ═══════
flow monitor FM-IPV4
 record FR-IPV4
 exporter FE-COLLECTOR
 cache timeout active 60              ! QUAN TRỌNG — xem cảnh báo dưới
 cache timeout inactive 15
 cache entries 4096

!═══════ ④ ÁP LÊN INTERFACE ═══════
interface GigabitEthernet0/0
 ip flow monitor FM-IPV4 input
 ip flow monitor FM-IPV4 output

!═══════ ⑤ (tùy chọn) SAMPLER cho link tốc độ cao ═══════
sampler SAMP-1-IN-100
 mode random 1 out-of 100
!
interface TenGigabitEthernet0/1
 ip flow monitor FM-IPV4 sampler SAMP-1-IN-100 input
```

> 🔴 ⭐⭐ **`cache timeout active` — con số quan trọng nhất và hay sai nhất:**
>
> | Timeout | Nghĩa | Mặc định |
> |---|---|:---:|
> | ⭐⭐ **active** | ⭐ **Flow ĐANG CHẠY bị đẩy lên collector sau bao lâu** | 🔴 ⭐ **1800 giây (30 PHÚT!)** |
> | ⭐ **inactive** | Flow **im lặng** bao lâu thì coi là kết thúc | 15 giây |
>
> 🔴 ⭐⭐ **Với mặc định 1800s: một cuộc tải file kéo dài 25 phút sẽ KHÔNG xuất hiện trên collector
> cho tới khi nó kết thúc.** ⭐ Bạn nhìn biểu đồ và tưởng mạng đang rảnh — ⭐ **trong khi nó đang nghẽn.**
>
> ⭐ **Thực tế: đặt `cache timeout active 60`** để có số liệu gần thời gian thực.

### 6.5 ⭐⭐ Verify — và LAB không cần collector

```
show flow record FR-IPV4                        ! xem lại record
show flow exporter FE-COLLECTOR                 ! cấu hình exporter
show flow exporter FE-COLLECTOR statistics    ! đã gửi bao nhiêu gói, lỗi không
show flow monitor FM-IPV4                       ! cấu hình monitor
show flow monitor FM-IPV4 cache              ! XEM TOÀN BỘ FLOW — LỆNH HAY NHẤT
show flow monitor FM-IPV4 cache format table  ! dạng bảng, dễ đọc hơn nhiều
show flow monitor FM-IPV4 statistics            ! số flow, cache có đầy không
show flow interface GigabitEthernet0/0          ! interface nào đang chạy monitor nào
```

> ⭐⭐ **Đây là điểm tuyệt vời của Flexible NetFlow khi lab:**
> ⭐ **`show flow monitor <FM> cache` cho bạn xem TOÀN BỘ bảng flow NGAY TRÊN ROUTER** —
> ⭐ **không cần collector, không cần server nào cả.**

⭐ **Đọc cache dạng bảng:**
```
R1# show flow monitor FM-IPV4 cache format table

  IPV4 SRC ADDR   IPV4 DST ADDR   TRNS SRC PORT  TRNS DST PORT  IP PROT   bytes  pkts
  ==============  ==============  =============  =============  =======   ========  ======
  10.1.1.10       8.8.8.8                 53124             53         17       248       4
  10.1.1.10       203.0.113.50            49832            443          6   1458200    1024
  10.1.1.20       203.0.113.50            51004            443          6      8420      18
```
⭐ **Đọc ngay ra:** ⭐ **`10.1.1.10` đang tải ~1.4 MB qua HTTPS tới `203.0.113.50`** —
⭐ **đó chính là "ai đang ăn băng thông".**

```
R1# show flow monitor FM-IPV4 statistics
  Cache type:                Normal (Platform cache)
  Cache size:                4096
  Current entries:          237
  High Watermark:           891
  Flows added:               15420
  Flows aged:               15183
    - Active timeout    (60 secs)     402
    - Inactive timeout  (15 secs)     14781
  - Emergency aged                  0      ← >0 nghĩa là CACHE ĐÃ ĐẦY
```
> 🔴 ⭐ **`Emergency aged > 0`** = ⭐ **cache đầy, flow bị đẩy ra sớm → số liệu KHÔNG chính xác.**
> ⭐ **Sửa: tăng `cache entries`, hoặc giảm số `match`, hoặc bật sampler.**

---

## 📘 7. 🔴 ⭐⭐ SPAN / RSPAN / ERSPAN (blueprint 4.4 — CONFIGURE AND VERIFY)

### 7.1 ⭐⭐ Bảng ba loại — học thuộc

```
   SPAN (local)          RSPAN (qua L2)              ERSPAN (qua L3)

   ┌──────────┐         ┌──────┐  ┌──────┐          ┌──────┐        ┌──────┐
   │  SW1     │         │ SW1  │══│ SW2  │          │ SW1  │≈≈GRE≈≈≈│ SW9  │
   │ src→dst  │         │ src  │  │ dst  │          │ src  │ (định  │ dst  │
   └──────────┘         └──────┘  └──────┘          └──────┘ tuyến) └──────┘
   Cùng 1 switch      Qua RSPAN VLAN           Qua mạng ĐÃ ĐỊNH TUYẾN
                        (phải trunk suốt đường)      (đi được BẤT KỲ ĐÂU)
```

| | ⭐ **SPAN** (local) | ⭐ **RSPAN** | ⭐⭐ **ERSPAN** |
|---|---|---|---|
| ⭐ **Phạm vi** | ⭐ **Cùng MỘT switch** | ⭐ **Qua nhiều switch, cùng L2** | ⭐⭐ **Qua mạng ĐỊNH TUYẾN (L3)** |
| ⭐ **Vận chuyển bằng** | Nội bộ switch | ⭐⭐ **VLAN RSPAN chuyên dụng** | ⭐⭐ **Đường hầm GRE** |
| Yêu cầu | Không | ⭐ **RSPAN VLAN phải tạo trên MỌI switch trên đường đi + trunk cho qua** | ⭐ Có IP kết nối giữa hai đầu |
| ⭐ Overhead | Thấp | Trung bình | ⭐ **Cao (thêm header GRE)** |
| Hỗ trợ | Mọi switch | Hầu hết switch quản lý được | ⭐ **Thiết bị cao cấp hơn** |
| ⭐ Dùng khi | Máy phân tích **cắm ngay tại switch đó** | Máy phân tích ở **switch khác cùng campus** | ⭐ **Máy phân tích ở DC/site khác** |

> ⭐ **Mẹo nhớ:** ⭐ **S**PAN = **S**ame switch · ⭐ **R**SPAN = **R**emote qua VLAN (L2) ·
> ⭐ **E**RSPAN = **E**ncapsulated qua GRE (L3, đi đâu cũng được).

### 7.2 ⭐⭐ SPAN cục bộ — cấu hình và những giới hạn phải biết

```
! Sao chép traffic của port Gi1/0/1 sang port Gi1/0/24 (máy phân tích cắm ở đó)
monitor session 1 source interface GigabitEthernet1/0/1 both
monitor session 1 destination interface GigabitEthernet1/0/24

! Các biến thể nguồn:
monitor session 1 source interface Gi1/0/1 rx        ! chỉ chiều VÀO
monitor session 1 source interface Gi1/0/1 tx        ! chỉ chiều RA
monitor session 1 source interface Gi1/0/1 - 4          ! nhiều port
monitor session 1 source vlan 10                      ! cả một VLAN (VSPAN)

! Đích có thể thêm tùy chọn:
monitor session 1 destination interface Gi1/0/24 encapsulation replicate
!                                                 └─ giữ nguyên tag 802.1Q/CDP/STP
monitor session 1 destination interface Gi1/0/24 ingress vlan 10
!                                                └─ cho phép cổng đích vẫn NHẬN traffic
```

> 🔴 ⭐⭐ **BỐN GIỚI HẠN PHẢI NHỚ — đề hỏi và ngoài đời cũng vấp:**
>
> | # | Giới hạn | Hệ quả |
> |:---:|---|---|
> | ⭐⭐ **1** | ⭐⭐ **Cổng ĐÍCH trở thành "câm"** — ⭐ **ngừng chuyển traffic bình thường**, ⭐ **không tham gia STP**, ⭐ **không học MAC** | 🔴 ⭐ **Cắm nhầm SPAN destination vào cổng đang có người dùng = người đó MẤT MẠNG** |
> | ⭐ **2** | ⭐ Một port **không thể vừa là source vừa là destination** trong cùng session | — |
> | ⭐⭐ **3** | ⭐⭐ **Oversubscription** — nhiều nguồn đổ vào một đích | 🔴 ⭐ **10 port 1 Gbps → 1 port 1 Gbps = MẤT GÓI.** ⭐ Bạn phân tích trên dữ liệu **thiếu** mà không biết |
> | ⭐ **4** | ⭐ **Số session bị giới hạn** (thường **2–4** local, tùy nền tảng) | Không bật được nhiều phiên cùng lúc |
>
> ⭐ **Giới hạn 3 là cái nguy hiểm nhất** vì nó **im lặng** — không có cảnh báo, chỉ là gói bị rơi.

```
show monitor session 1
show monitor session all
show monitor session 1 detail
```
```
Session 1
---------
Type                   : Local Session
Source Ports         :
    Both               : Gi1/0/1
Destination Ports    : Gi1/0/24
    Encapsulation      : Native
```

### 7.3 ⭐ RSPAN — qua nhiều switch trong cùng L2

```
!═══ BƯỚC 0: TẠO RSPAN VLAN TRÊN **MỌI** SWITCH TRÊN ĐƯỜNG ĐI ═══
!    (switch nguồn, các switch trung gian, VÀ switch đích)
vlan 999
 name RSPAN-VLAN
 remote-span                          ! DÒNG BẮT BUỘC — quên là hỏng

!═══ SWITCH NGUỒN ═══
monitor session 1 source interface GigabitEthernet1/0/1 both
monitor session 1 destination remote vlan 999

!═══ SWITCH ĐÍCH ═══
monitor session 2 source remote vlan 999
monitor session 2 destination interface GigabitEthernet1/0/24

!═══ TRÊN MỌI TRUNK TRÊN ĐƯỜNG ĐI ═══
interface GigabitEthernet1/0/48
 switchport mode trunk
 switchport trunk allowed vlan add 999    ! PHẢI cho VLAN 999 đi qua
```

> 🔴 ⭐⭐ **Ba lỗi RSPAN kinh điển:**
> 1. ⭐⭐ **Quên `remote-span`** trên một switch nào đó → ⭐ **VLAN đó thành VLAN thường** → traffic sao chép
>    bị **flood ra khắp nơi** hoặc không tới đích.
> 2. ⭐⭐ **Quên cho VLAN 999 qua trunk** ở một chặng → ⭐ **không tới được switch đích.**
> 3. ⭐ **Quên tạo VLAN trên switch trung gian** — ⭐ **nó cũng phải có `remote-span`**, dù không cắm gì.
>
> ⭐ **Đặc điểm RSPAN VLAN:** ⭐ **không học MAC, không chở traffic người dùng thường** — nó là VLAN chuyên dụng.

### 7.4 ⭐⭐ ERSPAN — vượt qua mạng định tuyến

```
!═══ PHÍA NGUỒN ═══
monitor session 1 type erspan-source
 source interface GigabitEthernet0/1 both
 no shutdown
 destination
  erspan-id 100                        ! PHẢI KHỚP hai đầu
  ip address 10.99.1.50                ! IP của đầu nhận
  origin ip address 10.1.1.1           ! IP nguồn của tunnel GRE

!═══ PHÍA ĐÍCH ═══
monitor session 2 type erspan-destination
 destination interface GigabitEthernet0/2
 no shutdown
 source
  erspan-id 100                        ! khớp với đầu kia
  ip address 10.99.1.50
```

> ⭐⭐ **Ba điều phải nhớ về ERSPAN:**
> 1. ⭐⭐ **Nó dùng GRE** → ⭐ **cùng vấn đề MTU như [Module-08 §4.4](Module-08-Virtualization-va-Overlay.md)**.
>    🔴 ⭐ **Gói sao chép 1500 byte + header GRE → vượt MTU → bị phân mảnh hoặc DROP** →
>    ⭐ **bản capture của bạn thiếu gói mà bạn không biết.**
> 2. ⭐⭐ **`erspan-id` phải khớp** hai đầu — nó phân biệt nhiều phiên ERSPAN chạy song song.
> 3. 🔴 ⭐ **ERSPAN tiêu tốn băng thông thật trên mạng sản xuất** — ⭐ **sao chép 1 Gbps traffic
>    = thêm 1 Gbps chạy qua mạng lõi.** ⭐ **Đừng bật rồi quên tắt.**

> ⚠️ ⭐ **Trong lab:** ⭐ **vIOS/vIOS-L2 thường KHÔNG hỗ trợ ERSPAN.** ⭐ Nếu `type erspan-source` báo
> `% Invalid input` → ⭐ **bình thường.** ⭐ **Đọc hiểu cấu hình trên là đủ cho đề** —
> blueprint hỏi *"configure and verify"* nhưng đề thi hỏi ở mức **nhận diện cấu hình đúng/sai**.

### 7.5 ⭐ Chọn công cụ nào — bảng quyết định

| Câu hỏi bạn cần trả lời | ⭐ Dùng công cụ |
|---|---|
| ⭐ *"Ai đang ăn hết băng thông?"* | ⭐⭐ **NetFlow** |
| ⭐ *"Traffic đi theo đường nào, tới đâu?"* | ⭐ **NetFlow** |
| ⭐ *"Chính xác trong gói tin có gì? Sao ứng dụng này lỗi?"* | ⭐⭐ **SPAN + Wireshark** |
| ⭐ *"Thiết bị có còn sống không? CPU bao nhiêu?"* | ⭐ **SNMP** |
| ⭐ *"Chuyện gì đã xảy ra lúc 2 giờ sáng?"* | ⭐⭐ **Syslog** |
| ⭐ *"Đường tới chi nhánh có đạt SLA không?"* | ⭐⭐ **IP SLA** *(§7)* |
| ⭐ *"Tôi cần thấy từng bước router xử lý gói này"* | ⭐ **Conditional debug** *(§8)* |

---

## 📘 8. 🔴 ⭐⭐ IP SLA (blueprint 4.5 — CONFIGURE AND VERIFY)

### 8.1 ⭐ Hai vai trò của IP SLA

> ⭐ Bạn **đã dùng IP SLA** ở [Module-03](Module-03-IP-Routing-Nen-tang.md) và
> [Module-06A](Module-06A-FHRP-HSRP-VRRP-GLBP.md) — nhưng chỉ ở vai trò **"công tắc failover"**.

| Vai trò | Dùng làm gì | Học ở đâu |
|---|---|---|
| ⭐ **Công tắc** *(ghép với `track`)* | ⭐ **Đổi route / đổi HSRP priority khi đường chết** | Module-03, Module-06A |
| ⭐⭐ **Thước đo** *(vai trò chính ở đây)* | ⭐⭐ **ĐO liên tục: RTT, jitter, mất gói, MOS** → chứng minh SLA với nhà mạng | ⭐ **Module-11 này** |

### 8.2 ⭐⭐ Các loại operation

| Operation | Đo gì | ⭐ Cần Responder? |
|---|---|:---:|
| ⭐⭐ **icmp-echo** | ⭐ **Kết nối + RTT** | ❌ **Không** |
| ⭐ **udp-echo** | RTT chính xác hơn icmp (bỏ qua độ trễ xử lý ICMP) | ⭐ **Có** |
| ⭐⭐ **udp-jitter** | ⭐⭐ **Jitter, mất gói theo từng chiều, one-way delay** | ⭐⭐ **CÓ — bắt buộc** |
| ⭐⭐ **udp-jitter codec g711alaw** | ⭐⭐ **Điểm MOS cho VoIP** | ⭐⭐ **CÓ** |
| ⭐ **tcp-connect** | Thời gian bắt tay TCP tới một port | ❌ (nếu tới dịch vụ thật) |
| ⭐ **http** | Thời gian tải trang (DNS + TCP + transfer) | ❌ |
| ⭐ **dns** | Thời gian phân giải tên | ❌ |
| **path-echo / path-jitter** | Đo theo **từng hop** | Tùy |

> ⭐⭐ **Nhớ cặp này cho đề:** ⭐ **`icmp-echo` = không cần Responder** ·
> ⭐⭐ **`udp-jitter` = BẮT BUỘC có Responder.**

### 8.3 ⭐⭐ Cấu hình cơ bản — icmp-echo + track

```
!═══ ① Định nghĩa phép đo ═══
ip sla 10
 icmp-echo 203.0.113.254 source-interface GigabitEthernet0/0
 frequency 5                       ! đo mỗi 5 giây
 timeout 500                       ! chờ tối đa 500 ms
 threshold 200                     ! >200 ms thì tính là "vượt ngưỡng"
 tag "ISP1-health-check"
 request-data-size 64

!═══ ② LÊN LỊCH — DÒNG HAY QUÊN NHẤT ═══
ip sla schedule 10 life forever start-time now

!═══ ③ Ghép với track (Module-03 / 06A) ═══
track 1 ip sla 10 reachability
 delay down 10 up 30                 ! chống "nhấp nháy"

!═══ ④ Dùng track ═══
ip route 0.0.0.0 0.0.0.0 203.0.113.254 track 1
ip route 0.0.0.0 0.0.0.0 198.51.100.254 10        ! floating static dự phòng
```

> 🔴 ⭐⭐ **`ip sla schedule` là dòng bị quên nhiều nhất.**
> ⭐ Không có nó, operation **tồn tại trong config nhưng KHÔNG BAO GIỜ CHẠY.**
> ⭐ **Dấu hiệu:** `show ip sla statistics` báo ⭐ **"Operation has not been scheduled"** hoặc mọi số đều **0**.

⭐ **Hai kiểu track hay dùng:**

| Lệnh | Theo dõi gì |
|---|---|
| ⭐ `track 1 ip sla 10 reachability` | ⭐ **Đích có tới được không** (Up/Down) |
| ⭐ `track 1 ip sla 10 state` | ⭐ **Có VƯỢT NGƯỠNG không** — dùng `threshold` để phát hiện **chậm** chứ không chỉ **chết** |

> ⭐ **Khác biệt quan trọng:** ⭐ **`reachability`** chỉ quan tâm *"còn sống không"*.
> ⭐⭐ **`state`** quan tâm *"có đạt chất lượng không"* — ⭐ **đường sống nhưng RTT 900 ms vẫn bị coi là Down.**
> ⭐ Với VoIP, ⭐ **`state` mới là cái bạn cần.**

### 8.4 ⭐⭐ IP SLA Responder — khi nào cần và vì sao

```
!═══ TRÊN THIẾT BỊ ĐÍCH (R2) ═══
ip sla responder
   ! hoặc chỉ định rõ:
   ! ip sla responder udp-echo ipaddress 10.0.0.2 port 5000

!═══ TRÊN THIẾT BỊ NGUỒN (R1) ═══
ip sla 20
 udp-jitter 10.0.0.2 5000 codec g711alaw
 frequency 30
 tos 184                            ! DSCP EF=46 → đo đúng hàng đợi voice (Module-09!)
ip sla schedule 20 life forever start-time now
```

> ⭐⭐ **Responder làm hai việc mà nếu thiếu thì số đo SAI:**
> 1. ⭐⭐ **Đóng dấu thời gian ở đầu kia** → ⭐ **loại bỏ độ trễ xử lý của thiết bị đích** khỏi kết quả.
>    ⭐ Không có nó, bạn đo cả thời gian router bên kia "bận" — ⭐ **RTT bị thổi phồng.**
> 2. ⭐⭐ **Cho phép tính ONE-WAY delay** (độ trễ từng chiều riêng biệt) — ⭐ **điều mà ping không bao giờ làm được.**

> 🔴 ⭐⭐ **CẢNH BÁO về one-way delay:** ⭐ **nó chỉ chính xác khi HAI đầu đồng bộ NTP với nhau.**
> ⭐ Lệch đồng hồ 50 ms → ⭐ **one-way delay sai 50 ms** → số liệu vô nghĩa.
> ⭐ **Đây lại là §2 — không có NTP thì đừng tin one-way delay.**

### 8.5 ⭐⭐ Verify và đọc kết quả

```
show ip sla configuration 10          ! xem lại cấu hình + lịch
show ip sla statistics 10           ! LỆNH CHÍNH — kết quả mới nhất
show ip sla statistics aggregated 10  ! thống kê gộp theo giờ
show ip sla summary                   ! tất cả operation trên một màn hình
show track 1                        ! trạng thái track + ai đang dùng nó
show ip sla responder                 ! trên thiết bị đích
debug ip sla trace 10                 ! ⚠️ chỉ lab
```

⭐ **Đọc `show ip sla statistics` cho icmp-echo:**
```
IPSLA operation id: 10
    Latest RTT: 12 milliseconds
    Latest operation start time: 14:23:45 ICT Thu Sep 10 2026
    Latest operation return code: OK          ← DÒNG QUAN TRỌNG NHẤT
    Number of successes: 1847
    Number of failures: 3
    Operation time to live: Forever
```

| ⭐ Return code | Nghĩa |
|---|---|
| ⭐ **OK** | ✅ Thành công |
| ⭐ **Timeout** | 🔴 Không nhận được trả lời trong `timeout` |
| ⭐ **No connection** | 🔴 Không tới được đích |
| **Over threshold** | ⚠️ Có trả lời nhưng **vượt `threshold`** |
| ⭐ **Error / Busy** | Lỗi cấu hình hoặc thiết bị bận |

⭐ **Đọc `show ip sla statistics` cho udp-jitter (VoIP):**
```
    Number of RTT: 1000       RTT Min/Avg/Max: 8/14/45 milliseconds
    Latency one-way SD (Source→Destination): Min/Avg/Max: 4/7/22
    Latency one-way DS (Destination→Source): Min/Avg/Max: 4/7/23
    Jitter SD: Min/Avg/Max: 0/2/11
    Jitter DS: Min/Avg/Max: 0/2/9
    Packet Loss SD: 0    Packet Loss DS: 2
    MOS score: 4.34                     ← điểm chất lượng thoại
```

> ⭐⭐ **Đối chiếu ngay với ngưỡng VoIP đã học ở [Module-09 §8.1](Module-09-Architecture-va-QoS.md):**
>
> | Chỉ số | ⭐ Ngưỡng | Ví dụ trên | Đạt? |
> |---|---|---|:---:|
> | ⭐ **One-way latency** | ⭐ **≤ 150 ms** | 7 ms | ✅ |
> | ⭐ **Jitter** | ⭐ **≤ 30 ms** | 2 ms | ✅ |
> | ⭐ **Loss** | ⭐ **≤ 1 %** | 2/1000 = 0.2 % | ✅ |
> | ⭐ **MOS** | ⭐ **> 4.0 là tốt** | 4.34 | ✅ |
>
> ⭐⭐ **Đây chính là cách bạn CHỨNG MINH với nhà mạng rằng họ vi phạm SLA** — ⭐ có số liệu,
> có thời điểm, có cả hai chiều riêng biệt. ⭐ **Ping không làm được điều đó.**

⭐ **Thang MOS (Mean Opinion Score):**

| MOS | Chất lượng |
|:---:|---|
| ⭐ **4.3 – 5.0** | Xuất sắc |
| ⭐ **4.0 – 4.3** | ⭐ **Tốt — mục tiêu thiết kế** |
| 3.6 – 4.0 | Chấp nhận được |
| 🔴 **< 3.6** | 🔴 Người dùng bắt đầu phàn nàn |

---

## 📘 9. 🔴 ⭐⭐ DEBUG AN TOÀN & CÔNG CỤ CHẨN ĐOÁN (blueprint 4.1)

### 9.1 🔴 ⭐⭐ Vì sao `debug all` là tự sát

```
   KỊCH BẢN: bạn gõ "debug all" trên router production

   ① Mọi hệ thống con bắt đầu sinh log ở mức 7
   ② Log mặc định đổ ra CONSOLE — mà console là ĐỒNG BỘ và CHẬM (9600 baud!)
   ③ CPU phải chờ từng ký tự được in ra console
   ④ CPU 100% → router NGỪNG xử lý OSPF hello, NGỪNG forward
   ⑤ Bạn KHÔNG GÕ ĐƯỢC "undebug all" nữa vì phiên của bạn cũng đơ
   ⑥ Phải RÚT ĐIỆN router
```

> 🔴 ⭐⭐ **Đây là câu chuyện có thật xảy ra thường xuyên.** ⭐ Nguyên nhân gốc **không phải debug** —
> ⭐ **mà là CONSOLE LOGGING.** ⭐ Console ghi **đồng bộ**: CPU phải đợi ký tự in xong mới làm việc khác.

### 9.2 ⭐⭐ Quy trình debug AN TOÀN — 5 bước

```
① TẮT LOG RA CONSOLE, CHUYỂN VÀO BUFFER
   no logging console
   logging buffered 128000 debugging
   clear logging

② KIỂM TRA CPU TRƯỚC KHI BẮT ĐẦU
   show processes cpu sorted | exclude 0.00
   CPU đã > 50% rồi thì ĐỪNG debug

③ BẬT DEBUG CÓ ĐIỀU KIỆN (không bao giờ debug trần)
   debug ip packet 199              ← lọc bằng ACL
   ! hoặc:  debug condition interface Gi0/0

④ TÁI HIỆN LỖI — CHỈ VÀI GIÂY, RỒI TẮT NGAY
   undebug all                      ← HỌC THUỘC LỆNH NÀY

⑤ ĐỌC KẾT QUẢ TỪ BUFFER (thoải mái, không áp lực thời gian)
   show logging
```

| Lệnh cứu hộ | ⭐ Nhớ nằm lòng |
|---|---|
| ⭐⭐ **`undebug all`** hoặc **`u all`** | ⭐⭐ **Tắt MỌI debug ngay lập tức** |
| ⭐ `show debugging` | ⭐ **Đang bật những debug nào** — kiểm tra trước khi rời máy |
| ⭐ `terminal no monitor` | Ngừng đổ log ra phiên SSH của bạn |

### 9.3 ⭐⭐ Conditional debug — kỹ năng quan trọng nhất mục 4.1

> ⭐ **Ý tưởng:** ⭐ **thay vì xem TẤT CẢ, chỉ xem đúng thứ bạn quan tâm.**

```
!═══ CÁCH 1: LỌC BẰNG ACL (phổ biến nhất) ═══
access-list 199 permit ip host 10.1.1.10 host 10.2.2.20
access-list 199 permit ip host 10.2.2.20 host 10.1.1.10    ! nhớ CẢ HAI CHIỀU
!
debug ip packet 199 detail

!═══ CÁCH 2: ĐIỀU KIỆN TOÀN CỤC (áp cho mọi debug đang bật) ═══
debug condition interface GigabitEthernet0/0
debug condition ip 10.1.1.10
debug condition username nam.tran
debug condition vlan 10
!
show debug condition                    ! đang có điều kiện nào
no debug condition all                  ! xóa hết điều kiện

!═══ CÁCH 3: IOS-XE — conditional debug hiện đại ═══
debug platform condition interface Gi0/0 both
debug platform condition start
   ... (tái hiện) ...
debug platform condition stop
show platform condition

!═══ CÁCH 4: WIRELESS (đã học Module-07B §9.4) ═══
debug wireless mac aabb.ccdd.eeff internal      ! RadioActive Trace
```

> 🔴 ⭐⭐ **Bẫy với `debug ip packet`:** ⭐ **nó CHỈ thấy gói được xử lý bằng process switching.**
> ⭐ Gói đi qua **CEF (fast path)** ⭐ **KHÔNG hiện ra** — mà đó là **99% traffic**
> *(nhắc lại [Module-01 §3](Module-01-Packet-Forwarding-va-Kien-truc-Thiet-bi.md))*.
>
> ⭐ **Hệ quả:** bạn debug và thấy "không có gói nào" → ⭐ **không có nghĩa là không có traffic**,
> mà là traffic đang được CEF xử lý. ⭐ **Muốn thấy hết phải `no ip cef`** — 🔴 ⭐ **tuyệt đối
> KHÔNG làm điều này trên production.**

### 9.4 ⭐⭐ Ping & Traceroute nâng cao

```
!═══ EXTENDED PING — mọi tùy chọn trên một dòng ═══
ping 10.2.2.2 source Loopback0 repeat 100 size 1400 df-bit timeout 1

! Các tùy chọn quan trọng:
!   source <intf>   → ép IP nguồn (test đúng đường về / khớp ACL, VRF)
!   size <n>        → kích thước gói
!   df-bit          → CẤM PHÂN MẢNH → dùng để TÌM MTU (Module-08 §4.4!)
!   repeat <n>      → số gói
!   timeout <n>     → giây chờ
!   tos <n>         → đặt DSCP (Module-09: tos 184 = DSCP EF 46)

!═══ TÌM MTU TỰ ĐỘNG bằng chế độ tương tác ═══
R1# ping
Protocol [ip]:
Target IP address: 10.2.2.2
Repeat count [5]: 1
Datagram size [100]: 
Extended commands [n]: y
Set DF bit in IP header? [no]: yes
Sweep range of sizes [n]: y
Sweep min size [36]: 1400
Sweep max size [18024]: 1500
Sweep interval [1]: 4
   → Router tự thử từng kích thước và cho biết ngưỡng nào bắt đầu FAIL

!═══ VRF (Module-08 §3.4) ═══
ping vrf KHACH-A 10.10.10.100
traceroute vrf KHACH-A 10.10.10.100

!═══ TRACEROUTE ═══
traceroute 10.2.2.2 source Loopback0 numeric probe 1 ttl 1 15
```

> ⭐⭐ **Đọc traceroute cho đúng — đây là chỗ nhiều người hiểu sai:**
>
> | Thấy gì | ⭐ Nghĩa |
> |---|---|
> | ⭐ `* * *` ở **một hop giữa** rồi các hop sau vẫn hiện | ⭐⭐ **BÌNH THƯỜNG** — hop đó **chặn ICMP** hoặc **không gửi TTL-exceeded**. ⭐ **KHÔNG phải lỗi** |
> | ⭐ `* * *` từ một hop **cho tới hết** | 🔴 ⭐ **Đường đứt thật từ hop đó** |
> | ⭐ Cùng một IP lặp lại nhiều lần | 🔴 ⭐ **Routing loop** |
> | ⭐ RTT tăng vọt ở một hop rồi **giảm lại** ở hop sau | ⭐ **BÌNH THƯỜNG** — hop đó **ưu tiên thấp cho traffic gửi TỚI chính nó** (chính là **CoPP** — [Module-10 §5](Module-10-Security.md)!). ⭐ **Không phải nghẽn** |

### 9.5 ⭐ Bảng chọn công cụ chẩn đoán theo tình huống

| Tình huống | ⭐ Công cụ đúng |
|---|---|
| "Có tới được không?" | ⭐ `ping` (kèm `source` cho đúng) |
| "Tắc ở chặng nào?" | ⭐ `traceroute` |
| "Gói lớn có qua được không?" | ⭐⭐ `ping ... df-bit size <n>` |
| "Chuyện gì đã xảy ra?" | ⭐⭐ `show logging` (syslog) |
| "Ai đang ăn băng thông?" | ⭐⭐ `show flow monitor ... cache` |
| "Chính xác trong gói có gì?" | ⭐ **SPAN + Wireshark** |
| "Router xử lý gói này thế nào?" | ⭐⭐ **Conditional debug** |
| "Đường có đạt chất lượng không?" | ⭐⭐ **IP SLA** |
| "Thiết bị còn sống? CPU bao nhiêu?" | ⭐ **SNMP** · `show processes cpu` |

---

## 📘 10. 🟡 DNA CENTER ASSURANCE (blueprint 4.6 — Describe)

> ⭐ Nhắc lại [Module-09 §7.8](Module-09-Architecture-va-QoS.md): DNA Center có **4 workflow** —
> ⭐ **Design → Policy → Provision → ASSURANCE**. ⭐ **Mục 4.6 hỏi về cái thứ tư.**

### 10.1 ⭐ Ý tưởng: từ "thiết bị sống không" sang "người dùng có hài lòng không"

| | ⭐ **Giám sát truyền thống** (SNMP/syslog) | ⭐⭐ **DNA Center Assurance** |
|---|---|---|
| Câu hỏi | ⭐ *"Interface có up không? CPU bao nhiêu?"* | ⭐⭐ *"Trải nghiệm của người dùng có tốt không?"* |
| Đơn vị theo dõi | Thiết bị, interface | ⭐⭐ **Client, ứng dụng, đường đi** |
| Khi có sự cố | ⭐ Bạn tự ghép log từ nhiều nguồn | ⭐ **Hệ thống đưa ra "Issue" + gợi ý khắc phục** |
| Dữ liệu quá khứ | Tùy công cụ | ⭐⭐ **Xem lại trạng thái mạng ở QUÁ KHỨ** |

### 10.2 ⭐⭐ Các tính năng Assurance phải biết tên

| Tính năng | ⭐ Làm gì |
|---|---|
| ⭐⭐ **Health Score** | ⭐ Điểm **0–10** cho **thiết bị** và cho **client**. ⭐ Nhìn một màn hình biết chỗ nào đang tệ |
| ⭐⭐ **Client 360 / Device 360** | ⭐ **Toàn bộ thông tin về MỘT client/thiết bị trên một trang**: kết nối, roaming, RSSI/SNR, ứng dụng, lịch sử lỗi |
| ⭐⭐ **Path Trace** | ⭐⭐ **Vẽ đường đi hop-by-hop giữa hai endpoint** — ⭐ **kèm phân tích ACL/QoS ở từng chặng** → chỉ ra **đúng chỗ gói bị chặn** |
| ⭐⭐ **Network Time Travel** | ⭐⭐ **Tua ngược trạng thái mạng về một thời điểm trong quá khứ.** ⭐ *"Lúc 2 giờ sáng client đó thấy gì?"* |
| ⭐ **Sensors** | ⭐ **AP ở chế độ `sensor`** *([Module-07A §5](Module-07A-Wireless-RF-802.11-AP-Antenna.md))* — ⭐ **tự đóng vai client giả**, chạy test DHCP/DNS/RADIUS/ping **chủ động** |
| ⭐ **AI Network Analytics** | Học ra "bình thường" của mạng bạn → báo khi có **bất thường** |
| ⭐ **Issues & Remediation** | Danh sách vấn đề + ⭐ **gợi ý cách sửa**, xếp theo mức ảnh hưởng |
| ⭐ **Application Experience** | Chất lượng theo **từng ứng dụng** (dựa trên NetFlow/AVC) |

> ⭐⭐ **Hai cái đề hay hỏi nhất: `Path Trace` và `Network Time Travel`.**
> ⭐ **Path Trace** = *"gói bị chặn ở đâu, bởi ACL nào"*.
> ⭐ **Network Time Travel** = *"xem lại quá khứ"* — ⭐ **giải quyết vấn đề kinh điển "sự cố đã hết,
> giờ không tái hiện được"**.

⭐ **Sensor mode nối lại với Module-07A:** ⭐ **AP không phục vụ client**, mà **giả làm client** để
⭐ **phát hiện lỗi TRƯỚC KHI người dùng than phiền** — đây là *"proactive"* thay vì *"reactive"*.

---

## 📘 11. ⭐ NETCONF & RESTCONF (blueprint 4.7) — tóm tắt, học sâu ở Module-12

> 🔴 ⭐⭐ **Nhắc lại cảnh báo §0.2: mục 4.7 THUỘC Domain 4.0**, dù nó có vẻ là chuyện "automation".
> ⭐ **Dưới đây là phần tối thiểu để bạn không hụt nếu thi sớm.** ⭐ **Chi tiết + LAB ở Module-12 §3.**

| | ⭐ **NETCONF** | ⭐ **RESTCONF** |
|---|---|---|
| ⭐ **Vận chuyển** | ⭐⭐ **SSH — port 830** | ⭐⭐ **HTTPS — port 443** |
| ⭐ **Định dạng dữ liệu** | ⭐ **Chỉ XML** | ⭐ **JSON hoặc XML** |
| ⭐ **Kiểu thao tác** | ⭐ **RPC** (`<get-config>`, `<edit-config>`…) | ⭐ **HTTP verb** (GET/POST/PUT/PATCH/DELETE) |
| ⭐ **Datastore** | ⭐⭐ **CÓ: `running`, `candidate`, `startup`** | ⭐ Chủ yếu `running` |
| ⭐ **Giao dịch (transaction)** | ⭐⭐ **CÓ — commit/rollback, all-or-nothing** | 🔴 **Không** |
| ⭐ **Mô hình dữ liệu** | ⭐ **YANG** | ⭐ **YANG** |
| ⭐ Hợp với | ⭐ **Thay đổi cấu hình phức tạp, cần rollback** | ⭐ **Đọc trạng thái, tích hợp nhanh với script/web** |

```
! Bật trên IOS-XE — chỉ hai dòng
netconf-yang
restconf
!
ip http secure-server                   ! RESTCONF cần HTTPS
!
show netconf-yang sessions
show platform software yang-management process
```

> ⭐⭐ **Ba con số phải nhớ ngay bây giờ:** ⭐ **NETCONF = SSH 830** · ⭐ **RESTCONF = HTTPS 443** ·
> ⭐ **cả hai đều dùng YANG làm mô hình dữ liệu.**
> ⭐ Và ⭐ **chỉ NETCONF có candidate datastore + commit/rollback.**

---

## 📘 12. 🟡 BỔ TRỢ — Model-Driven Telemetry

> ⚠️ ⭐ **Không nằm rõ trong blueprint ENCOR v1.1**, nhưng ⭐ **Cisco đang thay SNMP bằng nó**
> và bạn sẽ gặp trong tài liệu. ⭐ **Đọc 10 phút.**

| | ⭐ **SNMP (truyền thống)** | ⭐⭐ **Model-Driven Telemetry (MDT)** |
|---|---|---|
| ⭐ **Mô hình** | ⭐⭐ **PULL** — NMS **hỏi** mỗi N giây | ⭐⭐ **PUSH** — thiết bị **tự gửi** theo đăng ký |
| Độ trễ dữ liệu | 🔴 ⭐ Bằng chu kỳ polling (thường 5 phút) | ⭐ **Gần thời gian thực (giây)** |
| Tải khi quy mô lớn | 🔴 ⭐ **Rất nặng** — 1000 thiết bị × hàng nghìn OID | ⭐ **Nhẹ hơn nhiều** |
| Định dạng | ASN.1/BER | ⭐ **GPB / JSON / XML** |
| Mô hình dữ liệu | MIB | ⭐ **YANG** |
| Vận chuyển | UDP 161/162 | ⭐ **gRPC / NETCONF / TCP** |

⭐ **Hai kiểu đăng ký:** ⭐ **Dial-out** (thiết bị chủ động kết nối tới collector) ·
⭐ **Dial-in** (collector kết nối vào thiết bị rồi đăng ký).

> ⭐ **Ẩn dụ:** ⭐ **SNMP = bạn gọi điện hỏi "có gì mới không?" mỗi 5 phút.**
> ⭐⭐ **MDT = bạn đăng ký nhận thông báo, có gì mới là nó tự báo ngay.**

## 🧪 PHẦN 3 — NHÌN THẤY NÓ

> ### 👉 **[LAB 11 — Tuần 17: Syslog · SNMP · NetFlow · SPAN · IP SLA](Module-11-LAB.md)**

| LAB | Nội dung | Ví von ở Phần 1 | Cơ chế ở Phần 2 |
|---|---|---|---|
| **A** | Syslog — severity & cơ chế lọc | §2.2 thang báo động ngược | §4 |
| **B** | SNMPv2c + v3 | §2.1 năm giác quan | §5 |
| **C** | ⭐⭐ **Flexible NetFlow** *(lab hay nhất module)* | §2.3 hóa đơn điện thoại · §2.4 dòng hóa đơn nào | §6 |
| **D** | ⭐⭐ SPAN + **bẫy "cổng câm"** | §2.5 cổng bị trưng dụng | §7 |
| **E** | ⭐⭐ IP SLA + track + `udp-jitter` | §2.6 camera an ninh vs chụp ảnh | §8 |
| **F–I** | 🚀 Conditional debug · MTU · chẩn đoán tổng hợp | — | §9 |

> ⭐⭐ **LAB C là bài hay nhất module** — và là điều bất ngờ dễ chịu:
> `show flow monitor <FM> cache` cho bạn xem **toàn bộ bảng flow ngay trên router**,
> **không cần collector, không cần server nào cả**.
>
> Bạn sẽ nhìn thấy đúng thứ NetFlow làm trong mạng thật: *ai đang nói chuyện với ai, bao nhiêu byte*.

---

## 🏗️ PHẦN 4 — TOPO & KIẾN TRÚC

> Bạn vừa học năm công cụ. Phần này trả lời: **đặt chúng ở đâu, và dùng cái nào khi nào?**

### 4.1 Bản đồ: hệ thống giám sát của một doanh nghiệp

```
   ┌────────────────────────────────────────────────────────────┐
   │              TRUNG TÂM GIÁM SÁT (NOC)                       │
   │                                                             │
   │  ① Syslog server    ② NMS (SNMP)    ③ NetFlow collector    │
   │     UDP 514            UDP 161/162      UDP 2055            │
   └───────▲──────────────────▲──────────────────▲───────────────┘
           │                  │                  │
           │  ⑤ NTP đồng bộ TẤT CẢ (UDP 123)     │
           │  🔴 Sai giờ = mọi thứ trên đây thành rác
           │                  │                  │
   ┌───────┴──────────────────┴──────────────────┴───────────────┐
   │                    THIẾT BỊ MẠNG                             │
   │                                                              │
   │  ④ IP SLA: đo CHẤT LƯỢNG đường liên tục (RTT, jitter, MOS)  │
   │  ⑥ SPAN: chỉ bật KHI CẦN SOI CHI TIẾT (tốn tài nguyên)      │
   └──────────────────────────────────────────────────────────────┘
```

### 4.2 Bảng quyết định — câu hỏi nào dùng công cụ nào

| Bạn cần trả lời | Dùng | Vì sao |
|---|---|---|
| *Chuyện gì đã xảy ra lúc 2 giờ sáng?* | ⭐ **Syslog** | Nhật ký — chạy sẵn 24/7 |
| *Thiết bị còn sống? CPU bao nhiêu?* | ⭐ **SNMP** | Bắt mạch định kỳ |
| ⭐ *AI đang ăn hết băng thông?* | ⭐⭐ **NetFlow** | **Metadata, nhẹ, chạy 24/7** |
| *Chính xác trong gói tin có gì?* | ⭐ **SPAN + Wireshark** | Bản sao toàn bộ gói — **nặng, chỉ bật khi cần** |
| *Đường tới chi nhánh có đạt SLA không?* | ⭐⭐ **IP SLA** | Đo liên tục, có số liệu chứng minh |
| *Router xử lý gói này thế nào?* | ⭐ **Conditional debug** | Chỉ khi 5 cái trên chưa ra |

> ⭐⭐ **Nguyên tắc vàng: đi từ RẺ đến ĐẮT.**
> Syslog và NetFlow **đang chạy sẵn, không tốn gì thêm**.
> SPAN và debug **tốn tài nguyên** → để cuối cùng.
>
> ⭐ **Và câu chốt: NetFlow để PHÁT HIỆN, SPAN để SOI.**

### 4.3 Ba sự thật mà chỉ người đi làm mới biết

| Sự thật | Giải thích |
|---|---|
| 🔴 ⭐⭐ **Thủ phạm làm treo router KHÔNG phải lệnh debug** | Mà là **console logging** — nó **đồng bộ và chậm**, CPU phải đợi từng ký tự in xong. ⭐ **`no logging console` + `logging buffered` TRƯỚC khi debug**, và thuộc **`u all`** |
| 🔴 ⭐⭐ **Cổng SPAN destination thành "câm"** | Ngừng forward, không STP, không học MAC — nhưng ⭐ **`show interface` vẫn báo `up/up`, đèn vẫn sáng**. Thiết bị cắm vào đó **mất mạng mà không ai hiểu vì sao** |
| 🔴 ⭐⭐ **`cache timeout active` mặc định 1800 giây** | Một cuộc tải file 25 phút **không xuất hiện trên collector** cho tới khi nó kết thúc → bạn nhìn dashboard tưởng mạng rảnh trong khi nó đang nghẽn. ⭐ **Đặt 60** |

### 4.4 Những thứ này sẽ lớn lên thành gì

| Bạn vừa học | Sẽ thành | Ở module |
|---|---|---|
| ⭐ **NETCONF/RESTCONF** *(§11 — mục 4.7)* | 🔴 **Học sâu ở Module-12** — Domain 4.0 **chưa xong** sau module này | **Module-12 §3** |
| DNA Center Assurance | Gắn với 4 workflow đã học ở M09 | — |
| IP SLA đo chất lượng | Nguyên lý giống **AAR của SD-WAN** *(đo bằng BFD)* | — |
| Syslog severity, NTP | Nền của điều tra sự cố an ninh *(M10)* | — |

### 4.5 Vẽ lại để nhớ

> **Bài tập 15 phút, trên giấy.**
>
> 1. Vẽ lại sơ đồ §4.1, đánh dấu ① đến ⑥
> 2. Ghi rõ **port** của từng dịch vụ
> 3. Trả lời: *Người dùng kêu mạng chậm. Nêu thứ tự công cụ bạn dùng, và lý do của thứ tự đó.*

<details>
<summary>Đáp án câu 3</summary>

⭐⭐ **Nguyên tắc: đi từ RẺ đến ĐẮT.**

1. ⭐ **`show clock detail`** — thời gian có đúng không *(sai giờ thì mọi bước sau vô nghĩa)*
2. ⭐ **SYSLOG** — `show logging | include %LINK|%LINEPROTO|%SYS-5-CONFIG_I`
   → có flap? ai vừa đổi config?
3. ⭐ **Thiết bị** — `show processes cpu sorted` · `show interface | include rate|drops`
4. ⭐⭐ **NETFLOW** — `show flow monitor <FM> cache format table`
   → ⭐ **thường tìm ra thủ phạm ở đây**
5. ⭐ **IP SLA** — có vượt ngưỡng **150 / 30 / 1** không?
6. ⭐ **SPAN + Wireshark** hoặc **conditional debug** — chỉ khi 5 bước trên chưa ra

⭐ **Lý do của thứ tự:** syslog và NetFlow **đang chạy sẵn, không tốn gì thêm**.
SPAN và debug **tốn tài nguyên thiết bị** và có thể **gây thêm sự cố** → để cuối.

</details>

---

## 💡 4.6 Thực chiến đi làm

| # | Tình huống thật | 🔴 Điều người mới làm sai | ⭐ Cách làm đúng |
|:---:|---|---|---|
| 1 | Dựng syslog server, log về đầy đủ | Để mặc định `logging trap` | ⭐ **Mặc định là 6 (informational)** — rất nhiều. ⭐ Cân nhắc **4–5** cho mạng lớn, ⭐ **nhưng nhớ bẫy `%LINEPROTO-5`** |
| 2 | Log về server nhưng "lộn xộn, không biết của thiết bị nào" | Bỏ qua | ⭐⭐ **`logging source-interface Loopback0`** + `logging origin-id hostname`. ⭐ Không có nó, thiết bị nhiều interface gửi log với IP nguồn **thay đổi** |
| 3 | Router treo khi debug | Đổ lỗi cho lệnh debug | 🔴 ⭐⭐ **Thủ phạm là CONSOLE LOGGING (đồng bộ).** ⭐ **`no logging console` + `logging buffered` TRƯỚC KHI debug** |
| 4 | Cần debug trên production | `debug ip packet` trần | 🔴 ⭐⭐ **Luôn dùng ACL lọc.** ⭐ Và **học thuộc `u all`** trước khi bật bất cứ debug nào |
| 5 | Bật NetFlow, collector không thấy gì | Nghĩ cấu hình sai | ⭐ Kiểm tra: (a) đã `ip flow monitor` **lên interface** chưa · (b) ⭐ **`cache timeout active` còn là 1800?** · (c) firewall chặn UDP 2055 |
| 6 | NetFlow chạy, nhưng số liệu "kỳ lạ" | Tin tưởng biểu đồ | ⭐⭐ **Kiểm tra `Emergency aged`** — ⭐ **>0 = cache đầy = số liệu thiếu.** ⭐ Giảm `match` hoặc tăng `cache entries` |
| 7 | Cần bắt gói trên link 10 Gbps | SPAN thẳng vào laptop 1 Gbps | 🔴 ⭐⭐ **Oversubscription — mất gói ÂM THẦM.** ⭐ Dùng **filter trong SPAN**, hoặc **TAP phần cứng**, hoặc lọc trước bằng ACL |
| 8 | Cắm máy phân tích vào switch | Chọn đại một cổng trống làm destination | 🔴 ⭐⭐ **Kiểm tra cổng đó có ai dùng không.** ⭐ SPAN destination **làm thiết bị đó mất mạng dù `up/up`** |
| 9 | Bật SPAN để điều tra, xong việc | Để nguyên | 🔴 ⭐ **SPAN tốn tài nguyên switch, ERSPAN tốn cả băng thông mạng lõi.** ⭐ **Tắt sau khi xong** |
| 10 | Nhà mạng nói "đường chúng tôi vẫn tốt" | Cãi bằng cảm tính | ⭐⭐ **Dựng IP SLA `udp-jitter` chạy 24/7** → ⭐ **có số liệu one-way delay, jitter, loss theo từng chiều, kèm timestamp.** ⭐ **Đây là bằng chứng không cãi được** |
| 11 | IP SLA cấu hình rồi mà không chạy | Xóa đi làm lại | ⭐⭐ **99% là quên `ip sla schedule`.** ⭐ `show ip sla statistics` báo **"has not been scheduled"** |
| 12 | Đo one-way delay thấy số âm/vô lý | Nghĩ thiết bị lỗi | ⭐⭐ **Hai đầu chưa đồng bộ NTP.** ⭐ **One-way delay VÔ NGHĨA nếu đồng hồ lệch** |
| 13 | Track chỉ dùng `reachability` cho VoIP | Nghĩ vậy là đủ | ⭐ **`reachability` chỉ biết "sống/chết".** ⭐ Đường sống mà **RTT 900 ms** vẫn Up → ⭐ **dùng `state` + `threshold`** |
| 14 | Dùng SNMP v2c "cho nhanh" | Community `public` | 🔴 ⭐⭐ **Community đi PLAINTEXT trên đường truyền.** ⭐ Tối thiểu: **RO + ACL khóa nguồn**. ⭐ Đúng nhất: **v3 authPriv** |
| 15 | Cảnh báo quan trọng bị mất | Không biết vì sao | ⭐⭐ **Trap là "bắn rồi quên".** ⭐ Cảnh báo quan trọng → dùng ⭐ **Inform (có ACK, gửi lại)** |
| 16 | Sự cố đã hết, không tái hiện được | Bó tay | ⭐ Đây chính là lý do ⭐ **DNA Center Network Time Travel** tồn tại. ⭐ Không có DNAC thì ⭐ **syslog + NetFlow lưu trữ** là cách duy nhất |
| 17 | Đồng hồ thiết bị sai vài phút | "Không quan trọng lắm" | 🔴 ⭐⭐ **Nó phá HẾT: log không đối chiếu được · biểu đồ NetFlow sai giờ · one-way delay vô nghĩa · chứng thư 802.1X hỏng.** ⭐ **NTP là việc đầu tiên** |

> 🔴 ⭐⭐ **Bốn câu thần chú của module này:**
> 1. ⭐ **"NTP trước, giám sát sau. Không có thời gian đúng thì mọi số liệu là rác."**
> 2. ⭐ **"`no logging console` + `logging buffered` TRƯỚC KHI debug. Và thuộc `u all`."**
> 3. ⭐ **"NetFlow để PHÁT HIỆN, SPAN để SOI. Đừng dùng SPAN 24/7."**
> 4. ⭐ **"Quên `ip sla schedule` = IP SLA không bao giờ chạy."**

---

# 📎 PHỤ LỤC — TRA CỨU

> 🔴 **KHÔNG đọc phần này ở lần học đầu tiên.**
>
> | Khi nào | Mở mục nào |
> |---|---|
> | Đang lab mà lỗi | **Gỡ lỗi nhanh** (§18) — ⭐ quy trình 6 bước cho "mạng chậm" |
> | Quên lệnh | **Hộp lệnh** (§18.1) |
> | Tuần 20, ôn thi | **Bẫy đề** (§17) + **Quiz** (§19) |
> | Gặp từ lạ | **Thuật ngữ** (§20) |
> | Tự chấm | **Đúc kết** (§21) |

---

## 🎓 16. BẪY TRONG ĐỀ ENCOR

| # | ⭐ Bẫy | ✅ Sự thật |
|:---:|---|---|
| 1 | 🔴 ⭐⭐ "Severity 7 nghiêm trọng nhất" | 🔴 ⭐⭐ **SỐ CÀNG NHỎ CÀNG NGHIÊM TRỌNG.** ⭐ **0 = Emergency** (tệ nhất), **7 = Debugging** |
| 2 | 🔴 ⭐⭐ "`logging trap 4` chỉ gửi severity 4" | 🔴 ⭐⭐ **Gửi 0, 1, 2, 3 VÀ 4** — tức "mức 4 trở lên về độ nghiêm trọng" |
| 3 | "`logging trap 4` gửi 4,5,6,7" | 🔴 ⭐ **Ngược hoàn toàn.** Nó **bỏ qua** 5, 6, 7 |
| 4 | "Interface down chỉ sinh một dòng log" | 🔴 ⭐⭐ **Hai dòng: `%LINK-3-UPDOWN` (severity 3) và `%LINEPROTO-5-UPDOWN` (severity 5)** |
| 5 | "`service timestamps` là mặc định" | 🔴 ⭐ **Mặc định log chỉ có `uptime`** → ⭐ **vô dụng khi đối chiếu nhiều thiết bị.** Phải bật `datetime msec` |
| 6 | "Xem log trên SSH tự động được" | 🔴 ⭐ **Phải gõ `terminal monitor`** |
| 7 | "Console logging vô hại" | 🔴 ⭐⭐ **Console là ĐỒNG BỘ và CHẬM** — ⭐ **nguyên nhân số 1 làm router treo khi debug** |
| 8 | ⭐ "SNMP agent lắng nghe UDP 162" | 🔴 ⭐⭐ **Agent nghe UDP 161.** ⭐ **Manager nghe UDP 162** (trap/inform) |
| 9 | 🔴 ⭐⭐ "Trap có xác nhận" | 🔴 ⭐⭐ **Trap KHÔNG có ACK (bắn rồi quên).** ⭐ **INFORM mới có ACK và gửi lại** |
| 10 | "Inform có từ SNMPv1" | 🔴 ⭐ **Inform và GetBulk có từ v2c** |
| 11 | "SNMPv2c có mã hóa" | 🔴 ⭐⭐ **v1 và v2c dùng community string PLAINTEXT.** ⭐ **Chỉ v3 mới có mã hóa** |
| 12 | "authNoPriv có mã hóa" | 🔴 ⭐⭐ **`auth` = xác thực · `priv` = MÃ HÓA.** ⭐ **Chỉ `authPriv` có cả hai** |
| 13 | 🔴 ⭐⭐ "NetFlow flow được định nghĩa bởi 5-tuple" | 🔴 ⭐⭐ **7 trường** — 5-tuple **cộng thêm ⭐ ToS/DSCP và ⭐ input interface** |
| 14 | "NetFlow bắt được nội dung gói" | 🔴 ⭐⭐ **NetFlow chỉ là METADATA.** ⭐ **SPAN mới sao chép nội dung** |
| 15 | 🔴 ⭐⭐ "`collect` định nghĩa flow" | 🔴 ⭐⭐ **`match` = KEY = định nghĩa flow.** ⭐ **`collect` = non-key, chỉ ghi thêm** |
| 16 | "FNF có 3 thành phần" | 🔴 ⭐ **4: Flow Record · Flow Exporter · Flow Monitor · Flow Sampler (tùy chọn)** |
| 17 | "NetFlow v5 hỗ trợ IPv6" | 🔴 ⭐ **v5 chỉ IPv4 và cố định.** ⭐ **v9 dùng template → hỗ trợ IPv6/MPLS** |
| 18 | ⭐ "`cache timeout active` mặc định là 60 giây" | 🔴 ⭐⭐ **Mặc định 1800 giây (30 phút)** → ⭐ **flow dài không lên collector kịp** |
| 19 | 🔴 ⭐⭐ "SPAN destination vẫn chuyển traffic bình thường" | 🔴 ⭐⭐ **KHÔNG.** ⭐ Nó **ngừng forward, không STP, không học MAC** — ⭐ **thiết bị cắm vào đó MẤT MẠNG dù cổng `up/up`** |
| 20 | "RSPAN chỉ cần cấu hình ở switch nguồn và đích" | 🔴 ⭐⭐ **RSPAN VLAN phải tạo với `remote-span` trên MỌI switch trên đường đi**, và **được phép qua mọi trunk** |
| 21 | "ERSPAN đi được qua L2" | 🔴 ⭐ **ERSPAN dùng GRE → đi qua mạng ĐÃ ĐỊNH TUYẾN (L3).** ⭐ **RSPAN mới là L2** |
| 22 | "ERSPAN không ảnh hưởng MTU" | 🔴 ⭐ **GRE thêm header** → ⭐ **cùng vấn đề MTU như Module-08** |
| 23 | "SPAN nhiều nguồn vào một đích thì vẫn đủ" | 🔴 ⭐⭐ **Oversubscription → MẤT GÓI ÂM THẦM** |
| 24 | 🔴 ⭐⭐ "IP SLA cấu hình xong là chạy" | 🔴 ⭐⭐ **Phải có `ip sla schedule <id> life forever start-time now`** — ⭐ thiếu là **không bao giờ chạy** |
| 25 | "`icmp-echo` cần IP SLA Responder" | 🔴 ⭐ **KHÔNG cần.** ⭐ **`udp-jitter` mới BẮT BUỘC có Responder** |
| 26 | "One-way delay đo được mà không cần NTP" | 🔴 ⭐⭐ **Cần hai đầu đồng bộ NTP** — lệch đồng hồ = số liệu vô nghĩa |
| 27 | "`track ... reachability` phát hiện được đường chậm" | 🔴 ⭐ **`reachability` chỉ biết sống/chết.** ⭐ **Muốn phát hiện CHẬM → dùng `state` + `threshold`** |
| 28 | 🔴 ⭐⭐ "`debug ip packet` thấy mọi gói" | 🔴 ⭐⭐ **Chỉ thấy gói PROCESS-SWITCHED.** ⭐ Traffic đi xuyên qua router do **CEF** xử lý → **không hiện** |
| 29 | "`debug all` chỉ tốn chút CPU" | 🔴 ⭐⭐ **Có thể làm router treo hoàn toàn tới mức phải RÚT ĐIỆN** |
| 30 | "`* * *` trong traceroute nghĩa là mạng hỏng" | 🔴 ⭐⭐ **Nếu các hop SAU vẫn hiện → chỉ là hop đó chặn ICMP.** ⭐ **Bình thường** |
| 31 | "RTT tăng vọt ở một hop giữa = nghẽn ở đó" | 🔴 ⭐ **Không** — hop đó **ưu tiên thấp cho traffic gửi TỚI CHÍNH NÓ** (**CoPP**). ⭐ Xem hop sau: nếu RTT giảm lại thì **không có nghẽn** |
| 32 | 🔴 ⭐⭐ "NETCONF/RESTCONF thuộc Domain 6.0 Automation" | 🔴 ⭐⭐ **Thuộc mục 4.7 — Domain 4.0 Network Assurance** |
| 33 | ⭐ "NETCONF dùng HTTPS" | 🔴 ⭐⭐ **NETCONF = SSH port 830.** ⭐ **RESTCONF = HTTPS 443** |
| 34 | "RESTCONF có candidate datastore và rollback" | 🔴 ⭐⭐ **Chỉ NETCONF** có candidate/commit/rollback |
| 35 | "Path Trace giống traceroute" | 🔴 ⭐ **Path Trace của DNAC còn phân tích ACL/QoS ở từng chặng** → chỉ ra **chính xác chỗ gói bị chặn** |
| 36 | "SNMP cho dữ liệu thời gian thực" | 🔴 ⭐ **SNMP là PULL, độ trễ bằng chu kỳ polling.** ⭐ **Model-Driven Telemetry mới là PUSH gần real-time** |

---

## 🐛 17. GỠ LỖI NHANH

### 17.1 ⭐ Hộp lệnh vạn năng

```
═══ THỜI GIAN (làm trước mọi thứ) ═══
show clock detail                         ! "Time source is NTP"? có dấu * không?
show ntp status | include synchronized|stratum
show ntp associations

═══ SYSLOG ═══
show logging                            ! cấu hình + toàn bộ buffer
show logging | include %LINK|%LINEPROTO
show logging | include Trap logging|Buffer logging|dropped
show logging count                        ! đếm theo facility
clear logging                             ! xóa trước khi tái hiện
terminal monitor / terminal no monitor

═══ SNMP ═══
show snmp                                 ! thống kê chung
show snmp user                          ! v3: auth/priv protocol
show snmp group                         ! view + security level + ACL
show snmp host                            ! gửi trap/inform đi đâu
show snmp view / show snmp engineID

═══ NETFLOW ═══
show flow monitor <FM> cache format table    ! XEM FLOW — lệnh hay nhất
show flow monitor <FM> statistics             ! Emergency aged?
show flow monitor <FM>
show flow record <FR>
show flow exporter <FE> statistics            ! Packets sent có tăng không
show flow interface <intf>
clear flow monitor <FM> cache

═══ SPAN ═══
show monitor session all
show monitor session <n> detail
show vlan remote-span                     ! RSPAN VLAN
show interface <dst-port> | include line protocol

═══ IP SLA ═══
show ip sla configuration <id>            ! có lịch chưa
show ip sla statistics <id>             ! return code + số liệu
show ip sla statistics aggregated <id>
show ip sla summary
show track <n>                          ! trạng thái + ai dùng nó
show ip sla responder                     ! trên đầu đích
clear ip sla statistics <id>

═══ DEBUG ═══
show debugging                          ! đang bật gì
show debug condition
undebug all   (u all)                  ! HỌC THUỘC
show processes cpu sorted | exclude 0.00  ! kiểm tra TRƯỚC khi debug
show processes cpu history

═══ NETCONF/RESTCONF (§10) ═══
show netconf-yang sessions
show platform software yang-management process
```

### 17.2 ⭐⭐ Bảng: triệu chứng → nguyên nhân → cách sửa

| 🔴 Triệu chứng | ⭐ Nguyên nhân | ✅ Cách sửa |
|---|---|---|
| ⭐ **Log không có ngày giờ, chỉ có `*Mar 1 00:04:12`** | ⭐ Thiếu `service timestamps` · và/hoặc **chưa sync NTP** | ⭐ `service timestamps log datetime msec localtime show-timezone` + NTP *(§2)* |
| ⭐ **Log các thiết bị không đối chiếu được với nhau** | 🔴 ⭐ **Đồng hồ lệch** | ⭐ NTP + cùng `clock timezone` |
| ⭐ **Syslog server không nhận được gì** | (a) thiếu `logging host` · (b) ⭐ **`logging trap` quá thấp** · (c) firewall chặn **UDP 514** · (d) sai `source-interface` | ⭐ `show logging \| include Trap logging` — xem mức và `link up` |
| ⭐ **Thấy interface DOWN nhưng không thấy nó UP lại** | ⭐⭐ **`logging trap 4`** — `%LINK-3` qua được, `%LINEPROTO-5` bị lọc | ⭐ Nâng lên `logging trap 5` hoặc `6` |
| ⭐ **`show logging` báo `messages dropped > 0`** | ⭐ Buffer quá nhỏ hoặc quá tải | ⭐ Tăng `logging buffered`, giảm mức, thêm `logging rate-limit` |
| ⭐ **SSH vào mà không thấy log hiện ra** | ⭐ Chưa gõ `terminal monitor` | ⭐ `terminal monitor` |
| 🔴 ⭐ **Router treo/rất chậm khi debug** | ⭐⭐ **Console logging đồng bộ** | ⭐ `no logging console` + `logging buffered` **TRƯỚC** khi debug. ⭐ Cứu: **`u all`** |
| ⭐ **NMS không lấy được dữ liệu SNMP** | (a) sai community/user · (b) ⭐ **ACL chặn** · (c) firewall chặn **UDP 161** · (d) sai security level | ⭐ `show snmp group` (ACL nào) · `show snmp user` (auth/priv) |
| ⭐ **SNMPv3 báo "authorization error"** | ⭐ Sai **security level** — user tạo `authNoPriv` mà group yêu cầu `priv` | ⭐ `show snmp user` + `show snmp group` — hai bên **phải khớp mức** |
| ⭐ **Cảnh báo quan trọng thỉnh thoảng bị mất** | ⭐⭐ **Đang dùng Trap (không ACK)** | ⭐ Chuyển sang **Inform** |
| ⭐⭐ **NetFlow: collector không thấy flow nào** | (a) ⭐ **chưa `ip flow monitor` lên interface** · (b) sai IP/port exporter · (c) firewall chặn UDP 2055 · (d) ⭐ **`cache timeout active 1800`** | ⭐ `show flow interface <intf>` · `show flow exporter <FE> statistics` → **`Packets sent`** |
| ⭐⭐ **NetFlow: số liệu thiếu/kỳ lạ** | ⭐⭐ **Cache đầy** — `Emergency aged > 0` | ⭐ Tăng `cache entries` · **giảm số `match`** · bật sampler |
| ⭐ **Số flow tăng vọt bất thường** | ⭐ `match` quá nhiều trường (VD source-port) | ⭐ **Bỏ bớt key field không cần phân biệt** |
| 🔴 ⭐⭐ **Thiết bị mất mạng dù cổng `up/up`** | ⭐⭐ **Cổng đó bị đặt làm SPAN destination** | ⭐ `show monitor session all` → gỡ hoặc đổi cổng đích |
| ⭐ **SPAN: Wireshark thấy ít gói hơn thực tế** | ⭐⭐ **Oversubscription** (nhiều nguồn → một đích) | ⭐ Lọc bớt nguồn, hoặc dùng cổng đích tốc độ cao hơn / TAP |
| ⭐ **RSPAN không tới được switch đích** | (a) ⭐ **thiếu `remote-span`** trên một switch · (b) ⭐ **VLAN chưa được phép qua trunk** | ⭐ `show vlan remote-span` trên **mọi** switch · `show interface trunk` |
| ⭐ **ERSPAN: bản capture thiếu gói lớn** | ⭐ **GRE + MTU** *(Module-08 §4.4)* | ⭐ Tăng MTU đường đi, hoặc chấp nhận phân mảnh |
| 🔴 ⭐⭐ **IP SLA: mọi số đều 0** | ⭐⭐ **Quên `ip sla schedule`** | ⭐ `show ip sla statistics` → **"has not been scheduled"** → thêm dòng schedule |
| ⭐ **IP SLA `udp-jitter` luôn Timeout** | ⭐⭐ **Thiếu `ip sla responder`** ở đầu đích · hoặc sai port · hoặc ACL chặn | ⭐ `show ip sla responder` trên R2 |
| ⭐ **One-way delay âm hoặc vô lý** | ⭐⭐ **Hai đầu chưa đồng bộ NTP** | ⭐ `show clock` cả hai → sync NTP |
| ⭐ **Track không đổi trạng thái dù đường chậm** | ⭐ Dùng `reachability` (chỉ sống/chết) | ⭐ Đổi sang `state` + đặt `threshold` |
| ⭐ **Track "nhấp nháy" liên tục** | ⭐ Đường chập chờn, không có delay | ⭐ `delay down 10 up 30` |
| ⭐ **`debug ip packet` không thấy traffic** | ⭐⭐ **Traffic do CEF xử lý** (không punt lên CPU) | ⭐ **Bình thường.** Debug chỉ thấy gói process-switched *(§8.3)* |
| ⭐ **Không biết đang bật debug gì** | — | ⭐ `show debugging` · ⭐ **`u all` cho chắc** |

### 17.3 ⭐ Quy trình chẩn đoán "người dùng kêu mạng chậm" — dùng đủ 5 giác quan

```
① THỜI GIAN CÓ ĐÚNG KHÔNG?
      show clock detail (mọi thiết bị liên quan)
      → sai giờ thì mọi bước sau đều không đối chiếu được

② ĐÃ XẢY RA CHUYỆN GÌ?               → SYSLOG
      show logging | include %LINK|%LINEPROTO|%OSPF|%TUN
      → có flap? có ai đổi config (%SYS-5-CONFIG_I)?

③ THIẾT BỊ CÓ KHỎE KHÔNG?            → SNMP / show
      show processes cpu sorted · show interface | include rate|drops
      → CPU cao? interface có drop/error?

④ AI ĐANG ĂN BĂNG THÔNG?           → NETFLOW
      show flow monitor <FM> cache format table
      → ĐÂY thường là chỗ tìm ra thủ phạm

⑤ CHẤT LƯỢNG ĐƯỜNG CÓ ĐẠT KHÔNG?     → IP SLA
      show ip sla statistics
      → RTT/jitter/loss có vượt ngưỡng 150/30/1 không?

⑥ VẪN CHƯA RA?                        → SPAN + Wireshark (soi chi tiết)
      hoặc conditional debug (xem router xử lý gói thế nào)
```

> ⭐⭐ **Nguyên tắc: đi từ RẺ đến ĐẮT.** ⭐ Syslog và NetFlow **đang chạy sẵn, không tốn gì thêm.**
> ⭐ **SPAN và debug tốn tài nguyên → để cuối cùng.**

---

## 📝 18. QUIZ TỰ KIỂM TRA

**1.** Kể 8 mức syslog severity theo thứ tự. Mức nào nghiêm trọng nhất?
<details><summary>Đáp án</summary>

⭐ **0 Emergency · 1 Alert · 2 Critical · 3 Error · 4 Warning · 5 Notification · 6 Informational · 7 Debugging**

🔴 ⭐⭐ **SỐ CÀNG NHỎ CÀNG NGHIÊM TRỌNG** → ⭐ **0 (Emergency) là nặng nhất**, 7 (Debugging) nhẹ nhất.

⭐ **Mẹo nhớ:** *"**E**very **A**wesome **C**isco **E**ngineer **W**ill **N**eed **I**ce-cream **D**aily"*
</details>

**2.** `logging trap 4` gửi những severity nào lên syslog server?
<details><summary>Đáp án</summary>

⭐⭐ **Gửi mức 0, 1, 2, 3 VÀ 4.** 🔴 ⭐ **KHÔNG gửi 5, 6, 7.**

⭐ Bạn đang khai báo **ngưỡng nghiêm trọng tối thiểu** — cái gì nghiêm trọng **bằng hoặc hơn** ngưỡng thì được gửi.

🔴 ⭐⭐ **Hệ quả thực tế:** với `trap 4`, bạn nhận `%LINK-3-UPDOWN` (interface xuống) nhưng
⭐ **KHÔNG nhận `%LINEPROTO-5-UPDOWN`** → ⭐ **thấy nó down mà không thấy nó up lại.**
</details>

**3.** Mổ xẻ dòng: `000045: Sep 10 14:05:12.334 ICT: %LINEPROTO-5-UPDOWN: ...`
<details><summary>Đáp án</summary>

| Phần | Giá trị | Nhờ đâu có |
|---|---|---|
| ⭐ Sequence | `000045` | `service sequence-numbers` |
| ⭐ Timestamp | `Sep 10 14:05:12.334 ICT` | `service timestamps log datetime msec localtime show-timezone` |
| ⭐ Facility | `%LINEPROTO` | — |
| ⭐⭐ **Severity** | ⭐ **`5` = Notification** | — |
| ⭐ Mnemonic | `UPDOWN` | — |

⭐ **Định dạng chuẩn: `%FACILITY-SEVERITY-MNEMONIC: mô tả`**
</details>

**4.** SNMP: port nào cho agent, port nào cho manager? Trap khác Inform thế nào?
<details><summary>Đáp án</summary>

⭐⭐ **UDP 161 — agent lắng nghe** (manager gửi Get/Set vào đây)
⭐⭐ **UDP 162 — manager lắng nghe** (agent gửi trap/inform vào đây)

| | ⭐ **Trap** | ⭐ **Inform** |
|---|---|---|
| Xác nhận | 🔴 **Không** (bắn rồi quên) | ⭐ **Có ACK** |
| Mất gói | 🔴 **Mất luôn** | ⭐ **Gửi lại** |
| Tài nguyên | Ít | Nhiều hơn |
| Có từ | v1 | ⭐ **v2c** |

⭐ **Cảnh báo quan trọng → dùng Inform.**
</details>

**5.** Ba security level của SNMPv3? Cái nào có mã hóa?
<details><summary>Đáp án</summary>

⭐ **noAuthNoPriv** — chỉ username, không xác thực, không mã hóa
⭐ **authNoPriv** — xác thực (MD5/SHA), 🔴 **KHÔNG mã hóa**
⭐⭐ **authPriv** — ⭐ **xác thực + MÃ HÓA (DES/3DES/AES)** → ⭐ **mức duy nhất nên dùng thật**

⭐ **Nhớ: `auth` = xác thực (anh là ai) · `priv` = privacy = MÃ HÓA.**
⭐ Kiểm tra bằng `show snmp user` → nếu `Privacy Protocol: None` thì chỉ là `authNoPriv`.
</details>

**6.** Bảy trường định nghĩa một flow trong NetFlow truyền thống?
<details><summary>Đáp án</summary>

⭐ **① Source IP · ② Destination IP · ③ Source port · ④ Destination port · ⑤ Layer 3 protocol
· ⑥ ToS byte (DSCP) · ⑦ Input logical interface**

🔴 ⭐⭐ **Bẫy: người ta hay chỉ nhớ 5-tuple (①–⑤) và quên ⑥ ToS + ⑦ input interface.**
⭐ **Nhớ: 5-tuple là của FIREWALL. NetFlow là 7-tuple.**
</details>

**7.** Bốn thành phần của Flexible NetFlow? `match` khác `collect` thế nào?
<details><summary>Đáp án</summary>

⭐⭐ **① Flow Record** (đo gì) · **② Flow Exporter** (gửi đi đâu) · **③ Flow Monitor** (ghép lại + cache)
· **④ Flow Sampler** (tùy chọn, lấy mẫu 1/N)

| | ⭐⭐ **`match`** | ⭐⭐ **`collect`** |
|---|---|---|
| Là | ⭐ **KEY field** | ⭐ **NON-KEY field** |
| Vai trò | ⭐⭐ **ĐỊNH NGHĨA flow** — khác giá trị = flow khác | ⭐ Chỉ ghi thêm |

🔴 ⭐ **Hệ quả:** thêm một `match` = ⭐ **số flow có thể tăng vọt → cache đầy nhanh → số liệu sai.**
</details>

**8.** Giá trị mặc định của `cache timeout active` là bao nhiêu, và vì sao nó nguy hiểm?
<details><summary>Đáp án</summary>

🔴 ⭐⭐ **Mặc định 1800 giây = 30 PHÚT.**

⭐ **Nghĩa là:** một flow **đang chạy** chỉ được đẩy lên collector sau 30 phút.
🔴 ⭐⭐ **Một cuộc tải file 25 phút sẽ KHÔNG xuất hiện trên biểu đồ cho tới khi nó kết thúc**
→ ⭐ **bạn nhìn dashboard và tưởng mạng đang rảnh trong khi nó đang nghẽn.**

⭐ **Thực tế: đặt `cache timeout active 60`.**
</details>

**9.** So sánh SPAN, RSPAN, ERSPAN: phạm vi và cơ chế vận chuyển?
<details><summary>Đáp án</summary>

| | ⭐ **SPAN** | ⭐ **RSPAN** | ⭐⭐ **ERSPAN** |
|---|---|---|---|
| Phạm vi | ⭐ **Cùng một switch** | ⭐ **Qua L2** | ⭐⭐ **Qua L3 (mạng định tuyến)** |
| Vận chuyển | Nội bộ | ⭐ **VLAN RSPAN chuyên dụng** | ⭐⭐ **GRE tunnel** |
| Yêu cầu đặc biệt | — | ⭐ `remote-span` trên **MỌI** switch + trunk cho VLAN qua | ⭐ IP kết nối + `erspan-id` khớp |

⭐ **Mẹo: S**ame switch · **R**emote qua VLAN (L2) · **E**ncapsulated qua GRE (L3).
</details>

**10.** Điều gì xảy ra với một cổng khi bạn đặt nó làm SPAN destination?
<details><summary>Đáp án</summary>

⭐⭐ **Cổng bị "trưng dụng" hoàn toàn:**
- 🔴 ⭐ **Ngừng chuyển traffic bình thường**
- 🔴 ⭐ **Không tham gia STP**
- 🔴 ⭐ **Không học MAC address**
- ⭐ Chỉ phun bản sao ra ngoài

🔴 ⭐⭐ **Nguy hiểm nhất: `show interface` vẫn báo `up/up`, đèn vẫn sáng** —
⭐ **nhưng thiết bị cắm vào đó MẤT MẠNG hoàn toàn.**

⭐ **Luôn kiểm tra cổng có ai đang dùng không trước khi đặt làm SPAN destination.**
</details>

**11.** RSPAN không hoạt động. Ba nguyên nhân phổ biến?
<details><summary>Đáp án</summary>

1. ⭐⭐ **Quên `remote-span`** trên một switch nào đó (kể cả switch **trung gian**) → VLAN đó thành VLAN thường
2. ⭐⭐ **VLAN RSPAN chưa được phép qua trunk** ở một chặng nào đó
3. ⭐ **Quên tạo VLAN trên switch trung gian** — ⭐ **nó cũng phải có `remote-span`** dù không cắm gì

⭐ **Kiểm tra: `show vlan remote-span` trên MỌI switch + `show interface trunk`.**
</details>

**12.** IP SLA cấu hình xong nhưng mọi số đều 0. Nguyên nhân?
<details><summary>Đáp án</summary>

⭐⭐ **Quên `ip sla schedule <id> life forever start-time now`.**

⭐ Operation nằm đầy đủ trong config, ⭐ **`show run` trông hoàn toàn đúng — nhưng nó KHÔNG BAO GIỜ CHẠY.**

⭐ **Dấu hiệu:** `show ip sla statistics <id>` báo ⭐ **"Operation has not been scheduled"**.
⭐ **Đây là lỗi số 1 với IP SLA.**
</details>

**13.** Operation nào cần IP SLA Responder? Responder làm gì mà quan trọng vậy?
<details><summary>Đáp án</summary>

⭐⭐ **`udp-jitter` (và `udp-echo`) BẮT BUỘC cần Responder.** ⭐ **`icmp-echo` thì KHÔNG cần.**

⭐ **Responder làm hai việc:**
1. ⭐⭐ **Đóng dấu thời gian ở đầu kia** → ⭐ **loại bỏ độ trễ xử lý của thiết bị đích** khỏi kết quả
2. ⭐⭐ **Cho phép tính ONE-WAY delay** (độ trễ từng chiều riêng biệt) — ⭐ điều ping không làm được

🔴 ⭐⭐ **Nhưng one-way delay chỉ chính xác khi HAI ĐẦU ĐỒNG BỘ NTP.**
</details>

**14.** `track ... reachability` khác `track ... state` thế nào? Dùng cái nào cho VoIP?
<details><summary>Đáp án</summary>

⭐ **`reachability`** — chỉ quan tâm ⭐ **"đích còn sống không"** (Up/Down).
⭐⭐ **`state`** — quan tâm ⭐ **"có VƯỢT NGƯỠNG không"** (dùng `threshold`).

⭐⭐ **VoIP phải dùng `state` + `threshold`** — vì ⭐ **một đường RTT 900 ms vẫn "reachable" nhưng
hoàn toàn không dùng được cho thoại.**
</details>

**15.** Đọc kết quả `udp-jitter`: one-way SD avg 7 ms, jitter avg 2 ms, loss 0.2%, MOS 4.34. Đường này có đạt chuẩn VoIP không?
<details><summary>Đáp án</summary>

⭐ **ĐẠT — cả bốn chỉ số đều tốt** *(đối chiếu [Module-09 §8.1](Module-09-Architecture-va-QoS.md))*:

| Chỉ số | ⭐ Ngưỡng | Đo được | |
|---|---|---|:---:|
| One-way latency | ⭐ **≤ 150 ms** | 7 ms | ✅ |
| Jitter | ⭐ **≤ 30 ms** | 2 ms | ✅ |
| Loss | ⭐ **≤ 1 %** | 0.2 % | ✅ |
| MOS | ⭐ **> 4.0** | 4.34 | ✅ |
</details>

**16.** Vì sao `debug all` có thể làm router treo? Quy trình debug an toàn?
<details><summary>Đáp án</summary>

🔴 ⭐⭐ **Thủ phạm thật sự là CONSOLE LOGGING.** ⭐ Console ghi **đồng bộ** — CPU phải **đợi từng ký tự
in xong** mới làm việc khác. ⭐ Debug sinh hàng nghìn dòng/giây → ⭐ **CPU 100% → router ngừng
forward, ngừng gửi OSPF hello → và bạn không gõ nổi `undebug all` nữa.**

⭐ **Quy trình an toàn 5 bước:**
1. ⭐ `no logging console` + `logging buffered 128000 debugging` + `clear logging`
2. ⭐ `show processes cpu sorted` — CPU đã cao thì **đừng debug**
3. ⭐⭐ **Bật debug CÓ ĐIỀU KIỆN** (`debug ip packet <acl>`)
4. ⭐ Tái hiện vài giây → ⭐⭐ **`undebug all`**
5. ⭐ `show logging` đọc thoải mái
</details>

**17.** `debug ip packet` không hiện gói nào dù có traffic đi qua router. Vì sao?
<details><summary>Đáp án</summary>

⭐⭐ **Vì traffic đó được CEF (fast path) xử lý — không bị punt lên CPU.**

⭐ `debug ip packet` ⭐ **chỉ thấy gói PROCESS-SWITCHED.**
⭐ Gói **đi xuyên qua** router → CEF lo → **không hiện.**
⭐ Gói **gửi TỚI chính router** → punt lên CPU → **có hiện.**

*(Nhắc lại [Module-01 §3](Module-01-Packet-Forwarding-va-Kien-truc-Thiet-bi.md).)*
🔴 ⭐ **Đừng gõ `no ip cef` trên production để "nhìn thấy hết".**
</details>

**18.** Traceroute hiện `* * *` ở hop 4 nhưng hop 5, 6, 7 vẫn hiện bình thường. Có vấn đề gì không?
<details><summary>Đáp án</summary>

⭐⭐ **KHÔNG có vấn đề gì.** ⭐ Hop 4 chỉ đơn giản **không trả lời ICMP TTL-exceeded**
(bị firewall chặn, hoặc thiết bị được cấu hình không gửi).

⭐ **Chỉ đáng lo khi `* * *` xuất hiện từ một hop CHO TỚI HẾT** → đường đứt thật từ đó.

⭐ **Bonus:** nếu thấy **RTT tăng vọt ở một hop rồi GIẢM LẠI ở hop sau** → ⭐ **cũng bình thường** —
hop đó **ưu tiên thấp cho traffic gửi tới chính nó** (chính là **CoPP** — [Module-10 §5](Module-10-Security.md)).
</details>

**19.** NETCONF và RESTCONF: port nào, định dạng gì, cái nào có rollback? Chúng thuộc domain nào?
<details><summary>Đáp án</summary>

| | ⭐ **NETCONF** | ⭐ **RESTCONF** |
|---|---|---|
| Port | ⭐⭐ **SSH 830** | ⭐⭐ **HTTPS 443** |
| Định dạng | ⭐ **Chỉ XML** | ⭐ **JSON hoặc XML** |
| Thao tác | RPC (`<edit-config>`) | HTTP verb (GET/POST/PUT/PATCH/DELETE) |
| ⭐ **Rollback / candidate** | ⭐⭐ **CÓ** | 🔴 **Không** |
| Mô hình dữ liệu | ⭐ **YANG** | ⭐ **YANG** |

🔴 ⭐⭐ **Chúng thuộc mục 4.7 — Domain 4.0 Network Assurance**, ⭐ **KHÔNG phải Domain 6.0 Automation**
như nhiều người tưởng.
</details>

**20.** DNA Center Assurance: Path Trace và Network Time Travel làm gì?
<details><summary>Đáp án</summary>

⭐⭐ **Path Trace** — ⭐ **vẽ đường đi hop-by-hop giữa hai endpoint, KÈM phân tích ACL/QoS ở từng chặng**
→ ⭐ **chỉ ra chính xác chỗ gói bị chặn.** ⭐ Đây là thứ `traceroute` **không** cho bạn biết.

⭐⭐ **Network Time Travel** — ⭐ **tua ngược trạng thái mạng về một thời điểm trong quá khứ**
→ ⭐ **giải quyết vấn đề kinh điển "sự cố đã hết, giờ không tái hiện được".**

*(Các tính năng khác: Health Score 0–10 · Client 360 / Device 360 · Sensors (AP sensor mode) ·
AI Network Analytics · Issues & Remediation.)*
</details>

**21.** Khi nào dùng NetFlow, khi nào dùng SPAN?
<details><summary>Đáp án</summary>

⭐⭐ **NetFlow = metadata (ai nói với ai, bao nhiêu byte).** ⭐ **Nhẹ, chạy được 24/7.**
→ ⭐ Trả lời: ***"AI đang ăn hết băng thông? Traffic đi đâu?"***

⭐⭐ **SPAN = bản sao TOÀN BỘ gói.** ⭐ **Nặng, chỉ bật khi cần.**
→ ⭐ Trả lời: ***"Chính xác trong gói tin đó có gì?"***

⭐ **Quy trình thật:** ⭐ **NetFlow chạy liên tục để PHÁT HIỆN bất thường → rồi mới bật SPAN
vào đúng chỗ đó để SOI CHI TIẾT.**

⭐ **Ẩn dụ: NetFlow = hóa đơn điện thoại · SPAN = ghi âm cuộc gọi.**
</details>

**22.** Vì sao NTP là điều kiện tiên quyết của cả Module-11? Nêu 3 hậu quả nếu sai giờ.
<details><summary>Đáp án</summary>

⭐ **Ba (trong nhiều) hậu quả:**
1. ⭐⭐ **Syslog** — ⭐ **không đối chiếu được log giữa các thiết bị** → không dựng lại được trình tự sự cố
2. ⭐⭐ **IP SLA one-way delay** — ⭐ **tính SAI hoàn toàn** (lệch 50 ms = sai 50 ms)
3. ⭐ **NetFlow** — collector vẽ biểu đồ **sai thời điểm**

*(Thêm: chứng thư 802.1X/AP join hỏng — [Module-07B §3.4](Module-07B-CAPWAP-WLC-FlexConnect-Roaming.md);
log mất giá trị pháp lý khi điều tra an ninh.)*

⭐ **Ba dòng nền tảng:** `ntp server ...` · `service timestamps log datetime msec localtime show-timezone`
· `service sequence-numbers`
</details>

**23.** `show flow monitor FM-X statistics` báo `Emergency aged: 1240`. Nghĩa là gì và sửa thế nào?
<details><summary>Đáp án</summary>

🔴 ⭐⭐ **Cache đã ĐẦY** → flow bị đẩy ra **sớm hơn timeout** → ⭐ **số liệu KHÔNG chính xác**
(collector nhận được flow bị cắt ngang, thống kê thiếu).

⭐ **Ba cách sửa:**
1. ⭐ **Tăng `cache entries`**
2. ⭐⭐ **Giảm số `match`** — mỗi key field thêm vào làm số flow tăng vọt
3. ⭐ **Bật sampler** (`mode random 1 out-of 100`) trên link tốc độ cao
</details>

**24.** Bạn đặt `logging trap 3`. Sự kiện `%SYS-5-CONFIG_I` (ai đó vừa sửa config) có được gửi lên server không?
<details><summary>Đáp án</summary>

🔴 ⭐⭐ **KHÔNG.** ⭐ `logging trap 3` chỉ gửi mức **0, 1, 2, 3**. ⭐ `%SYS-5-CONFIG_I` là **severity 5** → **bị lọc.**

🔴 ⭐ **Đây là hậu quả thực tế nghiêm trọng:** ⭐ **bạn sẽ KHÔNG BIẾT ai đã sửa cấu hình thiết bị** —
một trong những log quan trọng nhất cho việc điều tra sự cố và audit.

⭐ **Muốn bắt được nó: `logging trap 5` trở lên** (thực tế thường dùng **6 = informational**).
</details>

**25.** Người dùng kêu "mạng chậm". Nêu thứ tự công cụ bạn dùng và lý do.
<details><summary>Đáp án</summary>

⭐⭐ **Nguyên tắc: đi từ RẺ đến ĐẮT** — syslog/NetFlow đang chạy sẵn, SPAN/debug tốn tài nguyên.

1. ⭐ **`show clock detail`** — thời gian có đúng không (nếu sai, mọi bước sau vô nghĩa)
2. ⭐ **SYSLOG** — `show logging | include %LINK|%LINEPROTO|%SYS-5-CONFIG_I` → có flap? ai đổi config?
3. ⭐ **Thiết bị** — `show processes cpu sorted` · `show interface | include rate|drops`
4. ⭐⭐ **NETFLOW** — `show flow monitor <FM> cache format table` → ⭐ **thường tìm ra thủ phạm ở đây**
5. ⭐ **IP SLA** — `show ip sla statistics` → có vượt ngưỡng 150/30/1 không?
6. ⭐ **SPAN + Wireshark** hoặc **conditional debug** — chỉ khi 5 bước trên chưa ra
</details>

---

## 📚 19. THUẬT NGỮ ANH–VIỆT

| English | Tiếng Việt / Giải thích |
|---|---|
| ⭐ **`service timestamps`** | ⭐ Gắn ngày giờ vào log — ⭐ **mặc định chỉ có uptime, phải bật `datetime msec`** |
| ⭐ **`service sequence-numbers`** | Đánh số thứ tự log — ⭐ **biết ngay nếu có dòng bị mất** |
| ⭐⭐ **Severity 0–7** | ⭐ **Emergency · Alert · Critical · Error · Warning · Notification · Informational · Debugging.** ⭐ **Số NHỎ = nghiêm trọng HƠN** |
| ⭐ **Facility** | Hệ thống con sinh ra log (`%LINK`, `%OSPF`, `%SEC`…) |
| ⭐ **Mnemonic** | Tên sự kiện (`UPDOWN`, `CONFIG_I`…) |
| ⭐⭐ **`logging trap <n>`** | ⭐ **Gửi lên server các mức 0 → n** |
| ⭐ **`logging buffered`** | Lưu log trong RAM — ⭐ **xem bằng `show logging`** |
| ⭐⭐ **`logging console`** | 🔴 ⭐ **ĐỒNG BỘ và CHẬM — nguyên nhân số 1 làm router treo khi debug** |
| ⭐ **`logging source-interface`** | ⭐ IP nguồn cố định — ⭐ **thiếu nó server tưởng là nhiều thiết bị khác nhau** |
| ⭐ **`terminal monitor`** | Bật xem log trên phiên SSH |
| ⭐ **SNMP Manager / Agent / MIB / OID** | NMS / phần mềm trên thiết bị / cây dữ liệu / địa chỉ một mục |
| ⭐⭐ **UDP 161 / UDP 162** | ⭐ **Agent lắng nghe** / ⭐ **Manager lắng nghe (trap-inform)** |
| ⭐ **Get / GetNext / GetBulk / Set** | Lấy một / lấy kế tiếp / ⭐ **lấy nhiều (v2c+)** / ⭐ **GHI** |
| ⭐⭐ **Trap vs Inform** | ⭐ **Bắn rồi quên (không ACK)** vs ⭐ **có ACK, gửi lại nếu mất (v2c+)** |
| ⭐⭐ **noAuthNoPriv / authNoPriv / authPriv** | ⭐ Chỉ username / xác thực không mã hóa / ⭐ **xác thực + MÃ HÓA** |
| ⭐ **USM / VACM / EngineID** | Mô hình bảo mật user / kiểm soát truy cập theo view / định danh agent |
| ⭐⭐ **NetFlow 7-tuple** | ⭐ src IP · dst IP · src port · dst port · protocol · ⭐ **ToS** · ⭐ **input interface** |
| ⭐ **NetFlow v5 / v9 / IPFIX** | Cố định, chỉ IPv4 / ⭐ **template, linh hoạt** / chuẩn IETF (v10) |
| ⭐⭐ **Flow Record / Exporter / Monitor / Sampler** | ⭐ **Đo gì / gửi đi đâu / ghép + cache / lấy mẫu 1-trên-N** |
| ⭐⭐ **`match` (key) vs `collect` (non-key)** | ⭐ **ĐỊNH NGHĨA flow** vs ⭐ **chỉ ghi thêm** |
| ⭐⭐ **`cache timeout active`** | ⭐ **Bao lâu thì đẩy flow ĐANG CHẠY lên collector.** 🔴 **Mặc định 1800s (30 phút)** |
| ⭐ **`cache timeout inactive`** | Flow im lặng bao lâu thì coi là kết thúc (mặc định 15s) |
| ⭐ **Emergency aged** | 🔴 ⭐ **Cache đầy, flow bị đẩy ra sớm → số liệu SAI** |
| ⭐⭐ **SPAN / RSPAN / ERSPAN** | ⭐ **Cùng switch** / ⭐ **qua L2 bằng RSPAN VLAN** / ⭐ **qua L3 bằng GRE** |
| ⭐ **`remote-span`** | ⭐ **Dòng bắt buộc trên RSPAN VLAN, ở MỌI switch trên đường đi** |
| ⭐ **`erspan-id`** | ⭐ Phải khớp hai đầu ERSPAN |
| ⭐ **`encapsulation replicate`** | Giữ nguyên tag 802.1Q/CDP/STP trong bản sao SPAN |
| ⭐⭐ **SPAN destination** | 🔴 ⭐ **Cổng bị trưng dụng: ngừng forward, không STP, không học MAC** — ⭐ **thiết bị cắm vào MẤT MẠNG dù `up/up`** |
| ⭐ **Oversubscription (SPAN)** | 🔴 Nhiều nguồn → một đích = ⭐ **mất gói ÂM THẦM** |
| ⭐⭐ **IP SLA operation** | `icmp-echo` (không cần Responder) · ⭐ **`udp-jitter` (BẮT BUỘC Responder)** · `tcp-connect` · `http` · `dns` |
| ⭐⭐ **`ip sla schedule`** | ⭐⭐ **Dòng KÍCH HOẠT — quên là operation KHÔNG BAO GIỜ CHẠY** |
| ⭐⭐ **IP SLA Responder** | ⭐ **Đóng dấu thời gian ở đầu kia** → loại độ trễ xử lý + ⭐ **tính được one-way delay** |
| ⭐ **`track ... reachability` vs `state`** | ⭐ **Sống/chết** vs ⭐ **có vượt `threshold` không** |
| ⭐ **Jitter SD / DS** | Độ dao động chiều **Source→Dest** / **Dest→Source** |
| ⭐⭐ **MOS score** | ⭐ Điểm chất lượng thoại 1–5 — ⭐ **> 4.0 là tốt** |
| ⭐⭐ **Conditional debug** | ⭐ Debug **có lọc** — `debug ip packet <acl>` · `debug condition interface` |
| ⭐⭐ **`undebug all` / `u all`** | ⭐⭐ **Lệnh cứu hộ — học thuộc trước khi bật bất kỳ debug nào** |
| ⭐ **Process-switched vs CEF** | ⭐ **`debug ip packet` CHỈ thấy gói process-switched** *(M01)* |
| ⭐ **Punt** | Gói bị đẩy từ ASIC lên CPU |
| ⭐ **`df-bit` + `size`** | ⭐ **Tìm MTU** *(Module-08 §4.4)* · ⭐ **`sweep`** = tự dò ngưỡng |
| ⭐ **Health Score** | Điểm 0–10 cho thiết bị/client trên DNA Center |
| ⭐⭐ **Path Trace** | ⭐ Đường đi hop-by-hop **kèm phân tích ACL/QoS** — hơn hẳn `traceroute` |
| ⭐⭐ **Network Time Travel** | ⭐ **Tua ngược trạng thái mạng về quá khứ** |
| ⭐ **Client 360 / Device 360** | Toàn bộ thông tin một client/thiết bị trên một trang |
| ⭐ **Sensor mode** | ⭐ AP đóng vai **client giả** chạy test chủ động *(M07A §5)* |
| ⭐⭐ **NETCONF** | ⭐ **SSH 830 · XML · RPC · CÓ candidate datastore + rollback** |
| ⭐⭐ **RESTCONF** | ⭐ **HTTPS 443 · JSON/XML · HTTP verb · KHÔNG có rollback** |
| ⭐ **YANG** | Mô hình dữ liệu dùng chung cho NETCONF/RESTCONF/telemetry |
| ⭐ **Model-Driven Telemetry (MDT)** | ⭐ **PUSH gần real-time** — thay thế mô hình **PULL** của SNMP |
| ⭐ **Dial-in / Dial-out** | Collector kết nối vào thiết bị / thiết bị chủ động gửi ra |

---

## 🎯 20. ĐÚC KẾT MODULE-11

**3 điều rút ra:**

1. 🔴 ⭐⭐ **Năm công cụ là năm GIÁC QUAN khác nhau — và chúng đều chết nếu đồng hồ sai:**
   ⭐ **Syslog** (*"đã xảy ra chuyện gì"*) · ⭐ **SNMP** (*"tình trạng hiện giờ"*) ·
   ⭐ **NetFlow** (*"ai ăn băng thông"*) · ⭐ **SPAN** (*"trong gói có gì"*) · ⭐ **IP SLA** (*"chất lượng có đạt không"*).
   ⭐⭐ **Nguyên tắc dùng: đi từ RẺ đến ĐẮT** — syslog và NetFlow chạy sẵn 24/7, ⭐ **SPAN và debug
   để cuối cùng.** ⭐ Và câu chốt: ⭐⭐ **NetFlow để PHÁT HIỆN, SPAN để SOI.**
   🔴 ⭐ **NTP là điều kiện tiên quyết của tất cả** — sai giờ thì log không đối chiếu được,
   one-way delay vô nghĩa, biểu đồ NetFlow sai thời điểm.

2. 🔴 ⭐⭐ **Bốn con số / cơ chế bị hỏi nhiều nhất, và cả bốn đều phản trực giác:**
   ⭐⭐ **Syslog severity: số NHỎ = nghiêm trọng HƠN**, và ⭐ **`logging trap 4` gửi 0–4 chứ không phải
   "chỉ 4" hay "4 trở lên"** — hệ quả là ⭐ **thấy `%LINK-3` down mà không thấy `%LINEPROTO-5` up lại.**
   ⭐⭐ **NetFlow là 7-tuple** (5-tuple **cộng ToS và input interface**), và ⭐⭐ **`match` = KEY định nghĩa
   flow, `collect` chỉ ghi thêm** — ⭐ thêm `match` = cache đầy nhanh.
   ⭐⭐ **`cache timeout active` mặc định 1800 giây (30 phút)** → ⭐ **collector không thấy flow dài.**
   ⭐⭐ **SNMP: agent nghe 161, manager nghe 162 · Trap không ACK, Inform có ACK · chỉ `authPriv` mới mã hóa.**

3. ⭐⭐ **Ba cái bẫy "im lặng" — hỏng mà không báo lỗi, và đó là lý do chúng nguy hiểm:**
   🔴 ⭐⭐ **SPAN destination biến cổng thành "câm"** — ⭐ **`show interface` vẫn `up/up`, đèn vẫn sáng,
   nhưng thiết bị cắm vào MẤT MẠNG.** *(Cộng thêm **oversubscription** làm mất gói âm thầm.)*
   🔴 ⭐⭐ **Quên `ip sla schedule`** — ⭐ **config trông hoàn hảo nhưng operation KHÔNG BAO GIỜ CHẠY.**
   🔴 ⭐⭐ **`debug ip packet` không thấy traffic đi xuyên qua router** — ⭐ **vì CEF xử lý, không punt lên CPU.**
   ⭐ Và bài học vận hành lớn nhất: ⭐⭐ **`no logging console` + `logging buffered` TRƯỚC KHI debug,
   và thuộc lòng `u all`.**

🧠 **Một câu để nhớ:** *Giám sát mạng là ⭐ **có đủ năm giác quan và biết dùng đúng cái nào**:
⭐ **syslog là nhật ký, SNMP là bắt mạch, NetFlow là sổ chi tiêu, SPAN là kính hiển vi,
IP SLA là máy đo huyết áp đeo liên tục** — ⭐ **và tất cả đều vô dụng nếu đồng hồ sai giờ**.
⭐ **NetFlow là hóa đơn điện thoại (ai gọi ai, bao lâu), SPAN là ghi âm cuộc gọi (nghe được hết
nhưng không ghi mãi được)** — ⭐ **nên dùng cái đầu để PHÁT HIỆN, cái sau để SOI**. Còn ⭐ **debug
là con dao mổ: rất sắc, và nếu không tắt console trước thì bạn mổ chính mình.***

---

### ✅ TỰ CHẤM

**Phần A — Trả lời được bằng lời của mình:**

| # | Câu | ✅ |
|:---:|---|:---:|
| 1 | 🔴 ⭐⭐ Vì sao **NTP là điều kiện tiên quyết** — nêu 3 hậu quả nếu sai giờ | ☐ |
| 2 | ⭐ Ba dòng `service ...` phải có · ⭐ **mặc định log hiện gì nếu không bật timestamps** | ☐ |
| 3 | ⭐⭐ **8 mức severity theo thứ tự** · ⭐ **số nhỏ hay lớn nghiêm trọng hơn** | ☐ |
| 4 | 🔴 ⭐⭐ **`logging trap 4` gửi những mức nào** | ☐ |
| 5 | 🔴 ⭐⭐ Vì sao `%LINK-3` và `%LINEPROTO-5` **cùng một sự kiện mà khác severity** — hệ quả | ☐ |
| 6 | ⭐ Mổ xẻ một dòng syslog thành **5 phần** | ☐ |
| 7 | ⭐ **5 nơi log có thể đi tới** · ⭐ **vì sao console nguy hiểm** | ☐ |
| 8 | ⭐ `logging source-interface` giải quyết vấn đề gì | ☐ |
| 9 | ⭐ 4 thành phần SNMP · ⭐⭐ **port 161 vs 162 — ai nghe cái nào** | ☐ |
| 10 | ⭐⭐ **Trap vs Inform** — cái nào có ACK, có từ phiên bản nào | ☐ |
| 11 | ⭐⭐ **v1 vs v2c vs v3** — cái nào có mã hóa, GetBulk có từ đâu | ☐ |
| 12 | ⭐⭐ **3 security level của v3** — cái nào có mã hóa | ☐ |
| 13 | ⭐ Thứ tự cấu hình v3: **VIEW → GROUP → USER** | ☐ |
| 14 | ⭐⭐ **NetFlow vs SPAN** — mỗi cái trả lời câu hỏi gì | ☐ |
| 15 | 🔴 ⭐⭐ **7 trường định nghĩa flow** (đừng quên **ToS** và **input interface**) | ☐ |
| 16 | ⭐ **NetFlow v5 vs v9 vs IPFIX** | ☐ |
| 17 | ⭐⭐ **4 thành phần Flexible NetFlow** | ☐ |
| 18 | 🔴 ⭐⭐ **`match` vs `collect`** — cái nào định nghĩa flow · hệ quả khi thêm match | ☐ |
| 19 | 🔴 ⭐⭐ **`cache timeout active` mặc định là bao nhiêu** · vì sao nguy hiểm | ☐ |
| 20 | ⭐ **`Emergency aged`** nghĩa là gì · 3 cách sửa | ☐ |
| 21 | ⭐⭐ **Bảng SPAN / RSPAN / ERSPAN** — phạm vi + cơ chế vận chuyển | ☐ |
| 22 | 🔴 ⭐⭐ **Cổng SPAN destination bị gì** — vì sao nguy hiểm | ☐ |
| 23 | ⭐ **Oversubscription của SPAN** — hậu quả | ☐ |
| 24 | ⭐⭐ **3 lỗi RSPAN kinh điển** · ⭐ `remote-span` phải có ở đâu | ☐ |
| 25 | ⭐ **ERSPAN dùng gì để vận chuyển** · hệ quả về MTU · `erspan-id` | ☐ |
| 26 | ⭐ Các loại **IP SLA operation** · ⭐ **cái nào cần Responder** | ☐ |
| 27 | 🔴 ⭐⭐ **`ip sla schedule`** — quên thì sao, dấu hiệu nhận biết | ☐ |
| 28 | ⭐⭐ **Responder làm 2 việc gì** · ⭐ **vì sao one-way delay cần NTP** | ☐ |
| 29 | ⭐⭐ **`track reachability` vs `track state`** — cái nào cho VoIP | ☐ |
| 30 | ⭐ Đọc kết quả `udp-jitter` · ⭐ **4 ngưỡng VoIP (150/30/1/MOS>4)** | ☐ |
| 31 | 🔴 ⭐⭐ **Vì sao `debug all` làm treo router** — thủ phạm thật là gì | ☐ |
| 32 | ⭐⭐ **Quy trình debug an toàn 5 bước** | ☐ |
| 33 | ⭐⭐ **3 cách conditional debug** | ☐ |
| 34 | 🔴 ⭐⭐ **Vì sao `debug ip packet` không thấy traffic đi xuyên router** | ☐ |
| 35 | ⭐ **`ping df-bit size`** dùng làm gì · chế độ `sweep` | ☐ |
| 36 | ⭐⭐ **Đọc traceroute**: `* * *` giữa chừng vs tới hết · RTT tăng rồi giảm | ☐ |
| 37 | ⭐ **DNA Center Assurance**: Health Score, Client 360, ⭐ **Path Trace**, ⭐ **Network Time Travel**, Sensors | ☐ |
| 38 | ⭐ **Path Trace hơn `traceroute` ở điểm nào** | ☐ |
| 39 | 🔴 ⭐⭐ **NETCONF vs RESTCONF**: port, định dạng, ⭐ **cái nào có rollback** | ☐ |
| 40 | 🔴 ⭐⭐ **NETCONF/RESTCONF thuộc DOMAIN NÀO** (bẫy §0.2!) | ☐ |
| 41 | ⭐ **SNMP (PULL) vs Model-Driven Telemetry (PUSH)** | ☐ |
| 42 | ⭐⭐ **Quy trình 6 bước chẩn đoán "mạng chậm"** — và nguyên tắc *rẻ trước, đắt sau* | ☐ |

**Phần B — Lab:**

| # | Yêu cầu | ✅ |
|:---:|---|:---:|
| 1 | ⭐ **LAB A2**: sinh sự kiện, thấy **CẢ `%LINK-3` LẪN `%LINEPROTO-5`** | ⭐ ☐ |
| 2 | ⭐ Mổ xẻ một dòng log thật thành **5 phần** | ☐ |
| 3 | ⭐⭐ **LAB A3**: so sánh **`Buffer logging` vs `Trap logging`** — chênh lệch số message | ⭐⭐ ☐ |
| 4 | ⭐ **LAB A4**: đổi `logging trap 4 → 6`, xác nhận số message gửi tăng | ☐ |
| 5 | ⭐ **LAB B**: cấu hình SNMPv3, `show snmp user` hiện **SHA + AES128** | ☐ |
| 6 | ⭐ Bỏ `priv` khi tạo user → thấy **`Privacy Protocol: None`** = `authNoPriv` | ⭐ ☐ |
| 7 | ⭐⭐ **LAB C1–C2**: cấu hình đủ **4 thành phần FNF**, `show flow monitor cache format table` **ra bảng flow** | ⭐⭐ ☐ |
| 8 | ⭐ Đọc được bảng flow và chỉ ra **"ai đang tải nhiều nhất"** | ☐ |
| 9 | ⭐⭐ **LAB C3**: bỏ một `match` → ⭐ **số flow GIẢM** → hiểu key vs non-key | ⭐⭐ ☐ |
| 10 | ⭐ **LAB C4**: kiểm tra `Emergency aged` = 0 và `Packets sent` của exporter | ☐ |
| 11 | ⭐⭐ **LAB C5**: đặt `cache timeout active 1800` → ⭐ **`Packets sent` gần như không tăng** | ⭐⭐ ☐ |
| 12 | ⭐ **LAB D**: cấu hình SPAN, `show monitor session 1` đúng source/destination | ☐ |
| 13 | 🔴 ⭐⭐ **LAB D1**: tái hiện **"cổng câm"** — thiết bị mất mạng dù cổng **`up/up`** | ⭐⭐ ☐ |
| 14 | ⭐ **LAB D2**: SPAN theo VLAN + `encapsulation replicate` | ☐ |
| 15 | 🚀 **LAB D3**: RSPAN — và thử **bỏ `remote-span`** để thấy nó hỏng | 🚀 ☐ |
| 16 | ⭐ **LAB E1**: `ip sla` + `track` — `show track 1` báo **Reachability Up** | ☐ |
| 17 | 🔴 ⭐⭐ **LAB E2**: quên `ip sla schedule` → ⭐ **"has not been scheduled"** | ⭐⭐ ☐ |
| 18 | ⭐⭐ **LAB E3**: test failover — shutdown → ⭐ **track Down → route TỰ BỊ GỠ** | ⭐⭐ ☐ |
| 19 | ⭐⭐ **LAB E4**: `udp-jitter` + Responder → đọc được **one-way SD/DS, jitter, MOS** | ⭐⭐ ☐ |
| 20 | ⭐ Đối chiếu kết quả với **4 ngưỡng VoIP** của Module-09 | ☐ |
| 21 | ⭐⭐ **LAB E5**: tắt Responder → ⭐ **`udp-jitter` Timeout, `icmp-echo` vẫn chạy** | ⭐⭐ ☐ |
| 22 | 🚀 ⭐⭐ **LAB F1**: debug an toàn đủ **5 bước**, dùng ACL lọc | 🚀 ⭐⭐ ☐ |
| 23 | 🚀 🔴 ⭐⭐ **LAB F2**: chứng minh **CEF làm debug không thấy traffic xuyên router** | 🚀 ⭐⭐ ☐ |
| 24 | 🚀 ⭐ **LAB F4**: bật `logging console debugging` + debug → ⭐ **thấy router chậm hẳn** | 🚀 ⭐ ☐ |
| 25 | 🚀 ⭐ **LAB G**: dùng `ping sweep df-bit` tìm ra ngưỡng MTU | 🚀 ☐ |
| 26 | 🚀 ⭐⭐ **LAB H**: gieo 1 lỗi rồi tự tìm ra bằng đúng công cụ (làm ≥ 4/8 tình huống) | 🚀 ⭐⭐ ☐ |
| 27 | 🚀 **LAB I**: chạy được **Path Trace** trên DevNet DNA Center | 🚀 ☐ |
| 28 | ⭐ Ghi ít nhất **3 mục** vào `SO-TAY-LOI.md` từ module này | ☐ |

> ⭐ **Nếu chỉ có thời gian làm một nửa:** ưu tiên ⭐⭐ **mục 3 (lọc syslog)**, ⭐⭐ **mục 7, 9, 11
> (Flexible NetFlow — LAB hay nhất module)**, ⭐⭐ **mục 13 (bẫy cổng câm)**, ⭐⭐ **mục 17–19, 21
> (IP SLA schedule + failover + Responder)**, và ⭐⭐ **mục 22–23 (debug an toàn + bẫy CEF)**.
>
> ⚠️ ⭐ **Chưa tick được ≥ 36/42 Phần A thì đọc lại §3, §5, §6, §7, §8** —
> ⭐ **năm mục đó là toàn bộ phần "configure and verify" của Domain 4.0.**
>
> 🔴 ⭐⭐ **NHẮC LẠI CẢNH BÁO §0.2:** ⭐ **Domain 4.0 CHƯA xong sau module này** —
> ⭐ **mục 4.7 (NETCONF/RESTCONF) nằm ở Module-12 §3.** ⭐ Đừng tick "xong Domain 4.0" vội.
>
> 🎉 ⭐ **Cộng dồn sau Module-11:** Infrastructure 30% + Security 20% + Architecture 15%
> + Virtualization 10% + **Assurance ~9%** (thiếu 4.7) = ⭐ **~84% nội dung đề.**
> ⭐ **Đây là mốc Tuần 17 của ROADMAP.**

---

## 🔗 21. TÀI LIỆU CHO MODULE NÀY

| Nguồn | Cụ thể |
|---|---|
| **Sách OCG 350-401** | Chương *Network Assurance*, *Foundational Network Programmability Concepts* |
| **Cisco doc** ⭐⭐ | ***Configuring System Message Logging*** — ⭐ tài liệu gốc cho §3, có bảng severity đầy đủ |
| **Cisco doc** ⭐ | *Troubleshooting and Fault Management — Syslog* · *System Message Guide* (tra ý nghĩa từng mnemonic) |
| **Cisco doc** ⭐⭐ | ***Configuring SNMP Support*** — ⭐ v3 view/group/user, trap vs inform |
| **Cisco doc** ⭐⭐ | ***Flexible NetFlow Configuration Guide*** — ⭐⭐ **tài liệu quan trọng nhất của §5**: record/exporter/monitor/sampler |
| **Cisco doc** ⭐ | *NetFlow Version 9 Flow-Record Format* · *Introduction to Cisco IOS NetFlow (White Paper)* — ⭐ giải thích 7-tuple |
| **Cisco doc** ⭐⭐ | ***Configuring SPAN and RSPAN*** — ⭐ **danh sách đầy đủ các hạn chế của SPAN destination** |
| **Cisco doc** ⭐ | *Configuring ERSPAN* — ⭐ cấu hình source/destination session |
| **Cisco doc** ⭐⭐ | ***IP SLAs Configuration Guide*** — ⭐ mọi loại operation, Responder, ⭐ chương *UDP Jitter* cho VoIP |
| **Cisco doc** ⭐ | *Configuring IP SLAs UDP Jitter Operations for VoIP* — ⭐ giải thích **MOS** |
| **Cisco doc** ⭐⭐ | ***Understanding the Ping and Traceroute Commands*** — ⭐ giải thích `* * *` và RTT bất thường |
| **Cisco doc** ⭐⭐ | ***Understanding Conditionally Triggered Debugging*** — ⭐ §8.3 |
| **Cisco doc** ⭐ | *Cisco DNA Center Assurance User Guide* — ⭐ Path Trace, Network Time Travel, Health Score |
| **Cisco doc** ⭐ | *Model-Driven Telemetry Configuration Guide* (§11) |
| **Cisco doc** ⭐ | *NETCONF/RESTCONF Programmability Configuration Guide* — ⭐ **mục 4.7**, học sâu ở Module-12 |
| **RFC 5424 / 3164** | Syslog Protocol (mới / cũ) |
| **RFC 3411–3418** | SNMPv3 framework |
| **RFC 3954 / 7011** | ⭐ **NetFlow v9** / ⭐ **IPFIX** |
| **RFC 6241 / 8040** | ⭐ **NETCONF** / ⭐ **RESTCONF** |
| **Cisco DevNet** ⭐ | `developer.cisco.com/site/sandbox/` — sandbox **DNA Center** (LAB I) |
| **Công cụ** ⭐ | ⭐ **Syslog server**: Kiwi (free), rsyslog, Graylog · ⭐ **NetFlow collector**: nfdump/nfsen, ntopng, Elastiflow · ⭐ **NMS**: Zabbix, LibreNMS, PRTG (free tier) · ⭐ **Wireshark** cho SPAN |
| **Video** ⭐ | CBT Nuggets ENCOR — module Network Assurance · **Keith Barker**: search `Keith Barker NetFlow`, `Keith Barker IP SLA`, `Keith Barker SPAN RSPAN ERSPAN` |
| **NetworkLessons** ⭐ | *Syslog*, *SNMP*, *Flexible NetFlow*, *SPAN/RSPAN/ERSPAN*, *IP SLA* — ⭐ nhiều bài free, có output mẫu |
| **Forum** | https://community.cisco.com — search: `logging trap severity levels`, `flexible netflow cache timeout active`, `span destination port not forwarding`, `rspan not working remote-span`, `ip sla not running schedule`, `udp jitter responder timeout`, `debug ip packet not showing traffic cef` |

---

**➡️ Tiếp theo:** Module-12 — Automation & Programmability
*(JSON/XML/YAML · REST API · **NETCONF/RESTCONF/YANG (mục 4.7!)** · EEM · Python netmiko/requests · Ansible · DNAC & vManage API — **Tuần 18–19**)*

> 🔴 ⭐⭐ **Module-12 khép lại HAI domain cùng lúc:** ⭐ **Domain 6.0 Automation (15%)**
> và ⭐ **mục 4.7 còn thiếu của Domain 4.0.**
>
> ⭐ **Và bạn có lợi thế lớn ở module này:** ⭐ **repo `network-automation-mastery` của bạn đã phủ
> phần lớn Ansible/Python/API** — ⭐ **học chéo được, đừng học lại từ đầu.**
> ⭐ Cộng thêm ba mối nối sẵn có: ⭐ **REST API security** ([Module-10 §10](Module-10-Security.md)) ·
> ⭐ **luồng token DNAC/vManage** · ⭐ **kinh nghiệm Terraform/Ansible đi làm của bạn.**
