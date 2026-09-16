# LAB 10 — Tuần 16: Hardening · AAA · ACL · CoPP · 802.1X

> 📘 **Lý thuyết:** [Module-10](Module-10-Security.md) —
> đọc **Phần 1** và **Phần 2 mục §3 (hardening), §4 (AAA), §5 (ACL), §6 (CoPP)** trước khi làm.
>
> ⏱️ **Thời gian:** ~7 giờ · 💾 **RAM:** 1.8 GB · 🧰 **Cần:** EVE-NG + 2× vIOS + 1× vIOS-L2

---

## ⭐ Không có RADIUS server vẫn lab được 80%

| Nội dung | Cần server? | Cách lab |
|---|:---:|---|
| Password type, SSH, hardening | ❌ | Lab đầy đủ |
| ⭐⭐ **AAA + fallback** | ❌ | ⭐ **Trỏ vào IP không tồn tại** → server "chết" → quan sát fallback sang `local`.<br>⭐ **Đây chính là điểm đề hỏi!** |
| ACL nâng cao, uRPF, VACL | ❌ | Lab đầy đủ |
| CoPP | ❌ | Lab đầy đủ |
| ⭐ 802.1X | ⚠️ | Quan sát `Unauthorized` + tái hiện **Critical VLAN** khi RADIUS chết |

> ⭐ **Lab "server chết → fallback" còn giá trị hơn lab "đăng nhập thành công"** —
> vì đề hỏi đúng cái tình huống hỏng.

---

## 🔴 CẢNH BÁO AN TOÀN — đọc trước khi gõ

| Việc | Vì sao nguy hiểm |
|---|---|
| 🔴 ⭐⭐ **TẠO USER LOCAL TRƯỚC khi gõ `aaa new-model`** | Thiếu bước này là **tự khóa mình ra khỏi router** |
| 🔴 ⭐⭐ **GIỮ MỘT PHIÊN SSH THỨ HAI đang mở** | Nếu hỏng thì còn đường sửa. LAB B **cố ý** cho bạn tự khóa mình một lần |
| ⭐ **`test aaa` TRƯỚC khi logout** | Đừng logout rồi mới biết |
| 🔴 **CoPP: bắt đầu `exceed-action transmit`** | Siết ngay là **tự đánh sập OSPF/SSH của chính mình** |

---

## 🧪 13. LAB 10 — Hardening, AAA, ACL, CoPP

### 13.1 Topology

```
        ┌──────────┐              ┌──────────┐              ┌──────────┐
        │    R1    │──Gi0/0───────│   SW1    │───────Gi0/1──│    R2    │
        │ 10.0.0.1 │              │ vIOS-L2  │              │ 10.0.0.2 │
        │ Lo0 1.1.1.1              │  VLAN 10 │              │ Lo0 2.2.2.2
        └──────────┘              └──────────┘              └──────────┘
                                        │
                                   Gi0/2 (cổng "người dùng" cho LAB E)
```

| Node | Image | RAM |
|---|---|:---:|
| R1, R2 | vIOS | 512 MB × 2 |
| SW1 | vIOS-L2 | 768 MB |
| ⭐ **Tổng** | | ⭐ **~1.8 GB** ✅ |

⭐ **Cấu hình nền (làm trước):**
```
!═══ R1 ═══
hostname R1
interface Loopback0
 ip address 1.1.1.1 255.255.255.255
interface GigabitEthernet0/0
 ip address 10.0.0.1 255.255.255.0
 no shutdown
ip route 2.2.2.2 255.255.255.255 10.0.0.2

!═══ R2 ═══ (đối xứng)
hostname R2
interface Loopback0
 ip address 2.2.2.2 255.255.255.255
interface GigabitEthernet0/0
 ip address 10.0.0.2 255.255.255.0
 no shutdown
ip route 1.1.1.1 255.255.255.255 10.0.0.1
```

---

### LAB A — ⭐⭐ Password types & Hardening (25 phút)

**Bước A1 — Thấy tận mắt sự khác nhau giữa các loại mật khẩu:**
```
R1(config)# enable password TestPlain
R1(config)# username u5 password TestType5
R1(config)# do show run | include enable password|username u5
enable password TestPlain              ← HIỆN NGUYÊN VĂN
username u5 password 0 TestType5       ← type 0 = plaintext
```
```
R1(config)# service password-encryption
R1(config)# do show run | include enable password|username u5
enable password 7 0822455D0A16         ← đã thành type 7
username u5 password 7 06120A2D4A1A
```
> 💡 🔴 ⭐⭐ **Chép chuỗi type 7 đó và tìm bất kỳ trang "cisco type 7 decrypt" nào.**
> ⭐ **Nó ra lại mật khẩu gốc trong 1 giây.** ⭐ **Đó là lý do type 7 KHÔNG PHẢI bảo mật.**

**Bước A2 — Dùng loại đúng:**
```
R1(config)# no enable password
R1(config)# enable algorithm-type scrypt secret MatKhauRatDaiVaKho2026
R1(config)# username admin privilege 15 algorithm-type scrypt secret MatKhauRatDaiVaKho2026
R1(config)# do show run | include enable secret|username admin
enable secret 9 $9$Ab3...               ← số 9 = scrypt ✅
username admin privilege 15 secret 9 $9$Xy7...
```
✅ **Checkpoint A2:** ⭐ **con số ngay sau `secret` phải là `9`.** ⭐ Nếu là `5` → bạn quên `algorithm-type scrypt`.

**Bước A3 — SSH + khóa VTY:**
```
R1(config)# ip domain-name cty.local
R1(config)# crypto key generate rsa modulus 2048
R1(config)# ip ssh version 2
R1(config)# ip access-list standard ACL-MGMT
R1(config-std-nacl)#  permit 2.2.2.2
R1(config-std-nacl)#  deny any log
R1(config)# line vty 0 15
R1(config-line)#  transport input ssh
R1(config-line)#  login local
R1(config-line)#  exec-timeout 5 0
R1(config-line)#  access-class ACL-MGMT in
R1(config)# banner login ^ CANH BAO: He thong rieng. Moi hoat dong bi ghi log. ^
```
✅ **Checkpoint A3 — test từ R2:**
```
R2# telnet 1.1.1.1
   Trying 1.1.1.1 ... Open
   [Connection closed by foreign host]     ← ĐÚNG: telnet bị cấm

R2# ssh -l admin 1.1.1.1
   CANH BAO: He thong rieng...              ← banner hiện ra
   Password:                                   ← SSH hoạt động
```
```
R1# show ip ssh
SSH Enabled - version 2.0                    ← phải là 2.0
```

**Bước A4 — ⭐ `login block-for` (rất đáng làm):**
```
R1(config)# login block-for 60 attempts 3 within 30
R1(config)# login on-failure log
R1(config)# login quiet-mode access-class ACL-MGMT
```
⭐ Từ R2, ⭐ **SSH sai mật khẩu 3 lần liên tiếp**, rồi xem trên R1:
```
R1# show login
   Router enabled to watch for login Attacks.
   Router presently in Quiet-Mode, will remain in Quiet-Mode for 47 seconds.
   Denying logins from all sources.
%SEC_LOGIN-1-QUIET_MODE_ON: Still timeleft for watching failures is 47 seconds,
   [user: admin] [Source: 10.0.0.2] [localport: 22] ...
```
> 💡 ⭐ **Bạn vừa chặn được brute-force bằng 1 dòng lệnh.** ⭐ Và `quiet-mode access-class` đảm bảo
> ⭐ **admin thật vẫn vào được** trong lúc đang khóa.

---

### LAB B — 🔴 ⭐⭐ AAA và bài học FALLBACK (35 phút) — **LAB quan trọng nhất module**

**Bước B1 — ⭐ Chuẩn bị AN TOÀN trước (đọc kỹ):**
```
! TẠO USER LOCAL TRƯỚC — nếu không bạn sẽ tự khóa mình
R1(config)# username admin privilege 15 algorithm-type scrypt secret MatKhauCuuHo
! MỞ SẴN MỘT PHIÊN SSH THỨ HAI tới R1 và ĐỪNG ĐÓNG NÓ
```

**Bước B2 — Bật AAA, trỏ vào server KHÔNG TỒN TẠI:**
```
R1(config)# aaa new-model
!
R1(config)# tacacs server FAKE-ISE
R1(config-server-tacacs)#  address ipv4 192.0.2.99      ! IP không tồn tại
R1(config-server-tacacs)#  key SecretGia
R1(config-server-tacacs)#  timeout 5
!
R1(config)# aaa group server tacacs+ GRP-TAC
R1(config-sg-tacacs+)#  server name FAKE-ISE
!
R1(config)# aaa authentication login default group GRP-TAC local
R1(config)# aaa authorization exec default group GRP-TAC local if-authenticated
```

**Bước B3 — ⭐⭐ Test TRƯỚC KHI logout:**
```
R1# test aaa group GRP-TAC admin MatKhauCuuHo legacy
   Attempting authentication test to server-group GRP-TAC using tacacs+
   No response from server                    ← server chết, đúng như thiết kế
```
```
R1# show aaa servers | include host|State|Dead
   TACACS+: id 1, priority 1, host 192.0.2.99, auth-port 49
        State: current DEAD, duration 35s      ← DEAD
        Dead: total time 35s, count 1
```

✅ **Checkpoint B3 — ⭐⭐ bài test quyết định:**
Từ R2, ⭐ **SSH vào R1 bằng `admin` / `MatKhauCuuHo`**:
```
R2# ssh -l admin 1.1.1.1
Password: ********
R1>                                            ← VÀO ĐƯỢC!
```
> 💡 ⭐⭐ **Bạn vừa chứng kiến FALLBACK hoạt động.** ⭐ TACACS+ **im lặng** → router chờ hết timeout →
> ⭐ **chuyển sang phương pháp thứ hai (`local`)** → dùng `username admin` trong config.
>
> 🔴 ⭐⭐ **Nếu bạn viết `aaa authentication login default group GRP-TAC` (KHÔNG có `local`) →
> bạn vừa TỰ KHÓA MÌNH RA KHỎI ROUTER.** ⭐ Đây là tai nạn số 1 khi triển khai AAA.

**Bước B4 — 🔴 ⭐⭐ Tái hiện tai nạn (an toàn, vì có phiên SSH thứ hai đang mở):**
```
! Trên phiên SSH THỨ NHẤT:
R1(config)# aaa authentication login default group GRP-TAC       ! BỎ "local"
```
⭐ Từ R2, thử SSH mới:
```
R2# ssh -l admin 1.1.1.1
Password: ********
% Authentication failed                       ← KHÔNG VÀO ĐƯỢC NỮA
```
⭐ **Dùng phiên SSH thứ hai (vẫn đang mở) để sửa:**
```
R1(config)# aaa authentication login default group GRP-TAC local
```
> 💡 🔴 ⭐⭐ **Ghi ngay vào `SO-TAY-LOI.md`.** ⭐ Trên thiết bị thật, nếu bạn không giữ phiên thứ hai,
> ⭐ **bạn phải đi tới tận nơi cắm cáp console và làm password recovery.**

**Bước B5 — ⭐ Phân biệt `reject` với `timeout`:**
```
! Bảo vệ console riêng — thực hành tốt
R1(config)# aaa authentication login CONSOLE-LOCAL local
R1(config)# line con 0
R1(config-line)#  login authentication CONSOLE-LOCAL
```
```
R1# show aaa servers | include Authen|accept|reject|timeout
   Authen: request 6, timeouts 6            ← TẤT CẢ là timeout, không có reject
```
> 💡 ⭐⭐ **Ghi nhớ bảng phân biệt:**
> ⭐ **`timeouts` tăng / `State: DEAD`** → server **im lặng** → ⭐ **CÓ fallback**
> ⭐ **`reject` tăng** → server **trả lời "sai mật khẩu"** → 🔴 ⭐ **KHÔNG fallback**
>
> ⭐ **Và: sai shared key cho ra biểu hiện GIỐNG HỆT "server chết"** — vì router không giải mã được câu trả lời.

---

### LAB C — ⭐⭐ ACL nâng cao (35 phút)

**Bước C1 — Named ACL + chèn dòng vào giữa:**
```
R1(config)# ip access-list extended ACL-TEST
R1(config-ext-nacl)#  10 permit icmp any any
R1(config-ext-nacl)#  20 permit tcp any any eq 22
R1(config-ext-nacl)#  30 deny ip any any log
!
R1(config)# interface Gi0/0
R1(config-if)#  ip access-group ACL-TEST in
```
```
! CHÈN vào giữa — không cần gõ lại cả ACL
R1(config)# ip access-list extended ACL-TEST
R1(config-ext-nacl)# 15 permit tcp any any eq telnet
!
R1# show access-lists ACL-TEST
Extended IP access list ACL-TEST
    10 permit icmp any any
    15 permit tcp any any eq telnet      ← đã chèn ĐÚNG VỊ TRÍ
    20 permit tcp any any eq 22
    30 deny ip any any log
```
✅ **Checkpoint C1:** ⭐ **thử làm điều tương tự với numbered ACL (`access-list 100 ...`)** → ⭐ **dòng mới
luôn nhảy xuống cuối, SAU dòng `deny`** → ⭐ **vô dụng.** ⭐ **Đây là lý do luôn dùng named ACL.**

**Bước C2 — ⭐⭐ Kỹ thuật troubleshoot ACL bằng bộ đếm:**
```
R1# clear ip access-list counters ACL-TEST
R2# ping 1.1.1.1 repeat 10
R2# ping 1.1.1.1 source 2.2.2.2 repeat 5
R1# show access-lists ACL-TEST
    10 permit icmp any any (15 matches)      ← ĐÂY là dòng đang quyết định
    15 permit tcp any any eq telnet
    20 permit tcp any any eq 22
    30 deny ip any any log
```
> 💡 ⭐⭐ **Đây là kỹ năng troubleshoot ACL quan trọng nhất:**
> ⭐ **clear counter → tạo traffic → xem dòng nào tăng.**
> ⭐ **Không dòng nào tăng = gói không tới interface đó, hoặc bạn áp sai chiều (in/out).**

**Bước C3 — ⭐ Deny tường minh để có bộ đếm:**
```
R2# telnet 1.1.1.1 8080
   (bị chặn)
R1# show access-lists ACL-TEST | include deny
    30 deny ip any any log (3 matches)      ← CÓ ĐẾM và CÓ LOG
R1# show logging | include ACL-TEST
%SEC-6-IPACCESSLOGP: list ACL-TEST denied tcp 10.0.0.2(...) -> 1.1.1.1(8080), 1 packet
```
> 💡 ⭐ **Nếu bạn không viết dòng `deny ip any any log`, gói vẫn bị chặn bởi deny NGẦM —
> nhưng ⭐ KHÔNG có bộ đếm và KHÔNG có log** → ⭐ **bạn mù hoàn toàn khi điều tra sự cố.**

**Bước C4 — 🔴 ⭐⭐ Tái hiện BẪY IPv6 ACL (bước giá trị nhất của LAB C):**
```
!═══ Bật IPv6 trên link R1–R2 ═══
!─── R1 ───
ipv6 unicast-routing
interface Gi0/0
 ipv6 address 2001:DB8::1/64
!─── R2 ───
ipv6 unicast-routing
interface Gi0/0
 ipv6 address 2001:DB8::2/64
```
```
R1# ping 2001:DB8::2
!!!!!                                            OK
R1# show ipv6 neighbors
2001:DB8::2   ...  REACH  Gi0/0               NDP hoạt động
```
```
! Giờ áp một ACL "trông có vẻ đúng":
R1(config)# ipv6 access-list ACL-V6-SAI
R1(config-ipv6-acl)#  permit tcp any any eq 22
R1(config-ipv6-acl)# deny ipv6 any any log        ! DÒNG GIẾT NDP
R1(config)# interface Gi0/0
R1(config-if)#  ipv6 traffic-filter ACL-V6-SAI in
```
```
R1# clear ipv6 neighbors
R1# ping 2001:DB8::2
.....                                          ← CHẾT HOÀN TOÀN
R1# show ipv6 neighbors
(trống — hoặc INCMP)                           ← KHÔNG phân giải được lớp 2
```
✅ **Sửa:**
```
R1(config)# ipv6 access-list ACL-V6-DUNG
R1(config-ipv6-acl)# permit icmp any any nd-na     ! PHẢI ĐẶT TRƯỚC
R1(config-ipv6-acl)# permit icmp any any nd-ns
R1(config-ipv6-acl)#  permit icmp any any            ! (cho ping test)
R1(config-ipv6-acl)#  permit tcp any any eq 22
R1(config-ipv6-acl)#  deny ipv6 any any log
R1(config)# interface Gi0/0
R1(config-if)#  ipv6 traffic-filter ACL-V6-DUNG in
!
R1# ping 2001:DB8::2
!!!!!                                          ← ✅ SỐNG LẠI
```
> 💡 🔴 ⭐⭐ **Bài học một câu — ghi vào `SO-TAY-LOI.md`:**
> ⭐ ***"Viết `deny ipv6 any any` tường minh thì PHẢI tự thêm `permit icmp any any nd-na` và
> `nd-ns` lên TRƯỚC — nếu không bạn giết NDP và IPv6 chết sạch."***

**Bước C5 — 🚀 `established` (tùy chọn, 5 phút):**
```
R1(config)# ip access-list extended ACL-EST
R1(config-ext-nacl)#  permit tcp any any established
R1(config-ext-nacl)#  permit icmp any any
R1(config-ext-nacl)#  deny ip any any log
```
✅ ⭐ Từ R2 thử `telnet 1.1.1.1 22` → 🔴 **bị chặn** (gói SYN đầu tiên **không có cờ ACK**).
⭐ Từ R1 thử `telnet 2.2.2.2 22` → ⭐ **gói trả về được phép** (có ACK).
> 💡 ⭐ **Bạn vừa thấy `established` chỉ cho phép traffic TRẢ LỜI.**

---

### LAB D — ⭐⭐ CoPP (30 phút)

**Bước D1 — Phân loại và áp policy ở chế độ "CHỈ ĐẾM":**
```
!═══ R1 ═══
ip access-list extended ACL-CP-ICMP
 permit icmp any any echo
 permit icmp any any echo-reply
!
ip access-list extended ACL-CP-SSH
 permit tcp any any eq 22
!
class-map match-all CM-CP-ICMP
 match access-group name ACL-CP-ICMP
class-map match-all CM-CP-SSH
 match access-group name ACL-CP-SSH
!
policy-map PM-COPP
 class CM-CP-ICMP
  police 8000 conform-action transmit exceed-action transmit   ! CHỈ ĐẾM
 class CM-CP-SSH
  police 100000 conform-action transmit exceed-action transmit
 class class-default
  police 500000 conform-action transmit exceed-action transmit
!
control-plane
 service-policy input PM-COPP
```

**Bước D2 — Tạo traffic và đọc bộ đếm:**
```
R2# ping 1.1.1.1 repeat 200 size 1400
R1# show policy-map control-plane input class CM-CP-ICMP
```
```
Control Plane
  Service-policy input: PM-COPP
    Class-map: CM-CP-ICMP (match-all)
      400 packets, 568000 bytes                ← CÓ ĐẾM
      police:  cir 8000 bps, bc 1500 bytes
        conformed 63 packets;  actions: transmit
        exceeded  337 packets; actions: transmit    ← VƯỢT nhưng VẪN CHO QUA
```
> 💡 ⭐⭐ **`exceeded` cao nhưng `actions: transmit` = CoPP đang ĐO chứ chưa CHẶN.**
> ⭐ **Đây chính xác là chế độ bạn phải chạy vài ngày trước khi siết.**

**Bước D3 — 🔴 ⭐ Siết lại và thấy hậu quả:**
```
R1(config)# policy-map PM-COPP
R1(config-pmap)#  class CM-CP-ICMP
R1(config-pmap-c)#  police 8000 conform-action transmit exceed-action drop
```
```
R2# ping 1.1.1.1 repeat 100 size 1400
!!!..!...!..!!....!...                        ← MẤT GÓI RẤT NHIỀU
Success rate is 22 percent (22/100)
```
```
R1# show policy-map control-plane input class CM-CP-ICMP | include exceeded
        exceeded 78 packets; actions: drop     ← GIỜ THÌ VỨT THẬT
```
> 💡 🔴 ⭐⭐ **Bạn vừa tự tay chứng minh vì sao CoPP nguy hiểm.**
> ⭐ Nếu class này là **OSPF** thay vì ICMP, ⭐ **bạn vừa đánh sập adjacency của chính mình.**
> ⭐⭐ **Luôn: đo trước, siết sau. Và để `class-default` rộng rãi.**

**Bước D4 — ⭐ Xem CPU (nối với lý thuyết §5.1):**
```
R1# show processes cpu sorted | exclude 0.00
R1# show processes cpu history
```
⭐ Chạy `ping 1.1.1.1 repeat 100000 size 1400` từ R2 rồi xem CPU của R1 nhích lên —
⭐ **đây là cơ chế tấn công control plane ở quy mô nhỏ.**

---

## 🚀 14. LAB NÂNG CAO

### 14.1 🚀 ⭐⭐ LAB E — 802.1X: máy trạng thái và Critical VLAN (30 phút)

> ⭐ **Không cần RADIUS thật.** ⭐ Ta trỏ vào server chết để ⭐ **quan sát đúng cái đề hỏi**:
> trạng thái `Unauthorized` và cơ chế **Critical VLAN**.

```
!═══ SW1 ═══
aaa new-model
username admin privilege 15 algorithm-type scrypt secret MatKhauCuuHo   ! trước tiên!
!
radius server FAKE-ISE
 address ipv4 192.0.2.99 auth-port 1812 acct-port 1813
 key SecretGia
!
aaa group server radius GRP-RAD
 server name FAKE-ISE
!
aaa authentication dot1x default group GRP-RAD
aaa authorization network default group GRP-RAD
!
dot1x system-auth-control                    ! DÒNG HAY QUÊN NHẤT
!
radius-server dead-criteria time 5 tries 2
radius-server deadtime 5
!
vlan 10
 name DATA
vlan 99
 name GUEST
!
interface GigabitEthernet0/2
 description Cong nguoi dung - LAB 802.1X
 switchport mode access
 switchport access vlan 10
 authentication port-control auto
 authentication host-mode multi-domain
 authentication order dot1x mab
 mab
 dot1x pae authenticator
 dot1x timeout tx-period 7
 spanning-tree portfast
```

✅ **Checkpoint E1 — cổng bị KHÓA:**
```
SW1# show access-session interface Gi0/2 details
            Interface: GigabitEthernet0/2
              Status: Unauthorized             ← cổng ĐANG ĐÓNG
      Oper host mode: multi-domain
   Method status list:
         Method      State
         dot1x       Running / Stopped
         mab         Running
```
```
SW1# show dot1x interface Gi0/2 details | include PortControl|Status
   PortControl = AUTO
   Port Status  = UNAUTHORIZED
```
> 💡 ⭐ **Bạn vừa thấy điều quan trọng nhất:** ⭐ **cổng ở trạng thái `AUTO` sẽ ĐÓNG cho tới khi
> có `Access-Accept`.** ⭐ Server chết → **không ai vào được.**

✅ **Checkpoint E2 — ⭐⭐ thêm Critical VLAN và thấy nó cứu tình hình:**
```
interface GigabitEthernet0/2
 authentication event server dead action authorize vlan 10
 authentication event server dead action authorize voice
 authentication event no-response action authorize vlan 99
 authentication event server alive action reinitialize
```
```
SW1# show access-session interface Gi0/2 details
              Status: Authorized
   Method status list:
         dot1x   Authc Failed / Not run
   Current Policy: Critical_Auth                ← Critical VLAN đã cứu
```
> 💡 🔴 ⭐⭐ **Đây là bài học đắt giá nhất của 802.1X ngoài đời:**
> ⭐ **Không có Critical VLAN → ISE bảo trì 10 phút = cả công ty mất mạng.**
> ⭐ **Và bạn cũng không SSH vào switch được** (nếu switch cũng dùng ISE cho AAA) →
> ⭐ **đó là lý do method list PHẢI có `local` ở cuối** *(LAB B)*.

✅ **Checkpoint E3 — 🔴 ⭐ tái hiện lỗi "quên dòng global":**
```
SW1(config)# no dot1x system-auth-control
SW1# show access-session interface Gi0/2 details
   (không có session nào — như thể 802.1X chưa từng được cấu hình)
SW1# show dot1x
   Sysauthcontrol         = Disabled            ← THỦ PHẠM
```
> 💡 🔴 ⭐⭐ **Cấu hình trên port vẫn còn nguyên, nhưng 802.1X hoàn toàn không chạy — và
> KHÔNG có thông báo lỗi nào.** ⭐ **Luôn kiểm tra `show dot1x | include Sysauthcontrol` đầu tiên.**

### 14.2 🚀 ⭐ LAB F — uRPF chống giả mạo (10 phút)

```
!═══ R1 ═══
interface GigabitEthernet0/0
 ip verify unicast source reachable-via rx
```
```
! Từ R2, gửi gói với source GIẢ (một IP R1 không có route về qua Gi0/0)
R2# ping 1.1.1.1 source Loopback0        ! 2.2.2.2 — R1 CÓ route → OK
!!!!!

! Tạo interface với IP "lạ" trên R2 rồi ping bằng nó:
R2(config)# interface Loopback9
R2(config-if)#  ip address 172.31.99.9 255.255.255.255
R2# ping 1.1.1.1 source Loopback9        ! R1 KHÔNG có route về 172.31.99.9
.....                                  ← uRPF VỨT
```
```
R1# show ip interface Gi0/0 | include verify|drop
   IP verify source reachable-via RX
   5 verification drops                  ← bằng chứng uRPF hoạt động
```
> 💡 ⭐ **Bây giờ đổi sang loose mode và thử lại:**
> `ip verify unicast source reachable-via any` → ⭐ **vẫn drop** (vì R1 **hoàn toàn không có** route
> tới `172.31.99.9`). ⭐ **Loose chỉ khác strict khi CÓ route nhưng qua interface KHÁC.**

### 14.3 🚀 ⭐ LAB G — VACL: chặn 2 máy trong CÙNG VLAN (15 phút)

> ⭐ **Đây là thứ RACL không làm được** — traffic không đi qua router.

```
!═══ SW1 ═══
ip access-list extended ACL-CHAN
 permit ip host 10.1.10.50 host 10.1.10.51
!
vlan access-map VMAP-10 10
 match ip address ACL-CHAN
 action drop
vlan access-map VMAP-10 20
 action forward                          ! BẮT BUỘC — nếu không chặn sạch VLAN
!
vlan filter VMAP-10 vlan-list 10
```
```
SW1# show vlan access-map
SW1# show vlan filter
```
✅ **Checkpoint G — 🔴 thử bỏ map 20 (`action forward`):**
```
SW1(config)# no vlan access-map VMAP-10 20
```
→ ⭐ **Toàn bộ VLAN 10 mất kết nối.** ⭐ **VACL kết thúc bằng `drop` ngầm.**
> 💡 🔴 ⭐⭐ **Ghi vào sổ lỗi: "VACL luôn phải có một map cuối `action forward`."**

### 14.4 🚀 ⭐ LAB H — DHCP Snooping + DAI (20 phút, bổ trợ)

```
!═══ SW1 ═══
ip dhcp snooping
ip dhcp snooping vlan 10
no ip dhcp snooping information option            ! tắt option 82 trong lab
!
interface GigabitEthernet0/0
 description Uplink toi DHCP server that
 ip dhcp snooping trust
!
interface GigabitEthernet0/2
 description Cong nguoi dung
 ip dhcp snooping limit rate 10
!
ip arp inspection vlan 10
interface GigabitEthernet0/0
 ip arp inspection trust
```
```
show ip dhcp snooping
show ip dhcp snooping binding                  ! bảng MAC↔IP↔port↔VLAN
show ip arp inspection statistics
```
> 💡 🔴 ⭐⭐ **Thử bật DAI mà CHƯA bật DHCP Snooping** → ⭐ **mọi ARP bị drop, VLAN chết.**
> ⭐ **Thứ tự: DHCP Snooping TRƯỚC → nó xây bảng binding → DAI mới có cái để so.**
> ⭐ Và với thiết bị IP tĩnh: ⭐ **phải khai `ip source binding` thủ công.**

### 14.5 🚀 ⭐ LAB I — Wireless security trên DevNet Sandbox (30 phút)

| Bước | Làm |
|:---:|---|
| 1 | `developer.cisco.com/site/sandbox/` → sandbox **Catalyst 9800** (⭐ Always-On) |
| 2 | ⚠️ ⭐ Lấy URL + tài khoản **từ chính trang sandbox** |

⭐ **Bảng việc — chỉ XEM, đừng đổi:**

| # | Tìm gì | ⭐ Liên hệ |
|:---:|---|:---:|
| 1 | ⭐ Một WLAN dùng **PSK** — xem `security wpa akm psk` | §7.2 |
| 2 | ⭐ Một WLAN dùng **802.1X** — xem `security dot1x authentication-list` | §7.3 |
| 3 | ⭐⭐ **Policy Profile có bật `aaa-override` không** | §7.3 |
| 4 | ⭐ Cấu hình **PMF**: `optional` hay `mandatory` | §7.1 |
| 5 | ⭐ RADIUS server đang trỏ đi đâu (`show aaa servers`) | §3 |
| 6 | ⭐ Nếu có client: `show wireless client mac-address <MAC> detail` → **VLAN, ACL, SGT** | §6.7 |

✅ **Checkpoint I:** ⭐ **vẽ lại trên giấy chuỗi bảo mật của MỘT WLAN có thật:**
`WLAN Profile (akm, cipher, pmf)` → `security dot1x authentication-list` → `aaa authentication dot1x` →
`aaa group server radius` → `radius server` → và ⭐ **Policy Profile có `aaa-override` chưa.**
