# Module-04B — OSPF: Area type, Summarization, Filtering, OSPFv3

> 🧭 **Lộ trình:** [Module-04A](Module-04A-OSPF-Nen-tang-va-LSDB.md) → `[Bạn đang ở đây] Module-04B` → Module-05 (BGP)
>
> 📊 **Blueprint:** Domain **3.0 Infrastructure (30%)**, mục **3.2.b — Configure and verify simple
> OSPF environments, including multiple normal areas, summarization, and filtering
> (neighbor adjacency, point-to-point and broadcast of OSPFv2 and OSPFv3, router ID)**
>
> ⏱️ **Tuần 8** · 10 giờ

---

## ✅ 1. Chuẩn bị

| Cần có | Chi tiết |
|---|---|
| **Kiến thức trước** | 🔴 **Module-04A BẮT BUỘC** — phải đọc được `show ip ospf database` và phân biệt LSA type 1/2/3 |
| | Module-03 §2.6 (redistribution, seed metric, E1 vs E2) |
| **Lab** | ⭐ **Dùng lại LAB 04A** (4 router + Bridge). Chỉ thêm cấu hình, không dựng lại |
| **RAM** | 4× 512 MB = **2 GB** ✅ |
| **Thời lượng** | 3h lý thuyết · 5h lab · 2h quiz |

> ⚠️ **Nếu bạn chưa làm xong Phần B của Module-04A** (đặc biệt mục 5–10: đọc LSDB) thì
> **quay lại làm cho xong trước**. Module này toàn bộ là câu chuyện về **LSA nào bị chặn ở đâu**
> — không đọc được LSDB thì không thể hiểu.

---

## 📘 2. LÝ THUYẾT

### 2.1 ⭐ LSA type 4, 5, 7 — hoàn thiện bảng LSA

Module-04A đã học type 1, 2, 3. Giờ thêm 3 loại liên quan tới **route từ ngoài OSPF**.

| Type | Tên | Ai sinh ra | Flood tới đâu | LS ID | Mô tả gì |
|:---:|---|---|---|---|---|
| **1** | Router LSA | Mọi router | Trong area | Router ID | Các link của router |
| **2** | Network LSA | DR | Trong area | IP của DR | Router nào trên segment transit |
| **3** | Summary LSA | ABR | Sang area khác | Địa chỉ mạng | "Area kia có mạng X, đi qua tôi" |
| **4** | **ASBR Summary** | ⭐ **ABR** | Sang area khác | ⭐ **Router ID của ASBR** | "Muốn tới ASBR đó thì đi qua tôi" |
| **5** | **AS External** | ⭐ **ASBR** | ⭐ **Toàn AS** (trừ stub/NSSA) | **Địa chỉ mạng ngoài** | Route redistribute từ ngoài |
| **7** | **NSSA External** | ⭐ **ASBR trong NSSA** | ⭐ **Chỉ trong NSSA** | Địa chỉ mạng ngoài | Như type 5 nhưng nội bộ NSSA |

> ℹ️ Type 6 (MOSPF) đã bị loại bỏ. Type 9/10/11 là **Opaque LSA** (dùng cho MPLS-TE, Segment Routing)
> — không có trong ENCOR.

#### ⭐ Vì sao cần LSA type 4 — câu hỏi hay của đề

**Vấn đề:** LSA type 5 được flood **toàn AS**, và nó nói *"mạng `8.8.8.0/24` có thể tới được
qua ASBR có Router ID `4.4.4.4`"*.

Nhưng router ở **area 1** làm sao biết **đi đường nào tới `4.4.4.4`**?
Nó không có LSA type 1 của R4 (LSA 1 không ra khỏi area)!

**Giải pháp:** ABR sinh **LSA type 4** = *"muốn tới ASBR `4.4.4.4` thì đi qua tôi, cost X"*.

```
    AREA 1                    AREA 0                   AREA 2
                                                                 external
  ┌────┐                    ┌────┐                    ┌────┐    8.8.8.0/24
  │ R1 │────────────────────│ R2 │────────────────────│ R4 │◀────────────
  └────┘                    └────┘                    └────┘
                             ABR                     ABR + ASBR

  R4 sinh  LSA 5: "8.8.8.0/24, tôi là ASBR 4.4.4.4"  ──▶ flood TOÀN AS
  R2 sinh  LSA 4: "muốn tới ASBR 4.4.4.4 → đi qua tôi (2.2.2.2), cost 100"

  R1 ghép:  LSA 5 (mạng ở đâu) + LSA 4 (ASBR ở đâu) = tính được đường đi
```

| Không có LSA 4 | ⭐ Có LSA 4 |
|---|---|
| R1 biết "mạng `8.8.8.0/24` ở sau ASBR `4.4.4.4`" nhưng **không biết `4.4.4.4` ở đâu** | R1 biết **cả hai** → tính được đường |
| Route bị **loại khỏi RIB** (unreachable ASBR) | Route vào RIB bình thường |

🧠 **Một câu để nhớ:** *LSA 5 nói **"mạng ở đâu"**. LSA 4 nói **"người giữ mạng đó ở đâu"**.
Thiếu một trong hai thì route vô dụng.*

⭐ **Chú ý:** ASBR **nằm trong cùng area** thì **không cần** LSA type 4 —
router đã có LSA type 1 của ASBR rồi.

#### E1 vs E2 (nhắc lại Module-03 §2.6)

| | **E1** (`metric-type 1`) | **E2** (mặc định) |
|---|---|---|
| Metric | External cost **+ internal cost tới ASBR** | ⭐ **Chỉ** external cost, **không đổi** toàn AS |
| Ký hiệu | `O E1` | `O E2` |
| Dùng khi | ⭐ **Nhiều ASBR** → chọn ASBR gần nhất | 1 ASBR, hoặc không quan tâm |

### 2.2 ⭐⭐ Năm loại Area — bảng quan trọng nhất Module-04B

**Ý tưởng:** router ở nhánh xa không cần biết mọi route external của Internet.
Chặn LSA không cần thiết → **LSDB nhỏ hơn, SPF nhanh hơn, tiết kiệm RAM/CPU**.

| Area type | LSA 1,2 | LSA 3 | LSA 4,5 | LSA 7 | Default route (0.0.0.0/0) | Lệnh |
|---|:---:|:---:|:---:|:---:|---|---|
| ⭐ **Backbone (Area 0)** | ✅ | ✅ | ✅ | ❌ | Nếu có | — |
| ⭐ **Normal / Standard** | ✅ | ✅ | ✅ | ❌ | Nếu có | — (mặc định) |
| ⭐ **Stub** | ✅ | ✅ | ❌ **chặn** | ❌ | ⭐ ABR tự inject **`O IA`** | `area X stub` |
| ⭐ **Totally Stubby** | ✅ | ❌ **chặn** | ❌ **chặn** | ❌ | ⭐ ABR tự inject **`O IA`** | `area X stub no-summary` *(chỉ ABR)* |
| ⭐ **NSSA** | ✅ | ✅ | ❌ **chặn** | ✅ **cho phép** | ⚠️ **KHÔNG tự động** — phải thêm `default-information-originate` | `area X nssa` |
| ⭐ **Totally NSSA** | ✅ | ❌ **chặn** | ❌ **chặn** | ✅ **cho phép** | ⭐ ABR tự inject | `area X nssa no-summary` *(chỉ ABR)* |

**Cách nhớ nhanh:**

| Từ khóa | Nghĩa |
|---|---|
| **Stub** | ⭐ Chặn **LSA 4 + 5** (external) |
| **Totally** *(`no-summary`)* | ⭐ Chặn **thêm LSA 3** (inter-area) |
| **NSSA** | ⭐ Như stub, **nhưng cho phép LSA 7** (có ASBR ngay trong area) |

```
        LSA 3 (inter-area)    LSA 4+5 (external)    LSA 7 (NSSA ext)
Normal:        ✅                    ✅                    ❌
Stub:          ✅                    ❌                    ❌
Total Stub:    ❌                    ❌                    ❌
NSSA:          ✅                    ❌                    ✅
Total NSSA:    ❌                    ❌                    ✅
```

#### Quy tắc bắt buộc khi cấu hình area type

| # | Quy tắc | Hệ quả nếu sai |
|:---:|---|---|
| 1 | 🔴 **MỌI router trong area phải khai cùng area type** | Neighbor **không lên** (E-bit / N-bit mismatch) |
| 2 | ⭐ `no-summary` **chỉ cấu hình trên ABR** | Router nội bộ khai `no-summary` → không có tác dụng (hoặc lỗi) |
| 3 | 🔴 **Area 0 KHÔNG THỂ là stub/NSSA** | Không cho phép — area 0 phải chở mọi LSA |
| 4 | 🔴 **Area có ASBR KHÔNG THỂ là stub** | Stub chặn LSA 5 → ASBR không quảng bá được. **Dùng NSSA** |
| 5 | ⚠️ **Virtual-link không đi qua stub area** | Virtual-link cần LSA 3/4/5 |

> ⭐ **Bit trong Hello quyết định adjacency:**
> - **E-bit** (External capability): `0` = stub area · `1` = normal. **Phải khớp** → điều kiện #8 ở Module-04A
> - **N-bit** (NSSA capability): dùng cho NSSA. Cũng phải khớp

**Cấu hình:**
```
! ═══ STUB ═══
! Trên MỌI router trong area 1 (kể cả ABR)
router ospf 1
 area 1 stub

! ═══ TOTALLY STUBBY ═══
! Router nội bộ: area 1 stub
! CHỈ ABR thêm no-summary:
router ospf 1
 area 1 stub no-summary

! ═══ NSSA ═══
! Trên MỌI router trong area 2
router ospf 1
 area 2 nssa

! NSSA + tự inject default route (chỉ ABR)
router ospf 1
 area 2 nssa default-information-originate

! ═══ TOTALLY NSSA ═══
! Router nội bộ: area 2 nssa
! CHỈ ABR: area 2 nssa no-summary
```

**Kiểm tra:**
```
show ip ospf | include Area|stub|nssa|It is
show ip ospf database database-summary        ! đếm LSA để CHỨNG MINH bị chặn
show ip route ospf
show ip ospf interface Gi0/0 | include Hello  ! xem E-bit qua debug/wireshark
```

**Output mẫu `show ip ospf`:**
```
 Routing Process "ospf 1" with ID 1.1.1.1
 It is an area border router
 Number of areas in this router is 2. 1 normal 1 stub 0 nssa
    Area BACKBONE(0)
    Area 1
        Number of interfaces in this area is 1
        It is a stub area
          generates stub default route with cost 1
```
⭐ Dòng `generates stub default route with cost 1` xác nhận ABR đang inject default route.

### 2.3 ⭐ Summarization — hai lệnh, hai chỗ khác nhau

Đây là chỗ đề ENCOR hỏi trực tiếp ("**including... summarization**").

| | **`area <X> range`** | **`summary-address`** |
|---|---|---|
| Cấu hình trên | ⭐ **ABR** | ⭐ **ASBR** |
| Gộp loại route nào | ⭐ **Inter-area** (LSA 3) | ⭐ **External** (LSA 5 / LSA 7) |
| Gộp route từ đâu | Từ **area X** sang area khác | Từ **redistribution** vào OSPF |
| Cú pháp | `area 1 range 172.16.0.0 255.255.252.0` | `summary-address 192.168.0.0 255.255.252.0` |
| Vị trí lệnh | Trong `router ospf` | Trong `router ospf` |

```
! ═══ Trên ABR: gộp các subnet của AREA 1 khi quảng bá ra ngoài ═══
router ospf 1
 area 1 range 172.16.0.0 255.255.252.0
!             └── gộp 172.16.0.0/24, .1.0/24, .2.0/24, .3.0/24 thành /22

! ═══ Trên ASBR: gộp các route EXTERNAL khi redistribute vào OSPF ═══
router ospf 1
 summary-address 192.168.0.0 255.255.252.0
 redistribute static subnets
```

#### ⭐ Lợi ích & cái giá của summarization

| Lợi ích | Cái giá |
|---|---|
| ⭐ LSDB nhỏ hơn nhiều (4 LSA → 1 LSA) | ⚠️ **Mất chi tiết** — không biết subnet nào up/down |
| ⭐ **Chặn LSA flooding** khi 1 subnet nhấp nháy → area khác **không chạy lại SPF** | ⚠️ Có thể **hút traffic vào hố đen** (xem dưới) |
| Bảng route nhỏ hơn | Cần thiết kế IP có kế hoạch (contiguous addressing) |

⭐ **Đây là lợi ích LỚN NHẤT của summarization:** nếu `172.16.1.0/24` trong area 1 nhấp nháy,
mà ABR đang quảng bá `172.16.0.0/22`, thì **LSA `/22` không đổi** → **area 0 và area 2 không hề biết**
→ **không chạy lại SPF**. Đây là **cách giới hạn fault domain hiệu quả nhất** của OSPF.

#### ⚠️ Metric của summary route & Null0 route

**Metric của summary LSA** = ⭐ **metric NHỎ NHẤT** trong các route thành phần
(hành vi mặc định của Cisco). Có thể ép:
```
router ospf 1
 area 1 range 172.16.0.0 255.255.252.0 cost 500
```

**⭐ Discard route (Null0):** khi bạn cấu hình summarization, IOS tự tạo route
`172.16.0.0/22 → Null0` **trên chính ABR/ASBR** để **chống routing loop**.

```
ABR# show ip route 172.16.0.0 255.255.252.0
Routing entry for 172.16.0.0/22
  Known via "ospf 1", distance 110, metric 1, type intra area
  Routing Descriptor Blocks:
  * directly connected, via Null0
```
⭐ **Vì sao cần:** ABR quảng bá `/22` ra ngoài. Nếu có gói tới `172.16.3.99`
mà subnet đó **không tồn tại**, ABR sẽ tra bảng route → nếu không có discard route,
nó có thể match một route mặc định và **gửi gói ngược ra ngoài → loop**.
Discard route **drop gói ngay** tại ABR.

```
! Tắt discard route (KHÔNG khuyến nghị)
router ospf 1
 no discard-route internal
 no discard-route external
```

#### ⚠️ Black hole do summarization

```
   AREA 1 chỉ có: 172.16.0.0/24 và 172.16.1.0/24
                  (KHÔNG có .2.0/24 và .3.0/24)
                          │
   ABR quảng bá: 172.16.0.0/22  ← ⚠️ bao gồm cả .2.0 và .3.0 KHÔNG TỒN TẠI
                          │
   Nếu .2.0/24 tồn tại ở NƠI KHÁC (VD area 2) và area 2 cũng quảng bá /24
   → Longest prefix match sẽ chọn /24 → ✅ OK
   
   Nhưng nếu .2.0/24 KHÔNG tồn tại ở đâu
   → traffic tới .2.0 bị hút vào area 1 → drop tại Null0 → ✅ đúng (không loop)
   → nhưng nếu ĐÚNG RA phải đi ra Internet → ⚠️ BLACK HOLE
```

⭐ **Bài học:** chỉ summarize khi **thiết kế IP có kế hoạch** —
mọi subnet trong dải gộp đều thuộc area đó.

### 2.4 ⭐ Filtering — ba cách, ba vị trí khác nhau

Đề hỏi trực tiếp ("**and filtering**"). Đây là bảng phân biệt.

| Cách | Lọc gì | Cấu hình trên | Ảnh hưởng LSDB? | Lệnh |
|---|---|---|:---:|---|
| **1. `area range ... not-advertise`** | ⭐ **LSA 3** (inter-area) | **ABR** | ✅ **Có** — LSA không được sinh | `area 1 range 172.16.2.0 255.255.255.0 not-advertise` |
| **2. `area filter-list`** | ⭐ **LSA 3** vào/ra area | **ABR** | ✅ **Có** | `area 1 filter-list prefix PL-X in\|out` |
| **3. `distribute-list ... in`** | ⭐ **Route vào RIB** | **Bất kỳ router** | ❌ **KHÔNG** — LSDB vẫn đủ | `distribute-list prefix PL-X in` |

#### Cách 1 — `not-advertise`: ẩn hẳn một dải

```
router ospf 1
 area 1 range 172.16.2.0 255.255.255.0 not-advertise
```
→ ABR **không sinh LSA 3** cho `172.16.2.0/24` → area khác **hoàn toàn không biết** mạng này tồn tại.

#### Cách 2 — `area filter-list`: lọc theo prefix-list, có chiều in/out

```
ip prefix-list PL-BLOCK seq 5 deny 172.16.2.0/24
ip prefix-list PL-BLOCK seq 10 permit 0.0.0.0/0 le 32     ! catch-all, đừng quên
!
router ospf 1
 area 1 filter-list prefix PL-BLOCK out         ! chặn LSA 3 ĐI RA khỏi area 1
!area 1 filter-list prefix PL-BLOCK in          ! chặn LSA 3 ĐI VÀO area 1
```

⭐ **Hiểu chiều `in`/`out` — nhìn từ góc độ AREA:**

| Chiều | Nghĩa |
|---|---|
| `out` | ⭐ Lọc LSA 3 **ABR sinh ra ĐỂ GỬI RA KHỎI** area 1 (area khác không thấy mạng của area 1) |
| `in` | ⭐ Lọc LSA 3 **ABR sinh ra ĐỂ GỬI VÀO** area 1 (area 1 không thấy mạng của area khác) |

> ⚠️ **Prefix-list cũng có implicit deny** — thiếu dòng `permit 0.0.0.0/0 le 32` ở cuối
> sẽ **chặn hết mọi LSA 3** thay vì chỉ 1 dải.

#### Cách 3 — `distribute-list in`: lọc RIB, không lọc LSDB

```
ip prefix-list PL-NO-RIB seq 5 deny 172.16.2.0/24
ip prefix-list PL-NO-RIB seq 10 permit 0.0.0.0/0 le 32
!
router ospf 1
 distribute-list prefix PL-NO-RIB in
```

| | LSDB | RIB (bảng route) | Router khác |
|---|:---:|:---:|:---:|
| Cách 1 & 2 (`area range/filter-list`) | ⭐ LSA **bị chặn** | Không có route | ⭐ **Cũng không biết** |
| ⭐ Cách 3 (`distribute-list in`) | ⭐ LSA **VẪN CÓ ĐỦ** | ⭐ **Không có route** | Vẫn biết bình thường |

> ⭐ **Điểm cực quan trọng của `distribute-list in` trong OSPF:**
> Vì OSPF là link-state, **LSA phải được flood nguyên vẹn** để LSDB đồng bộ.
> `distribute-list in` **chỉ ngăn route vào RIB của chính router đó** — LSDB vẫn đầy đủ,
> và router **vẫn flood LSA cho neighbor**.
>
> ⚠️ **Nguy hiểm:** dùng `distribute-list in` để "chặn" route có thể tạo **routing black hole**
> — router này không có route nhưng router khác vẫn tin nó có đường đi qua đây.
>
> 🎓 **Đề hay hỏi:** *"Lệnh nào lọc route OSPF mà KHÔNG ảnh hưởng LSDB?"* → `distribute-list in`

> ⚠️ **`distribute-list out` trong OSPF:** chỉ hoạt động **trên ASBR** và chỉ lọc
> **route được redistribute** (LSA 5), **không** lọc LSA 3. Khác hoàn toàn với EIGRP/RIP.

### 2.5 Default route origination

```
! Trên ASBR / router có đường ra Internet
router ospf 1
 default-information originate                    ! chỉ quảng bá NẾU có 0.0.0.0/0 trong RIB
 default-information originate always             ! quảng bá LUÔN, dù không có route
 default-information originate metric 50 metric-type 1
```

| Tùy chọn | Hành vi | Rủi ro |
|---|---|---|
| *(không có `always`)* | ⭐ Chỉ quảng bá khi **router có `0.0.0.0/0` trong RIB** | An toàn — mất default thì ngừng quảng bá |
| ⚠️ `always` | Quảng bá **bất kể** có default route hay không | 🔴 **Hút traffic vào hố đen** nếu router mất đường ra Internet |

> ⭐ **Best practice:** dùng **không có `always`** + kết hợp **IP SLA/track** (Module-03 §2.4)
> cho default route → khi ISP chết, default route bị xóa → OSPF ngừng quảng bá →
> traffic tự chuyển sang router khác.

**Default route trong các area type:**

| Area type | Default route đến từ đâu |
|---|---|
| Normal | LSA 5 từ ASBR (`default-information originate`) |
| **Stub** | ⭐ **ABR tự inject** LSA 3 → route là **`O IA`** |
| **Totally Stubby** | ⭐ **ABR tự inject** → `O IA` (và đây là **route duy nhất** ngoài intra-area) |
| ⚠️ **NSSA** | 🔴 **KHÔNG tự động!** Phải thêm `area X nssa default-information-originate` |
| **Totally NSSA** | ⭐ ABR tự inject (vì có `no-summary`) |

⭐ **Bẫy đề:** NSSA **không** tự động có default route, khác với stub. Đây là điểm hay bị nhầm.

### 2.6 Authentication

| Loại | Bảo mật | Lệnh interface | Ghi chú |
|---|---|---|---|
| **Null** (không auth) | ❌ | *(mặc định)* | |
| **Plain text** (type 1) | ⚠️ Rất yếu | `ip ospf authentication` + `ip ospf authentication-key <key>` | Key gửi **rõ** trên đường truyền |
| ⭐ **MD5** (type 2) | 🟡 Trung bình | `ip ospf authentication message-digest` + `ip ospf message-digest-key 1 md5 <key>` | Phổ biến nhất |
| ⭐ **SHA** (type 3) | ✅ **Mạnh** | `ip ospf authentication key-chain <name>` | Dùng **key chain**, hỗ trợ rotate key |

**Hai cấp cấu hình:**

```
! ═══ CÁCH A: theo AREA (áp cho mọi interface trong area) ═══
router ospf 1
 area 0 authentication message-digest         ! MD5 cho cả area 0
!area 0 authentication                        ! plain text cho cả area 0
!
interface GigabitEthernet0/1
 ip ospf message-digest-key 1 md5 MyS3cr3tK3y  ! key vẫn phải đặt trên interface

! ═══ CÁCH B: theo INTERFACE (linh hoạt hơn, khuyến nghị) ═══
interface GigabitEthernet0/1
 ip ospf authentication message-digest
 ip ospf message-digest-key 1 md5 MyS3cr3tK3y

! ═══ SHA (key chain) — bảo mật nhất ═══
key chain OSPF-KC
 key 1
  key-string MyStr0ngK3y
  cryptographic-algorithm hmac-sha-256
!
interface GigabitEthernet0/1
 ip ospf authentication key-chain OSPF-KC
```

> ⭐ **Interface-level thắng area-level.** Muốn tắt auth trên 1 interface trong area có auth:
> ```
> interface Gi0/2
>  ip ospf authentication null
> ```

**Kiểm tra:**
```
show ip ospf interface Gi0/1 | include authentication|Message digest|Cryptographic
```
**Output mẫu:**
```
  Message digest authentication enabled
    Youngest key id is 1
```

⚠️ **Auth mismatch** → neighbor **không lên**, và log:
```
%OSPF-4-BADLSATYPE: Invalid lsa: Bad LSA type ...
! hoặc
%OSPF-4-ERRRCV: Received invalid packet: mismatched authentication type, from 10.0.0.3
```

### 2.7 Virtual Link — vá lỗi thiết kế

**Quy tắc OSPF:** ⭐ **mọi area phải nối trực tiếp tới area 0.**
Nếu vi phạm → **virtual link** là cách vá (không phải cách thiết kế).

```
   ⚠️ THIẾT KẾ SAI: area 2 KHÔNG nối tới area 0
   
   AREA 0          AREA 1          AREA 2
  ┌────┐          ┌────┐          ┌────┐
  │ R2 │──────────│ R3 │──────────│ R4 │
  └────┘          └────┘          └────┘
                  ABR(0,1)        ABR(1,2)  ← ⚠️ không có interface trong area 0
                                              → route area 2 KHÔNG tới được area 0

   ✅ SỬA bằng VIRTUAL LINK qua AREA 1 (transit area):
   
        ╔══════════ virtual-link ══════════╗
        ║   (area 0 "mở rộng" logic)        ║
   ┌────┐          ┌────┐          ┌────┐
   │ R2 │──────────│ R3 │──────────│ R4 │
   └────┘          └────┘          └────┘
```

⚠️ **Nhưng ví dụ trên vẫn sai** — virtual link phải nối **2 ABR đều có interface trong transit area**,
và **một đầu phải ở area 0**. Cấu hình đúng:

```
! Trên R3 (ABR có area 0 và area 1)
router ospf 1
 area 1 virtual-link 4.4.4.4          ! dùng ROUTER ID của đầu kia

! Trên R4 (ABR có area 1 và area 2)
router ospf 1
 area 1 virtual-link 3.3.3.3
!         └── area 1 là TRANSIT AREA
```

| Quy tắc virtual link | Chi tiết |
|---|---|
| Dùng **Router ID**, không phải IP interface | `area 1 virtual-link 4.4.4.4` |
| ⭐ **Transit area** = area mà virtual link **đi qua** | Ở đây là area 1 |
| 🔴 **Transit area KHÔNG được là stub/NSSA** | Cần LSA 3/4/5 đi qua |
| ⭐ Cả 2 đầu phải là **ABR** | |
| Sinh ra **Link Type 4** trong LSA type 1 | `Virtual link` |
| Auth phải khớp | `area 1 virtual-link 4.4.4.4 message-digest-key 1 md5 KEY` |

**Kiểm tra:**
```
show ip ospf virtual-links
```
**Output mẫu:**
```
Virtual Link OSPF_VL0 to router 4.4.4.4 is up
  Run as demand circuit
  DoNotAge LSA allowed.
  Transit area 1, via interface GigabitEthernet0/1
  Topology-MTID    Cost    Disabled     Shutdown      Topology Name
        0            100      no           no            Base
  Transmit Delay is 1 sec, State POINT_TO_POINT,
  Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5
    Adjacency State FULL (Hello suppressed)
```
✅ `is up` · `Adjacency State FULL` · `Transit area 1`

```
show ip ospf neighbor              ! virtual link xuất hiện như 1 neighbor OSPF_VL0
show ip ospf database router | include Virtual
```

> ⚠️ **Virtual link là giải pháp tạm.** Nếu bạn phải dùng nó lâu dài → **thiết kế area sai**,
> nên sửa topology (thêm link vật lý tới area 0, hoặc gộp area).

### 2.8 ⭐ OSPFv3 (OSPF cho IPv6)

Blueprint ghi rõ: *"point-to-point and broadcast of **OSPFv2 and OSPFv3**"*.

#### Bảng so sánh OSPFv2 vs OSPFv3

| | **OSPFv2** (IPv4) | **OSPFv3** (IPv6) |
|---|---|---|
| RFC | 2328 | **5340** |
| Chạy trên | IPv4 | ⭐ **IPv6** (protocol 89 trong IPv6 header) |
| Multicast | 224.0.0.5 / 224.0.0.6 | ⭐ **FF02::5** / **FF02::6** |
| Nguồn gói Hello | IP interface | ⭐ **Link-local address** (`FE80::/10`) |
| **Router ID** | 32-bit (thường = IP) | ⭐ **VẪN LÀ 32-bit dạng IPv4!** ⚠️ Phải **gõ tay** nếu không có IPv4 nào |
| Cấu hình interface vào OSPF | `network <ip> <wildcard> area X` | ⭐ **`ipv6 ospf 1 area X`** (trên interface) |
| Authentication | Có sẵn (plain/MD5/SHA) | ⭐ Dùng **IPsec (AH/ESP)** — v3 không có auth riêng |
| Nhiều instance / link | ❌ 1 | ⭐ ✅ Có (**Instance ID**) |
| Flooding scope | Chỉ trong area | ⭐ Rõ ràng: link-local / area / AS |
| LSA type 3 | "Summary LSA" | ⭐ Đổi tên **Inter-Area Prefix LSA** (type 0x2003) |
| LSA type 4 | "ASBR Summary" | ⭐ Đổi tên **Inter-Area Router LSA** (type 0x2004) |
| LSA mới | — | ⭐ **Link LSA (type 8)** · **Intra-Area Prefix LSA (type 9)** |
| Stub/NSSA | ✅ | ✅ Giống |
| Neighbor state | 8 trạng thái | ⭐ **Giống hệt** |
| DR/BDR | Có (broadcast) | ⭐ **Giống hệt** |
| Network type | 5 loại | ⭐ **Giống hệt** |

#### ⭐ Năm điểm phải nhớ về OSPFv3

| # | Điểm | Chi tiết |
|:---:|---|---|
| **1** | 🔴 **Router ID vẫn là 32-bit dạng IPv4** | Nếu router **không có IPv4 nào** → OSPFv3 **không khởi động được** → **phải gõ tay** `router-id` |
| **2** | ⭐ **Cấu hình trên interface**, không dùng `network` | `ipv6 ospf 1 area 0` |
| **3** | ⭐ Hello dùng **link-local** (`FE80::...`) | `show ipv6 ospf neighbor` hiện link-local |
| **4** | ⭐ Authentication qua **IPsec** | OSPFv3 không có field auth riêng |
| **5** | ⭐ Multicast **FF02::5** và **FF02::6** | Tương ứng 224.0.0.5 / 224.0.0.6 |

#### Cấu hình OSPFv3 — 2 cách

```
! ═══ CÁCH 1 (cổ điển, hay xuất hiện trong đề): ipv6 router ospf ═══
ipv6 unicast-routing                            ! BẮT BUỘC, thiếu là không chạy
!
ipv6 router ospf 1
 router-id 1.1.1.1                              ! vẫn dạng IPv4
 auto-cost reference-bandwidth 100000
 passive-interface Loopback0
!
interface GigabitEthernet0/0
 ipv6 address 2001:DB8:0:12::1/64
 ipv6 enable
 ipv6 ospf 1 area 0                             ! bật trên interface
 ipv6 ospf network point-to-point               ! đổi network type
!
interface Loopback0
 ipv6 address 2001:DB8::1/128
 ipv6 ospf 1 area 0

! ═══ CÁCH 2 (Address Family — mới hơn, chạy cả IPv4+IPv6 trong 1 process) ═══
router ospfv3 1
 router-id 1.1.1.1
 !
 address-family ipv6 unicast
  exit-address-family
 !
 address-family ipv4 unicast
  exit-address-family
!
interface GigabitEthernet0/0
 ospfv3 1 ipv6 area 0
 ospfv3 1 ipv4 area 0
```

**Lệnh kiểm tra OSPFv3 (chú ý: `ipv6` thay vì `ip`):**
```
show ipv6 ospf                              ! Router ID, area, ABR/ASBR
show ipv6 ospf neighbor                     ! neighbor (địa chỉ là link-local)
show ipv6 ospf interface                    ! area, cost, network type, DR/BDR
show ipv6 ospf interface brief
show ipv6 ospf database                     ! LSDB
show ipv6 route ospf                        ! bảng route IPv6
show ipv6 protocols
debug ipv6 ospf adj                         ! ⚠️ chỉ lab
```

**Output mẫu `show ipv6 ospf neighbor`:**
```
            OSPFv3 1 address-family ipv6 (router-id 1.1.1.1)

Neighbor ID     Pri   State           Dead Time   Interface ID    Interface
2.2.2.2           1   FULL/  -        00:00:35    3               GigabitEthernet0/0
```
⭐ Chú ý: `Neighbor ID` vẫn là **dạng IPv4** (`2.2.2.2`), và có thêm cột **`Interface ID`**.

**Output mẫu `show ipv6 ospf database`:**
```
            OSPFv3 1 address-family ipv6 (router-id 1.1.1.1)

                Router Link States (Area 0)
ADV Router      Age  Seq#        Fragment ID  Link count  Bits
1.1.1.1         245  0x80000003  0            1           None
2.2.2.2         240  0x80000004  0            1           B

                Link (Type-8) Link States (Area 0)          ← LSA MỚI của v3
ADV Router      Age  Seq#        Link ID    Interface
1.1.1.1         245  0x80000002  3          Gi0/0
2.2.2.2         240  0x80000002  3          Gi0/0

                Intra Area Prefix Link States (Area 0)      ← LSA MỚI (type 9)
ADV Router      Age  Seq#        Link ID    Ref-lstype  Ref-LSID
1.1.1.1         245  0x80000002  0          0x2001      0
```

⭐ **Hai LSA mới của OSPFv3:**

| LSA | Tên | Nhiệm vụ |
|---|---|---|
| **Type 8** | **Link LSA** | Quảng bá **link-local address** + prefix trên link. Scope = **chỉ trên link đó** |
| **Type 9** | **Intra-Area Prefix LSA** | ⭐ Mang **prefix IPv6** — trong v3, LSA type 1/2 **không mang prefix nữa**, chúng chỉ mô tả **topology** |

> ⭐ **Đây là thay đổi kiến trúc quan trọng nhất của OSPFv3:**
> **tách topology khỏi địa chỉ**. LSA 1/2 chỉ nói "ai nối với ai",
> LSA 9 nói "trên đó có prefix gì". Nhờ vậy đổi địa chỉ IPv6 **không cần tính lại SPF**.

---

## 📖 3. HIỂU RÕ HƠN

### 3.1 Area type như mức độ "được biết" của một chi nhánh

Công ty có trụ sở (area 0) và các chi nhánh:

| Area type | Chi nhánh được nhận thông tin gì |
|---|---|
| **Normal** | ⭐ **Toàn bộ**: danh bạ nội bộ (LSA 3) + danh bạ đối tác ngoài (LSA 5) + địa chỉ người liên hệ đối tác (LSA 4) |
| **Stub** | Chỉ **danh bạ nội bộ công ty** (LSA 3). Đối tác ngoài? *"Có gì cứ gửi về trụ sở"* (default route) |
| **Totally Stubby** | ⭐ **Chỉ biết chi nhánh mình**. Mọi thứ khác: *"gửi về trụ sở"* — LSDB nhỏ nhất |
| **NSSA** | Như stub, **nhưng chi nhánh này CÓ đối tác riêng** (có ASBR) nên được phép **giới thiệu đối tác của mình lên trụ sở** (LSA 7) |

🧠 **Một câu để nhớ:** *Stub = **"đừng kể chuyện bên ngoài cho tôi"**.
Totally = **"cũng đừng kể chuyện các chi nhánh khác"**.
NSSA = **"đừng kể cho tôi, nhưng TÔI có chuyện muốn kể cho các anh"**.*

⭐ Và đó là **định nghĩa chính xác** của NSSA: *Not-So-Stubby Area* —
"không hẳn là cụt", vì nó **vẫn có đường ra ngoài riêng**.

### 3.2 Vì sao LSA type 4 tồn tại — như địa chỉ người giao hàng

Bạn ở area 1. Nhận được thông báo (LSA 5):
> *"Hàng `8.8.8.0/24` do anh **R4 (4.4.4.4)** giữ."*

Nhưng bạn ở area 1, **không có bản đồ area 2** (LSA 1 không ra khỏi area)
→ bạn **không biết anh R4 ở đâu** → thông báo vô dụng.

Nên ABR phải dán thêm một tờ (LSA 4):
> *"Muốn tới anh R4 (4.4.4.4) thì đi qua tôi, cách 100 bước."*

🧠 **Một câu để nhớ:** *LSA 5 = **"hàng ở đâu"**. LSA 4 = **"người giữ hàng ở đâu"**.
Đó là lý do LSA 4 do **ABR** sinh (chỉ ABR biết đường tới area khác),
và cũng là lý do **stub area chặn CẢ 4 VÀ 5** — chặn 5 mà giữ 4 thì vô nghĩa.*

### 3.3 Summarization = xây tường chắn sự cố

Area 1 có 4 subnet `172.16.0.0/24` → `172.16.3.0/24`.

**Không summarize:** subnet `.1.0/24` nhấp nháy → LSA 3 của `.1.0/24` đổi →
flood ra area 0 và area 2 → ⭐ **MỌI router trong AS chạy lại SPF** mỗi lần nhấp nháy.

**Có summarize (`/22`):** ABR chỉ quảng bá **một** LSA 3 cho `172.16.0.0/22`.
Subnet `.1.0/24` nhấp nháy → ⭐ **LSA `/22` KHÔNG ĐỔI** (vì `/22` vẫn còn `.0.0`, `.2.0`, `.3.0`)
→ **area 0 và area 2 không hề biết** → **không chạy lại SPF**.

🧠 **Một câu để nhớ:** *Summarization không chỉ để **bảng route gọn** —
lợi ích lớn hơn nhiều là **giới hạn phạm vi lan của sự cố**.
Đó là bức tường chắn giữa các area.*

⭐ Và **cái giá**: bạn mất khả năng biết subnet nào đang chết.
Bức tường chắn cả **thông tin xấu** lẫn **thông tin hữu ích**.

### 3.4 `distribute-list in` — chặn ở cửa nhà, không chặn ở bưu điện

| | `area filter-list` / `not-advertise` | ⭐ `distribute-list in` |
|---|---|---|
| Ví von | ⭐ **Chặn ở bưu điện** — thư không bao giờ được gửi đi | ⭐ **Chặn ở cửa nhà mình** — thư vẫn đến, mình không mở |
| LSDB | LSA **không tồn tại** | LSA **vẫn có đủ** |
| Router khác | Cũng không biết | ⭐ **Vẫn biết bình thường** |
| Vẫn flood cho neighbor? | Không có gì để flood | ⭐ **Vẫn flood** |

🔴 **Vì sao `distribute-list in` nguy hiểm:** router A không có route (không mở thư),
nhưng router B **vẫn thấy LSA** và tin *"đi qua A là tới được"* →
gửi traffic cho A → **A không biết forward đi đâu → drop** → **black hole**.

🧠 **Một câu để nhớ:** *Trong OSPF, LSA **phải** được flood nguyên vẹn để LSDB đồng bộ —
nên `distribute-list in` **không thể** chặn LSA, nó chỉ chặn **route vào RIB của chính mình**.
Đây là điểm khác biệt cốt lõi giữa lọc trong link-state và lọc trong distance-vector.*

### 3.5 OSPFv3 tách topology khỏi địa chỉ

**OSPFv2:** LSA type 1 nói *"tôi nối R2, và trên link đó có subnet `10.0.12.0/30`"*
→ **topology và địa chỉ trộn vào nhau**.
→ Đổi địa chỉ subnet = đổi LSA 1 = ⭐ **chạy lại SPF** (dù topology không đổi!)

**OSPFv3:** tách làm hai:
- **LSA 1/2**: *"tôi nối R2 qua Interface ID 3"* — ⭐ **chỉ topology, không có prefix**
- **LSA 9 (Intra-Area Prefix)**: *"trên Interface ID 3 có prefix `2001:DB8:0:12::/64`"*

→ Đổi prefix chỉ đổi LSA 9 → ⭐ **cập nhật bảng route mà KHÔNG chạy lại SPF**.

🧠 **Một câu để nhớ:** *OSPFv3 hỏi hai câu riêng: **"ai nối với ai"** (LSA 1/2)
và **"trên đó có địa chỉ gì"** (LSA 9). Tách ra nên đổi địa chỉ không phải vẽ lại bản đồ.*

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

## 💡 5. THỰC CHIẾN ĐI LÀM

| Chủ đề | Thi dạy | Thực tế đi làm |
|---|---|---|
| **Area type** | 5 loại | ⭐ Thực tế **90% là Normal area**. Stub/NSSA dùng cho **nhánh xa, thiết bị yếu** (router chi nhánh, switch access L3). Đừng phức tạp hóa nếu không có lý do |
| ⭐ **Chọn area type nào** | Bảng LSA | ⭐ Quy tắc thực tế: nhánh **không có ASBR** → **Totally Stubby** (LSDB nhỏ nhất). Nhánh **có ASBR riêng** → **NSSA** (hoặc Totally NSSA). Backbone/core → **Normal** |
| ⭐ **Khai area type** | Trên mọi router | 🔴 **Thiếu 1 router = mất neighbor.** Quy trình: viết block config → copy-paste **cùng một block** lên mọi router trong area → verify `show ip ospf \| inc stub\|nssa` trên **tất cả** |
| **`no-summary`** | Chỉ trên ABR | ⭐ Nhớ: khai trên router nội bộ **không lỗi nhưng vô tác dụng** — dễ tưởng đã cấu hình xong |
| ⚠️ **NSSA default route** | Bẫy đề | 🔴 **NSSA KHÔNG tự có default route.** Rất nhiều người triển khai NSSA rồi thắc mắc "sao nhánh không ra được Internet". Phải thêm `area X nssa default-information-originate` |
| ⭐ **Summarization** | Gộp route | ⭐ **Lợi ích thật không phải bảng route gọn** — mà là **chặn LSA flooding**: subnet nhấp nháy trong area không làm area khác chạy lại SPF. Đây là **cách giới hạn fault domain hiệu quả nhất** của OSPF |
| ⭐ **Thiết kế IP** | Không dạy | 🔴 **Không có contiguous addressing thì không summarize được.** Phải quy hoạch IP theo area **NGAY TỪ ĐẦU** (VD area 1 = `10.1.0.0/16`, area 2 = `10.2.0.0/16`). Sửa sau = re-IP toàn mạng |
| **Discard route (Null0)** | Không dạy | ⭐ IOS tự tạo — **đừng xóa nó**. Nó chống loop khi có gói tới subnet không tồn tại trong dải gộp |
| ⚠️ **Black hole do summarize** | Không dạy | ⚠️ Chỉ gộp dải mà **mọi subnet trong đó đều thuộc area này**. Gộp `/22` khi chỉ có 2/4 subnet → hút traffic của 2 subnet còn lại vào hố đen |
| **`area range` metric** | Nhỏ nhất | ⭐ Ép `cost` khi muốn điều khiển đường đi giữa 2 ABR cùng quảng bá 1 dải gộp |
| 🔴 **`distribute-list in`** | Có lệnh | 🔴 **Cực nguy hiểm ở production.** Nó chỉ chặn RIB của **1 router**, LSDB vẫn đủ, router khác vẫn tin "đi qua đây tới được" → **black hole**. ⭐ Muốn lọc thật thì dùng **`area filter-list`** hoặc **`area range not-advertise`** trên ABR |
| ⭐ **Prefix-list catch-all** | Bẫy | 🔴 Prefix-list có **implicit deny**. Thiếu `permit 0.0.0.0/0 le 32` ở cuối = **chặn hết**. Đây là lỗi gây downtime thật |
| **`default-information originate always`** | Có tùy chọn | 🔴 **Tránh `always`.** Router mất đường ra Internet mà vẫn quảng bá default → hút toàn bộ traffic vào hố đen. ⭐ Dùng **không có `always`** + **IP SLA/track** trên default route (Module-03 §2.4) |
| **Authentication** | 3 loại | ⭐ Production nên bật ít nhất **MD5** trên **mọi** link OSPF (chống router lạ cắm vào). SHA (key-chain) nếu thiết bị hỗ trợ. Dùng **interface-level** cho linh hoạt |
| **Rotate key** | Không dạy | ⭐ MD5 hỗ trợ nhiều key ID — thêm key mới (`key 2`) trên mọi router **trước**, rồi xóa key cũ. Không bị downtime |
| ⚠️ **Virtual link** | Cách vá | ⚠️ **Là dấu hiệu thiết kế sai**, không phải giải pháp. Nếu phải dùng lâu dài → thêm link vật lý tới area 0 hoặc gộp area. Virtual link thêm độ phức tạp và điểm lỗi |
| ⭐ **OSPFv3 Router ID** | 32-bit dạng IPv4 | 🔴 Router **IPv6-only** → OSPFv3 **không tự chọn được Router ID** → **không khởi động**. ⭐ **LUÔN gõ tay `router-id`** trong mọi triển khai OSPFv3 |
| **OSPFv3 auth** | Qua IPsec | ⭐ Phức tạp hơn v2 nhiều. Nhiều nơi bỏ auth OSPFv3 và dựa vào bảo mật L2/port security thay thế |
| **Chạy song song v2 + v3** | Không dạy | ⭐ Bình thường ở production (dual-stack). ⚠️ Nhớ: **2 process độc lập**, LSDB riêng, có thể có **topology khác nhau** cho IPv4 và IPv6 → phải verify **cả hai** |
| **Tài liệu hóa** | Không có | ⭐ Bảng bắt buộc có: area nào loại gì · ABR/ASBR nào · dải IP mỗi area · summarize ở đâu với mask nào · filter nào ở đâu và **vì sao** · auth key. Thiếu tài liệu = không ai dám sửa |

---

## 🎓 6. BẪY TRONG ĐỀ ENCOR

| # | Bẫy | Sự thật |
|:---:|---|---|
| 1 | LSA **type 4** — ai sinh, LS ID là gì | ⭐ **ABR** sinh · LS ID = ⭐ **Router ID của ASBR** |
| 2 | LSA **type 5** — ai sinh, flood đâu | ⭐ **ASBR** sinh · flood ⭐ **TOÀN AS** (trừ stub/NSSA) |
| 3 | ⭐ Vì sao cần LSA type 4 | Router ở area khác **không có LSA 1 của ASBR** → không biết ASBR ở đâu → LSA 5 vô dụng. LSA 4 nói "ASBR ở hướng này" |
| 4 | ASBR **cùng area** có cần LSA 4? | ❌ **Không** — đã có LSA type 1 của ASBR |
| 5 | ⭐ **Stub** chặn LSA nào | ⭐ **LSA 4 + 5** |
| 6 | ⭐ **Totally Stubby** chặn LSA nào | ⭐ **LSA 3 + 4 + 5** (thêm LSA 3 so với stub) |
| 7 | ⭐ **NSSA** chặn LSA nào, cho phép gì | Chặn **4 + 5**, ⭐ **cho phép LSA 7** |
| 8 | **Totally NSSA** | Chặn **3 + 4 + 5**, cho phép **LSA 7** |
| 9 | ⭐ `no-summary` cấu hình ở đâu | ⭐ **CHỈ trên ABR** |
| 10 | 🔴 Area type khai ở đâu | ⭐ **MỌI router trong area** — thiếu 1 = **E-bit mismatch** = mất neighbor |
| 11 | Area 0 có thể là stub? | ❌ **KHÔNG** |
| 12 | Area có ASBR có thể là stub? | ❌ **KHÔNG** (stub chặn LSA 5) → ⭐ **dùng NSSA** |
| 13 | 🔴 **NSSA có tự động default route?** | ❌ **KHÔNG!** Khác stub. Phải `area X nssa default-information-originate` |
| 14 | Default route trong stub là loại gì | ⭐ **`O*IA`** — LSA type **3** do ABR inject (không phải LSA 5) |
| 15 | LSA 7 → 5 do ai dịch | ⭐ **ABR của NSSA** (NSSA translator) |
| 16 | `Forward Address` trong LSA 7 | ⭐ Là **IP của ASBR** (không phải `0.0.0.0` như LSA 5 thường) |
| 17 | Ký hiệu route NSSA external | **`O N1`** / **`O N2`** |
| 18 | ⭐ `area range` vs `summary-address` | `area range` → ⭐ **ABR**, gộp **LSA 3** · `summary-address` → ⭐ **ASBR**, gộp **LSA 5/7** |
| 19 | ⭐ Lợi ích lớn nhất của summarization | ⭐ **Chặn LSA flooding** → subnet nhấp nháy không làm area khác chạy lại SPF (không chỉ là "bảng route gọn") |
| 20 | Metric của summary route (mặc định) | ⭐ **Metric NHỎ NHẤT** trong các route thành phần |
| 21 | Discard route Null0 để làm gì | ⭐ **Chống loop** — drop gói tới subnet không tồn tại trong dải gộp, ngay tại ABR/ASBR |
| 22 | ⭐ Lệnh nào lọc route mà **KHÔNG** ảnh hưởng LSDB | ⭐ **`distribute-list ... in`** |
| 23 | 🔴 Vì sao `distribute-list in` nguy hiểm | LSDB vẫn đủ, router khác **vẫn tin** "đi qua đây tới được" → ⭐ **black hole** |
| 24 | `area filter-list ... in` vs `out` | `in` = chặn LSA 3 **VÀO** area · `out` = chặn LSA 3 **RA KHỎI** area (nhìn từ góc độ area) |
| 25 | `distribute-list out` trong OSPF | ⚠️ Chỉ hoạt động **trên ASBR**, chỉ lọc route **redistribute** — **không** lọc LSA 3 |
| 26 | Prefix-list thiếu catch-all | 🔴 **Implicit deny** → chặn **hết** thay vì 1 dải |
| 27 | `default-information originate` vs `always` | Không `always`: chỉ quảng bá **nếu có** `0.0.0.0/0` trong RIB · ⚠️ `always`: quảng bá **luôn** → nguy cơ black hole |
| 28 | Auth: interface-level vs area-level | ⭐ **Interface-level thắng.** `ip ospf authentication null` tắt auth trên 1 interface |
| 29 | Virtual link dùng gì để chỉ đầu kia | ⭐ **Router ID**, không phải IP interface |
| 30 | Transit area của virtual link có thể là stub? | ❌ **KHÔNG** — cần LSA 3/4/5 đi qua |
| 31 | Virtual link sinh Link Type nào trong LSA 1 | **Type 4** (Virtual link) |
| 32 | 🔴 **OSPFv3 Router ID** | ⭐ **VẪN LÀ 32-bit dạng IPv4.** Router IPv6-only → **không tự chọn được** → **phải gõ tay** |
| 33 | OSPFv3 bật vào OSPF bằng lệnh gì | ⭐ **`ipv6 ospf 1 area X`** trên **interface** (không dùng `network`) |
| 34 | OSPFv3 multicast | ⭐ **FF02::5** và **FF02::6** |
| 35 | OSPFv3 Hello dùng địa chỉ nguồn nào | ⭐ **Link-local (`FE80::/10`)** |
| 36 | OSPFv3 authentication | ⭐ Dùng **IPsec (AH/ESP)** — không có field auth riêng |
| 37 | ⭐ LSA mới của OSPFv3 | ⭐ **Type 8 (Link LSA)** và **Type 9 (Intra-Area Prefix LSA)** |
| 38 | ⭐ Vì sao v3 có Type 9 | ⭐ Trong v3, LSA 1/2 **không mang prefix** — chỉ mô tả topology. Prefix nằm ở LSA 9 → **tách topology khỏi địa chỉ** |
| 39 | LSA 3 và 4 trong OSPFv3 gọi là gì | LSA 3 → **Inter-Area Prefix LSA** · LSA 4 → **Inter-Area Router LSA** |
| 40 | Ký hiệu route OSPFv3 inter-area | ⭐ **`OI`** (v2 là `O IA`) |
| 41 | Next-hop trong `show ipv6 route ospf` | ⭐ **Link-local address**, không phải global unicast |
| 42 | Thiếu `ipv6 unicast-routing` | OSPFv3 **không chạy** — không có neighbor, không có route |

---

## 🐛 7. GỠ LỖI NHANH

### 7.1 Hộp lệnh vạn năng

```
! ═══ AREA TYPE ═══
show ip ospf | include Area|stub|nssa|It is|generates    ! area type + ABR/ASBR
show ip ospf database database-summary                   ! ĐẾM LSA — chứng minh bị chặn
show ip ospf | section Area 1                            ! chi tiết 1 area

! ═══ LSA TYPE 4, 5, 7 ═══
show ip ospf database asbr-summary                       ! LSA 4
show ip ospf database external                            ! LSA 5
show ip ospf database external <prefix>
show ip ospf database nssa-external                       ! LSA 7
show ip ospf border-routers                               ! ABR/ASBR nào biết + cost

! ═══ SUMMARIZATION ═══
show ip ospf database summary | include <prefix>          ! LSA 3 có bị gộp?
show ip route | include Null0                             ! discard route
show ip route <summary-prefix>                            ! metric + Null0
show running-config | section router ospf                 ! xem area range / summary-address

! ═══ FILTERING ═══
show ip prefix-list
show ip prefix-list detail <TÊN>                          ! có counter hit
show ip ospf | include filter
show running-config | include distribute-list|filter-list
! SO SÁNH LSDB vs RIB để biết lọc ở đâu:
show ip ospf database summary | include <prefix>          ! LSA còn không?
show ip route <prefix>                                    ! route có không?

! ═══ AUTHENTICATION ═══
show ip ospf interface Gi0/0 | include authentication|Message digest|Cryptographic|key
show key chain

! ═══ VIRTUAL LINK ═══
show ip ospf virtual-links
show ip ospf neighbor | include VL
show ip ospf database router | include Virtual

! ═══ DEFAULT ROUTE ═══
show ip route 0.0.0.0
show ip ospf database external 0.0.0.0
show ip ospf | include default

! ═══ SPF (đo lợi ích summarization) ═══
show ip ospf | include SPF algorithm executed             ! đếm số lần SPF
show ip ospf statistics                                    ! chi tiết SPF theo area

! ═══ OSPFv3 (chú ý: ipv6 thay vì ip) ═══
show ipv6 ospf                                            ! Router ID, area, ABR/ASBR
show ipv6 ospf neighbor                                   ! neighbor
show ipv6 ospf interface                                  ! link-local, Interface ID
show ipv6 ospf interface brief
show ipv6 ospf database                                   ! Type-8, Type-9
show ipv6 route ospf                                      ! ký hiệu OI, next-hop link-local
show ipv6 protocols
debug ipv6 ospf adj                                       ! ⚠️ chỉ lab

! ═══ DEBUG (⚠️ chỉ lab) ═══
debug ip ospf adj                                         ! lỗi adjacency (E-bit/auth/area)
debug ip ospf lsa-generation                              ! xem LSA nào được sinh
debug ip ospf spf                                         ! xem SPF chạy
undebug all
```

### 7.2 Bảng lỗi: triệu chứng → nguyên nhân → cách sửa

| # | Triệu chứng | Nguyên nhân | Lệnh chẩn đoán | Cách sửa |
|:---:|---|---|---|---|
| 1 | 🔴 Mất neighbor sau khi cấu hình stub/NSSA | ⭐ **Area type không khai đủ mọi router** (E-bit/N-bit mismatch) | `show ip ospf \| inc stub\|nssa` trên **MỌI** router trong area · `debug ip ospf adj` | Khai area type trên **tất cả** router |
| 2 | Khai `no-summary` mà LSA 3 vẫn có | `no-summary` khai trên **router nội bộ**, không phải ABR | `show ip ospf \| inc It is an` (có "area border router"?) | Khai `no-summary` **trên ABR** |
| 3 | Area có ASBR mà route external không ra được | Area được khai **stub** (chặn LSA 5) | `show ip ospf \| inc stub` | ⭐ Đổi sang **NSSA** |
| 4 | 🔴 NSSA: nhánh **không ra được Internet** | ⭐ **NSSA không tự có default route** | `show ip route 0.0.0.0` → không có | ⭐ `area X nssa default-information-originate` trên ABR |
| 5 | Route external biến mất ở area khác | Area đó là stub/NSSA (đúng thiết kế) | `show ip ospf db database-summary` → Type-5 = 0 | ✅ Đúng — dùng default route |
| 6 | `O E2` có nhưng ping fail | ⭐ **Thiếu LSA type 4** → không biết đường tới ASBR | `show ip ospf db asbr-summary` · `show ip ospf border-routers` | Kiểm tra ABR có sinh LSA 4 · kiểm tra area type có chặn LSA 4 |
| 7 | Summarize rồi mà bên kia vẫn thấy route lẻ | `area range` khai trên **router sai** (không phải ABR của area đó) | `show run \| sec router ospf` · `show ip ospf \| inc It is an` | Khai trên **ABR của area chứa các subnet đó** |
| 8 | `summary-address` không có tác dụng | Khai trên **ABR** thay vì **ASBR** | `show ip ospf \| inc autonomous system` | Khai trên **ASBR** |
| 9 | ⚠️ Traffic tới subnet không tồn tại bị **drop** | ✅ **Discard route Null0** — đúng thiết kế | `show ip route \| inc Null0` | Không cần sửa (nếu subnet đúng ra phải ở nơi khác thì sửa thiết kế) |
| 10 | ⚠️ **Black hole** sau khi summarize | Dải gộp bao gồm subnet **không thuộc area này** | `show ip route <summary>` trên ABR · so với thiết kế IP | Chỉ gộp dải mà mọi subnet đều thuộc area · sửa quy hoạch IP |
| 11 | 🔴 Sau khi thêm prefix-list, **mất gần hết route** | ⭐ **Prefix-list thiếu catch-all** (implicit deny) | `show ip prefix-list detail <TÊN>` → xem counter | Thêm `permit 0.0.0.0/0 le 32` ở seq cuối |
| 12 | ⭐ Route bị lọc trên 1 router, router khác vẫn gửi traffic qua đó | ⭐ Dùng **`distribute-list in`** — LSDB vẫn đủ → **black hole** | So `show ip ospf db summary <prefix>` (có LSA) vs `show ip route <prefix>` (không route) | ⭐ Dùng **`area filter-list`** hoặc **`area range not-advertise`** trên ABR |
| 13 | Filter `out` không có tác dụng | Nhầm chiều — `out` lọc LSA **ra khỏi** area | `show run \| inc filter-list` | Đổi sang `in` (hoặc ngược lại) |
| 14 | Mất neighbor sau khi bật auth | Key hoặc loại auth **lệch** | `show ip ospf int Gi0/0 \| inc auth\|digest` cả 2 đầu · `debug ip ospf adj` | Khớp loại + key ID + key string |
| 15 | Bật area auth mà 1 link vẫn không lên | Interface đó chưa đặt `message-digest-key` | `show ip ospf int <if> \| inc digest` | Đặt key trên interface, hoặc `ip ospf authentication null` |
| 16 | ⚠️ Default route hút traffic vào hố đen | ⭐ `default-information originate **always**` mà router mất đường ra | `show ip route 0.0.0.0` trên ASBR | Bỏ `always` + dùng **IP SLA/track** (Module-03) |
| 17 | Virtual link `down` | Transit area là **stub/NSSA** · sai Router ID · auth lệch | `show ip ospf virtual-links` · `show ip ospf \| inc stub` | Transit area phải là **normal** · dùng đúng Router ID · khớp auth |
| 18 | Route area xa không tới được | Area **không nối area 0** | `show ip ospf \| inc Area` trên các ABR | Thêm link tới area 0, hoặc **virtual link** (tạm) |
| 19 | 🔴 **OSPFv3 không chạy** — không neighbor, không route | ⭐ Thiếu **`ipv6 unicast-routing`** | `show ipv6 protocols` · `show run \| inc ipv6 unicast` | `ipv6 unicast-routing` |
| 20 | 🔴 OSPFv3 báo **không chọn được Router ID** | ⭐ Router **IPv6-only**, không có IPv4 nào | `show ipv6 ospf \| inc Router ID` | ⭐ **Gõ tay** `router-id x.x.x.x` |
| 21 | OSPFv3 neighbor không lên | Network type lệch · area lệch · MTU · thiếu `ipv6 enable` | `show ipv6 ospf interface <if>` **cả 2 đầu** rồi so | Khớp từng dòng |
| 22 | Có route OSPFv2 nhưng không có OSPFv3 (dual-stack) | ⭐ **2 process độc lập** — cấu hình v3 chưa đủ | `show ipv6 ospf interface brief` (interface nào trong v3?) | Bật `ipv6 ospf 1 area X` trên đủ interface |
| 23 | ⭐ CPU cao, SPF chạy liên tục | Link nhấp nháy + **không có summarization** → LSA flood toàn AS | ⭐ `show ip ospf \| inc SPF algorithm executed` (tăng nhanh?) · `show ip ospf db router` → Seq# | Sửa link flapping · ⭐ **thêm summarization** để chặn LSA lan |

### 7.3 ⭐ Quy trình troubleshoot Module-04B — 4 câu hỏi

```
CÂU HỎI 1: "Route bị mất — LSA có tồn tại không?"
   show ip ospf database database-summary
   show ip ospf database summary|external|asbr-summary|nssa-external
   ├─ LSA KHÔNG CÓ  → bị chặn ở NGUỒN → sang câu hỏi 2
   └─ LSA CÓ mà route không có → bị chặn ở RIB → distribute-list in!
        ↓
CÂU HỎI 2: "LSA bị chặn bởi cái gì?"
   show ip ospf | include stub|nssa|It is
   ├─ Area là STUB      → LSA 4, 5 bị chặn (đúng thiết kế)
   ├─ Area là TOTALLY   → LSA 3, 4, 5 bị chặn
   ├─ Area là NSSA      → LSA 4, 5 bị chặn, LSA 7 OK
   └─ Area NORMAL       → sang câu hỏi 3
        ↓
CÂU HỎI 3: "Có filter hoặc summarize nào không?"
   show running-config | section router ospf
   ├─ area range ... not-advertise  → LSA bị ẩn
   ├─ area filter-list              → check chiều in/out + prefix-list catch-all
   ├─ area range <prefix>           → route bị GỘP (tìm prefix ngắn hơn!)
   └─ summary-address               → external bị gộp
        ↓
   show ip prefix-list detail <TÊN>   → counter có hit không? catch-all có chưa?
        ↓
CÂU HỎI 4: "Có route dạng gộp hoặc default không?"
   show ip route <prefix>            → % Network not in table?
   show ip route 0.0.0.0             → có default (O*IA / O*E2)?
   show ip route | include Null0      → discard route?
   → Nếu có default route thì traffic VẪN ĐI ĐƯỢC dù không có route cụ thể
```

> ⭐ **Câu hỏi 1 là bước quan trọng nhất và người mới hay bỏ:**
> **"LSA có tồn tại không?"** — nó phân chia bài toán làm hai nửa hoàn toàn khác nhau.
> LSA không có = chặn ở nguồn (area type / filter trên ABR).
> LSA có mà route không có = ⭐ **`distribute-list in`** (và đó là dấu hiệu của black hole).

---

## 📝 8. QUIZ TỰ KIỂM TRA

**Câu 1.** LSA type 4 do ai sinh ra? LS ID là gì? Vì sao nó cần tồn tại?

<details><summary>Xem đáp án</summary>

- **Ai sinh:** ⭐ **ABR**
- **LS ID:** ⭐ **Router ID của ASBR**
- **Flood tới:** area khác

**Vì sao cần:**

LSA type 5 (do ASBR sinh, flood **toàn AS**) nói: *"mạng `8.8.8.0/24` tới được qua ASBR `4.4.4.4`"*.

Nhưng router ở **area khác** **không có LSA type 1 của ASBR** (LSA 1 không ra khỏi area)
→ nó **không biết đi đường nào tới `4.4.4.4`** → **LSA 5 vô dụng**, route bị loại khỏi RIB.

**LSA type 4** vá chỗ đó: ABR nói *"muốn tới ASBR `4.4.4.4` thì đi qua tôi, cost X"*.

🧠 **LSA 5 = "mạng ở đâu" · LSA 4 = "người giữ mạng ở đâu".** Thiếu một trong hai thì route vô dụng.

⭐ **Ngoại lệ:** ASBR **cùng area** thì **không cần** LSA 4 — router đã có LSA type 1 của ASBR.

**Verify:**
```
show ip ospf database asbr-summary        ! Link State ID = Router ID của ASBR
show ip ospf border-routers               ! ASBR nào biết + cost
```
</details>

---

**Câu 2.** Điền bảng: mỗi area type chặn LSA nào, có default route tự động không?

<details><summary>Xem đáp án</summary>

| Area type | LSA 1,2 | LSA 3 | LSA 4,5 | LSA 7 | Default tự động |
|---|:---:|:---:|:---:|:---:|---|
| **Normal / Backbone** | ✅ | ✅ | ✅ | ❌ | Nếu có ASBR quảng bá |
| **Stub** | ✅ | ✅ | ❌ **chặn** | ❌ | ⭐ **Có** — ABR inject → `O*IA` |
| **Totally Stubby** | ✅ | ❌ **chặn** | ❌ **chặn** | ❌ | ⭐ **Có** — ABR inject |
| **NSSA** | ✅ | ✅ | ❌ **chặn** | ✅ **OK** | 🔴 **KHÔNG!** Phải `default-information-originate` |
| **Totally NSSA** | ✅ | ❌ **chặn** | ❌ **chặn** | ✅ **OK** | ⭐ **Có** (vì `no-summary`) |

**Cách nhớ:**
- **Stub** = chặn **4 + 5** (external)
- **Totally** (`no-summary`) = chặn **thêm 3** (inter-area)
- **NSSA** = như stub, **nhưng cho phép 7**

🔴 **Bẫy đề số 1:** **NSSA KHÔNG tự có default route** (khác stub).
Vì NSSA **có ASBR riêng** → có thể tự có đường ra → Cisco không tự inject để tránh ghi đè.
</details>

---

**Câu 3.** Bạn cấu hình `area 1 stub` và mất neighbor ngay. Nguyên nhân và cách sửa?

<details><summary>Xem đáp án</summary>

**Nguyên nhân: chưa khai `area 1 stub` trên MỌI router trong area 1.**

**Cơ chế:** trong gói Hello có **E-bit** (External capability):
- E-bit = **1** → area **normal**
- E-bit = **0** → area **stub**

E-bit là **điều kiện adjacency** (điều kiện #8 ở Module-04A §2.5) → lệch = **không lên neighbor**.

**Chẩn đoán:**
```
show ip ospf | include stub|nssa|Area          ← chạy trên MỌI router trong area
debug ip ospf adj
! %OSPF-5-ADJCHG: ... Neighbor Down: Adjacency forced to reset
```

**Sửa:** khai `area 1 stub` trên **tất cả** router có interface trong area 1 — **kể cả ABR**.

⭐ **Quy trình production:**
1. Viết block config một lần
2. Copy-paste **cùng block** lên mọi router trong area
3. Verify `show ip ospf | include stub` trên **tất cả**
4. ⚠️ Có cửa sổ bảo trì — thay đổi area type gây hội tụ lại

**Lưu ý về `no-summary`:** chỉ ABR cần thêm. Khai trên router nội bộ **không lỗi**
nhưng **không có tác dụng** — dễ tưởng đã xong.
</details>

---

**Câu 4.** Phân biệt `area 1 range` và `summary-address`: cấu hình ở đâu, gộp loại route nào?

<details><summary>Xem đáp án</summary>

| | **`area <X> range`** | **`summary-address`** |
|---|---|---|
| Cấu hình trên | ⭐ **ABR** | ⭐ **ASBR** |
| Gộp loại LSA | ⭐ **LSA 3** (Summary/inter-area) | ⭐ **LSA 5 / LSA 7** (External) |
| Route bị gộp | `O IA` | `O E1` / `O E2` / `O N1` / `O N2` |
| Nguồn route | Từ **area X** sang area khác | Từ **redistribution** vào OSPF |
| Cú pháp | `area 1 range 172.16.0.0 255.255.252.0` | `summary-address 203.0.112.0 255.255.252.0` |
| Discard route Null0 | ✅ Tự tạo trên ABR | ✅ Tự tạo trên ASBR |
| Metric mặc định | Nhỏ nhất trong nhóm | Nhỏ nhất trong nhóm |

🧠 **Cách nhớ:** *`area range` — có chữ "**area**" → ⭐ **ABR** (router biên **area**), gộp route giữa area.
`summary-address` — không có chữ "area" → ⭐ **ASBR** (router biên **AS**), gộp route ngoài AS.*

⭐ **Bẫy đề:** khai `summary-address` trên ABR (không phải ASBR) → **không có tác dụng**, và ngược lại.
</details>

---

**Câu 5.** Nêu lợi ích **lớn nhất** của summarization (không phải "bảng route gọn"), và giải thích cơ chế.

<details><summary>Xem đáp án</summary>

⭐ **Lợi ích lớn nhất: CHẶN LSA FLOODING → giới hạn phạm vi chạy SPF (fault domain).**

**Cơ chế:**

Area 1 có 4 subnet `172.16.0.0/24` → `172.16.3.0/24`.

**KHÔNG summarize:**
- Subnet `172.16.1.0/24` nhấp nháy
- → LSA 3 của `172.16.1.0/24` bị withdraw rồi re-advertise
- → Flood ra **area 0 và mọi area khác**
- → ⚠️ **MỌI router trong AS chạy lại SPF** mỗi lần nhấp nháy
- → CPU cao toàn mạng, route flapping, CEF dựng lại FIB liên tục (Module-01)

**CÓ summarize (`area 1 range 172.16.0.0 255.255.252.0`):**
- ABR chỉ quảng bá **một** LSA 3 cho `172.16.0.0/22`
- Subnet `.1.0/24` nhấp nháy
- → ⭐ **LSA `/22` KHÔNG ĐỔI** (vì `/22` vẫn còn `.0.0`, `.2.0`, `.3.0`)
- → Area 0 và area 2 ⭐ **KHÔNG NHẬN LSA MỚI**
- → ⭐ **KHÔNG chạy lại SPF**

**Cách đo trong lab:**
```
show ip ospf | include SPF algorithm executed     ← trước
! làm subnet nhấp nháy
show ip ospf | include SPF algorithm executed     ← sau: có tăng không?
```

**Cái giá phải trả:**
- ⚠️ Mất chi tiết — không biết subnet nào đang chết
- ⚠️ Nguy cơ **black hole** nếu dải gộp bao gồm subnet không tồn tại ở area này
- 🔴 **Yêu cầu quy hoạch IP theo area NGAY TỪ ĐẦU** (contiguous addressing) —
  không có thì không summarize được

🧠 **Summarization là bức tường chắn giữa các area** — nó chắn cả thông tin xấu (LSA flapping)
lẫn thông tin hữu ích (subnet nào up/down).
</details>

---

**Câu 6.** Sau khi cấu hình `area 1 range 172.16.0.0 255.255.252.0`, trên ABR xuất hiện
route `172.16.0.0/22 → Null0`. Đây là gì và vì sao cần?

<details><summary>Xem đáp án</summary>

**Đây là DISCARD ROUTE** (route loại bỏ), IOS **tự tạo** trên ABR/ASBR khi bạn cấu hình summarization.

```
ABR# show ip route 172.16.0.0 255.255.252.0
Routing entry for 172.16.0.0/22
  Known via "ospf 1", distance 110, metric 1, type intra area
  Routing Descriptor Blocks:
  * directly connected, via Null0
```

**Vì sao cần — chống routing loop:**

1. ABR quảng bá `172.16.0.0/22` ra area khác
2. Có gói tới `172.16.9.9` — subnet này **không tồn tại** trong area 1
3. Router area 0 thấy `/22` → gửi gói cho ABR
4. ⚠️ **Nếu không có discard route:** ABR tra bảng route → không có `/24` cụ thể →
   có thể match **default route** hoặc route khác → **gửi gói NGƯỢC ra area 0** → **LOOP**
5. ✅ **Có discard route:** ABR match `/22 → Null0` → ⭐ **drop gói ngay tại ABR**

⭐ **Đừng xóa nó.** Có thể tắt nhưng không nên:
```
router ospf 1
 no discard-route internal        ! ⚠️ KHÔNG khuyến nghị
 no discard-route external
```

**Cách nhìn thấy:**
```
show ip route | include Null0
! O        172.16.0.0/22 is a summary, 00:01:22, Null0
```

**Test:** `ping 172.16.9.9` từ area khác → fail (bị drop tại Null0) — **đúng, không loop**.
</details>

---

**Câu 7.** Lệnh nào lọc route OSPF mà **KHÔNG** ảnh hưởng LSDB? Vì sao nó nguy hiểm?

<details><summary>Xem đáp án</summary>

⭐ **`distribute-list <prefix-list|acl> in`**

```
ip prefix-list PL-X seq 5 deny 172.16.4.0/24
ip prefix-list PL-X seq 10 permit 0.0.0.0/0 le 32
!
router ospf 1
 distribute-list prefix PL-X in
```

**Vì sao LSDB không bị ảnh hưởng:**

OSPF là **link-state** → LSA **phải** được flood **nguyên vẹn** để mọi router cùng area có
LSDB giống nhau. Nếu cho phép lọc LSA giữa các router thì LSDB sẽ lệch → SPF ra kết quả khác nhau
→ routing loop.

Nên `distribute-list in` chỉ can thiệp ở bước **LSDB → RIB** trên **chính router đó**.

**Chứng minh:**
```
show ip ospf database summary | include 172.16.4      ← LSA VẪN CÓ
show ip route 172.16.4.0                               ← ❌ route KHÔNG có
```

🔴 **Vì sao nguy hiểm — BLACK HOLE:**
- Router A: không có route (đã lọc) — không biết forward `172.16.4.0/24` đi đâu
- Router B: ⭐ **vẫn thấy LSA đầy đủ**, và LSA đó nói "đi qua A là tới được"
- → B gửi traffic cho A → **A drop** → ⭐ **black hole**

⭐ **Muốn lọc THẬT thì dùng trên ABR:**
```
router ospf 1
 area 1 range 172.16.4.0 255.255.255.0 not-advertise     ! LSA không được sinh
! hoặc
 area 1 filter-list prefix PL-X out                       ! lọc LSA 3 theo prefix-list
```
→ LSA **không tồn tại** → **mọi router** đều không biết → **nhất quán**, không black hole.

**Bảng so sánh:**

| | LSDB | RIB local | Router khác biết? |
|---|:---:|:---:|:---:|
| `area range not-advertise` / `area filter-list` | ❌ Không có LSA | ❌ | ❌ **Không** |
| ⭐ `distribute-list in` | ⭐ **Vẫn có** | ❌ | ⭐ **Vẫn biết** → 🔴 black hole |
</details>

---

**Câu 8.** Prefix-list này apply vào `area 1 filter-list prefix PL-X out`. Hậu quả?
```
ip prefix-list PL-X seq 5 deny 172.16.2.0/24
```

<details><summary>Xem đáp án</summary>

🔴 **Chặn HẾT mọi LSA type 3 đi ra khỏi area 1** — không chỉ `172.16.2.0/24`.

**Vì sao:** prefix-list có ⭐ **implicit deny** ở cuối. Prefix nào **không khớp dòng nào**
sẽ bị **deny mặc định**.

Ở đây chỉ có 1 dòng (`deny 172.16.2.0/24`) → mọi prefix khác **không khớp** → bị **implicit deny**
→ **không LSA 3 nào được sinh ra** → area 0 và area 2 **mất toàn bộ route** từ area 1.

**Sửa — thêm catch-all:**
```
ip prefix-list PL-X seq 5  deny   172.16.2.0/24
ip prefix-list PL-X seq 10 permit 0.0.0.0/0 le 32     ! catch-all
```

`permit 0.0.0.0/0 le 32` = "cho phép mọi prefix với độ dài mask từ 0 đến 32".

**Verify:**
```
show ip prefix-list detail PL-X
! ip prefix-list PL-X:
!    Description:
!    count: 2, range entries: 1, sequences: 5 - 10
!    seq 5 deny 172.16.2.0/24 (hit count: 1, refcount: 1)
!    seq 10 permit 0.0.0.0/0 le 32 (hit count: 8, refcount: 1)
```
⭐ **`hit count`** cho biết prefix-list có thật sự được dùng và mỗi dòng khớp bao nhiêu lần.

⚠️ **Đây là lỗi gây downtime thật ở production** — cùng loại với lỗi thiếu catch-all trong
route-map (Module-03 §2.7).
</details>

---

**Câu 9.** Bạn triển khai NSSA cho area 2. Neighbor lên đủ, LSA 7 có, nhưng router trong area 2
**không ra được Internet**. Nguyên nhân?

<details><summary>Xem đáp án</summary>

🔴 **NSSA KHÔNG tự động inject default route** (khác với stub area).

**Chẩn đoán:**
```
R-in-area2# show ip route 0.0.0.0
! % Network not in table

R-ABR# show ip ospf | include nssa|generates
!     Area 2
!         It is a NSSA area
!         (KHÔNG có dòng "generates stub default route")
```

Area 2 là NSSA → **LSA 4 và 5 bị chặn** → router trong area 2 **không có route external nào**,
và **cũng không có default route** → không biết gửi traffic Internet đi đâu.

**Sửa — trên ABR của NSSA:**
```
router ospf 1
 area 2 nssa default-information-originate
```

**Verify:**
```
R-ABR# show ip ospf | include generates
!         generates stub default route with cost 1

R-in-area2# show ip route 0.0.0.0
! O*IA  0.0.0.0/0 [110/1] via ...        ← đã có
```

⭐ **Vì sao Cisco thiết kế khác stub:** NSSA **có ASBR riêng** → rất có thể nó **tự có đường ra**
qua ASBR của mình. Tự động inject default route có thể **ghi đè đường đi tốt hơn**
→ Cisco để bạn **chủ động** quyết định.

**Các biến thể:**
```
area 2 nssa default-information-originate                    ! chỉ khi có default trong RIB
area 2 nssa default-information-originate metric 50          ! ép metric
area 2 nssa no-summary                                        ! Totally NSSA → tự inject
```
</details>

---

**Câu 10.** OSPFv3: nêu 5 điểm khác biệt quan trọng nhất so với OSPFv2 (dạng đề hỏi trực tiếp).

<details><summary>Xem đáp án</summary>

| # | Điểm | OSPFv2 | **OSPFv3** |
|:---:|---|---|---|
| **1** | 🔴 **Router ID** | 32-bit (thường lấy từ IP) | ⭐ **VẪN 32-bit dạng IPv4** → router **IPv6-only phải gõ tay `router-id`**, không thì OSPFv3 **không khởi động** |
| **2** | ⭐ **Cách bật vào OSPF** | `network <ip> <wildcard> area X` | ⭐ **`ipv6 ospf 1 area X`** trên **interface** |
| **3** | ⭐ **Địa chỉ nguồn Hello** | IP interface | ⭐ **Link-local (`FE80::/10`)** — next-hop trong bảng route cũng là link-local |
| **4** | ⭐ **Authentication** | Có sẵn (plain/MD5/SHA) | ⭐ Dùng **IPsec (AH/ESP)** — v3 không có field auth riêng |
| **5** | ⭐ **Multicast** | 224.0.0.5 / 224.0.0.6 | ⭐ **FF02::5 / FF02::6** |

**Bổ sung hay hỏi:**

| | OSPFv2 | OSPFv3 |
|---|---|---|
| LSA mới | — | ⭐ **Type 8 (Link LSA)** + **Type 9 (Intra-Area Prefix LSA)** |
| LSA 1/2 mang prefix? | ✅ Có | ⭐ **KHÔNG** — chỉ mô tả topology. Prefix ở LSA 9 |
| LSA 3 / LSA 4 gọi là gì | Summary / ASBR Summary | **Inter-Area Prefix** / **Inter-Area Router** |
| Nhiều instance/link | ❌ | ⭐ ✅ (**Instance ID**) |
| Ký hiệu route inter-area | `O IA` | ⭐ **`OI`** |
| RFC | 2328 | **5340** |

⭐ **GIỐNG NHAU hoàn toàn:** 8 neighbor state · DR/BDR election (non-preemptive) ·
5 network type · timer 10/40 và 30/120 · Dijkstra SPF · area & area 0 backbone ·
stub/NSSA · cost formula.

🧠 **Ý nghĩa của Type 9:** OSPFv3 **tách topology khỏi địa chỉ**. LSA 1/2 nói *"ai nối với ai"*,
LSA 9 nói *"trên đó có prefix gì"*. Nhờ vậy **đổi địa chỉ IPv6 không cần chạy lại SPF**.
</details>

---

**Câu 11.** Bạn muốn ẩn `172.16.2.0/24` của area 1 khỏi mọi area khác, và muốn **mọi router**
đều không biết mạng này. Dùng lệnh nào, trên router nào? Nêu 2 cách.

<details><summary>Xem đáp án</summary>

⭐ Cấu hình trên **ABR của area 1**. Hai cách:

**Cách 1 — `area range ... not-advertise`** (đơn giản nhất cho 1 dải):
```
router ospf 1
 area 1 range 172.16.2.0 255.255.255.0 not-advertise
```

**Cách 2 — `area filter-list`** (linh hoạt hơn, dùng prefix-list):
```
ip prefix-list PL-HIDE seq 5  deny   172.16.2.0/24
ip prefix-list PL-HIDE seq 10 permit 0.0.0.0/0 le 32     ! đừng quên catch-all
!
router ospf 1
 area 1 filter-list prefix PL-HIDE out
```
⭐ `out` = chặn LSA 3 **đi RA khỏi** area 1.

**Cả hai cách đều:** ABR **không sinh LSA type 3** cho `172.16.2.0/24` →
⭐ **mọi router ở area khác hoàn toàn không biết** mạng này tồn tại → **nhất quán**, không black hole.

**Verify:**
```
! Trên router ở area khác:
show ip ospf database summary | include 172.16.2      ← TRỐNG (LSA không tồn tại)
show ip route 172.16.2.0                               ← không có route
```

🔴 **KHÔNG dùng `distribute-list in`** cho mục đích này — nó chỉ chặn RIB của 1 router,
LSDB vẫn đủ, router khác vẫn tin "đi qua đây tới được" → **black hole**.

**Chọn cách nào:**
| Tình huống | Dùng |
|---|---|
| Ẩn 1–2 dải cố định | `area range ... not-advertise` |
| Ẩn nhiều dải, cần linh hoạt, cần cả chiều `in` | `area filter-list` |
</details>

---

**Câu 12.** Cấu hình `default-information originate always` trên router biên. Router này mất
kết nối tới ISP (mất route `0.0.0.0/0` trong RIB). Chuyện gì xảy ra? Cách làm đúng?

<details><summary>Xem đáp án</summary>

🔴 **Router VẪN tiếp tục quảng bá `0.0.0.0/0` vào OSPF** → mọi router trong AS vẫn gửi traffic
Internet về đây → router này **không có đường ra** → ⭐ **drop toàn bộ traffic → BLACK HOLE**.

Và nếu có router biên thứ 2 còn sống, traffic vẫn có thể bị **hút về router chết** này
(nếu cost tới nó nhỏ hơn).

**Vì sao:** `always` nghĩa là *"quảng bá default route **bất kể** tôi có `0.0.0.0/0` trong RIB
hay không"*.

**Cách làm đúng — 2 lớp:**

**Lớp 1 — bỏ `always`:**
```
router ospf 1
 default-information originate         ! chỉ quảng bá NẾU có 0.0.0.0/0 trong RIB
```
→ Mất default route trong RIB → OSPF **tự động ngừng quảng bá** → traffic chuyển sang router khác.

**Lớp 2 — ⭐ IP SLA + track cho default route** (Module-03 §2.4):
```
ip sla 1
 icmp-echo 8.8.8.8 source-interface GigabitEthernet0/0      ! source-interface bắt buộc
 frequency 5
ip sla schedule 1 life forever start-time now                ! đừng quên
!
track 1 ip sla 1 reachability
 delay down 3 up 5
!
ip route 0.0.0.0 0.0.0.0 203.0.113.2 track 1                 ! route bị xóa nếu SLA fail
!
router ospf 1
 default-information originate
```

**Chuỗi tác động khi ISP chết:**
```
IP SLA ping fail → track 1 Down → static default route bị XÓA khỏi RIB
                 → OSPF không còn 0.0.0.0/0 → NGỪNG quảng bá LSA 5 default
                 → mọi router chuyển sang router biên khác ✅
```

⭐ **Đây là lý do Module-03 (IP SLA) và Module-04B (default origination) phải học cùng nhau** —
một mình mỗi cái đều không đủ để làm dual-ISP đúng.

**Verify:**
```
show ip sla statistics 1        ! return code OK? time to live Forever?
show track 1                     ! Reachability Up? Tracked by STATIC-IP-ROUTING?
show ip route 0.0.0.0            ! có trong RIB?
show ip ospf database external 0.0.0.0     ! LSA 5 default có được sinh?
```
</details>

---

## 📚 9. THUẬT NGỮ ANH–VIỆT

| Tiếng Anh | Tiếng Việt | Ghi chú |
|---|---|---|
| **ASBR Summary LSA (Type 4)** | LSA tóm tắt ASBR | ⭐ **ABR** sinh · LS ID = **Router ID của ASBR** · "ASBR ở hướng này" |
| **AS External LSA (Type 5)** | LSA ngoại vi AS | ⭐ **ASBR** sinh · flood **toàn AS** · route redistribute |
| **NSSA External LSA (Type 7)** | LSA ngoại vi NSSA | ⭐ **ASBR trong NSSA** sinh · chỉ trong NSSA · ABR dịch → LSA 5 |
| **ASBR** (AS Boundary Router) | Router biên hệ tự trị | Router redistribute route ngoài vào OSPF |
| **Forward Address** | Địa chỉ chuyển tiếp | ⭐ Trong LSA 7 là **IP của ASBR** (LSA 5 thường là `0.0.0.0`) |
| **NSSA Translator** | Bộ dịch NSSA | ⭐ **ABR của NSSA** — dịch LSA 7 → LSA 5 |
| **Normal / Standard area** | Vùng bình thường | Nhận đủ LSA 3, 4, 5 |
| ⭐ **Stub area** | Vùng cụt | Chặn **LSA 4 + 5**. ABR tự inject default (`O*IA`) |
| ⭐ **Totally Stubby area** | Vùng cụt hoàn toàn | Chặn **LSA 3 + 4 + 5**. LSDB nhỏ nhất |
| ⭐ **NSSA** (Not-So-Stubby Area) | Vùng "không hẳn cụt" | Chặn 4+5, ⭐ **cho phép LSA 7** (có ASBR riêng) |
| **Totally NSSA** | NSSA hoàn toàn | Chặn 3+4+5, cho phép 7 |
| **`no-summary`** | Không tóm tắt | ⭐ Chặn thêm LSA 3. **CHỈ cấu hình trên ABR** |
| **E-bit** (External capability) | Bit ngoại vi | ⭐ Trong Hello. `0` = stub · `1` = normal. **Phải khớp** |
| **N-bit** (NSSA capability) | Bit NSSA | Trong Hello, cho NSSA. Phải khớp |
| **Route summarization** | Tóm tắt route | Gộp nhiều prefix thành 1 prefix ngắn hơn |
| ⭐ **`area <X> range`** | Dải của area | ⭐ Trên **ABR** — gộp **LSA 3** (inter-area) |
| ⭐ **`summary-address`** | Địa chỉ tóm tắt | ⭐ Trên **ASBR** — gộp **LSA 5/7** (external) |
| ⭐ **Discard route** | Route loại bỏ | ⭐ `<summary> → Null0`, IOS tự tạo, **chống loop** |
| **Contiguous addressing** | Địa chỉ liền mạch | ⭐ Điều kiện để summarize được — phải quy hoạch IP theo area từ đầu |
| **Black hole** | Hố đen | Traffic bị hút vào rồi drop, không có thông báo |
| **`not-advertise`** | Không quảng bá | ⭐ Ẩn hẳn 1 dải — LSA 3 không được sinh |
| ⭐ **`area filter-list`** | Danh sách lọc area | ⭐ Trên **ABR** — lọc **LSA 3** vào (`in`) / ra (`out`) area |
| ⭐ **`distribute-list ... in`** | Danh sách phân phối | ⭐ Lọc **route vào RIB**, ⭐ **KHÔNG** ảnh hưởng LSDB → 🔴 nguy cơ black hole |
| **Prefix-list** | Danh sách tiền tố | ⚠️ Có **implicit deny** — cần catch-all `permit 0.0.0.0/0 le 32` |
| **`le` / `ge`** | Nhỏ hơn/bằng · Lớn hơn/bằng | Giới hạn độ dài mask trong prefix-list |
| **Catch-all statement** | Câu bắt tất cả | ⭐ `permit 0.0.0.0/0 le 32` — chống implicit deny |
| **Hit count** | Số lần khớp | ⭐ `show ip prefix-list detail` — kiểm tra filter có hoạt động |
| **`default-information originate`** | Khởi tạo thông tin mặc định | Quảng bá `0.0.0.0/0` vào OSPF |
| ⚠️ **`always`** | Luôn luôn | ⚠️ Quảng bá default **dù không có** trong RIB → nguy cơ black hole |
| **Candidate default** | Ứng viên mặc định | Ký hiệu `*` trong `O*IA` / `O*E2` |
| **MD5 authentication** | Xác thực MD5 | `ip ospf authentication message-digest` + `message-digest-key` |
| **Key chain** | Chuỗi khóa | Dùng cho SHA auth, hỗ trợ rotate key |
| **`ip ospf authentication null`** | Tắt xác thực | ⭐ Interface-level **thắng** area-level |
| **Virtual link** | Liên kết ảo | ⚠️ Vá lỗi area không nối area 0. **Dấu hiệu thiết kế sai** |
| **Transit area** | Vùng trung chuyển | Area mà virtual link đi qua. 🔴 **Không được là stub/NSSA** |
| **OSPFv3** | OSPF phiên bản 3 | RFC **5340**, cho IPv6 |
| ⭐ **Link LSA (Type 8)** | LSA liên kết | ⭐ Mới trong v3 — quảng bá link-local + prefix trên link |
| ⭐ **Intra-Area Prefix LSA (Type 9)** | LSA tiền tố nội vùng | ⭐ Mới trong v3 — **mang prefix IPv6** (LSA 1/2 không mang) |
| **Inter-Area Prefix LSA** | LSA tiền tố liên vùng | ⭐ = LSA type 3 của v2, đổi tên |
| **Inter-Area Router LSA** | LSA router liên vùng | ⭐ = LSA type 4 của v2, đổi tên |
| **Instance ID** | ID thực thể | ⭐ v3 hỗ trợ nhiều instance OSPF trên 1 link |
| **Interface ID** | ID interface | Mới trong v3, xuất hiện trong `show ipv6 ospf neighbor` |
| **Link-local address** | Địa chỉ liên kết cục bộ | ⭐ `FE80::/10` — nguồn Hello và next-hop của OSPFv3 |
| **`ipv6 unicast-routing`** | Bật định tuyến IPv6 | 🔴 **BẮT BUỘC** — thiếu là OSPFv3 không chạy |
| **`OI`** | OSPF Inter-area (IPv6) | Ký hiệu trong `show ipv6 route` (v2 là `O IA`) |
| **Dual-stack** | Ngăn xếp kép | Chạy IPv4 + IPv6 song song. ⭐ v2 và v3 là **2 process độc lập** |

---

## 🎯 10. ĐÚC KẾT MODULE-04B

**3 điều rút ra:**

1. ⭐ **Mọi thứ trong module này là câu hỏi "LSA nào bị chặn ở đâu".**
   **Stub** chặn LSA 4+5 · **Totally** chặn thêm LSA 3 · **NSSA** như stub nhưng cho LSA 7.
   Và lệnh chứng minh duy nhất bạn cần: **`show ip ospf database database-summary`** —
   đếm LSA trước và sau khi cấu hình. Trong lab bạn đã tự đo được **18 → 3 LSA**.

2. ⭐ **Summarization không phải để bảng route gọn — mà để chặn LSA flooding.**
   Subnet nhấp nháy trong area không làm area khác chạy lại SPF. Đó là **bức tường chắn sự cố**
   hiệu quả nhất của OSPF. Nhưng nó **đòi hỏi quy hoạch IP theo area NGAY TỪ ĐẦU** —
   không có contiguous addressing thì không summarize được, và sửa sau = re-IP toàn mạng.

3. 🔴 **`distribute-list in` là cái bẫy nguy hiểm nhất của module này.**
   Vì OSPF là link-state, **LSA phải flood nguyên vẹn** → `distribute-list in` chỉ chặn
   **RIB của 1 router**, LSDB vẫn đủ, **router khác vẫn tin "đi qua đây tới được"** → **black hole**.
   Muốn lọc thật thì dùng **`area filter-list`** hoặc **`area range not-advertise`** trên **ABR**.

🧠 **Một câu để nhớ:** *Khi route bị mất, hỏi đúng một câu trước tiên:
**"LSA còn tồn tại không?"** — LSA không có = bị chặn ở nguồn (area type / filter trên ABR).
LSA có mà route không có = `distribute-list in`, và đó là dấu hiệu của một black hole đang chờ.*

---

### ✅ TỰ CHẤM

**Phần A — Trả lời được bằng lời của mình, không nhìn tài liệu:**

| # | Câu | ✅ |
|:---:|---|:---:|
| 1 | LSA type 4: ai sinh, LS ID là gì, ⭐ **vì sao cần tồn tại**? | ☐ |
| 2 | LSA type 5: ai sinh, flood tới đâu? | ☐ |
| 3 | LSA type 7: ai sinh, flood tới đâu, ai dịch thành LSA 5? | ☐ |
| 4 | `Forward Address` trong LSA 7 khác LSA 5 thế nào? | ☐ |
| 5 | ⭐ Điền bảng 5 area type: chặn LSA nào, default route tự động không? | ☐ |
| 6 | `no-summary` cấu hình ở đâu? Khai sai chỗ thì sao? | ☐ |
| 7 | Area type khai ở đâu? Thiếu 1 router thì sao? Bit nào gây lỗi? | ☐ |
| 8 | Area 0 / area có ASBR có thể là stub không? Vì sao? | ☐ |
| 9 | 🔴 NSSA có tự động default route không? Vì sao Cisco thiết kế vậy? | ☐ |
| 10 | Default route trong stub là loại LSA nào? Ký hiệu route là gì? | ☐ |
| 11 | ⭐ `area range` vs `summary-address`: ở đâu, gộp gì? | ☐ |
| 12 | ⭐ Lợi ích **lớn nhất** của summarization? Cơ chế? | ☐ |
| 13 | Metric của summary route (mặc định)? Cách ép? | ☐ |
| 14 | Discard route Null0 là gì, vì sao cần? | ☐ |
| 15 | ⭐ 3 cách filtering, mỗi cách ở đâu, ảnh hưởng LSDB không? | ☐ |
| 16 | 🔴 Vì sao `distribute-list in` nguy hiểm? | ☐ |
| 17 | `area filter-list in` vs `out` — chiều nào là gì? | ☐ |
| 18 | Prefix-list thiếu catch-all → hậu quả? Dòng catch-all viết thế nào? | ☐ |
| 19 | `default-information originate` vs `always` — rủi ro? Cách làm đúng? | ☐ |
| 20 | Auth: interface-level vs area-level, cái nào thắng? Cách tắt trên 1 interface? | ☐ |
| 21 | Virtual link: dùng gì chỉ đầu kia, transit area có điều kiện gì? | ☐ |
| 22 | ⭐ 5 điểm khác biệt OSPFv3 vs OSPFv2? | ☐ |
| 23 | 🔴 Vì sao router IPv6-only phải gõ tay `router-id` OSPFv3? | ☐ |
| 24 | ⭐ LSA type 8 và 9 của OSPFv3 làm gì? Ý nghĩa kiến trúc? | ☐ |
| 25 | Ký hiệu route OSPFv3 inter-area? Next-hop là loại địa chỉ gì? | ☐ |

**Phần B — Lab (tự làm không xem hướng dẫn):**

| # | Yêu cầu | ✅ |
|:---:|---|:---:|
| 1 | Biến R4 thành **ASBR** (redistribute static + connected có route-map lọc) | ☐ |
| 2 | ⭐ Đọc **LSA 5**: chỉ ra `Advertising Router` = ASBR, `Metric Type 2`, `Metric 20` | ☐ |
| 3 | ⭐⭐ Đọc **LSA 4**: chỉ ra `LS ID` = Router ID của ASBR, `ADV Router` = ABR | ☐ |
| 4 | Dùng `show ip ospf border-routers` chỉ ra ASBR + cost tới nó | ☐ |
| 5 | So sánh `O E1` vs `O E2` trong **cùng một** bảng route, giải thích metric | ☐ |
| 6 | ⭐⭐ Biến area 1 thành **Stub** → **chứng minh LSA 4 và 5 = 0** bằng `database-summary` | ☐ |
| 7 | Chỉ ra default route `O*IA` và giải thích vì sao là **LSA 3** chứ không phải LSA 5 | ☐ |
| 8 | ⭐ Tái hiện lỗi **quên khai stub trên 1 router** → mất neighbor → sửa | ☐ |
| 9 | ⭐⭐ Biến thành **Totally Stubby** → chứng minh chỉ còn **1 LSA 3** (default) và **1 route OSPF** | ☐ |
| 10 | ⭐ Điền đầy đủ bảng so sánh LSA count: **Normal 18 → Stub 12 → Totally Stub 3** | ☐ |
| 11 | Chứng minh khai `no-summary` trên router nội bộ **không có tác dụng** | ☐ |
| 12 | Tạo ASBR trong area 2, cấu hình **NSSA** | ☐ |
| 13 | ⭐ Đọc **LSA 7**: chỉ ra `Forward Address` ≠ `0.0.0.0` | ☐ |
| 14 | ⭐ Chứng minh **LSA 7 → LSA 5** ở ABR (so LSDB của R3 và R2) | ☐ |
| 15 | 🔴 Chứng minh **NSSA không có default route** → thêm `default-information-originate` → có | ☐ |
| 16 | ⭐⭐ Cấu hình `area range` gộp 4 subnet `/24` → **1 route `/22`**, xác nhận **4 LSA → 1 LSA** | ☐ |
| 17 | ⭐ Chỉ ra **discard route Null0** trên ABR và test nó drop gói tới subnet không tồn tại | ☐ |
| 18 | Ép metric summary bằng `... cost 500` và verify | ☐ |
| 19 | ⭐⭐ **ĐO lợi ích summarization**: đếm `SPF algorithm executed` trên R3, làm subnet area 1 nhấp nháy, so **có** vs **không** summarize | ☐ |
| 20 | Cấu hình `summary-address` trên **ASBR** gộp 4 external → 1 route | ☐ |
| 21 | Filtering cách 1: `area range ... not-advertise` → LSA không tồn tại | ☐ |
| 22 | Filtering cách 2: `area filter-list prefix ... out` và `... in`, hiểu đúng chiều | ☐ |
| 23 | 🔴 Tái hiện lỗi **prefix-list thiếu catch-all** → mất gần hết route → sửa | ☐ |
| 24 | ⭐⭐ Filtering cách 3: `distribute-list in` → **chứng minh LSA VẪN CÓ mà route KHÔNG CÓ** | ☐ |
| 25 | Điền bảng so sánh 3 cách filtering (LSDB / RIB / router khác có biết) | ☐ |
| 26 | Bật **MD5 auth** trên link, tái hiện lỗi key lệch → sửa | ☐ |
| 27 | Test **interface-level thắng area-level** bằng `ip ospf authentication null` | ☐ |
| 28 | ⭐ Cấu hình **OSPFv3** trên ít nhất 2 router, neighbor `FULL` | ☐ |
| 29 | ⭐ Đọc `show ipv6 ospf interface`: chỉ ra `Link Local Address`, `Interface ID`, `Instance ID` | ☐ |
| 30 | ⭐⭐ Đọc `show ipv6 ospf database`: chỉ ra **Link (Type-8)** và **Intra Area Prefix (Type-9)** | ☐ |
| 31 | Chỉ ra ký hiệu **`OI`** và **next-hop là link-local** trong `show ipv6 route ospf` | ☐ |
| 32 | Tái hiện lỗi thiếu **`ipv6 unicast-routing`** → OSPFv3 không chạy | ☐ |
| 33 | Cố ý phá 1 thứ bất kỳ, tự tìm ra bằng **4 câu hỏi §7.3** trong 10 phút | ☐ |

> ⚠️ **Đây là milestone tuần 8 — mốc quan trọng nhất nửa đầu khóa.**
> Nếu tick được hết Phần B thì bạn đã nắm **toàn bộ OSPF ở mức ENCOR** —
> phần lớn nhất của domain Infrastructure (30% đề).
>
> ⭐ **Nếu chỉ có thời gian làm một nửa:** ưu tiên **mục 6–10** (chứng minh LSA bị chặn),
> **mục 16–19** (summarization + đo SPF), và **mục 24** (`distribute-list in` không ảnh hưởng LSDB).
> Ba phần đó là ba câu hỏi mà đề ENCOR hỏi nhiều nhất, và cũng là ba thứ có giá trị nhất khi đi làm.

---

## 🔗 11. TÀI LIỆU CHO MODULE NÀY

| Nguồn | Cụ thể |
|---|---|
| **Sách OCG 350-401** | Chương **OSPF** thứ hai (thường *"Advanced OSPF"*) — area types, LSA 4/5/7, summarization, filtering + chương **OSPFv3** |
| **Cisco doc** ⭐⭐ | ***OSPF Design Guide*** — phần *Area Types*, *Stub Areas*, *NSSA*, *Route Summarization*. **Tài liệu tốt nhất về vì sao**, không chỉ cách làm |
| **Cisco doc** ⭐ | *IP Routing: OSPF Configuration Guide* → *Configuring OSPF NSSA*, *Configuring OSPF Stub Areas*, *Configuring Route Summarization* |
| **Cisco doc** ⭐ | *OSPF Not-So-Stubby Area (NSSA)* — giải thích chi tiết type 7 → 5 translation |
| **Cisco doc** ⭐ | *OSPF Database Explanation Guide* — từng field của LSA type 4, 5, 7 |
| **Cisco doc** | *How Does OSPF Generate Default Routes?* — giải thích `default-information originate` và `always` |
| **Cisco doc** | *Understanding OSPF Filtering* — phân biệt `area filter-list`, `distribute-list`, `area range not-advertise` |
| **Cisco doc** | *OSPF Virtual Link* · *Configuring OSPF Authentication* |
| **Cisco doc** ⭐ | *Implementing OSPFv3* / *IPv6 Routing: OSPFv3 Configuration Guide* |
| **RFC 3101** | The OSPF NSSA Option — nguồn gốc của NSSA |
| **RFC 5340** | OSPF for IPv6 — đọc **Section 2 (Differences from OSPF for IPv4)** nếu muốn nguồn gốc |
| **Cisco Live** ⭐ | Search `Cisco Live OSPF deployment best practices` · `Cisco Live IPv6 routing OSPFv3` |
| **NetworkLessons** ⭐ | Loạt bài *OSPF Stub Area*, *OSPF NSSA*, *OSPF Summarization*, *OSPF Filtering*, *OSPFv3* |
| **Video** | CBT Nuggets ENCOR — module Advanced OSPF · Keith Barker: search `Keith Barker OSPF stub NSSA`, `Keith Barker OSPFv3` |
| **Wireshark** | Filter `ospf` → xem **E-bit** trong Hello (Options field) để hiểu vì sao stub mismatch gây mất neighbor. Filter `ospf.v3` cho OSPFv3 |
| **Forum** | https://community.cisco.com — search `nssa default route not working`, `ospf distribute-list in lsdb`, `ospfv3 router-id ipv6 only` |

---

**➡️ Tiếp theo:** [Module-05 — BGP: eBGP và Path Selection](Module-05-BGP-eBGP-va-Path-Selection.md)
*(AS · eBGP peering · neighbor states · attribute · **13 bước path selection** · community · filtering — **Tuần 9–10**)*
