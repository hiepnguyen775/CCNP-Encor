# LAB 01 — Nhìn thấy CEF hoạt động

> 📘 **Lý thuyết:** [Module-01](Module-01-Packet-Forwarding-va-Kien-truc-Thiet-bi.md) —
> đọc trọn **Phần 1 (Cái đó là gì)** và **Phần 2 mục §3.1–3.3** trước khi làm lab này.
> Chưa đọc mà lab thì bạn chỉ gõ lệnh chứ không hiểu mình đang nhìn cái gì.
>
> ⏱️ **Thời gian:** 3–4 giờ · 💾 **RAM:** 1.5 GB · 🧰 **Cần:** EVE-NG + 3× vIOS

---

## Lab này trả lời 5 câu hỏi

| # | Câu hỏi | Bước |
|:---:|---|:---:|
| 1 | Bảng route (RIB) và bảng CEF (FIB) khác nhau chỗ nào? | Bước 2 |
| 2 | Vì sao ping lần đầu hay mất đúng 1 gói (`.!!!!`)? | Bước 4 |
| 3 | Vì sao `debug ip packet` không thấy traffic của người dùng? | Bước 5 |
| 4 | Khi có 2 đường bằng nhau, router chọn đường nào cho flow của tôi? | Bước 6 |
| 5 | CPU cao thì làm sao biết lỗi ở data plane hay control plane? | Bước 7 |

> Làm hết 7 bước bạn sẽ **nhìn thấy tận mắt** cả 5 câu trả lời, thay vì học thuộc.

---

## Chuẩn bị

### Sơ đồ

```
                        10.0.12.0/30
          ┌──────────────────────────────────┐
          │ Gi0/0                      Gi0/0 │
     ┌────┴────┐                        ┌────┴────┐
     │   R1    │                        │   R2    │
     │ 1.1.1.1 │                        │ 2.2.2.2 │
     └────┬────┘                        └────┬────┘
          │ Gi0/1                      Gi0/1 │
          │                                  │
          │ 10.0.13.0/30      10.0.23.0/30   │
          │          ┌────────────┐          │
          └──────────┤     R3     ├──────────┘
              Gi0/0  │  3.3.3.3   │  Gi0/1
                     └────────────┘

  Định tuyến: CHỈ DÙNG STATIC ROUTE — cố ý không dùng OSPF
```

> **Vì sao lab này dùng static chứ không phải OSPF?**
> Module-01 nói về **cách gói được chuyển đi**, không phải về giao thức định tuyến.
> Static route cho đủ mọi thứ lab cần (route để so RIB/FIB, ECMP, traffic transit)
> mà **không thêm một thứ có thể hỏng**. Nếu OSPF neighbor không lên, bạn sẽ mất
> hàng giờ debug OSPF và không học được gì về CEF.
>
> *(Nếu bạn vẫn còn LAB P0-5 chạy OSPF thì dùng lại cũng được — kết quả tương đương,
> chỉ khác ký hiệu `O` thay vì `S` trong bảng route.)*

| Node | Image | RAM | Interface |
|---|---|:---:|---|
| **R1** | vIOS | 512 MB | Gi0/0 → R2 · Gi0/1 → R3 · Lo0 = 1.1.1.1/32 |
| **R2** | vIOS | 512 MB | Gi0/0 → R1 · Gi0/1 → R3 · Lo0 = 2.2.2.2/32 |
| **R3** | vIOS | 512 MB | Gi0/0 → R1 · Gi0/1 → R2 · Lo0 = 3.3.3.3/32 |

**Tổng: 1.5 GB** ✅

### Bảng nối dây trong EVE-NG

| Từ | Cổng | Tới | Cổng | Mạng |
|---|---|---|---|---|
| R1 | Gi0/0 | R2 | Gi0/0 | 10.0.12.0/30 |
| R1 | Gi0/1 | R3 | Gi0/0 | 10.0.13.0/30 |
| R2 | Gi0/1 | R3 | Gi0/1 | 10.0.23.0/30 |

### Config — dán nguyên khối vào từng router

<details>
<summary><b>📋 R1 — bấm để mở</b></summary>

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
 description ---> R2
 ip address 10.0.12.1 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/1
 description ---> R3
 ip address 10.0.13.1 255.255.255.252
 no shutdown
!
ip route 2.2.2.2 255.255.255.255 10.0.12.2
ip route 3.3.3.3 255.255.255.255 10.0.13.2
!
! Hai dong sau CO Y tro cung mot dich qua hai next-hop khac nhau
!   -> tao ra ECMP de dung o Buoc 6
ip route 10.0.23.0 255.255.255.252 10.0.12.2
ip route 10.0.23.0 255.255.255.252 10.0.13.2
!
line con 0
 exec-timeout 0 0
 logging synchronous
!
end
write memory
```
</details>

<details>
<summary><b>📋 R2 — bấm để mở</b></summary>

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
 description ---> R1
 ip address 10.0.12.2 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/1
 description ---> R3
 ip address 10.0.23.1 255.255.255.252
 no shutdown
!
ip route 1.1.1.1 255.255.255.255 10.0.12.1
ip route 10.0.13.0 255.255.255.252 10.0.12.1
!
! CO Y di vong qua R1 (thay vi qua link truc tiep R2-R3)
!   -> tao traffic TRANSIT qua R1 de dung o Buoc 5
ip route 3.3.3.3 255.255.255.255 10.0.12.1
!
line con 0
 exec-timeout 0 0
 logging synchronous
!
end
write memory
```
</details>

<details>
<summary><b>📋 R3 — bấm để mở</b></summary>

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
 description ---> R1
 ip address 10.0.13.2 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/1
 description ---> R2
 ip address 10.0.23.2 255.255.255.252
 no shutdown
!
ip route 1.1.1.1 255.255.255.255 10.0.13.1
ip route 10.0.12.0 255.255.255.252 10.0.13.1
!
! CO Y di vong qua R1 — chieu ve cua traffic transit o Buoc 5
ip route 2.2.2.2 255.255.255.255 10.0.13.1
!
line con 0
 exec-timeout 0 0
 logging synchronous
!
end
write memory
```
</details>

### ✅ Kiểm tra trước khi bắt đầu

**① Ba loopback phải ping được từ R1:**
```
R1# ping 2.2.2.2 source 1.1.1.1
R1# ping 3.3.3.3 source 1.1.1.1
```
Cả hai phải `!!!!!`. Chưa được thì dừng lại sửa, đừng làm tiếp.

**② Phải có ECMP (hai đường tới `10.0.23.0/30`) — cần cho Bước 6:**
```
R1# show ip route 10.0.23.0
```
Phải thấy **hai dòng `via`**:
```
  Routing entry for 10.0.23.0/30
    Known via "static", distance 1, metric 0
    Routing Descriptor Blocks:
    * 10.0.13.2
        ...
      10.0.12.2
        ...
```

**③ Traffic R2 → R3 phải đi VÒNG QUA R1 — cần cho Bước 5:**
```
R2# show ip route 3.3.3.3
```
Phải thấy `via 10.0.12.1` (tức là qua R1), **không phải** `via 10.0.23.2`.

> ⚠️ **Lưu ý về con số trong output mẫu:** số entry, địa chỉ MAC, thời gian của bạn sẽ **khác**
> với output mẫu dưới đây tùy image và thời điểm. Hãy đối chiếu **cấu trúc và từ khóa**
> (`receive`, `attached`, `drop`, `Encap length`…), đừng so từng con số.

---

# Bước 1 — CEF có đang bật không?

**🎯 Mục tiêu:** xác nhận điểm xuất phát trước khi so sánh.

**Gõ:**
```
R1# show ip cef summary
```

**Sẽ thấy:**
```
IPv4 CEF is enabled for distributed and running
VRF Default:
 10 prefixes (10/0 fwd/non-fwd)
 Table id 0x0
 Database epoch: 0 (10 entries at this epoch)
```

**Gõ tiếp:**
```
R1# show ip interface GigabitEthernet0/0 | include CEF|switching
```

**Sẽ thấy:**
```
  IP CEF switching is enabled
  IP CEF switching turbo vector
  IP Null turbo vector
```

**💡 Vì sao quan trọng:** CEF bật ở **hai mức** — toàn cục và từng interface. Cả hai đều phải bật
thì gói mới đi hardware. Ở bước 5 bạn sẽ tắt nó đi để thấy khác biệt.

✅ **Checkpoint 1:** thấy dòng `IPv4 CEF is enabled` và `IP CEF switching is enabled`.

---

# Bước 2 — RIB và FIB khác nhau ở đâu

> Đây là **bài học chính** của module. Đừng lướt qua bước này.

**🎯 Mục tiêu:** nhìn thấy tận mắt rằng FIB **không phải bản sao** của RIB.

### a) RIB — bảng "của người đọc"

```
R1# show ip route
```

```
      1.0.0.0/32 is subnetted, 1 subnets
C        1.1.1.1 is directly connected, Loopback0
      2.0.0.0/32 is subnetted, 1 subnets
S        2.2.2.2 [1/0] via 10.0.12.2
      3.0.0.0/32 is subnetted, 1 subnets
S        3.3.3.3 [1/0] via 10.0.13.2
      10.0.0.0/8 is variably subnetted, 6 subnets, 2 masks
C        10.0.12.0/30 is directly connected, GigabitEthernet0/0
L        10.0.12.1/32 is directly connected, GigabitEthernet0/0
C        10.0.13.0/30 is directly connected, GigabitEthernet0/1
L        10.0.13.1/32 is directly connected, GigabitEthernet0/1
S        10.0.23.0/30 [1/0] via 10.0.13.2
                      [1/0] via 10.0.12.2
```

> `S` = static · `[1/0]` = **AD 1 / metric 0**. Nếu bạn dùng lại LAB P0-5 (OSPF) thì
> chỗ này là `O` và `[110/11]` — **không sao, phần so sánh bên dưới vẫn đúng y hệt.**

### b) FIB — bảng "của máy"

```
R1# show ip cef
```

```
Prefix               Next Hop             Interface
0.0.0.0/0            no route
0.0.0.0/8            drop
0.0.0.0/32           receive
1.1.1.1/32           receive              Loopback0
2.2.2.2/32           10.0.12.2            GigabitEthernet0/0
3.3.3.3/32           10.0.13.2            GigabitEthernet0/1
10.0.12.0/30         attached             GigabitEthernet0/0
10.0.12.0/32         receive              GigabitEthernet0/0
10.0.12.1/32         receive              GigabitEthernet0/0
10.0.12.3/32         receive              GigabitEthernet0/0
10.0.13.0/30         attached             GigabitEthernet0/1
10.0.23.0/30         10.0.13.2            GigabitEthernet0/1
                     10.0.12.2            GigabitEthernet0/0
224.0.0.0/4          drop
255.255.255.255/32   receive
```

### c) Đặt hai bảng cạnh nhau

Mở hai cửa sổ terminal, chạy `show ip route` ở một bên và `show ip cef` ở bên kia. Rồi tự điền:

| Câu hỏi | RIB | FIB |
|---|:---:|:---:|
| Có `[1/0]` (AD/metric) không? | ☐ | ☐ |
| Có ghi **nguồn route** (static hay OSPF) không? | ☐ | ☐ |
| Có ký hiệu `S`, `C`, `L` không? | ☐ | ☐ |
| Có entry `receive` không? | ☐ | ☐ |
| Có entry `drop` không? | ☐ | ☐ |
| `10.0.23.0/30` có mấy next-hop? | ☐ | ☐ |

<details>
<summary>Đáp án</summary>

| Câu hỏi | RIB | FIB |
|---|:---:|:---:|
| AD/metric `[1/0]` | ✅ có | ❌ **không** |
| Nguồn route (static/OSPF) | ✅ có | ❌ **không** |
| Ký hiệu `S` `C` `L` | ✅ có | ❌ không |
| `receive` | ❌ không | ✅ **có** |
| `drop` | ❌ không | ✅ **có** |
| Số next-hop của `10.0.23.0/30` | 2 dòng `via` | 2 next-hop |

**Rút ra:** FIB **vứt bỏ** mọi thứ dùng để *so sánh và chọn đường* (AD, metric, nguồn),
vì việc chọn đã xong rồi. Đổi lại nó **thêm** những entry mà ASIC cần để hành động ngay
(`receive`, `drop`, `attached`).

</details>

### d) Ba từ khóa của FIB

| Từ khóa | Nghĩa |
|---|---|
| `receive` | Gói gửi tới **chính router này** → đẩy lên CPU |
| `attached` | Subnet cắm trực tiếp → **chưa biết MAC**, phải ARP (xem bước 4) |
| `drop` | Địa chỉ không hợp lệ → bỏ gói ngay ở hardware |

**💡 Vì sao FIB khác RIB:** RIB là nơi các giao thức **tranh luận** xem đường nào tốt
(nên cần AD, metric, uptime để so sánh). FIB là **kết luận cuối cùng** đưa cho ASIC thi hành —
ASIC không cần biết "vì sao", chỉ cần biết "đẩy ra đâu".

> **Một câu để nhớ:** RIB là **biên bản họp**, FIB là **quyết định đã ký**.

✅ **Checkpoint 2:** chỉ ra được **3 thứ RIB có mà FIB không có**, và **2 thứ FIB có mà RIB không có**.

---

# Bước 3 — Adjacency Table: 14 byte được chuẩn bị sẵn

**🎯 Mục tiêu:** thấy CEF chuẩn bị sẵn header L2 trước khi gói đến.

**Gõ:**
```
R1# show adjacency detail
```

**Sẽ thấy:**
```
Protocol Interface                 Address
IP       GigabitEthernet0/0        10.0.12.2(7)
                                   0 packets, 0 bytes
                                   epoch 0
                                   sourced in sev-epoch 0
                                   Encap length 14
                                   0C1A2B000200 0C1A2B000100 0800
                                   ARP
```

**Mổ xẻ chuỗi hex đó:**

```
   0C1A2B000200      0C1A2B000100      0800
   └──────┬─────┘    └──────┬─────┘    └─┬──┘
     MAC ĐÍCH           MAC NGUỒN     EtherType
     (của R2)           (của R1)      0x0800 = IPv4
      6 byte             6 byte        2 byte

                    tổng = 14 byte  ✅
```

**Đối chiếu với bảng ARP:**
```
R1# show arp
```
MAC của `10.0.12.2` trong bảng ARP phải **khớp** với 6 byte đầu của chuỗi hex trên.

**💡 Vì sao quan trọng:** đây chính là **"L2 rewrite information"**. Khi gói đến, ASIC không phải
tra ARP, không phải tính toán gì — chỉ **dán 14 byte này vào đầu gói rồi bắn ra**. Đó là lý do CEF nhanh.

✅ **Checkpoint 3:** thấy `Encap length 14`, và MAC trong chuỗi hex khớp với `show arp`.

---

# Bước 4 — Vì sao ping lần đầu mất 1 gói

**🎯 Mục tiêu:** giải thích hiện tượng `.!!!!` mà bạn đã thấy từ thời CCNA.

### a) Xóa ARP để quay về trạng thái ban đầu

```
R1# clear arp-cache
R1# show arp
```

### b) Xem FIB entry của subnet cắm trực tiếp

```
R1# show ip cef 10.0.12.0/30 detail
```

```
10.0.12.0/30, epoch 0, flags [attached, connected, cover dependents]
  attached to GigabitEthernet0/0
```

Từ khóa `attached` = **glean adjacency**: *"tôi biết subnet này ở cửa Gi0/0, nhưng chưa biết MAC
của host cụ thể — phải đi hỏi ARP đã."*

### c) Ping và quan sát

```
R1# ping 10.0.12.2
```

```
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 10.0.12.2, timeout is 2 seconds:
.!!!!
Success rate is 80 percent (4/5), round-trip min/avg/max = 1/2/5 ms
```

### d) Chuyện gì vừa xảy ra

```
   Gói 1:  FIB tra ra "attached"  →  chưa có MAC
              ↓
           PUNT lên CPU  →  CPU gửi ARP request  →  chờ reply
              ↓
           Gói ICMP số 1 bị BỎ trong lúc chờ          →  dấu  .

   Gói 2-5: ARP đã có  →  adjacency hoàn chỉnh (Encap length 14)
              ↓
           Đi thẳng hardware                          →  !!!!
```

### e) Xác nhận adjacency đã hoàn chỉnh

```
R1# show adjacency 10.0.12.2 detail
```
Giờ đã có `Encap length 14` với MAC đầy đủ.

**💡 Đây là câu trả lời cấp CCNP** cho một hiện tượng bạn thấy từ CCNA. Đáng ghi vào `SO-TAY-LOI.md`.

✅ **Checkpoint 4:** tái hiện được `.!!!!` sau `clear arp-cache`, và giải thích được dấu `.` đầu tiên
bằng từ **glean** và **punt**.

---

# Bước 5 — Vì sao `debug ip packet` không thấy gì

> **Bước giá trị nhất của lab này.** Nó chứng minh bằng tay một câu hỏi đề ENCOR hay ra.

**🎯 Mục tiêu:** thấy rằng traffic đi qua router **không hiện** trong debug — và hiểu vì sao.

### a) Xác nhận traffic R2→R3 đi vòng qua R1

Config ở phần chuẩn bị đã **cố ý** trỏ R2 và R3 đi vòng qua R1 (thay vì dùng link trực tiếp
R2–R3). Chỉ cần kiểm tra lại:

```
R2# show ip route 3.3.3.3
```
Phải thấy `via 10.0.12.1` — tức là **đi qua R1**, không phải `via 10.0.23.2`.

> Nếu bạn dùng lại LAB P0-5 (OSPF), OSPF sẽ chọn link trực tiếp R2–R3 nên **không có transit**.
> Khi đó phải tạm `shutdown` cổng `Gi0/1` của R2 rồi chờ OSPF hội tụ (~30 giây).
> Dùng static như hướng dẫn này thì **không cần bước đó**.

### b) Bật debug trên R1

```
R1# debug ip packet
IP packet debugging is on
```

### c) Từ R2 ping R3

```
R2# ping 3.3.3.3 source 2.2.2.2 repeat 20
```

### d) Nhìn màn hình R1

```
R1#
```

**Trống. Không có dòng nào.**

> ⭐ **Đây là ĐÚNG, không phải lỗi cấu hình.**

**💡 Vì sao:** `debug ip packet` là công cụ của **CPU**. Nó chỉ thấy gói nào **CPU phải xử lý**.
Traffic transit đi qua **CEF ở hardware** → CPU hoàn toàn không nhìn thấy.

### e) Chứng minh bằng cách tắt CEF

> ⚠️ **CHỈ LÀM TRONG LAB.** Tắt CEF trên thiết bị thật = CPU 100% = sự cố ngay.

```
R1(config)# interface GigabitEthernet0/0
R1(config-if)# no ip route-cache cef
R1(config-if)# exit
R1(config)# interface GigabitEthernet0/1
R1(config-if)# no ip route-cache cef
R1(config-if)# end
```

Ping lại từ R2:
```
R2# ping 3.3.3.3 source 2.2.2.2 repeat 5
```

**Giờ R1 hiện ra:**
```
IP: tableid=0, s=2.2.2.2 (GigabitEthernet0/0), d=3.3.3.3 (GigabitEthernet0/1),
    routed via RIB
IP: s=2.2.2.2 (GigabitEthernet0/0), d=3.3.3.3 (GigabitEthernet0/1), g=10.0.13.2,
    len 100, forward
```

Chú ý dòng **`routed via RIB`** — không dùng FIB nữa, CPU tra thẳng RIB cho **từng gói một**.
Đó chính là **process switching**.

### f) 🔴 DỌN DẸP — bắt buộc làm

```
R1# undebug all
R1# configure terminal
R1(config)# interface GigabitEthernet0/0
R1(config-if)#  ip route-cache cef
R1(config-if)# exit
R1(config)# interface GigabitEthernet0/1
R1(config-if)#  ip route-cache cef
R1(config-if)# end
R1# show ip cef summary
```

> Dùng static thì **không có gì khác phải dọn** — bạn không hề shutdown cổng nào.
> *(Nếu bạn đi theo nhánh OSPF ở mục (a) thì nhớ `no shutdown` cổng `Gi0/1` của R2.)*

✅ **Checkpoint 5 — tự điền:**

| Trạng thái CEF | `debug ip packet` có thấy traffic transit? |
|---|:---:|
| CEF bật (mặc định) | ☐ |
| CEF tắt | ☐ |

<details>
<summary>Đáp án + vì sao đề hay hỏi</summary>

| Trạng thái CEF | Thấy? | Vì sao |
|---|:---:|---|
| CEF **bật** | ❌ **Không** | Gói đi hardware, CPU không tham gia |
| CEF **tắt** | ✅ Có (`routed via RIB`) | Gói bị đẩy lên CPU = process switching |

**Dạng câu hỏi đề:** *"Kỹ sư gõ `debug ip packet` để xem traffic người dùng nhưng không thấy gì.
Vì sao?"* → **Vì CEF forward ở data plane; debug chỉ thấy gói process-switched.**

</details>

---

# Bước 6 — Hai đường bằng nhau, flow của tôi đi đường nào?

**🎯 Mục tiêu:** thấy CEF chia tải **theo flow**, không phải ngẫu nhiên.

### a) Xác nhận có ECMP trong FIB

```
R1# show ip cef 10.0.23.0/30
```

```
Prefix               Next Hop             Interface
10.0.23.0/30         10.0.13.2            GigabitEthernet0/1
                     10.0.12.2            GigabitEthernet0/0
```
Hai next-hop = ECMP.

### b) Lệnh hay nhất của module

```
R1# show ip cef exact-route 1.1.1.1 10.0.23.1
```

```
1.1.1.1 -> 10.0.23.1 => IP adj out of GigabitEthernet0/0, addr 10.0.12.2
```

### c) Thử 4 cặp và tự điền bảng

```
R1# show ip cef exact-route 1.1.1.1   10.0.23.1
R1# show ip cef exact-route 1.1.1.1   10.0.23.2
R1# show ip cef exact-route 10.0.12.1 10.0.23.1
R1# show ip cef exact-route 10.0.13.1 10.0.23.2
```

| Source | Destination | Ra interface nào |
|---|---|---|
| 1.1.1.1 | 10.0.23.1 | |
| 1.1.1.1 | 10.0.23.2 | |
| 10.0.12.1 | 10.0.23.1 | |
| 10.0.13.1 | 10.0.23.2 | |

### d) Chạy lại **đúng cặp đầu tiên** một lần nữa

Kết quả có **giống hệt** lần trước không?

**💡 Bài học:** cùng cặp (nguồn, đích) → **luôn ra cùng một interface**. Đổi nguồn hoặc đích → có thể
đổi interface. Đó là **per-destination load-balancing**: hash theo cặp src+dst, nên mỗi flow **dính
cố định vào một đường** → gói không bao giờ đến đích sai thứ tự.

### e) Xem chế độ đang dùng

```
R1# show cef interface GigabitEthernet0/0 | include load|Load
```
```
  Load sharing: per-destination
```

### f) 🚀 Tùy chọn — thấy polarization bằng thực nghiệm

```
R1(config)# ip cef load-sharing algorithm universal 1A2B3C4D
R1(config)# end
R1# show ip cef exact-route 1.1.1.1 10.0.23.1
```

Chạy lại **cùng cặp src/dst như bước (b)** → kết quả có thể **ra interface khác**.

> **Ý nghĩa:** cùng flow, cùng topology, chỉ đổi ID hash là đổi đường. Trong mạng nhiều tầng,
> nếu mọi tầng dùng **cùng ID** thì mọi tầng chọn **cùng nhánh** → dồn tải một bên =
> **CEF polarization**. Đổi ID ở mỗi tầng thì tải phân tán đều.

✅ **Checkpoint 6:** điền xong bảng 4 dòng, và xác nhận **chạy lại cùng cặp thì kết quả không đổi**.

---

# Bước 7 — CPU cao: lỗi ở data plane hay control plane?

**🎯 Mục tiêu:** đọc được một con số mà bạn sẽ dùng suốt sự nghiệp.

**Gõ:**
```
R1# show processes cpu sorted | exclude 0.00
```

**Sẽ thấy:**
```
CPU utilization for five seconds: 3%/0%; one minute: 4%; five minutes: 4%
 PID Runtime(ms)     Invoked      uSecs   5Sec   1Min   5Min TTY Process
 108       12345        4567       2703  1.20%  1.10%  1.05%   0 IP RIB Update
  67        8765        3210       2730  0.80%  0.90%  0.85%   0 IP Input
  22        4321        9876        437  0.30%  0.25%  0.20%   0 Per-Second Jobs
```

> Danh sách tiến trình của bạn sẽ khác. Nếu chạy OSPF thì có thêm `OSPF-1 Router`;
> lab static này thì không. **Điều cần nhìn là dòng ĐẦU TIÊN**, không phải danh sách bên dưới.

**Đọc dòng đầu tiên — đây là phần quan trọng:**

```
   CPU utilization for five seconds:  3% / 0%
                                      │     │
                                      │     └── % dành cho INTERRUPT
                                      │         = CPU đang FORWARD GÓI
                                      └──────── % TỔNG
```

| Tổng | Interrupt | Nghĩa | Có đáng lo? |
|:---:|:---:|---|---|
| Cao | **Thấp** | CPU bận vì **control plane** (OSPF/BGP tính toán) | Bình thường lúc hội tụ |
| Cao | **Cao** | CPU đang **forward gói** → gói bị **punt** nhiều | 🔴 **Xấu**: CEF tắt, TCAM đầy, hoặc bị tấn công |

**Thử tạo interrupt cao (chỉ trong lab):**
```
R1(config)# no ip cef
R1(config)# end
```
Rồi từ R2:
```
R2# ping 3.3.3.3 source 2.2.2.2 repeat 1000 size 1500
```
Trên R1:
```
R1# show processes cpu | include utilization
```
→ **interrupt % tăng vọt**.

**🔴 Bật lại ngay:**
```
R1(config)# ip cef
R1(config)# end
R1# show ip cef summary
```

**💡 Bài học đi làm:** gặp thiết bị CPU cao, lệnh **đầu tiên** là
`show processes cpu sorted | exclude 0.00`, và **đọc con số interrupt**:
- Interrupt **cao** → vấn đề **data plane** (punt / CEF / TCAM)
- Interrupt **thấp** → vấn đề **control plane** (giao thức)

✅ **Checkpoint 7:** giải thích được ý nghĩa `3%/0%`, và quan sát được interrupt tăng khi tắt CEF.

---

# 🚀 Bước 8 (tùy chọn) — TCAM & SDM

> ℹ️ vIOS là router ảo, **không có TCAM thật**. Phần này cần switch thật hoặc
> **DevNet Sandbox** (Catalyst 9000 always-on): `developer.cisco.com/site/sandbox/`

```
show sdm prefer
show platform hardware fed switch active fwd-asic resource tcam utilization
show mac address-table count
```

| Câu hỏi | Trả lời của bạn |
|---|---|
| Template SDM đang dùng là gì? | |
| MAC table đang có bao nhiêu entry / tối đa bao nhiêu? | |
| Muốn chứa nhiều route hơn thì đổi template nào? Sau đó phải làm gì? | |

<details>
<summary>Gợi ý câu 3</summary>

Đổi bằng `sdm prefer <template>`, và **bắt buộc `reload`** — TCAM được phân vùng lúc khởi động,
không đổi nóng được.

</details>

---

# ✅ Tự chấm LAB 01

| # | Làm được | ✅ |
|:---:|---|:---:|
| 1 | Dựng xong topology, ping được `2.2.2.2` và `3.3.3.3` từ R1, và có **ECMP** tới `10.0.23.0/30` | ☐ |
| 2 | Chỉ ra **3 thứ RIB có mà FIB không**, **2 thứ FIB có mà RIB không** | ☐ |
| 3 | Giải thích `receive` / `attached` / `drop` trong FIB | ☐ |
| 4 | Tìm được `Encap length 14` và đối chiếu MAC với `show arp` | ☐ |
| 5 | Tái hiện `.!!!!` và giải thích bằng **glean + punt** | ☐ |
| 6 | **Chứng minh `debug ip packet` không thấy traffic transit khi CEF bật** | ☐ |
| 7 | Tắt CEF → thấy `routed via RIB` → bật lại | ☐ |
| 8 | Điền bảng `exact-route` 4 dòng, xác nhận tính nhất quán | ☐ |
| 9 | Đọc được `3%/0%` và nói được interrupt cao nghĩa là gì | ☐ |
| 10 | Đã **dọn dẹp**: CEF bật lại (`show ip cef summary`), debug đã tắt (`show debugging` trống) | ☐ |

> **Chưa tick được mục 2, 5, 6 thì chưa nên sang Module-02** — ba mục đó là toàn bộ
> giá trị của Module-01.

---

**📘 Quay lại lý thuyết:** [Module-01](Module-01-Packet-Forwarding-va-Kien-truc-Thiet-bi.md)
**➡️ Module tiếp theo:** [Module-02 — Layer 2](Module-02-Layer2-STP-RSTP-MST-EtherChannel.md)
