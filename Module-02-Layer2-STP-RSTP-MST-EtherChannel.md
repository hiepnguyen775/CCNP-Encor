# Module-02 — Layer 2: STP, RSTP, MST, EtherChannel

> 🧭 **Lộ trình:** Module-01 → `[Bạn đang ở đây] Module-02` → Module-03 (IP Routing) → …
>
> 📊 **Vị trí trong blueprint:** Domain **3.0 Infrastructure (30% — nặng nhất)**, mục
> **3.1 Layer 2** — *troubleshoot static and dynamic 802.1q trunking protocols · static and dynamic
> EtherChannels · configure and verify common Spanning Tree Protocols (RSTP, MST)*.
>
> ⏱️ **Tuần 4–5** · 20 giờ · 2 tuần

---

## ✅ 1. Chuẩn bị trước khi học

| Cần có | Chi tiết |
|---|---|
| **Kiến thức trước** | Module-P0 §2.3 (VLAN/Trunk) và §2.4 (STP từ gốc). ⭐ **Bắt buộc** — module này giả định bạn đã biết bầu Root Bridge, port role, timer |
| **Lab** | 4× vIOS-L2 (switch). Không có image switch → xem §1.1 Plan B |
| **RAM** | 4× 768 MB = **3 GB** ✅ |
| **Thời lượng** | **Tuần 4:** STP sâu + RSTP + Guards · **Tuần 5:** MST + EtherChannel |

### 1.1 Plan B nếu chưa có image vIOS-L2

| Nội dung | Packet Tracer | DevNet Sandbox (Cat9k) | vIOS-L2 |
|---|:---:|:---:|:---:|
| STP/RSTP cơ bản, bầu root, port role | ✅ Tốt | ✅ | ✅ |
| Guards (PortFast/BPDU Guard/Root Guard) | ✅ Được | ✅ | ✅ |
| Loop Guard / UDLD | ⚠️ Hạn chế | ✅ | ✅ |
| **MST** | ⚠️ Hạn chế | ✅ | ✅ |
| EtherChannel LACP/PAgP | ✅ Được | ✅ | ✅ |
| Bắt gói BPDU bằng Wireshark | ❌ | ❌ | ⭐ ✅ |

> 💡 **Khuyến nghị:** làm Tuần 4 bằng Packet Tracer nếu chưa có image (đủ 80%),
> nhưng **cố gắng có vIOS-L2 trước Tuần 5** vì MST và EtherChannel cần output thật.

---

## 📘 2. LÝ THUYẾT — PHẦN A: STP CHUYÊN SÂU

### 2.1 Ôn nhanh (nếu 5 dòng này bạn không trả lời được → quay lại Module-P0 §2.4)

| Câu | Đáp án 1 dòng |
|---|---|
| Bầu Root Bridge bằng gì? | Bridge ID nhỏ nhất = (Priority + Ext System ID) rồi tới MAC |
| Ext System ID là gì? | = VLAN ID. Nên VLAN 10 hiện priority **32778** |
| Cost của link 1 Gbps? | **4** (short mode) |
| STP có mấy state? | 5: Disabled, Blocking, Listening, Learning, Forwarding |
| Convergence direct / indirect? | **30 s** / **50 s** |

---

### 2.2 Cấu trúc BPDU — đọc được là troubleshoot được

BPDU (Bridge Protocol Data Unit) là "phiếu bầu" mà switch gửi cho nhau. Gửi tới địa chỉ
multicast **`01:80:C2:00:00:00`**.

| Trường trong BPDU | Nội dung | Dùng để làm gì |
|---|---|---|
| Protocol ID | `0x0000` | Nhận dạng STP |
| Version | `0` = STP · `2` = RSTP · `3` = MST | ⭐ Phân biệt loại STP |
| BPDU Type | `0x00` = Configuration · `0x80` = TCN | |
| **Flags** | Bit **TC** (Topology Change), **TCA** (TC Acknowledgment). RSTP dùng thêm bit cho role/state/proposal/agreement | ⭐ RSTP dùng nhiều bit hơn |
| **Root ID** | Bridge ID của root **hiện tại** | Switch so sánh để biết ai là root |
| **Root Path Cost** | Tổng cost từ switch gửi về root | Chọn Root Port |
| **Bridge ID** | Bridge ID của switch **đang gửi** | Tie-break |
| **Port ID** | Priority + số port của port gửi | Tie-break cuối |
| Message Age | BPDU này đã "đi" bao xa (tăng mỗi hop) | So với Max Age |
| Max Age | 20 s | Timer |
| Hello Time | 2 s | Timer |
| Forward Delay | 15 s | Timer |

> ⭐ **Điểm quan trọng:** timer (Hello/MaxAge/ForwardDelay) **lấy từ Root Bridge**, không phải
> từ cấu hình local. Muốn đổi timer cho cả mạng → **đổi trên Root Bridge**.
> Đổi trên switch thường thì chỉ có tác dụng nếu nó trở thành root.

#### Superior BPDU vs Inferior BPDU

| Loại | Nghĩa | Hệ quả |
|---|---|---|
| **Superior BPDU** | BPDU có Root ID **tốt hơn** (nhỏ hơn) BPDU hiện tại | Switch chấp nhận root mới → tính lại cả cây |
| **Inferior BPDU** | BPDU có Root ID **kém hơn** | Switch bỏ qua, và gửi lại BPDU tốt hơn cho neighbor |

⭐ Khái niệm **Superior BPDU** là nền của **Root Guard** (§2.6).

---

### 2.3 Topology Change — vì sao mạng "chậm 30 giây" sau khi cắm lại dây

Khi topology đổi, không chỉ port role đổi — mà **bảng MAC phải được dọn**.

**Quy trình STP 802.1D:**

```
1. SW-X phát hiện thay đổi (link up/down)
        ↓
2. SW-X gửi TCN BPDU ra Root Port  ──▶  (hướng về root)
        ↓
3. Switch trung gian nhận TCN → trả TCA → rồi tự gửi TCN tiếp lên root
        ↓
4. ROOT nhận TCN → bật bit TC trong Configuration BPDU
        ↓
5. Root gửi BPDU có bit TC trong (Max Age + Forward Delay) = 20 + 15 = 35 giây
        ↓
6. MỌI switch nhận BPDU có bit TC → giảm MAC aging từ 300 s xuống 15 s (forward delay)
        ↓
7. MAC table được học lại nhanh → mạng ổn định
```

| Vì sao phải làm vậy | Giải thích |
|---|---|
| MAC aging mặc định **300 giây** | Nếu topology đổi mà MAC table vẫn giữ 300s → switch gửi frame ra **port cũ đã bị block** → traffic chết tới 5 phút |
| Giảm xuống **15 giây** | MAC cũ hết hạn nhanh, switch flood để học lại đường mới |

> ⭐ **RSTP làm khác hoàn toàn:** switch phát hiện thay đổi sẽ **flood TC ra mọi hướng ngay**
> (không cần đi qua root), và **xóa thẳng (flush) MAC table** thay vì chỉ giảm aging.
> Đây là một trong những lý do RSTP nhanh hơn.

**Xem TC counter — lệnh troubleshoot rất hữu ích:**
```
show spanning-tree detail | include ieee|occurr|from|is exec
```
→ Nếu số lần topology change **tăng liên tục** = có link đang nhấp nháy (flapping) ở đâu đó.

---

### 2.4 PVST+ — và vấn đề của nó

| | Nội dung |
|---|---|
| **PVST+** | Per-VLAN Spanning Tree Plus — **1 instance STP riêng cho MỖI VLAN** |
| Ưu điểm | ⭐ **Load-balance được**: VLAN 10 root ở SW-A, VLAN 20 root ở SW-B → cả 2 uplink đều dùng |
| Nhược điểm | ⚠️ **Tốn CPU**: 500 VLAN = 500 instance STP = 500 lần tính toán + 500 luồng BPDU |
| BPDU | Gửi trên mỗi VLAN (có tag) |

**Load-balance bằng PVST+ (kỹ thuật thực tế hay dùng):**

```
! Trên SW-A: làm root cho VLAN chẵn
spanning-tree vlan 10,30,50 priority 4096
spanning-tree vlan 20,40,60 priority 8192      ! làm backup root

! Trên SW-B: làm root cho VLAN lẻ
spanning-tree vlan 20,40,60 priority 4096
spanning-tree vlan 10,30,50 priority 8192      ! làm backup root
```

```
       VLAN 10,30,50 →  ┌────────┐  ← VLAN 20,40,60
                        │        │
     [SW-A root chẵn]───┤        ├───[SW-B root lẻ]
                        │        │
                     Uplink A  Uplink B
                     (dùng cho  (dùng cho
                      VLAN chẵn) VLAN lẻ)
```
→ Cả 2 uplink đều có traffic, không có link nào block hoàn toàn.

> ⭐ **Đây là câu trả lời cho "vì sao PVST+ tồn tại dù tốn CPU"** — nó là cách duy nhất
> load-balance L2 trước khi có MST.

---

## 📘 3. LÝ THUYẾT — PHẦN B: RSTP (802.1w)

### 3.1 RSTP nhanh hơn STP nhờ 4 thay đổi

| # | Thay đổi | STP 802.1D | RSTP 802.1w |
|:---:|---|---|---|
| 1 | **Ai tạo BPDU** | Chỉ **root** tạo, switch khác **chuyển tiếp** | ⭐ **Mọi switch tự tạo** BPDU mỗi hello |
| 2 | **BPDU là keepalive** | Không — chờ **Max Age 20 s** | ⭐ Có — mất **3 hello (6 s)** là coi như neighbor chết |
| 3 | **Chuyển state** | Chờ timer (Listening 15 + Learning 15) | ⭐ **Proposal/Agreement handshake** — chuyển gần như tức thì |
| 4 | **Xử lý Topology Change** | Gửi TCN lên root, root bật bit TC 35 s, mọi switch giảm MAC aging | ⭐ Flood TC ra mọi hướng ngay + **flush MAC table** |

### 3.2 Port role & state RSTP

| Port Role | Nghĩa | Tương ứng STP |
|---|---|---|
| **Root Port** | Đường về root tốt nhất | Root Port |
| **Designated Port** | Forward trên 1 segment | Designated Port |
| ⭐ **Alternate Port** | Dự phòng cho **Root Port** — có đường khác về root | Blocking |
| ⭐ **Backup Port** | Dự phòng cho **Designated Port** trên **cùng segment** (chỉ có ở hub/half-duplex) | Blocking |
| Disabled | Port bị shutdown | Disabled |

| Port State RSTP | Learn MAC? | Forward? | Tương ứng STP |
|---|:---:|:---:|---|
| **Discarding** | ❌ | ❌ | Disabled + Blocking + Listening |
| **Learning** | ✅ | ❌ | Learning |
| **Forwarding** | ✅ | ✅ | Forwarding |

> ⭐ **Bẫy đề:** RSTP có **3 state**, không phải 5. Và **Alternate ≠ Backup**:
> - **Alternate** = có đường khác về root (dự phòng Root Port) → **hay gặp**
> - **Backup** = 2 port của **cùng switch** nối vào **cùng segment** → chỉ gặp khi có hub/half-duplex

### 3.3 ⭐ Link Type — quyết định RSTP có nhanh được hay không

| Link Type | Điều kiện | RSTP làm gì |
|---|---|---|
| ⭐ **Edge** | Port bật **PortFast** (nối PC/server) | Lên Forwarding **ngay**, không cần handshake |
| ⭐ **Point-to-point** | **Full-duplex** | Dùng **Proposal/Agreement** → chuyển nhanh (vài chục ms) |
| ⚠️ **Shared** | **Half-duplex** (có hub) | ❌ **KHÔNG dùng được handshake** → rơi về hành vi 802.1D chậm (chờ timer) |

```
! Xem link type
show spanning-tree vlan 10 | include P2p|Shr|Edge

! Đặt tay (thường không cần, IOS tự phát hiện qua duplex)
interface Gi0/1
 spanning-tree link-type point-to-point
 spanning-tree link-type shared
```

> ⭐ **Bài học thực chiến:** một port bị **half-duplex** (do duplex mismatch hoặc cắm vào hub cũ)
> sẽ biến thành **shared link** → RSTP mất khả năng chuyển nhanh trên port đó → hội tụ lại chậm 30–50 s.
> **Duplex mismatch không chỉ gây lỗi CRC, nó còn phá RSTP.**

### 3.4 Proposal / Agreement — cơ chế làm RSTP nhanh

Đây là phần đề ENCOR hay hỏi. Diễn biến khi 1 link mới lên giữa SW-A (gần root) và SW-B:

```
   SW-A (gần root)                      SW-B (xa root)
        │                                    │
   1. Gửi BPDU có bit PROPOSAL ─────────────▶│
        │                                    │
        │                    2. SW-B nhận: "à, đây là đường về root tốt hơn"
        │                       → SW-B thực hiện SYNC:
        │                         · block TẤT CẢ port non-edge designated của mình
        │                         · (port edge/PortFast KHÔNG bị block)
        │                                    │
        │◀──── 3. Gửi lại BPDU có bit AGREEMENT
        │                                    │
   4. SW-A: nhận agreement → chuyển port sang FORWARDING NGAY
        │                                    │
                                        5. SW-B lặp lại quy trình
                                           với các switch phía dưới nó
```

| Bước | Ý nghĩa |
|:---:|---|
| **Proposal** | "Tôi muốn cho port này forward ngay, đồng ý không?" |
| **Sync** | SW-B tự block hết port designated của mình **trước** → đảm bảo **không thể có loop** |
| **Agreement** | "Tôi đã dọn sạch phía sau, bạn forward đi" |

> 🧠 **Vì sao an toàn mà vẫn nhanh:** STP chờ timer vì nó *"không biết phía kia thế nào,
> nên chờ cho chắc"*. RSTP **hỏi thẳng** và bên kia **tự dọn dẹp rồi trả lời**.
> Có xác nhận thì không cần chờ.

### 3.5 Rapid PVST+ vs RSTP

| | RSTP (802.1w) | **Rapid PVST+** |
|---|---|---|
| Chuẩn | IEEE | Cisco |
| Số instance | 1 cho cả mạng | **1 cho mỗi VLAN** |
| Load-balance theo VLAN | ❌ | ✅ |
| Tốn CPU | Ít | Nhiều nếu nhiều VLAN |
| Trên Cisco | Có nhưng ít dùng | ⭐ **Cisco khuyến nghị** cho mạng vừa |

```
! Bật Rapid PVST+
configure terminal
 spanning-tree mode rapid-pvst
end

! Kiểm tra
show spanning-tree summary
```

---

## 📘 4. LÝ THUYẾT — PHẦN C: MST (802.1s)

### 4.1 MST giải quyết vấn đề gì

| Tình huống | PVST+ | MST |
|---|---|---|
| 4 VLAN, 2 nhóm đường đi khác nhau | 4 instance | 2 instance |
| **500 VLAN**, chỉ cần 2 nhóm đường | ⚠️ **500 instance** → CPU nghẹt | ⭐ **2 instance** |
| Load-balance | ✅ | ✅ |

⭐ **Ý tưởng MST:** *hầu hết VLAN trong một mạng đều có cùng topology mong muốn.*
Không cần 500 cây riêng — chỉ cần **nhóm các VLAN có cùng đường đi vào 1 instance**.

```
     PVST+                              MST
  ─────────                          ───────
  VLAN 10 → cây 1                    VLAN 10,30,50,70…250  ┐
  VLAN 20 → cây 2                                          ├─▶ MST Instance 1 (1 cây)
  VLAN 30 → cây 3                    VLAN 20,40,60,80…500  ┐
  ...                                                       ├─▶ MST Instance 2 (1 cây)
  VLAN 500 → cây 500
  = 500 lần tính toán                = 2 lần tính toán
```

### 4.2 ⭐ MST Region — 3 điều PHẢI GIỐNG NHAU

Các switch chỉ ở **cùng một MST region** khi **cả 3** thứ sau khớp chính xác:

| # | Thành phần | Ghi chú |
|:---:|---|---|
| 1 | **Configuration Name** | Tên region, VD `CAMPUS-01`. Phân biệt chữ hoa/thường |
| 2 | **Revision Number** | Số nguyên, VD `1`. Tăng lên mỗi lần đổi mapping (để quản lý) |
| 3 | ⭐ **VLAN-to-Instance Mapping** | VLAN nào thuộc instance nào. **Phải khớp từng VLAN** |

> ⚠️ **Đây là lỗi số 1 khi triển khai MST:** thiếu 1 VLAN trong mapping trên 1 switch →
> switch đó **ra khỏi region** → trở thành **boundary** → cây bị chia đôi, traffic đi đường lạ,
> hoặc block port không mong muốn.
>
> Cisco tính một **digest (hash)** từ mapping và đưa vào BPDU. Lệch 1 VLAN = digest khác = khác region.

### 4.3 Các loại cây trong MST

| Tên | Viết tắt | Là gì |
|---|---|---|
| **IST** | Internal Spanning Tree = **MST0** | ⭐ Cây **bắt buộc có**. Chứa mọi VLAN **chưa được map** vào instance khác. Là cây duy nhất trao đổi BPDU với bên ngoài region |
| **MSTI** | MST Instance (MST1, MST2…) | Các cây do bạn tạo, chỉ tồn tại **trong** region |
| **CST** | Common Spanning Tree | Cây ở **ngoài** region — nhìn cả region như 1 switch ảo |
| **CIST** | Common and Internal Spanning Tree | Tổng thể: CST + IST |

> 🧠 **Cách hiểu:** từ ngoài nhìn vào, **cả region MST giống như MỘT switch khổng lồ**.
> Bên ngoài chỉ nói chuyện với IST (MST0). Bên trong region thì có nhiều cây con (MST1, MST2…).

### 4.4 Boundary Port & PVST Simulation

| Khái niệm | Nghĩa |
|---|---|
| **Boundary port** | Port nối ra ngoài region: sang region MST khác, hoặc sang switch chạy PVST+/RSTP/STP |
| **PVST Simulation** | MST tự "giả vờ" gửi BPDU theo kiểu PVST+ trên boundary port để tương thích. **Mặc định bật** |

```
! Xem port nào là boundary
show spanning-tree mst | include Bound|Boun

! Tắt PVST simulation (nếu chắc chắn bên kia cũng MST)
interface Gi0/1
 no spanning-tree mst simulate pvst
! Hoặc toàn cục
spanning-tree mst simulate pvst global      ! bật (mặc định)
no spanning-tree mst simulate pvst global   ! tắt
```

⚠️ **Lỗi `PVST_PEER_INC` / `simulate pvst inconsistent`:** boundary port nhận BPDU PVST+
không nhất quán → port bị block. Nguyên nhân: bên kia chạy PVST+ nhưng root của các VLAN
không đồng nhất. Xử lý: đảm bảo bên PVST+ có cùng root cho các VLAN thuộc cùng MST instance.

### 4.5 Cấu hình MST

```
configure terminal
!
spanning-tree mode mst
!
spanning-tree mst configuration
 name CAMPUS-01                    ! ⭐ giống nhau MỌI switch
 revision 1                            ! ⭐ giống nhau MỌI switch
 instance 1 vlan 10,30,50              ! ⭐ mapping giống nhau MỌI switch
 instance 2 vlan 20,40,60
 exit
!
! Ép root: SW-A làm root cho MST1, backup cho MST2
spanning-tree mst 1 priority 4096
spanning-tree mst 2 priority 8192
!
end
write memory
```

**Trên SW-B (đối xứng để load-balance):**
```
spanning-tree mst 1 priority 8192
spanning-tree mst 2 priority 4096
```

**Kiểm tra:**

| Lệnh | Xem gì |
|---|---|
| ⭐ `show spanning-tree mst configuration` | **Name, revision, mapping** — lệnh đầu tiên khi troubleshoot MST |
| `show spanning-tree mst configuration digest` | Hash của mapping — **so sánh giữa 2 switch** |
| `show spanning-tree mst` | Tổng quan mọi instance |
| `show spanning-tree mst 1` | Chi tiết instance 1: root, port role |
| `show spanning-tree mst interface Gi0/1` | Port này ở role gì trong từng instance |

**Output mẫu `show spanning-tree mst configuration`:**
```
Name      [CAMPUS-01]
Revision  1     Instances configured 3

Instance  Vlans mapped
--------  ---------------------------------------------------------------------
0         1-9,11-19,21-29,31-39,41-49,51-59,61-4094
1         10,30,50
2         20,40,60
-------------------------------------------------------------------------------
```
⭐ Chú ý: **instance 0 (IST) tự nhận mọi VLAN còn lại**. Bạn không cần map VLAN vào instance 0.

### 4.6 So sánh 3 chế độ — bảng phải thuộc

| | **PVST+** | **Rapid PVST+** | **MST** |
|---|---|---|---|
| Chuẩn | Cisco | Cisco | **IEEE 802.1s** |
| Tốc độ hội tụ | Chậm (30–50 s) | **Nhanh** (vài giây) | **Nhanh** (dùng RSTP bên trong) |
| Số instance | 1 / VLAN | 1 / VLAN | **1 / nhóm VLAN** |
| CPU với 500 VLAN | ⚠️ Rất cao | ⚠️ Rất cao | ⭐ Thấp |
| Load-balance | ✅ | ✅ | ✅ |
| Đa vendor | ❌ | ❌ | ⭐ ✅ |
| Cấu hình | Đơn giản | Đơn giản | **Phức tạp hơn** (phải khớp region) |
| Dùng khi | Mạng nhỏ, ít VLAN | ⭐ Mạng vừa | ⭐ Mạng lớn / nhiều VLAN / đa vendor |
| Số instance tối đa | — | — | Tùy platform (thường 16, một số tới 65) |

---

## 📘 5. LÝ THUYẾT — PHẦN D: BẢO VỆ STP (Guards & UDLD)

### 5.1 Bảng tổng hợp — thuộc bảng này là xong 1/3 câu hỏi L2 của đề

| Tính năng | Đặt ở port nào | Chống / Làm gì | Khi kích hoạt thì | Lệnh |
|---|---|---|---|---|
| **PortFast** | Access port nối **PC/server** | Bỏ Listening/Learning → Forwarding ngay | — | `spanning-tree portfast` |
| **PortFast trunk** | Trunk nối **hypervisor / server ảo hóa** | Như trên, cho port trunk | — | `spanning-tree portfast trunk` |
| **BPDU Guard** | Port có PortFast | Ai cắm **switch** vào port PC → chặn | Port → **err-disable** (tắt hẳn) | `spanning-tree bpduguard enable` |
| ⚠️ **BPDU Filter** | (cẩn thận) | **Không gửi và không nhận** BPDU | — | `spanning-tree bpdufilter enable` |
| **Root Guard** | Port hướng **xuống** switch cấp dưới / sang đối tác | Không cho switch lạ thành root | Port → **root-inconsistent** (block), **tự hồi phục** | `spanning-tree guard root` |
| **Loop Guard** | Port **Root / Alternate** (uplink) | Chống loop khi BPDU **im lặng một chiều** | Port → **loop-inconsistent** (block), **tự hồi phục** | `spanning-tree guard loop` |
| **UDLD** | Link **fiber** (và cả copper) | Phát hiện link **một chiều** ở tầng vật lý | Log (normal) hoặc **err-disable** (aggressive) | `udld port aggressive` |

### 5.2 PortFast — 3 dạng và cái bẫy với ảo hóa

```
! Dạng 1 — access port (phổ biến nhất)
interface Gi0/1
 spanning-tree portfast

! Dạng 2 — TRUNK port (⭐ dùng cho uplink tới hypervisor)
interface Gi0/2
 spanning-tree portfast trunk

! Dạng 3 — bật mặc định cho MỌI access port (tiết kiệm công gõ)
spanning-tree portfast default
spanning-tree portfast bpduguard default      ! ⭐ đi kèm luôn
```

> ⭐ **Điểm liên quan trực tiếp tới công việc của bạn:** port switch nối vào **host ảo hóa**
> (Proxmox/ESXi) thường là **trunk** chở nhiều VLAN. vSwitch bên trong hypervisor
> **không chạy STP** và **không gửi BPDU**. Nếu không bật `portfast trunk`, mỗi lần host reboot,
> port phải chờ 30 s mới forward → **VM mất mạng 30 giây mỗi lần host lên**.
>
> Nhưng ⚠️ **vẫn phải bật BPDU Guard** — nếu ai đó cấu hình sai làm host trở thành switch
> (bridge 2 NIC), BPDU Guard sẽ chặn loop ngay.

### 5.3 ⚠️ BPDU Filter — tính năng nguy hiểm nhất

Đây là chỗ đề hay gài, và cũng là chỗ gây sự cố thật.

| Cấu hình ở đâu | Hành vi | Mức nguy hiểm |
|---|---|---|
| ⛔ **Interface level**<br>`spanning-tree bpdufilter enable` | **Không gửi VÀ không nhận** BPDU trên port đó → **STP bị vô hiệu hoàn toàn** trên port | 🔴 **Rất nguy hiểm** — cắm switch vào port này = loop, không ai chặn |
| ✅ **Global level**<br>`spanning-tree portfast bpdufilter default` | Chỉ tác dụng lên **port PortFast**. Gửi vài BPDU đầu rồi ngừng gửi. **Nếu NHẬN được BPDU → tự tắt PortFast và trở về STP bình thường** | 🟢 An toàn hơn nhiều |

> ⛔ **Nguyên tắc:** trên production, **không dùng BPDU Filter ở interface level** trừ khi có
> lý do rất cụ thể và bạn hiểu hết rủi ro. Nếu chỉ muốn port lên nhanh → dùng **PortFast**.
> Nếu muốn chống switch lạ → dùng **BPDU Guard**.
>
> 🎓 **Đề ENCOR hỏi:** *"Sự khác biệt giữa BPDU Filter ở interface và global?"* →
> Interface = tắt STP hẳn (nguy hiểm). Global = chỉ trên PortFast port, nhận BPDU thì tự hồi phục.

### 5.4 Root Guard vs Loop Guard — cặp dễ lẫn nhất

| | **Root Guard** | **Loop Guard** |
|---|---|---|
| **Vấn đề nó chống** | Switch lạ / switch không mong muốn **trở thành Root Bridge** | Loop do **link một chiều** (BPDU đột ngột im lặng) |
| **Kích hoạt khi** | Nhận được **Superior BPDU** trên port | **Ngừng nhận** BPDU trên Root/Alternate port |
| **Trạng thái port** | `ROOT_Inc` (root-inconsistent) → block | `LOOP_Inc` (loop-inconsistent) → block |
| **Đặt ở đâu** | Port **hướng xuống** (downstream), port nối đối tác/khách | Port **hướng lên** (uplink) = Root Port & Alternate Port |
| **Tự hồi phục?** | ✅ Có — khi hết Superior BPDU | ✅ Có — khi BPDU quay lại |
| **Câu thần chú** | *"Không cho ai lạ làm vua"* | *"Im lặng bất thường thì đừng vội forward"* |

**Vì sao Loop Guard cần thiết — tình huống thật:**

```
Bình thường:                        Khi BPDU im lặng một chiều:
  SW-A ═══BPDU═══▶ SW-B               SW-A ──✂ (không gửi được BPDU do lỗi
       (Alternate port                       software/fiber một chiều)
        của SW-B đang block)               │
                                           ▼
                                  SW-B: "20 s không có BPDU → chắc link chết
                                         → port Alternate thành Designated
                                         → FORWARDING"
                                           │
                                           ▼
                                  ⚠️ Nhưng link vẫn UP về mặt vật lý
                                     → LOOP xuất hiện, không ai phát hiện
```

**Với Loop Guard:** thay vì chuyển sang Forwarding, SW-B đưa port vào `LOOP_Inc` (block)
→ **loop không bao giờ hình thành**.

```
! Bật per-interface (uplink)
interface Gi0/1
 spanning-tree guard loop

! Bật toàn cục cho mọi port P2P (thực tế hay dùng)
spanning-tree loopguard default
```

⚠️ **Không bật Root Guard và Loop Guard trên cùng 1 port** — chúng loại trừ nhau về mục đích
(một cái cho downstream, một cái cho upstream).

### 5.5 UDLD — bảo vệ ở tầng thấp hơn STP

| | Nội dung |
|---|---|
| Là gì | Protocol L2 của Cisco, gửi **echo** chứa Device ID + Port ID của mình |
| Nguyên lý | Nếu echo tôi gửi ra **không quay lại kèm thông tin của tôi** → link một chiều |
| Timer mặc định | Gửi message mỗi **15 giây** |
| Dùng cho | ⭐ **Link fiber** (nơi TX/RX là 2 sợi riêng — dễ đứt một chiều) |

| Mode | Khi phát hiện **link một chiều rõ ràng** | Khi chỉ **mất thông tin UDLD** (timeout) |
|---|---|---|
| **Normal** | **err-disable** port | Chỉ log, port giữ nguyên trạng thái (undetermined) |
| ⭐ **Aggressive** | **err-disable** port | Thử lại **8 lần** → vẫn không được → **err-disable** port |

```
! Toàn cục — chỉ tác dụng lên port FIBER
udld enable                      ! normal mode
udld aggressive                  ! aggressive mode

! Per-interface — tác dụng cả copper
interface Gi0/1
 udld port                       ! normal
 udld port aggressive            ! ⭐ aggressive

! Kiểm tra
show udld
show udld Gi0/1
show udld neighbors

! Bật lại port bị UDLD tắt
udld reset
```

#### ⭐ Loop Guard vs UDLD — bảng đề hay hỏi

| | **Loop Guard** | **UDLD** |
|---|---|---|
| Tầng hoạt động | **STP** (dựa vào BPDU) | **L2 độc lập** (protocol riêng) |
| Phạm vi | Per-VLAN (theo instance STP) | Per-port (toàn bộ port) |
| Phát hiện | BPDU ngừng đến | Echo không quay lại |
| Chống được lỗi software STP | ✅ | ⚠️ Không trực tiếp |
| Chống được đứt fiber một chiều | ✅ (gián tiếp) | ⭐ ✅ (trực tiếp, nhanh hơn) |
| Cần bên kia hỗ trợ? | Không | ⭐ **Có** — bên kia phải chạy UDLD |
| Khuyến nghị Cisco | ⭐ **Dùng CẢ HAI** | ⭐ **Dùng CẢ HAI** |

### 5.6 Err-disable & tự động hồi phục

Khi BPDU Guard / UDLD / Port Security kích hoạt, port vào trạng thái **err-disable** (tắt hẳn).
Mặc định **phải vào tay `shutdown` / `no shutdown`** mới bật lại.

```
! Xem port nào bị err-disable và VÌ SAO
show interfaces status err-disabled

! Xem cấu hình auto-recovery
show errdisable recovery

! Bật tự hồi phục cho nguyên nhân cụ thể
configure terminal
 errdisable recovery cause bpduguard
 errdisable recovery cause udld
 errdisable recovery cause link-flap
 errdisable recovery interval 300          ! thử lại sau 300 s (mặc định 300)
end
```

**Output mẫu:**
```
SW1# show interfaces status err-disabled
Port      Name               Status       Reason               Err-disabled Vlans
Gi0/1     PC-Ke-toan         err-disabled bpduguard
```
⭐ Cột `Reason` cho biết chính xác tính năng nào đã tắt port → đi thẳng vào nguyên nhân.

> 💡 **Thực chiến:** bật `errdisable recovery cause bpduguard` với interval 300 s là cân bằng tốt:
> loop bị chặn ngay, nhưng nếu là sự cố nhất thời thì port tự lên lại sau 5 phút,
> không cần người ra tủ mạng lúc 2 giờ sáng.

---

## 📘 6. LÝ THUYẾT — PHẦN E: ETHERCHANNEL

### 6.1 EtherChannel là gì và giải quyết vấn đề gì

| Vấn đề | Không có EtherChannel | ⭐ Có EtherChannel |
|---|---|---|
| 2 link 1G giữa 2 switch | STP **block 1 link** → chỉ dùng 1 Gbps | **Gộp thành 1 link logic 2 Gbps** |
| Link chính đứt | Chờ STP hội tụ (vài giây → 50 s) | **Không có TC** — link còn lại gánh ngay, dưới 1 giây |
| STP nhìn thấy | 2 port riêng | ⭐ **1 port logic duy nhất** → không có loop → không block |

```
   Không có EtherChannel              Có EtherChannel
   ─────────────────────              ───────────────
   SW-A ══════ SW-B                   SW-A ══════ SW-B
        ┄┄┄┄┄┄  ← STP block                ══════  ← cả 2 đều forward
                                      (STP thấy là 1 port: Po1)
```

### 6.2 Ba cách tạo EtherChannel

| Protocol | Chuẩn | Mode | Ghi chú |
|---|---|---|---|
| **LACP** | ⭐ IEEE **802.3ad / 802.1AX** | `active` · `passive` | **Đa vendor** — dùng cái này |
| **PAgP** | Cisco độc quyền | `desirable` · `auto` | Chỉ Cisco–Cisco |
| **Static** | Không có protocol | `on` | Không đàm phán → dễ tạo loop nếu cấu hình lệch |

#### ⭐ Bảng tương thích mode — PHẢI THUỘC (đề hỏi trực tiếp)

**LACP:**

| | `active` | `passive` |
|---|:---:|:---:|
| **`active`** | ✅ **Bundle** | ✅ **Bundle** |
| **`passive`** | ✅ **Bundle** | ❌ **KHÔNG** |

**PAgP:**

| | `desirable` | `auto` |
|---|:---:|:---:|
| **`desirable`** | ✅ **Bundle** | ✅ **Bundle** |
| **`auto`** | ✅ **Bundle** | ❌ **KHÔNG** |

**Static (`on`):**

| | `on` | `active`/`passive` | `desirable`/`auto` |
|---|:---:|:---:|:---:|
| **`on`** | ✅ **Bundle** | ❌ | ❌ |

> ⭐ **Quy tắc nhớ 1 câu:** *phải có **ít nhất một bên chủ động***.
> `passive+passive` ❌ · `auto+auto` ❌ (cả hai đều chờ được mời).
> Và **`on` chỉ bắt tay với `on`** — trộn `on` với LACP/PAgP là **không bundle**,
> port thành individual → ⚠️ **có thể gây loop**.
>
> 💡 Giống hệt bảng DTP ở Module-P0 §2.3 — cùng một logic "ai chủ động".

```
! LACP (khuyến nghị)
interface range GigabitEthernet0/1 - 2
 channel-protocol lacp
 channel-group 1 mode active
!
! PAgP
interface range GigabitEthernet0/1 - 2
 channel-protocol pagp
 channel-group 1 mode desirable
!
! Static
interface range GigabitEthernet0/1 - 2
 channel-group 1 mode on
```

### 6.3 ⭐ Điều kiện bundle — 6 thứ phải GIỐNG NHAU

Nếu 1 trong 6 thứ này lệch giữa các member port → port **không vào bundle**
(thành `suspended` hoặc `individual`).

| # | Phải giống nhau | Kiểm tra bằng |
|:---:|---|---|
| 1 | **Speed** | `show interfaces status` |
| 2 | **Duplex** | `show interfaces status` |
| 3 | **Switchport mode** (access hay trunk) | `show interfaces Gi0/1 switchport` |
| 4 | **Native VLAN** (nếu trunk) | `show interfaces trunk` |
| 5 | **Allowed VLAN list** (nếu trunk) | ⭐ `show interfaces trunk` — hay lệch nhất |
| 6 | **Access VLAN** (nếu access) | `show vlan brief` |
| + | Trunk encapsulation · MTU · không trộn L2/L3 | |

> ⚠️ **Lỗi phổ biến nhất khi làm EtherChannel:** cấu hình xong `channel-group` rồi mới sửa
> `switchport trunk allowed vlan` trên **1 port** → port đó rơi ra khỏi bundle.
>
> ⭐ **Cách làm đúng:** **luôn cấu hình trên `interface Port-channel1`**, không cấu hình
> trên member port. Lệnh trên Port-channel tự động áp xuống mọi member.

```
! ✅ CÁCH ĐÚNG
interface range GigabitEthernet0/1 - 2
 channel-group 1 mode active           ! chỉ gõ dòng này ở member port
!
interface Port-channel1                ! ⭐ mọi cấu hình khác gõ Ở ĐÂY
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 switchport trunk native vlan 999
 switchport nonegotiate
```

### 6.4 EtherChannel L2 vs L3

| | **L2 EtherChannel** | **L3 EtherChannel** |
|---|---|---|
| Dùng ở | Switch–switch, chở VLAN | Switch L3 ↔ router, hoặc core L3 |
| Cấu hình | `switchport mode trunk` trên Po | `no switchport` + `ip address` trên Po |
| STP | Tham gia STP như 1 port | Không tham gia STP (là L3) |

```
! L3 EtherChannel
interface range GigabitEthernet0/1 - 2
 no switchport                          ! ⭐ phải làm trên MEMBER trước
 channel-group 1 mode active
!
interface Port-channel1
 no switchport
 ip address 10.0.0.1 255.255.255.252
 no shutdown
```
> ⚠️ Thứ tự quan trọng: `no switchport` trên **member port TRƯỚC**, rồi mới `channel-group`.
> Làm ngược sẽ lỗi.

### 6.5 Load-balancing — vì sao 3 link chia tải không đều

```
! Xem thuật toán hiện tại
show etherchannel load-balance

! Đổi (global, không phải per-port-channel trên nhiều platform)
port-channel load-balance src-dst-ip
```

| Thuật toán | Hash theo | Tốt cho |
|---|---|---|
| `src-mac` | MAC nguồn | Nhiều client → 1 server |
| `dst-mac` | MAC đích | 1 server → nhiều client |
| `src-dst-mac` | Cả hai MAC | Traffic cùng subnet |
| `src-ip` | IP nguồn | |
| `dst-ip` | IP đích | |
| ⭐ `src-dst-ip` | Cả hai IP | **Thường tốt nhất** cho traffic qua router |
| `src-dst-mixed-ip-port` | IP + **port L4** | ⭐ Phân tán tốt nhất — nhiều flow từ cùng cặp IP |

#### ⭐ Vì sao nên dùng 2, 4 hoặc 8 link (đề hay hỏi)

Hash cho ra kết quả rồi chia vào **8 "gáo"** (bucket). Số bucket được chia cho số link:

| Số link | Bucket mỗi link | Đều không? |
|:---:|---|:---:|
| **2** | 4 : 4 | ✅ **Đều** |
| 3 | 3 : 3 : 2 | ⚠️ Lệch |
| **4** | 2 : 2 : 2 : 2 | ✅ **Đều** |
| 5 | 2:2:2:1:1 | ⚠️ Lệch |
| 6 | 2:2:1:1:1:1 | ⚠️ Lệch |
| 7 | 2:1:1:1:1:1:1 | ⚠️ Lệch |
| **8** | 1 mỗi link | ✅ **Đều** |

> ⭐ **Quy tắc thực chiến:** dùng **2, 4, hoặc 8** link trong 1 EtherChannel.
> 3 link không phải là "1.5 lần tốt hơn 2 link" — nó là "2 link + 1 link chạy non tải".

### 6.6 Tính năng LACP nâng cao

| Tính năng | Lệnh | Tác dụng |
|---|---|---|
| **LACP rate fast** | `lacp rate fast` (trên member port) | Gửi LACP PDU mỗi **1 s** thay vì 30 s → phát hiện lỗi nhanh (3 s thay vì 90 s) |
| **min-links** | `port-channel min-links 2` (trên Po) | Bundle chỉ **up** khi có tối thiểu N link. Tránh 1 link gánh tải của 8 |
| **max-bundle** | `lacp max-bundle 4` (trên Po) | Tối đa N link **active**, còn lại thành **hot-standby** |
| **port-priority** | `lacp port-priority 100` | Quyết định link nào active, link nào standby (số nhỏ = ưu tiên) |
| **system-priority** | `lacp system-priority 100` (global) | Quyết định switch nào là "decider" của bundle |
| **Misconfig guard** | `spanning-tree etherchannel guard misconfig` (global) | ⭐ Phát hiện EtherChannel cấu hình lệch → err-disable, chống loop |

> ⭐ **`spanning-tree etherchannel guard misconfig` nên bật luôn.** Nó bảo vệ khỏi tình huống
> nguy hiểm nhất: một bên `on` (static), một bên chưa cấu hình → bên chưa cấu hình thấy 2 port riêng
> → **loop**.

### 6.7 Đọc `show etherchannel summary` — lệnh quan trọng nhất

```
SW1# show etherchannel summary
```
**Output mẫu:**
```
Flags:  D - down        P - bundled in port-channel
        I - stand-alone s - suspended
        H - Hot-standby (LACP only)
        R - Layer3      S - Layer2
        U - in use      f - failed to allocate aggregator
        M - not in use, minimum links not met
        u - unsuitable for bundling
        w - waiting to be aggregated
        d - default port

Number of channel-groups in use: 1
Number of aggregators:           1

Group  Port-channel  Protocol    Ports
------+-------------+-----------+----------------------------------------------
1      Po1(SU)         LACP      Gi0/1(P)    Gi0/2(P)
```

⭐ **Bảng dịch flag — học bảng này là troubleshoot được 90% lỗi EtherChannel:**

| Flag Port-channel | Nghĩa | Đánh giá |
|---|---|---|
| `(SU)` | **S**=Layer2 + **U**=in use | ✅ **Đúng — mục tiêu** |
| `(RU)` | **R**=Layer3 + **U**=in use | ✅ Đúng (L3 EtherChannel) |
| `(SD)` | Layer2 + **D**own | ❌ Bundle down |
| `(SM)` | Layer2 + **M** = minimum links not met | ⚠️ Chưa đủ số link theo `min-links` |

| Flag Port | Nghĩa | Nguyên nhân |
|---|---|---|
| ⭐ `(P)` | **bundled** — đã vào bundle | ✅ **Đúng** |
| ⚠️ `(I)` | **stand-alone / individual** — LACP không bắt tay được, port hoạt động **độc lập** | Bên kia chưa cấu hình LACP, hoặc bên kia dùng `on` (static) → ⚠️ **NGUY CƠ LOOP** |
| ⚠️ `(s)` | **suspended** — LACP cấu hình nhưng partner không phản hồi gì | Bên kia chưa cấu hình gì cả |
| `(H)` | **Hot-standby** — dự phòng nóng | Do `lacp max-bundle` |
| `(D)` | **down** | Port down vật lý |
| `(w)` | waiting to be aggregated | Đang đàm phán, chờ vài giây |
| `(u)` | **unsuitable for bundling** | ⭐ **Tham số lệch** — kiểm tra 6 điều kiện ở §6.3 |

> ⭐ **`(I)` vs `(s)` — phân biệt để tìm nhanh nguyên nhân:**
> - `(s)` **suspended** = "tôi gửi LACP mà **không ai trả lời**" → bên kia chưa cấu hình gì
> - `(I)` **individual** = "LACP có hoạt động nhưng **không thỏa thuận được**" → bên kia dùng `on`,
>   hoặc tham số lệch. **Đây là trạng thái nguy hiểm** vì port vẫn forward độc lập → có thể loop

**Các lệnh kiểm tra khác:**
```
show etherchannel summary                   ! ⭐ lệnh đầu tiên
show etherchannel 1 detail                  ! chi tiết group 1
show etherchannel 1 port-channel            ! thông tin port-channel
show interfaces Port-channel1               ! như 1 interface thường
show interfaces Port-channel1 etherchannel
show lacp neighbor                          ! ⭐ thấy partner không?
show lacp counters                          ! LACP PDU gửi/nhận
show pagp neighbor
show etherchannel load-balance
```

---

## 📖 7. HIỂU RÕ HƠN — mô hình tư duy

### 7.1 RSTP nhanh hơn vì "hỏi thẳng" thay vì "chờ cho chắc"

**STP như người mới đi làm, quá cẩn thận:**
> "Tôi nghĩ đường này thông rồi, nhưng biết đâu phía kia còn ai đang đi.
> Thôi tôi **đợi 15 giây** rồi lại **đợi 15 giây nữa** cho chắc."

**RSTP như người có kinh nghiệm, biết cách xác nhận:**
> "Này, tôi định cho xe đi qua đây, bạn dọn đường phía bạn chưa?" *(**Proposal**)*
> — "Tôi vừa **chặn hết các lối khác của tôi** rồi, bạn đi đi." *(**Sync** rồi **Agreement**)*
> → Đi ngay, không cần đợi.

🧠 **Một câu để nhớ:** *STP chờ vì không dám hỏi. RSTP hỏi rồi đi ngay.
Có xác nhận thì không cần timer.*

**Và đây là lý do `shared link` (half-duplex) phá RSTP:** trên môi trường half-duplex,
bạn không thể "vừa hỏi vừa nghe" — nên không handshake được, phải quay về chờ timer.

### 7.2 MST như gộp chuyến xe bus

Bạn quản lý tuyến xe cho 500 khu phố:

| Cách làm | Kết quả |
|---|---|
| **PVST+** — mỗi khu phố **1 tuyến xe riêng** | 500 tuyến, 500 tài xế, 500 lộ trình phải tính. Chính xác nhưng **tốn kém khủng khiếp** |
| ⭐ **MST** — nhận ra *"250 khu ở phía Đông đi cùng đường, 250 khu phía Tây đi cùng đường"* | **2 tuyến xe**, 2 lộ trình. Vẫn phục vụ đủ 500 khu |

Và **MST Region** = *"chúng ta phải cùng thống nhất **khu nào đi tuyến nào**"*.
Nếu một tài xế có bảng phân tuyến khác → anh ta **không thuộc công ty này nữa** (ra khỏi region)
→ hành khách bị lạc.

🧠 **Một câu để nhớ:** *MST không giảm số VLAN, nó giảm **số cây phải tính**.
Và giá phải trả là: mọi switch bắt buộc có **cùng bảng phân nhóm** (name + revision + mapping).*

### 7.3 Root Guard vs Loop Guard — hai loại cửa khác nhau

| | Root Guard | Loop Guard |
|---|---|---|
| Vị trí | ⬇️ **Cửa hướng ra ngoài / xuống dưới** | ⬆️ **Cửa hướng lên trên (về nhà)** |
| Câu nói | *"Ngoài kia có ai tự nhận là vua thì **chặn lại**"* | *"Đường về nhà **im lặng bất thường** → đừng vội tin là thông"* |
| Chống | Kẻ lạ chiếm quyền | Ảo giác "đường đã thông" |

🧠 **Một câu để nhớ:** *Root Guard bảo vệ **quyền lực** (ai làm root). Loop Guard bảo vệ khỏi
**sự im lặng lừa dối** (BPDU mất mà link vẫn up).*

### 7.4 EtherChannel như gộp làn đường

**Không có EtherChannel:** 2 làn đường song song, nhưng luật giao thông (STP) sợ tai nạn
nên **đóng 1 làn**. Bạn có 2 làn mà chỉ dùng được 1.

**Có EtherChannel:** hai làn được **sơn lại thành một đường lớn có 2 làn**.
Luật giao thông giờ chỉ thấy **một con đường** → không cần đóng làn nào.

**Load-balancing hash** = cách phân xe vào làn nào. Và đây là điểm quan trọng:
> **Xe cùng một chuyến (cùng flow) luôn đi cùng làn** — để không bị đến sai thứ tự.
> Vì thế **một chuyến xe siêu tải (elephant flow) không thể chia ra 2 làn.**

🧠 **Một câu để nhớ:** *EtherChannel tăng **tổng băng thông**, không tăng băng thông của **một flow**.
2 link 1G ≠ 1 link 2G cho một file transfer duy nhất.*

### 7.5 Vì sao `(I)` individual đáng sợ hơn `(s)` suspended

| | `(s)` suspended | `(I)` individual |
|---|---|---|
| Port có forward traffic? | ❌ **Không** | ⚠️ **CÓ — forward độc lập** |
| Nguy cơ loop | Không (port không hoạt động) | ⭐ **CÓ** |
| Ví von | Cánh cửa **khóa lại** | Cánh cửa **mở tự do, không ai canh** |

🧠 **Một câu để nhớ:** *`suspended` là hệ thống tự bảo vệ (khóa cửa lại).
`individual` là hệ thống nói "tôi bỏ cuộc, cứ đi tự do" — và đó là lúc loop xuất hiện.
Vì vậy phải bật `spanning-tree etherchannel guard misconfig`.*

---

## 🧪 8. LAB — TUẦN 4: STP · RSTP · GUARDS

### LAB 02-1 — Topology chuẩn campus (4 switch)

#### Topology

```
              ╔═══════════════════════════════╗
              ║   TẦNG DISTRIBUTION           ║
              ║                               ║
              ║   [SW-D1]═══Gi0/3═══[SW-D2]   ║   ← link giữa 2 dist
              ║    │  │              │  │     ║
              ╚════│══│══════════════│══│═════╝
                   │  └──────┐  ┌────┘  │
              Gi0/1│    Gi0/2│  │Gi0/1  │Gi0/2
                   │         │  │       │
              ┌────┴─────────┴──┴───────┴────┐
              │  [SW-A1]        [SW-A2]      │  ← TẦNG ACCESS
              │   Gi0/3 → PC      Gi0/3 → PC │
              └──────────────────────────────┘
```

| Link | Đầu A | Đầu B | Ghi chú |
|---|---|---|---|
| 1 | SW-D1 Gi0/3 | SW-D2 Gi0/3 | Link giữa 2 distribution |
| 2 | SW-A1 Gi0/1 | SW-D1 Gi0/1 | Uplink A1 → D1 |
| 3 | SW-A1 Gi0/2 | SW-D2 Gi0/1 | Uplink A1 → D2 |
| 4 | SW-A2 Gi0/1 | SW-D1 Gi0/2 | Uplink A2 → D1 |
| 5 | SW-A2 Gi0/2 | SW-D2 Gi0/2 | Uplink A2 → D2 |
| 6 | SW-A1 Gi0/3 | PC1 (VPCS) | Access VLAN 10 |
| 7 | SW-A2 Gi0/3 | PC2 (VPCS) | Access VLAN 10 |

**RAM: 4× 768 MB = 3 GB** ✅ · Topology này **có vòng lặp** (cố ý) — đây là topology campus thật.

#### Bước 1 — Cấu hình nền (làm giống nhau, chỉ đổi hostname)

```
enable
configure terminal
!
hostname SW-D1                             ! đổi theo từng switch
no ip domain lookup
!
vlan 10
 name USERS
vlan 20
 name SERVERS
vlan 999
 name NATIVE-UNUSED                        ! ⭐ native VLAN "rác"
exit
!
line con 0
 exec-timeout 0 0
 logging synchronous
!
end
write memory
```

#### Bước 2 — Cấu hình trunk (mọi link switch–switch)

**Trên SW-D1:**
```
configure terminal
interface range GigabitEthernet0/1 - 3
 description ---> TRUNK
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk allowed vlan 10,20
 switchport trunk native vlan 999
 switchport nonegotiate
 no shutdown
end
```

**Trên SW-D2:** giống hệt (Gi0/1–3).

**Trên SW-A1 và SW-A2:**
```
configure terminal
! Uplink
interface range GigabitEthernet0/1 - 2
 description ---> UPLINK TRUNK
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk allowed vlan 10,20
 switchport trunk native vlan 999
 switchport nonegotiate
 no shutdown
!
! Port PC
interface GigabitEthernet0/3
 description ---> PC
 switchport mode access
 switchport access vlan 10
 no shutdown
end
write memory
```

✅ **Checkpoint:** `show interfaces trunk` trên mọi switch → mọi link switch–switch đều `trunking`,
allowed vlan `10,20`, native vlan `999`.

#### Bước 3 — Quan sát STP TRƯỚC khi can thiệp

```
SW-D1# show spanning-tree vlan 10
```

**Điền bảng — chạy lệnh trên cả 4 switch:**

| Switch | MAC address | Là Root? | Root Port | Port Blocking |
|---|---|:---:|---|---|
| SW-D1 | | | | |
| SW-D2 | | | | |
| SW-A1 | | | | |
| SW-A2 | | | | |

```
! Xem nhanh port nào bị block toàn mạng
SW-A1# show spanning-tree vlan 10 | include BLK|Altn|Desg|Root
```

⚠️ **Nhận xét bạn phải rút ra:** root hiện tại là switch có **MAC nhỏ nhất** —
rất có thể là một **switch ACCESS**, không phải distribution. **Đây là thiết kế sai.**

```
! Chứng minh: đếm số hop từ SW-A2 về root
SW-A2# show spanning-tree vlan 10 | include Root ID|Cost
```

#### Bước 4 — ⭐ Ép root đúng thiết kế + backup root

```
! SW-D1 — root chính cho VLAN 10, backup cho VLAN 20
SW-D1(config)# spanning-tree vlan 10 priority 4096
SW-D1(config)# spanning-tree vlan 20 priority 8192

! SW-D2 — root chính cho VLAN 20, backup cho VLAN 10
SW-D2(config)# spanning-tree vlan 20 priority 4096
SW-D2(config)# spanning-tree vlan 10 priority 8192
```

**Kiểm tra:**
```
SW-D1# show spanning-tree vlan 10 | include Root|priority
```
**Output mẫu:**
```
  Root ID    Priority    4106
             Address     0c:1a:2b:00:d1:00
             This bridge is the root
  Bridge ID  Priority    4106  (priority 4096 sys-id-ext 10)
```
✅ `4106 = 4096 + 10`.

```
SW-D1# show spanning-tree vlan 20 | include Root ID|This bridge
```
✅ VLAN 20: SW-D1 **không** là root (SW-D2 là root).

**Xác nhận load-balancing đã hoạt động:**
```
SW-A1# show spanning-tree vlan 10 | include Root FWD|Altn
SW-A1# show spanning-tree vlan 20 | include Root FWD|Altn
```
⭐ **Kết quả mong đợi:** Root Port của **VLAN 10** và **VLAN 20** là **2 port khác nhau**
→ cả 2 uplink đều có traffic.

✅ **Checkpoint bước 4:**

| Kiểm tra | Mong đợi |
|---|---|
| VLAN 10: root = SW-D1 | ✅ |
| VLAN 20: root = SW-D2 | ✅ |
| Trên SW-A1: Root Port của VLAN 10 ≠ Root Port của VLAN 20 | ⭐ ✅ Load-balance |
| Đúng 1 port block mỗi VLAN trên mỗi switch access | ✅ |

#### Bước 5 — Bảo vệ STP: 4 lớp Guard

**a) PortFast + BPDU Guard trên port PC:**
```
! SW-A1 và SW-A2
configure terminal
interface GigabitEthernet0/3
 spanning-tree portfast
 spanning-tree bpduguard enable
end
```

Hoặc cách thực chiến (bật mặc định toàn switch):
```
configure terminal
 spanning-tree portfast default
 spanning-tree portfast bpduguard default
end
```

**b) Root Guard trên port hướng xuống access (trên distribution):**
```
! SW-D1
configure terminal
interface range GigabitEthernet0/1 - 2
 description ---> DOWN to ACCESS - Root Guard
 spanning-tree guard root
end
```
Làm tương tự trên SW-D2.

**c) Loop Guard trên uplink (trên access):**
```
! SW-A1 và SW-A2
configure terminal
interface range GigabitEthernet0/1 - 2
 description ---> UPLINK - Loop Guard
 spanning-tree guard loop
end
```
Hoặc toàn cục: `spanning-tree loopguard default`

**d) UDLD + errdisable recovery + misconfig guard:**
```
configure terminal
 udld aggressive                                       ! link fiber
 spanning-tree etherchannel guard misconfig            ! ⭐ chuẩn bị cho tuần 5
 errdisable recovery cause bpduguard
 errdisable recovery cause udld
 errdisable recovery interval 300
end
write memory
```

**Kiểm tra:**
```
show spanning-tree summary
```
**Output mẫu:**
```
Switch is in rapid-pvst mode
Root bridge for: VLAN0010
Extended system ID           is enabled
Portfast Default             is enabled
PortFast BPDU Guard Default  is enabled
Portfast BPDU Filter Default is disabled
Loopguard Default            is disabled
EtherChannel misconfig guard is enabled
UplinkFast                   is disabled
BackboneFast                 is disabled
```
⭐ Đọc bảng này để xác nhận mọi guard đã bật đúng.
Chú ý: `BPDU Filter Default is disabled` — **đúng, không được bật cái này**.

```
show errdisable recovery
show udld
show spanning-tree interface Gi0/1 detail | include guard|Guard
```

✅ **Checkpoint bước 5:** `show spanning-tree summary` cho thấy PortFast Default + BPDU Guard Default
đã bật, BPDU Filter Default **tắt**, misconfig guard bật.

#### Bước 6 — ⭐ TEST TỪNG GUARD (phần giá trị nhất)

Không test thì bạn chỉ *biết* guard tồn tại, chứ chưa *thấy* nó làm gì.

**Test 1 — BPDU Guard**

Mô phỏng "ai đó cắm switch vào port PC":
1. Trong EVE-NG, thêm 1 vIOS-L2 mới tên `SW-ROGUE`
2. Nối `SW-ROGUE Gi0/0` ↔ `SW-A1 Gi0/3` (port PC, đang có PortFast + BPDU Guard)
3. Trên SW-ROGUE: cấu hình `vlan 10`, `interface Gi0/0` → `switchport mode trunk` → `no shut`

**Trên SW-A1 quan sát:**
```
SW-A1#
%SPANTREE-2-BLOCK_BPDUGUARD: Received BPDU on port GigabitEthernet0/3 with BPDU Guard enabled.
                             Disabling port.
%PM-4-ERR_DISABLE: bpduguard error detected on Gi0/3, putting Gi0/3 in err-disable state
```
```
SW-A1# show interfaces status err-disabled
Port      Name               Status       Reason               Err-disabled Vlans
Gi0/3     PC                 err-disabled bpduguard
```
✅ **Checkpoint:** port bị `err-disable`, `Reason = bpduguard`. **Loop bị chặn trước khi hình thành.**

**Bật lại port:**
```
SW-A1(config)# interface Gi0/3
SW-A1(config-if)# shutdown
SW-A1(config-if)# no shutdown
```
(hoặc chờ 300 s để `errdisable recovery` tự bật lại)

---

**Test 2 — Root Guard**

Mô phỏng "switch access cố chiếm quyền root":
```
! Trên SW-A1 — cố tình đặt priority thấp nhất để chiếm root
SW-A1(config)# spanning-tree vlan 10 priority 0
```

**Trên SW-D1 (có Root Guard ở port hướng xuống) quan sát:**
```
SW-D1#
%SPANTREE-2-ROOTGUARD_BLOCK: Root guard blocking port GigabitEthernet0/1 on VLAN0010.
```
```
SW-D1# show spanning-tree inconsistentports
```
**Output mẫu:**
```
Name                 Interface              Inconsistency
-------------------- ---------------------- ------------------
VLAN0010             GigabitEthernet0/1     Root Inconsistent

Number of inconsistent ports (segments) in the system : 1
```
```
SW-D1# show spanning-tree vlan 10 | include ROOT_Inc|BKN
Gi0/1               Desg BKN*4         128.2    P2p *ROOT_Inc
```

⭐ **Bài học:** SW-A1 **không trở thành root được**. Port bị block cho tới khi hết Superior BPDU.

**Hoàn tác:**
```
SW-A1(config)# spanning-tree vlan 10 priority 32768
! Hoặc: no spanning-tree vlan 10 priority
```
Sau vài giây, kiểm tra lại — port tự hồi phục:
```
SW-D1# show spanning-tree inconsistentports
Number of inconsistent ports (segments) in the system : 0
```
✅ **Root Guard tự hồi phục**, không cần can thiệp tay.

---

**Test 3 — Đo hội tụ STP vs RSTP (bài lab quan trọng nhất tuần 4)**

**a) Chuyển về PVST+ (STP chậm) trên cả 4 switch:**
```
configure terminal
 spanning-tree mode pvst
end
```
Xác nhận: `show spanning-tree summary | include mode`

**b) Ping liên tục từ PC1 sang PC2, rồi cắt Root Port của SW-A1:**

Trên PC1 (VPCS):
```
PC1> ping 10.10.10.12 -c 100
```

Trên SW-A1, cắt Root Port đang forward (giả sử Gi0/1):
```
SW-A1(config)# interface GigabitEthernet0/1
SW-A1(config-if)# shutdown
```

**Đếm số gói ping mất.**

**c) Chuyển sang Rapid PVST+ và đo lại:**
```
! Trên CẢ 4 switch
configure terminal
 spanning-tree mode rapid-pvst
end
```
Bật lại Gi0/1, chờ ổn định, rồi lặp lại bài đo.

⭐ **BẢNG KẾT QUẢ — điền vào:**

| Mode | Số gói mất | Thời gian (~) | Ghi chú |
|---|:---:|---|---|
| PVST+ (802.1D) | | | Chờ Listening + Learning |
| Rapid PVST+ (802.1w) | | | Proposal/Agreement |

**Kết quả mong đợi:** PVST+ mất ~15–30 gói · Rapid PVST+ mất **1–3 gói**.

---

**Test 4 — Link type & tác động của duplex**

```
! Xem link type hiện tại
SW-A1# show spanning-tree vlan 10 | include P2p|Shr
```
Mọi link phải là `P2p` (vì full-duplex).

**Ép half-duplex để thấy nó biến thành shared:**
```
SW-A1(config)# interface GigabitEthernet0/1
SW-A1(config-if)# duplex half
SW-A1(config-if)# speed 100
```
```
SW-A1# show spanning-tree vlan 10 | include Gi0/1
```
→ Link type đổi thành **`Shr`**.

Đo lại hội tụ với Rapid PVST+ → **chậm lại** vì không handshake được.

**Hoàn tác:**
```
SW-A1(config-if)# duplex auto
SW-A1(config-if)# speed auto
```

⭐ **Bài học thực chiến:** một duplex mismatch không chỉ gây lỗi CRC — nó **phá luôn khả năng
hội tụ nhanh của RSTP** trên port đó.

---

**Test 5 — Bắt gói BPDU bằng Wireshark**

1. Trong EVE-NG: click phải link SW-A1↔SW-D1 → **Capture**
2. Trong Wireshark, filter: `stp`

⭐ **Điền bảng từ những gì bạn thấy trong gói BPDU:**

| Trường trong BPDU | Giá trị bạn thấy |
|---|---|
| Protocol Version Identifier (0=STP, 2=RSTP) | |
| BPDU Type | |
| Root Identifier (priority + MAC) | |
| Root Path Cost | |
| Bridge Identifier | |
| Port Identifier | |
| Message Age / Max Age / Hello / Forward Delay | |
| Flags (TC bit? Proposal? Agreement?) | |

**Thử nghiệm:** chuyển giữa `pvst` và `rapid-pvst` rồi bắt lại → xem trường **Version** đổi từ `0` → `2`.
Và trong RSTP, tìm gói có bit **Proposal/Agreement** lúc link vừa lên.

> ⭐ Đây là lúc lý thuyết §2.2 và §3.4 trở thành thứ bạn **nhìn thấy được**. Đừng bỏ bước này.

---

## 🧪 9. LAB — TUẦN 5: MST · ETHERCHANNEL

### LAB 02-2A — MST

Dùng lại topology LAB 02-1 (4 switch).

#### Bước 1 — Thêm VLAN để thấy giá trị của MST

```
! Trên CẢ 4 switch
configure terminal
vlan 10
 name USERS-A
vlan 20
 name USERS-B
vlan 30
 name USERS-C
vlan 40
 name SERVERS-A
vlan 50
 name SERVERS-B
vlan 60
 name SERVERS-C
exit
!
! Cho phép trên mọi trunk
interface range GigabitEthernet0/1 - 3
 switchport trunk allowed vlan 10,20,30,40,50,60
end
```

**Xem gánh nặng của Rapid PVST+ với 6 VLAN:**
```
SW-D1# show spanning-tree summary totals
```
**Output mẫu:**
```
Switch is in rapid-pvst mode
...
Name                   Blocking Listening Learning Forwarding STP Active
---------------------- -------- --------- -------- ---------- ----------
6 vlans                       6         0        0         18         24
```
⭐ **6 VLAN = 6 instance STP.** Hình dung 500 VLAN → 500 instance.

#### Bước 2 — Chuyển sang MST

```
! ⭐ Làm GIỐNG NHAU trên CẢ 4 switch — không được sai 1 ký tự
configure terminal
!
spanning-tree mode mst
!
spanning-tree mst configuration
 name CAMPUS-01
 revision 1
 instance 1 vlan 10,20,30
 instance 2 vlan 40,50,60
 exit
!
end
write memory
```

#### Bước 3 — Ép root cho từng instance (load-balance)

```
! SW-D1: root MST1, backup MST2
SW-D1(config)# spanning-tree mst 1 priority 4096
SW-D1(config)# spanning-tree mst 2 priority 8192

! SW-D2: root MST2, backup MST1
SW-D2(config)# spanning-tree mst 2 priority 4096
SW-D2(config)# spanning-tree mst 1 priority 8192
```

#### Bước 4 — Kiểm tra

**a) ⭐ Lệnh đầu tiên khi troubleshoot MST — xác nhận region:**
```
SW-D1# show spanning-tree mst configuration
```
**Output mẫu:**
```
Name      [CAMPUS-01]
Revision  1     Instances configured 3

Instance  Vlans mapped
--------  ---------------------------------------------------------------------
0         1-9,11-19,21-29,31-39,41-49,51-59,61-4094
1         10,20,30
2         40,50,60
-------------------------------------------------------------------------------
```

**b) So sánh digest giữa các switch — cách nhanh nhất để phát hiện lệch region:**
```
SW-D1# show spanning-tree mst configuration digest
```
**Output mẫu:**
```
Name      [CAMPUS-01]
Revision  1     Instances configured 3
Digest    0x1A2B3C4D5E6F708192A3B4C5D6E7F809
Pre-std Digest  0x...
```
⭐ **Chạy lệnh này trên cả 4 switch. `Digest` PHẢI GIỐNG NHAU HOÀN TOÀN.**
Lệch 1 ký tự = lệch region = cây bị chia đôi.

**Điền bảng:**

| Switch | Name | Revision | Digest (8 ký tự đầu) | Cùng region? |
|---|---|:---:|---|:---:|
| SW-D1 | | | | |
| SW-D2 | | | | |
| SW-A1 | | | | |
| SW-A2 | | | | |

**c) Xem cây từng instance:**
```
SW-D1# show spanning-tree mst
```
**Output mẫu:**
```
##### MST0    vlans mapped:   1-9,11-19,21-29,31-39,41-49,51-59,61-4094
Bridge        address 0c1a.2b00.d100  priority  32768 (32768 sysid 0)
Root          this switch for the CIST
Operational   hello time 2, forward delay 15, max age 20, txholdcount 6
Configured    hello time 2, forward delay 15, max age 20, max hops 20

Interface        Role Sts Cost      Prio.Nbr Type
---------------- ---- --- --------- -------- --------------------------------
Gi0/1            Desg FWD 20000     128.2    P2p
Gi0/2            Desg FWD 20000     128.3    P2p
Gi0/3            Desg FWD 20000     128.4    P2p

##### MST1    vlans mapped:   10,20,30
Bridge        address 0c1a.2b00.d100  priority  4097  (4096 sysid 1)
Root          this switch for MST1

Interface        Role Sts Cost      Prio.Nbr Type
---------------- ---- --- --------- -------- --------------------------------
Gi0/1            Desg FWD 20000     128.2    P2p
Gi0/2            Desg FWD 20000     128.3    P2p
Gi0/3            Desg FWD 20000     128.4    P2p

##### MST2    vlans mapped:   40,50,60
Bridge        address 0c1a.2b00.d100  priority  8194  (8192 sysid 2)
Root          0c1a.2b00.d200  priority 4098  cost 20000
              port Gi0/3
```

⭐ **Đọc output này:**
- `priority 4097 (4096 sysid 1)` → priority 4096 + **instance ID 1** (không phải VLAN ID như PVST+!)
- MST1: `Root this switch` → SW-D1 là root
- MST2: `Root 0c1a.2b00.d200` → SW-D2 là root ✅ load-balance thành công
- `Cost 20000` → MST dùng **long path cost** mặc định (1 Gbps = 20000)

> ⭐ **Bẫy đề:** trong MST, `sysid` là **Instance ID**, không phải VLAN ID.
> MST1 priority 4096 → hiện **4097**. Trong PVST+ thì VLAN 10 priority 4096 → hiện **4106**.

**d) Xem giảm gánh nặng:**
```
SW-D1# show spanning-tree summary totals
```
**Output mẫu:**
```
Switch is in mst mode (IEEE Standard)
...
Name                   Blocking Listening Learning Forwarding STP Active
---------------------- -------- --------- -------- ---------- ----------
3 msts                        2         0        0          7          9
```
⭐ **Từ "6 vlans" xuống "3 msts"** (MST0 + MST1 + MST2). Với 500 VLAN thì vẫn là 3 msts.

**e) Xem port role cho 1 instance cụ thể:**
```
SW-A1# show spanning-tree mst 1
SW-A1# show spanning-tree mst 2
SW-A1# show spanning-tree mst interface GigabitEthernet0/1
```

✅ **Checkpoint LAB 02-2A:**

| Kiểm tra | Mong đợi |
|---|---|
| `show spanning-tree mst configuration digest` giống nhau trên cả 4 switch | ⭐ ✅ |
| MST1 root = SW-D1 · MST2 root = SW-D2 | ✅ |
| Trên SW-A1: Root Port của MST1 ≠ Root Port của MST2 | ⭐ ✅ Load-balance |
| `show spanning-tree summary totals` báo `3 msts` (không phải `6 vlans`) | ✅ |
| Ping PC1↔PC2 vẫn hoạt động | ✅ |

#### Bước 5 — ⭐ Tái hiện lỗi MST kinh điển (làm để nhớ mãi)

**Lỗi: thiếu 1 VLAN trong mapping trên 1 switch**

```
! Trên SW-A2 — cố ý làm SAI: bỏ VLAN 30 khỏi instance 1
SW-A2(config)# spanning-tree mst configuration
SW-A2(config-mst)# instance 1 vlan 10,20
SW-A2(config-mst)# exit
```

**Quan sát:**
```
SW-A2# show spanning-tree mst configuration digest
```
→ **Digest ĐÃ ĐỔI** → SW-A2 ra khỏi region.

```
SW-A2# show spanning-tree mst | include Boun|Bound
```
→ Port uplink của SW-A2 giờ là **boundary port**.

```
SW-A2# show spanning-tree mst 1
```
→ Cây MST1 nhìn khác hoàn toàn so với 3 switch kia.

⭐ **Bài học:** chỉ thiếu **1 VLAN** trong mapping → switch ra khỏi region → topology thay đổi.
Đây là lỗi số 1 khi triển khai MST ở production. **Ghi vào `SO-TAY-LOI.md`.**

**Sửa lại:**
```
SW-A2(config)# spanning-tree mst configuration
SW-A2(config-mst)# instance 1 vlan 10,20,30
SW-A2(config-mst)# exit
```
Xác nhận digest quay về giống 3 switch kia.

**Lỗi 2: lệch revision number**
```
SW-A1(config)# spanning-tree mst configuration
SW-A1(config-mst)# revision 2                    ! cố ý sai
SW-A1(config-mst)# exit
```
→ Digest cũng đổi → cùng hậu quả. Sửa về `revision 1`.

---

### LAB 02-2B — EtherChannel

#### Bước 1 — L2 EtherChannel với LACP

Gộp 2 link giữa SW-D1 và SW-D2. Hiện tại chỉ có Gi0/3 — thêm link thứ 2:

1. Trong EVE-NG: **Stop** SW-D1 và SW-D2 (không nối được dây khi node đang chạy)
2. Nối thêm: `SW-D1 Gi0/4` ↔ `SW-D2 Gi0/4`
3. Start lại

> 💡 Khi Add node, nhớ đặt **Ethernets = 6** để có đủ port. Nếu đã tạo với 4 port,
> phải xóa node và tạo lại (hoặc dùng cặp port khác đang rỗi).

**Cấu hình SW-D1:**
```
configure terminal
!
! === Bước 1: xóa cấu hình cũ trên member port (quan trọng) ===
default interface GigabitEthernet0/3
!
! === Bước 2: chỉ gõ channel-group trên member port ===
interface range GigabitEthernet0/3 - 4
 description ---> ETHERCHANNEL to SW-D2
 channel-protocol lacp
 channel-group 1 mode active
 no shutdown
!
! === Bước 3: MỌI cấu hình khác gõ trên Port-channel ===
interface Port-channel1
 description ---> Po1 to SW-D2
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30,40,50,60
 switchport trunk native vlan 999
 switchport nonegotiate
 no shutdown
!
end
write memory
```

**Cấu hình SW-D2:** giống hệt (dùng `channel-group 1 mode active`).

> 💡 `default interface Gi0/3` xóa toàn bộ cấu hình interface về mặc định — rất tiện khi làm lại.

#### Bước 2 — Kiểm tra

**a) ⭐ Lệnh quan trọng nhất:**
```
SW-D1# show etherchannel summary
```
**Output mong đợi:**
```
Group  Port-channel  Protocol    Ports
------+-------------+-----------+----------------------------------------------
1      Po1(SU)         LACP      Gi0/3(P)    Gi0/4(P)
```
✅ **Checkpoint:** `Po1(SU)` và **cả 2 port đều `(P)`**.

⚠️ Nếu thấy `(I)`, `(s)`, `(u)`, `(D)` → xem bảng §6.7 và §10.2.

**b) Thấy partner không:**
```
SW-D1# show lacp neighbor
```
**Output mẫu:**
```
Flags:  S - Device is requesting Slow LACPDUs
        F - Device is requesting Fast LACPDUs
        A - Device is in Active mode       P - Device is in Passive mode

Channel group 1 neighbors
Partner's information:
                  LACP port                        Oper    Port     Port
Port      Flags   Priority  Dev ID          Age    Key     Number   State
Gi0/3     SA      32768     0c1a.2b00.d200  12s    0x1     0x104    0x3D
Gi0/4     SA      32768     0c1a.2b00.d200  15s    0x1     0x105    0x3D
```
✅ Thấy `Dev ID` của SW-D2 → LACP bắt tay thành công.
`Flags SA` = **S**low LACPDU + **A**ctive mode.

**c) STP giờ chỉ thấy 1 port logic:**
```
SW-D1# show spanning-tree mst 1 | include Po1|Gi0/3|Gi0/4
```
**Output mẫu:**
```
Po1              Desg FWD 10000     128.65   P2p
```
⭐ **Chỉ có `Po1`, không còn `Gi0/3`/`Gi0/4` riêng lẻ.** Và cost = **10000** thay vì 20000
(2 link 1G gộp lại = 2 Gbps → cost giảm một nửa).

**d) Interface Port-channel dùng như interface thường:**
```
SW-D1# show interfaces Port-channel1
SW-D1# show interfaces trunk
```
→ `Po1` xuất hiện như 1 trunk bình thường.

#### Bước 3 — ⭐ Test failover (giá trị nhất)

**a) Ping liên tục PC1 → PC2** (đường đi qua Po1):
```
PC1> ping 10.10.10.12 -c 200
```

**b) Cắt 1 member link:**
```
SW-D1(config)# interface GigabitEthernet0/3
SW-D1(config-if)# shutdown
```

**c) Đếm gói mất:**
```
SW-D1# show etherchannel summary
```
```
1      Po1(SU)         LACP      Gi0/3(D)    Gi0/4(P)
```
⭐ `Po1` **vẫn `(SU)`** — bundle còn sống, chỉ mất 1 member.

⭐ **BẢNG SO SÁNH — điền vào:**

| Tình huống | Số gói ping mất | Có Topology Change? |
|---|:---:|:---:|
| Cắt 1 member của EtherChannel | | |
| (so sánh với LAB 02-1) Cắt Root Port khi **không** có EtherChannel, Rapid PVST+ | | |

**Kết quả mong đợi:** cắt member EtherChannel mất **0–1 gói** và **KHÔNG có TC**
(vì STP không thấy gì thay đổi — `Po1` vẫn up). Đây là ưu điểm lớn nhất của EtherChannel
so với dựa vào STP.

**Kiểm tra không có TC:**
```
SW-A1# show spanning-tree mst 1 detail | include topology change
```

**d) Bật lại:**
```
SW-D1(config-if)# no shutdown
```

#### Bước 4 — Tái hiện các lỗi EtherChannel (làm để nhớ)

**Lỗi 1 — `passive + passive` không bundle**
```
SW-D1(config)# interface range Gi0/3 - 4
SW-D1(config-if-range)# channel-group 1 mode passive
! Trên SW-D2 cũng passive
```
```
show etherchannel summary
```
→ Port thành `(s)` **suspended** hoặc bundle không lên.
**Bài học:** phải có ít nhất 1 bên `active`. Sửa: đưa 1 bên về `active`.

---

**Lỗi 2 — ⚠️ Trộn `on` với LACP (nguy hiểm nhất)**
```
SW-D1(config)# interface range Gi0/3 - 4
SW-D1(config-if-range)# channel-group 1 mode on          ! static
! SW-D2 vẫn để mode active (LACP)
```
```
SW-D2# show etherchannel summary
```
→ SW-D2 báo `Gi0/3(I) Gi0/4(I)` — **individual**.

⚠️ **Nguy hiểm:** SW-D1 gộp 2 port thành 1 (không gửi BPDU riêng), SW-D2 coi là 2 port riêng
→ **có thể tạo loop**.

**Xem misconfig guard bảo vệ:**
```
SW-D2# show spanning-tree summary | include misconfig
EtherChannel misconfig guard is enabled
```
Nếu loop hình thành, guard này sẽ err-disable port.

**Sửa:** đưa cả 2 bên về cùng protocol (`active`/`active`).

---

**Lỗi 3 — Tham số lệch giữa member port**
```
SW-D1(config)# interface GigabitEthernet0/3
SW-D1(config-if)# switchport trunk allowed vlan 10          ! cố ý khác Gi0/4
```
```
show etherchannel summary
```
→ `Gi0/3(u)` — **unsuitable for bundling**.

```
SW-D1# show interfaces Gi0/3 etherchannel | include reason|Reason
! hoặc xem log
SW-D1# show logging | include EC5|ETHERCHANNEL
%EC-5-CANNOT_BUNDLE2: Gi0/3 is not compatible with Gi0/4 and will be suspended
                      (trunk vlan mismatch)
```
⭐ **Log nói thẳng nguyên nhân: `trunk vlan mismatch`.**

**Sửa:**
```
SW-D1(config)# default interface GigabitEthernet0/3
SW-D1(config)# interface GigabitEthernet0/3
SW-D1(config-if)# channel-group 1 mode active
```
→ Rồi cấu hình lại **trên `interface Port-channel1`**, không trên member.

**Bài học:** đây là lý do quy tắc *"chỉ gõ `channel-group` trên member, mọi thứ khác trên Port-channel"*.

#### Bước 5 — LACP nâng cao & load-balancing

```
! LACP rate fast — phát hiện lỗi trong 3 s thay vì 90 s
SW-D1(config)# interface range GigabitEthernet0/3 - 4
SW-D1(config-if-range)# lacp rate fast
! ⚠️ Phải đặt CẢ 2 BÊN
```
```
SW-D1# show lacp neighbor | include Flags|Gi0
```
→ Flag đổi từ `SA` (Slow+Active) sang **`FA`** (Fast+Active).

```
! min-links: bundle chỉ up khi có ≥ 2 link
SW-D1(config)# interface Port-channel1
SW-D1(config-if)# port-channel min-links 2
```
Test: shutdown 1 member → **cả Po1 xuống** (`Po1(SM)` = minimum links not met).

> ⭐ **Vì sao dùng min-links:** nếu bạn có 4×10G = 40G và 3 link chết, 1 link 10G còn lại
> sẽ **bị dội 40G traffic** → drop nghiêm trọng. Thà cho bundle xuống để traffic đi đường khác.

**Hoàn tác:**
```
SW-D1(config-if)# no port-channel min-links
```

```
! Load-balancing
SW-D1# show etherchannel load-balance
SW-D1(config)# port-channel load-balance src-dst-ip
SW-D1# show etherchannel load-balance
```

#### Bước 6 — 🚀 L3 EtherChannel (nâng cao)

Nếu image hỗ trợ `ip routing`:
```
! Trên SW-D1
configure terminal
ip routing
!
default interface range GigabitEthernet0/3 - 4
!
interface range GigabitEthernet0/3 - 4
 no switchport                          ! ⭐ TRƯỚC channel-group
 channel-group 2 mode active
 no shutdown
!
interface Port-channel2
 no switchport
 ip address 10.99.99.1 255.255.255.252
 no shutdown
end
```
Trên SW-D2: `ip address 10.99.99.2 255.255.255.252`

**Kiểm tra:**
```
SW-D1# show etherchannel summary
```
→ `Po2(RU)` — **R** = Layer3, **U** = in use.

```
SW-D1# ping 10.99.99.2
SW-D1# show spanning-tree mst 1 | include Po2
```
→ **`Po2` KHÔNG xuất hiện trong STP** (vì là L3, không tham gia STP).

✅ **Checkpoint LAB 02-2B:**

| Kiểm tra | Mong đợi |
|---|---|
| `show etherchannel summary` → `Po1(SU)` + cả 2 port `(P)` | ✅ |
| `show lacp neighbor` thấy Dev ID của switch đối diện | ✅ |
| STP chỉ thấy `Po1`, không thấy member riêng lẻ | ⭐ ✅ |
| Cắt 1 member: mất 0–1 gói ping, **không có TC** | ⭐ ✅ |
| Tái hiện được `(s)`, `(I)`, `(u)` và giải thích từng cái | ✅ |
| L3 EtherChannel: `Po2(RU)`, ping được, không có trong STP | ✅ |

---

## 💡 10. THỰC CHIẾN ĐI LÀM

| Chủ đề | Thi dạy | Thực tế đi làm |
|---|---|---|
| **Root Bridge** | Bầu bằng MAC nhỏ nhất | ⛔ **Không bao giờ để mạng tự bầu.** Luôn ép: root chính = distribution/core, **và luôn có backup root** (priority cao hơn 1 bậc). Ghi vào standard config |
| **Native VLAN** | Mặc định VLAN 1 | ⭐ Đổi sang VLAN "rác" (VD 999), **không gán port nào** vào nó, và **prune nó khỏi allowed list** nếu được. Chống VLAN hopping |
| **PortFast trunk** | Ít nhắc | ⭐ **Cực quan trọng với hạ tầng ảo hóa của bạn.** Port trunk nối Proxmox/ESXi phải có `spanning-tree portfast trunk`, nếu không VM mất mạng 30 s mỗi lần host reboot |
| **BPDU Guard** | Cấu hình được | ⭐ Bật **mặc định toàn switch**: `spanning-tree portfast bpduguard default`. Không có ngoại lệ. Đây là lá chắn duy nhất giữa bạn và một cú loop 3 giờ sáng |
| **BPDU Filter** | Có lệnh | ⛔ **Không dùng interface-level.** Nó tắt STP trên port đó. Nhiều sự cố loop lớn bắt nguồn từ đây |
| **Loop Guard + UDLD** | Riêng lẻ | ⭐ Cisco khuyến nghị **dùng CẢ HAI**: `spanning-tree loopguard default` + `udld aggressive`. Chúng bắt 2 loại lỗi khác nhau |
| **errdisable recovery** | Không dạy | ⭐ Bật `errdisable recovery cause bpduguard/udld/link-flap` với interval 300 s. Sự cố nhất thời tự lành, không cần ra tủ mạng ban đêm |
| **MST region** | Cấu hình được | ⚠️ **Đây là nơi mọi triển khai MST thất bại.** Quy trình bắt buộc: (1) viết mapping vào tài liệu, (2) copy-paste **cùng một block** lên mọi switch, (3) verify bằng `show spanning-tree mst configuration digest` — **digest phải giống nhau tuyệt đối** |
| **MST mapping** | `instance 1 vlan 10,20,30` | ⭐ Nên map **theo dải rộng** (`instance 1 vlan 1-1000`, `instance 2 vlan 1001-2000`) thay vì liệt kê từng VLAN → thêm VLAN mới **không cần sửa mapping** trên mọi switch |
| **Đổi STP mode** | Một lệnh | ⚠️ Đổi `pvst` → `mst` gây **hội tụ lại toàn mạng** = downtime. Phải có cửa sổ bảo trì. Và đổi theo thứ tự: **core trước, access sau** (hoặc ngược lại, nhưng phải có kế hoạch) |
| **EtherChannel cấu hình** | Trên member port | ⭐ **Quy tắc sắt:** chỉ gõ `channel-group` trên member. **Mọi thứ khác gõ trên `interface Port-channel`**. Vi phạm quy tắc này = nguồn gốc 80% lỗi EtherChannel |
| **Số link EtherChannel** | Tối đa 8 | ⭐ Dùng **2, 4, hoặc 8**. 3 link chia tải 3:3:2 — không phải "1.5× của 2 link" |
| **LACP vs PAgP vs on** | Bảng tương thích | ⭐ **Luôn dùng LACP** (`active`/`active`). Đa vendor, có đàm phán, phát hiện lỗi cấu hình. **Tránh `on`** — không đàm phán = dễ tạo loop |
| **misconfig guard** | Không dạy | ⭐ `spanning-tree etherchannel guard misconfig` — bật luôn. Đây là lá chắn cho tình huống `(I) individual` |
| **min-links** | Tùy chọn | ⭐ Dùng trên uplink quan trọng. 4×10G mà còn 1 link thì thà cho bundle xuống hơn là để 1 link gánh 40G |
| **lacp rate fast** | Tùy chọn | Dùng khi cần phát hiện lỗi nhanh, nhưng **phải đặt cả 2 bên**. Tăng nhẹ CPU |
| **Duplex mismatch** | Gây lỗi CRC | ⭐ Còn **phá RSTP** — half-duplex → shared link → mất proposal/agreement → hội tụ chậm lại 30–50 s. Luôn kiểm tra `show interfaces status` |
| **Đếm TC** | Không dạy | ⭐ `show spanning-tree detail \| include occurr` — nếu TC tăng liên tục = có link flapping. Đây là lệnh đầu tiên khi "mạng chậm không rõ nguyên nhân" |
| **Tài liệu hóa** | Không có | ⭐ Mỗi switch phải có file ghi: root cho VLAN/instance nào, MST mapping, guard nào ở port nào. Không có tài liệu = người sau (hoặc bạn 6 tháng sau) không dám sửa |

---

## 🎓 11. BẪY TRONG ĐỀ ENCOR

| # | Bẫy | Sự thật |
|:---:|---|---|
| 1 | *"RSTP có 5 state"* | ❌ **3 state**: Discarding, Learning, Forwarding |
| 2 | Alternate vs Backup port | **Alternate** = đường khác về root (dự phòng Root Port, hay gặp) · **Backup** = 2 port cùng switch trên cùng segment (chỉ có hub/half-duplex) |
| 3 | *"RSTP luôn hội tụ nhanh"* | ❌ Trên **shared link (half-duplex)** thì RSTP **rơi về hành vi 802.1D chậm** — không handshake được |
| 4 | MST region cần khớp gì | ⭐ **3 thứ**: Name + Revision + **VLAN-to-instance mapping**. Thiếu 1 VLAN = khác region |
| 5 | MST0 là gì | **IST** — bắt buộc có, chứa mọi VLAN chưa map, là cây duy nhất nói chuyện ra ngoài region |
| 6 | *"MST priority hiện = priority + VLAN ID"* | ❌ Trong MST, `sysid` = **Instance ID**. MST1 priority 4096 → **4097**. (PVST+ mới là + VLAN ID) |
| 7 | BPDU Filter interface vs global | **Interface** = không gửi & không nhận → **tắt STP hẳn** (nguy hiểm) · **Global** = chỉ trên PortFast port, nhận BPDU thì tự tắt PortFast và hồi phục |
| 8 | Root Guard kích hoạt khi nào | Nhận **Superior BPDU** → port `ROOT_Inc` → block → **tự hồi phục** |
| 9 | Loop Guard kích hoạt khi nào | **Ngừng nhận** BPDU trên Root/Alternate port → `LOOP_Inc` → block → **tự hồi phục** |
| 10 | Đặt Root Guard ở đâu | Port **hướng xuống** (downstream) / nối đối tác. **Không** đặt trên uplink |
| 11 | Đặt Loop Guard ở đâu | Port **hướng lên** (Root/Alternate port = uplink) |
| 12 | UDLD normal vs aggressive | **Normal**: phát hiện unidirectional rõ ràng → err-disable; chỉ timeout → **chỉ log** · **Aggressive**: timeout cũng err-disable sau **8 lần** thử lại |
| 13 | ⭐ LACP `passive + passive` | ❌ **KHÔNG bundle.** Cần ít nhất 1 bên `active` |
| 14 | ⭐ PAgP `auto + auto` | ❌ **KHÔNG bundle.** Cần ít nhất 1 bên `desirable` |
| 15 | `on` + `active` | ❌ **KHÔNG bundle.** `on` chỉ bắt tay với `on` |
| 16 | `(I)` vs `(s)` trong `show etherchannel summary` | `(s)` **suspended** = không có partner, port **không forward** (an toàn) · `(I)` **individual** = port **forward độc lập** → ⚠️ **nguy cơ loop** |
| 17 | `(u)` nghĩa là gì | **unsuitable for bundling** = tham số lệch giữa member port |
| 18 | `Po1(SU)` nghĩa là gì | **S** = Layer2 · **U** = in use → ✅ đúng. `(RU)` = Layer3 in use |
| 19 | Số link EtherChannel nên dùng | **2, 4, 8** (chia đều 8 bucket). 3/5/6/7 chia không đều |
| 20 | *"EtherChannel 2×1G = 1 flow được 2 Gbps"* | ❌ **Một flow chỉ đi 1 link.** EtherChannel tăng tổng băng thông, không tăng băng thông 1 flow |
| 21 | Cấu hình EtherChannel ở đâu | ⭐ `channel-group` trên **member port** · mọi thứ khác trên **`interface Port-channel`** |
| 22 | L3 EtherChannel thứ tự | `no switchport` trên **member TRƯỚC**, rồi `channel-group`, rồi `no switchport` + IP trên Po |
| 23 | STP timer đổi ở đâu | ⭐ Trên **Root Bridge** — timer trong BPDU lấy từ root |
| 24 | Cắt 1 member EtherChannel có gây TC? | ❌ **Không** — STP vẫn thấy `Po1` up. Đó là ưu điểm chính |
| 25 | MST cost link 1 Gbps | **20000** (long path cost). PVST+ short mode là **4** |

---

## 🐛 12. GỠ LỖI NHANH

### 12.1 Hộp lệnh vạn năng

```
! === STP tổng quan ===
show spanning-tree summary                     ! ⭐ mode + guard nào bật
show spanning-tree summary totals              ! đếm instance
show spanning-tree vlan 10                     ! ⭐ chi tiết 1 VLAN
show spanning-tree root                        ! ai là root từng VLAN
show spanning-tree blockedports                ! port nào bị block
show spanning-tree inconsistentports           ! ⭐ port bị guard chặn
show spanning-tree interface Gi0/1 detail      ! chi tiết 1 port
show spanning-tree detail | include occurr     ! ⭐ đếm topology change

! === MST ===
show spanning-tree mst configuration           ! ⭐ LỆNH ĐẦU TIÊN khi lỗi MST
show spanning-tree mst configuration digest    ! ⭐ so sánh giữa các switch
show spanning-tree mst                         ! mọi instance
show spanning-tree mst 1                       ! 1 instance
show spanning-tree mst interface Gi0/1
show spanning-tree mst | include Boun           ! port boundary

! === Guards / UDLD ===
show spanning-tree interface Gi0/1 detail | include guard
show errdisable recovery
show interfaces status err-disabled            ! ⭐ port nào tắt + VÌ SAO
show udld
show udld neighbors
udld reset                                     ! bật lại port UDLD tắt

! === EtherChannel ===
show etherchannel summary                      ! ⭐ LỆNH ĐẦU TIÊN
show etherchannel 1 detail
show etherchannel load-balance
show lacp neighbor                             ! ⭐ có partner không
show lacp counters                             ! PDU gửi/nhận
show lacp internal
show pagp neighbor
show interfaces Port-channel1
show interfaces Gi0/3 etherchannel

! === Nền tảng L2 ===
show interfaces status                         ! ⭐ speed/duplex/vlan
show interfaces trunk                          ! ⭐ trunk + allowed + native
show vlan brief
show mac address-table
show logging | include SPANTREE|EC-|PM-|UDLD   ! ⭐ đọc log
```

### 12.2 Bảng lỗi: triệu chứng → nguyên nhân → cách sửa

#### STP / RSTP

| # | Triệu chứng | Nguyên nhân | Cách sửa |
|:---:|---|---|---|
| 1 | Root bridge là switch access "vô lý" | Không ai ép priority → MAC nhỏ nhất thắng | `spanning-tree vlan X priority 4096` trên switch core + backup root |
| 2 | Mạng chậm bất thường, MAC table nhảy liên tục | ⚠️ **STP loop**, hoặc link flapping | `show spanning-tree blockedports` (phải có port block) · `show spanning-tree detail \| inc occurr` (TC tăng?) · tìm switch tắt STP hoặc BPDU Filter interface-level |
| 3 | `show spanning-tree detail` TC tăng liên tục | Link flapping / port nhấp nháy | `show interfaces \| include flapped` · `show logging` tìm link up/down · sửa cáp/SFP · bật `errdisable recovery cause link-flap` |
| 4 | Port PC lên mất 30 s | Thiếu PortFast | `spanning-tree portfast` (hoặc `portfast default`) |
| 5 | VM mất mạng 30 s mỗi lần host ảo hóa reboot | Trunk tới hypervisor thiếu PortFast | ⭐ `spanning-tree portfast trunk` + giữ BPDU Guard |
| 6 | Port `err-disabled`, reason `bpduguard` | Có switch cắm vào port PortFast | Tìm ai cắm sai → `shut`/`no shut` (hoặc chờ errdisable recovery) |
| 7 | Port `BKN *ROOT_Inc` | **Root Guard** chặn Superior BPDU | Tìm switch đang cố làm root (`show spanning-tree root`) → sửa priority của nó |
| 8 | Port `BKN *LOOP_Inc` | **Loop Guard**: ngừng nhận BPDU trên Root/Alternate port | Kiểm tra link một chiều (`show udld`), lỗi SFP/fiber, hoặc CPU switch đối diện quá cao |
| 9 | Port `BKN *PVST_Peer_Inc` | Boundary port MST nhận BPDU PVST+ không nhất quán | Đảm bảo bên PVST+ có cùng root cho các VLAN thuộc cùng MST instance |
| 10 | Rapid PVST+ mà vẫn hội tụ chậm | Link là **shared** (half-duplex) | `show spanning-tree \| include Shr` → sửa duplex về full/auto |
| 11 | Log `NATIVE_VLAN_MISMATCH` | Native VLAN 2 đầu trunk lệch | Đặt giống nhau |
| 12 | Đổi timer STP không có tác dụng | Timer lấy từ **Root Bridge** | Đổi trên root, hoặc đừng đổi timer (dùng RSTP thay) |

#### MST

| # | Triệu chứng | Nguyên nhân | Cách sửa |
|:---:|---|---|---|
| 13 | ⭐ Cây MST "chia đôi", switch nhìn topology khác nhau | **Region không khớp** | `show spanning-tree mst configuration digest` trên mọi switch → digest phải **giống tuyệt đối**. Sửa name/revision/mapping |
| 14 | Port bất ngờ thành **boundary** | Switch đó ra khỏi region (thiếu VLAN trong mapping, lệch revision) | So digest → sửa mapping |
| 15 | VLAN mới thêm vào bị block hết | VLAN chưa map → rơi vào **MST0 (IST)**, mà IST có topology khác | Map VLAN mới vào instance đúng **trên MỌI switch**, hoặc dùng mapping theo dải rộng ngay từ đầu |
| 16 | Đổi sang MST làm mất mạng | Đổi mode gây hội tụ lại toàn mạng | Đây là hành vi bình thường → phải có cửa sổ bảo trì |

#### EtherChannel

| # | Triệu chứng (`show etherchannel summary`) | Nguyên nhân | Cách sửa |
|:---:|---|---|---|
| 17 | `Gi0/3(s)` **suspended** | LACP cấu hình 1 bên, bên kia **chưa cấu hình gì** — hoặc `passive+passive` / `auto+auto` | Cấu hình bên kia · đảm bảo ít nhất 1 bên `active`/`desirable` |
| 18 | ⚠️ `Gi0/3(I)` **individual** | Bên kia dùng `on` (static) trong khi bên này LACP · hoặc LACP không thỏa thuận được | ⭐ **Nguy hiểm — có thể loop.** Đưa 2 bên về cùng protocol. Bật `spanning-tree etherchannel guard misconfig` |
| 19 | `Gi0/3(u)` **unsuitable** | ⭐ Tham số lệch giữa member: speed/duplex/mode/native VLAN/**allowed VLAN** | `show logging \| include EC-5` → log nói thẳng lý do · `default interface Gi0/3` rồi cấu hình lại đúng quy tắc (mọi thứ trên Port-channel) |
| 20 | `Po1(SM)` | **min-links not met** | Đủ số link, hoặc giảm/bỏ `port-channel min-links` |
| 21 | `Po1(SD)` — bundle down | Mọi member down, hoặc Po bị shutdown | `show interfaces status` · `no shutdown` trên Po và member |
| 22 | Bundle up nhưng tải lệch nặng | Hash + số flow ít + số link không phải 2/4/8 | `port-channel load-balance src-dst-mixed-ip-port` · dùng 2/4/8 link |
| 23 | Sau khi tạo EtherChannel, cấu hình trunk "mất" | Đã cấu hình trên member thay vì Port-channel | ⭐ Cấu hình lại trên `interface Port-channel1` |
| 24 | `show lacp neighbor` trống | LACP PDU không tới được | `show lacp counters` (có gửi không?) · kiểm tra port up · kiểm tra bên kia có LACP |
| 25 | L3 EtherChannel không lên | Thiếu `no switchport` trên member trước khi `channel-group` | `default interface` rồi làm lại đúng thứ tự |

### 12.3 Quy trình troubleshoot L2 — 6 bước

```
1. LỚP 1 — VẬT LÝ
   show interfaces status
   → up/down? speed? duplex? (⚠️ half-duplex phá RSTP)
        ↓
2. PORT CÓ BỊ TẮT BỞI TÍNH NĂNG NÀO?
   show interfaces status err-disabled     → Reason = ?
   show spanning-tree inconsistentports    → ROOT_Inc / LOOP_Inc / PVST_Peer_Inc?
        ↓
3. LỚP 2 — VLAN & TRUNK
   show vlan brief          → VLAN có tồn tại trên MỌI switch?
   show interfaces trunk    → trunking? allowed vlan? native vlan?
        ↓
4. ETHERCHANNEL (nếu có)
   show etherchannel summary → (P) hết chưa? có (I)/(s)/(u) không?
   show lacp neighbor        → thấy partner?
        ↓
5. STP
   show spanning-tree summary        → mode? guard?
   show spanning-tree vlan X         → root đúng thiết kế? port role hợp lý?
   show spanning-tree blockedports   → có port block (chống loop) không?
   show spanning-tree detail | inc occurr  → TC có tăng liên tục?
        ↓
6. MST (nếu dùng MST)
   show spanning-tree mst configuration digest  → GIỐNG NHAU trên mọi switch?
```

> ⭐ **Bước 2 là bước người mới hay bỏ qua.** Rất nhiều lần "port không hoạt động" thực ra là
> port đã bị guard tắt, và cột `Reason` nói thẳng nguyên nhân. Đọc trước khi đoán.

---

## 📝 13. QUIZ TỰ KIỂM TRA

**Câu 1.** Nêu 4 thay đổi khiến RSTP nhanh hơn STP.

<details><summary>Xem đáp án</summary>

1. **Mọi switch tự tạo BPDU** mỗi hello (STP: chỉ root tạo, switch khác chuyển tiếp)
2. **BPDU là keepalive**: mất **3 hello (6 s)** là coi neighbor chết (STP: chờ Max Age 20 s)
3. **Proposal/Agreement handshake** thay vì chờ timer Listening+Learning (30 s)
4. **Topology Change**: flood TC ra mọi hướng ngay + **flush MAC table** (STP: gửi TCN lên root,
   root bật bit TC 35 s, các switch chỉ **giảm** MAC aging xuống 15 s)
</details>

---

**Câu 2.** RSTP đang chạy nhưng hội tụ vẫn mất ~30 giây trên một port. Nguyên nhân khả năng cao nhất?

<details><summary>Xem đáp án</summary>

**Port đó là `shared` link — tức đang chạy half-duplex.**

RSTP chỉ dùng được **Proposal/Agreement** trên **point-to-point (full-duplex)** link.
Trên shared link (half-duplex, hoặc có hub), RSTP **rơi về hành vi 802.1D**: chờ timer.

**Kiểm tra:** `show spanning-tree vlan X | include Shr`
**Nguyên nhân thường gặp:** duplex mismatch, hoặc port bị hardcode `duplex half`.
**Sửa:** `duplex auto` (hoặc `duplex full` cả 2 đầu).

⭐ Bài học: duplex mismatch không chỉ gây CRC error — nó phá luôn hội tụ nhanh của RSTP.
</details>

---

**Câu 3.** 3 thứ nào phải khớp để 2 switch cùng một MST region? Kiểm tra nhanh bằng lệnh gì?

<details><summary>Xem đáp án</summary>

**3 thứ phải khớp:**
1. **Configuration Name** (VD `CAMPUS-01`) — phân biệt chữ hoa/thường
2. **Revision Number** (VD `1`)
3. ⭐ **VLAN-to-Instance Mapping** — phải khớp **từng VLAN**

**Lệnh kiểm tra nhanh nhất:**
```
show spanning-tree mst configuration digest
```
Cisco tính một **digest (hash)** từ cả 3 thứ trên và đưa vào BPDU.
**Digest phải giống nhau tuyệt đối** giữa mọi switch trong region.

Thiếu **1 VLAN** trong mapping trên 1 switch → digest khác → switch đó **ra khỏi region**
→ trở thành **boundary** → cây bị chia, traffic đi đường lạ.
</details>

---

**Câu 4.** MST1 được đặt `spanning-tree mst 1 priority 4096`. `show spanning-tree mst 1` hiện
priority bao nhiêu? So sánh với PVST+ VLAN 10 priority 4096.

<details><summary>Xem đáp án</summary>

| | Hiển thị | Công thức |
|---|:---:|---|
| **MST1** priority 4096 | **4097** | 4096 + **Instance ID (1)** |
| **PVST+ VLAN 10** priority 4096 | **4106** | 4096 + **VLAN ID (10)** |

⭐ **Điểm khác biệt quan trọng:** trong MST, `sysid` là **Instance ID**.
Trong PVST+/Rapid PVST+, `sysid` là **VLAN ID**.

Đề hay cho output MST rồi hỏi "priority thực tế là bao nhiêu" — phải trừ đúng Instance ID.
</details>

---

**Câu 5.** Phân biệt BPDU Filter cấu hình ở interface level và global level. Cái nào nguy hiểm?

<details><summary>Xem đáp án</summary>

| | **Interface level**<br>`spanning-tree bpdufilter enable` | **Global level**<br>`spanning-tree portfast bpdufilter default` |
|---|---|---|
| Tác dụng lên | **Bất kỳ** port được cấu hình | **Chỉ** port PortFast |
| Hành vi | ⛔ **Không gửi VÀ không nhận** BPDU → **STP bị vô hiệu hoàn toàn** trên port | Gửi vài BPDU đầu rồi ngừng. **Nếu NHẬN được BPDU → tự tắt PortFast, port trở về STP bình thường** |
| Nguy hiểm | 🔴 **Rất nguy hiểm** — cắm switch vào port này = loop, không ai chặn | 🟢 An toàn hơn nhiều (tự bảo vệ) |

⛔ **Interface level nguy hiểm.** Trên production không dùng, trừ khi có lý do rất cụ thể.

**Nếu chỉ muốn port lên nhanh** → dùng **PortFast**.
**Nếu muốn chống switch lạ** → dùng **BPDU Guard**.
</details>

---

**Câu 6.** Root Guard và Loop Guard: mỗi cái kích hoạt khi nào, đặt ở port nào, trạng thái port là gì?

<details><summary>Xem đáp án</summary>

| | **Root Guard** | **Loop Guard** |
|---|---|---|
| Kích hoạt khi | Nhận **Superior BPDU** (BPDU có Root ID tốt hơn) | **Ngừng nhận** BPDU trên Root Port / Alternate Port |
| Chống | Switch lạ chiếm quyền **Root Bridge** | **Loop** do link một chiều / lỗi software (BPDU im lặng mà link vẫn up) |
| Đặt ở port | ⬇️ **Hướng xuống** (downstream), port nối đối tác/khách | ⬆️ **Hướng lên** (uplink = Root/Alternate port) |
| Trạng thái port | `ROOT_Inc` (root-inconsistent) → block | `LOOP_Inc` (loop-inconsistent) → block |
| Tự hồi phục | ✅ Khi hết Superior BPDU | ✅ Khi BPDU quay lại |

⚠️ **Không bật cả hai trên cùng 1 port** — mục đích ngược nhau.

**Kiểm tra:** `show spanning-tree inconsistentports`
</details>

---

**Câu 7.** SW-A: `channel-group 1 mode passive`. SW-B: `channel-group 1 mode passive`.
Kết quả? Nếu SW-B đổi thành `mode on` thì sao?

<details><summary>Xem đáp án</summary>

**Trường hợp 1 — `passive` + `passive`: KHÔNG bundle.**
Cả hai đều **chờ được mời**, không ai gửi LACP PDU chủ động → port thành `(s)` **suspended**.
Cần ít nhất 1 bên `active`.

**Trường hợp 2 — `passive` (LACP) + `on` (static): KHÔNG bundle, và NGUY HIỂM.**
- SW-B (`on`) gộp 2 port thành Po1 ngay, **không đàm phán**, STP chỉ thấy 1 port
- SW-A (LACP passive) không nhận được LACP PDU → port thành `(I)` **individual** → **forward độc lập**
- → SW-A thấy 2 port riêng, SW-B thấy 1 port → ⚠️ **có thể tạo LOOP**

**Phòng ngừa:** `spanning-tree etherchannel guard misconfig` (global) sẽ err-disable port khi
phát hiện tình huống này.

⭐ **Quy tắc:** `on` **chỉ** bắt tay với `on`. Và tốt nhất **đừng dùng `on`** — luôn dùng LACP `active`/`active`.
</details>

---

**Câu 8.** Giải thích khác biệt giữa `(s)` suspended và `(I)` individual. Cái nào nguy hiểm hơn?

<details><summary>Xem đáp án</summary>

| | `(s)` **suspended** | `(I)` **individual** |
|---|---|---|
| Nghĩa | LACP cấu hình nhưng **partner không phản hồi gì** | LACP có hoạt động nhưng **không thỏa thuận được** |
| Nguyên nhân | Bên kia chưa cấu hình gì · `passive+passive` | Bên kia dùng `on` (static) · tham số lệch |
| Port có forward? | ❌ **Không** | ⚠️ **CÓ — forward độc lập** |
| Nguy cơ loop | Không | ⭐ **CÓ** |

**`(I)` individual nguy hiểm hơn.** `(s)` là hệ thống tự bảo vệ (khóa cửa lại).
`(I)` là hệ thống nói "tôi bỏ cuộc, port cứ hoạt động tự do" — và đó là lúc loop xuất hiện.

**Phòng ngừa:** bật `spanning-tree etherchannel guard misconfig`.
</details>

---

**Câu 9.** Bạn có 4 link 1G giữa 2 switch. Đồng nghiệp đề nghị thêm link thứ 5 để "tăng 25% băng thông".
Bạn nói gì?

<details><summary>Xem đáp án</summary>

**Không nên. Nên dùng 4 hoặc 8 link, không dùng 5.**

**Lý do:** hash load-balancing chia kết quả vào **8 bucket**, rồi phân bucket cho các link:

| Số link | Phân bucket | Đều? |
|:---:|---|:---:|
| **4** | 2 : 2 : 2 : 2 | ✅ Đều |
| **5** | 2 : 2 : 2 : 1 : 1 | ⚠️ **Lệch** — 3 link gánh 2 bucket, 2 link gánh 1 bucket |
| **8** | 1 mỗi link | ✅ Đều |

Với 5 link: 3 link chạy ~25% tải mỗi cái, 2 link chạy ~12.5% → **không phải tăng 25% đều**.
Băng thông tổng tăng, nhưng phân bố lệch → link "nặng" sẽ nghẽn trước khi tổng đạt 5 Gbps.

**Đề xuất thay thế:**
1. Giữ 4 link, đổi hash sang `src-dst-mixed-ip-port` để phân tán tốt hơn
2. Nếu cần thêm → nhảy lên **8 link**
3. Hoặc **nâng cấp lên 10G** — tốt hơn nhiều so với gộp thêm link 1G

⭐ Và nhắc thêm: nếu vấn đề là **một flow lớn** (backup, storage) thì EtherChannel
**không giúp gì cả** — một flow chỉ đi được 1 link.
</details>

---

**Câu 10.** `show etherchannel summary` báo `Gi0/3(u)`. Nguyên nhân? Tìm chính xác bằng cách nào?

<details><summary>Xem đáp án</summary>

`(u)` = **unsuitable for bundling** → **tham số lệch** giữa member port.

**6 thứ phải giống nhau giữa các member:**
1. Speed
2. Duplex
3. Switchport mode (access / trunk)
4. Native VLAN
5. ⭐ **Allowed VLAN list** (lệch nhiều nhất)
6. Access VLAN (nếu access)

**Tìm chính xác nguyên nhân:**
```
show logging | include EC-5|CANNOT_BUNDLE
```
**Output mẫu:**
```
%EC-5-CANNOT_BUNDLE2: Gi0/3 is not compatible with Gi0/4 and will be suspended
                      (trunk vlan mismatch)
```
⭐ **Log nói thẳng lý do** trong dấu ngoặc.

Kèm theo: `show interfaces status` (speed/duplex) · `show interfaces trunk` (allowed/native VLAN)

**Cách sửa & phòng ngừa:**
```
default interface GigabitEthernet0/3        ! xóa cấu hình lệch
interface GigabitEthernet0/3
 channel-group 1 mode active                ! CHỈ dòng này trên member
! Mọi cấu hình khác gõ trên interface Port-channel1
```
</details>

---

**Câu 11.** Bạn cắt 1 member link của EtherChannel 2×1G. Có Topology Change không? Vì sao?
So sánh với việc cắt 1 uplink khi không có EtherChannel.

<details><summary>Xem đáp án</summary>

**Không có Topology Change.**

**Vì sao:** STP nhìn EtherChannel như **một port logic duy nhất (`Po1`)**.
Cắt 1 member thì `Po1` **vẫn UP** (còn member kia) → từ góc nhìn STP, **không có gì thay đổi**
→ không TC, không tính lại cây, không flush MAC table.

Kết quả: mất **0–1 gói ping**, khôi phục dưới 1 giây.

**So sánh — không có EtherChannel:**

| | Cắt member EtherChannel | Cắt uplink không có EtherChannel |
|---|:---:|:---:|
| Topology Change | ❌ Không | ✅ Có |
| STP tính lại cây | ❌ Không | ✅ Có |
| Flush/giảm MAC aging | ❌ Không | ✅ Có |
| Gói mất (Rapid PVST+) | **0–1** | 1–3 (vài giây) |
| Gói mất (PVST+) | **0–1** | 15–30 (30 giây) |

⭐ Đây là **lý do quan trọng nhất** để dùng EtherChannel — không chỉ để tăng băng thông,
mà để **loại bỏ hoàn toàn STP convergence** khỏi kịch bản mất 1 link.
</details>

---

**Câu 12.** So sánh Loop Guard và UDLD: mỗi cái hoạt động ở tầng nào, phát hiện gì, có cần bên kia
hỗ trợ không? Nên dùng cái nào?

<details><summary>Xem đáp án</summary>

| | **Loop Guard** | **UDLD** |
|---|---|---|
| Tầng | **STP** (dựa vào BPDU) | **L2 độc lập** (protocol riêng của Cisco) |
| Phạm vi | Per-VLAN / per-instance | Per-port (toàn bộ port) |
| Phát hiện bằng | BPDU **ngừng đến** trên Root/Alternate port | **Echo** gửi ra không quay lại kèm thông tin của mình |
| Bắt được lỗi software STP | ✅ | ⚠️ Không trực tiếp |
| Bắt được đứt fiber một chiều | ✅ (gián tiếp, qua mất BPDU) | ⭐ ✅ (trực tiếp, nhanh hơn) |
| Cần bên kia hỗ trợ? | ❌ Không | ⭐ **Có** — bên kia phải chạy UDLD |
| Hành động | Port → `LOOP_Inc` (block), tự hồi phục | err-disable (aggressive) hoặc log (normal) |

⭐ **Cisco khuyến nghị dùng CẢ HAI** — chúng bắt 2 loại lỗi khác nhau và bổ trợ nhau:

```
spanning-tree loopguard default        ! global
udld aggressive                        ! global (fiber)
! hoặc per-port:
interface Gi0/1
 udld port aggressive
```
</details>

---

## 📚 14. THUẬT NGỮ ANH–VIỆT

| Tiếng Anh | Tiếng Việt | Ghi chú |
|---|---|---|
| BPDU | Đơn vị dữ liệu giao thức bridge | Gói STP, gửi tới `01:80:C2:00:00:00` |
| Configuration BPDU | BPDU cấu hình | BPDU thường, mỗi 2 s |
| TCN BPDU | BPDU thông báo thay đổi topology | Gửi về root khi có thay đổi |
| Superior BPDU | BPDU "tốt hơn" | Có Root ID nhỏ hơn → nền của Root Guard |
| Inferior BPDU | BPDU "kém hơn" | Bị bỏ qua |
| Topology Change (TC) | Thay đổi topology | Gây flush/giảm MAC aging |
| MAC aging | Thời gian hết hạn entry MAC | Mặc định 300 s, giảm còn 15 s khi có TC |
| Root Bridge | Switch gốc | Điểm tham chiếu của cây |
| Root Port | Cổng gốc | Đường về root tốt nhất |
| Designated Port | Cổng chỉ định | Forward trên 1 segment |
| **Alternate Port** | Cổng thay thế | RSTP: dự phòng cho **Root Port** |
| **Backup Port** | Cổng dự phòng | RSTP: dự phòng cho **Designated Port** cùng segment |
| Discarding | Loại bỏ | State RSTP, gộp Blocking+Listening+Disabled |
| **Edge port** | Cổng biên | Port PortFast (nối PC/server) |
| **Point-to-point link** | Liên kết điểm-điểm | Full-duplex → RSTP dùng handshake |
| ⚠️ **Shared link** | Liên kết chia sẻ | Half-duplex → RSTP mất khả năng nhanh |
| **Proposal / Agreement** | Đề xuất / Đồng thuận | Handshake làm RSTP nhanh |
| **Sync** | Đồng bộ hóa | Switch block hết port designated trước khi Agreement |
| PVST+ | STP mỗi VLAN | 1 instance/VLAN. Load-balance được nhưng tốn CPU |
| Rapid PVST+ | PVST+ nhanh | RSTP + per-VLAN. Cisco khuyến nghị |
| **MST / MSTP** | Multiple Spanning Tree | IEEE 802.1s. Nhóm VLAN vào ít instance |
| **MST Region** | Vùng MST | Xác định bởi Name + Revision + Mapping |
| **Digest** | Hash của mapping | ⭐ So sánh digest = cách nhanh nhất tìm lệch region |
| **IST (MST0)** | Cây nội bộ | Bắt buộc có, chứa VLAN chưa map, nói chuyện ra ngoài region |
| MSTI | Instance MST | MST1, MST2… chỉ tồn tại trong region |
| CST | Cây chung | Cây ở ngoài region |
| CIST | Cây chung và nội bộ | CST + IST |
| **Boundary port** | Cổng biên region | Nối ra ngoài region hoặc sang PVST+ |
| PVST Simulation | Mô phỏng PVST | MST giả vờ nói tiếng PVST+ ở boundary |
| **PortFast** | Chuyển nhanh | Bỏ Listening/Learning → Forwarding ngay |
| **BPDU Guard** | Bảo vệ BPDU | Nhận BPDU trên PortFast port → err-disable |
| ⚠️ **BPDU Filter** | Lọc BPDU | Interface-level = tắt STP hẳn (nguy hiểm) |
| **Root Guard** | Bảo vệ root | Superior BPDU → `ROOT_Inc` block |
| **Loop Guard** | Bảo vệ chống loop | BPDU ngừng đến → `LOOP_Inc` block |
| **UDLD** | Phát hiện link một chiều | Echo-based, L2 độc lập. Normal / Aggressive |
| Unidirectional link | Liên kết một chiều | TX được, RX không (hay gặp ở fiber) |
| **Err-disable** | Vô hiệu do lỗi | Trạng thái port bị guard tắt |
| Errdisable recovery | Tự hồi phục | Tự bật lại port sau interval |
| Inconsistent port | Cổng không nhất quán | `ROOT_Inc` / `LOOP_Inc` / `PVST_Peer_Inc` |
| **EtherChannel / Port-channel** | Gộp cổng | Nhiều link vật lý → 1 link logic |
| **LACP** (802.3ad / 802.1AX) | Giao thức kết tập link | ⭐ Chuẩn IEEE, đa vendor. `active`/`passive` |
| **PAgP** | Giao thức gộp cổng | Cisco độc quyền. `desirable`/`auto` |
| Static / `on` mode | Gộp tĩnh | Không đàm phán → dễ tạo loop |
| Bundle | Bó / gộp | Tập hợp port đã gộp thành công |
| `(P)` bundled | Đã vào bó | ✅ Trạng thái đúng |
| ⚠️ `(I)` individual | Độc lập | LACP thất bại, port **vẫn forward** → nguy cơ loop |
| `(s)` suspended | Tạm ngưng | Không có partner, port **không forward** |
| `(u)` unsuitable | Không phù hợp | Tham số lệch giữa member |
| `(H)` hot-standby | Dự phòng nóng | Do `lacp max-bundle` |
| min-links | Số link tối thiểu | Bundle chỉ up khi đủ N link |
| max-bundle | Số link active tối đa | Còn lại thành hot-standby |
| LACP rate fast | Nhịp LACP nhanh | 1 s thay vì 30 s |
| Misconfig guard | Bảo vệ cấu hình sai | Chống loop do EtherChannel lệch |
| Load-balancing hash | Băm chia tải | Quyết định flow đi link nào |
| **Elephant flow** | Luồng "voi" | 1 flow rất lớn — **không chia được** qua nhiều link |
| Bucket | Gáo / khay | 8 gáo hash → nên dùng 2/4/8 link |

---

## 🎯 15. ĐÚC KẾT MODULE-02

**3 điều rút ra:**

1. **RSTP nhanh vì "hỏi rồi đi", STP chậm vì "chờ cho chắc".** Proposal/Agreement thay thế timer.
   Nhưng điều đó **chỉ hoạt động trên point-to-point (full-duplex)** — một duplex mismatch
   sẽ biến port thành shared link và **phá luôn khả năng hội tụ nhanh**.

2. **MST không giảm số VLAN, nó giảm số cây phải tính.** Giá phải trả: **mọi switch bắt buộc
   có cùng Name + Revision + Mapping**. Thiếu 1 VLAN trong mapping = ra khỏi region = cây chia đôi.
   Lệnh cứu mạng: `show spanning-tree mst configuration digest` — **digest phải giống tuyệt đối**.

3. **EtherChannel loại bỏ STP convergence khỏi kịch bản mất 1 link.** STP chỉ thấy `Po1`,
   nên cắt 1 member = **không có Topology Change** = mất 0–1 gói. Và quy tắc sắt:
   **`channel-group` trên member, mọi thứ khác trên `interface Port-channel`.**

🧠 **Một câu để nhớ:** *L2 không có TTL nên loop là chết. Mọi thứ trong module này —
STP, RSTP, MST, các Guard, UDLD, EtherChannel — chỉ là các cách khác nhau để trả lời một câu hỏi
duy nhất: **"làm sao dùng được mọi đường dây mà không tạo vòng lặp?"***

---

### ✅ TỰ CHẤM

**Phần A — Trả lời được bằng lời của mình, không nhìn tài liệu:**

| # | Câu | ✅ |
|:---:|---|:---:|
| 1 | Kể 4 thay đổi khiến RSTP nhanh hơn STP | ☐ |
| 2 | RSTP có mấy state? Kể ra. Alternate vs Backup port khác gì? | ☐ |
| 3 | 3 loại link type của RSTP? Cái nào phá hội tụ nhanh, vì sao? | ☐ |
| 4 | Mô tả quy trình Proposal → Sync → Agreement | ☐ |
| 5 | Superior BPDU là gì? Liên quan tính năng nào? | ☐ |
| 6 | STP xử lý Topology Change thế nào? RSTP khác ra sao? | ☐ |
| 7 | 3 thứ phải khớp cho MST region? Kiểm tra bằng lệnh gì? | ☐ |
| 8 | MST0/IST là gì? Boundary port là gì? | ☐ |
| 9 | MST priority hiện = priority + gì? Khác PVST+ ra sao? | ☐ |
| 10 | BPDU Filter interface vs global — cái nào nguy hiểm, vì sao? | ☐ |
| 11 | Root Guard vs Loop Guard: kích hoạt khi nào, đặt ở port nào, trạng thái gì? | ☐ |
| 12 | UDLD normal vs aggressive khác gì? Có cần bên kia hỗ trợ? | ☐ |
| 13 | Loop Guard vs UDLD: tầng nào, bắt lỗi gì, nên dùng cái nào? | ☐ |
| 14 | Bảng tương thích LACP và PAgP — cặp nào KHÔNG bundle? | ☐ |
| 15 | 6 điều kiện phải giống nhau để member port vào bundle | ☐ |
| 16 | `(P)`, `(I)`, `(s)`, `(u)`, `(H)`, `(SU)`, `(RU)`, `(SM)` nghĩa là gì? | ☐ |
| 17 | Vì sao `(I)` nguy hiểm hơn `(s)`? | ☐ |
| 18 | Vì sao nên dùng 2/4/8 link EtherChannel? | ☐ |
| 19 | Cắt 1 member EtherChannel có gây TC không? Vì sao? | ☐ |
| 20 | Quy tắc cấu hình EtherChannel (gõ gì ở đâu)? | ☐ |

**Phần B — Lab (từ topology 4 switch, tự làm không xem hướng dẫn):**

| # | Yêu cầu | ✅ |
|:---:|---|:---:|
| 1 | Dựng 4 switch có vòng, trunk đầy đủ, native VLAN 999, nonegotiate | ☐ |
| 2 | Ép root: D1 root VLAN 10 + backup VLAN 20 · D2 ngược lại. **Chứng minh load-balance** (Root Port khác nhau giữa 2 VLAN) | ☐ |
| 3 | Bật đủ 4 lớp bảo vệ: PortFast+BPDU Guard (access), Root Guard (downstream), Loop Guard (uplink), UDLD aggressive | ☐ |
| 4 | Xác nhận bằng `show spanning-tree summary` — và BPDU Filter Default phải **tắt** | ☐ |
| 5 | ⭐ **Test BPDU Guard**: cắm switch lạ vào port PC → port err-disable, đọc được `Reason` | ☐ |
| 6 | ⭐ **Test Root Guard**: ép switch access priority 0 → thấy `ROOT_Inc`, rồi tự hồi phục | ☐ |
| 7 | ⭐ **Đo hội tụ** PVST+ vs Rapid PVST+, điền bảng số gói mất | ☐ |
| 8 | Ép half-duplex → chứng minh link thành `Shr` và hội tụ chậm lại | ☐ |
| 9 | Bắt gói BPDU bằng Wireshark, đọc được Root ID / Cost / Flags, thấy Version đổi 0→2 | ☐ |
| 10 | Chuyển sang **MST**: region `CAMPUS-01` rev 1, instance 1 = VLAN 10,20,30 · instance 2 = VLAN 40,50,60 | ☐ |
| 11 | Xác nhận **digest giống nhau** trên cả 4 switch | ☐ |
| 12 | Load-balance MST: MST1 root D1, MST2 root D2, Root Port khác nhau | ☐ |
| 13 | ⭐ **Tái hiện lỗi MST**: bỏ 1 VLAN khỏi mapping trên 1 switch → digest đổi → thành boundary → sửa lại | ☐ |
| 14 | Tạo **L2 EtherChannel LACP** 2 link, `Po1(SU)` + cả 2 port `(P)` | ☐ |
| 15 | ⭐ **Test failover EtherChannel**: cắt 1 member → 0–1 gói mất, **không có TC** | ☐ |
| 16 | Tái hiện đủ 3 lỗi: `passive+passive` → `(s)` · trộn `on`+LACP → `(I)` · lệch allowed VLAN → `(u)` | ☐ |
| 17 | Đọc được log `%EC-5-CANNOT_BUNDLE2` và tìm ra nguyên nhân từ log | ☐ |
| 18 | Bật `lacp rate fast` (thấy flag đổi `SA`→`FA`) và `min-links` (thấy `Po1(SM)`) | ☐ |
| 19 | Tạo **L3 EtherChannel**: `Po2(RU)`, ping được, **không xuất hiện trong STP** | ☐ |
| 20 | Cố ý phá 1 thứ bất kỳ, tự tìm ra bằng quy trình 6 bước §12.3 trong 10 phút | ☐ |

> ⚠️ **Chưa tick hết Phần B thì đừng sang Module-03.** Layer 2 chiếm phần lớn câu simulation
> và câu "đọc output" của đề. Và ở production, sự cố L2 là loại khó tìm nhất — không lab đủ
> thì sau này bạn sẽ ngồi trước một cái loop lúc 3 giờ sáng mà không biết bắt đầu từ đâu.

---

## 🔗 16. TÀI LIỆU CHO MODULE NÀY

| Nguồn | Cụ thể |
|---|---|
| **Sách OCG 350-401** | Chương *Spanning Tree Protocol* (thường 2 chương: STP/RSTP và MST) + chương *EtherChannel*. ⭐ Đọc kỹ bảng so sánh mode |
| **Cisco doc** ⭐ | *Layer 2 Configuration Guide* → chương **Configuring Spanning Tree Protocol**, **Configuring MSTP**, **Configuring Optional STP Features**, **Configuring EtherChannels**. Search: `Catalyst 9300 spanning tree configuration guide` |
| **Cisco doc** ⭐ | *Understanding Rapid Spanning Tree Protocol (802.1w)* — tài liệu kinh điển giải thích Proposal/Agreement rõ nhất |
| **Cisco doc** | *Understanding Multiple Spanning Tree Protocol (802.1s)* |
| **Cisco doc** | *Spanning Tree Protocol Root Guard Enhancement* · *Spanning Tree PortFast BPDU Guard Enhancement* · *Understanding UDLD* |
| **Cisco doc** | *Understanding EtherChannel Load Balancing and Redundancy* |
| **Cisco Live** ⭐ | Search `Cisco Live spanning tree deep dive` và `Cisco Live campus LAN design best practices` — slide PDF chất lượng như sách |
| **NetworkLessons** ⭐ | Loạt bài STP/RSTP/MST — giải thích rõ nhất trên internet, nhiều bài free |
| **Video** | CBT Nuggets ENCOR — module Layer 2 · Keith Barker: search `Keith Barker RSTP`, `Keith Barker MST` |
| **Wireshark** | Filter `stp` (BPDU) · `slow` hoặc `lacp` (LACP PDU) · `vlan` (802.1Q tag) |
| **Forum** | https://community.cisco.com — search `MST region mismatch`, `etherchannel individual`, `loop guard vs udld` để đọc case thật |

---

**➡️ Tiếp theo:** [Module-03 — IP Routing nền tảng](Module-03-IP-Routing-Nen-tang.md)
*(Bảng định tuyến · AD · redistribute · EIGRP mức ENCOR · PBR)*
