# Module-05A — BGP: Nền tảng & eBGP Peering

> 🧭 **Lộ trình:** [Module-04B](Module-04B-OSPF-Area-Summarization-OSPFv3.md) → `[Bạn đang ở đây] Module-05A` → [Module-05B](Module-05B-BGP-Path-Selection-va-Filtering.md) → Module-06
>
> 📊 **Blueprint:** Domain **3.0 Infrastructure (30%)**, mục **3.2.c — Configure and verify eBGP
> between directly connected neighbors (best path selection algorithm and neighbor relationships)**
>
> ⏱️ **Tuần 9** · 10 giờ

---

## ⭐ 0. ĐỌC TRƯỚC — phạm vi BGP trong ENCOR

Giống như EIGRP ở Module-03, BGP cũng có một giới hạn phạm vi quan trọng:

> **Blueprint chỉ yêu cầu: `eBGP` giữa **neighbor kề nhau trực tiếp** (directly connected).**
>
> Nguyên văn 3.2.c: *"Configure and verify **eBGP** between **directly connected** neighbors
> (best path selection algorithm and neighbor relationships)"*

| Chủ đề BGP | ENCOR yêu cầu | Thời gian nên dành |
|---|---|---|
| ⭐ **eBGP peering** giữa router kề nhau | ⭐ **Cấu hình + verify** | Tuần 9 (module này) |
| ⭐ **Best path selection algorithm** | ⭐ **Hiểu sâu + thao tác được** | Tuần 10 (Module-05B) |
| ⭐ **Neighbor relationships** (states, messages) | ⭐ **Hiểu + troubleshoot** | Tuần 9 |
| 🟡 **iBGP** | 🟡 **Chỉ khái niệm** (để hiểu vì sao AD 200, split-horizon rule) | ~1 giờ |
| 🟡 Route Reflector / Confederation | 🟡 Biết tên + mục đích | ~15 phút |
| ⛔ MPLS L3VPN / VPNv4 / BGP scaling lớn | ❌ **Không có trong ENCOR** | 0 |
| ⛔ eBGP multihop phức tạp, BGP over IPsec | ❌ Ngoài phạm vi (biết lệnh là đủ) | 0 |

> ✅ **Nghĩa là:** bạn **không cần** dựng lab iBGP full-mesh hay Route Reflector.
> Nhưng **phải cực vững** eBGP peering, 6 neighbor state, và **13 bước path selection**.
>
> ⚠️ Nếu sau này thi **ENARSI (300-410)** hoặc **CCIE** thì mới cần iBGP/RR sâu.

---

## ✅ 1. Chuẩn bị

| Cần có | Chi tiết |
|---|---|
| **Kiến thức trước** | Module-03 §2.1–2.2 (route selection, AD) · Module-03 §2.7 (route-map) · Module-04A (đọc bảng, 3 bảng của protocol) |
| **Lab** | 4× vIOS (mỗi router = 1 AS) |
| **RAM** | 4× 512 MB = **2 GB** ✅ |
| **Thời lượng** | 3h lý thuyết · 5h lab · 2h quiz |

### Module 05A vs 05B

| Chủ đề | 05A (Tuần 9) | 05B (Tuần 10) |
|---|:---:|:---:|
| AS · ASN · path-vector · AD | ⭐ | |
| eBGP vs iBGP · split-horizon rule · `next-hop-self` | ⭐ | |
| **6 neighbor state** · **5 message type** · timer | ⭐ | |
| 3 bảng của BGP · `network` statement | ⭐ | |
| Cấu hình eBGP peering · verify · troubleshoot | ⭐ | |
| Phân loại attribute (4 nhóm) | ⭐ | |
| ⭐ **13 bước path selection** | | ⭐ |
| **Weight · Local Pref · AS-path prepend · MED** | | ⭐ |
| **Community** (`no-export`, `no-advertise`, `local-AS`) | | ⭐ |
| **Filtering**: prefix-list · AS-path ACL · route-map | | ⭐ |
| Summarization (`aggregate-address`) | | ⭐ |

---

## 📘 2. LÝ THUYẾT

### 2.1 BGP trong 1 bảng

| Thuộc tính | Giá trị |
|---|---|
| Loại | ⭐ **Path Vector** (không phải distance vector, không phải link-state) |
| Chuẩn | **RFC 4271** (BGP-4) |
| Transport | ⭐ **TCP port 179** — khác hẳn OSPF (IP 89) và EIGRP (IP 88) |
| AD | ⭐ **eBGP = 20** · **iBGP = 200** · Local = 200 |
| Metric | Không có metric đơn giản — dùng ⭐ **13 bước path selection** trên các **attribute** |
| Đơn vị tổ chức | ⭐ **AS (Autonomous System)** |
| ASN 16-bit | **1 – 65535** (`64512–65534` = private) |
| ASN 32-bit | **1 – 4294967295** (RFC 6793) · `4200000000–4294967294` = private |
| Timer | ⭐ **Keepalive 60 s** · **Hold time 180 s** (= 3× keepalive) |
| Update | ⭐ **Incremental** — chỉ gửi thay đổi, không refresh định kỳ |
| Loop prevention | ⭐ **AS-path** (eBGP) · **split-horizon rule** (iBGP) |
| Dùng cho | Internet (định tuyến giữa các tổ chức), multi-homing, MPLS VPN |

#### ⭐ Vì sao BGP dùng TCP — điểm khác biệt cốt lõi

| | OSPF / EIGRP | ⭐ **BGP** |
|---|---|---|
| Transport | IP protocol riêng (89 / 88) | ⭐ **TCP 179** |
| Tự lo reliability | Có cơ chế riêng (LSAck, ACK) | ⭐ **Để TCP lo** (retransmit, ordering, windowing) |
| Neighbor phải kề nhau? | ⭐ **Có** (multicast trên link) | ⭐ **KHÔNG** — chỉ cần **IP reachable** |
| Cần IGP trước? | Không | ⭐ **Có** (với iBGP) — cần route để TCP tới được peer |
| Kích thước update | Giới hạn bởi MTU | Không giới hạn (TCP tự phân đoạn) |
| Có thể chở bao nhiêu route | Hàng chục nghìn | ⭐ **Hàng triệu** (Internet full table > 900k prefix) |

> ⭐ **Hệ quả quan trọng của "dùng TCP":** BGP neighbor **không tự tìm nhau** —
> bạn **phải khai báo tay** bằng `neighbor <ip> remote-as <asn>`.
> Không có multicast discovery như OSPF/EIGRP.

### 2.2 AS & ASN

| Khái niệm | Nội dung |
|---|---|
| **AS** (Autonomous System) | Một tập hợp router dưới **cùng một chính sách quản trị** — VD: 1 ISP, 1 doanh nghiệp lớn |
| **ASN** | Số định danh AS. Do **IANA/RIR** cấp (như APNIC ở châu Á) |
| **Private ASN** | ⭐ `64512–65534` (16-bit) · `4200000000–4294967294` (32-bit) — dùng nội bộ, không quảng bá ra Internet |
| **AS-path** | ⭐ Danh sách các AS mà route đã đi qua — dùng để **chống loop** và **chọn đường** |

**Cấu hình ASN 32-bit — 2 định dạng:**
```
router bgp 65000                  ! asplain (số thường)
router bgp 1.100                  ! asdot (1×65536 + 100 = 65636)
!
bgp asnotation dot                ! đổi cách hiển thị sang asdot
```

### 2.3 ⭐ eBGP vs iBGP — bảng phải thuộc

| | ⭐ **eBGP** (External BGP) | 🟡 **iBGP** (Internal BGP) |
|---|---|---|
| Giữa | ⭐ **AS khác nhau** | ⭐ **Cùng một AS** |
| Cấu hình | `neighbor 10.0.12.2 remote-as 65002` | `neighbor 10.0.13.2 remote-as 65001` *(cùng ASN với mình)* |
| **AD** | ⭐ **20** | ⭐ **200** |
| **TTL** của gói BGP | ⭐ **1** (phải kề nhau trực tiếp) | ⭐ **255** (đi qua nhiều hop được) |
| Neighbor cần kề nhau? | ⭐ **Có** (mặc định) — trừ khi dùng `ebgp-multihop` | Không cần — chỉ cần IP reachable qua IGP |
| ⭐ **AS-path** khi quảng bá | ⭐ **THÊM ASN của mình vào đầu** | ⭐ **KHÔNG thay đổi** |
| ⭐ **Next-hop** khi quảng bá | ⭐ **Đổi thành IP của mình** | ⭐ **KHÔNG đổi** → cần `next-hop-self` |
| **Local Preference** | ⭐ Không gửi qua eBGP | ⭐ **Gửi trong AS** |
| **MED** | ⭐ Gửi sang AS kề (không gửi tiếp) | Gửi trong AS |
| ⭐ **Split-horizon rule** | Không áp dụng | ⭐ **Route học từ iBGP KHÔNG quảng bá cho iBGP peer khác** |
| Yêu cầu topology | Không | ⭐ **Full mesh** (hoặc Route Reflector) |

#### ⭐ Split-horizon rule của iBGP — vì sao cần full mesh

> ⭐ **Quy tắc:** *route học được từ **một iBGP peer** thì **KHÔNG** được quảng bá cho
> **iBGP peer khác**.*

**Vì sao:** iBGP **không thêm ASN vào AS-path** (vì cùng AS) → **không có cơ chế chống loop**
→ nếu cho phép quảng bá lại, route sẽ chạy vòng vô tận trong AS.

**Hệ quả:** mọi router iBGP trong AS phải **peer trực tiếp với nhau** (full mesh):

```
   n router → n(n-1)/2 phiên iBGP

   3 router  →  3 phiên       ✅ OK
   10 router →  45 phiên      ⚠️ Bắt đầu khó
   50 router →  1225 phiên    🔴 Không khả thi
```

**Hai giải pháp** (🟡 chỉ cần biết tên cho ENCOR):

| Giải pháp | Ý tưởng |
|---|---|
| ⭐ **Route Reflector (RR)** | 1 router làm "trung tâm" — được **phá** split-horizon rule, phản chiếu route cho các client. Giống DR của OSPF |
| **Confederation** | Chia AS lớn thành nhiều **sub-AS**, giữa các sub-AS dùng eBGP-like |

#### ⭐ `next-hop-self` — vì sao route "học được mà không dùng được"

```
   AS 65002              AS 65001 (nội bộ)
  ┌──────┐             ┌──────┐  iBGP   ┌──────┐
  │  R2  │─────eBGP────│  R1  │─────────│  R3  │
  └──────┘  10.0.12.0  └──────┘         └──────┘
   quảng bá             next-hop         R3 nhận route với
   10.20.20.0/24        = 10.0.12.2      next-hop = 10.0.12.2
                                          ⚠️ nhưng R3 KHÔNG có route
                                             tới 10.0.12.0/30!
                                          → route INACCESSIBLE
```

⭐ **iBGP không đổi next-hop** → R3 nhận route với next-hop là IP **bên ngoài AS**
→ nếu IGP không quảng bá subnet đó, R3 **không tới được next-hop** → route bị **loại khỏi RIB**.

**Sửa — 2 cách:**
```
! ⭐ Cách 1 (khuyến nghị): next-hop-self trên router biên
router bgp 65001
 neighbor 10.0.13.2 next-hop-self          ! R1 đổi next-hop thành IP của mình

! Cách 2: quảng bá subnet eBGP vào IGP (không khuyến nghị — làm IGP phình)
router ospf 1
 network 10.0.12.0 0.0.0.3 area 0
```

**Dấu hiệu nhận biết:**
```
show ip bgp
!    Network          Next Hop     Metric LocPrf Weight Path
! *  10.20.20.0/24    10.0.12.2         0    100      0 65002 i
!  ↑ dấu * KHÔNG có ">" = route valid nhưng KHÔNG best (next-hop không tới được)
show ip bgp 10.20.20.0
! ... (inaccessible) ...
```

### 2.4 ⭐ Ba bảng của BGP

```
┌────────────────────────────────────────────────────────────────────┐
│ 1. NEIGHBOR TABLE       "Tôi peer với ai, phiên TCP thế nào?"      │
│    show ip bgp summary                                             │
│    → Neighbor IP · ASN · State/PfxRcd · Up/Down · MsgRcvd/Sent     │
├────────────────────────────────────────────────────────────────────┤
│ 2. BGP TABLE (BGP RIB)  "Mọi đường tôi biết tới mỗi đích"          │
│    show ip bgp                                                     │
│    → ⭐ Có thể có NHIỀU path cho 1 prefix. Chỉ 1 được chọn "best"  │
│       Adj-RIB-In  →  Local BGP RIB  →  Adj-RIB-Out                 │
├────────────────────────────────────────────────────────────────────┤
│              │ chạy 13 bước Best Path Selection                    │
│              ▼ (chỉ path "best" được đưa xuống)                    │
│ 3. ROUTING TABLE (RIB)  "Đường thật sự dùng để forward"            │
│    show ip route bgp                                               │
└────────────────────────────────────────────────────────────────────┘
```

| Bảng | Lệnh | Điểm đặc biệt |
|---|---|---|
| Neighbor | `show ip bgp summary` | ⭐ Cột `State/PfxRcd` — số = đã Established |
| **BGP table** | `show ip bgp` | ⭐ **Chứa NHIỀU path cho 1 prefix**. Đây là điểm khác OSPF |
| Routing table | `show ip route bgp` | ⭐ **Chỉ chứa best path** |

⭐ **Sự khác biệt cốt lõi so với OSPF:** OSPF chạy SPF ra **một** kết quả rồi vào RIB.
BGP **giữ lại mọi path** trong BGP table, và bạn **có thể xem hết** —
đó là lý do `show ip bgp` cực hữu ích cho troubleshoot.

#### Ba sub-table trong BGP table (⭐ đề hay hỏi tên)

| Tên | Nội dung |
|---|---|
| **Adj-RIB-In** | Route **nhận** từ mỗi neighbor, **trước** khi áp inbound policy |
| **Local BGP RIB** | Route sau khi áp inbound policy, đã chạy path selection |
| **Adj-RIB-Out** | Route sẽ **gửi** cho mỗi neighbor, sau khi áp outbound policy |

```
show ip bgp neighbors 10.0.12.2 received-routes     ! ⚠️ cần soft-reconfiguration inbound
show ip bgp neighbors 10.0.12.2 routes              ! route đã qua policy
show ip bgp neighbors 10.0.12.2 advertised-routes   ! ⭐ Adj-RIB-Out
```

### 2.5 ⭐ Sáu trạng thái neighbor

```
IDLE ──▶ CONNECT ──▶ OPENSENT ──▶ OPENCONFIRM ──▶ ESTABLISHED
  │         │
  │         └──▶ ACTIVE ──┐
  └◀─────────────────────┘
```

| State | Chuyện gì đang xảy ra | ⚠️ Kẹt ở đây = lỗi gì |
|---|---|---|
| **Idle** | Chưa làm gì. Đang chờ / đã bị reset | ⭐ **Không có route tới neighbor** · neighbor bị `shutdown` · ACL chặn |
| **Connect** | Đang **mở phiên TCP** (3-way handshake) | Đang trong quá trình — bình thường nếu chỉ vài giây |
| ⚠️ **Active** | ⭐ **TCP thất bại → đang CHỦ ĐỘNG thử lại** | 🔴 **"Active" KHÔNG phải trạng thái tốt!** TCP 179 bị chặn · sai IP neighbor · route bất đối xứng |
| **OpenSent** | Đã gửi **OPEN message**, chờ OPEN của peer | Sai ASN · sai Router ID |
| **OpenConfirm** | Đã nhận OPEN, chờ **KEEPALIVE** đầu tiên | Auth (MD5) lệch · timer lệch |
| ✅ **Established** | ⭐ Phiên hoạt động, đang trao đổi **UPDATE** | Đích cần đạt |

#### 🔴 "Active" là bẫy đề số 1 của BGP

> ⭐ Trong tiếng Anh thông thường "active" nghĩa là *đang hoạt động tốt*.
> Trong BGP, **`Active` nghĩa là "TCP đang THẤT BẠI và tôi đang chủ động thử kết nối lại"**.

**Chu kỳ Idle ↔ Active:**
```
Idle → thử mở TCP → thất bại → Active (thử lại) → thất bại → Idle → ...
```
Nếu bạn thấy neighbor **nhảy giữa Idle và Active**, đó là **TCP không lên được**.

**Ba nguyên nhân theo thứ tự kiểm tra:**

| # | Kiểm tra | Lệnh |
|:---:|---|---|
| 1 | ⭐ **Có route tới neighbor IP không?** | `show ip route <neighbor-ip>` · `ping <neighbor-ip>` |
| 2 | ⭐ **TCP 179 có bị chặn?** | `show access-lists` · `telnet <neighbor-ip> 179` |
| 3 | **Sai IP neighbor / sai `update-source`** | `show run \| sec router bgp` · `show ip bgp neighbors <ip> \| inc Local host` |

```
! Test TCP 179 — cách nhanh nhất
R1# telnet 10.0.12.2 179
Trying 10.0.12.2, 179 ... Open          ← ✅ TCP thông
! hoặc
Trying 10.0.12.2, 179 ...
% Connection refused by remote host      ← ⚠️ TCP bị chặn / BGP không listen
```

### 2.6 Năm loại BGP message

| # | Message | Nhiệm vụ | Khi nào gửi |
|:---:|---|---|---|
| **1** | **OPEN** | ⭐ Đàm phán: **ASN**, **BGP Router ID**, **Hold time**, capabilities | Sau khi TCP lên |
| **2** | **UPDATE** | ⭐ Quảng bá route mới (**NLRI** + attribute) hoặc rút route (**withdrawn**) | Khi có thay đổi |
| **3** | **KEEPALIVE** | Duy trì phiên | Mỗi **60 s** (mặc định) |
| **4** | **NOTIFICATION** | ⭐ **Báo lỗi rồi ĐÓNG phiên** | Khi có lỗi |
| **5** | **ROUTE-REFRESH** | ⭐ Xin gửi lại toàn bộ route (không cần reset phiên) | Khi đổi inbound policy |

**Trường trong OPEN message — phải khớp để lên Established:**

| Trường | Phải khớp? |
|---|---|
| **Version** (4) | ✅ |
| ⭐ **My Autonomous System** | ⭐ Phải **khớp với `remote-as`** mà peer khai cho mình |
| ⭐ **BGP Identifier** (Router ID) | ⭐ Phải **unique** (không trùng) |
| **Hold Time** | ⭐ **Không cần khớp** — 2 bên dùng **giá trị NHỎ HƠN** |
| Optional Capabilities | Đàm phán (route-refresh, 4-byte ASN, address family…) |

⭐ **Hold time:** không cần khớp! Nếu R1 khai 180 và R2 khai 60 → **cả hai dùng 60**.
Đây là điểm khác OSPF (timer phải khớp tuyệt đối).

**Đọc NOTIFICATION để tìm lỗi:**
```
show ip bgp neighbors 10.0.12.2 | include Last reset|notification
```
**Output mẫu:**
```
  Last reset 00:02:15, due to BGP Notification received, administrative shutdown
! hoặc
  Last reset 00:00:45, due to BGP Notification sent, bad AS number
```
⭐ ⭐ `bad AS number` → sai `remote-as`. Đây là cách nhanh nhất tìm nguyên nhân reset.

**Route-refresh — vì sao quan trọng:**
```
show ip bgp neighbors 10.0.12.2 | include refresh
!  Route refresh: advertised and received(new)     ← ✅ hỗ trợ
!
clear ip bgp 10.0.12.2 soft in         ! ⭐ dùng route-refresh, KHÔNG reset phiên
clear ip bgp 10.0.12.2                 ! 🔴 HARD RESET — đóng phiên TCP, gây downtime
```

### 2.7 Timer

| Timer | Mặc định | Ý nghĩa |
|---|:---:|---|
| **Keepalive** | **60 s** | Gửi KEEPALIVE mỗi 60 s |
| **Hold time** | **180 s** | Không nhận gì trong 180 s → đóng phiên |
| ConnectRetry | 60 s | Thử mở TCP lại sau 60 s (Active state) |
| **Advertisement interval** | eBGP **30 s** · iBGP **0 s** | ⭐ Gom nhiều thay đổi rồi gửi 1 lần |

```
! Đổi timer (global cho mọi neighbor)
router bgp 65001
 timers bgp 10 30                        ! keepalive 10, hold 30

! Đổi timer cho 1 neighbor
 neighbor 10.0.12.2 timers 10 30
```
⭐ **Hold time không cần khớp** — dùng giá trị nhỏ hơn. Nhưng **hold time = 0** nghĩa là **tắt keepalive**
(phiên không bao giờ timeout) — chỉ dùng khi có BFD.

> ⭐ **Thực tế:** thay vì tune timer BGP xuống thấp (tốn CPU), dùng **BFD**:
> ```
> interface Gi0/0
>  bfd interval 300 min_rx 300 multiplier 3
> router bgp 65001
>  neighbor 10.0.12.2 fall-over bfd
> ```
> → phát hiện lỗi trong **~900 ms** thay vì 180 s.

### 2.8 Cấu hình eBGP cơ bản

```
router bgp 65001                                  ! ⭐ ASN CỦA MÌNH
 bgp router-id 1.1.1.1                            ! ⭐ nên gõ tay
 bgp log-neighbor-changes                         ! ⭐ log khi neighbor up/down
 no bgp default ipv4-unicast                      ! (tùy chọn — xem §2.9)
 !
 neighbor 10.0.12.2 remote-as 65002               ! ⭐ ASN CỦA PEER
 neighbor 10.0.12.2 description ---> To AS65002 R2
 !
 network 10.1.1.0 mask 255.255.255.0              ! ⭐ quảng bá prefix
 network 1.1.1.1 mask 255.255.255.255
```

#### ⭐ `network` statement của BGP — KHÁC HẲN OSPF

| | OSPF `network` | ⭐ **BGP `network`** |
|---|---|---|
| Ý nghĩa | "Bật OSPF **trên interface** khớp wildcard" | ⭐ "**Quảng bá prefix này**, nếu nó **có trong RIB**" |
| Cú pháp | `network 10.1.1.0 0.0.0.255 area 0` (wildcard) | `network 10.1.1.0 mask 255.255.255.0` (**subnet mask**) |
| Yêu cầu | Interface tồn tại | ⭐ **Prefix phải KHỚP CHÍNH XÁC trong bảng route** |

🔴 **Bẫy đề & bẫy thực tế:** BGP `network` yêu cầu **khớp chính xác** cả **prefix VÀ mask**.

```
! RIB có: 10.1.1.0/24
network 10.1.1.0 mask 255.255.255.0        ! ✅ khớp → quảng bá được
network 10.1.0.0 mask 255.255.0.0          ! ❌ RIB không có /16 → KHÔNG quảng bá
network 10.1.1.0 mask 255.255.255.128      ! ❌ RIB không có /25 → KHÔNG quảng bá
```

**Cách kiểm tra:**
```
show ip route 10.1.1.0 255.255.255.0     ! prefix có trong RIB đúng mask này?
show ip bgp 10.1.1.0                      ! đã vào BGP table?
show ip bgp | include 10.1.1.0
```

> ⭐ **Cách vượt qua:** nếu muốn quảng bá prefix không có trong RIB, tạo **static route tới Null0**:
> ```
> ip route 10.1.0.0 255.255.0.0 Null0
> router bgp 65001
>  network 10.1.0.0 mask 255.255.0.0
> ```
> Đây là kỹ thuật chuẩn công nghiệp (và Module-05B sẽ dùng nó cho `aggregate-address`).

#### `no bgp default ipv4-unicast` — hiểu để không bị bối rối

| | Mặc định (không gõ) | ⭐ Có gõ `no bgp default ipv4-unicast` |
|---|---|---|
| `neighbor x remote-as y` | Tự động **activate** cho IPv4 unicast | ⭐ **KHÔNG** tự activate |
| Cần thêm gì | — | ⭐ Phải gõ `neighbor x activate` trong address-family |

```
! Kiểu address-family (hay dùng khi có nhiều AF: IPv4 + IPv6 + VPNv4)
router bgp 65001
 no bgp default ipv4-unicast
 neighbor 10.0.12.2 remote-as 65002
 neighbor 2001:DB8:0:12::2 remote-as 65002
 !
 address-family ipv4 unicast
  neighbor 10.0.12.2 activate                    ! ⭐ bắt buộc
  network 10.1.1.0 mask 255.255.255.0
 exit-address-family
 !
 address-family ipv6 unicast
  neighbor 2001:DB8:0:12::2 activate
  network 2001:DB8:1::/64
 exit-address-family
```

> ⭐ **Đề hay hỏi:** neighbor `Established` nhưng **không nhận route nào** (`PfxRcd = 0`)
> → kiểm tra đã `activate` chưa (nếu dùng `no bgp default ipv4-unicast`).

#### eBGP multihop & update-source

```
! eBGP giữa 2 loopback (không kề nhau trực tiếp)
router bgp 65001
 neighbor 2.2.2.2 remote-as 65002
 neighbor 2.2.2.2 ebgp-multihop 2                 ! ⭐ tăng TTL từ 1 lên 2
 neighbor 2.2.2.2 update-source Loopback0         ! ⭐ dùng loopback làm source
!
! Và phải có route tới loopback của peer:
ip route 2.2.2.2 255.255.255.255 10.0.12.2
```

| Lệnh | Vì sao cần |
|---|---|
| ⭐ `ebgp-multihop <ttl>` | eBGP mặc định **TTL = 1** → gói chết sau 1 hop. Peer qua loopback = **2 hop** |
| ⭐ `update-source <if>` | BGP dùng IP của **interface đi ra** làm source. Peer khai `neighbor 1.1.1.1` → source phải là `1.1.1.1` (loopback), nếu không → ⭐ **peer từ chối** |

> ⚠️ **Bẫy:** thiếu `update-source` → source IP là IP interface vật lý → peer nhận connection từ
> IP **không khớp** với `neighbor` đã khai → **từ chối** → kẹt **Active/Idle**.

#### Bảo mật phiên BGP

```
router bgp 65001
 neighbor 10.0.12.2 password MyBgpS3cret          ! ⭐ MD5 cho phiên TCP
 neighbor 10.0.12.2 ttl-security hops 1           ⭐ ! GTSM — chỉ nhận gói TTL ≥ 254
 neighbor 10.0.12.2 maximum-prefix 100000 90      ! ⭐ chống nhận quá nhiều prefix
```

| Lệnh | Chống gì |
|---|---|
| `password` | Ai đó giả mạo peer |
| ⭐ `ttl-security hops <n>` | **GTSM** — chống tấn công từ xa (spoofed packet có TTL thấp) |
| ⭐ `maximum-prefix <n> <%>` | ⭐ **Route leak** — peer vô tình gửi cả full Internet table → router hết RAM |

> ⭐ `maximum-prefix` là **bắt buộc** ở mọi phiên eBGP với ISP thật.
> Nhiều sự cố Internet toàn cầu bắt nguồn từ route leak — thiếu lệnh này thì router bạn chết theo.

### 2.9 ⭐ Phân loại BGP Attribute — 4 nhóm

Đây là nền để hiểu 13 bước path selection (Module-05B).

| Nhóm | Định nghĩa | Attribute |
|---|---|---|
| ⭐ **Well-known Mandatory** | **Mọi** BGP phải hiểu, **phải có** trong mọi UPDATE | **AS-path** · **Next-hop** · **Origin** |
| ⭐ **Well-known Discretionary** | Mọi BGP phải hiểu, **không bắt buộc có** | **Local Preference** · **Atomic Aggregate** |
| ⭐ **Optional Transitive** | Có thể không hiểu, nhưng ⭐ **vẫn chuyển tiếp** cho peer | **Community** · **Aggregator** |
| ⭐ **Optional Non-transitive** | Có thể không hiểu, ⭐ **KHÔNG chuyển tiếp** | **MED** (Multi-Exit Discriminator) · Originator-ID · Cluster-list |

**Bảng attribute chi tiết — phạm vi lan truyền:**

| Attribute | Nhóm | Lan tới đâu | Ý nghĩa |
|---|---|---|---|
| ⭐ **Weight** | ⚠️ **Cisco-only, KHÔNG phải attribute BGP** | ⭐ **CHỈ local router** — không gửi đi đâu | Ưu tiên outbound cao nhất, càng **CAO** càng tốt |
| ⭐ **Local Preference** | Well-known Discretionary | ⭐ **Trong AS** (qua iBGP), **không** qua eBGP | Chọn đường **ra** khỏi AS. Càng **CAO** càng tốt. Mặc định **100** |
| ⭐ **AS-path** | Well-known Mandatory | ⭐ **Qua eBGP** (thêm ASN mỗi hop) | Chống loop + chọn đường. Càng **NGẮN** càng tốt |
| ⭐ **Origin** | Well-known Mandatory | Qua eBGP | ⭐ `i` (IGP/network) < `e` (EGP) < `?` (incomplete/redistribute) |
| ⭐ **MED** | Optional Non-transitive | ⭐ **Sang AS kề, KHÔNG gửi tiếp** | Gợi ý cho AS kề chọn điểm **vào** AS mình. Càng **THẤP** càng tốt |
| **Next-hop** | Well-known Mandatory | eBGP: đổi · iBGP: không đổi | IP để tới đích |
| ⭐ **Community** | Optional Transitive | Qua eBGP (nếu bật `send-community`) | Nhãn để nhóm route → áp chính sách |
| Atomic Aggregate | Well-known Discretionary | Qua eBGP | Cảnh báo route đã bị gộp, mất chi tiết AS-path |
| Aggregator | Optional Transitive | Qua eBGP | ASN + Router ID của router đã gộp |

⭐ **Bảng nhớ nhanh "CAO tốt hay THẤP tốt":**

| Càng **CAO** càng tốt | Càng **THẤP** càng tốt |
|---|---|
| ⭐ **Weight** | ⭐ **AS-path length** |
| ⭐ **Local Preference** | ⭐ **MED** |
| | Origin (i < e < ?) |
| | Router ID (tie-break cuối) |
| | IGP metric tới next-hop |

> 🧠 **Mẹo nhớ:** *Hai cái đầu tiên trong path selection (**Weight, LocPref**) — **CAO thắng**.
> Còn lại hầu hết — **THẤP thắng**.*

#### ⭐ Origin code — đọc trong `show ip bgp`

| Ký hiệu | Tên | Nghĩa | Ưu tiên |
|:---:|---|---|:---:|
| **`i`** | IGP | Route được quảng bá bằng ⭐ **`network` statement** | ⭐ **1 (tốt nhất)** |
| **`e`** | EGP | Từ EGP (protocol cổ, không còn dùng) | 2 |
| ⭐ **`?`** | Incomplete | Route được ⭐ **`redistribute`** vào BGP | ⭐ **3 (kém nhất)** |

> ⭐ **Bài học thực chiến:** dùng **`network` statement** (origin `i`) thay vì `redistribute`
> (origin `?`) — vì origin `i` được **ưu tiên hơn** trong path selection.

---

## 📖 3. HIỂU RÕ HƠN

### 3.1 Path Vector — không phải distance, mà là "đã đi qua đâu"

| Loại | Câu nó trả lời |
|---|---|
| **Distance Vector** (RIP) | *"Đến X **xa 3 hop**"* — quan tâm **khoảng cách** |
| **Link-State** (OSPF) | *"Đây là **bản đồ** toàn area"* — quan tâm **topology** |
| ⭐ **Path Vector** (BGP) | *"Đến X thì **đi qua các AS: 65002, 65003, 65010**"* — quan tâm ⭐ **đã đi qua đâu** |

**Vì sao BGP không quan tâm "xa bao nhiêu":**
BGP là protocol **giữa các tổ chức**. Bạn **không biết** và **không cần biết** bên trong AS
của ISP có bao nhiêu hop. Bạn chỉ cần biết: *"đi qua AS nào"* — vì đó là thứ liên quan tới
**hợp đồng, chi phí, chính sách**.

🧠 **Một câu để nhớ:** *OSPF chọn đường **ngắn nhất về mặt kỹ thuật**.
BGP chọn đường **hợp chính sách nhất về mặt kinh doanh**.
Đó là lý do BGP có 13 bước attribute chứ không có một cái metric duy nhất.*

### 3.2 AS-path = chống loop bằng "danh sách nơi đã đến"

Route đi từ AS 65001 → 65002 → 65003, AS-path thành `65002 65001`
(⭐ mỗi eBGP hop **thêm ASN vào ĐẦU**).

Khi route quay lại AS 65001, router AS 65001 nhìn AS-path thấy **có ASN của chính mình**
→ ⭐ **từ chối ngay** → không loop.

🧠 **Một câu để nhớ:** *AS-path như **danh sách con dấu hộ chiếu** (giống route tag ở Module-03 §3.6,
nhưng tự động và bắt buộc). Thấy dấu của chính mình = đã từng đi qua = quay lại = từ chối.*

⭐ **Và đó là lý do iBGP cần split-horizon rule:** iBGP **không thêm dấu** (cùng AS)
→ không có cơ chế phát hiện → phải chặn bằng quy tắc "không quảng bá lại cho iBGP peer khác".

### 3.3 "Active" là trạng thái xấu — bẫy ngôn ngữ

| Từ | Nghĩa thông thường | ⭐ Nghĩa trong BGP |
|---|---|---|
| **Active** | Đang hoạt động tốt ✅ | 🔴 **TCP THẤT BẠI, đang chủ động thử lại** |
| **Established** | Đã thành lập | ✅ **Trạng thái TỐT** |
| **Idle** | Rảnh rỗi | ⚠️ Chưa/không kết nối được |

🧠 **Một câu để nhớ:** *Trong BGP, **`Established` là tốt, `Active` là xấu**.
"Active" = "tôi đang **tích cực gõ cửa** mà không ai mở" — nghĩa là TCP không lên được.*

⭐ **Ba thứ kiểm tra khi thấy Active:** (1) có route tới neighbor? (2) TCP 179 bị chặn?
(3) sai IP / thiếu `update-source`?

### 3.4 BGP table giữ nhiều path — như nhiều báo giá

**OSPF:** chạy Dijkstra → ra **một** kết quả → vào RIB. Bạn **không thấy** các phương án bị loại.

**BGP:** như bạn đi hỏi giá 3 nhà cung cấp. Bạn ⭐ **giữ cả 3 báo giá** trong file
(BGP table), rồi chọn 1 để ký hợp đồng (RIB).

⭐ **Lợi ích:** khi cần troubleshoot *"vì sao chọn đường này"*, bạn **mở lại cả 3 báo giá** và
so từng tiêu chí:
```
show ip bgp 10.20.20.0
! → hiện MỌI path, và ghi rõ path nào "best" cùng LÝ DO
```

🧠 **Một câu để nhớ:** *`show ip bgp` là **hồ sơ đầy đủ**, `show ip route bgp` là **quyết định cuối**.
Troubleshoot BGP luôn bắt đầu từ `show ip bgp`, không phải `show ip route`.*

### 3.5 `network` statement của BGP như "đăng ký hàng có sẵn"

BGP `network 10.1.1.0 mask 255.255.255.0` không phải *"bật BGP trên interface"* —
nó là ⭐ ***"tôi muốn bán mặt hàng `10.1.1.0/24`, nếu tôi CÓ nó trong kho (RIB)"***.

- Kho có đúng `10.1.1.0/24` → ✅ bán được
- Kho có `10.1.1.0/25` và `10.1.1.128/25` (2 nửa) → ❌ **không bán được `/24`** — không khớp chính xác
- Kho không có gì → ❌ không bán được

⭐ **Cách "tạo hàng giả để bán":** `ip route 10.1.0.0 255.255.0.0 Null0` →
kho có `/16` → bán được `/16`. Traffic tới subnet không tồn tại thì drop tại Null0
(giống discard route ở Module-04B §2.3).

🧠 **Một câu để nhớ:** *BGP không tạo route, nó chỉ **quảng bá route đã có**.
Không có trong RIB đúng mask = không quảng bá được, và **không có thông báo lỗi nào**.*

---

## 🧪 4. LAB 05A — eBGP 3 AS

### 4.1 Topology

```
        AS 65001                AS 65002                AS 65003
                                                                  
      ┌────────┐  10.0.12.0/30  ┌────────┐  10.0.23.0/30  ┌────────┐
      │   R1   │════════════════│   R2   │════════════════│   R3   │
      └────────┘  Gi0/0   Gi0/0 └────────┘  Gi0/1   Gi0/0 └────────┘
       Lo0 1.1.1.1                Lo0 2.2.2.2               Lo0 3.3.3.3
       Lo1 10.1.1.0/24            Lo1 10.2.2.0/24           Lo1 10.3.3.0/24
       Lo2 10.1.2.0/24                                      Lo2 10.3.4.0/24
           │
           │ 10.0.14.0/30 (Gi0/1)
           │
      ┌────────┐
      │   R4   │  AS 65004
      └────────┘
       Lo0 4.4.4.4
       Lo1 10.4.4.0/24
```

| Node | AS | Interface | IP |
|---|:---:|---|---|
| **R1** | **65001** | Lo0 | 1.1.1.1/32 |
| | | Lo1 | 10.1.1.1/24 |
| | | Lo2 | 10.1.2.1/24 |
| | | Gi0/0 | 10.0.12.1/30 → R2 |
| | | Gi0/1 | 10.0.14.1/30 → R4 |
| **R2** | **65002** | Lo0 | 2.2.2.2/32 |
| | | Lo1 | 10.2.2.1/24 |
| | | Gi0/0 | 10.0.12.2/30 → R1 |
| | | Gi0/1 | 10.0.23.1/30 → R3 |
| **R3** | **65003** | Lo0 | 3.3.3.3/32 |
| | | Lo1 | 10.3.3.1/24 |
| | | Lo2 | 10.3.4.1/24 |
| | | Gi0/0 | 10.0.23.2/30 → R2 |
| **R4** | **65004** | Lo0 | 4.4.4.4/32 |
| | | Lo1 | 10.4.4.1/24 |
| | | Gi0/1 | 10.0.14.2/30 → R1 |

**RAM: 4× 512 MB = 2 GB** ✅

> 💡 Topology này cho phép: eBGP peering 3 chiều · AS-path dài dần · và
> **Module-05B** sẽ dùng đường dự phòng R1→R4 để thao tác path selection.

### 4.2 Config đầy đủ

**R1 (AS 65001):**
```
enable
configure terminal
hostname R1
no ip domain lookup
!
interface Loopback0
 ip address 1.1.1.1 255.255.255.255
interface Loopback1
 ip address 10.1.1.1 255.255.255.0
interface Loopback2
 ip address 10.1.2.1 255.255.255.0
!
interface GigabitEthernet0/0
 description ---> eBGP to AS65002 (R2)
 ip address 10.0.12.1 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/1
 description ---> eBGP to AS65004 (R4)
 ip address 10.0.14.1 255.255.255.252
 no shutdown
!
router bgp 65001
 bgp router-id 1.1.1.1
 bgp log-neighbor-changes
 !
 neighbor 10.0.12.2 remote-as 65002
 neighbor 10.0.12.2 description ---> AS65002 R2
 neighbor 10.0.14.2 remote-as 65004
 neighbor 10.0.14.2 description ---> AS65004 R4
 !
 network 10.1.1.0 mask 255.255.255.0
 network 10.1.2.0 mask 255.255.255.0
 network 1.1.1.1 mask 255.255.255.255
!
line con 0
 exec-timeout 0 0
 logging synchronous
end
write memory
```

**R2 (AS 65002):**
```
enable
configure terminal
hostname R2
no ip domain lookup
!
interface Loopback0
 ip address 2.2.2.2 255.255.255.255
interface Loopback1
 ip address 10.2.2.1 255.255.255.0
!
interface GigabitEthernet0/0
 description ---> eBGP to AS65001 (R1)
 ip address 10.0.12.2 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/1
 description ---> eBGP to AS65003 (R3)
 ip address 10.0.23.1 255.255.255.252
 no shutdown
!
router bgp 65002
 bgp router-id 2.2.2.2
 bgp log-neighbor-changes
 !
 neighbor 10.0.12.1 remote-as 65001
 neighbor 10.0.12.1 description ---> AS65001 R1
 neighbor 10.0.23.2 remote-as 65003
 neighbor 10.0.23.2 description ---> AS65003 R3
 !
 network 10.2.2.0 mask 255.255.255.0
 network 2.2.2.2 mask 255.255.255.255
!
line con 0
 exec-timeout 0 0
 logging synchronous
end
write memory
```

**R3 (AS 65003):**
```
enable
configure terminal
hostname R3
no ip domain lookup
!
interface Loopback0
 ip address 3.3.3.3 255.255.255.255
interface Loopback1
 ip address 10.3.3.1 255.255.255.0
interface Loopback2
 ip address 10.3.4.1 255.255.255.0
!
interface GigabitEthernet0/0
 description ---> eBGP to AS65002 (R2)
 ip address 10.0.23.2 255.255.255.252
 no shutdown
!
router bgp 65003
 bgp router-id 3.3.3.3
 bgp log-neighbor-changes
 !
 neighbor 10.0.23.1 remote-as 65002
 neighbor 10.0.23.1 description ---> AS65002 R2
 !
 network 10.3.3.0 mask 255.255.255.0
 network 10.3.4.0 mask 255.255.255.0
 network 3.3.3.3 mask 255.255.255.255
!
line con 0
 exec-timeout 0 0
 logging synchronous
end
write memory
```

**R4 (AS 65004):**
```
enable
configure terminal
hostname R4
no ip domain lookup
!
interface Loopback0
 ip address 4.4.4.4 255.255.255.255
interface Loopback1
 ip address 10.4.4.1 255.255.255.0
!
interface GigabitEthernet0/1
 description ---> eBGP to AS65001 (R1)
 ip address 10.0.14.2 255.255.255.252
 no shutdown
!
router bgp 65004
 bgp router-id 4.4.4.4
 bgp log-neighbor-changes
 !
 neighbor 10.0.14.1 remote-as 65001
 neighbor 10.0.14.1 description ---> AS65001 R1
 !
 network 10.4.4.0 mask 255.255.255.0
 network 4.4.4.4 mask 255.255.255.255
!
line con 0
 exec-timeout 0 0
 logging synchronous
end
write memory
```

---

### Bước 1 — ⭐ Verify neighbor (Bảng 1)

```
R1# show ip bgp summary
```
**Output mẫu:**
```
BGP router identifier 1.1.1.1, local AS number 65001
BGP table version is 9, main routing table version 9
8 network entries using 1152 bytes of memory
9 path entries using 720 bytes of memory
5/4 BGP path/bestpath attribute entries using 800 bytes of memory
3 BGP AS-PATH entries using 72 bytes of memory
0 BGP route-map cache entries using 0 bytes of memory
0 BGP filter-list cache entries using 0 bytes of memory
BGP using 2744 total bytes of memory
BGP activity 8/0 prefixes, 9/0 paths, scan interval 60 secs

Neighbor        V           AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
10.0.12.2       4        65002      12      13        9    0    0 00:07:12        5
10.0.14.2       4        65004      10      11        9    0    0 00:06:45        2
```

⭐ **Bảng đọc output — lệnh quan trọng nhất của BGP:**

| Cột | Nghĩa | Cần chú ý gì |
|---|---|---|
| `Neighbor` | IP của peer | |
| `V` | BGP version | Luôn là **4** |
| `AS` | ⭐ ASN của peer | Đúng chưa? |
| `MsgRcvd` / `MsgSent` | Số message nhận/gửi | ⭐ **Cả hai đều tăng** = phiên khỏe |
| `TblVer` | Version bảng BGP đã gửi cho peer | |
| `InQ` / `OutQ` | Queue chờ xử lý | ⭐ **Nên là 0**. Khác 0 lâu = CPU cao / phiên nghẽn |
| `Up/Down` | ⭐ Phiên đã lên bao lâu | ⭐ **Reset liên tục** = có vấn đề |
| ⭐ `State/PfxRcd` | ⭐ **CỘT QUAN TRỌNG NHẤT** | Xem bảng dưới |

⭐ **Đọc cột `State/PfxRcd`:**

| Giá trị | Nghĩa |
|---|---|
| **Số** (VD `5`) | ⭐ ✅ **Established**, và đã nhận **5 prefix** |
| **`0`** | ⚠️ Established nhưng **nhận 0 prefix** → peer chưa quảng bá gì, hoặc thiếu `activate`, hoặc filter chặn hết |
| **`Idle`** | ⚠️ Chưa kết nối · không có route tới neighbor |
| ⚠️ **`Active`** | 🔴 **TCP thất bại**, đang thử lại |
| `OpenSent` / `OpenConfirm` | Đang đàm phán |
| **`Idle (Admin)`** | Neighbor bị `neighbor x shutdown` |

✅ **Checkpoint bước 1 — điền bảng (chạy trên cả 4 router):**

| Router | Neighbor | Peer AS | State/PfxRcd | Up/Down |
|---|---|:---:|:---:|---|
| R1 | 10.0.12.2 | | | |
| R1 | 10.0.14.2 | | | |
| R2 | 10.0.12.1 | | | |
| R2 | 10.0.23.2 | | | |
| R3 | 10.0.23.1 | | | |
| R4 | 10.0.14.1 | | | |

**Xem chi tiết 1 neighbor:**
```
R1# show ip bgp neighbors 10.0.12.2
```
**Output mẫu (các dòng quan trọng):**
```
BGP neighbor is 10.0.12.2,  remote AS 65002, external link
  Description: ---> AS65002 R2
  BGP version 4, remote router ID 2.2.2.2
  BGP state = Established, up for 00:08:33
  Last read 00:00:22, last write 00:00:19, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable (disabled)
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Four-octets ASN Capability: advertised and received
    Address family IPv4 Unicast: advertised and received
  ...
  For address family: IPv4 Unicast
  Session: 10.0.12.2
  BGP table version 9, neighbor version 9/0
  Output queue size : 0
  Index 1, Advertise bit 0
   Prefix activity:               ----               ----
    Prefixes Current:                3                  5 (Consumes 400 bytes)
    Prefixes Total:                  3                  5
  ...
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  ...
  Local host: 10.0.12.1, Local port: 179
  Foreign host: 10.0.12.2, Foreign port: 51234
```

⭐ **Bảng đọc — các dòng dùng để troubleshoot:**

| Dòng | Dùng để kiểm tra |
|---|---|
| `remote AS 65002, external link` | ⭐ **`external link` = eBGP** · `internal link` = iBGP |
| `remote router ID 2.2.2.2` | Router ID của peer — kiểm tra trùng |
| ⭐ `BGP state = Established, up for ...` | ⭐ Trạng thái + thời gian |
| `hold time is 180, keepalive interval is 60` | ⭐ Timer **đã đàm phán** (giá trị nhỏ hơn của 2 bên) |
| ⭐ `Route refresh: advertised and received` | ⭐ Có dùng được `soft in` không |
| `Four-octets ASN Capability` | Hỗ trợ ASN 32-bit |
| `Address family IPv4 Unicast: advertised and received` | ⭐ Đã **activate** cho IPv4 |
| `Prefixes Current: 3 / 5` | ⭐ **Gửi 3 / Nhận 5** prefix |
| ⭐ `Connections established 1; dropped 0` | ⭐ **`dropped` cao = phiên bất ổn** |
| ⭐ `Last reset never` | ⭐ Nếu có reset → **nói rõ nguyên nhân** |
| ⭐ `Local host: 10.0.12.1, Local port: 179` | ⭐ **Source IP thật** — kiểm tra `update-source` |

---

### Bước 2 — ⭐⭐ Đọc BGP table (Bảng 2) — phần quan trọng nhất

```
R1# show ip bgp
```
**Output mẫu:**
```
BGP table version is 9, local router ID is 1.1.1.1
Status codes: s suppressed, d damped, h history, * valid, > best, i - internal,
              r RIB-failure, S Stale, m multipath, b backup-path, f RT-Filter,
              x best-external, a additional-path, c RIB-compressed,
              t secondary path, L long-lived-stale,
Origin codes: i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

     Network          Next Hop            Metric LocPrf Weight Path
 *>  1.1.1.1/32       0.0.0.0                  0         32768 i
 *>  2.2.2.2/32       10.0.12.2                0             0 65002 i
 *>  3.3.3.3/32       10.0.12.2                              0 65002 65003 i
 *>  4.4.4.4/32       10.0.14.2                0             0 65004 i
 *>  10.1.1.0/24      0.0.0.0                  0         32768 i
 *>  10.1.2.0/24      0.0.0.0                  0         32768 i
 *>  10.2.2.0/24      10.0.12.2                0             0 65002 i
 *>  10.3.3.0/24      10.0.12.2                              0 65002 65003 i
 *>  10.3.4.0/24      10.0.12.2                              0 65002 65003 i
 *>  10.4.4.0/24      10.0.14.2                0             0 65004 i
```

⭐ **BẢNG GIẢI MÃ — học bảng này là đọc được BGP:**

| Thành phần | Nghĩa |
|---|---|
| ⭐ **`*`** | ⭐ **valid** — path hợp lệ (next-hop **reachable**) |
| ⭐ **`>`** | ⭐ **best** — path được chọn, ⭐ **đưa xuống RIB** |
| ⭐ **`*>`** | ⭐ **valid + best** — trạng thái mong muốn |
| **`*`** (không có `>`) | ⚠️ Valid nhưng **KHÔNG best** — có path khác tốt hơn |
| ⚠️ Không có `*` | 🔴 **Không valid** — thường là **next-hop unreachable** |
| **`i`** (đầu dòng) | Path học từ **iBGP** |
| **`r`** | ⚠️ **RIB-failure** — BGP chọn best nhưng RIB từ chối (có route AD tốt hơn) |
| **`s`** | Suppressed (bị `aggregate-address` gộp — Module-05B) |
| **`m`** | Multipath |
| `Network` | Prefix |
| ⭐ `Next Hop` | ⭐ **`0.0.0.0` = route do CHÍNH router này sinh** (từ `network` statement) |
| `Metric` | ⭐ = **MED** |
| `LocPrf` | ⭐ **Local Preference** (trống = 100 mặc định cho route local) |
| ⭐ `Weight` | ⭐ **`32768`** = route do chính mình sinh · **`0`** = học từ peer |
| ⭐ `Path` | ⭐ **AS-path** — danh sách AS đã đi qua, **đọc từ PHẢI sang TRÁI** |
| ⭐ Ký tự cuối `Path` | ⭐ **Origin code**: `i` = IGP (`network`) · `e` = EGP · `?` = incomplete (`redistribute`) |

⭐ **Đọc AS-path `65002 65003 i`:**
- Đọc **từ phải sang trái**: route xuất phát từ **AS 65003** (origin `i` = dùng `network`),
  rồi đi qua **AS 65002**, rồi tới tôi (AS 65001)
- **Độ dài AS-path = 2** → dùng cho bước 4 của path selection (Module-05B)

⭐ **Ba con số Weight phải nhớ:**

| Weight | Nghĩa |
|:---:|---|
| **32768** | ⭐ Route do **chính router này** sinh ra (`network` / `redistribute`) |
| **0** | ⭐ Route **học từ peer** |
| Khác | Đã được đặt tay bằng `neighbor x weight` hoặc route-map |

#### Xem chi tiết 1 prefix — lệnh quan trọng nhất khi troubleshoot

```
R1# show ip bgp 10.3.3.0
```
**Output mẫu:**
```
BGP routing table entry for 10.3.3.0/24, version 6
Paths: (1 available, best #1, table default)
  Advertised to update-groups:
     1          2
  Refresh Epoch 1
  65002 65003
    10.0.12.2 from 10.0.12.2 (2.2.2.2)
      Origin IGP, localpref 100, valid, external, best
      rx pathid: 0, tx pathid: 0x0
```

⭐ **Đọc — đây là output bạn sẽ dùng ở Module-05B để giải thích "vì sao chọn path này":**

| Dòng | Nghĩa |
|---|---|
| `Paths: (1 available, best #1, ...)` | ⭐ Có **1 path**, path số **1** là best |
| `Advertised to update-groups: 1 2` | Đã quảng bá cho 2 nhóm peer |
| `65002 65003` | ⭐ **AS-path** |
| `10.0.12.2 from 10.0.12.2 (2.2.2.2)` | Next-hop / học từ peer nào / (Router ID của peer) |
| ⭐ `Origin IGP, localpref 100, valid, external, best` | ⭐ **Origin · LocPref · valid · eBGP · BEST** |

**Xem trên R3 — nơi có nhiều path hơn:**
```
R3# show ip bgp
```
**Output mẫu:**
```
     Network          Next Hop            Metric LocPrf Weight Path
 *>  1.1.1.1/32       10.0.23.1                              0 65002 65001 i
 *>  2.2.2.2/32       10.0.23.1                0             0 65002 i
 *>  3.3.3.3/32       0.0.0.0                  0         32768 i
 *>  4.4.4.4/32       10.0.23.1                              0 65002 65001 65004 i
 *>  10.1.1.0/24      10.0.23.1                              0 65002 65001 i
 *>  10.1.2.0/24      10.0.23.1                              0 65002 65001 i
 *>  10.2.2.0/24      10.0.23.1                0             0 65002 i
 *>  10.3.3.0/24      0.0.0.0                  0         32768 i
 *>  10.3.4.0/24      0.0.0.0                  0         32768 i
 *>  10.4.4.0/24      10.0.23.1                              0 65002 65001 65004 i
```
⭐ **AS-path dài dần:** `65002 65001 65004` = 3 AS → route của R4 phải đi qua 3 AS mới tới R3.

**Lệnh xem có lọc:**
```
show ip bgp                                      ! toàn bộ BGP table
show ip bgp <prefix>                             ! ⭐ chi tiết 1 prefix + lý do best
show ip bgp summary                              ! ⭐ neighbor
show ip bgp neighbors <ip> routes                ! route nhận từ peer đó (sau policy)
show ip bgp neighbors <ip> advertised-routes     ! ⭐ route gửi cho peer đó
show ip bgp regexp _65003_                       ! ⭐ route đi qua AS 65003
show ip bgp regexp ^65002_                       ! route từ AS kề 65002
show ip bgp regexp ^$                            ! ⭐ route sinh trong AS của mình
show ip bgp | include 10.3                       ! grep
show ip bgp paths                                ! danh sách AS-path
show ip bgp all summary                          ! mọi address family
```

✅ **Checkpoint bước 2:**

| Kiểm tra | Mong đợi |
|---|---|
| Mọi prefix đều có ⭐ **`*>`** | ✅ |
| Route local (`10.1.1.0/24` trên R1) có `Next Hop = 0.0.0.0` và `Weight = 32768` | ⭐ ✅ |
| Route học từ peer có `Weight = 0` | ✅ |
| Mọi `Path` kết thúc bằng ⭐ **`i`** (dùng `network` statement) | ✅ |
| R3 thấy AS-path `65002 65001 65004` (3 AS) tới `10.4.4.0/24` | ⭐ ✅ |
| `show ip bgp 10.3.3.0` trên R1 hiện `valid, external, best` | ✅ |

---

### Bước 3 — Verify routing table (Bảng 3) & kết nối

```
R1# show ip route bgp
```
**Output mẫu:**
```
      2.0.0.0/32 is subnetted, 1 subnets
B        2.2.2.2 [20/0] via 10.0.12.2, 00:10:22
      3.0.0.0/32 is subnetted, 1 subnets
B        3.3.3.3 [20/0] via 10.0.12.2, 00:09:15
      4.0.0.0/32 is subnetted, 1 subnets
B        4.4.4.4 [20/0] via 10.0.14.2, 00:09:44
      10.0.0.0/8 is variably subnetted, 10 subnets, 3 masks
B        10.2.2.0/24 [20/0] via 10.0.12.2, 00:10:22
B        10.3.3.0/24 [20/0] via 10.0.12.2, 00:09:15
B        10.3.4.0/24 [20/0] via 10.0.12.2, 00:09:15
B        10.4.4.0/24 [20/0] via 10.0.14.2, 00:09:44
```
⭐ **`[20/0]`** = **AD 20 (eBGP) / metric 0**. Ký hiệu **`B`**.

**Test kết nối:**
```
R1# ping 10.3.3.1 source 10.1.1.1
R1# ping 10.4.4.1 source 10.1.1.1
R3# ping 10.4.4.1 source 10.3.3.1
R3# traceroute 10.4.4.1 source 10.3.3.1
```
**Output mẫu traceroute:**
```
  1 10.0.23.1 2 msec 1 msec 1 msec        ← R2 (AS 65002)
  2 10.0.12.1 3 msec 2 msec 2 msec        ← R1 (AS 65001)
  3 10.0.14.2 4 msec 3 msec 3 msec        ← R4 (AS 65004)
```
⭐ Traceroute đi qua **3 AS** — khớp với AS-path `65002 65001 65004`.

✅ **Checkpoint bước 3:**

| Kiểm tra | Mong đợi |
|---|---|
| `show ip route bgp` có ký hiệu **`B`** và **`[20/0]`** | ✅ |
| Ping full-mesh giữa các loopback `10.x.x.1` | ✅ |
| Traceroute đi qua đúng số AS như AS-path | ⭐ ✅ |

---

### Bước 4 — ⭐ Chứng minh AS-path chống loop

**a) Xem R3 có nhận được prefix của chính AS 65003 quay lại không:**
```
R3# show ip bgp 10.3.3.0
```
**Output mẫu:**
```
BGP routing table entry for 10.3.3.0/24, version 8
Paths: (1 available, best #1, table default)
  ...
  Local
    0.0.0.0 from 0.0.0.0 (3.3.3.3)
      Origin IGP, metric 0, localpref 100, weight 32768, valid, sourced, local, best
```
⭐ **Chỉ có 1 path — path local.** Không có path nào "quay lại" từ R2.

**b) Chứng minh R2 KHÔNG quảng bá route của AS 65003 trở lại cho AS 65003:**
```
R2# show ip bgp neighbors 10.0.23.2 advertised-routes
```
**Output mẫu:**
```
     Network          Next Hop            Metric LocPrf Weight Path
 *>  1.1.1.1/32       10.0.12.2                              0 65001 i
 *>  2.2.2.2/32       0.0.0.0                  0         32768 i
 *>  4.4.4.4/32       10.0.12.2                              0 65001 65004 i
 *>  10.1.1.0/24      10.0.12.2                              0 65001 i
 *>  10.1.2.0/24      10.0.12.2                              0 65001 i
 *>  10.2.2.0/24      0.0.0.0                  0         32768 i
 *>  10.4.4.0/24      10.0.12.2                              0 65001 65004 i
```
⭐ **KHÔNG có `10.3.3.0/24` và `10.3.4.0/24`** — R2 **không quảng bá lại** route của AS 65003
cho chính AS 65003.

> ⭐ **Cơ chế:** khi R2 chuẩn bị quảng bá cho neighbor AS 65003, nó kiểm tra AS-path.
> Route `10.3.3.0/24` có AS-path chứa `65003` → ⭐ **loại bỏ ngay** (AS-path loop prevention).

**c) ⭐ Chứng minh bằng cách "cố tình tạo loop":**

Cấu hình R3 có 1 prefix và cho phép nhận lại AS của mình:
```
R3(config)# router bgp 65003
R3(config-router)# neighbor 10.0.23.1 allowas-in 3          ! ⚠️ cho phép nhận AS mình 3 lần
```
```
R3# clear ip bgp 10.0.23.1 soft in
R3# show ip bgp 10.3.3.0
```
→ Vẫn chỉ có path local, vì **R2 không gửi**. `allowas-in` chỉ ảnh hưởng bên **nhận**.

**Dọn dẹp:**
```
R3(config-router)# no neighbor 10.0.23.1 allowas-in
```

> ⭐ **`allowas-in` dùng khi nào (thực tế):** MPLS VPN hub-and-spoke, hoặc khi 2 site cùng ASN
> nối qua ISP. **Rất ít khi cần** ở mạng thường — và dùng sai là mở đường cho loop.

✅ **Checkpoint bước 4:**

| Kiểm tra | Mong đợi |
|---|---|
| `show ip bgp neighbors <peer> advertised-routes` trên R2 **KHÔNG** có prefix của AS 65003 | ⭐ ✅ |
| R3 chỉ thấy 1 path (local) cho prefix của chính nó | ✅ |
| Giải thích được cơ chế AS-path loop prevention | ⭐ ✅ |

---

### Bước 5 — ⭐⭐ Tái hiện & sửa 8 lỗi BGP kinh điển

Làm từng lỗi, **tự chẩn đoán trước khi xem cách sửa**.

#### Lỗi 1 — 🔴 Sai `remote-as`

```
R1(config)# router bgp 65001
R1(config-router)# no neighbor 10.0.12.2 remote-as 65002
R1(config-router)# neighbor 10.0.12.2 remote-as 65099        ! cố ý sai
```
```
R1# show ip bgp summary | begin Neighbor
Neighbor        V           AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
10.0.12.2       4        65099       0       0        1    0    0 00:00:15 Idle
```
⭐ Kẹt **`Idle`** hoặc nhảy Idle/Active.

**Chẩn đoán — lệnh vàng:**
```
R1# show ip bgp neighbors 10.0.12.2 | include Last reset|notification
  Last reset 00:00:22, due to BGP Notification received, bad AS number
```
⭐⭐ **`bad AS number`** — nói thẳng nguyên nhân!

Hoặc:
```
R2# show logging | include BGP
%BGP-3-NOTIFICATION: sent to neighbor 10.0.12.1 2/2 (peer in wrong AS) 2 bytes FE43
```
⭐ **`peer in wrong AS`**.

**Sửa:**
```
R1(config-router)# no neighbor 10.0.12.2 remote-as 65099
R1(config-router)# neighbor 10.0.12.2 remote-as 65002
```

---

#### Lỗi 2 — 🔴 Không có route tới neighbor → `Idle`

```
R1(config)# interface Gi0/0
R1(config-if)# shutdown
```
```
R1# show ip bgp summary | begin Neighbor
10.0.12.2       4        65002       0       0        1    0    0 00:00:05 Idle
```
```
R1# show ip route 10.0.12.2
% Subnet not in table
R1# ping 10.0.12.2
! fail
```
⭐ **Không có route tới neighbor = BGP không thể mở TCP = `Idle`.**

**Sửa:** `no shutdown`

---

#### Lỗi 3 — 🔴🔴 TCP 179 bị chặn → `Active` (bẫy đề số 1)

```
R2(config)# access-list 100 deny tcp any any eq 179
R2(config)# access-list 100 permit ip any any
R2(config)# interface Gi0/0
R2(config-if)# ip access-group 100 in
```
```
R1# clear ip bgp 10.0.12.2
R1# show ip bgp summary | begin Neighbor
10.0.12.2       4        65002       0       0        1    0    0 00:00:20 Active
```
⭐⭐ **`Active`** — và ping vẫn **thành công** (ACL chỉ chặn TCP 179):
```
R1# ping 10.0.12.2
Success rate is 100 percent (5/5)          ← ⚠️ ping OK mà BGP không lên!
```

**Chẩn đoán:**
```
R1# telnet 10.0.12.2 179
Trying 10.0.12.2, 179 ...
% Connection timed out; remote host not responding
```
⭐⭐ **Đây là cách nhanh nhất phân biệt "không có route" (Idle) với "TCP bị chặn" (Active).**

```
R2# show access-lists 100
Extended IP access list 100
    10 deny tcp any any eq bgp (12 matches)         ← ⭐ counter tăng!
    20 permit ip any any (45 matches)
```

**Sửa:**
```
R2(config)# interface Gi0/0
R2(config-if)# no ip access-group 100 in
R2(config)# no access-list 100
R1# clear ip bgp 10.0.12.2
```

> ⭐ **Ghi vào `SO-TAY-LOI.md`:**
> **`Idle`** = không có route tới neighbor (ping fail)
> **`Active`** = có route nhưng TCP 179 không lên (ping OK, telnet 179 fail)

---

#### Lỗi 4 — `Established` nhưng `PfxRcd = 0`

```
R2(config)# router bgp 65002
R2(config-router)# no network 10.2.2.0 mask 255.255.255.0
R2(config-router)# no network 2.2.2.2 mask 255.255.255.255
```
```
R1# show ip bgp summary | begin Neighbor
10.0.12.2       4        65002      15      16        9    0    0 00:12:33        3
```
→ Vẫn nhận 3 prefix (route của AS 65003 đi qua R2).

**Trường hợp nhận 0 — thiếu `activate` khi dùng `no bgp default ipv4-unicast`:**
```
R2(config)# router bgp 65002
R2(config-router)# no bgp default ipv4-unicast
R2(config-router)# exit
R1# clear ip bgp 10.0.12.2
R1# show ip bgp summary | begin Neighbor
10.0.12.2       4        65002       5       5        1    0    0 00:00:30        0
```
⭐ **`PfxRcd = 0`** — Established nhưng không nhận gì.

**Chẩn đoán:**
```
R1# show ip bgp neighbors 10.0.12.2 | include Address family|Session
! → nếu không thấy "Address family IPv4 Unicast: advertised and received" = chưa activate
```

**Sửa:**
```
R2(config-router)# address-family ipv4 unicast
R2(config-router-af)#  neighbor 10.0.12.1 activate
R2(config-router-af)#  neighbor 10.0.23.2 activate
R2(config-router-af)#  network 10.2.2.0 mask 255.255.255.0
R2(config-router-af)#  network 2.2.2.2 mask 255.255.255.255
R2(config-router-af)# exit-address-family
```
Hoặc đơn giản: `no no bgp default ipv4-unicast` → `bgp default ipv4-unicast`.

---

#### Lỗi 5 — 🔴 `network` statement không khớp mask

```
R1(config)# router bgp 65001
R1(config-router)# network 10.1.0.0 mask 255.255.0.0        ! /16 — RIB không có
```
```
R1# show ip bgp | include 10.1.0.0
! → TRỐNG, không có gì
```
⭐ **Không có thông báo lỗi nào** — prefix chỉ đơn giản là không xuất hiện.

**Chẩn đoán:**
```
R1# show ip route 10.1.0.0 255.255.0.0
% Subnet not in table                                ← ⭐ RIB không có /16
R1# show ip route | include 10.1
C        10.1.1.0/24 is directly connected, Loopback1
L        10.1.1.1/32 is directly connected, Loopback1
C        10.1.2.0/24 is directly connected, Loopback2
```
⭐ RIB chỉ có `/24`, không có `/16` → `network ... mask 255.255.0.0` **không khớp**.

**Sửa — 2 cách:**
```
! Cách 1: dùng đúng mask có trong RIB
R1(config-router)# no network 10.1.0.0 mask 255.255.0.0
R1(config-router)# network 10.1.1.0 mask 255.255.255.0

! ⭐ Cách 2: tạo static route Null0 để "có hàng trong kho"
R1(config)# ip route 10.1.0.0 255.255.0.0 Null0
R1(config)# router bgp 65001
R1(config-router)#  network 10.1.0.0 mask 255.255.0.0
```
```
R1# show ip bgp | include 10.1.0.0
 *>  10.1.0.0/16      0.0.0.0                  0         32768 i        ← ✅
```

---

#### Lỗi 6 — ⭐ Next-hop unreachable (path valid nhưng không best)

Mô phỏng: dùng loopback peering **mà thiếu route**.
```
R1(config)# router bgp 65001
R1(config-router)# neighbor 3.3.3.3 remote-as 65003
R1(config-router)# neighbor 3.3.3.3 ebgp-multihop 2
R1(config-router)# neighbor 3.3.3.3 update-source Loopback0
! ⚠️ CỐ Ý không tạo route tới 3.3.3.3
```
```
R1# show ip bgp summary | begin Neighbor
3.3.3.3         4        65003       0       0        1    0    0 00:00:25 Idle
```
→ `Idle` vì không có route tới `3.3.3.3`.

**Sửa:**
```
R1(config)# ip route 3.3.3.3 255.255.255.255 10.0.12.2
! Và trên R3:
R3(config)# ip route 1.1.1.1 255.255.255.255 10.0.23.1
R3(config)# router bgp 65003
R3(config-router)#  neighbor 1.1.1.1 remote-as 65001
R3(config-router)#  neighbor 1.1.1.1 ebgp-multihop 2
R3(config-router)#  neighbor 1.1.1.1 update-source Loopback0
```
```
R1# show ip bgp summary | begin Neighbor
3.3.3.3         4        65003       4       4        9    0    0 00:00:35        3
```
✅ Established.

**⚠️ Test bỏ `update-source`:**
```
R1(config-router)# no neighbor 3.3.3.3 update-source Loopback0
R1# clear ip bgp 3.3.3.3
R1# show ip bgp summary | begin Neighbor
3.3.3.3         4        65003       0       0        1    0    0 00:00:15 Active
```
⭐ **`Active`** — R1 gửi từ IP `10.0.12.1`, nhưng R3 khai `neighbor 1.1.1.1` → **từ chối**.

```
R1# show ip bgp neighbors 3.3.3.3 | include Local host
  Local host: 10.0.12.1, Local port: 0            ← ⭐ source SAI
```

**Sửa:** đặt lại `update-source Loopback0`.

**⚠️ Test bỏ `ebgp-multihop`:**
```
R1(config-router)# no neighbor 3.3.3.3 ebgp-multihop
R1# clear ip bgp 3.3.3.3
```
→ `Active`/`Idle` — vì TTL = 1, gói chết trước khi tới `3.3.3.3` (2 hop).

**Dọn dẹp lỗi 6** (bỏ peering loopback để giữ topology gọn cho Module-05B):
```
R1(config-router)# no neighbor 3.3.3.3
R3(config-router)# no neighbor 1.1.1.1
```

---

#### Lỗi 7 — BGP password lệch

```
R1(config)# router bgp 65001
R1(config-router)# neighbor 10.0.12.2 password Secret123
! (R2 chưa có password)
```
```
R1# show logging | include BGP|TCP
%TCP-6-BADAUTH: No MD5 digest from 10.0.12.2(179) to 10.0.12.1(35123) tableid - 0
```
⭐ **`BADAUTH`** — nói thẳng vấn đề MD5.

```
R1# show ip bgp summary | begin Neighbor
10.0.12.2       4        65002      20      22        1    0    0 00:00:40 Idle
```

**Sửa:**
```
R2(config)# router bgp 65002
R2(config-router)# neighbor 10.0.12.1 password Secret123
```
✅ Lên `Established` sau vài giây.

**Dọn dẹp:**
```
R1(config-router)# no neighbor 10.0.12.2 password
R2(config-router)# no neighbor 10.0.12.1 password
```

---

#### Lỗi 8 — ⭐ RIB-failure (`r` trong `show ip bgp`)

```
! Tạo static route AD 1 cho một prefix BGP đang học
R1(config)# ip route 10.2.2.0 255.255.255.0 10.0.12.2
```
```
R1# show ip bgp | include 10.2.2.0
 r>  10.2.2.0/24      10.0.12.2                0             0 65002 i
```
⭐ **`r>`** = ⭐ **RIB-failure** — BGP chọn path này là best, nhưng ⭐ **RIB từ chối cài**
vì đã có route AD tốt hơn (static AD 1 < eBGP AD 20).

```
R1# show ip bgp rib-failure
```
**Output mẫu:**
```
Network            Next Hop                      RIB-failure   RIB-NH Matches
10.2.2.0/24        10.0.12.2                Higher admin distance              n/a
```
⭐ **`Higher admin distance`** — nói rõ nguyên nhân.

```
R1# show ip route 10.2.2.0
Routing entry for 10.2.2.0/24
  Known via "static", distance 1, metric 0                    ← static thắng
```

> ⭐ **`r` KHÔNG phải lỗi** — nó là thông báo *"BGP đã chọn xong, nhưng RIB dùng route khác tốt hơn"*.
> ⚠️ Nhưng cần chú ý: BGP **vẫn quảng bá** path này cho peer, dù nó không thật sự được dùng
> để forward → có thể gây **suboptimal routing hoặc black hole**.

**Sửa:**
```
R1(config)# no ip route 10.2.2.0 255.255.255.0 10.0.12.2
```

✅ **Checkpoint bước 5 — điền bảng (bảng này bằng vàng khi troubleshoot):**

| Lỗi | State/triệu chứng | Lệnh chẩn đoán nhanh nhất |
|---|---|---|
| Sai `remote-as` | | |
| Không có route tới neighbor | | |
| TCP 179 bị chặn | | |
| Thiếu `activate` | | |
| `network` không khớp mask | | |
| Thiếu `update-source` | | |
| Password lệch | | |
| RIB-failure | | |

<details><summary>Đáp án</summary>

| Lỗi | State/triệu chứng | Lệnh chẩn đoán nhanh nhất |
|---|---|---|
| Sai `remote-as` | `Idle`, nhảy Idle/Active | ⭐ `show ip bgp neighbors <ip> \| inc Last reset` → **`bad AS number`** |
| Không có route tới neighbor | ⭐ **`Idle`**, ping **fail** | `show ip route <neighbor-ip>` · `ping <neighbor-ip>` |
| TCP 179 bị chặn | ⭐ **`Active`**, ping **OK** | ⭐ `telnet <neighbor-ip> 179` · `show access-lists` |
| Thiếu `activate` | ⭐ `Established` nhưng **`PfxRcd = 0`** | `show ip bgp neighbors <ip> \| inc Address family` |
| `network` không khớp mask | Prefix **không xuất hiện** trong `show ip bgp`, **không có log** | ⭐ `show ip route <prefix> <mask>` → `% Subnet not in table` |
| Thiếu `update-source` | ⭐ `Active` | ⭐ `show ip bgp neighbors <ip> \| inc Local host` |
| Password lệch | `Idle`, log `BADAUTH` | ⭐ `show logging \| include BADAUTH` |
| RIB-failure | ⭐ **`r>`** trong `show ip bgp` | ⭐ `show ip bgp rib-failure` |
</details>

---

### Bước 6 — 🚀 Bảo mật & soft reset

```
! Bảo mật phiên
R1(config)# router bgp 65001
R1(config-router)#  neighbor 10.0.12.2 password BgpS3cr3t2026
R1(config-router)#  neighbor 10.0.12.2 ttl-security hops 1
R1(config-router)#  neighbor 10.0.12.2 maximum-prefix 1000 90
!
R2(config)# router bgp 65002
R2(config-router)#  neighbor 10.0.12.1 password BgpS3cr3t2026
R2(config-router)#  neighbor 10.0.12.1 ttl-security hops 1
R2(config-router)#  neighbor 10.0.12.1 maximum-prefix 1000 90
```

> ⚠️ `ttl-security hops` và `ebgp-multihop` **loại trừ nhau** — không dùng cùng lúc.

**Test `maximum-prefix`:**
```
R1(config-router)# neighbor 10.0.12.2 maximum-prefix 2 90
```
```
R1# clear ip bgp 10.0.12.2
R1# show logging | include MAXPFX|maximum
%BGP-4-MAXPFX: No. of prefix received from 10.0.12.2 (afi 0) reaches 2, max 2
%BGP-3-MAXPFXEXCEED: No. of prefix received from 10.0.12.2 (afi 0): 3 exceed limit 2
%BGP-5-ADJCHANGE: neighbor 10.0.12.2 Down BGP Notification sent
```
⭐ **Phiên bị đóng** khi vượt giới hạn. Muốn chỉ **cảnh báo** không đóng:
```
R1(config-router)# neighbor 10.0.12.2 maximum-prefix 2 warning-only
```
**Trả về:**
```
R1(config-router)# neighbor 10.0.12.2 maximum-prefix 1000 90
R1# clear ip bgp 10.0.12.2
```

**⭐ Soft reset vs Hard reset:**
```
! ⭐ SOFT (dùng route-refresh, KHÔNG đóng phiên TCP)
clear ip bgp 10.0.12.2 soft in            ! xin peer gửi lại route (sau khi đổi inbound policy)
clear ip bgp 10.0.12.2 soft out           ! gửi lại route cho peer (sau khi đổi outbound policy)
clear ip bgp * soft

! 🔴 HARD (đóng phiên TCP — GÂY DOWNTIME)
clear ip bgp 10.0.12.2
clear ip bgp *                            ! 🔴 reset MỌI phiên — không bao giờ trên production
```

**Kiểm tra route-refresh có hỗ trợ:**
```
R1# show ip bgp neighbors 10.0.12.2 | include Route refresh
    Route refresh: advertised and received(new)          ← ✅ dùng soft được
```

**Nếu peer KHÔNG hỗ trợ route-refresh** → phải lưu route nhận được trong RAM:
```
R1(config-router)# neighbor 10.0.12.2 soft-reconfiguration inbound
```
⭐ Sau đó mới dùng được:
```
R1# show ip bgp neighbors 10.0.12.2 received-routes      ! ⭐ Adj-RIB-In thật
```
⚠️ Tốn RAM (lưu 2 bản copy) — chỉ dùng khi cần.

✅ **Checkpoint bước 6:**

| Kiểm tra | Mong đợi |
|---|---|
| `password` khớp 2 bên → `Established` | ✅ |
| `maximum-prefix` vượt giới hạn → phiên **bị đóng** + log `MAXPFXEXCEED` | ⭐ ✅ |
| `warning-only` → chỉ log, không đóng phiên | ✅ |
| `show ip bgp neighbors <ip> \| inc Route refresh` → hỗ trợ | ✅ |
| Phân biệt được `clear ip bgp x soft in` vs `clear ip bgp x` | ⭐ ✅ |

---

## 💡 5. THỰC CHIẾN ĐI LÀM

| Chủ đề | Thi dạy | Thực tế đi làm |
|---|---|---|
| ⭐ **`maximum-prefix`** | Ít nhắc | 🔴 **BẮT BUỘC trên mọi phiên eBGP với ISP.** Peer route-leak cả full table (>900k prefix) → router hết RAM → sập. Đặt ~1.5× số prefix mong đợi |
| ⭐ **`password`** | Có lệnh | ⭐ Bật trên **mọi** phiên eBGP. Chi phí bằng 0, chống giả mạo peer |
| ⭐ **`ttl-security hops 1`** | Ít nhắc | ⭐ **GTSM** — chống tấn công BGP từ xa. Bật cho eBGP kề nhau. ⚠️ Loại trừ với `ebgp-multihop` |
| ⭐ **`bgp router-id`** | Tự chọn | ⭐ **LUÔN gõ tay** (IP loopback). Router ID nhảy = phiên reset |
| ⭐ **`bgp log-neighbor-changes`** | Không nhắc | ⭐ **Bật luôn.** Không có nó thì phiên flap mà không có log → không biết gì |
| ⭐ **`description`** cho neighbor | Không nhắc | ⭐ Bắt buộc: `neighbor x description ---> ISP-VNPT circuit#12345`. 6 tháng sau bạn sẽ cảm ơn chính mình |
| 🔴 **`clear ip bgp *`** | Lệnh reset | 🔴 **KHÔNG BAO GIỜ gõ trên production.** Nó reset **mọi** phiên → mất toàn bộ Internet route → sập. ⭐ Dùng `clear ip bgp <ip> soft in/out` |
| ⭐ **Soft reset** | Ít nhắc | ⭐ Đổi inbound policy → `soft in`. Đổi outbound policy → `soft out`. Dùng route-refresh, **không downtime** |
| **`soft-reconfiguration inbound`** | Có lệnh | ⚠️ Tốn RAM (2 bản copy route). Chỉ bật khi peer **không** hỗ trợ route-refresh (thiết bị cổ) |
| ⭐ **`network` vs `redistribute`** | Cả hai | ⭐ **Ưu tiên `network`** (origin `i`) hơn `redistribute` (origin `?`) — origin `i` **thắng** trong path selection. Và `redistribute` dễ leak route ngoài ý muốn |
| ⭐ **Null0 static + `network`** | Không dạy | ⭐ Kỹ thuật chuẩn để quảng bá prefix gộp mà không có trong RIB: `ip route <agg> <mask> Null0` + `network <agg> mask <mask>` |
| **eBGP TTL = 1** | Bẫy đề | ⭐ Thực tế eBGP với ISP **luôn** kề nhau trực tiếp → không cần `ebgp-multihop`. Nếu phải dùng multihop, nhớ **luôn kèm `update-source`** |
| ⭐ **`update-source`** | Có lệnh | 🔴 Thiếu nó khi peer qua loopback = **kẹt Active**, và rất khó tìm. Nhớ: `show ip bgp neighbors <ip> \| inc Local host` |
| **Timer BGP** | 60/180 | ⭐ Đừng tune xuống thấp (tốn CPU, và Internet table lớn thì keepalive chậm). ⭐ **Dùng BFD** (`neighbor x fall-over bfd`) — phát hiện ~900 ms |
| ⭐ **`fall-over`** | Không dạy | ⭐ `neighbor x fall-over` — phiên xuống **ngay** khi mất route tới neighbor, không chờ hold time 180 s |
| ⭐ **`Active` state** | Bẫy đề | ⭐ Quy trình 3 bước: (1) `ping <neighbor>` — fail thì là routing · (2) `telnet <neighbor> 179` — fail thì TCP bị chặn · (3) `show ip bgp nei <ip> \| inc Local host` — sai source |
| ⭐ **`show ip bgp <prefix>`** | Ít nhắc | ⭐ **Lệnh troubleshoot số 1 của BGP.** Nó hiện **mọi path** + **lý do path nào best**. Học đọc output này thay vì đoán |
| ⭐ **`r` RIB-failure** | Ít nhắc | ⚠️ BGP **vẫn quảng bá** path RIB-failure cho peer dù không dùng để forward → **suboptimal/black hole**. `show ip bgp rib-failure` để rà soát |
| ⭐ **Bảng route BGP lớn** | Không dạy | ⚠️ Full Internet table >900k prefix, cần **≥ 4 GB RAM** trên router. Nhận **default route only** từ ISP nếu không cần full table |
| ⭐ **Tài liệu hóa** | Không có | ⭐ Bảng bắt buộc: mỗi phiên eBGP — peer IP, ASN, circuit ID, nhà cung cấp, prefix mình quảng bá, prefix mong đợi nhận, `maximum-prefix`, người liên hệ NOC |

---

## 🎓 6. BẪY TRONG ĐỀ ENCOR

| # | Bẫy | Sự thật |
|:---:|---|---|
| 1 | 🔴 **`Active` là trạng thái tốt?** | ❌ **KHÔNG!** ⭐ `Active` = **TCP thất bại, đang thử lại**. `Established` mới là tốt |
| 2 | ⭐ Phân biệt `Idle` vs `Active` | ⭐ `Idle` = **không có route** tới neighbor (ping fail) · `Active` = **có route nhưng TCP 179 không lên** (ping OK, telnet 179 fail) |
| 3 | 6 neighbor state theo thứ tự | **Idle → Connect → (Active) → OpenSent → OpenConfirm → Established** |
| 4 | BGP dùng transport gì | ⭐ **TCP port 179** |
| 5 | AD của eBGP / iBGP | ⭐ **20 / 200** |
| 6 | Loại protocol | ⭐ **Path Vector** (không phải distance vector / link-state) |
| 7 | Timer BGP | ⭐ **Keepalive 60 s · Hold 180 s** |
| 8 | ⭐ Hold time có phải khớp? | ❌ **KHÔNG** — 2 bên dùng ⭐ **giá trị NHỎ HƠN** (khác OSPF!) |
| 9 | 5 message type | **OPEN · UPDATE · KEEPALIVE · NOTIFICATION · ROUTE-REFRESH** |
| 10 | Message nào **đóng phiên** | ⭐ **NOTIFICATION** |
| 11 | Trường nào trong OPEN phải khớp | ⭐ **My AS** (khớp `remote-as` của peer) và **BGP ID unique**. Hold time **không** cần khớp |
| 12 | ⭐ eBGP TTL mặc định | ⭐ **1** → phải kề nhau. Peer qua loopback cần `ebgp-multihop` + `update-source` |
| 13 | Thiếu `update-source` khi peer qua loopback | ⭐ Kẹt **`Active`** — peer từ chối vì source IP không khớp |
| 14 | ⭐ `network` của BGP khác OSPF thế nào | ⭐ BGP: **"quảng bá prefix NẾU có trong RIB, khớp CHÍNH XÁC prefix + mask"** · dùng **subnet mask** (không phải wildcard) |
| 15 | 🔴 `network 10.1.0.0 mask 255.255.0.0` mà RIB chỉ có `/24` | ❌ **KHÔNG quảng bá**, và ⭐ **không có log lỗi** |
| 16 | Cách quảng bá prefix không có trong RIB | ⭐ `ip route <prefix> <mask> Null0` rồi `network` |
| 17 | ⭐ eBGP có đổi next-hop? iBGP? | ⭐ eBGP **đổi** thành IP của mình · iBGP ⭐ **KHÔNG đổi** → cần `next-hop-self` |
| 18 | ⭐ eBGP có thêm ASN vào AS-path? iBGP? | ⭐ eBGP **thêm** (vào **đầu**) · iBGP ⭐ **không thêm** |
| 19 | ⭐ **iBGP split-horizon rule** | ⭐ Route học từ **iBGP peer** ⭐ **KHÔNG quảng bá cho iBGP peer khác** → cần **full mesh** hoặc **Route Reflector** |
| 20 | Số phiên iBGP full mesh cho n router | ⭐ **n(n-1)/2** |
| 21 | ⭐ `*` và `>` trong `show ip bgp` | ⭐ `*` = **valid** (next-hop reachable) · `>` = **best** (vào RIB) · `*>` = cả hai |
| 22 | `*` mà không có `>` nghĩa là gì | Valid nhưng **không best** — có path khác tốt hơn |
| 23 | Không có `*` nghĩa là gì | 🔴 **Không valid** — thường là **next-hop unreachable** |
| 24 | ⭐ **`r`** trong `show ip bgp` | ⭐ **RIB-failure** — BGP chọn best nhưng RIB có route **AD tốt hơn**. `show ip bgp rib-failure` |
| 25 | ⭐ `Next Hop = 0.0.0.0` nghĩa là gì | ⭐ Route do **CHÍNH router này** sinh ra |
| 26 | ⭐ `Weight = 32768` nghĩa là gì | ⭐ Route do **chính router này** sinh · `0` = học từ peer |
| 27 | ⭐ Cột `Metric` trong `show ip bgp` là gì | ⭐ Là **MED** |
| 28 | ⭐ Đọc AS-path `65002 65003 i` | ⭐ Đọc **từ phải sang trái**: xuất phát AS **65003**, qua AS **65002**. Độ dài = **2** |
| 29 | ⭐ 3 Origin code + thứ tự ưu tiên | ⭐ **`i` (IGP/`network`) < `e` (EGP) < `?` (incomplete/`redistribute`)** — `i` **tốt nhất** |
| 30 | ⭐ Weight thuộc nhóm attribute nào | ⭐ **KHÔNG phải attribute BGP** — là **Cisco-only**, ⭐ **chỉ local**, không gửi đi đâu |
| 31 | 4 nhóm attribute | ⭐ **Well-known Mandatory** (AS-path, Next-hop, Origin) · **Well-known Discretionary** (LocPref, Atomic Aggregate) · **Optional Transitive** (Community, Aggregator) · **Optional Non-transitive** (MED) |
| 32 | ⭐ MED thuộc nhóm nào, lan tới đâu | ⭐ **Optional Non-transitive** — gửi **sang AS kề**, ⭐ **KHÔNG gửi tiếp** |
| 33 | ⭐ Local Preference lan tới đâu | ⭐ **Trong AS** (qua iBGP), ⭐ **KHÔNG** qua eBGP. Mặc định **100** |
| 34 | Attribute nào **CAO** tốt, nào **THẤP** tốt | ⭐ **CAO tốt: Weight, Local Pref** · **THẤP tốt: AS-path length, MED, Origin, Router ID** |
| 35 | ⭐ `Established` nhưng `PfxRcd = 0` | ⭐ Thiếu `neighbor x activate` (khi dùng `no bgp default ipv4-unicast`) · peer không quảng bá · filter chặn hết |
| 36 | ⭐ `soft in` vs `clear ip bgp <ip>` | ⭐ `soft in` = dùng **route-refresh**, **không đóng phiên** · `clear ip bgp <ip>` = 🔴 **hard reset, đóng TCP** |
| 37 | Lệnh xem route **gửi cho** peer | ⭐ `show ip bgp neighbors <ip> advertised-routes` |
| 38 | Lệnh xem route **nhận từ** peer (trước policy) | `show ip bgp neighbors <ip> received-routes` — ⚠️ cần `soft-reconfiguration inbound` |
| 39 | `maximum-prefix` vượt giới hạn thì sao | ⭐ **Đóng phiên** (mặc định). Muốn chỉ cảnh báo → `warning-only` |
| 40 | ⭐ `ttl-security` và `ebgp-multihop` | ⭐ **Loại trừ nhau** — không dùng cùng lúc |

---

## 🐛 7. GỠ LỖI NHANH

### 7.1 Hộp lệnh vạn năng

```
! ═══ BẢNG 1: NEIGHBOR ═══
show ip bgp summary                              ! ⭐⭐ LỆNH ĐẦU TIÊN LUÔN
show ip bgp summary | begin Neighbor             ! chỉ phần bảng neighbor
show ip bgp neighbors                             ! chi tiết mọi neighbor
show ip bgp neighbors <ip>                        ! ⭐ chi tiết 1 neighbor
show ip bgp neighbors <ip> | include Last reset|notification    ! ⭐⭐ LÝ DO RESET
show ip bgp neighbors <ip> | include Local host|Foreign host    ! ⭐ source IP thật
show ip bgp neighbors <ip> | include state|up for|dropped
show ip bgp neighbors <ip> | include Address family|Route refresh

! ═══ BẢNG 2: BGP TABLE ═══
show ip bgp                                       ! ⭐ toàn bộ BGP table
show ip bgp <prefix>                              ! ⭐⭐ MỌI path + LÝ DO best
show ip bgp <prefix> <mask>
show ip bgp neighbors <ip> routes                 ! route nhận từ peer (sau policy)
show ip bgp neighbors <ip> advertised-routes      ! ⭐ route GỬI cho peer
show ip bgp neighbors <ip> received-routes        ! ⚠️ cần soft-reconfiguration inbound
show ip bgp rib-failure                           ! ⭐ path 'r' và lý do
show ip bgp paths                                  ! danh sách AS-path
show ip bgp regexp ^$                             ! ⭐ route sinh trong AS mình
show ip bgp regexp _65003_                        ! route đi qua AS 65003
show ip bgp regexp ^65002_                        ! route từ AS kề 65002

! ═══ BẢNG 3: ROUTING TABLE ═══
show ip route bgp
show ip route <prefix>                            ! AD 20 (eBGP) hay 200 (iBGP)?

! ═══ NỀN TẢNG (đừng bỏ) ═══
show ip route <neighbor-ip>                       ! ⭐ có route tới neighbor?
ping <neighbor-ip>                                ! ⭐ L3 thông?
telnet <neighbor-ip> 179                          ! ⭐⭐ TCP 179 thông?
show access-lists                                 ! ACL chặn 179?
show tcp brief                                     ! phiên TCP 179 đang mở?
show logging | include BGP|BADAUTH|MAXPFX|TCP     ! ⭐ log nói thẳng nguyên nhân

! ═══ RESET ═══
clear ip bgp <ip> soft in                         ! ⭐ route-refresh, KHÔNG downtime
clear ip bgp <ip> soft out
clear ip bgp <ip>                                 ! 🔴 hard reset
clear ip bgp *                                    ! 🔴🔴 KHÔNG DÙNG TRÊN PRODUCTION

! ═══ DEBUG (⚠️ chỉ lab) ═══
debug ip bgp                                       ! sự kiện chung
debug ip bgp <ip>                                  ! 1 neighbor
debug ip bgp events
debug ip bgp updates                               ! ⚠️ RẤT nhiều output
debug ip tcp transactions                          ! ⭐ xem TCP 179 lên/xuống
undebug all
```

### 7.2 Bảng lỗi: triệu chứng → nguyên nhân → cách sửa

| # | Triệu chứng | Nguyên nhân | Lệnh chẩn đoán | Cách sửa |
|:---:|---|---|---|---|
| 1 | ⭐ **`Idle`**, `ping` neighbor **fail** | ⭐ **Không có route** tới neighbor IP | `show ip route <neighbor-ip>` · `ping` | Sửa routing/interface |
| 2 | ⭐ **`Idle`**, `ping` **OK** | Sai `remote-as` · password lệch · neighbor bị `shutdown` | ⭐ `show ip bgp nei <ip> \| inc Last reset` · `show logging \| inc BGP\|BADAUTH` | Sửa theo lý do trong log |
| 3 | ⭐🔴 **`Active`**, `ping` **OK** | ⭐ **TCP 179 bị chặn** · thiếu `update-source` · sai IP neighbor | ⭐⭐ `telnet <neighbor-ip> 179` · `show access-lists` · `show ip bgp nei <ip> \| inc Local host` | Mở ACL cho TCP 179 · thêm `update-source` |
| 4 | `Idle (Admin)` | Neighbor bị `neighbor x shutdown` | `show run \| sec router bgp` | `no neighbor x shutdown` |
| 5 | Kẹt `OpenSent` | Sai ASN · Router ID trùng | `show ip bgp nei <ip> \| inc Last reset` → `bad AS number` | Sửa `remote-as` / `bgp router-id` |
| 6 | Kẹt `OpenConfirm` | Password/auth lệch · capability không tương thích | `show logging \| inc BADAUTH` | Khớp password |
| 7 | ⭐ `Established` nhưng **`PfxRcd = 0`** | ⭐ Thiếu `activate` · peer chưa `network` gì · filter chặn hết | `show ip bgp nei <ip> \| inc Address family` · `show ip bgp nei <ip> advertised-routes` **trên peer** | `neighbor x activate` · thêm `network` · rà filter |
| 8 | 🔴 Prefix **không xuất hiện** trong `show ip bgp`, **không log** | ⭐ **`network` không khớp prefix+mask trong RIB** | ⭐ `show ip route <prefix> <mask>` → `% Subnet not in table` | Dùng đúng mask · hoặc `ip route <prefix> <mask> Null0` |
| 9 | ⭐ Path có `*` nhưng **không có `>`** | Có path khác tốt hơn (đúng) — hoặc ⭐ **next-hop unreachable** | ⭐ `show ip bgp <prefix>` → đọc `valid`/`inaccessible` · `show ip route <next-hop>` | Thêm route tới next-hop · `next-hop-self` (iBGP) |
| 10 | Path **không có `*`** | 🔴 **Next-hop unreachable** | `show ip bgp <prefix>` · `show ip route <next-hop>` | `next-hop-self` · quảng bá subnet vào IGP |
| 11 | ⭐ **`r>`** RIB-failure | ⭐ RIB có route **AD tốt hơn** (static/IGP) | ⭐ `show ip bgp rib-failure` · `show ip route <prefix>` | Xóa route AD thấp · hoặc đổi AD BGP (`distance bgp`) |
| 12 | Phiên **flap liên tục** (`dropped` cao) | Link nhấp nháy · `maximum-prefix` vượt · CPU cao · MTU/MSS | `show ip bgp nei <ip> \| inc dropped\|Last reset` · `show logging` · `show interfaces \| inc flapped` | Sửa link · tăng `maximum-prefix` · bật BFD |
| 13 | ⭐ Phiên đóng, log `MAXPFXEXCEED` | ⭐ Peer gửi quá `maximum-prefix` | `show logging \| inc MAXPFX` | Tăng giới hạn · hoặc lọc bớt prefix nhận · hoặc `warning-only` |
| 14 | Log `%TCP-6-BADAUTH` | ⭐ **BGP password lệch** | `show logging \| inc BADAUTH` | Khớp `neighbor x password` |
| 15 | `InQ`/`OutQ` khác 0 lâu | CPU cao · bảng BGP quá lớn · phiên nghẽn | `show processes cpu sorted` (M01) · `show ip bgp summary` | Giảm prefix nhận · nâng cấp thiết bị |
| 16 | Đổi route-map/filter mà **không có tác dụng** | ⭐ Chưa reset phiên | — | ⭐ `clear ip bgp <ip> soft in` (inbound) / `soft out` (outbound) |
| 17 | `received-routes` báo lỗi/không có gì | Chưa bật `soft-reconfiguration inbound` | `show run \| sec router bgp` | `neighbor x soft-reconfiguration inbound` (⚠️ tốn RAM) |
| 18 | Peer qua loopback không lên (`Active`) | ⭐ Thiếu `ebgp-multihop` **hoặc** `update-source` **hoặc** route tới loopback peer | `show ip bgp nei <ip> \| inc Local host` · `show ip route <peer-loopback>` | Thêm cả **3** thứ |
| 19 | Route của AS mình **quay lại** | ⭐ Ai đó bật `allowas-in` | `show run \| inc allowas-in` | Bỏ `allowas-in` |
| 20 | ⭐ Nhận full Internet table ngoài ý muốn | Không có filter inbound + ISP gửi full table | `show ip bgp summary` (PfxRcd rất lớn) | ⭐ `maximum-prefix` · prefix-list inbound (Module-05B) · xin ISP gửi default-only |

### 7.3 ⭐ Quy trình troubleshoot BGP — 4 bước

```
0. LỆNH ĐẦU TIÊN LUÔN
   show ip bgp summary
   → đọc cột State/PfxRcd
        ↓
1. PHIÊN CHƯA ESTABLISHED?
   ├─ Idle   → ping <neighbor-ip>
   │           ├─ FAIL → ⭐ vấn đề ROUTING (không có route tới neighbor)
   │           └─ OK   → show ip bgp nei <ip> | inc Last reset
   │                     → "bad AS number"? password? shutdown?
   │
   ├─ Active → ⭐⭐ telnet <neighbor-ip> 179
   │           ├─ FAIL → ⭐ TCP 179 BỊ CHẶN (ACL/firewall)
   │           └─ OK   → show ip bgp nei <ip> | inc Local host
   │                     → source IP sai? thiếu update-source?
   │
   ├─ OpenSent/OpenConfirm → sai ASN / Router ID trùng / password
   └─ Idle (Admin)          → neighbor bị shutdown
        ↓
2. ESTABLISHED nhưng PfxRcd = 0?
   ├─ show ip bgp nei <ip> | inc Address family    → đã activate?
   ├─ (TRÊN PEER) show ip bgp nei <my-ip> advertised-routes  → peer có gửi gì?
   └─ show run | sec router bgp                     → filter inbound chặn hết?
        ↓
3. CÓ PREFIX NHƯNG KHÔNG VÀO RIB?
   show ip bgp <prefix>
   ├─ Không có `*`  → ⭐ NEXT-HOP UNREACHABLE → show ip route <next-hop>
   ├─ Có `*` không `>` → path khác best hơn (đọc lý do trong output)
   ├─ Có `r`        → ⭐ RIB-FAILURE → show ip bgp rib-failure
   └─ Có `*>`       → ✅ vào RIB → show ip route <prefix>
        ↓
4. PREFIX MÌNH MUỐN QUẢNG BÁ KHÔNG XUẤT HIỆN?
   ⭐ show ip route <prefix> <mask>
   ├─ "% Subnet not in table" → ⭐ network statement KHÔNG KHỚP
   │                             → dùng đúng mask, hoặc ip route ... Null0
   └─ Có trong RIB → kiểm tra filter outbound · show ip bgp nei <peer> advertised-routes
```

> ⭐ **Hai lệnh phân biệt nhanh nhất:**
> **`ping <neighbor>`** → phân biệt "vấn đề routing" (Idle) vs "vấn đề khác"
> **`telnet <neighbor> 179`** → phân biệt "TCP bị chặn" (Active) vs "vấn đề BGP"

---

## 📝 8. QUIZ TỰ KIỂM TRA

**Câu 1.** Neighbor BGP ở state `Active`. Đây là trạng thái tốt hay xấu? Nêu 3 nguyên nhân
và lệnh chẩn đoán từng cái.

<details><summary>Xem đáp án</summary>

🔴 **Trạng thái XẤU.** `Active` = **"TCP thất bại, tôi đang CHỦ ĐỘNG thử kết nối lại"**.
`Established` mới là trạng thái tốt.

⭐ **Đây là bẫy ngôn ngữ** — "active" trong tiếng Anh thông thường nghĩa là tốt, trong BGP thì ngược lại.

**3 nguyên nhân + lệnh chẩn đoán:**

| # | Nguyên nhân | Lệnh chẩn đoán |
|:---:|---|---|
| 1 | ⭐ **TCP 179 bị chặn** (ACL/firewall) | ⭐⭐ `telnet <neighbor-ip> 179` → timeout/refused · `show access-lists` (xem counter) |
| 2 | ⭐ **Thiếu `update-source`** khi peer qua loopback | ⭐ `show ip bgp neighbors <ip> \| include Local host` → source IP không khớp `neighbor` peer khai |
| 3 | **Sai IP neighbor** · route bất đối xứng | `show run \| sec router bgp` · `show ip route <neighbor-ip>` |

⭐ **Phân biệt `Idle` vs `Active` — quan trọng nhất:**

| | `Idle` | `Active` |
|---|---|---|
| `ping <neighbor>` | ❌ **FAIL** | ✅ **OK** |
| Nghĩa | **Không có route** tới neighbor | Có route nhưng **TCP không lên** |
| Kiểm tra | `show ip route <neighbor-ip>` | ⭐ `telnet <neighbor-ip> 179` |
</details>

---

**Câu 2.** So sánh eBGP và iBGP theo 6 tiêu chí: AD, TTL, AS-path, Next-hop, Local Pref,
split-horizon rule.

<details><summary>Xem đáp án</summary>

| Tiêu chí | ⭐ **eBGP** | ⭐ **iBGP** |
|---|---|---|
| **AD** | **20** | **200** |
| **TTL** gói BGP | **1** (phải kề nhau) | **255** (đi nhiều hop được) |
| ⭐ **AS-path** khi quảng bá | ⭐ **THÊM ASN của mình vào ĐẦU** | ⭐ **KHÔNG thay đổi** |
| ⭐ **Next-hop** khi quảng bá | ⭐ **ĐỔI thành IP của mình** | ⭐ **KHÔNG đổi** → cần `next-hop-self` |
| **Local Preference** | ⭐ **KHÔNG gửi** qua eBGP | ⭐ **Gửi** trong AS |
| ⭐ **Split-horizon rule** | Không áp dụng | ⭐ **Route học từ iBGP KHÔNG quảng bá cho iBGP peer khác** → cần **full mesh** hoặc **Route Reflector** |

⭐ **Vì sao iBGP cần split-horizon rule:** iBGP **không thêm ASN vào AS-path** (cùng AS)
→ **không có cơ chế chống loop** → nếu cho quảng bá lại thì route chạy vòng vô tận trong AS.

⭐ **Vì sao eBGP TTL = 1:** eBGP giả định peer **kề nhau trực tiếp** (1 hop).
Muốn peer xa hơn → `ebgp-multihop <ttl>` **+ `update-source`**.
</details>

---

**Câu 3.** Bạn cấu hình `network 10.1.0.0 mask 255.255.0.0` nhưng prefix không xuất hiện trong
`show ip bgp`, và không có log lỗi nào. Nguyên nhân? 2 cách sửa?

<details><summary>Xem đáp án</summary>

⭐ **BGP `network` statement yêu cầu prefix KHỚP CHÍNH XÁC (cả prefix VÀ mask) trong bảng route.**

RIB chỉ có `10.1.1.0/24`, `10.1.2.0/24` — **không có** `10.1.0.0/16` → `network` không khớp
→ ⭐ **BGP không quảng bá, và không có thông báo lỗi**.

**Chẩn đoán:**
```
show ip route 10.1.0.0 255.255.0.0
! % Subnet not in table                        ← ⭐ đây là câu trả lời
show ip route | include 10.1
! C  10.1.1.0/24 is directly connected, Loopback1
! C  10.1.2.0/24 is directly connected, Loopback2
```

**Cách sửa 1 — dùng đúng mask có trong RIB:**
```
router bgp 65001
 no network 10.1.0.0 mask 255.255.0.0
 network 10.1.1.0 mask 255.255.255.0
 network 10.1.2.0 mask 255.255.255.0
```

⭐ **Cách sửa 2 — tạo static route Null0 (kỹ thuật chuẩn công nghiệp):**
```
ip route 10.1.0.0 255.255.0.0 Null0
router bgp 65001
 network 10.1.0.0 mask 255.255.0.0
```
Giờ RIB **có** `/16` → `network` khớp → quảng bá được.
Traffic tới subnet không tồn tại trong `/16` sẽ **drop tại Null0** —
giống discard route của OSPF summarization (Module-04B §2.3).

⭐ **Khác biệt với OSPF:** OSPF `network 10.1.0.0 0.0.255.255 area 0` nghĩa là
*"bật OSPF trên mọi interface có IP khớp wildcard"* — hoàn toàn khác.
Và BGP dùng **subnet mask**, OSPF dùng **wildcard mask**.
</details>

---

**Câu 4.** Đọc dòng này trong `show ip bgp`. Giải thích **từng** thành phần.
```
 *>  10.3.3.0/24      10.0.12.2                              0 65002 65003 i
```

<details><summary>Xem đáp án</summary>

| Thành phần | Nghĩa |
|---|---|
| ⭐ **`*`** | **valid** — path hợp lệ, next-hop **reachable** |
| ⭐ **`>`** | **best** — path này được chọn, ⭐ **đưa xuống RIB** |
| `10.3.3.0/24` | Prefix (NLRI) |
| `10.0.12.2` | **Next-hop** — IP để tới đích |
| *(Metric trống)* | ⭐ **MED không được đặt** |
| *(LocPrf trống)* | Local Preference = **100** (mặc định), hoặc không áp dụng vì là eBGP |
| ⭐ **`0`** | ⭐ **Weight = 0** → route **học từ peer** (nếu là 32768 thì do chính router sinh) |
| ⭐ **`65002 65003`** | ⭐ **AS-path** — đọc **từ PHẢI sang TRÁI**: route xuất phát từ AS **65003**, đi qua AS **65002**, rồi tới tôi. ⭐ **Độ dài = 2** |
| ⭐ **`i`** (ký tự cuối) | ⭐ **Origin code = IGP** → route được quảng bá bằng **`network` statement** (tốt nhất trong 3 loại) |

⭐ **3 Origin code:** `i` (IGP/`network`) **<** `e` (EGP) **<** `?` (incomplete/`redistribute`)
— `i` **được ưu tiên nhất**.

⭐ **3 giá trị Weight phải nhớ:** `32768` = route **của chính mình** · `0` = **học từ peer** ·
khác = đã đặt tay.
</details>

---

**Câu 5.** Điền bảng 4 nhóm attribute và ví dụ. Weight thuộc nhóm nào?

<details><summary>Xem đáp án</summary>

| Nhóm | Định nghĩa | Ví dụ |
|---|---|---|
| ⭐ **Well-known Mandatory** | Mọi BGP **phải hiểu**, **phải có** trong mọi UPDATE | ⭐ **AS-path · Next-hop · Origin** |
| ⭐ **Well-known Discretionary** | Mọi BGP phải hiểu, **không bắt buộc có** | ⭐ **Local Preference** · Atomic Aggregate |
| ⭐ **Optional Transitive** | Có thể không hiểu, nhưng ⭐ **vẫn chuyển tiếp** | ⭐ **Community** · Aggregator |
| ⭐ **Optional Non-transitive** | Có thể không hiểu, ⭐ **KHÔNG chuyển tiếp** | ⭐ **MED** · Originator-ID · Cluster-list |

⭐⭐ **Weight KHÔNG thuộc nhóm nào — nó KHÔNG PHẢI attribute BGP.**

| Weight | Chi tiết |
|---|---|
| Bản chất | ⭐ **Cisco proprietary** — không có trong RFC 4271 |
| Phạm vi | ⭐ **CHỈ local trên router đó** — ⭐ **không bao giờ được gửi** cho bất kỳ peer nào |
| Giá trị | 0–65535. `32768` = route của chính mình · `0` = học từ peer |
| Tốt nhất | Càng **CAO** càng tốt |
| Vị trí trong path selection | ⭐ **BƯỚC 1** (Module-05B) |

⭐ **Bảng "CAO tốt vs THẤP tốt":**

| Càng **CAO** càng tốt | Càng **THẤP** càng tốt |
|---|---|
| ⭐ **Weight** | ⭐ **AS-path length** |
| ⭐ **Local Preference** | ⭐ **MED** · Origin (i<e<?) · Router ID · IGP metric |

🧠 *Hai cái đầu (Weight, LocPref) — CAO thắng. Còn lại — THẤP thắng.*
</details>

---

**Câu 6.** BGP neighbor `Established` nhưng `State/PfxRcd` = `0`. Nêu 3 nguyên nhân và cách kiểm tra.

<details><summary>Xem đáp án</summary>

| # | Nguyên nhân | Cách kiểm tra |
|:---:|---|---|
| 1 | ⭐ **Thiếu `neighbor x activate`** (khi dùng `no bgp default ipv4-unicast`) | ⭐ `show ip bgp neighbors <ip> \| include Address family` → phải thấy `Address family IPv4 Unicast: advertised and received` |
| 2 | ⭐ **Peer không quảng bá gì** (thiếu `network` / `network` không khớp mask) | ⭐ **TRÊN PEER**: `show ip bgp neighbors <my-ip> advertised-routes` · `show ip bgp` |
| 3 | ⭐ **Filter inbound chặn hết** (prefix-list/route-map thiếu catch-all) | `show run \| sec router bgp` · `show ip prefix-list detail` (xem hit count) · `show route-map` (xem counter) |

**Sửa từng cái:**
```
! 1. activate
router bgp 65001
 address-family ipv4 unicast
  neighbor 10.0.12.2 activate

! 2. peer thiếu network (làm trên peer)
router bgp 65002
 network 10.2.2.0 mask 255.255.255.0        ! đúng mask có trong RIB!

! 3. filter thiếu catch-all
ip prefix-list PL-IN seq 100 permit 0.0.0.0/0 le 32     ! ⭐ catch-all
! rồi: clear ip bgp 10.0.12.2 soft in
```

⭐ **Lưu ý:** sau khi đổi filter, phải `clear ip bgp <ip> soft in` — nếu không, filter mới
**không được áp** cho route đã nhận trước đó.
</details>

---

**Câu 7.** Trong `show ip bgp` bạn thấy `r>` trước một prefix. Nghĩa là gì? Có phải lỗi không?
Rủi ro là gì?

<details><summary>Xem đáp án</summary>

⭐ **`r` = RIB-failure.** BGP đã chọn path này là **best**, nhưng ⭐ **RIB từ chối cài nó**
vì đã có route từ nguồn khác với **AD tốt hơn**.

**Ví dụ:** BGP học `10.2.2.0/24` qua eBGP (AD **20**), nhưng có static route cho cùng prefix
(AD **1**) → static thắng → BGP path bị **RIB-failure**.

**Chẩn đoán:**
```
show ip bgp rib-failure
! Network        Next Hop      RIB-failure              RIB-NH Matches
! 10.2.2.0/24    10.0.12.2     Higher admin distance    n/a
show ip route 10.2.2.0
! Known via "static", distance 1, metric 0
```

**Có phải lỗi không:** ⭐ **Không hẳn** — nó là **thông báo trạng thái**, có thể hoàn toàn đúng ý bạn
(bạn **muốn** static thắng BGP).

⚠️ **Nhưng rủi ro thật:**

⭐ **BGP VẪN quảng bá path này cho peer** — dù nó **không thật sự được dùng để forward**.
Nghĩa là:
- Bạn nói với peer *"gửi traffic `10.2.2.0/24` cho tôi, tôi biết đường"*
- Nhưng thực tế bạn forward theo **static route**, có thể đi hướng **khác hoàn toàn**
- → ⭐ **Suboptimal routing**, hoặc **black hole** nếu static route trỏ sai/Null0

**Cách xử lý:**
```
! Cách 1: xóa route AD thấp nếu không cần
no ip route 10.2.2.0 255.255.255.0 10.0.12.2

! Cách 2: đổi AD của BGP để nó thắng (⚠️ cẩn thận)
router bgp 65001
 distance bgp 20 200 200
! hoặc distance <ext> <int> <local> với giá trị nhỏ hơn AD của nguồn kia

! Cách 3: rà soát định kỳ
show ip bgp rib-failure
```

⭐ **Best practice:** chạy `show ip bgp rib-failure` khi nhận bàn giao mạng BGP —
nó thường phơi ra những static route "tạm" mà ai đó để lại và quên xóa.
</details>

---

**Câu 8.** Bạn muốn peer eBGP giữa 2 loopback (`1.1.1.1` ↔ `3.3.3.3`), 2 router cách nhau 2 hop.
Cần những gì? Thiếu mỗi cái thì kẹt state nào?

<details><summary>Xem đáp án</summary>

⭐ **Cần 3 thứ trên MỖI router:**

```
! Trên R1 (AS 65001)
ip route 3.3.3.3 255.255.255.255 10.0.12.2          ! ⭐ 1. Route tới loopback peer
!
router bgp 65001
 neighbor 3.3.3.3 remote-as 65003
 neighbor 3.3.3.3 ebgp-multihop 2                    ! ⭐ 2. Tăng TTL (mặc định eBGP = 1)
 neighbor 3.3.3.3 update-source Loopback0            ! ⭐ 3. Source = loopback

! Trên R3 (AS 65003) — đối xứng
ip route 1.1.1.1 255.255.255.255 10.0.23.1
router bgp 65003
 neighbor 1.1.1.1 remote-as 65001
 neighbor 1.1.1.1 ebgp-multihop 2
 neighbor 1.1.1.1 update-source Loopback0
```

⭐ **Thiếu mỗi cái thì sao:**

| Thiếu | State | Vì sao | Lệnh chẩn đoán |
|---|:---:|---|---|
| **Route tới loopback peer** | ⭐ **`Idle`** | Không mở được TCP tới `3.3.3.3` | `show ip route 3.3.3.3` · `ping 3.3.3.3` |
| ⭐ **`ebgp-multihop`** | **`Active`**/`Idle` | TTL = 1 → gói chết sau hop đầu (peer cách 2 hop) | `debug ip tcp transactions` |
| ⭐ **`update-source`** | ⭐ **`Active`** | Source IP là IP interface vật lý (`10.0.12.1`), nhưng R3 khai `neighbor 1.1.1.1` → ⭐ **R3 TỪ CHỐI** connection | ⭐ `show ip bgp neighbors 3.3.3.3 \| include Local host` → thấy source **sai** |

⚠️ **Lưu ý:** `ttl-security hops` và `ebgp-multihop` ⭐ **loại trừ nhau** — không dùng cùng lúc.

⭐ **Thực tế:** eBGP với ISP **hầu như luôn** kề nhau trực tiếp → **không cần** multihop.
Loopback peering chủ yếu dùng cho **iBGP** (để phiên không phụ thuộc 1 interface vật lý cụ thể).
</details>

---

**Câu 9.** Phân biệt `clear ip bgp 10.0.12.2 soft in` và `clear ip bgp 10.0.12.2`.
Khi nào dùng cái nào?

<details><summary>Xem đáp án</summary>

| | ⭐ **`clear ip bgp <ip> soft in`** | 🔴 **`clear ip bgp <ip>`** |
|---|---|---|
| Cơ chế | ⭐ Dùng **ROUTE-REFRESH message** | Đóng **phiên TCP** rồi mở lại |
| Phiên TCP | ⭐ **GIỮ NGUYÊN** | 🔴 **Đóng và mở lại** |
| Downtime | ⭐ **Không có** | 🔴 **Có** — mất toàn bộ route của peer đó trong lúc reset |
| Dùng khi | ⭐ Đổi **inbound** policy (prefix-list/route-map inbound) | Chỉ khi bắt buộc (đổi ASN, đổi Router ID) |

**Các biến thể:**
```
clear ip bgp <ip> soft in            ! ⭐ đổi INBOUND policy → xin peer gửi lại
clear ip bgp <ip> soft out           ! ⭐ đổi OUTBOUND policy → gửi lại cho peer
clear ip bgp <ip> soft               ! cả hai chiều
clear ip bgp * soft                  ! soft cho mọi peer
!
clear ip bgp <ip>                    ! 🔴 hard reset 1 peer
clear ip bgp *                       ! 🔴🔴 hard reset MỌI peer — KHÔNG BAO GIỜ trên production
```

**Điều kiện để `soft in` hoạt động:** peer phải hỗ trợ **route-refresh capability**:
```
show ip bgp neighbors 10.0.12.2 | include Route refresh
!  Route refresh: advertised and received(new)        ← ✅ OK
```

⭐ **Nếu peer KHÔNG hỗ trợ route-refresh** (thiết bị rất cổ) → phải lưu bản copy trong RAM:
```
router bgp 65001
 neighbor 10.0.12.2 soft-reconfiguration inbound     ! ⚠️ tốn RAM (2 bản copy)
```
Bù lại, khi bật nó thì dùng được:
```
show ip bgp neighbors 10.0.12.2 received-routes       ! ⭐ Adj-RIB-In thật (trước policy)
```

🔴 **Cảnh báo production:** `clear ip bgp *` trên router biên Internet = **mất toàn bộ
Internet route** trong vài phút (thời gian nhận lại full table) = **sự cố diện rộng**.
Đây là một trong những lệnh gây sự cố do người vận hành nhiều nhất.
</details>

---

**Câu 10.** BGP dùng TCP 179. Nêu 3 hệ quả quan trọng của lựa chọn thiết kế này
(so với OSPF dùng IP protocol 89).

<details><summary>Xem đáp án</summary>

| # | Hệ quả | Chi tiết |
|:---:|---|---|
| **1** | ⭐ **Neighbor KHÔNG tự tìm nhau — phải khai báo tay** | OSPF/EIGRP gửi Hello **multicast** trên link → tự phát hiện neighbor. BGP dùng TCP unicast → ⭐ **bắt buộc** `neighbor <ip> remote-as <asn>` |
| **2** | ⭐ **Neighbor KHÔNG cần kề nhau** | Chỉ cần **IP reachable**. Đây là nền tảng cho **iBGP peer qua loopback** và **eBGP multihop**. ⚠️ Nhưng eBGP mặc định TTL=1 nên vẫn phải kề nhau, trừ khi `ebgp-multihop` |
| **3** | ⭐ **BGP không tự lo reliability — để TCP lo** | TCP xử lý retransmit, ordering, windowing, flow control. Nên BGP **không cần** cơ chế ACK riêng như OSPF (LSAck). ⭐ Và vì TCP tự phân đoạn, BGP chở được **hàng triệu prefix** không bị giới hạn MTU |

**Hệ quả phụ (hay hỏi):**

| Hệ quả | Chi tiết |
|---|---|
| ⭐ **Cần IGP trước** (với iBGP) | TCP phải tới được peer → cần route. Đây là lý do iBGP luôn chạy **trên nền một IGP** |
| ⭐ **TCP 179 có thể bị firewall chặn** | → gây state **`Active`**. Lệnh test: `telnet <peer> 179` |
| ⭐ **Có thể bảo mật bằng MD5 của TCP** | `neighbor x password` — dùng TCP MD5 signature option |
| **Update incremental** | Không cần refresh định kỳ như OSPF (30 phút) — TCP đảm bảo đã nhận |
| Có thể có nhiều phiên qua 1 link | Multi-session, multiple address family |

🧠 **Một câu tổng kết:** *BGP "thuê" TCP làm phần khó (tin cậy, thứ tự, phân đoạn)
để tập trung vào việc của nó: **chính sách định tuyến**. Cái giá là phải khai báo neighbor tay
và phụ thuộc vào việc TCP 179 thông.*
</details>

---

## 📚 9. THUẬT NGỮ ANH–VIỆT

| Tiếng Anh | Tiếng Việt | Ghi chú |
|---|---|---|
| **BGP** (Border Gateway Protocol) | Giao thức cổng biên | RFC 4271. Protocol của Internet |
| ⭐ **Path Vector** | Vector đường đi | ⭐ Quan tâm **"đã đi qua AS nào"**, không phải "xa bao nhiêu" |
| **AS** (Autonomous System) | Hệ tự trị | Tập router dưới cùng một chính sách quản trị |
| **ASN** | Số hiệu AS | 16-bit (1–65535) hoặc 32-bit. Private: `64512–65534` |
| ⭐ **eBGP** (External BGP) | BGP ngoại | ⭐ Giữa **AS khác nhau**. AD **20**, TTL **1** |
| ⭐ **iBGP** (Internal BGP) | BGP nội | ⭐ Trong **cùng AS**. AD **200**, TTL 255 |
| ⭐ **Split-horizon rule (iBGP)** | Quy tắc chân trời chia | ⭐ Route học từ iBGP **không** quảng bá cho iBGP peer khác |
| ⭐ **Full mesh** | Lưới đầy đủ | Mọi router iBGP peer với nhau. **n(n-1)/2** phiên |
| **Route Reflector (RR)** | Bộ phản chiếu route | 🟡 Phá split-horizon rule → khỏi cần full mesh |
| **Confederation** | Liên hợp | 🟡 Chia AS lớn thành sub-AS |
| ⭐ **`next-hop-self`** | Tự làm next-hop | ⭐ Router biên đổi next-hop thành IP của mình khi quảng bá cho iBGP peer |
| **Peer / Neighbor** | Đối tác / Láng giềng | ⭐ Phải **khai báo tay** — BGP không tự tìm |
| ⭐ **`Established`** | Đã thành lập | ✅ **Trạng thái TỐT** |
| ⭐ **`Active`** | "Chủ động" | 🔴 **Trạng thái XẤU** — TCP thất bại, đang thử lại |
| **`Idle`** | Rảnh | ⚠️ Không có route tới neighbor |
| **`Connect`** | Đang kết nối | Đang mở TCP |
| **`OpenSent` / `OpenConfirm`** | Đã gửi/xác nhận OPEN | Đang đàm phán |
| **OPEN message** | Bản tin mở | Đàm phán ASN, Router ID, hold time, capabilities |
| **UPDATE message** | Bản tin cập nhật | Quảng bá (NLRI + attribute) hoặc rút route |
| **KEEPALIVE** | Duy trì | Mỗi 60 s |
| ⭐ **NOTIFICATION** | Thông báo lỗi | ⭐ **Báo lỗi rồi ĐÓNG phiên**. Đọc lý do reset ở đây |
| ⭐ **ROUTE-REFRESH** | Làm mới route | ⭐ Xin gửi lại route **không cần reset phiên** |
| **NLRI** (Network Layer Reachability Info) | Thông tin khả năng tới được | = prefix trong UPDATE |
| **Withdrawn routes** | Route bị rút | Prefix không còn hợp lệ |
| **Hold time** | Thời gian giữ | 180 s. ⭐ **Không cần khớp** — dùng giá trị nhỏ hơn |
| **Adj-RIB-In / Out** | RIB kề vào / ra | Route nhận từ / gửi cho mỗi neighbor |
| ⭐ **`*` valid** | Hợp lệ | Next-hop **reachable** |
| ⭐ **`>` best** | Tốt nhất | ⭐ Path được chọn, đưa xuống RIB |
| ⭐ **`r` RIB-failure** | Thất bại cài RIB | ⭐ BGP chọn best nhưng RIB có route **AD tốt hơn** |
| **`s` suppressed** | Bị đè | Bị `aggregate-address` gộp (Module-05B) |
| **`d` damped** | Bị dập | Route flap damping |
| ⭐ **AS-path** | Đường AS | ⭐ Chống loop + chọn đường. eBGP **thêm ASN vào đầu**. Đọc **phải→trái** |
| ⭐ **Origin** | Nguồn gốc | ⭐ `i` (IGP/`network`) **<** `e` (EGP) **<** `?` (incomplete/`redistribute`) |
| ⭐ **Weight** | Trọng số | ⭐ **Cisco-only, KHÔNG phải attribute BGP**, ⭐ **chỉ local**. `32768` = của mình · `0` = học từ peer. **CAO** tốt |
| ⭐ **Local Preference** | Ưu tiên cục bộ | ⭐ Trong AS, mặc định **100**. **CAO** tốt. Chọn đường **RA** khỏi AS |
| ⭐ **MED** (Multi-Exit Discriminator) | Phân biệt đa lối ra | ⭐ **Optional Non-transitive** — sang AS kề, **không gửi tiếp**. **THẤP** tốt. Gợi ý điểm **VÀO** AS mình |
| **Next-hop** | Chặng kế | eBGP đổi · iBGP không đổi |
| ⭐ **Community** | Cộng đồng | ⭐ **Optional Transitive** — nhãn nhóm route (Module-05B) |
| **Atomic Aggregate** | Gộp nguyên tử | Cảnh báo route đã gộp, mất chi tiết AS-path |
| **Aggregator** | Bộ gộp | ASN + Router ID của router đã gộp |
| ⭐ **Well-known Mandatory** | Nổi tiếng bắt buộc | ⭐ AS-path · Next-hop · Origin |
| ⭐ **Well-known Discretionary** | Nổi tiếng tùy chọn | ⭐ Local Pref · Atomic Aggregate |
| ⭐ **Optional Transitive** | Tùy chọn chuyển tiếp | ⭐ Community · Aggregator — **vẫn chuyển tiếp** dù không hiểu |
| ⭐ **Optional Non-transitive** | Tùy chọn không chuyển tiếp | ⭐ MED · Originator-ID — **không chuyển tiếp** |
| ⭐ **`ebgp-multihop`** | eBGP nhiều hop | ⭐ Tăng TTL (mặc định eBGP TTL = **1**) |
| ⭐ **`update-source`** | Nguồn cập nhật | ⭐ Interface làm source IP. Thiếu = kẹt **`Active`** |
| ⭐ **`activate`** | Kích hoạt | ⭐ Bắt buộc khi dùng `no bgp default ipv4-unicast`. Thiếu = **`PfxRcd = 0`** |
| ⭐ **`maximum-prefix`** | Số prefix tối đa | ⭐ Chống **route leak** làm router hết RAM. **BẮT BUỘC** với ISP |
| **Route leak** | Rò rỉ route | Peer vô tình quảng bá quá nhiều prefix |
| ⭐ **`ttl-security hops`** (GTSM) | Bảo mật TTL | ⭐ Chỉ nhận gói TTL ≥ 255−n. ⚠️ Loại trừ với `ebgp-multihop` |
| ⭐ **Soft reset** | Reset mềm | ⭐ Dùng route-refresh, **không đóng phiên TCP**, không downtime |
| 🔴 **Hard reset** | Reset cứng | 🔴 `clear ip bgp <ip>` — đóng TCP, **gây downtime** |
| **`soft-reconfiguration inbound`** | Cấu hình lại mềm chiều vào | Lưu bản copy route nhận (⚠️ tốn RAM). Cần cho `received-routes` |
| ⭐ **`fall-over`** | Xuống ngay | ⭐ Phiên xuống ngay khi mất route tới neighbor (không chờ hold 180 s) |
| **`allowas-in`** | Cho phép AS mình | ⚠️ Cho phép nhận route có ASN của mình trong AS-path. Dùng sai = mở đường loop |
| **BFD** (Bidirectional Forwarding Detection) | Phát hiện chuyển tiếp 2 chiều | ⭐ Phát hiện lỗi ~900 ms thay vì 180 s |

---

## 🎯 10. ĐÚC KẾT MODULE-05A

**3 điều rút ra:**

1. ⭐ **`Established` là tốt, `Active` là XẤU.** Và hai lệnh phân biệt nhanh nhất:
   **`ping <neighbor>`** (fail → `Idle`, vấn đề routing) và **`telnet <neighbor> 179`**
   (fail → `Active`, TCP 179 bị chặn). Hai lệnh này thay thế được nửa giờ đoán mò.

2. ⭐ **BGP `network` statement khác OSPF hoàn toàn:** nó nói *"quảng bá prefix này **NẾU** nó có trong RIB,
   **khớp CHÍNH XÁC** prefix + mask"* — và nếu không khớp thì ⭐ **im lặng, không có log lỗi**.
   Cách vượt qua: `ip route <prefix> <mask> Null0` rồi `network`.

3. ⭐ **`show ip bgp <prefix>` là lệnh troubleshoot số 1 của BGP.** BGP **giữ lại mọi path**
   trong BGP table (khác OSPF chỉ giữ kết quả SPF) → bạn xem được **toàn bộ phương án** và
   **lý do path nào best**. Đọc `*` (valid), `>` (best), `r` (RIB-failure) là đọc được BGP.

🧠 **Một câu để nhớ:** *OSPF chọn đường **ngắn nhất về kỹ thuật**, BGP chọn đường
**hợp chính sách nhất về kinh doanh**. Đó là lý do BGP không có một cái metric duy nhất
mà có **13 bước attribute** — và đó chính là Module-05B.*

---

### ✅ TỰ CHẤM

**Phần A — Trả lời được bằng lời của mình:**

| # | Câu | ✅ |
|:---:|---|:---:|
| 1 | BGP là loại protocol gì? Transport? AD eBGP/iBGP? | ☐ |
| 2 | Nêu 3 hệ quả của việc BGP dùng TCP 179 | ☐ |
| 3 | 6 neighbor state theo thứ tự | ☐ |
| 4 | ⭐ Phân biệt `Idle` vs `Active` — 2 lệnh phân biệt nhanh nhất? | ☐ |
| 5 | 5 message type + message nào đóng phiên? | ☐ |
| 6 | Trường nào trong OPEN phải khớp? Hold time có phải khớp? | ☐ |
| 7 | Timer BGP mặc định? | ☐ |
| 8 | eBGP vs iBGP theo 6 tiêu chí (AD, TTL, AS-path, Next-hop, LocPref, split-horizon) | ☐ |
| 9 | ⭐ Vì sao iBGP cần split-horizon rule? Hệ quả? 2 giải pháp? | ☐ |
| 10 | `next-hop-self` giải quyết vấn đề gì? | ☐ |
| 11 | 3 bảng của BGP + tên 3 sub-table | ☐ |
| 12 | ⭐ BGP `network` khác OSPF `network` thế nào? 2 cách quảng bá prefix không có trong RIB? | ☐ |
| 13 | ⭐ Đọc được `*`, `>`, `*>`, `r`, `s`, `i` trong `show ip bgp` | ☐ |
| 14 | ⭐ `Next Hop = 0.0.0.0` và `Weight = 32768` nghĩa là gì? | ☐ |
| 15 | ⭐ Đọc AS-path `65002 65003 i` — hướng đọc, độ dài, origin | ☐ |
| 16 | 3 Origin code + thứ tự ưu tiên | ☐ |
| 17 | ⭐ 4 nhóm attribute + ví dụ. Weight thuộc nhóm nào? | ☐ |
| 18 | ⭐ Attribute nào CAO tốt, nào THẤP tốt? | ☐ |
| 19 | MED và Local Pref lan tới đâu? | ☐ |
| 20 | ⭐ `Established` nhưng `PfxRcd = 0` — 3 nguyên nhân? | ☐ |
| 21 | ⭐ `r` RIB-failure là gì? Rủi ro? | ☐ |
| 22 | Peer qua loopback cần 3 thứ gì? Thiếu mỗi cái kẹt state nào? | ☐ |
| 23 | ⭐ `soft in` vs `clear ip bgp <ip>` — khi nào dùng cái nào? | ☐ |
| 24 | `maximum-prefix` chống gì? Vượt giới hạn thì sao? | ☐ |

**Phần B — Lab:**

| # | Yêu cầu | ✅ |
|:---:|---|:---:|
| 1 | Dựng 4 router / 4 AS, eBGP peering đầy đủ, mọi phiên `Established` | ☐ |
| 2 | ⭐ Đọc và giải thích **từng cột** của `show ip bgp summary` | ☐ |
| 3 | ⭐ Đọc và giải thích **từng cột** của `show ip bgp` (kể cả `*`, `>`, Weight, Path, Origin) | ☐ |
| 4 | ⭐ Dùng `show ip bgp <prefix>` chỉ ra path, next-hop, `valid/external/best` | ☐ |
| 5 | Đọc `show ip bgp neighbors <ip>`: `external link`, timer đã đàm phán, `Prefixes Current`, `Local host` | ☐ |
| 6 | Verify `show ip route bgp` có `B` và `[20/0]`, ping/traceroute full-mesh | ☐ |
| 7 | ⭐⭐ **Chứng minh AS-path chống loop**: `advertised-routes` trên R2 **không có** prefix của AS 65003 | ☐ |
| 8 | 🔴 Tái hiện **sai `remote-as`** → chẩn đoán bằng `Last reset` → thấy `bad AS number` | ☐ |
| 9 | Tái hiện **không có route tới neighbor** → `Idle`, ping fail | ☐ |
| 10 | ⭐⭐ Tái hiện **ACL chặn TCP 179** → `Active`, **ping OK** nhưng `telnet 179` fail | ☐ |
| 11 | Tái hiện **thiếu `activate`** → `Established` nhưng `PfxRcd = 0` | ☐ |
| 12 | ⭐ Tái hiện **`network` không khớp mask** → prefix không xuất hiện, **không log** → sửa bằng Null0 | ☐ |
| 13 | ⭐ Cấu hình **peer qua loopback** (`ebgp-multihop` + `update-source` + static route) | ☐ |
| 14 | ⭐ Tái hiện **thiếu `update-source`** → `Active` → chẩn đoán bằng `Local host` | ☐ |
| 15 | Tái hiện **password lệch** → log `BADAUTH` | ☐ |
| 16 | ⭐ Tái hiện **RIB-failure** (`r>`) bằng static AD 1 → `show ip bgp rib-failure` | ☐ |
| 17 | Bật `password` + `ttl-security` + `maximum-prefix`, test vượt giới hạn → log `MAXPFXEXCEED` | ☐ |
| 18 | Phân biệt thực tế `clear ip bgp x soft in` vs `clear ip bgp x` (quan sát `Up/Down` reset hay không) | ☐ |
| 19 | Dùng `show ip bgp regexp ^$` và `_65003_` để lọc route theo AS-path | ☐ |
| 20 | ⭐ Điền đủ **bảng 8 lỗi** ở §4 bước 5 (triệu chứng ↔ lệnh chẩn đoán nhanh nhất) | ☐ |
| 21 | Cố ý phá 1 thứ, tự tìm ra bằng **quy trình 4 bước §7.3** trong 10 phút | ☐ |

> ⚠️ **Giữ nguyên lab này** — Module-05B dùng chính topology 4 AS này để thao tác
> Weight / Local Pref / AS-path prepend / MED. Nhớ **Export CFG** trước khi đóng lab (Module-00 §8.3).

---

## 🔗 11. TÀI LIỆU CHO MODULE NÀY

| Nguồn | Cụ thể |
|---|---|
| **Sách OCG 350-401** | Chương **BGP** đầu tiên — đọc kỹ phần neighbor states, message types, `network` statement, attribute classification |
| **Cisco doc** ⭐ | *IP Routing: BGP Configuration Guide* → *Configuring a Basic BGP Network* |
| **Cisco doc** ⭐⭐ | ***BGP Case Studies*** — tài liệu kinh điển của Cisco, giải thích bằng ví dụ thực tế. Search: `cisco bgp case studies` |
| **Cisco doc** ⭐ | *Troubleshooting BGP* — quy trình chuẩn cho `Idle`/`Active` |
| **Cisco doc** | *BGP Neighbor States* · *Understanding and Configuring the `network` Command in BGP* |
| **Cisco doc** | *BGP Support for TTL Security Check* (GTSM) · *BGP Maximum-Prefix* |
| **RFC 4271** | BGP-4 — đọc **Section 8 (Finite State Machine)** và **Section 5 (Path Attributes)** |
| **Cisco Live** ⭐ | Search `Cisco Live BGP best practices enterprise` · `Cisco Live BGP troubleshooting` |
| **NetworkLessons** ⭐ | Loạt bài *BGP Neighbor Adjacency*, *BGP Attributes*, *eBGP Multihop* — nhiều bài free |
| **Video** | CBT Nuggets ENCOR — module BGP · Keith Barker: search `Keith Barker BGP neighbor states` |
| **Wireshark** | Filter `bgp` → xem OPEN (ASN, hold time, capabilities), UPDATE (NLRI + attribute), NOTIFICATION. ⭐ Bắt trên link R1↔R2 lúc `clear ip bgp` để thấy trọn quá trình |
| **Forum** | https://community.cisco.com — search `bgp stuck active`, `bgp established 0 prefixes received`, `bgp network statement not advertised` |

---

**➡️ Tiếp theo:** [Module-05B — BGP: Path Selection & Filtering](Module-05B-BGP-Path-Selection-va-Filtering.md)
*(⭐ **13 bước best path selection** · Weight · Local Pref · AS-path prepend · MED ·
Community · prefix-list / AS-path ACL / route-map · `aggregate-address` — **Tuần 10**)*
