# LAB 05A — Tuần 9: eBGP 3 AS

> 📘 **Lý thuyết:** [Module-05A](Module-05A-BGP-Nen-tang-va-eBGP-Peering.md) —
> đọc **Phần 1** và **Phần 2 mục §3.3 (eBGP vs iBGP), §3.4 (ba bảng), §3.5 (sáu trạng thái)** trước khi làm.
>
> ⏱️ **Thời gian:** ~7 giờ · 💾 **RAM:** 4 GB · 🧰 **Cần:** EVE-NG + 4–5× vIOS

---

## Lab này trả lời 6 câu hỏi

| # | Câu hỏi | Bước |
|:---:|---|:---:|
| 1 | Hai router khác AS bắt tay BGP qua mấy trạng thái? Kẹt ở đâu = lỗi gì? | 1 |
| 2 | BGP table chứa gì mà routing table không có? Dấu `*` và `>` nghĩa là gì? | 2 |
| 3 | Vì sao route vào được BGP table nhưng **không** vào được routing table? | 3 |
| 4 | AS-path chống loop bằng cách nào — chứng minh bằng thực nghiệm | 4 |
| 5 | Tám lỗi BGP kinh điển — triệu chứng và cách tìm ra | 5 |
| 6 | `soft reset` khác `hard reset` chỗ nào, vì sao quan trọng? | 6 |

> **Bước 2 (đọc BGP table) là phần quan trọng nhất module.** BGP có **ba bảng** chứ không phải
> một — và hiểu được bảng giữa là hiểu được toàn bộ BGP. Module-05B (13 bước path selection)
> xây thẳng lên đó.

---

## ⚠️ Đọc trước khi bắt đầu

| Điều cần biết | Chi tiết |
|---|---|
| **BGP rất chậm** | Timer mặc định: keepalive 60s, hold 180s. Sau thay đổi phải **chờ tới 60 giây**. Đừng vội kết luận hỏng |
| **`Active` KHÔNG phải trạng thái tốt** | Nghe như "đang hoạt động" nhưng thực ra là **đang thử kết nối mà chưa được**. Xem §3.5 |
| **Số liệu của bạn sẽ khác** | Router ID, uptime, số prefix sẽ khác output mẫu |
| **Bước 5 là cố ý phá** | Tám lỗi được gieo có chủ đích. Làm xong **nhớ sửa lại** trước khi sang Module-05B |
| **Giữ topology này** | Module-05B dùng lại đúng topology 3 AS này |
| **Lỗi > 15 phút** | Ghi vào [`SO-TAY-LOI.md`](SO-TAY-LOI.md) |

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
show ip bgp <prefix>                             ! chi tiết 1 prefix + lý do best
show ip bgp summary                              ! neighbor
show ip bgp neighbors <ip> routes                ! route nhận từ peer đó (sau policy)
show ip bgp neighbors <ip> advertised-routes     ! route gửi cho peer đó
show ip bgp regexp _65003_                       ! route đi qua AS 65003
show ip bgp regexp ^65002_                       ! route từ AS kề 65002
show ip bgp regexp ^$                            ! route sinh trong AS của mình
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
    10 deny tcp any any eq bgp (12 matches)         ← counter tăng!
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
% Subnet not in table                                ← RIB không có /16
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

! Cách 2: tạo static route Null0 để "có hàng trong kho"
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
  Local host: 10.0.12.1, Local port: 0            ← source SAI
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
! SOFT (dùng route-refresh, KHÔNG đóng phiên TCP)
clear ip bgp 10.0.12.2 soft in            ! xin peer gửi lại route (sau khi đổi inbound policy)
clear ip bgp 10.0.12.2 soft out           ! gửi lại route cho peer (sau khi đổi outbound policy)
clear ip bgp * soft

! HARD (đóng phiên TCP — GÂY DOWNTIME)
clear ip bgp 10.0.12.2
clear ip bgp *                            ! reset MỌI phiên — không bao giờ trên production
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
R1# show ip bgp neighbors 10.0.12.2 received-routes      ! Adj-RIB-In thật
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
