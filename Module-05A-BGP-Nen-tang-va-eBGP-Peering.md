# Module-05A — BGP: Nền tảng & eBGP Peering

> 🧭 **Lộ trình:** [Module-04B](Module-04B-OSPF-Area-Summarization-OSPFv3.md) → `[Bạn đang ở đây] Module-05A` → [Module-05B](Module-05B-BGP-Path-Selection-va-Filtering.md) → Module-06
>
> 📊 **Blueprint:** Domain **3.0 Infrastructure (30%)**, mục **3.2.c — Configure and verify eBGP
> between directly connected neighbors (best path selection algorithm and neighbor relationships)**
>
> ⏱️ **Tuần 9** · 10 giờ

---

# 📌 TÓM TẮT — đọc 10 phút là nắm khung

## Module này trả lời một câu hỏi duy nhất

> **"Hai công ty KHÁC NHAU, không tin nhau, muốn trao đổi thông tin định tuyến —
> làm sao làm được mà không ai phá được ai?"**

Đó là lý do BGP tồn tại và vì sao nó **khác hẳn OSPF**.

## BGP khác IGP ở đâu — hình này giải thích tất cả

```
   OSPF/EIGRP (IGP)                    BGP
   ─────────────────                   ───
   "Đường nào NGẮN NHẤT?"              "Đi qua NHỮNG AI?"

   Đo bằng: cost, bandwidth            Đo bằng: AS-PATH
                                       (danh sách AS đã đi qua)

   Trong MỘT tổ chức                   Giữa CÁC tổ chức khác nhau
   → tin nhau hoàn toàn                → KHÔNG tin nhau

   Hội tụ: vài GIÂY                    Hội tụ: vài PHÚT
   → ưu tiên NHANH                     → ưu tiên ỔN ĐỊNH và KIỂM SOÁT ĐƯỢC
```

⭐ **Chống loop cũng khác:** IGP dùng thuật toán (SPF/DUAL).
BGP dùng **AS-path**: *"thấy số AS của mình trong danh sách → route này đã đi qua đây rồi → BỎ."*

## Ba bảng của BGP — chỗ người mới hay vấp nhất

```
   ① NEIGHBOR TABLE      "Tôi peering được với ai?"
      show ip bgp summary          ← phải thấy số prefix, KHÔNG phải Active/Idle
              │
              ▼
   ② BGP TABLE           "Tôi biết những ĐƯỜNG NÀO tới mỗi đích?"
      show ip bgp                  ← giữ MỌI path, kể cả path không dùng
              │  chọn best path (13 bước — Module-05B)
              ▼
   ③ ROUTING TABLE       "Đường nào THỰC SỰ được dùng?"
      show ip route bgp            ← chỉ path best (>) VÀ next-hop phải tới được

   🔴 Bẫy lớn nhất: route NẰM TRONG BGP table nhưng KHÔNG vào routing table.
      Thường vì next-hop không reachable.
```

## 7 ý phải nhớ

| # | Ý | Một câu |
|:---:|---|---|
| 1 | **BGP là path-vector** | Không đo khoảng cách — đếm **đã đi qua những AS nào** |
| 2 | ⭐ **eBGP vs iBGP** | eBGP = **giữa các AS**, AD **20**, TTL 1 · iBGP = **trong cùng AS**, AD **200** |
| 3 | 🔴 ⭐⭐ **"Active" là trạng thái XẤU** | Nó nghĩa là *đang thử kết nối mà chưa được*. Tốt là **`Established`** |
| 4 | **Sáu trạng thái** | Idle → Connect → Active → OpenSent → OpenConfirm → **Established** |
| 5 | ⭐ **Ba bảng** | Neighbor → **BGP table** (giữ mọi path) → Routing table (chỉ path best) |
| 6 | ⭐ **`network` phải khớp CHÍNH XÁC** | Prefix và mask phải **có sẵn trong routing table**, sai một bit là không quảng bá |
| 7 | 🔴 **iBGP không quảng bá lại route học từ iBGP** | Nên ≥ 3 router iBGP phải **full-mesh** với nhau |

## Bảng lệnh cốt lõi

| Lệnh | Cho biết gì |
|---|---|
| `show ip bgp summary` | Peering lên chưa — nhìn cột **State/PfxRcd** |
| `show ip bgp` | **BGP table** — mọi path, dấu `*` (hợp lệ) và `>` (best) |
| `show ip bgp <prefix>` | Chi tiết một prefix: mọi path, vì sao chọn path đó |
| `show ip bgp neighbors <ip>` | Chi tiết peering: timer, capability, số message |
| `show ip route bgp` | Kết quả cuối — path best đã vào routing table |
| `clear ip bgp * soft in` | ⭐ **Xin gửi lại route mà KHÔNG ngắt phiên** |
| `debug ip bgp updates` | Theo dõi update *(chỉ lab)* |

## 🗺️ Bố cục module — đọc theo đúng thứ tự này

| Phần | Tên | Đọc thế nào | Thời gian |
|:---:|---|---|:---:|
| **1** | 🧠 **CÁI ĐÓ LÀ GÌ** | 5 ví von, đọc **một mạch** | 45 phút |
| **2** | ⚙️ **NÓ CHẠY THẾ NÀO** | 9 mục. ⭐ **Then chốt: §3.3, §3.4, §3.5** | 4 giờ |
| **3** | 🧪 **NHÌN THẤY NÓ** | [LAB 05A](Module-05A-LAB.md) — 6 bước, có 8 lỗi kinh điển | 7 giờ |
| **4** | 🏗️ **TOPO & KIẾN TRÚC** | Khi nào cần BGP, đấu nối ra sao. **Vẽ lại trên giấy** | 45 phút |
| **📎** | **PHỤ LỤC** | 🔴 **KHÔNG đọc lần đầu** — chỉ tra | — |

> ⭐ **Điều quan trọng nhất cần đổi trong đầu khi học BGP:**
> bạn đã quen IGP suốt 3 module (03, 04A, 04B) với tư duy *"tìm đường ngắn nhất"*.
> **BGP không quan tâm đường ngắn.** Nó quan tâm **chính sách** — *"tôi MUỐN traffic đi đường nào"*.
>
> Nếu thấy BGP "vô lý", thường là vì bạn đang áp tư duy IGP vào nó.

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

## 🧠 PHẦN 1 — CÁI ĐÓ LÀ GÌ

> **Đọc phần này TRƯỚC, đọc một mạch.** Không lệnh, không bảng tra.
>
> BGP khác hẳn OSPF: nó **không quan tâm đường nào ngắn**, mà quan tâm **đi qua những ai**.
> Năm ví von dưới đây là cách đổi tư duy từ IGP sang BGP.
>
> **Tự kiểm tra:** đọc xong mỗi mục, gấp tài liệu lại, nói lại trong 3 câu.

### 2.1 Path Vector — không phải distance, mà là "đã đi qua đâu"

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

### 2.2 AS-path = chống loop bằng "danh sách nơi đã đến"

Route đi từ AS 65001 → 65002 → 65003, AS-path thành `65002 65001`
(⭐ mỗi eBGP hop **thêm ASN vào ĐẦU**).

Khi route quay lại AS 65001, router AS 65001 nhìn AS-path thấy **có ASN của chính mình**
→ ⭐ **từ chối ngay** → không loop.

🧠 **Một câu để nhớ:** *AS-path như **danh sách con dấu hộ chiếu** (giống route tag ở Module-03 §3.6,
nhưng tự động và bắt buộc). Thấy dấu của chính mình = đã từng đi qua = quay lại = từ chối.*

⭐ **Và đó là lý do iBGP cần split-horizon rule:** iBGP **không thêm dấu** (cùng AS)
→ không có cơ chế phát hiện → phải chặn bằng quy tắc "không quảng bá lại cho iBGP peer khác".

### 2.3 "Active" là trạng thái xấu — bẫy ngôn ngữ

| Từ | Nghĩa thông thường | ⭐ Nghĩa trong BGP |
|---|---|---|
| **Active** | Đang hoạt động tốt ✅ | 🔴 **TCP THẤT BẠI, đang chủ động thử lại** |
| **Established** | Đã thành lập | ✅ **Trạng thái TỐT** |
| **Idle** | Rảnh rỗi | ⚠️ Chưa/không kết nối được |

🧠 **Một câu để nhớ:** *Trong BGP, **`Established` là tốt, `Active` là xấu**.
"Active" = "tôi đang **tích cực gõ cửa** mà không ai mở" — nghĩa là TCP không lên được.*

⭐ **Ba thứ kiểm tra khi thấy Active:** (1) có route tới neighbor? (2) TCP 179 bị chặn?
(3) sai IP / thiếu `update-source`?

### 2.4 BGP table giữ nhiều path — như nhiều báo giá

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

### 2.5 `network` statement của BGP như "đăng ký hàng có sẵn"

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

## ⚙️ PHẦN 2 — NÓ CHẠY THẾ NÀO

> Giờ lắp **cơ chế thật, con số và câu lệnh** vào hình dung bạn vừa có.
>
> | Phần 1 (ví von) | → | Phần 2 (cơ chế) |
> |---|:---:|---|
> | §2.1 path vector · §2.2 danh sách nơi đã đến | → | **§3.1 BGP trong 1 bảng · §3.3 eBGP vs iBGP** |
> | §2.3 "Active" là bẫy ngôn ngữ | → | **§3.5 Sáu trạng thái neighbor** |
> | §2.4 nhiều báo giá | → | **§3.4 Ba bảng của BGP** ⭐ |
> | §2.5 đăng ký hàng có sẵn | → | **§3.8 Cấu hình eBGP · `network` statement** |
>
> ⚠️ **Ba mục then chốt: §3.3** (eBGP vs iBGP), **§3.4** (ba bảng), **§3.5** (sáu trạng thái).
> Ba mục đó chiếm phần lớn câu hỏi BGP cơ bản của đề.

### 3.1 BGP trong 1 bảng

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

### 3.2 AS & ASN

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

### 3.3 ⭐ eBGP vs iBGP — bảng phải thuộc

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
   50 router →  1225 phiên    Không khả thi
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
! Cách 1 (khuyến nghị): next-hop-self trên router biên
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

### 3.4 ⭐ Ba bảng của BGP

```
┌────────────────────────────────────────────────────────────────────┐
│ 1. NEIGHBOR TABLE       "Tôi peer với ai, phiên TCP thế nào?"      │
│    show ip bgp summary                                             │
│    → Neighbor IP · ASN · State/PfxRcd · Up/Down · MsgRcvd/Sent     │
├────────────────────────────────────────────────────────────────────┤
│ 2. BGP TABLE (BGP RIB)  "Mọi đường tôi biết tới mỗi đích"          │
│    show ip bgp                                                     │
│    → Có thể có NHIỀU path cho 1 prefix. Chỉ 1 được chọn "best"  │
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
show ip bgp neighbors 10.0.12.2 advertised-routes   ! Adj-RIB-Out
```

### 3.5 ⭐ Sáu trạng thái neighbor

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

### 3.6 Năm loại BGP message

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
clear ip bgp 10.0.12.2 soft in         ! dùng route-refresh, KHÔNG reset phiên
clear ip bgp 10.0.12.2                 ! HARD RESET — đóng phiên TCP, gây downtime
```

### 3.7 Timer

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

### 3.8 Cấu hình eBGP cơ bản

```
router bgp 65001                                  ! ASN CỦA MÌNH
 bgp router-id 1.1.1.1                            ! nên gõ tay
 bgp log-neighbor-changes                         ! log khi neighbor up/down
 no bgp default ipv4-unicast                      ! (tùy chọn — xem §2.9)
 !
 neighbor 10.0.12.2 remote-as 65002               ! ASN CỦA PEER
 neighbor 10.0.12.2 description ---> To AS65002 R2
 !
 network 10.1.1.0 mask 255.255.255.0              ! quảng bá prefix
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
  neighbor 10.0.12.2 activate                    ! bắt buộc
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
 neighbor 2.2.2.2 ebgp-multihop 2                 ! tăng TTL từ 1 lên 2
 neighbor 2.2.2.2 update-source Loopback0         ! dùng loopback làm source
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
 neighbor 10.0.12.2 password MyBgpS3cret          ! MD5 cho phiên TCP
 neighbor 10.0.12.2 ttl-security hops 1           ! GTSM — chỉ nhận gói TTL ≥ 254
 neighbor 10.0.12.2 maximum-prefix 100000 90      ! chống nhận quá nhiều prefix
```

| Lệnh | Chống gì |
|---|---|
| `password` | Ai đó giả mạo peer |
| ⭐ `ttl-security hops <n>` | **GTSM** — chống tấn công từ xa (spoofed packet có TTL thấp) |
| ⭐ `maximum-prefix <n> <%>` | ⭐ **Route leak** — peer vô tình gửi cả full Internet table → router hết RAM |

> ⭐ `maximum-prefix` là **bắt buộc** ở mọi phiên eBGP với ISP thật.
> Nhiều sự cố Internet toàn cầu bắt nguồn từ route leak — thiếu lệnh này thì router bạn chết theo.

### 3.9 ⭐ Phân loại BGP Attribute — 4 nhóm

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

## 🧪 PHẦN 3 — NHÌN THẤY NÓ

> LAB đã tách ra file riêng để bạn **mở song song** với lý thuyết.

> ### 👉 **[LAB 05A — Tuần 9: eBGP 3 AS](Module-05A-LAB.md)**

| Bước | Nội dung | Ví von ở Phần 1 | Cơ chế ở Phần 2 |
|:---:|---|---|---|
| 1 | Verify neighbor | §2.3 "Active" là bẫy ngôn ngữ | §3.5 · §3.6 |
| 2 | ⭐⭐ **Đọc BGP table** | §2.4 nhiều báo giá | §3.4 |
| 3 | Verify routing table | §2.4 | §3.4 |
| 4 | ⭐ Chứng minh AS-path chống loop | §2.1 path vector · §2.2 danh sách nơi đã đến | §3.3 |
| 5 | ⭐⭐ Tái hiện 8 lỗi kinh điển | §2.5 đăng ký hàng có sẵn | §3.8 |
| 6 | 🚀 Soft reset & bảo mật | — | §3.7 |

> ⚠️ **Bước 2 là phần quan trọng nhất của Module-05A.**
> BGP có **BA bảng**, không phải một — và bảng ở giữa (BGP table) là thứ phân biệt
> người hiểu BGP với người chỉ biết gõ lệnh.
>
> Ở bước 3 bạn sẽ thấy tình huống gây bối rối nhất của BGP: ⭐ **route nằm trong BGP table
> nhưng KHÔNG vào được routing table**. Hiểu được vì sao là qua được nửa chặng đường.

---

## 🏗️ PHẦN 4 — TOPO & KIẾN TRÚC

> Bạn vừa học cơ chế BGP. Phần này trả lời: **doanh nghiệp dùng BGP khi nào, và đấu nối ra sao?**

### 4.1 Bản đồ: BGP trong doanh nghiệp thật

```
        AS 64500 (ISP-A)              AS 64600 (ISP-B)
             │                              │
             │  eBGP                        │  eBGP
             │  (AD 20)                     │  (AD 20)
        ┌────┴──────────┐          ┌────────┴────┐
        │  Edge-1       │          │   Edge-2    │   ① Router BIÊN
        │  AS 65000     │◄──iBGP──►│  AS 65000   │      nói eBGP ra ngoài
        └────┬──────────┘  (AD 200)└────────┬────┘
             │                              │
             │      ② iBGP giữa 2 edge      │
             │         — BẮT BUỘC            │
             │                              │
        ┌────┴──────────────────────────────┴────┐
        │            MẠNG NỘI BỘ                  │   ③ Bên trong dùng
        │         OSPF / EIGRP                    │      IGP, KHÔNG dùng BGP
        │      (AD 110 / 90)                      │
        └─────────────────────────────────────────┘

   ④ Redistribute IGP → BGP? ⚠️ CẨN THẬN. Thường dùng `network` statement thay thế
```

### 4.2 Năm quyết định — và sai thì hỏng thế nào

| # | Quyết định | Vì sao | 🔴 Sai thì hỏng thế nào |
|:---:|---|---|---|
| ① | **Khi nào cần BGP?** | Chỉ khi có **≥ 2 ISP** và cần chủ động chọn đường vào/ra | Một ISP duy nhất → ⭐ **default route là đủ.** Dùng BGP là tự làm khổ mình |
| ② | **Hai edge phải có iBGP giữa chúng** | Route học từ ISP-A phải tới được Edge-2 | Thiếu iBGP → Edge-2 không biết route của ISP-A → **traffic ra sai hướng** |
| ③ | **Nội bộ dùng IGP, không dùng BGP** | BGP hội tụ **chậm** (tính bằng phút), IGP tính bằng giây | Chạy BGP nội bộ → đứt link là **chờ rất lâu mới hội tụ** |
| ④ | **Dùng `network` thay redistribute IGP→BGP** | Redistribute cả bảng IGP vào BGP = **bơm rác ra Internet** | Redistribute bừa → quảng bá cả mạng riêng ra ngoài, ISP có thể **cắt peering** |
| ⑤ | **Lọc cả chiều VÀO và chiều RA** | Mặc định BGP **nhận và quảng bá mọi thứ** | Không lọc chiều ra → ⭐ **bạn thành ISP trung chuyển bất đắc dĩ** cho traffic của người khác |

### 4.3 Ba sự thật mà chỉ người đi làm mới biết

| Sự thật | Giải thích |
|---|---|
| ⭐⭐ **"Active" là trạng thái XẤU** | Nghe như "đang hoạt động" nhưng thực ra là ⭐ **đang thử mở TCP mà chưa được**. Thấy `Active` = **đang hỏng**. Trạng thái tốt là `Established` |
| ⭐⭐ **Route trong BGP table ≠ route trong routing table** | BGP table giữ **mọi path học được**, nhưng chỉ path **best** (`>`) mới được đưa vào routing table. Và nó còn phải **qua được kiểm tra next-hop reachable** |
| ⭐ **Luôn dùng `soft reset`, đừng `clear ip bgp *`** | ⭐ `clear ip bgp *` **đánh sập toàn bộ peering** → mạng mất kết nối vài phút.<br>⭐ `clear ip bgp * soft in` chỉ **xin gửi lại route**, không ngắt phiên |

### 4.4 Những thứ này sẽ lớn lên thành gì

| Bạn vừa học | Sẽ thành | Ở module |
|---|---|---|
| BGP attribute (4 nhóm) | **13 bước path selection** · Weight/LocPref/MED/prepend | **Module-05B** |
| `network` statement | `aggregate-address` · community · filtering | **Module-05B** |
| eBGP đa ISP | NAT dual-ISP · IP SLA failover | **Module-06B** |
| AS-path chống loop | Kiểm soát traffic vào/ra bằng prepend | **Module-05B** |
| Peering ra ngoài | SD-WAN chọn đường theo ứng dụng | **Module-09 §6** |

### 4.5 Vẽ lại để nhớ

> **Bài tập 15 phút, trên giấy.**
>
> 1. Vẽ lại sơ đồ §4.1 **không nhìn tài liệu**
> 2. Ghi rõ chỗ nào là **eBGP**, chỗ nào là **iBGP**, chỗ nào là **IGP**, kèm **AD** của mỗi loại
> 3. Trả lời: *"Vì sao hai router Edge bắt buộc phải có iBGP giữa chúng?"*

<details>
<summary>Đáp án câu 3</summary>

Vì ⭐ **route học từ eBGP KHÔNG tự động lan sang router khác trong cùng AS**.

Edge-1 học route của ISP-A qua eBGP. Nếu không có iBGP giữa Edge-1 và Edge-2 thì
Edge-2 **hoàn toàn không biết** route đó tồn tại → traffic nào đi qua Edge-2 sẽ bị
đẩy sai hướng hoặc bị bỏ.

⭐ **Và đây cũng là gốc của quy tắc quan trọng:** *"iBGP không quảng bá lại route
học từ iBGP"* — nên nếu có **3 router iBGP trở lên**, chúng phải **full-mesh** với nhau
*(hoặc dùng route reflector — ngoài phạm vi ENCOR)*.

</details>

---

## 💡 4.6 Thực chiến đi làm

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

# 📎 PHỤ LỤC — TRA CỨU

> 🔴 **KHÔNG đọc phần này ở lần học đầu tiên.**
>
> | Khi nào | Mở mục nào |
> |---|---|
> | Đang lab mà lỗi | **Gỡ lỗi nhanh** (§7) — quy trình 4 bước cho BGP |
> | Quên lệnh | **Hộp lệnh** (§7.1) |
> | Tuần 20, ôn thi | **Bẫy đề** (§6) + **Quiz** (§8) |
> | Gặp từ lạ | **Thuật ngữ** (§9) |
> | Tự chấm | **Đúc kết** (§10) |

---

## 🎓 6. BẪY TRONG ĐỀ ENCOR

| # | Bẫy | Sự thật |
|:---:|---|---|
| 1 | 🔴 **`Active` là trạng thái tốt?** | ❌ **KHÔNG!**  `Active` = **TCP thất bại, đang thử lại**. `Established` mới là tốt |
| 2 | Phân biệt `Idle` vs `Active` | `Idle` = **không có route** tới neighbor (ping fail) · `Active` = **có route nhưng TCP 179 không lên** (ping OK, telnet 179 fail) |
| 3 | 6 neighbor state theo thứ tự | **Idle → Connect → (Active) → OpenSent → OpenConfirm → Established** |
| 4 | BGP dùng transport gì | **TCP port 179** |
| 5 | AD của eBGP / iBGP | **20 / 200** |
| 6 | Loại protocol | **Path Vector** (không phải distance vector / link-state) |
| 7 | Timer BGP | **Keepalive 60 s · Hold 180 s** |
| 8 | Hold time có phải khớp? | ❌ **KHÔNG** — 2 bên dùng  **giá trị NHỎ HƠN** (khác OSPF!) |
| 9 | 5 message type | **OPEN · UPDATE · KEEPALIVE · NOTIFICATION · ROUTE-REFRESH** |
| 10 | Message nào **đóng phiên** | **NOTIFICATION** |
| 11 | Trường nào trong OPEN phải khớp | **My AS** (khớp `remote-as` của peer) và **BGP ID unique**. Hold time **không** cần khớp |
| 12 | eBGP TTL mặc định | **1** → phải kề nhau. Peer qua loopback cần `ebgp-multihop` + `update-source` |
| 13 | Thiếu `update-source` khi peer qua loopback | Kẹt **`Active`** — peer từ chối vì source IP không khớp |
| 14 | `network` của BGP khác OSPF thế nào | BGP: **"quảng bá prefix NẾU có trong RIB, khớp CHÍNH XÁC prefix + mask"** · dùng **subnet mask** (không phải wildcard) |
| 15 | 🔴 `network 10.1.0.0 mask 255.255.0.0` mà RIB chỉ có `/24` | ❌ **KHÔNG quảng bá**, và  **không có log lỗi** |
| 16 | Cách quảng bá prefix không có trong RIB | `ip route <prefix> <mask> Null0` rồi `network` |
| 17 | eBGP có đổi next-hop? iBGP? | eBGP **đổi** thành IP của mình · iBGP  **KHÔNG đổi** → cần `next-hop-self` |
| 18 | eBGP có thêm ASN vào AS-path? iBGP? | eBGP **thêm** (vào **đầu**) · iBGP  **không thêm** |
| 19 | **iBGP split-horizon rule** | Route học từ **iBGP peer**  **KHÔNG quảng bá cho iBGP peer khác** → cần **full mesh** hoặc **Route Reflector** |
| 20 | Số phiên iBGP full mesh cho n router | **n(n-1)/2** |
| 21 | `*` và `>` trong `show ip bgp` | `*` = **valid** (next-hop reachable) · `>` = **best** (vào RIB) · `*>` = cả hai |
| 22 | `*` mà không có `>` nghĩa là gì | Valid nhưng **không best** — có path khác tốt hơn |
| 23 | Không có `*` nghĩa là gì | 🔴 **Không valid** — thường là **next-hop unreachable** |
| 24 | **`r`** trong `show ip bgp` | **RIB-failure** — BGP chọn best nhưng RIB có route **AD tốt hơn**. `show ip bgp rib-failure` |
| 25 | `Next Hop = 0.0.0.0` nghĩa là gì | Route do **CHÍNH router này** sinh ra |
| 26 | `Weight = 32768` nghĩa là gì | Route do **chính router này** sinh · `0` = học từ peer |
| 27 | Cột `Metric` trong `show ip bgp` là gì | Là **MED** |
| 28 | Đọc AS-path `65002 65003 i` | Đọc **từ phải sang trái**: xuất phát AS **65003**, qua AS **65002**. Độ dài = **2** |
| 29 | 3 Origin code + thứ tự ưu tiên | **`i` (IGP/`network`) < `e` (EGP) < `?` (incomplete/`redistribute`)** — `i` **tốt nhất** |
| 30 | Weight thuộc nhóm attribute nào | **KHÔNG phải attribute BGP** — là **Cisco-only**,  **chỉ local**, không gửi đi đâu |
| 31 | 4 nhóm attribute | **Well-known Mandatory** (AS-path, Next-hop, Origin) · **Well-known Discretionary** (LocPref, Atomic Aggregate) · **Optional Transitive** (Community, Aggregator) · **Optional Non-transitive** (MED) |
| 32 | MED thuộc nhóm nào, lan tới đâu | **Optional Non-transitive** — gửi **sang AS kề**,  **KHÔNG gửi tiếp** |
| 33 | Local Preference lan tới đâu | **Trong AS** (qua iBGP),  **KHÔNG** qua eBGP. Mặc định **100** |
| 34 | Attribute nào **CAO** tốt, nào **THẤP** tốt | **CAO tốt: Weight, Local Pref** · **THẤP tốt: AS-path length, MED, Origin, Router ID** |
| 35 | `Established` nhưng `PfxRcd = 0` | Thiếu `neighbor x activate` (khi dùng `no bgp default ipv4-unicast`) · peer không quảng bá · filter chặn hết |
| 36 | `soft in` vs `clear ip bgp <ip>` | `soft in` = dùng **route-refresh**, **không đóng phiên** · `clear ip bgp <ip>` = 🔴 **hard reset, đóng TCP** |
| 37 | Lệnh xem route **gửi cho** peer | `show ip bgp neighbors <ip> advertised-routes` |
| 38 | Lệnh xem route **nhận từ** peer (trước policy) | `show ip bgp neighbors <ip> received-routes` — ⚠️ cần `soft-reconfiguration inbound` |
| 39 | `maximum-prefix` vượt giới hạn thì sao | **Đóng phiên** (mặc định). Muốn chỉ cảnh báo → `warning-only` |
| 40 | `ttl-security` và `ebgp-multihop` | **Loại trừ nhau** — không dùng cùng lúc |

---

## 🐛 7. GỠ LỖI NHANH

### 7.1 Hộp lệnh vạn năng

```
! ═══ BẢNG 1: NEIGHBOR ═══
show ip bgp summary                              ! LỆNH ĐẦU TIÊN LUÔN
show ip bgp summary | begin Neighbor             ! chỉ phần bảng neighbor
show ip bgp neighbors                             ! chi tiết mọi neighbor
show ip bgp neighbors <ip>                        ! chi tiết 1 neighbor
show ip bgp neighbors <ip> | include Last reset|notification    ! LÝ DO RESET
show ip bgp neighbors <ip> | include Local host|Foreign host    ! source IP thật
show ip bgp neighbors <ip> | include state|up for|dropped
show ip bgp neighbors <ip> | include Address family|Route refresh

! ═══ BẢNG 2: BGP TABLE ═══
show ip bgp                                       ! toàn bộ BGP table
show ip bgp <prefix>                              ! MỌI path + LÝ DO best
show ip bgp <prefix> <mask>
show ip bgp neighbors <ip> routes                 ! route nhận từ peer (sau policy)
show ip bgp neighbors <ip> advertised-routes      ! route GỬI cho peer
show ip bgp neighbors <ip> received-routes        ! ⚠️ cần soft-reconfiguration inbound
show ip bgp rib-failure                           ! path 'r' và lý do
show ip bgp paths                                  ! danh sách AS-path
show ip bgp regexp ^$                             ! route sinh trong AS mình
show ip bgp regexp _65003_                        ! route đi qua AS 65003
show ip bgp regexp ^65002_                        ! route từ AS kề 65002

! ═══ BẢNG 3: ROUTING TABLE ═══
show ip route bgp
show ip route <prefix>                            ! AD 20 (eBGP) hay 200 (iBGP)?

! ═══ NỀN TẢNG (đừng bỏ) ═══
show ip route <neighbor-ip>                       ! có route tới neighbor?
ping <neighbor-ip>                                ! L3 thông?
telnet <neighbor-ip> 179                          ! TCP 179 thông?
show access-lists                                 ! ACL chặn 179?
show tcp brief                                     ! phiên TCP 179 đang mở?
show logging | include BGP|BADAUTH|MAXPFX|TCP     ! log nói thẳng nguyên nhân

! ═══ RESET ═══
clear ip bgp <ip> soft in                         ! route-refresh, KHÔNG downtime
clear ip bgp <ip> soft out
clear ip bgp <ip>                                 ! hard reset
clear ip bgp *                                    ! KHÔNG DÙNG TRÊN PRODUCTION

! ═══ DEBUG (⚠️ chỉ lab) ═══
debug ip bgp                                       ! sự kiện chung
debug ip bgp <ip>                                  ! 1 neighbor
debug ip bgp events
debug ip bgp updates                               ! ⚠️ RẤT nhiều output
debug ip tcp transactions                          ! xem TCP 179 lên/xuống
undebug all
```

### 7.2 Bảng lỗi: triệu chứng → nguyên nhân → cách sửa

| # | Triệu chứng | Nguyên nhân | Lệnh chẩn đoán | Cách sửa |
|:---:|---|---|---|---|
| 1 | **`Idle`**, `ping` neighbor **fail** | **Không có route** tới neighbor IP | `show ip route <neighbor-ip>` · `ping` | Sửa routing/interface |
| 2 | **`Idle`**, `ping` **OK** | Sai `remote-as` · password lệch · neighbor bị `shutdown` | `show ip bgp nei <ip> \| inc Last reset` · `show logging \| inc BGP\|BADAUTH` | Sửa theo lý do trong log |
| 3 | 🔴 **`Active`**, `ping` **OK** | **TCP 179 bị chặn** · thiếu `update-source` · sai IP neighbor | `telnet <neighbor-ip> 179` · `show access-lists` · `show ip bgp nei <ip> \| inc Local host` | Mở ACL cho TCP 179 · thêm `update-source` |
| 4 | `Idle (Admin)` | Neighbor bị `neighbor x shutdown` | `show run \| sec router bgp` | `no neighbor x shutdown` |
| 5 | Kẹt `OpenSent` | Sai ASN · Router ID trùng | `show ip bgp nei <ip> \| inc Last reset` → `bad AS number` | Sửa `remote-as` / `bgp router-id` |
| 6 | Kẹt `OpenConfirm` | Password/auth lệch · capability không tương thích | `show logging \| inc BADAUTH` | Khớp password |
| 7 | `Established` nhưng **`PfxRcd = 0`** | Thiếu `activate` · peer chưa `network` gì · filter chặn hết | `show ip bgp nei <ip> \| inc Address family` · `show ip bgp nei <ip> advertised-routes` **trên peer** | `neighbor x activate` · thêm `network` · rà filter |
| 8 | 🔴 Prefix **không xuất hiện** trong `show ip bgp`, **không log** | **`network` không khớp prefix+mask trong RIB** | `show ip route <prefix> <mask>` → `% Subnet not in table` | Dùng đúng mask · hoặc `ip route <prefix> <mask> Null0` |
| 9 | Path có `*` nhưng **không có `>`** | Có path khác tốt hơn (đúng) — hoặc  **next-hop unreachable** | `show ip bgp <prefix>` → đọc `valid`/`inaccessible` · `show ip route <next-hop>` | Thêm route tới next-hop · `next-hop-self` (iBGP) |
| 10 | Path **không có `*`** | 🔴 **Next-hop unreachable** | `show ip bgp <prefix>` · `show ip route <next-hop>` | `next-hop-self` · quảng bá subnet vào IGP |
| 11 | **`r>`** RIB-failure | RIB có route **AD tốt hơn** (static/IGP) | `show ip bgp rib-failure` · `show ip route <prefix>` | Xóa route AD thấp · hoặc đổi AD BGP (`distance bgp`) |
| 12 | Phiên **flap liên tục** (`dropped` cao) | Link nhấp nháy · `maximum-prefix` vượt · CPU cao · MTU/MSS | `show ip bgp nei <ip> \| inc dropped\|Last reset` · `show logging` · `show interfaces \| inc flapped` | Sửa link · tăng `maximum-prefix` · bật BFD |
| 13 | Phiên đóng, log `MAXPFXEXCEED` | Peer gửi quá `maximum-prefix` | `show logging \| inc MAXPFX` | Tăng giới hạn · hoặc lọc bớt prefix nhận · hoặc `warning-only` |
| 14 | Log `%TCP-6-BADAUTH` | **BGP password lệch** | `show logging \| inc BADAUTH` | Khớp `neighbor x password` |
| 15 | `InQ`/`OutQ` khác 0 lâu | CPU cao · bảng BGP quá lớn · phiên nghẽn | `show processes cpu sorted` (M01) · `show ip bgp summary` | Giảm prefix nhận · nâng cấp thiết bị |
| 16 | Đổi route-map/filter mà **không có tác dụng** | Chưa reset phiên | — | `clear ip bgp <ip> soft in` (inbound) / `soft out` (outbound) |
| 17 | `received-routes` báo lỗi/không có gì | Chưa bật `soft-reconfiguration inbound` | `show run \| sec router bgp` | `neighbor x soft-reconfiguration inbound` (⚠️ tốn RAM) |
| 18 | Peer qua loopback không lên (`Active`) | Thiếu `ebgp-multihop` **hoặc** `update-source` **hoặc** route tới loopback peer | `show ip bgp nei <ip> \| inc Local host` · `show ip route <peer-loopback>` | Thêm cả **3** thứ |
| 19 | Route của AS mình **quay lại** | Ai đó bật `allowas-in` | `show run \| inc allowas-in` | Bỏ `allowas-in` |
| 20 | Nhận full Internet table ngoài ý muốn | Không có filter inbound + ISP gửi full table | `show ip bgp summary` (PfxRcd rất lớn) | `maximum-prefix` · prefix-list inbound (Module-05B) · xin ISP gửi default-only |

### 7.3  Quy trình troubleshoot BGP — 4 bước

```
0. LỆNH ĐẦU TIÊN LUÔN
   show ip bgp summary
   → đọc cột State/PfxRcd
        ↓
1. PHIÊN CHƯA ESTABLISHED?
   ├─ Idle   → ping <neighbor-ip>
   │           ├─ FAIL → vấn đề ROUTING (không có route tới neighbor)
   │           └─ OK   → show ip bgp nei <ip> | inc Last reset
   │                     → "bad AS number"? password? shutdown?
   │
   ├─ Active → telnet <neighbor-ip> 179
   │           ├─ FAIL → TCP 179 BỊ CHẶN (ACL/firewall)
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
   ├─ Không có `*`  → NEXT-HOP UNREACHABLE → show ip route <next-hop>
   ├─ Có `*` không `>` → path khác best hơn (đọc lý do trong output)
   ├─ Có `r`        → RIB-FAILURE → show ip bgp rib-failure
   └─ Có `*>`       → ✅ vào RIB → show ip route <prefix>
        ↓
4. PREFIX MÌNH MUỐN QUẢNG BÁ KHÔNG XUẤT HIỆN?
   show ip route <prefix> <mask>
   ├─ "% Subnet not in table" → network statement KHÔNG KHỚP
   │                             → dùng đúng mask, hoặc ip route ... Null0
   └─ Có trong RIB → kiểm tra filter outbound · show ip bgp nei <peer> advertised-routes
```

> **Hai lệnh phân biệt nhanh nhất:**
> **`ping <neighbor>`** → phân biệt "vấn đề routing" (Idle) vs "vấn đề khác"
> **`telnet <neighbor> 179`** → phân biệt "TCP bị chặn" (Active) vs "vấn đề BGP"

---

## 📝 8. QUIZ TỰ KIỂM TRA

**Câu 1.** Neighbor BGP ở state `Active`. Đây là trạng thái tốt hay xấu? Nêu 3 nguyên nhân
và lệnh chẩn đoán từng cái.

<details><summary>Xem đáp án</summary>

🔴 **Trạng thái XẤU.** `Active` = **"TCP thất bại, tôi đang CHỦ ĐỘNG thử kết nối lại"**.
`Established` mới là trạng thái tốt.

 **Đây là bẫy ngôn ngữ** — "active" trong tiếng Anh thông thường nghĩa là tốt, trong BGP thì ngược lại.

**3 nguyên nhân + lệnh chẩn đoán:**

| # | Nguyên nhân | Lệnh chẩn đoán |
|:---:|---|---|
| 1 | **TCP 179 bị chặn** (ACL/firewall) | `telnet <neighbor-ip> 179` → timeout/refused · `show access-lists` (xem counter) |
| 2 | **Thiếu `update-source`** khi peer qua loopback | `show ip bgp neighbors <ip> \| include Local host` → source IP không khớp `neighbor` peer khai |
| 3 | **Sai IP neighbor** · route bất đối xứng | `show run \| sec router bgp` · `show ip route <neighbor-ip>` |

 **Phân biệt `Idle` vs `Active` — quan trọng nhất:**

| | `Idle` | `Active` |
|---|---|---|
| `ping <neighbor>` | ❌ **FAIL** | ✅ **OK** |
| Nghĩa | **Không có route** tới neighbor | Có route nhưng **TCP không lên** |
| Kiểm tra | `show ip route <neighbor-ip>` | `telnet <neighbor-ip> 179` |
</details>

---

**Câu 2.** So sánh eBGP và iBGP theo 6 tiêu chí: AD, TTL, AS-path, Next-hop, Local Pref,
split-horizon rule.

<details><summary>Xem đáp án</summary>

| Tiêu chí | **eBGP** | **iBGP** |
|---|---|---|
| **AD** | **20** | **200** |
| **TTL** gói BGP | **1** (phải kề nhau) | **255** (đi nhiều hop được) |
| **AS-path** khi quảng bá | **THÊM ASN của mình vào ĐẦU** | **KHÔNG thay đổi** |
| **Next-hop** khi quảng bá | **ĐỔI thành IP của mình** | **KHÔNG đổi** → cần `next-hop-self` |
| **Local Preference** | **KHÔNG gửi** qua eBGP | **Gửi** trong AS |
| **Split-horizon rule** | Không áp dụng | **Route học từ iBGP KHÔNG quảng bá cho iBGP peer khác** → cần **full mesh** hoặc **Route Reflector** |

 **Vì sao iBGP cần split-horizon rule:** iBGP **không thêm ASN vào AS-path** (cùng AS)
→ **không có cơ chế chống loop** → nếu cho quảng bá lại thì route chạy vòng vô tận trong AS.

 **Vì sao eBGP TTL = 1:** eBGP giả định peer **kề nhau trực tiếp** (1 hop).
Muốn peer xa hơn → `ebgp-multihop <ttl>` **+ `update-source`**.
</details>

---

**Câu 3.** Bạn cấu hình `network 10.1.0.0 mask 255.255.0.0` nhưng prefix không xuất hiện trong
`show ip bgp`, và không có log lỗi nào. Nguyên nhân? 2 cách sửa?

<details><summary>Xem đáp án</summary>

 **BGP `network` statement yêu cầu prefix KHỚP CHÍNH XÁC (cả prefix VÀ mask) trong bảng route.**

RIB chỉ có `10.1.1.0/24`, `10.1.2.0/24` — **không có** `10.1.0.0/16` → `network` không khớp
→  **BGP không quảng bá, và không có thông báo lỗi**.

**Chẩn đoán:**
```
show ip route 10.1.0.0 255.255.0.0
! % Subnet not in table                        ← đây là câu trả lời
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

 **Cách sửa 2 — tạo static route Null0 (kỹ thuật chuẩn công nghiệp):**
```
ip route 10.1.0.0 255.255.0.0 Null0
router bgp 65001
 network 10.1.0.0 mask 255.255.0.0
```
Giờ RIB **có** `/16` → `network` khớp → quảng bá được.
Traffic tới subnet không tồn tại trong `/16` sẽ **drop tại Null0** —
giống discard route của OSPF summarization (Module-04B §2.3).

 **Khác biệt với OSPF:** OSPF `network 10.1.0.0 0.0.255.255 area 0` nghĩa là
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
| **`*`** | **valid** — path hợp lệ, next-hop **reachable** |
| **`>`** | **best** — path này được chọn,  **đưa xuống RIB** |
| `10.3.3.0/24` | Prefix (NLRI) |
| `10.0.12.2` | **Next-hop** — IP để tới đích |
| *(Metric trống)* | **MED không được đặt** |
| *(LocPrf trống)* | Local Preference = **100** (mặc định), hoặc không áp dụng vì là eBGP |
| **`0`** | **Weight = 0** → route **học từ peer** (nếu là 32768 thì do chính router sinh) |
| **`65002 65003`** | **AS-path** — đọc **từ PHẢI sang TRÁI**: route xuất phát từ AS **65003**, đi qua AS **65002**, rồi tới tôi.  **Độ dài = 2** |
| **`i`** (ký tự cuối) | **Origin code = IGP** → route được quảng bá bằng **`network` statement** (tốt nhất trong 3 loại) |

 **3 Origin code:** `i` (IGP/`network`) **<** `e` (EGP) **<** `?` (incomplete/`redistribute`)
— `i` **được ưu tiên nhất**.

 **3 giá trị Weight phải nhớ:** `32768` = route **của chính mình** · `0` = **học từ peer** ·
khác = đã đặt tay.
</details>

---

**Câu 5.** Điền bảng 4 nhóm attribute và ví dụ. Weight thuộc nhóm nào?

<details><summary>Xem đáp án</summary>

| Nhóm | Định nghĩa | Ví dụ |
|---|---|---|
| **Well-known Mandatory** | Mọi BGP **phải hiểu**, **phải có** trong mọi UPDATE | **AS-path · Next-hop · Origin** |
| **Well-known Discretionary** | Mọi BGP phải hiểu, **không bắt buộc có** | **Local Preference** · Atomic Aggregate |
| **Optional Transitive** | Có thể không hiểu, nhưng  **vẫn chuyển tiếp** | **Community** · Aggregator |
| **Optional Non-transitive** | Có thể không hiểu,  **KHÔNG chuyển tiếp** | **MED** · Originator-ID · Cluster-list |

 **Weight KHÔNG thuộc nhóm nào — nó KHÔNG PHẢI attribute BGP.**

| Weight | Chi tiết |
|---|---|
| Bản chất | **Cisco proprietary** — không có trong RFC 4271 |
| Phạm vi | **CHỈ local trên router đó** —  **không bao giờ được gửi** cho bất kỳ peer nào |
| Giá trị | 0–65535. `32768` = route của chính mình · `0` = học từ peer |
| Tốt nhất | Càng **CAO** càng tốt |
| Vị trí trong path selection | **BƯỚC 1** (Module-05B) |

 **Bảng "CAO tốt vs THẤP tốt":**

| Càng **CAO** càng tốt | Càng **THẤP** càng tốt |
|---|---|
| **Weight** | **AS-path length** |
| **Local Preference** | **MED** · Origin (i<e<?) · Router ID · IGP metric |

🧠 *Hai cái đầu (Weight, LocPref) — CAO thắng. Còn lại — THẤP thắng.*
</details>

---

**Câu 6.** BGP neighbor `Established` nhưng `State/PfxRcd` = `0`. Nêu 3 nguyên nhân và cách kiểm tra.

<details><summary>Xem đáp án</summary>

| # | Nguyên nhân | Cách kiểm tra |
|:---:|---|---|
| 1 | **Thiếu `neighbor x activate`** (khi dùng `no bgp default ipv4-unicast`) | `show ip bgp neighbors <ip> \| include Address family` → phải thấy `Address family IPv4 Unicast: advertised and received` |
| 2 | **Peer không quảng bá gì** (thiếu `network` / `network` không khớp mask) | **TRÊN PEER**: `show ip bgp neighbors <my-ip> advertised-routes` · `show ip bgp` |
| 3 | **Filter inbound chặn hết** (prefix-list/route-map thiếu catch-all) | `show run \| sec router bgp` · `show ip prefix-list detail` (xem hit count) · `show route-map` (xem counter) |

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
ip prefix-list PL-IN seq 100 permit 0.0.0.0/0 le 32     ! catch-all
! rồi: clear ip bgp 10.0.12.2 soft in
```

 **Lưu ý:** sau khi đổi filter, phải `clear ip bgp <ip> soft in` — nếu không, filter mới
**không được áp** cho route đã nhận trước đó.
</details>

---

**Câu 7.** Trong `show ip bgp` bạn thấy `r>` trước một prefix. Nghĩa là gì? Có phải lỗi không?
Rủi ro là gì?

<details><summary>Xem đáp án</summary>

 **`r` = RIB-failure.** BGP đã chọn path này là **best**, nhưng  **RIB từ chối cài nó**
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

**Có phải lỗi không:**  **Không hẳn** — nó là **thông báo trạng thái**, có thể hoàn toàn đúng ý bạn
(bạn **muốn** static thắng BGP).

⚠️ **Nhưng rủi ro thật:**

 **BGP VẪN quảng bá path này cho peer** — dù nó **không thật sự được dùng để forward**.
Nghĩa là:
- Bạn nói với peer *"gửi traffic `10.2.2.0/24` cho tôi, tôi biết đường"*
- Nhưng thực tế bạn forward theo **static route**, có thể đi hướng **khác hoàn toàn**
- →  **Suboptimal routing**, hoặc **black hole** nếu static route trỏ sai/Null0

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

 **Best practice:** chạy `show ip bgp rib-failure` khi nhận bàn giao mạng BGP —
nó thường phơi ra những static route "tạm" mà ai đó để lại và quên xóa.
</details>

---

**Câu 8.** Bạn muốn peer eBGP giữa 2 loopback (`1.1.1.1` ↔ `3.3.3.3`), 2 router cách nhau 2 hop.
Cần những gì? Thiếu mỗi cái thì kẹt state nào?

<details><summary>Xem đáp án</summary>

 **Cần 3 thứ trên MỖI router:**

```
! Trên R1 (AS 65001)
ip route 3.3.3.3 255.255.255.255 10.0.12.2          ! 1. Route tới loopback peer
!
router bgp 65001
 neighbor 3.3.3.3 remote-as 65003
 neighbor 3.3.3.3 ebgp-multihop 2                    ! 2. Tăng TTL (mặc định eBGP = 1)
 neighbor 3.3.3.3 update-source Loopback0            ! 3. Source = loopback

! Trên R3 (AS 65003) — đối xứng
ip route 1.1.1.1 255.255.255.255 10.0.23.1
router bgp 65003
 neighbor 1.1.1.1 remote-as 65001
 neighbor 1.1.1.1 ebgp-multihop 2
 neighbor 1.1.1.1 update-source Loopback0
```

 **Thiếu mỗi cái thì sao:**

| Thiếu | State | Vì sao | Lệnh chẩn đoán |
|---|:---:|---|---|
| **Route tới loopback peer** | **`Idle`** | Không mở được TCP tới `3.3.3.3` | `show ip route 3.3.3.3` · `ping 3.3.3.3` |
| **`ebgp-multihop`** | **`Active`**/`Idle` | TTL = 1 → gói chết sau hop đầu (peer cách 2 hop) | `debug ip tcp transactions` |
| **`update-source`** | **`Active`** | Source IP là IP interface vật lý (`10.0.12.1`), nhưng R3 khai `neighbor 1.1.1.1` →  **R3 TỪ CHỐI** connection | `show ip bgp neighbors 3.3.3.3 \| include Local host` → thấy source **sai** |

⚠️ **Lưu ý:** `ttl-security hops` và `ebgp-multihop`  **loại trừ nhau** — không dùng cùng lúc.

 **Thực tế:** eBGP với ISP **hầu như luôn** kề nhau trực tiếp → **không cần** multihop.
Loopback peering chủ yếu dùng cho **iBGP** (để phiên không phụ thuộc 1 interface vật lý cụ thể).
</details>

---

**Câu 9.** Phân biệt `clear ip bgp 10.0.12.2 soft in` và `clear ip bgp 10.0.12.2`.
Khi nào dùng cái nào?

<details><summary>Xem đáp án</summary>

| | **`clear ip bgp <ip> soft in`** | 🔴 **`clear ip bgp <ip>`** |
|---|---|---|
| Cơ chế | Dùng **ROUTE-REFRESH message** | Đóng **phiên TCP** rồi mở lại |
| Phiên TCP | **GIỮ NGUYÊN** | 🔴 **Đóng và mở lại** |
| Downtime | **Không có** | 🔴 **Có** — mất toàn bộ route của peer đó trong lúc reset |
| Dùng khi | Đổi **inbound** policy (prefix-list/route-map inbound) | Chỉ khi bắt buộc (đổi ASN, đổi Router ID) |

**Các biến thể:**
```
clear ip bgp <ip> soft in            ! đổi INBOUND policy → xin peer gửi lại
clear ip bgp <ip> soft out           ! đổi OUTBOUND policy → gửi lại cho peer
clear ip bgp <ip> soft               ! cả hai chiều
clear ip bgp * soft                  ! soft cho mọi peer
!
clear ip bgp <ip>                    ! hard reset 1 peer
clear ip bgp *                       ! hard reset MỌI peer — KHÔNG BAO GIỜ trên production
```

**Điều kiện để `soft in` hoạt động:** peer phải hỗ trợ **route-refresh capability**:
```
show ip bgp neighbors 10.0.12.2 | include Route refresh
!  Route refresh: advertised and received(new)        ← ✅ OK
```

 **Nếu peer KHÔNG hỗ trợ route-refresh** (thiết bị rất cổ) → phải lưu bản copy trong RAM:
```
router bgp 65001
 neighbor 10.0.12.2 soft-reconfiguration inbound     ! ⚠️ tốn RAM (2 bản copy)
```
Bù lại, khi bật nó thì dùng được:
```
show ip bgp neighbors 10.0.12.2 received-routes       ! Adj-RIB-In thật (trước policy)
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
| **1** | **Neighbor KHÔNG tự tìm nhau — phải khai báo tay** | OSPF/EIGRP gửi Hello **multicast** trên link → tự phát hiện neighbor. BGP dùng TCP unicast →  **bắt buộc** `neighbor <ip> remote-as <asn>` |
| **2** | **Neighbor KHÔNG cần kề nhau** | Chỉ cần **IP reachable**. Đây là nền tảng cho **iBGP peer qua loopback** và **eBGP multihop**. ⚠️ Nhưng eBGP mặc định TTL=1 nên vẫn phải kề nhau, trừ khi `ebgp-multihop` |
| **3** | **BGP không tự lo reliability — để TCP lo** | TCP xử lý retransmit, ordering, windowing, flow control. Nên BGP **không cần** cơ chế ACK riêng như OSPF (LSAck).  Và vì TCP tự phân đoạn, BGP chở được **hàng triệu prefix** không bị giới hạn MTU |

**Hệ quả phụ (hay hỏi):**

| Hệ quả | Chi tiết |
|---|---|
| **Cần IGP trước** (với iBGP) | TCP phải tới được peer → cần route. Đây là lý do iBGP luôn chạy **trên nền một IGP** |
| **TCP 179 có thể bị firewall chặn** | → gây state **`Active`**. Lệnh test: `telnet <peer> 179` |
| **Có thể bảo mật bằng MD5 của TCP** | `neighbor x password` — dùng TCP MD5 signature option |
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
| **Path Vector** | Vector đường đi | Quan tâm **"đã đi qua AS nào"**, không phải "xa bao nhiêu" |
| **AS** (Autonomous System) | Hệ tự trị | Tập router dưới cùng một chính sách quản trị |
| **ASN** | Số hiệu AS | 16-bit (1–65535) hoặc 32-bit. Private: `64512–65534` |
| **eBGP** (External BGP) | BGP ngoại | Giữa **AS khác nhau**. AD **20**, TTL **1** |
| **iBGP** (Internal BGP) | BGP nội | Trong **cùng AS**. AD **200**, TTL 255 |
| **Split-horizon rule (iBGP)** | Quy tắc chân trời chia | Route học từ iBGP **không** quảng bá cho iBGP peer khác |
| **Full mesh** | Lưới đầy đủ | Mọi router iBGP peer với nhau. **n(n-1)/2** phiên |
| **Route Reflector (RR)** | Bộ phản chiếu route | 🟡 Phá split-horizon rule → khỏi cần full mesh |
| **Confederation** | Liên hợp | 🟡 Chia AS lớn thành sub-AS |
| **`next-hop-self`** | Tự làm next-hop | Router biên đổi next-hop thành IP của mình khi quảng bá cho iBGP peer |
| **Peer / Neighbor** | Đối tác / Láng giềng | Phải **khai báo tay** — BGP không tự tìm |
| **`Established`** | Đã thành lập | ✅ **Trạng thái TỐT** |
| **`Active`** | "Chủ động" | 🔴 **Trạng thái XẤU** — TCP thất bại, đang thử lại |
| **`Idle`** | Rảnh | ⚠️ Không có route tới neighbor |
| **`Connect`** | Đang kết nối | Đang mở TCP |
| **`OpenSent` / `OpenConfirm`** | Đã gửi/xác nhận OPEN | Đang đàm phán |
| **OPEN message** | Bản tin mở | Đàm phán ASN, Router ID, hold time, capabilities |
| **UPDATE message** | Bản tin cập nhật | Quảng bá (NLRI + attribute) hoặc rút route |
| **KEEPALIVE** | Duy trì | Mỗi 60 s |
| **NOTIFICATION** | Thông báo lỗi | **Báo lỗi rồi ĐÓNG phiên**. Đọc lý do reset ở đây |
| **ROUTE-REFRESH** | Làm mới route | Xin gửi lại route **không cần reset phiên** |
| **NLRI** (Network Layer Reachability Info) | Thông tin khả năng tới được | = prefix trong UPDATE |
| **Withdrawn routes** | Route bị rút | Prefix không còn hợp lệ |
| **Hold time** | Thời gian giữ | 180 s.  **Không cần khớp** — dùng giá trị nhỏ hơn |
| **Adj-RIB-In / Out** | RIB kề vào / ra | Route nhận từ / gửi cho mỗi neighbor |
| **`*` valid** | Hợp lệ | Next-hop **reachable** |
| **`>` best** | Tốt nhất | Path được chọn, đưa xuống RIB |
| **`r` RIB-failure** | Thất bại cài RIB | BGP chọn best nhưng RIB có route **AD tốt hơn** |
| **`s` suppressed** | Bị đè | Bị `aggregate-address` gộp (Module-05B) |
| **`d` damped** | Bị dập | Route flap damping |
| **AS-path** | Đường AS | Chống loop + chọn đường. eBGP **thêm ASN vào đầu**. Đọc **phải→trái** |
| **Origin** | Nguồn gốc | `i` (IGP/`network`) **<** `e` (EGP) **<** `?` (incomplete/`redistribute`) |
| **Weight** | Trọng số | **Cisco-only, KHÔNG phải attribute BGP**,  **chỉ local**. `32768` = của mình · `0` = học từ peer. **CAO** tốt |
| **Local Preference** | Ưu tiên cục bộ | Trong AS, mặc định **100**. **CAO** tốt. Chọn đường **RA** khỏi AS |
| **MED** (Multi-Exit Discriminator) | Phân biệt đa lối ra | **Optional Non-transitive** — sang AS kề, **không gửi tiếp**. **THẤP** tốt. Gợi ý điểm **VÀO** AS mình |
| **Next-hop** | Chặng kế | eBGP đổi · iBGP không đổi |
| **Community** | Cộng đồng | **Optional Transitive** — nhãn nhóm route (Module-05B) |
| **Atomic Aggregate** | Gộp nguyên tử | Cảnh báo route đã gộp, mất chi tiết AS-path |
| **Aggregator** | Bộ gộp | ASN + Router ID của router đã gộp |
| **Well-known Mandatory** | Nổi tiếng bắt buộc | AS-path · Next-hop · Origin |
| **Well-known Discretionary** | Nổi tiếng tùy chọn | Local Pref · Atomic Aggregate |
| **Optional Transitive** | Tùy chọn chuyển tiếp | Community · Aggregator — **vẫn chuyển tiếp** dù không hiểu |
| **Optional Non-transitive** | Tùy chọn không chuyển tiếp | MED · Originator-ID — **không chuyển tiếp** |
| **`ebgp-multihop`** | eBGP nhiều hop | Tăng TTL (mặc định eBGP TTL = **1**) |
| **`update-source`** | Nguồn cập nhật | Interface làm source IP. Thiếu = kẹt **`Active`** |
| **`activate`** | Kích hoạt | Bắt buộc khi dùng `no bgp default ipv4-unicast`. Thiếu = **`PfxRcd = 0`** |
| **`maximum-prefix`** | Số prefix tối đa | Chống **route leak** làm router hết RAM. **BẮT BUỘC** với ISP |
| **Route leak** | Rò rỉ route | Peer vô tình quảng bá quá nhiều prefix |
| **`ttl-security hops`** (GTSM) | Bảo mật TTL | Chỉ nhận gói TTL ≥ 255−n. ⚠️ Loại trừ với `ebgp-multihop` |
| **Soft reset** | Reset mềm | Dùng route-refresh, **không đóng phiên TCP**, không downtime |
| 🔴 **Hard reset** | Reset cứng | 🔴 `clear ip bgp <ip>` — đóng TCP, **gây downtime** |
| **`soft-reconfiguration inbound`** | Cấu hình lại mềm chiều vào | Lưu bản copy route nhận (⚠️ tốn RAM). Cần cho `received-routes` |
| **`fall-over`** | Xuống ngay | Phiên xuống ngay khi mất route tới neighbor (không chờ hold 180 s) |
| **`allowas-in`** | Cho phép AS mình | ⚠️ Cho phép nhận route có ASN của mình trong AS-path. Dùng sai = mở đường loop |
| **BFD** (Bidirectional Forwarding Detection) | Phát hiện chuyển tiếp 2 chiều | Phát hiện lỗi ~900 ms thay vì 180 s |

---

## 🎯 10. ĐÚC KẾT MODULE-05A

**3 điều rút ra:**

1.  **`Established` là tốt, `Active` là XẤU.** Và hai lệnh phân biệt nhanh nhất:
   **`ping <neighbor>`** (fail → `Idle`, vấn đề routing) và **`telnet <neighbor> 179`**
   (fail → `Active`, TCP 179 bị chặn). Hai lệnh này thay thế được nửa giờ đoán mò.

2.  **BGP `network` statement khác OSPF hoàn toàn:** nó nói *"quảng bá prefix này **NẾU** nó có trong RIB,
   **khớp CHÍNH XÁC** prefix + mask"* — và nếu không khớp thì  **im lặng, không có log lỗi**.
   Cách vượt qua: `ip route <prefix> <mask> Null0` rồi `network`.

3.  **`show ip bgp <prefix>` là lệnh troubleshoot số 1 của BGP.** BGP **giữ lại mọi path**
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
| 4 | Phân biệt `Idle` vs `Active` — 2 lệnh phân biệt nhanh nhất? | ☐ |
| 5 | 5 message type + message nào đóng phiên? | ☐ |
| 6 | Trường nào trong OPEN phải khớp? Hold time có phải khớp? | ☐ |
| 7 | Timer BGP mặc định? | ☐ |
| 8 | eBGP vs iBGP theo 6 tiêu chí (AD, TTL, AS-path, Next-hop, LocPref, split-horizon) | ☐ |
| 9 | Vì sao iBGP cần split-horizon rule? Hệ quả? 2 giải pháp? | ☐ |
| 10 | `next-hop-self` giải quyết vấn đề gì? | ☐ |
| 11 | 3 bảng của BGP + tên 3 sub-table | ☐ |
| 12 | BGP `network` khác OSPF `network` thế nào? 2 cách quảng bá prefix không có trong RIB? | ☐ |
| 13 | Đọc được `*`, `>`, `*>`, `r`, `s`, `i` trong `show ip bgp` | ☐ |
| 14 | `Next Hop = 0.0.0.0` và `Weight = 32768` nghĩa là gì? | ☐ |
| 15 | Đọc AS-path `65002 65003 i` — hướng đọc, độ dài, origin | ☐ |
| 16 | 3 Origin code + thứ tự ưu tiên | ☐ |
| 17 | 4 nhóm attribute + ví dụ. Weight thuộc nhóm nào? | ☐ |
| 18 | Attribute nào CAO tốt, nào THẤP tốt? | ☐ |
| 19 | MED và Local Pref lan tới đâu? | ☐ |
| 20 | `Established` nhưng `PfxRcd = 0` — 3 nguyên nhân? | ☐ |
| 21 | `r` RIB-failure là gì? Rủi ro? | ☐ |
| 22 | Peer qua loopback cần 3 thứ gì? Thiếu mỗi cái kẹt state nào? | ☐ |
| 23 | `soft in` vs `clear ip bgp <ip>` — khi nào dùng cái nào? | ☐ |
| 24 | `maximum-prefix` chống gì? Vượt giới hạn thì sao? | ☐ |

**Phần B — Lab:**

| # | Yêu cầu | ✅ |
|:---:|---|:---:|
| 1 | Dựng 4 router / 4 AS, eBGP peering đầy đủ, mọi phiên `Established` | ☐ |
| 2 | Đọc và giải thích **từng cột** của `show ip bgp summary` | ☐ |
| 3 | Đọc và giải thích **từng cột** của `show ip bgp` (kể cả `*`, `>`, Weight, Path, Origin) | ☐ |
| 4 | Dùng `show ip bgp <prefix>` chỉ ra path, next-hop, `valid/external/best` | ☐ |
| 5 | Đọc `show ip bgp neighbors <ip>`: `external link`, timer đã đàm phán, `Prefixes Current`, `Local host` | ☐ |
| 6 | Verify `show ip route bgp` có `B` và `[20/0]`, ping/traceroute full-mesh | ☐ |
| 7 | **Chứng minh AS-path chống loop**: `advertised-routes` trên R2 **không có** prefix của AS 65003 | ☐ |
| 8 | 🔴 Tái hiện **sai `remote-as`** → chẩn đoán bằng `Last reset` → thấy `bad AS number` | ☐ |
| 9 | Tái hiện **không có route tới neighbor** → `Idle`, ping fail | ☐ |
| 10 | Tái hiện **ACL chặn TCP 179** → `Active`, **ping OK** nhưng `telnet 179` fail | ☐ |
| 11 | Tái hiện **thiếu `activate`** → `Established` nhưng `PfxRcd = 0` | ☐ |
| 12 | Tái hiện **`network` không khớp mask** → prefix không xuất hiện, **không log** → sửa bằng Null0 | ☐ |
| 13 | Cấu hình **peer qua loopback** (`ebgp-multihop` + `update-source` + static route) | ☐ |
| 14 | Tái hiện **thiếu `update-source`** → `Active` → chẩn đoán bằng `Local host` | ☐ |
| 15 | Tái hiện **password lệch** → log `BADAUTH` | ☐ |
| 16 | Tái hiện **RIB-failure** (`r>`) bằng static AD 1 → `show ip bgp rib-failure` | ☐ |
| 17 | Bật `password` + `ttl-security` + `maximum-prefix`, test vượt giới hạn → log `MAXPFXEXCEED` | ☐ |
| 18 | Phân biệt thực tế `clear ip bgp x soft in` vs `clear ip bgp x` (quan sát `Up/Down` reset hay không) | ☐ |
| 19 | Dùng `show ip bgp regexp ^$` và `_65003_` để lọc route theo AS-path | ☐ |
| 20 | Điền đủ **bảng 8 lỗi** ở §4 bước 5 (triệu chứng ↔ lệnh chẩn đoán nhanh nhất) | ☐ |
| 21 | Cố ý phá 1 thứ, tự tìm ra bằng **quy trình 4 bước §7.3** trong 10 phút | ☐ |

> ⚠️ **Giữ nguyên lab này** — Module-05B dùng chính topology 4 AS này để thao tác
> Weight / Local Pref / AS-path prepend / MED. Nhớ **Export CFG** trước khi đóng lab (Module-00 §8.3).

---

## 🔗 11. TÀI LIỆU CHO MODULE NÀY

| Nguồn | Cụ thể |
|---|---|
| **Sách OCG 350-401** | Chương **BGP** đầu tiên — đọc kỹ phần neighbor states, message types, `network` statement, attribute classification |
| **Cisco doc**  | *IP Routing: BGP Configuration Guide* → *Configuring a Basic BGP Network* |
| **Cisco doc**  | ***BGP Case Studies*** — tài liệu kinh điển của Cisco, giải thích bằng ví dụ thực tế. Search: `cisco bgp case studies` |
| **Cisco doc**  | *Troubleshooting BGP* — quy trình chuẩn cho `Idle`/`Active` |
| **Cisco doc** | *BGP Neighbor States* · *Understanding and Configuring the `network` Command in BGP* |
| **Cisco doc** | *BGP Support for TTL Security Check* (GTSM) · *BGP Maximum-Prefix* |
| **RFC 4271** | BGP-4 — đọc **Section 8 (Finite State Machine)** và **Section 5 (Path Attributes)** |
| **Cisco Live**  | Search `Cisco Live BGP best practices enterprise` · `Cisco Live BGP troubleshooting` |
| **NetworkLessons**  | Loạt bài *BGP Neighbor Adjacency*, *BGP Attributes*, *eBGP Multihop* — nhiều bài free |
| **Video** | CBT Nuggets ENCOR — module BGP · Keith Barker: search `Keith Barker BGP neighbor states` |
| **Wireshark** | Filter `bgp` → xem OPEN (ASN, hold time, capabilities), UPDATE (NLRI + attribute), NOTIFICATION.  Bắt trên link R1↔R2 lúc `clear ip bgp` để thấy trọn quá trình |
| **Forum** | https://community.cisco.com — search `bgp stuck active`, `bgp established 0 prefixes received`, `bgp network statement not advertised` |

---

**➡️ Tiếp theo:** [Module-05B — BGP: Path Selection & Filtering](Module-05B-BGP-Path-Selection-va-Filtering.md)
*( **13 bước best path selection** · Weight · Local Pref · AS-path prepend · MED ·
Community · prefix-list / AS-path ACL / route-map · `aggregate-address` — **Tuần 10**)*
