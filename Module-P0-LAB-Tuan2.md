# LAB P0 — Tuần 2: Routing (Static · OSPF · NAT · ACL)

> 📘 **Lý thuyết:** [Module-P0](Module-P0-Nen-tang-Ready-for-ENCOR.md) —
> đọc **Phần 2 mục §3.5, §3.6, §3.7, §3.8** trước khi làm.
>
> ⏱️ **Thời gian:** ~5 giờ · 💾 **RAM:** 3 GB · 🧰 **Cần:** EVE-NG + 4× vIOS

---

## Ba lab này trả lời 5 câu hỏi

| # | Câu hỏi | LAB |
|:---:|---|:---:|
| 1 | Router chọn đường theo thứ tự nào khi có nhiều lựa chọn? | P0-4 |
| 2 | "Floating static" là gì, và nó dự phòng bằng cách nào? | P0-4 |
| 3 | OSPF tự tìm đường ra sao? Neighbor lên qua mấy bước? | P0-5 |
| 4 | Nhiều máy dùng chung một IP public bằng cách nào? | P0-6 |
| 5 | ACL chặn gói ở đâu, và vì sao đặt sai chỗ là hỏng? | P0-6 |

> Đây là **nền của Module-03 (routing) và Module-04 (OSPF)** — hai module nặng nhất
> của khối Infrastructure. Làm chắc ở đây, bạn tiết kiệm được cả tuần về sau.

---

## ⚠️ Đọc trước khi bắt đầu

| Điều cần biết | Chi tiết |
|---|---|
| **Làm xong LAB Tuần 1 chưa?** | Không bắt buộc dùng lại topology, nhưng nên nắm VLAN/trunk trước |
| **Giữ lại topology LAB P0-5** | Module-01 có thể dùng lại — nhưng cũng có config riêng nếu bạn đã xóa |
| **Số liệu của bạn sẽ khác** | Metric, thời gian, số entry sẽ khác output mẫu. Đối chiếu **cấu trúc**, đừng so từng số |
| **Lỗi là chuyện bình thường** | Mất > 15 phút vì một lỗi → ghi vào [`SO-TAY-LOI.md`](SO-TAY-LOI.md) |

---



# LAB P0-4 — Static route + Floating static

#### Topology

```
              10.0.12.0/30
      R1 ─────────────────── R2
       │  Gi0/0        Gi0/0  │
       │                      │
Gi0/1  │  10.0.13.0/30        │ Gi0/1
       └────── R3 ────────────┘
            10.0.23.0/30

Loopback: R1=1.1.1.1/32 · R2=2.2.2.2/32 · R3=3.3.3.3/32
```

| Link | Đầu A | Đầu B |
|---|---|---|
| R1 Gi0/0 (10.0.12.1/30) | | R2 Gi0/0 (10.0.12.2/30) |
| R1 Gi0/1 (10.0.13.1/30) | | R3 Gi0/0 (10.0.13.2/30) |
| R2 Gi0/1 (10.0.23.1/30) | | R3 Gi0/1 (10.0.23.2/30) |

**RAM: 3× 512 MB = 1.5 GB** ✅

#### Cấu hình R1

```
enable
configure terminal
hostname R1
no ip domain lookup
!
interface Loopback0
 ip address 1.1.1.1 255.255.255.255
!
interface GigabitEthernet0/0
 description ---> To R2
 ip address 10.0.12.1 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/1
 description ---> To R3
 ip address 10.0.13.1 255.255.255.252
 no shutdown
!
! === Đường CHÍNH tới 2.2.2.2: đi trực tiếp qua R2 (AD mặc định = 1) ===
ip route 2.2.2.2 255.255.255.255 10.0.12.2
!
! === Đường DỰ PHÒNG: đi vòng qua R3, AD = 200 (floating static) ===
ip route 2.2.2.2 255.255.255.255 10.0.13.2 200
!
line con 0
 exec-timeout 0 0
 logging synchronous
end
write memory
```

#### Cấu hình R2

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
 description ---> To R1
 ip address 10.0.12.2 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/1
 description ---> To R3
 ip address 10.0.23.1 255.255.255.252
 no shutdown
!
ip route 1.1.1.1 255.255.255.255 10.0.12.1
ip route 1.1.1.1 255.255.255.255 10.0.23.2 200
!
line con 0
 exec-timeout 0 0
 logging synchronous
end
write memory
```

#### Cấu hình R3 (router trung chuyển)

```
enable
configure terminal
hostname R3
no ip domain lookup
!
interface Loopback0
 ip address 3.3.3.3 255.255.255.255
!
interface GigabitEthernet0/0
 description ---> To R1
 ip address 10.0.13.2 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/1
 description ---> To R2
 ip address 10.0.23.2 255.255.255.252
 no shutdown
!
ip route 1.1.1.1 255.255.255.255 10.0.13.1
ip route 2.2.2.2 255.255.255.255 10.0.23.1
!
line con 0
 exec-timeout 0 0
 logging synchronous
end
write memory
```

#### Kiểm tra & bài học chính

**a) Đường nào đang được dùng?**
```
R1# show ip route 2.2.2.2
```
**Output mẫu:**
```
Routing entry for 2.2.2.2/32
  Known via "static", distance 1, metric 0
  Routing Descriptor Blocks:
  * 10.0.12.2
      Route metric is 0, traffic share count is 1
```
✅ `distance 1` → đang dùng đường **chính** qua R2. Route AD 200 **không xuất hiện** trong bảng.

**b) Xác nhận bằng traceroute:**
```
R1# traceroute 2.2.2.2 source 1.1.1.1
```
**Output mẫu:**
```
  1 10.0.12.2 2 msec 1 msec 1 msec    ← đi trực tiếp qua R2, 1 hop
```

**c) ⭐ Test failover — đây là mục tiêu của lab:**

```
R1(config)# interface GigabitEthernet0/0
R1(config-if)# shutdown
```

Chờ vài giây rồi:
```
R1# show ip route 2.2.2.2
```
**Output mẫu:**
```
Routing entry for 2.2.2.2/32
  Known via "static", distance 200, metric 0
  Routing Descriptor Blocks:
  * 10.0.13.2
```
✅ **Route AD 200 đã "nổi lên"** thay thế. Đây chính là ý nghĩa của từ *floating*.

```
R1# traceroute 2.2.2.2 source 1.1.1.1
```
**Output mẫu:**
```
  1 10.0.13.2 2 msec 1 msec 1 msec    ← qua R3
  2 10.0.23.1 3 msec 2 msec 2 msec    ← rồi tới R2
```

**d) Bật lại link chính:**
```
R1(config-if)# no shutdown
```
→ `show ip route 2.2.2.2` phải quay về `distance 1`.

✅ **Checkpoint LAB P0-4:**

| Kiểm tra | Mong đợi |
|---|---|
| Bình thường: `show ip route 2.2.2.2` | `distance 1`, next-hop 10.0.12.2 |
| Bình thường: traceroute | 1 hop |
| Sau khi shut Gi0/0: `show ip route 2.2.2.2` | `distance 200`, next-hop 10.0.13.2 |
| Sau khi shut: traceroute | 2 hop, qua R3 |
| Sau `no shut`: | Quay về distance 1 |

#### 🧪 Thử nghiệm

| Thử nghiệm | Gõ gì | Quan sát | Bài học |
|---|---|---|---|
| Đặt 2 static cùng AD | `ip route 2.2.2.2 255.255.255.255 10.0.13.2` (bỏ số 200) | `show ip route 2.2.2.2` có **cả 2** next-hop | Cùng AD + cùng metric = **ECMP load-balance** |
| Longest prefix thắng AD | Thêm `ip route 2.2.2.0 255.255.255.0 10.0.13.2` | `show ip route 2.2.2.2` vẫn dùng `/32` | `/32` cụ thể hơn `/24` → thắng bất kể AD |
| Route tới đích không tồn tại | `ip route 9.9.9.9 255.255.255.255 10.0.12.2` | Route vẫn cài vào bảng, nhưng ping fail | Static route **không kiểm tra** đích có thật hay không |
| Next-hop không reachable | `ip route 8.8.8.8 255.255.255.255 172.16.99.99` | Route **không** vào bảng route | Static cần next-hop reachable — gọi là *recursive lookup* |

---

# LAB P0-5 — OSPF single-area

**Mục tiêu:** thay toàn bộ static route bằng OSPF, thấy được sự khác biệt.

#### Topology — giống LAB P0-4

Dùng lại lab cũ. **Trước tiên xóa hết static route:**

```
! Trên cả R1, R2, R3
configure terminal
no ip route 1.1.1.1 255.255.255.255 10.0.12.1
no ip route 1.1.1.1 255.255.255.255 10.0.23.2 200
no ip route 2.2.2.2 255.255.255.255 10.0.12.2
no ip route 2.2.2.2 255.255.255.255 10.0.13.2 200
no ip route 2.2.2.2 255.255.255.255 10.0.23.1
no ip route 1.1.1.1 255.255.255.255 10.0.13.1
end
```
Xác nhận sạch: `show ip route static` → không còn gì.

#### Cấu hình OSPF — R1

```
configure terminal
!
router ospf 1
 router-id 1.1.1.1
 auto-cost reference-bandwidth 10000        ! tránh mọi link Gi đều cost 1
 network 1.1.1.1 0.0.0.0 area 0             ! quảng bá loopback
 network 10.0.12.0 0.0.0.3 area 0
 network 10.0.13.0 0.0.0.3 area 0
!
end
write memory
```

#### R2

```
configure terminal
router ospf 1
 router-id 2.2.2.2
 auto-cost reference-bandwidth 10000
 network 2.2.2.2 0.0.0.0 area 0
 network 10.0.12.0 0.0.0.3 area 0
 network 10.0.23.0 0.0.0.3 area 0
end
write memory
```

#### R3

```
configure terminal
router ospf 1
 router-id 3.3.3.3
 auto-cost reference-bandwidth 10000
 network 3.3.3.3 0.0.0.0 area 0
 network 10.0.13.0 0.0.0.3 area 0
 network 10.0.23.0 0.0.0.3 area 0
end
write memory
```

> 💡 `network 1.1.1.1 0.0.0.0 area 0` — wildcard `0.0.0.0` nghĩa là "đúng chính xác IP này".
> Đây là cách chuẩn để quảng bá 1 loopback `/32`.

#### Kiểm tra — theo đúng thứ tự này

**a) Neighbor đã lên Full chưa? (lệnh đầu tiên luôn phải chạy)**
```
R1# show ip ospf neighbor
```
**Output mẫu:**
```
Neighbor ID     Pri   State           Dead Time   Address         Interface
2.2.2.2           1   FULL/BDR        00:00:35    10.0.12.2       GigabitEthernet0/0
3.3.3.3           1   FULL/BDR        00:00:33    10.0.13.2       GigabitEthernet0/1
```
✅ **Checkpoint:** cả 2 neighbor ở `FULL`. `Dead Time` đếm ngược từ 40s và **reset liên tục**.

**Cách đọc `FULL/BDR`:** state là `FULL`, và **neighbor đó** đang giữ vai trò BDR trên segment.
Trên link P2P giữa 2 router bạn có thể thấy `FULL/DROTHER` hoặc `FULL/  -` — đều bình thường.

**b) Bảng route đã học được gì?**
```
R1# show ip route ospf
```
**Output mẫu:**
```
      2.0.0.0/32 is subnetted, 1 subnets
O        2.2.2.2 [110/2] via 10.0.12.2, 00:02:14, GigabitEthernet0/0
      3.0.0.0/32 is subnetted, 1 subnets
O        3.3.3.3 [110/2] via 10.0.13.2, 00:02:14, GigabitEthernet0/1
      10.0.0.0/8 is variably subnetted, 6 subnets, 2 masks
O        10.0.23.0/30 [110/11] via 10.0.13.2, 00:02:14, GigabitEthernet0/1
                              [110/11] via 10.0.12.2, 00:02:14, GigabitEthernet0/0
```
✅ **Checkpoint:**
- `[110/x]` → AD 110 = OSPF ✅
- `10.0.23.0/30` có **2 next-hop** → cost bằng nhau → **ECMP load-balance** ⭐

**c) Interface nào đang chạy OSPF:**
```
R1# show ip ospf interface brief
```
**Output mẫu:**
```
Interface    PID   Area   IP Address/Mask    Cost  State Nbrs F/C
Lo0          1     0      1.1.1.1/32         1     LOOP  0/0
Gi0/0        1     0      10.0.12.1/30       10    BDR   1/1
Gi0/1        1     0      10.0.13.1/30       10    BDR   1/1
```
✅ Cost = **10** (không phải 1) → `auto-cost reference-bandwidth 10000` đã có tác dụng
(10000 Mbps / 1000 Mbps = 10).

**d) Xem LSDB — bản đồ mạng:**
```
R1# show ip ospf database
```
Bạn sẽ thấy `Router Link States (Area 0)` với 3 dòng — mỗi router 1 LSA type 1.
**Module-04 sẽ đào rất sâu vào đây.** Giờ chỉ cần biết: LSDB là bản đồ, và 3 router phải có
bản đồ **giống nhau**.

**e) Ping full mesh:**
```
R1# ping 2.2.2.2 source 1.1.1.1
R1# ping 3.3.3.3 source 1.1.1.1
```
✅ Cả hai 100%.

#### ⚠️ Nếu neighbor không lên Full — checklist theo thứ tự

| # | Triệu chứng | Kiểm tra | Nguyên nhân |
|:---:|---|---|---|
| 1 | Không thấy neighbor nào | `show ip ospf interface brief` | Interface không nằm trong OSPF → sai wildcard trong `network` |
| 2 | Không thấy neighbor nào | `show ip protocols \| inc Passive` | Interface bị `passive-interface` |
| 3 | Kẹt ở **INIT** | Ping 2 chiều được không? | Hello đi 1 chiều — ACL chặn, hoặc lỗi L2 |
| 4 | Kẹt ở **EXSTART/EXCHANGE** | `show int Gi0/0 \| inc MTU` cả 2 đầu | ⭐ **MTU lệch** — lỗi kinh điển nhất |
| 5 | Neighbor **flapping** liên tục | `show ip ospf int Gi0/0 \| inc Timer` | Hello/Dead timer lệch |
| 6 | Neighbor lên rồi tụt | `show ip ospf \| inc ID` cả 2 router | **Router-ID trùng nhau** |
| 7 | Neighbor Full nhưng không có route | `show ip ospf database` | Area lệch, hoặc network chưa được quảng bá |

**Lệnh debug khi bí:**
```
R1# debug ip ospf adj
! ... xem log ...
R1# undebug all              ! ⚠️ ĐỪNG QUÊN
```

#### 🧪 Thử nghiệm — so sánh với static route

| Thử nghiệm | Gõ gì | Quan sát | Bài học |
|---|---|---|---|
| ⭐ **Failover tự động** | R1: `int Gi0/0` → `shutdown` | Sau ~40s, route 2.2.2.2 chuyển sang qua R3 **tự động, không cần cấu hình gì** | Đây là điểm hơn hẳn static route: OSPF tự phát hiện và tự tính lại |
| Đo thời gian hội tụ | Ping liên tục rồi shutdown | Mất ~40 gói (dead interval) | Vì sao production tune timer hoặc dùng BFD |
| Tune timer cho nhanh | `int Gi0/1` → `ip ospf hello-interval 1` + `ip ospf dead-interval 4` (cả 2 đầu) | Hội tụ còn ~4s | ⚠️ Phải đặt **cả 2 đầu**, nếu 1 đầu → neighbor xuống |
| Đổi cost đổi đường | R1: `int Gi0/0` → `ip ospf cost 500` | Route 2.2.2.2 chuyển đi qua R3 | Cost điều khiển đường đi |
| Lệch MTU (tái hiện lỗi #4) | R1: `int Gi0/0` → `mtu 1400` | Neighbor kẹt **EXSTART** | ⭐ Tự tay tạo ra lỗi kinh điển để nhớ mãi |
| Trùng Router-ID | R2: `router ospf 1` → `router-id 1.1.1.1` → `clear ip ospf process` | Log báo duplicate router-id | Router-ID phải unique |
| Bắt gói OSPF Hello | Capture link R1↔R2, filter `ospf` | Thấy Hello mỗi 10s tới 224.0.0.5, có Router-ID, Area, timer | ⭐ Nhìn thấy điều kiện "phải khớp" bằng mắt |

---

# LAB P0-6 — NAT + ACL

**Mục tiêu:** cho mạng nội bộ ra "Internet" qua PAT, và dùng ACL lọc truy cập.

#### Topology

```
                            NAT boundary
                                 │
 [PC1 10.10.10.11]              │
        │                        │
       SW1 ── R1 ──────────────  R-ISP ── [SRV 8.8.8.8]
              │  203.0.113.1/30 │ .2
         (gateway               │
          10.10.10.1)      "Internet"
```

| Thiết bị | Vai | Interface | IP |
|---|---|---|---|
| R1 | Router biên (NAT) | Gi0/0 (outside) | 203.0.113.1/30 |
| | | Gi0/1 (inside) | 10.10.10.1/24 |
| R-ISP | Giả lập Internet | Gi0/0 | 203.0.113.2/30 |
| | | Loopback0 | 8.8.8.8/32 (giả làm server ngoài) |
| PC1 | Máy nội bộ | e0 | 10.10.10.11/24, GW 10.10.10.1 |

**RAM: 2× vIOS (1 GB) + 1× vIOS-L2 (768 MB) + VPCS ≈ 1.8 GB** ✅

#### Cấu hình R1 (router biên)

```
enable
configure terminal
hostname R1
no ip domain lookup
!
interface GigabitEthernet0/0
 description ---> OUTSIDE to ISP
 ip address 203.0.113.1 255.255.255.252
 ip nat outside
 no shutdown
!
interface GigabitEthernet0/1
 description ---> INSIDE to LAN
 ip address 10.10.10.1 255.255.255.0
 ip nat inside
 no shutdown
!
! === Default route ra Internet — BẮT BUỘC, thiếu là NAT vô nghĩa ===
ip route 0.0.0.0 0.0.0.0 203.0.113.2
!
! === ACL định nghĩa mạng nào được NAT ===
ip access-list standard ACL-NAT
 permit 10.10.10.0 0.0.0.255
!
! === Bật PAT (overload) ===
ip nat inside source list ACL-NAT interface GigabitEthernet0/0 overload
!
line con 0
 exec-timeout 0 0
 logging synchronous
end
write memory
```

#### Cấu hình R-ISP (giả lập Internet)

```
enable
configure terminal
hostname R-ISP
no ip domain lookup
!
interface Loopback0
 description ---> Gia lam server tren Internet
 ip address 8.8.8.8 255.255.255.255
!
interface GigabitEthernet0/0
 ip address 203.0.113.2 255.255.255.252
 no shutdown
!
! ⚠️ CỐ Ý KHÔNG có route về 10.10.10.0/24
!    Đây là điểm quan trọng: ISP không biết mạng private của bạn.
!    Nếu NAT hoạt động đúng thì vẫn ping được — đó là chứng minh NAT thật sự chạy.
!
line con 0
 exec-timeout 0 0
 logging synchronous
end
write memory
```

#### Kiểm tra NAT

**a) Từ PC1 ping ra "Internet":**
```
PC1> ping 8.8.8.8
```
✅ **Phải được.** Nếu được → NAT đang hoạt động (vì R-ISP không có route về 10.10.10.0/24).

**b) Xem bảng NAT — bằng chứng trực tiếp:**
```
R1# show ip nat translations
```
**Output mẫu:**
```
Pro Inside global         Inside local          Outside local         Outside global
icmp 203.0.113.1:1        10.10.10.11:1         8.8.8.8:1             8.8.8.8:1
```

**Đọc bảng này:**

| Cột | Giá trị | Nghĩa |
|---|---|---|
| Inside local | `10.10.10.11:1` | IP **thật** của PC1 |
| Inside global | `203.0.113.1:1` | IP PC1 **hóa trang thành** — chính là IP interface outside |
| Outside global | `8.8.8.8:1` | Đích |

⭐ **Đây là toàn bộ bản chất của PAT:** nhiều IP nội bộ dùng chung 1 IP public,
phân biệt nhau bằng **port number**.

**c) Thống kê:**
```
R1# show ip nat statistics
```
**Output mẫu:**
```
Total active translations: 1 (0 static, 1 dynamic; 1 extended)
Outside interfaces:
  GigabitEthernet0/0
Inside interfaces:
  GigabitEthernet0/1
Hits: 15  Misses: 0
```
✅ `Hits` tăng khi có traffic. `Misses` cao là dấu hiệu có vấn đề.

**d) Chứng minh bằng phản chứng — quan trọng:**
```
R-ISP# ping 10.10.10.11
```
❌ **Phải FAIL.** Vì R-ISP không có route về mạng private. Điều này chứng minh:
traffic từ PC1 ra được **là nhờ NAT**, không phải nhờ routing.

#### Thêm ACL — lọc truy cập

**Yêu cầu:** PC1 chỉ được ping và truy cập web ra ngoài, chặn mọi thứ khác.

```
R1(config)# ip access-list extended ACL-LAN-OUT
R1(config-ext-nacl)#  permit icmp 10.10.10.0 0.0.0.255 any
R1(config-ext-nacl)#  permit tcp  10.10.10.0 0.0.0.255 any eq 80
R1(config-ext-nacl)#  permit tcp  10.10.10.0 0.0.0.255 any eq 443
R1(config-ext-nacl)#  permit udp  10.10.10.0 0.0.0.255 any eq 53
R1(config-ext-nacl)#  deny   ip   any any log
R1(config-ext-nacl)# exit
R1(config)# interface GigabitEthernet0/1
R1(config-if)#  ip access-group ACL-LAN-OUT in
```

> 💡 **Vì sao apply `in` trên Gi0/1 (inside):** ACL extended nên đặt **gần source** để chặn sớm.
> Traffic từ PC1 **đi vào** router qua Gi0/1 → dùng chiều `in`.

**Kiểm tra:**
```
R1# show access-lists ACL-LAN-OUT
```
**Output mẫu:**
```
Extended IP access list ACL-LAN-OUT
    10 permit icmp 10.10.10.0 0.0.0.255 any (12 matches)
    20 permit tcp 10.10.10.0 0.0.0.255 any eq www
    30 permit tcp 10.10.10.0 0.0.0.255 any eq 443
    40 permit udp 10.10.10.0 0.0.0.255 any eq domain
    50 deny ip any any log (3 matches)
```
✅ **Checkpoint:** counter `(12 matches)` ở dòng permit icmp tăng khi bạn ping.
Dòng `deny ... log` có match → có traffic bị chặn (xem `show logging`).

✅ **Checkpoint LAB P0-6:**

| Kiểm tra | Mong đợi |
|---|---|
| PC1 ping 8.8.8.8 | ✅ Được |
| `show ip nat translations` | Có entry với Inside local = 10.10.10.11 |
| R-ISP ping 10.10.10.11 | ❌ Fail (đúng — chứng minh NAT hoạt động) |
| `show access-lists` | Counter dòng permit icmp tăng |
| Sau ACL: PC1 ping vẫn được | ✅ (icmp được permit) |
| `show logging \| include list` | Có log của traffic bị deny |

#### 🧪 Thử nghiệm

| Thử nghiệm | Gõ gì | Quan sát | Bài học |
|---|---|---|---|
| Xóa default route | R1: `no ip route 0.0.0.0 0.0.0.0 203.0.113.2` | PC1 ping fail | ⭐ **Routing xảy ra TRƯỚC NAT.** Không có route thì NAT vô nghĩa |
| Đặt sai chiều inside/outside | Đổi Gi0/0 thành `ip nat inside` | NAT không hoạt động | Chiều inside/outside sai là hỏng hoàn toàn |
| Xem NAT hoạt động | `debug ip nat` rồi ping từ PC1 | Log từng gói được dịch | Nhớ `undebug all` |
| ACL chặn ICMP | Xóa dòng `permit icmp` | PC1 ping fail ngay | Implicit `deny any` ở cuối ACL |
| Thứ tự ACL sai | Đưa `deny ip any any` lên **dòng 5** | Chặn hết mọi thứ | ⭐ ACL xử lý từ trên xuống, khớp là dừng |
| Bắt gói 2 bên NAT | Capture Gi0/1 (inside) và Gi0/0 (outside) cùng lúc | Inside: src = 10.10.10.11 · Outside: src = 203.0.113.1 | ⭐ Nhìn thấy NAT đổi IP bằng mắt |

