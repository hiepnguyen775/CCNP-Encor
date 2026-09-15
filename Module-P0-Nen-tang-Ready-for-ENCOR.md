# Module-P0 — Nền tảng "Ready for ENCOR"

> 🧭 **Lộ trình:** Module-00 → `[Bạn đang ở đây] Module-P0` → Module-01 → Module-02 …
> **Tuần 1–2** · Không nằm trong blueprint 350-401, nhưng **nếu thiếu phần này thì đọc Module-04 (OSPF)
> và Module-05 (BGP) sẽ như đọc tiếng nước ngoài.**

---

## 🎯 Module này giải quyết vấn đề gì của bạn

Bạn tự đánh giá: *"biết VLAN/trunk/IP, mờ về OSPF/BGP/STP"*. Module này viết **đúng cho chỗ mờ đó**:

| Bạn đã biết | Module này làm gì |
|---|---|
| VLAN, trunk, IP, subnet | ✅ **Chỉ ôn nhanh dạng bảng** — không giảng lại từ đầu, đỡ mất thời gian |
| CLI Cisco | ⚡ Học có hệ thống: mode, `show`, `debug`, lưu config, hoàn tác |
| STP | 🔴 **Dạy từ gốc** — đây là chỗ mờ, và Module-02 sẽ đào rất sâu |
| Cách router chọn đường | 🔴 **Dạy từ gốc** — nền của cả 5 module routing sau |
| OSPF | 🔴 **Dạy mức single-area cho vững** — Module-04 sẽ nâng lên multi-area |
| NAT, ACL | 🟡 Dạy đủ dùng — Module-06 và Module-10 sẽ nâng cao |
| BGP | ⏭️ **Không học ở đây.** BGP cần nền routing vững trước. Để Module-05 |

**Kết thúc module này bạn phải làm được:** từ lab trắng, tự dựng 2 switch + trunk + 2 VLAN + inter-VLAN
routing + 3 router OSPF + NAT + ACL, **trong 60 phút, không nhìn tài liệu.**

---

# 📌 TÓM TẮT — đọc 10 phút là nắm khung

## Module này trả lời một câu hỏi duy nhất

> **"Một gói tin đi từ máy tôi ra Internet thì gặp những gì trên đường?"**

Sáu thứ bạn sắp học chính là **sáu trạm** trên hành trình đó. Không phải sáu chủ đề rời rạc.

## Toàn module trong một hình

```
   [PC]  ──①──▶  SWITCH L2  ──②──▶  ROUTER L3  ──③──▶  ROUTER BIÊN  ──▶ INTERNET

   ① VLAN     — cách ly máy nào nói chuyện được với máy nào       (§3.3)
      STP     — chặn vòng lặp để mạng không tự sập                (§3.4)

   ② Bảng route — chọn đường: longest prefix → AD → metric        (§3.5)
      OSPF      — router tự học đường, không phải khai tay        (§3.6)

   ③ NAT     — đổi IP riêng thành IP public                       (§3.7)
      ACL     — quyết định gói nào được đi, gói nào bị chặn       (§3.8)
```

## 7 ý phải nhớ

| # | Ý | Một câu |
|:---:|---|---|
| 1 | **VLAN** | Cắt một switch vật lý thành nhiều mạng logic. **Khác VLAN thì phải có router mới nói chuyện được** |
| 2 | **Trunk** | Một sợi cáp chở **nhiều VLAN**, phân biệt bằng thẻ 802.1Q. VLAN phải tồn tại ở **cả hai đầu** |
| 3 | **STP** | Mạng có vòng lặp thì broadcast chạy mãi → sập. STP **chủ động chặn bớt đường** để còn đúng một lối đi |
| 4 | **Thứ tự chọn đường** | **Longest prefix → AD → metric.** Đúng thứ tự này, không bao giờ đảo |
| 5 | **AD** | Mức độ *tin cậy nguồn tin*: Connected 0 · Static 1 · OSPF 110 · RIP 120. **Số nhỏ = tin hơn** |
| 6 | **NAT** | Nhiều máy dùng chung một IP public, phân biệt nhau bằng **số port** |
| 7 | **ACL** | Duyệt **từ trên xuống, khớp dòng nào dừng dòng đó**, và cuối luôn có `deny` ngầm |

## Bảng lệnh cốt lõi

| Lệnh | Cho biết gì |
|---|---|
| `show vlan brief` | VLAN nào tồn tại, port nào thuộc VLAN nào |
| `show interfaces trunk` | Trunk lên chưa, chở được VLAN nào |
| `show spanning-tree` | Ai là Root Bridge, port nào bị chặn |
| `show ip route` | Bảng định tuyến — đường đi router đang dùng |
| `show ip ospf neighbor` | OSPF đã bắt tay được chưa (phải `FULL`) |
| `show ip nat translations` | NAT đang đổi IP nào thành IP nào |
| `show access-lists` | ACL đang chặn/cho qua bao nhiêu gói |

## 🗺️ Bố cục module — đọc theo đúng thứ tự này

| Phần | Tên | Đọc thế nào | Thời gian |
|:---:|---|---|:---:|
| **1** | 🧠 **CÁI ĐÓ LÀ GÌ** | Đọc **một mạch**, toàn ví von, không lệnh | 1 giờ |
| **2** | ⚙️ **NÓ CHẠY THẾ NÀO** | Đọc kỹ, đối chiếu sơ đồ. Bảng để tra sau | 4 giờ |
| **3** | 🧪 **NHÌN THẤY NÓ** | [LAB Tuần 1](Module-P0-LAB-Tuan1.md) + [LAB Tuần 2](Module-P0-LAB-Tuan2.md) | 10 giờ |
| **4** | 🏗️ **TOPO & KIẾN TRÚC** | Ghép 6 thứ thành một mạng. **Vẽ lại trên giấy** | 1 giờ |
| **📎** | **PHỤ LỤC** | 🔴 **KHÔNG đọc lần đầu** — chỉ tra khi cần | — |

**Chia theo 2 tuần:**

| Tuần | Đọc gì | Lab gì |
|:---:|---|---|
| **1** | Phần 1 (toàn bộ) → Phần 2 mục **§3.1–3.4** | [LAB Tuần 1](Module-P0-LAB-Tuan1.md): VLAN · Inter-VLAN · STP |
| **2** | Phần 2 mục **§3.5–3.8** → **Phần 4** | [LAB Tuần 2](Module-P0-LAB-Tuan2.md): Static · OSPF · NAT · ACL |

> **Nếu bạn thấy nản giữa chừng:** đọc lại **Phần 1**. Nó ngắn, không có lệnh,
> và nó là thứ duy nhất bạn thật sự cần *hiểu* — phần còn lại chỉ là chi tiết để tra.

---

## ✅ 1. Chuẩn bị trước khi học

| Cần có | Chi tiết |
|---|---|
| Lab | EVE-NG chạy được, đã qua checklist Module-00 §9 |
| Image | **1 image router** (vIOS) + **1 image switch** (vIOS-L2). Chưa có switch → dùng Packet Tracer cho Tuần 1 |
| RAM | Lab lớn nhất module này: 3× vIOS-L2 + 2× vIOS = **3.3 GB** ✅ thoải mái |
| Thời lượng | 2 tuần × 10 giờ = 20 giờ |
| Kiến thức trước | Biết IP là gì, biết subnet mask. Nếu chưa chắc subnet → xem §2.1 |

---

## 🧠 PHẦN 1 — CÁI ĐÓ LÀ GÌ

> **Đọc phần này TRƯỚC, đọc một mạch, đừng ghi chép gì.** Ở đây không có lệnh, không có bảng tra —
> chỉ có ví von đời thường để bạn bật ra *"à, ra nó là thế"*.
>
> **Cách tự kiểm tra:** đọc xong mỗi mục, gấp tài liệu lại và **nói lại bằng lời của bạn trong 3 câu**.
> Nói được thì đi tiếp. Không nói được thì đọc lại mục đó — đừng cố nhớ, hãy cố *hiểu*.

### 2.1 STP như một cái cây trong rừng dây

Tưởng tượng bạn có 4 switch nối chéo nhau đủ đường — đó là một **mạng lưới** (mesh), có vòng.
STP không cắt dây vật lý, nó **chọn ra một cái cây** (tree) từ mạng lưới đó:

- **Root Bridge** = gốc cây. Cả mạng chỉ có 1 gốc.
- **Root Port** = mỗi switch có 1 nhánh chỉ về gốc. "Đường về nhà của tôi là đường này."
- **Blocking port** = những cành gây vòng → STP **treo biển "cấm đi"**, nhưng dây vẫn ở đó.
- Khi 1 nhánh chính đứt → STP **bỏ biển cấm** ở cành dự phòng → mạng tự lành.

🧠 **Một câu để nhớ:** *STP không xóa dây, nó chỉ chọn dây nào được dùng. Dây bị block vẫn nằm đó
chờ tới lượt.*

**Vì sao phải hiểu chỗ này:** người mới hay nghĩ "block port là port hỏng". Không —
port blocking vẫn **nhận BPDU** để biết khi nào cần chuyển sang forwarding. Nó đang canh, không đang ngủ.

### 2.2 Longest prefix match như địa chỉ nhà

Bạn có 3 tờ chỉ đường đến nhà tôi:

| Tờ | Nội dung | Prefix |
|---|---|---|
| A | "Đi Việt Nam" | `/8` |
| B | "Đi TP.HCM" | `/16` |
| C | "Đi số 12 đường Nguyễn Huệ, Quận 1, TP.HCM" | `/32` |

Bạn dùng tờ nào? **Tờ C** — cụ thể nhất, dù cả 3 đều đúng.

Router y hệt: có `10.0.0.0/8`, `10.1.0.0/16`, `10.1.1.0/24` — gói tới `10.1.1.5` sẽ đi theo `/24`.
**Không quan tâm route nào học từ protocol nào.**

🧠 **Một câu để nhớ:** *Cụ thể thắng tin cậy. Longest prefix đứng trước AD, luôn luôn.*

### 2.3 AD như mức độ tin cậy nguồn tin

Bạn muốn biết đường đi. Có 4 người nói khác nhau:

| Người | AD | Vì sao tin cỡ đó |
|---|:---:|---|
| Bạn **tự nhìn thấy** con đường | 0 | Không gì tin hơn mắt mình → Connected |
| **Bạn tự tay ghi** vào sổ | 1 | Bạn ghi thì bạn chịu trách nhiệm → Static |
| Người **cùng công ty**, có bản đồ đầy đủ | 110 | Đồng nghiệp đáng tin → OSPF |
| Người **nghe kể lại** từ người khác | 120 | Truyền tai → RIP |

🧠 **Một câu để nhớ:** *AD = "tôi tin nguồn này bao nhiêu". Số càng nhỏ càng tin.*

### 2.4 OSPF: link-state vs distance-vector

| | Distance-vector (RIP) | Link-state (OSPF) |
|---|---|---|
| Kiểu thông tin | "Đến X thì đi hướng tôi, xa 3 hop" | "Đây là **toàn bộ bản đồ** mạng" |
| Ví von | **Hỏi đường người đi qua** | **Có bản đồ Google Maps offline** |
| Tính đường | Tin lời người ta | **Tự tính** bằng Dijkstra |
| Hội tụ | Chậm, dễ loop | Nhanh, không loop trong 1 area |
| Tốn tài nguyên | Ít | Nhiều CPU/RAM (phải lưu bản đồ) |

🧠 **Một câu để nhớ:** *RIP hỏi đường, OSPF có bản đồ. Vì có bản đồ nên OSPF phải đồng bộ bản đồ —
đó chính là ý nghĩa của LSDB và của việc neighbor phải lên "Full".*

### 2.5 Vì sao OSPF có "area"

Có bản đồ toàn mạng là tốt, nhưng mạng 500 router thì bản đồ khổng lồ:
- Mỗi lần 1 link đâu đó nhấp nháy → **cả 500 router** phải tính lại Dijkstra
- Router nhỏ ở nhánh xa không đủ RAM lưu bản đồ

**Area = chia bản đồ thành từng tờ.** Router trong area 10 chỉ giữ chi tiết area 10, còn các area
khác chỉ biết "có mạng đó, đi qua ABR này". Link nhấp nháy trong area 10 **không làm area 20 tính lại**.

🧠 **Một câu để nhớ:** *Area tồn tại để giới hạn phạm vi ảnh hưởng của một sự cố. Đây là ý tưởng cốt lõi
mà Module-04 sẽ khai thác qua LSA type và stub area.*

---

## ⚙️ PHẦN 2 — NÓ CHẠY THẾ NÀO

> Giờ bạn đã có **hình dung**. Phần này lắp **tên gọi kỹ thuật, con số và câu lệnh thật** vào đó.
>
> Mỗi mục nối ngược về một ví von ở Phần 1:
>
> | Phần 1 (ví von) | → | Phần 2 (cơ chế) |
> |---|:---:|---|
> | §2.1 cái cây trong rừng dây | → | **§3.4 STP** |
> | §2.2 địa chỉ nhà · §2.3 nguồn tin | → | **§3.5 Router chọn đường** |
> | §2.4 link-state · §2.5 vì sao có area | → | **§3.6 OSPF** |
>
> ⚠️ **Bảng trong phần này là để TRA CỨU về sau, không phải để học thuộc ngay.**
> Đọc hiểu ý chính, rồi quay lại tra khi làm LAB.

### 3.1 Ôn nhanh: IP & Subnet (chỉ để đối chiếu, không giảng lại)

| Khái niệm | Nội dung |
|---|---|
| Địa chỉ IPv4 | 32 bit, viết 4 octet: `192.168.1.10` |
| Subnet mask | Phần nào là "mạng", phần nào là "host". `/24` = 24 bit đầu là mạng |
| Số host dùng được | `2^(32-prefix) - 2` (trừ network address và broadcast) |
| `/30` | 4 địa chỉ → **2 host** → chuẩn cho link point-to-point giữa 2 router |
| `/31` | 2 địa chỉ → 2 host (RFC 3021) → tiết kiệm hơn `/30` cho P2P |
| `/32` | 1 địa chỉ → loopback |
| Private IP (RFC1918) | `10.0.0.0/8` · `172.16.0.0/12` · `192.168.0.0/16` |
| Wildcard mask | **Ngược của subnet mask.** `255.255.255.0` → wildcard `0.0.0.255`. Dùng trong ACL và OSPF `network` |

**Bảng prefix hay dùng — nên nhớ thuộc:**

| Prefix | Mask | Host dùng được | Dùng cho |
|---|---|:---:|---|
| /30 | 255.255.255.252 | 2 | Link P2P router-router |
| /29 | 255.255.255.248 | 6 | Segment rất nhỏ |
| /28 | 255.255.255.240 | 14 | Phòng nhỏ |
| /27 | 255.255.255.224 | 30 | VLAN nhỏ |
| /26 | 255.255.255.192 | 62 | VLAN vừa |
| /25 | 255.255.255.128 | 126 | VLAN lớn |
| /24 | 255.255.255.0 | 254 | VLAN chuẩn |

> 💡 **Wildcard mask — mẹo tính:** lấy `255.255.255.255` trừ subnet mask.
> `/26` = `255.255.255.192` → wildcard = `0.0.0.63`.

---

### 3.2 CLI Cisco — bảng bạn sẽ dùng suốt 20 tuần

**Các mode và cách di chuyển:**

| Mode | Prompt | Vào bằng | Làm được gì |
|---|---|---|---|
| User EXEC | `R1>` | Mặc định khi vào console | Chỉ vài lệnh `show` giới hạn |
| Privileged EXEC | `R1#` | `enable` | Toàn bộ `show`, `debug`, `ping`, `copy` |
| Global config | `R1(config)#` | `configure terminal` | Cấu hình toàn thiết bị |
| Interface config | `R1(config-if)#` | `interface Gi0/0` | Cấu hình 1 interface |
| Routing config | `R1(config-router)#` | `router ospf 1` | Cấu hình protocol định tuyến |
| Line config | `R1(config-line)#` | `line con 0` | Cấu hình console/vty |

**Cách thoát:** `exit` = lùi 1 cấp · `end` hoặc `Ctrl+Z` = về Privileged EXEC ngay.

**Lệnh phải thuộc lòng:**

| Lệnh | Làm gì | Ghi chú |
|---|---|---|
| `show running-config` | Config **đang chạy** (trong RAM) | Viết tắt `sh run` |
| `show startup-config` | Config **lúc khởi động** (trong NVRAM) | |
| `write memory` / `copy run start` | **Lưu config** | ⚠️ Không gõ = reboot là mất hết |
| `show ip interface brief` | Bảng IP + trạng thái mọi interface | ⭐ Lệnh dùng nhiều nhất. Viết tắt `sh ip int br` |
| `show ip route` | Bảng định tuyến | ⭐ |
| `show version` | Version IOS, uptime, license | |
| `show interfaces Gi0/0` | Chi tiết 1 interface: lỗi, tốc độ, duplex, drop | Dùng khi troubleshoot lớp 1–2 |
| `show cdp neighbors detail` | Thiết bị Cisco kề bên + IP của nó | ⭐ Vẽ lại topology khi không có sơ đồ |
| `show logging` | Log của thiết bị | |
| `terminal monitor` | Cho log hiện ra khi vào bằng **SSH** | Console tự có, SSH thì phải bật |
| `no debug all` / `undebug all` | **Tắt hết debug** | ⚠️ Nhớ lệnh này — debug bật quên tắt là treo thiết bị |

**Thủ thuật CLI tiết kiệm thời gian:**

| Thủ thuật | Ví dụ | Tác dụng |
|---|---|---|
| Viết tắt | `sh ip int br` | Gõ đủ để không nhập nhằng là được |
| `Tab` | `sh ru` + Tab → `show running-config` | Tự hoàn thành |
| `?` | `show ip ?` | Liệt kê lệnh tiếp theo |
| Pipe filter | `sh run \| section ospf` | ⭐ Chỉ xem phần OSPF |
| | `sh run \| include ip address` | Chỉ các dòng chứa chuỗi đó |
| | `sh ip route \| begin 10.0` | Từ dòng đó trở xuống |
| `no <lệnh>` | `no ip address` | Hoàn tác |
| `do` | `R1(config)# do sh ip int br` | Chạy lệnh EXEC khi đang ở config mode |
| `Ctrl+Shift+6` | | Ngắt lệnh đang treo (ping/traceroute) |

**3 lệnh nên gõ ngay khi vào lab mới** (đỡ khổ về sau):

```
no ip domain lookup        ! Gõ sai lệnh không bị treo 30s để tra DNS
line con 0
 exec-timeout 0 0          ! Console không tự logout
 logging synchronous       ! Log không cắt ngang dòng đang gõ
```

---

### 3.3 VLAN & Trunk

| Khái niệm | Nội dung |
|---|---|
| VLAN là gì | Chia 1 switch vật lý thành nhiều broadcast domain logic |
| VLAN ID | 12 bit → **1–4094**. VLAN 1 mặc định. 1002–1005 dành riêng (Token Ring/FDDI) |
| Access port | Thuộc **1 VLAN**, frame gửi ra **không có tag** |
| Trunk port | Chở **nhiều VLAN**, frame có **tag 802.1Q** |
| 802.1Q tag | Thêm **4 byte** vào frame Ethernet: TPID `0x8100` + PCP(3 bit CoS) + DEI + VLAN ID(12 bit) |
| Native VLAN | VLAN duy nhất trên trunk **không bị tag**. Mặc định VLAN 1 |
| DTP | Cisco protocol tự đàm phán trunk. **Nên tắt** (`switchport nonegotiate`) vì là lỗ hổng bảo mật |
| SVI | `interface Vlan10` — interface logic L3 của VLAN, làm gateway |
| Voice VLAN | Cho IP phone: 1 access VLAN cho PC + 1 voice VLAN có tag |

**Lệnh VLAN:**

| Việc | Lệnh |
|---|---|
| Tạo VLAN | `vlan 10` → `name SALES` |
| Gán access port | `int Gi0/1` → `switchport mode access` → `switchport access vlan 10` |
| Tạo trunk | `int Gi0/0` → `switchport trunk encapsulation dot1q` → `switchport mode trunk` |
| Giới hạn VLAN trên trunk | `switchport trunk allowed vlan 10,20,99` |
| Đổi native VLAN | `switchport trunk native vlan 99` |
| Tắt DTP | `switchport nonegotiate` |
| Xem VLAN | `show vlan brief` |
| Xem trunk | `show interfaces trunk` ⭐ |

**Bảng đàm phán trunk (`switchport mode`) — đề CCNA/ENCOR hay hỏi:**

| Đầu A ↓ / Đầu B → | access | trunk | dynamic desirable | dynamic auto |
|---|:---:|:---:|:---:|:---:|
| **access** | access | ⚠️ lệch | access | access |
| **trunk** | ⚠️ lệch | **trunk** | **trunk** | **trunk** |
| **dynamic desirable** | access | **trunk** | **trunk** | **trunk** |
| **dynamic auto** | access | **trunk** | **trunk** | ❌ access |

> ⚠️ Nhớ ô cuối: **auto ↔ auto = KHÔNG lên trunk** (cả hai đều chờ bên kia mời).
> Trong thực tế production: **luôn cấu hình `mode trunk` tĩnh + `nonegotiate`**, không dựa vào DTP.

**Hai cách làm inter-VLAN routing:**

| Cách | Thiết bị | Cấu hình | Dùng khi nào |
|---|---|---|---|
| **Router-on-a-stick** | Router + switch L2 | Sub-interface `Gi0/0.10` + `encapsulation dot1Q 10` | Lab, mạng nhỏ. Nghẽn ở 1 link |
| **SVI trên switch L3** | Multilayer switch | `ip routing` + `interface Vlan10` | ⭐ Chuẩn production. Nhanh hơn nhiều |

---

### 3.4 STP — dạy từ gốc

#### Vấn đề STP giải quyết

Mạng L2 có vòng lặp (loop) thì xảy ra 3 thảm họa:

| Thảm họa | Chuyện gì xảy ra |
|---|---|
| **Broadcast storm** | 1 frame broadcast chạy vòng vô tận, nhân đôi mỗi vòng → chiếm hết băng thông, switch chết |
| **MAC table instability** | Cùng 1 MAC xuất hiện ở nhiều port, switch liên tục ghi lại bảng MAC |
| **Multiple frame copies** | Máy nhận cùng 1 frame nhiều lần → ứng dụng lỗi |

> ⚠️ **Vì sao L2 không tự chống loop được:** frame Ethernet **không có TTL**. Gói IP có TTL nên loop ở L3
> tự chết sau 255 hop. Frame L2 thì chạy mãi mãi. **Đây là lý do tồn tại của STP.**

#### STP hoạt động thế nào — 4 bước

| Bước | Việc | Chi tiết |
|:---:|---|---|
| **1** | Bầu **Root Bridge** | 1 switch duy nhất trong mạng làm "gốc" |
| **2** | Mỗi switch chọn **Root Port** | Port có đường về Root Bridge tốt nhất |
| **3** | Mỗi segment chọn **Designated Port** | 1 port được forward trên mỗi segment |
| **4** | Các port còn lại → **Blocking** | Chặn để phá vòng lặp |

#### Bước 1 — Bầu Root Bridge (bằng Bridge ID nhỏ nhất)

```
Bridge ID = [Bridge Priority (4 bit) + Extended System ID (12 bit = VLAN ID)] + MAC Address
              └─ 16 bit ─────────────────────────────────────────────────┘   └─ 48 bit ─┘
```

| So sánh theo thứ tự | Chi tiết |
|:---:|---|
| **1. Bridge Priority thấp hơn** | Mặc định **32768**. Chỉ đặt được **bội số của 4096** (0, 4096, 8192, … 61440) |
| **2. MAC address thấp hơn** | Nếu priority bằng nhau |

> ⭐ **Chi tiết ENCOR hay hỏi:** với **Extended System ID** (mặc định bật), priority hiển thị =
> `priority + VLAN ID`. Nên trong VLAN 10, priority mặc định hiện là **32778** (= 32768 + 10),
> không phải 32768. Đừng nhầm là ai đó đã đổi priority.

**Ép 1 switch làm root:**
```
spanning-tree vlan 10 priority 4096          ! đặt thẳng giá trị
spanning-tree vlan 10 root primary           ! macro: IOS tự tính priority thấp hơn root hiện tại
```

#### Bước 2 — Chọn Root Port (Root Path Cost nhỏ nhất)

| So sánh theo thứ tự | Chi tiết |
|:---:|---|
| 1. **Root Path Cost** thấp nhất | Tổng cost các link trên đường về root |
| 2. **Bridge ID của neighbor** thấp nhất | Nếu cost bằng nhau |
| 3. **Port ID** (priority + số port) thấp nhất | Tie-break cuối |

**Bảng cost (802.1D short mode — nhớ 3 con số này):**

| Tốc độ link | Cost (short) | Cost (long / 128-bit) |
|---|:---:|:---:|
| 10 Mbps | 100 | 2,000,000 |
| 100 Mbps | **19** | 200,000 |
| **1 Gbps** | **4** | **20,000** |
| 10 Gbps | **2** | 2,000 |

> 💡 Cost được cộng **khi frame ĐI VÀO** port, không phải đi ra. Chi tiết này quan trọng khi tính tay.

#### Port role & state

| Port Role | Nghĩa | STP | RSTP |
|---|---|:---:|:---:|
| **Root Port** | Đường về root tốt nhất (1 port/switch) | ✅ | ✅ |
| **Designated Port** | Port forward trên 1 segment | ✅ | ✅ |
| **Non-Designated / Blocking** | Bị chặn | ✅ | — |
| **Alternate Port** | Dự phòng cho Root Port | — | ✅ |
| **Backup Port** | Dự phòng cho Designated Port (cùng segment) | — | ✅ |

| Port State | STP (5 state) | Thời gian | RSTP (3 state) |
|---|:---:|---|:---:|
| Disabled | ✅ | — | — |
| **Blocking** | ✅ | — | → **Discarding** |
| **Listening** | ✅ | 15s (forward delay) | → Discarding |
| **Learning** | ✅ | 15s (forward delay) | ✅ **Learning** |
| **Forwarding** | ✅ | — | ✅ **Forwarding** |

#### Timer & thời gian hội tụ

| Timer | Mặc định | Ý nghĩa |
|---|:---:|---|
| **Hello** | 2 s | Root gửi BPDU mỗi 2 giây |
| **Forward Delay** | 15 s | Thời gian ở Listening và ở Learning |
| **Max Age** | 20 s | Không nhận BPDU trong 20s thì coi như mất root |

| Loại lỗi | Thời gian hội tụ STP | Vì sao |
|---|:---:|---|
| **Direct failure** (link cắm vào switch chết) | **~30 s** | Listening 15s + Learning 15s |
| **Indirect failure** (link ở xa chết) | **~50 s** | Max Age 20s + Listening 15s + Learning 15s |

> ⭐ **Đây chính là lý do RSTP ra đời.** 50 giây downtime là không thể chấp nhận. RSTP hội tụ trong
> **vài giây** nhờ: bỏ Listening, dùng **proposal/agreement handshake** thay vì chờ timer,
> và mọi switch đều tạo BPDU (không chỉ chuyển tiếp BPDU của root).

#### Các loại STP (bảng phải nhớ)

| Loại | Chuẩn | Số instance | Ghi chú |
|---|---|---|---|
| **STP / 802.1D** | IEEE | 1 cho cả mạng (CST) | Cổ, chậm (30–50s) |
| **PVST+** | Cisco | **1 instance mỗi VLAN** | Load-balance được theo VLAN. Tốn CPU nếu nhiều VLAN |
| **RSTP / 802.1w** | IEEE | 1 | Nhanh (vài giây) |
| **Rapid PVST+** | Cisco | 1 instance mỗi VLAN, nhanh | ⭐ Cisco khuyến nghị dùng |
| **MST / 802.1s** | IEEE | **Nhóm nhiều VLAN vào 1 instance** | Giải quyết vấn đề tốn CPU của PVST+. Học sâu ở Module-02 |

**Kiểm tra mode đang dùng:** `show spanning-tree summary`

#### Các loại Guard (Module-02 sẽ đào sâu, đây là bảng nhận diện)

| Guard | Đặt ở port nào | Chống gì | Lệnh |
|---|---|---|---|
| **PortFast** | Access port nối **PC/server** | Bỏ qua Listening/Learning → up ngay | `spanning-tree portfast` |
| **BPDU Guard** | Access port có PortFast | Ai cắm switch lạ vào → **err-disable port** | `spanning-tree bpduguard enable` |
| **Root Guard** | Port hướng xuống switch cấp dưới | Không cho switch lạ trở thành root | `spanning-tree guard root` |
| **Loop Guard** | Port root/alternate | Chống loop khi BPDU im lặng một chiều | `spanning-tree guard loop` |

> ⚠️ **Cặp đôi bắt buộc:** PortFast **luôn** đi cùng BPDU Guard. Bật PortFast mà không bật BPDU Guard
> là mời loop vào nhà.

---

### 3.5 Router chọn đường thế nào

#### Thứ tự 3 bước — PHẢI ĐÚNG THỨ TỰ NÀY

```
┌────────────────────────────────────────────────────────────────┐
│  1. LONGEST PREFIX MATCH   → prefix dài nhất (cụ thể nhất) thắng│
│     ↓ (nếu nhiều route CÙNG prefix, khác protocol)             │
│  2. ADMINISTRATIVE DISTANCE → AD thấp nhất thắng               │
│     ↓ (nếu cùng protocol, cùng prefix)                         │
│  3. METRIC                  → metric thấp nhất thắng           │
│     ↓ (nếu metric bằng nhau)                                   │
│  → ECMP: cài cả hai vào bảng, load-balance                     │
└────────────────────────────────────────────────────────────────┘
```

> ⚠️ **Sai lầm kinh điển:** nghĩ rằng "OSPF có AD 110 nên luôn thắng RIP (120)".
> Sai — nếu RIP có route `/24` và OSPF có `/16` cho cùng đích, thì **RIP thắng** vì prefix dài hơn.
> **Longest prefix đứng TRƯỚC AD.** Đề ENCOR gài chỗ này rất nhiều.

#### Bảng Administrative Distance — phải thuộc lòng

| Nguồn route | AD | Ghi nhớ |
|---|:---:|---|
| **Connected interface** | **0** | Không gì tin hơn cái mình nhìn thấy |
| **Static route** | **1** | Admin tự tay gõ → rất tin |
| EIGRP summary | 5 | |
| **eBGP** | **20** | Từ AS khác → tin hơn iBGP (nghe lạ nhưng đúng) |
| **EIGRP (internal)** | **90** | |
| OSPF | **110** | |
| IS-IS | 115 | |
| RIP | **120** | |
| EIGRP (external) | 170 | |
| **iBGP** | **200** | |
| Unreachable | 255 | AD 255 = **không cài vào bảng route** |

**6 con số phải nhớ chắc: `0 – 1 – 20 – 90 – 110 – 200`**

#### Đọc bảng định tuyến

```
R1# show ip route
Codes: L - local, C - connected, S - static, R - RIP, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area
       N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
       E1 - OSPF external type 1, E2 - OSPF external type 2

Gateway of last resort is 203.0.113.1 to network 0.0.0.0

S*    0.0.0.0/0 [1/0] via 203.0.113.1
      10.0.0.0/8 is variably subnetted, 4 subnets, 2 masks
C        10.0.0.0/30 is directly connected, GigabitEthernet0/0
L        10.0.0.1/32 is directly connected, GigabitEthernet0/0
O        10.1.1.0/24 [110/2] via 10.0.0.2, 00:05:12, GigabitEthernet0/0
O IA     10.2.2.0/24 [110/3] via 10.0.0.2, 00:04:58, GigabitEthernet0/0
```

| Thành phần | Nghĩa |
|---|---|
| `S*` | Static route, và `*` = **default route** (gateway of last resort) |
| `C` | Connected — subnet cắm trực tiếp |
| `L` | Local — chính IP của interface, luôn là `/32` |
| `O` | OSPF **intra-area** (trong cùng area) |
| `O IA` | OSPF **inter-area** (từ area khác, LSA type 3) |
| `O E2` | OSPF **external type 2** (redistribute từ ngoài) |
| `[110/2]` | **[AD / Metric]** ⭐ đọc được cái này là đọc được bảng route |
| `via 10.0.0.2` | Next-hop |
| `00:05:12` | Route học được cách đây bao lâu |

#### Static route

| Kiểu | Lệnh | Ghi chú |
|---|---|---|
| Chỉ next-hop | `ip route 10.1.1.0 255.255.255.0 10.0.0.2` | Chuẩn dùng nhất |
| Chỉ exit interface | `ip route 10.1.1.0 255.255.255.0 Gi0/0` | Dùng cho link P2P |
| Cả hai | `ip route 10.1.1.0 255.255.255.0 Gi0/0 10.0.0.2` | ⭐ Rõ ràng nhất |
| **Default route** | `ip route 0.0.0.0 0.0.0.0 203.0.113.1` | "Không biết đi đâu thì đi đây" |
| **Floating static** | `ip route 10.1.1.0 255.255.255.0 10.0.0.6 **200**` | ⭐ Thêm AD 200 → chỉ dùng khi route chính (AD nhỏ hơn) chết |
| Null route | `ip route 10.9.9.0 255.255.255.0 null0` | Bỏ traffic đi đâu đó |

> 💡 **Floating static hoạt động thế nào:** route chính AD=1, route dự phòng AD=200.
> Bảng route chỉ cài route AD nhỏ hơn. Khi route chính chết → biến mất khỏi bảng → route AD 200
> "nổi lên" (float) thay thế. Đây là cách làm backup đơn giản nhất, dùng rất nhiều ở thực tế.

---

### 3.6 OSPF single-area

| Khái niệm | Nội dung |
|---|---|
| Loại protocol | **Link-state** — mọi router biết toàn bộ bản đồ mạng (khác vector-distance chỉ biết "đi hướng nào") |
| Thuật toán | **Dijkstra SPF** — tự tính cây đường đi ngắn nhất từ chính mình |
| AD | **110** |
| Metric | **Cost** = `reference-bandwidth / interface-bandwidth` |
| Reference bandwidth | Mặc định **100 Mbps** |
| Multicast | Hello gửi tới `224.0.0.5` (all OSPF), `224.0.0.6` (DR/BDR) |
| Protocol number | IP protocol **89** (không phải TCP/UDP) |
| Router ID | 32 bit dạng IP. Ưu tiên: `router-id` gõ tay → IP loopback cao nhất → IP interface active cao nhất |
| Area | Nhóm router chia sẻ cùng LSDB. **Area 0 = backbone** |

> ⭐ **Bẫy cost trên Gigabit:** cost = 100 / 1000 = 0.1 → IOS làm tròn thành **1**.
> Nghĩa là **Gi (1G), 10G, 100G đều có cost = 1** → OSPF không phân biệt được! Cách sửa:
> ```
> router ospf 1
>  auto-cost reference-bandwidth 100000    ! đơn vị Mbps → 100 Gbps
> ```
> ⚠️ Phải đặt **giống nhau trên MỌI router** trong domain OSPF. Đề ENCOR hỏi chỗ này.

**Bảng cost mặc định (reference 100 Mbps):**

| Interface | Bandwidth | Cost |
|---|---|:---:|
| Serial | 1.544 Mbps | 64 |
| Ethernet | 10 Mbps | 10 |
| FastEthernet | 100 Mbps | 1 |
| GigabitEthernet | 1 Gbps | **1** ⚠️ |
| 10 GigabitEthernet | 10 Gbps | **1** ⚠️ |

**7 trạng thái neighbor (Module-04 sẽ đào sâu, đây là nhận diện):**

| State | Nghĩa | Kẹt ở đây thường vì |
|---|---|---|
| Down | Chưa nghe gì | Interface down, hoặc `passive-interface` |
| Init | Nhận hello nhưng chưa thấy tên mình trong đó | Một chiều — ACL chặn, hoặc lỗi L2 |
| 2-Way | Thấy nhau, đủ để bầu DR/BDR | ⭐ Bình thường nếu cả 2 đều là DROther |
| ExStart | Đàm phán ai là master | ⚠️ **Kẹt ở đây = MTU lệch** (lỗi kinh điển) |
| Exchange | Trao đổi mô tả database | |
| Loading | Xin các LSA còn thiếu | |
| **Full** | ✅ Đồng bộ hoàn tất | Đích cần đạt |

**Điều kiện phải khớp để lên neighbor (nhớ danh sách này để troubleshoot):**

| # | Phải khớp | Kiểm tra bằng |
|:---:|---|---|
| 1 | **Area ID** | `show ip ospf interface Gi0/0` |
| 2 | **Cùng subnet + mask** | `show ip int br` |
| 3 | **Hello / Dead interval** (mặc định 10 / 40 s) | `show ip ospf interface` |
| 4 | **Authentication** (loại + key) | `show ip ospf interface` |
| 5 | **MTU** | `show interfaces Gi0/0` |
| 6 | **Stub area flag** | `show ip ospf` |
| 7 | Router ID **không được trùng** | `show ip ospf` |
| 8 | Interface không được `passive-interface` | `show ip protocols` |

**Cấu hình OSPF cơ bản — 2 cách:**

```
! Cách 1 — dùng lệnh network (cách kinh điển, đề hỏi nhiều)
router ospf 1
 router-id 1.1.1.1
 network 10.0.0.0 0.0.0.3 area 0        ! 0.0.0.3 = wildcard của /30
 network 192.168.1.0 0.0.0.255 area 0
 passive-interface GigabitEthernet0/2   ! interface nối user: không gửi hello

! Cách 2 — bật trên interface (gọn hơn, thực tế hay dùng)
interface GigabitEthernet0/0
 ip ospf 1 area 0
```

**Lệnh kiểm tra OSPF:**

| Lệnh | Xem gì |
|---|---|
| `show ip ospf neighbor` | ⭐ Ai là neighbor, đang ở state nào |
| `show ip ospf interface brief` | Interface nào đang chạy OSPF, area nào, cost bao nhiêu |
| `show ip ospf interface Gi0/0` | Chi tiết: timer, DR/BDR, network type, auth |
| `show ip ospf database` | LSDB — bản đồ mạng |
| `show ip route ospf` | Chỉ các route học từ OSPF |
| `show ip protocols` | Tóm tắt cấu hình protocol + passive interface |
| `debug ip ospf adj` | ⚠️ Xem quá trình lên neighbor. Nhớ `undebug all` sau |

---

### 3.7 NAT — đủ dùng cho ENCOR

| Loại NAT | Làm gì | Dùng khi nào |
|---|---|---|
| **Static NAT** | 1 private ↔ 1 public, cố định | Server nội bộ cần ra Internet với IP cố định |
| **Dynamic NAT** | Nhiều private ↔ pool public, 1-1 | Ít dùng (tốn IP public) |
| **PAT / NAT overload** | Nhiều private → **1 public**, phân biệt bằng port | ⭐ Cái mà mọi mạng đang dùng |

**Quy tắc inside/outside — sai chiều là hỏng:**

| Thuật ngữ | Nghĩa |
|---|---|
| `ip nat inside` | Đặt trên interface hướng vào **mạng nội bộ** |
| `ip nat outside` | Đặt trên interface hướng ra **Internet** |
| Inside local | IP thật của máy nội bộ (VD `192.168.1.10`) |
| Inside global | IP nội bộ **sau khi NAT** (VD `203.0.113.5`) |
| Outside global | IP thật của máy ngoài Internet |

**Cấu hình PAT (dùng nhiều nhất):**
```
! 1. Định nghĩa mạng nào được NAT
access-list 1 permit 192.168.1.0 0.0.0.255

! 2. Chỉ định chiều
interface GigabitEthernet0/1
 ip nat inside
interface GigabitEthernet0/0
 ip nat outside

! 3. Bật PAT dùng IP của interface outside
ip nat inside source list 1 interface GigabitEthernet0/0 overload
```

**Kiểm tra:**
```
show ip nat translations         ! bảng NAT hiện tại
show ip nat statistics           ! đếm hit/miss
clear ip nat translation *       ! xóa bảng để test lại
debug ip nat                     ! xem NAT hoạt động (nhớ tắt)
```

> ⚠️ **Thứ tự xử lý:** với traffic từ **inside → outside**, router **routing TRƯỚC, NAT SAU**.
> Nghĩa là router phải có route tới đích **trước khi** NAT xảy ra. Nhiều người cấu hình NAT đúng
> nhưng thiếu default route nên vẫn không ra được Internet.

---

### 3.8 ACL — đủ dùng cho ENCOR

| Loại ACL | Số hiệu | Lọc theo | Đặt ở đâu |
|---|---|---|---|
| **Standard** | 1–99, 1300–1999 | **Chỉ source IP** | Gần **destination** (vì lọc thô) |
| **Extended** | 100–199, 2000–2699 | Source + Dest + Protocol + Port | Gần **source** (chặn sớm, tiết kiệm băng thông) |
| **Named** | Tên chữ | Cả hai loại trên | ⭐ Nên dùng — dễ sửa, dễ đọc |

**4 quy tắc vàng của ACL:**

| # | Quy tắc | Hệ quả |
|:---:|---|---|
| 1 | Xử lý **từ trên xuống**, khớp dòng nào **dừng luôn** | Đặt câu cụ thể lên trên, câu chung xuống dưới |
| 2 | Cuối ACL luôn có **implicit `deny any`** (ẩn, không thấy trong config) | ACL chỉ có `permit` vẫn chặn hết phần còn lại |
| 3 | ACL **chưa apply vào interface** thì chưa có tác dụng | Viết ACL xong phải `ip access-group` |
| 4 | 1 interface / 1 chiều / 1 protocol = **tối đa 1 ACL** | Muốn thêm rule thì sửa ACL, không tạo ACL thứ 2 |

**Cú pháp:**
```
! Standard (chỉ source)
access-list 10 permit 192.168.1.0 0.0.0.255
access-list 10 deny   any

! Extended (đầy đủ)
access-list 100 permit tcp 192.168.1.0 0.0.0.255 any eq 80
access-list 100 permit tcp 192.168.1.0 0.0.0.255 any eq 443
access-list 100 deny   ip  any any log

! Named — cách nên dùng
ip access-list extended ACL-USER-OUT
 permit tcp 192.168.1.0 0.0.0.255 any eq 80
 permit tcp 192.168.1.0 0.0.0.255 any eq 443
 permit icmp any any
 deny   ip any any log

! Apply
interface GigabitEthernet0/1
 ip access-group ACL-USER-OUT in
```

**Kiểm tra:**
```
show access-lists                        ! xem ACL + số lần match từng dòng 
show ip interface Gi0/1 | include access ! ACL nào đang apply
clear access-list counters               ! reset bộ đếm để test lại
```

> 💡 **Mẹo troubleshoot ACL:** `show access-lists` hiện **số lần match** mỗi dòng.
> Nếu dòng bạn nghĩ phải khớp mà counter = 0 → traffic không đến đó, hoặc đã bị dòng trên khớp trước.

---

## 🧪 PHẦN 3 — NHÌN THẤY NÓ

> LAB đã tách ra file riêng để bạn **mở song song** với lý thuyết — một cửa sổ đọc, một cửa sổ gõ.

> ### 👉 **[LAB Tuần 1 — Switching (VLAN · Inter-VLAN · STP)](Module-P0-LAB-Tuan1.md)**
> ### 👉 **[LAB Tuần 2 — Routing (Static · OSPF · NAT · ACL)](Module-P0-LAB-Tuan2.md)**

| Tuần | LAB | Trả lời câu hỏi | Ví von ở Phần 1 | Cơ chế ở Phần 2 |
|:---:|---|---|---|---|
| 1 | **P0-1** VLAN + Trunk | VLAN cách ly bằng cách nào? | — | §3.3 |
| 1 | **P0-2** Inter-VLAN Routing | Hai VLAN nói chuyện qua đâu? | — | §3.3 |
| 1 | **P0-3** STP | Có vòng lặp thì sao? Ép Root Bridge thế nào? | §2.1 cái cây | §3.4 |
| 2 | **P0-4** Static + Floating | Router chọn đường theo thứ tự nào? | §2.2 địa chỉ nhà · §2.3 nguồn tin | §3.5 |
| 2 | **P0-5** OSPF single-area | OSPF tự tìm đường ra sao? | §2.4 · §2.5 | §3.6 |
| 2 | **P0-6** NAT + ACL | Nhiều máy chung 1 IP public? ACL đặt ở đâu? | — | §3.7 · §3.8 |

> ⚠️ **Đọc lý thuyết mà không làm LAB thì coi như chưa học module này.**
> P0 là module **vá nền tảng** — nếu bạn chỉ đọc mà không gõ, lỗ hổng vẫn còn nguyên
> và nó sẽ lộ ra ở Module-02, 03, 04 khi mọi thứ khó hơn nhiều.


## 🏗️ PHẦN 4 — TOPO & KIẾN TRÚC

> Bạn vừa học **6 thứ rời rạc**: VLAN, STP, routing, OSPF, NAT, ACL.
> Phần này ghép chúng lại thành **một mạng hoàn chỉnh** để bạn thấy mỗi thứ nằm ở đâu.

### 4.1 Toàn bộ những gì bạn vừa học, trên một sơ đồ

```
                                    INTERNET
                                        ▲
                                        │ IP public: 203.0.113.1
                              ┌─────────┴─────────┐
                              │   ROUTER BIÊN     │
                              │                   │
                              │  ⑤ NAT: đổi IP    │  ← §3.7
                              │     private→public│
                              │  ⑥ ACL: chặn gói  │  ← §3.8
                              └─────────┬─────────┘
                                        │
                              ┌─────────┴─────────┐
                              │  ROUTER / SW L3   │
                              │                   │
                              │  ③ Bảng route:    │  ← §3.5
                              │     longest prefix│
                              │     → AD → metric │
                              │  ④ OSPF tự học    │  ← §3.6
                              │     đường         │
                              └────┬─────────┬────┘
                                   │ SVI     │ SVI
                          VLAN 10  │         │  VLAN 20
                              ┌────┴─────────┴────┐
                              │     SWITCH L2     │
                              │                   │
                              │  ② STP chặn vòng  │  ← §3.4
                              │     lặp           │
                              │  ① VLAN cách ly   │  ← §3.3
                              └──┬─────┬─────┬────┘
                                 │     │     │
                              [PC1] [PC2] [Máy in]
                              V10   V20    V20
```

### 4.2 Thứ tự một gói tin đi qua — và nó gặp cái gì

Bạn ở PC1 (VLAN 10, IP `10.10.10.11`), mở một trang web:

| # | Chặng | Cái bạn vừa học được dùng | Nếu hỏng thì sao |
|:---:|---|---|---|
| 1 | PC1 → switch | **VLAN** gắn gói vào broadcast domain 10 | Sai VLAN → không thấy gateway |
| 2 | Trong switch | **STP** đảm bảo không có vòng lặp | Có loop → broadcast storm, mạng chết |
| 3 | Switch → SVI VLAN 10 | Đây là **default gateway** của PC1 | Sai gateway → không ra khỏi VLAN được |
| 4 | Router tra bảng | **Longest prefix → AD → metric** chọn đường | Thiếu route → gói bị bỏ |
| 5 | Router biên | **NAT** đổi `10.10.10.11` → `203.0.113.1` | Không NAT → Internet không biết đường trả lời |
| 6 | Trước khi ra | **ACL** quyết định cho đi hay chặn | ACL sai chiều → chặn nhầm traffic hợp lệ |

> **Đây là toàn bộ Module-P0 trong một câu chuyện.** Nếu bạn kể lại được 6 chặng này
> bằng lời của mình, bạn đã "Ready for ENCOR".

### 4.3 Sáu thứ này sẽ lớn lên thành gì

| Bạn vừa học (P0) | Sẽ thành | Ở module |
|---|---|---|
| VLAN, trunk cơ bản | MST, EtherChannel, các loại Guard | **Module-02** |
| STP cơ bản | RSTP, MST, Root Guard, Loop Guard, BPDU Guard | **Module-02** |
| Bảng route, AD, static | Floating static, IP SLA + track, redistribute | **Module-03** |
| OSPF single-area | LSA type 1–7, area stub/NSSA, summarization, OSPFv3 | **Module-04A/B** |
| NAT cơ bản | NAT dual-ISP, thứ tự NAT–routing, NAT64 | **Module-06B** |
| ACL cơ bản | ACL nâng cao, CoPP, VACL/PACL, uRPF | **Module-10** |

> **Vì sao P0 đáng bỏ 2 tuần:** mọi module sau đều **xây tiếp** lên đúng 6 thứ này.
> Học hời hợt ở đây thì Module-04 (OSPF) sẽ như đọc tiếng nước ngoài.

### 4.4 Vẽ lại để nhớ

> **Bài tập 15 phút, làm trên giấy — đừng bỏ qua.**
>
> 1. Vẽ lại sơ đồ §4.1 **không nhìn tài liệu**
> 2. Đánh số ① → ⑥ vào đúng chỗ mỗi công nghệ nằm
> 3. Kể lại hành trình gói tin từ PC1 ra Internet, **nói thành tiếng**

<details>
<summary>Tự chấm</summary>

Bạn phải đặt được:
- **VLAN + STP** ở **switch L2** (dưới cùng)
- **Bảng route + OSPF** ở **router / switch L3** (giữa)
- **NAT + ACL** ở **router biên** (trên cùng, sát Internet)

Nếu bạn đặt NAT ở switch L2 hoặc STP ở router biên → **đọc lại §4.1**.

</details>

---

## 💡 4.5 Thực chiến đi làm — điều giáo trình thi không dạy

| Chủ đề | Thi dạy | Thực tế đi làm |
|---|---|---|
| **Native VLAN** | Mặc định VLAN 1 | ⭐ **Không bao giờ dùng VLAN 1 làm native.** Đổi sang VLAN "rác" không dùng (VD 999) và **không gán port nào vào đó**. Chống VLAN hopping |
| **`switchport mode dynamic`** | Có bảng đàm phán DTP | ⭐ Production **luôn cấu hình tĩnh** `mode trunk` hoặc `mode access` + `nonegotiate`. DTP là lỗ hổng |
| **VLAN 1** | VLAN mặc định | Không dùng VLAN 1 cho bất kỳ traffic thật nào. Prune nó khỏi trunk |
| **Root Bridge** | Bầu bằng MAC nhỏ nhất | ⚠️ **Không bao giờ để mạng tự bầu root.** MAC nhỏ nhất thường là switch cũ nhất, yếu nhất, ở tủ xa nhất. **Luôn ép root = switch core** |
| **STP** | Cấu hình được là xong | Sự cố L2 khó tìm nhất là **STP loop do 1 port bị bật sai**. Vì vậy: PortFast + BPDU Guard trên **mọi** access port, không có ngoại lệ |
| **Static route** | Cấu hình được | Static route đông (>20 dòng) là **nợ kỹ thuật**. Không ai nhớ dòng nào để làm gì → luôn viết `description`/comment và ghi vào tài liệu |
| **Floating static** | Backup route | Cẩn thận: static route **không biết đích có sống hay không**. Link vẫn "up" mà bên kia chết → traffic đi vào hố đen. Production dùng **IP SLA + object tracking** (Module-06/11) |
| **OSPF `network`** | Dùng `network x wildcard area 0` | Nhiều nơi thích `ip ospf 1 area 0` trên interface — rõ ràng hơn, không sợ sai wildcard |
| **`passive-interface`** | Có lệnh này | ⭐ Production dùng `passive-interface default` rồi `no passive-interface <link uplink>` — **an toàn hơn** (mặc định tắt, chỉ bật chỗ cần) |
| **reference-bandwidth** | Có lệnh đổi | Phải đổi **đồng loạt cả domain**. Đổi lẻ 1 router = tính cost lệch = đường đi kỳ dị. Ghi vào standard config của công ty |
| **NAT** | Cấu hình PAT | PAT có giới hạn ~65000 session/IP public. Mạng lớn phải dùng nhiều IP public (NAT pool). Và NAT làm **khó troubleshoot** — log phải lưu cả bảng NAT |
| **ACL** | Cấu hình được | ⚠️ **Luôn có dòng cuối `deny ip any any log`** — không phải để chặn (đã implicit) mà để **CÓ LOG**. Không log thì không biết mình vừa chặn mất dịch vụ nào |
| **Sửa ACL đang chạy** | Không dạy | ⚠️ Sửa named ACL đang apply trên production = **có khoảng thời gian ACL không đầy đủ** → có thể chặn mất traffic. Cách an toàn: tạo ACL mới tên khác → apply → xóa ACL cũ |
| **`write memory`** | Nhớ gõ | ⭐ Thói quen production: **backup config ra ngoài** trước khi sửa. `show run` → lưu file. Module-12 sẽ tự động hóa bằng Ansible |
| **Console timeout** | `exec-timeout 0 0` cho tiện | ⚠️ **Chỉ dùng trong lab.** Production phải có timeout (VD `exec-timeout 10 0`) — bỏ máy đi ăn cơm mà console mở là rủi ro bảo mật |

---

# 📎 PHỤ LỤC — TRA CỨU

> 🔴 **KHÔNG đọc phần này ở lần học đầu tiên.** Đây là tài liệu **tra cứu**, không phải để học.
>
> | Khi nào | Mở mục nào |
> |---|---|
> | Đang lab mà lỗi | **Gỡ lỗi nhanh** (§8) — có bảng *triệu chứng → nguyên nhân → cách sửa* |
> | Quên một lệnh | **Hộp lệnh** (§8.1) |
> | Tuần 20, đang ôn thi | **Bẫy đề** (§7) + **Quiz** (§9) |
> | Gặp từ tiếng Anh lạ | **Thuật ngữ** (§10) |
> | Học xong, muốn tự chấm | **Đúc kết + Milestone** (§11) |
>
> Đọc tuần tự phụ lục ở lần đầu là **cách nhanh nhất để kiệt sức và bỏ cuộc**.

---

## 🎓 7. BẪY TRONG ĐỀ ENCOR

Những chỗ đề 350-401 gài liên quan tới nội dung module này:

| # | Bẫy | Sự thật |
|:---:|---|---|
| 1 | *"OSPF AD 110 < RIP 120 nên OSPF luôn thắng"* | ❌ **Longest prefix match đứng TRƯỚC AD.** RIP `/24` thắng OSPF `/16` |
| 2 | *"STP priority mặc định là 32768"* | ⚠️ Hiển thị là **32768 + VLAN ID**. VLAN 10 → **32778**. Đề cho output và hỏi "ai đổi priority?" → không ai đổi |
| 3 | *"Gigabit và 10-Gigabit có OSPF cost khác nhau"* | ❌ Với reference 100 Mbps mặc định, **cả hai đều cost 1** |
| 4 | *"auto ↔ auto sẽ lên trunk"* | ❌ **dynamic auto ↔ dynamic auto = access.** Cả hai đều chờ được mời |
| 5 | Neighbor OSPF kẹt ở **EXSTART** | ⭐ Nghĩ ngay tới **MTU mismatch**. Đây là câu hỏi rất hay xuất hiện |
| 6 | Neighbor OSPF ở **2-WAY** mà không lên Full | ⚠️ Đây có thể **bình thường** — 2 router DROther trên segment broadcast không cần Full với nhau |
| 7 | *"ACL chỉ có permit thì cho qua hết"* | ❌ Vẫn có **implicit `deny any`** ở cuối |
| 8 | Standard ACL đặt ở đâu | Gần **destination** (vì chỉ lọc source, đặt gần source sẽ chặn oan) |
| 9 | Extended ACL đặt ở đâu | Gần **source** (chặn sớm, tiết kiệm băng thông) |
| 10 | NAT không hoạt động dù config đúng | ⭐ Kiểm tra **có route tới đích chưa** — routing xảy ra trước NAT |
| 11 | *"Floating static tự phát hiện đích chết"* | ❌ Static route chỉ theo trạng thái **interface**. Đích chết mà link up thì route vẫn còn |
| 12 | Direct vs indirect failure STP | Direct = **30s** (2× forward delay) · Indirect = **50s** (max age + 2× forward delay) |
| 13 | *"RSTP có 5 state như STP"* | ❌ RSTP có **3 state**: Discarding, Learning, Forwarding |
| 14 | `switchport trunk allowed vlan 10` | ⚠️ Lệnh này **THAY THẾ** toàn bộ danh sách, không phải thêm vào. Muốn thêm dùng `allowed vlan add 10` |
| 15 | Priority STP = 5000 | ❌ Chỉ nhận **bội số của 4096** |

---

## 🐛 8. GỠ LỖI NHANH

### 8.1 Hộp lệnh debug vạn năng

```
! === Lớp 1-2 ===
show ip interface brief                  ! interface nào up/down
show interfaces Gi0/0                    ! lỗi, drop, duplex, speed
show interfaces status                   ! (switch) trạng thái + VLAN + duplex
show cdp neighbors detail                ! ai đang cắm vào đâu
show mac address-table                   ! (switch) MAC học được ở port nào

! === VLAN / Trunk ===
show vlan brief                          ! VLAN + port nào thuộc VLAN nào
show interfaces trunk                    ! trunk status + allowed vlan
show interfaces Gi0/0 switchport         ! chi tiết mode, native vlan

! === STP ===
show spanning-tree vlan 10               ! root, port role, cost
show spanning-tree summary               ! mode đang dùng + số port từng state
show spanning-tree interface Gi0/1 detail
show spanning-tree inconsistentports     ! port bị guard chặn

! === Routing ===
show ip route                            ! bảng route
show ip route 10.1.1.1                   ! route cụ thể nào được dùng + AD
show ip protocols                        ! protocol nào chạy, passive interface
show ip cef 10.1.1.1                     ! đường forward thật sự

! === OSPF ===
show ip ospf neighbor                    ! lệnh đầu tiên phải chạy
show ip ospf interface brief              ! interface nào trong OSPF, cost
show ip ospf interface Gi0/0             ! timer, DR/BDR, auth, network type
show ip ospf database                    ! LSDB

! === NAT / ACL ===
show ip nat translations                 ! bảng NAT
show ip nat statistics
show access-lists                        ! ACL + counter match
show ip interface Gi0/1 | include access ! ACL nào đang apply

! === Debug (nhớ TẮT) ===
debug ip ospf adj
debug ip nat
debug ip packet detail                   ! ⚠️ NGUY HIỂM, chỉ dùng với ACL giới hạn
undebug all                              ! THUỘC LÒNG LỆNH NÀY
```

### 8.2 Bảng lỗi: triệu chứng → nguyên nhân → cách sửa

| # | Triệu chứng | Nguyên nhân thường gặp | Cách sửa |
|:---:|---|---|---|
| 1 | Interface `administratively down` | Chưa `no shutdown` | `int Gi0/0` → `no shutdown` |
| 2 | Interface `up` nhưng Protocol `down` | Lỗi lớp 2: encapsulation lệch, keepalive fail | `show int Gi0/0` xem chi tiết |
| 3 | Ping gói đầu mất, gói sau OK | ARP chưa học | ✅ Bình thường, không phải lỗi |
| 4 | 2 PC cùng VLAN không ping được | VLAN chưa tồn tại trên switch trung gian | `show vlan brief` **trên mọi switch** |
| 5 | Trunk không lên | 1 đầu là access, hoặc `allowed vlan` thiếu | `show int trunk` cả 2 đầu |
| 6 | Log `NATIVE_VLAN_MISMATCH` | Native VLAN 2 đầu trunk lệch | Đặt giống nhau |
| 7 | Access port `err-disable` | BPDU Guard bắt được BPDU → có switch cắm vào port PC | `show int status err-disabled` → tìm ai cắm sai · `shut`/`no shut` để bật lại |
| 8 | Mạng chậm bất thường, MAC table nhảy | ⚠️ **STP loop** | `show spanning-tree` tìm port lẽ ra phải block · kiểm tra có switch nào tắt STP |
| 9 | PC khác VLAN không ping được nhau | Thiếu inter-VLAN routing, hoặc PC thiếu default gateway | Cấu hình SVI/sub-interface · `show ip` trên PC |
| 10 | `show ip route` không có route mong đợi | Longest prefix khác đang thắng, hoặc AD lớn hơn | `show ip route <ip đích>` xem route nào thắng |
| 11 | Static route không vào bảng route | Next-hop không reachable | `ping <next-hop>` · dùng cả interface + next-hop |
| 12 | OSPF neighbor kẹt **INIT** | Hello 1 chiều | Ping 2 chiều · kiểm tra ACL trên interface |
| 13 | OSPF neighbor kẹt **EXSTART** | ⭐ **MTU lệch** | `show int \| inc MTU` cả 2 đầu → đặt giống nhau |
| 14 | OSPF neighbor **flap** liên tục | Hello/Dead timer lệch, hoặc CPU cao | `show ip ospf int Gi0/0 \| inc Timer` |
| 15 | OSPF Full nhưng route thiếu | Network chưa quảng bá (sai wildcard) | `show ip ospf int brief` xem interface có trong OSPF không |
| 16 | Đường OSPF đi "vòng vô lý" | Cost sai, hoặc `reference-bandwidth` lệch giữa các router | `show ip ospf int brief` so cost · thống nhất reference-bw |
| 17 | NAT config đúng nhưng không ra Internet | ⭐ Thiếu default route | `show ip route 0.0.0.0` |
| 18 | NAT: `show ip nat translations` trống | Chiều inside/outside sai, hoặc ACL không match | `show run \| inc nat` kiểm tra 2 chiều |
| 19 | ACL chặn mất dịch vụ không mong muốn | Thiếu dòng permit, hoặc thứ tự sai | `show access-lists` xem counter dòng nào ăn traffic |
| 20 | Sửa xong reboot mất hết | Chưa `write memory` | ⭐ Tập thói quen gõ `wr` sau mỗi lần sửa |

### 8.3 Quy trình troubleshoot 5 bước (dùng cả 20 tuần)

```
1. LỚP 1-2 TRƯỚC:  show ip int br  →  interface up/up chưa?
        ↓ có
2. LỚP 2:          show vlan brief · show int trunk · show mac address-table
        ↓ ổn
3. LỚP 3 - LOCAL:  ping next-hop trực tiếp được chưa?
        ↓ được
4. LỚP 3 - ROUTE:  show ip route <đích>  →  có route không? AD/metric đúng chưa?
        ↓ có
5. LỌC / DỊCH:     show access-lists · show ip nat translations
```

> 💡 **Nguyên tắc:** luôn đi **từ dưới lên** (lớp 1 → lớp 3 → lớp 4+).
> 80% sự cố nằm ở lớp 1–2. Nhảy ngay vào debug OSPF khi interface còn down là mất thời gian vô ích.

---

## 📝 9. QUIZ TỰ KIỂM TRA

**Câu 1.** Router có 3 route tới `10.1.1.5`: OSPF `10.1.0.0/16` (AD 110), RIP `10.1.1.0/24` (AD 120),
static `10.0.0.0/8` (AD 1). Route nào được dùng?

<details><summary>Xem đáp án</summary>

**RIP `10.1.1.0/24`.**

Longest prefix match đứng **trước** AD. `/24` là prefix dài nhất khớp với `10.1.1.5`,
nên nó thắng dù AD 120 là cao nhất. AD chỉ được xét khi **nhiều route có CÙNG prefix**.
</details>

---

**Câu 2.** `show spanning-tree vlan 20` báo `Priority 32788`. Có ai đổi priority không?

<details><summary>Xem đáp án</summary>

**Không.** `32788 = 32768 (mặc định) + 20 (VLAN ID)`.

Với Extended System ID bật (mặc định), giá trị hiển thị luôn = priority + VLAN ID.
Priority thực tế vẫn là mặc định 32768.
</details>

---

**Câu 3.** SW-A port `dynamic auto`, SW-B port `dynamic auto`. Link giữa 2 switch thành gì?

<details><summary>Xem đáp án</summary>

**Access port** (không lên trunk).

`dynamic auto` = "tôi sẽ lên trunk **nếu được mời**", nhưng không tự mời.
Hai bên cùng chờ → không ai mời → về access.

Cặp lên được trunk: `desirable↔desirable`, `desirable↔auto`, `trunk↔trunk`, `trunk↔desirable`, `trunk↔auto`.
</details>

---

**Câu 4.** OSPF neighbor kẹt ở **EXSTART**. Nguyên nhân khả năng cao nhất là gì?

<details><summary>Xem đáp án</summary>

**MTU mismatch** giữa 2 interface.

Ở giai đoạn ExStart, 2 router trao đổi DBD packet. Nếu MTU lệch, packet lớn bị drop →
không hoàn tất được đàm phán master/slave → kẹt mãi ở ExStart.

Kiểm tra: `show interfaces Gi0/0 | include MTU` trên **cả hai** router.

Các nguyên nhân khác (ít gặp hơn): trùng router-ID, lỗi unicast.
</details>

---

**Câu 5.** Cả 3 interface `GigabitEthernet`, `TenGigabitEthernet`, `FastEthernet` chạy OSPF với
cấu hình mặc định. Cost của mỗi cái là bao nhiêu?

<details><summary>Xem đáp án</summary>

Reference bandwidth mặc định = **100 Mbps**. Cost = `100 / bandwidth(Mbps)`, làm tròn lên, tối thiểu 1.

| Interface | Tính | Cost |
|---|---|:---:|
| FastEthernet (100 Mbps) | 100/100 = 1 | **1** |
| GigabitEthernet (1000 Mbps) | 100/1000 = 0.1 → làm tròn | **1** |
| TenGigabitEthernet (10000) | 100/10000 = 0.01 → làm tròn | **1** |

**Cả ba đều cost 1** → OSPF không phân biệt được link nhanh/chậm.
Đó là lý do phải đặt `auto-cost reference-bandwidth` (giống nhau trên mọi router).
</details>

---

**Câu 6.** ACL sau apply vào interface. Traffic HTTP từ `192.168.1.10` tới `8.8.8.8` có qua được không?

```
ip access-list extended TEST
 deny   ip any any
 permit tcp 192.168.1.0 0.0.0.255 any eq 80
```

<details><summary>Xem đáp án</summary>

**Không qua được.**

ACL xử lý **từ trên xuống, khớp dòng nào dừng luôn**. Dòng đầu `deny ip any any` khớp mọi traffic
→ chặn hết. Dòng `permit` bên dưới **không bao giờ được xét tới**.

Đây là lỗi kinh điển: câu deny chung phải đặt **cuối cùng**.
</details>

---

**Câu 7.** Cấu hình NAT/PAT đúng hoàn toàn, `ip nat inside`/`outside` đúng chiều, nhưng PC nội bộ
vẫn không ra được Internet. Kiểm tra gì trước?

<details><summary>Xem đáp án</summary>

**Kiểm tra có default route chưa:** `show ip route 0.0.0.0`

Với traffic inside → outside, router **routing TRƯỚC, NAT SAU**. Không có route tới đích thì
router drop gói trước khi NAT kịp xảy ra.

Thứ tự kiểm tra: (1) default route → (2) `show ip nat statistics` xem Hits có tăng →
(3) ACL định nghĩa NAT có match đúng subnet → (4) chiều inside/outside.
</details>

---

**Câu 8.** Mạng dùng STP 802.1D. Một link **ở xa** (không cắm trực tiếp vào switch đang xét) bị đứt.
Thời gian hội tụ là bao lâu, và tính thế nào?

<details><summary>Xem đáp án</summary>

**~50 giây** (indirect failure).

`Max Age (20s)` + `Listening (15s)` + `Learning (15s)` = **50s**

- Switch không cắm trực tiếp vào link đứt nên không biết ngay → phải chờ **Max Age 20s** để hết hạn BPDU cũ
- Rồi port blocking chuyển qua Listening (15s) → Learning (15s) → Forwarding

So sánh: **direct failure** (link cắm trực tiếp vào switch) = **30s** vì switch biết ngay,
không cần chờ Max Age.
</details>

---

**Câu 9.** Bạn gõ `switchport trunk allowed vlan 30` trên trunk đang allow VLAN 10,20.
Kết quả thế nào?

<details><summary>Xem đáp án</summary>

**Trunk giờ chỉ allow VLAN 30.** VLAN 10 và 20 bị loại bỏ → traffic 2 VLAN đó **chết**.

Lệnh `allowed vlan <list>` **THAY THẾ** toàn bộ danh sách.

Muốn **thêm vào**: `switchport trunk allowed vlan add 30`
Muốn **bớt ra**: `switchport trunk allowed vlan remove 20`

⚠️ Đây là lỗi gây downtime thật ở production. Rất nhiều người bị.
</details>

---

**Câu 10.** Có 2 static route tới cùng đích, cùng `/24`, một cái AD mặc định, một cái AD 200.
`show ip route` hiện mấy route?

<details><summary>Xem đáp án</summary>

**1 route** — cái AD 1 (mặc định của static).

Bảng route chỉ cài route có AD **nhỏ nhất**. Route AD 200 nằm chờ trong RIB nhưng không hiện
trong bảng forwarding.

Khi route AD 1 mất (interface down / next-hop unreachable) → route AD 200 **"nổi lên"** thay thế.
Đây là **floating static route**.

Nếu 2 route **cùng AD** → cả hai vào bảng → **ECMP load-balance**.
</details>

---

**Câu 11.** Bảng NAT hiện: `icmp 203.0.113.1:5 → 10.10.10.11:5 → 8.8.8.8:5`.
`10.10.10.11` gọi là gì? `203.0.113.1` gọi là gì?

<details><summary>Xem đáp án</summary>

- `10.10.10.11` = **Inside Local** (IP thật của máy nội bộ)
- `203.0.113.1` = **Inside Global** (IP mà máy nội bộ hóa trang thành, nhìn từ Internet)
- `8.8.8.8` = **Outside Global** (IP thật của máy ngoài)

Ghi nhớ: **Inside/Outside** = máy đó thuộc mạng nào · **Local/Global** = nhìn từ phía nào.
</details>

---

**Câu 12.** Vì sao PortFast phải luôn đi cùng BPDU Guard?

<details><summary>Xem đáp án</summary>

PortFast cho port **bỏ qua Listening/Learning** và vào Forwarding ngay. Điều đó an toàn khi port
nối **PC/server** (thiết bị không gửi BPDU).

Nhưng nếu ai đó cắm một **switch** vào port PortFast đó → port đã Forwarding ngay → **tạo loop tức thì**,
STP không có thời gian phản ứng.

**BPDU Guard** giải quyết: hễ port PortFast **nhận được BPDU** → chứng tỏ có switch cắm vào →
lập tức đưa port vào **err-disable** (tắt port). Loop bị chặn trong tích tắc.

Vì vậy trên production: **mọi access port** đều phải có cả hai.
</details>

---

## 📚 10. THUẬT NGỮ ANH–VIỆT

| Tiếng Anh | Tiếng Việt | Ghi chú |
|---|---|---|
| Broadcast domain | Miền quảng bá | 1 VLAN = 1 broadcast domain |
| Collision domain | Miền xung đột | Switch: mỗi port là 1 collision domain |
| Trunk | Đường trục chở nhiều VLAN | Frame có tag 802.1Q |
| Access port | Cổng truy cập | Thuộc 1 VLAN, frame không tag |
| Native VLAN | VLAN gốc trên trunk | VLAN duy nhất không bị tag |
| Tag / Tagging | Gắn nhãn VLAN | 4 byte thêm vào frame |
| SVI (Switch Virtual Interface) | Interface ảo của VLAN | `interface Vlan10` — gateway của VLAN |
| Sub-interface | Interface con | `Gi0/0.10` — dùng cho router-on-a-stick |
| Inter-VLAN routing | Định tuyến giữa các VLAN | |
| Spanning Tree | Cây bao trùm | Chọn cây từ mạng lưới có vòng |
| Loop | Vòng lặp | Thảm họa của mạng L2 |
| Root Bridge | Switch gốc | Điểm tham chiếu của cả cây STP |
| Root Port | Cổng gốc | Đường về root tốt nhất của mỗi switch |
| Designated Port | Cổng chỉ định | Port được forward trên 1 segment |
| Blocking / Discarding | Chặn / Loại bỏ | Port bị STP chặn để phá vòng |
| BPDU | Bridge Protocol Data Unit | Gói STP dùng để trao đổi thông tin |
| Bridge ID | Danh tính switch trong STP | Priority + Extended System ID + MAC |
| Convergence | Hội tụ | Thời gian mạng tự ổn định lại sau sự cố |
| Err-disable | Cổng bị vô hiệu do lỗi | Trạng thái BPDU Guard đưa port vào |
| Administrative Distance (AD) | Khoảng cách quản trị | Mức độ tin cậy của nguồn route |
| Metric | Số đo | Chi phí đi đường trong cùng protocol |
| Longest prefix match | Khớp tiền tố dài nhất | Route cụ thể nhất thắng |
| Next-hop | Chặng kế tiếp | Router kế tiếp trên đường đi |
| Default route | Đường mặc định | `0.0.0.0/0` — không biết đi đâu thì đi đây |
| Floating static | Static route "nổi" | Route dự phòng có AD cao hơn |
| Recursive lookup | Tra cứu đệ quy | Router tra next-hop rồi tra tiếp đường tới next-hop |
| ECMP | Định tuyến đa đường chi phí bằng nhau | Nhiều route cùng AD + metric → load-balance |
| Link-state | Trạng thái liên kết | OSPF — mỗi router có bản đồ toàn mạng |
| Distance-vector | Vector khoảng cách | RIP — chỉ biết "hướng nào, xa bao nhiêu" |
| LSDB | Link-State Database | Bản đồ mạng mà OSPF lưu |
| LSA | Link-State Advertisement | 1 mảnh thông tin trong LSDB |
| Adjacency | Quan hệ kề | Neighbor đã đồng bộ (state Full) |
| Area | Vùng | Cách OSPF chia nhỏ bản đồ |
| ABR / ASBR | Router biên vùng / biên hệ tự trị | Học sâu ở Module-04 |
| Passive interface | Interface thụ động | Không gửi hello, nhưng subnet vẫn được quảng bá |
| Reference bandwidth | Băng thông tham chiếu | Tử số trong công thức tính OSPF cost |
| NAT | Dịch địa chỉ mạng | Đổi IP trong header gói tin |
| PAT / NAT Overload | Dịch địa chỉ theo cổng | Nhiều IP private → 1 IP public |
| Inside local / global | IP nội bộ thật / sau khi dịch | |
| ACL | Danh sách kiểm soát truy cập | Lọc traffic |
| Implicit deny | Chặn ngầm | Dòng `deny any` ẩn ở cuối mọi ACL |
| Wildcard mask | Mặt nạ đại diện | Ngược của subnet mask, dùng trong ACL/OSPF |

---

## 🎯 11. ĐÚC KẾT MODULE-P0

**3 điều rút ra:**

1. **Thứ tự chọn route là `Longest prefix → AD → Metric`, không được đổi thứ tự.**
   Đây là nền của cả 5 module routing sau. Nhớ sai chỗ này thì Module-04 và Module-05 sẽ sai theo.

2. **STP không xóa dây, nó chọn dây nào được dùng.** Và **không bao giờ để mạng tự bầu root** —
   MAC nhỏ nhất thường là switch tệ nhất. Cặp PortFast + BPDU Guard là bắt buộc trên mọi access port.

3. **Routing xảy ra trước NAT.** Cấu hình NAT hoàn hảo mà thiếu default route thì vô nghĩa.
   Nguyên tắc chung: **luôn troubleshoot từ lớp thấp lên lớp cao.**

🧠 **Một câu để nhớ:** *L2 lo "frame đi trong cùng một mạng", L3 lo "gói đi giữa các mạng".
Mọi thứ trong 18 tuần tới chỉ là hai câu này được làm cho phức tạp hơn.*

---

### ✅ TỰ CHẤM — Milestone "Ready for ENCOR"

**Phần A — Trả lời được bằng lời của mình, không nhìn tài liệu:**

| # | Câu | ✅ |
|:---:|---|:---:|
| 1 | Thứ tự 3 bước router chọn route? | ☐ |
| 2 | AD của Connected, Static, eBGP, EIGRP, OSPF, iBGP? | ☐ |
| 3 | Nêu 2 bước bầu Root Bridge | ☐ |
| 4 | Vì sao `show spanning-tree vlan 10` báo priority 32778? | ☐ |
| 5 | STP direct failure mất bao lâu? Indirect failure? Tính thế nào? | ☐ |
| 6 | Kể tên 5 state của STP và 3 state của RSTP | ☐ |
| 7 | PortFast và BPDU Guard, mỗi cái làm gì, vì sao phải đi cùng nhau? | ☐ |
| 8 | Kể 5 điều kiện phải khớp để OSPF lên neighbor | ☐ |
| 9 | Neighbor OSPF kẹt EXSTART → nghi gì đầu tiên? | ☐ |
| 10 | Công thức OSPF cost? Vì sao Gi và 10G đều cost 1? | ☐ |
| 11 | 4 quy tắc vàng của ACL | ☐ |
| 12 | Standard ACL đặt gần đâu, Extended đặt gần đâu, vì sao? | ☐ |
| 13 | Inside local / Inside global / Outside global là gì? | ☐ |
| 14 | Floating static hoạt động thế nào? Điểm yếu của nó? | ☐ |
| 15 | `dynamic auto ↔ dynamic auto` ra kết quả gì? | ☐ |

**Phần B — Lab thực hành (bài kiểm tra cuối module):**

> ⏱️ **Từ lab TRẮNG, trong 60 phút, KHÔNG nhìn tài liệu**, dựng và verify:

| # | Yêu cầu | ✅ |
|:---:|---|:---:|
| 1 | 2 switch nối trunk, allowed vlan 10,20, native vlan 999, nonegotiate | ☐ |
| 2 | Access port có PortFast + BPDU Guard | ☐ |
| 3 | Ép 1 switch làm root bridge cho cả VLAN 10 và 20 | ☐ |
| 4 | Inter-VLAN routing hoạt động (PC VLAN 10 ping được PC VLAN 20) | ☐ |
| 5 | 3 router chạy OSPF area 0, tất cả neighbor **FULL** | ☐ |
| 6 | `auto-cost reference-bandwidth` đặt đồng nhất | ☐ |
| 7 | NAT/PAT cho LAN ra được "Internet" (loopback router giả ISP) | ☐ |
| 8 | ACL extended cho phép icmp/80/443, `deny ip any any log` ở cuối | ☐ |
| 9 | Verify được bằng: `show int trunk`, `show spanning-tree`, `show ip ospf nei`, `show ip nat trans`, `show access-lists` | ☐ |
| 10 | Cố ý phá 1 thứ, tự tìm ra và sửa được trong 10 phút | ☐ |

> ⚠️ **Chưa tick hết Phần B thì đừng sang Module-01.** Không phải để làm khó bạn —
> mà vì Module-02 đến Module-06 xây trực tiếp trên nền này. Thiếu nền thì càng học càng mờ,
> và đó là lúc người ta bỏ ngang.
>
> Nếu chưa đạt: **làm lại LAB P0-1 → P0-6 một lượt nữa**, lần này không xem hướng dẫn. Mất thêm 1 tuần
> nhưng tiết kiệm 5 tuần vật vã ở các module sau.

---

## 🔗 12. TÀI LIỆU CHO MODULE NÀY

| Nguồn | Cụ thể |
|---|---|
| **Sách OCG 350-401** | Các chương về Spanning Tree, EtherChannel, IP Routing, OSPF (đọc phần cơ bản, để phần nâng cao cho Module-02/04) |
| **Video** ⭐ | **Jeremy's IT Lab** (YouTube) — CCNA full course free. Xem các bài về VLAN, Trunk, STP, OSPF. Đúng level bạn cần vá |
| **Cisco doc** | *IP Routing Configuration Guide* · *Layer 2 Configuration Guide* (chương Spanning Tree) · *IP Routing: OSPF Configuration Guide* |
| **NetworkLessons** | Bài về STP và OSPF — giải thích rõ nhất trên internet. Có bài free |
| **Forum** | Kẹt lab → https://community.cisco.com · Kẹt EVE-NG → https://www.eve-ng.net/forum/ |
| **Wireshark** | Bắt gói BPDU (`filter: stp`), OSPF (`filter: ospf`), 802.1Q tag (`filter: vlan`) |

---

**➡️ Tiếp theo:** Module-01 — Packet Forwarding & Kiến trúc thiết bị *(sẽ viết ở batch 3)*
