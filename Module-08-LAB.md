# LAB 08 — Tuần 14: VRF · GRE · IPsec

> 📘 **Lý thuyết:** [Module-08](Module-08-Virtualization-va-Overlay.md) —
> đọc **Phần 1** và **Phần 2 mục §4 (VRF), §5 (GRE), §6–7 (IPsec)** trước khi làm.
>
> ⏱️ **Thời gian:** ~5 giờ · 💾 **RAM:** 2 GB *(hoặc ~7 GB nếu phải dùng CSR1000v cho crypto)*
> · 🧰 **Cần:** EVE-NG + 3× vIOS

---

## Lab này trả lời 6 câu hỏi

| # | Câu hỏi | Bước |
|:---:|---|:---:|
| 1 | Hai interface **cùng một IP** trên một router — làm sao được? | 1 |
| 2 | Vì sao gán VRF xong thì **IP biến mất**? | 1 |
| 3 | Vì sao `ping <ip>` **không bao giờ** tới host trong VRF? | 1 |
| 4 | Gói đi qua Internet mà ISP **không biết** mạng nội bộ — bằng cách nào? | 2 |
| 5 | Tunnel lên rồi xuống liên tục — vì sao, và sửa thế nào? | 3 |
| 6 | Bắt gói trước/sau khi bật IPsec — khác nhau thế nào? | 5, §11.5 |

> ⭐ **Bước 3 (tái hiện recursive routing) là bước giá trị nhất.**
> Lab hỏng dạy nhiều hơn lab chạy — bạn sẽ thấy tunnel flapping thật và hiểu vì sao.

---

## ⚠️ Đọc trước khi bắt đầu

| Điều cần biết | Chi tiết |
|---|---|
| ⚠️ **Kiểm tra crypto TRƯỚC** | Gõ `crypto isakmp policy 10` trên R1. Báo `% Invalid input` thì image thiếu `securityk9` — đổi R1/R2 sang **CSR1000v**, hoặc bỏ bước 5 và đọc kỹ cấu hình |
| ⭐ **VRF: gán VRF TRƯỚC, đặt IP SAU** | Làm ngược thì IP bị xóa. Trên thiết bị thật, nếu đang SSH qua chính interface đó thì **mất kết nối** |
| ⭐ **Ping trong VRF phải gõ `vrf`** | `ping vrf KHACH-A <ip>` — quên là dùng bảng global, không bao giờ tới |
| **Bước 3 và 6 là cố ý phá** | Làm xong nhớ sửa lại |
| **Lỗi > 15 phút** | Ghi vào [`SO-TAY-LOI.md`](SO-TAY-LOI.md) |

---

## 🧪 10. LAB 08 — VRF + GRE + IPsec

### 10.1 Topology

```
        ┌─ SITE A ─────────────┐                    ┌─ SITE B ─────────────┐
        │                      │                    │                      │
   Lo10 │ 10.1.1.1/24 ┌──────┐ │ Gi0/0              │ Gi0/0 ┌──────┐       │ Lo10
   Lo20 │ 10.10.10.1  │  R1  │─┼─203.0.113.1        203.0.113.2─│  R2  │───┼─10.2.2.1/24
   Lo30 │ 10.10.10.1  │      │ │       ╲              ╱         └──────┘   │
        │ (TRÙNG!) └──────┘ │        ╲            ╱                     │
        └──────────────────────┘         ╲          ╱                      └──────────────┘
                                      ┌───────────────┐
                                      │    R-ISP      │  đóng vai "Internet"
                                      │ 203.0.113.254 │  KHÔNG biết gì về 10.x
                                      └───────────────┘
```

| Node | Image | RAM | Vai trò |
|---|---|:---:|---|
| **R1** | vIOS *(hoặc CSR1000v nếu cần crypto)* | 512 MB / 3 GB | Site A — VRF + đầu tunnel |
| **R2** | vIOS *(hoặc CSR1000v)* | 512 MB / 3 GB | Site B — đầu tunnel kia |
| **R-ISP** | vIOS | 512 MB | ⭐ "Internet" — **cố ý không biết mạng 10.x** |

⭐ **Tổng RAM: ~1.5 GB (vIOS) hoặc ~6.5 GB (2× CSR1000v)** ✅

### 10.2 Bảng nối dây

| Từ | Interface | Tới | Interface | Mạng |
|---|---|---|---|---|
| R1 | Gi0/0 | R-ISP | Gi0/0 | 203.0.113.0/30 *(R1=.1, ISP=.254 dùng /24 cho tiện)* |
| R2 | Gi0/0 | R-ISP | Gi0/1 | 203.0.113.0/24 |

⭐ **Đơn giản hóa:** dùng chung subnet `203.0.113.0/24` cho cả hai link, R-ISP có 2 interface trong đó.
*(Không "đúng chuẩn" nhưng ⭐ **giữ lab gọn và không ảnh hưởng bài học**.)*

---

### Bước 0 — ⭐ Cấu hình nền (underlay)

```
!═══════ R-ISP ═══════ (đóng vai Internet: CHỈ biết mạng public)
hostname R-ISP
interface GigabitEthernet0/0
 ip address 203.0.113.254 255.255.255.0
 no shutdown
interface GigabitEthernet0/1
 ip address 203.0.113.253 255.255.255.0
 no shutdown
! CỐ Ý KHÔNG cấu hình route nào tới 10.0.0.0/8
!    → Chứng minh traffic 10.x chỉ đi được nhờ TUNNEL

!═══════ R1 ═══════
hostname R1
interface GigabitEthernet0/0
 ip address 203.0.113.1 255.255.255.0
 no shutdown
interface Loopback10
 ip address 10.1.1.1 255.255.255.0        ! LAN site A
!
ip route 0.0.0.0 0.0.0.0 203.0.113.254    ! default ra "Internet"

!═══════ R2 ═══════
hostname R2
interface GigabitEthernet0/0
 ip address 203.0.113.2 255.255.255.0
 no shutdown
interface Loopback10
 ip address 10.2.2.1 255.255.255.0        ! LAN site B
!
ip route 0.0.0.0 0.0.0.0 203.0.113.253
```

✅ **Checkpoint 0:**
```
R1# ping 203.0.113.2
!!!!!                                      ! ✅ underlay thông

R1# ping 10.2.2.1 source 10.1.1.1
.....                                      ! ✅ ĐÚNG như mong đợi — PHẢI THẤT BẠI
                                           ! vì ISP không biết mạng 10.x
```
> 💡 ⭐ **Vì sao bước này quan trọng:** bạn vừa **chứng minh xuất phát điểm**.
> ⭐ Mọi thứ hoạt động sau đây **chỉ có thể là nhờ tunnel**, không phải nhờ may mắn.

---

### Bước 1 — ⭐⭐ VRF-lite và sức mạnh "IP trùng nhau"

```
!═══════ TRÊN R1 ═══════
vrf definition KHACH-A
 rd 65001:1
 address-family ipv4
 exit-address-family
!
vrf definition KHACH-B
 rd 65001:2
 address-family ipv4
 exit-address-family
!
! HAI interface, CÙNG một dải IP, khác VRF
interface Loopback20
 vrf forwarding KHACH-A                   ! GÁN VRF TRƯỚC
 ip address 10.10.10.1 255.255.255.0      ! ĐẶT IP SAU
 description LAN cua KHACH-A
!
interface Loopback30
 vrf forwarding KHACH-B                   ! VRF khác
 ip address 10.10.10.1 255.255.255.0      ! IP GIỐNG HỆT — VÀ NÓ CHẠY!
 description LAN cua KHACH-B
```

✅ **Checkpoint 1.1 — ⭐ chứng kiến điều "không thể":**
```
R1# show ip interface brief | include Loopback
Loopback10   10.1.1.1     YES manual up  up
Loopback20   10.10.10.1   YES manual up  up      
Loopback30   10.10.10.1   YES manual up  up      CÙNG IP, KHÔNG BÁO LỖI!
```

> 💡 ⭐⭐ **Dừng lại và ngẫm 30 giây.** Trên một router bình thường, đặt cùng IP lên 2 interface sẽ báo:
> `% 10.10.10.1 overlaps with Loopback20`.
> ⭐ **Ở đây không báo gì cả** — vì hai interface **sống trong hai vũ trụ khác nhau**.
> ⭐ **Đây chính là toàn bộ ý nghĩa của VRF.**

✅ **Checkpoint 1.2 — ba bảng route độc lập:**
```
R1# show vrf
  Name        Default RD    Protocols   Interfaces
  KHACH-A     65001:1       ipv4        Lo20
  KHACH-B     65001:2       ipv4        Lo30

R1# show ip route | include 10.10.10
                                          KHÔNG CÓ GÌ — global table không thấy

R1# show ip route vrf KHACH-A | include 10.10.10
C     10.10.10.0/24 is directly connected, Loopback20      chỉ thấy của mình

R1# show ip route vrf KHACH-B | include 10.10.10
C     10.10.10.0/24 is directly connected, Loopback30      cũng chỉ thấy của mình
```

✅ **Checkpoint 1.3 — ⭐⭐ tái hiện BẪY SỐ 2 (bẫy quan trọng nhất của VRF):**
```
R1# ping 10.10.10.1
!!!!!            ! ⚠️ Thành công NHƯNG... nó ping vào đâu?

! Thử ping một địa chỉ KHÁC trong VRF, từ global:
R1# ping 10.10.10.99
.....            ! THẤT BẠI

R1# ping vrf KHACH-A 10.10.10.99
.....            ! (vẫn fail vì không có host thật, nhưng hãy so sánh cách nó gửi gói)
```
> 💡 🔴 ⭐⭐ **Bài học:** ⭐ **quên `vrf` = đang dùng bảng global = KHÔNG BAO GIỜ tới được VRF.**
> ⭐ Đây là nguyên nhân của 90% ca *"tôi cấu hình VRF rồi mà không ping được"*.

✅ **Checkpoint 1.4 — ⭐ tái hiện BẪY SỐ 1 (mất IP khi gán VRF):**
```
R1(config)# interface Loopback40
R1(config-if)# ip address 192.168.99.1 255.255.255.0    ! đặt IP TRƯỚC (cố ý làm sai)
R1(config-if)# vrf forwarding KHACH-A                   ! rồi mới gán VRF

% Interface Loopback40 IPv4 disabled and address(es) removed due to enabling VRF KHACH-A

R1(config-if)# do show ip interface brief | include Loopback40
Loopback40    unassigned    YES unset  up  up         IP ĐÃ BAY MẤT
```
> 💡 🔴 ⭐⭐ **Ghi ngay vào `SO-TAY-LOI.md`.** ⭐ Trên production, nếu bạn đang SSH qua interface đó
> thì bạn **vừa tự cắt kết nối tới thiết bị**. ⭐ **Luôn: VRF trước, IP sau.**

---

### Bước 2 — ⭐⭐ GRE tunnel giữa hai site

```
!═══════ R1 ═══════
interface Tunnel0
 description GRE toi Site-B
 ip address 172.16.0.1 255.255.255.252
 tunnel source GigabitEthernet0/0
 tunnel destination 203.0.113.2
 keepalive 10 3

!═══════ R2 ═══════
interface Tunnel0
 description GRE toi Site-A
 ip address 172.16.0.2 255.255.255.252
 tunnel source GigabitEthernet0/0
 tunnel destination 203.0.113.1
 keepalive 10 3
```

✅ **Checkpoint 2.1:**
```
R1# show ip interface brief | include Tunnel
Tunnel0   172.16.0.1   YES manual up  up      up/up

R1# ping 172.16.0.2
!!!!!                                          tunnel thông
```

✅ **Checkpoint 2.2 — ⭐ đọc thông số tunnel:**
```
R1# show interface tunnel0 | include MTU|Tunnel source|transport
  MTU 17916 bytes, BW 100 Kbit/sec
  Tunnel source 203.0.113.1 (GigabitEthernet0/0), destination 203.0.113.2
  Tunnel transport MTU 1476 bytes         ← 1500 − 24 = GRE overhead
```
> 💡 ⭐ **Con số 1476 là bằng chứng vật lý cho lý thuyết §4.1.** ⭐ Nhìn thấy nó một lần là nhớ mãi.

Giờ chạy **OSPF qua tunnel** để hai LAN thấy nhau:
```
!═══════ R1 ═══════
router ospf 1
 network 172.16.0.0 0.0.0.3 area 0        ! mạng tunnel
 network 10.1.1.0 0.0.0.255 area 0        ! LAN site A
 ! CHÚ Ý: KHÔNG có 203.0.113.0 ở đây!

!═══════ R2 ═══════
router ospf 1
 network 172.16.0.0 0.0.0.3 area 0
 network 10.2.2.0 0.0.0.255 area 0
```

✅ **Checkpoint 2.3 — ⭐⭐ bài test quyết định:**
```
R1# show ip ospf neighbor
Neighbor ID   Pri  State     Dead Time  Address      Interface
2.2.2.2         0  FULL/  -  00:00:35   172.16.0.2   Tunnel0

R1# show ip route ospf
O   10.2.2.0/24 [110/1001] via 172.16.0.2, 00:01:12, Tunnel0

R1# ping 10.2.2.1 source 10.1.1.1
!!!!!                                    THÀNH CÔNG!
```
> 💡 ⭐⭐ **So sánh với Checkpoint 0** — cùng lệnh ping đó, lúc nãy **thất bại hoàn toàn**.
> ⭐ **R-ISP vẫn KHÔNG hề biết gì về mạng 10.x** — nó chỉ thấy các gói IP giữa 203.0.113.1 và 203.0.113.2.
> ⭐ **Đó chính là ý nghĩa của overlay.**

⭐ **Kiểm chứng thêm (rất đáng làm):**
```
R-ISP# show ip route | include 10\.
                                         TRỐNG. ISP hoàn toàn không biết mạng 10.x
```

---

### Bước 3 — 🔴 ⭐⭐ CỐ Ý TÁI HIỆN RECURSIVE ROUTING

> ⭐ **Đây là bước giá trị nhất của cả LAB.** ⭐ **Đừng bỏ qua.** Lab hỏng dạy nhiều hơn lab chạy.

```
! Trên CẢ R1 VÀ R2 — cố ý advertise mạng WAN vào OSPF-qua-tunnel:
router ospf 1
 network 203.0.113.0 0.0.0.255 area 0     ! DÒNG GÂY THẢM HỌA
```

✅ **Checkpoint 3.1 — quan sát vụ nổ (chờ ~30–60 giây):**
```
%TUN-5-RECURDOWN: Tunnel0 temporarily disabled due to recursive routing
%LINEPROTO-5-UPDOWN: Line protocol on Interface Tunnel0, changed state to down
%OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel0 from FULL to DOWN
%LINEPROTO-5-UPDOWN: Line protocol on Interface Tunnel0, changed state to up
%TUN-5-RECURDOWN: Tunnel0 temporarily disabled due to recursive routing
   ...LẶP MÃI. Đây là "tunnel flapping".
```

✅ **Checkpoint 3.2 — nhìn vào NGUYÊN NHÂN (bắt lúc tunnel đang up):**
```
R1# show ip route 203.0.113.2
Routing entry for 203.0.113.0/24
  Known via "ospf 1", distance 110, metric 1001
   * 172.16.0.2, from 2.2.2.2, via Tunnel0      ← NHÌN DÒNG NÀY!

"Muốn tới 203.0.113.2 → đi qua Tunnel0"
Nhưng Tunnel0 cần biết đường tới 203.0.113.2 để hoạt động
→ VÒNG LẶP. Router phát hiện và tự tắt tunnel.
```

✅ **Checkpoint 3.3 — sửa bằng CẢ HAI cách, hiểu vì sao mỗi cách có tác dụng:**

```
! CÁCH 1 (đúng nhất) — gỡ mạng WAN khỏi OSPF-qua-tunnel:
router ospf 1
 no network 203.0.113.0 0.0.0.255 area 0
```
```
! CÁCH 2 — static route AD thấp hơn "đè" lên OSPF:
ip route 203.0.113.2 255.255.255.255 203.0.113.254
!    AD 1  <  AD 110 của OSPF → static LUÔN THẮNG
!    Và /32 dài hơn /24 → longest-prefix cũng thắng (Module-03!)
```

✅ **Xác nhận đã ổn:**
```
R1# show ip route 203.0.113.2
   phải trỏ ra GigabitEthernet0/0, KHÔNG được trỏ ra Tunnel0

R1# show interface tunnel0 | include line protocol
Tunnel0 is up, line protocol is up        ổn định, không flap nữa
```

> 💡 🔴 ⭐⭐ **Bài học một câu — ghi vào `SO-TAY-LOI.md`:**
> ⭐ ***"Đường tới tunnel destination KHÔNG BAO GIỜ được đi qua chính tunnel đó."***

---

### Bước 4 — ⭐⭐ MTU & MSS

✅ **Checkpoint 4.1 — tìm ra ngưỡng MTU thật của tunnel:**
```
R1# ping 172.16.0.2 df-bit size 1400
!!!!!                                    ✅ qua được

R1# ping 172.16.0.2 df-bit size 1476
!!!!!                                    ✅ vẫn qua — đây là ĐÚNG giới hạn

R1# ping 172.16.0.2 df-bit size 1477
Packet sent with the DF bit set
.....                                    THẤT BẠI
   Bạn vừa TỰ TAY tìm ra con số 1476 = 1500 − 24 (GRE overhead)
```

✅ **Checkpoint 4.2 — áp cấu hình chuẩn (⭐ trên CẢ HAI đầu):**
```
interface Tunnel0
 ip mtu 1400
 ip tcp adjust-mss 1360
```
```
R1# show interface tunnel0 | include MTU
  MTU 17916 bytes ...
  IP MTU 1400 bytes
  Tunnel transport MTU 1476 bytes
```

> 💡 ⭐ **Vì sao vẫn nên đặt 1400 dù tunnel chịu được 1476?**
> ⭐ Vì lát nữa thêm **IPsec** sẽ ăn thêm ~50–60 byte. ⭐ **Đặt 1400 ngay từ đầu là an toàn cho cả hai trường hợp** —
> đây cũng là con số các nhà mạng và nhà tích hợp dùng mặc định ngoài đời.

---

### Bước 5 — ⭐⭐ Thêm IPsec: biến GRE thành GRE over IPsec

> 🔴 ⚠️ **Nếu vIOS báo `% Invalid input` ở lệnh `crypto isakmp policy` → xem §1.1**,
> đổi R1/R2 sang **CSR1000v**, hoặc **bỏ qua bước này và đọc kỹ cấu hình** (vẫn nắm được để thi).

```
!═══════ TRÊN R1 ═══════
crypto isakmp policy 10
 encryption aes 256
 hash sha256
 authentication pre-share
 group 14
!
crypto isakmp key CCNP-ENCOR-2026 address 203.0.113.2
!
crypto ipsec transform-set TSET esp-aes 256 esp-sha256-hmac
 mode transport                                ! TRANSPORT cho GRE over IPsec
!
crypto ipsec profile IPSEC-PROF
 set transform-set TSET
!
interface Tunnel0
 tunnel protection ipsec profile IPSEC-PROF    ! dòng duy nhất cần thêm vào tunnel

!═══════ TRÊN R2 ═══════ (giống hệt, chỉ đổi địa chỉ peer)
crypto isakmp key CCNP-ENCOR-2026 address 203.0.113.1
   ! phần còn lại y hệt R1
```

✅ **Checkpoint 5.1 — Phase 1:**
```
R1# ping 172.16.0.2                       ! tạo traffic để kích hoạt VPN
!!!!!

R1# show crypto isakmp sa
dst           src           state     conn-id status
203.0.113.2   203.0.113.1   QM_IDLE   1001  ACTIVE
                            "QM_IDLE" = Phase 1 XONG. ĐÂY LÀ TRẠNG THÁI TỐT.
```

✅ **Checkpoint 5.2 — ⭐⭐ Phase 2 và bằng chứng dữ liệu đang được mã hóa:**
```
R1# show crypto ipsec sa | include ident|encaps|decaps|encrypt|decrypt
   local  ident (addr/mask/prot/port): (203.0.113.1/255.255.255.255/47/0)
   remote ident (addr/mask/prot/port): (203.0.113.2/255.255.255.255/47/0)
                                                                    47 = GRE!
    #pkts encaps: 58, #pkts encrypt: 58
    #pkts decaps: 56, #pkts decrypt: 56

! BÀI TEST QUYẾT ĐỊNH — ping rồi xem số có TĂNG không:
R1# ping 10.2.2.1 source 10.1.1.1 repeat 20
!!!!!!!!!!!!!!!!!!!!

R1# show crypto ipsec sa | include encaps|decaps
    #pkts encaps: 78    (58 + 20)
    #pkts decaps: 76    (56 + 20)
```

> 💡 ⭐⭐ **`encaps` và `decaps` CÙNG TĂNG = VPN thật sự đang chở dữ liệu.**
> ⭐ Đây là bằng chứng mạnh hơn nhiều so với việc chỉ nhìn `QM_IDLE`.
> ⭐ **`prot 47` (GRE) trong ident** chính là bằng chứng bạn đang chạy ⭐ **GRE over IPsec**,
> chứ không phải IPsec thuần.

```
R1# show crypto session
Interface: Tunnel0
Session status: UP-ACTIVE
Peer: 203.0.113.2 port 500
  IKEv1 SA: local 203.0.113.1/500 remote 203.0.113.2/500 Active
  IPSEC FLOW: permit 47 host 203.0.113.1 host 203.0.113.2
        Active SAs: 2, origin: crypto map
```

✅ **Checkpoint 5.3 — ⭐ OSPF vẫn chạy (đây là điều IPsec thuần không làm được):**
```
R1# show ip ospf neighbor
2.2.2.2   0  FULL/  -  00:00:33  172.16.0.2  Tunnel0
```
> 💡 ⭐⭐ **Đây là câu trả lời sống động cho câu hỏi "vì sao phải GRE over IPsec".**
> ⭐ Nếu dùng **IPsec thuần (crypto map)**, ⭐ **OSPF sẽ KHÔNG chạy được** vì multicast `224.0.0.5`
> không đi qua được. ⭐ **Bạn vừa nhìn thấy tận mắt lý do tồn tại của cả mục 2.2.b.**

---

### Bước 6 — 🔴 ⭐⭐ CỐ Ý PHÁ IPsec (bắt buộc làm)

**Phá 1 — sai pre-shared key:**
```
R1(config)# no crypto isakmp key CCNP-ENCOR-2026 address 203.0.113.2
R1(config)# crypto isakmp key SAI-MAT-KHAU address 203.0.113.2
R1# clear crypto isakmp
R1# clear crypto sa
R1# ping 172.16.0.2
```
✅ **Quan sát:**
```
R1# show crypto isakmp sa
dst           src           state           conn-id status
203.0.113.2   203.0.113.1   MM_NO_STATE   1002  ACTIVE (deleted)
                            "MM_NO_STATE" = PHASE 1 THẤT BẠI
```
> 💡 ⭐⭐ **Ghi nhớ cặp đối lập này — đề hỏi rất nhiều:**
> ⭐ **`QM_IDLE` = Phase 1 THÀNH CÔNG** · 🔴 ⭐ **`MM_NO_STATE` / `MM_KEY_EXCH` = Phase 1 ĐANG HỎNG**

⭐ **Sửa lại key rồi `clear crypto isakmp` — xác nhận quay về `QM_IDLE`.**

**Phá 2 — lệch transform-set:**
```
R2(config)# crypto ipsec transform-set TSET esp-aes 128 esp-sha256-hmac
!                                             128 thay vì 256
R1# clear crypto sa
```
✅ **Quan sát:** ⭐ **Phase 1 vẫn `QM_IDLE` ✅ nhưng `show crypto ipsec sa` KHÔNG có SA nào active**,
⭐ `encaps`/`decaps` **đứng yên**.
> 💡 ⭐⭐ **Bài học:** ⭐ **Phase 1 OK mà không có dữ liệu chảy → lỗi ở PHASE 2** (transform-set / ACL).
> ⭐ Đây là cách khoanh vùng nhanh nhất khi troubleshoot IPsec.

**Phá 3 — tắt tunnel protection ở một đầu:**
```
R2(config-if)# no tunnel protection ipsec profile IPSEC-PROF
```
✅ **Quan sát:** ⭐ tunnel vẫn có thể hiện up (GRE stateless) nhưng ⭐ **traffic không qua được** —
một đầu mã hóa, đầu kia không hiểu.
> 💡 ⭐ **Bài học:** ⭐ **`tunnel protection` phải có ở CẢ HAI đầu.**

---

## 🚀 11. LAB NÂNG CAO

### 11.1 🚀 ⭐ Tunnel nằm TRONG VRF (rất hay gặp ngoài đời)

⭐ **Tình huống:** interface WAN nằm trong VRF `INTERNET`, nhưng traffic của tunnel là mạng nội bộ.

```
interface Tunnel0
 ip address 172.16.0.1 255.255.255.252
 tunnel source GigabitEthernet0/0
 tunnel destination 203.0.113.2
 tunnel vrf INTERNET              ! "hãy TÌM ĐƯỜNG tới destination trong VRF INTERNET"
```
> ⭐⭐ **Phân biệt hai lệnh dễ lẫn — đề có thể hỏi:**
> · ⭐ **`vrf forwarding X`** trên Tunnel0 = ⭐ **traffic BÊN TRONG tunnel thuộc VRF X** (overlay)
> · ⭐ **`tunnel vrf X`** = ⭐ **đường đi TỚI tunnel destination nằm trong VRF X** (underlay)
>
> ⭐ **Mẹo nhớ:** ⭐ *"`tunnel vrf` nói về VỎ, `vrf forwarding` nói về RUỘT."*

### 11.2 🚀 ⭐ Route leaking giữa VRF và global

```
! Cho VRF KHACH-A đi ra Internet (bảng global)
ip route vrf KHACH-A 0.0.0.0 0.0.0.0 203.0.113.254 global
!                                                   từ khóa quan trọng
! Chiều về: từ global trỏ ngược vào VRF
ip route 10.10.10.0 255.255.255.0 Loopback20
```
✅ **Test:** `ping vrf KHACH-A 203.0.113.254` → phải thành công.
⭐ **Nhớ:** ⭐ **route leaking phải làm CẢ HAI CHIỀU** mới thông.

### 11.3 🚀 ⭐ OSPF chạy trong VRF

```
router ospf 100 vrf KHACH-A
 router-id 1.1.1.100
 network 10.10.10.0 0.0.0.255 area 0
!
show ip ospf 100                          ! process riêng
show ip route vrf KHACH-A ospf
show ip ospf neighbor vrf KHACH-A
```

### 11.4 🚀 So sánh: IPsec thuần (crypto map) — để thấy nó KHÔNG chạy được OSPF

⭐ **Bài tập:** tháo GRE, dựng IPsec thuần bằng crypto map giữa R1–R2 (§5.4), rồi thử bật OSPF.
✅ **Bạn sẽ thấy:** ⭐ **OSPF neighbor KHÔNG BAO GIỜ lên** (multicast `224.0.0.5` không qua được crypto map).
⭐ **Đây là cách chứng minh mạnh nhất vì sao GRE over IPsec tồn tại.**

### 11.5 🚀 Bắt gói bằng Wireshark

⭐ Bắt gói trên link R1↔R-ISP trong EVE-NG *(chuột phải link → Capture)*:

| Giai đoạn | ⭐ Bạn sẽ thấy |
|---|---|
| ⭐ **Trước khi bật IPsec** | ⭐ **Gói GRE — và Wireshark GIẢI MÃ ĐƯỢC toàn bộ**: thấy rõ IP nội bộ 10.1.1.1, thấy cả gói OSPF bên trong. 🔴 ⭐ **Bằng chứng GRE không mã hóa gì cả** |
| ⭐ **Sau khi bật IPsec** | ⭐ **Chỉ thấy `ESP`** — nội dung là **một khối byte vô nghĩa**. ⭐ Không đọc được IP nội bộ, không thấy OSPF |
| ⭐ **Lúc mới bật** | ⭐ Thấy **ISAKMP trên UDP 500** — chính là Phase 1 đang bắt tay |

> 💡 ⭐⭐ **Đây là bài lab thuyết phục nhất cả module.** ⭐ Chụp lại hai ảnh Wireshark (trước/sau)
> và dán vào `SO-TAY-LOI.md`. ⭐ **Nhìn một lần là nhớ cả đời sự khác nhau giữa GRE và GRE over IPsec.**
