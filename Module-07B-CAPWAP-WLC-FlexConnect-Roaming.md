# Module-07B — CAPWAP, WLC, FlexConnect & Roaming

> 🧭 **Lộ trình:** [Module-07A](Module-07A-Wireless-RF-802.11-AP-Antenna.md) → `[Bạn đang ở đây] Module-07B` → Module-08 (Virtualization & Overlay)
>
> 📊 **Blueprint — Domain 3.3 Wireless (thuộc Infrastructure 30%):**
> · **3.3.c — Describe access point discovery and join process (discovery algorithms, WLC selection process)**
> · **3.3.d — Describe the main principles and use cases for Layer 2 and Layer 3 roaming**
> · 🔴  **3.3.e — Troubleshoot WLAN configuration and wireless client connectivity issues**
>
> 📊 Chạm thêm: **5.4 — Wireless security features (EAP, WebAuth, PSK)** — giới thiệu ở §8, đào sâu ở Module-10
>
> ⏱️ **Tuần 13** · 8–10 giờ

---

# 📌 TÓM TẮT — đọc 10 phút là nắm khung

## Module này trả lời một câu hỏi duy nhất

> **AP là một hộp nhỏ gắn trần, không có cấu hình gì. Vậy nó lấy cấu hình ở đâu,
> và làm sao client đi lại khắp tòa nhà mà không rớt mạng?**

## Split-MAC — hiểu cái này là hiểu cả module

```
   ┌───────── AP (lễ tân giỏi tay chân, KHÔNG có quyền) ─────────┐
   │  Việc phải xong trong MICRO-GIÂY  ->  AP tự làm             │
   │   · Beacon, Probe Response                                  │
   │   · ACK  (phải trả trong SIFS ~10 us — không kịp hỏi WLC)   │
   │   · Mã hóa/giải mã AES-CCMP                                 │
   │   · CSMA/CA, backoff, retransmission                        │
   └──────────────────────┬──────────────────────────────────────┘
                          │
          CAPWAP CONTROL  │  UDP 5246  (DTLS LUÔN bật)
          CAPWAP DATA     │  UDP 5247  (DTLS tùy chọn)
                          │
   ┌──────────────────────┴──────────────────────────────────────┐
   │  WLC (sếp) — việc chậm hơn được  ->  WLC làm                │
   │   · Xác thực 802.1X / RADIUS                                │
   │   · Quản lý client database, quyết định roaming             │
   │   · RRM: chọn channel và công suất cho TOÀN BỘ AP           │
   └─────────────────────────────────────────────────────────────┘

   Nguyên tắc chia: "việc này có phải xong trong vài micro-giây không?"
```

## 7 ý phải nhớ

| # | Ý | Một câu |
|:---:|---|---|
| 1 | ⭐ **CAPWAP hai tunnel** | **Control = UDP 5246** *(DTLS luôn bật)* · **Data = UDP 5247** *(DTLS tùy chọn, mặc định tắt)* |
| 2 | **5 cách AP tìm WLC** | Primed/NVRAM · tĩnh · **DHCP option 43** · **DNS** · broadcast.<br>🔴 **Broadcast KHÔNG qua router** nên khác subnet phải có option 43 hoặc DNS |
| 3 | ⭐ **Thứ tự chọn WLC** | Primary → Secondary → Tertiary → Master → **Least-loaded**.<br> *Least-loaded nghĩa là **dư nhiều chỗ nhất**, KHÔNG phải ít AP nhất* |
| 4 | 🔴  **Sai giờ thì AP không join** | DTLS dùng **chứng thư số** nên đồng hồ sai sẽ làm chứng thư bị coi là chưa hiệu lực |
| 5 | ⭐ **Roaming L2 vs L3** | L2 (cùng subnet) bản ghi **MOVE**, không cần tunnel · **L3** (khác subnet) bản ghi **COPY** + **mobility tunnel**, **ANCHOR** là WLC gốc, **FOREIGN** là WLC hiện tại |
| 6 | ⭐ **FlexConnect standalone** | Local switching + **local auth** thì sống hết · Local switching + **central auth** thì client **cũ sống, mới chết** · **Central switching** thì **rớt ngay** |
| 7 | 🔴  **AP Registered KHÔNG phải là SSID đã phát** | Còn phải **gán Policy Tag**. Luôn chạy `show ap tag summary` |

## Bảng lệnh cốt lõi

| Lệnh | Cho biết gì |
|---|---|
| `show ap summary` | AP nào up, mode gì, bao nhiêu client |
| ⭐ `show ap tag summary` | **AP đang dùng tag nào** — thiếu tag là không phát SSID |
| ⭐ `show ap join stats detailed <mac>` | **AP hỏng ở BƯỚC NÀO** của quá trình join |
| ⭐ `show wireless client mac-address <mac> detail` | **Client dừng ở State nào** — lệnh quan trọng nhất |
| `show wireless mobility summary` | Mobility peer Up hay Down |
| ⭐ `show interface trunk` *(trên SWITCH)* | **VLAN có thật sự đi được không** |

## 🗺️ Bố cục module

| Phần | Tên | Thời gian |
|:---:|---|:---:|
| **1** | 🧠 **CÁI ĐÓ LÀ GÌ** — 4 ví von | 45 phút |
| **2** | ⚙️ **NÓ CHẠY THẾ NÀO** — ⭐ **§10 Troubleshoot là phần quan trọng nhất** | 5 giờ |
| **3** | 🧪 **NHÌN THẤY NÓ** — [LAB 07B](Module-07B-LAB.md), ⭐ **học bằng đầu, RAM 0 GB** | 3 giờ |
| **4** | 🏗️ **TOPO & KIẾN TRÚC** — Local mode vs FlexConnect | 45 phút |
| **📎** | **PHỤ LỤC** — 🔴 không đọc lần đầu | — |

> 🔴  **Điều quan trọng nhất của module này:** mục **3.3.e (Troubleshoot)** là
> **mục DUY NHẤT trong cả Domain 3.3 không dùng từ Describe**.
>
> Nghĩa là đề **sẽ cho bạn một tình huống hỏng** và bắt chỉ ra nguyên nhân.
> ⭐ **§10 (quy trình 6 tầng) và [LAB B](Module-07B-LAB.md) là phần đáng đầu tư nhất.**
>
> 🎉 **Hết module này là hết khối Wireless — và hết trọn Domain 3.0 Infrastructure (30% đề).**

---

## ⭐ 0. Phạm vi

### 0.1 Điều khác biệt của module này

> 🔴  **3.3.e là mục DUY NHẤT trong toàn bộ Domain 3.3 không dùng từ "Describe" — nó dùng "Troubleshoot".**
>
> Nghĩa là: ⭐ **đề SẼ cho bạn một tình huống** — *"client không vào được mạng"*, *"AP không join WLC"*,
> *"client roam thì rớt cuộc gọi"* — ⭐ **và bắt bạn chỉ ra nguyên nhân**.
> ⭐ **§9 (phương pháp troubleshoot 6 tầng) là phần quan trọng nhất của module này.**

| Chủ đề | Blueprint | Mức cần đạt | Thời gian |
|---|---|---|---|
| ⭐ **Split-MAC** — AP làm gì, WLC làm gì | nền cho 3.3.c | **Bảng phân chia chức năng** | 45 phút |
| ⭐ **CAPWAP** — 2 tunnel, port, DTLS, MTU | 3.3.c | **Nhớ port 5246/5247** + hiểu vấn đề MTU | 45 phút |
| ⭐ **AP join process** — 6 giai đoạn | 3.3.c | **Thuộc thứ tự** | 1 giờ |
| ⭐ **Discovery algorithms** (5 cách tìm WLC) | **3.3.c nói thẳng** | **Học thuộc 5 cách + thứ tự** | 1 giờ |
| ⭐ **WLC selection process** | **3.3.c nói thẳng** | **Học thuộc thứ tự ưu tiên** | 30 phút |
| ⭐ **AP HA** (primary/secondary/tertiary, SSO, N+1) | 3.3.c + 1.1.b | Hiểu cơ chế | 30 phút |
| ⭐ **FlexConnect** — switching/auth, standalone | 3.3.b nối tiếp | **Bảng "cái gì sống sót khi mất WAN"** | 1 giờ |
| ⭐ **Roaming L2 vs L3** — anchor/foreign | **3.3.d nói thẳng** | **Phần đề hỏi nhiều nhất của 07B** | 1.5 giờ |
| ⭐ **Fast roaming** (11r/k/v, OKC, PMK cache) | 3.3.d | Phân biệt được các cơ chế | 45 phút |
| ⭐ **WLAN config** — mô hình Tag của C9800 | 3.3.e | Hiểu chuỗi WLAN→Policy→Tag→AP | 45 phút |
| 🟡 **Wireless security** (WPA2/3, EAP, WebAuth) | 5.4 | ⭐ Vừa đủ để **troubleshoot**. Đào sâu ở **Module-10** | 45 phút |
| 🔴  **TROUBLESHOOT WLAN & client** | **3.3.e** | **Phương pháp 6 tầng + bảng triệu chứng** | 1.5 giờ |
| WLC deployment model & location services | 1.2.a, 1.2.b | ➡️ **Module-09** (phần thiết kế/kiến trúc) | — |

### 0.2 ⭐ Về vấn đề "không có thiết bị"

| Thực tế | Cách xử lý trong module này |
|---|---|
| PC 16 GB **không dựng nổi** WLC + AP thật | ⭐ Dùng **DevNet Sandbox Catalyst 9800 always-on** (miễn phí) — LAB C |
| Không có AP thật để xem quá trình join | ⭐ **LAB A: "lab trên giấy"** — cho tình huống, bạn suy ra AP sẽ join WLC nào và vì sao.  **Đây chính là dạng câu hỏi của đề** |
| Không tái hiện được lỗi client thật | ⭐ **LAB B: bảng chẩn đoán 12 tình huống** — luyện đúng kỹ năng 3.3.e |
| Muốn thấy roaming thật | ⭐ **LAB D: dùng chính laptop** — `wlanreport` + đi bộ quanh văn phòng, xem BSSID đổi |

> ⭐ **Đây là module bạn học bằng ĐẦU chứ không bằng tay.** Đừng thấy thiếu lab mà nản —
> đề cũng hỏi bạn bằng đầu, không bắt gõ lệnh.

---

## ✅ 1. Chuẩn bị

| Cần có | Chi tiết |
|---|---|
| **Kiến thức trước** | ⭐ **Module-07A toàn bộ** (RSSI, SNR, BSSID, ESS, AP mode) · Module-01 §2 (3 plane) · Module-P0 §2.1 (VLAN/trunk) · Module-02 §6 (trunk/native VLAN) · Module-03 (routing, để hiểu vì sao roam L3 cần tunnel) |
| **Lab** | ⭐ Không cần EVE-NG. Dùng **DevNet Sandbox** + laptop |
| **RAM** | **0 GB** |
| **Cần chuẩn bị** | Tài khoản Cisco (miễn phí) để vào DevNet Sandbox · laptop Windows có Wi-Fi |
| **Thời lượng** | 5h lý thuyết · 3h lab · 1h quiz |

---

## 🧠 PHẦN 1 — CÁI ĐÓ LÀ GÌ

> **Đọc phần này TRƯỚC, đọc một mạch.** Không lệnh, không bảng tra.
>
> Module-07B toàn cơ chế vô hình: AP nói chuyện với WLC qua đường hầm, client nhảy giữa
> các AP mà không đứt kết nối. Bốn ví von dưới đây làm chúng hiện ra.
>
> **Tự kiểm tra:** đọc xong mỗi mục, gấp tài liệu lại, nói lại trong 3 câu.

### 2.1 CAPWAP là "cái ống nói" giữa AP và WLC

⭐ AP giống một **nhân viên lễ tân giỏi việc tay chân** nhưng **không có quyền quyết định**:
- Lễ tân **tự chào khách, tự gật đầu xác nhận** (beacon, ACK) — không thể chạy đi hỏi sếp mỗi lần
- Nhưng ⭐ **"anh này có được vào không?"** thì phải bấm  **ống nói** hỏi sếp (CAPWAP control 5246)
- Và ⭐ **hàng hóa khách mang theo** thì đưa qua  **băng chuyền riêng** (CAPWAP data 5247)

⭐ **Ống nói luôn được mã hóa** (DTLS bắt buộc) vì nó chở mật khẩu và cấu hình.
⭐ **Băng chuyền thì thường không** — vì hàng đã được đóng gói mã hóa từ trước rồi (WPA2), và mã hóa thêm sẽ chậm.

⭐ **FlexConnect** = lễ tân được **giao chìa khóa cửa sau**: khách đã duyệt rồi thì
⭐ **cho đi thẳng ra ngoài**, không cần đi vòng qua phòng sếp.

### 2.2 Roaming L3 là "chuyển tiếp thư"

Bạn có địa chỉ nhà ở Quận 1 (⭐ **IP gốc**). Bạn chuyển tạm sang Quận 7 ( **foreign**).

- 🔴 **Cách tệ:** khai địa chỉ mới →  **mọi thư đang gửi tới địa chỉ cũ đều thất lạc** (session TCP đứt)
- ⭐ **Cách hay:** đăng ký  **dịch vụ chuyển tiếp thư** ở bưu điện Quận 1 ( **anchor**).
  Thư vẫn gửi tới Quận 1, ⭐ bưu điện Quận 1 chuyển tiếp sang Quận 7.

⭐ Với thế giới bên ngoài,  **bạn vẫn ở Quận 1**. Đó chính là mobility tunnel.
⭐ **Anchor = bưu điện nơi bạn đăng ký hộ khẩu. Foreign = nơi bạn đang ở thật.**

⭐ **Và guest anchor** là phiên bản cố ý: khách vào tòa nhà nào cũng được, nhưng
⭐ **thư của khách luôn được chuyển hết về một bưu điện đặt ngoài hàng rào (DMZ)** —
để không ai đi lang thang trong nhà.

### 2.3 Vì sao "AP join được nhưng không phát SSID" lại phổ biến đến thế

⭐ Vì có **hai chuỗi độc lập** phải cùng đúng:

```
   Chuỗi 1 — AP có kết nối được với WLC không?
       IP → Discovery → Select → DTLS → Image → Config → AP "UP"

   Chuỗi 2 — WLC có BẢO AP phát gì không?
       WLAN Profile + Policy Profile → Policy Tag → GÁN TAG CHO AP
```

⭐ **Chuỗi 1 đúng mà chuỗi 2 sai** → AP hiện `Registered/Up` trên WLC,
⭐ **đèn xanh, mọi thứ trông ổn — nhưng trên không trung không có SSID nào.**
🔴  **Đây là lý do bạn phải luôn chạy `show ap tag summary`, không chỉ `show ap summary`.**

### 2.4 Split-MAC: ai làm gì phụ thuộc vào "có kịp không"

⭐ **Một câu hỏi duy nhất quyết định mọi thứ:** *"Việc này có phải xong trong vài micro-giây không?"*

- ⭐ **ACK** phải trả trong  **SIFS ~10 µs** →  **không thể** chạy về WLC (đi về mất hàng ms) → **AP làm**
- ⭐ **Xác thực RADIUS** mất hàng trăm ms và **client sẵn sàng chờ** →  **WLC làm**
- ⭐ **Chọn channel cho toàn tòa nhà** cần dữ liệu của **mọi AP** → chỉ WLC có →  **WLC làm**

⭐ **Nhớ nguyên tắc này thì không cần học thuộc bảng §2.2.**


---

## ⚙️ PHẦN 2 — NÓ CHẠY THẾ NÀO

> | Phần 1 (ví von) | → | Phần 2 (cơ chế) |
> |---|:---:|---|
> | §2.1 ống nói giữa lễ tân và sếp | → | **§3 Split-MAC · §4 CAPWAP** ⭐ |
> | §2.2 dịch vụ chuyển tiếp thư | → | **§7 Roaming L3 (anchor/foreign)** ⭐ |
> | §2.3 hai chuỗi độc lập | → | **§10 Troubleshoot** 🔴  |
> | §2.4 ai làm gì phụ thuộc "có kịp không" | → | **§3 Split-MAC** |
>
> ⚠️ **Mục §10 (Troubleshoot) là phần quan trọng nhất module** — vì **3.3.e là mục DUY NHẤT
> trong Domain 3.3 không dùng từ "Describe"**. Đề sẽ cho tình huống và bắt bạn chỉ ra nguyên nhân.

---

## 📘 3. SPLIT-MAC — nền tảng của mọi thứ trong module này

### 3.1 Autonomous vs Lightweight — nhắc lại và mở rộng

| | ⭐ **Autonomous AP** | **Lightweight AP (LAP)** |
|---|---|---|
| Cấu hình nằm ở đâu | ⭐ **Trong chính AP** | **Trên WLC** — AP tải về mỗi lần join |
| Cần WLC? | ❌ Không | ✅ **Bắt buộc** |
| Quản lý 200 AP | 🔴 Vào từng cái một | Một chỗ duy nhất |
| RRM / roaming / rogue detection tập trung | ❌ Không có | ✅ Có |
| ⭐ Mất WLC thì sao? | Vẫn chạy bình thường | **Ngừng phục vụ** — *(trừ FlexConnect, xem §5)* |
| Còn dùng không? | Vài trường hợp rất nhỏ | ⭐ **Gần như toàn bộ mạng doanh nghiệp hiện nay** |

### 3.2 ⭐ Split-MAC — chia việc như thế nào

> ⭐ **Ý tưởng:** chức năng MAC của 802.11 bị **chẻ đôi** giữa AP và WLC.
> ⭐ **Nguyên tắc chia: việc gì phải làm NGAY (tính bằng micro-giây) thì để ở AP.
> Việc gì có thể chậm hơn một chút thì đưa lên WLC.**

```
   ┌─────────────────── AP (Lightweight) ───────────────────┐
   │  REAL-TIME — phải xong trong micro-giây             │
   │  · Beacon & Probe Response                             │
   │  · ACK cho frame nhận được                          │
   │  · Điều khiển truy nhập môi trường (CSMA/CA, backoff)  │
   │  · Mã hóa / giải mã frame (AES-CCMP)                   │
   │  · Frame queueing theo QoS · retransmission            │
   │  · Đo & báo cáo RF (RSSI, noise, rogue)                │
   └───────────────────────────┬────────────────────────────┘
                               │  CAPWAP tunnel
   ┌───────────────────────────┴────────────────────────────┐
   │  WLC — NON-REAL-TIME — có thể chậm vài ms           │
   │  · Xác thực & liên lạc RADIUS (802.1X)              │
   │  · Association / Reassociation (quản lý client DB)  │
   │  · Quản lý key bảo mật                              │
   │  · RRM: chọn channel & công suất (DCA/TPC)          │
   │  · Quyết định roaming & mobility tunnel             │
   │  · Chính sách QoS, ACL, VLAN mapping                   │
   │  · Bridging ra mạng có dây (nếu central switching)     │
   └────────────────────────────────────────────────────────┘
```

| ⭐ Chức năng | Ai làm | Vì sao |
|---|:---:|---|
| Beacon, Probe Response | **AP** | Phải phát đều đặn, không chờ được |
| ⭐ **ACK frame 802.11** | **AP** | Phải trả trong **SIFS** (~10 µs) — không thể chạy về WLC |
| CSMA/CA, backoff, NAV | **AP** | Điều phối tức thời trên không trung |
| ⭐ **Mã hóa/giải mã (AES-CCMP)** | **AP** | Từng frame, cần tốc độ dòng |
| Retransmission, fragmentation | **AP** | Tức thời |
| Đo RSSI/noise, phát hiện rogue | **AP** (báo cáo) | AP là "tai mắt", WLC là "bộ não" |
| ⭐ **802.1X / RADIUS** | **WLC** | Mất hàng trăm ms, không cần realtime |
| ⭐ **Association / client database** | **WLC** | Cần cái nhìn toàn cục để roam |
| ⭐ **Quản lý & phân phối key** | **WLC** | Cần chia key cho nhiều AP (fast roaming) |
| ⭐ **RRM (DCA / TPC)** | **WLC** | Cần dữ liệu **của tất cả AP** mới quyết được |
| ⭐ **Roaming & mobility** | **WLC** | Chỉ WLC mới biết client đang ở AP nào |
| VLAN / ACL / QoS policy | **WLC** | Chính sách tập trung |

> 🔴  **Bẫy đề hay gặp:** *"Chức năng nào do AP xử lý trong kiến trúc split-MAC?"*
> ⭐ Nhớ nguyên tắc:  **cái gì tính bằng micro-giây → AP.**  **ACK và mã hóa luôn ở AP.**
> 🔴  **Xác thực 802.1X KHÔNG ở AP** (trừ FlexConnect local auth — xem §5).

### 3.3 ⭐ Nền tảng WLC — biết tên để không bỡ ngỡ

| Nền tảng | OS | Ghi chú |
|---|---|---|
| ⭐ **Catalyst 9800** (9800-40, -80, **-L**,  **-CL** = máy ảo) | **IOS-XE** | **Dòng hiện tại.** CLI giống router/switch IOS.  **Dùng mô hình Tag** (§7) |
| **AireOS WLC** (2504, 3504, 5520, 8540) | AireOS | ⭐ Thế hệ cũ, đang bị thay thế. CLI kiểu `config wlan …`, `show client detail …` |
| ⭐ **EWC** (Embedded Wireless Controller) | IOS-XE | **WLC chạy ngay trên một AP** trong nhóm — site nhỏ, không cần mua WLC |
| **Mobility Express** | AireOS | Tiền thân của EWC — đã ngừng phát triển |
| **Meraki MR** | Cloud | ⭐ Quản lý từ dashboard đám mây, không có WLC on-prem |
| **Catalyst 9800-CL trên cloud** | IOS-XE | Chạy trên AWS/Azure — "WLC as a VM" |

> ⭐ **Cho đề thi:** biết  **C9800 = IOS-XE = hiện tại**,  **AireOS = cũ**.
> Đề mới thiên về C9800 nhưng vẫn có thể hỏi khái niệm chung.
> ⭐ **Cho công việc:** nếu bạn gặp WLC ở công ty, xem `show version` để biết mình đang ở nền tảng nào.

---

## 📘 4. ⭐ CAPWAP (blueprint 3.3.c)

### 4.1 CAPWAP là gì

> ⭐ **CAPWAP** = *Control And Provisioning of Wireless Access Points* — **RFC 5415**.
> ⭐ Đây là **giao thức đường hầm giữa AP và WLC**. Nó thay thế **LWAPP** (giao thức Cisco độc quyền cũ).

| | LWAPP (cũ) | ⭐ **CAPWAP** (hiện tại) |
|---|---|---|
| Chuẩn | Cisco độc quyền | ⭐ **RFC 5415** (chuẩn mở) |
| Tầng vận chuyển | L2 hoặc L3 | ⭐ **Chỉ L3 — UDP/IP** |
| Bảo mật | AES key riêng | ⭐ **DTLS** |
| Port | 12222 / 12223 | ⭐ **5246 / 5247** |

### 4.2 ⭐ Hai tunnel — bảng PHẢI thuộc

```
     [ Lightweight AP ]                              [ WLC ]
            │                                           │
            │═══ CONTROL  ── UDP 5246 ── DTLS LUÔN BẬT ═══│
            │      (join, config, RRM, thống kê, key)       │
            │                                           │
            │═══ DATA     ── UDP 5247 ── DTLS TÙY CHỌN ══│
            │      (traffic thật của client, đã bọc lại)    │
```

| Tunnel | ⭐ Port | Chở gì | Mã hóa |
|---|:---:|---|---|
| ⭐ **Control** | **UDP 5246** | Join, tải config, tải image, lệnh RRM, thống kê, quản lý key | **DTLS — LUÔN BẬT, không tắt được** |
| ⭐ **Data** | **UDP 5247** | **Traffic thật của người dùng**, bọc trong CAPWAP | **DTLS TÙY CHỌN** — mặc định **tắt** (bật thì tốn CPU, một số nền tảng cần license) |

> 🔴  **Ba câu hỏi đề chắc chắn hỏi:**
> 1. ⭐ **Control = 5246, Data = 5247** — nhớ "control nhỏ hơn data".
> 2. ⭐ **Control LUÔN được DTLS mã hóa.** Data thì **không**, trừ khi bật.
> 3. ⭐ **CAPWAP chạy trên UDP/IP → AP và WLC KHÔNG cần cùng subnet, cùng VLAN.**
>  Đây chính là điều làm mô hình tập trung khả thi.

### 4.3 ⭐ Vấn đề MTU — nguyên nhân "lỗi khó tìm" số 1

```
  Frame gốc của client (tối đa 1500 byte)
            ↓  AP bọc thêm CAPWAP + UDP + IP + Ethernet (~48 byte)
  Gói đi trên mạng có dây  =  1500 + ~48  =  ~1548 byte
            ↓
  Nếu đường đi (WAN/tunnel/firewall) chỉ cho MTU 1400
     → phải phân mảnh, hoặc bị DROP
```

| 🔴 Triệu chứng | Nguyên nhân |
|---|---|
| ⭐ AP **join được** nhưng client **kết nối chập chờn**, tải file lớn thì treo | **MTU trên đường AP↔WLC quá nhỏ** — gói nhỏ (join, ping) qua được, gói lớn bị drop |
| AP **không join nổi**, thử đi thử lại | MTU quá nhỏ ngay từ giai đoạn tải config/image |
| Chỉ AP ở **chi nhánh qua VPN** bị, AP tại HQ bình thường | ⭐ **Đúng dấu hiệu MTU** — VPN/GRE làm giảm MTU khả dụng |

> ⭐ **Khuyến nghị Cisco: đường đi giữa AP và WLC nên hỗ trợ MTU ≥ 1500.**
> ⭐ **Tối thiểu tuyệt đối khoảng 1485** — thấp hơn thì CAPWAP hỏng.
> ⭐ **Cách kiểm tra:** ping với cờ *don't fragment* và kích thước lớn từ subnet AP tới WLC:
> ```
> ping <IP-WLC> df-bit size 1500 source <interface-của-subnet-AP>
> ```
> Không đi được ở size lớn nhưng đi được ở size nhỏ → ⭐ **chắc chắn là MTU**.

### 4.4 ⭐ AP JOIN PROCESS — 6 giai đoạn, học thuộc thứ tự

```
  ① AP BOOT & LẤY IP
     └─ DHCP (phổ biến) hoặc IP tĩnh gõ qua console
        ⚠️ Không có IP  →  KHÔNG BAO GIỜ join được. Đây là chỗ hỏng thường gặp nhất.

  ② DISCOVERY  — "Có WLC nào ngoài kia không?"
     └─ AP gửi CAPWAP Discovery Request theo 5 CÁCH (xem §3.5)
     └─ Mọi WLC nhận được đều trả CAPWAP Discovery Response
     └─ AP GOM tất cả response thành một DANH SÁCH ỨNG VIÊN

  ③ SELECTION  — "Chọn WLC nào trong danh sách?"
     └─ Áp dụng thứ tự ưu tiên (xem §3.6)

  ④ DTLS + JOIN
     └─ Bắt tay DTLS trên UDP 5246 (xác thực bằng CHỨNG THƯ SỐ trong AP và WLC)
     └─ Gửi Join Request → nhận Join Response
     ⚠️ Sai thời gian hệ thống (NTP!) → chứng thư "chưa hiệu lực/hết hạn" → JOIN HỎNG

  ⑤ KIỂM TRA IMAGE
     └─ Version AP == version WLC?
        ├─ Khớp  → sang bước ⑥
        └─ Lệch → AP TẢI IMAGE từ WLC → TỰ REBOOT → quay lại bước ①
           (lần join đầu tiên có thể mất 5–10 phút vì lý do này — KHÔNG phải lỗi)

  ⑥ TẢI CONFIG → vào trạng thái RUN
     └─ AP nhận: tên AP, mode (§07A-5), channel/power, danh sách WLAN, tag (§7)
     └─ AP bắt đầu phát sóng. Chỉ đến ĐÂY client mới thấy SSID.
```

⭐ **Bốn điểm hay bị hỏi:**

| # | Điểm | Chi tiết |
|:---:|---|---|
| 1 | ⭐ **Discovery ≠ Join** | Discovery là **hỏi thăm nhiều WLC**. Join là **cam kết với một WLC** |
| 2 | **DTLS dùng chứng thư số** | AP có **MIC** (Manufacturer Installed Certificate) từ nhà máy · 🔴  **sai giờ = chứng thư không hợp lệ = không join** |
| 3 | ⭐ **AP tự tải image từ WLC** | Không cần TFTP thủ công. AP luôn chạy đúng version của WLC |
| 4 | ⭐ **AP chỉ phát sóng ở bước ⑥** | AP đang join = **chưa có SSID** |

---

### 4.5 ⭐ DISCOVERY ALGORITHMS — 5 cách AP tìm WLC (blueprint nói thẳng)

> ⭐ **AP dùng TẤT CẢ các cách dưới đây để XÂY DANH SÁCH ứng viên**, rồi mới chọn ở §3.6.
> ⭐ **Thứ tự dưới đây là thứ tự thường được dạy và hỏi trong đề.**

| # | ⭐ Cách | Cơ chế | Khi nào dùng thực tế |
|:---:|---|---|---|
| **1** | ⭐ **Primed / đã học trước** (lưu trong NVRAM) | AP nhớ: **Primary / Secondary / Tertiary** đã cấu hình, **WLC đã join lần trước**, và  **các thành viên mobility group** của WLC đó | AP đã từng chạy — cách này gần như luôn thắng |
| **2** | ⭐ **Cấu hình tĩnh qua console** | Gõ tay trên AP:<br>`capwap ap controller ip address 10.10.10.5`<br>`capwap ap primary-base WLC-HQ 10.10.10.5` | Khi mọi thứ khác hỏng — **cứu hộ tại chỗ** |
| **3** | ⭐ **DHCP Option 43** | Server DHCP trả về danh sách IP WLC trong option 43 | **Cách phổ biến nhất khi AP ở SUBNET KHÁC WLC** |
| **4** | ⭐ **DNS** | AP hỏi DNS bản ghi A của<br> `CISCO-CAPWAP-CONTROLLER.<domain>`<br>*(cũ: `CISCO-LWAPP-CONTROLLER`)* | Khi không muốn động vào DHCP ·  AP phải nhận **domain name** từ DHCP option 15 |
| **5** | **Broadcast/subnet local** | AP gửi CAPWAP Discovery Request ra **subnet của chính nó** | **Chỉ chạy khi AP và WLC CÙNG SUBNET.** 🔴 Broadcast **không đi qua router** |

> 🔴  **Câu hỏi kinh điển của đề:** *"AP nằm ở VLAN 100, WLC ở VLAN 10. AP không join được. Vì sao?"*
> ⭐ **Vì broadcast không qua router.** Phải dùng  **DHCP Option 43** hoặc  **DNS** hoặc  **cấu hình tĩnh**.

#### ⭐ DHCP Option 43 — cấu hình thật (rất hay ra đề dạng "dòng nào đúng")

```
! ═══ Trên router/switch Cisco làm DHCP server ═══
ip dhcp pool VLAN100-AP
 network 10.100.0.0 255.255.255.0
 default-router 10.100.0.1
 domain-name cty.local                        ! cần cho phương án DNS (option 15)
 option 43 hex f104.0a0a.0a05                 ! WLC = 10.10.10.5
!
! CÁCH ĐỌC chuỗi hex:
!    f1   = sub-option 241 (danh sách WLC của Cisco)
!    04   = độ dài  (4 byte = 1 địa chỉ IP)
!    0a0a.0a05 = 10.10.10.5   (0a=10, 0a=10, 0a=10, 05=5)
!
! Hai WLC (10.10.10.5 và 10.10.10.6):
 option 43 hex f108.0a0a.0a05.0a0a.0a06       ! 08 = 8 byte = 2 IP
```

⭐ **Quy tắc tính độ dài:** `len = 4 × số WLC` → 1 WLC = `04`, 2 WLC = `08`, 3 WLC = `0C`.

> ⭐ **Trên Windows DHCP Server:** thêm Vendor Class `Cisco AP c3700` (tùy model),
> rồi cấu hình option 241 với cùng dữ liệu hex.

#### ⭐ DNS — cấu hình thật

```
! Trên DNS server, tạo bản ghi A:
CISCO-CAPWAP-CONTROLLER.cty.local.     IN  A   10.10.10.5
CISCO-CAPWAP-CONTROLLER.cty.local.     IN  A   10.10.10.6     ! nhiều bản ghi = nhiều WLC

! ĐIỀU KIỆN BẮT BUỘC: AP phải nhận được DOMAIN NAME và DNS SERVER từ DHCP
!    → DHCP phải có: option 15 (domain-name) + option 6 (dns-server)
```

🔴  **Lỗi thường gặp:** tạo bản ghi DNS đúng nhưng  **quên `domain-name` trong DHCP pool** →
AP không biết ghép hậu tố nào → không phân giải được → không join.

---

### 4.6 ⭐ WLC SELECTION PROCESS — thứ tự ưu tiên (blueprint nói thẳng)

> ⭐ AP đã có danh sách WLC trả lời Discovery.  **Bây giờ chọn theo đúng thứ tự này:**

```
  ① PRIMARY controller  (tên đã cấu hình trên AP)
        ├─ Có trong danh sách và còn chỗ?  →  JOIN ✅
        └─ Không                            →  ②

  ② SECONDARY controller
        └─ Không  →  ③

  ③ TERTIARY controller
        └─ Không  →  ④

  ④ MASTER controller
        (WLC được đánh dấu "master" — nhận MỌI AP mới chưa được gán primary)
        └─ Không có master  →  ⑤

  ⑤ LEAST-LOADED controller
        = WLC còn NHIỀU CHỖ TRỐNG NHẤT (excess AP capacity lớn nhất)
        KHÔNG phải "ít AP nhất" — mà là "còn dư nhiều nhất so với sức chứa"
```

> 🔴  **Bẫy ở bước ⑤:** *"AP sẽ join WLC có ít AP nhất"* — **SAI**.
> ⭐ Là WLC có **dung lượng dư nhiều nhất**.
>
> **Ví dụ:** WLC-A chứa tối đa 500 AP, đang có **200** → dư **300**.
> WLC-B chứa tối đa 150 AP, đang có **50** → dư **100**.
> ⭐ **AP chọn WLC-A** (dư 300) — dù WLC-B đang có ít AP hơn.

⭐ **Cấu hình primary/secondary/tertiary trên C9800:**
```
! Cách 1 — trong AP Join Profile (áp dụng cho cả nhóm AP qua Site Tag)
wireless profile ap-join AP-JOIN-HQ
 capwap-backup primary WLC-HQ-01 10.10.10.5
 capwap-backup secondary WLC-HQ-02 10.10.10.6

! Cách 2 — gán riêng cho một AP
ap name AP-TANG3-01 controller primary WLC-HQ-01 10.10.10.5
ap name AP-TANG3-01 controller secondary WLC-HQ-02 10.10.10.6
```

### 4.7 ⭐ AP High Availability

| Cơ chế | Là gì | ⭐ Khi WLC chính chết thì sao |
|---|---|---|
| ⭐ **Primary/Secondary/Tertiary** | Danh sách WLC dự phòng gán sẵn cho AP | AP **join lại** WLC dự phòng →  **client BỊ RỚT vài chục giây** (AP phải discovery+join lại) |
| ⭐ **N+1 Redundancy** | Một WLC dự phòng dùng chung cho nhiều WLC chính | Như trên — có gián đoạn |
| ⭐ **HA SSO (AP SSO)** | **Hai WLC ghép thành CẶP Active/Standby**, đồng bộ trạng thái AP (và cả client với Client SSO) | **AP KHÔNG phải join lại** — chuyển sang WLC standby gần như tức thời.  **Đây là mức HA tốt nhất** |
| ⭐ **AP Fallback** | Khi WLC primary sống lại, AP **tự quay về** | ⚠️  Gây **rớt lần nữa** → nhiều nơi **tắt** fallback hoặc hẹn giờ ngoài giờ làm việc |
| ⭐ **Stateful Switchover cho client** | Client SSO — giữ cả phiên client | Client không phải xác thực lại |

> ⭐ **Liên hệ Module-06A:** đây chính là ý tưởng **SSO/NSF** bạn đã học ở FHRP,
> áp dụng cho WLC. ⭐ Blueprint 1.1.b (*High availability techniques*) hỏi cả hai.

---

## 📘 5. ⭐ ĐƯỜNG ĐI CỦA TRAFFIC — Centralized (Local mode)

```
   Client  ~~~~  [ AP - Local mode ]                    [ WLC ]           [ Mạng có dây ]
                       │                                   │                     │
                       │══ CAPWAP data tunnel (5247) ═══│                     │
                       │                                   ├─────────────────────┤
                       │                                   Ở ĐÂY traffic mới
                       │                                     được "đổ" ra VLAN đích
```

> 🔴  **Điểm mấu chốt của Local mode:**  **TẤT CẢ traffic của client — kể cả khi hai client
> ngồi cạnh nhau, chung một AP — đều phải chạy về WLC rồi mới quay lại.**
> ⭐ Gọi là **"hairpinning"** (uốn ngược như cái kẹp tóc).

| Hệ quả | Chi tiết |
|---|---|
| ✅ **Chính sách tập trung** | Mọi ACL/QoS/VLAN áp một chỗ. Roaming rất mượt |
| ✅ **Switch port của AP đơn giản** | ⭐ Chỉ cần **access port** ở VLAN quản lý AP — không cần trunk |
| 🔴  **Tốn băng thông đường trục** | Traffic đi vòng. Với chi nhánh qua WAN →  **thảm họa** |
| 🔴  **Mất WLC = mất Wi-Fi hoàn toàn** | AP Local mode không tự phục vụ được |
| 🔴  **Độ trễ tăng** | Nhất là khi WLC ở xa |

⭐ **Chính hai dòng đỏ cuối là lý do FlexConnect tồn tại.**

⭐ **Bảng so sánh các mô hình triển khai** *(phần thiết kế/lựa chọn — blueprint 1.2.a — sẽ phân tích kỹ ở **Module-09**)*:

| Mô hình | AP mode | Traffic đi đâu | Hợp với |
|---|---|---|---|
| ⭐ **Centralized** | Local | Về WLC (CAPWAP) | Campus, tòa nhà, WLC ở cùng site |
| ⭐ **Distributed / Branch** | **FlexConnect** | **Ra thẳng LAN tại chỗ** | Chi nhánh, WLC ở HQ |
| **Embedded (EWC)** | Local | Về AP-controller trong site | Site nhỏ (< ~100 AP), không mua WLC |
| **Cloud** | — | Tùy giải pháp (Meraki: ra thẳng LAN) | Nhiều site nhỏ, quản lý tập trung qua đám mây |
| **Autonomous** | — | Ra thẳng LAN | Rất nhỏ, 1–2 AP |

---

## 📘 6. ⭐ FLEXCONNECT

### 6.1 Ý tưởng

> ⭐ **FlexConnect** (tên cũ **H-REAP** — *Hybrid Remote Edge AP*): AP vẫn **do WLC ở HQ quản lý**,
> nhưng ⭐ **traffic của client được đổ thẳng ra mạng LAN tại chỗ**, không chạy về HQ.

```
   ═══ CHI NHÁNH ═══                    WAN                 ═══ HQ ═══
                                                                
   Client ~~~ [ AP FlexConnect ]═══ CAPWAP CONTROL (5246) ═══[ WLC ]
                     │                (chỉ quản lý, rất ít băng thông)
                     │
                     └──► DATA đổ THẲNG ra switch chi nhánh (local switching)
                              KHÔNG chạy về HQ
```

### 6.2 ⭐ Hai trục lựa chọn — bảng phải hiểu

⭐ FlexConnect có **hai quyết định độc lập nhau**:

| Trục | Lựa chọn | Nghĩa |
|---|---|---|
| ⭐ **SWITCHING** (dữ liệu đi đâu) | **Central switching** | Traffic vẫn tunnel về WLC (như Local mode) |
| | ⭐ **Local switching** | Traffic đổ ra VLAN tại chi nhánh |
| ⭐ **AUTHENTICATION** (ai kiểm mật khẩu) | **Central auth** | WLC liên hệ RADIUS ở HQ |
| | ⭐ **Local auth** | **AP tự làm 802.1X** với RADIUS tại chỗ, hoặc **Local EAP trên AP** |

⭐ **Bốn tổ hợp:**

| Switching | Auth | ⭐ Dùng khi |
|---|---|---|
| Central | Central | ⭐ Giống hệt Local mode — dùng khi muốn chính sách tập trung tuyệt đối |
| ⭐ **Local** | **Central** | **Phổ biến nhất ở chi nhánh** — data đi tắt, xác thực vẫn tập trung |
| ⭐ **Local** | **Local** | Chi nhánh cần **sống sót khi đứt WAN** hoàn toàn |
| Central | Local | Hiếm |

### 6.3 ⭐ Connected mode vs Standalone mode — bảng đề rất hay hỏi

| | ⭐ **Connected mode** | **Standalone mode** |
|---|---|---|
| Điều kiện | **WLC còn liên lạc được** | 🔴  **Mất CAPWAP control tới WLC** |
| AP làm gì | Bình thường | ⭐ AP **tự xoay xở** với config đã lưu |

⭐ **Cái gì sống sót khi vào Standalone mode — bảng PHẢI thuộc:**

| Loại WLAN | Client **đang kết nối** | Client **mới** muốn vào |
|---|:---:|:---:|
| ⭐ **Local switching + Local auth** | ✅ **Tiếp tục chạy** | ✅  **Vẫn vào được** |
| **Local switching + Central auth** | ✅  **Tiếp tục chạy** *(đã xác thực rồi)* | 🔴  **KHÔNG vào được** — không tới được RADIUS/WLC |
| 🔴 **Central switching** (bất kỳ auth nào) | 🔴  **RỚT NGAY** — tunnel data đã đứt | 🔴 **Không** |

> 🔴  **Đây là bảng ăn điểm.** Nhớ logic thay vì học vẹt:
> ⭐ **Central switching cần tunnel → đứt tunnel là chết.**
> ⭐ **Central auth cần WLC → client CŨ (đã xác thực xong) sống, client MỚI chết.**
> ⭐ **Local + Local = tự chủ hoàn toàn → sống hết.**

⭐ **Ngoài ra khi ở Standalone mode:**
- ❌ Không có RRM (channel/power **đóng băng** ở giá trị cuối)
- ❌ Không phát hiện rogue tập trung, không báo cáo lên WLC
- ⚠️ ⭐ Roaming giữa các AP chi nhánh vẫn được **nếu** dùng  **FlexConnect Group** (chia sẻ key)
- ⭐ AP liên tục thử liên lạc lại WLC; nối lại được → tự về Connected mode

### 6.4 ⭐ Cấu hình FlexConnect — những điểm bắt buộc

```
! ═══ ĐIỀU KIỆN 1: PORT SWITCH CỦA AP PHẢI LÀ TRUNK ═══
!   (khác với Local mode chỉ cần access port!)
interface GigabitEthernet1/0/10
 description AP-CHINHANH-01
 switchport mode trunk
 switchport trunk native vlan 100          ! VLAN quản lý AP = NATIVE (không tag)
 switchport trunk allowed vlan 100,20,30   ! 100=mgmt AP, 20/30 = VLAN của client
 spanning-tree portfast trunk
```

> 🔴  **Lỗi FlexConnect số 1:**  **quên đổi port AP từ access sang trunk**, hoặc
> ⭐ **native VLAN không khớp** với VLAN quản lý AP. Triệu chứng: AP join được (vì mgmt VLAN đúng)
> nhưng ⭐ **client có IP sai hoặc không có IP** (vì VLAN client không được cho qua).

```
! ═══ ĐIỀU KIỆN 2: VLAN MAPPING trên WLC (C9800 - Flex Profile) ═══
wireless profile flex FLEX-CHINHANH-HN
 native-vlan-id 100
 vlan-name VLAN-NHANVIEN
  vlan-id 20
 vlan-name VLAN-KHACH
  vlan-id 30
 ! Local auth / backup RADIUS khi mất WAN:
 local-auth ap eap-fast
!
! ═══ Gắn Flex Profile vào Site Tag, rồi gán Site Tag cho AP ═══
wireless tag site SITE-CHINHANH-HN
 flex-profile FLEX-CHINHANH-HN
 no local-site                              ! DÒNG NÀY BẬT FLEXCONNECT
```

> 🔴  **`no local-site` — dòng dễ quên nhất trên C9800.**
> ⭐ `local-site` = AP ở **cùng site với WLC** → chạy **Local mode**.
> ⭐ `no local-site` = AP ở **site xa** → chạy **FlexConnect**.
> ⭐ Quên dòng này thì mọi cấu hình flex profile ở trên **không có tác dụng**.

### 6.5 ⭐ FlexConnect Group & các biến thể

| Tính năng | Làm gì |
|---|---|
| ⭐ **FlexConnect Group** | Nhóm các AP cùng chi nhánh để **chia sẻ PMK/key** →  **roaming nhanh vẫn hoạt động khi mất WAN** · chia sẻ backup RADIUS · chia sẻ danh sách user Local EAP |
| ⭐ **Split tunneling** | Một phần traffic đi local, một phần tunnel về HQ (theo ACL) |
| ⭐ **OEAP** (OfficeExtend AP) | AP mang về **nhà nhân viên**, tự dựng **DTLS tunnel qua Internet** về WLC ở HQ. Người dùng ở nhà y như ngồi văn phòng |
| **Flex + Bridge** | FlexConnect **cộng** mesh (§07A-5) |
| **Efficient AP Image Upgrade** | ⭐ Một AP tại chi nhánh tải image trước rồi **chia lại cho các AP còn lại** → không tải 20 lần qua WAN |

---

## 📘 7. ⭐ ROAMING (blueprint 3.3.d)

### 7.1 Nguyên tắc nền — nhắc lại và nhấn mạnh

> 🔴  **CLIENT quyết định khi nào roam, và roam sang AP nào. WLC KHÔNG ép được.**
> ⭐ WLC chỉ có thể: (a) **gợi ý** qua **802.11v**, (b) **cung cấp thông tin** qua **802.11k**,
> (c) **làm cho việc roam nhanh hơn** qua **802.11r/OKC**, (d) ⭐ **từ chối** client ở dưới ngưỡng (RX-SOP / optimized roaming).

⭐ **Điều kiện tiên quyết để roam mượt** (thiết kế, không phải cấu hình):

| Điều kiện | Con số |
|---|---|
| ⭐ **RSSI ở mọi điểm** | **≥ −67 dBm** (chuẩn Voice) |
| ⭐ **Cell overlap** giữa các AP liền kề | **15–20%** |
| ⭐ **Cùng SSID** trên các AP | Bắt buộc — đây là định nghĩa của **ESS** |
| ⭐ **Cùng cấu hình bảo mật** | Khác nhau → client phải xác thực lại từ đầu |
| ⭐ **Thời gian roam mục tiêu** | **< 150 ms** tổng ·  **< 50 ms** cho phần trao đổi key (Voice) |

---

### 7.2 ⭐ BA LOẠI ROAM — bảng cốt lõi của 3.3.d

| | ⭐ **Intra-controller**<br>*(Layer 2, cùng WLC)* | **Inter-controller Layer 2**<br>*(khác WLC, CÙNG subnet)* | **Inter-controller Layer 3**<br>*(khác WLC, KHÁC subnet)* |
|---|---|---|---|
| Client đổi AP | ✅ | ✅ | ✅ |
| Client đổi **WLC** | ❌ Không | ✅ Có | ✅ Có |
| **VLAN/subnet client** | Không đổi | **Giống nhau** trên 2 WLC | 🔴  **KHÁC nhau** |
| ⭐ Bản ghi client trong DB | Cập nhật tại chỗ | **DI CHUYỂN** (move) sang WLC mới | **NHÂN BẢN** (copy) sang WLC mới,  **bản gốc GIỮ LẠI** |
| ⭐ Client có **giữ IP** không | ✅ Có | ✅ Có | **CÓ — nhờ tunnel** |
| ⭐ Cần **mobility tunnel**? | ❌ Không | ❌ Không | **CÓ — bắt buộc** |
| ⭐ Vai trò | — | — | **ANCHOR** (WLC gốc) ↔  **FOREIGN** (WLC mới) |
| Tốc độ | ⭐ Nhanh nhất | Nhanh | Chậm hơn (thêm tunnel) |

#### ⭐ Sơ đồ Layer 2 inter-controller roam

```
   TRƯỚC:                                  SAU:
   [WLC-A]──AP1  ← client                 [WLC-A]──AP1
   [WLC-B]──AP2                           [WLC-B]──AP2  ← client
   
   VLAN 20 trên CẢ HAI WLC (cùng subnet 10.0.20.0/24)
   → Bản ghi client được CHUYỂN HẲN từ WLC-A sang WLC-B
   → WLC-A xóa bản ghi. Client giữ IP vì subnet không đổi.
   → KHÔNG cần tunnel.
```

#### ⭐ Sơ đồ Layer 3 roam — ANCHOR / FOREIGN

```
   Client có IP 10.0.20.55 (từ VLAN 20 của WLC-A)
   Client đi sang vùng của WLC-B — nhưng WLC-B chỉ có VLAN 30 (10.0.30.0/24)

   Nếu không làm gì → client phải đổi IP → ĐỨT hết session TCP, rớt cuộc gọi

   GIẢI PHÁP: MOBILITY TUNNEL

        [ WLC-A = ANCHOR ]                      [ WLC-B = FOREIGN ]
         (nơi client "sinh ra")                     (nơi client đang đứng)
         giữ VLAN 20 / 10.0.20.0/24                       │
                    │                                     │
                    │◄══ MOBILITY TUNNEL ═════════════►│
                    │      UDP 16666 (control)            │
                    │      UDP 16667 (data)               │
                    │                                    AP2
                    │                                     │
              ra mạng có dây                         ~~~ client (vẫn 10.0.20.55) 
              với IP GỐC 10.0.20.55

   Traffic của client: AP2 → WLC-B (foreign) → TUNNEL → WLC-A (anchor) → mạng
   Với thế giới bên ngoài, client vẫn "ở" trên WLC-A. IP không đổi. Session không đứt.
```

| Vai trò | ⭐ Nghĩa |
|---|---|
| ⭐ **Anchor controller** | WLC **client kết nối lần đầu** — nơi **giữ IP/VLAN gốc** của client |
| ⭐ **Foreign controller** | WLC **client đang đứng ở đó bây giờ** — nhận traffic rồi **tunnel về anchor** |
| ⭐ **Symmetric tunneling** | Traffic **cả hai chiều** đều qua anchor.  **Cách hiện đại** — cần thiết vì có RPF check/firewall ở đường ra |
| **Asymmetric tunneling** | (cũ) chỉ chiều về qua anchor → hay bị firewall/uRPF chặn |

---

### 7.3 ⭐ Mobility Group & Mobility Domain

| Khái niệm | Nghĩa |
|---|---|
| ⭐ **Mobility Group** | Nhóm WLC **tin cậy nhau**, chia sẻ thông tin client →  **roaming nhanh giữa chúng**.  *(AireOS: tối đa **24 WLC** / group)* |
| ⭐ **Mobility Domain** | Tập hợp các mobility group **nhìn thấy nhau** → roam được nhưng **chậm hơn** *(AireOS: tối đa **72 WLC**)* |
| ⭐ **Điều kiện tham gia** | **Cùng tên mobility group** · biết IP+MAC của nhau ·  **(AireOS) cùng virtual IP** · phiên bản tương thích |
| ⭐ **Port mobility tunnel** | **UDP 16666** (control, được DTLS) ·  **UDP 16667** (data). *(AireOS đời cũ dùng **EoIP — IP protocol 97**)* |

```
! Kiểm tra trên C9800
show wireless mobility summary
show wireless mobility peer ip <ip>
```

> 🔴  **Triệu chứng khi mobility group cấu hình sai:** client roam giữa 2 WLC thì
> ⭐ **phải xác thực lại từ đầu và đổi IP** → rớt session.  Kiểm tra ngay `show wireless mobility summary`
> xem peer có ở trạng thái **Up** không.

### 7.4 ⭐ Guest Anchor — ứng dụng thực tế quan trọng nhất của L3 roaming

> ⭐ Đây là **use case số 1** mà blueprint nhắc tới bằng cụm *"use cases for L3 roaming"*.

```
   ═══ CAMPUS (vùng tin cậy) ═══           ═══ DMZ ═══         Internet
                                                                  
   Client-khách ~~~ AP ─── [ WLC-Campus ]══ tunnel ══[ WLC-DMZ ]────►
                            FOREIGN                ANCHOR
                                                          │
                            Traffic khách KHÔNG BAO GIỜ
                              chạm vào mạng nội bộ campus
```

| Vì sao làm thế | Lợi ích |
|---|---|
| ⭐ **Cách ly traffic khách** | Khách không bao giờ vào được VLAN nội bộ —  **tách bằng đường hầm, không chỉ bằng ACL** |
| ⭐ **Một điểm kiểm soát duy nhất** | Toàn bộ khách của mọi tòa nhà đổ về **một WLC ở DMZ** → đặt firewall, WebAuth, rate-limit ở đó |
| ⭐ **Không cần kéo VLAN khách khắp campus** | Không phải trunk VLAN-guest qua mọi switch — giảm rủi ro và độ phức tạp |

⭐ **Đây gọi là "auto-anchor" / "guest tunneling"** — client được **anchor sẵn** vào WLC DMZ ngay từ đầu,
chứ không phải do roam.

---

### 7.5 ⭐ Fast Roaming — làm sao roam < 50 ms

⭐ **Vấn đề:** với **WPA2-Enterprise (802.1X)**, mỗi lần roam mà phải làm lại **toàn bộ** EAP với RADIUS
→  **mất 300–800 ms** → 🔴 **rớt cuộc gọi VoIP**.

| Cơ chế | Chuẩn? | Cách hoạt động | ⭐ Ghi chú |
|---|:---:|---|---|
| ⭐ **PMK Caching** (Sticky Key Caching) | 802.11i | Client & AP nhớ PMK cũ → quay lại **đúng AP đó** thì không cần EAP lại | Chỉ giúp khi **quay lại AP CŨ** |
| ⭐ **OKC** (Opportunistic Key Caching) | Không chuẩn (rộng rãi) | **WLC phân phát PMK cho TẤT CẢ AP trước** → client roam tới AP mới đã có sẵn key | Rất phổ biến, đa số client hỗ trợ |
| **CCKM** | Cisco (CCX) | Tương tự OKC, cơ chế Cisco đời trước | ⭐ Cần client CCX — chủ yếu là **điện thoại Wi-Fi Cisco** |
| ⭐ **802.11r (FT)** | **Chuẩn IEEE** | Client **chuẩn bị key với AP đích TRƯỚC KHI rời AP cũ** | **Nhanh nhất & là chuẩn.** ⚠️  Một số client cũ **không join được** WLAN bật 11r → thường tạo **WLAN riêng cho voice** |
| ⭐ **802.11k** | Chuẩn | AP gửi **Neighbor Report**: "AP hàng xóm ở channel 36, 44, 149" | Client **không phải quét mù cả band** → tiết kiệm hàng trăm ms |
| ⭐ **802.11v** | Chuẩn | **BSS Transition Management** — WLC **gợi ý** client chuyển sang AP nào | Giúp trị **sticky client** |

⭐ **Hai chế độ của 802.11r:**

| Chế độ | Cách trao đổi |
|---|---|
| ⭐ **Over-the-Air** | Client nói **trực tiếp với AP đích** qua sóng |
| ⭐ **Over-the-DS** (Distribution System) | Client nói với **AP hiện tại**, AP hiện tại chuyển tiếp qua **mạng có dây** tới AP đích.  Tốt hơn khi tín hiệu AP đích còn yếu |

> ⭐ **Thứ tự áp dụng trong thực tế:** bật  **802.11k + 802.11v** cho mọi WLAN (gần như không có nhược điểm),
> rồi bật ⭐ **802.11r** cho WLAN voice — và  **kiểm tra kỹ client cũ** trước khi bật đại trà.

### 7.6 🔴  Sticky client — vấn đề roaming số 1 ngoài đời

> ⭐ **"Sticky client"**: client **bám dai** vào AP cũ dù đã đi rất xa, vì nó **chỉ roam khi RSSI quá tệ**.

```
   Client đi từ AP1 sang AP2:
   
   AP1: RSSI −78 dBm  (rất tệ, tốc độ 6 Mbps)      ← client VẪN BÁM
   AP2: RSSI −45 dBm  (tuyệt vời, tốc độ 800 Mbps) ← client phớt lờ
   
   Hậu quả: client đó chậm, VÀ nó chiếm airtime rất lâu cho mỗi gói
      → làm chậm CẢ CELL của AP1 (Module-07A §3.4)
```

| ⭐ Cách trị | Cơ chế |
|---|---|
| ⭐ **Giảm công suất AP** | Cell nhỏ → tín hiệu tụt nhanh hơn → client buộc phải quyết định sớm |
| ⭐ **Tắt data rate thấp** | Client không thể "cố" bám ở tốc độ 1–11 Mbps nữa |
| ⭐ **Bật 802.11k + v** | Chỉ đường và **gợi ý** cho client |
| ⭐ **Optimized Roaming** | WLC **chủ động đá** client xuống dưới ngưỡng RSSI/data-rate → buộc nó tìm AP mới |
| ⭐ **RX-SOP** | AP **bỏ qua** tín hiệu yếu hơn ngưỡng → cell "cứng" hơn |
| ⭐ Cập nhật driver Wi-Fi của client | Nhiều trường hợp sticky là **lỗi driver** — đây là cách sửa thật sự |

---

## 📘 8. ⭐ CẤU HÌNH WLAN — mô hình TAG của Catalyst 9800

> ⭐ Phần này phục vụ trực tiếp **3.3.e** (*Troubleshoot **WLAN configuration***).
> ⭐ Không cần thuộc lệnh —  **cần hiểu chuỗi liên kết**, vì lỗi cấu hình WLAN 90% là **đứt chuỗi này**.

### 8.1 ⭐ Chuỗi liên kết trên C9800

```
   ┌─────────────────┐     ┌──────────────────┐
   │  WLAN Profile   │     │  Policy Profile  │
   │  · SSID (tên)   │     │  · VLAN       │
   │  · Bảo mật      │     │  · ACL / QoS     │
   │  · Radio band   │     │  · Central/Local │
   │  · 11r/k/v      │     │    switching     │
   └────────┬────────┘     └────────┬─────────┘
            └──────────┬────────────┘
                       ▼
              ┌─────────────────┐
              │ POLICY TAG   │  ← "SSID này chạy với chính sách kia"
              └────────┬────────┘
                       │
   ┌─────────────────┐ │ ┌──────────────┐   ┌─────────────┐
   │ SITE TAG     │ │ │ RF TAG    │   │             │
   │ · AP Join Prof. │ │ │ · RF profile │   │             │
   │ · Flex Profile  │ │ │   2.4/5/6GHz │   │             │
   │ · local-site?   │ │ └──────┬───────┘   │             │
   └────────┬────────┘ │        │           │             │
            └──────────┼────────┘           │             │
                       ▼                                  │
                 ┌───────────┐                            │
                 │   AP   │ ◄──── 3 tag được GÁN cho AP │
                 └───────────┘                            │
                       │                                  │
                       ▼                                  │
                AP phát SSID  ◄────────────────────────┘
```

| Tag | Chứa gì | ⭐ Trả lời câu hỏi |
|---|---|---|
| ⭐ **Policy Tag** | **WLAN Profile** ↔ **Policy Profile** | *"AP này phát SSID nào, và mỗi SSID vào VLAN nào?"* |
| ⭐ **Site Tag** | **AP Join Profile** + **Flex Profile** +  `local-site` / `no local-site` | *"AP này ở site nào? Local mode hay FlexConnect?"* |
| ⭐ **RF Tag** | RF profile cho từng band | *"AP này dùng thiết lập RF nào (công suất, data rate, channel)?"* |

> 🔴  **Ba lỗi cấu hình WLAN kinh điển trên C9800 — nhớ kỹ, đây là 3.3.e:**
>
> | # | Lỗi | Triệu chứng |
> |:---:|---|---|
> | 1 | ⭐ **Tạo WLAN nhưng quên gắn vào Policy Tag** | **SSID hoàn toàn không xuất hiện** trên không trung |
> | 2 | ⭐ **Gắn vào Policy Tag nhưng chưa gán Tag đó cho AP** | Chỉ **một số AP** phát SSID, số khác thì không |
> | 3 | ⭐ **WLAN đã enable nhưng Policy Profile bị disable** | Client **thấy SSID, kết nối được, nhưng không có IP** |
>
> ⭐ **Thêm hai điểm hay quên:**
> · ⭐ **`default-policy-tag` chỉ tự map WLAN có ID 1–16.** Tạo WLAN ID 17 rồi thắc mắc sao không thấy → đây.
> · ⭐ **Đổi tag của một AP làm AP đó JOIN LẠI** (rớt ~1 phút).  **Đừng làm giờ hành chính.**

### 8.2 ⭐ Cấu hình mẫu tối thiểu (C9800 CLI)

```
! ═══ ① WLAN Profile — tên SSID + bảo mật ═══
wlan WLAN-NHANVIEN 1 CTY-CORP
 security wpa psk set-key ascii 0 MatKhauRatDai2026
 security wpa wpa2
 security wpa wpa2 ciphers aes
 security ft                              ! bật 802.11r (fast transition)
 security pmf optional                    ! 802.11w
 no shutdown                              ! RẤT HAY QUÊN

! ═══ ② Policy Profile — VLAN + hành vi ═══
wireless profile policy POL-NHANVIEN
 vlan 20                                  ! VLAN client đổ vào
 central switching                        ! (hoặc: no central switching → FlexConnect local)
 central authentication
 no shutdown                              ! CŨNG RẤT HAY QUÊN

! ═══ ③ Policy Tag — buộc ① với ② ═══
wireless tag policy TAG-POL-HQ
 wlan WLAN-NHANVIEN policy POL-NHANVIEN

! ═══ ④ Gán tag cho AP ═══
ap 00aa.bbcc.ddee                          ! MAC ethernet của AP
 policy-tag TAG-POL-HQ
 site-tag  SITE-HQ
 rf-tag    default-rf-tag

! ═══ ⑤ Kiểm tra ═══
show wlan summary
show wireless profile policy summary
show wireless tag policy summary
show ap tag summary                        ! AP nào đang dùng tag nào
show ap summary
```

⭐ **Tương đương trên AireOS (nếu bạn gặp WLC đời cũ):**
`WLAN` → gắn vào **Interface/VLAN** → tùy chọn gom AP bằng **AP Group**. Đơn giản hơn nhưng kém linh hoạt.

---

## 📘 9. 🟡 WIRELESS SECURITY — vừa đủ để troubleshoot (blueprint 5.4)

> ⭐ **Module-10 sẽ đào sâu 802.1X/RADIUS/ISE.** Ở đây chỉ cần đủ để **đọc được lỗi client**.

### 9.1 ⭐ Các thế hệ bảo mật

| Thế hệ | Xác thực | Mã hóa | ⭐ Trạng thái |
|---|---|---|---|
| **WEP** | Shared key | RC4 | 🔴  **Vỡ hoàn toàn.** Không bao giờ dùng |
| **WPA** | PSK / 802.1X | TKIP | 🔴 Đã lỗi thời |
| ⭐ **WPA2** | **PSK** hoặc  **802.1X/EAP** | **AES-CCMP** | **Phổ biến nhất hiện nay** |
| ⭐ **WPA3** | **SAE** (Personal) / 802.1X (Enterprise) | AES-GCMP / CCMP | **Bắt buộc PMF (802.11w)** · chống dò mật khẩu offline |
| **OWE** (Enhanced Open) | Không có mật khẩu | Có **mã hóa** | ⭐ Cho Wi-Fi công cộng — mã hóa mà không cần mật khẩu |

### 9.2 ⭐ Personal vs Enterprise — phân biệt cho chắc

| | ⭐ **Personal (PSK / SAE)** | **Enterprise (802.1X / EAP)** |
|---|---|---|
| Xác thực bằng | ⭐ **Một mật khẩu dùng chung** | **Tài khoản riêng từng người** hoặc **chứng thư số** |
| Cần RADIUS? | ❌ Không | ⭐ **Có — bắt buộc** (ISE / FreeRADIUS / NPS) |
| Đổi mật khẩu khi nhân viên nghỉ | 🔴  **Phải đổi cho TẤT CẢ mọi người** | **Chỉ khóa tài khoản đó** |
| Gán VLAN động theo người dùng | ❌ | ⭐ **Có** (RADIUS trả về VLAN/ACL) |
| Hợp với | Nhà, quán, mạng khách | ⭐ **Mọi mạng doanh nghiệp** |
| ⭐ WPA3 dùng gì | **SAE** (Simultaneous Authentication of Equals) thay PSK | 802.1X |

### 9.3 ⭐ Các loại EAP — bảng nhận biết

| EAP type | Server cần | Client cần | ⭐ Ghi chú |
|---|---|---|---|
| ⭐ **EAP-TLS** | **Chứng thư** | **Chứng thư** | **An toàn nhất.** Cần hạ tầng PKI → triển khai nặng |
| ⭐ **PEAP** (MSCHAPv2) | **Chứng thư** | **Username + password** | **Phổ biến nhất** — dựng đường hầm TLS rồi mới gửi mật khẩu |
| **EAP-TTLS** | Chứng thư | Username/password | Tương tự PEAP, linh hoạt hơn về giao thức bên trong |
| **EAP-FAST** | (PAC) | PAC / username | ⭐ Của Cisco — dùng **PAC** thay chứng thư |
| **EAP-MD5** | — | — | 🔴 Không dùng cho Wi-Fi (không tạo key mã hóa) |

### 9.4 ⭐ WebAuth (Captive Portal) — cho khách

| Kiểu | Trang đăng nhập ở đâu |
|---|---|
| ⭐ **Local WebAuth (LWA)** | Trên chính **WLC** |
| ⭐ **Central WebAuth (CWA)** | Trên **ISE** — WLC chuyển hướng client sang ISE |
| **External WebAuth** | Trên một web server riêng |

⭐ **Luồng khách điển hình:** kết nối SSID mở (hoặc OWE) → nhận IP → mở trình duyệt →
⭐ **bị chuyển hướng** về portal → nhập thông tin → WLC/ISE cho phép → vào mạng.

> 🔴  **Lỗi WebAuth kinh điển:**  **client phải có DNS hoạt động và DHCP trước** thì mới bị
> chuyển hướng được. ⭐ **ACL pre-auth phải mở cổng DNS (53) và DHCP (67/68)**, nếu không
> trình duyệt không mở nổi trang nào → không có portal.

### 9.5 ⭐ PMF / 802.11w

| | Nghĩa |
|---|---|
| ⭐ Vấn đề | Frame **quản lý** 802.11 (deauth, disassoc) **không được ký** → ai cũng giả mạo được →  **deauth attack** đá văng client |
| ⭐ **802.11w / PMF** | **Ký số** các frame quản lý → không giả mạo được |
| Trạng thái | ⭐ **Optional** (client cũ vẫn vào được) · **Required** (bắt buộc).  **WPA3 bắt buộc PMF** |
| 🔴 Bẫy | Đặt **PMF Required** →  **client cũ không hỗ trợ 802.11w sẽ không join được** |

---

## 📘 10. 🔴  TROUBLESHOOT (blueprint 3.3.e) — phần quan trọng nhất module

### 10.1 ⭐ Phương pháp 6 TẦNG — học thuộc thứ tự này

> ⭐ **Nguyên tắc: đi từ dưới lên. Đừng nhảy cóc.**
> ⭐ 80% ca "wireless hỏng" thật ra dừng ở tầng 1 hoặc tầng 5.

```
  ⑥ UPSTREAM / DỊCH VỤ    "Có IP rồi mà không ra Internet?"
     └─ Routing, ACL, firewall, DNS, NAT, proxy   →  ĐÂY LÀ MẠNG CÓ DÂY, không phải Wi-Fi
                              ▲
  ⑤ IP / DHCP           "Đã xác thực xong mà không có IP?"
     └─ DHCP scope cạn · VLAN sai · DHCP relay thiếu · VLAN không có trên trunk
                              ▲
  ④ XÁC THỰC          "Associate được rồi mà bị đá ra?"
     └─ Sai PSK · RADIUS không tới được · chứng thư hết hạn · PMF mismatch · sai EAP type
                              ▲
  ③ WLAN CONFIG        "Thấy SSID nhưng không kết nối được?"
     └─ WLAN shutdown · Policy Profile shutdown · Tag chưa gán · WLAN ID > 16 với default tag
                              ▲
  ② AP ↔ WLC           "Không thấy SSID nào cả?"
     └─ AP chưa join: IP? discovery? DTLS/giờ? image? MTU? tag?
                              ▲
  ① RF (Layer 1)      "Sóng có tới không, có sạch không?"
     └─ RSSI ≥ −67? SNR ≥ 20–25? Noise? CCI/ACI? Channel DFS? Band client hỗ trợ?
        → Toàn bộ Module-07A
```

### 10.2 ⭐ Trạng thái client — dừng ở đâu là biết lỗi ở đâu

```
  Idle → Associating → Authenticating (L2) → IP Learn / DHCP → (Web Auth) → RUN
     │          │                  │                      │                │           │
     │          │                  │                      │                │           └─ ✅ OK
     │          │                  │                      │                └─ Kẹt: ACL pre-auth
     │          │                  │                      │                        chặn DNS?
     │          │                  │                      └─ Kẹt: DHCP/VLAN/trunk
     │          │                  └─ Kẹt: sai PSK · RADIUS · chứng thư · PMF
     │          └─ Kẹt: WLAN config · tag · AP quá tải · client bị loại
     └─ Không thấy client ở đây → vấn đề TẦNG 1 (RF) hoặc client không thấy SSID
```

> 🔴  **Đây là công cụ chẩn đoán mạnh nhất bạn có.** Câu hỏi đầu tiên **luôn** là:
> ⭐ ***"Client dừng ở trạng thái nào?"*** — trả lời được câu đó là đã khoanh vùng xong 80%.
>
> ```
> show wireless client mac-address <MAC> detail | include State
> ```

### 10.3 ⭐ Bảng chẩn đoán — triệu chứng → nguyên nhân → cách kiểm chứng

#### A. AP không join WLC (tầng ②)

| 🔴 Triệu chứng | Nguyên nhân | ✅ Kiểm chứng / sửa |
|---|---|---|
| ⭐ AP không có đèn / không boot | PoE không đủ (AP Wi-Fi 6 cần **802.3at/bt**) | `show power inline <port>` trên switch |
| ⭐ AP có nguồn nhưng **không có IP** | DHCP scope AP hết · VLAN sai · port sai | Console vào AP: `show ip interface brief` |
| ⭐ AP có IP nhưng **không tìm thấy WLC** | AP khác subnet với WLC → **broadcast không qua router** | Kiểm tra **DHCP option 43** / **DNS** / cấu hình tĩnh (§3.5) |
| ⭐ Ping được WLC nhưng vẫn không join | Firewall chặn **UDP 5246/5247** | Mở port trên firewall giữa AP và WLC |
| 🔴  Join **hỏng ở bước DTLS** | **Sai thời gian hệ thống** → chứng thư "chưa hiệu lực/hết hạn" | Đồng bộ **NTP** cho WLC (**Module-06B §3**!) · `show clock` cả hai đầu |
| ⭐ AP join rồi lại rớt, lặp vô tận | **MTU** trên đường đi quá nhỏ · hoặc AP đang tải image | `ping <WLC> df-bit size 1500` · xem `show ap join stats detailed <mac>` |
| ⭐ AP mất **5–10 phút** mới join lần đầu | **Đang tải image** từ WLC rồi reboot | **Bình thường**, không phải lỗi |
| AP join WLC **sai** (không phải cái mong muốn) | Chưa gán primary/secondary, hoặc có **master controller** hút hết | ⭐ Gán primary (§3.6) · kiểm tra WLC nào đang là master |
| ⭐ AP join xong nhưng **không phát SSID nào** | **Chưa gán Policy Tag**, hoặc tag không có WLAN nào | `show ap tag summary` · `show wlan summary` |

#### B. Client không kết nối được (tầng ③ ④ ⑤)

| 🔴 Triệu chứng | Nguyên nhân | ✅ Kiểm chứng / sửa |
|---|---|---|
| ⭐ **Không thấy SSID** | (a) AP chưa join · (b) WLAN `shutdown` · (c) chưa gán tag · (d)  **client không hỗ trợ band/channel** (DFS!) · (e) SSID ẩn | `show wlan summary` · `show ap tag summary` · thử client khác |
| ⭐ **Thấy SSID, gõ mật khẩu, bị đá ra ngay** | **Sai PSK** · hoặc **PMF Required** mà client không hỗ trợ 802.11w | Trạng thái dừng ở **Authenticating** · thử `pmf optional` |
| ⭐ **Enterprise: xác thực thất bại** | RADIUS không tới được · shared secret sai · chứng thư hết hạn · sai EAP type · tài khoản khóa | `test aaa …` từ WLC · xem log RADIUS/ISE ·  **kiểm tra ngày hết hạn chứng thư** |
| ⭐ **Authenticated nhưng KHÔNG CÓ IP** | **Tầng ⑤:** VLAN sai trong Policy Profile ·  **VLAN chưa cho qua trunk** · DHCP scope cạn · thiếu `ip helper-address` | `show vlan` / `show interface trunk` trên switch ·  `show ip dhcp binding` |
| ⭐ **FlexConnect: có IP nhưng SAI subnet** | **VLAN mapping trong Flex Profile sai** · native VLAN của trunk sai | Kiểm tra `wireless profile flex …` và trunk của port AP (§5.4) |
| ⭐ Có IP nhưng **không ra Internet** | **Tầng ⑥ — không phải lỗi Wi-Fi**: routing, ACL, firewall, DNS, NAT | Ping gateway → ping IP ngoài → ping tên miền.  **Đây là Module-03/06B** |
| ⭐ **Khách không thấy trang đăng nhập** | **ACL pre-auth chặn DNS** · client dùng DNS-over-HTTPS · HSTS cache | Mở **UDP 53** và **DHCP** trong ACL pre-auth · thử vào `http://` (không phải https) |
| ⭐ **Chỉ một loại thiết bị bị lỗi** (VD máy quét, máy in) | Chỉ hỗ trợ **2.4 GHz** · không hỗ trợ **DFS** · cần **data rate thấp** đã bị tắt · không hỗ trợ **WPA3/PMF** | Đây là **client capabilities** (Module-07A §4.1) |
| ⭐ **Kết nối được nhưng vài phút lại rớt** | Session timeout · idle timeout ·  **DFS đổi channel** · roaming hỏng | `show wireless stats client delete reasons` |

#### C. Roaming lỗi (tầng ④ + thiết kế)

| 🔴 Triệu chứng | Nguyên nhân | ✅ Cách sửa |
|---|---|---|
| ⭐ Đi lại thì **rớt cuộc gọi VoIP** | Roam quá chậm (làm lại toàn bộ 802.1X) | Bật **802.11r** (+ k, v) · hoặc **OKC** |
| ⭐ Roam giữa 2 WLC thì **đổi IP, đứt session** | **Mobility group chưa cấu hình** hoặc peer **Down** | `show wireless mobility summary` — peer phải **Up** |
| ⭐ **Client bám AP cũ dù đã đi rất xa** | **Sticky client** | Giảm công suất · tắt rate thấp · bật 11k/v · Optimized Roaming (§6.6) |
| ⭐ Có vùng **mất sóng hẳn** khi đi qua | Thiếu **cell overlap** (cần 15–20%) | Khảo sát lại, thêm AP (Module-07A) |
| ⭐ Bật 802.11r xong **một số máy không join được** | Client cũ không hiểu FT | Đổi sang **FT adaptive**, hoặc **tách WLAN riêng cho voice** |
| ⭐ **FlexConnect: roam trong chi nhánh chậm** khi mất WAN | Chưa cấu hình **FlexConnect Group** → AP không chia sẻ key | Tạo FlexConnect Group cho các AP cùng site (§5.5) |

### 10.4 ⭐ Bộ lệnh troubleshoot

```
═══ CATALYST 9800 (IOS-XE) — dùng cái này là chính ═══
show ap summary                                  ! AP nào up, mode gì, bao nhiêu client
show ap uptime                                   ! AP nào vừa reboot
show ap tag summary                              ! AP đang dùng policy/site/rf tag nào
show ap join stats summary                       ! AP nào join hỏng
show ap join stats detailed <mac-ethernet>       ! HỎNG Ở BƯỚC NÀO của quá trình join
show wlan summary                                ! WLAN nào tồn tại, enable chưa
show wlan id <n>                                 ! chi tiết một WLAN
show wireless profile policy summary             ! Policy Profile & trạng thái
show wireless tag policy detailed <tag>          ! tag này map WLAN nào với policy nào
show wireless client summary                     ! danh sách client
show wireless client mac-address <mac> detail    ! LỆNH QUAN TRỌNG NHẤT
                                                 !   → State, RSSI, SNR, AP, VLAN, IP, policy
show wireless client mac-address <mac> mobility history   ! lịch sử roam của client
show wireless mobility summary                   ! peer mobility Up hay Down
show wireless stats client delete reasons        ! vì sao client bị xóa
show ap dot11 5ghz summary                       ! channel, Tx power từng AP
show ap auto-rf dot11 5ghz                       ! noise, interference, load — dữ liệu RRM

! RadioActive Trace — theo dấu MỘT client qua toàn bộ quá trình:
debug wireless mac <H.H.H> internal
   ... (tái hiện lỗi) ...
no debug wireless mac <H.H.H> internal
   → sinh file /bootflash/ra_trace_MAC_*.txt   đọc file này thấy TỪNG BƯỚC client làm gì

═══ AIREOS (WLC đời cũ) ═══
show ap summary
show ap join stats summary all
show client summary
show client detail <mac>              ! tương đương lệnh detail của C9800
show mobility summary
debug client <mac>                    ! theo dấu 1 client

═══ TRÊN SWITCH nối AP (rất hay bị bỏ qua!) ═══
show power inline <interface>         ! PoE có đủ không
show interface <intf> status          ! up/down, speed
show interface trunk                  ! VLAN nào thật sự được phép qua (FlexConnect!)
show mac address-table interface <intf>
show cdp neighbors detail             ! nhìn thấy AP model, IP

═══ TRÊN CLIENT (Module-07A §11.1) ═══
netsh wlan show interfaces
netsh wlan show wlanreport            ! lịch sử roam & lý do rớt
```

> 🔴  **Nếu chỉ nhớ được 3 lệnh:**
> 1. ⭐ `show wireless client mac-address <mac> detail` —  **client dừng ở State nào**
> 2. ⭐ `show ap join stats detailed <mac>` —  **AP hỏng ở bước join nào**
> 3. ⭐ `show interface trunk` **trên switch** —  **VLAN có thật sự đi được không**

## 🧪 PHẦN 3 — NHÌN THẤY NÓ

> ### 👉 **[LAB 07B — Tuần 13: AP join · Roaming · Chẩn đoán](Module-07B-LAB.md)**

> ⭐ **Module học bằng ĐẦU, không phải bằng tay.** PC 16 GB không dựng nổi WLC + AP,
> nhưng đề cũng **không bắt cấu hình** — nó cho tình huống và bắt **chỉ ra nguyên nhân**.

| LAB | Nội dung | Ví von ở Phần 1 | Cơ chế ở Phần 2 |
|---|---|---|---|
| **A** | ⭐ **AP sẽ join WLC nào?** (6 tình huống) | §2.1 ống nói | §3.5 · §3.6 |
| **B** | ⭐ **12 tình huống chẩn đoán** | §2.3 hai chuỗi độc lập | §3.9 |
| **C** | Nhìn WLC thật trên DevNet | §2.1 | §3.7 |
| **D** | Quan sát roaming bằng laptop | §2.2 chuyển tiếp thư | §3.6 |

> ⚠️ **LAB A và B luyện đúng hai mục khó nhất của blueprint:**
> **3.3.c** (*"discovery algorithms, WLC selection process"*) và
> **3.3.e** (*"troubleshoot WLAN configuration and wireless client connectivity issues"*).
>
> ⭐ **3.3.e là mục DUY NHẤT trong Domain 3.3 không dùng từ "Describe"** — nên LAB B
> là phần đáng đầu tư nhất module này.

---

## 🏗️ PHẦN 4 — TOPO & KIẾN TRÚC

> Bạn vừa học cơ chế. Phần này trả lời: **triển khai WLC cho doanh nghiệp nhiều chi nhánh thế nào?**

### 4.1 Bản đồ: hai mô hình, hai đường đi của traffic

```
   ====== CAMPUS (Local mode) ======      ====== CHI NHÁNH (FlexConnect) ======

        ┌─────────────┐                          ┌─────────────┐
        │     WLC     │                          │  WLC ở HQ   │
        └──────┬──────┘                          └──────┬──────┘
               │                                        │ chỉ CAPWAP CONTROL
      CAPWAP control + DATA                             │ (5246, rất nhẹ)
               │                                        │
        ┌──────┴──────┐                          ┌──────┴──────┐
        │     AP      │                          │     AP      │
        └──────┬──────┘                          └──────┬──────┘
               │                                        │
            [client]                                 [client]
                                                        │
   Traffic đi VÒNG về WLC rồi quay lại         Traffic đổ THẲNG ra LAN chi nhánh
   ("hairpinning")                              (local switching)

   ✅ Chính sách tập trung, roaming mượt        ✅ Không tốn băng thông WAN
   🔴 Tốn băng thông, mất WLC = mất Wi-Fi       🔴 Chính sách phân tán hơn
```

### 4.2 Năm quyết định — và sai thì hỏng thế nào

| # | Quyết định | 🔴 Sai thì hỏng thế nào |
|:---:|---|---|
| ① | **Chi nhánh qua WAN thì dùng FlexConnect** | Dùng Local mode thì **toàn bộ traffic 30 AP chạy về HQ** qua WAN 50 Mbps — nghẽn và độ trễ cao |
| ② | **FlexConnect: port AP phải là TRUNK** | Để access port thì AP join được (VLAN mgmt đúng) nhưng **client sai VLAN hoặc không có IP** |
| ③ | ⭐ **Cấu hình Critical VLAN** *(nếu dùng 802.1X)* | ISE bảo trì 10 phút thì **cả công ty mất mạng**, và bạn cũng không SSH vào được |
| ④ | ⭐ **NTP trước, WLC sau** | Sai giờ thì chứng thư DTLS bị coi là *chưa hiệu lực* —  **AP KHÔNG JOIN ĐƯỢC**, và không có thông báo nào nói rõ |
| ⑤ | **MTU đường AP↔WLC ≥ 1500** | MTU nhỏ thì AP join được nhưng ⭐ **client tải file lớn bị treo** (gói nhỏ qua, gói lớn drop) |

### 4.3 Ba sự thật mà chỉ người đi làm mới biết

| Sự thật | Giải thích |
|---|---|
| 🔴  **AP Registered KHÔNG có nghĩa là SSID đã phát** | Có **hai chuỗi độc lập**: (1) AP↔WLC join được chưa · (2) WLC có **bảo AP phát gì** không. Chuỗi 1 đúng mà chuỗi 2 sai thì AP hiện `Up`, đèn xanh, **nhưng không có SSID nào trên không trung**.  **Luôn chạy `show ap tag summary`, không chỉ `show ap summary`** |
| ⭐ **Client không có IP thì đi xem SWITCH** | Đa số ca *Wi-Fi hỏng* thực ra là **VLAN chưa được phép qua trunk**. Lệnh đầu tiên là `show interface trunk` **trên switch**, không phải soi WLC |
| ⭐ **CLIENT quyết định khi nào roam** | WLC **không ép được**. Nó chỉ **gợi ý** (802.11v), **chỉ đường** (802.11k), **làm nhanh hơn** (802.11r). Sticky client thường là **lỗi driver của client** |

### 4.4 Những thứ này sẽ lớn lên thành gì

| Bạn vừa học | Sẽ thành | Ở module |
|---|---|---|
| CAPWAP, split-MAC | ⭐ **SD-Access wireless**: data đi **VXLAN thẳng vào edge**, không CAPWAP về WLC | **Module-09 §7.5** |
| Roaming L3 anchor/foreign | Guest anchor về DMZ | **Module-09 §6.4** |
| Wireless security (§9) | 802.1X · EAP · WebAuth · PMF ở mức cấu hình | **Module-10 §7** |
| WLC deployment model | Thiết kế WLAN (blueprint 1.2.a) | **Module-09 §4** |
| Troubleshoot 6 tầng | Quy trình chẩn đoán chung | **Module-11** |

### 4.5 Vẽ lại để nhớ

> **Bài tập 15 phút, trên giấy.**
>
> 1. Vẽ lại **cả hai** mô hình ở §4.1, chỉ rõ đường đi của **control** và **data**
> 2. Đánh dấu ① đến ⑤
> 3. Trả lời: *AP hiện Registered trên WLC, đèn xanh, mọi thứ trông ổn — nhưng không client nào thấy SSID. Bạn gõ lệnh gì ĐẦU TIÊN?*

<details>
<summary>Đáp án câu 3</summary>

⭐ **`show ap tag summary`**

Vì có **hai chuỗi độc lập** phải cùng đúng:

```
Chuỗi 1 — AP có kết nối được với WLC không?
   IP -> Discovery -> Select -> DTLS -> Image -> Config -> AP "UP"   ✅ đang đúng

Chuỗi 2 — WLC có BẢO AP phát gì không?
   WLAN Profile + Policy Profile -> Policy Tag -> GÁN TAG CHO AP     ❌ thường thiếu ở đây
```

`show ap summary` chỉ cho biết **chuỗi 1** — nên nó báo `Registered` và bạn tưởng ổn.

⭐ Kiểm tra thêm: WLAN đã `no shutdown` chưa · Policy Profile đã `no shutdown` chưa ·
WLAN ID có **lớn hơn 16** không *(`default-policy-tag` chỉ tự map WLAN ID 1 đến 16)*.

</details>

---

## 💡 4.6 Thực chiến đi làm

| # | Tình huống thật | ⭐ Điều người mới làm sai | Cách làm đúng |
|:---:|---|---|---|
| 1 | Triển khai Wi-Fi cho 20 chi nhánh, WLC ở HQ | Dùng **Local mode** cho tất cả | 🔴  Toàn bộ traffic chi nhánh chạy về HQ qua WAN → nghẽn + độ trễ.  **Dùng FlexConnect local switching** |
| 2 | Chi nhánh hay đứt WAN | Chấp nhận "đứt WAN thì mất Wi-Fi" | ⭐ **FlexConnect + Local auth + FlexConnect Group** → nhân viên vẫn dùng được (§5.3) |
| 3 | Lắp AP mới nhưng port switch vẫn để access | Không hiểu vì sao client sai VLAN | ⭐ **FlexConnect BẮT BUỘC trunk** với native VLAN = VLAN quản lý AP (§5.4) |
| 4 | Cần Wi-Fi cho khách | Tạo VLAN guest rồi trunk khắp campus | 🔴  Rủi ro + phức tạp.  **Guest anchor về WLC ở DMZ** (§6.4) |
| 5 | Điện thoại VoIP rớt khi đi lại | Tăng công suất AP | ⭐ Sai hướng.  Cần **RSSI ≥ −67 khắp nơi**, **overlap 15–20%**, và bật **802.11r/k/v** |
| 6 | Bật 802.11r cho tất cả WLAN | Một số máy cũ không join được | ⭐ Dùng **FT adaptive**, hoặc  **WLAN riêng cho voice có 11r**, WLAN data thì không |
| 7 | WLC cần bảo trì ban ngày | Reboot thẳng | 🔴  Mọi AP Local mode rớt → mất Wi-Fi toàn bộ.  Cần **HA SSO** (§3.7), hoặc làm ngoài giờ |
| 8 | Đổi tag của một nhóm AP | Làm lúc 10 giờ sáng | 🔴  **Đổi tag = AP JOIN LẠI** → rớt ~1 phút.  **Làm ngoài giờ** |
| 9 | WLC không đồng bộ NTP, "để sau" | Nghĩ chỉ ảnh hưởng log | 🔴  **AP sẽ không join được** (DTLS/chứng thư), và log không đối chiếu được.  **NTP là việc đầu tiên** khi dựng WLC (Module-06B) |
| 10 | Không backup config WLC | — | ⭐ WLC giữ **toàn bộ** cấu hình của mọi AP. Mất WLC không backup =  **dựng lại từ đầu** |
| 11 | Đặt WLC ở chi nhánh cho "nhanh" | Mỗi site một WLC nhỏ | ⭐ Tốn license + khó quản lý +  **roaming giữa các site không hoạt động**.  Tập trung + FlexConnect thường tốt hơn |
| 12 | AP mới không join, nghi AP hỏng, gửi bảo hành | — | ⭐ **Kiểm tra theo thứ tự:** PoE → IP → option 43/DNS → firewall 5246/5247 → NTP/giờ → MTU.  **AP hỏng thật là rất hiếm** |

> 🔴  **Ba câu thần chú của người vận hành WLC:**
> 1. ⭐ **"NTP trước, WLC sau."**
> 2. ⭐ **"`show ap summary` chưa đủ — phải xem `show ap tag summary`."**
> 3. ⭐ **"Client không có IP thì đi xem TRUNK trên switch, đừng ngồi soi WLC."**

---

# 📎 PHỤ LỤC — TRA CỨU

> 🔴 **KHÔNG đọc phần này ở lần học đầu tiên.**
>
> | Khi nào | Mở mục nào |
> |---|---|
> | Đang lab mà lỗi | **Gỡ lỗi nhanh** (§14) +  **§10 Troubleshoot 6 tầng** ở Phần 2 |
> | Quên lệnh | **Hộp lệnh** (§14.1) |
> | Tuần 20, ôn thi | **Bẫy đề** (§13) + **Quiz** (§15) |
> | Gặp từ lạ | **Thuật ngữ** (§16) |
> | Tự chấm | **Đúc kết** (§17) |

---

## 🎓 13. BẪY TRONG ĐỀ ENCOR

| # | Bẫy | ✅ Sự thật |
|:---:|---|---|
| 1 | "CAPWAP control là 5247" | 🔴  **Control = 5246 · Data = 5247** |
| 2 | "Cả hai tunnel CAPWAP đều được mã hóa mặc định" | 🔴  **Control: DTLS LUÔN BẬT. Data: DTLS TÙY CHỌN, mặc định TẮT** |
| 3 | "CAPWAP chạy ở Layer 2" | 🔴  **CAPWAP chỉ L3 (UDP/IP).** LWAPP cũ mới có chế độ L2 |
| 4 | "AP và WLC phải cùng subnet" | 🔴  **Không.** Nhưng khác subnet thì **phải có option 43 / DNS / cấu hình tĩnh** |
| 5 | "Broadcast discovery đi qua được router" | 🔴  **Không.** Đây là lý do cần option 43 |
| 6 | "AP luôn join WLC có ít AP nhất" | 🔴  **Là WLC có DUNG LƯỢNG DƯ nhiều nhất** (excess capacity), không phải ít AP nhất |
| 7 | "Primary/Secondary/Tertiary xét sau least-loaded" | 🔴  **Ngược.** Thứ tự: **Primary → Secondary → Tertiary → Master → Least-loaded** |
| 8 | "AP tự tải image từ TFTP server" | 🔴  **AP tải image TỪ WLC** trong quá trình join |
| 9 | "AP xử lý xác thực 802.1X" | 🔴  **WLC làm** (trừ FlexConnect **local auth**) |
| 10 | "WLC gửi ACK cho frame của client" | 🔴  **AP làm** — ACK phải trả trong **SIFS (~10 µs)** |
| 11 | "WLC mã hóa/giải mã frame 802.11" | 🔴  **AP làm** (AES-CCMP tại AP) |
| 12 | "FlexConnect nghĩa là AP không cần WLC" | 🔴  **Vẫn cần WLC** để quản lý. Chỉ **DATA** là đi tắt |
| 13 | "Mất WAN thì FlexConnect mất hết" | 🔴  **Local switching + local auth vẫn chạy hết.** Local switching + central auth: **client cũ sống, client mới chết** |
| 14 | "FlexConnect dùng access port như Local mode" | 🔴  **Phải là TRUNK**, native VLAN = VLAN quản lý AP |
| 15 | "Roam L2 cần mobility tunnel" | 🔴  **Không.**  **Chỉ roam L3 mới cần tunnel** |
| 16 | "Roam L3 thì client đổi IP" | 🔴  **KHÔNG đổi** — đó chính là mục đích của anchor/foreign tunnel |
| 17 | "Anchor là WLC client đang đứng ở đó" | 🔴  **Ngược. Anchor = WLC GỐC. Foreign = WLC HIỆN TẠI** |
| 18 | "Roam L2 inter-controller thì bản ghi client được copy" | 🔴  **L2 = MOVE (di chuyển). L3 = COPY (nhân bản, giữ bản gốc ở anchor)** |
| 19 | "WLC quyết định client roam khi nào" | 🔴  **CLIENT quyết định.** WLC chỉ gợi ý (11v) / chỉ đường (11k) / làm nhanh hơn (11r) |
| 20 | "802.11k làm roam nhanh hơn bằng cách trao đổi key" | 🔴  **11k = neighbor report (chỉ đường).**  **11r mới là trao đổi key trước** |
| 21 | "OKC là chuẩn IEEE" | 🔴  **OKC không phải chuẩn.**  **802.11r (FT) mới là chuẩn** |
| 22 | "Mobility group không giới hạn số WLC" | 🔴  AireOS: **24 WLC/group**, **72 WLC/domain** |
| 23 | "Guest anchor là để tăng tốc độ cho khách" | 🔴  Là để **cách ly traffic khách** và **tập trung kiểm soát ở DMZ** |
| 24 | "AP hiện Registered nghĩa là SSID đã phát" | 🔴  **Không.** Còn phải **gán Policy Tag** có chứa WLAN |
| 25 | "802.11 Authentication là kiểm mật khẩu" | 🔴  Không — kiểm ở **4-way handshake / 802.1X** (Module-07A §3.5) |
| 26 | "WPA3 vẫn dùng PSK" | 🔴  **WPA3-Personal dùng SAE**, không phải PSK. Và  **bắt buộc PMF** |
| 27 | "PEAP cần chứng thư ở cả client và server" | 🔴  **PEAP: chỉ SERVER cần chứng thư.**  **EAP-TLS mới cần cả hai** |
| 28 | "MTU không ảnh hưởng CAPWAP" | 🔴  **Ảnh hưởng nặng.**  Dấu hiệu: gói nhỏ OK, gói lớn treo |
| 29 | "Sai giờ chỉ ảnh hưởng log" | 🔴  **Sai giờ làm DTLS/chứng thư hỏng → AP KHÔNG JOIN ĐƯỢC** |
| 30 | "HA SSO và N+1 giống nhau" | 🔴  **HA SSO: AP KHÔNG phải join lại** (active/standby đồng bộ).  **N+1: AP phải join lại** → có gián đoạn |

---

## 🐛 14. GỠ LỖI NHANH

### 14.1  Bảng port phải nhớ

| Dịch vụ | Port | Ghi chú |
|---|---|---|
| **CAPWAP Control** | **UDP 5246** | DTLS luôn bật |
| **CAPWAP Data** | **UDP 5247** | DTLS tùy chọn |
| **Mobility Control** | **UDP 16666** | Giữa các WLC |
| **Mobility Data** | **UDP 16667** | *(AireOS cũ: EoIP = IP protocol 97)* |
| **RADIUS** | UDP 1812 (auth) / 1813 (acct) | ➡️ Module-10 |
| **TACACS+** | TCP 49 | ➡️ Module-10 |
| **NTP** | UDP 123 | **Bắt buộc cho WLC** — Module-06B |
| **DHCP** | UDP 67/68 | Option 43 (§3.5) |
| **DNS** | UDP/TCP 53 | `CISCO-CAPWAP-CONTROLLER` |
| **HTTPS (GUI WLC)** | TCP 443 | |
| **SSH** | TCP 22 | |

### 14.2  Quy trình 60 giây — khi có người báo "Wi-Fi hỏng"

```
① HỎI: "MỘT người hay NHIỀU người? MỘT chỗ hay KHẮP NƠI? Từ khi nào?"
      · 1 người, 1 máy      → client (driver, năng lực, cấu hình máy)
      · 1 khu vực           → AP đó (join? channel? RF?)
      · toàn bộ             → WLC / RADIUS / DHCP / mạng lõi
      · "từ sau khi đổi X"  → chính X là thủ phạm — kiểm tra trước tiên

② show wireless client mac-address <mac> detail | include State
      → CLIENT DỪNG Ở TRẠNG THÁI NÀO?  (§9.2 — bước quyết định nhất)

③ Theo trạng thái đó, nhảy đúng tầng trong 6 tầng (§9.1)

④ Nếu client không xuất hiện trong danh sách → quay lại TẦNG ① (RF) hoặc ② (AP join)
      show ap summary  +  show ap tag summary

⑤ Nếu nghi VLAN/IP → ĐI XEM SWITCH, không ngồi soi WLC
      show interface trunk  ·  show vlan  ·  show ip dhcp binding
```

### 14.3  Bảng tra nhanh: "Client dừng ở State X" → xem gì

| Client dừng ở | Nhìn vào |
|---|---|
| **Không xuất hiện trong `show wireless client`** | RF (RSSI/SNR/channel/band) · AP đã join chưa · SSID có được phát không (`show ap tag summary`) |
| **Associating** | WLAN config · AP quá tải · client bị loại (exclusion list) |
| **Authenticating / 8021X_REQD** | **PSK sai** · **RADIUS không tới được** · **chứng thư hết hạn** · **PMF mismatch** · sai EAP type |
| **IP Learn / DHCP_REQD** | **VLAN sai** · **trunk chưa cho VLAN qua** · **DHCP cạn** · thiếu `ip helper-address` |
| **Webauth Pending** | **ACL pre-auth chặn DNS** · portal không tới được |
| **RUN nhưng vẫn "không vào mạng được"** | **TẦNG ⑥ — mạng có dây:** routing, ACL, firewall, NAT, DNS.  **Không còn là vấn đề Wi-Fi** |

---

## 📝 15. QUIZ TỰ KIỂM TRA

**1.** Port và trạng thái mã hóa của hai tunnel CAPWAP?
<details><summary>Đáp án</summary>

 **Control: UDP 5246 — DTLS LUÔN BẬT (không tắt được)**
 **Data: UDP 5247 — DTLS TÙY CHỌN, mặc định TẮT**

 Data thường không mã hóa vì traffic client **đã được WPA2 mã hóa** rồi, và DTLS thêm sẽ tốn CPU.
</details>

**2.** Kể 5 cách AP tìm WLC. Cách nào **không hoạt động** khi AP khác subnet với WLC?
<details><summary>Đáp án</summary>

 **5 cách:** (1) primed/NVRAM (primary-secondary-tertiary + WLC đã join + mobility group members) ·
(2) cấu hình tĩnh qua console · (3)  **DHCP option 43** · (4)  **DNS `CISCO-CAPWAP-CONTROLLER.<domain>`** ·
(5)  **broadcast subnet local**

🔴  **Broadcast (5) không hoạt động khi khác subnet** — broadcast không qua router.
 **Đây là câu hỏi phổ biến nhất của 3.3.c.**
</details>

**3.** Thứ tự WLC selection process?
<details><summary>Đáp án</summary>

 **Primary → Secondary → Tertiary → Master controller → Least-loaded**

🔴  **"Least-loaded" = WLC có DUNG LƯỢNG DƯ (excess capacity) lớn nhất**,  **không phải** WLC có ít AP nhất,
 **cũng không phải** WLC có % tải thấp nhất.
</details>

**4.** AP có IP, ping được WLC, firewall đã mở 5246/5247, nhưng join hỏng ở bước DTLS. Nguyên nhân?
<details><summary>Đáp án</summary>

 **Sai thời gian hệ thống.** DTLS dùng **chứng thư số**, chứng thư có ngày hiệu lực/hết hạn.
Đồng hồ sai → chứng thư bị coi là không hợp lệ.

 **Sửa: cấu hình NTP** (Module-06B §3) và kiểm tra `show clock` trên cả WLC và AP.
</details>

**5.** Trong split-MAC, AP làm gì và WLC làm gì? Nêu nguyên tắc chia.
<details><summary>Đáp án</summary>

 **Nguyên tắc:**  **việc gì phải xong trong micro-giây → AP. Việc gì chậm hơn được → WLC.**

 **AP (real-time):** beacon/probe response ·  **ACK (phải trả trong SIFS ~10 µs)** · CSMA/CA & backoff ·
 **mã hóa/giải mã AES-CCMP** · retransmission · đo & báo cáo RF

 **WLC (non-real-time):**  **802.1X/RADIUS** · association & client database ·  **quản lý key** ·
 **RRM (DCA/TPC)** · quyết định roaming/mobility · VLAN/ACL/QoS policy
</details>

**6.** FlexConnect với **local switching + central auth**, mất WAN. Client đang kết nối và client mới thì sao?
<details><summary>Đáp án</summary>

 **Client đang kết nối: ✅ TIẾP TỤC CHẠY** — đã xác thực xong, data đi local nên không cần WLC.
🔴  **Client MỚI: ❌ KHÔNG vào được** — cần WLC/RADIUS để xác thực mà không tới được.

 Muốn client mới cũng vào được → phải dùng  **local auth** (+ **FlexConnect Group** cho backup RADIUS/Local EAP).
</details>

**7.** So sánh roam L2 inter-controller và roam L3 inter-controller: bản ghi client, IP, tunnel.
<details><summary>Đáp án</summary>

| | **L2 inter-controller** | **L3 inter-controller** |
|---|---|---|
| Subnet client trên 2 WLC | **Giống nhau** | 🔴  **Khác nhau** |
| Bản ghi client | **MOVE** (chuyển hẳn, WLC cũ xóa) | **COPY** (nhân bản, WLC gốc **giữ lại**) |
| Client giữ IP | ✅ (vì subnet không đổi) | **✅ — nhờ tunnel** |
| Mobility tunnel | ❌ **Không cần** | **CÓ — bắt buộc** |
| Vai trò | — | **Anchor** (WLC gốc) ↔  **Foreign** (WLC hiện tại) |
</details>

**8.** Anchor và Foreign — cái nào là WLC gốc? Guest anchor dùng để làm gì?
<details><summary>Đáp án</summary>

 **Anchor = WLC GỐC** (nơi client kết nối lần đầu, giữ IP/VLAN gốc).
 **Foreign = WLC HIỆN TẠI** (nơi client đang đứng, tunnel traffic về anchor).

 **Guest anchor:** WLAN khách được **anchor sẵn** về một WLC đặt ở **DMZ**.
 Traffic khách **không bao giờ chạm mạng nội bộ campus**, và toàn bộ khách đổ về **một điểm kiểm soát duy nhất**
(firewall, WebAuth, rate-limit).  Cũng tránh phải trunk VLAN guest khắp campus.
</details>

**9.** Phân biệt 802.11k, 802.11v, 802.11r.
<details><summary>Đáp án</summary>

| | Làm gì |
|---|---|
| **802.11k** | **Neighbor report** — AP cho client biết AP hàng xóm ở channel nào → **không phải quét mù** |
| **802.11v** | **BSS Transition Management** — WLC **gợi ý** client nên chuyển sang AP nào |
| **802.11r** | **Fast Transition** — **chuẩn bị key TRƯỚC khi rời AP cũ** →  **roam < 50 ms** |

 **Mẹo nhớ:** **k** = **K**now (biết hàng xóm) · **v** = ad**V**ise (khuyên) · **r** = **R**oam fast (chuyển nhanh).
 Chỉ **802.11r** thực sự làm việc trao đổi key.
</details>

**10.** AP hiện `Registered` trên WLC, đèn xanh, nhưng không thấy SSID nào. Kiểm tra gì?
<details><summary>Đáp án</summary>

 **`show ap tag summary`** — kiểm tra **Policy Tag** đã gán cho AP chưa, và tag đó có **chứa WLAN** nào không.

 Có **hai chuỗi độc lập** (§10.3):
· Chuỗi 1 (AP↔WLC): IP → discovery → select → DTLS → image → config → **AP Up** ✅
·  Chuỗi 2 (WLC bảo AP phát gì): WLAN Profile + Policy Profile → **Policy Tag** →  **gán cho AP**

 Kiểm tra thêm: WLAN có `no shutdown` chưa · Policy Profile có `no shutdown` chưa ·
 WLAN ID có **> 16** không (default-policy-tag chỉ map ID 1–16).
</details>

**11.** Client kết nối được, ping và web nhỏ OK, nhưng tải file lớn thì treo. AP ở chi nhánh qua VPN. Nguyên nhân?
<details><summary>Đáp án</summary>

 **MTU** trên đường AP ↔ WLC quá nhỏ (§3.3).
 CAPWAP thêm ~48 byte overhead → gói 1500 byte thành ~1548 byte → bị drop trên đường VPN/GRE có MTU nhỏ.
 **Gói nhỏ (ping, DNS, web nhẹ) vẫn qua được** — đây là dấu hiệu nhận dạng.

 **Kiểm chứng:** `ping <WLC> df-bit size 1500 source <intf-subnet-AP>` → thất bại ở size lớn, thành công ở size nhỏ.
 **Sửa:** tăng MTU trên đường đi (khuyến nghị ≥ 1500, tối thiểu ~1485).
</details>

**12.** Client `Authenticated` nhưng không có IP. Ba nguyên nhân, và **lệnh đầu tiên** bạn gõ?
<details><summary>Đáp án</summary>

 **Đây là tầng ⑤** (§9.1).

 **Ba nguyên nhân:**
1.  **VLAN sai** trong Policy Profile
2.  **VLAN chưa được phép qua trunk** của port AP *(rất hay gặp với FlexConnect)*
3.  **DHCP scope cạn** hoặc **thiếu `ip helper-address`** trên SVI

 **Lệnh đầu tiên: `show interface trunk` TRÊN SWITCH** — không phải trên WLC.
 **Đây là bài học lớn: rất nhiều "lỗi Wi-Fi" thật ra nằm ở mạng có dây.**
</details>

**13.** HA SSO khác N+1 redundancy ở điểm nào quan trọng nhất?
<details><summary>Đáp án</summary>

 **HA SSO: AP KHÔNG phải join lại.** Hai WLC là cặp Active/Standby đồng bộ trạng thái AP
(và cả client nếu có Client SSO) → chuyển đổi gần như tức thời.

 **N+1: AP PHẢI discovery + join lại** WLC dự phòng →  **gián đoạn vài chục giây**, client bị rớt.
</details>

**14.** Sticky client là gì, gây hại thế nào, và 4 cách trị?
<details><summary>Đáp án</summary>

 **Sticky client:** client **bám AP cũ** dù đã đi xa và có AP tốt hơn ở gần.

🔴  **Hai tác hại:** (1) chính client đó chậm; (2)  **quan trọng hơn — nó chiếm airtime rất lâu
cho mỗi gói (vì tốc độ thấp) → làm chậm CẢ CELL của AP cũ.**

 **4 cách trị:** (1)  **giảm công suất AP** (cell nhỏ, tín hiệu tụt nhanh) · (2)  **tắt data rate thấp** ·
(3)  **bật 802.11k + 802.11v** (chỉ đường + gợi ý) · (4)  **Optimized Roaming / RX-SOP**
(WLC chủ động đá client dưới ngưỡng).  *(Cộng thêm: cập nhật driver Wi-Fi của client.)*
</details>

**15.** Chi nhánh 30 AP, WLC ở HQ cách 800 km, WAN 50 Mbps hay đứt. Bạn thiết kế thế nào và vì sao?
<details><summary>Đáp án</summary>

 **FlexConnect + local switching + local auth + FlexConnect Group.**

| Lựa chọn | Lý do |
|---|---|
| **FlexConnect (không Local mode)** | Local mode tunnel toàn bộ data về HQ → **50 Mbps WAN không kham nổi 30 AP**, và độ trễ cao |
| **Local switching** | Traffic đổ thẳng ra LAN chi nhánh — chỉ **CAPWAP control** đi qua WAN (rất nhẹ) |
| **Local auth** (RADIUS tại chỗ hoặc Local EAP) | **Đứt WAN thì client MỚI vẫn vào được** (§5.3) |
| **FlexConnect Group** | Chia sẻ key giữa các AP → **roaming vẫn nhanh khi ở Standalone mode** · backup RADIUS |
| **Port switch = TRUNK** | Native VLAN = VLAN quản lý AP, cho phép các VLAN client (§5.4) |
| **`no local-site`** trong Site Tag | Dòng thực sự bật FlexConnect trên C9800 |
| **Efficient AP Image Upgrade** | 30 AP tải image qua WAN 30 lần = thảm họa. Cho 1 AP tải rồi chia lại |
</details>

---

## 📚 16. THUẬT NGỮ ANH–VIỆT

| English | Tiếng Việt / Giải thích |
|---|---|
| **CAPWAP** | Giao thức đường hầm AP↔WLC (RFC 5415).  Control **5246** / Data **5247** |
| **LWAPP** | Giao thức Cisco cũ, tiền thân của CAPWAP |
| **DTLS** | TLS chạy trên UDP — mã hóa tunnel CAPWAP |
| **Split-MAC** | Chia chức năng MAC giữa AP (real-time) và WLC (non-real-time) |
| **Lightweight AP / Autonomous AP** | AP cần WLC / AP độc lập |
| **WLC** (Wireless LAN Controller) | Bộ điều khiển WLAN |
| **C9800 / AireOS** | Nền tảng WLC hiện tại (IOS-XE) / thế hệ cũ |
| **EWC** | WLC nhúng chạy trên một AP |
| **MIC** (Manufacturer Installed Certificate) | Chứng thư nhà máy trong AP — dùng cho DTLS |
| **Discovery / Join** | Hỏi thăm các WLC / Cam kết với một WLC |
| **DHCP Option 43** | Trường DHCP chở danh sách IP WLC (sub-option **f1**) |
| **CISCO-CAPWAP-CONTROLLER** | Tên DNS AP tự tra để tìm WLC |
| **Primary / Secondary / Tertiary** | Danh sách WLC ưu tiên gán cho AP |
| **Master controller** | WLC nhận mọi AP mới chưa được gán primary |
| **Least-loaded** | WLC còn **dung lượng dư** lớn nhất |
| **HA SSO / N+1** | Cặp WLC Active-Standby (AP **không** join lại) / dự phòng chung (AP **phải** join lại) |
| **AP Fallback** | AP tự quay về WLC primary khi nó sống lại |
| **FlexConnect** (H-REAP) | AP ở chi nhánh, data đổ ra LAN tại chỗ |
| **Central / Local switching** | Data tunnel về WLC / đổ ra VLAN tại chỗ |
| **Central / Local authentication** | WLC xác thực / AP tự xác thực |
| **Connected / Standalone mode** | FlexConnect còn liên lạc WLC / mất liên lạc |
| **FlexConnect Group** | Nhóm AP cùng site chia sẻ key & backup RADIUS |
| **OEAP** (OfficeExtend AP) | AP mang về nhà, tunnel DTLS qua Internet về WLC |
| **Split tunneling** | Một phần traffic local, một phần về HQ |
| **Hairpinning** | Traffic đi vòng về WLC rồi quay lại |
| **Intra-controller roam** | Đổi AP, cùng WLC |
| **Inter-controller L2 roam** | Đổi WLC, **cùng** subnet → bản ghi **MOVE**, không cần tunnel |
| **Inter-controller L3 roam** | Đổi WLC, **khác** subnet → bản ghi **COPY** + **mobility tunnel** |
| **Anchor / Foreign controller** | WLC **gốc** (giữ IP) / WLC **hiện tại** |
| **Symmetric / Asymmetric tunneling** | Cả hai chiều qua anchor / chỉ một chiều |
| **Mobility Group / Domain** | Nhóm WLC roam nhanh (≤24) / tập hợp lớn hơn (≤72) |
| **Guest anchor / Auto-anchor** | Neo WLAN khách về WLC ở DMZ |
| **PMK caching / OKC / CCKM** | Các cơ chế cache key để roam nhanh (không phải chuẩn IEEE) |
| **802.11r (FT)** | Fast Transition — chuẩn IEEE, chuẩn bị key trước khi roam |
| **802.11k / 802.11v** | Neighbor report / BSS Transition Management |
| **Over-the-Air / Over-the-DS** | Hai chế độ trao đổi FT |
| **Sticky client** | Client bám AP cũ dù đã đi xa |
| **Optimized Roaming / RX-SOP** | WLC đá client yếu / AP bỏ qua tín hiệu dưới ngưỡng |
| **Policy Tag / Site Tag / RF Tag** | Ba tag của C9800 gán cho AP |
| **WLAN Profile / Policy Profile** | Định nghĩa SSID+bảo mật / VLAN+chính sách |
| **`local-site` / `no local-site`** | Local mode / **FlexConnect** |
| **WPA2 / WPA3 / SAE / OWE** | Chuẩn bảo mật · SAE thay PSK ở WPA3 · OWE = mở nhưng có mã hóa |
| **PSK / 802.1X (Enterprise)** | Mật khẩu chung / tài khoản riêng qua RADIUS |
| **EAP-TLS / PEAP / EAP-TTLS / EAP-FAST** | Các loại EAP — xem §8.3 |
| **WebAuth (LWA / CWA)** | Captive portal trên WLC / trên ISE |
| **PMF / 802.11w** | Bảo vệ frame quản lý — chống deauth attack |
| **RA Trace** (RadioActive Trace) | Công cụ theo dấu một client qua toàn bộ quá trình trên C9800 |

---

## 🎯 17. ĐÚC KẾT MODULE-07B

**3 điều rút ra:**

1. 🔴  **Quá trình AP join là một chuỗi 6 bước, và mỗi bước có một kiểu hỏng riêng:**
    **IP → Discovery (5 cách) → Selection (Primary→Secondary→Tertiary→Master→Least-loaded)
   → DTLS/Join → Image → Config → RUN.**
    Nhớ  **CAPWAP control 5246 (DTLS luôn bật) / data 5247 (DTLS tùy chọn)** ·
    **broadcast không qua router → khác subnet phải có option 43 / DNS** ·
    **least-loaded = dư nhiều nhất, KHÔNG phải ít AP nhất** ·
   🔴  **sai giờ = DTLS hỏng = không join** ·  **MTU nhỏ = gói lớn treo**.

2. 🔴  **Roaming: chỉ Layer 3 mới cần tunnel, và client LUÔN giữ IP:**
    **Intra-controller** (cùng WLC) ·  **Inter-controller L2** (cùng subnet → bản ghi **MOVE**, không tunnel) ·
    **Inter-controller L3** (khác subnet → bản ghi **COPY** + **mobility tunnel UDP 16666/16667**,
    **ANCHOR = WLC gốc**,  **FOREIGN = WLC hiện tại**).  Ứng dụng lớn nhất là  **guest anchor về DMZ**.
   Và luôn nhớ:  **CLIENT quyết định roam** — 11k chỉ đường, 11v gợi ý,  **11r mới thực sự làm nhanh**.

3. 🔴  **Troubleshoot (3.3.e) là mục duy nhất không "describe" — và câu hỏi đầu tiên LUÔN là
   "client dừng ở State nào":**  đi theo  **6 tầng: RF → AP join → WLAN config → Auth → IP/DHCP → Upstream**.
    Hai bài học đắt nhất:  **"AP Registered ≠ SSID được phát"** (phải xem  `show ap tag summary`,
   vì có **hai chuỗi độc lập**) và  **"Client không có IP thì đi xem TRUNK trên switch"** —
   🔴  **đa số ca "Wi-Fi hỏng" thật ra nằm ở cấu hình, VLAN, hoặc mạng có dây.**

🧠 **Một câu để nhớ:** *AP là  **lễ tân giỏi tay chân nhưng không có quyền** — nó tự chào khách và
tự gật đầu (beacon, ACK, mã hóa) nhưng mọi quyết định phải bấm  **ống nói 5246** hỏi sếp;
 **FlexConnect là đưa lễ tân chìa khóa cửa sau**;  **roaming L3 là dịch vụ chuyển tiếp thư** để bạn
đổi chỗ ở mà không đổi địa chỉ; và khi có sự cố,  **đừng hỏi "Wi-Fi sao thế" — hãy hỏi
"client đang dừng ở bước nào".***

---

### ✅ TỰ CHẤM

**Phần A — Trả lời được bằng lời của mình:**

| # | Câu | ✅ |
|:---:|---|:---:|
| 1 | **Autonomous vs Lightweight AP** — mất WLC thì mỗi loại thế nào | ☐ |
| 2 | **Split-MAC**: AP làm gì, WLC làm gì, **nguyên tắc chia** là gì | ☐ |
| 3 | 🔴  Vì sao **ACK và mã hóa phải ở AP**? (con số SIFS) | ☐ |
| 4 | **CAPWAP: 2 tunnel, 2 port, tunnel nào luôn mã hóa** | ☐ |
| 5 | CAPWAP chạy ở tầng nào? Hệ quả gì? | ☐ |
| 6 | **Vấn đề MTU**: triệu chứng nhận dạng + lệnh kiểm chứng | ☐ |
| 7 | **6 giai đoạn AP join** — theo thứ tự | ☐ |
| 8 | Vì sao lần join đầu có thể mất 5–10 phút | ☐ |
| 9 | **5 cách discovery** — cách nào chết khi khác subnet | ☐ |
| 10 | Đọc được chuỗi hex **DHCP option 43** (`f104.0a0a.0a05` = ?) | ☐ |
| 11 | Điều kiện bắt buộc để phương án **DNS** hoạt động | ☐ |
| 12 | **Thứ tự WLC selection** — 5 bước | ☐ |
| 13 | 🔴  **"Least-loaded" nghĩa chính xác là gì** — cho ví dụ bằng số | ☐ |
| 14 | **HA SSO vs N+1** — khác biệt quan trọng nhất | ☐ |
| 15 | Local mode: traffic đi đường nào? **Hairpinning** là gì? | ☐ |
| 16 | **FlexConnect: 2 trục lựa chọn, 4 tổ hợp** | ☐ |
| 17 | 🔴  **Bảng "cái gì sống sót ở Standalone mode"** (3 dòng) | ☐ |
| 18 | Vì sao FlexConnect **bắt buộc trunk**? Native VLAN là gì? | ☐ |
| 19 | **`no local-site`** làm gì trên C9800 | ☐ |
| 20 | **FlexConnect Group** giải quyết vấn đề gì | ☐ |
| 21 | **OEAP** là gì | ☐ |
| 22 | 🔴  **3 loại roam** — bảng đầy đủ (MOVE vs COPY, tunnel hay không) | ☐ |
| 23 | **Anchor vs Foreign** — cái nào là WLC gốc | ☐ |
| 24 | **Port mobility tunnel** | ☐ |
| 25 | **Mobility Group vs Domain** — số lượng tối đa | ☐ |
| 26 | **Guest anchor** — 3 lợi ích | ☐ |
| 27 | **802.11k / v / r** — phân biệt rõ | ☐ |
| 28 | **OKC vs 802.11r** — cái nào là chuẩn IEEE | ☐ |
| 29 | **Over-the-Air vs Over-the-DS** | ☐ |
| 30 | **Sticky client** — tác hại (2) và cách trị (4) | ☐ |
| 31 | Điều kiện thiết kế để roam mượt (RSSI, overlap, thời gian) | ☐ |
| 32 | **Chuỗi WLAN Profile → Policy Profile → Policy Tag → AP** | ☐ |
| 33 | **3 tag của C9800** — mỗi tag trả lời câu hỏi gì | ☐ |
| 34 | 🔴  **3 lỗi cấu hình WLAN kinh điển** + giới hạn WLAN ID 1–16 | ☐ |
| 35 | **WPA2 vs WPA3** · **PSK vs SAE** · **Personal vs Enterprise** | ☐ |
| 36 | **EAP-TLS vs PEAP** — bên nào cần chứng thư | ☐ |
| 37 | **WebAuth**: LWA vs CWA · vì sao ACL pre-auth phải mở DNS | ☐ |
| 38 | **PMF/802.11w** chống gì · bẫy khi đặt Required | ☐ |
| 39 | 🔴  **6 tầng troubleshoot** — theo thứ tự | ☐ |
| 40 | 🔴  **Client dừng ở State nào → xem gì** (bảng §14.3) | ☐ |
| 41 | 3 lệnh quan trọng nhất khi troubleshoot | ☐ |
| 42 | Vì sao **"AP Registered ≠ SSID được phát"** (2 chuỗi độc lập) | ☐ |
| 43 | **Bảng port** (5246, 5247, 16666, 16667, 123, 1812) | ☐ |
| 44 | 🔴  Vì sao **NTP là việc đầu tiên** khi dựng WLC | ☐ |

**Phần B — Lab:**

| # | Yêu cầu | ✅ |
|:---:|---|:---:|
| 1 | **LAB A**: làm đúng ≥ 5/6 tình huống **trước khi mở đáp án** | ☐ |
| 2 | 🔴  Riêng **tình huống 2** — giải thích được *"ping được ≠ join được"* | ☐ |
| 3 | 🔴  Riêng **tình huống 4** — tính đúng **excess capacity**, không bị bẫy | ☐ |
| 4 | Riêng **tình huống 6** — nối được sang **NTP/Module-06B** | ☐ |
| 5 | **LAB B**: làm đúng ≥ 9/12 tình huống chẩn đoán | ☐ |
| 6 | Với mỗi câu LAB B, xác định đúng **tầng** trong 6 tầng | ☐ |
| 7 | 🔴  Nhận ra **chỉ câu 12 là vấn đề RF thuần túy** | ☐ |
| 8 | 🚀 **LAB C**: đăng nhập được DevNet Sandbox C9800 | 🚀 ☐ |
| 9 | 🚀  Vẽ lại được chuỗi **WLAN→Policy→Tag→AP** của 1 SSID có thật | 🚀  ☐ |
| 10 | 🚀  Chỉ ra 1 AP và nói được nó **Local mode hay FlexConnect** — dựa vào đâu | 🚀  ☐ |
| 11 | 🚀  Trả lời được: đổi VLAN của SSID thì sửa ở **Policy Profile** hay **WLAN Profile** | 🚀 ☐ |
| 12 | 🚀  Tìm được **State / RSSI / SNR / VLAN** của một client thật | 🚀 ☐ |
| 13 | **LAB D**: quan sát được **BSSID đổi mà SSID giữ nguyên** = roaming | ☐ |
| 14 | Xác nhận **IP không đổi** khi roam | ☐ |
| 15 | Trong `wlanreport`, tìm được lần **rớt hẳn** (roam thất bại) hoặc xác nhận không có | ☐ |
| 16 | Quan sát hiện tượng **ping-pong** hoặc **sticky** ở chính môi trường của bạn | ☐ |

> **Nếu chỉ có thời gian làm một nửa:** ưu tiên **mục 1–4** (LAB A — đúng dạng câu hỏi 3.3.c)
> và **mục 5–7** (LAB B — đúng dạng câu hỏi 3.3.e).  **Hai LAB này làm trên giấy, không cần thiết bị,
> và bao phủ chính xác hai mục blueprint khó nhất của khối wireless.**
>
> ⚠️  **Chưa tick được ≥ 38/44 ở Phần A thì nên đọc lại §3, §6, §9 trước khi sang Module-08.**
>
> 🎉  **Hết Module-07B = hết khối Wireless.** Bạn đã xong  **toàn bộ Domain 3.0 Infrastructure (30% đề)**
> — khối lớn nhất và khó nhất của ENCOR.  **Đây là mốc Tuần 13 của ROADMAP.**

---

## 🔗 18. TÀI LIỆU CHO MODULE NÀY

| Nguồn | Cụ thể |
|---|---|
| **Sách OCG 350-401** | Chương *Wireless Infrastructure* và *Wireless Roaming and Location Services* |
| **Cisco doc**  | ***Lightweight AP (LAP) Registration to a Wireless LAN Controller (WLC)*** —  **tài liệu gốc cho toàn bộ §3.4–3.6.** Search: `cisco lightweight ap registration wlc` |
| **Cisco doc**  | ***Wireless LAN Controller Configuration Guide (Catalyst 9800, IOS-XE)*** — chương *AP Join*, *Mobility*, *FlexConnect*, *Tags & Profiles* |
| **Cisco doc**  | ***Catalyst 9800 Best Practices Guide*** —  giải thích mô hình **Tag** rõ nhất (§7) |
| **Cisco doc**  | *DHCP Option 43 for Lightweight Cisco Aironet APs Configuration Example* —  chuỗi hex từng bước |
| **Cisco doc**  | *FlexConnect Feature Matrix* —  bảng chính thống "tính năng nào chạy ở Standalone mode" (§5.3) |
| **Cisco doc**  | *Wireless Mobility Groups / Inter-Controller Roaming* —  anchor/foreign, symmetric tunneling |
| **Cisco doc**  | *Wireless Guest Anchor Configuration Example* —  use case §6.4 |
| **Cisco doc**  | *802.11r Fast Transition Deployment Guide* · *802.11k/v Assisted Roaming* |
| **Cisco doc**  | ***Troubleshoot Client Connectivity Issues on Catalyst 9800*** —  **RadioActive Trace** từng bước (§9.4) |
| **Cisco doc** | *High Availability SSO Deployment Guide for Catalyst 9800* |
| **RFC 5415** | CAPWAP Protocol Specification |
| **Cisco Validated Design**  | *Campus Wireless LAN Design Guide* · *SD-Access Wireless Design Guide* ( liên hệ Module-09) |
| **Cisco DevNet**  | `developer.cisco.com/site/sandbox/` — sandbox **Catalyst 9800** (LAB C) |
| **Video**  | CBT Nuggets ENCOR — module Wireless · **Keith Barker**: search `Keith Barker CAPWAP`, `Keith Barker wireless roaming` |
| **Blog**  | **mrncciew.com** ( có bài phân tích **từng frame** của quá trình AP join và roaming — cực kỳ đáng đọc) · **wifinigel.blogspot.com** · **Clear To Send** podcast |
| **NetworkLessons** | *CAPWAP*, *Wireless LAN Controller*, *FlexConnect*, *Wireless Roaming* |
| **Forum** | https://community.cisco.com → **Wireless - Mobility**. Search: `ap not joining wlc dtls`, `ap registered but no ssid`, `capwap mtu issue`, `flexconnect standalone mode clients`, `9800 policy tag ssid not broadcasting`, `l3 roaming anchor foreign` |

---

**➡️ Tiếp theo:** Module-08 — Virtualization & Overlay
*(VRF-lite · GRE · IPsec · GRE over IPsec · LISP · VXLAN · hypervisor & vSwitch — **Tuần 14**)*

> **Tin vui:** Module-08 **quay lại lab được trên EVE-NG** — VRF-lite và GRE over IPsec đều là
> **"configure and verify"** (blueprint 2.2), dựng ngon trên máy 16 GB.
> Và  **LISP + VXLAN học ở Module-08 chính là nền tảng của SD-Access ở Module-09** — đừng bỏ qua.
