# LAB 04A — Tuần 7: OSPF nền tảng & LSDB

> 📘 **Lý thuyết:** [Module-04A](Module-04A-OSPF-Nen-tang-va-LSDB.md) —
> đọc **Phần 1** và **Phần 2 mục §3.4 (neighbor state), §3.8 (network type), §3.9 (DR/BDR), §3.11 (LSA)**
> trước khi làm.
>
> ⏱️ **Thời gian:** ~7 giờ · 💾 **RAM:** 3 GB · 🧰 **Cần:** EVE-NG + 5× vIOS

---

## Lab này trả lời 6 câu hỏi

| # | Câu hỏi | Bước |
|:---:|---|:---:|
| 1 | Hai router bắt tay OSPF qua mấy bước, và kẹt ở bước nào nghĩa là lỗi gì? | 1 |
| 2 | LSDB thực sự chứa gì — và vì sao mọi router trong area đều có bản y hệt? | 2 |
| 3 | LSA type 1, 2, 3 trông như thế nào trong output thật? | 2 |
| 4 | Ai làm DR, và vì sao bầu lại không đổi được người đang làm? | 4 |
| 5 | Đổi network type sang point-to-point thì DR/BDR biến đi đâu? | 5 |
| 6 | Sáu lỗi OSPF kinh điển — triệu chứng và cách tìm ra | 6 |

> **Bước 2 (đọc LSDB) là phần quan trọng nhất module.** Đây là lúc OSPF thôi là "giao thức
> tự chạy" và trở thành thứ bạn **nhìn thấy được**. Module-04B xây thẳng lên đó.

---

## ⚠️ Đọc trước khi bắt đầu

| Điều cần biết | Chi tiết |
|---|---|
| **OSPF cần thời gian hội tụ** | Sau mỗi thay đổi, chờ **~40 giây** rồi mới xem kết quả. Đừng vội kết luận là hỏng |
| **Số liệu của bạn sẽ khác** | Router ID, LSA age, sequence number sẽ khác output mẫu. Đối chiếu **cấu trúc**, đừng so từng số |
| **Bước 6 là cố ý phá** | Sáu lỗi được gieo có chủ đích. Làm xong **nhớ sửa lại** trước khi sang Module-04B |
| **Giữ topology này** | Module-04B dùng lại đúng topology multi-area này |
| **Lỗi > 15 phút** | Ghi vào [`SO-TAY-LOI.md`](SO-TAY-LOI.md) |

---

## 🧪 4. LAB 04A — Topology multi-area + broadcast segment

### 4.1 Topology

```
   ┌─ AREA 1 ─┐        ┌────────── AREA 0 (broadcast) ──────────┐
                                                                  
  ┌────┐              ┌────┐        ┌─────────┐        ┌────┐
  │ R1 │══════════════│ R2 │────────│ BRIDGE  │────────│ R3 │
  └────┘  10.1.12.0/30└────┘ Gi0/1  │  (SW)   │ Gi0/1  └────┘
   Lo0: 1.1.1.1        Gi0/0        │10.0.0.0 │         Lo0: 3.3.3.3
   Lo1: 172.16.1.0/24  ABR          │   /24   │         Lo1: 172.16.3.0/24
                                    └────┬────┘           (AREA 2)
                                         │ Gi0/1
                                      ┌──┴─┐
                                      │ R4 │
                                      └────┘
                                    Lo0: 4.4.4.4
                                    Lo1: 172.16.4.0/24
                                        (AREA 3)
```

| Node | Interface | IP | Area | Vai trò |
|---|---|---|:---:|---|
| **R1** | Lo0 | 1.1.1.1/32 | 1 | Internal Router (area 1) |
| | Lo1 | 172.16.1.1/24 | 1 | |
| | Gi0/0 | 10.1.12.1/30 | 1 | |
| **R2** | Lo0 | 2.2.2.2/32 | 0 | ⭐ **ABR** (area 1 + area 0) |
| | Gi0/0 | 10.1.12.2/30 | 1 | |
| | Gi0/1 | 10.0.0.2/24 | 0 | Vào bridge |
| **R3** | Lo0 | 3.3.3.3/32 | 0 | ⭐ **ABR** (area 0 + area 2) |
| | Lo1 | 172.16.3.1/24 | 2 | |
| | Gi0/1 | 10.0.0.3/24 | 0 | Vào bridge |
| **R4** | Lo0 | 4.4.4.4/32 | 0 | ⭐ **ABR** (area 0 + area 3) |
| | Lo1 | 172.16.4.1/24 | 3 | |
| | Gi0/1 | 10.0.0.4/24 | 0 | Vào bridge |

**RAM: 4× 512 MB = 2 GB** ✅ · Bridge của EVE-NG **không tốn RAM**.

### 4.2 Dựng trong EVE-NG

1. Add new lab: `LAB-04A-OSPF-MultiArea`
2. Add node: **4× vIOS**, RAM 512, Ethernets **4**, prefix `R`
3. Click phải vùng trắng → **Network** → Type **Bridge**, name `SW-AREA0`
4. Nối dây:
   - `R1 Gi0/0` ↔ `R2 Gi0/0`
   - `R2 Gi0/1` ↔ `SW-AREA0`
   - `R3 Gi0/1` ↔ `SW-AREA0`
   - `R4 Gi0/1` ↔ `SW-AREA0`
5. Start all nodes

> 💡 **Object Bridge** là switch ảo thuần L2 của EVE-NG — dùng để tạo **segment broadcast**
> cho ≥3 router. Không ăn RAM, không cần cấu hình.

### 4.3 Config đầy đủ

**R1** (Internal Router, area 1):
```
enable
configure terminal
hostname R1
no ip domain lookup
!
interface Loopback0
 ip address 1.1.1.1 255.255.255.255
!
interface Loopback1
 ip address 172.16.1.1 255.255.255.0
!
interface GigabitEthernet0/0
 description ---> To R2 (AREA 1)
 ip address 10.1.12.1 255.255.255.252
 no shutdown
!
router ospf 1
 router-id 1.1.1.1
 auto-cost reference-bandwidth 100000
 network 1.1.1.1 0.0.0.0 area 1
 network 172.16.1.0 0.0.0.255 area 1
 network 10.1.12.0 0.0.0.3 area 1
 passive-interface Loopback0
 passive-interface Loopback1
!
line con 0
 exec-timeout 0 0
 logging synchronous
end
write memory
```

**R2** (ABR: area 1 + area 0):
```
enable
configure terminal
hostname R2
no ip domain lookup
!
interface Loopback0
 ip address 2.2.2.2 255.255.255.255
!
interface GigabitEthernet0/0
 description ---> To R1 (AREA 1)
 ip address 10.1.12.2 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/1
 description ---> To BRIDGE (AREA 0)
 ip address 10.0.0.2 255.255.255.0
 no shutdown
!
router ospf 1
 router-id 2.2.2.2
 auto-cost reference-bandwidth 100000
 network 2.2.2.2 0.0.0.0 area 0
 network 10.1.12.0 0.0.0.3 area 1
 network 10.0.0.0 0.0.0.255 area 0
 passive-interface Loopback0
!
line con 0
 exec-timeout 0 0
 logging synchronous
end
write memory
```

**R3** (ABR: area 0 + area 2):
```
enable
configure terminal
hostname R3
no ip domain lookup
!
interface Loopback0
 ip address 3.3.3.3 255.255.255.255
!
interface Loopback1
 description ---> AREA 2
 ip address 172.16.3.1 255.255.255.0
!
interface GigabitEthernet0/1
 description ---> To BRIDGE (AREA 0)
 ip address 10.0.0.3 255.255.255.0
 no shutdown
!
router ospf 1
 router-id 3.3.3.3
 auto-cost reference-bandwidth 100000
 network 3.3.3.3 0.0.0.0 area 0
 network 10.0.0.0 0.0.0.255 area 0
 network 172.16.3.0 0.0.0.255 area 2
 passive-interface Loopback0
 passive-interface Loopback1
!
line con 0
 exec-timeout 0 0
 logging synchronous
end
write memory
```

**R4** (ABR: area 0 + area 3):
```
enable
configure terminal
hostname R4
no ip domain lookup
!
interface Loopback0
 ip address 4.4.4.4 255.255.255.255
!
interface Loopback1
 description ---> AREA 3
 ip address 172.16.4.1 255.255.255.0
!
interface GigabitEthernet0/1
 description ---> To BRIDGE (AREA 0)
 ip address 10.0.0.4 255.255.255.0
 no shutdown
!
router ospf 1
 router-id 4.4.4.4
 auto-cost reference-bandwidth 100000
 network 4.4.4.4 0.0.0.0 area 0
 network 10.0.0.0 0.0.0.255 area 0
 network 172.16.4.0 0.0.0.255 area 3
 passive-interface Loopback0
 passive-interface Loopback1
!
line con 0
 exec-timeout 0 0
 logging synchronous
end
write memory
```

> 💡 **Về `passive-interface Loopback0`:** loopback không có neighbor nên gửi Hello là vô ích.
> `passive-interface` **vẫn quảng bá subnet** nhưng **không gửi Hello** — tiết kiệm và an toàn hơn.
> Ở production nên dùng `passive-interface default` rồi `no passive-interface <uplink>`.

---

### Bước 1 — Verify neighbor (Bảng 1)

```
R2# show ip ospf neighbor
```
**Output mẫu:**
```
Neighbor ID     Pri   State           Dead Time   Address         Interface
1.1.1.1           1   FULL/BDR        00:00:35    10.1.12.1       GigabitEthernet0/0
3.3.3.3           1   FULL/DROTHER    00:00:33    10.0.0.3        GigabitEthernet0/1
4.4.4.4           1   FULL/BDR        00:00:31    10.0.0.4        GigabitEthernet0/1
```

⭐ **Điền bảng — chạy `show ip ospf neighbor` trên cả 4 router:**

| Router | Neighbor & State | Ai là DR trên segment 10.0.0.0/24? | Ai là BDR? |
|---|---|---|---|
| R1 | | — (link P2P) | — |
| R2 | | | |
| R3 | | | |
| R4 | | | |

**Xác nhận DR/BDR:**
```
R2# show ip ospf interface GigabitEthernet0/1 | include State|Priority|Designated|Backup
```
**Output mẫu:**
```
  State DROTHER, Priority 1, Designated Router (ID) 4.4.4.4, Interface address 10.0.0.4
  Backup Designated router (ID) 3.3.3.3, Interface address 10.0.0.3
```

✅ **Checkpoint bước 1:**

| Kiểm tra | Mong đợi |
|---|---|
| Trên bridge (area 0): có đúng **1 DR** và **1 BDR** | ✅ |
| DR = router có **Router ID cao nhất** (priority đều = 1) → **R4 (4.4.4.4)** | ✅ |
| BDR = Router ID cao thứ 2 → **R3 (3.3.3.3)** | ✅ |
| ⭐ Giữa 2 DROther → state là **`2WAY/DROTHER`** | ⭐ ✅ **BÌNH THƯỜNG** |
| R1↔R2 (link P2P) → state `FULL/BDR` hoặc `FULL/  -` | ✅ |

> ⭐ **Chú ý:** ở topology này chỉ có R2 là DROther trên segment (R3=BDR, R4=DR),
> nên không thấy `2WAY/DROTHER`. Bước 4 sẽ ép tình huống đó xuất hiện.

**Xem chi tiết mọi thông số của interface — lệnh quan trọng nhất:**
```
R2# show ip ospf interface GigabitEthernet0/1
```
**Output mẫu:**
```
GigabitEthernet0/1 is up, line protocol is up
  Internet Address 10.0.0.2/24, Area 0, Attached via Network Statement
  Process ID 1, Router ID 2.2.2.2, Network Type BROADCAST, Cost: 100
  Topology-MTID    Cost    Disabled    Shutdown      Topology Name
        0           100       no          no            Base
  Transmit Delay is 1 sec, State DROTHER, Priority 1
  Designated Router (ID) 4.4.4.4, Interface address 10.0.0.4
  Backup Designated router (ID) 3.3.3.3, Interface address 10.0.0.3
  Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5
    oob-resync timeout 40
    Hello due in 00:00:03
  Supports Link-local Signaling (LLS)
  Cisco NSF helper support enabled
  IETF NSF helper support enabled
  Index 1/1/1, flood queue length 0
  Next 0x0(0)/0x0(0)/0x0(0)
  Last flood scan length is 3, maximum is 5
  Last flood scan time is 0 msec, maximum is 1 msec
  Neighbor Count is 2, Adjacent neighbor count is 2
    Adjacent with neighbor 3.3.3.3  (Backup Designated Router)
    Adjacent with neighbor 4.4.4.4  (Designated Router)
  Suppress hello for 0 neighbor(s)
```

⭐ **Bảng đọc output này — đây là lệnh bạn sẽ dùng 1000 lần:**

| Dòng | Nghĩa | Dùng để kiểm tra |
|---|---|---|
| `Area 0` | Area của interface | ⭐ Điều kiện #4 |
| `Attached via Network Statement` | Vào OSPF bằng `network` (hay `ip ospf area`) | Điều kiện #2 |
| `Network Type BROADCAST` | ⭐ Loại network | ⭐ Có bầu DR không |
| `Cost: 100` | Cost = 100000/1000 = 100 | reference-bandwidth |
| `State DROTHER, Priority 1` | Vai trò + priority | DR election |
| `Designated Router (ID) 4.4.4.4` | ⭐ Ai là DR | |
| `Hello 10, Dead 40` | ⭐ Timer | ⭐ Điều kiện #6 |
| `Wait 40` | Thời gian chờ trước khi bầu DR | Vì sao P2P hội tụ nhanh hơn |
| `Neighbor Count is 2, Adjacent neighbor count is 2` | ⭐ 2 neighbor, cả 2 đều **Full** | |
| *(không có dòng auth)* | Không bật authentication | Điều kiện #7 |

---

### Bước 2 — ⭐ Đọc LSDB (Bảng 2) — phần quan trọng nhất module

```
R1# show ip ospf database
```
**Output mẫu (R1 — chỉ ở area 1):**
```
            OSPF Router with ID (1.1.1.1) (Process ID 1)

                Router Link States (Area 1)

Link ID         ADV Router      Age  Seq#       Checksum Link count
1.1.1.1         1.1.1.1         120  0x80000004 0x00A3B1 3
2.2.2.2         2.2.2.2         118  0x80000003 0x001C2D 2

                Summary Net Link States (Area 1)

Link ID         ADV Router      Age  Seq#       Checksum
2.2.2.2         2.2.2.2         115  0x80000001 0x004E5F
3.3.3.3         2.2.2.2         115  0x80000001 0x00617A
4.4.4.4         2.2.2.2         115  0x80000001 0x00738C
10.0.0.0        2.2.2.2         115  0x80000001 0x0085AE
172.16.3.0      2.2.2.2         110  0x80000001 0x0097C0
172.16.4.0      2.2.2.2         110  0x80000001 0x00A9D2
```

⭐ **Nhận xét PHẢI rút ra — điền vào:**

| Câu hỏi | Trả lời của bạn |
|---|---|
| R1 có mấy **Router LSA (Type 1)**? Của ai? | |
| R1 có **Network LSA (Type 2)** không? Vì sao? | |
| Ai là **ADV Router** của mọi Summary LSA (Type 3)? Vì sao? | |
| `172.16.3.0` và `172.16.4.0` thuộc area nào? R1 biết topology của chúng không? | |
| R1 có thấy LSA nào của **area 2 / area 3** không (Router LSA)? | |

<details><summary>Đáp án</summary>

| Câu hỏi | Đáp án |
|---|---|
| Router LSA (Type 1)? | **2 cái**: của R1 (1.1.1.1) và R2 (2.2.2.2) — **chỉ router trong area 1** |
| Network LSA (Type 2)? | ⭐ **KHÔNG có.** Link R1↔R2 là **point-to-point** (serial-like) nên **không có DR** → không sinh Type 2. Segment broadcast nằm ở area 0, R1 không thấy |
| ADV Router của mọi Type 3? | ⭐ **2.2.2.2 (R2)** — vì **R2 là ABR duy nhất** của area 1. Mọi thông tin từ area khác đều do R2 "kể lại" |
| `172.16.3.0`, `172.16.4.0` | Thuộc **area 2** và **area 3**. R1 ⭐ **KHÔNG biết topology** của chúng — chỉ biết "đi qua R2, cost X" |
| LSA của area 2/3? | ⭐ **KHÔNG có Router LSA nào.** Type 1 và Type 2 **không bao giờ ra khỏi area**. R1 chỉ nhận **Type 3** |

⭐ **Đây là bằng chứng thực nghiệm cho câu:** *"OSPF là link-state TRONG area,
distance-vector GIỮA các area."*
</details>

**So sánh với LSDB của R2 (ABR, thấy 2 area):**
```
R2# show ip ospf database
```
**Output mẫu:**
```
            OSPF Router with ID (2.2.2.2) (Process ID 1)

                Router Link States (Area 0)

Link ID         ADV Router      Age  Seq#       Checksum Link count
2.2.2.2         2.2.2.2         200  0x80000004 0x00112A 2
3.3.3.3         3.3.3.3         198  0x80000005 0x00223B 2
4.4.4.4         4.4.4.4         195  0x80000005 0x00334C 2

                Net Link States (Area 0)

Link ID         ADV Router      Age  Seq#       Checksum
10.0.0.4        4.4.4.4         190  0x80000002 0x00445D

                Summary Net Link States (Area 0)

Link ID         ADV Router      Age  Seq#       Checksum
1.1.1.1         2.2.2.2         185  0x80000001 0x00556E
10.1.12.0       2.2.2.2         185  0x80000001 0x00667F
172.16.1.0      2.2.2.2         185  0x80000001 0x00788A
172.16.3.0      3.3.3.3         180  0x80000001 0x00899B
172.16.4.0      4.4.4.4         180  0x80000001 0x009AAC

                Router Link States (Area 1)

Link ID         ADV Router      Age  Seq#       Checksum Link count
1.1.1.1         1.1.1.1         120  0x80000004 0x00A3B1 3
2.2.2.2         2.2.2.2         118  0x80000003 0x001C2D 2

                Summary Net Link States (Area 1)
...
```

⭐ **Nhận xét:**
- R2 có **2 khối `Router Link States`** — một cho area 0, một cho area 1 → **ABR giữ LSDB riêng cho từng area**
- Có **`Net Link States (Area 0)`** với `Link ID 10.0.0.4` và `ADV Router 4.4.4.4`
  → ⭐ **LSA Type 2 do DR (R4) sinh ra**, LS ID = **IP interface của DR**
- Trong `Summary (Area 0)`: `172.16.3.0` do **3.3.3.3** sinh, `172.16.4.0` do **4.4.4.4** sinh
  → mỗi ABR tự quảng bá area của mình

#### Xem chi tiết từng loại LSA

**a) Type 1 — Router LSA:**
```
R1# show ip ospf database router 1.1.1.1
```
**Output mẫu:**
```
                Router Link States (Area 1)

  LS age: 145
  Options: (No TOS-capability, DC)
  LS Type: Router Links
  Link State ID: 1.1.1.1
  Advertising Router: 1.1.1.1
  LS Seq Number: 80000004
  Checksum: 0xA3B1
  Length: 60
   Number of Links: 3

    Link connected to: another Router (point-to-point)
     (Link ID) Neighboring Router ID: 2.2.2.2
     (Link Data) Router Interface address: 10.1.12.1
       TOS 0 Metrics: 100

    Link connected to: a Stub Network
     (Link ID) Network/subnet number: 10.1.12.0
     (Link Data) Network Mask: 255.255.255.252
       TOS 0 Metrics: 100

    Link connected to: a Stub Network
     (Link ID) Network/subnet number: 172.16.1.0
     (Link Data) Network Mask: 255.255.255.0
       TOS 0 Metrics: 1
```

⭐ **Đọc:** R1 khai 3 link — 1 link **point-to-point** tới R2, 2 link **stub network**
(subnet `10.1.12.0/30` và LAN `172.16.1.0/24`).

> 💡 Loopback0 (`1.1.1.1/32`) cũng là stub network nhưng có thể hiển thị riêng —
> tùy IOS version. Nếu bạn thấy `Number of Links: 4` thì đó là bình thường.

**b) Type 2 — Network LSA (chỉ trên segment broadcast):**
```
R2# show ip ospf database network
```
**Output mẫu:**
```
                Net Link States (Area 0)

  LS age: 210
  Options: (No TOS-capability, DC)
  LS Type: Network Links
  Link State ID: 10.0.0.4 (address of Designated Router)
  Advertising Router: 4.4.4.4
  LS Seq Number: 80000002
  Checksum: 0x445D
  Length: 36
  Network Mask: /24
        Attached Router: 4.4.4.4
        Attached Router: 3.3.3.3
        Attached Router: 2.2.2.2
```

⭐ **Đọc:**
- `Link State ID: 10.0.0.4 (address of Designated Router)` → ⭐ **LS ID = IP của DR**, không phải Router ID
- `Advertising Router: 4.4.4.4` → **DR sinh ra LSA này**
- `Attached Router` × 3 → cả 3 router trên segment

**c) Type 3 — Summary LSA:**
```
R1# show ip ospf database summary 172.16.3.0
```
**Output mẫu:**
```
                Summary Net Link States (Area 1)

  LS age: 165
  Options: (No TOS-capability, DC, Upward)
  LS Type: Summary Links(Network)
  Link State ID: 172.16.3.0 (summary Network Number)
  Advertising Router: 2.2.2.2
  LS Seq Number: 80000001
  Checksum: 0x97C0
  Length: 28
  Network Mask: /24
        MTID: 0         Metric: 101
```

⭐ **Đọc:**
- `Advertising Router: 2.2.2.2` → **R2 (ABR) sinh ra**, dù mạng gốc thuộc R3
- `Metric: 101` → cost từ **R2** tới `172.16.3.0` (100 qua bridge + 1 loopback)
- R1 sẽ **cộng thêm** cost từ R1 tới R2 (100) → **201**

**Kiểm tra dự đoán:**
```
R1# show ip route 172.16.3.0
```
**Output mẫu:**
```
Routing entry for 172.16.3.0/24
  Known via "ospf 1", distance 110, metric 201, type inter area
  Last update from 10.1.12.2 on GigabitEthernet0/0, 00:03:12 ago
```
✅ **`metric 201` = 101 (trong LSA) + 100 (R1→R2)** · `type inter area` → **`O IA`**

**d) Lệnh tổng hợp hữu ích:**
```
R2# show ip ospf database database-summary
```
**Output mẫu:**
```
            OSPF Router with ID (2.2.2.2) (Process ID 1)

Area 0 database summary
  LSA Type      Count    Delete   Maxage
  Router        3        0        0
  Network       1        0        0
  Summary Net   5        0        0
  Summary ASBR  0        0        0
  Type-7 Ext    0        0        0
  Opaque Link   0        0        0
  Opaque Area   0        0        0
  Subtotal      9        0        0

Area 1 database summary
  LSA Type      Count    Delete   Maxage
  Router        2        0        0
  Network       0        0        0
  Summary Net   6        0        0
  ...
```
⭐ **Đây là cách nhanh nhất đếm LSA theo type và area.** Chú ý:
`Area 0` có **1 Network LSA** (segment broadcast) · `Area 1` có **0 Network LSA** (link P2P).

```
R1# show ip ospf database self-originate         ! LSA do CHÍNH R1 sinh
R1# show ip ospf database adv-router 2.2.2.2     ! mọi LSA do R2 sinh
```

✅ **Checkpoint bước 2:**

| Kiểm tra | Mong đợi |
|---|---|
| R1: có **2** Router LSA (R1, R2) — không có LSA của R3/R4 | ⭐ ✅ |
| R1: **0** Network LSA (link P2P) | ✅ |
| R1: mọi Summary LSA đều có `ADV Router = 2.2.2.2` | ⭐ ✅ |
| R2: có **2 khối** `Router Link States` (Area 0 + Area 1) | ✅ |
| R2: Network LSA có `Link State ID` = **IP của DR** (`10.0.0.4`) | ⭐ ✅ |
| Metric trong `show ip route` = metric trong LSA 3 **+** cost tới ABR | ⭐ ✅ |
| `show ip ospf database database-summary`: Area 0 có 1 Network LSA, Area 1 có 0 | ✅ |

---

### Bước 3 — Verify routing table (Bảng 3)

```
R1# show ip route ospf
```
**Output mẫu:**
```
      2.0.0.0/32 is subnetted, 1 subnets
O IA     2.2.2.2 [110/101] via 10.1.12.2, 00:05:11, GigabitEthernet0/0
      3.0.0.0/32 is subnetted, 1 subnets
O IA     3.3.3.3 [110/201] via 10.1.12.2, 00:05:11, GigabitEthernet0/0
      4.0.0.0/32 is subnetted, 1 subnets
O IA     4.4.4.4 [110/201] via 10.1.12.2, 00:05:11, GigabitEthernet0/0
      10.0.0.0/8 is variably subnetted, 4 subnets, 3 masks
O IA     10.0.0.0/24 [110/200] via 10.1.12.2, 00:05:11, GigabitEthernet0/0
      172.16.0.0/16 is variably subnetted, 4 subnets, 2 masks
O IA     172.16.3.0/24 [110/201] via 10.1.12.2, 00:05:11, GigabitEthernet0/0
O IA     172.16.4.0/24 [110/201] via 10.1.12.2, 00:05:11, GigabitEthernet0/0
```

⭐ **Nhận xét:** **mọi route** trên R1 đều là **`O IA`** (inter-area) — vì R1 ở area 1,
mọi thứ khác đều nằm ngoài area 1.

**So sánh với R3 (ở area 0):**
```
R3# show ip route ospf
```
**Output mẫu:**
```
O        2.2.2.2 [110/100] via 10.0.0.2, 00:05:30, GigabitEthernet0/1      ← intra-area
O        4.4.4.4 [110/100] via 10.0.0.4, 00:05:30, GigabitEthernet0/1      ← intra-area
O IA     1.1.1.1 [110/201] via 10.0.0.2, 00:05:11, GigabitEthernet0/1      ← inter-area
O IA     10.1.12.0/30 [110/200] via 10.0.0.2, 00:05:11, GigabitEthernet0/1
O IA     172.16.1.0/24 [110/201] via 10.0.0.2, 00:05:11, GigabitEthernet0/1
O IA     172.16.4.0/24 [110/101] via 10.0.0.4, 00:05:11, GigabitEthernet0/1
```
⭐ R3 có **cả `O` (intra) và `O IA` (inter)** — vì R3 ở area 0 nên các router area 0 khác là intra-area.

**Test kết nối toàn mạng:**
```
R1# ping 172.16.3.1 source 172.16.1.1
R1# ping 172.16.4.1 source 172.16.1.1
R1# traceroute 172.16.4.1 source 172.16.1.1
```
**Output mẫu traceroute:**
```
  1 10.1.12.2 2 msec 1 msec 1 msec        ← R2 (ABR)
  2 10.0.0.4 3 msec 2 msec 2 msec         ← R4 qua bridge
```

✅ **Checkpoint bước 3:**

| Kiểm tra | Mong đợi |
|---|---|
| R1: **mọi** route OSPF là `O IA` | ✅ |
| R3: có cả `O` và `O IA` | ✅ |
| Metric `O IA` = metric trong LSA 3 + cost tới ABR | ⭐ ✅ |
| Ping full-mesh giữa 172.16.1.1 ↔ 172.16.3.1 ↔ 172.16.4.1 | ✅ |
| `traceroute` đi qua đúng ABR | ✅ |

---

### Bước 4 — ⭐ Thao tác DR/BDR Election

#### 4a) Xác nhận DR hiện tại

```
R2# show ip ospf interface Gi0/1 | include Designated|Backup
  Designated Router (ID) 4.4.4.4, Interface address 10.0.0.4
  Backup Designated router (ID) 3.3.3.3, Interface address 10.0.0.3
```
✅ Priority đều = 1 → **Router ID cao nhất thắng**: R4 = DR, R3 = BDR, R2 = DROther.

#### 4b) ⭐ Chứng minh NON-PREEMPTIVE (bẫy đề quan trọng nhất)

```
! Trên R2 — đặt priority CAO NHẤT
R2(config)# interface GigabitEthernet0/1
R2(config-if)# ip ospf priority 255
```

Chờ 60 giây rồi kiểm tra:
```
R2# show ip ospf interface Gi0/1 | include State|Priority|Designated
```
**Output mẫu:**
```
  Transmit Delay is 1 sec, State DROTHER, Priority 255
  Designated Router (ID) 4.4.4.4, Interface address 10.0.0.4
```

⭐ **KẾT QUẢ: R2 vẫn là `DROTHER` dù priority 255!** R4 (priority 1) **vẫn là DR**.

🎓 **Đây chính là non-preemptive.** Đề ENCOR hỏi đúng tình huống này.

#### 4c) Buộc bầu lại — 2 cách

**Cách 1 — `clear ip ospf process` trên mọi router của segment:**
```
R2# clear ip ospf process
Reset ALL OSPF processes? [no]: yes
R3# clear ip ospf process
Reset ALL OSPF processes? [no]: yes
R4# clear ip ospf process
Reset ALL OSPF processes? [no]: yes
```

**Cách 2 — shut/no shut interface của DR và BDR:**
```
R4(config)# interface Gi0/1
R4(config-if)# shutdown
! chờ vài giây
R4(config-if)# no shutdown
R3(config)# interface Gi0/1
R3(config-if)# shutdown
R3(config-if)# no shutdown
```

**Kiểm tra lại (chờ ~40 s cho Wait timer):**
```
R2# show ip ospf interface Gi0/1 | include State|Designated|Backup
```
**Output mẫu:**
```
  Transmit Delay is 1 sec, State DR, Priority 255
  Designated Router (ID) 2.2.2.2, Interface address 10.0.0.2
  Backup Designated router (ID) 4.4.4.4, Interface address 10.0.0.4
```
✅ Giờ **R2 = DR** (priority 255), **R4 = BDR** (Router ID cao nhất trong số còn lại).

#### 4d) Ép router KHÔNG bao giờ làm DR

```
R2(config)# interface GigabitEthernet0/1
R2(config-if)# ip ospf priority 0
```
Chờ, rồi:
```
R2# show ip ospf interface Gi0/1 | include State|Priority
  Transmit Delay is 1 sec, State DROTHER, Priority 0
```
⭐ **Priority 0 = luôn là DROther**, không bao giờ được bầu.

#### 4e) ⭐ Tạo tình huống `2WAY/DROTHER`

Đặt **cả R2 và R3** priority 0 → chỉ R4 có thể làm DR:
```
R2(config)# interface Gi0/1
R2(config-if)# ip ospf priority 0
R3(config)# interface Gi0/1
R3(config-if)# ip ospf priority 0
R4(config)# interface Gi0/1
R4(config-if)# ip ospf priority 255
```
Rồi `clear ip ospf process` trên cả 3.

```
R2# show ip ospf neighbor
```
**Output mẫu:**
```
Neighbor ID     Pri   State           Dead Time   Address         Interface
1.1.1.1           1   FULL/  -        00:00:35    10.1.12.1       GigabitEthernet0/0
3.3.3.3           0   2WAY/DROTHER    00:00:33    10.0.0.3        GigabitEthernet0/1
4.4.4.4         255   FULL/DR         00:00:31    10.0.0.4        GigabitEthernet0/1
```

⭐ **`3.3.3.3 → 2WAY/DROTHER`** — R2 và R3 đều DROther nên **không cần Full với nhau**.
**ĐÂY LÀ BÌNH THƯỜNG, KHÔNG PHẢI LỖI.**

Và chú ý: **không có BDR** (vì chỉ R4 có priority > 0) → nếu R4 chết, phải bầu DR mới từ đầu.

**Kiểm tra vẫn đủ route:**
```
R2# ping 172.16.3.1 source 2.2.2.2
```
✅ Vẫn thông — vì thông tin đi qua DR.

#### 4f) Dọn dẹp — trả về mặc định

```
R2(config)# interface Gi0/1
R2(config-if)# no ip ospf priority
R3(config)# interface Gi0/1
R3(config-if)# no ip ospf priority
R4(config)# interface Gi0/1
R4(config-if)# no ip ospf priority
! rồi clear ip ospf process trên cả 3
```

✅ **Checkpoint bước 4 — điền bảng:**

| Cấu hình | DR | BDR | Bài học |
|---|---|---|---|
| Priority đều 1 | | | Router ID cao nhất thắng |
| R2 priority 255 (không clear) | | | ⭐ |
| Sau `clear ip ospf process` | | | |
| R2 & R3 priority 0, R4 = 255 | | | ⭐ `2WAY/DROTHER` xuất hiện |

---

### Bước 5 — ⭐ Network Type: đổi Ethernet sang point-to-point

**a) Xem trạng thái hiện tại của link R1↔R2:**
```
R1# show ip ospf interface Gi0/0 | include Network Type|State|Designated|Wait
```
**Output mẫu:**
```
  Process ID 1, Router ID 1.1.1.1, Network Type BROADCAST, Cost: 100
  Transmit Delay is 1 sec, State BDR, Priority 1
  Designated Router (ID) 2.2.2.2, Interface address 10.1.12.2
  Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5
```
⚠️ Đây là link Ethernet **chỉ có 2 router** mà **vẫn bầu DR/BDR** — vô nghĩa.

**b) Đếm LSA trước khi đổi:**
```
R1# show ip ospf database database-summary | begin Area 1
```
Ghi lại số `Network` LSA của area 1.

**c) Đổi sang point-to-point (CẢ 2 ĐẦU):**
```
R1(config)# interface GigabitEthernet0/0
R1(config-if)# ip ospf network point-to-point
!
R2(config)# interface GigabitEthernet0/0
R2(config-if)# ip ospf network point-to-point
```

**d) Kiểm tra:**
```
R1# show ip ospf interface Gi0/0 | include Network Type|State|Designated|Wait|Hello
```
**Output mẫu:**
```
  Process ID 1, Router ID 1.1.1.1, Network Type POINT_TO_POINT, Cost: 100
  Transmit Delay is 1 sec, State POINT_TO_POINT
  Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5
```
⭐ `State POINT_TO_POINT` · ⭐ **không còn dòng `Designated Router`**

```
R1# show ip ospf neighbor
```
**Output mẫu:**
```
Neighbor ID     Pri   State           Dead Time   Address         Interface
2.2.2.2           0   FULL/  -        00:00:38    10.1.12.2       GigabitEthernet0/0
```
⭐ `FULL/  -` — **không có vai trò DR/BDR** · `Pri 0` (priority vô nghĩa trên P2P)

```
R1# show ip ospf database database-summary | begin Area 1
```
✅ Số `Network` LSA của area 1 = **0** (nếu trước đó đã là 0 thì confirm không tăng).

**e) ⚠️ Test lỗi: đổi 1 bên thôi**
```
R2(config)# interface Gi0/0
R2(config-if)# ip ospf network broadcast          ! cố ý lệch
```
```
R1# show ip ospf neighbor
```
→ Neighbor **mất** (hoặc kẹt, tùy IOS). Log có thể báo lỗi.

**Sửa lại:**
```
R2(config-if)# ip ospf network point-to-point
```

✅ **Checkpoint bước 5:**

| Kiểm tra | Mong đợi |
|---|---|
| `Network Type POINT_TO_POINT` trên cả 2 router | ✅ |
| `show ip ospf neighbor` → state `FULL/  -` | ⭐ ✅ |
| Không còn dòng `Designated Router` | ✅ |
| Area 1 không có Network LSA (Type 2) | ⭐ ✅ |
| Đổi 1 bên thôi → neighbor mất | ⭐ ✅ |

---

### Bước 6 — 🚀 LAB nâng cao: tái hiện & sửa 6 lỗi kinh điển

Làm từng lỗi, **tự chẩn đoán trước khi xem đáp án**, rồi sửa.

#### Lỗi 1 — 🔴 MTU mismatch → kẹt `EXSTART`

```
R1(config)# interface GigabitEthernet0/0
R1(config-if)# mtu 1400
```
Chờ ~60 s (hoặc `clear ip ospf process`):
```
R1# show ip ospf neighbor
```
**Output mẫu:**
```
Neighbor ID     Pri   State           Dead Time   Address         Interface
2.2.2.2           0   EXSTART/  -     00:00:35    10.1.12.2       GigabitEthernet0/0
```
⭐ **Kẹt `EXSTART`!**

**Chẩn đoán:**
```
R1# show interfaces Gi0/0 | include MTU
  MTU 1400 bytes, BW 1000000 Kbit/sec, DLY 10 usec,
R2# show interfaces Gi0/0 | include MTU
  MTU 1500 bytes, BW 1000000 Kbit/sec, DLY 10 usec,
```
```
R1# debug ip ospf adj
! Output sẽ báo:
%OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on GigabitEthernet0/0 from EXSTART to DOWN,
                Neighbor Down: Too many retransmissions
R1# undebug all
```

**Sửa:**
```
R1(config)# interface GigabitEthernet0/0
R1(config-if)# no mtu
```
✅ Neighbor lên `FULL` sau vài giây.

> ⭐ **Ghi vào `SO-TAY-LOI.md`:** `EXSTART` hoặc `EXCHANGE` → **kiểm tra MTU trước mọi thứ khác**.

#### Lỗi 2 — Area mismatch

```
R1(config)# router ospf 1
R1(config-router)# no network 10.1.12.0 0.0.0.3 area 1
R1(config-router)# network 10.1.12.0 0.0.0.3 area 5      ! cố ý sai area
```
```
R1# show ip ospf neighbor
! → Trống hoặc mất neighbor 2.2.2.2
R1# show ip ospf interface Gi0/0 | include Area
  Internet Address 10.1.12.1/30, Area 5, Attached via Network Statement
R2# show ip ospf interface Gi0/0 | include Area
  Internet Address 10.1.12.2/30, Area 1, Attached via Network Statement
```
⭐ **`Area 5` vs `Area 1`** → không lên neighbor.

**Chẩn đoán bằng debug:**
```
R2# debug ip ospf adj
%OSPF-4-ERRRCV: Received invalid packet: mismatched area ID, from backbone area
                must be virtual-link but not found from 10.1.12.1, GigabitEthernet0/0
R2# undebug all
```

**Sửa:**
```
R1(config)# router ospf 1
R1(config-router)# no network 10.1.12.0 0.0.0.3 area 5
R1(config-router)# network 10.1.12.0 0.0.0.3 area 1
```

#### Lỗi 3 — Timer mismatch

```
R1(config)# interface Gi0/0
R1(config-if)# ip ospf hello-interval 5
```
```
R1# show ip ospf neighbor
! → mất neighbor
R1# show ip ospf interface Gi0/0 | include Timer
  Timer intervals configured, Hello 5, Dead 20, Wait 20, Retransmit 5
R2# show ip ospf interface Gi0/0 | include Timer
  Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5
```
⭐ Chú ý: đổi hello 10→5, IOS **tự tính dead = 4×5 = 20**.

**Sửa (2 lựa chọn):**
```
! Cách A — trả về mặc định
R1(config-if)# no ip ospf hello-interval

! Cách B — đặt giống nhau cả 2 đầu (nếu muốn hội tụ nhanh)
R1(config-if)# ip ospf hello-interval 3
R1(config-if)# ip ospf dead-interval 12
R2(config-if)# ip ospf hello-interval 3
R2(config-if)# ip ospf dead-interval 12
```

#### Lỗi 4 — Duplicate Router ID

```
R3(config)# router ospf 1
R3(config-router)# router-id 4.4.4.4          ! trùng với R4
R3# clear ip ospf process
Reset ALL OSPF processes? [no]: yes
```
**Quan sát log:**
```
R2#
%OSPF-4-DUP_RTRID_NBR: OSPF detected duplicate router-id 4.4.4.4 from 10.0.0.3
                       on interface GigabitEthernet0/1
```
```
R2# show ip ospf neighbor
! → neighbor nhấp nháy, LSDB bất thường
R2# show ip ospf database router
! → LSA type 1 của 4.4.4.4 có Seq# tăng RẤT NHANH (2 router cùng ghi đè)
```

**Sửa:**
```
R3(config)# router ospf 1
R3(config-router)# router-id 3.3.3.3
R3# clear ip ospf process
```

> ⭐ **Dấu hiệu nhận diện duplicate Router ID:** `Seq#` của một LSA type 1 **tăng liên tục rất nhanh**
> (2 router tranh nhau ghi đè cùng 1 LSA).

#### Lỗi 5 — `passive-interface` sai chỗ

```
R2(config)# router ospf 1
R2(config-router)# passive-interface GigabitEthernet0/0
```
```
R2# show ip ospf neighbor
! → mất neighbor 1.1.1.1
R2# show ip protocols | include Passive
    Passive Interface(s):
      GigabitEthernet0/0
      Loopback0
```
⭐ Nhưng chú ý: `show ip route` trên R2 **vẫn có** subnet `10.1.12.0/30` (connected)
và R2 **vẫn quảng bá** nó — `passive-interface` chỉ **không gửi Hello**.

**Sửa:**
```
R2(config-router)# no passive-interface GigabitEthernet0/0
```

#### Lỗi 6 — `reference-bandwidth` lệch

```
R1(config)# router ospf 1
R1(config-router)# auto-cost reference-bandwidth 100        ! chỉ R1 đổi
```
```
R1# show ip ospf interface brief
Interface    PID   Area   IP Address/Mask     Cost  State Nbrs F/C
Gi0/0        1     1      10.1.12.1/30        1     P2P   1/1     ← cost 1
Lo1          1     1      172.16.1.1/24       1     LOOP  0/0

R2# show ip ospf interface brief
Interface    PID   Area   IP Address/Mask     Cost  State Nbrs F/C
Gi0/0        1     1      10.1.12.2/30        100   P2P   1/1     ← cost 100
```
⭐ **Cùng một link mà 2 router tính cost khác nhau (1 vs 100).**

Neighbor **vẫn lên Full** (cost không phải điều kiện adjacency) — nhưng
**đường đi được chọn có thể sai**, và trong topology phức tạp có thể gây **routing loop**.

```
R1# show ip route ospf | include 172.16.3.0
! metric khác so với trước
```

**Sửa:**
```
R1(config-router)# auto-cost reference-bandwidth 100000
```

> ⭐ **Bài học:** đây là loại lỗi **không làm mất neighbor** nên rất khó phát hiện —
> nó chỉ làm traffic đi đường sai. **Luôn verify `show ip ospf | include Reference bandwidth`
> trên mọi router** khi nhận bàn giao một mạng OSPF.

✅ **Checkpoint bước 6:** tái hiện và sửa được **cả 6 lỗi**, và với mỗi lỗi bạn nói được:
**(a) triệu chứng · (b) lệnh chẩn đoán · (c) cách sửa**.

---
