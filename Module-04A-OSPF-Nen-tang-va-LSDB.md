# Module-04A — OSPF: Nền tảng, Neighbor, Network Type & LSDB

> 🧭 **Lộ trình:** Module-03 → `[Bạn đang ở đây] Module-04A` → [Module-04B](Module-04B-OSPF-Area-Summarization-OSPFv3.md) → Module-05 (BGP)
>
> 📊 **Blueprint:** Domain **3.0 Infrastructure (30%)**, mục **3.2.b — Configure and verify
> simple OSPF environments, including multiple normal areas, summarization, and filtering
> (neighbor adjacency, point-to-point and broadcast of OSPFv2 and OSPFv3, router ID)**
>
> ⏱️ **Tuần 7** · 10 giờ
>
> ⚠️ OSPF là **protocol duy nhất** mà ENCOR yêu cầu cấu hình + verify + troubleshoot ở mức sâu.
> Cùng với Module-04B, đây là **2 tuần quan trọng nhất** của cả khóa.

---

# 📌 TÓM TẮT — đọc 10 phút là nắm khung

## Module này trả lời một câu hỏi duy nhất

> **"Làm sao hàng trăm router tự vẽ được CÙNG MỘT tấm bản đồ mạng — rồi mỗi con tự tính
> đường đi ngắn nhất từ chỗ mình?"**

Đó là toàn bộ ý tưởng của OSPF. Mọi thứ còn lại chỉ là **chi tiết của cách vẽ bản đồ đó**.

## Ba bảng — xương sống của cả module

```
   ① NEIGHBOR TABLE          "Tôi đang nói chuyện được với ai?"
      show ip ospf neighbor          ← phải thấy FULL
              │
              │  trao đổi LSA
              ▼
   ② LSDB  (Link-State Database)     "Tấm BẢN ĐỒ của cả area"
      show ip ospf database          ← MỌI router trong area có bản Y HỆT
              │
              │  chạy thuật toán SPF (Dijkstra)
              ▼
   ③ ROUTING TABLE                   "Từ CHỖ TÔI, đi đâu thì qua cửa nào?"
      show ip route ospf             ← mỗi router tính ra KẾT QUẢ KHÁC NHAU

   ⭐ Bản đồ giống nhau, nhưng đường đi khác nhau — vì điểm xuất phát khác nhau.
```

## 7 ý phải nhớ

| # | Ý | Một câu |
|:---:|---|---|
| 1 | **OSPF là link-state** | Mỗi router có **bản đồ cả area**, tự tính đường — khác EIGRP chỉ "hỏi hàng xóm" |
| 2 | **Ba bảng** | Neighbor → **LSDB** → Routing table. LSDB giống nhau, routing table khác nhau |
| 3 | **Tám neighbor state** | Luồng thường (7 bước): Down → Init → 2-Way → ExStart → Exchange → Loading → **Full**.<br>⭐ Trạng thái thứ 8 là **Attempt** — **chỉ xuất hiện trên NBMA**, không nằm trong luồng thường.<br>⭐ Kẹt **ExStart/Exchange = MTU mismatch** |
| 4 | **DR/BDR** | Chỉ bầu trên **broadcast / non-broadcast**. ⭐ **KHÔNG có preemption** — priority cao hơn không cướp được |
| 5 | **Network type quyết định tất cả** | Nó quyết định: có bầu DR không · timer bao nhiêu · có cần `neighbor` không |
| 6 | **LSA type 1, 2, 3** | **1** = router tự khai · **2** = DR khai segment · **3** = ABR tóm tắt area khác |
| 7 | ⭐ **Cost = ref-bw / bandwidth** | Mặc định ref-bw 100 Mbps → **mọi link ≥ 100M đều cost 1**. Phải chỉnh, và chỉnh **đồng loạt** |

## Bảng lệnh cốt lõi

| Lệnh | Cho biết gì |
|---|---|
| `show ip ospf neighbor` | Neighbor lên chưa — phải `FULL` |
| `show ip ospf interface <x>` | Network type, cost, timer, DR/BDR là ai |
| `show ip ospf database` | **LSDB** — tấm bản đồ |
| `show ip ospf database router` | LSA type 1 chi tiết |
| `show ip route ospf` | Kết quả cuối: `O` · `O IA` · `O E1/E2` |
| `show ip protocols` | Đang quảng bá mạng nào, RID là gì |
| `debug ip ospf adj` | Theo dõi quá trình bắt tay *(chỉ lab)* |

## 🗺️ Bố cục module — đọc theo đúng thứ tự này

| Phần | Tên | Đọc thế nào | Thời gian |
|:---:|---|---|:---:|
| **1** | 🧠 **CÁI ĐÓ LÀ GÌ** | 5 ví von, đọc **một mạch**, không lệnh | 45 phút |
| **2** | ⚙️ **NÓ CHẠY THẾ NÀO** | 12 mục. **Ba mục then chốt: §3.4, §3.9, §3.11** | 5 giờ |
| **3** | 🧪 **NHÌN THẤY NÓ** | [LAB 04A](Module-04A-LAB.md) — 6 bước | 7 giờ |
| **4** | 🏗️ **TOPO & KIẾN TRÚC** | Thiết kế area. **Vẽ lại trên giấy** | 45 phút |
| **📎** | **PHỤ LỤC** | 🔴 **KHÔNG đọc lần đầu** — chỉ tra | — |

> **Nếu bạn chỉ có thời gian cho một thứ:** làm **[LAB 04A bước 2 — đọc LSDB](Module-04A-LAB.md)**.
> Đó là lúc OSPF thôi là "giao thức tự chạy" và trở thành thứ bạn **nhìn thấy được**.
> Toàn bộ Module-04B xây thẳng lên đó.

---

## ✅ 1. Chuẩn bị

| Cần có | Chi tiết |
|---|---|
| **Kiến thức trước** | ⭐ Module-P0 §2.6 (OSPF single-area) + Module-03 §2.1 (3 bước chọn đường). **Bắt buộc** |
| **Lab** | 4× vIOS + 1 object **Bridge** (switch ảo của EVE-NG, miễn phí RAM) |
| **RAM** | 4× 512 MB = **2 GB** ✅ |
| **Thời lượng** | 3h lý thuyết · 5h lab · 2h quiz |

### Module 04A vs 04B — học gì ở đâu

| Chủ đề | 04A (Tuần 7) | 04B (Tuần 8) |
|---|:---:|:---:|
| 3 bảng của OSPF · 5 loại packet | ⭐ | |
| Neighbor state (8 trạng thái) + điều kiện adjacency | ⭐ | |
| Router ID · Cost · reference-bandwidth | ⭐ | |
| **Network type** (5 loại) · **DR/BDR election** | ⭐ | |
| **LSA type 1, 2, 3** + đọc LSDB | ⭐ | |
| Area cơ bản · ABR | ⭐ | |
| LSA type 4, 5, 7 · ASBR | | ⭐ |
| **Area type**: stub, totally stub, NSSA | | ⭐ |
| **Summarization** (`area range` / `summary-address`) | | ⭐ |
| **Filtering** · Virtual-link · Authentication | | ⭐ |
| Default route origination · **OSPFv3** | | ⭐ |

---

## 🧠 PHẦN 1 — CÁI ĐÓ LÀ GÌ

> **Đọc phần này TRƯỚC, đọc một mạch.** Không lệnh, không bảng tra.
>
> OSPF là giao thức **khó hình dung nhất** cho tới khi bạn có đúng vài ví von.
> Năm mục dưới đây là cách nhanh nhất để "nhìn thấy" nó trước khi vào cơ chế.
>
> **Tự kiểm tra:** đọc xong mỗi mục, gấp tài liệu lại, nói lại trong 3 câu.

### 2.1 Tại sao có DR — cuộc họp có người chủ trì

**Không có DR** — 10 người trong phòng, ai cũng phải nói riêng với 9 người còn lại:
`10 × 9 / 2 = 45` cuộc hội thoại. Ai cập nhật gì cũng phải nhắc lại 9 lần.

**Có DR** — 1 người làm **chủ trì**. Ai có thông tin thì nói với chủ trì,
chủ trì **thông báo lại cho cả phòng**. Chỉ cần **9 kênh liên lạc**.

**Và BDR?** — **phó chủ trì**, ngồi nghe hết mọi thứ. Chủ trì nghỉ thì phó tiếp ngay,
**không cần họp lại từ đầu**.

**DROther ↔ DROther = 2-Way** — hai người tham dự **biết mặt nhau** (2-Way)
nhưng **không cần trao đổi tài liệu riêng** với nhau (không cần Full). Mọi thứ qua chủ trì.

🧠 **Một câu để nhớ:** *DR không phải "router mạnh nhất", nó là **người chủ trì cuộc họp**.
Và vì đổi chủ trì giữa cuộc họp rất tốn công, nên DR là **non-preemptive**.*

### 2.2 Ba bảng OSPF — như chuẩn bị một chuyến đi

| Bảng | Ví von |
|---|---|
| **Neighbor table** | Danh sách người bạn đang liên lạc để **xin bản đồ** |
| **LSDB** | ⭐ **Bản đồ** đã ghép từ mọi mảnh mà bạn bè gửi |
| **Routing table** | ⭐ **Lộ trình** bạn tự vạch ra sau khi xem bản đồ |

Và **Dijkstra SPF** là **hành động ngồi xem bản đồ rồi vạch lộ trình**.

🧠 **Một câu để nhớ:** *Không có bạn → không có bản đồ → không có lộ trình.
Troubleshoot OSPF luôn đi theo thứ tự đó: neighbor → LSDB → route.*

### 2.3 LSA type 1, 2, 3 — ba loại giấy tờ

| LSA | Ví von | Ai viết |
|---|---|---|
| **Type 1** | ⭐ **"Tờ khai của tôi"**: "Tôi tên R1, tôi có 3 cửa: cửa A nối R2, cửa B nối mạng 10.1.1.0, cửa C là loopback" | Mọi router |
| **Type 2** | ⭐ **"Biên bản điểm danh"**: "Tại hội trường 10.0.0.0/24 này, có mặt R2, R3, R4" | **DR** |
| **Type 3** | ⭐ **"Thông báo dán ở cửa"**: "Bên tòa nhà A có phòng 10.1.12.0/30, đi qua tôi, cách 100 bước" | **ABR** |

⭐ **Vì sao ghép Type 1 + Type 2 lại là đủ để vẽ bản đồ:**
- Type 1 nói "tôi nối vào hội trường X"
- Type 2 nói "hội trường X có những ai"
- → Ghép lại: biết **chính xác ai nối với ai** → vẽ được bản đồ → chạy Dijkstra được

Còn **Type 3 không phải bản đồ** — nó chỉ là **danh sách địa chỉ + khoảng cách**.
Router ở area khác **không thể vẽ được bản đồ area A**.

🧠 **Một câu để nhớ:** ⭐ ***OSPF là link-state TRONG area, và distance-vector GIỮA các area.***
*Đó là lý do area vừa là ưu điểm (giới hạn SPF) vừa là hạn chế (mất tầm nhìn topology).*

### 2.4 MTU mismatch kẹt ExStart — như gửi phong bì quá khổ

Ở ExStart, hai router gửi nhau **danh mục LSA (DBD)** — có thể là gói lớn.

- R1 có hộp thư khe **1500** — gửi phong bì 1500
- R2 có hộp thư khe **1400** — ⚠️ phong bì 1500 **không nhét vào được** → rơi mất

R1 chờ mãi không thấy trả lời → **gửi lại → lại rơi → kẹt vĩnh viễn ở ExStart**.

Và điều nguy hiểm: **Hello packet nhỏ nên vẫn qua được** → hai router **vẫn thấy nhau**,
`show ip ospf neighbor` **vẫn có entry** — chỉ là mãi không lên Full.

🧠 **Một câu để nhớ:** *Thấy `EXSTART` hoặc `EXCHANGE` → nghĩ **MTU** trước mọi thứ khác.
Hello nhỏ nên qua được, DBD lớn nên rơi — đó là dấu hiệu nhận diện.*

### 2.5 Reference bandwidth — thước đo bị hỏng

Reference mặc định 100 Mbps được thiết kế năm 1998, khi FastEthernet là nhanh nhất.

Giờ bạn đo link 1G, 10G, 100G bằng cái thước chỉ có vạch tới 100 Mbps
→ **cả ba đều "vượt vạch cuối"** → **cost = 1 hết**.

OSPF nhìn vào và nói: *"3 đường này như nhau"* → chọn bừa → traffic đi đường 1G
trong khi có đường 100G nằm không.

🧠 **Một câu để nhớ:** *`auto-cost reference-bandwidth 100000` là thay cái thước.
Nhưng **mọi router phải dùng CÙNG cái thước** — người đo bằng cm, người đo bằng inch
thì so sánh vô nghĩa.*

---

## ⚙️ PHẦN 2 — NÓ CHẠY THẾ NÀO

> Giờ lắp **cơ chế thật, con số và câu lệnh** vào hình dung bạn vừa có.
>
> | Phần 1 (ví von) | → | Phần 2 (cơ chế) |
> |---|:---:|---|
> | §2.1 cuộc họp có người chủ trì | → | **§3.8 Network type · §3.9 DR/BDR** |
> | §2.2 chuẩn bị một chuyến đi | → | **§3.2 Ba bảng của OSPF** |
> | §2.3 ba loại giấy tờ | → | **§3.11 LSA type 1, 2, 3** |
> | §2.4 gửi phong bì quá khổ | → | **§3.4 Neighbor state · §3.5 Chín điều kiện** |
> | §2.5 thước đo bị hỏng | → | **§3.7 Cost & reference-bandwidth** |
>
> ⚠️ **Phần này dài (12 mục) — đừng cố đọc hết trong một buổi.**
> Ba mục quan trọng nhất: **§3.4** (neighbor state), **§3.9** (DR/BDR), **§3.11** (LSA).

### 3.1 OSPF trong 1 bảng

| Thuộc tính | Giá trị |
|---|---|
| Loại | **Link-State** |
| Thuật toán | **Dijkstra SPF** (Shortest Path First) |
| Chuẩn | **RFC 2328** (OSPFv2 / IPv4) · **RFC 5340** (OSPFv3 / IPv6) |
| AD | **110** (mọi loại route: intra, inter, external) |
| Metric | **Cost** = `reference-bandwidth / interface-bandwidth` |
| Transport | **IP protocol 89** (không dùng TCP/UDP) |
| Multicast | **224.0.0.5** = AllSPFRouters · **224.0.0.6** = AllDRouters |
| Đơn vị tổ chức | **Area** — area 0 là **backbone** |
| Router ID | 32 bit, định dạng như IP |
| Hỗ trợ VLSM/CIDR | ✅ |
| Unequal-cost LB | ❌ **Không** (chỉ ECMP — xem Module-03 §2.5) |
| Max ECMP path | Mặc định 4, tối đa 16–32 tùy platform (`maximum-paths`) |

### 3.2 ⭐ Ba bảng của OSPF

Hiểu 3 bảng này là hiểu cách OSPF vận hành. Mọi lệnh `show` đều thuộc 1 trong 3.

```
┌──────────────────────────────────────────────────────────────────────┐
│ 1. NEIGHBOR TABLE       "Tôi đang nói chuyện với ai?"                │
│    show ip ospf neighbor                                             │
│    → Router ID · State · Dead Time · Interface                       │
├──────────────────────────────────────────────────────────────────────┤
│ 2. LSDB (Link-State Database)   "Bản đồ mạng của tôi"                │
│    show ip ospf database                                             │
│    → Tập hợp mọi LSA. MỌI router trong CÙNG AREA phải GIỐNG NHAU  │
├──────────────────────────────────────────────────────────────────────┤
│              │ chạy Dijkstra SPF trên LSDB                           │
│              ▼                                                        │
│ 3. ROUTING TABLE        "Đường đi tốt nhất"                          │
│    show ip route ospf                                                │
│    → Kết quả tính toán, đưa vào RIB (rồi vào FIB — Module-01)        │
└──────────────────────────────────────────────────────────────────────┘
```

| Bảng | Tương đương | Nếu sai thì |
|---|---|---|
| Neighbor table | Danh bạ điện thoại | Không có neighbor → không nhận được bản đồ |
| **LSDB** | ⭐ **Bản đồ** | LSDB lệch giữa 2 router **cùng area** = **lỗi nghiêm trọng** |
| Routing table | Lộ trình đã vạch | Route sai = LSDB sai, hoặc cost sai |

> ⭐ **Nguyên tắc troubleshoot OSPF:** đi theo đúng thứ tự **1 → 2 → 3**.
> Không có route (bảng 3) thì kiểm tra LSDB (bảng 2). LSDB thiếu thì kiểm tra neighbor (bảng 1).
> Nhảy thẳng vào `show ip route` là mất thời gian.

### 3.3 Năm loại OSPF packet

| # | Tên | Viết tắt | Nhiệm vụ | Xuất hiện ở state nào |
|:---:|---|---|---|---|
| **1** | **Hello** | — | Tìm neighbor, duy trì quan hệ, bầu DR/BDR | Mọi lúc (mỗi 10 s) |
| **2** | **Database Description** | **DBD** / DD | Gửi **danh mục** LSA mình có (không gửi nội dung) | ExStart, Exchange |
| **3** | **Link State Request** | **LSR** | "Cho tôi xin LSA số X" | Exchange, Loading |
| **4** | **Link State Update** | **LSU** | ⭐ Gửi **nội dung LSA thật** | Loading, và mỗi khi có thay đổi |
| **5** | **Link State Acknowledgment** | **LSAck** | Xác nhận đã nhận LSU | Loading, Full |

> 🧠 **Ví von:** DBD như **mục lục sách** ("tôi có chương 1, 3, 5"). LSR là **"cho tôi xin chương 3"**.
> LSU là **nội dung chương 3 thật**. LSAck là **"đã nhận, cảm ơn"**.

**Nội dung gói Hello — quyết định neighbor có lên được không:**

| Trường trong Hello | Phải khớp? |
|---|:---:|
| **Router ID** | Phải **unique** (không được trùng) |
| ⭐ **Area ID** | ✅ **Phải khớp** |
| ⭐ **Network mask** | ✅ Phải khớp (trừ P2P) |
| ⭐ **Hello interval** | ✅ **Phải khớp** |
| ⭐ **Dead interval** | ✅ **Phải khớp** |
| ⭐ **Authentication** | ✅ Phải khớp (loại + key) |
| ⭐ **Options — E bit** (external capability) | ✅ Phải khớp → **stub flag** |
| Router Priority | Không cần khớp (dùng bầu DR) |
| DR / BDR | Không cần khớp |
| Neighbor list | Dùng để chuyển Init → 2-Way |

### 3.4 ⭐ Tám trạng thái neighbor — đọc để troubleshoot

```
DOWN ──▶ ATTEMPT (chỉ NBMA) ──▶ INIT ──▶ 2-WAY ──▶ EXSTART ──▶ EXCHANGE ──▶ LOADING ──▶ FULL
```

| State | Chuyện gì đang xảy ra | ⚠️ Kẹt ở đây = lỗi gì |
|---|---|---|
| **Down** | Chưa nhận Hello nào từ neighbor | Interface down · `passive-interface` · sai `network` statement |
| **Attempt** | *(chỉ NBMA)* Đã gửi Hello unicast tới `neighbor` khai báo tay, chưa có phản hồi | Sai IP trong lệnh `neighbor` · L2 không thông |
| **Init** | ⭐ **Đã nhận Hello, nhưng Hello đó KHÔNG chứa Router ID của mình** | ⭐ **Hello đi một chiều** — ACL chặn, lỗi L2 một chiều, multicast bị block |
| **2-Way** | Thấy nhau (Hello có chứa Router ID của mình). Đủ để **bầu DR/BDR** | ⭐ **Có thể BÌNH THƯỜNG** — 2 router DROther trên segment broadcast dừng ở đây |
| **ExStart** | Đàm phán ai là **Master/Slave** (Router ID lớn hơn làm Master) bằng DBD rỗng | 🔴 **MTU MISMATCH** — lỗi kinh điển nhất |
| **Exchange** | Trao đổi **DBD** (danh mục LSA) | MTU mismatch · MTU quá nhỏ · lỗi truyền gói lớn |
| **Loading** | Gửi **LSR**, nhận **LSU**, gửi **LSAck** | LSA bị lỗi · MTU · bug IOS |
| ✅ **Full** | ⭐ **LSDB đã đồng bộ hoàn tất** | Đích cần đạt |

#### ⚠️ Hai state hay bị hiểu sai

**a) Kẹt ở `2-WAY` — thường là BÌNH THƯỜNG**

Trên segment **broadcast** (Ethernet), router **DROther** chỉ tạo adjacency **Full** với **DR và BDR**.
Với các DROther khác, nó dừng ở **2-Way** — **và đó là thiết kế đúng**.

```
   Segment broadcast có 4 router:
   
        R1 (DR)        R2 (BDR)       R3 (DROther)   R4 (DROther)
         │              │                │              │
         └──────────────┴────────────────┴──────────────┘
   
   R3 ↔ R1 (DR)    = FULL ✅
   R3 ↔ R2 (BDR)   = FULL ✅
   R3 ↔ R4         = 2-WAY ✅ (BÌNH THƯỜNG — không cần Full)
```

> ⭐ **Vì sao thiết kế vậy:** nếu 10 router trên 1 segment đều Full với nhau
> → `10 × 9 / 2 = 45` adjacency → 45 luồng đồng bộ LSDB → quá tốn.
> Có DR làm trung gian → chỉ cần **9 adjacency**. DR "gom" thông tin rồi phát lại.

**b) Kẹt ở `EXSTART` — 99% là MTU mismatch**

Ở ExStart, 2 router trao đổi **DBD packet**. Nếu MTU lệch, gói DBD lớn từ bên MTU cao
bị bên MTU thấp **drop** → không hoàn tất đàm phán Master/Slave → **kẹt vĩnh viễn**.

```
R1# show interfaces Gi0/0 | include MTU
  MTU 1500 bytes, BW 1000000 Kbit/sec

R2# show interfaces Gi0/0 | include MTU
  MTU 1400 bytes, BW 1000000 Kbit/sec      ← ⚠️ LỆCH
```

**Cách sửa:** đặt MTU giống nhau. Hoặc (chỉ khi bắt buộc) bỏ qua kiểm tra:
```
interface GigabitEthernet0/0
 ip ospf mtu-ignore                      ! ⚠️ chỉ dùng khi hiểu rõ rủi ro
```
> ⚠️ `mtu-ignore` chỉ **che triệu chứng**. LSA lớn vẫn có thể bị drop → LSDB không đồng bộ.
> Luôn ưu tiên **sửa MTU cho khớp**.

### 3.5 ⭐ Chín điều kiện để OSPF lên `FULL`

Đây là **checklist troubleshoot** — học thuộc, dùng suốt sự nghiệp.

| # | Điều kiện | Kiểm tra bằng | Kẹt ở state |
|:---:|---|---|---|
| 1 | Interface **up/up** | `show ip int brief` | Down |
| 2 | Interface **nằm trong OSPF** (đúng `network`/`ip ospf area`) | ⭐ `show ip ospf interface brief` | Down |
| 3 | **Không** bị `passive-interface` | `show ip protocols` | Down |
| 4 | ⭐ **Area ID khớp** | `show ip ospf interface Gi0/0` | Init / không lên |
| 5 | ⭐ **Cùng subnet + mask** | `show ip int brief` | Không lên |
| 6 | ⭐ **Hello / Dead interval khớp** | `show ip ospf interface Gi0/0` | Không lên / flapping |
| 7 | ⭐ **Authentication khớp** (loại + key) | `show ip ospf interface Gi0/0` | Không lên |
| 8 | ⭐ **Stub area flag (E-bit) khớp** | `show ip ospf` | Không lên |
| 9 | ⭐ **Router ID unique** | `show ip ospf` cả 2 router | Lên rồi tụt / flapping |
| + | ⭐ **MTU khớp** | `show interfaces \| include MTU` | 🔴 **ExStart / Exchange** |
| + | **Network type tương thích** | `show ip ospf interface Gi0/0` | Không lên (VD P2P ↔ Broadcast) |

> 💡 **Mẹo nhớ:** một lệnh duy nhất cho gần hết:
> ```
> show ip ospf interface GigabitEthernet0/0
> ```
> Nó hiện: Area, Process ID, Router ID, Network Type, Cost, State, Priority, DR/BDR,
> Timer (Hello/Dead/Wait/Retransmit), Authentication, số neighbor.
> **Chạy lệnh này trên CẢ HAI router rồi so từng dòng.**

### 3.6 Router ID — chọn thế nào và bẫy khi đổi

**Thứ tự ưu tiên:**

| Ưu tiên | Nguồn |
|:---:|---|
| **1** | ⭐ Lệnh `router-id x.x.x.x` (gõ tay) |
| **2** | IP **cao nhất** trên **loopback** đang `up` |
| **3** | IP **cao nhất** trên **interface vật lý** đang `up` |

```
router ospf 1
 router-id 1.1.1.1
```

> ⭐ **Best practice:** **luôn gõ tay** `router-id`, dùng IP của loopback.
> Lý do: (a) không đổi khi interface up/down, (b) dễ nhận diện router trong LSDB,
> (c) tránh Router ID nhảy khi thêm/bớt interface.

⚠️ **Bẫy đề & bẫy thực tế:** đổi `router-id` **KHÔNG có tác dụng ngay**. Phải:
```
clear ip ospf process
! → Router hỏi: Reset ALL OSPF processes? [no]: yes
```
⚠️ Lệnh này **reset toàn bộ OSPF** → mất neighbor tạm thời → **downtime**.
Trên production phải làm trong cửa sổ bảo trì.

**Kiểm tra:**
```
show ip ospf | include Router ID|ID
show ip protocols | include Router ID
```

⚠️ **Router ID trùng nhau:** neighbor lên rồi tụt liên tục, log báo:
```
%OSPF-4-DUP_RTRID_NBR: OSPF detected duplicate router-id 2.2.2.2 from 10.0.12.2 on interface Gi0/0
```

### 3.7 Cost & reference-bandwidth

```
Cost = reference-bandwidth (Mbps) / interface-bandwidth (Mbps)
       ↑ mặc định 100 Mbps
Làm tròn xuống, TỐI THIỂU = 1
```

| Interface | BW | Cost (ref 100) | Cost (ref 100000) |
|---|---|:---:|:---:|
| Serial T1 | 1.544 Mbps | 64 | 64766 |
| Ethernet | 10 Mbps | 10 | 10000 |
| FastEthernet | 100 Mbps | 1 | 1000 |
| **GigabitEthernet** | 1 Gbps | ⚠️ **1** | **100** |
| **10 GigabitEthernet** | 10 Gbps | ⚠️ **1** | **10** |
| **100 GigabitEthernet** | 100 Gbps | ⚠️ **1** | **1** |
| **Loopback** | — | **1** | 1 |

🔴 **Vấn đề:** với reference mặc định 100 Mbps, **Gi / 10G / 100G đều cost = 1**
→ OSPF **không phân biệt được** link nhanh/chậm → chọn đường sai.

**Ba cách đặt cost:**

```
! === Cách 1 (KHUYẾN NGHỊ): đổi reference-bandwidth ===
router ospf 1
 auto-cost reference-bandwidth 100000       ! đơn vị Mbps → 100 Gbps
! ⚠️ PHẢI đặt GIỐNG NHAU trên MỌI router trong domain OSPF

! === Cách 2: đặt cost trực tiếp trên interface (thắng mọi cách khác) ===
interface GigabitEthernet0/0
 ip ospf cost 50

! === Cách 3 (KHÔNG khuyến nghị): đổi bandwidth của interface ===
interface GigabitEthernet0/0
 bandwidth 100000                            ! ⚠️ ảnh hưởng cả QoS, EIGRP, SNMP
```

> ⭐ **Bẫy đề:** *"Đặt `auto-cost reference-bandwidth 10000` trên 1 router thôi thì sao?"*
> → Router đó tính cost khác các router khác → **so sánh cost lệch** → đường đi kỳ dị,
> thậm chí **routing loop**. **Luôn đặt đồng loạt.**

**Kiểm tra:**
```
show ip ospf | include Reference bandwidth
show ip ospf interface brief                 ! cột Cost
show ip ospf interface Gi0/0 | include Cost
```

### 3.8 ⭐ Năm loại Network Type — bảng phải thuộc

Network type quyết định: **có bầu DR/BDR không**, **timer bao nhiêu**, **tìm neighbor tự động hay tay**.

| Network Type | Bầu DR/BDR? | Hello / Dead | Tìm neighbor | Mặc định trên | LSA sinh ra |
|---|:---:|:---:|---|---|---|
| ⭐ **Broadcast** | ✅ **Có** | **10 / 40** | Tự động (multicast) | **Ethernet** | Type 1 + **Type 2** |
| **Non-Broadcast (NBMA)** | ✅ **Có** | **30 / 120** | ⚠️ **Khai báo tay** (`neighbor`) | Frame Relay (main) | Type 1 + Type 2 |
| ⭐ **Point-to-Point** | ❌ **Không** | **10 / 40** | Tự động | Serial, sub-if P2P | **Chỉ Type 1** |
| **Point-to-Multipoint** | ❌ Không | **30 / 120** | Tự động | — (đặt tay) | Chỉ Type 1 |
| **Point-to-Multipoint Non-Broadcast** | ❌ Không | **30 / 120** | ⚠️ Khai báo tay | — (đặt tay) | Chỉ Type 1 |
| *(Loopback)* | — | — | — | Loopback | Quảng bá thành **`/32`** |

**Hai con số phải nhớ: `10/40` và `30/120`.**

```
! Đổi network type
interface GigabitEthernet0/0
 ip ospf network point-to-point              ! hay dùng nhất
 ip ospf network broadcast
 ip ospf network non-broadcast
 ip ospf network point-to-multipoint

! Đổi timer (⚠️ PHẢI đặt CẢ 2 ĐẦU)
interface GigabitEthernet0/0
 ip ospf hello-interval 3
 ip ospf dead-interval 12
```

> ⚠️ **Dead interval mặc định = 4 × Hello interval.** Đổi hello mà không đổi dead
> thì IOS tự tính lại dead = 4×hello **trên router đó** — nhưng nếu bên kia không đổi
> thì **timer lệch → neighbor không lên**. **Luôn đặt cả 2 đầu.**

#### ⭐ Kỹ thuật thực chiến: đổi Ethernet P2P sang `point-to-point`

Trên link Ethernet **chỉ có 2 router** (rất phổ biến ở campus/DC), Ethernet mặc định là
**broadcast** → vẫn bầu DR/BDR dù chỉ 2 router. Điều đó **vô nghĩa và có hại**:

| | Giữ `broadcast` | ⭐ Đổi `point-to-point` |
|---|---|---|
| Bầu DR/BDR | ✅ Có (vô ích với 2 router) | ❌ Không |
| Thời gian chờ bầu (**Wait timer** = dead interval) | ⚠️ Chậm hơn khi hội tụ | ⭐ Nhanh hơn |
| LSA sinh ra | Type 1 + **Type 2** | ⭐ **Chỉ Type 1** → LSDB nhỏ hơn |
| Mask có phải khớp? | ✅ Phải | Linh hoạt hơn |

```
! Làm trên CẢ 2 router của link
interface GigabitEthernet0/0
 ip ospf network point-to-point
```

> ⭐ Đây là **best practice chuẩn công nghiệp** cho link P2P Ethernet. Vừa hội tụ nhanh hơn,
> vừa giảm kích thước LSDB. Đề ENCOR hỏi về lợi ích này.

### 3.9 ⭐ DR / BDR Election

**Chỉ xảy ra trên network type `broadcast` và `non-broadcast`.**

#### Quy trình bầu

| Bước | So sánh |
|:---:|---|
| **1** | ⭐ **Priority CAO NHẤT** thắng (0–255, mặc định **1**) |
| **2** | Nếu bằng nhau → **Router ID CAO NHẤT** thắng |

⚠️ **Chú ý ngược với STP:** OSPF chọn **giá trị CAO**, STP chọn **giá trị THẤP**.

| Priority | Ý nghĩa |
|:---:|---|
| **0** | ⭐ **Không bao giờ** làm DR/BDR (luôn là **DROther**) |
| 1 | Mặc định |
| 2–255 | Càng cao càng ưu tiên |

```
interface GigabitEthernet0/1
 ip ospf priority 255            ! ép làm DR
 ip ospf priority 0              ! ép KHÔNG làm DR/BDR
```

#### 🔴 DR/BDR là NON-PREEMPTIVE — bẫy đề quan trọng nhất

> ⭐ **Sau khi DR đã được bầu, một router mới với priority CAO HƠN sẽ KHÔNG chiếm quyền DR.**
> Nó phải **chờ DR hiện tại chết**.

**Ví dụ đề hay hỏi:**
```
1. R1 (priority 1) và R2 (priority 1) lên trước → R2 có Router ID cao hơn → R2 = DR, R1 = BDR
2. R3 (priority 255) bật lên sau
3. Câu hỏi: R3 có thành DR không?
   → ❌ KHÔNG. R3 = DROther. R2 vẫn là DR.
4. Muốn R3 thành DR thì phải làm gì?
   → clear ip ospf process trên MỌI router của segment
     (hoặc shut/no shut interface của DR và BDR)
```

> 🧠 **Vì sao thiết kế non-preemptive:** nếu DR có thể bị chiếm quyền bất cứ lúc nào,
> thì mỗi lần một router mới bật lên, cả segment phải **đồng bộ lại LSDB** → bất ổn.
> Cisco chọn **ổn định** thay vì **tối ưu**.

#### Khi DR chết

```
DR chết ──▶ BDR lên làm DR ngay (đã có LSDB đồng bộ, không cần đồng bộ lại)
        ──▶ Bầu BDR mới trong số các DROther
```
⭐ Đây là lý do **có BDR**: nếu chỉ có DR, khi DR chết thì cả segment phải đồng bộ lại từ đầu.

#### Vai trò của DR

| Vai | Việc |
|---|---|
| **DR** | ⭐ Sinh ra **LSA type 2 (Network LSA)** · nhận LSU từ mọi router rồi **phát lại** cho cả segment |
| **BDR** | Nghe mọi thứ, giữ LSDB đồng bộ, **chờ thay DR** |
| **DROther** | Full với DR + BDR · **2-Way** với DROther khác |

**Multicast address:**

| Địa chỉ | Tên | Ai gửi tới |
|---|---|---|
| **224.0.0.5** | AllSPFRouters | Mọi router OSPF (Hello) · DR dùng để **phát lại** LSU |
| **224.0.0.6** | AllDRouters | ⭐ **DROther gửi LSU tới DR/BDR** |

```
DROther ──LSU──▶ 224.0.0.6 (DR + BDR)
DR ──────LSU──▶ 224.0.0.5 (mọi router trên segment)
```

**Kiểm tra:**
```
show ip ospf interface Gi0/1 | include State|Priority|Designated
```
**Output mẫu:**
```
  State DROTHER, Priority 1, Designated Router (ID) 3.3.3.3, Interface address 10.0.0.3
  Backup Designated router (ID) 2.2.2.2, Interface address 10.0.0.2
```

⭐ **Đọc `show ip ospf neighbor` trên segment broadcast:**
```
Neighbor ID     Pri   State           Dead Time   Address         Interface
2.2.2.2           1   FULL/BDR        00:00:35    10.0.0.2        GigabitEthernet0/1
3.3.3.3           1   FULL/DR         00:00:33    10.0.0.3        GigabitEthernet0/1
4.4.4.4           1   2WAY/DROTHER    00:00:36    10.0.0.4        GigabitEthernet0/1
```

| Cột `State` | Nghĩa |
|---|---|
| `FULL/DR` | Full với router đó, **router đó là DR** |
| `FULL/BDR` | Full với router đó, **router đó là BDR** |
| ⭐ `2WAY/DROTHER` | ⭐ **BÌNH THƯỜNG** — cả hai đều DROther, không cần Full |
| `FULL/DROTHER` | Full với DROther → nghĩa là **mình** là DR hoặc BDR |
| `FULL/  -` | Trên link **point-to-point** (không có DR/BDR) |

### 3.10 Area — khái niệm và các vai trò router

| Khái niệm | Nội dung |
|---|---|
| **Area** | Nhóm router chia sẻ **cùng một LSDB** |
| ⭐ **Area 0 = Backbone** | **Mọi area khác PHẢI nối tới area 0** (trực tiếp hoặc qua virtual-link) |
| **Area ID** | 32 bit — viết dạng số (`area 1`) hoặc dạng IP (`area 0.0.0.1`) |

**Vì sao cần area** (nhắc lại Module-P0 §3.5):

| Không có area (1 area khổng lồ) | ⭐ Có area |
|---|---|
| 1 link nhấp nháy → **mọi router** chạy lại SPF | Chỉ router **trong area đó** chạy lại SPF |
| LSDB khổng lồ → tốn RAM | LSDB nhỏ hơn nhiều |
| SPF chạy trên toàn mạng → tốn CPU | SPF chỉ trong area |

⭐ **Area = giới hạn phạm vi ảnh hưởng của một sự cố (fault domain).**

#### Bốn vai trò router

| Vai | Định nghĩa | Sinh LSA nào |
|---|---|---|
| **Internal Router** | Mọi interface trong **cùng 1 area** | Type 1 |
| **Backbone Router** | Có ít nhất 1 interface trong **area 0** | Type 1 |
| ⭐ **ABR** (Area Border Router) | Interface ở **≥ 2 area**, trong đó **phải có area 0** | Type 1 + ⭐ **Type 3** (+ Type 4) |
| ⭐ **ASBR** (AS Boundary Router) | Router **redistribute** route từ ngoài vào OSPF | Type 1 + ⭐ **Type 5** (hoặc 7) |

```
   AREA 1                AREA 0 (backbone)              AREA 2
                                                                    ┌── redistribute
  ┌────┐              ┌─────┐         ┌─────┐         ┌────┐        │   static/BGP
  │ R1 │──────────────│ R2  │─────────│ R3  │─────────│ R4 │◀───────┘
  └────┘              └─────┘         └─────┘         └────┘
  Internal              ABR          Backbone      ABR + ASBR
  Router                            Router
```

> ⚠️ **Một router có thể vừa là ABR vừa là ASBR** — rất phổ biến ở biên mạng.

**Kiểm tra:**
```
show ip ospf | include Area|area|It is an
```
**Output mẫu:**
```
 Routing Process "ospf 1" with ID 2.2.2.2
 It is an area border router                 ← ABR
 Number of areas in this router is 2. 2 normal 0 stub 0 nssa
    Area BACKBONE(0)
    Area 1
```

```
show ip ospf border-routers                  ! ABR/ASBR nào đang biết
show ip ospf interface brief                 ! interface nào thuộc area nào
```

### 3.11 ⭐ LSA type 1, 2, 3 (type 4, 5, 7 học ở Module-04B)

#### Bảng tổng hợp

| Type | Tên | Ai sinh ra | Flood tới đâu | LS ID là gì | Mô tả gì |
|:---:|---|---|---|---|---|
| **1** | **Router LSA** | ⭐ **MỌI** router | **Trong area** | **Router ID** | Các link của router đó |
| **2** | **Network LSA** | ⭐ **DR** | **Trong area** | **IP interface của DR** | Router nào đang gắn vào segment transit |
| **3** | **Summary LSA** | ⭐ **ABR** | **Sang area khác** | **Địa chỉ mạng** | "Ở area kia có mạng X, đi qua tôi" |

#### LSA Type 1 — Router LSA

Mỗi router tự mô tả **các link của mình**. Trong LSA type 1 có các **Link Type**:

| Link Type trong LSA 1 | Nghĩa |
|:---:|---|
| **1** | Point-to-point connection to another router |
| **2** | ⭐ **Connection to a transit network** (segment có DR) |
| **3** | ⭐ **Connection to a stub network** (subnet không có router khác — VD loopback, LAN có PC) |
| **4** | Virtual link (Module-04B) |

```
show ip ospf database router
show ip ospf database router 1.1.1.1              ! LSA type 1 của R1
show ip ospf database router self-originate       ! LSA type 1 của chính mình
```

**Output mẫu (`show ip ospf database router 2.2.2.2`):**
```
            OSPF Router with ID (1.1.1.1) (Process ID 1)

                Router Link States (Area 1)

  LS age: 245
  Options: (No TOS-capability, DC)
  LS Type: Router Links
  Link State ID: 2.2.2.2
  Advertising Router: 2.2.2.2
  LS Seq Number: 80000004
  Checksum: 0x1A2B
  Length: 48
  Area Border Router                              ← R2 là ABR
   Number of Links: 2

    Link connected to: another Router (point-to-point)
     (Link ID) Neighboring Router ID: 1.1.1.1
     (Link Data) Router Interface address: 10.1.12.2
      Number of MTID metrics: 0
       TOS 0 Metrics: 100

    Link connected to: a Stub Network
     (Link ID) Network/subnet number: 10.1.12.0
     (Link Data) Network Mask: 255.255.255.252
      Number of MTID metrics: 0
       TOS 0 Metrics: 100
```

⭐ **Đọc output:** `Area Border Router` xác nhận R2 là ABR · `Number of Links: 2` ·
link đầu là **point-to-point** tới R1, link sau là **stub network** (chính subnet đó).

#### LSA Type 2 — Network LSA

**Chỉ tồn tại trên segment có DR** (broadcast / NBMA). **DR sinh ra**, mô tả
"những router nào đang gắn vào segment này".

```
show ip ospf database network
```
**Output mẫu:**
```
                Net Link States (Area 0)

  LS age: 312
  LS Type: Network Links
  Link State ID: 10.0.0.3 (address of Designated Router)      ← IP của DR
  Advertising Router: 3.3.3.3                                  ← DR sinh ra
  Network Mask: /24
        Attached Router: 3.3.3.3
        Attached Router: 2.2.2.2
        Attached Router: 4.4.4.4
```

⭐ **Điểm quan trọng:** `Link State ID` của LSA type 2 là **IP interface của DR**,
không phải Router ID. Đây là bẫy đề.

> ⭐ **Không có LSA type 2 trên link point-to-point** — đây là lý do đổi Ethernet sang
> `ip ospf network point-to-point` làm LSDB nhỏ hơn (§2.8).

#### LSA Type 3 — Summary LSA

**ABR sinh ra** để nói với area B: *"ở area A có mạng X, muốn tới thì đi qua tôi."*

⚠️ **Tên gây nhầm:** "Summary" **không** có nghĩa là đã được gộp (summarize).
Mặc định ABR sinh **1 LSA type 3 cho MỖI subnet** ở area kia. Muốn gộp thật thì phải cấu hình
`area range` (Module-04B).

```
show ip ospf database summary
show ip ospf database summary 10.1.12.0
```
**Output mẫu:**
```
                Summary Net Link States (Area 0)

  LS age: 180
  LS Type: Summary Links(Network)
  Link State ID: 10.1.12.0 (summary Network Number)           ← địa chỉ mạng
  Advertising Router: 2.2.2.2                                  ← ABR sinh ra
  Network Mask: /30
        MTID: 0         Metric: 100
```

⭐ **Điểm quan trọng về LSA type 3:**

| Đặc điểm | Chi tiết |
|---|---|
| Metric | ⭐ **Cost từ ABR tới mạng đó**. Router nhận sẽ **cộng thêm** cost tới ABR |
| Không mang topology | ⭐ Router area B **không biết** topology area A — chỉ biết "đi qua ABR này" |
| Ký hiệu trong route | **`O IA`** (Inter-Area) |
| ABR không flood ngược | LSA type 3 học từ area 0 **không** được flood lại vào area 0 |

> 🧠 **Đây là ý nghĩa thật của "link-state chỉ trong area":** router chỉ có **bản đồ chi tiết**
> của area mình. Với area khác, nó chỉ có **danh sách địa chỉ + khoảng cách** — giống distance vector.
> **OSPF là link-state TRONG area, và distance-vector GIỮA các area.** Đây là câu trả lời
> ở mức CCNP mà đề rất thích hỏi.

#### Lệnh xem LSDB — bảng tra cứu

```
show ip ospf database                        ! tổng quan MỌI LSA
show ip ospf database router                 ! Type 1
show ip ospf database network                ! Type 2
show ip ospf database summary                ! Type 3
show ip ospf database asbr-summary           ! Type 4  (04B)
show ip ospf database external                ! Type 5  (04B)
show ip ospf database nssa-external            ! Type 7  (04B)
show ip ospf database self-originate          ! LSA do CHÍNH mình sinh
show ip ospf database adv-router 2.2.2.2      ! mọi LSA do R2 sinh
show ip ospf database database-summary        ! đếm LSA theo type/area
```

**Output mẫu `show ip ospf database`:**
```
            OSPF Router with ID (1.1.1.1) (Process ID 1)

                Router Link States (Area 1)

Link ID         ADV Router      Age  Seq#       Checksum Link count
1.1.1.1         1.1.1.1         312  0x80000005 0x00A1B2 2
2.2.2.2         2.2.2.2         245  0x80000004 0x001A2B 2

                Summary Net Link States (Area 1)

Link ID         ADV Router      Age  Seq#       Checksum
10.0.0.0        2.2.2.2         180  0x80000002 0x004C5D
3.3.3.3         2.2.2.2         180  0x80000002 0x00778A
4.4.4.4         2.2.2.2         180  0x80000002 0x0099AB
```

| Cột | Nghĩa |
|---|---|
| **Link ID** | LS ID — nghĩa **khác nhau tùy type** (xem bảng §2.11) |
| **ADV Router** | ⭐ Router nào **sinh ra** LSA này |
| **Age** | Tuổi (giây). ⭐ **Tối đa 3600 s** — LSA được refresh mỗi **1800 s** (30 phút) |
| **Seq#** | Số thứ tự, bắt đầu `0x80000001`, tăng dần mỗi lần LSA đổi |
| **Checksum** | Kiểm tra toàn vẹn |
| **Link count** | (Type 1) Số link của router đó |

> ⭐ **Age tăng liên tục tới 3600 rồi reset về 0** = LSA được refresh bình thường (mỗi 1800 s).
> ⚠️ **Seq# tăng liên tục rất nhanh** = LSA đang bị **flapping** → có link nhấp nháy ở đâu đó.

### 3.12 Thứ tự ưu tiên route trong OSPF

Khi cùng một prefix xuất hiện dưới nhiều dạng LSA:

```
1. Intra-area  (O)      ← LSA 1 + 2, trong cùng area — TỐT NHẤT
2. Inter-area  (O IA)   ← LSA 3, từ area khác
3. External E1 (O E1)   ← LSA 5 với metric-type 1
4. External E2 (O E2)   ← LSA 5 với metric-type 2 — KÉM NHẤT
```

⚠️ **Bẫy đề:** thứ tự này áp dụng **TRƯỚC** khi so metric.
Route `O IA` metric 5000 **vẫn thắng** route `O E1` metric 5.

> ℹ️ Còn `O N1`/`O N2` (NSSA external) — Module-04B.

---

## 🧪 PHẦN 3 — NHÌN THẤY NÓ

> LAB đã tách ra file riêng để bạn **mở song song** với lý thuyết.

> ### 👉 **[LAB 04A — Tuần 7: OSPF nền tảng & LSDB](Module-04A-LAB.md)**

| Bước | Nội dung | Trả lời câu hỏi | Ví von ở Phần 1 | Cơ chế ở Phần 2 |
|:---:|---|---|---|---|
| 1 | Verify neighbor | Bắt tay qua mấy bước, kẹt ở đâu = lỗi gì? | §2.4 phong bì quá khổ | §3.4 · §3.5 |
| 2 | ⭐ **Đọc LSDB** | LSDB chứa gì? LSA 1/2/3 trông ra sao? | §2.2 chuyến đi · §2.3 ba loại giấy tờ | §3.2 · §3.11 |
| 3 | Verify routing table | LSDB biến thành route bằng cách nào? | §2.2 | §3.12 |
| 4 | DR/BDR election | Ai làm DR? Vì sao bầu lại không đổi? | §2.1 người chủ trì | §3.9 |
| 5 | Đổi network type | Point-to-point thì DR biến đi đâu? | §2.1 | §3.8 |
| 6 | 🚀 Tái hiện 6 lỗi | Sáu lỗi kinh điển — triệu chứng & cách tìm | §2.4 | §3.5 |

> ⚠️ **Bước 2 là phần quan trọng nhất của cả Module-04A.**
> Trước bước này, OSPF là một giao thức "tự chạy" mà bạn chỉ biết kết quả.
> Sau bước này, bạn **nhìn thấy** cơ sở dữ liệu mà nó dùng để tính toán — và
> **Module-04B (LSA 4/5/7, stub area, summarization) xây thẳng lên đó.**

---

## 🏗️ PHẦN 4 — TOPO & KIẾN TRÚC

> Bạn vừa học cơ chế OSPF. Phần này trả lời: **thiết kế OSPF thế nào cho một doanh nghiệp thật?**

### 4.1 Bản đồ: OSPF area trong một doanh nghiệp

```
                    ┌──────────────────────────────┐
                    │        AREA 0 (backbone)     │   ⭐ MỌI area khác
      LÕI           │   ┌──────┐      ┌──────┐     │      PHẢI nối vào đây
                    │   │Core-1│══════│Core-2│     │
                    │   └───┬──┘      └──┬───┘     │
                    └───────┼────────────┼─────────┘
                       ABR  │            │  ABR      ① ABR = router
                    ┌───────┴──┐      ┌──┴────────┐     đứng GIỮA 2 area
                    │  Dist-A  │      │  Dist-B   │
                    └────┬─────┘      └─────┬─────┘
                         │                  │
              ┌──────────┴───┐     ┌────────┴──────────┐
              │   AREA 1     │     │     AREA 2        │
              │ (Tòa nhà A)  │     │  (Tòa nhà B)      │
              │              │     │                   │
              │ ② LSA 1,2    │     │  ② LSA 1,2        │  ② chỉ lưu hành
              │    trong area│     │     trong area    │     TRONG area
              └──────────────┘     └───────────────────┘

   ③ ABR tóm tắt area 1 thành LSA type 3, bơm vào area 0
   ④ Router trong area 1 KHÔNG biết chi tiết topology area 2 — chỉ biết "đi qua ABR"
```

### 4.2 Năm quyết định thiết kế — và sai thì hỏng thế nào

| # | Quyết định | Vì sao | 🔴 Sai thì hỏng thế nào |
|:---:|---|---|---|
| ① | **Mọi area phải nối vào Area 0** | OSPF chống loop bằng cấu trúc **hình sao**, không phải bằng thuật toán | Area 1 nối thẳng Area 2 không qua Area 0 → **route không lan được**, phải chữa cháy bằng virtual-link |
| ② | **Chia area khi nào?** | LSDB càng lớn, SPF chạy càng lâu, mọi router phải giữ bản sao | Nhồi 200 router vào Area 0 → **mỗi lần flap là toàn mạng tính lại SPF** |
| ③ | **Đặt ABR ở Distribution** | ABR là chỗ **tóm tắt** — phải nằm ở ranh giới tự nhiên | Đặt ABR ở access → tóm tắt sai chỗ, không giảm được LSDB |
| ④ | **Chỉnh `reference-bandwidth` GIỐNG NHAU mọi router** | Mặc định 100 Mbps → **mọi link ≥ 100M đều cost 1** | Chỉnh một nửa số router → ⭐ **cost không đồng nhất → chọn đường sai, rất khó tìm ra** |
| ⑤ | **Router ID đặt tay bằng loopback** | RID tự chọn đổi theo interface, và **đổi RID = reset toàn bộ neighbor** | Không đặt tay → một hôm loopback lên/xuống là **OSPF reset cả vùng** |

### 4.3 Ba sự thật mà chỉ người đi làm mới biết

| Sự thật | Giải thích |
|---|---|
| ⭐ **MTU mismatch là lỗi OSPF phổ biến nhất** | Neighbor kẹt ở **ExStart/Exchange** mãi. Vì hai bên trao đổi DBD mà MTU khác nhau → không ai chịu ai. Triệu chứng rất đặc trưng, nhớ là tìm ra trong 1 phút |
| ⭐ **DR không có preemption** | Router priority cao hơn **KHÔNG cướp** được DR đang tại vị. Muốn đổi DR phải **clear process** hoặc tắt interface. Nhiều người tưởng đổi priority là xong |
| ⭐ **Đổi `reference-bandwidth` phải làm ĐỒNG LOẠT** | Đây là thay đổi nguy hiểm âm thầm nhất của OSPF: mạng vẫn chạy, nhưng **traffic đi đường sai** vì cost hai bên tính theo hai thước đo khác nhau |

### 4.4 Những thứ này sẽ lớn lên thành gì

| Bạn vừa học | Sẽ thành | Ở module |
|---|---|---|
| LSA type 1, 2, 3 | LSA 4, 5, 7 · stub/NSSA · summarization | **Module-04B** |
| Area, ABR | Virtual-link · OSPF authentication · OSPFv3 | **Module-04B** |
| Cost, chọn đường | 13 bước path selection của BGP | **Module-05B** |
| Neighbor state, troubleshoot | Quy trình chẩn đoán 6 tầng cho wireless | **Module-07B** |
| Thiết kế area | Thiết kế campus 2-tier/3-tier, SD-Access underlay | **Module-09** |

### 4.5 Vẽ lại để nhớ

> **Bài tập 15 phút, trên giấy.**
>
> 1. Vẽ lại sơ đồ §4.1 **không nhìn tài liệu**
> 2. Đánh dấu ① → ④, ghi rõ **LSA type nào đi tới đâu**
> 3. Trả lời: *"Vì sao router trong Area 1 KHÔNG cần biết topology chi tiết của Area 2?"*

<details>
<summary>Đáp án câu 3</summary>

Vì **ABR tóm tắt** Area 2 thành **LSA type 3** (Summary LSA) rồi bơm vào Area 0, và Area 0
lại bơm tiếp vào Area 1. LSA type 3 chỉ nói *"mạng X tồn tại, chi phí Y, đi qua tôi"* —
**không mang chi tiết router nào nối router nào**.

**Lợi ích:** router Area 1 giữ LSDB nhỏ hơn, SPF chạy nhanh hơn, và **một link flap ở Area 2
không làm Area 1 phải tính lại SPF** — nó chỉ thấy cost thay đổi.

Đây chính là lý do **chia area** tồn tại, và là nền của **summarization** ở Module-04B.

</details>

---

## 💡 4.6 Thực chiến đi làm

| Chủ đề | Thi dạy | Thực tế đi làm |
|---|---|---|
| **Router ID** | Thứ tự ưu tiên | ⭐ **LUÔN gõ tay** `router-id <IP loopback>`. Không bao giờ để OSPF tự chọn — Router ID nhảy khi thêm/bớt interface là nguồn của sự cố khó hiểu |
| **Đổi Router ID** | Cần `clear ip ospf process` | ⚠️ Lệnh đó **reset toàn bộ OSPF** = **downtime**. Phải xin cửa sổ bảo trì. Đặt Router ID **đúng ngay từ đầu** |
| ⭐ **`ip ospf network point-to-point`** | Ít nhắc | ⭐ **Best practice chuẩn công nghiệp** cho **mọi link Ethernet chỉ có 2 router**: hội tụ nhanh hơn (không chờ Wait timer), LSDB nhỏ hơn (không có LSA 2). Đưa vào standard config |
| **`passive-interface`** | Có lệnh | ⭐ Dùng **`passive-interface default`** rồi `no passive-interface <uplink>` — mặc định an toàn (tắt hết), chỉ bật chỗ cần. An toàn hơn nhiều so với liệt kê từng interface cần tắt |
| ⭐ **`auto-cost reference-bandwidth`** | Bẫy đề | 🔴 **Phải đặt đồng loạt MỌI router.** Lệch = đường đi sai mà **neighbor vẫn Full** → cực khó phát hiện. Ghi vào standard config, và **verify khi nhận bàn giao mạng** |
| **Giá trị reference-bandwidth** | 100000 | ⭐ Chọn theo link nhanh nhất trong mạng + dư 10× cho tương lai. Mạng có 10G → dùng `100000` (100G). Đổi sau này = phải đổi mọi router |
| **`ip ospf cost`** | Cách 2 | ⭐ Dùng khi cần **ép đường đi** cụ thể (VD ưu tiên link fiber hơn link 4G backup). Rõ ràng hơn đổi `bandwidth` |
| ⚠️ **Đổi `bandwidth`** để đổi cost | Cách 3 | ⛔ **Tránh.** `bandwidth` ảnh hưởng cả **QoS shaping, EIGRP, SNMP counter, NetFlow**. Dùng `ip ospf cost` |
| **Timer nhanh** (hello 1–3 s) | Có lệnh | ⚠️ Đặt cả 2 đầu, và ⭐ **cân nhắc dùng BFD thay** (`bfd interval 300 min_rx 300 multiplier 3` + `ip ospf bfd`) — phát hiện lỗi ms mà không tăng gánh nặng OSPF |
| **DR/BDR** | Non-preemptive | ⭐ Trên segment broadcast quan trọng: **ép DR/BDR là 2 switch core/distribution** (priority 255 và 200), **các router access đặt priority 0**. Không để mạng tự bầu |
| ⭐ **`2WAY/DROTHER`** | Ít nhắc | ⭐ **Không phải lỗi.** Rất nhiều người mới báo sự cố vì thấy state này. Biết điều này tiết kiệm nhiều giờ |
| **MTU** | Bẫy đề ExStart | ⭐ Chuẩn hóa MTU toàn mạng. Đặc biệt cẩn thận khi có **tunnel (GRE/IPsec — Module-08)** hoặc **jumbo frame** — đó là nơi MTU lệch xuất hiện nhiều nhất |
| **`ip ospf mtu-ignore`** | Có lệnh | ⚠️ **Chỉ che triệu chứng.** Neighbor lên Full nhưng LSA lớn vẫn có thể bị drop → LSDB không đồng bộ → sự cố tệ hơn. **Sửa MTU, đừng ignore** |
| **`clear ip ospf process`** | Lệnh reset | 🔴 **Không bao giờ gõ trên production ngoài cửa sổ bảo trì.** Nó reset **mọi** OSPF process → mất mọi neighbor. Dùng `clear ip ospf <pid> redistribution` hay `shut/no shut` 1 interface nếu chỉ cần reset cục bộ |
| **LSDB** | Lệnh `show` | ⭐ Khi nhận bàn giao mạng OSPF: chạy `show ip ospf database database-summary` trên mọi router. Số LSA quá lớn (>vài nghìn) = thiết kế area sai, cần chia lại |
| **`Seq#` tăng nhanh** | Không dạy | ⭐ Dấu hiệu **LSA flapping** (link nhấp nháy) hoặc **duplicate Router ID**. `show ip ospf database router` rồi so `Seq#` sau vài phút |
| **Số router / area** | Không có con số cứng | ⭐ Hướng dẫn thực tế: **≤ 50 router/area**, **≤ 3 area/ABR** — nhưng phụ thuộc CPU/RAM thiết bị và độ ổn định link. Quan trọng hơn: **link ổn định**, vì link flapping làm SPF chạy liên tục |
| **Tài liệu hóa** | Không có | ⭐ Vẽ sơ đồ ghi rõ: area nào, ABR nào, Router ID nào, reference-bandwidth bao nhiêu, DR/BDR ép ở đâu. Không có tài liệu = không ai dám sửa |

---

# 📎 PHỤ LỤC — TRA CỨU

> 🔴 **KHÔNG đọc phần này ở lần học đầu tiên.**
>
> | Khi nào | Mở mục nào |
> |---|---|
> | Đang lab mà lỗi | **Gỡ lỗi nhanh** (§7) — quy trình 5 bước cho OSPF |
> | Quên lệnh | **Hộp lệnh** (§7.1) |
> | Tuần 20, ôn thi | **Bẫy đề** (§6) + **Quiz** (§8) |
> | Gặp từ lạ | **Thuật ngữ** (§9) |
> | Tự chấm | **Đúc kết** (§10) |

---

## 🎓 6. BẪY TRONG ĐỀ ENCOR

| # | Bẫy | Sự thật |
|:---:|---|---|
| 1 | 🔴 Neighbor kẹt **`EXSTART`** / `EXCHANGE` | ⭐ **MTU mismatch** — nghĩ tới điều này TRƯỚC mọi thứ khác |
| 2 | 🔴 Neighbor ở **`2WAY/DROTHER`** | ⭐ **BÌNH THƯỜNG** — 2 DROther trên segment broadcast không cần Full |
| 3 | Neighbor kẹt **`INIT`** | Hello **một chiều** — ACL chặn, lỗi L2 một chiều, multicast bị block |
| 4 | Neighbor ở **`ATTEMPT`** | Chỉ xảy ra trên **NBMA** — đã gửi Hello unicast tới `neighbor` khai tay, chưa có phản hồi |
| 5 | 🔴 **DR/BDR có preemption?** | ⭐ **KHÔNG.** Router priority cao bật lên sau **không** chiếm quyền DR. Phải `clear ip ospf process` hoặc chờ DR chết |
| 6 | Bầu DR: cao hay thấp thắng? | ⭐ **Priority CAO NHẤT** thắng (ngược với STP!). Tie → **Router ID CAO NHẤT** |
| 7 | Priority 0 nghĩa là gì | ⭐ **Không bao giờ** làm DR/BDR — luôn DROther |
| 8 | Đổi `router-id` có tác dụng ngay? | ❌ **Không.** Phải `clear ip ospf process` |
| 9 | Thứ tự chọn Router ID | `router-id` gõ tay → **IP cao nhất trên loopback up** → IP cao nhất trên interface up |
| 10 | Network type nào **bầu DR/BDR** | ⭐ **Broadcast** và **Non-Broadcast (NBMA)**. P2P và P2MP thì **không** |
| 11 | Timer của Broadcast / P2P | **10 / 40** |
| 12 | Timer của NBMA / P2MP | **30 / 120** |
| 13 | Network type nào cần khai `neighbor` tay | ⭐ **Non-Broadcast (NBMA)** và **P2MP Non-Broadcast** |
| 14 | Dead interval mặc định | ⭐ **4 × Hello**. Đổi hello thì IOS tự tính lại dead trên router đó |
| 15 | ⭐ Lợi ích đổi Ethernet sang `point-to-point` | Không bầu DR/BDR → hội tụ nhanh hơn · ⭐ **không sinh LSA type 2** → LSDB nhỏ hơn |
| 16 | LSA **type 1** — ai sinh, flood đâu, LS ID | ⭐ **Mọi router** · **trong area** · LS ID = **Router ID** |
| 17 | LSA **type 2** — ai sinh, flood đâu, LS ID | ⭐ **DR** · **trong area** · LS ID = ⭐ **IP interface của DR** (không phải Router ID!) |
| 18 | LSA **type 3** — ai sinh, flood đâu, LS ID | ⭐ **ABR** · **sang area khác** · LS ID = **địa chỉ mạng** |
| 19 | LSA type 2 có trên link P2P? | ❌ **Không** — không có DR thì không có Network LSA |
| 20 | "Summary LSA" (type 3) đã được gộp chưa? | ❌ **Chưa.** Mặc định 1 LSA type 3 cho **mỗi** subnet. Muốn gộp phải cấu hình `area range` (04B) |
| 21 | ⭐ Router area B có biết topology area A? | ❌ **KHÔNG.** Type 1/2 **không ra khỏi area**. Chỉ nhận Type 3 = địa chỉ + metric ⭐ **OSPF là link-state TRONG area, distance-vector GIỮA các area** |
| 22 | Metric của route `O IA` tính thế nào | **Metric trong LSA 3** (cost từ ABR tới mạng) **+ cost từ router hiện tại tới ABR** |
| 23 | Thứ tự ưu tiên route OSPF | ⭐ **Intra (O) → Inter (O IA) → E1 → E2** — áp dụng **TRƯỚC** khi so metric |
| 24 | `O IA` metric 5000 vs `O E1` metric 5 | ⭐ **`O IA` thắng** — thứ tự loại route đứng trước metric |
| 25 | Multicast: mọi router / DR | **224.0.0.5** (AllSPFRouters) / **224.0.0.6** (AllDRouters). DROther gửi LSU tới `.6`, DR phát lại ra `.5` |
| 26 | IP protocol number của OSPF | **89** |
| 27 | LSA Age tối đa / chu kỳ refresh | **3600 s** / refresh mỗi **1800 s** (30 phút) |
| 28 | `Seq#` tăng rất nhanh nghĩa là gì | ⭐ **LSA flapping** (link nhấp nháy) hoặc **duplicate Router ID** |
| 29 | ABR là gì (định nghĩa chính xác) | Interface ở **≥ 2 area**, trong đó ⭐ **phải có area 0** |
| 30 | `passive-interface` có ngừng quảng bá subnet? | ❌ **Không** — subnet **vẫn được quảng bá**, chỉ **không gửi Hello** |
| 31 | `auto-cost reference-bandwidth` đặt lệch 1 router | ⚠️ Neighbor **vẫn Full** nhưng cost lệch → **đường đi sai**, có thể loop. Rất khó phát hiện |
| 32 | Cost của Gi / 10G / 100G với reference mặc định | ⭐ **Đều = 1** |

---

## 🐛 7. GỠ LỖI NHANH

### 7.1 Hộp lệnh vạn năng

```
! ═══ BẢNG 1: NEIGHBOR ═══
show ip ospf neighbor                           ! LỆNH ĐẦU TIÊN LUÔN
show ip ospf neighbor detail                    ! chi tiết từng neighbor
show ip ospf interface brief                    ! interface nào trong OSPF, area, cost, số Nbr
show ip ospf interface GigabitEthernet0/0       ! LỆNH VẠN NĂNG — chạy trên CẢ 2 ROUTER rồi so
show ip protocols                               ! passive-interface, network statement, redistribute

! ═══ BẢNG 2: LSDB ═══
show ip ospf database                           ! tổng quan
show ip ospf database database-summary          ! đếm LSA theo type + area
show ip ospf database router                    ! Type 1
show ip ospf database router <router-id>
show ip ospf database network                   ! Type 2
show ip ospf database summary                   ! Type 3
show ip ospf database self-originate            ! LSA của chính mình
show ip ospf database adv-router <router-id>    ! mọi LSA do router đó sinh

! ═══ BẢNG 3: ROUTE ═══
show ip route ospf
show ip route <prefix>                          ! AD, metric, type (intra/inter/extern)
show ip ospf border-routers                     ! ABR/ASBR nào đang biết
show ip ospf statistics                         ! số lần chạy SPF + thời gian

! ═══ TỔNG QUAN PROCESS ═══
show ip ospf                                    ! Router ID, area, ABR/ASBR, reference-bw, SPF count
show ip ospf | include Reference bandwidth      ! verify khi nhận bàn giao mạng
show ip ospf | include It is an                 ! ABR? ASBR?

! ═══ NỀN TẢNG (đừng bỏ) ═══
show ip interface brief                         ! up/up?
show interfaces Gi0/0 | include MTU             ! MTU — chạy CẢ 2 ĐẦU
show access-lists                               ! ACL chặn multicast?

! ═══ DEBUG (⚠️ chỉ lab, hoặc production có kiểm soát) ═══
debug ip ospf adj                               ! quá trình lên neighbor — hữu ích nhất
debug ip ospf hello                             ! ⚠️ rất nhiều output
debug ip ospf events
debug ip ospf packet
undebug all                                     ! THUỘC LÒNG

! ═══ RESET (⚠️ gây downtime) ═══
clear ip ospf process                           ! reset TOÀN BỘ — chỉ khi cần
clear ip ospf counters
```

### 7.2 Bảng lỗi: triệu chứng → nguyên nhân → cách sửa

| # | Triệu chứng | Nguyên nhân | Lệnh chẩn đoán | Cách sửa |
|:---:|---|---|---|---|
| 1 | ⭐ Kẹt **`EXSTART`** / `EXCHANGE` | 🔴 **MTU mismatch** | `show interfaces Gi0/0 \| inc MTU` **cả 2 đầu** | Đặt MTU giống nhau |
| 2 | Kẹt **`INIT`** | Hello **một chiều** | `show access-lists` · `debug ip ospf hello` · ping 2 chiều | Bỏ ACL chặn · sửa lỗi L2 · kiểm tra multicast qua switch |
| 3 | Kẹt **`ATTEMPT`** | NBMA: sai IP trong lệnh `neighbor` | `show run \| sec router ospf` | Sửa IP `neighbor` |
| 4 | ⭐ Ở **`2WAY/DROTHER`** | ✅ **BÌNH THƯỜNG** — 2 DROther | `show ip ospf int Gi0/1 \| inc State` | **Không cần sửa** |
| 5 | **Không có neighbor nào** | Interface không trong OSPF (sai wildcard) | ⭐ `show ip ospf interface brief` | Sửa `network <ip> <wildcard> area X` hoặc dùng `ip ospf 1 area X` |
| 6 | **Không có neighbor nào** | `passive-interface` | `show ip protocols \| inc Passive` | `no passive-interface <if>` |
| 7 | Neighbor không lên, Area lệch | **Area ID mismatch** | `show ip ospf int Gi0/0 \| inc Area` cả 2 đầu · `debug ip ospf adj` | Sửa area cho khớp |
| 8 | Neighbor không lên / **flapping** | **Hello/Dead timer lệch** | `show ip ospf int Gi0/0 \| inc Timer` cả 2 đầu | Đặt giống nhau **cả 2 đầu** |
| 9 | Neighbor không lên | **Authentication lệch** (04B) | `show ip ospf int Gi0/0 \| inc authentication` | Khớp loại + key |
| 10 | Neighbor không lên | **Subnet/mask lệch** | `show ip int brief` cả 2 đầu | Sửa IP/mask |
| 11 | Neighbor không lên | **Network type lệch** (P2P ↔ Broadcast) | `show ip ospf int Gi0/0 \| inc Network Type` | Đặt giống nhau |
| 12 | Neighbor không lên | **Stub flag (E-bit) lệch** (04B) | `show ip ospf \| inc stub\|Area` | Khớp area type |
| 13 | ⭐ Neighbor **lên rồi tụt liên tục** | **Duplicate Router ID** | `show logging \| inc DUP_RTRID` · `show ip ospf db router` → `Seq#` tăng nhanh | Đặt Router ID unique + `clear ip ospf process` |
| 14 | Neighbor `FULL` nhưng **thiếu route** | Subnet chưa được quảng bá | ⭐ `show ip ospf interface brief` trên router **có** subnet đó | Thêm vào OSPF |
| 15 | Neighbor `FULL` nhưng thiếu route | Area type filter (stub/NSSA — 04B) | `show ip ospf \| inc Area` | Xem 04B |
| 16 | ⭐ Đường đi **"kỳ dị"** dù neighbor đều Full | ⭐ **`reference-bandwidth` lệch giữa các router** | ⭐ `show ip ospf \| inc Reference bandwidth` trên **MỌI** router | Đặt đồng loạt |
| 17 | Đường đi kỳ dị | `ip ospf cost` đặt tay ở đâu đó | `show ip ospf interface brief` — so cột Cost | Rà soát `show run \| inc ospf cost` |
| 18 | Route `O IA` metric bất thường cao | Cost tới ABR cao, hoặc reference-bw lệch | `show ip ospf db summary <prefix>` → so metric trong LSA vs trong route | Tính lại cost |
| 19 | **DR không đúng router mong muốn** | Non-preemptive | `show ip ospf int Gi0/1 \| inc Priority\|Designated` | `ip ospf priority` + `clear ip ospf process` trên **mọi** router của segment |
| 20 | ⭐ **CPU cao**, `show ip ospf statistics` SPF chạy liên tục | **Link flapping** → LSA flooding liên tục | ⭐ `show ip ospf statistics` · `show ip ospf db router` → `Seq#` · `show interfaces \| inc flapped` | Tìm & sửa link nhấp nháy · cân nhắc `ip ospf dead-interval` dài hơn hoặc SPF throttle |
| 21 | LSDB **lệch giữa 2 router cùng area** | Lỗi nghiêm trọng: MTU, bug IOS, LSA corrupt | `show ip ospf db database-summary` cả 2 · so `Checksum` | Sửa MTU · `clear ip ospf process` · kiểm tra bug IOS version |
| 22 | Route OSPF có nhưng ping fail | Vấn đề ở FIB/CEF hoặc ACL/NAT | `show ip cef <prefix>` (M01) · `show access-lists` | Xem Module-01 §7.3 |

### 7.3 ⭐ Quy trình troubleshoot OSPF — 5 bước

```
0. NỀN TẢNG TRƯỚC (đừng bỏ qua)
   show ip interface brief          → interface up/up?
   ping <IP neighbor>               → L2/L3 local thông?
        ↓
1. BẢNG 1 — NEIGHBOR
   show ip ospf neighbor
   ├─ TRỐNG?              → show ip ospf interface brief (interface có trong OSPF?)
   │                      → show ip protocols | inc Passive
   ├─ Kẹt EXSTART/EXCHANGE→ MTU! show interfaces | inc MTU (CẢ 2 ĐẦU)
   ├─ Kẹt INIT            → Hello một chiều: ACL? multicast? L2?
   ├─ 2WAY/DROTHER        → ✅ BÌNH THƯỜNG, bỏ qua
   ├─ Lên rồi tụt         → duplicate Router ID? timer lệch?
   └─ FULL ✅             → sang bước 2
        ↓
   NẾU KHÔNG LÊN: chạy lệnh này trên CẢ 2 ROUTER rồi SO TỪNG DÒNG:
      show ip ospf interface GigabitEthernet0/0
      → Area · Network Type · Cost · Timer (Hello/Dead) · Authentication
        ↓
2. BẢNG 2 — LSDB
   show ip ospf database database-summary
   ├─ Thiếu LSA của mạng cần → router có mạng đó chưa quảng bá?
   │                            show ip ospf interface brief TRÊN ROUTER ĐÓ
   ├─ Chỉ có Type 3, không có Type 1 của area khác → ✅ ĐÚNG (LSA 1/2 không ra khỏi area)
   ├─ Thiếu Type 5/7          → xem Module-04B (area type filter)
   └─ LSDB lệch giữa 2 router cùng area → lỗi nghiêm trọng (MTU/bug)
        ↓
3. BẢNG 3 — ROUTE
   show ip route <prefix>
   ├─ Không có route      → LSDB có LSA không? (quay lại bước 2)
   ├─ Có nhưng metric lạ  → show ip ospf | inc Reference bandwidth (MỌI router!)
   │                      → show ip ospf interface brief (so cột Cost)
   └─ Có route, metric ổn → sang bước 4
        ↓
4. FORWARDING (Module-01)
   show ip cef <prefix>                → FIB khớp RIB?
   traceroute <ip> source <ip>         → đường thật
   show access-lists                   → ACL chặn?
```

> ⭐ **Nguyên tắc vàng:** ***`show ip ospf interface <if>` trên CẢ HAI router, rồi so từng dòng.***
> Một lệnh này phủ 7 trong 9 điều kiện adjacency. Đừng đoán — hãy so.

---

## 📝 8. QUIZ TỰ KIỂM TRA

**Câu 1.** Neighbor OSPF kẹt ở `EXSTART`. Nguyên nhân số 1 là gì, và vì sao Hello vẫn qua được
mà DBD thì không?

<details><summary>Xem đáp án</summary>

**MTU mismatch.**

**Vì sao Hello qua được mà DBD không:**
- **Hello packet nhỏ** (vài chục byte) → nhét vào MTU nào cũng được → 2 router **vẫn thấy nhau**,
  `show ip ospf neighbor` **vẫn có entry**
- Ở **ExStart**, hai router trao đổi **DBD packet** (danh mục LSA) — có thể **lớn**
- Bên MTU cao gửi DBD lớn → bên MTU thấp **drop** → không hoàn tất đàm phán Master/Slave
- Router gửi lại → lại drop → **kẹt vĩnh viễn ở ExStart**

**Chẩn đoán:**
```
show interfaces GigabitEthernet0/0 | include MTU      ← chạy trên CẢ 2 ROUTER
debug ip ospf adj                                      ← thấy "Too many retransmissions"
```

**Sửa:** đặt MTU giống nhau. ⚠️ **Không dùng `ip ospf mtu-ignore`** — nó chỉ che triệu chứng,
LSA lớn vẫn có thể bị drop → LSDB không đồng bộ (tệ hơn).
</details>

---

**Câu 2.** Segment broadcast có 4 router. R3 (DROther) báo neighbor R4 ở state `2WAY/DROTHER`.
Đây là lỗi không? Giải thích.

<details><summary>Xem đáp án</summary>

**KHÔNG phải lỗi — đây là hành vi đúng theo thiết kế.**

Trên segment **broadcast**, router **DROther** chỉ tạo adjacency **FULL** với **DR** và **BDR**.
Với các **DROther khác**, nó dừng ở **2-Way** (thấy nhau, đủ để bầu DR — nhưng không đồng bộ LSDB riêng).

**Vì sao:** nếu 10 router trên 1 segment đều Full với nhau → `10×9/2 = 45` adjacency
→ 45 luồng đồng bộ LSDB → quá tốn CPU/băng thông.
Có DR làm trung gian → chỉ cần **9 adjacency**. DR "gom" LSU rồi phát lại ra `224.0.0.5`.

**Cách xác nhận đúng:** trên chính router đó chạy
```
show ip ospf interface Gi0/1 | include State
```
Nếu thấy `State DROTHER` → mọi neighbor DROther khác ở `2WAY` là bình thường.
Chỉ cần neighbor với **DR và BDR** ở `FULL` là mạng hoạt động đúng.

⭐ Đây là một trong những "sự cố giả" mà người mới báo nhiều nhất.
</details>

---

**Câu 3.** Segment broadcast: R1 (pri 1, RID 1.1.1.1) và R2 (pri 1, RID 2.2.2.2) lên trước.
Sau đó R3 (pri 255, RID 3.3.3.3) bật lên. Ai là DR? Muốn R3 làm DR thì phải làm gì?

<details><summary>Xem đáp án</summary>

**DR = R2** (RID 2.2.2.2), **BDR = R1**. **R3 là DROther** dù priority 255.

**Vì sao:** DR/BDR election của OSPF là ⭐ **NON-PREEMPTIVE**. Sau khi DR đã được bầu,
router mới có priority cao hơn **KHÔNG chiếm quyền** — phải chờ DR hiện tại chết.

Ban đầu chỉ có R1 và R2: priority bằng nhau (1) → **Router ID CAO NHẤT** thắng → R2 = DR, R1 = BDR.

**Muốn R3 làm DR — 2 cách:**

```
! Cách 1: reset OSPF trên MỌI router của segment
R1# clear ip ospf process        (yes)
R2# clear ip ospf process        (yes)
R3# clear ip ospf process        (yes)

! Cách 2: shut/no shut interface của DR và BDR
R2(config-if)# shutdown / no shutdown       ← DR
R1(config-if)# shutdown / no shutdown       ← BDR
```

⚠️ **Cả 2 cách đều gây downtime** → phải có cửa sổ bảo trì.

⭐ **Bài học thực chiến:** ép DR/BDR **ngay từ khi triển khai** (priority 255 và 200 cho
2 switch core, priority 0 cho router access). Không để mạng tự bầu rồi phải sửa sau.

🧠 **Vì sao Cisco chọn non-preemptive:** nếu DR bị chiếm quyền bất cứ lúc nào, mỗi router mới
bật lên sẽ làm cả segment đồng bộ lại LSDB → bất ổn. Chọn **ổn định** thay vì **tối ưu**.
</details>

---

**Câu 4.** Điền bảng: mỗi network type có bầu DR/BDR không, timer bao nhiêu, tìm neighbor tự động hay tay?

<details><summary>Xem đáp án</summary>

| Network Type | Bầu DR/BDR | Hello/Dead | Tìm neighbor | Mặc định trên |
|---|:---:|:---:|---|---|
| **Broadcast** | ✅ **Có** | **10 / 40** | Tự động (multicast) | **Ethernet** |
| **Non-Broadcast (NBMA)** | ✅ **Có** | **30 / 120** | ⚠️ **Tay** (`neighbor`) | Frame Relay (main if) |
| **Point-to-Point** | ❌ Không | **10 / 40** | Tự động | Serial, sub-if P2P |
| **Point-to-Multipoint** | ❌ Không | **30 / 120** | Tự động | — (đặt tay) |
| **P2MP Non-Broadcast** | ❌ Không | **30 / 120** | ⚠️ **Tay** | — (đặt tay) |

**Hai con số phải nhớ: `10/40` và `30/120`.**

**Quy tắc nhớ:**
- Có chữ **"Broadcast"** hoặc **"Non-Broadcast"** (không phải "Point") → **bầu DR/BDR**
- Có chữ **"Non-Broadcast"** → **khai `neighbor` bằng tay**
- Có chữ **"Multipoint"** hoặc **"Non-Broadcast"** → timer **30/120**
</details>

---

**Câu 5.** Nêu 3 lợi ích của việc đổi link Ethernet 2 router sang `ip ospf network point-to-point`.

<details><summary>Xem đáp án</summary>

1. ⭐ **Không bầu DR/BDR** → bỏ được **Wait timer** (= dead interval, 40 s) khi interface lên
   → **hội tụ nhanh hơn**
2. ⭐ **Không sinh LSA type 2 (Network LSA)** → **LSDB nhỏ hơn**, ít LSA phải flood và lưu
   → tiết kiệm CPU/RAM, SPF chạy nhanh hơn
3. **Linh hoạt hơn về subnet mask** — P2P không yêu cầu mask khớp nghiêm ngặt như broadcast
4. *(bonus)* Cấu hình đơn giản hơn — không cần lo priority, DR/BDR, non-preemptive

**Cách làm — phải đặt CẢ 2 ĐẦU:**
```
interface GigabitEthernet0/0
 ip ospf network point-to-point
```
⚠️ Đặt 1 bên thôi → **network type lệch** → neighbor **không lên**.

**Verify:**
```
show ip ospf interface Gi0/0 | include Network Type|State
!   Network Type POINT_TO_POINT
!   State POINT_TO_POINT              ← không còn dòng "Designated Router"
show ip ospf neighbor
!   State: FULL/  -                   ← không có vai trò DR/BDR
```

⭐ Đây là **best practice chuẩn công nghiệp** cho mọi link Ethernet chỉ có 2 router
(rất phổ biến ở campus core và data center).
</details>

---

**Câu 6.** Điền bảng LSA type 1, 2, 3: ai sinh ra, flood tới đâu, LS ID là gì?

<details><summary>Xem đáp án</summary>

| Type | Tên | Ai sinh ra | Flood tới đâu | LS ID |
|:---:|---|---|---|---|
| **1** | **Router LSA** | ⭐ **MỌI router** | **Trong area** | **Router ID** |
| **2** | **Network LSA** | ⭐ **DR** | **Trong area** | ⭐ **IP interface của DR** |
| **3** | **Summary LSA** | ⭐ **ABR** | **Sang area khác** | **Địa chỉ mạng** |

**Bẫy hay gặp:**
- ⚠️ LS ID của **Type 2** là **IP interface của DR**, **KHÔNG** phải Router ID
- ⚠️ **Type 1 và Type 2 KHÔNG BAO GIỜ ra khỏi area**
- ⚠️ "Summary" trong Type 3 **không** có nghĩa đã được gộp — mặc định 1 LSA cho **mỗi** subnet.
  Muốn gộp thật phải cấu hình `area range` (Module-04B)
- ⚠️ **Không có Type 2 trên link point-to-point** (không có DR)

**Link Type trong LSA type 1** (hay hỏi):
| Link Type | Nghĩa |
|:---:|---|
| 1 | Point-to-point tới router khác |
| 2 | Transit network (segment có DR) |
| 3 | Stub network (subnet không có router khác) |
| 4 | Virtual link |
</details>

---

**Câu 7.** R1 ở area 1. R1 có thể biết topology của area 2 không? Giải thích, và cho biết
câu này liên quan tới nhận định nổi tiếng nào về OSPF.

<details><summary>Xem đáp án</summary>

**KHÔNG.** R1 **không thể** biết topology area 2.

**Vì sao:**
- **LSA type 1** (Router LSA) và **type 2** (Network LSA) — hai loại chứa **thông tin topology thật**
  ("router X nối với router Y qua segment Z") — ⭐ **KHÔNG BAO GIỜ ra khỏi area**
- R1 chỉ nhận **LSA type 3 (Summary)** từ ABR, chứa: **địa chỉ mạng + mask + metric**
  → R1 chỉ biết *"có mạng `172.16.3.0/24`, đi qua ABR này, cost X"*
- R1 **không biết**: area 2 có bao nhiêu router, nối với nhau thế nào, có bao nhiêu đường

**Nhận định nổi tiếng:**

⭐ ***"OSPF là link-state TRONG area, và distance-vector GIỮA các area."***

Vì với area khác, OSPF hành xử đúng như distance vector: chỉ biết **"hướng nào (next-hop là ABR),
xa bao nhiêu (metric)"** — không có bản đồ, phải **tin lời ABR**.

**Hệ quả thực tế:**
- ✅ **Ưu điểm:** giới hạn phạm vi chạy SPF → link nhấp nháy trong area 2 **không** làm R1 chạy lại SPF
- ⚠️ **Nhược điểm:** mất tầm nhìn topology → không thể tối ưu đường đi liên area như trong area,
  và ⭐ **có thể xảy ra suboptimal routing** giữa các area

**Cách chứng minh trong lab:**
```
R1# show ip ospf database
! → Router Link States (Area 1) chỉ có LSA của R1 và R2
! → KHÔNG có LSA type 1 nào của R3, R4
! → Chỉ có Summary Net Link States với ADV Router = ABR
```
</details>

---

**Câu 8.** LSA type 3 cho `172.16.3.0/24` có `Metric: 101`, do ABR `2.2.2.2` sinh ra.
Cost từ R1 tới ABR là 100. Route trên R1 sẽ có metric bao nhiêu? Route đó là `O` hay `O IA`?

<details><summary>Xem đáp án</summary>

**Metric = 201** · **Loại route = `O IA`** (inter-area).

**Cách tính:**
```
Metric trong LSA type 3 (cost từ ABR tới mạng)      = 101
+ Cost từ R1 tới ABR                                 = 100
─────────────────────────────────────────────────────────
= Metric trong bảng route của R1                     = 201
```

**Verify:**
```
R1# show ip ospf database summary 172.16.3.0
!   Metric: 101
R1# show ip route 172.16.3.0
!   Known via "ospf 1", distance 110, metric 201, type inter area
R1# show ip route ospf | include 172.16.3.0
!   O IA     172.16.3.0/24 [110/201] via 10.1.12.2, ...
```

⭐ **Nguyên lý:** LSA type 3 mang **cost từ ABR tới mạng đích**.
Mỗi router nhận sẽ **cộng thêm cost của chính nó tới ABR**.
Đây chính là hành vi **distance-vector** — mỗi hop cộng thêm khoảng cách của mình.
</details>

---

**Câu 9.** Bảng route có 2 entry cho cùng prefix `10.5.5.0/24`:
- `O IA` metric **5000**
- `O E1` metric **5**

Router chọn cái nào? Vì sao?

<details><summary>Xem đáp án</summary>

**Chọn `O IA` (metric 5000).**

**Vì sao:** trong OSPF, **loại route** được xét **TRƯỚC metric**:

```
1. Intra-area  (O)      ← tốt nhất
2. Inter-area  (O IA)   ← thắng ở đây
3. External E1 (O E1)
4. External E2 (O E2)   ← kém nhất
```

`O IA` (inter-area, từ LSA type 3) **luôn thắng** `O E1`/`O E2` (external, từ LSA type 5)
**bất kể metric**.

⭐ **Logic đằng sau:** route inter-area là mạng **bên trong** domain OSPF của bạn
(đáng tin, bạn kiểm soát được). Route external đến từ **ngoài** domain
(redistribute từ BGP/static/protocol khác) → OSPF ưu tiên "người trong nhà".

⚠️ **Cả 2 route đều có AD = 110** (mọi loại OSPF đều AD 110) → nên **không thể** dùng AD
để phân biệt. Việc chọn xảy ra **bên trong** thuật toán OSPF, trước khi đưa vào RIB.

*(Nếu có NSSA — Module-04B — thứ tự đầy đủ còn có `O N1`/`O N2` xen vào.)*
</details>

---

**Câu 10.** Mọi neighbor đều `FULL`, mọi route đều có, nhưng traffic đi đường "kỳ dị" —
qua link 100 Mbps thay vì link 10 Gbps. Nguyên nhân khả năng cao nhất và cách kiểm tra?

<details><summary>Xem đáp án</summary>

**Hai nguyên nhân, kiểm tra theo thứ tự:**

**1. ⭐ `auto-cost reference-bandwidth` lệch giữa các router** (khả năng cao nhất)

```
show ip ospf | include Reference bandwidth        ← chạy trên MỌI router
```
Nếu lệch → router này tính cost khác router kia → **so sánh cost vô nghĩa** → đường đi sai.

⚠️ **Loại lỗi này KHÔNG làm mất neighbor** (cost không phải điều kiện adjacency) →
cực khó phát hiện nếu không chủ động kiểm tra.

**2. Reference-bandwidth mặc định (100 Mbps) → mọi link ≥ 100 Mbps đều cost = 1**

```
show ip ospf interface brief          ← so cột Cost
```
Với reference 100: FastEthernet, Gi, 10G, 100G **đều cost = 1** → OSPF không phân biệt được
→ chọn bừa (theo Router ID hoặc thứ tự học route).

**3. Ai đó đặt `ip ospf cost` bằng tay**
```
show running-config | include ip ospf cost
show ip ospf interface brief          ← cột Cost có giá trị lạ?
```

**Cách sửa:**
```
! Trên MỌI router trong domain OSPF — không được sót
router ospf 1
 auto-cost reference-bandwidth 100000        ! 100 Gbps
```

**Verify sau khi sửa:**
```
show ip ospf | include Reference bandwidth    ← giống nhau mọi router
show ip ospf interface brief                  ← Gi=100, 10G=10, 100G=1
show ip route <prefix>                        ← metric hợp lý
traceroute <ip>                               ← đi đúng đường
```

⭐ **Bài học thực chiến:** khi **nhận bàn giao** một mạng OSPF, việc đầu tiên là chạy
`show ip ospf | include Reference bandwidth` trên mọi router. Đây là lỗi cấu hình phổ biến nhất
mà không ai để ý vì "mạng vẫn chạy".
</details>

---

**Câu 11.** `show ip ospf database router` cho thấy LSA của `4.4.4.4` có `Seq#` tăng từ
`0x80000012` lên `0x80000089` trong 2 phút. Chuyện gì đang xảy ra?

<details><summary>Xem đáp án</summary>

**Hai khả năng:**

**1. ⭐ Duplicate Router ID** (khả năng cao nhất khi Seq# tăng rất nhanh)

Hai router **cùng dùng Router ID `4.4.4.4`** → cả hai đều sinh LSA type 1 với cùng LS ID
→ **tranh nhau ghi đè**, mỗi lần ghi đè lại tăng Seq#.

```
show logging | include DUP_RTRID
! %OSPF-4-DUP_RTRID_NBR: OSPF detected duplicate router-id 4.4.4.4 from ...
show ip ospf | include Router ID          ← chạy trên mọi router, tìm cái trùng
```

**Sửa:** đặt Router ID unique + `clear ip ospf process` (⚠️ gây downtime).

**2. LSA flapping do link nhấp nháy**

Router `4.4.4.4` có 1 interface đang up/down liên tục → mỗi lần đổi, nó phải **sinh LSA type 1 mới**
với Seq# tăng.

```
show ip ospf statistics                   ! SPF chạy bao nhiêu lần
show interfaces | include flapped|reset
show logging | include LINK-3|LINEPROTO
```

**Hậu quả (cả 2 trường hợp):**
- LSA flood liên tục ra toàn area
- **Mọi router trong area chạy lại SPF liên tục** → ⭐ **CPU cao toàn mạng**
- Route nhấp nháy → CEF dựng lại FIB liên tục (Module-01)

**Cách phân biệt nhanh:**
| | Duplicate Router ID | Link flapping |
|---|---|---|
| Log | `DUP_RTRID` | `LINK-3-UPDOWN` |
| Neighbor | Lên rồi tụt liên tục | Có thể ổn định |
| `show ip ospf \| inc Router ID` | Tìm thấy 2 router trùng | Không trùng |

⭐ **Bình thường:** `Age` tăng tới 3600 rồi reset (refresh mỗi 1800 s), `Seq#` chỉ tăng
**khi có thay đổi thật**. Seq# tăng nhanh = có vấn đề.
</details>

---

**Câu 12.** Bạn cần troubleshoot "neighbor OSPF không lên" nhưng chỉ được chạy **một** lệnh
trên mỗi router. Chọn lệnh nào? Nó cho bạn kiểm tra được mấy điều kiện adjacency?

<details><summary>Xem đáp án</summary>

```
show ip ospf interface GigabitEthernet0/0
```

**Chạy trên CẢ HAI router rồi so từng dòng.** Nó phủ **7 trong 9+ điều kiện**:

| Điều kiện adjacency | Dòng trong output |
|---|---|
| ✅ **Interface trong OSPF** | Nếu lệnh trả về output = interface đã trong OSPF (`Attached via ...`) |
| ✅ ⭐ **Area ID khớp** | `Internet Address 10.0.0.2/24, Area 0` |
| ✅ ⭐ **Subnet + mask khớp** | `Internet Address 10.0.0.2/24` |
| ✅ ⭐ **Hello/Dead interval khớp** | `Timer intervals configured, Hello 10, Dead 40, ...` |
| ✅ ⭐ **Authentication khớp** | Dòng auth (nếu bật) |
| ✅ **Network type tương thích** | `Network Type BROADCAST` |
| ✅ **Router ID** | `Process ID 1, Router ID 2.2.2.2` (so 2 router có trùng không) |
| ✅ *(bonus)* Cost | `Cost: 100` — không phải điều kiện, nhưng phát hiện reference-bw lệch |
| ✅ *(bonus)* Số neighbor | `Neighbor Count is 2, Adjacent neighbor count is 2` |
| ❌ **MTU** | ⚠️ **KHÔNG có** — cần `show interfaces \| include MTU` |
| ❌ **passive-interface** | ⚠️ **KHÔNG có** — cần `show ip protocols` |

**Hai điều kiện còn thiếu và lệnh bổ sung:**
```
show interfaces GigabitEthernet0/0 | include MTU      ! cho EXSTART/EXCHANGE
show ip protocols | include Passive                    ! cho trạng thái Down
```

⭐ **Đây là quy trình chuẩn:** thay vì đoán từng khả năng, **chạy 1 lệnh trên 2 router và so từng dòng**.
Cái nào lệch thì đó là nguyên nhân. Nhanh hơn debug rất nhiều.
</details>

---

## 📚 9. THUẬT NGỮ ANH–VIỆT

| Tiếng Anh | Tiếng Việt | Ghi chú |
|---|---|---|
| **Link-State** | Trạng thái liên kết | Mỗi router có bản đồ toàn area |
| **Dijkstra SPF** | Thuật toán đường ngắn nhất | Chạy trên LSDB → ra routing table |
| **LSDB** (Link-State Database) | Cơ sở dữ liệu trạng thái liên kết | ⭐ "Bản đồ". Mọi router **cùng area** phải giống nhau |
| **LSA** (Link-State Advertisement) | Bản tin quảng bá trạng thái liên kết | 1 mảnh của LSDB |
| **Adjacency** | Quan hệ kề | Neighbor đã đồng bộ LSDB (state **Full**) |
| **Neighbor table** | Bảng láng giềng | `show ip ospf neighbor` |
| **Hello packet** | Gói chào | Tìm & duy trì neighbor, mỗi 10 s |
| **DBD** (Database Description) | Mô tả cơ sở dữ liệu | ⭐ "Mục lục" LSA — gói này lớn → **MTU quan trọng** |
| **LSR** (Link State Request) | Yêu cầu trạng thái liên kết | "Cho tôi xin LSA X" |
| **LSU** (Link State Update) | Cập nhật trạng thái liên kết | ⭐ Chứa **nội dung LSA thật** |
| **LSAck** (LS Acknowledgment) | Xác nhận | "Đã nhận" |
| **Down** | Xuống | Chưa nhận Hello nào |
| **Attempt** | Thử | Chỉ NBMA — đã gửi Hello unicast, chưa có phản hồi |
| **Init** | Khởi tạo | ⭐ Nhận Hello nhưng Hello **không chứa** Router ID của mình → **một chiều** |
| **2-Way** | Hai chiều | ⭐ Thấy nhau. **Bình thường** giữa 2 DROther |
| **ExStart** | Bắt đầu trao đổi | ⭐ Đàm phán Master/Slave. 🔴 **Kẹt đây = MTU mismatch** |
| **Exchange** | Trao đổi | Gửi DBD |
| **Loading** | Đang tải | Gửi LSR, nhận LSU |
| **Full** | Đầy đủ | ✅ LSDB đã đồng bộ |
| **Router ID** | Danh tính router | 32 bit dạng IP. ⭐ Nên gõ tay |
| **Cost** | Chi phí | `reference-bw / interface-bw` |
| **Reference bandwidth** | Băng thông tham chiếu | ⭐ Mặc định 100 Mbps. **Phải đồng nhất mọi router** |
| **Area** | Vùng | Nhóm router chia sẻ cùng LSDB |
| **Backbone (Area 0)** | Vùng xương sống | ⭐ Mọi area khác phải nối tới đây |
| **Internal Router** | Router nội vùng | Mọi interface cùng 1 area |
| **Backbone Router** | Router xương sống | Có interface trong area 0 |
| **ABR** (Area Border Router) | Router biên vùng | ⭐ Interface ở ≥2 area, **phải có area 0**. Sinh **LSA 3** |
| **ASBR** (AS Boundary Router) | Router biên hệ tự trị | Redistribute route ngoài vào OSPF. Sinh **LSA 5/7** (04B) |
| **Router LSA (Type 1)** | LSA router | ⭐ Mọi router sinh · trong area · LS ID = Router ID |
| **Network LSA (Type 2)** | LSA mạng | ⭐ **DR** sinh · trong area · LS ID = **IP của DR** |
| **Summary LSA (Type 3)** | LSA tóm tắt | ⭐ **ABR** sinh · sang area khác · LS ID = địa chỉ mạng |
| **Transit network** | Mạng chuyển tiếp | Segment có ≥2 router (có DR) → Link Type 2 trong LSA 1 |
| **Stub network** | Mạng cụt | Subnet không có router khác (loopback, LAN) → Link Type 3 |
| **Intra-area route** | Route nội vùng | `O` — trong cùng area |
| **Inter-area route** | Route liên vùng | `O IA` — từ LSA type 3 |
| **DR** (Designated Router) | Router chỉ định | ⭐ "Chủ trì" — sinh LSA 2, phát lại LSU |
| **BDR** (Backup DR) | DR dự phòng | "Phó chủ trì" — sẵn sàng thay DR |
| **DROther** | Router khác | Không phải DR/BDR. Full với DR+BDR, 2-Way với DROther |
| **Non-preemptive** | Không chiếm quyền | ⭐ Priority cao bật sau **không** chiếm DR |
| **Router Priority** | Ưu tiên router | 0–255, mặc định 1. ⭐ **0 = không bao giờ làm DR/BDR** |
| **AllSPFRouters** | Mọi router OSPF | **224.0.0.5** |
| **AllDRouters** | Mọi DR/BDR | **224.0.0.6** — DROther gửi LSU tới đây |
| **Network Type** | Loại mạng | ⭐ Quyết định DR/BDR, timer, cách tìm neighbor |
| **Broadcast** | Quảng bá | Mặc định Ethernet. Bầu DR, 10/40 |
| **NBMA** (Non-Broadcast Multi-Access) | Đa truy nhập không quảng bá | Bầu DR, 30/120, ⚠️ khai `neighbor` tay |
| **Point-to-Point** | Điểm-điểm | ⭐ **Không** bầu DR, 10/40, **không sinh LSA 2** |
| **Point-to-Multipoint** | Điểm-đa điểm | Không bầu DR, 30/120 |
| **Wait timer** | Bộ đếm chờ | = dead interval. Chờ trước khi bầu DR → P2P bỏ được bước này |
| **Passive interface** | Interface thụ động | ⭐ **Không gửi Hello** nhưng **vẫn quảng bá subnet** |
| **MTU mismatch** | Lệch MTU | 🔴 Nguyên nhân #1 của kẹt ExStart |
| **`mtu-ignore`** | Bỏ qua kiểm tra MTU | ⚠️ Chỉ che triệu chứng — nên sửa MTU |
| **Duplicate Router ID** | Trùng Router ID | Neighbor lên rồi tụt · Seq# tăng nhanh |
| **LSA Age** | Tuổi LSA | Tối đa **3600 s**, refresh mỗi **1800 s** |
| **Sequence Number** | Số thứ tự | Bắt đầu `0x80000001`. ⭐ Tăng nhanh = flapping/trùng RID |
| **LSA flooding** | Lan truyền LSA | Phát LSA ra toàn area |
| **BFD** (Bidirectional Forwarding Detection) | Phát hiện chuyển tiếp hai chiều | ⭐ Phát hiện lỗi trong ms — tốt hơn timer OSPF nhanh |

---

## 🎯 10. ĐÚC KẾT MODULE-04A

**3 điều rút ra:**

1. ⭐ **Troubleshoot OSPF luôn đi theo 3 bảng: Neighbor → LSDB → Route.**
   Và khi neighbor không lên, chạy **`show ip ospf interface <if>` trên CẢ HAI router rồi so từng dòng**
   — một lệnh phủ 7/9 điều kiện adjacency. Hai thứ nó **không** cho bạn: **MTU** (dùng
   `show interfaces | include MTU`) và **passive-interface** (dùng `show ip protocols`).

2. ⭐ **OSPF là link-state TRONG area, distance-vector GIỮA các area.**
   LSA type 1 và 2 (chứa topology thật) **không bao giờ ra khỏi area**. Router area khác chỉ nhận
   LSA type 3 = "địa chỉ + metric, đi qua ABR này". Đó vừa là ưu điểm (giới hạn SPF, giới hạn
   fault domain) vừa là hạn chế (mất tầm nhìn topology liên area).

3. ⭐ **Hai lỗi cấu hình "im lặng" nguy hiểm nhất:** (a) **`reference-bandwidth` lệch** —
   neighbor vẫn Full nhưng đường đi sai, cực khó phát hiện; (b) **DR/BDR non-preemptive** —
   router priority cao bật sau không chiếm quyền, nên phải **ép DR/BDR ngay từ khi triển khai**,
   đừng để mạng tự bầu rồi sửa sau (sửa = downtime).

🧠 **Một câu để nhớ:** *Hello nhỏ nên luôn qua được, DBD lớn nên hay bị rơi.
Đó là lý do bạn **thấy** neighbor mà nó **mãi không lên Full** — và là lý do
`EXSTART` gần như luôn có nghĩa **MTU**.*

---

### ✅ TỰ CHẤM

**Phần A — Trả lời được bằng lời của mình, không nhìn tài liệu:**

| # | Câu | ✅ |
|:---:|---|:---:|
| 1 | 3 bảng của OSPF, mỗi bảng lệnh gì, thứ tự troubleshoot? | ☐ |
| 2 | 5 loại OSPF packet và nhiệm vụ từng loại? | ☐ |
| 3 | 8 trạng thái neighbor, theo thứ tự? | ☐ |
| 4 | Kẹt `EXSTART` → nghi gì? Vì sao Hello qua được mà DBD không? | ☐ |
| 5 | Kẹt `INIT` → nghi gì? | ☐ |
| 6 | `2WAY/DROTHER` có phải lỗi? Giải thích tại sao có DR | ☐ |
| 7 | Kể 9+ điều kiện để OSPF lên `FULL` | ☐ |
| 8 | **Một** lệnh nào phủ nhiều điều kiện nhất? Nó thiếu 2 điều kiện nào? | ☐ |
| 9 | Thứ tự chọn Router ID? Đổi rồi cần làm gì? | ☐ |
| 10 | Công thức cost? Vì sao Gi/10G/100G đều cost 1? 3 cách sửa? | ☐ |
| 11 | Bảng 5 network type: DR/BDR, timer, tìm neighbor tự động/tay | ☐ |
| 12 | 3 lợi ích của `ip ospf network point-to-point`? | ☐ |
| 13 | Bầu DR: so gì trước, gì sau? Cao hay thấp thắng? | ☐ |
| 14 | ⭐ Non-preemptive nghĩa là gì? Muốn đổi DR thì làm sao? | ☐ |
| 15 | Priority 0 nghĩa là gì? Vì sao cần BDR? | ☐ |
| 16 | 224.0.0.5 vs 224.0.0.6 — ai gửi tới đâu? | ☐ |
| 17 | 4 vai trò router (Internal/Backbone/ABR/ASBR) — định nghĩa ABR chính xác | ☐ |
| 18 | LSA type 1/2/3: ai sinh, flood đâu, LS ID là gì? | ☐ |
| 19 | 4 Link Type trong LSA type 1? | ☐ |
| 20 | ⭐ Router area 1 có biết topology area 2? Liên quan nhận định nào? | ☐ |
| 21 | Metric của `O IA` tính thế nào? | ☐ |
| 22 | Thứ tự ưu tiên route OSPF? `O IA` metric 5000 vs `O E1` metric 5 — ai thắng? | ☐ |
| 23 | LSA Age tối đa? Chu kỳ refresh? `Seq#` tăng nhanh nghĩa là gì? | ☐ |
| 24 | `passive-interface` có ngừng quảng bá subnet không? | ☐ |

**Phần B — Lab (tự làm không xem hướng dẫn):**

| # | Yêu cầu | ✅ |
|:---:|---|:---:|
| 1 | Dựng 4 router + 1 Bridge: area 1 (R1-R2), area 0 (R2-R3-R4 broadcast), area 2 (R3), area 3 (R4) | ☐ |
| 2 | Mọi neighbor `FULL` · verify bằng `show ip ospf neighbor` trên cả 4 router | ☐ |
| 3 | Xác định đúng DR/BDR trên segment broadcast và giải thích **vì sao** router đó thắng | ☐ |
| 4 | Đọc và giải thích **từng dòng** của `show ip ospf interface Gi0/1` | ☐ |
| 5 | ⭐ Chứng minh R1 **không có** LSA type 1 nào của R3/R4 — chỉ có LSA type 3 từ ABR | ☐ |
| 6 | Đọc LSA type 1: chỉ ra `Number of Links`, phân biệt `point-to-point` vs `Stub Network` | ☐ |
| 7 | ⭐ Đọc LSA type 2: chỉ ra `Link State ID` = **IP của DR**, và `Attached Router` | ☐ |
| 8 | ⭐ Đọc LSA type 3: chỉ ra `ADV Router` = ABR, và **chứng minh** metric route = metric LSA + cost tới ABR | ☐ |
| 9 | Dùng `show ip ospf database database-summary` chỉ ra Area 0 có Network LSA, Area 1 thì không | ☐ |
| 10 | Phân biệt route `O` vs `O IA` trên R1 và R3, giải thích vì sao khác nhau | ☐ |
| 11 | ⭐⭐ **Chứng minh non-preemptive**: đặt priority 255 → vẫn DROther | ☐ |
| 12 | Buộc bầu lại DR bằng `clear ip ospf process` → priority 255 thành DR | ☐ |
| 13 | ⭐ Tạo tình huống `2WAY/DROTHER` (2 router priority 0, 1 router 255) | ☐ |
| 14 | ⭐ Đổi link Ethernet sang `point-to-point` cả 2 đầu → state `FULL/  -`, Area 1 không có LSA 2 | ☐ |
| 15 | Đổi 1 bên thôi → neighbor mất (chứng minh network type phải khớp) | ☐ |
| 16 | 🔴 **Tái hiện MTU mismatch** → kẹt `EXSTART` → chẩn đoán bằng `show interfaces \| inc MTU` → sửa | ☐ |
| 17 | Tái hiện **area mismatch** → chẩn đoán bằng `show ip ospf int \| inc Area` + `debug ip ospf adj` → sửa | ☐ |
| 18 | Tái hiện **timer mismatch** → chẩn đoán → sửa (và thấy dead tự tính = 4×hello) | ☐ |
| 19 | Tái hiện **duplicate Router ID** → thấy log `DUP_RTRID` và `Seq#` tăng nhanh → sửa | ☐ |
| 20 | Tái hiện **`passive-interface` sai chỗ** → mất neighbor nhưng subnet vẫn được quảng bá | ☐ |
| 21 | ⭐ Tái hiện **`reference-bandwidth` lệch** → neighbor **vẫn Full** nhưng cost lệch → sửa | ☐ |
| 22 | Cố ý phá 1 thứ bất kỳ, tự tìm ra bằng **quy trình 5 bước §7.3** trong 10 phút | ☐ |

> ⚠️ **Chưa tick hết Phần B thì đừng sang Module-04B.** Module-04B (area type, summarization,
> filtering, virtual-link, OSPFv3) xây **trực tiếp** lên khả năng đọc LSDB của bạn.
> Không đọc được LSA type 1/2/3 thì không hiểu được stub area chặn LSA nào,
> `area range` gộp cái gì, hay virtual-link tạo ra LSA gì.
>
> ⭐ **Nếu chỉ có thời gian làm một nửa lab:** ưu tiên **mục 5–10 (đọc LSDB)** và
> **mục 16–21 (tái hiện 6 lỗi)**. Đó là hai phần có giá trị cao nhất cho cả thi và làm việc.

---

## 🔗 11. TÀI LIỆU CHO MODULE NÀY

| Nguồn | Cụ thể |
|---|---|
| **Sách OCG 350-401** | Chương **OSPF** đầu tiên (thường là *"OSPF"* hoặc *"OSPFv2"*) — đọc kỹ phần neighbor states, network types, DR/BDR, LSA types |
| **Cisco doc** ⭐ | *IP Routing: OSPF Configuration Guide* — chương *Configuring OSPF*. Search: `IOS-XE OSPF configuration guide` |
| **Cisco doc** ⭐⭐ | ***OSPF Design Guide*** — tài liệu kinh điển của Cisco, giải thích **vì sao** có area, DR, LSA types. Search: `cisco ospf design guide` |
| **Cisco doc** ⭐ | *OSPF Neighbor Problems Explained* — troubleshooting guide chính thức, đúng bảng 9 điều kiện adjacency |
| **Cisco doc** | *Why Does the `show ip ospf neighbor` Command Reveal Neighbors in the Init State?* |
| **Cisco doc** | *OSPF Database Explanation Guide* — giải thích từng field của mọi LSA type |
| **Cisco doc** | *Understanding and Configuring the OSPF `network` Command* + *OSPF Cost* |
| **RFC 2328** | OSPFv2 — đọc **Section 7 (Bringing Up Adjacencies)** và **Section 12 (LSA)** nếu muốn nguồn gốc |
| **Cisco Live** ⭐ | Search `Cisco Live OSPF deployment best practices` · `Cisco Live OSPF troubleshooting` — slide PDF chất lượng như sách |
| **NetworkLessons** ⭐ | Loạt bài OSPF (neighbor states, network types, DR/BDR, LSA types) — giải thích rõ nhất trên internet, nhiều bài free |
| **Video** | CBT Nuggets ENCOR — module OSPF · Keith Barker: search `Keith Barker OSPF LSA types`, `Keith Barker OSPF DR BDR` |
| **Wireshark** | Filter `ospf` — bắt gói Hello (xem Router ID, Area, timer, DR/BDR, neighbor list), DBD, LSU. ⭐ **Bắt trên link R1↔R2 và trên bridge để so** |
| **Forum** | https://community.cisco.com — search `ospf stuck exstart mtu`, `ospf 2way drother normal`, `ospf reference bandwidth mismatch` |

---

**➡️ Tiếp theo:** [Module-04B — OSPF: Area type, Summarization, Filtering, OSPFv3](Module-04B-OSPF-Area-Summarization-OSPFv3.md)
*(LSA 4–5–7 · ASBR · Stub/Totally Stub/NSSA · `area range` & `summary-address` · LSA filtering ·
Virtual-link · Authentication · Default route origination · OSPFv3 — **Tuần 8**)*
