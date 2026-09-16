# Module-01 — Packet Forwarding & Kiến trúc thiết bị

> 🧭 **Lộ trình:** Module-00 → Module-P0 → `[Bạn đang ở đây] Module-01` → Module-02 (Layer 2) → …
>
> 📊 **Vị trí trong blueprint:** mục **1.7 — Differentiate hardware and software switching mechanisms**
> (Domain 1.0 Architecture, 15%). Cụ thể: *Process switching vs CEF · MAC address table và TCAM · FIB vs RIB*.
>
> ⏱️ **Tuần 3** · 10 giờ · 1 tuần

---

# 📌 TÓM TẮT — đọc 10 phút là nắm khung

## Module này trả lời một câu hỏi duy nhất

> **"Gói tin đi qua router/switch bằng đường nào — và vì sao đường đó nhanh?"**

Trả lời được câu đó thì bạn hiểu luôn 4 thứ tưởng như không liên quan:
vì sao `debug ip packet` im lặng · vì sao ping lần đầu mất 1 gói ·
vì sao ACL không apply được khi TCAM đầy · vì sao switch L3 nhanh hơn router.

## Bức tranh toàn module trong một hình

```
   ┌──────────────────────────────────────────────────────────────┐
   │  CONTROL PLANE  —  chạy trên CPU  —  "người lập kế hoạch"     │
   │                                                              │
   │   OSPF · BGP · Static ──▶  RIB  (bảng route, có AD/metric)   │
   │   ARP ─────────────────▶  ARP table                          │
   └──────────────┬────────────────────────┬──────────────────────┘
                  │ dịch sang              │ dịch sang
                  ▼                        ▼
   ┌──────────────────────────────────────────────────────────────┐
   │  DATA PLANE  —  chạy trên ASIC  —  "người thi hành"           │
   │                                                              │
   │      FIB              +        Adjacency Table               │
   │  "đi ra cửa nào"           "dán 14 byte L2 nào vào đầu gói"  │
   │                                                              │
   │   Gói vào ──▶ tra FIB ──▶ dán header ──▶ Gói ra   (rất nhanh)│
   └──────────────────────────────────────────────────────────────┘
                  │
                  │  ⚠️ Gói ASIC không xử lý nổi thì bị "PUNT" ngược lên CPU
                  ▼        (gói gửi tới chính router, cần ARP, cần fragment…)
             CPU xử lý  —  chậm  —  punt nhiều = CPU 100% = sự cố
```

## 7 ý phải nhớ

| # | Ý | Một câu |
|:---:|---|---|
| 1 | **3 plane** | Data = ASIC (chuyển gói) · Control = CPU (xây bảng) · Management = quản lý (SSH/SNMP) |
| 2 | **PUNT** | ASIC gặp gói khó → đẩy lên CPU. **Punt nhiều = CPU 100%** = nguyên nhân số 1 của "thiết bị chậm bất thường" |
| 3 | **CEF vs Fast switching** | CEF = **topology-driven** (bảng dựng sẵn từ RIB) · Fast switching = **traffic-driven** (gói đầu tạo cache, đã bị bỏ) |
| 4 | **RIB → FIB** | RIB là **biên bản họp** (có AD, metric, uptime) · FIB là **quyết định đã ký** (chỉ còn "đi ra đâu") |
| 5 | **Adjacency Table** | Chứa sẵn **14 byte header L2** (MAC đích + MAC nguồn + EtherType) để ASIC dán vào gói |
| 6 | **CAM vs TCAM** | CAM: tra **MAC**, khớp chính xác · TCAM: tra **ACL/QoS**, có bit *"don't care"* nên khớp được dải |
| 7 | **`debug ip packet`** | Chỉ thấy gói **process-switched**. CEF bật → **không thấy traffic người dùng** ← bẫy đề kinh điển |

## Bảng lệnh cốt lõi

| Lệnh | Cho biết gì |
|---|---|
| `show ip cef summary` | CEF có bật không |
| `show ip route` vs `show ip cef` | **So sánh RIB và FIB** — bài học chính |
| `show adjacency detail` | 14 byte header L2 đã chuẩn bị sẵn |
| `show ip cef exact-route <src> <dst>` | Flow cụ thể này đi ra interface nào |
| `show processes cpu sorted \| exclude 0.00` | CPU bận vì control plane hay data plane |
| `show sdm prefer` | TCAM đang chia phần thế nào (switch thật) |

## 🗺️ Bố cục module — đọc theo đúng thứ tự này

| Phần | Tên | Trả lời câu hỏi | Đọc thế nào | Thời gian |
|:---:|---|---|---|:---:|
| **1** | 🧠 **CÁI ĐÓ LÀ GÌ** | *"À, ra nó là thế"* | Đọc **một mạch**. Toàn ví von, không lệnh | 45 phút |
| **2** | ⚙️ **NÓ CHẠY THẾ NÀO** | Cơ chế thật + tên gọi kỹ thuật | Đọc kỹ, đối chiếu sơ đồ | 1.5 giờ |
| **3** | 🧪 **NHÌN THẤY NÓ** | [LAB](Module-01-LAB.md) — gõ tay | Vừa đọc vừa gõ | 3 giờ |
| **4** | 🏗️ **TOPO & KIẾN TRÚC** | *"Nó nằm ở đâu trong mạng thật?"* | Đọc + **vẽ lại trên giấy** | 45 phút |
| **📎** | **PHỤ LỤC** | Bảng, bẫy đề, quiz, thuật ngữ | 🔴 **KHÔNG đọc lần đầu** — chỉ Ctrl+F | — |

**Ba mức ưu tiên nếu thiếu thời gian:**

| Mức | Làm gì |
|---|---|
| 🔴 **Tối thiểu** | Phần 1 (toàn bộ) → Phần 2 mục **3.1, 3.2, 3.3** → [LAB](Module-01-LAB.md) **bước 2, 4, 5** |
| 🟡 **Nên có** | Thêm Phần 2 mục **3.4, 3.6** → LAB **bước 6, 7** → **Phần 4** |
| ⚪ **Khi rảnh** | §3.5 (dCEF) · §4.1 (phần cứng) · §4.2 (multilayer switch) |

> **Nếu bạn chỉ có 1 buổi:** đọc trọn **Phần 1**, rồi làm thẳng **LAB bước 2, 4, 5**.
> Phần 1 cho bạn hình dung, ba bước lab đó cho bạn bằng chứng. Đủ để không quên.

---

## ✅ 1. Chuẩn bị trước khi học

| Cần có | Chi tiết |
|---|---|
| **Kiến thức trước** | Module-P0 §2.5 (router chọn đường thế nào) và §2.6 (OSPF cơ bản). Bạn phải đọc được `show ip route` |
| **Lab** | 👉 **[Module-01-LAB.md](Module-01-LAB.md)** — 3 router OSPF area 0. **Config đầy đủ nằm ngay trong file LAB**, dán là chạy (dùng lại được LAB P0-5 nếu còn) |
| **RAM** | 3× vIOS = **1.5 GB** ✅ nhẹ |
| **Thời lượng** | 10 giờ: 3h lý thuyết · 4h lab · 3h ôn + quiz |

> 💡 **Vì sao module này quan trọng hơn vẻ ngoài của nó:** đề ENCOR hỏi ít câu về CEF,
> nhưng **hiểu CEF là điều kiện để hiểu vì sao `debug ip packet` không thấy gì**,
> vì sao TCAM hết chỗ thì ACL không apply được, và vì sao switch L3 nhanh hơn router.
> Đây là module "ít điểm nhưng mở khóa nhiều thứ".

---

## 🧠 PHẦN 1 — CÁI ĐÓ LÀ GÌ

> **Đọc phần này TRƯỚC, và đọc một mạch.** Ở đây không có bảng tra cứu, không có lệnh —
> chỉ có ví von đời thường để bạn bật ra được *"à, ra nó là thế"*.
>
> **Cách tự kiểm tra:** đọc xong mỗi mục, gấp tài liệu lại và **giải thích cho đồng nghiệp trong 3 câu**.
> Nói được thì sang mục sau. Không nói được thì đọc lại mục đó — đừng đi tiếp.

### 2.1 Ba plane như một nhà hàng

| Plane | Trong nhà hàng | Đặc điểm |
|---|---|---|
| **Data plane** | **Bồi bàn** — chỉ việc mang đồ từ bếp ra bàn, cực nhanh, không suy nghĩ | Làm 1 việc duy nhất, làm cực nhanh |
| **Control plane** | **Quản lý** — quyết định bàn nào ngồi đâu, viết sơ đồ bàn cho bồi bàn | Suy nghĩ chậm, nhưng bồi bàn phải theo |
| **Management plane** | **Chủ nhà hàng** gọi điện hỏi tình hình | Không tham gia phục vụ |

**Punt** = bồi bàn gặp khách hỏi câu khó ("cho tôi món không có trong menu") → phải **gọi quản lý ra**.
Nếu 100 khách cùng hỏi câu khó → quản lý quá tải → **cả nhà hàng đứng**.

🧠 **Một câu để nhớ:** *Punt nhiều = CPU cao = thiết bị chậm. Đó là lý do CoPP tồn tại.*

### 2.2 Process switching vs CEF như đi giao hàng

**Process switching** — người giao hàng mỗi lần giao đều **mở Google Maps tra lại từ đầu**:
- Gói 1: tra đường (2 phút) → giao
- Gói 2 cùng địa chỉ: **tra lại từ đầu** (2 phút) → giao
- 1000 gói = 2000 phút tra đường

**Fast switching** — tra 1 lần rồi **ghi vào sổ tay**:
- Gói 1: tra đường (2 phút) → **ghi vào sổ** → giao
- Gói 2–1000: xem sổ (2 giây) → giao
- ⚠️ Nhưng gói 1 vẫn phải "hy sinh" 2 phút. Và địa chỉ mới nào cũng phải hy sinh 1 gói.

**CEF** — **in sẵn cả bản đồ khu vực trước khi đi làm**:
- Sáng ra: nhận bản đồ (FIB) đã in sẵn từ phòng kế hoạch (RIB)
- Gói 1 đến gói 1000: nhìn bản đồ (2 giây) → giao
- ⭐ **Không có gói nào bị hy sinh**

🧠 **Một câu để nhớ:** *Fast switching học **từ traffic** (traffic-driven). CEF học **từ bảng route**
(topology-driven). Vì thế CEF không cần gói đầu tiên làm vật thí nghiệm.*

### 2.3 FIB và Adjacency Table như tra bưu phẩm

Bạn cần gửi thư tới `10.1.1.5`:

| Bảng | Câu hỏi nó trả lời | Kết quả |
|---|---|---|
| **FIB** | *"Thư này đi hướng nào?"* | "Đưa cho anh `10.0.0.2`" |
| **Adjacency table** | *"Anh `10.0.0.2` mặt mũi thế nào (MAC gì), tôi đưa qua cửa nào?"* | "MAC `aa:bb:cc:00:00:02`, cửa `Gi0/0`" |

⭐ Điểm hay của CEF: **hai bảng này được nối sẵn bằng con trỏ**. Tra FIB một lần là ra luôn cả
next-hop **và** thông tin L2. Không phải tra 2 lần rời rạc.

🧠 **Một câu để nhớ:** *FIB nói "đi đâu", Adjacency nói "dán nhãn gì và ra cửa nào". Một lần tra, đủ cả hai.*

### 2.4 TCAM: vì sao cần "don't care"

Bạn là bảo vệ, có danh sách được vào:

**CAM (chỉ khớp chính xác)** — danh sách phải liệt kê **từng người**:
```
Nguyễn Văn A  → cho vào
Nguyễn Văn B  → cho vào
...  (phải ghi 254 dòng cho 1 subnet /24!)
```

**TCAM (có "don't care")** — ghi **một dòng có mask**:
```
Value:  "Ai làm ở phòng 192.168.1.*"
Mask:   phần * = don't care
Result: cho vào
→ 1 dòng thay 254 dòng
```

🧠 **Một câu để nhớ:** *TCAM = CAM + khả năng nói "phần này tôi không quan tâm".
Đó là lý do ACL và bảng route phải dùng TCAM, còn MAC table thì CAM là đủ.*

### 2.5 Vì sao TCAM luôn thiếu

TCAM khớp **song song toàn bộ bảng trong 1 chu kỳ clock** — nghĩa là mỗi entry có mạch so sánh riêng.
Điều đó khiến TCAM:
- **đắt** (nhiều transistor/bit)
- **tốn điện & nóng**
- → nhà sản xuất chỉ cho một lượng có hạn

🧠 **Một câu để nhớ:** *TCAM nhanh vì so sánh song song, nhưng chính vì song song nên nó đắt và ít.
Vì ít nên phải chia phần (SDM template), và vì chia phần nên có thể hết chỗ.*

---

## ⚙️ PHẦN 2 — NÓ CHẠY THẾ NÀO

> Giờ bạn đã có **hình dung** rồi. Phần này lắp **tên gọi kỹ thuật và cơ chế thật** vào hình dung đó.
>
> Mỗi mục ở đây nối thẳng với một mục ở Phần 1:
> **2.1 nhà hàng → 3.1 ba plane** · **2.2 giao hàng → 3.2 ba phương pháp** ·
> **2.3 bưu phẩm → 3.3 RIB/FIB** · **2.4–2.5 bảo vệ → 3.6 CAM/TCAM**
>
> Bảng trong phần này là **để tra cứu về sau**, không phải để học thuộc ngay.

### 3.1 Ba mặt phẳng (plane) của thiết bị mạng

Đây là mô hình tư duy quan trọng nhất của module này. Mọi thứ trong 17 tuần tới đều xếp vào 1 trong 3 ô này.

| Plane | Nhiệm vụ | Chạy ở đâu | Ví dụ cụ thể |
|---|---|---|---|
| **Data plane**<br>*(Forwarding plane)* | **Chuyển gói đi** — nhận vào port này, đẩy ra port kia | ⭐ **ASIC / hardware** (nhanh) | Forward gói IP, switch frame, áp ACL, đánh dấu QoS, NAT (hardware) |
| **Control plane** | **Xây bảng** cho data plane dùng | **CPU** (chậm hơn) | OSPF, BGP, EIGRP, STP, ARP, CDP/LLDP, HSRP, LACP |
| **Management plane** | **Cho người/hệ thống quản lý** thiết bị | **CPU** | SSH, Telnet, SNMP, NETCONF/RESTCONF, Syslog, NTP, HTTP |

```
┌─────────────────────────────────────────────────────────────┐
│  MANAGEMENT PLANE   (SSH · SNMP · NETCONF · Syslog)         │
│         ↕ người quản trị                                     │
├─────────────────────────────────────────────────────────────┤
│  CONTROL PLANE      (OSPF · BGP · STP · ARP)      ← CPU     │
│         │ xây bảng                                           │
│         ▼  RIB → FIB · ARP → Adjacency Table                │
├─────────────────────────────────────────────────────────────┤
│  DATA PLANE         (forward gói)                 ← ASIC    │
│    Gói vào ──▶ tra FIB ──▶ ghi lại header ──▶ Gói ra         │
└─────────────────────────────────────────────────────────────┘
```

**Vì sao chia 3 plane — 3 lý do thực tế:**

| Lý do | Giải thích |
|---|---|
| **Tốc độ** | Data plane chạy hardware, xử lý hàng triệu gói/giây. Control plane chạy CPU, chỉ cần xử lý vài trăm gói giao thức/giây |
| **Bảo vệ** | Control plane bị flood (tấn công) → thiết bị **mất neighbor OSPF, mất STP** → cả mạng sập. Đó là lý do có **CoPP** (Module-10) |
| **Độc lập** | Control plane restart (VD OSPF reload) mà data plane vẫn forward tiếp → gọi là **NSF/graceful restart** |

> ⭐ **Thuật ngữ phải nhớ: PUNT.** Khi data plane (ASIC) gặp gói **không xử lý nổi**,
> nó "**punt**" gói đó lên CPU. Ví dụ: gói có IP Options, gói cần fragment, gói gửi **tới chính router**
> (OSPF hello, SSH), gói cần ARP mà chưa có MAC.
>
> Punt quá nhiều = **CPU 100%** = thiết bị chậm/mất neighbor. Đây là nguyên nhân số 1 của sự cố
> "switch chạy chậm bất thường" ở production.

---

### 3.2 Ba phương pháp chuyển mạch (switching method)

Đây là phần đề ENCOR hỏi trực tiếp.

| # | Phương pháp | Cách hoạt động | Tốc độ | Trạng thái |
|:---:|---|---|:---:|---|
| 1 | **Process switching** | CPU xét **từng gói một**: tra RIB, tính lại header, forward | 🐌 Rất chậm | Chỉ dùng cho gói đặc biệt |
| 2 | **Fast switching**<br>*(route cache)* | Gói **đầu tiên** process-switch, kết quả cache lại. Gói sau dùng cache | 🚶 Nhanh hơn | **Đã bỏ** (deprecated) |
| 3 | **CEF**<br>*(Cisco Express Forwarding)* | ⭐ Xây bảng FIB **trước**, mọi gói đều đi hardware. Không có gói nào bị "hy sinh" | 🚀 Rất nhanh | **Mặc định bật** trên mọi IOS hiện đại |

#### So sánh 3 phương pháp — bảng đề hay hỏi

| | Process | Fast switching | **CEF** |
|---|---|---|---|
| Kiểu hoạt động | Per-packet | **Traffic-driven** (gói đầu tạo cache) | ⭐ **Topology-driven** (bảng xây trước) |
| Gói đầu tiên | Chậm | Chậm | **Nhanh như mọi gói khác** |
| Nơi xử lý | CPU | CPU + cache | ASIC / hardware |
| Bảng dùng | RIB (routing table) | Route cache | **FIB + Adjacency table** |
| Có gánh nặng CPU? | Rất cao | Trung bình | Rất thấp |
| Load-balance | Được | Kém | ⭐ Tốt (per-destination / per-packet) |
| Trạng thái | Fallback cho gói đặc biệt | Đã loại bỏ | **Mặc định** |

> ⭐ **Điểm cốt lõi phải nhớ:** *Fast switching là **traffic-driven** (phải có traffic mới có cache).
> CEF là **topology-driven** (bảng dựng sẵn từ bảng route, không cần chờ traffic).*
> Đề ENCOR hỏi đúng cặp từ này.

#### Khi nào gói vẫn bị process-switch (dù CEF đã bật)

| Loại gói | Vì sao phải lên CPU |
|---|---|
| Gói **gửi tới chính router** | OSPF hello, BGP update, SSH vào router, ping tới IP router |
| Gói có **IP Options** | ASIC không xử lý option header |
| Gói cần **fragment** | Gói lớn hơn MTU đường ra |
| Gói cần **ICMP unreachable/TTL exceeded** | Router phải tự sinh gói mới |
| Gói tới subnet connected mà **chưa có ARP** | Cần "glean" → gửi ARP request |
| Traffic bị **encrypt/tunnel** (tùy platform) | Một số platform xử lý ở software |

---

### 3.3 CEF — RIB, FIB và Adjacency Table

Đây là phần quan trọng nhất module này. **Nhớ 3 bảng và quan hệ giữa chúng.**

```
   CONTROL PLANE                                DATA PLANE
   ─────────────                                ──────────
   
   OSPF/BGP/Static ──┐
                     ├──▶  RIB  ────copy&tối ưu───▶  FIB   ──┐
   Connected ────────┘   (Routing              (Forwarding    │
                          Information            Information  │  1 lần tra
                          Base)                 Base)         │  → có đủ
                                                              ├──▶ Forward gói
   ARP / neighbor ──────▶ ARP table ──────▶ Adjacency Table ──┘
                                            (thông tin ghi lại
                                             header L2: MAC đích)
```

| Bảng | Tên đầy đủ | Chứa gì | Xem bằng lệnh |
|---|---|---|---|
| **RIB** | Routing Information Base | Bảng định tuyến "của con người". Có AD, metric, uptime, protocol | `show ip route` |
| **FIB** | Forwarding Information Base | ⭐ Bản sao RIB **đã tối ưu để tra cứu nhanh** (cấu trúc mtrie). Chỉ giữ **đường tốt nhất** | `show ip cef` |
| **Adjacency Table** | — | Thông tin **L2 rewrite**: next-hop nào thì dán MAC đích nào | `show adjacency detail` |

#### RIB vs FIB — bảng so sánh (đề hỏi trực tiếp mục 1.7)

| | **RIB** | **FIB** |
|---|---|---|
| Thuộc plane | Control plane | ⭐ **Data plane** |
| Ai đọc | CPU / process routing | ASIC / hardware |
| Chứa | **Mọi** route ứng viên + AD + metric + protocol + uptime | **Chỉ** route tốt nhất + next-hop pointer |
| Cấu trúc | Bảng để người đọc | **mtrie** — tối ưu cho longest-prefix match cực nhanh |
| Có AD/metric? | ✅ Có | ❌ Không cần (đã chọn xong rồi) |
| Lệnh | `show ip route` | `show ip cef` |

🧠 **Một câu để nhớ:** *RIB là **sổ ghi chép của người quản trị** (có đủ lý do, ghi chú, ngày tháng).
FIB là **tờ giấy nhắc việc dán trên tường** (chỉ có kết quả, để đọc trong 1 giây).*

#### Các loại Adjacency — bảng đề hay hỏi

| Loại adjacency | Nghĩa | Khi nào xuất hiện |
|---|---|---|
| **Cached / Complete** | Đã có đủ MAC đích → forward ngay | Bình thường |
| ⭐ **Glean** | "Tôi biết subnet này cắm trực tiếp, nhưng **chưa biết MAC của host đó**" → punt lên CPU để **gửi ARP** | Gói đầu tiên tới 1 host trong subnet connected |
| **Punt** | Gói cần xử lý ở tầng cao hơn → đẩy lên CPU | IP Options, cần fragment |
| **Drop** | Bỏ gói | Không có route, hoặc bị ACL |
| **Discard** | Bỏ gói (khác drop ở cách đếm counter) | |
| **Null** | Gửi vào `Null0` | Route trỏ null0 |
| **No route** | Không có entry trong FIB | Gói bị drop |

> ⭐ **Glean adjacency giải thích một hiện tượng bạn đã gặp ở LAB-00:** ping lần đầu mất 1 gói.
> Gói đầu tiên gặp glean adjacency → punt lên CPU → CPU gửi ARP → chờ reply → gói bị drop.
> Từ gói thứ 2, adjacency đã complete → đi hardware → `!!!!`.
>
> **Đây chính là câu trả lời cho câu hỏi "vì sao ping đầu mất 1 gói" ở mức CCNP.**

---

### 3.4 CEF load-balancing & Polarization

Khi có **nhiều đường cùng cost** (ECMP — bạn đã thấy ở LAB P0-5), CEF phải chọn đường cho từng flow.

| Chế độ | Cách chọn | Ưu | Nhược |
|---|---|---|---|
| ⭐ **Per-destination** *(mặc định)* | Hash **(src IP, dst IP)** → chọn đường | Gói cùng 1 flow luôn đi cùng đường → **không bị out-of-order** | 1 flow lớn không chia được qua 2 link |
| **Per-packet** | Xoay vòng từng gói | Chia tải đều nhất | ⚠️ Gói **đến sai thứ tự** → hỏng VoIP, TCP giảm hiệu năng |

```
! Xem đang dùng chế độ nào
show cef interface GigabitEthernet0/0 | include load

! Đổi chế độ (per-interface)
interface GigabitEthernet0/0
 ip load-sharing per-packet          ! ⚠️ hầu như không dùng ở production
 ip load-sharing per-destination     ! mặc định
```

#### ⭐ CEF Polarization — khái niệm đề hay hỏi

**Vấn đề:** nếu nhiều tầng switch trong mạng dùng **cùng một thuật toán hash** với **cùng seed**,
thì một flow đi qua tầng 1 chọn link A, tới tầng 2 lại chọn link A → **tất cả traffic dồn vào một nhánh**,
nhánh còn lại rỗng. Gọi là **CEF polarization** (phân cực).

```
        ┌── Link A ──┐        ┌── Link A ──┐     ← tất cả traffic dồn đây
  SW1 ──┤            ├── SW2 ─┤            ├── SW3
        └── Link B ──┘        └── Link B ──┘     ← rỗng
        (cùng hash → cùng chọn A)
```

**Cách sửa:** đặt **ID khác nhau** cho thuật toán hash ở từng tầng:

```
ip cef load-sharing algorithm universal 1234ABCD     ! tầng access
ip cef load-sharing algorithm universal 5678EF00     ! tầng distribution — ID KHÁC
```

| Thuật toán | Ghi chú |
|---|---|
| `original` | Cũ, dễ bị polarization |
| ⭐ `universal` *(mặc định)* | Có **unique ID** để phá polarization |
| `tunnel` | Tối ưu cho traffic có ít cặp src/dst (VD tunnel) |
| `include-ports` | Hash cả **port** L4 → phân tán tốt hơn (tùy platform) |

---

### 3.5 dCEF — Distributed CEF

| | **CEF tập trung** | **dCEF (distributed)** |
|---|---|---|
| FIB nằm ở | Route Processor / Supervisor | ⭐ **Bản sao FIB trên MỖI line card** |
| Ai quyết định forward | Supervisor | **Line card tự quyết** |
| Traffic giữa 2 port cùng line card | Phải qua supervisor | ⭐ Không cần đi qua supervisor |
| Hiệu năng | Tốt | Rất cao — scale theo số line card |
| Thiết bị | Switch/router nhỏ-vừa | Chassis lớn (Catalyst 9600, ASR) |

> 💡 Ý tưởng của dCEF: thay vì 1 người gác cổng duy nhất, **mỗi cửa có một người gác riêng
> cầm bản sao cùng một danh sách**.

---

### 3.6 CAM vs TCAM — bit "don't care"

| | **CAM** (Content Addressable Memory) | **TCAM** (Ternary CAM) |
|---|---|---|
| Trạng thái mỗi bit | **2 trạng thái**: `0`, `1` | ⭐ **3 trạng thái**: `0`, `1`, **`X` (don't care)** |
| Kiểu khớp | **Exact match** (khớp chính xác) | ⭐ **Khớp có mask** (khớp một phần) |
| Dùng cho | ⭐ **MAC address table** | ⭐ **ACL · QoS · route lookup (FIB) · NAT · PBR** |
| Input → Output | MAC → port | Gói → permit/deny, hoặc → next-hop |
| Số lần tra | **1 chu kỳ** (song song toàn bảng) | 1 chu kỳ |
| Giá / điện | Đắt | **Rất đắt, tốn điện** → nên dung lượng có hạn |

#### Nhìn hai loại bộ nhớ cạnh nhau

```
 ══════════ CAM — chỉ trả lời "CÓ / KHÔNG" ══════════

   Hỏi:  "MAC aabb.cc11.2233 ở cổng nào?"
                    │
                    ▼
        ┌───────────────────────────┐
        │ aabb.cc11.2233  →  Gi1/0/5│ ◀── khớp ĐÚNG TỪNG BIT
        │ aabb.cc11.2299  →  Gi1/0/7│
        │ 0050.56aa.0001  →  Gi1/0/9│
        └───────────────────────────┘
                    │
                    ▼   Gi1/0/5
   ✅ Hợp với MAC: không có chuyện "MAC gần giống"


 ══════════ TCAM — trả lời được "MỘT DẢI" ══════════

   Hỏi:  "Gói đi tới 192.168.1.99 — permit hay deny?"
                    │
                    ▼
        ┌──────────────────────────────────────────────┐
        │ Value  : 1100 0000 . 1010 1000 . 0000 0001 . 0000 0000 │
        │ Mask   : 1111 1111 . 1111 1111 . 1111 1111 . X X X X X │
        │                                              └────┬────┘
        │                                    8 bit cuối = "KHÔNG QUAN TÂM"
        │ Result : PERMIT                                   │
        └──────────────────────────────────────────────┘
                    │
                    ▼
   ✅ Khớp CẢ 192.168.1.1, .99, .254 … chỉ bằng MỘT entry

        Nếu dùng CAM thì phải tạo 254 entry riêng cho 254 host!
```

> **Đó chính là chữ "Ternary" (tam phân):** mỗi bit có **3** trạng thái `0` / `1` / `X`,
> thay vì 2 như bộ nhớ thường. Cái giá phải trả: ⭐ **TCAM rất đắt và tốn điện**,
> nên dung lượng luôn có hạn — dẫn thẳng tới vấn đề "hết TCAM" ở mục dưới.

⭐ **Cấu trúc một entry TCAM gọi là VMR: Value – Mask – Result.**

#### Hết TCAM thì sao? (chuyện xảy ra thật ở production)

| Triệu chứng | Nguyên nhân |
|---|---|
| Apply ACL báo lỗi `TCAM capacity exceeded` | Hết chỗ TCAM |
| ACL apply được nhưng **traffic bị process-switch** → CPU 100% | ACL không vào được TCAM → phải xử lý software |
| Route table lớn không vào hardware | FIB TCAM đầy |

**Kiểm tra:**
```
show platform tcam utilization              ! ⚠️ lệnh khác nhau theo platform
show platform hardware fed switch active fwd-asic resource tcam utilization    ! Cat9k
show sdm prefer                             ! xem template đang dùng
```

#### SDM Template — chia phần TCAM

**SDM (Switching Database Manager)** quyết định TCAM được chia cho tính năng nào bao nhiêu.

| Template | Ưu tiên cho | Dùng khi |
|---|---|---|
| `default` | Cân bằng | Mặc định |
| `vlan` | MAC table lớn, **không route** | Switch access thuần L2 |
| ⭐ `routing` | **Route/FIB nhiều** | Switch L3 ở distribution/core |
| `advanced` | Cân bằng cho tính năng mới (Cat9k) | Mặc định trên Cat9k |

```
show sdm prefer                      ! xem hiện tại
configure terminal
 sdm prefer routing                  ! đổi template
end
write memory
reload                               ! ⚠️ PHẢI RELOAD mới có tác dụng
```

> ⭐ **Bẫy đề ENCOR:** đổi SDM template **bắt buộc reload** mới áp dụng. Đề hay hỏi "sau khi gõ
> `sdm prefer routing`, cần làm gì tiếp?" → **reload**.

---

## 🧪 PHẦN 3 — NHÌN THẤY NÓ

> ### 👉 **[Mở LAB 01 — Nhìn thấy CEF hoạt động](Module-01-LAB.md)**
>
> File LAB có **config đầy đủ dán là chạy**, 7 bước theo nhịp cố định
> *Mục tiêu → Gõ gì → Thấy gì → Vì sao → Checkpoint*.

**LAB trả lời 5 câu hỏi mà lý thuyết ở trên chỉ mô tả bằng chữ:**

| # | Câu hỏi | Ví von ở Phần 1 | Cơ chế ở Phần 2 |
|:---:|---|---|---|
| 1 | RIB và FIB khác nhau chỗ nào? | §2.3 bưu phẩm | §3.3 |
| 2 | Vì sao ping lần đầu mất đúng 1 gói (`.!!!!`)? | §2.3 bưu phẩm | §3.3 (glean) |
| 3 | Vì sao `debug ip packet` không thấy traffic người dùng? | §2.2 giao hàng | §3.2 + §3.3 |
| 4 | Hai đường bằng nhau, flow của tôi đi đường nào? | — | §3.4 |
| 5 | CPU cao — lỗi ở data plane hay control plane? | §2.1 nhà hàng | §3.1 (punt) |

> ⚠️ **Đọc lý thuyết mà không làm LAB thì coi như chưa học module này.**
> Ba bước quan trọng nhất là **Bước 2** (RIB vs FIB), **Bước 4** (glean) và **Bước 5**
> (`debug ip packet` im lặng) — chúng biến ba khái niệm trừu tượng thành thứ nhìn thấy được.

---

## 🏗️ PHẦN 4 — TOPO & KIẾN TRÚC

> Bạn đã biết **nó là gì** (Phần 1), **chạy thế nào** (Phần 2), và **nhìn thấy nó** (Phần 3).
> Phần này trả lời câu cuối: ⭐ **"Nó nằm ở đâu trong mạng thật, và thiết kế sai thì hỏng ra sao?"**

### 4.1 Bản đồ: CEF và TCAM nằm ở đâu trong một campus thật

```
                          ┌──────────────┐
                 INTERNET │   Firewall   │
                     ▲    └──────┬───────┘
                     │           │
              ┌──────┴───────────┴──────┐
     CORE     │   Core SW (L3)          │   TCAM: bảng FIB LỚN (nhiều route)
              │   Cat9500 / 9600        │   ACL: gần như KHÔNG có (giữ cho nhanh)
              └────┬───────────────┬────┘   CEF: bắt buộc, ECMP nhiều đường
                   │               │
        ┌──────────┴───┐     ┌─────┴────────┐
DISTRO  │ Dist SW (L3) │     │ Dist SW (L3) │  TCAM: CHIA ĐÔI gánh nặng —
        │  Cat9400     │     │  Cat9400     │     vừa FIB (route) vừa ACL (policy)
        └──┬────────┬──┘     └──────────────┘  ĐÂY LÀ CHỖ TCAM HAY HẾT NHẤT
           │        │
     ┌─────┴──┐  ┌──┴─────┐
ACCESS│Acc SW │  │ Acc SW │    CAM: bảng MAC lớn (nhiều máy cắm vào)
     │Cat9200│  │Cat9200 │    TCAM: ít route, nhưng nhiều ACL 802.1X/dACL
     └───┬───┘  └────┬───┘    SDM template: ưu tiên MAC, không ưu tiên route
         │           │
       PC/IP Phone/AP
```

### 4.2 Ba quyết định thiết kế xuất phát từ Module này

| Quyết định | Vì sao liên quan tới Module-01 | Sai thì hỏng thế nào |
|---|---|---|
| **Chọn SDM template cho từng lớp** | TCAM có hạn và **phải chia phần trước** *(§3.6)* | Access switch dùng template "routing" → hết chỗ MAC → **flood toàn mạng** |
| **Đặt ACL ở lớp nào** | ACL ăn TCAM. Core cần TCAM cho **FIB**, không phải ACL | Nhồi ACL vào core → **hết TCAM** → ACL rơi xuống xử lý bằng CPU → **CPU 100%** |
| **Số đường ECMP ở core** | Mỗi đường ECMP nhân thêm entry adjacency *(§3.4)* | Quá nhiều đường + hash giống nhau mọi tầng → **CEF polarization**, một nhánh nghẽn, nhánh kia rỗng |

> ⭐ **Đây là lý do Module-01 "ít điểm nhưng mở khóa nhiều thứ":** ba quyết định trên bạn sẽ
> gặp lại ở **Module-09 (thiết kế campus)** và **Module-10 (đặt ACL/CoPP ở đâu)**.

### 4.3 Vẽ lại để nhớ

> **Bài tập 10 phút, làm trên giấy — đừng bỏ qua.**
>
> 1. Vẽ lại sơ đồ 3 lớp ở trên **không nhìn tài liệu**
> 2. Với mỗi lớp, ghi: **CAM dùng cho gì · TCAM dùng cho gì · SDM nên ưu tiên gì**
> 3. Khoanh tròn lớp mà **TCAM dễ hết nhất** và viết một câu vì sao

<details>
<summary>Đáp án</summary>

**Lớp Distribution** dễ hết TCAM nhất — vì nó là lớp **duy nhất phải gánh cả hai**:
vừa giữ bảng **FIB** (nó là ranh giới L3, có nhiều route), vừa chứa **ACL/policy**
(nó là nơi đặt chính sách — xem Module-09 §2.1).

Core chỉ cần FIB (không ACL). Access chỉ cần CAM lớn (ít route).

</details>

---

### 4.4 Kiến trúc phần cứng thiết bị

| Thành phần | Vai trò | Thuộc plane |
|---|---|---|
| **Supervisor Engine / Route Processor (RP)** | "Bộ não" — chạy IOS, control plane, management plane | Control + Management |
| **Line card / Module** | Chứa port + **ASIC/NPU** để forward | Data plane |
| **ASIC** (Application-Specific Integrated Circuit) | Chip chuyên dụng forward gói, cực nhanh, **không lập trình lại được** | Data plane |
| **NPU** (Network Processing Unit) | Như ASIC nhưng **lập trình được** → thêm tính năng mới bằng software | Data plane |
| **Backplane / Switch Fabric** | Đường nối giữa các line card. Băng thông tổng của switch | Data plane |
| **TCAM / CAM** | Bộ nhớ tra cứu siêu nhanh | Data plane |

| Kiểu forwarding | Quyết định ở đâu | Thiết bị |
|---|---|---|
| **Centralized** | Supervisor quyết định cho mọi port | Switch nhỏ/vừa (Cat 9200/9300) |
| **Distributed** | Mỗi line card tự quyết (dCEF) | Chassis lớn (Cat 9600, ASR 9000) |

---

### 4.5 Multilayer Switch — vì sao switch L3 nhanh hơn router

| | **Router truyền thống** | **Multilayer Switch (L3 switch)** |
|---|---|---|
| Forward bằng | CPU + CEF software (hoặc NPU) | ⭐ **ASIC — hardware thuần** |
| Tốc độ | Gbps | **Multi-Terabit** |
| Mạnh về | Tính năng phức tạp: NAT, VPN, QoS sâu, BGP full table | Forward L2/L3 cực nhanh, số port lớn |
| Interface | Ít port, nhiều loại WAN | Nhiều port Ethernet |
| Dùng ở | Biên WAN / Internet edge | ⭐ Campus: access / distribution / core |

**Hai loại interface L3 trên switch:**

| Loại | Lệnh | Nghĩa |
|---|---|---|
| **SVI** | `interface Vlan10` + `ip address …` | Interface logic đại diện cho 1 VLAN. ⭐ Gateway của VLAN |
| **Routed port** | `interface Gi0/1` → `no switchport` → `ip address …` | Biến 1 port switch thành port router thuần, **không thuộc VLAN nào** |

⚠️ **Điều kiện bắt buộc:** phải có `ip routing` ở global config, nếu không SVI **không route**.

```
! Bật routing trên switch L3
configure terminal
 ip routing                          ! thiếu dòng này thì SVI vô dụng

! SVI
 interface Vlan10
  ip address 10.10.10.1 255.255.255.0
  no shutdown

! Routed port
 interface GigabitEthernet1/0/24
  no switchport                      ! biến thành port L3
  ip address 10.0.0.1 255.255.255.252
  no shutdown
end
```

---

### 4.6 Thực chiến đi làm

| Chủ đề | Thi dạy | Thực tế đi làm |
|---|---|---|
| **`debug ip packet`** | Có lệnh này | ⚠️ **Gần như vô dụng ở production**: (1) không thấy traffic CEF, (2) nếu thấy thì đang có vấn đề, (3) bật lên có thể làm CPU 100% → sự cố. Thay bằng **ERSPAN** (Module-11) hoặc **Embedded Packet Capture** |
| **Tắt CEF để debug** | Không dạy | ⛔ **TUYỆT ĐỐI KHÔNG** trên production. `no ip cef` trên router đang chạy = CPU 100% = mất OSPF/BGP neighbor = sự cố toàn mạng |
| **Embedded Packet Capture (EPC)** | Không có trong blueprint | ⭐ Công cụ thay thế `debug ip packet`, bắt gói **an toàn** ngay trên IOS: `monitor capture CAP interface Gi0/0 both` → `monitor capture CAP start` → `show monitor capture CAP buffer brief`. **Học cái này, dùng cả đời** |
| **CPU cao** | Không dạy cách tìm | ⭐ Quy trình thật: `show processes cpu sorted \| exclude 0.00` → đọc `%/%` → nếu **interrupt cao** thì `show interfaces \| include rate` tìm interface bị flood → kiểm tra CEF, TCAM, và có ai tắt hardware switching không |
| **TCAM** | Khái niệm | ⚠️ Sự cố thật: apply ACL lớn lên switch access → **hết TCAM** → ACL rơi xuống software → CPU 100%. Luôn kiểm tra `show platform tcam utilization` **trước** khi apply ACL lớn |
| **SDM template** | Có lệnh đổi | ⚠️ Đổi SDM = **reload** = **downtime**. Phải xin cửa sổ bảo trì. Và đổi rồi thì mọi switch cùng vai trò nên đổi giống nhau → ghi vào standard config |
| **CEF polarization** | Khái niệm | ⭐ Sự cố thật ở campus 3 tầng: 2 uplink 10G nhưng 1 cái 95%, cái kia 5%. Nguyên nhân: cùng hash ID ở nhiều tầng. Sửa bằng `ip cef load-sharing algorithm universal <ID khác nhau>` |
| **Per-packet load-sharing** | Có tùy chọn này | ⛔ Không dùng. Gói out-of-order → VoIP rè, TCP retransmit, firewall stateful drop gói |
| **`ip routing`** trên switch L3 | Có lệnh | ⚠️ Lỗi hay gặp nhất khi lên switch L3 mới: cấu hình SVI đủ hết nhưng **quên `ip routing`** → không route được, tìm cả tiếng |
| **Punt** | Không dạy sâu | ⭐ Cat9k có `show platform software fed switch active punt cause summary` — xem gói bị punt vì lý do gì. Cực hữu ích khi CPU cao |
| **Số port vs backplane** | Không dạy | Switch 48 port 1G = 48 Gbps nhưng backplane có thể chỉ 20 Gbps → **oversubscription**. Đọc datasheet trước khi mua, đừng tin số port |

---

# 📎 PHỤ LỤC — TRA CỨU

> 🔴 **KHÔNG đọc phần này ở lần học đầu tiên.**
>
> Đây là tài liệu **tra cứu**, không phải tài liệu học. Cách dùng đúng:
>
> | Khi nào | Mở mục nào |
> |---|---|
> | Đang lab mà lỗi | **Gỡ lỗi nhanh** (§7) |
> | Quên một lệnh | **Hộp lệnh** (§7.1) |
> | Tuần 20, đang ôn thi | **Bẫy đề** (§6) + **Quiz** (§8) |
> | Gặp từ tiếng Anh lạ | **Thuật ngữ** (§9) |
> | Học xong, muốn tự chấm | **Đúc kết + Tự chấm** (§10) |
>
> Đọc tuần tự phụ lục ở lần đầu là **cách nhanh nhất để kiệt sức và bỏ cuộc**.

---

## 🎓 6. BẪY TRONG ĐỀ ENCOR

| # | Bẫy | Sự thật |
|:---:|---|---|
| 1 | *"CEF là traffic-driven"* | ❌ **CEF là topology-driven.** Fast switching mới là traffic-driven |
| 2 | *"FIB giống RIB"* | ❌ FIB **không có** AD/metric/protocol/uptime, nhưng **có** `receive`/`drop`/`attached` |
| 3 | *"MAC table dùng TCAM"* | ❌ MAC table dùng **CAM** (exact match). TCAM cho ACL/QoS/FIB |
| 4 | *"TCAM có 2 trạng thái"* | ❌ **3 trạng thái**: 0, 1, **X (don't care)**. "Ternary" = tam phân |
| 5 | *"`debug ip packet` xem được traffic user"* | ❌ Chỉ thấy gói **process-switched**. Traffic transit qua CEF thì **không thấy** |
| 6 | *"Gói đầu tiên trong CEF bị chậm"* | ❌ Đó là **fast switching**. CEF dựng bảng trước nên gói đầu cũng nhanh |
| 7 | *"Đổi SDM template có tác dụng ngay"* | ❌ **Phải `reload`** |
| 8 | Adjacency `glean` nghĩa là gì | Subnet connected nhưng **chưa có MAC** → cần ARP. Giải thích `.!!!!` |
| 9 | *"Per-packet load-balancing tốt hơn vì chia đều"* | ⚠️ Chia đều hơn nhưng gây **out-of-order** → thực tế không dùng |
| 10 | CPU cao, interrupt % cao nghĩa là gì | Gói đang bị **punt/process-switch** → vấn đề **data plane** (không phải protocol) |
| 11 | *"dCEF nghĩa là CEF nhanh hơn"* | ❌ dCEF = **FIB được copy xuống từng line card**, line card tự quyết định forward |
| 12 | 3 plane — OSPF thuộc plane nào | **Control plane** (nó xây bảng). Forward gói OSPF hello tới router = punt lên CPU |
| 13 | SVI cấu hình đủ mà không route | Thiếu **`ip routing`** ở global config |
| 14 | *"Routed port thuộc VLAN nào?"* | ❌ **Không thuộc VLAN nào.** `no switchport` biến nó thành interface L3 thuần |
| 15 | Polarization sửa bằng gì | `ip cef load-sharing algorithm universal <ID>` với **ID khác nhau ở từng tầng** |

---

## 🐛 7. GỠ LỖI NHANH

### 7.1 Hộp lệnh vạn năng cho module này

```
! === CEF ===
show ip cef summary                          ! CEF bật chưa, bao nhiêu prefix
show ip cef                                  ! toàn bộ FIB
show ip cef <prefix> detail                  ! chi tiết 1 prefix
show ip cef exact-route <src> <dst>          ! flow này đi đường nào
show adjacency detail                        ! thông tin L2 rewrite
show cef interface Gi0/0                     ! CEF trên interface + load-sharing mode
show ip interface Gi0/0 | include CEF        ! CEF bật ở interface chưa

! === So sánh RIB vs FIB ===
show ip route <ip>                           ! RIB nói gì
show ip cef <ip>                             ! FIB nói gì
! → Nếu 2 cái LỆCH NHAU = có vấn đề nghiêm trọng (CEF inconsistency)

! === CPU / Punt ===
show processes cpu sorted | exclude 0.00     ! CPU đang làm gì
show processes cpu history                   ! đồ thị CPU theo thời gian
show interfaces | include rate|packets input ! interface nào đang bị dội

! === CAM / TCAM (switch) ===
show mac address-table                       ! CAM
show mac address-table count                 ! đếm entry
show sdm prefer                              ! template TCAM
show platform tcam utilization               ! ⚠️ lệnh khác nhau theo platform

! === Bắt gói AN TOÀN (thay debug ip packet) ===
monitor capture CAP interface Gi0/0 both
monitor capture CAP match ipv4 any any
monitor capture CAP start
show monitor capture CAP buffer brief
monitor capture CAP stop
no monitor capture CAP
```

### 7.2 Bảng lỗi: triệu chứng → nguyên nhân → cách sửa

| # | Triệu chứng | Nguyên nhân | Cách sửa |
|:---:|---|---|---|
| 1 | `debug ip packet` không thấy traffic transit | ✅ **Bình thường** — CEF forward ở hardware | Dùng **Embedded Packet Capture** hoặc ERSPAN |
| 2 | CPU 100%, **interrupt % cao** | Gói bị punt: CEF tắt, TCAM đầy, hoặc bị flood | `show ip cef summary` · `show platform tcam utilization` · tìm interface bị dội |
| 3 | CPU cao, **interrupt % thấp** | Control plane busy: OSPF/BGP hội tụ, hoặc quá nhiều neighbor | `show processes cpu sorted` xem process nào |
| 4 | `show ip route` **có** route, `show ip cef` **không có** | ⚠️ **CEF inconsistency** — lỗi nghiêm trọng | `clear ip route *` (⚠️ gây ngắt ngắn) · nặng thì reload · kiểm tra bug IOS version |
| 5 | Apply ACL báo `TCAM capacity exceeded` | Hết TCAM | Gộp/tối giản ACL · đổi SDM template · nâng cấp thiết bị |
| 6 | ACL apply được nhưng CPU tăng vọt | ACL không vào TCAM → xử lý software | Kiểm tra TCAM utilization · tối giản ACL |
| 7 | 2 uplink ECMP nhưng tải lệch nặng | **CEF polarization**, hoặc ít flow (elephant flow) | Đổi `load-sharing algorithm universal <ID>` khác ở mỗi tầng |
| 8 | Ping đầu luôn mất 1 gói | ✅ **Bình thường** — glean adjacency + ARP | Không phải lỗi |
| 9 | SVI có IP, interface up, nhưng không route giữa VLAN | Thiếu `ip routing` | `configure terminal` → `ip routing` |
| 10 | Sau `sdm prefer routing` mà TCAM không đổi | Chưa reload | `write memory` → `reload` |
| 11 | Traffic đi đường "vô lý" trong ECMP | Hash quyết định, không phải lỗi | `show ip cef exact-route <src> <dst>` để xác nhận |
| 12 | `show adjacency` thiếu entry cho next-hop | ARP chưa resolve | `ping <next-hop>` · `show arp` · kiểm tra L2 |

### 7.3 Quy trình xác định "gói bị forward ở hardware hay software"

```
1. show ip cef summary
      ↓ CEF enabled?
      ├─ Không → CEF bị tắt → BẬT LẠI (ip cef)
      └─ Có ↓
2. show ip interface Gi0/0 | include CEF
      ↓ CEF bật ở interface?
      ├─ Không → ip route-cache cef
      └─ Có ↓
3. show ip cef <đích>
      ↓ Có entry với next-hop rõ ràng?
      ├─ receive/attached/drop → gói sẽ bị punt lên CPU (đúng thiết kế)
      └─ Có next-hop ↓
4. show adjacency detail
      ↓ Có Encap length + MAC?
      ├─ Không (incomplete/glean) → thiếu ARP → gói punt để ARP
      └─ Có → ✅ Gói đi HARDWARE
5. show processes cpu sorted | exclude 0.00
      → interrupt % thấp = xác nhận không punt
```

---

## 📝 8. QUIZ TỰ KIỂM TRA

**Câu 1.** Phân biệt fast switching và CEF bằng đúng một cặp thuật ngữ.

<details><summary>Xem đáp án</summary>

**Fast switching = traffic-driven · CEF = topology-driven.**

- **Fast switching (traffic-driven):** phải có traffic đến trước, gói đầu tiên bị process-switch để
  tạo cache, gói sau mới nhanh.
- **CEF (topology-driven):** FIB được xây **từ bảng route** ngay khi bảng route thay đổi,
  không cần chờ traffic. Nên **không có gói nào bị hy sinh**.
</details>

---

**Câu 2.** Nêu 3 thông tin có trong RIB nhưng **không** có trong FIB, và 2 thông tin có trong FIB
nhưng **không** có trong RIB.

<details><summary>Xem đáp án</summary>

**Có trong RIB, không có trong FIB:**
1. **Administrative Distance** (`[110/...]`)
2. **Metric** (`[.../11]`)
3. **Uptime** (`00:12:03`)
4. (thêm) **Ký hiệu protocol** (`O`, `C`, `L`, `B`)

**Có trong FIB, không có trong RIB:**
1. **`receive`** — địa chỉ của chính router, gói tới thì punt lên CPU
2. **`drop`** — các dải không hợp lệ (`0.0.0.0/8`, `224.0.0.0/4`)
3. (thêm) **`attached`** cho subnet connected (glean)

**Lý do:** FIB chỉ giữ những gì ASIC cần để forward. AD/metric đã dùng xong ở control plane
để **chọn** route — chọn xong rồi thì data plane không cần biết nữa.
</details>

---

**Câu 3.** MAC address table dùng CAM hay TCAM? Vì sao? ACL dùng cái nào? Vì sao?

<details><summary>Xem đáp án</summary>

| | Bộ nhớ | Vì sao |
|---|---|---|
| **MAC address table** | **CAM** | MAC là **exact match** — phải khớp đúng từng bit. CAM (2 trạng thái: 0/1) là đủ, và rẻ hơn |
| **ACL** | **TCAM** | ACL cần **khớp một phần**: `permit 192.168.1.0/24` phải khớp mọi host trong subnet. Cần trạng thái thứ 3 **`X` (don't care)** để mask 8 bit cuối |

TCAM cũng dùng cho: **QoS classification, FIB (route lookup hardware), NAT, PBR**.

Cấu trúc TCAM entry: **VMR = Value – Mask – Result**.
</details>

---

**Câu 4.** Kỹ sư gõ `debug ip packet` trên router để xem traffic của user đi qua, nhưng không thấy
output nào. Router hoạt động bình thường, user vẫn truy cập được. Giải thích.

<details><summary>Xem đáp án</summary>

**Vì CEF đang forward traffic ở data plane (hardware/ASIC), CPU không hề nhìn thấy gói.**

`debug ip packet` là công cụ của control plane — nó chỉ hiện gói nào **được CPU xử lý**
(process-switched). Traffic transit bình thường đi qua FIB + adjacency table ở fast path,
**bỏ qua CPU hoàn toàn**.

**Đây là hành vi đúng, không phải lỗi.** Nếu `debug ip packet` mà **thấy** nhiều traffic transit
→ đó mới là dấu hiệu xấu (CEF bị tắt, hoặc gói đang bị punt).

**Cách xem traffic đúng:** **Embedded Packet Capture** (`monitor capture`), **ERSPAN/SPAN**,
hoặc **NetFlow** (Module-11).
</details>

---

**Câu 5.** `show ip cef 10.0.12.0/30` trả về `attached to GigabitEthernet0/0`. Loại adjacency này
gọi là gì và nó gây ra hiện tượng gì mà bạn thấy hằng ngày?

<details><summary>Xem đáp án</summary>

**Glean adjacency.**

Nghĩa: "subnet này cắm trực tiếp vào Gi0/0, tôi biết hướng, nhưng **chưa biết MAC** của host cụ thể".

**Hiện tượng gây ra:** ping lần đầu tới một host trong subnet đó **mất gói đầu tiên** (`.!!!!`).

Diễn biến:
1. Gói ICMP đầu tiên tra FIB → gặp glean → **punt lên CPU**
2. CPU gửi **ARP request**, gói ICMP bị **drop** (→ dấu `.`)
3. ARP reply về → adjacency chuyển sang **complete** (có Encap length 14 + MAC)
4. Gói 2–5 đi hardware bình thường (→ `!!!!`)
</details>

---

**Câu 6.** `show processes cpu` báo `CPU utilization for five seconds: 85%/78%`. Vấn đề nằm ở
control plane hay data plane? Bạn kiểm tra gì tiếp?

<details><summary>Xem đáp án</summary>

**Data plane.**

Đọc con số: `85%` = tổng, `78%` = **phần dành cho interrupt** (xử lý gói ở fast path).
Interrupt chiếm gần hết → CPU đang **forward gói**, nghĩa là gói bị **punt lên CPU** thay vì
đi hardware.

**Kiểm tra tiếp, theo thứ tự:**
1. `show ip cef summary` — CEF có bị tắt không?
2. `show ip interface <x> | include CEF` — CEF tắt ở interface nào?
3. `show platform tcam utilization` — TCAM đầy → ACL/route rơi xuống software?
4. `show interfaces | include rate` — interface nào đang bị flood (có thể đang bị tấn công)?
5. (Cat9k) `show platform software fed switch active punt cause summary` — punt vì lý do gì?

**Ngược lại:** nếu là `85%/2%` → interrupt thấp → vấn đề **control plane**
(OSPF/BGP đang hội tụ, quá nhiều neighbor, hoặc bug protocol).
</details>

---

**Câu 7.** Mạng campus có 2 uplink 10G từ access lên distribution, cấu hình ECMP. Đo thấy 1 link
chạy 92%, link kia 6%. Nêu 2 nguyên nhân có thể và cách xử lý.

<details><summary>Xem đáp án</summary>

**Nguyên nhân 1 — CEF polarization:** các tầng switch dùng **cùng thuật toán hash với cùng ID**,
nên flow chọn nhánh A ở tầng dưới thì lên tầng trên lại chọn nhánh A → dồn tải.

*Xử lý:* đặt **ID hash khác nhau ở từng tầng**:
```
! Tầng access
ip cef load-sharing algorithm universal 1111AAAA
! Tầng distribution — ID KHÁC
ip cef load-sharing algorithm universal 2222BBBB
```

**Nguyên nhân 2 — Elephant flow / quá ít flow:** load-balancing per-destination hash theo
cặp (src, dst). Nếu traffic chủ yếu là **1–2 flow rất lớn** (VD backup từ 1 server tới 1 storage),
thì hash chỉ ra 1 kết quả → **1 flow không thể chia qua 2 link**.

*Xử lý:* dùng thuật toán hash **có tính cả port L4** (`include-ports`, tùy platform),
hoặc thiết kế lại (LACP với hash L4, hoặc tách traffic backup ra đường riêng).

⚠️ **Không** chuyển sang `per-packet` — sẽ gây out-of-order.

*Cách xác nhận nguyên nhân:* `show ip cef exact-route <src> <dst>` với nhiều cặp thực tế →
xem có phải mọi cặp đều ra cùng interface.
</details>

---

**Câu 8.** Bạn gõ `sdm prefer routing` trên switch Catalyst. Cần làm gì để nó có tác dụng?
Và tác dụng đó là gì?

<details><summary>Xem đáp án</summary>

**Cần `reload`** (khởi động lại switch). Nên `write memory` trước.

**Tác dụng:** SDM (Switching Database Manager) **chia lại phần TCAM** giữa các tính năng.
Template `routing` **cấp nhiều TCAM hơn cho bảng route/FIB**, đổi lại giảm phần cho MAC table
và một số tính năng khác.

**Dùng khi nào:** switch làm vai trò **L3 ở distribution/core**, cần chứa nhiều route.
Ngược lại, switch access thuần L2 thì dùng template `vlan` (ưu tiên MAC table).

⚠️ **Thực tế:** đây là thao tác **gây downtime** (reload) → phải xin cửa sổ bảo trì,
và mọi switch cùng vai trò nên dùng cùng template.
</details>

---

**Câu 9.** Điền plane cho từng thứ: OSPF · forward gói IP · SNMP · áp ACL lên traffic đi qua ·
STP · NETCONF · ARP · đánh dấu DSCP.

<details><summary>Xem đáp án</summary>

| Thành phần | Plane |
|---|---|
| OSPF | **Control** (xây bảng route) |
| Forward gói IP | **Data** |
| SNMP | **Management** |
| Áp ACL lên traffic đi qua | **Data** (thực thi trong TCAM) |
| STP | **Control** (xây cây, quyết định port nào forward) |
| NETCONF | **Management** |
| ARP | **Control** (xây adjacency/ARP table) |
| Đánh dấu DSCP | **Data** |

💡 **Cách phân biệt nhanh:** *"Nó **xây bảng** hay nó **dùng bảng**?"*
Xây bảng → control. Dùng bảng để xử lý gói → data. Người/hệ thống nói chuyện với thiết bị → management.
</details>

---

**Câu 10.** `show ip route 10.5.5.0` có route, nhưng `show ip cef 10.5.5.0` không có entry tương ứng.
Đây là gì và nguy hiểm ra sao?

<details><summary>Xem đáp án</summary>

**CEF inconsistency** — RIB và FIB không đồng bộ. Đây là **lỗi nghiêm trọng**.

**Nguy hiểm:** control plane tin rằng có đường đi (RIB có route, `show ip route` đẹp,
OSPF neighbor Full), nhưng **data plane không biết forward đi đâu** → gói bị **drop âm thầm**.

Đây là loại sự cố khó tìm nhất: mọi lệnh `show` của protocol đều bình thường, mà traffic vẫn chết.

**Xử lý:**
1. `show ip cef inconsistency` (nếu platform hỗ trợ) để xác nhận
2. `clear ip route *` — buộc dựng lại FIB từ RIB (⚠️ gây ngắt ngắn)
3. Không hết → **reload** thiết bị trong cửa sổ bảo trì
4. Kiểm tra **bug IOS version** hiện tại trên Cisco Bug Search Tool → nâng cấp IOS

**Phòng ngừa:** đây thường là bug software → chạy IOS version đã được kiểm chứng (Cisco
"Suggested Release"), không chạy version quá mới.
</details>

---

## 📚 9. THUẬT NGỮ ANH–VIỆT

| Tiếng Anh | Tiếng Việt | Ghi chú |
|---|---|---|
| Data plane / Forwarding plane | Mặt phẳng dữ liệu | Nơi gói thật sự được chuyển đi. Chạy hardware |
| Control plane | Mặt phẳng điều khiển | Nơi xây bảng: OSPF, BGP, STP, ARP. Chạy CPU |
| Management plane | Mặt phẳng quản lý | SSH, SNMP, NETCONF, Syslog |
| **Punt** | Đẩy gói lên CPU | Gói hardware không xử lý nổi → nhờ CPU. Punt nhiều = CPU cao |
| Process switching | Chuyển mạch bằng tiến trình | CPU xử lý từng gói. Chậm nhất |
| Fast switching | Chuyển mạch nhanh (route cache) | **Traffic-driven**. Đã bị loại bỏ |
| **CEF** (Cisco Express Forwarding) | Chuyển tiếp nhanh của Cisco | **Topology-driven**. Mặc định |
| dCEF (Distributed CEF) | CEF phân tán | FIB copy xuống từng line card |
| **RIB** (Routing Information Base) | Cơ sở dữ liệu định tuyến | `show ip route`. Có AD, metric |
| **FIB** (Forwarding Information Base) | Cơ sở dữ liệu chuyển tiếp | `show ip cef`. Chỉ đường tốt nhất |
| Adjacency table | Bảng kề | Thông tin L2 rewrite (MAC đích) |
| **Glean adjacency** | Adjacency "gom" | Subnet connected nhưng chưa có MAC → cần ARP |
| L2 rewrite | Ghi lại header lớp 2 | Dán MAC nguồn/đích + EtherType vào gói |
| Encapsulation length | Độ dài đóng gói | Ethernet = 14 byte (6+6+2) |
| **CAM** (Content Addressable Memory) | Bộ nhớ định địa chỉ theo nội dung | 2 trạng thái. Dùng cho MAC table |
| **TCAM** (Ternary CAM) | CAM tam phân | **3 trạng thái (0/1/X)**. Dùng cho ACL/QoS/FIB |
| VMR (Value–Mask–Result) | Giá trị–Mặt nạ–Kết quả | Cấu trúc 1 entry TCAM |
| Don't care bit | Bit không quan tâm | Trạng thái `X` của TCAM |
| **SDM** (Switching Database Manager) | Bộ quản lý cơ sở dữ liệu chuyển mạch | Chia phần TCAM. Đổi template phải reload |
| ASIC | Chip chuyên dụng | Cực nhanh, không lập trình lại được |
| NPU (Network Processing Unit) | Bộ xử lý mạng | Như ASIC nhưng lập trình được |
| Supervisor Engine / Route Processor | Bộ điều khiển trung tâm | Chạy IOS, control plane |
| Line card | Thẻ đường truyền | Chứa port + ASIC |
| Backplane / Switch fabric | Đường trục nội bộ switch | Băng thông tổng |
| Oversubscription | Vượt mức thuê bao | Tổng băng thông port > backplane |
| **ECMP** (Equal-Cost Multi-Path) | Đa đường chi phí bằng nhau | Nhiều next-hop cùng cost |
| Per-destination load-sharing | Chia tải theo đích | Hash (src, dst). Mặc định. Giữ thứ tự gói |
| Per-packet load-sharing | Chia tải theo từng gói | Chia đều nhất nhưng **out-of-order** |
| **CEF polarization** | Phân cực CEF | Nhiều tầng cùng hash → dồn tải 1 nhánh |
| Elephant flow | Luồng "voi" | 1 flow rất lớn, không chia được qua nhiều link |
| Multilayer switch | Switch đa lớp | Vừa switch L2 vừa route L3 trong hardware |
| **SVI** (Switch Virtual Interface) | Interface ảo của VLAN | `interface Vlan10`. Gateway của VLAN |
| Routed port | Cổng định tuyến | `no switchport` → port L3 thuần, không thuộc VLAN |
| CEF inconsistency | RIB/FIB không đồng bộ | Lỗi nghiêm trọng: gói drop âm thầm |
| EPC (Embedded Packet Capture) | Bắt gói nhúng trong IOS | Công cụ an toàn thay `debug ip packet` |

---

## 🎯 10. ĐÚC KẾT MODULE-01

**3 điều rút ra:**

1. **Mọi thứ trong mạng đều xếp vào 1 trong 3 plane.** "Nó **xây bảng** hay **dùng bảng**?" —
   xây bảng thì control plane (CPU, chậm), dùng bảng để xử lý gói thì data plane (ASIC, nhanh).
   Khi thiết bị chậm bất thường, câu hỏi đầu tiên là: **có phải gói đang bị punt lên CPU?**

2. **RIB là sổ của người, FIB là giấy nhắc của máy.** FIB **bỏ** AD/metric/uptime (đã dùng xong),
   **thêm** `receive`/`drop`/`attached` (ASIC cần). Hai bảng lệch nhau = CEF inconsistency =
   gói drop âm thầm dù mọi `show` đều đẹp.

3. **`debug ip packet` không thấy traffic là ĐÚNG.** CEF forward ở hardware, CPU không nhìn thấy.
   Ở production dùng **Embedded Packet Capture** hoặc ERSPAN. Tắt CEF để debug là tự tạo sự cố.

🧠 **Một câu để nhớ:** *CEF dựng bản đồ trước khi ra đường (topology-driven), fast switching
vẽ bản đồ trong lúc đi (traffic-driven). Đó là toàn bộ khác biệt, và đó là lý do CEF thắng.*

---

### ✅ TỰ CHẤM

**Phần A — Trả lời được bằng lời của mình, không nhìn tài liệu:**

| # | Câu | ✅ |
|:---:|---|:---:|
| 1 | Kể 3 plane, mỗi plane 3 ví dụ, chạy ở đâu (CPU/ASIC)? | ☐ |
| 2 | "Punt" là gì? Punt nhiều dẫn tới hậu quả gì? | ☐ |
| 3 | Fast switching vs CEF — phân biệt bằng 1 cặp thuật ngữ? | ☐ |
| 4 | 3 thứ có trong RIB mà không có trong FIB? 2 thứ ngược lại? | ☐ |
| 5 | Adjacency table chứa gì? `Encap length 14` gồm những gì? | ☐ |
| 6 | Glean adjacency là gì? Nó giải thích hiện tượng nào? | ☐ |
| 7 | CAM vs TCAM: mỗi cái mấy trạng thái, dùng cho gì? | ☐ |
| 8 | VMR là gì? | ☐ |
| 9 | Vì sao `debug ip packet` không thấy traffic transit? | ☐ |
| 10 | Đọc `85%/78%` trong `show processes cpu` nghĩa là gì? | ☐ |
| 11 | CEF polarization là gì, sửa thế nào? | ☐ |
| 12 | Vì sao per-packet load-sharing không dùng ở production? | ☐ |
| 13 | SDM template làm gì? Đổi rồi cần làm gì? | ☐ |
| 14 | SVI vs routed port khác nhau gì? Điều kiện để SVI route được? | ☐ |
| 15 | CEF inconsistency là gì, vì sao đáng sợ? | ☐ |

**Phần B — Lab (tự làm lại KHÔNG xem hướng dẫn):**

> Đây là bản kiểm tra **sau khi** đã làm xong [Module-01-LAB.md](Module-01-LAB.md).
> Checklist từng bước có sẵn ở cuối file LAB — phần này để bạn tự đánh giá **đã thuộc chưa**.

| # | Yêu cầu | ✅ |
|:---:|---|:---:|
| 1 | Chạy được `show ip cef` và **chỉ ra** entry `receive`, `attached`, `drop`, và giải thích từng loại | ☐ |
| 2 | Chạy `show adjacency detail` và **giải mã** chuỗi hex thành MAC đích / MAC nguồn / EtherType | ☐ |
| 3 | Tái hiện glean: `clear arp-cache` → ping → giải thích `.!!!!` | ☐ |
| 4 | Chứng minh `debug ip packet` không thấy traffic CEF, rồi tắt CEF cho nó hiện ra, rồi **bật lại CEF** | ☐ |
| 5 | Dùng `show ip cef exact-route` xác định 4 cặp src/dst đi đường nào, và giải thích tính deterministic | ☐ |
| 6 | Đổi `load-sharing algorithm universal <ID>` và chứng minh đường đi của cùng 1 flow thay đổi | ☐ |
| 7 | Đọc `show processes cpu` và phân biệt được vấn đề control plane vs data plane | ☐ |
| 8 | Dùng `monitor capture` (EPC) bắt được gói — công cụ thay thế `debug ip packet` | ☐ |

---

## 🔗 11. TÀI LIỆU CHO MODULE NÀY

| Nguồn | Cụ thể |
|---|---|
| **Sách OCG 350-401** | Chương về *Packet Forwarding* (thường là chương 1 hoặc 2) — đọc kỹ phần CEF, FIB/RIB, TCAM |
| **Cisco doc**  | *IP Switching Cisco Express Forwarding Configuration Guide* — search: `IOS-XE CEF configuration guide` |
| **Cisco doc** | *Cisco Nonstop Forwarding* (hiểu vì sao tách control/data plane có giá trị) |
| **Cisco doc** | Trang *"How to Choose a Cisco IOS Switching Path"* — bảng so sánh process/fast/CEF gốc từ Cisco |
| **Cisco Live**  | Search `Cisco Live campus switching architecture ASIC` — session giải thích ASIC/TCAM rất trực quan |
| **Cisco doc** | *Embedded Packet Capture Configuration Guide* — công cụ bạn sẽ dùng cả đời |
| **Video** | CBT Nuggets ENCOR — bài về Packet Forwarding · Keith Barker: search `Keith Barker CEF` |
| **DevNet Sandbox** | Catalyst 9000 always-on — nơi duy nhất bạn xem được TCAM/SDM thật (vIOS không có) |
| **Forum** | https://community.cisco.com — search `CEF inconsistency`, `high CPU interrupt` để đọc case thật |

---

**➡️ Tiếp theo:** [Module-02 — Layer 2: STP, RSTP, MST, EtherChannel](Module-02-Layer2-STP-RSTP-MST-EtherChannel.md)
*(Domain Infrastructure 30% — bắt đầu khối nặng nhất của đề)*
