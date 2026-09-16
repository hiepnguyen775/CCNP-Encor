# Module-03 — IP Routing nền tảng

> 🧭 **Lộ trình:** Module-02 (Layer 2) → `[Bạn đang ở đây] Module-03` → Module-04 (OSPF sâu) → …
>
> 📊 **Vị trí trong blueprint:** Domain **3.0 Infrastructure (30%)**, mục **3.2 Layer 3** —
> đặc biệt **3.2.a Compare routing concepts of EIGRP and OSPF** *(advanced distance vector vs
> link-state, load balancing, path selection, path operations, metrics)*.
>
> ⏱️ **Tuần 6** · 10 giờ · 1 tuần

---

# 📌 TÓM TẮT — đọc 10 phút là nắm khung

## Module này trả lời một câu hỏi duy nhất

> **"Có nhiều đường tới cùng một đích — router quyết định đi đường nào, và dựa vào gì?"**

## Ba bước chọn đường — xương sống của cả module

```
   Gói tin cần tới 10.1.1.50 — router có 3 lựa chọn trong bảng:

      A) 10.1.1.0/24   học từ OSPF   (AD 110)
      B) 10.1.1.0/26   học từ RIP    (AD 120)
      C) 10.0.0.0/8    static        (AD 1)

   ┌─────────────────────────────────────────────────────────────┐
   │ BƯỚC 1 — LONGEST PREFIX MATCH   "cái nào CỤ THỂ nhất?"       │
   │          /26 > /24 > /8   →   B thắng                        │
   │          ⚠️ AD KHÔNG được xét ở bước này!                    │
   ├─────────────────────────────────────────────────────────────┤
   │ BƯỚC 2 — ADMINISTRATIVE DISTANCE  (chỉ khi CÙNG prefix)      │
   │          "tin nguồn tin nào hơn?"  số NHỎ = tin hơn          │
   ├─────────────────────────────────────────────────────────────┤
   │ BƯỚC 3 — METRIC   (chỉ khi cùng prefix VÀ cùng giao thức)    │
   │          "đường nào ngắn hơn?"                               │
   └─────────────────────────────────────────────────────────────┘

   ⭐ B thắng — dù AD 120 là cao nhất. Vì bước 1 xét TRƯỚC.
```

## 6 ý phải nhớ

| # | Ý | Một câu |
|:---:|---|---|
| 1 | **Thứ tự chọn đường** | **Longest prefix → AD → Metric.** Không bao giờ đảo. Prefix dài **luôn** thắng trước |
| 2 | **AD là "tin ai hơn"** | Connected 0 · Static 1 · eBGP 20 · EIGRP 90 · **OSPF 110** · RIP 120 · iBGP 200 |
| 3 | **Floating static** | Static dự phòng đặt **AD cao hơn** → chỉ vào bảng khi đường chính rớt |
| 4 | ⭐ **`up/up` ≠ thông** | Interface sống không có nghĩa đầu kia còn sống → **phải dùng IP SLA + track** |
| 5 | **EIGRP vs OSPF** | EIGRP = **hỏi hàng xóm** (distance vector nâng cao) · OSPF = **có bản đồ cả vùng** (link-state) |
| 6 | **Redistribution** | Nối 2 giao thức = nguy cơ **routing loop**. Chặn bằng **route tag** |

## Bảng lệnh cốt lõi

| Lệnh | Cho biết gì |
|---|---|
| `show ip route` | Bảng định tuyến — đường router đang dùng |
| `show ip route 10.1.1.50` | **Router chọn route nào cho ĐÍCH cụ thể này** |
| `show ip route <prefix> longer-prefixes` | Mọi route con của một dải |
| `show ip protocols` | Giao thức nào đang chạy, AD bao nhiêu, quảng bá mạng nào |
| `show ip sla statistics` | Phép đo IP SLA — đường còn sống không |
| `show track` | Trạng thái track + ai đang dùng nó |
| `show route-map` | Route-map khớp bao nhiêu lần |

## 🗺️ Bố cục module — đọc theo đúng thứ tự này

| Phần | Tên | Đọc thế nào | Thời gian |
|:---:|---|---|:---:|
| **1** | 🧠 **CÁI ĐÓ LÀ GÌ** | 6 ví von, đọc **một mạch**, không lệnh | 45 phút |
| **2** | ⚙️ **NÓ CHẠY THẾ NÀO** | Cơ chế + bảng AD + IP SLA + redistribution | 4 giờ |
| **3** | 🧪 **NHÌN THẤY NÓ** | [LAB 03](Module-03-LAB.md) — 3 bài, dùng chung 1 topology | 7 giờ |
| **4** | 🏗️ **TOPO & KIẾN TRÚC** | 6 quyết định thiết kế. **Vẽ lại trên giấy** | 45 phút |
| **📎** | **PHỤ LỤC** | 🔴 **KHÔNG đọc lần đầu** — chỉ tra | — |

> **Bài quan trọng nhất module: [LAB 03-2 — IP SLA + Object Tracking](Module-03-LAB.md).**
> Nó dạy bạn một sự thật mà không bảng nào truyền tải được:
> ⭐ **interface báo `up/up` KHÔNG có nghĩa là đường còn thông.**
> Kỹ thuật này quay lại ở **Module-06A** (HSRP tracking) và **Module-11** (đo chất lượng đường).

---

## ⭐ 0. ĐỌC TRƯỚC — một thông tin tiết kiệm cho bạn 2 tuần

Rất nhiều người tự học ENCOR dành **2–3 tuần học cấu hình EIGRP** rồi vào phòng thi mới biết:

> **Blueprint ENCOR chỉ yêu cầu SO SÁNH (compare) EIGRP với OSPF — KHÔNG yêu cầu cấu hình EIGRP.**
>
> Nguyên văn mục 3.2.a: *"**Compare** routing concepts of EIGRP and OSPF"*.
> Còn mục 3.2.b nói rõ *"**Configure and verify** simple **OSPF** environments"* — chỉ OSPF.

| Protocol | ENCOR yêu cầu | Thời gian nên dành |
|---|---|---|
| **OSPF** | ⭐ **Cấu hình + verify + troubleshoot** (sâu) | 2 tuần (Module-04) |
| **eBGP** | ⭐ **Cấu hình + verify** (giữa neighbor kề nhau) | 2 tuần (Module-05) |
| **EIGRP** | 🟡 **CHỈ so sánh khái niệm** với OSPF | ⭐ **~2 giờ** — bảng §2.5 của module này |

> ✅ **Vậy module này làm gì:** dạy **nền tảng chung của mọi protocol định tuyến**
> (cách router chọn đường, static route, redistribution) + **bảng so sánh EIGRP↔OSPF đủ để thi**.
> Không dạy cấu hình EIGRP.
>
> ⚠️ Nếu sau này bạn thi **ENARSI (300-410)** thì mới cần EIGRP sâu. Lúc đó quay lại học.
> **Bây giờ thì đừng.**

---

## ✅ 1. Chuẩn bị trước khi học

| Cần có | Chi tiết |
|---|---|
| **Kiến thức trước** | ⭐ Module-P0 §2.5 (router chọn đường) và §2.6 (OSPF single-area) — **bắt buộc** |
| **Lab** | 3× vIOS (router). Dùng lại **LAB P0-4/P0-5** rồi mở rộng |
| **RAM** | 3–4× 512 MB = **1.5–2 GB** ✅ nhẹ |
| **Thời lượng** | 10 giờ: 3h lý thuyết · 5h lab · 2h quiz + đúc kết |

---

## 🧠 PHẦN 1 — CÁI ĐÓ LÀ GÌ

> **Đọc phần này TRƯỚC, đọc một mạch.** Không lệnh, không bảng tra — chỉ ví von.
>
> Routing là chủ đề **trừu tượng** nhưng lại có ví von rất dễ: nó giống hệt việc
> bạn hỏi đường và chọn chỉ dẫn nào đáng tin nhất.
>
> **Tự kiểm tra:** đọc xong mỗi mục, gấp tài liệu lại, nói lại trong 3 câu.

### 2.1 Longest prefix match — GPS chọn chỉ dẫn cụ thể nhất

Bạn đi tìm *"số 12 Nguyễn Huệ, Quận 1, TP.HCM"*. Có 3 tấm biển:

| Biển | Nội dung | Prefix |
|---|---|---|
| A | → Việt Nam | `/8` |
| B | → TP.HCM | `/16` |
| C | → số 12 Nguyễn Huệ, Quận 1 | `/32` |

Bạn theo biển **C**. Không quan tâm biển nào do ai dựng (protocol nào), ai đáng tin hơn (AD).
**Cụ thể nhất thì thắng.**

🧠 **Một câu để nhớ:** *Cụ thể thắng tin cậy. Longest prefix ĐỨNG TRƯỚC AD, luôn luôn.*

### 2.2 Recursive lookup — tra địa chỉ 2 lần

Bạn cần gửi thư tới `10.1.1.5`. Sổ ghi: *"Đưa cho anh Hai (`10.0.12.2`)"*.

Nhưng câu hỏi tiếp theo là: **"Anh Hai ở đâu?"** Bạn phải tra sổ **lần thứ hai**.

- Tra được → ✅ gửi được
- Không tra được ("không biết anh Hai ở đâu") → ❌ **cả chỉ dẫn ban đầu trở nên vô dụng**

🧠 **Một câu để nhớ:** *Static route có trong config mà không có trong `show ip route`
= recursion thất bại = next-hop không reachable.*

### 2.3 Floating static vs IP SLA — hai cách kiểm tra "đường còn thông không"

**Floating static** như *nhìn ra cửa xem đường có bị rào không*:
> "Cửa còn mở → chắc đường thông." — Nhưng đường có thể sập ở km thứ 50 mà cửa vẫn mở.

**IP SLA** như *gọi điện cho người ở đầu bên kia*:
> "Anh có nghe tôi không?" — Không trả lời → đường có vấn đề, **dù cửa vẫn mở**.

🧠 **Một câu để nhớ:** *Interface `up` không có nghĩa là **đích** còn sống.
Floating static tin vào cửa, IP SLA tin vào tiếng trả lời.*

### 2.4 EIGRP vs OSPF — hỏi đường vs có bản đồ

| | **EIGRP** — *người hỏi đường thông minh* | **OSPF** — *người có bản đồ* |
|---|---|---|
| Biết gì | Chỉ biết mỗi neighbor nói "từ tôi tới đó xa X km" | ⭐ Biết **toàn bộ bản đồ** thành phố |
| Tính đường | So sánh lời kể của các neighbor | ⭐ **Tự tính** bằng Dijkstra |
| Có bản đồ dự phòng? | ⭐ **Có** — ghi sẵn "nếu đường A tắc thì đi anh B" (**Feasible Successor**) → chuyển ngay | Có bản đồ → **tự tính lại** (mất chút CPU) |
| Khi bí | ⚠️ Phải **đi hỏi khắp nơi** (query) → có thể bị treo (**SIA**) | Xem lại bản đồ, tự tính ra |
| Chi phí | Nhẹ (không cần lưu bản đồ) | Tốn RAM (lưu LSDB) + CPU (chạy SPF) |
| Cần chia vùng? | Không bắt buộc | ⭐ **Bắt buộc** (area) khi mạng lớn — bản đồ quá to |

🧠 **Một câu để nhớ:** *EIGRP nhanh vì **có sẵn phương án B đã được kiểm chứng** (Feasible Successor).
OSPF nhanh vì **có bản đồ nên tự tính được** phương án mới. Hai triết lý khác nhau,
và đó là toàn bộ nội dung câu "compare EIGRP and OSPF" của đề.*

### 2.5 Feasibility Condition — mẹo chống loop bằng một phép so sánh

Bạn ở Hà Nội, muốn đi Sài Gòn (2000 km). Hai người báo:

| Người | Họ nói | RD | Có thể tin làm phương án B? |
|---|---|:---:|:---:|
| Anh A | "Từ **chỗ tôi** tới Sài Gòn còn **1800 km**" | 1800 | ✅ **Tin được** (1800 < 2000) |
| Anh B | "Từ **chỗ tôi** tới Sài Gòn còn **2100 km**" | 2100 | ❌ **Không tin** (2100 > 2000) |

**Vì sao không tin anh B:** nếu anh B ở xa Sài Gòn **hơn tôi**, rất có thể anh ta đang tính
đường **đi qua tôi**. Dùng anh B làm phương án B = **gửi traffic vòng lại chính mình** = loop.

🧠 **Một câu để nhớ:** *`RD < FD` — "neighbor phải gần đích hơn tôi" — nghĩa là nó không đi qua tôi.
Một phép so sánh đơn giản mà chống được loop, không cần hỏi ai. Đó là sự thanh lịch của DUAL.*

### 2.6 Route tag — con dấu hộ chiếu

Route được redistribute từ OSPF sang EIGRP → **dập dấu "xuất phát từ OSPF"** (`set tag 100`).

Khi route đó đi lòng vòng trong EIGRP rồi tới một cửa khác muốn **nhập lại vào OSPF**,
hải quan xem hộ chiếu, thấy dấu "xuất phát từ OSPF" → **"Anh vốn là người của chúng tôi,
không cần nhập cảnh lại"** → từ chối.

🧠 **Một câu để nhớ:** *Không có tag thì route không có ký ức về nguồn gốc của mình —
và nó sẽ đi vòng mãi. Tag cho route một trí nhớ.*

---

## ⚙️ PHẦN 2 — NÓ CHẠY THẾ NÀO

> Giờ lắp **cơ chế thật, con số và câu lệnh** vào hình dung bạn vừa có.
>
> | Phần 1 (ví von) | → | Phần 2 (cơ chế) |
> |---|:---:|---|
> | §2.1 GPS chọn chỉ dẫn cụ thể nhất | → | **§3.1 Ba bước chọn đường** |
> | §2.2 tra địa chỉ 2 lần | → | **§3.3 Static route & recursive lookup** |
> | §2.3 hai cách kiểm tra đường | → | **§3.4 IP SLA + Object Tracking** |
> | §2.4 hỏi đường vs có bản đồ · §2.5 | → | **§3.5 EIGRP vs OSPF** |
> | §2.6 con dấu hộ chiếu | → | **§3.6 Redistribution · §3.7 Route-map** |
>
> ⚠️ **Bảng trong phần này là để TRA CỨU về sau.** Đọc hiểu ý chính, quay lại tra khi làm LAB.

### 3.1 Router chọn đường: 3 bước (đào sâu hơn Module-P0)

```
┌───────────────────────────────────────────────────────────────────────┐
│  BƯỚC 1 — LONGEST PREFIX MATCH                                        │
│  Trong tất cả route KHỚP với IP đích → chọn prefix DÀI NHẤT           │
│  (không quan tâm protocol, không quan tâm AD)                         │
│         ↓ nếu nhiều route CÙNG prefix, KHÁC protocol                  │
│  BƯỚC 2 — ADMINISTRATIVE DISTANCE                                     │
│  Chọn AD nhỏ nhất → route đó vào RIB, các route khác bị loại          │
│         ↓ nếu nhiều route CÙNG prefix, CÙNG protocol                  │
│  BƯỚC 3 — METRIC                                                      │
│  Chọn metric nhỏ nhất                                                 │
│         ↓ nếu metric BẰNG NHAU                                        │
│  → ECMP: cài tất cả vào RIB, chia tải (per-destination hash — M01)    │
└───────────────────────────────────────────────────────────────────────┘
```

#### Ví dụ có lời giải — làm 3 ví dụ này là hiểu

**Ví dụ 1 — Longest prefix thắng AD**

Gói tới `10.1.1.5`. Router có:

| Route | Nguồn | AD | Khớp `10.1.1.5`? |
|---|---|:---:|:---:|
| `10.0.0.0/8` | Static | 1 | ✅ |
| `10.1.0.0/16` | OSPF | 110 | ✅ |
| `10.1.1.0/24` | RIP | 120 | ✅ |

**→ Chọn `10.1.1.0/24` (RIP).** Prefix dài nhất thắng, dù AD 120 là **tệ nhất**.

**Ví dụ 2 — Cùng prefix, AD quyết định**

Gói tới `10.1.1.5`. Router có:

| Route | Nguồn | AD |
|---|---|:---:|
| `10.1.1.0/24` | OSPF | 110 |
| `10.1.1.0/24` | EIGRP | 90 |
| `10.1.1.0/24` | RIP | 120 |

**→ Chọn EIGRP (AD 90).** Cùng `/24` → so AD → 90 nhỏ nhất.
⭐ **2 route kia bị loại khỏi RIB hoàn toàn** — không phải "dự phòng". Chúng nằm trong database
của protocol (`show ip ospf database`) nhưng **không vào bảng route**.

**Ví dụ 3 — Cùng prefix, cùng protocol → metric**

| Route | Nguồn | AD | Metric |
|---|---|:---:|:---:|
| `10.1.1.0/24` via `10.0.12.2` | OSPF | 110 | 20 |
| `10.1.1.0/24` via `10.0.13.2` | OSPF | 110 | 20 |

**→ Cả hai vào RIB (ECMP).** Metric bằng nhau → chia tải.
Nếu một cái metric 30 → chỉ cái metric 20 vào RIB.

> ⚠️ **Sai lầm phổ biến nhất của người tự học:** *"OSPF AD 110 < RIP 120 nên OSPF luôn thắng."*
> **Sai.** Longest prefix match **đứng trước** AD. Đề ENCOR gài chỗ này rất nhiều.

### 3.2 Administrative Distance — bảng đầy đủ

| Nguồn route | AD | Ghi nhớ |
|---|:---:|---|
| **Connected interface** | **0** | Không gì tin hơn cái mình nhìn thấy |
| **Static route** | **1** | Admin tự tay gõ |
| EIGRP summary route | 5 | |
| **eBGP** | **20** | Từ AS khác → tin hơn iBGP |
| **EIGRP (internal)** | **90** | |
| IGRP | 100 | (đã lỗi thời) |
| **OSPF** | **110** | Mọi loại: intra, inter, external |
| IS-IS | 115 | |
| **RIP** | **120** | |
| EIGRP (external) | **170** | Route redistribute vào EIGRP |
| **iBGP** | **200** | |
| **Unreachable** | **255** | ⭐ AD 255 = **KHÔNG cài vào RIB** |

**6 con số phải thuộc: `0 – 1 – 20 – 90 – 110 – 200`**

> ⭐ **Vì sao eBGP (20) tin hơn iBGP (200)?**
> eBGP route đến từ **AS khác** → là route "thật" của Internet, đã đi qua chính sách của AS đó.
> iBGP route là route **đã được học từ eBGP rồi lan trong nội bộ** → xa nguồn hơn.
> Và AD 200 cao có mục đích: để **IGP nội bộ (OSPF 110) luôn thắng iBGP** cho các subnet nội bộ.

#### Đổi AD — 3 cách

```
! === Cách 1: đổi AD của cả protocol ===
router ospf 1
 distance 130                            ! mọi route OSPF thành AD 130

! === Cách 2: đổi AD theo nguồn / theo prefix (dùng ACL) ===
access-list 10 permit 10.1.1.0 0.0.0.255
router ospf 1
 distance 200 10.0.12.2 0.0.0.0 10       ! route về 10.1.1.0/24 học từ neighbor 10.0.12.2 → AD 200
!                └ neighbor ┘ └wildcard┘ └ACL

! === Cách 3: đổi AD của static route (floating static) ===
ip route 10.1.1.0 255.255.255.0 10.0.12.2 200
!                                          └── AD 200
```

**Đặc biệt cho OSPF — đổi AD theo loại route:**
```
router ospf 1
 distance ospf intra-area 110 inter-area 115 external 130
```

**Đặc biệt cho BGP:**
```
router bgp 65001
 distance bgp 20 200 200
!             │   │   └─ local
!             │   └───── internal (iBGP)
!             └───────── external (eBGP)
```

> ⚠️ **Cảnh báo:** đổi AD là công cụ mạnh nhưng **dễ gây routing loop** nếu không đổi đồng bộ
> trên mọi router liên quan. Chỉ dùng khi hiểu rõ. Ở production, ưu tiên dùng **route-map + tag**
> (§2.7) thay vì đổi AD.

### 3.3 Static route — đào sâu

| Kiểu | Cú pháp | Ghi chú |
|---|---|---|
| **Next-hop** | `ip route 10.1.1.0 255.255.255.0 10.0.12.2` | Cần **recursive lookup** |
| **Exit interface** | `ip route 10.1.1.0 255.255.255.0 Gi0/0` | Chỉ dùng cho link **P2P** |
| ⭐ **Fully specified** | `ip route 10.1.1.0 255.255.255.0 Gi0/0 10.0.12.2` | **Rõ ràng nhất** — nên dùng |
| **Default route** | `ip route 0.0.0.0 0.0.0.0 203.0.113.2` | Gateway of last resort |
| **Floating static** | `ip route 10.1.1.0 255.255.255.0 10.0.12.2 200` | AD cao → route dự phòng |
| **Null route** | `ip route 10.9.9.0 255.255.255.0 null0` | Bỏ traffic (chống loop, blackhole) |
| **Permanent** | `ip route 10.1.1.0 255.255.255.0 10.0.12.2 permanent` | ⚠️ Giữ route **dù interface down** |
| ⭐ **Tracked** | `ip route 0.0.0.0 0.0.0.0 203.0.113.2 track 1` | Xóa route nếu IP SLA fail — xem §2.4 |

#### ⭐ Recursive lookup — vì sao static route "không vào bảng"

Khi bạn gõ `ip route 10.1.1.0 255.255.255.0 10.0.12.2`, router phải làm **2 lần tra cứu**:

```
1. "Đi tới 10.1.1.0/24 thì next-hop là 10.0.12.2"
        ↓  (recursion — tra tiếp)
2. "Nhưng 10.0.12.2 ở đâu?" → tra RIB → "connected trên Gi0/0"
        ↓
3. ✅ Cài route vào RIB
```

⚠️ **Nếu bước 2 thất bại** (không có route tới `10.0.12.2`) → **static route KHÔNG được cài vào RIB**.
Nó không hiện trong `show ip route`, dù bạn đã gõ đúng.

| Trường hợp | Static route có vào RIB? |
|---|:---:|
| Next-hop reachable (connected hoặc có route) | ✅ Có |
| Next-hop **không** reachable | ❌ **Không** |
| Dùng **exit interface** và interface `up` | ✅ Có |
| Dùng exit interface và interface `down` | ❌ Không |
| `permanent` + interface down | ⚠️ **Vẫn có** (nguy hiểm — traffic vào hố đen) |

**Kiểm tra:**
```
show ip route static                    ! static nào vào được RIB
show ip route 10.1.1.0                  ! chi tiết + có "recursive via" không
show running-config | include ip route  ! static nào đã cấu hình
```
→ **So sánh 2 lệnh đầu với lệnh cuối.** Static có trong config mà không có trong RIB = recursion fail.

#### ⚠️ Điểm yếu của floating static (bạn đã gặp ở Module-P0)

```
ip route 2.2.2.2 255.255.255.255 10.0.12.2         ! chính, AD 1
ip route 2.2.2.2 255.255.255.255 10.0.13.2 200     ! dự phòng, AD 200
```

| Tình huống | Floating static có failover? |
|---|:---:|
| Interface local `down` | ✅ Có |
| Next-hop chết → mất route tới next-hop | ✅ Có |
| ⚠️ **Đích chết nhưng đường đi vẫn up** | ❌ **KHÔNG** |
| ⚠️ **ISP nhận link nhưng mạng bên trong ISP chết** | ❌ **KHÔNG** |

> 🔴 **Đây là lỗ hổng thật gây sự cố ở production.** Link tới ISP vẫn "up" (switch của ISP còn sống),
> nhưng router core của ISP chết → traffic của bạn đi vào **hố đen** mà floating static **không hề biết**.
>
> ✅ **Giải pháp: IP SLA + object tracking** — §2.4.

### 3.4 ⭐ IP SLA + Object Tracking — vá lỗ hổng của static route

**Ý tưởng:** thay vì tin vào trạng thái interface, hãy **thực sự ping thử đích** rồi mới quyết định.

```
      ┌─────────────┐  ping mỗi 5 s   ┌──────────────┐
      │   IP SLA    │ ──────────────▶ │  8.8.8.8     │
      │  operation  │ ◀────────────── │  (đích thật) │
      └──────┬──────┘   reply         └──────────────┘
             │ kết quả (up/down)
             ▼
      ┌─────────────┐
      │   TRACK     │  object theo dõi kết quả IP SLA
      └──────┬──────┘
             │ trạng thái
             ▼
      ┌─────────────────────────────────────┐
      │  ip route 0.0.0.0 0.0.0.0 <ISP1>    │  ← xóa route nếu track DOWN
      │           track 1                    │
      └─────────────────────────────────────┘
```

**Cấu hình đầy đủ:**

```
! ═══ BƯỚC 1: Tạo IP SLA operation ═══
ip sla 1
 icmp-echo 8.8.8.8 source-interface GigabitEthernet0/0
 frequency 5                          ! ping mỗi 5 giây
 timeout 2000                         ! chờ reply 2000 ms
 threshold 1000                       ! coi là "chậm" nếu > 1000 ms
!
ip sla schedule 1 life forever start-time now      ! THIẾU DÒNG NÀY = SLA không chạy
!
! ═══ BƯỚC 2: Tạo track object theo dõi SLA ═══
track 1 ip sla 1 reachability
 delay down 3 up 5                    ! chống nhấp nháy: chờ 3 s mới báo down, 5 s mới báo up
!
! ═══ BƯỚC 3: Gắn track vào static route ═══
ip route 0.0.0.0 0.0.0.0 203.0.113.2 track 1       ! ISP1 — chính
ip route 0.0.0.0 0.0.0.0 198.51.100.2 200          ! ISP2 — dự phòng (floating)
```

**Cơ chế:** IP SLA ping `8.8.8.8` qua ISP1. Nếu fail → track 1 `Down` → **route ISP1 bị xóa khỏi RIB**
→ route ISP2 (AD 200) nổi lên. Khi ISP1 hồi phục → track `Up` → route ISP1 quay lại.

**Các loại IP SLA operation hay dùng:**

| Loại | Lệnh | Đo gì |
|---|---|---|
| ⭐ **icmp-echo** | `icmp-echo 8.8.8.8` | Reachability, RTT |
| **udp-jitter** | `udp-jitter 10.1.1.1 5000` | Jitter, packet loss — cho VoIP |
| **tcp-connect** | `tcp-connect 10.1.1.1 80` | Dịch vụ TCP có sống không |
| **http** | `http get http://server/` | Web service có trả về không |
| **dns** | `dns www.example.com name-server 8.8.8.8` | DNS resolve được không |
| **path-jitter** | `path-jitter 10.1.1.1` | Jitter theo từng hop |

**Kiểm tra:**
```
show ip sla configuration 1                  ! cấu hình
show ip sla statistics 1                     ! kết quả: bao nhiêu lần OK/fail, RTT
show ip sla summary                          ! tóm tắt mọi SLA
show track                                   ! trạng thái track object
show track 1
show ip route 0.0.0.0                        ! route đang dùng cái nào
```

**Output mẫu `show track 1`:**
```
Track 1
  IP SLA 1 reachability
  Reachability is Up
    3 changes, last change 00:05:12
  Delay up 5 secs, down 3 secs
  Latest operation return code: OK
  Latest RTT (millisecs) 24
  Tracked by:
    STATIC-IP-ROUTING 0
```
⭐ Dòng `Tracked by: STATIC-IP-ROUTING 0` xác nhận static route đang dùng track object này.

> ⭐ **`delay down 3 up 5` — vì sao cần:** không có delay, một cú nhấp nháy 1 giây của mạng
> sẽ làm route bị xóa rồi cài lại → **route flapping** → CEF phải dựng lại FIB liên tục.
> Đặt `up` lớn hơn `down` để route mới phải "chứng minh mình ổn định" trước khi được dùng lại.

> 💡 **Nâng cao (Module-11 sẽ học):** IP SLA + track còn dùng cho **HSRP** (Module-06),
> **PBR**, và **EEM** (Module-12). Đây là một trong những công cụ đa dụng nhất của IOS.

### 3.5 ⭐ EIGRP vs OSPF — bảng cần cho đề (học bảng này, đừng học cấu hình)

#### Bảng so sánh chính

| | **EIGRP** | **OSPF** |
|---|---|---|
| **Loại** | ⭐ **Advanced Distance Vector** (hybrid) | ⭐ **Link-State** |
| **Thuật toán** | ⭐ **DUAL** (Diffusing Update Algorithm) | ⭐ **Dijkstra SPF** |
| **Biết gì về mạng** | Chỉ biết **khoảng cách qua neighbor** ("đi hướng này, xa X") | ⭐ Biết **toàn bộ bản đồ** (LSDB) |
| **Metric** | ⭐ **Composite**: Bandwidth + Delay (mặc định) | ⭐ **Cost** = reference-bw / interface-bw |
| **AD** | **90** (internal) / **170** (external) / 5 (summary) | **110** (mọi loại) |
| **Unequal-cost load balancing** | ⭐ **CÓ** — lệnh `variance` | ⭐ **KHÔNG** — chỉ equal-cost (ECMP) |
| **Summarization** | ⭐ **Ở bất kỳ đâu** (mọi interface) | ⭐ **Chỉ ở ABR / ASBR** |
| **Cần thiết kế phân cấp?** | ❌ Không bắt buộc | ⭐ **Có — bắt buộc area, area 0 là backbone** |
| **Chuẩn** | Cisco (nay là RFC 7868 — *informational*) | ⭐ **Open standard** RFC 2328 (v2) / 5340 (v3) |
| **Đa vendor** | ⚠️ Thực tế chỉ Cisco | ⭐ ✅ Mọi vendor |
| **IP protocol number** | **88** | **89** |
| **Multicast address** | **224.0.0.10** | **224.0.0.5** (all) / **224.0.0.6** (DR/BDR) |
| **Hello / Hold-Dead** | 5 / 15 s (link nhanh) · 60 / 180 s (link < T1) | 10 / 40 s (broadcast, P2P) · 30 / 120 s (NBMA) |
| **Update** | ⭐ **Partial + bounded** — chỉ gửi phần thay đổi, chỉ cho router liên quan | Flood LSA trong area, refresh mỗi 30 phút |
| **VLSM / CIDR** | ✅ | ✅ |
| **Cấu trúc database** | Neighbor table + **Topology table** + Routing table | Neighbor table + **LSDB** + Routing table |
| **Hội tụ** | ⭐ Cực nhanh **nếu có Feasible Successor** (tính local, không hỏi ai) | Nhanh, nhưng phải **chạy lại SPF** |
| **Rủi ro khi hội tụ** | ⚠️ **SIA** (Stuck-In-Active) nếu query lan quá xa | ⚠️ SPF tốn CPU nếu area quá lớn |
| **Tài nguyên** | CPU/RAM thấp hơn | Tốn RAM (lưu LSDB) + CPU (chạy SPF) |

#### DUAL — 4 khái niệm phải hiểu (đề hỏi)

| Thuật ngữ | Nghĩa |
|---|---|
| **FD** — Feasible Distance | Metric **tốt nhất** của tôi tới đích |
| **RD** — Reported Distance<br>(*Advertised Distance*) | Metric mà **neighbor báo** cho tôi (khoảng cách từ **neighbor** tới đích) |
| ⭐ **Successor** | Neighbor có metric tổng nhỏ nhất → **route chính**, vào RIB |
| ⭐ **Feasible Successor (FS)** | Route **dự phòng** đã được kiểm chứng **không tạo loop** → nằm sẵn trong topology table |

**⭐ Feasibility Condition (điều kiện để làm FS):**

```
              RD (của neighbor)  <  FD (của tôi)
```

> 🧠 **Vì sao điều kiện này chống được loop:** nếu neighbor báo khoảng cách của nó tới đích
> **nhỏ hơn** khoảng cách hiện tại của tôi → chứng tỏ neighbor **không đi qua tôi** để tới đích.
> Nếu nó đi qua tôi thì khoảng cách của nó phải **lớn hơn** của tôi.
>
> Đây là mẹo toán học đơn giản nhưng cực hiệu quả — và là lý do EIGRP hội tụ nhanh:
> khi Successor chết, router **dùng ngay FS mà không cần hỏi ai** (tính toán local, ~0 giây).

**Khi KHÔNG có Feasible Successor:**
```
Successor chết + không có FS
        ↓
Route vào trạng thái ACTIVE
        ↓
Router gửi QUERY ra mọi neighbor: "ai biết đường tới đích này?"
        ↓
Neighbor không biết → gửi query tiếp cho neighbor của nó… (lan rộng)
        ↓
⚠️ Nếu query lan quá xa / có router không trả lời → SIA (Stuck-In-Active) → route bị xóa
```
→ Đây là lý do EIGRP cần **stub router** và **summarization** để **giới hạn phạm vi query**.

#### Metric của EIGRP

**Classic metric (K values mặc định: K1=1, K2=0, K3=1, K4=0, K5=0):**

```
Metric = 256 × [ (10^7 / min-bandwidth-kbps) + (tổng delay-microsec / 10) ]
                  └──── K1: bandwidth ────┘     └──── K3: delay ────┘
```

| Tham số | Có dùng mặc định? | Ghi chú |
|---|:---:|---|
| **Bandwidth** (K1) | ✅ | ⭐ Lấy **bandwidth NHỎ NHẤT** trên đường đi (bottleneck) |
| **Delay** (K3) | ✅ | ⭐ **CỘNG DỒN** delay của mọi interface |
| Load (K2) | ❌ | Tắt mặc định — nếu bật sẽ gây route flapping |
| Reliability (K4) | ❌ | Tắt mặc định |
| MTU (K5) | ❌ | ⚠️ **MTU KHÔNG tham gia tính metric** — chỉ là tie-breaker |

> ⭐ **Bẫy đề kinh điển:** *"MTU có nằm trong công thức metric EIGRP không?"* → **KHÔNG.**
> MTU được **gửi kèm** trong update nhưng **không tính vào metric**.

**Wide metric (EIGRP named mode):** metric 64-bit thay vì 32-bit, dùng **Throughput** và **Latency**
để phân biệt được link 10G/40G/100G (classic metric bị "trần" ở tốc độ cao).

#### OSPF metric — nhắc lại để so sánh

```
Cost = reference-bandwidth (Mbps) / interface-bandwidth (Mbps)
Mặc định reference = 100 Mbps
```

| Interface | Cost mặc định |
|---|:---:|
| FastEthernet (100 Mbps) | 1 |
| GigabitEthernet | **1** ⚠️ |
| 10 GigabitEthernet | **1** ⚠️ |

→ Phải đặt `auto-cost reference-bandwidth 100000` **đồng nhất mọi router** (Module-P0 §2.6).

#### ⭐ Unequal-cost load balancing — khác biệt lớn nhất về mặt tính năng

| | EIGRP | OSPF |
|---|---|---|
| Equal-cost (ECMP) | ✅ | ✅ |
| **Unequal-cost** | ⭐ ✅ `variance <multiplier>` | ⭐ ❌ **Không hỗ trợ** |

```
! EIGRP: dùng cả đường có metric ≤ (metric tốt nhất × variance)
router eigrp 100
 variance 2                     ! chấp nhận đường có metric tới 2× đường tốt nhất
```

Điều kiện: đường đó phải là **Feasible Successor** (thỏa Feasibility Condition).

> 🎓 **Đề hay hỏi:** *"Protocol nào hỗ trợ unequal-cost load balancing?"* → **EIGRP**.
> OSPF muốn "unequal-cost" thì phải dùng cách khác (PBR, hoặc tune cost thủ công).

### 3.6 Redistribution — nối 2 protocol lại

**Redistribution** = lấy route từ protocol A đưa vào protocol B.

#### ⭐ Seed metric — bảng phải nhớ

Khi redistribute vào protocol B, route "không có metric của B" → phải cấp **seed metric**.

| Redistribute **VÀO** | Seed metric mặc định | Cần chỉ định tay? |
|---|---|:---:|
| **OSPF** | **20** (từ BGP thì là **1**), type **E2** | ❌ Không cần |
| **EIGRP** | ⚠️ **INFINITE** | ⭐ **BẮT BUỘC** — không thì route bị bỏ |
| **RIP** | ⚠️ **INFINITE** | ⭐ **BẮT BUỘC** |
| **BGP** | Metric của IGP → thành **MED** | ❌ Không cần |
| **IS-IS** | 0 | ❌ |

> 🔴 **Đây là lỗi số 1 khi redistribute:** đưa route vào **EIGRP hoặc RIP** mà không chỉ định metric
> → seed metric = infinite → **route bị bỏ âm thầm**. `show ip route` bên kia không có gì,
> mà không có thông báo lỗi nào.

```
! ✅ ĐÚNG — chỉ định metric khi vào EIGRP
router eigrp 100
 redistribute ospf 1 metric 10000 100 255 1 1500
!                          │     │   │  │  └ MTU
!                          │     │   │  └── load
!                          │     │   └───── reliability
!                          │     └───────── delay
!                          └─────────────── bandwidth

! Hoặc đặt default-metric cho mọi redistribution
router eigrp 100
 default-metric 10000 100 255 1 1500
 redistribute ospf 1
```

```
! Vào OSPF — không cần metric, nhưng cần "subnets"
router ospf 1
 redistribute eigrp 100 subnets
 redistribute static subnets
 redistribute connected subnets
```

#### ⭐ Từ khóa `subnets` — bẫy đề

| Có `subnets` | Không có `subnets` |
|---|---|
| Redistribute **mọi subnet** | ⚠️ Chỉ redistribute **classful network** (VD `10.0.0.0/8`), **bỏ hết subnet** như `10.1.1.0/24` |

> ⭐ Trên IOS/IOS-XE cổ điển, thiếu `subnets` là nguyên nhân kinh điển của "redistribute rồi mà
> bên kia không có route". Một số IOS-XE mới mặc định bật subnets, nhưng **cứ gõ `subnets` cho chắc** —
> gõ thêm không có hại, và đề vẫn hỏi.

#### ⭐ OSPF External Type 1 vs Type 2

| | **E1** (`metric-type 1`) | **E2** (`metric-type 2`) — mặc định |
|---|---|---|
| Metric | ⭐ **External cost + internal cost tới ASBR** | ⭐ **Chỉ external cost** — **không đổi** trong toàn domain |
| Nghĩa | "Chi phí đi tới đích, tính cả đường đi trong nhà" | "Chi phí ra khỏi nhà" |
| Khi có **nhiều ASBR** | ⭐ Router chọn **ASBR gần nhất** (vì cộng thêm internal cost) | ⚠️ Không phân biệt được — mọi ASBR cùng metric |
| Ký hiệu trong `show ip route` | `O E1` | `O E2` |
| Dùng khi | ⭐ Có **nhiều điểm ra** và muốn traffic ra điểm gần nhất | Chỉ có 1 điểm ra, hoặc không quan tâm |

```
router ospf 1
 redistribute static subnets metric-type 1      ! chọn E1
```

> 🎓 **Đề hay hỏi:** *"Mạng có 2 ASBR. Muốn router nội bộ chọn ASBR gần nhất. Dùng loại nào?"*
> → **E1**, vì E1 cộng thêm internal cost nên ASBR gần sẽ có metric nhỏ hơn.

#### ⭐ Thứ tự ưu tiên route trong OSPF

Khi cùng một prefix xuất hiện dưới nhiều dạng, OSPF chọn theo thứ tự:

```
1. Intra-area (O)         ← trong cùng area, tốt nhất
2. Inter-area (O IA)      ← từ area khác
3. External E1 (O E1)
4. External E2 (O E2)     ← kém nhất
```

⭐ **Lưu ý:** thứ tự này **chỉ áp dụng trong OSPF**, và nó là bước **trước** khi so metric.
Một route `O IA` metric 1000 vẫn thắng route `O E1` metric 5. Đây là bẫy đề.

#### ⚠️ Mutual redistribution & routing loop

Khi redistribute **cả hai chiều tại 2 điểm khác nhau** → route có thể "đi vòng" quay lại:

```
    OSPF domain                            EIGRP domain
         │                                      │
    ┌────┴────┐  redistribute cả 2 chiều  ┌────┴────┐
    │   R1    │◀════════════════════════▶│         │
    └─────────┘                           │         │
    ┌─────────┐  redistribute cả 2 chiều  │  EIGRP  │
    │   R2    │◀════════════════════════▶│         │
    └────┬────┘                           └────┬────┘
         │                                      │
    ⚠️ Route OSPF → vào EIGRP ở R1 → chạy trong EIGRP →
       quay lại OSPF ở R2 → OSPF thấy đây là route "mới" (E2, AD 110)
       → có thể thắng route OSPF gốc → LOOP hoặc suboptimal routing
```

**3 cách chống:**

| Cách | Nguyên lý | Mức khuyến nghị |
|---|---|:---:|
| ⭐ **Route tag** | Đánh tag khi redistribute ra, **chặn tag đó** khi redistribute vào | ⭐⭐⭐ **Tốt nhất** |
| **Prefix-list / distribute-list** | Lọc theo prefix cụ thể | ⭐⭐ Được, nhưng phải bảo trì danh sách |
| **Đổi AD** | Tăng AD của route redistribute để IGP gốc thắng | ⭐ Dễ sai, dễ gây loop mới |

#### ⭐ Route tag — kỹ thuật chuẩn công nghiệp

```
! ═══ Trên R1: OSPF → EIGRP, đánh tag 100 ═══
route-map OSPF-TO-EIGRP permit 10
 match tag 200                        ! CHẶN route đã có tag 200 (từ EIGRP đi ra)
 ! → không có "set", và deny ở dưới
!
route-map OSPF-TO-EIGRP deny 5
 match tag 200
route-map OSPF-TO-EIGRP permit 10
 set tag 100                          ! đánh dấu "route này từ OSPF"
!
router eigrp 100
 redistribute ospf 1 metric 10000 100 255 1 1500 route-map OSPF-TO-EIGRP

! ═══ Trên R1: EIGRP → OSPF, đánh tag 200 ═══
route-map EIGRP-TO-OSPF deny 5
 match tag 100                        ! CHẶN route đã có tag 100 (từ OSPF đi ra)
route-map EIGRP-TO-OSPF permit 10
 set tag 200
!
router ospf 1
 redistribute eigrp 100 subnets route-map EIGRP-TO-OSPF
```

**Cấu hình y hệt trên R2.** Kết quả: route từ OSPF mang tag 100, khi cố quay lại OSPF ở R2
sẽ bị `deny` vì có tag 100 → **loop bị chặn**.

**Kiểm tra tag:**
```
show ip route 10.1.1.0 255.255.255.0        ! có dòng "Route tag 100"
show ip ospf database external              ! xem tag trong LSA type 5
show route-map                              ! đếm số route khớp từng dòng
```

> 🧠 **Ví von:** route tag như **con dấu trên hộ chiếu**. Route ra khỏi OSPF được dập dấu "đã từ OSPF ra".
> Khi nó xin quay lại OSPF ở cửa khác, hải quan thấy dấu → **từ chối nhập cảnh** → không có vòng lặp.

### 3.7 Route-map — công cụ đa dụng nhất của IOS

Bạn sẽ gặp `route-map` ở Module-05 (BGP), Module-06 (PBR) và Module-10 (Security). Học đúng ở đây.

**Cấu trúc:**
```
route-map <TÊN> <permit|deny> <sequence>
 match <điều kiện>                    ! nếu KHÔNG có match → khớp MỌI THỨ
 set <hành động>                      ! chỉ có tác dụng với permit
```

**4 quy tắc vàng của route-map:**

| # | Quy tắc | Hệ quả |
|:---:|---|---|
| 1 | Xử lý **từ sequence nhỏ đến lớn**, khớp thì **dừng** | Đặt câu cụ thể ở sequence nhỏ |
| 2 | ⭐ Cuối route-map có **implicit `deny`** | Route không khớp dòng nào → **bị loại** |
| 3 | ⭐ Statement **không có `match`** = khớp **mọi thứ** | Dùng làm dòng "catch-all" cuối |
| 4 | Nhiều `match` **cùng dòng** = **OR** · nhiều `match` **khác loại** = **AND** | `match ip address 1 2` = ACL 1 **hoặc** 2 |

**Các `match` hay dùng:**

| `match` | Khớp gì |
|---|---|
| `match ip address <acl/prefix-list>` | Prefix của route |
| `match ip next-hop <acl>` | Next-hop |
| `match tag <số>` | ⭐ Route tag |
| `match metric <số>` | Metric |
| `match interface <if>` | Route học qua interface nào |
| `match route-type internal\|external` | Loại route |
| `match as-path <số>` | (BGP) AS-path |
| `match community <số>` | (BGP) Community |

**Các `set` hay dùng:**

| `set` | Đặt gì |
|---|---|
| `set tag <số>` | ⭐ Đánh tag |
| `set metric <số>` | Metric |
| `set metric-type type-1\|type-2` | E1 / E2 cho OSPF |
| `set ip next-hop <ip>` | ⭐ Next-hop (dùng cho PBR) |
| `set local-preference <số>` | (BGP) Local Preference |
| `set weight <số>` | (BGP) Weight |
| `set as-path prepend <as>` | (BGP) AS-path prepend |

**Ví dụ đọc hiểu:**
```
route-map DEMO deny 10
 match ip address 10                  ! ACL 10 → BỊ LOẠI
route-map DEMO permit 20
 match tag 500
 set metric 100                       ! có tag 500 → cho qua, metric = 100
route-map DEMO permit 30              ! không có match → khớp mọi thứ còn lại
```
| Route | Kết quả |
|---|---|
| Khớp ACL 10 | ❌ Bị loại (deny 10) |
| Không khớp ACL 10, có tag 500 | ✅ Qua, metric 100 |
| Không khớp gì ở trên | ✅ Qua (permit 30 catch-all) |

⚠️ **Nếu bỏ dòng `permit 30`** → mọi route không khớp 2 dòng đầu sẽ bị **implicit deny** → mất hết.

### 3.8 🟡 PBR — Policy-Based Routing (bổ trợ, không bắt buộc ENCOR)

> ℹ️ PBR **không nằm rõ trong blueprint ENCOR** (nó thuộc ENARSI), nhưng hay xuất hiện trong
> câu hỏi kiểu "làm sao ép traffic đi đường không phải đường tốt nhất". Đọc để **hiểu**,
> không cần luyện sâu.

**Ý tưởng:** bình thường router forward theo **đích**. PBR cho phép forward theo **nguồn, port,
kích thước gói** — tức là "định tuyến theo chính sách", **bỏ qua bảng route**.

```
! Ví dụ: traffic từ mạng Kế toán đi ISP2, còn lại đi ISP1 (theo bảng route)
access-list 110 permit ip 192.168.10.0 0.0.0.255 any
!
route-map PBR-KETOAN permit 10
 match ip address 110
 set ip next-hop 198.51.100.2              ! ép đi ISP2
!
interface GigabitEthernet0/1                ! apply trên interface traffic ĐI VÀO
 ip policy route-map PBR-KETOAN
```

| Lệnh kiểm tra | Xem gì |
|---|---|
| `show ip policy` | Interface nào có PBR |
| `show route-map PBR-KETOAN` | Số gói đã khớp |
| `debug ip policy` | ⚠️ Xem PBR hoạt động (chỉ lab) |

> ⭐ **PBR + IP SLA:** dùng `set ip next-hop verify-availability <ip> <seq> track <n>` để PBR
> **tự bỏ qua** next-hop đã chết. Không có cái này thì PBR ép traffic vào hố đen khi ISP2 chết.

---

## 🧪 PHẦN 3 — NHÌN THẤY NÓ

> LAB đã tách ra file riêng để bạn **mở song song** với lý thuyết.

> ### 👉 **[LAB 03 — Tuần 6: Routing nền tảng](Module-03-LAB.md)**

| LAB | Nội dung | Trả lời câu hỏi | Ví von ở Phần 1 | Cơ chế ở Phần 2 |
|---|---|---|---|---|
| **03-1** | Đọc bảng route, chứng minh 3 bước chọn đường | Router chọn đường nào? | §2.1 GPS · §2.2 tra 2 lần | §3.1 · §3.2 |
| **03-2** | ⭐ IP SLA + Object Tracking | Đường "up" mà chết thì sao? | §2.3 hai cách kiểm tra | §3.4 |
| **03-3** | Redistribution + Route tag | Nối 2 protocol thì loop ra sao? | §2.6 con dấu hộ chiếu | §3.6 · §3.7 |

> ⚠️ **LAB 03-2 là bài quan trọng nhất module.** Nó dạy bạn một sự thật mà lý thuyết
> không truyền tải được: ⭐ **interface báo `up/up` KHÔNG có nghĩa là đường còn thông.**
>
> Bạn sẽ tự tay tạo ra tình huống "đường chết mà router không biết", rồi dùng IP SLA
> để router tự phát hiện. Kỹ thuật này quay lại ở **Module-06A** và **Module-11**.

---

## 🏗️ PHẦN 4 — TOPO & KIẾN TRÚC

> Bạn vừa học: 3 bước chọn đường, AD, static, IP SLA, EIGRP/OSPF, redistribution, route-map.
> Phần này ghép chúng vào **một mạng doanh nghiệp thật**.

### 4.1 Bản đồ: routing nằm ở đâu trong doanh nghiệp

```
                    ISP-1 (chính)          ISP-2 (dự phòng)
                       │                        │
                  203.0.113.1              198.51.100.1
                       │                        │
                  ┌────┴────────────────────────┴────┐
   ROUTER BIÊN    │   ⑤ Default route + IP SLA       │
                  │      "ISP còn sống không?"       │
                  │   ⑥ Floating static  AD 10       │
                  └───────────────┬──────────────────┘
                                  │
                  ┌───────────────┴──────────────────┐
   LÕI / DIST     │   ② OSPF — mạng CHÍNH của mình   │
                  │      (link-state, hội tụ nhanh)  │
                  │                                  │
                  │   ④ Redistribution ở ĐÂY         │
                  │      + route tag chống loop      │
                  └───┬──────────────────────────┬───┘
                      │                          │
          ┌───────────┴──────┐        ┌──────────┴───────────┐
   NHÁNH  │  ③ EIGRP         │        │  ① Static route      │
          │  (mạng công ty   │        │     (chi nhánh nhỏ,  │
          │   mua lại)       │        │      1 đường duy nhất)│
          └──────────────────┘        └──────────────────────┘
```

### 4.2 Sáu quyết định — và sai thì hỏng thế nào

| # | Quyết định | Vì sao | 🔴 Sai thì hỏng thế nào |
|:---:|---|---|---|
| ① | **Chi nhánh 1 đường → dùng STATIC** | Chỉ có một lối đi, chạy giao thức động là thừa | Chạy OSPF cho chi nhánh 1 link → tốn CPU, tốn băng thông hello, không được gì |
| ② | **Mạng chính → dùng OSPF** | Nhiều đường, cần hội tụ nhanh, cần chuẩn mở | Dùng static cho mạng 50 router → **không ai bảo trì nổi**, đứt link là sập |
| ③ | **Có 2 giao thức → không tránh được** | Sáp nhập công ty, thiết bị đa hãng | — |
| ④ | **Redistribution đặt ở ĐÚNG MỘT chỗ nếu được** | Hai điểm redistribute = **vòng lặp route** | Redistribute 2 chiều ở 2 router mà không tag → ⭐ **route quay vòng, mạng loạn** |
| ⑤ | **Default route ra ISP + IP SLA** | Interface `up` **không có nghĩa là ISP còn sống** | Chỉ dùng static thường → ISP chết mà router vẫn đẩy traffic ra → **mất mạng mà không ai biết vì sao** |
| ⑥ | **Floating static AD cao hơn** | Đường dự phòng chỉ vào khi đường chính rớt | Đặt cùng AD → **ECMP chia tải ra cả đường backup chậm** |

### 4.3 Ba sự thật mà chỉ người đi làm mới biết

| Sự thật | Giải thích |
|---|---|
| ⭐ **`up/up` KHÔNG có nghĩa là thông** | Cáp cắm vào switch của ISP, switch đó vẫn sống — nhưng **router ISP phía sau đã chết**. Interface bạn vẫn `up`. Đây là lý do **IP SLA tồn tại** |
| ⭐ **Redistribution là chỗ sinh sự cố nhiều nhất** | Nó nối hai thế giới có **metric khác nhau hoàn toàn** (OSPF cost vs EIGRP composite). Không có route tag = sớm muộn cũng loop |
| ⭐ **AD là "tin ai hơn", không phải "đường nào ngắn hơn"** | Static AD 1 **luôn thắng** OSPF AD 110, kể cả khi đường static đi vòng xa hơn. Router tin **nguồn tin**, không tự đánh giá đường |

### 4.4 Những thứ này sẽ lớn lên thành gì

| Bạn vừa học | Sẽ thành | Ở module |
|---|---|---|
| OSPF single-area, cost | LSA type 1–7, area stub/NSSA, summarization | **Module-04A/B** |
| AD, chọn đường | 13 bước path selection của BGP | **Module-05B** |
| IP SLA + track | HSRP tracking · đo jitter/MOS cho VoIP | **Module-06A · Module-11** |
| Route-map | Filtering BGP · PBR · NAT theo route-map | **Module-05B · Module-06B** |
| Redistribution | Nối SD-Access với mạng cũ qua border node | **Module-09** |

### 4.5 Vẽ lại để nhớ

> **Bài tập 15 phút, trên giấy.**
>
> 1. Vẽ lại sơ đồ §4.1 **không nhìn tài liệu**
> 2. Đánh dấu ① → ⑥
> 3. Trả lời: *"Nếu tôi redistribute hai chiều giữa OSPF và EIGRP ở CẢ HAI router nhánh, mà không dùng route tag — chuyện gì xảy ra?"*

<details>
<summary>Đáp án câu 3</summary>

Route từ OSPF chảy vào EIGRP ở router A → đi vòng trong EIGRP → tới router B →
router B redistribute **ngược lại** vào OSPF → OSPF thấy đó là route "mới" →
⭐ **route quay vòng vô tận (routing loop)**.

Tệ hơn nữa: route redistribute vào có **AD của external** (OSPF E2 = 110, EIGRP EX = 170),
nên nó có thể **thắng route gốc** → traffic đi đường vòng.

**Cách chặn:** gắn **route tag** khi redistribute vào, rồi **deny tag đó** khi redistribute ngược ra.
Đây chính là LAB 03-3.

</details>

---

## 💡 4.6 Thực chiến đi làm

| Chủ đề | Thi dạy | Thực tế đi làm |
|---|---|---|
| **Static route** | Cấu hình được | ⚠️ >20 dòng static = **nợ kỹ thuật**. Không ai nhớ dòng nào để làm gì. Luôn có tài liệu ghi rõ mỗi static route phục vụ cái gì, ai yêu cầu, ngày nào |
| **Static route syntax** | 3 kiểu | ⭐ Dùng **fully specified** (`Gi0/0 10.0.12.2`) — rõ ràng, tránh recursive lookup không mong muốn, và tránh lỗi ARP proxy trên multi-access |
| **`permanent`** | Có tùy chọn | ⛔ **Gần như không bao giờ dùng.** Nó giữ route dù interface down → traffic vào hố đen mà bảng route trông vẫn "đẹp" |
| ⭐ **Floating static** | Backup route | 🔴 **Không đủ cho production.** Phải đi kèm **IP SLA + track**. Đây là lỗi thiết kế phổ biến nhất ở dual-ISP: cấu hình floating static rồi tưởng đã có HA |
| ⭐ **IP SLA `source-interface`** | Ít nhắc | 🔴 **BẮT BUỘC.** Không có nó, SLA ping theo bảng route → khi ISP1 chết nó ping qua ISP2 và báo "OK" → track không bao giờ Down. **Lỗi rất khó tìm** |
| **IP SLA `delay down/up`** | Tùy chọn | ⭐ Luôn dùng, và `up` **lớn hơn** `down`. Không có delay → route flapping → CEF dựng lại FIB liên tục → CPU cao |
| **Track nhiều đích** | Không dạy | ⭐ Dùng `track <n> list boolean and` với 2–3 đích khác nhau (VD `8.8.8.8` + `1.1.1.1`). Một đích chết ≠ ISP chết |
| **`redistribute connected`** | Một lệnh | ⚠️ Đưa **mọi** subnet connected vào — kể cả mạng quản lý, mạng test, mạng không nên public. ⭐ **Luôn kèm route-map + prefix-list lọc** |
| ⭐ **Redistribute vào EIGRP/RIP** | Bảng seed metric | 🔴 Thiếu metric = route bị bỏ **âm thầm, không có log lỗi**. Đây là nguyên nhân của rất nhiều giờ debug vô ích |
| **`subnets` keyword** | Bẫy đề | ⭐ Cứ gõ luôn cho mọi `redistribute ... into ospf`. Gõ thêm không hại, thiếu thì mất route |
| **E1 vs E2** | Khái niệm | ⭐ Có **nhiều ASBR / nhiều điểm ra Internet** → dùng **E1** để traffic ra điểm gần nhất. Đây là quyết định thiết kế thật, không phải chi tiết học thuộc |
| ⭐ **Mutual redistribution** | Có thể gây loop | 🔴 **Luôn dùng route tag** ngay từ ngày đầu, kể cả khi mới có 1 điểm redistribute. Thêm điểm thứ 2 sau này mà không có tag = sự cố. Tag là chi phí bằng 0, bảo hiểm rất lớn |
| **Đổi AD** | 3 cách | ⚠️ Công cụ mạnh nhưng dễ gây loop nếu không đổi đồng bộ mọi router. Ưu tiên **route-map + tag** trước, đổi AD là phương án cuối |
| **Route-map** | Cú pháp | ⭐ **Luôn có dòng catch-all cuối** (`route-map X permit 999` không có match) nếu bạn muốn "chặn vài cái, cho qua phần còn lại". Thiếu nó = implicit deny = mất hết route |
| **`show route-map`** | Ít nhắc | ⭐ Có **counter số route/gói khớp từng dòng**. Đây là cách nhanh nhất kiểm tra route-map có thật sự hoạt động — nếu counter = 0 thì route-map không được gọi hoặc không khớp |
| **EIGRP** | Compare only cho ENCOR | ⭐ Ở Việt Nam nhiều doanh nghiệp vẫn chạy EIGRP (di sản Cisco-only). Biết **đọc** `show ip eigrp topology` là đủ để vận hành. Học cấu hình sâu khi nào thật cần |
| **Documentation** | Không có | ⭐ Mỗi lần thêm static/redistribute/route-map: ghi vào file (ngày, lý do, ai yêu cầu, cách hoàn tác). Không có tài liệu = 6 tháng sau chính bạn không dám xóa dòng nào |

---

# 📎 PHỤ LỤC — TRA CỨU

> 🔴 **KHÔNG đọc phần này ở lần học đầu tiên.**
>
> | Khi nào | Mở mục nào |
> |---|---|
> | Đang lab mà lỗi | **Gỡ lỗi nhanh** (§7) — quy trình 6 bước cho routing |
> | Quên lệnh | **Hộp lệnh** (§7.1) |
> | Tuần 20, ôn thi | **Bẫy đề** (§6) + **Quiz** (§8) |
> | Gặp từ lạ | **Thuật ngữ** (§9) |
> | Tự chấm | **Đúc kết** (§10) |

---

## 🎓 6. BẪY TRONG ĐỀ ENCOR

| # | Bẫy | Sự thật |
|:---:|---|---|
| 1 | ⭐ *"AD nhỏ hơn thì luôn thắng"* | ❌ **Longest prefix match ĐỨNG TRƯỚC AD.** `/24` RIP thắng `/16` OSPF |
| 2 | *"Blueprint ENCOR yêu cầu cấu hình EIGRP"* | ❌ Chỉ **compare** EIGRP với OSPF. Cấu hình thì chỉ **OSPF** và **eBGP** |
| 3 | EIGRP là loại protocol gì | ⭐ **Advanced Distance Vector** (không phải link-state, không phải "hybrid" theo cách gọi cũ) |
| 4 | Thuật toán EIGRP / OSPF | **DUAL** / **Dijkstra SPF** |
| 5 | ⭐ Protocol nào hỗ trợ **unequal-cost load balancing** | **EIGRP** (`variance`). OSPF **chỉ** equal-cost |
| 6 | ⭐ MTU có trong công thức metric EIGRP? | ❌ **KHÔNG.** Mặc định chỉ **Bandwidth (K1) + Delay (K3)**. MTU chỉ được gửi kèm |
| 7 | EIGRP metric: bandwidth lấy thế nào? Delay? | Bandwidth = **NHỎ NHẤT** trên đường (bottleneck) · Delay = **CỘNG DỒN** |
| 8 | Feasibility Condition | ⭐ **RD < FD** (neighbor phải gần đích hơn tôi) |
| 9 | SIA là gì | **Stuck-In-Active** — query lan quá xa / không ai trả lời → route bị xóa |
| 10 | EIGRP summarization ở đâu | ⭐ **Bất kỳ đâu.** OSPF **chỉ ở ABR/ASBR** |
| 11 | AD của EIGRP internal / external | **90** / **170** |
| 12 | Multicast: EIGRP / OSPF | **224.0.0.10** / **224.0.0.5** và **224.0.0.6** |
| 13 | IP protocol number: EIGRP / OSPF | **88** / **89** |
| 14 | ⭐ Seed metric khi redistribute vào **EIGRP/RIP** | ⚠️ **INFINITE** → **bắt buộc** chỉ định metric, nếu không route bị bỏ |
| 15 | Seed metric khi redistribute vào **OSPF** | **20** (từ BGP: **1**), type **E2** |
| 16 | Thiếu `subnets` khi redistribute vào OSPF | Chỉ redistribute **classful network**, **bỏ hết subnet** |
| 17 | ⭐ **E1 vs E2** | **E1** = external + internal cost tới ASBR (chọn ASBR gần) · **E2** = **chỉ** external, không đổi toàn domain |
| 18 | Thứ tự ưu tiên route OSPF | **Intra (O) → Inter (O IA) → E1 → E2**. Áp dụng **trước** khi so metric |
| 19 | Static route trong config mà không trong `show ip route` | **Recursive lookup thất bại** — next-hop không reachable |
| 20 | ⭐ Floating static có phát hiện "đích chết, link up"? | ❌ **KHÔNG.** Cần **IP SLA + track** |
| 21 | Quên `ip sla schedule ... start-time now` | SLA **không chạy** → track Down → route bị xóa. Kiểm tra `Operation time to live` |
| 22 | IP SLA thiếu `source-interface` | ⚠️ SLA ping theo bảng route → có thể đi qua đường dự phòng → **không bao giờ phát hiện lỗi** |
| 23 | AD 255 nghĩa là gì | **Không cài vào RIB** |
| 24 | Route-map không có `match` | ⭐ Khớp **MỌI THỨ** (catch-all) |
| 25 | Cuối route-map có gì | ⭐ **Implicit deny** — route không khớp dòng nào bị loại |
| 26 | Nhiều `match` cùng dòng vs khác dòng | Cùng dòng (`match ip address 1 2`) = **OR** · Khác loại `match` = **AND** |
| 27 | ⭐ Chống mutual redistribution loop | **Route tag** (tốt nhất) · prefix-list · đổi AD (dễ sai) |
| 28 | Tag được mang ở đâu trong OSPF | **LSA type 5** — trường `External Route Tag` |

---

## 🐛 7. GỠ LỖI NHANH

### 7.1 Hộp lệnh vạn năng

```
! === Bảng định tuyến ===
show ip route                                ! toàn bộ RIB
show ip route <ip>                           ! route nào được dùng + AD + metric + tag
show ip route static                         ! chỉ static ĐÃ VÀO RIB
show ip route ospf                           ! chỉ OSPF
show ip route connected
show ip route | include ^O E2|^O E1           ! chỉ external
show ip route summary                        ! đếm route theo nguồn
show ip protocols                            ! protocol nào chạy, redistribute gì, passive
show ip cef <ip>                             ! FIB nói gì (Module-01)

! === So sánh config vs RIB (tìm recursion fail) ===
show running-config | include ip route        ! static đã CẤU HÌNH
show ip route static                          ! static đã VÀO RIB
! → Có trong config mà không trong RIB = recursion thất bại

! === IP SLA + Track ===
show ip sla configuration <n>                 ! cấu hình
show ip sla statistics <n>                    ! return code, successes/failures, RTT
show ip sla summary
show track                                    ! mọi track object
show track <n>                                ! chi tiết + "Tracked by"
debug ip sla trace <n>                        ! ⚠️ chỉ lab
debug track                                   ! ⚠️ chỉ lab

! === Redistribution ===
show ip protocols | section ospf              ! redistribute gì vào OSPF
show ip ospf database external                ! LSA type 5 + tag + metric type
show ip ospf database external <prefix>
show route-map                                ! counter số route khớp từng dòng
show route-map <TÊN>
show ip prefix-list
show ip prefix-list detail <TÊN>              ! có counter hit

! === EIGRP (đọc hiểu, không cấu hình) ===
show ip eigrp neighbors
show ip eigrp topology                        ! FD, RD, Successor, FS
show ip eigrp topology <prefix>               ! chi tiết 1 prefix
show ip eigrp interfaces

! === PBR ===
show ip policy
show route-map <TÊN>
debug ip policy                               ! ⚠️ chỉ lab
```

### 7.2 Bảng lỗi: triệu chứng → nguyên nhân → cách sửa

| # | Triệu chứng | Nguyên nhân | Cách sửa |
|:---:|---|---|---|
| 1 | Static route trong `show run` mà **không** trong `show ip route` | ⭐ **Recursive lookup thất bại** — next-hop không reachable | `ping <next-hop>` · `show ip route <next-hop>` · dùng **fully specified** (`Gi0/0 10.0.12.2`) |
| 2 | Route "vô lý" được chọn thay vì route bạn mong đợi | Longest prefix match — có route cụ thể hơn | ⭐ `show ip route <ip đích>` → xem prefix nào đang thắng |
| 3 | Route mong đợi không được dùng dù AD tốt | Có route prefix **dài hơn** từ nguồn khác | `show ip route <ip>` · so prefix, không so AD trước |
| 4 | Redistribute rồi mà bên kia **không có route** | ⭐ Vào EIGRP/RIP: **thiếu metric** · Vào OSPF: **thiếu `subnets`** · route-map implicit deny | `show ip protocols` · thêm `metric`/`default-metric` · thêm `subnets` · thêm dòng catch-all vào route-map |
| 5 | Redistribute chỉ vào **một phần** subnet | Thiếu `subnets` (chỉ classful) | Thêm `subnets` |
| 6 | Route external có metric **không đổi** dù đi xa | ✅ Bình thường — đây là **E2** | Muốn phản ánh khoảng cách → dùng `metric-type 1` |
| 7 | Traffic ra Internet chọn ASBR **xa** thay vì gần | Dùng **E2** (không tính internal cost) | Chuyển sang **E1** (`metric-type 1`) trên mọi ASBR |
| 8 | ⭐ Routing loop / route "nhảy qua nhảy lại" sau khi thêm điểm redistribute thứ 2 | **Mutual redistribution không có tag** | Thêm **route tag**: `set tag` khi ra, `match tag` + `deny` khi vào |
| 9 | Route bị mất bất ngờ sau khi thêm route-map | ⭐ **Implicit deny** ở cuối route-map | Thêm dòng catch-all: `route-map X permit 999` (không có `match`) |
| 10 | Route-map "không có tác dụng" | Chưa được gọi, hoặc match không khớp | ⭐ `show route-map` → xem **counter**. Counter = 0 → không được gọi hoặc không khớp |
| 11 | ⭐ IP SLA `Number of successes: 0`, `time to live: 0` | ⭐ **Quên `ip sla schedule <n> life forever start-time now`** | Thêm dòng schedule |
| 12 | Track luôn `Up` dù đường chính đã chết | ⭐ **Thiếu `source-interface`** → SLA ping qua đường dự phòng | Thêm `source-interface <if đường chính>` |
| 13 | Track `Down` ngay khi vừa cấu hình | SLA chưa chạy đủ chu kỳ, hoặc đích không ping được từ đầu | `show ip sla statistics` · thử ping tay từ đúng source |
| 14 | Route flapping liên tục (up/down/up) | Thiếu `delay down/up` trong track, hoặc `frequency` quá ngắn | `track <n> ip sla <n> reachability` → `delay down 3 up 10` |
| 15 | Failover xảy ra nhưng **không hồi phục** | `delay up` quá lớn, hoặc SLA vẫn fail qua đường chính | `show track` xem `Reachability` · `show ip sla stat` |
| 16 | Sau khi đổi AD, mạng bị loop | AD đổi không đồng bộ giữa các router | ⛔ Hoàn tác ngay · dùng route tag thay vì đổi AD |
| 17 | `show ip route` có ECMP mà traffic chỉ đi 1 đường | ✅ Bình thường — CEF per-destination hash (Module-01) | `show ip cef exact-route <src> <dst>` để xác nhận |
| 18 | PBR không hoạt động | Apply sai chiều/interface, hoặc next-hop không reachable | `show ip policy` · `show route-map` counter · apply trên interface traffic **đi vào** |
| 19 | PBR ép traffic vào hố đen khi next-hop chết | PBR **không tự kiểm tra** next-hop | Dùng `set ip next-hop verify-availability <ip> <seq> track <n>` |
| 20 | Không có `Gateway of last resort` | Chưa có default route | `ip route 0.0.0.0 0.0.0.0 <gw>` · hoặc `default-information originate` (OSPF, Module-04) |

### 7.3 Quy trình troubleshoot routing — 6 bước

```
1. LỚP 1-2 TRƯỚC (Module-P0, Module-02)
   show ip interface brief      → up/up?
   ping <next-hop>              → L2/L3 local thông?
        ↓
2. ROUTE CÓ TRONG RIB?
   show ip route <ip đích>
   ├─ KHÔNG có → sang bước 3
   └─ CÓ nhưng "sai" đường → sang bước 4
        ↓
3. VÌ SAO ROUTE KHÔNG CÓ?
   · Static?         → recursion fail? show ip route <next-hop>
   · Từ protocol?    → show ip ospf neighbor (Full?) · show ip protocols
   · Redistribute?   → thiếu metric (EIGRP/RIP)? thiếu subnets (OSPF)?
                       route-map implicit deny? → show route-map counter
        ↓
4. VÌ SAO CHỌN ĐƯỜNG NÀY?
   show ip route <ip đích>
   → Đọc theo đúng 3 bước:
     a) Prefix bao nhiêu? Có route nào prefix DÀI HƠN không?
     b) AD bao nhiêu? Có nguồn nào AD NHỎ HƠN cùng prefix không?
     c) Metric bao nhiêu? Có ECMP không?
        ↓
5. FORWARDING THẬT SỰ (Module-01)
   show ip cef <ip đích>            → FIB có khớp RIB?
   show ip cef exact-route <s> <d>  → flow này đi đâu?
   traceroute <ip> source <ip>      → đường thật
        ↓
6. CÓ GÌ CHẶN/DỊCH KHÔNG?
   show access-lists                → ACL
   show ip nat translations         → NAT (Module-06)
   show ip policy                   → PBR
```

> ⭐ **Bước 4 là bước phân biệt người mới với người có kinh nghiệm.** Người mới nhìn `show ip route`
> rồi nói "route sai". Người có kinh nghiệm đọc **prefix → AD → metric** theo đúng thứ tự
> và giải thích được **vì sao** router chọn như vậy — rồi mới quyết định sửa gì.

---

## 📝 8. QUIZ TỰ KIỂM TRA

**Câu 1.** Router nhận gói tới `172.16.5.100`. Bảng route có:

| Route | Nguồn | AD | Metric |
|---|---|:---:|:---:|
| `172.16.0.0/16` | Static | 1 | 0 |
| `172.16.4.0/22` | EIGRP | 90 | 3072 |
| `172.16.5.0/24` | RIP | 120 | 5 |
| `0.0.0.0/0` | OSPF | 110 | 10 |

Route nào được dùng?

<details><summary>Xem đáp án</summary>

**`172.16.5.0/24` (RIP).**

Bước 1 — Longest prefix match. Kiểm tra route nào **khớp** `172.16.5.100`:
- `172.16.0.0/16` ✅ khớp (16 bit)
- `172.16.4.0/22` ✅ khớp (`/22` = `172.16.4.0`–`172.16.7.255`, chứa `172.16.5.100`) — 22 bit
- `172.16.5.0/24` ✅ khớp — **24 bit ← dài nhất**
- `0.0.0.0/0` ✅ khớp (0 bit)

→ `/24` thắng. **AD 120 (tệ nhất) không quan trọng** vì AD chỉ được xét khi các route **cùng prefix**.

⭐ Đây là bẫy đề số 1 của module này.
</details>

---

**Câu 2.** Blueprint ENCOR yêu cầu gì về EIGRP? Bạn nên dành bao nhiêu thời gian cho nó?

<details><summary>Xem đáp án</summary>

**Chỉ yêu cầu SO SÁNH (compare) EIGRP với OSPF** — mục 3.2.a:
*"Compare routing concepts of EIGRP and OSPF (advanced distance vector vs. link state,
load balancing, path selection, path operations, metrics)"*.

**KHÔNG yêu cầu cấu hình EIGRP.** Mục 3.2.b nói rõ *"Configure and verify simple **OSPF**
environments"* — chỉ OSPF. Và 3.2.c là **eBGP**.

**Thời gian nên dành:** ~2 giờ để nắm bảng so sánh (loại protocol, thuật toán, metric, AD,
unequal-cost LB, summarization, multicast, protocol number). **Không cần** lab cấu hình EIGRP.

⚠️ Nếu sau này thi **ENARSI (300-410)** thì mới cần EIGRP sâu.
</details>

---

**Câu 3.** Nêu 5 khác biệt quan trọng nhất giữa EIGRP và OSPF (dạng đề hỏi trực tiếp).

<details><summary>Xem đáp án</summary>

| | **EIGRP** | **OSPF** |
|---|---|---|
| **1. Loại protocol** | Advanced **Distance Vector** | **Link-State** |
| **2. Thuật toán** | **DUAL** | **Dijkstra SPF** |
| **3. Unequal-cost LB** | ⭐ **CÓ** (`variance`) | ⭐ **KHÔNG** (chỉ ECMP) |
| **4. Summarization** | ⭐ **Bất kỳ đâu** | ⭐ **Chỉ ABR/ASBR** |
| **5. Cần thiết kế phân cấp** | ❌ Không bắt buộc | ⭐ **Có** (area, area 0 backbone) |

**Bổ sung hay hỏi:**
- Metric: EIGRP = composite **Bandwidth + Delay** · OSPF = **cost = ref-bw / int-bw**
- AD: EIGRP **90**/170 · OSPF **110**
- Multicast: **224.0.0.10** · **224.0.0.5**/224.0.0.6
- IP protocol: **88** · **89**
- Chuẩn: Cisco (RFC 7868 informational) · **Open standard** RFC 2328
</details>

---

**Câu 4.** Trong EIGRP: FD = 3000, có 3 neighbor báo RD lần lượt 2500, 3200, 1800.
Neighbor nào có thể làm **Feasible Successor**? Vì sao?

<details><summary>Xem đáp án</summary>

**Neighbor có RD = 2500 và RD = 1800.**

**Feasibility Condition: `RD < FD`**

| Neighbor | RD | RD < FD (3000)? | Là FS? |
|---|:---:|:---:|:---:|
| A | 2500 | ✅ 2500 < 3000 | ✅ **Có** |
| B | 3200 | ❌ 3200 > 3000 | ❌ Không |
| C | 1800 | ✅ 1800 < 3000 | ✅ **Có** |

**Vì sao điều kiện này chống loop:** nếu neighbor báo khoảng cách của **nó** tới đích
**nhỏ hơn** khoảng cách hiện tại của **tôi**, thì nó **không thể** đi qua tôi để tới đích
(nếu đi qua tôi thì khoảng cách của nó phải lớn hơn của tôi).

Neighbor B (RD 3200 > FD 3000) có thể đang tính đường **đi qua tôi** → dùng nó = **loop**.

**Hệ quả:** khi Successor chết, router dùng ngay FS — **tính toán local, không cần query ai**
→ hội tụ gần như tức thì. Không có FS thì phải gửi **query** → nguy cơ **SIA**.
</details>

---

**Câu 5.** MTU có nằm trong công thức tính metric của EIGRP không?

<details><summary>Xem đáp án</summary>

**KHÔNG.**

Với **K values mặc định (K1=1, K2=0, K3=1, K4=0, K5=0)**, metric chỉ dùng:
- **K1 = Bandwidth** (lấy giá trị **nhỏ nhất** trên đường đi — bottleneck)
- **K3 = Delay** (**cộng dồn** delay của mọi interface)

```
Metric = 256 × [ (10^7 / min-bandwidth-kbps) + (tổng delay-microsec / 10) ]
```

**MTU (K5) mặc định tắt.** MTU được **gửi kèm** trong EIGRP update (bạn thấy nó trong
`show ip eigrp topology`) nhưng **không tham gia tính metric** — nó chỉ là tie-breaker.

Load (K2) và Reliability (K4) cũng tắt mặc định — bật lên sẽ gây **route flapping**
vì chúng thay đổi liên tục theo tải.

⭐ Đây là bẫy đề rất phổ biến.
</details>

---

**Câu 6.** Bạn redistribute static route vào EIGRP nhưng bên kia không có route nào. Config đúng cú pháp,
không có log lỗi. Nguyên nhân?

<details><summary>Xem đáp án</summary>

**Thiếu seed metric.**

| Redistribute VÀO | Seed metric mặc định | Cần chỉ định tay? |
|---|---|:---:|
| **EIGRP** | ⚠️ **INFINITE** | ⭐ **BẮT BUỘC** |
| **RIP** | ⚠️ **INFINITE** | ⭐ **BẮT BUỘC** |
| OSPF | 20 (từ BGP: 1) | ❌ Không cần |
| BGP | Metric IGP → MED | ❌ Không cần |

Seed metric = infinite → EIGRP coi route **không thể tới được** → **bỏ âm thầm**, không log lỗi.

**Sửa:**
```
router eigrp 100
 redistribute static metric 10000 100 255 1 1500
!                    bw    delay rel load MTU
! Hoặc:
 default-metric 10000 100 255 1 1500
 redistribute static
```

⭐ Đây là nguyên nhân của rất nhiều giờ debug vô ích. Ghi vào sổ tay lỗi.
</details>

---

**Câu 7.** Mạng OSPF có 2 ASBR (R2 gần, R5 xa) đều redistribute `0.0.0.0/0`.
Bạn muốn mỗi router nội bộ ra Internet qua **ASBR gần nhất**. Dùng E1 hay E2? Vì sao?

<details><summary>Xem đáp án</summary>

**Dùng E1** (`metric-type 1`).

| | **E2** (mặc định) | **E1** |
|---|---|---|
| Metric | **Chỉ** external cost — **không đổi** trong toàn domain | ⭐ External cost **+ internal cost tới ASBR** |
| Phân biệt ASBR gần/xa? | ❌ Cả 2 ASBR cùng metric 20 | ⭐ ✅ ASBR gần có metric nhỏ hơn |

Với **E2**: mọi router nội bộ thấy `0.0.0.0/0` metric 20 từ **cả hai** ASBR
→ không phân biệt được → có thể ECMP hoặc chọn theo forward metric (không đảm bảo).

Với **E1**: router gần R2 thấy metric = 20 + (cost tới R2, VD 10) = **30**,
và metric = 20 + (cost tới R5, VD 100) = **120** → chọn **R2** ✅.

**Cấu hình (trên MỌI ASBR):**
```
router ospf 1
 redistribute static subnets metric-type 1
```
⚠️ Phải đặt **giống nhau trên mọi ASBR**, nếu không sẽ so sánh lệch.
</details>

---

**Câu 8.** Static route này có trong `show running-config` nhưng **không** có trong `show ip route`.
Nguyên nhân và cách sửa?
```
ip route 10.5.5.0 255.255.255.0 172.16.99.99
```

<details><summary>Xem đáp án</summary>

**Recursive lookup thất bại** — router không có route tới next-hop `172.16.99.99`.

Static route kiểu next-hop cần **2 lần tra cứu**:
1. "Đi `10.5.5.0/24` → next-hop `172.16.99.99`"
2. ⚠️ "Nhưng `172.16.99.99` ở đâu?" → tra RIB → **không có** → route **không được cài**

**Kiểm tra:**
```
show ip route 172.16.99.99          ! có route tới next-hop không?
ping 172.16.99.99                   ! reachable không?
```

**Cách sửa:**
1. Sửa next-hop cho đúng (IP của router kề)
2. Hoặc dùng **fully specified** — an toàn hơn:
   ```
   ip route 10.5.5.0 255.255.255.0 GigabitEthernet0/0 172.16.99.99
   ```
3. Hoặc dùng **exit interface** (chỉ với link P2P):
   ```
   ip route 10.5.5.0 255.255.255.0 GigabitEthernet0/0
   ```

⭐ **Cách phát hiện nhanh:** so sánh
`show running-config | include ip route` (đã cấu hình) với
`show ip route static` (đã vào RIB). Chênh lệch = recursion fail.
</details>

---

**Câu 9.** Bạn cấu hình dual-ISP với floating static. Link tới ISP1 vẫn `up`, nhưng router core
của ISP1 chết nên traffic không ra được Internet. Route có failover sang ISP2 không?
Giải pháp đúng là gì?

<details><summary>Xem đáp án</summary>

**KHÔNG failover.**

Floating static chỉ theo dõi: (a) trạng thái **interface local**, (b) **next-hop có reachable không**.
Cả hai đều bình thường → route chính (AD 1) vẫn trong RIB → route dự phòng (AD 200) **không được kích hoạt**
→ **traffic vào hố đen**.

**Giải pháp: IP SLA + Object Tracking**

```
! 1. IP SLA — ping THẬT một đích trên Internet, qua ĐÚNG đường ISP1
ip sla 1
 icmp-echo 8.8.8.8 source-interface GigabitEthernet0/0    ! source-interface BẮT BUỘC
 frequency 5
 timeout 2000
ip sla schedule 1 life forever start-time now              ! KHÔNG ĐƯỢC QUÊN

! 2. Track theo dõi kết quả
track 1 ip sla 1 reachability
 delay down 3 up 5                                         ! chống flapping

! 3. Gắn track vào static route
ip route 0.0.0.0 0.0.0.0 203.0.113.2 track 1               ! ISP1
ip route 0.0.0.0 0.0.0.0 198.51.100.2 200                  ! ISP2 dự phòng
```

**Hai điểm dễ sai nhất:**
1. ⭐ **Quên `ip sla schedule`** → SLA không chạy → track Down ngay → route bị xóa.
   Kiểm tra: `show ip sla statistics 1` → `Operation time to live` phải là `Forever`
2. ⭐ **Thiếu `source-interface`** → SLA ping theo bảng route → khi ISP1 chết nó ping qua ISP2
   và báo "OK" → **track không bao giờ Down**. Lỗi rất khó tìm

**Nâng cao:** dùng `track <n> list boolean and` với 2–3 đích khác nhau —
một đích chết không có nghĩa ISP chết.
</details>

---

**Câu 10.** Route-map này apply vào redistribution. Kết quả với 3 route bên dưới?

```
route-map RM deny 10
 match tag 100
route-map RM permit 20
 match ip address prefix-list PL-A
 set metric 50
```

| Route | Tag | Khớp PL-A? |
|---|:---:|:---:|
| `10.1.1.0/24` | 100 | ✅ |
| `10.2.2.0/24` | — | ✅ |
| `10.3.3.0/24` | — | ❌ |

<details><summary>Xem đáp án</summary>

| Route | Kết quả | Vì sao |
|---|---|---|
| `10.1.1.0/24` | ❌ **Bị loại** | Khớp `deny 10` (tag 100) → dừng ngay |
| `10.2.2.0/24` | ✅ **Được redistribute, metric 50** | Không khớp deny 10 → khớp `permit 20` |
| `10.3.3.0/24` | ❌ **Bị loại** | Không khớp dòng nào → ⭐ **implicit deny** ở cuối route-map |

⭐ **Nếu bạn muốn `10.3.3.0/24` được redistribute** (chỉ chặn tag 100), phải thêm **catch-all**:
```
route-map RM permit 999
!  (không có match → khớp MỌI THỨ còn lại)
```

**Bài học:** đây là lỗi phổ biến nhất khi dùng route-map — quên rằng cuối route-map có
**implicit deny**. "Tôi chỉ muốn chặn vài cái" nhưng thực tế **chặn hết những gì không khớp**.

**Cách kiểm tra:** `show route-map RM` → xem **counter** từng dòng.
</details>

---

**Câu 11.** Mutual redistribution giữa OSPF và EIGRP tại 2 router (R1 và R2). Vì sao có thể loop,
và cách chống chuẩn công nghiệp là gì?

<details><summary>Xem đáp án</summary>

**Vì sao loop:**
1. Route `X` gốc từ OSPF
2. R1 redistribute `X` **OSPF → EIGRP** → `X` giờ là route EIGRP
3. `X` chạy trong domain EIGRP tới R2
4. R2 redistribute `X` **EIGRP → OSPF** → `X` quay lại OSPF dưới dạng **external E2, AD 110**
5. ⚠️ Router nào đó có thể thấy route E2 này **tốt hơn** route OSPF gốc (VD prefix giống nhưng
   đường ngắn hơn về mặt cost) → chọn route đã "đi vòng" → **loop hoặc suboptimal routing**

**Cách chống chuẩn: ROUTE TAG**

```
! ═══ Trên CẢ R1 và R2 (giống nhau) ═══

! OSPF → EIGRP: chặn route đã từ EIGRP ra (tag 200), đánh dấu 100
route-map OSPF-TO-EIGRP deny 5
 match tag 200
route-map OSPF-TO-EIGRP permit 10
 set tag 100

! EIGRP → OSPF: chặn route đã từ OSPF ra (tag 100), đánh dấu 200
route-map EIGRP-TO-OSPF deny 5
 match tag 100
route-map EIGRP-TO-OSPF permit 10
 set tag 200

router eigrp 100
 redistribute ospf 1 metric 10000 100 255 1 1500 route-map OSPF-TO-EIGRP
router ospf 1
 redistribute eigrp 100 subnets route-map EIGRP-TO-OSPF
```

**Nguyên lý:** route được **dập dấu nguồn gốc**. Khi nó cố quay lại protocol gốc ở điểm
redistribute khác → bị nhận diện và **từ chối**.

**Kiểm tra:** `show ip route <prefix>` → dòng `Tag 100` ·
`show ip ospf database external` → `External Route Tag: 100`

**Hai cách khác** (kém hơn): prefix-list/distribute-list (phải bảo trì danh sách),
đổi AD (dễ gây loop mới nếu không đồng bộ).

⭐ **Thực chiến:** dùng tag **ngay từ ngày đầu**, kể cả khi mới có 1 điểm redistribute.
Chi phí bằng 0, và ngày bạn thêm điểm thứ 2 sẽ không thành sự cố.
</details>

---

**Câu 12.** `show ip sla statistics 1` cho ra output này. Vấn đề là gì?
```
IPSLA operation id: 1
        Latest RTT: NoConnection/Busy/Timeout
Latest operation return code: No connection
Number of successes: 0
Number of failures: 0
Operation time to live: 0
```

<details><summary>Xem đáp án</summary>

⭐ **`Operation time to live: 0` + `successes: 0` + `failures: 0`** → **SLA chưa bao giờ chạy.**

**Nguyên nhân: quên dòng schedule.**

```
ip sla schedule 1 life forever start-time now
```

**Cách nhận biết:** nếu SLA **đang chạy mà fail**, bạn sẽ thấy `Number of failures` **tăng dần**.
Ở đây **cả successes và failures đều = 0** → nghĩa là operation chưa được kích hoạt lần nào.

**Hậu quả nếu không phát hiện:** track object sẽ ở trạng thái `Down` →
static route có `track` bị **xóa khỏi RIB** → traffic chuyển hết sang đường dự phòng
(hoặc mất kết nối nếu không có dự phòng). Và bạn sẽ debug OSPF/interface/ACL cả buổi
trong khi lỗi chỉ là thiếu 1 dòng.

**Sau khi thêm schedule, xác nhận:**
```
show ip sla statistics 1
! Mong đợi:
!   Latest operation return code: OK
!   Number of successes: <tăng dần>
!   Operation time to live: Forever
show track 1
! Mong đợi: Reachability is Up
```
</details>

---

## 📚 9. THUẬT NGỮ ANH–VIỆT

| Tiếng Anh | Tiếng Việt | Ghi chú |
|---|---|---|
| **RIB** (Routing Information Base) | Cơ sở dữ liệu định tuyến | `show ip route` |
| **FIB** (Forwarding Information Base) | Cơ sở dữ liệu chuyển tiếp | `show ip cef` (Module-01) |
| **Longest prefix match** | Khớp tiền tố dài nhất | ⭐ **Bước 1**, đứng trước AD |
| **Administrative Distance (AD)** | Khoảng cách quản trị | Mức tin cậy nguồn route. Bước 2 |
| Metric | Số đo / chi phí | Trong cùng protocol. Bước 3 |
| **ECMP** (Equal-Cost Multi-Path) | Đa đường chi phí bằng nhau | Cùng prefix, cùng AD, cùng metric |
| **Recursive lookup** | Tra cứu đệ quy | Tra next-hop, rồi tra đường tới next-hop |
| Fully specified static route | Static route chỉ định đầy đủ | Có cả exit interface **và** next-hop |
| **Floating static** | Static route "nổi" | AD cao → dự phòng. ⚠️ Không biết đích chết |
| Null route / blackhole | Route hố đen | Trỏ vào `Null0` |
| Gateway of last resort | Cổng cuối cùng | Default route `0.0.0.0/0` |
| **IP SLA** | Thỏa thuận mức dịch vụ IP | Chủ động đo/ping để kiểm tra đường |
| **Object tracking** | Theo dõi đối tượng | Nối kết quả IP SLA vào route/HSRP/PBR |
| Reachability | Khả năng tới được | Loại track hay dùng nhất |
| `delay down/up` | Độ trễ báo xuống/lên | ⭐ Chống route flapping |
| `source-interface` | Interface nguồn | ⭐ Bắt buộc — để SLA đi đúng đường cần kiểm |
| Route flapping | Route nhấp nháy | Route liên tục vào/ra RIB |
| **Distance Vector** | Vector khoảng cách | Chỉ biết "hướng nào, xa bao nhiêu" |
| **Advanced Distance Vector** | Vector khoảng cách nâng cao | ⭐ EIGRP |
| **Link-State** | Trạng thái liên kết | ⭐ OSPF — có bản đồ toàn mạng |
| **DUAL** (Diffusing Update Algorithm) | Thuật toán cập nhật khuếch tán | Thuật toán của EIGRP |
| **Dijkstra SPF** | Thuật toán đường ngắn nhất | Thuật toán của OSPF |
| **FD** (Feasible Distance) | Khoảng cách khả thi | Metric tốt nhất **của tôi** tới đích |
| **RD** (Reported Distance) | Khoảng cách được báo | Metric mà **neighbor** báo |
| **Successor** | Người kế vị | Route chính, vào RIB |
| **Feasible Successor (FS)** | Người kế vị khả thi | ⭐ Route dự phòng đã kiểm chứng không loop |
| **Feasibility Condition** | Điều kiện khả thi | ⭐ **RD < FD** |
| **SIA** (Stuck-In-Active) | Kẹt ở trạng thái Active | Query lan quá xa → route bị xóa |
| Composite metric | Metric tổng hợp | EIGRP: Bandwidth + Delay |
| **K values** | Hệ số K | K1=bw, K2=load, K3=delay, K4=rel, K5=MTU. Mặc định chỉ K1, K3 |
| Wide metric | Metric rộng (64-bit) | EIGRP named mode — phân biệt link 10G/40G/100G |
| **Variance** | Hệ số dao động | ⭐ EIGRP unequal-cost load balancing |
| Unequal-cost load balancing | Chia tải chi phí không bằng | ⭐ **Chỉ EIGRP**, OSPF không có |
| **Redistribution** | Phân phối lại route | Đưa route từ protocol A sang B |
| **Seed metric** | Metric hạt giống | ⭐ Metric ban đầu khi vào protocol mới |
| `subnets` keyword | Từ khóa subnets | Thiếu = chỉ redistribute classful network |
| **E1** (External Type 1) | Ngoại vi loại 1 | External cost **+ internal cost** tới ASBR |
| **E2** (External Type 2) | Ngoại vi loại 2 | ⭐ **Chỉ** external cost, không đổi toàn domain |
| **ASBR** (AS Boundary Router) | Router biên hệ tự trị | Router làm redistribution vào OSPF |
| **Mutual redistribution** | Phân phối lại hai chiều | ⚠️ Nguy cơ loop nếu không có tag |
| **Route tag** | Nhãn route | ⭐ "Con dấu hộ chiếu" chống loop |
| **Route-map** | Bản đồ route | Công cụ lọc/sửa thuộc tính route |
| Implicit deny | Chặn ngầm | ⭐ Dòng deny ẩn ở cuối route-map |
| Catch-all statement | Câu bắt tất cả | `permit` không có `match` |
| **Prefix-list** | Danh sách tiền tố | Lọc route theo prefix + độ dài mask |
| Distribute-list | Danh sách phân phối | Lọc route vào/ra protocol |
| **PBR** (Policy-Based Routing) | Định tuyến theo chính sách | Forward theo nguồn/port, bỏ qua bảng route |
| `verify-availability` | Kiểm tra khả dụng | PBR + track → không ép vào hố đen |

---

## 🎯 10. ĐÚC KẾT MODULE-03

**3 điều rút ra:**

1. **`Longest prefix → AD → Metric`, đúng thứ tự này, không đổi.** Longest prefix match
   **đứng trước** AD — một route `/24` từ RIP (AD 120) thắng route `/16` từ OSPF (AD 110).
   Mọi câu "vì sao router chọn đường này" đều trả lời được bằng cách đọc theo đúng 3 bước.

2. **Interface `up` không có nghĩa là đích còn sống.** Floating static tin vào trạng thái interface —
   đó là lỗ hổng thật gây sự cố ở production. **IP SLA + object tracking** vá lỗ hổng đó bằng cách
   **thực sự ping đích**. Hai điều dễ sai nhất: quên `ip sla schedule` và thiếu `source-interface`.

3. **Redistribution là chỗ dễ mất route nhất, và luôn dùng route tag.** Vào EIGRP/RIP **bắt buộc
   chỉ định metric** (thiếu = route bị bỏ âm thầm). Vào OSPF cần `subnets`. Và route-map có
   **implicit deny** ở cuối — thiếu dòng catch-all là mất route. Tag chống mutual redistribution loop
   với chi phí bằng 0 — **dùng ngay từ ngày đầu**.

🧠 **Một câu để nhớ:** *EIGRP nhanh vì **có sẵn phương án B đã kiểm chứng** (Feasible Successor).
OSPF nhanh vì **có bản đồ nên tự tính được** phương án mới. Hai triết lý khác nhau —
và đó là toàn bộ nội dung câu "compare EIGRP and OSPF" mà đề ENCOR hỏi.*

---

### ✅ TỰ CHẤM

**Phần A — Trả lời được bằng lời của mình, không nhìn tài liệu:**

| # | Câu | ✅ |
|:---:|---|:---:|
| 1 | 3 bước router chọn đường, đúng thứ tự? | ☐ |
| 2 | AD của: connected, static, eBGP, EIGRP internal, EIGRP external, OSPF, RIP, iBGP, unreachable | ☐ |
| 3 | Vì sao eBGP (20) tin hơn iBGP (200)? | ☐ |
| 4 | Recursive lookup là gì? Dấu hiệu nó thất bại? | ☐ |
| 5 | Điểm yếu của floating static? Giải pháp? | ☐ |
| 6 | 3 bước cấu hình IP SLA + track? Hai lỗi dễ sai nhất? | ☐ |
| 7 | ⭐ Blueprint ENCOR yêu cầu gì về EIGRP? | ☐ |
| 8 | 5 khác biệt chính giữa EIGRP và OSPF | ☐ |
| 9 | FD, RD, Successor, Feasible Successor là gì? | ☐ |
| 10 | Feasibility Condition? Vì sao nó chống được loop? | ☐ |
| 11 | SIA là gì? Vì sao xảy ra? | ☐ |
| 12 | Công thức metric EIGRP dùng gì? MTU có trong đó không? | ☐ |
| 13 | Protocol nào hỗ trợ unequal-cost load balancing? Lệnh gì? | ☐ |
| 14 | Seed metric khi redistribute vào OSPF / EIGRP / RIP / BGP? | ☐ |
| 15 | Từ khóa `subnets` làm gì? Thiếu nó thì sao? | ☐ |
| 16 | E1 vs E2 khác gì? Khi nào dùng E1? | ☐ |
| 17 | Thứ tự ưu tiên route trong OSPF (intra/inter/E1/E2)? | ☐ |
| 18 | 4 quy tắc vàng của route-map? | ☐ |
| 19 | Route-map không có `match` thì khớp gì? | ☐ |
| 20 | Mutual redistribution loop: vì sao xảy ra, chống thế nào? | ☐ |

**Phần B — Lab (từ topology 3–4 router, tự làm không xem hướng dẫn):**

| # | Yêu cầu | ✅ |
|:---:|---|:---:|
| 1 | Dựng 3 router OSPF area 0, mọi neighbor `FULL` | ☐ |
| 2 | Giải mã được toàn bộ output `show ip route`: `C`, `L`, `O`, `O IA`, `O E1`, `O E2`, `[AD/metric]`, `variably subnetted` | ☐ |
| 3 | ⭐ **Chứng minh longest prefix thắng AD**: thêm static `/8` AD 1 → route OSPF `/32` vẫn thắng | ☐ |
| 4 | ⭐ **Chứng minh ngược**: thêm static `/32` AD 1 → giờ static thắng | ☐ |
| 5 | Tái hiện recursion fail: static với next-hop không reachable → không vào RIB | ☐ |
| 6 | ⭐ **Tái hiện lỗ hổng floating static**: cắt đường **phía sau** next-hop → link vẫn up → route KHÔNG failover → ping fail | ☐ |
| 7 | ⭐⭐ Cấu hình **IP SLA + track + static tracked** đầy đủ 3 bước | ☐ |
| 8 | Verify: `show ip sla statistics` (`return code: OK`, `time to live: Forever`) + `show track` (`Up`, `Tracked by`) | ☐ |
| 9 | ⭐ **Test failover thật**: cắt đường phía sau ISP1 → track `Down` → route chuyển ISP2 → ping OK trở lại | ☐ |
| 10 | Test hồi phục: bật lại → track `Up` → route quay về ISP1 | ☐ |
| 11 | Tái hiện lỗi **quên `ip sla schedule`** và nhận diện qua `time to live: 0` | ☐ |
| 12 | ⭐ Tái hiện lỗi **thiếu `source-interface`** → SLA ping qua đường dự phòng → track không bao giờ Down | ☐ |
| 13 | `redistribute connected subnets` → thấy `O E2` metric 20 | ☐ |
| 14 | Lọc redistribution bằng **route-map + prefix-list** (chỉ 1 subnet được vào) | ☐ |
| 15 | ⭐ **So sánh E1 vs E2**: đổi `metric-type 1` → metric = external + internal, chọn ASBR gần | ☐ |
| 16 | Đánh **route tag** và thấy nó trong `show ip route <prefix>` và `show ip ospf database external` | ☐ |
| 17 | Viết route-map `deny tag` + `permit` catch-all, verify bằng counter `show route-map` | ☐ |
| 18 | Tái hiện lỗi redistribute vào EIGRP **thiếu metric** → route bị bỏ âm thầm | ☐ |
| 19 | Đọc được `show ip eigrp topology` và chỉ ra FD, RD, Successor, FS | ☐ |
| 20 | Cố ý phá 1 thứ, tự tìm ra bằng **quy trình 6 bước §7.3** trong 10 phút | ☐ |

> ⚠️ **Chưa tick hết Phần B thì đừng sang Module-04.** OSPF chuyên sâu (2 tuần tới) xây trực tiếp
> lên nền này: LSA type, area type, summarization — tất cả đều là câu chuyện về **route được học
> từ đâu, mang metric gì, và router chọn cái nào**.
>
> ⭐ Riêng mục **6–12 (IP SLA + track)** là phần **giá trị nhất cho công việc thật** của cả module.
> Nếu chỉ có thời gian làm một nửa lab, hãy làm phần đó.

---

## 🔗 11. TÀI LIỆU CHO MODULE NÀY

| Nguồn | Cụ thể |
|---|---|
| **Sách OCG 350-401** | Chương *IP Routing Essentials* (bảng AD, route selection) + chương *Advanced Distance Vector — EIGRP* (⭐ **đọc phần khái niệm và bảng so sánh, BỎ phần cấu hình chi tiết**) |
| **Cisco doc** ⭐ | *IP Routing: Protocol-Independent Configuration Guide* — chương *Configuring Static Routes* và *Route Redistribution* |
| **Cisco doc** ⭐ | *IP SLAs Configuration Guide* — chương *IP SLAs ICMP Echo Operations* |
| **Cisco doc** ⭐ | *Enhanced Object Tracking Configuration Guide* — cách track kết hợp với static route / HSRP / PBR |
| **Cisco doc** | *Redistributing Routing Protocols* — tài liệu kinh điển, có đúng bảng seed metric bạn cần thuộc |
| **Cisco doc** | *Route Selection in Cisco Routers* — giải thích thứ tự longest prefix → AD → metric từ chính Cisco |
| **Cisco doc** | *Introduction to EIGRP* + RFC 7868 — cho phần compare (đọc mục Metric và DUAL) |
| **Cisco doc** | *Route-Maps for IP Routing Protocol Redistribution Configuration* |
| **Cisco Live** ⭐ | Search `Cisco Live routing protocol design best practices` · `Cisco Live EIGRP vs OSPF` |
| **NetworkLessons** | Bài *Administrative Distance*, *Route Redistribution*, *IP SLA*, *EIGRP DUAL* — giải thích rõ, nhiều bài free |
| **Video** | CBT Nuggets ENCOR — module IP Routing · Keith Barker: search `Keith Barker IP SLA`, `Keith Barker route redistribution` |
| **Forum** | https://community.cisco.com — search `redistribute eigrp no metric`, `ip sla track static route`, `mutual redistribution loop` để đọc case thật |

---

**➡️ Tiếp theo:** [Module-04 — OSPF chuyên sâu](Module-04-OSPF-Chuyen-sau.md)
*(LSA type 1–7 · Area type · DR/BDR · Network type · Summarization · Virtual-link · Auth · OSPFv3 — **2 tuần, phần nặng nhất của Infrastructure**)*
