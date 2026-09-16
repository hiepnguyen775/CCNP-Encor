# LAB 04B — Tuần 8: Area type · Summarization · OSPFv3

> 📘 **Lý thuyết:** [Module-04B](Module-04B-OSPF-Area-Summarization-OSPFv3.md) —
> đọc **Phần 1** và **Phần 2 mục §3.1 (LSA 4/5/7), §3.2 (5 loại area), §3.3 (summarization)** trước khi làm.
>
> ⏱️ **Thời gian:** ~8 giờ · 💾 **RAM:** 4 GB · 🧰 **Cần:** EVE-NG + 5–6× vIOS
>
> 👉 **Dùng lại topology của [LAB 04A](Module-04A-LAB.md)** rồi mở rộng thêm — không dựng lại từ đầu.

---

## Lab này trả lời 7 câu hỏi

| # | Câu hỏi | Bước |
|:---:|---|:---:|
| 1 | LSA type 4 và 5 xuất hiện khi nào, trông ra sao? | 1 |
| 2 | E1 và E2 khác nhau thế nào khi tính cost? | 2 |
| 3 | Biến một area thành **stub** thì LSA nào biến mất? | 3–4 |
| 4 | **NSSA** giải quyết mâu thuẫn gì mà stub không làm được? | 5 |
| 5 | `area range` và `summary-address` — đặt ở đâu, khác nhau chỗ nào? | 6 |
| 6 | Ba cách filtering đặt ở ba vị trí khác nhau — cái nào dùng khi nào? | 7 |
| 7 | OSPFv3 khác OSPFv2 ở những điểm nào? | 9 |

> **Bước 3–5 (stub / totally stubby / NSSA) là phần đề hỏi nhiều nhất Module-04B.**
> Sau mỗi bước bạn sẽ chạy `show ip ospf database` và **thấy LSA biến mất khỏi bảng** —
> đó là cách duy nhất để nhớ được bảng area type.

---

## ⚠️ Đọc trước khi bắt đầu

| Điều cần biết | Chi tiết |
|---|---|
| **Đây là lab dài nhất repo (10 bước)** | Chia làm 2–3 buổi. Bước 1–5 là bắt buộc, bước 9–10 là tùy chọn |
| **Đổi area type = reset neighbor** | Mọi router trong area **phải khai cùng loại**. Sai một con là neighbor rớt |
| **Chờ hội tụ ~40 giây** | Sau mỗi thay đổi area/summarization, chờ rồi mới xem LSDB |
| **So sánh TRƯỚC và SAU** | Mỗi bước hãy chạy `show ip ospf database` **trước khi** đổi, lưu lại, rồi so với **sau khi** đổi |
| **Lỗi > 15 phút** | Ghi vào [`SO-TAY-LOI.md`](SO-TAY-LOI.md) |

---

## 🧪 4. LAB 04B

### 4.1 Chuẩn bị — mở rộng LAB 04A

Dùng lại topology Module-04A. **Thêm 1 loopback "external" trên R4** để có ASBR:

```
   ┌─ AREA 1 ─┐    ┌────── AREA 0 (broadcast) ──────┐
                                                       
  ┌────┐          ┌────┐      ┌────────┐      ┌────┐
  │ R1 │══════════│ R2 │──────│ BRIDGE │──────│ R3 │  Lo1: 172.16.3.0/24 (AREA 2)
  └────┘  P2P     └────┘      │10.0.0.0│      └────┘
  Lo0 1.1.1.1     ABR         │  /24   │      ABR
  Lo1 172.16.1.0  (0,1)       └───┬────┘      (0,2)
      (AREA 1)                    │
                               ┌──┴─┐
                               │ R4 │  Lo1: 172.16.4.0/24 (AREA 3)
                               └────┘  Lo8: 8.8.8.8/32   ← EXTERNAL (redistribute)
                               ABR (0,3) + ASBR
```

**Thêm trên R4:**
```
R4(config)# interface Loopback8
R4(config-if)#  description ---> Gia lap mang EXTERNAL
R4(config-if)#  ip address 8.8.8.8 255.255.255.255
R4(config-if)# exit
R4(config)# interface Loopback9
R4(config-if)#  ip address 9.9.9.9 255.255.255.255
R4(config-if)# exit
!
! Static route để có thứ mà redistribute
R4(config)# ip route 203.0.113.0 255.255.255.0 Null0
R4(config)# ip route 203.0.113.64 255.255.255.192 Null0
R4(config)# ip route 203.0.114.0 255.255.255.0 Null0
R4(config)# ip route 203.0.115.0 255.255.255.0 Null0
!
! Biến R4 thành ASBR
R4(config)# router ospf 1
R4(config-router)#  redistribute connected subnets route-map RM-EXT
R4(config-router)#  redistribute static subnets
R4(config-router)# exit
!
R4(config)# ip prefix-list PL-EXT permit 8.8.8.8/32
R4(config)# ip prefix-list PL-EXT permit 9.9.9.9/32
R4(config)# route-map RM-EXT permit 10
R4(config-route-map)#  match ip address prefix-list PL-EXT
```

> 💡 Dùng `route-map` để chỉ redistribute Lo8/Lo9, không đưa mọi loopback vào (Module-03 §5).

**Verify R4 đã là ASBR:**
```
R4# show ip ospf | include It is an
 It is an area border and autonomous system boundary router
```
✅ ⭐ **ABR + ASBR** cùng lúc.

---

### Bước 1 — ⭐ LSA type 4 và 5

**a) Xem LSA type 5 trên R1 (area 1):**
```
R1# show ip ospf database external
```
**Output mẫu:**
```
                Type-5 AS External Link States

  LS age: 145
  Options: (No TOS-capability, DC)
  LS Type: AS External Link
  Link State ID: 8.8.8.8 (External Network Number)
  Advertising Router: 4.4.4.4                          ← ASBR sinh ra
  LS Seq Number: 80000001
  Checksum: 0x3A4B
  Length: 36
  Network Mask: /32
        Metric Type: 2 (Larger than any link state path)
        MTID: 0
        Metric: 20                                      ← seed metric mặc định
        Forward Address: 0.0.0.0
        External Route Tag: 0
```

⭐ **Đọc:**
- `Advertising Router: 4.4.4.4` → **ASBR sinh ra** (không phải ABR!) — chứng minh **LSA 5 flood toàn AS**
- `Metric Type: 2` → **E2** (mặc định)
- `Metric: 20` → seed metric mặc định khi redistribute vào OSPF (Module-03 §2.6)

**b) ⭐ Xem LSA type 4:**
```
R1# show ip ospf database asbr-summary
```
**Output mẫu:**
```
                Summary ASB Link States (Area 1)

  LS age: 140
  Options: (No TOS-capability, DC, Upward)
  LS Type: Summary Links(AS Boundary Router)
  Link State ID: 4.4.4.4 (AS Boundary Router address)   ← Router ID của ASBR
  Advertising Router: 2.2.2.2                            ← ABR sinh ra
  LS Seq Number: 80000001
  Checksum: 0x5C6D
  Length: 28
  Network Mask: /0
        MTID: 0         Metric: 200
```

⭐ **Đọc — đây là điểm cốt lõi:**
- `Link State ID: 4.4.4.4 (AS Boundary Router address)` → ⭐ LS ID = **Router ID của ASBR**
- `Advertising Router: 2.2.2.2` → ⭐ **ABR (R2) sinh ra**, không phải ASBR
- `Metric: 200` → cost từ **R2** tới ASBR **R4**

**c) Chứng minh cần cả LSA 4 + LSA 5:**
```
R1# show ip route 8.8.8.8
```
**Output mẫu:**
```
Routing entry for 8.8.8.8/32
  Known via "ospf 1", distance 110, metric 20, type extern 2, forward metric 300
  Last update from 10.1.12.2 on GigabitEthernet0/0, 00:02:11 ago
  Routing Descriptor Blocks:
  * 10.1.12.2, from 4.4.4.4, 00:02:11 ago, via GigabitEthernet0/0
      Route metric is 20, traffic share count is 1
```
⭐ **Đọc:**
- `metric 20` → **E2**: metric = **chỉ** external cost, **không đổi** dù R1 xa
- `forward metric 300` → cost thật để tới ASBR (100 R1→R2 + 200 R2→R4)
- `from 4.4.4.4` → nguồn là **ASBR**, không phải ABR

```
R1# show ip ospf border-routers
```
**Output mẫu:**
```
OSPF Router with ID (1.1.1.1) (Process ID 1)

Base Topology (MTID 0)

Internal Router Routing Table
Codes: i - Intra-area route, I - Inter-area route

i 2.2.2.2 [100] via 10.1.12.2, GigabitEthernet0/0, ABR, Area 1, SPF 5
I 4.4.4.4 [300] via 10.1.12.2, GigabitEthernet0/0, ASBR, Area 1, SPF 5
```
⭐ **R1 biết đường tới ASBR `4.4.4.4` cost 300** — thông tin này đến **từ LSA type 4**.
`I` = Inter-area (biết qua ABR).

**d) Đếm LSA để có mốc so sánh cho các bước sau:**
```
R1# show ip ospf database database-summary
```
**Output mẫu:**
```
Area 1 database summary
  LSA Type      Count    Delete   Maxage
  Router        2        0        0
  Network       0        0        0
  Summary Net   9        0        0       ← LSA 3
  Summary ASBR  1        0        0       ← LSA 4
  Type-7 Ext    0        0        0
  Subtotal      12       0        0

Process 1 database summary
  LSA Type      Count    Delete   Maxage
  Router        2        0        0
  Network       0        0        0
  Summary Net   9        0        0
  Summary ASBR  1        0        0
  Type-5 Ext    6        0        0       ← LSA 5
  Type-7 Ext    0        0        0
  Total         18       0        0
```

⭐ **GHI LẠI BẢNG NÀY** — bạn sẽ so sánh sau khi biến area 1 thành stub:

| Loại LSA trên R1 | Count (Normal area) | Sau khi → Stub | Sau khi → Totally Stub |
|---|:---:|:---:|:---:|
| Router (Type 1) | | | |
| Network (Type 2) | | | |
| Summary Net (Type 3) | | | |
| ⭐ Summary ASBR (Type 4) | | | |
| ⭐ Type-5 Ext | | | |
| **Total** | | | |

✅ **Checkpoint bước 1:**

| Kiểm tra | Mong đợi |
|---|---|
| LSA 5: `Advertising Router` = **4.4.4.4 (ASBR)** | ⭐ ✅ |
| LSA 5 xuất hiện được ở **area 1** (flood toàn AS) | ✅ |
| LSA 4: `Link State ID` = **4.4.4.4 (Router ID của ASBR)** | ⭐ ✅ |
| LSA 4: `Advertising Router` = **2.2.2.2 (ABR)** | ⭐ ✅ |
| `show ip ospf border-routers` trên R1 thấy ASBR `4.4.4.4` | ✅ |
| Route `8.8.8.8` là `O E2`, metric **20** (không đổi), `forward metric 300` | ⭐ ✅ |

---

### Bước 2 — ⭐ E1 vs E2 (nhắc lại + verify)

```
R4(config)# router ospf 1
R4(config-router)#  redistribute static subnets metric-type 1
```
```
R1# show ip route 203.0.113.0
```
**Output mẫu:**
```
Routing entry for 203.0.113.0/24
  Known via "ospf 1", distance 110, metric 320, type extern 1
```
⭐ **`metric 320` = 20 (external) + 300 (internal tới ASBR)** · `type extern 1` → **`O E1`**

```
R1# show ip route ospf | include E1|E2
O E1     203.0.113.0/24 [110/320] via 10.1.12.2, ...
O E2     8.8.8.8/32 [110/20] via 10.1.12.2, ...
```
⭐ **Nhìn thấy rõ khác biệt trong cùng một bảng route.**

**Trả về E2:**
```
R4(config-router)# no redistribute static subnets metric-type 1
R4(config-router)# redistribute static subnets
```

---

### Bước 3 — ⭐⭐ STUB AREA

#### 3a) Biến area 1 thành Stub

```
! Trên MỌI router trong area 1 — bao gồm cả ABR (R2)
R1(config)# router ospf 1
R1(config-router)#  area 1 stub
!
R2(config)# router ospf 1
R2(config-router)#  area 1 stub
```

**Verify:**
```
R1# show ip ospf | include Area|stub|It is
```
**Output mẫu:**
```
 Routing Process "ospf 1" with ID 1.1.1.1
 Number of areas in this router is 1. 0 normal 1 stub 0 nssa
    Area 1
        Number of interfaces in this area is 3
        It is a stub area
```

```
R2# show ip ospf | include Area|stub|generates
```
**Output mẫu:**
```
 It is an area border router
 Number of areas in this router is 2. 1 normal 1 stub 0 nssa
    Area BACKBONE(0)
    Area 1
        It is a stub area
          generates stub default route with cost 1     ← ABR tự inject default
```

#### 3b) ⭐ CHỨNG MINH LSA bị chặn — phần giá trị nhất

```
R1# show ip ospf database database-summary
```
**Output mẫu:**
```
Area 1 database summary
  LSA Type      Count    Delete   Maxage
  Router        2        0        0
  Network       0        0        0
  Summary Net   10       0        0       ← TĂNG 1 (thêm default route 0.0.0.0/0)
  Summary ASBR  0        0        0       ← TỪ 1 → 0 : LSA 4 BỊ CHẶN
  Type-7 Ext    0        0        0
  Subtotal      12       0        0

Process 1 database summary
  ...
  Type-5 Ext    0        0        0       ← TỪ 6 → 0 : LSA 5 BỊ CHẶN
  Total         12       0        0
```

⭐⭐ **ĐÂY LÀ BẰNG CHỨNG:** LSA type **4 và 5 = 0**.

```
R1# show ip ospf database external
! → TRỐNG (không có Type-5)
R1# show ip ospf database asbr-summary
! → TRỐNG (không có Type-4)
```

#### 3c) Default route tự động

```
R1# show ip route 0.0.0.0
```
**Output mẫu:**
```
Routing entry for 0.0.0.0/0, supernet
  Known via "ospf 1", distance 110, metric 101, candidate default path
  Tag 1, type inter area                            ← type INTER AREA (LSA 3!)
  Last update from 10.1.12.2 on GigabitEthernet0/0, 00:01:22 ago
  Routing Descriptor Blocks:
  * 10.1.12.2, from 2.2.2.2, 00:01:22 ago, via GigabitEthernet0/0
```
⭐ **`type inter area`** → default route đến từ **LSA type 3** do ABR inject, **không phải LSA 5**.

```
R1# show ip route ospf | include 0.0.0.0
O*IA  0.0.0.0/0 [110/101] via 10.1.12.2, 00:01:22, GigabitEthernet0/0
```
⭐ Ký hiệu **`O*IA`** — `*` = candidate default, `IA` = inter-area.

**Test kết nối vẫn hoạt động:**
```
R1# ping 8.8.8.8 source 1.1.1.1
```
✅ **Vẫn ping được** — dù R1 **không có** route cụ thể tới `8.8.8.8`, nó dùng **default route**.

```
R1# show ip route 8.8.8.8
! → % Network not in table  (hoặc match 0.0.0.0/0)
R1# traceroute 8.8.8.8 source 1.1.1.1
  1 10.1.12.2 ...       ← R2
  2 10.0.0.4 ...        ← R4
```
⭐ **Đây là toàn bộ ý tưởng của stub area:** *"tôi không cần biết chi tiết Internet,
cứ gửi về ABR."*

#### 3d) ⚠️ Tái hiện lỗi: quên khai stub trên 1 router

```
R1(config)# router ospf 1
R1(config-router)# no area 1 stub
```
```
R1# show ip ospf neighbor
! → MẤT neighbor 2.2.2.2
R2# debug ip ospf adj
%OSPF-4-BADLSATYPE: ...
! hoặc
%OSPF-5-ADJCHG: Process 1, Nbr 1.1.1.1 on Gi0/0 from FULL to DOWN,
                Neighbor Down: Adjacency forced to reset
R2# undebug all
```

**Nguyên nhân:** ⭐ **E-bit trong Hello lệch**. R1 gửi Hello với E-bit = 1 (normal),
R2 gửi E-bit = 0 (stub) → **không lên adjacency**.

**Sửa:**
```
R1(config-router)# area 1 stub
```

> 🔴 **Bài học:** area type **phải khai trên MỌI router trong area**.
> Thiếu 1 router = mất neighbor. **Ghi vào `SO-TAY-LOI.md`.**

---

### Bước 4 — ⭐⭐ TOTALLY STUBBY

```
! CHỈ trên ABR (R2). R1 giữ nguyên "area 1 stub"
R2(config)# router ospf 1
R2(config-router)#  area 1 stub no-summary
```

**Verify:**
```
R1# show ip ospf database database-summary
```
**Output mẫu:**
```
Area 1 database summary
  LSA Type      Count    Delete   Maxage
  Router        2        0        0
  Network       0        0        0
  Summary Net   1        0        0       ← TỪ 10 → 1 : chỉ còn default route!
  Summary ASBR  0        0        0
  Type-7 Ext    0        0        0
  Subtotal      3        0        0       ← LSDB CỰC NHỎ
```

⭐⭐ **`Summary Net` từ 10 xuống 1** — LSA 3 bị chặn hết, chỉ giữ lại **default route**.

```
R1# show ip ospf database summary
```
**Output mẫu:**
```
                Summary Net Link States (Area 1)

  LS Type: Summary Links(Network)
  Link State ID: 0.0.0.0 (summary Network Number)      ← CHỈ CÓ DEFAULT ROUTE
  Advertising Router: 2.2.2.2
  Network Mask: /0
        MTID: 0         Metric: 1
```

```
R1# show ip route ospf
```
**Output mẫu:**
```
O*IA  0.0.0.0/0 [110/101] via 10.1.12.2, 00:00:45, GigabitEthernet0/0
```
⭐ **CHỈ CÓ MỘT ROUTE OSPF DUY NHẤT!** Toàn bộ `172.16.3.0`, `172.16.4.0`, `10.0.0.0/24`,
`8.8.8.8` — biến mất.

```
R1# show ip route
! → chỉ còn: C/L (connected/local) + O*IA 0.0.0.0/0
```

**Test kết nối:**
```
R1# ping 172.16.3.1 source 172.16.1.1
R1# ping 8.8.8.8 source 1.1.1.1
```
✅ **Vẫn thông hết** — mọi thứ đi qua default route.

⭐ **BẢNG SO SÁNH — điền vào (đây là bảng quan trọng nhất Module-04B):**

| Loại LSA trên R1 | Normal | Stub | Totally Stub |
|---|:---:|:---:|:---:|
| Router (Type 1) | 2 | 2 | 2 |
| Network (Type 2) | 0 | 0 | 0 |
| Summary Net (Type 3) | 9 | 10 | **1** |
| ⭐ Summary ASBR (Type 4) | 1 | **0** | **0** |
| ⭐ Type-5 External | 6 | **0** | **0** |
| **TOTAL** | **18** | **12** | ⭐ **3** |
| Số route OSPF trong RIB | ~9 | ~10 | ⭐ **1** |

> ⭐ **18 → 3 LSA.** Đây là con số bạn **tự tay đo được**, và nó cho thấy chính xác
> giá trị của totally stubby area: LSDB nhỏ nhất, SPF nhanh nhất, RAM ít nhất.

#### ⚠️ Tái hiện lỗi: khai `no-summary` trên router nội bộ

```
R1(config)# router ospf 1
R1(config-router)# area 1 stub no-summary
```
```
R1# show ip ospf | include stub
        It is a stub area, no summary LSA in this area
```
→ Không gây lỗi, nhưng **không có tác dụng gì** — R1 không phải ABR nên không sinh LSA 3.

```
R1(config-router)# area 1 stub          ! trả về
```

> ⭐ **Bài học:** `no-summary` **chỉ có ý nghĩa trên ABR**. Đề hay hỏi "cấu hình ở đâu".

---

### Bước 5 — ⭐⭐ NSSA

**Tình huống:** area 2 (của R3) cần **có ASBR riêng** — VD nối tới một mạng đối tác.
Stub **không cho phép** (chặn LSA 5). → Dùng **NSSA**.

#### 5a) Tạo ASBR trong area 2

```
R3(config)# interface Loopback7
R3(config-if)#  description ---> Mang doi tac (external trong AREA 2)
R3(config-if)#  ip address 7.7.7.7 255.255.255.255
R3(config-if)# exit
R3(config)# ip route 198.18.0.0 255.255.255.0 Null0
R3(config)# router ospf 1
R3(config-router)#  redistribute static subnets
```

```
R3# show ip ospf | include It is an
 It is an area border and autonomous system boundary router
```
✅ R3 giờ là **ABR + ASBR**.

#### 5b) ⚠️ Thử làm area 2 thành Stub → sẽ thất bại

```
R3(config)# router ospf 1
R3(config-router)# area 2 stub
```
```
R3# show ip ospf database external
! → LSA type 5 của 198.18.0.0 vẫn tồn tại (vì R3 sinh cho area 0)
R3# show ip ospf | include Area 2 -A3
```
⚠️ **Vấn đề:** area 2 là stub → **không chở được LSA 5**.
Nếu area 2 có router khác cần biết external của area 2 thì không được.

> ℹ️ Trong lab này area 2 chỉ có loopback của R3 nên không thấy rõ hậu quả.
> Ở mạng thật, area 2 có router nội bộ → chúng **không nhận được** external route của chính area mình.

**Bỏ stub, chuyển sang NSSA:**
```
R3(config-router)# no area 2 stub
```

#### 5c) Cấu hình NSSA

```
! Trên MỌI router trong area 2 (ở đây chỉ có R3)
R3(config)# router ospf 1
R3(config-router)#  area 2 nssa
```

**Verify:**
```
R3# show ip ospf | include Area|nssa|It is
```
**Output mẫu:**
```
 It is an area border and autonomous system boundary router
 Number of areas in this router is 2. 1 normal 0 stub 1 nssa
    Area BACKBONE(0)
    Area 2
        It is a NSSA area
```

#### 5d) ⭐ Xem LSA type 7 và quá trình chuyển đổi 7 → 5

**Trên R3 (trong NSSA) — thấy LSA type 7:**
```
R3# show ip ospf database nssa-external
```
**Output mẫu:**
```
                Type-7 AS External Link States (Area 2)

  LS age: 65
  Options: (No TOS-capability, Type 7/5 translation, DC)
  LS Type: AS External Link
  Link State ID: 198.18.0.0 (External Network Number)
  Advertising Router: 3.3.3.3                          ← ASBR trong NSSA
  LS Seq Number: 80000001
  Network Mask: /24
        Metric Type: 2
        Metric: 20
        Forward Address: 3.3.3.3                       ← CHÚ Ý: KHÔNG phải 0.0.0.0
        External Route Tag: 0
```

⭐ **Điểm quan trọng:** `Forward Address: 3.3.3.3` — LSA 7 mang **địa chỉ forward thật**
(không phải `0.0.0.0` như LSA 5 thường). Đây là cơ chế để ABR biết chuyển tiếp về đâu sau khi
dịch 7 → 5.

**Trên R2 (area 0) — LSA 7 đã được dịch thành LSA 5:**
```
R2# show ip ospf database external 198.18.0.0
```
**Output mẫu:**
```
                Type-5 AS External Link States

  LS Type: AS External Link
  Link State ID: 198.18.0.0 (External Network Number)
  Advertising Router: 3.3.3.3                          ← ABR dịch (NSSA translator)
  Network Mask: /24
        Metric Type: 2
        Metric: 20
        Forward Address: 3.3.3.3                       ← giữ lại forward address
```

⭐ **Quá trình:** ASBR trong NSSA sinh **LSA 7** (chỉ trong NSSA) →
**ABR của NSSA** dịch thành **LSA 5** → flood ra toàn AS.

**Xem router nào làm NSSA translator:**
```
R3# show ip ospf | include Translat
        Perform type-7/type-5 LSA translation
```

```
R1# show ip route 198.18.0.0
! (nếu area 1 vẫn là totally stub → chỉ có default route)
! Tạm bỏ totally stub để thấy:
R2(config)# router ospf 1
R2(config-router)# area 1 stub                ! bỏ no-summary
```

**Ký hiệu route NSSA:**
```
R3# show ip route ospf | include N1|N2
O N2     ...           ! NSSA external type 2
```

| Ký hiệu | Nghĩa |
|---|---|
| `O N1` | NSSA external **type 1** (external + internal cost) |
| `O N2` | NSSA external **type 2** (chỉ external cost) — mặc định |

#### 5e) ⭐ NSSA KHÔNG tự có default route (bẫy đề)

```
R3# show ip route 0.0.0.0
! → % Network not in table    (nếu area 2 có router nội bộ, chúng cũng không có default)
```

⭐ **Khác với stub!** NSSA **không** tự inject default route.

**Sửa:**
```
R3(config)# router ospf 1
R3(config-router)#  area 2 nssa default-information-originate
```
```
R3# show ip ospf | include nssa|default
    Area 2
        It is a NSSA area
          generates stub default route with cost 1
```

> ⭐ **Vì sao NSSA khác stub ở điểm này:** NSSA **có ASBR riêng** → có thể nó **tự có đường ra**
> qua ASBR của mình → Cisco không tự động inject default để tránh ghi đè đường đi tốt hơn.
> Bạn phải **chủ động** yêu cầu.

#### 5f) Totally NSSA

```
! CHỈ trên ABR của NSSA (R3)
R3(config)# router ospf 1
R3(config-router)#  area 2 nssa no-summary
```
→ Chặn thêm LSA 3 vào area 2. ABR **tự inject** default route (vì có `no-summary`).

✅ **Checkpoint bước 3–5 — điền bảng tổng hợp:**

| Area type | LSA 3 | LSA 4 | LSA 5 | LSA 7 | Default route | Verify bằng |
|---|:---:|:---:|:---:|:---:|---|---|
| Normal | | | | | | `show ip ospf db database-summary` |
| Stub | | | | | | + `show ip route 0.0.0.0` → `O*IA` |
| Totally Stub | | | | | | + `show ip ospf db summary` chỉ có `0.0.0.0` |
| NSSA | | | | | | + `show ip ospf db nssa-external` |
| Totally NSSA | | | | | | |

---

### Bước 6 — ⭐⭐ SUMMARIZATION

#### 6a) Chuẩn bị — tạo nhiều subnet trong area 1

```
R1(config)# interface Loopback11
R1(config-if)#  ip address 172.16.0.1 255.255.255.0
R1(config)# interface Loopback12
R1(config-if)#  ip address 172.16.1.1 255.255.255.0
R1(config)# interface Loopback13
R1(config-if)#  ip address 172.16.2.1 255.255.255.0
R1(config)# interface Loopback14
R1(config-if)#  ip address 172.16.3.1 255.255.255.0
R1(config-if)# exit
!
R1(config)# router ospf 1
R1(config-router)#  network 172.16.0.0 0.0.3.255 area 1
R1(config-router)#  passive-interface Loopback11
R1(config-router)#  passive-interface Loopback12
R1(config-router)#  passive-interface Loopback13
R1(config-router)#  passive-interface Loopback14
```

> ⚠️ Nếu bạn đã đặt area 1 là totally stub, tạm bỏ `no-summary` trên R2 để thấy LSA 3:
> ```
> R2(config)# router ospf 1
> R2(config-router)# area 1 stub
> ```

**Trước khi summarize — xem R3 (area 0) nhận được gì:**
```
R3# show ip route ospf | include 172.16.[0-3]
```
**Output mẫu:**
```
O IA     172.16.0.0/24 [110/201] via 10.0.0.2, 00:01:11, GigabitEthernet0/1
O IA     172.16.1.0/24 [110/201] via 10.0.0.2, 00:01:11, GigabitEthernet0/1
O IA     172.16.2.0/24 [110/201] via 10.0.0.2, 00:01:11, GigabitEthernet0/1
O IA     172.16.3.0/24 [110/201] via 10.0.0.2, 00:01:11, GigabitEthernet0/1
```
⭐ **4 route riêng lẻ** = 4 LSA type 3.

```
R3# show ip ospf database summary | include 172.16
```
→ 4 LSA.

#### 6b) ⭐ `area range` trên ABR

```
! Trên ABR của area 1 (R2)
R2(config)# router ospf 1
R2(config-router)#  area 1 range 172.16.0.0 255.255.252.0
```

**Verify trên R3:**
```
R3# show ip route ospf | include 172.16
```
**Output mẫu:**
```
O IA     172.16.0.0/22 [110/201] via 10.0.0.2, 00:00:32, GigabitEthernet0/1
```
⭐⭐ **4 route → 1 route `/22`!**

```
R3# show ip ospf database summary | include 172.16
```
**Output mẫu:**
```
172.16.0.0      2.2.2.2         35   0x80000001 0x00A1B2
```
⭐ **4 LSA → 1 LSA.**

#### 6c) ⭐ Discard route (Null0) trên ABR

```
R2# show ip route 172.16.0.0 255.255.252.0
```
**Output mẫu:**
```
Routing entry for 172.16.0.0/22
  Known via "ospf 1", distance 110, metric 1, type intra area
  Routing Descriptor Blocks:
  * directly connected, via Null0                    ← DISCARD ROUTE
      Route metric is 1, traffic share count is 1
```
⭐ **IOS tự tạo route `/22 → Null0` trên ABR để chống loop.**

```
R2# show ip route | include Null0
O        172.16.0.0/22 is a summary, 00:01:22, Null0
```

**Test discard route hoạt động:**
```
R3# ping 172.16.9.9
! → fail (đúng: bị drop tại Null0 của R2, không loop ra ngoài)
R2# show ip route 172.16.9.9
! → match 172.16.0.0/22 → Null0 → drop
```

#### 6d) Metric của summary route

```
R3# show ip ospf database summary 172.16.0.0
```
**Output mẫu:**
```
  Link State ID: 172.16.0.0 (summary Network Number)
  Advertising Router: 2.2.2.2
  Network Mask: /22
        MTID: 0         Metric: 101
```
⭐ **Metric = metric NHỎ NHẤT trong 4 route thành phần** (hành vi mặc định Cisco).

**Ép metric:**
```
R2(config-router)# area 1 range 172.16.0.0 255.255.252.0 cost 500
```
```
R3# show ip route 172.16.0.0 255.255.252.0
!   metric = 500 + 100 (R3→R2) = 600
```
**Trả về:**
```
R2(config-router)# area 1 range 172.16.0.0 255.255.252.0
```

#### 6e) ⭐ CHỨNG MINH lợi ích lớn nhất: chặn LSA flooding

**a) Đếm số lần SPF chạy trên R3 trước khi test:**
```
R3# show ip ospf statistics | include Area 0 -A5
```
Hoặc đơn giản:
```
R3# show ip ospf | include SPF algorithm executed
    SPF algorithm executed 12 times
```
**Ghi lại số này.**

**b) Làm 1 subnet trong area 1 nhấp nháy:**
```
R1(config)# interface Loopback12
R1(config-if)# shutdown
! chờ 10 s
R1(config-if)# no shutdown
! chờ 10 s
R1(config-if)# shutdown
R1(config-if)# no shutdown
```

**c) Kiểm tra R3 có chạy lại SPF không:**
```
R3# show ip ospf | include SPF algorithm executed
```

⭐ **BẢNG KẾT QUẢ — điền vào:**

| | Số lần SPF trên R3 (trước) | Sau khi Lo12 nhấp nháy 2 lần | Chênh lệch |
|---|:---:|:---:|:---:|
| **CÓ** summarization (`/22`) | | | ⭐ **≈ 0** |
| **KHÔNG** summarization | | | ⚠️ tăng |

**d) Bỏ summarization rồi lặp lại để so:**
```
R2(config)# router ospf 1
R2(config-router)# no area 1 range 172.16.0.0 255.255.252.0
```
Lặp lại bước (b) và (c).

⭐ **Kết quả mong đợi:**
- **Có summarize:** LSA `/22` **không đổi** (vì `/22` vẫn còn 3 subnet khác) →
  R3 **không nhận LSA mới** → ⭐ **không chạy lại SPF**
- **Không summarize:** LSA 3 của `172.16.1.0/24` bị withdraw rồi re-advertise →
  R3 nhận LSA mới → ⚠️ **chạy lại SPF** mỗi lần

> ⭐⭐ **Đây là bài lab quan trọng nhất Module-04B.** Bạn vừa **tự tay chứng minh** rằng
> summarization không chỉ làm bảng route gọn — nó **giới hạn phạm vi lan của sự cố**.
> Con số bạn tự đo sẽ không bao giờ quên.

**Bật lại summarization:**
```
R2(config-router)# area 1 range 172.16.0.0 255.255.252.0
```

#### 6f) `summary-address` trên ASBR

R4 đang redistribute 4 static route: `203.0.113.0/24`, `203.0.113.64/26`,
`203.0.114.0/24`, `203.0.115.0/24`.

**Trước khi summarize:**
```
R3# show ip route ospf | include 203.0.11
O E2     203.0.113.0/24 [110/20] via 10.0.0.4, ...
O E2     203.0.113.64/26 [110/20] via 10.0.0.4, ...
O E2     203.0.114.0/24 [110/20] via 10.0.0.4, ...
O E2     203.0.115.0/24 [110/20] via 10.0.0.4, ...
```
⭐ 4 LSA type 5.

**Summarize trên ASBR:**
```
! Trên ASBR (R4), KHÔNG phải ABR
R4(config)# router ospf 1
R4(config-router)#  summary-address 203.0.112.0 255.255.252.0
```

**Verify:**
```
R3# show ip route ospf | include 203.0.11
```
**Output mẫu:**
```
O E2     203.0.112.0/22 [110/20] via 10.0.0.4, 00:00:25, GigabitEthernet0/1
```
⭐⭐ **4 route → 1 route.**

```
R3# show ip ospf database external | include 203.0
203.0.112.0     4.4.4.4         ...
```
⭐ 1 LSA type 5.

**Discard route trên ASBR:**
```
R4# show ip route 203.0.112.0 255.255.252.0
Routing entry for 203.0.112.0/22
  Known via "ospf 1", ...
  * directly connected, via Null0
```

⭐ **BẢNG PHÂN BIỆT — thuộc bảng này là xong câu hỏi summarization của đề:**

| | `area <X> range` | `summary-address` |
|---|---|---|
| Cấu hình trên | ⭐ **ABR** (R2) | ⭐ **ASBR** (R4) |
| Gộp | ⭐ **LSA 3** (inter-area) | ⭐ **LSA 5 / 7** (external) |
| Route bị gộp | `O IA` | `O E1` / `O E2` / `O N1` / `O N2` |
| Discard route Null0 | ✅ Tự tạo trên ABR | ✅ Tự tạo trên ASBR |
| Metric mặc định | Nhỏ nhất trong nhóm | Nhỏ nhất trong nhóm |
| Ép metric | `... cost 500` | `... cost 500` |

---

### Bước 7 — ⭐ FILTERING (3 cách)

#### 7a) Cách 1 — `area range ... not-advertise`

```
! Trên ABR (R2) — ẩn hẳn 172.16.2.0/24 khỏi area khác
R2(config)# router ospf 1
R2(config-router)#  no area 1 range 172.16.0.0 255.255.252.0
R2(config-router)#  area 1 range 172.16.2.0 255.255.255.0 not-advertise
```

**Verify:**
```
R3# show ip route ospf | include 172.16.[0-3]
O IA     172.16.0.0/24 [110/201] via 10.0.0.2, ...
O IA     172.16.1.0/24 [110/201] via 10.0.0.2, ...
O IA     172.16.3.0/24 [110/201] via 10.0.0.2, ...
!        ⚠️ 172.16.2.0/24 KHÔNG CÓ
```
```
R3# show ip ospf database summary | include 172.16.2
! → TRỐNG — LSA không tồn tại
```
⭐ **LSA 3 không được sinh ra** → area 0 và area 2 **hoàn toàn không biết** mạng này.

**Dọn dẹp:**
```
R2(config-router)# no area 1 range 172.16.2.0 255.255.255.0 not-advertise
```

#### 7b) Cách 2 — `area filter-list`

```
! Trên ABR (R2)
R2(config)# ip prefix-list PL-BLOCK-OUT seq 5 deny 172.16.2.0/24
R2(config)# ip prefix-list PL-BLOCK-OUT seq 10 permit 0.0.0.0/0 le 32    ! catch-all
R2(config)# router ospf 1
R2(config-router)#  area 1 filter-list prefix PL-BLOCK-OUT out
```

**Verify:**
```
R3# show ip route ospf | include 172.16.2
! → TRỐNG
R3# show ip ospf database summary | include 172.16.2
! → TRỐNG
R2# show ip ospf | include filter
```

**⚠️ Test lỗi: quên catch-all**
```
R2(config)# no ip prefix-list PL-BLOCK-OUT
R2(config)# ip prefix-list PL-BLOCK-OUT seq 5 deny 172.16.2.0/24
!             (KHÔNG có dòng permit)
```
```
R3# show ip route ospf | include IA
! → ⚠️ MẤT GẦN HẾT route O IA từ area 1!
```
⭐ **Prefix-list có implicit deny** → chặn mọi LSA 3 thay vì chỉ 1 dải.

**Sửa & test chiều `in`:**
```
R2(config)# ip prefix-list PL-BLOCK-OUT seq 10 permit 0.0.0.0/0 le 32
!
! Test chiều IN: chặn LSA 3 ĐI VÀO area 1
R2(config)# ip prefix-list PL-BLOCK-IN seq 5 deny 172.16.4.0/24
R2(config)# ip prefix-list PL-BLOCK-IN seq 10 permit 0.0.0.0/0 le 32
R2(config)# router ospf 1
R2(config-router)#  area 1 filter-list prefix PL-BLOCK-IN in
```
```
R1# show ip route ospf | include 172.16.4
! → TRỐNG (R1 trong area 1 không biết 172.16.4.0/24)
R3# show ip route ospf | include 172.16.4
! → VẪN CÓ (area 0 không bị ảnh hưởng)
```
⭐ **`in` = chặn LSA 3 đi VÀO area · `out` = chặn LSA 3 đi RA khỏi area.**

**Dọn dẹp:**
```
R2(config-router)# no area 1 filter-list prefix PL-BLOCK-OUT out
R2(config-router)# no area 1 filter-list prefix PL-BLOCK-IN in
```

#### 7c) ⭐⭐ Cách 3 — `distribute-list in` (KHÔNG ảnh hưởng LSDB)

```
! Trên R1 (router nội bộ — không cần là ABR)
R1(config)# ip prefix-list PL-NO-RIB seq 5 deny 172.16.4.0/24
R1(config)# ip prefix-list PL-NO-RIB seq 10 permit 0.0.0.0/0 le 32
R1(config)# router ospf 1
R1(config-router)#  distribute-list prefix PL-NO-RIB in
```

**⭐ Verify — đây là điểm cốt lõi:**
```
R1# show ip route ospf | include 172.16.4
! → TRỐNG — route KHÔNG vào RIB
```
```
R1# show ip ospf database summary | include 172.16.4
```
**Output mẫu:**
```
172.16.4.0      2.2.2.2         245  0x80000002 0x00B3C4
```
⭐⭐ **LSA VẪN CÓ TRONG LSDB!** Chỉ route không vào RIB.

```
R1# show ip ospf database database-summary
! → Summary Net count KHÔNG giảm
```

⭐ **BẢNG SO SÁNH 3 CÁCH FILTERING — điền vào:**

| Cách | LSDB của R1 | RIB của R1 | R3 (router khác) có biết? | Cấu hình trên |
|---|:---:|:---:|:---:|---|
| `area range not-advertise` | | | | |
| `area filter-list out` | | | | |
| ⭐ `distribute-list in` | | | | |

<details><summary>Đáp án</summary>

| Cách | LSDB của R1 | RIB của R1 | R3 có biết? | Cấu hình trên |
|---|:---:|:---:|:---:|---|
| `area range not-advertise` | ❌ Không có LSA | ❌ Không route | ❌ **Không biết** | **ABR** |
| `area filter-list out` | ❌ Không có LSA | ❌ Không route | ❌ **Không biết** | **ABR** |
| ⭐ `distribute-list in` | ⭐ **VẪN CÓ LSA** | ❌ Không route | ⭐ **VẪN BIẾT** | **Bất kỳ router** |

⭐ **Vì sao:** OSPF là link-state → **LSA phải flood nguyên vẹn** để LSDB đồng bộ.
`distribute-list in` chỉ can thiệp ở bước **LSDB → RIB** trên chính router đó.

🔴 **Rủi ro:** R1 không có route nhưng R3 vẫn tin *"đi qua R1 tới được"* → **black hole**.
</details>

**Dọn dẹp:**
```
R1(config-router)# no distribute-list prefix PL-NO-RIB in
```

---

### Bước 8 — Authentication

```
! Trên CẢ 2 ĐẦU của link R1↔R2
R1(config)# interface GigabitEthernet0/0
R1(config-if)#  ip ospf authentication message-digest
R1(config-if)#  ip ospf message-digest-key 1 md5 CcnpEncor2026
!
R2(config)# interface GigabitEthernet0/0
R2(config-if)#  ip ospf authentication message-digest
R2(config-if)#  ip ospf message-digest-key 1 md5 CcnpEncor2026
```

**Verify:**
```
R1# show ip ospf interface Gi0/0 | include authentication|Message digest|key
```
**Output mẫu:**
```
  Message digest authentication enabled
    Youngest key id is 1
```
```
R1# show ip ospf neighbor
! → vẫn FULL ✅
```

**⚠️ Tái hiện lỗi: key lệch**
```
R2(config-if)# ip ospf message-digest-key 1 md5 WrongKey
```
```
R1# show ip ospf neighbor
! → mất neighbor sau ~40 s (dead interval)
R1# debug ip ospf adj
%OSPF-4-ERRRCV: Received invalid packet: mismatched authentication key, from 10.1.12.2
R1# undebug on
```

**Sửa:**
```
R2(config-if)# ip ospf message-digest-key 1 md5 CcnpEncor2026
```

**Test area-level auth:**
```
R2(config)# router ospf 1
R2(config-router)#  area 0 authentication message-digest
R2(config-router)# exit
R2(config)# interface GigabitEthernet0/1
R2(config-if)#  ip ospf message-digest-key 1 md5 Area0Key
!
! Phải làm tương tự trên R3 và R4
R3(config)# router ospf 1
R3(config-router)#  area 0 authentication message-digest
R3(config)# interface Gi0/1
R3(config-if)#  ip ospf message-digest-key 1 md5 Area0Key
!
R4(config)# router ospf 1
R4(config-router)#  area 0 authentication message-digest
R4(config)# interface Gi0/1
R4(config-if)#  ip ospf message-digest-key 1 md5 Area0Key
```

⭐ **Test interface-level thắng area-level:**
```
R2(config)# interface Gi0/1
R2(config-if)# ip ospf authentication null      ! tắt auth trên interface này
```
→ Neighbor với R3/R4 **mất** (vì R3/R4 vẫn yêu cầu auth).

```
R2(config-if)# no ip ospf authentication        ! trả về (dùng area-level)
```

---

### Bước 9 — 🚀 OSPFv3

#### 9a) Cấu hình OSPFv3 trên link R1↔R2

```
! ═══ R1 ═══
R1(config)# ipv6 unicast-routing                 ! BẮT BUỘC
!
R1(config)# interface Loopback0
R1(config-if)#  ipv6 address 2001:DB8::1/128
R1(config-if)#  ipv6 ospf 1 area 1
!
R1(config)# interface GigabitEthernet0/0
R1(config-if)#  ipv6 address 2001:DB8:0:12::1/64
R1(config-if)#  ipv6 enable
R1(config-if)#  ipv6 ospf 1 area 1
R1(config-if)#  ipv6 ospf network point-to-point
!
R1(config)# ipv6 router ospf 1
R1(config-rtr)#  router-id 1.1.1.1               ! VẪN dạng IPv4
R1(config-rtr)#  auto-cost reference-bandwidth 100000

! ═══ R2 ═══
R2(config)# ipv6 unicast-routing
!
R2(config)# interface Loopback0
R2(config-if)#  ipv6 address 2001:DB8::2/128
R2(config-if)#  ipv6 ospf 1 area 0
!
R2(config)# interface GigabitEthernet0/0
R2(config-if)#  ipv6 address 2001:DB8:0:12::2/64
R2(config-if)#  ipv6 enable
R2(config-if)#  ipv6 ospf 1 area 1
R2(config-if)#  ipv6 ospf network point-to-point
!
R2(config)# interface GigabitEthernet0/1
R2(config-if)#  ipv6 address 2001:DB8:0:0::2/64
R2(config-if)#  ipv6 enable
R2(config-if)#  ipv6 ospf 1 area 0
!
R2(config)# ipv6 router ospf 1
R2(config-rtr)#  router-id 2.2.2.2
R2(config-rtr)#  auto-cost reference-bandwidth 100000
```

**Làm tương tự trên R3, R4** (area 0 trên Gi0/1, `2001:DB8:0:0::3/64` và `::4/64`).

#### 9b) Verify OSPFv3

```
R1# show ipv6 ospf neighbor
```
**Output mẫu:**
```
            OSPFv3 1 address-family ipv6 (router-id 1.1.1.1)

Neighbor ID     Pri   State           Dead Time   Interface ID    Interface
2.2.2.2           1   FULL/  -        00:00:34     3               GigabitEthernet0/0
```
⭐ **Đọc:**
- `Neighbor ID 2.2.2.2` → ⭐ **Router ID vẫn dạng IPv4**
- `FULL/  -` → point-to-point, không có DR/BDR
- ⭐ Có cột **`Interface ID`** (mới trong v3)

```
R1# show ipv6 ospf interface GigabitEthernet0/0
```
**Output mẫu:**
```
GigabitEthernet0/0 is up, line protocol is up
  Link Local Address FE80::C81A:2BFF:FE00:100, Interface ID 3
  Area 1, Process ID 1, Instance ID 0, Router ID 1.1.1.1
  Network Type POINT_TO_POINT, Cost: 100
  Transmit Delay is 1 sec, State POINT_TO_POINT
  Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5
    Hello due in 00:00:07
  Graceful restart helper support enabled
  Index 1/1/1, flood queue length 0
  Neighbor Count is 1, Adjacent neighbor count is 1
    Adjacent with neighbor 2.2.2.2
```
⭐ **Đọc:**
- `Link Local Address FE80::...` → ⭐ **Hello dùng link-local**
- `Interface ID 3` → ID mới của v3
- `Instance ID 0` → ⭐ v3 hỗ trợ nhiều instance trên 1 link
- ⭐ Neighbor state, network type, timer, cost — **giống hệt OSPFv2**

```
R1# show ipv6 ospf database
```
**Output mẫu:**
```
            OSPFv3 1 address-family ipv6 (router-id 1.1.1.1)

                Router Link States (Area 1)

ADV Router      Age  Seq#        Fragment ID  Link count  Bits
1.1.1.1         245  0x80000003  0            1           None
2.2.2.2         240  0x80000004  0            1           B

                Link (Type-8) Link States (Area 1)              ← LSA MỚI
ADV Router      Age  Seq#        Link ID    Interface
1.1.1.1         245  0x80000002  3          Gi0/0
2.2.2.2         240  0x80000002  3          Gi0/0

                Intra Area Prefix Link States (Area 1)          ← LSA MỚI (Type-9)
ADV Router      Age  Seq#        Link ID    Ref-lstype  Ref-LSID
1.1.1.1         245  0x80000003  0          0x2001      0
2.2.2.2         240  0x80000002  0          0x2001      0

                Inter Area Prefix Link States (Area 1)          ← LSA 3 đổi tên
ADV Router      Age  Seq#        Prefix
2.2.2.2         235  0x80000001  2001:DB8::2/128
2.2.2.2         235  0x80000001  2001:DB8:0:0::/64
```

⭐ **Nhận xét quan trọng:**
- **`Bits` = `B`** trên LSA của R2 → **B = Border router (ABR)**
- ⭐ **`Link (Type-8)`** — LSA mới, quảng bá link-local + prefix trên link
- ⭐ **`Intra Area Prefix (Type-9)`** — LSA mới, **mang prefix IPv6**
  (trong v3, LSA 1/2 **không mang prefix**)
- ⭐ **`Inter Area Prefix`** = LSA type 3 của v2, **đã đổi tên**

```
R1# show ipv6 route ospf
```
**Output mẫu:**
```
OI  2001:DB8::2/128 [110/100]
     via FE80::C81A:2BFF:FE00:200, GigabitEthernet0/0
OI  2001:DB8:0:0::/64 [110/200]
     via FE80::C81A:2BFF:FE00:200, GigabitEthernet0/0
```
⭐ **Đọc:**
- **`OI`** = OSPF **Inter-area** (tương đương `O IA` của v2)
- `via FE80::...` → ⭐ **next-hop là LINK-LOCAL address**, không phải global unicast!

**Test:**
```
R1# ping ipv6 2001:DB8::2 source 2001:DB8::1
```

#### 9c) ⚠️ Tái hiện lỗi kinh điển của OSPFv3

**Lỗi 1 — quên `ipv6 unicast-routing`**
```
R1(config)# no ipv6 unicast-routing
```
```
R1# show ipv6 ospf neighbor
! → TRỐNG
R1# show ipv6 route
! → không có route nào
```
**Sửa:** `ipv6 unicast-routing`

**Lỗi 2 — ⭐ không có IPv4 nào và không gõ `router-id`**

Mô phỏng: xóa `router-id` khi router **chỉ có IPv6** (trong lab R1 vẫn có IPv4 nên
OSPFv3 tự lấy được — nhưng ở mạng IPv6-only thì sẽ lỗi):
```
R1(config)# ipv6 router ospf 1
R1(config-rtr)# no router-id
```
```
R1# show ipv6 ospf | include Router ID
! → nếu router không có IPv4 nào: %OSPFv3 could not pick a router-id
```

> 🔴 **Đây là điểm khác biệt quan trọng nhất về mặt vận hành của OSPFv3:**
> Router ID **vẫn là 32-bit dạng IPv4**. Trên router **IPv6-only** (không có interface IPv4 nào),
> OSPFv3 **không tự chọn được Router ID** → **không khởi động** →
> ⭐ **PHẢI gõ tay `router-id`**.

**Sửa:**
```
R1(config-rtr)# router-id 1.1.1.1
```

**Lỗi 3 — network type lệch**
```
R2(config)# interface Gi0/0
R2(config-if)# no ipv6 ospf network point-to-point
```
```
R1# show ipv6 ospf neighbor
! → mất neighbor (broadcast vs point-to-point)
```
**Sửa:** đặt lại `ipv6 ospf network point-to-point`.

✅ **Checkpoint bước 9:**

| Kiểm tra | Mong đợi |
|---|---|
| `show ipv6 ospf neighbor` → `FULL`, Neighbor ID **dạng IPv4** | ⭐ ✅ |
| `show ipv6 ospf interface` → `Link Local Address FE80::...`, `Interface ID` | ⭐ ✅ |
| `show ipv6 ospf database` → có **Link (Type-8)** và **Intra Area Prefix (Type-9)** | ⭐ ✅ |
| `show ipv6 ospf database` → LSA 3 đổi tên **Inter Area Prefix** | ✅ |
| `show ipv6 route ospf` → ký hiệu **`OI`**, next-hop là **link-local** | ⭐ ✅ |
| Tái hiện lỗi thiếu `ipv6 unicast-routing` | ✅ |
| Hiểu vì sao router IPv6-only **phải** gõ tay `router-id` | ⭐ ✅ |

---

### Bước 10 — 🚀 Virtual Link (tùy chọn)

**Tạo tình huống sai thiết kế:** biến R4 thành ABR của một area **không nối area 0**.

```
! Trên R4 — chuyển interface area 0 sang area 3 (cố ý làm sai)
! ⚠️ Bước này phá vỡ kết nối — chỉ làm khi đã xong các bước trên
R4(config)# interface Gi0/1
R4(config-if)# no ip ospf 1 area 0
```

> ℹ️ Topology lab này không thuận lợi để mô phỏng virtual link đúng cách
> (cần ít nhất 3 router xếp chuỗi qua transit area). Nếu muốn thực hành đầy đủ,
> thêm router thứ 5. **Với ENCOR, hiểu khái niệm + đọc được `show ip ospf virtual-links` là đủ.**

**Nếu bạn dựng được topology chuỗi:**
```
! Trên ABR có area 0 (R3)
R3(config)# router ospf 1
R3(config-router)#  area 2 virtual-link 4.4.4.4

! Trên ABR không có area 0 (R4)
R4(config)# router ospf 1
R4(config-router)#  area 2 virtual-link 3.3.3.3
```
```
R3# show ip ospf virtual-links
Virtual Link OSPF_VL0 to router 4.4.4.4 is up
  Transit area 2, via interface GigabitEthernet0/1
  ...
  Adjacency State FULL (Hello suppressed)
```

**Dọn dẹp:** trả R4 Gi0/1 về area 0.
```
R4(config)# interface Gi0/1
R4(config-if)# ip ospf 1 area 0
```

---
