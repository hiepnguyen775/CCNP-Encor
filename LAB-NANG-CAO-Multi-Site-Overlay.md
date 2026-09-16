# LAB NÂNG CAO — Mạng nhiều site: từ DMVPN đến SD-WAN

> 🎓 **Đây là LAB MỞ RỘNG, làm SAU khi xong [LAB Capstone](Module-13-LAB-Capstone.md).**
> Mục tiêu không phải thi, mà là **hiểu mô hình nhiều site đang chạy ngoài đời**.
>
> ⏱️ **15–20 giờ** *(chia 7 giai đoạn, mỗi giai đoạn dừng được)* · 💾 **RAM: ~2,5 GB** · 🧰 **5 router vIOS**

---

## ⚠️ PHẠM VI — đọc trước, để không hiểu nhầm

| Nội dung | Có trong blueprint ENCOR? |
|---|---|
| **GRE · IPsec** | ✅ **Có** — mục 2.2 |
| **VRF** | ✅ **Có** — mục 2.2 |
| **BGP** | ✅ **Có** — mục 3.2 |
| **QoS** | ✅ **Có** — Domain 1.0 |
| 🔴 **DMVPN · NHRP** | 🔴 **KHÔNG** — thuộc ENARSI / thực chiến |
| **SD-WAN** | ⚠️ Chỉ ở mức **"describe"** — không phải cấu hình |

> 🔴 **Nghĩa là: bạn KHÔNG cần lab này để thi ENCOR.**
> Nhưng bạn cần nó để **hiểu thứ mình sẽ gặp khi đi làm**, và để
> **SD-WAN thôi là từ khoá marketing** mà trở thành thứ bạn hình dung được.

---

## 📋 BỐI CẢNH

> Công ty **VLT** giờ có **3 site**: trụ sở (HQ) và hai chi nhánh.
> Ba site nối nhau **qua Internet** — không thuê MPLS vì đắt.
>
> Câu hỏi thiết kế: *"Làm sao để 3 site nói chuyện với nhau **an toàn**,
> mà **thêm site thứ 4 không phải đụng vào cấu hình của 3 site cũ**?"*

### Vì sao câu hỏi đó khó — bài toán N site

```
   Nối thủ công từng cặp (full-mesh):

    3 site  →  3 đường hầm
    5 site  →  10 đường
   10 site  →  45 đường
   50 site  →  🔴 1.225 đường     ← công thức N(N−1)/2

   🔴 Thêm 1 site = phải sửa cấu hình TẤT CẢ site cũ.
```

> 🔴 **Đây là bài toán mà DMVPN sinh ra để giải, và sau này SD-WAN giải lại theo cách khác.**
> Cả hai đều dựa trên cùng một ý tưởng: **có một chỗ TẬP TRUNG biết ai ở đâu**,
> còn dữ liệu thì **đi thẳng giữa các site**.

---

## 🗺️ SƠ ĐỒ

```
                        ┌────────────────────┐
                        │        NET         │  mô phỏng Internet
                        │   Lo0: 8.8.8.8/32  │
                        └──┬──────┬───────┬──┘
           203.0.113.0/30  │      │       │  192.0.2.0/30
                           │      │ 198.51.100.0/30
              ┌────────────┘      │       └────────────┐
              │                   │                    │
        ┌─────┴─────┐       ┌─────┴─────┐       ┌──────┴────┐
        │    HUB    │       │   SITE2   │       │   SITE3   │
        │   (HQ)    │       │           │       │           │
        │ Tun0 .1   │       │ Tun0 .2   │       │ Tun0 .3   │
        └─────┬─────┘       └─────┬─────┘       └─────┬─────┘
       LAN 10.1.0.0/16      10.2.0.0/16          10.3.0.0/16

        ═══════════ ĐƯỜNG HẦM ẢO 10.255.0.0/24 ═══════════
        (chồng lên Internet — "overlay" nằm trên "underlay")
```

### Bảng địa chỉ

| Thiết bị | Cổng | IP | Vai trò |
|---|---|---|---|
| **NET** | Lo0 | `8.8.8.8/32` | đích test Internet |
| | Gi0/0 | `203.0.113.2/30` | ← HUB |
| | Gi0/1 | `198.51.100.2/30` | ← SITE2 |
| | Gi0/2 | `192.0.2.2/30` | ← SITE3 |
| | Gi0/3 | `209.165.200.2/30` | ← HUB2 *(giai đoạn 6)* |
| **HUB** | Gi0/0 | `203.0.113.1/30` | mặt Internet |
| | Tunnel0 | `10.255.0.1/24` | mặt overlay |
| | Lo1 | `10.1.1.1/24` | 🔴 **giả lập LAN** *(tiết kiệm RAM)* |
| | Lo0 | `1.1.1.1/32` | Router-ID |
| **SITE2** | Gi0/0 | `198.51.100.1/30` | |
| | Tunnel0 | `10.255.0.2/24` | |
| | Lo1 | `10.2.1.1/24` | giả lập LAN |
| | Lo0 | `2.2.2.2/32` | |
| **SITE3** | Gi0/0 | `192.0.2.1/30` | |
| | Tunnel0 | `10.255.0.3/24` | |
| | Lo1 | `10.3.1.1/24` | giả lập LAN |
| | Lo0 | `3.3.3.3/32` | |

> 💡 **Vì sao dùng Loopback thay cho switch + PC:**
> Tiết kiệm RAM, và **bài này không học về LAN** — nó học về **đường giữa các site**.
> Muốn thật hơn thì cắm switch vào, nhưng để sau.
>
> 🔴 **Chừa RAM để làm gì:** với 2,5 GB bạn còn thừa rất nhiều —
> **hãy dùng phần thừa đó để thêm SITE4, SITE5** ở giai đoạn 8 và tự quan sát
> chuyện gì xảy ra khi mạng lớn dần. **Đó mới là phần nghiên cứu thật.**

---

# 🏗️ GIAI ĐOẠN 0 — Nền: ba site nhìn thấy Internet

> **Mục tiêu:** dựng "underlay" — tức là **mạng vật lý bên dưới**.
> ⏱️ ~45 phút

**NET** *(mô phỏng Internet — không cần định tuyến, tất cả đều là mạng nối trực tiếp)*:

```
hostname NET
!
interface Loopback0
 ip address 8.8.8.8 255.255.255.255
!
interface GigabitEthernet0/0
 ip address 203.0.113.2 255.255.255.252
 no shutdown
interface GigabitEthernet0/1
 ip address 198.51.100.2 255.255.255.252
 no shutdown
interface GigabitEthernet0/2
 ip address 192.0.2.2 255.255.255.252
 no shutdown
```

**HUB:**

```
hostname HUB
!
interface Loopback0
 ip address 1.1.1.1 255.255.255.255
interface Loopback1
 ip address 10.1.1.1 255.255.255.0      ! gia lap LAN cua HQ
!
interface GigabitEthernet0/0
 ip address 203.0.113.1 255.255.255.252
 no shutdown
!
ip route 0.0.0.0 0.0.0.0 203.0.113.2
```

**SITE2** *(SITE3 làm tương tự với `192.0.2.1`, `3.3.3.3`, `10.3.1.1`)*:

```
hostname SITE2
!
interface Loopback0
 ip address 2.2.2.2 255.255.255.255
interface Loopback1
 ip address 10.2.1.1 255.255.255.0
!
interface GigabitEthernet0/0
 ip address 198.51.100.1 255.255.255.252
 no shutdown
!
ip route 0.0.0.0 0.0.0.0 198.51.100.2
```

## 🔍 Quan sát giai đoạn 0

| Từ | Ping tới | Kết quả mong đợi |
|---|---|---|
| HUB | `8.8.8.8` | ✅ Thông |
| HUB | `198.51.100.1` *(IP công cộng SITE2)* | ✅ Thông |
| HUB | 🔴 `10.2.1.1` *(LAN của SITE2)* | 🔴 **PHẢI HỎNG** |

> 🔴 **Dòng thứ ba hỏng mới là ĐÚNG — và đó chính là lý do tồn tại của cả bài lab này.**
>
> Internet **biết đường tới IP công cộng** của bạn, nhưng **không biết gì về mạng nội bộ**
> `10.x.x.x` — và cũng không nên biết.
>
> **Việc còn lại của lab: xây một lớp mạng CHỒNG LÊN Internet** để các mạng `10.x` nói chuyện được
> với nhau, mà Internet vẫn không hề hay biết.
> ⭐ **Đó là ý nghĩa của hai từ "underlay" và "overlay"** — thứ bạn đã đọc ở
> [Module-08](Module-08-Virtualization-va-Overlay.md), giờ nhìn thấy bằng mắt.

---

# 🌐 GIAI ĐOẠN 1 — Dựng đường hầm DMVPN

> **Mục tiêu:** một đường hầm **đa điểm** — hub chỉ cấu hình **một lần**, thêm site không phải sửa hub.
> ⏱️ ~2 giờ

## 1.1 Ba mảnh ghép của DMVPN

| Mảnh | Làm gì | Ví von |
|---|---|---|
| **mGRE** *(multipoint GRE)* | 🔴 **MỘT interface tunnel nói chuyện được với NHIỀU đầu kia** | Một cái loa phát cho cả nhóm, thay vì N cái điện thoại |
| **NHRP** | 🔴 **Sổ danh bạ: "IP hầm 10.255.0.2 hiện đang ở IP công cộng 198.51.100.1"** | Tổng đài hỏi đáp số điện thoại |
| **IPsec** *(giai đoạn 4)* | Mã hoá nội dung | Phong bì niêm phong |

> 🔴 **Hiểu NHRP là hiểu DMVPN.**
> GRE thường bắt bạn khai cứng *"đầu kia ở đâu"* — nên **N site = N đường khai tay**.
> NHRP thay việc đó bằng: ⭐ **spoke tự ĐĂNG KÝ với hub khi khởi động**, và
> ⭐ **muốn tìm ai thì HỎI hub**.
>
> **Đó là lý do thêm site thứ 4 không phải đụng vào 3 site cũ** — site mới tự đăng ký.

## 1.2 Cấu hình HUB

```
interface Tunnel0
 ip address 10.255.0.1 255.255.255.0
 !
 ip mtu 1400                              ! xem muc 1.4 - RAT quan trong
 ip tcp adjust-mss 1360
 !
 ip nhrp network-id 100                   ! dinh danh dam may DMVPN
 ip nhrp authentication VLT2026
 ip nhrp map multicast dynamic            ! ← DONG THEN CHOT (xem duoi)
 !
 tunnel source GigabitEthernet0/0
 tunnel mode gre multipoint               ! ← mGRE: da diem
 tunnel key 100
```

> 🔴 **`ip nhrp map multicast dynamic` là dòng làm nên toàn bộ giá trị của DMVPN.**
>
> Nó nói với hub: ⭐ **"ai đăng ký với tôi thì tự động thêm vào danh sách nhận multicast"**.
> Không có dòng này, bạn phải **khai tay từng spoke trên hub** — và mất sạch ưu điểm mở rộng.
>
> ⭐ **Nhớ: hub KHÔNG có dòng `ip nhrp nhs` nào cả** — hub *chính là* NHS *(Next Hop Server)*.

## 1.3 Cấu hình SITE2 *(SITE3 giống hệt, chỉ đổi IP tunnel sang `.3`)*

```
interface Tunnel0
 ip address 10.255.0.2 255.255.255.0
 !
 ip mtu 1400
 ip tcp adjust-mss 1360
 !
 ip nhrp network-id 100
 ip nhrp authentication VLT2026
 !
 ip nhrp map 10.255.0.1 203.0.113.1        ! IP ham cua HUB -> IP cong cong cua HUB
 ip nhrp map multicast 203.0.113.1          ! gui multicast toi HUB
 ip nhrp nhs 10.255.0.1                     ! HUB la "tong dai" cua toi
 !
 tunnel source GigabitEthernet0/0
 tunnel mode gre multipoint
 tunnel key 100
```

> ⭐ **Ba dòng `ip nhrp map / map multicast / nhs` là thứ duy nhất spoke phải khai cứng**,
> và chúng **chỉ trỏ tới HUB**. 🔴 **Spoke KHÔNG hề biết gì về các spoke khác** — đó là cả vấn đề.
>
> 💡 **IOS mới gộp được thành một dòng:** `ip nhrp nhs 10.255.0.1 nbma 203.0.113.1 multicast`.
> ⭐ **Trên vIOS cũ thì dùng dạng ba dòng như trên cho chắc.**

## 1.4 🔴 MTU — chỗ làm hỏng lab nhiều nhất

```
   Gói gốc                              1500 byte
   + GRE header                         −24  →  1476
   + IPsec (giai đoạn 4)                −~50 →  ~1426
   ────────────────────────────────────────────────
   Đặt ip mtu 1400 để CHỪA CHỖ cho cả hai
```

> 🔴 **Triệu chứng nếu quên MTU — rất khó đoán:**
> ⭐ **`ping` bình thường CHẠY** *(gói nhỏ)*, tunnel `up`, `show dmvpn` đẹp —
> nhưng 🔴 **mở web thì treo, copy file thì đứng, SSH gõ vài chữ là đơ.**
>
> Vì sao: gói lớn bị phân mảnh hoặc rơi âm thầm, mà **ping không bao giờ phát hiện ra**.
>
> ⭐ **`ip tcp adjust-mss 1360`** bảo TCP **tự thoả thuận gói nhỏ hơn ngay từ đầu** —
> đây là cách chữa thật, không phải vá.
>
> 🔴 **Tự kiểm bằng ping gói lớn, không phân mảnh:**
> ```
> SITE2# ping 10.255.0.1 size 1400 df-bit
> ```

## 1.5 Kiểm chứng

```
HUB# show dmvpn
Interface: Tunnel0, IPv4 NHRP Details
Type:Hub, NHRP Peers:2,

 # Ent  Peer NBMA Addr   Peer Tunnel Add  State  UpDn Tm  Attrb
 ----- ---------------- ---------------- ------ -------- -----
     1   198.51.100.1      10.255.0.2       UP   00:05:12    D
     1     192.0.2.1       10.255.0.3       UP   00:04:48    D
                                                             ↑
                                        D = Dynamic: spoke TU dang ky ✅

HUB# show ip nhrp
10.255.0.2/32 via 10.255.0.2
   Tunnel0 created 00:05:12, expire 01:54:48
   Type: dynamic, Flags: unique registered used nhop
   NBMA address: 198.51.100.1
```

## 🔍 Quan sát giai đoạn 1 — làm bài này, đừng bỏ qua

| # | Việc | Ghi lại kết quả |
|:---:|---|---|
| 1 | Từ SITE2 ping `10.255.0.1` *(hub)* | Thông? |
| 2 | 🔴 Từ SITE2 ping `10.255.0.3` *(SITE3 qua hầm)* | 🔴 **Thông — nhưng đi đường nào?** |
| 3 | 🔴 `traceroute 10.255.0.3` từ SITE2 | 🔴 **Đếm số chặng** |
| 4 | Từ SITE2 ping `10.3.1.1` *(LAN của SITE3)* | 🔴 **PHẢI HỎNG — vì sao?** |

<details><summary>💡 Giải thích — mở sau khi đã tự quan sát</summary>

**Câu 3:** traceroute cho **2 chặng**: `SITE2 → HUB → SITE3`.
🔴 **Mọi traffic giữa hai spoke đều VÒNG QUA HUB.**

Vì sao: spoke chỉ có sổ danh bạ trỏ tới **hub**. Muốn gửi cho `10.255.0.3`,
nó không biết IP công cộng của SITE3 nên **đẩy hết cho hub xử lý**.

🔴 **Đây là điểm yếu của giai đoạn này** — hub thành nút cổ chai, và đường đi vòng vô lý:
nếu SITE2 ở Đà Nẵng, SITE3 ở Cần Thơ, HUB ở Hà Nội thì gói phải chạy ra Hà Nội rồi vòng về.
**Giai đoạn 3 sẽ sửa chuyện này.**

**Câu 4 hỏng là ĐÚNG:** đường hầm mới chỉ nối các **IP tunnel** `10.255.0.x`.
🔴 **Chưa ai nói cho SITE2 biết `10.3.1.0/24` nằm sau SITE3.**
Đó là việc của **định tuyến** — giai đoạn 2.
</details>

---

# 🧭 GIAI ĐOẠN 2 — Định tuyến trên overlay bằng iBGP

> **Mục tiêu:** để các site **học được mạng LAN của nhau**, và
> 🔴 **thêm site mới KHÔNG phải sửa cấu hình hub**.
> ⏱️ ~2 giờ

## 2.1 Vì sao chọn BGP chứ không phải OSPF

| | **OSPF trên DMVPN** | 🔴 **BGP trên DMVPN** |
|---|---|---|
| Thêm site mới | Phải cân nhắc area, network type | 🔴 **Hub tự nhận, không sửa gì** |
| Số site chịu được | Vài chục là bắt đầu nặng | 🔴 **Hàng nghìn** |
| Nhiễu khi một site chập chờn | 🔴 **Chạy lại SPF toàn vùng** | Chỉ ảnh hưởng tuyến đó |
| Điều khiển chính sách | Hạn chế | 🔴 **Rất mạnh** *(cộng đồng, route-map)* |

> 🔴 **Đây là lý do thật khiến mọi thiết kế nhiều site hiện nay đều dùng BGP** —
> và cũng là lý do **SD-WAN bên trong cũng là BGP** *(vSmart thực chất là một route-reflector)*.

## 2.2 HUB — làm route-reflector, và nhận neighbor ĐỘNG

```
router bgp 65000
 bgp router-id 1.1.1.1
 bgp log-neighbor-changes
 !
 ! ═══ DONG QUAN TRONG NHAT CUA CA GIAI DOAN 2 ═══
 bgp listen range 10.255.0.0/24 peer-group SPOKES
 !
 neighbor SPOKES peer-group
 neighbor SPOKES remote-as 65000
 !
 address-family ipv4
  network 10.1.1.0 mask 255.255.255.0
  neighbor SPOKES activate
  neighbor SPOKES route-reflector-client
 exit-address-family
```

> 🔴 **`bgp listen range` = "ai trong dải `10.255.0.0/24` gọi tới thì tôi nhận".**
>
> ⭐ **Nghĩa là: thêm SITE4, SITE5, SITE50 — hub KHÔNG phải sửa một dòng nào.**
> Đây chính là câu trả lời cho câu hỏi thiết kế ở đầu bài.
>
> ⚠️ **Nếu vIOS của bạn không nhận lệnh này** *(bản quá cũ)*, dùng cách khai tay:
> ```
> neighbor 10.255.0.2 remote-as 65000
> neighbor 10.255.0.2 peer-group SPOKES
> neighbor 10.255.0.3 remote-as 65000
> neighbor 10.255.0.3 peer-group SPOKES
> ```
> ⭐ **Rồi tự cảm nhận sự khác biệt** khi phải thêm site thứ 4 — đó cũng là một bài học.

## 2.3 SITE2 *(SITE3 tương tự)*

```
router bgp 65000
 bgp router-id 2.2.2.2
 neighbor 10.255.0.1 remote-as 65000
 !
 address-family ipv4
  network 10.2.1.0 mask 255.255.255.0
  neighbor 10.255.0.1 activate
 exit-address-family
```

## 2.4 🔴 Chỗ ngược đời so với Capstone — đọc kỹ

> Ở [LAB Capstone Task 6](Module-13-LAB-Capstone.md), tôi nhấn mạnh rằng
> 🔴 **iBGP BẮT BUỘC phải có `next-hop-self`**, thiếu là tuyến không dùng được.
>
> 🔴 **Ở đây thì NGƯỢC LẠI: TUYỆT ĐỐI KHÔNG đặt `next-hop-self` trên hub.**

| | Capstone | Lab này |
|---|---|---|
| Next-hop gốc là gì | 🔴 **IP của ISP** — nằm ngoài AS | 🔴 **IP tunnel của spoke kia** — `10.255.0.x` |
| iBGP peer có tới được không | 🔴 **KHÔNG** → phải `next-hop-self` | ✅ **CÓ** — cùng subnet tunnel `10.255.0.0/24` |
| Nếu đặt `next-hop-self` | Đúng | 🔴 **SAI — giết chết đường spoke-to-spoke ở giai đoạn 3** |

> ⭐ **Bài học thật sự ở đây không phải "nhớ lệnh nào" mà là:**
> 🔴 **`next-hop-self` cần khi và chỉ khi peer KHÔNG tự tới được next-hop gốc.**
>
> ⭐ Học thuộc *"iBGP thì luôn next-hop-self"* là học sai — và lab này chứng minh điều đó.
> **Phải hiểu LÝ DO, không phải nhớ QUY TẮC.**

## 2.5 Kiểm chứng

```
HUB# show ip bgp summary
Neighbor      V    AS  MsgRcvd MsgSent  Up/Down  State/PfxRcd
*10.255.0.2   4 65000     142     145   02:05:11        1
*10.255.0.3   4 65000     139     141   02:03:47        1
↑
dau * = neighbor DONG, sinh ra tu "bgp listen range" ✅

SITE2# show ip bgp
   Network          Next Hop         Metric LocPrf Weight Path
 *>i 10.1.1.0/24    10.255.0.1            0    100      0 i
 *>  10.2.1.0/24    0.0.0.0               0         32768 i
 *>i 10.3.1.0/24    10.255.0.3            0    100      0 i
                                          ↑
              next-hop GIU NGUYEN la SITE3, khong bi hub doi thanh 10.255.0.1 ✅
```

## 🔍 Quan sát giai đoạn 2

| # | Việc | Ghi lại |
|:---:|---|---|
| 1 | Từ SITE2 ping `10.3.1.1` *(LAN SITE3)* | ✅ Giờ đã thông |
| 2 | 🔴 `traceroute 10.3.1.1` từ SITE2 | 🔴 **Vẫn mấy chặng?** |
| 3 | Trên SITE2: `show ip route 10.3.1.0` | Next-hop là gì? |
| 4 | Trên HUB: `show ip nhrp` | Có bản ghi nào cho SITE2↔SITE3 không? |

<details><summary>💡 Giải thích</summary>

**Câu 2:** vẫn **2 chặng** — `SITE2 → HUB → SITE3`.

Bảng định tuyến đã đúng: SITE2 biết `10.3.1.0/24` có next-hop là `10.255.0.3`.
Nhưng khi gửi gói, nó tra NHRP hỏi *"`10.255.0.3` đang ở IP công cộng nào?"* —
🔴 **NHRP không có câu trả lời**, nên gói bị đẩy cho hub *(đầu duy nhất nó biết)*.

**Câu 4:** trên hub **không có** bản ghi nào cho cặp SITE2↔SITE3 — hai spoke vẫn chưa biết nhau.

🔴 **Vậy là: định tuyến đã đúng, nhưng đường đi vẫn vòng.**
⭐ **Đây là lúc bạn thấy rõ "bảng định tuyến đúng" và "gói đi đúng đường" là HAI chuyện khác nhau.**
Giai đoạn 3 sẽ nối nốt phần còn thiếu.
</details>

---

# ⚡ GIAI ĐOẠN 3 — Cho hai site nói chuyện TRỰC TIẾP

> **Mục tiêu:** bỏ đường vòng qua hub. ⏱️ ~1,5 giờ
>
> 🔴 **Giai đoạn này chỉ thêm ĐÚNG 2 DÒNG** — nhưng nó đổi hẳn hành vi của cả hệ thống.
> **Đây là phần đáng nghiên cứu nhất của bài lab.**

## 3.1 Hai dòng đó

**Trên HUB:**

```
interface Tunnel0
 ip nhrp redirect
```

**Trên MỌI SPOKE:**

```
interface Tunnel0
 ip nhrp shortcut
```

## 3.2 Cơ chế — chuyện gì xảy ra bên trong

```
 ① Gói ĐẦU TIÊN từ SITE2 tới LAN của SITE3 vẫn đi vòng qua hub
    SITE2 ──────────▶ HUB ──────────▶ SITE3

 ② HUB nhận ra điều bất thường: "gói này VÀO Tunnel0 rồi lại RA Tunnel0"
    → nghĩa là hai đầu đều nằm trong cùng đám mây DMVPN, đi vòng qua tôi là phí
    → HUB gửi ngược lại SITE2 một bản tin NHRP REDIRECT
       "anh đi sai đường rồi, hỏi thẳng nó đi"

 ③ SITE2 gửi NHRP RESOLUTION REQUEST (vẫn qua hub) hỏi SITE3
    "LAN 10.3.1.0/24 thì IP công cộng của anh là gì?"

 ④ SITE3 trả lời TRỰC TIẾP cho SITE2: "IP công cộng của tôi là 192.0.2.1"

 ⑤ SITE2 ghi vào sổ NHRP + cài một tuyến tắt (shortcut)

 ⑥ Từ gói THỨ HAI trở đi:
    SITE2 ══════════════════════════▶ SITE3      ĐI THẲNG ✅
           (đường hầm động, tự dựng, tự hết hạn)
```

> ⭐ **Điểm tinh tế đáng để ý:**  **đường hầm spoke-to-spoke KHÔNG tồn tại sẵn.**
> Nó **tự sinh ra khi có nhu cầu**, và **tự biến mất khi hết hạn** *(mặc định khoảng 2 tiếng)*.
>
> 🔴 **Đó là lý do mô hình này mở rộng được tới hàng nghìn site:**
> mỗi site chỉ giữ đường hầm tới **những site nó thật sự đang nói chuyện**,
> chứ không phải tới **tất cả**.

## 3.3 🔍 Quan sát — làm CHẬM và kỹ, đây là phần quan trọng nhất

**Bước 1 — xoá sạch để quan sát từ đầu:**

```
SITE2# clear ip nhrp
SITE2# show ip nhrp          ← phai rong (chi con ban ghi toi hub)
```

**Bước 2 — traceroute LẦN ĐẦU:**

```
SITE2# traceroute 10.3.1.1
  1  10.255.0.1  ...      ← qua HUB
  2  10.255.0.3  ...      ← roi moi toi SITE3
```

**Bước 3 — ping một lúc cho NHRP kịp làm việc:**

```
SITE2# ping 10.3.1.1 repeat 20
```

**Bước 4 — 🔴 traceroute LẠI:**

```
SITE2# traceroute 10.3.1.1
  1  10.255.0.3  ...      ← 🔴 ĐI THẲNG! Hub biến mất khỏi đường đi ✅
```

**Bước 5 — xem sổ NHRP đã có gì mới:**

```
SITE2# show ip nhrp
10.3.1.0/24 via 10.255.0.3
   Tunnel0 created 00:00:412, expire 01:59:48
   Type: dynamic, Flags: router rib nho
   NBMA address: 192.0.2.1            ← IP cong cong cua SITE3, tu hoc duoc ✅

SITE2# show dmvpn
 # Ent  Peer NBMA Addr   Peer Tunnel Add  State  UpDn Tm  Attrb
 ----- ---------------- ---------------- ------ -------- -----
     1     203.0.113.1      10.255.0.1       UP   02:10:33     S    ← hub (tinh)
     1       192.0.2.1      10.255.0.3       UP   00:00:41     D    ← SITE3 (dong!) ✅
```

**Bước 6 — kiểm tra tuyến tắt trong bảng định tuyến:**

```
SITE2# show ip route 10.3.1.0
Routing entry for 10.3.1.0/24
  Known via "nhrp", distance 250, metric 1
                        ↑
            tuyen do NHRP cai vao - AD 250, chi dung khi co nhu cau
```

## 3.4 Câu hỏi tự trả lời

> ⭐ **Trả lời được 5 câu này nghĩa là bạn đã thật sự hiểu DMVPN Phase 3:**

| # | Câu hỏi |
|:---:|---|
| 1 | Vì sao gói **đầu tiên** vẫn phải đi qua hub? Có cách nào tránh không? |
| 2 | Nếu **hub chết** sau khi đường spoke-to-spoke đã dựng — SITE2 còn nói chuyện với SITE3 được không? |
| 3 | Tuyến NHRP có **AD 250**. Vì sao chọn số cao như vậy mà không phải số thấp? |
| 4 | Nếu **50 site** cùng nói chuyện với nhau thì SITE2 giữ bao nhiêu đường hầm? |
| 5 | Vì sao hub **được phép tóm tắt tuyến** ở Phase 3, mà ở Phase 2 thì không? |

<details><summary>💡 Đáp án</summary>

**1.** Vì NHRP **chỉ học theo nhu cầu** — chưa có ai hỏi thì chưa có câu trả lời.
Không tránh được, và **cũng không nên tránh**: nếu dựng sẵn đường hầm tới mọi site thì
bạn quay về đúng bài toán full-mesh N(N−1)/2 ở đầu bài.
⭐ **Cái giá phải trả là một gói đi vòng — quá rẻ.**

**2.** 🔴 **CÓ, vẫn nói chuyện được** trong thời gian đường hầm còn hạn.
Nhưng khi hết hạn *(~2 tiếng)* mà hub vẫn chết thì **không dựng lại được** —
vì không còn ai làm tổng đài. 🔴 **Đó chính là lý do giai đoạn 6 phải có hub thứ hai.**

**3.** AD 250 rất cao nên tuyến NHRP **chỉ thắng khi không có tuyến nào khác**,
và **không bao giờ đè lên** tuyến học từ BGP/OSPF.
⭐ Nó là **đường tắt bổ sung**, không phải nguồn định tuyến chính — thiết kế rất có chủ ý.

**4.** 🔴 **Chỉ giữ đường hầm tới những site nó ĐANG nói chuyện**, không phải 49.
Thực tế phần lớn site chỉ nói chuyện với vài site + hub.
⭐ **Đây là điểm mấu chốt giúp mô hình mở rộng được.**

**5.** Ở **Phase 2**, spoke phải **tự biết next-hop gốc** để dựng đường trực tiếp →
🔴 **hub tóm tắt tuyến là làm mất thông tin đó** → hỏng spoke-to-spoke.
Ở **Phase 3**, spoke **không cần biết trước** — nó được hub **chỉ đường bằng Redirect** khi cần.
⭐ **Nên hub tóm tắt thoải mái**, và bảng định tuyến ở spoke gọn hơn hẳn.
🔴 **Đây chính là lý do Phase 3 thay thế Phase 2 trong mọi thiết kế mới.**
</details>

---

# 🔐 GIAI ĐOẠN 4 — Bọc IPsec

> **Mục tiêu:** đường hầm đang chạy **trần trên Internet** — ai chặn được là đọc được.
> ⏱️ ~2 giờ

## 4.1 Cấu hình — dùng IKEv2 *(chuẩn hiện nay)*

**Giống nhau trên CẢ BA thiết bị:**

```
crypto ikev2 proposal PROP-VLT
 encryption aes-cbc-256
 integrity sha256
 group 14
!
crypto ikev2 policy POL-VLT
 proposal PROP-VLT
!
crypto ikev2 keyring KR-VLT
 peer BAT-KY
  address 0.0.0.0 0.0.0.0
  pre-shared-key KhoaChungRatDaiCuaVLT2026
!
crypto ikev2 profile PROF-VLT
 match identity remote address 0.0.0.0
 authentication local  pre-share
 authentication remote pre-share
 keyring local KR-VLT
!
crypto ipsec transform-set TS-VLT esp-aes 256 esp-sha256-hmac
 mode transport                      ! ← KHONG phai tunnel. Xem 4.2
!
crypto ipsec profile IPSEC-DMVPN
 set transform-set TS-VLT
 set ikev2-profile PROF-VLT
!
interface Tunnel0
 tunnel protection ipsec profile IPSEC-DMVPN shared
```

> ⚠️ **Nếu vIOS của bạn không nhận lệnh `crypto ikev2`** *(bản cũ)*, dùng IKEv1:
> ```
> crypto isakmp policy 10
>  encryption aes 256
>  hash sha256
>  authentication pre-share
>  group 14
> crypto isakmp key KhoaChungRatDaiCuaVLT2026 address 0.0.0.0
> !
> crypto ipsec transform-set TS-VLT esp-aes 256 esp-sha256-hmac
>  mode transport
> crypto ipsec profile IPSEC-DMVPN
>  set transform-set TS-VLT
> ```
> ⭐ **Ngoài đời hiện nay dùng IKEv2** — nhanh hơn, chống tấn công tốt hơn, hỗ trợ NAT tốt hơn.

## 4.2 🔴 Ba chi tiết đáng nhớ

| Chi tiết | Vì sao |
|---|---|
| 🔴 **`mode transport`** *(không phải `tunnel`)* | GRE **đã có sẵn** header IP ngoài. Dùng `tunnel mode` là **thêm một header IP thừa → tốn 20 byte vô ích** |
| 🔴 **`address 0.0.0.0 0.0.0.0`** | Hub **không biết trước** spoke sẽ đến từ IP nào *(nhiều spoke dùng IP động)* → phải nhận **mọi nguồn**, và dựa vào **khoá chung** để xác thực |
| 🔴 **Từ khoá `shared`** | Cần khi **nhiều tunnel dùng CHUNG một `tunnel source`** — giai đoạn 5 sẽ có 2 tunnel. Thiếu nó thì tunnel thứ hai **không lên** |

## 4.3 Kiểm chứng

```
SITE2# show crypto ikev2 sa
 Tunnel-id  Local            Remote           fvrf/ivrf   Status
 1          198.51.100.1/500 203.0.113.1/500  none/none   READY

SITE2# show crypto ipsec sa | include encaps|decaps
    #pkts encaps: 1284, #pkts encrypt: 1284       ← dang ma hoa ✅
    #pkts decaps: 1277, #pkts decrypt: 1277

SITE2# show dmvpn detail | include Crypto
 Crypto Session Status: UP-ACTIVE
```

## 🔍 Quan sát giai đoạn 4

| # | Việc | Ghi lại |
|:---:|---|---|
| 1 | Ping SITE3 rồi xem `#pkts encrypt` có tăng không | Tăng? |
| 2 | 🔴 Đường **spoke-to-spoke** có được mã hoá không, hay chỉ đường tới hub? | |
| 3 | 🔴 Ping `size 1400 df-bit` — còn chạy không? | **Thử lại!** |

<details><summary>💡 Giải thích</summary>

**Câu 2:** 🔴 **CÓ — được mã hoá tự động.**
Vì `tunnel protection` áp lên **interface Tunnel0**, mà mọi đường hầm động
*(kể cả spoke-to-spoke)* đều **sinh ra từ chính interface đó**.
⭐ **Bạn không phải cấu hình gì thêm cho từng cặp site** — đây là một trong những
điểm mạnh lớn nhất của DMVPN.

**Câu 3:** 🔴 **Đây là lý do tôi bắt bạn thử lại.**
IPsec vừa **ăn thêm ~50–60 byte nữa**. Nếu ở giai đoạn 1 bạn để `ip mtu 1476`
thay vì `1400`, thì **bây giờ mới hỏng** — và triệu chứng vẫn là
*"ping nhỏ chạy, tải file thì treo"*.

⭐ **Bài học: MTU phải tính cho TOÀN BỘ chồng giao thức ngay từ đầu**,
đừng tính từng lớp rồi vá dần.
</details>

---

# 🧱 GIAI ĐOẠN 5 — Tách vùng bằng VRF: hai đám mây trên một hạ tầng

> **Mục tiêu:** cùng 3 site, cùng một đường Internet, nhưng **hai luồng hoàn toàn không thấy nhau**.
> ⏱️ ~2,5 giờ
>
> ⭐ **Đây là phần nối thẳng với mô hình phân vùng của ngân hàng/doanh nghiệp lớn.**

## 5.1 Bài toán thật

> *"Camera an ninh ở 3 chi nhánh cần về trung tâm. Nhưng 🔴 **tuyệt đối không được
> chung mạng với hệ thống nghiệp vụ** — camera Trung Quốc giá rẻ là rủi ro bảo mật.
> Tôi **không muốn thuê thêm đường truyền thứ hai**."*

**Lời giải:** ⭐ **hai đám mây DMVPN độc lập, chạy trên cùng một sợi cáp,
đặt trong hai VRF khác nhau.**

```
                      MỘT đường Internet duy nhất
                               │
              ┌────────────────┴────────────────┐
              │                                 │
    ═══ Tunnel0 · VRF NGHIEP-VU ═══   ═══ Tunnel1 · VRF CAMERA ═══
        network-id 100                     network-id 200
        tunnel key 100                     tunnel key 200
        10.255.0.0/24                      10.254.0.0/24
              │                                 │
    🔴 HAI BẢNG ĐỊNH TUYẾN RIÊNG — không có đường nào đi giữa hai bên
```

## 5.2 Cấu hình *(trên cả HUB và các SPOKE)*

```
vrf definition NGHIEP-VU
 rd 65000:1
 address-family ipv4
 exit-address-family
!
vrf definition CAMERA
 rd 65000:2
 address-family ipv4
 exit-address-family
!
! ═══ Dam may thu hai - CHO CAMERA ═══
interface Tunnel1
 vrf forwarding CAMERA                    ! ← tunnel nam TRONG vrf CAMERA
 ip address 10.254.0.1 255.255.255.0      ! (spoke dung .2 / .3)
 ip mtu 1400
 ip tcp adjust-mss 1360
 !
 ip nhrp network-id 200                   ! KHAC 100 cua dam may kia
 ip nhrp authentication VLTCam2026
 ip nhrp map multicast dynamic            ! (tren HUB)
 ip nhrp redirect                         ! (tren HUB)
 !
 tunnel source GigabitEthernet0/0         ! CHUNG cong vat ly voi Tunnel0
 tunnel mode gre multipoint
 tunnel key 200                           ! ← 🔴 PHAI khac tunnel key cua Tunnel0
 tunnel protection ipsec profile IPSEC-DMVPN shared
!
! LAN camera, dat trong VRF
interface Loopback2
 vrf forwarding CAMERA
 ip address 10.1.2.1 255.255.255.0
```

> 🔴 **Ba thứ BẮT BUỘC phải khác nhau giữa hai đám mây:**
> ⭐ **`ip nhrp network-id`** ·  **`tunnel key`** ·  **dải IP tunnel**.
>
> 🔴 **Đặc biệt `tunnel key`:** hai tunnel dùng **chung một `tunnel source`**,
> nên thiết bị **phân biệt gói của tunnel nào bằng chính khoá này**.
> Trùng khoá → **gói đi nhầm đám mây** hoặc tunnel thứ hai **không lên**.
>
> 🔴 **Và nhớ từ khoá `shared`** ở `tunnel protection` — thiếu nó, hai tunnel
> cùng `tunnel source` sẽ **tranh nhau phiên IPsec** và cái thứ hai không lên.

## 5.3 BGP cho VRF

```
router bgp 65000
 !
 address-family ipv4 vrf CAMERA
  network 10.1.2.0 mask 255.255.255.0
  neighbor 10.254.0.2 remote-as 65000
  neighbor 10.254.0.2 activate
  neighbor 10.254.0.2 route-reflector-client
  neighbor 10.254.0.3 remote-as 65000
  neighbor 10.254.0.3 activate
  neighbor 10.254.0.3 route-reflector-client
 exit-address-family
```

> ⚠️ **Lưu ý thực tế:** `bgp listen range` *(neighbor động)* **có thể không dùng được
> trong `address-family vrf` trên vIOS cũ.** Nếu vậy thì khai tay như trên —
> ⭐ và bạn sẽ **tự cảm nhận** vì sao ngoài đời người ta chuyển sang **MPLS L3VPN over DMVPN**
> khi số VRF và số site cùng tăng.

## 🔍 Quan sát giai đoạn 5

| # | Việc | Kết quả mong đợi |
|:---:|---|---|
| 1 | `ping vrf CAMERA 10.3.2.1` từ SITE2 | ✅ Thông |
| 2 | 🔴 `ping 10.3.2.1` **không khai vrf** | 🔴 **PHẢI HỎNG** |
| 3 | `show ip route vrf CAMERA` so với `show ip route vrf NGHIEP-VU` | 🔴 **Hai bảng khác hẳn nhau** |
| 4 | `show dmvpn` | **Hai đám mây, hai danh sách peer riêng** |

> 🔴 **Câu 2 hỏng mới là ĐÚNG** — và đây chính là thứ bạn đã học ở
> [Module-08](Module-08-Virtualization-va-Overlay.md): **không khai `vrf` thì lệnh dùng bảng global.**
>
> ⭐ **Giờ bạn đã tự tay dựng được thứ mà ngân hàng gọi là "phân vùng":**
> hai hệ thống dùng chung hạ tầng vật lý nhưng **không có đường nào đi giữa chúng** —
> trừ khi bạn **cố ý** mở một cửa *(và cửa đó ngoài đời sẽ là firewall)*.

---

# 🏰 GIAI ĐOẠN 6 — Hub thứ hai: xoá điểm chết đơn lẻ

> **Mục tiêu:** trả lời câu hỏi 2 ở giai đoạn 3 — *"hub chết thì sao?"*
> ⏱️ ~2 giờ · **Thêm node HUB2** *(+512 MB)*

## 6.1 Vì sao bắt buộc phải có

> 🔴 **Hub là tổng đài. Tổng đài chết thì:**
> - Đường hầm **đang chạy** vẫn sống tới khi hết hạn *(~2 tiếng)*
> - 🔴 **Nhưng không site mới nào đăng ký được, và đường hầm hết hạn không dựng lại được**
> - 🔴 **Sau ~2 tiếng: toàn bộ mạng nhiều site SẬP**
>
> ⭐ **Một hub = một điểm chết đơn lẻ.** Không thiết kế thật nào chấp nhận điều này.

## 6.2 Cấu hình HUB2

```
hostname HUB2
!
interface Loopback0
 ip address 4.4.4.4 255.255.255.255
interface GigabitEthernet0/0
 ip address 209.165.200.1 255.255.255.252
 no shutdown
ip route 0.0.0.0 0.0.0.0 209.165.200.2
!
! ═══ CUNG dam may voi HUB1: cung network-id, cung tunnel key, cung subnet ═══
interface Tunnel0
 ip address 10.255.0.11 255.255.255.0
 ip mtu 1400
 ip tcp adjust-mss 1360
 ip nhrp network-id 100                   ! GIONG HUB1
 ip nhrp authentication VLT2026
 ip nhrp map multicast dynamic
 ip nhrp redirect
 tunnel source GigabitEthernet0/0
 tunnel mode gre multipoint
 tunnel key 100                           ! GIONG HUB1
 tunnel protection ipsec profile IPSEC-DMVPN shared
!
router bgp 65000
 bgp router-id 4.4.4.4
 bgp listen range 10.255.0.0/24 peer-group SPOKES
 neighbor SPOKES peer-group
 neighbor SPOKES remote-as 65000
 address-family ipv4
  neighbor SPOKES activate
  neighbor SPOKES route-reflector-client
 exit-address-family
```

## 6.3 Thêm vào MỌI SPOKE

```
interface Tunnel0
 ip nhrp map 10.255.0.11 209.165.200.1     ! tong dai thu hai
 ip nhrp map multicast 209.165.200.1
 ip nhrp nhs 10.255.0.11
!
router bgp 65000
 neighbor 10.255.0.11 remote-as 65000
 address-family ipv4
  neighbor 10.255.0.11 activate
  neighbor 10.255.0.1  route-map UU-TIEN-HUB1 in
 exit-address-family
!
route-map UU-TIEN-HUB1 permit 10
 set local-preference 200
```

> ⭐ **Spoke giờ đăng ký với CẢ HAI hub cùng lúc** *(không phải chờ cái này chết mới sang cái kia)*.
> 🔴 **Local Preference 200 làm HUB1 thắng khi cả hai còn sống** — đúng thứ bạn đã dùng ở
> [Capstone Task 6](Module-13-LAB-Capstone.md), nhưng lần này dùng cho mục đích khác.

## 🔍 Quan sát giai đoạn 6

| # | Việc | Kết quả |
|:---:|---|---|
| 1 | `show dmvpn` trên SITE2 | Thấy **2 hub**, cả hai `UP` |
| 2 | `show ip bgp 10.3.1.0` trên SITE2 | Nhận **2 đường**, HUB1 thắng nhờ LocPrf 200 |
| 3 | 🔴 **Tắt HUB1**, ping liên tục SITE2→SITE3 | 🔴 **Mất mấy gói?** |
| 4 | 🔴 Sau khi HUB1 chết, `clear ip nhrp` rồi thử dựng lại đường spoke-to-spoke | 🔴 **Còn dựng được không?** |

<details><summary>💡 Giải thích</summary>

**Câu 3:** mất một ít gói trong lúc BGP hội tụ *(vài chục giây với timer mặc định)*.
⭐ Muốn nhanh hơn: chỉnh timer BGP hoặc dùng **BFD** — hướng nghiên cứu thêm ở §8.

**Câu 4:** 🔴 **CÓ — và đây là điểm quan trọng nhất giai đoạn 6.**
HUB2 cũng có `ip nhrp redirect` nên nó **làm tổng đài thay HUB1** được ngay.
⭐ **So sánh với giai đoạn 3 câu 2:** lúc đó chỉ có 1 hub, hub chết là sau 2 tiếng mạng sập.
**Giờ thì không.**
</details>

---

# 📊 GIAI ĐOẠN 7 — QoS: hub đừng "dìm chết" chi nhánh nhỏ

> **Mục tiêu:** hub có đường 1 Gbps, chi nhánh chỉ có 10 Mbps.
> 🔴 **Hub gửi hết công suất là chi nhánh nghẹn.** ⏱️ ~1,5 giờ

## 7.1 Bài toán "per-tunnel QoS"

```
   HUB (1 Gbps)  ────────▶  SITE2 (10 Mbps)     🔴 nghen o phia SITE2
                 ────────▶  SITE3 (100 Mbps)

   🔴 Shaping o interface vat ly cua HUB KHONG giai quyet duoc:
      no bop CHUNG ca hai site, trong khi van de chi o site nho.
   ⭐ Can bop RIENG cho TUNG dam ham -> "per-tunnel QoS".
```

## 7.2 Cấu hình trên HUB

```
class-map match-all CM-THOAI
 match dscp ef
!
policy-map PM-BEN-TRONG
 class CM-THOAI
  priority percent 30                  ! thoai duoc uu tien tuyet doi
 class class-default
  fair-queue
!
policy-map PM-BOP-10M
 class class-default
  shape average 10000000               ! bop xuong 10 Mbps
  service-policy PM-BEN-TRONG          ! roi phan chia BEN TRONG 10M do
!
interface Tunnel0
 ip nhrp map group NHOM-10M service-policy output PM-BOP-10M
```

## 7.3 Trên SPOKE nhỏ *(SITE2)*

```
interface Tunnel0
 ip nhrp group NHOM-10M        ! "toi thuoc nhom 10 Mbps"
```

> ⭐ **Cơ chế rất gọn:** spoke **tự khai mình thuộc nhóm nào** khi đăng ký với hub,
> và hub **tự động áp đúng chính sách** cho đường hầm tới spoke đó.
>
> 🔴 **Thêm site mới chỉ cần khai một dòng `ip nhrp group` ở site đó** —
> **hub không phải sửa gì.** Lại đúng nguyên tắc xuyên suốt cả bài lab này.

**Kiểm chứng:**

```
HUB# show dmvpn detail | include Group|QoS
   NHRP group: NHOM-10M
   Output QoS service-policy applied: PM-BOP-10M

HUB# show policy-map multipoint
```

---

# 🚀 8. TỪ DMVPN SANG SD-WAN — cái bạn vừa làm ánh xạ sang đâu

> ⭐ **Đây là phần trả lời câu hỏi "mô hình hiện nay".**
> 🔴 **SD-WAN không phát minh ra ý tưởng mới — nó TỰ ĐỘNG HOÁ đúng những gì bạn vừa làm tay.**

| Thứ bạn vừa dựng | Trong SD-WAN (Cisco Viptela) gọi là |
|---|---|
| **HUB làm NHS** *(tổng đài biết ai ở đâu)* | 🔴 **vSmart** — controller, thực chất là **route-reflector** |
| **NHRP** *(đăng ký + hỏi đáp vị trí)* | 🔴 **OMP** — Overlay Management Protocol |
| **Khai tay `ip nhrp map` trên spoke** | 🔴 **vBond** — thiết bị mới **tự tìm về**, không khai gì |
| **Khoá chung `pre-shared-key`** | 🔴 **Chứng thư số** — mỗi thiết bị một danh tính riêng |
| **BGP chọn đường** | 🔴 **App-aware routing** — đo **jitter/mất gói/trễ THẬT** rồi mới chọn |
| **`ip nhrp group` + service-policy** | **Chính sách QoS tập trung trên vManage** |
| **SSH vào từng router gõ CLI** | 🔴 **Template tập trung** — sửa một chỗ, đẩy xuống hàng trăm site |

## 8.1 Ba thứ SD-WAN làm được mà DMVPN không

| | Vì sao quan trọng |
|---|---|
| 🔴 **Đo chất lượng đường theo thời gian thực** | DMVPN chọn đường bằng **BGP — chỉ biết "có/không"**. SD-WAN biết *"đường này đang mất 2% gói, jitter 40 ms"* và **tự chuyển thoại sang đường khác** trong khi vẫn để web đi đường cũ |
| 🔴 **Nhiều đường WAN cùng lúc, chính sách theo ỨNG DỤNG** | MPLS + Internet + 4G chạy song song: thoại đi MPLS, backup đi Internet, dự phòng 4G — **tự động** |
| 🔴 **Zero-touch** | Cắm điện router ở chi nhánh mới, nó **tự gọi về và tự nhận cấu hình**. Không cần kỹ sư đến nơi |

> ⭐ **Nhưng đây là điều đáng nói nhất:**
> 🔴 **Bên dưới lớp giao diện đẹp đẽ của SD-WAN vẫn là IPsec, vẫn là BGP,
> vẫn là bài toán overlay-trên-underlay, vẫn là MTU, vẫn là chọn đường.**
>
> ⭐ **Người đã tự tay dựng DMVPN sẽ gỡ lỗi SD-WAN nhanh hơn hẳn người chỉ biết bấm nút vManage** —
> vì khi có sự cố, thứ hỏng thường nằm ở đúng những lớp bên dưới đó.

---

# 🔬 9. HƯỚNG NGHIÊN CỨU TIẾP — bạn còn thừa RAM

> Lab này mới dùng ~3 GB. ⭐ **Bạn còn khoảng 7 GB để nghịch.** Vài hướng đáng thử:

| # | Hướng | Học được gì |
|:---:|---|---|
| 1 | 🔴 **Thêm SITE4, SITE5, SITE6** | Quan sát `show ip nhrp` phình ra thế nào · hub có phải sửa gì không · **tự chứng minh tính mở rộng** |
| 2 | **Bật BFD trên BGP** | Hội tụ từ *hàng chục giây* xuống **dưới 1 giây** — thứ ngoài đời luôn bật |
| 3 | 🔴 **FVRF (front-door VRF)** | Đặt **đường transport vào một VRF riêng** → spoke có **2 nhà mạng**, mỗi đường một VRF. Đây là nền của SD-WAN đa đường |
| 4 | **Dual-cloud DMVPN** | Hai tunnel qua **hai đường WAN khác nhau** *(Internet + MPLS)*, dùng BGP chọn đường |
| 5 | **Spoke nằm sau NAT** | Thêm NAT giữa spoke và Internet — xem NHRP xoay xở thế nào *(rất thật: chi nhánh dùng cáp quang dân dụng)* |
| 6 | **So sánh với MPLS L3VPN** | Dựng PE-P-PE với MP-BGP/VPNv4 — hiểu vì sao doanh nghiệp bỏ MPLS sang Internet |
| 7 | 🔴 **Tự động hoá bằng Ansible** | **Viết playbook sinh cấu hình spoke từ template.** Thêm site = sửa 1 dòng inventory → [Module-12 §11](Module-12-Automation-va-Programmability.md) |
| 8 | **EEM tự cảnh báo khi tunnel rớt** | Applet bắt `%NHRP` hoặc `%DMVPN` → [Module-12 §8](Module-12-Automation-va-Programmability.md) |

> 🔴 **Hướng số 7 là hướng hợp với bạn nhất.**
> ⭐ Với nền DevOps/IaC, bạn sẽ thấy ngay: **cấu hình spoke là một template lặp lại
> chỉ khác vài biến** *(IP tunnel, IP public, dải LAN)*.
> ⭐ **Đó chính xác là bài toán Ansible sinh ra để giải** — và cũng chính là
> **thứ SD-WAN bán cho bạn dưới dạng sản phẩm.**

---

# ✅ 10. TỰ CHẤM

| ☐ | Bạn làm được gì |
|:---:|---|
| ☐ | Giải thích được **overlay khác underlay** thế nào bằng lời của mình |
| ☐ | Nói được **NHRP giải bài toán gì** — và vì sao nó khiến "thêm site" trở nên rẻ |
| ☐ | 🔴 **Tự tay thấy traceroute đổi từ 2 chặng xuống 1 chặng** sau khi bật shortcut |
| ☐ | Giải thích được **vì sao lab này KHÔNG dùng `next-hop-self`** mà Capstone thì phải dùng |
| ☐ | 🔴 **Ping `size 1400 df-bit` chạy được** sau khi đã bật IPsec |
| ☐ | Dựng được **hai VRF không thấy nhau** trên cùng một đường truyền |
| ☐ | Tắt HUB1 mà mạng vẫn sống, và **dựng lại được** đường spoke-to-spoke |
| ☐ | 🔴 **Ánh xạ được 5 thành phần DMVPN sang 5 thành phần SD-WAN** *(§8)* |

## 🎯 Ba điều đáng mang theo

> 🔴 **1. "Bảng định tuyến đúng" và "gói đi đúng đường" là hai chuyện khác nhau.**
> Giai đoạn 2 bạn đã có bảng route hoàn hảo mà gói vẫn đi vòng qua hub.
> ⭐ **Luôn `traceroute`, đừng chỉ `show ip route`.**

> 🔴 **2. Đừng học quy tắc, hãy học lý do.**
> *"iBGP thì luôn `next-hop-self`"* là một quy tắc — và lab này chứng minh nó **sai**
> trong hoàn cảnh khác. ⭐ **Cái đúng là: cần nó khi peer không tự tới được next-hop gốc.**

> 🔴 **3. MTU phải tính cho TOÀN BỘ chồng giao thức ngay từ đầu.**
> ⭐ Triệu chứng *"ping chạy nhưng tải file treo"* là chữ ký của lỗi MTU,
> và nó sẽ theo bạn suốt sự nghiệp — GRE, IPsec, VXLAN, VPN, container overlay đều dính.

---

> 🧭 **Quay lại:** [README](README.md) · [LAB Capstone](Module-13-LAB-Capstone.md) ·
> [Module-08 — Overlay](Module-08-Virtualization-va-Overlay.md) ·
> [Module-12 — Automation](Module-12-Automation-va-Programmability.md)
