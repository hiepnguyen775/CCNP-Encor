# LAB 06B — Tuần 11: NAT/PAT · NTP · Multicast

> 📘 **Lý thuyết:** [Module-06B](Module-06B-NAT-NTP-Multicast.md) —
> đọc **Phần 1** và **Phần 2 mục §3.2 (thứ tự NAT–routing), §4 (NTP)** trước khi làm.
>
> ⏱️ **Thời gian:** ~6 giờ · 💾 **RAM:** 2.3 GB · 👉 **Dùng lại topology [LAB 06A](Module-06A-LAB.md)**

---

## Lab này trả lời 6 câu hỏi

| # | Câu hỏi | Bước |
|:---:|---|:---:|
| 1 | Nhiều máy dùng chung 1 IP public — router phân biệt chúng bằng gì? | 1 |
| 2 | ⭐ Vì sao **thiếu default route** làm NAT **không chạy** dù cấu hình đúng? | 1 |
| 3 | Port forward vào được — nhưng ACL nên dùng IP **private hay public**? | 2 |
| 4 | Hai ISP: vì sao NAT thường **không failover được**, và sửa bằng gì? | 4 |
| 5 | NTP chưa đồng bộ — nhìn dấu hiệu nào biết ngay? | 5 |
| 6 | 🚀 Multicast đi thế nào (tùy chọn) | 6 |

> ⭐ **Bước 1 và 2 chứa hai bẫy khó tìm nhất khi làm NAT ngoài đời.**
> Cả hai đều xuất phát từ **thứ tự xử lý NAT và routing** — thứ mà cấu hình *"trông đúng"*
> không bao giờ cho bạn thấy.

---

## ⚠️ Đọc trước khi bắt đầu

| Điều cần biết | Chi tiết |
|---|---|
| **Dùng lại LAB 06A** | Không cần dựng mới — chỉ thêm cấu hình NAT/NTP lên topology cũ |
| **Bẫy ở bước 1–2 là CỐ Ý** | Bạn sẽ thấy NAT "không chạy" dù config đúng. Đó là bài học |
| **`clear ip nat translation *`** | Sau mỗi thay đổi NAT, xóa bảng dịch cũ rồi mới test lại |
| **NTP rất chậm** | Đồng bộ mất **vài phút**. `stratum 16` lúc đầu là bình thường — chờ |
| **Lỗi > 15 phút** | Ghi vào [`SO-TAY-LOI.md`](SO-TAY-LOI.md) |

---

## 🧪 7. LAB 06B

### 7.1 Chuẩn bị — dùng lại LAB 06A

```
                  ┌──────────────┐
                  │    R-ISP     │  Lo8: 8.8.8.8/32
                  └──┬────────┬──┘  Lo9: 9.9.9.9/32
      203.0.113.0/30 │        │ 198.51.100.0/30
                 Gi0/1│        │Gi0/1
                 ┌───┴──┐  ┌──┴───┐
                 │  R1  │  │  R2  │
                 └───┬──┘  └──┬───┘
                     │  SW1   │
                     └───┬────┘
                    [PC1] 10.1.10.100
                    [SRV] 10.1.10.50 (giả lập web server)
```

⭐ **Thay đổi trên R-ISP:** ⭐ **XÓA route về LAN private** để chứng minh NAT thật sự hoạt động.
```
R-ISP(config)# no ip route 10.1.10.0 255.255.255.0 203.0.113.1
R-ISP(config)# no ip route 10.1.20.0 255.255.255.0 198.51.100.1
```
⭐ Giờ R-ISP **không biết** mạng `10.1.10.0/24` → nếu PC1 ping được `8.8.8.8`
thì **chắc chắn là nhờ NAT**.

⭐ **Thêm SRV (giả lập web server)** — dùng VPCS thứ 2 hoặc 1 vIOS nhẹ:
```
! Nếu dùng VPCS:
SRV> ip 10.1.10.50/24 10.1.10.1
SRV> save
```

---

### Bước 1 — ⭐ PAT overload + chứng minh thứ tự NAT-Routing

#### 1a) Cấu hình PAT trên R1

```
R1(config)# interface GigabitEthernet0/0.10
R1(config-subif)#  ip nat inside
R1(config-subif)# exit
R1(config)# interface GigabitEthernet0/0.20
R1(config-subif)#  ip nat inside
R1(config-subif)# exit
R1(config)# interface GigabitEthernet0/1
R1(config-if)#  ip nat outside
R1(config-if)# exit
!
R1(config)# ip access-list standard ACL-NAT
R1(config-std-nacl)#  permit 10.1.10.0 0.0.0.255
R1(config-std-nacl)#  permit 10.1.20.0 0.0.0.255
R1(config-std-nacl)# exit
!
R1(config)# ip nat inside source list ACL-NAT interface GigabitEthernet0/1 overload
```

**Làm tương tự trên R2** (uplink `Gi0/1` = `198.51.100.1`).

#### 1b) Test & đọc bảng NAT

```
PC1> ping 8.8.8.8
! ✅ thành công (dù R-ISP KHÔNG có route về 10.1.10.0/24)
```
```
R1# show ip nat translations
```
**Output mẫu:**
```
Pro  Inside global      Inside local       Outside local      Outside global
icmp 203.0.113.1:7      10.1.10.100:7      8.8.8.8:7          8.8.8.8:7
```

⭐ **Điền bảng 4 thuật ngữ từ output này:**

| Thuật ngữ | Giá trị | Nghĩa |
|---|---|---|
| Inside Local | | |
| Inside Global | | |
| Outside Local | | |
| Outside Global | | |

<details><summary>Đáp án</summary>

| Thuật ngữ | Giá trị | Nghĩa |
|---|---|---|
| ⭐ **Inside Local** | `10.1.10.100` | IP **thật** của PC1 |
| ⭐ **Inside Global** | `203.0.113.1` | PC1 **hóa trang thành** IP này (= IP interface outside của R1) |
| **Outside Local** | `8.8.8.8` | Đích, nhìn từ nội bộ |
| **Outside Global** | `8.8.8.8` | Đích, nhìn từ ngoài (giống Outside Local vì không dùng `ip nat outside source`) |
</details>

```
R1# show ip nat statistics
```
**Output mẫu:**
```
Total active translations: 1 (0 static, 1 dynamic; 1 extended)
Peak translations: 3, occurred 00:02:11 ago
Outside interfaces:
  GigabitEthernet0/1
Inside interfaces:
  GigabitEthernet0/0.10, GigabitEthernet0/0.20
Hits: 24  Misses: 0
CEF Translated packets: 24, CEF Punted packets: 6
Expired translations: 2
Dynamic mappings:
-- Inside Source
[Id: 1] access-list ACL-NAT interface GigabitEthernet0/1 refcount 1
```
⭐ `Hits` tăng = NAT hoạt động · ⚠️ `Misses` cao = có traffic khớp ACL nhưng không NAT được.

**⭐ Chứng minh NAT thật sự cần thiết:**
```
R-ISP# ping 10.1.10.100
! ❌ FAIL — R-ISP không có route về mạng private
```
⭐ **PC1 ra được nhờ NAT, không phải nhờ routing.**

#### 1c) ⭐⭐ CHỨNG MINH: thiếu default route → NAT vô nghĩa

```
R1(config)# no ip route 0.0.0.0 0.0.0.0 203.0.113.2
```
```
PC1> ping 8.8.8.8
! ❌ FAIL 100%
R1# show ip nat translations
! → TRỐNG (không có entry nào được tạo)
R1# show ip nat statistics | include Misses
! Hits: 24  Misses: 0                          ← Misses KHÔNG tăng
```

⭐⭐ **Bài học:** NAT **không được gọi tới** — vì ⭐ **routing xảy ra TRƯỚC NAT**
ở chiều inside→outside. Không có route → gói bị **drop trước khi NAT kịp làm gì**.

**Bật lại:**
```
R1(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.2
```

#### 1d) 🧪 Bắt gói 2 bên NAT để nhìn thấy dịch địa chỉ

1. EVE-NG: **Capture** link `R1 Gi0/0` (inside) → Wireshark, filter `icmp`
2. EVE-NG: **Capture** link `R1 Gi0/1` (outside) → Wireshark, filter `icmp`
3. PC1 ping `8.8.8.8`

⭐ **Kết quả:**

| Bắt ở | Source IP | Nghĩa |
|---|---|---|
| **Inside** (`Gi0/0`) | `10.1.10.100` | ⭐ **Inside Local** |
| **Outside** (`Gi0/1`) | `203.0.113.1` | ⭐ **Inside Global** |

⭐ **Nhìn thấy NAT bằng mắt.** Đừng bỏ bước này.

✅ **Checkpoint bước 1:**

| Kiểm tra | Mong đợi |
|---|---|
| PC1 ping `8.8.8.8` OK dù R-ISP không có route về LAN | ⭐ ✅ |
| `show ip nat translations` có entry, đọc đúng 4 thuật ngữ | ⭐ ✅ |
| ⭐ Xóa default route → NAT **không tạo entry**, ping fail | ⭐⭐ ✅ |
| Bắt gói 2 bên → source IP **khác nhau** | ⭐ ✅ |

---

### Bước 2 — ⭐⭐ Static PAT (port forwarding) + bẫy ACL

#### 2a) Publish web server nội bộ

```
! Port forward: Internet:80 → 10.1.10.50:80
R1(config)# ip nat inside source static tcp 10.1.10.50 80 interface GigabitEthernet0/1 80

! Publish thêm SSH qua port khác
R1(config)# ip nat inside source static tcp 10.1.10.50 22 interface GigabitEthernet0/1 2222
```

```
R1# show ip nat translations
```
**Output mẫu:**
```
Pro  Inside global         Inside local       Outside local      Outside global
tcp  203.0.113.1:80        10.1.10.50:80      ---                ---
tcp  203.0.113.1:2222      10.1.10.50:22      ---                ---
```
⭐ Static entry hiện **ngay lập tức** (không cần traffic) và **`---`** ở 2 cột outside
= **chờ kết nối từ bất kỳ ai**.

#### 2b) Test từ "Internet"

> 💡 VPCS không mở port TCP. Dùng **vIOS làm SRV** để test thật:
> trên SRV bật `ip http server`, rồi từ R-ISP `telnet 203.0.113.1 80`.

**Nếu SRV là vIOS:**
```
SRV(config)# ip http server
SRV(config)# interface Gi0/0
SRV(config-if)#  ip address 10.1.10.50 255.255.255.0
SRV(config)# ip route 0.0.0.0 0.0.0.0 10.1.10.1
```
```
R-ISP# telnet 203.0.113.1 80
Trying 203.0.113.1, 80 ... Open              ← ✅ Port forward hoạt động
```
```
R1# show ip nat translations | include :80
tcp  203.0.113.1:80   10.1.10.50:80   203.0.113.2:38412   203.0.113.2:38412
```
⭐ Giờ 2 cột outside đã có giá trị (kết nối thật).

#### 2c) 🔴⭐⭐ BẪY ACL — dùng IP private là SAI

```
! ❌ SAI — ACL dùng IP PRIVATE
R1(config)# ip access-list extended ACL-OUT-IN
R1(config-ext-nacl)#  permit tcp any host 10.1.10.50 eq 80
R1(config-ext-nacl)#  permit icmp any any
R1(config-ext-nacl)#  deny   ip any any log
R1(config-ext-nacl)# exit
R1(config)# interface GigabitEthernet0/1
R1(config-if)#  ip access-group ACL-OUT-IN in
```
```
R-ISP# telnet 203.0.113.1 80
! ❌ FAIL — Connection refused / timeout
```
```
R1# show access-lists ACL-OUT-IN
Extended IP access list ACL-OUT-IN
    10 permit tcp any host 10.1.10.50 eq www (0 matches)      ← 0 MATCHES!
    20 permit icmp any any (5 matches)
    30 deny ip any any log (3 matches)                         ← bị chặn ở đây
```

⭐⭐ **`0 matches` ở dòng permit** — ACL **không khớp** vì ở chiều **outside→inside**,
⭐ **ACL inbound chạy TRƯỚC NAT** → lúc đó gói vẫn có destination = **`203.0.113.1` (IP public)**,
chưa phải `10.1.10.50`.

```
! ✅ ĐÚNG — ACL dùng IP PUBLIC (Inside Global)
R1(config)# no ip access-list extended ACL-OUT-IN
R1(config)# ip access-list extended ACL-OUT-IN
R1(config-ext-nacl)#  permit tcp any host 203.0.113.1 eq 80       ! IP PUBLIC
R1(config-ext-nacl)#  permit tcp any host 203.0.113.1 eq 2222
R1(config-ext-nacl)#  permit icmp any any
R1(config-ext-nacl)#  deny   ip any any log
```
```
R-ISP# telnet 203.0.113.1 80
Trying 203.0.113.1, 80 ... Open              ← ✅ HOẠT ĐỘNG
R1# show access-lists ACL-OUT-IN
    10 permit tcp any host 203.0.113.1 eq www (2 matches)         ← CÓ MATCH
```

> ⭐⭐ **Ghi vào `SO-TAY-LOI.md`:** ⭐ **ACL inbound trên interface OUTSIDE
> phải dùng IP PUBLIC (Inside Global)**, vì ACL chạy **TRƯỚC** NAT ở chiều outside→inside.

**Dọn dẹp:**
```
R1(config)# interface GigabitEthernet0/1
R1(config-if)#  no ip access-group ACL-OUT-IN in
```

✅ **Checkpoint bước 2:**

| Kiểm tra | Mong đợi |
|---|---|
| Static PAT entry hiện **ngay** trong `show ip nat translations` với `---` | ✅ |
| Từ "Internet" telnet vào port 80 → thành công | ✅ |
| ⭐⭐ ACL dùng **IP private** → `0 matches`, bị chặn | ⭐⭐ ✅ |
| ⭐ ACL dùng **IP public** → có match, hoạt động | ⭐ ✅ |

---

### Bước 3 — ⭐ Dynamic NAT với pool (và test cạn pool)

```
R1(config)# no ip nat inside source list ACL-NAT interface GigabitEthernet0/1 overload
!
R1(config)# ip nat pool POOL-SMALL 203.0.113.10 203.0.113.11 netmask 255.255.255.252
R1(config)# ip nat inside source list ACL-NAT pool POOL-SMALL       ! ⚠️ KHÔNG có overload
```
> ⚠️ Pool chỉ có **2 IP** và **không overload** → chỉ 2 host NAT được cùng lúc.
> R-ISP cần route về pool: `ip route 203.0.113.8 255.255.255.248 203.0.113.1`

```
R-ISP(config)# ip route 203.0.113.8 255.255.255.248 203.0.113.1
```

**Test:**
```
PC1> ping 8.8.8.8            ! ✅ dùng 203.0.113.10
SRV> ping 8.8.8.8            ! ✅ dùng 203.0.113.11
! Host thứ 3 (nếu có) → ❌ FAIL
```
```
R1# show ip nat translations
Pro  Inside global      Inside local       Outside local      Outside global
---  203.0.113.10       10.1.10.100        ---                ---
---  203.0.113.11       10.1.10.50         ---                ---
R1# show ip nat statistics | include Misses|pool
! Hits: 40  Misses: 6                       ← Misses TĂNG = có host không NAT được
R1# show logging | include NAT
%NAT-4-ADDR_ALLOC_FAILURE: Address allocation failed; pool POOL-SMALL may be exhausted
```
⭐⭐ **`Misses` tăng + log `ADDR_ALLOC_FAILURE`** = ⭐ **pool cạn**.
Đây là dấu hiệu nhận diện Dynamic NAT hết IP.

**⭐ Thêm `overload` → thành PAT với pool:**
```
R1(config)# no ip nat inside source list ACL-NAT pool POOL-SMALL
R1(config)# ip nat inside source list ACL-NAT pool POOL-SMALL overload
R1# clear ip nat translation *
```
→ Giờ **nhiều host chung 1 IP + port** → không còn cạn pool.

**Trả về PAT interface (đơn giản nhất):**
```
R1(config)# no ip nat inside source list ACL-NAT pool POOL-SMALL overload
R1(config)# ip nat inside source list ACL-NAT interface GigabitEthernet0/1 overload
R1# clear ip nat translation *
```

---

### Bước 4 — ⭐⭐ NAT route-map cho dual-ISP

#### 4a) Cấu hình R1 với 2 uplink

> 💡 Trong lab này R1 chỉ có 1 uplink tới R-ISP. Để mô phỏng dual-ISP,
> thêm `R1 Gi0/2` ↔ `R-ISP Gi0/3` với dải `192.0.2.0/30`.

```
! ═══ R-ISP ═══
R-ISP(config)# interface GigabitEthernet0/3
R-ISP(config-if)#  description ---> To R1 ISP2
R-ISP(config-if)#  ip address 192.0.2.2 255.255.255.252
R-ISP(config-if)#  no shutdown

! ═══ R1 ═══
R1(config)# interface GigabitEthernet0/2
R1(config-if)#  description ---> UPLINK ISP2
R1(config-if)#  ip address 192.0.2.1 255.255.255.252
R1(config-if)#  ip nat outside                             ! cũng là outside
R1(config-if)#  no shutdown
```

#### 4b) Routing failover (Module-03) + NAT route-map

```
! ═══ IP SLA + track cho ISP1 ═══
R1(config)# ip sla 1
R1(config-ip-sla)#  icmp-echo 8.8.8.8 source-interface GigabitEthernet0/1
R1(config-ip-sla-echo)#  frequency 5
R1(config-ip-sla-echo)# exit
R1(config)# ip sla schedule 1 life forever start-time now
R1(config)# track 1 ip sla 1 reachability
R1(config-track)#  delay down 3 up 10
R1(config-track)# exit
!
! ═══ Floating static ═══
R1(config)# no ip route 0.0.0.0 0.0.0.0 203.0.113.2
R1(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.2 track 1        ! ISP1, AD 1
R1(config)# ip route 0.0.0.0 0.0.0.0 192.0.2.2 200              ! ISP2, AD 200
!
! ═══ NAT ROUTE-MAP ═══
R1(config)# no ip nat inside source list ACL-NAT interface GigabitEthernet0/1 overload
!
R1(config)# route-map RM-NAT-ISP1 permit 10
R1(config-route-map)#  match ip address ACL-NAT
R1(config-route-map)#  match interface GigabitEthernet0/1       ! ISP1
R1(config-route-map)# exit
R1(config)# route-map RM-NAT-ISP2 permit 10
R1(config-route-map)#  match ip address ACL-NAT
R1(config-route-map)#  match interface GigabitEthernet0/2       ! ISP2
R1(config-route-map)# exit
!
R1(config)# ip nat inside source route-map RM-NAT-ISP1 interface GigabitEthernet0/1 overload
R1(config)# ip nat inside source route-map RM-NAT-ISP2 interface GigabitEthernet0/2 overload
```

#### 4c) Test failover NAT

```
! Bình thường
PC1> ping 8.8.8.8            ! ✅
R1# show ip nat translations
! icmp 203.0.113.1:8   10.1.10.100:8   8.8.8.8:8   8.8.8.8:8      ← IP của ISP1
R1# show ip route 0.0.0.0
! * 203.0.113.2                                                     ← ISP1
```

```
! Cắt ISP1 (mô phỏng: shutdown Lo8 trên R-ISP để IP SLA fail)
R-ISP(config)# interface GigabitEthernet0/1
R-ISP(config-if)# shutdown
```
Chờ ~10 giây:
```
R1# show track 1
!   Reachability is Down
R1# show ip route 0.0.0.0
! * 192.0.2.2                                                       ← ĐÃ CHUYỂN ISP2
!
! Clear NAT để entry cũ không giữ traffic
R1# clear ip nat translation *
```
```
PC1> ping 8.8.8.8            ! ✅ hoạt động lại
R1# show ip nat translations
! icmp 192.0.2.1:9   10.1.10.100:9   8.8.8.8:9   8.8.8.8:9         ← IP của ISP2!
```
⭐⭐ **NAT đã tự dùng IP của ISP2** — nhờ `match interface` trong route-map.

**⚠️ Test không clear NAT:**
```
R-ISP(config-if)# no shutdown       ! bật lại ISP1
! chờ track Up, route về ISP1
PC1> ping 8.8.8.8
```
→ Nếu entry cũ (IP ISP2) còn, gói ra ISP1 với source IP của ISP2 → có thể fail
cho tới khi entry hết hạn.

⭐ **Giải pháp production — dùng EEM tự động clear NAT khi track đổi trạng thái** (Module-12):
```
event manager applet CLEAR-NAT-ON-FAILOVER
 event track 1 state any
 action 1.0 cli command "enable"
 action 2.0 cli command "clear ip nat translation *"
 action 3.0 syslog msg "NAT translations cleared due to track 1 state change"
```

✅ **Checkpoint bước 4:**

| Kiểm tra | Mong đợi |
|---|---|
| Bình thường: NAT dùng **IP của ISP1** | ✅ |
| Cắt ISP1 → track `Down` → route chuyển ISP2 | ✅ |
| ⭐ Sau `clear ip nat translation *` → NAT dùng **IP của ISP2** | ⭐⭐ ✅ |
| Hiểu vì sao cần route-map (fully-extended entry) thay vì NAT thường | ⭐ ✅ |

**Dọn dẹp (giữ lại nếu muốn):**
```
R1(config)# no ip nat inside source route-map RM-NAT-ISP2 interface GigabitEthernet0/2 overload
R1(config)# no ip nat inside source route-map RM-NAT-ISP1 interface GigabitEthernet0/1 overload
R1(config)# ip nat inside source list ACL-NAT interface GigabitEthernet0/1 overload
R1# clear ip nat translation *
```

---

### Bước 5 — ⭐ NTP với authentication

#### 5a) R-ISP làm NTP master (giả lập NTP server công cộng)

```
R-ISP(config)# clock timezone UTC 0
R-ISP(config)# clock set 10:00:00 Sep 9 2026
R-ISP(config)# ntp master 3                              ! stratum 3
R-ISP(config)# ntp authenticate
R-ISP(config)# ntp authentication-key 1 md5 NtpS3cret2026
R-ISP(config)# ntp trusted-key 1
```
```
R-ISP# show ntp status
! Clock is synchronized, stratum 3, reference is 127.127.1.1
```
⭐ `reference is 127.127.1.1` = **đồng hồ nội bộ của chính router** (khi làm `ntp master`).

#### 5b) R1, R2 làm NTP client

```
! ═══ R1 ═══
R1(config)# clock timezone ICT 7                          ! Việt Nam UTC+7
R1(config)# ntp authenticate
R1(config)# ntp authentication-key 1 md5 NtpS3cret2026
R1(config)# ntp trusted-key 1
R1(config)# ntp server 203.0.113.2 key 1 prefer
R1(config)# ntp source GigabitEthernet0/1
R1(config)# ntp update-calendar
!
! Bật timestamp cho log (rất quan trọng — Module-11)
R1(config)# service timestamps log datetime msec localtime show-timezone
R1(config)# service timestamps debug datetime msec localtime show-timezone
```
Làm tương tự R2 (`ntp server 198.51.100.2 key 1`).

#### 5c) Verify (chờ 1–3 phút để đồng bộ)

```
R1# show ntp status
```
**Output mẫu:**
```
Clock is synchronized, stratum 4, reference is 203.0.113.2
nominal freq is 250.0000 Hz, actual freq is 250.0000 Hz, precision is 2**10
reference time is E8F3A2B1.7C3D4E5F (17:15:32.485 ICT Mon Sep 9 2026)
clock offset is 0.5432 msec, root delay is 3.21 msec
root dispersion is 12.34 msec, peer dispersion is 0.98 msec
system poll interval is 64, last update was 45 sec ago.
```
✅ ⭐ `Clock is synchronized` · ⭐ `stratum 4` (= master 3 + 1) · `reference is 203.0.113.2`

```
R1# show ntp associations
```
**Output mẫu:**
```
  address         ref clock       st   when   poll reach  delay  offset   disp
*~203.0.113.2    127.127.1.1      3     45     64   377   3.210   0.543  0.980
 * sys.peer, # selected, + candidate, - outlier, x falseticker, ~ configured
```
⭐ ⭐ **`*`** trước địa chỉ = ⭐ **sys.peer** (đang thực sự dùng) · ⭐ **`reach 377`** = 8/8 poll OK

```
R1# show clock detail
```
**Output mẫu:**
```
17:20:15.485 ICT Mon Sep 9 2026
Time source is NTP                              ← nguồn là NTP
```
⭐ **Không có dấu `*`** trước giờ = ⭐ **thời gian đáng tin**.

#### 5d) ⚠️ Tái hiện 3 lỗi NTP

**Lỗi 1 — key lệch:**
```
R1(config)# ntp authentication-key 1 md5 WrongKey
R1# clear ntp ?               ! (không có lệnh clear ntp — chờ hoặc no ntp server rồi thêm lại)
R1(config)# no ntp server 203.0.113.2
R1(config)# ntp server 203.0.113.2 key 1 prefer
```
Chờ 1–2 phút:
```
R1# show ntp associations
!  ~203.0.113.2    0.0.0.0         16     -      64     0   0.000   0.000 16000.
!  ↑ KHÔNG có dấu * · st = 16 · reach = 0
R1# show ntp status
! Clock is unsynchronized, stratum 16, no reference clock       ← STRATUM 16!
```
⭐⭐ **`stratum 16` + `reach 0` + không có `*`** = **không đồng bộ được**.

**Sửa:**
```
R1(config)# ntp authentication-key 1 md5 NtpS3cret2026
```

**Lỗi 2 — thiếu `ntp trusted-key`:**
```
R1(config)# no ntp trusted-key 1
```
→ Cùng triệu chứng: `stratum 16`, `reach 0`. ⭐ **Phải có CẢ BA:**
`ntp authenticate` + `ntp authentication-key` + `ntp trusted-key`.

**Sửa:** `ntp trusted-key 1`

**Lỗi 3 — chưa bao giờ sync:**
```
R2(config)# no ntp server 198.51.100.2
R2# show clock
! *17:25:30.123 ICT Mon Sep 9 2026        ← DẤU * = giờ KHÔNG đáng tin
R2# show clock detail
! *17:25:30.123 ICT Mon Sep 9 2026
! Time source is user configuration        ← đặt tay, sẽ drift
```
⭐ **Dấu `*` trước giờ** là dấu hiệu nhận diện nhanh nhất.

**Sửa:** `ntp server 198.51.100.2 key 1`

#### 5e) ⭐ NTP access-group (chống NTP amplification)

```
R1(config)# ip access-list standard ACL-NTP-PEER
R1(config-std-nacl)#  permit 203.0.113.2
R1(config-std-nacl)# exit
R1(config)# ip access-list standard ACL-NTP-SERVE
R1(config-std-nacl)#  permit 10.0.0.0 0.255.255.255
R1(config-std-nacl)# exit
R1(config)# ntp access-group peer ACL-NTP-PEER
R1(config)# ntp access-group serve-only ACL-NTP-SERVE
```
⭐ Giờ R1 chỉ sync với `203.0.113.2`, và chỉ trả lời giờ cho mạng `10.0.0.0/8`.

✅ **Checkpoint bước 5:**

| Kiểm tra | Mong đợi |
|---|---|
| `show ntp status` → `Clock is synchronized, stratum 4` | ✅ |
| `show ntp associations` → có ⭐ **`*`** và ⭐ **`reach 377`** | ⭐ ✅ |
| `show clock detail` → `Time source is NTP`, **không có dấu `*`** | ⭐ ✅ |
| ⭐ Tái hiện key lệch → `stratum 16`, `reach 0`, không có `*` | ⭐⭐ ✅ |
| Hiểu phải có **cả 3** lệnh auth | ⭐ ✅ |
| Log có timestamp đầy đủ (`service timestamps log datetime msec localtime`) | ✅ |

---

### Bước 6 — 🚀 PIM-SM cơ bản (TÙY CHỌN — blueprint chỉ "describe")

> ⭐ **Bỏ qua bước này nếu bạn đang bám tiến độ.** Đề chỉ hỏi khái niệm.
> Làm nếu bạn muốn **thấy** `(*,G)` và `(S,G)` bằng mắt.

```
! ═══ Trên R1, R2, R-ISP ═══
ip multicast-routing
!
interface <mọi interface tham gia>
 ip pim sparse-mode
 ip igmp version 2
!
! R-ISP làm RP
R-ISP(config)# interface Loopback99
R-ISP(config-if)#  ip address 10.99.99.1 255.255.255.255
R-ISP(config-if)#  ip pim sparse-mode
R-ISP(config)# ip pim rp-address 10.99.99.1
!
! Trên MỌI router: khai RP (static)
R1(config)# ip pim rp-address 10.99.99.1
R2(config)# ip pim rp-address 10.99.99.1
! Và cần route tới 10.99.99.1 trên R1/R2
R1(config)# ip route 10.99.99.1 255.255.255.255 203.0.113.2
```

**Mô phỏng receiver — cho interface join group:**
```
R1(config)# interface GigabitEthernet0/0.10
R1(config-subif)#  ip igmp join-group 239.1.1.1
```

**Mô phỏng source — ping multicast từ R-ISP:**
```
R-ISP# ping 239.1.1.1 repeat 10 source Loopback8
```

**Verify:**
```
R1# show ip pim neighbor
R1# show ip pim rp mapping
R1# show ip igmp groups
R1# show ip mroute
```
**Output mẫu `show ip mroute`:**
```
(*, 239.1.1.1), 00:02:15/stopped, RP 10.99.99.1, flags: SJCL
  Incoming interface: GigabitEthernet0/1, RPF nbr 203.0.113.2
  Outgoing interface list:
    GigabitEthernet0/0.10, Forward/Sparse, 00:02:15/00:02:44

(8.8.8.8, 239.1.1.1), 00:00:12/00:02:47, flags: LJT
  Incoming interface: GigabitEthernet0/1, RPF nbr 203.0.113.2
  Outgoing interface list:
    GigabitEthernet0/0.10, Forward/Sparse, 00:00:12/00:02:47
```
⭐ **Nhìn thấy cả `(*, G)` và `(S, G)`** — và flag `T` = đã **SPT switchover**.

```
R1# show ip rpf 8.8.8.8
! RPF information for ? (8.8.8.8)
!   RPF interface: GigabitEthernet0/1
!   RPF neighbor: ? (203.0.113.2)
!   RPF route/mask: 0.0.0.0/0
!   RPF type: unicast (static)
```
⭐ **Đây là RPF check** — router dùng bảng **unicast** để xác định interface hợp lệ cho multicast.

✅ **Checkpoint bước 6 (tùy chọn):** thấy được `(*,G)` với `RP`, `(S,G)` với flag `T`,
và `show ip rpf` chỉ ra RPF interface.
