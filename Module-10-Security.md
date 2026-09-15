# Module-10 — Security

> 🧭 **Lộ trình:** [Module-09](Module-09-Architecture-va-QoS.md) → `[Bạn đang ở đây] Module-10` → Module-11 (Network Assurance)
>
> 📊 **Blueprint — Domain 5.0 Security (20% đề) — khối lớn THỨ HAI của kỳ thi:**
> · 🔴 ⭐⭐ **5.1 — CONFIGURE AND VERIFY device access control** (5.1.a lines & password protection · 5.1.b authentication & authorization dùng AAA)
> · 🔴 ⭐⭐ **5.2 — CONFIGURE AND VERIFY infrastructure security features** (5.2.a ACL · 5.2.b CoPP)
> · 🟡 **5.3 — Describe REST API security**
> · 🔴 ⭐⭐ **5.4 — CONFIGURE AND VERIFY wireless security features** (5.4.a EAP · 5.4.b WebAuth · 5.4.c PSK)
> · 🟡 **5.5 — Describe the components of network security design** (threat defense · endpoint security · NGFW · TrustSec/MACsec · NAC với 802.1X, MAB, WebAuth)
>
> ⏱️ **Tuần 16** · 10–12 giờ

---

## ⭐ 0. Phạm vi — module "nửa cấu hình nửa khái niệm", và bẫy nằm ở chỗ chia đôi

### 0.1 Đọc bảng này trước, nó tiết kiệm cho bạn vài ngày

> 🔴 ⭐⭐ **Domain 5.0 là domain CHIA ĐÔI rõ rệt nhất của cả kỳ thi:**
> ⭐ **5.1, 5.2, 5.4 = "Configure and verify"** → ⭐ **phải gõ được**
> ⭐ **5.3, 5.5 = "Describe"** → ⭐ **chỉ cần nói được**
>
> 🔴 ⭐ **Sai lầm điển hình:** dành cả tuần đọc về Firepower/Umbrella/Zero Trust (mục 5.5, chỉ "describe",
> và rất hấp dẫn) rồi ⭐ **không cấu hình nổi một method list AAA có fallback** (mục 5.1, "configure").

| Chủ đề | Blueprint | ⭐ Mức cần đạt | Thời gian |
|---|---|---|---|
| 🔴 ⭐⭐ **Lines & password protection** | ⭐⭐ **5.1.a Configure** | ⭐ **Gõ được**: password type, privilege level, SSH, `login block-for`, banner | 1.5 giờ |
| 🔴 ⭐⭐ **AAA (authn + authz)** | ⭐⭐ **5.1.b Configure** | ⭐⭐ **Method list + fallback + TACACS+ vs RADIUS.** ⭐ **Trọng tâm số 1** | 2 giờ |
| 🔴 ⭐⭐ **ACL nâng cao** | ⭐⭐ **5.2.a Configure** | ⭐ Named ACL + sequence · time-based · `established` · ⭐ **bẫy IPv6 ACL** · PACL/VACL/RACL | 2 giờ |
| 🔴 ⭐⭐ **CoPP** | ⭐⭐ **5.2.b Configure** | ⭐ MQC áp lên `control-plane` · ⭐ **vì sao phải bắt đầu ở chế độ "chỉ đếm"** | 1.5 giờ |
| 🟡 **REST API security** | 🟡 **5.3 Describe** | ⭐ Token flow · **401 vs 403** · HTTPS · rate limit | 45 phút |
| 🔴 ⭐⭐ **Wireless security** | ⭐⭐ **5.4 Configure** | ⭐ **PSK/SAE · EAP · WebAuth trên C9800** *(nối tiếp [07B §8](Module-07B-CAPWAP-WLC-FlexConnect-Roaming.md))* | 1.5 giờ |
| ⭐⭐ **NAC: 802.1X / MAB / WebAuth** | 🟡 5.5.e *Describe*<br>⭐ (nhưng 5.1.b + 5.4 kéo nó thành **configure**) | ⭐⭐ **3 vai · luồng EAPoL · host mode · guest/critical VLAN · monitor mode** | 2 giờ |
| ⭐ **TrustSec & MACsec** | 🟡 **5.5.d Describe** | ⭐ **3 pha TrustSec** · ⭐ **MACsec L2 hop-by-hop vs IPsec L3 end-to-end** | 1 giờ |
| 🟡 **Threat defense · Endpoint · NGFW** | 🟡 **5.5.a/b/c Describe** | ⭐ **NGFW khác firewall thường** · **IDS vs IPS** · biết tên sản phẩm Cisco | 1 giờ |

### 0.2 ⭐ Ba mối nối với những gì bạn đã học

| Nối với | Chỗ nào |
|---|---|
| ⭐ **[Module-09 §7.6](Module-09-Architecture-va-QoS.md)** — SD-Access | ⭐⭐ **TrustSec/SGT ở §8 CHÍNH LÀ policy plane của SD-Access** |
| ⭐ **[Module-07B §8](Module-07B-CAPWAP-WLC-FlexConnect-Roaming.md)** — wireless security | ⭐ Ở đó là "vừa đủ để troubleshoot", ⭐ **ở đây là cấu hình thật** |
| ⭐ **[Module-01 §2](Module-01-Packet-Forwarding-va-Kien-truc-Thiet-bi.md)** — 3 plane | ⭐⭐ **CoPP ở §5 bảo vệ đúng cái "control plane" bạn học ở M01** |
| ⭐ **[Module-06B §3](Module-06B-NAT-NTP-Multicast.md)** — NTP | ⭐ Chứng thư EAP-TLS và log an ninh **vô nghĩa nếu sai giờ** |
| ⭐ **Module-12** (Automation) | ⭐ REST API security ở §10 là **nền** cho việc gọi API DNAC/vManage |

---

## ✅ 1. Chuẩn bị

| Cần có | Chi tiết |
|---|---|
| **Kiến thức trước** | Module-P0 §2.8 (ACL cơ bản) · Module-01 §2 (control/data/management plane) · Module-02 (VLAN, trunk, PortFast) · Module-07B §8 (wireless security ở mức khái niệm) |
| **Lab** | ⭐ **EVE-NG**: `R1`, `R2` (vIOS 512 MB) + `SW1` (vIOS-L2 768 MB) |
| **RAM** | ⭐ **~1.8 GB** ✅ |
| **Tùy chọn** | ⭐ Một máy **Linux chạy FreeRADIUS** (hoặc **NPS trên Windows**) nếu muốn lab 802.1X đầy đủ — ⭐ **xem §1.1, có phương án thay thế không cần server** |
| **Thời lượng** | 6h lý thuyết · 5h lab · 1h quiz |

### 1.1 ⭐ Nếu bạn không có RADIUS server — vẫn lab được 80%

| Nội dung | Cần RADIUS thật? | ⭐ Phương án không cần server |
|---|:---:|---|
| Password type, privilege level, SSH, banner | ❌ | ⭐ Lab đầy đủ |
| ⭐⭐ **AAA method list + fallback** | ❌ | ⭐⭐ **Trỏ vào một IP KHÔNG TỒN TẠI** → server "chết" → ⭐ **quan sát fallback sang `local`.** ⭐ **Đây chính là điểm đề hỏi!** |
| ACL nâng cao, uRPF | ❌ | ⭐ Lab đầy đủ |
| CoPP | ❌ | ⭐ Lab đầy đủ |
| ⭐ **802.1X trên switch** | ⚠️ Một phần | ⭐ Cấu hình xong, ⭐ **quan sát port ở trạng thái `Unauthorized`**, rồi ⭐ **tái hiện critical VLAN khi RADIUS chết**. ⭐ Vẫn học được máy trạng thái |
| Wireless security (C9800) | ❌ | ⭐ **DevNet Sandbox** — chỉ xem cấu hình |

> ⭐ **Kết luận:** ⭐ **đừng để việc thiếu RADIUS chặn bạn.** ⭐ Lab "server chết → fallback" thậm chí
> **giá trị hơn** lab "server sống → đăng nhập thành công", vì ⭐ **đề hỏi đúng cái tình huống hỏng.**

---

## 📘 2. DEVICE ACCESS CONTROL (blueprint 5.1.a — CONFIGURE)

### 2.1 ⭐ Ba đường vào thiết bị

| Line | Là gì | ⭐ Rủi ro |
|---|---|---|
| ⭐ **Console** (`line con 0`) | Cổng vật lý | ⭐ Cần tiếp cận vật lý — ⭐ **nhưng nhiều người quên đặt mật khẩu cho nó** |
| ⭐⭐ **VTY** (`line vty 0 15`) | ⭐ **Telnet/SSH qua mạng** | ⭐⭐ **Rủi ro cao nhất — ai cũng thử được từ xa** |
| ⭐ **AUX** (`line aux 0`) | Cổng phụ (modem đời cũ) | 🔴 ⭐ **Hầu như không dùng → PHẢI TẮT HẲN** |

```
! Tắt AUX — việc hardening đầu tiên ai cũng quên
line aux 0
 no exec
 transport input none
```

### 2.2 ⭐⭐ Các loại mật khẩu — bảng phải nhớ

| Type | Thuật toán | ⭐ An toàn? | Ghi chú |
|:---:|---|:---:|---|
| **0** | ⭐ **Không mã hóa — plaintext** | 🔴 ❌ | Hiện nguyên văn trong config |
| **4** | SHA-256 (bản cài đặt lỗi) | 🔴 ❌ | ⭐ **Cisco đã gỡ bỏ** |
| ⭐ **5** | ⭐ **MD5 có salt** | 🟡 Yếu | ⭐ Rất phổ biến (`enable secret`), nhưng MD5 đã lỗi thời |
| 🔴 ⭐⭐ **7** | ⭐⭐ **Vigenère — MÃ HÓA ĐẢO NGƯỢC ĐƯỢC** | 🔴 ⭐⭐ **KHÔNG AN TOÀN** | ⭐ **Chỉ để che mắt người đứng sau lưng.** ⭐ Có hàng chục web giải mã trong 1 giây |
| ⭐ **8** | ⭐ **PBKDF2 + SHA-256** | ✅ **Tốt** | ⭐ Nên dùng |
| ⭐⭐ **9** | ⭐⭐ **scrypt** | ✅ ⭐ **Tốt nhất** | ⭐⭐ **Khuyến nghị hiện nay** |

```
! KHÔNG BAO GIỜ dùng — type 7 hoặc plaintext
enable password Cisco123

! 🟡 Chấp nhận được (type 5 - MD5)
enable secret Cisco123

! ĐÚNG — type 9 (scrypt)
enable algorithm-type scrypt secret MatKhauRatDaiVaKho2026
username admin privilege 15 algorithm-type scrypt secret MatKhauRatDaiVaKho2026

! Kiểm chứng — nhìn số ngay sau dấu $
R1# show running-config | include enable secret|username
enable secret 9 $9$xxxxx...          ! số 9 = scrypt ✅
username admin privilege 15 secret 9 $9$yyyy...
```

> 🔴 ⭐⭐ **Hai bẫy về mật khẩu, đề hỏi cả hai:**
> 1. ⭐⭐ **`service password-encryption` CHỈ tạo ra type 7** — ⭐ **nó là "che mắt", KHÔNG phải bảo mật.**
>    ⭐ Vẫn nên bật (để mật khẩu không nằm trần trong config), ⭐ **nhưng đừng tin nó.**
> 2. ⭐⭐ **`enable secret` LUÔN THẮNG `enable password`** khi cả hai cùng tồn tại.
>    ⭐ Nên: ⭐ **xóa hẳn `enable password`**, chỉ giữ `enable secret`.

```
! Vài lệnh hardening mật khẩu khác
service password-encryption               ! che type 0 → type 7 (cosmetic)
security passwords min-length 10          ! ép độ dài tối thiểu
no enable password                        ! xóa cái yếu, chỉ giữ enable secret
```

### 2.3 ⭐ Privilege level & Role-Based CLI

| Level | Mặc định là gì |
|:---:|---|
| ⭐ **0** | Chỉ 5 lệnh: `disable`, `enable`, `exit`, `help`, `logout` |
| ⭐ **1** | ⭐ **User EXEC** — dấu nhắc `>`, chỉ xem được vài thứ |
| **2–14** | ⭐ **Trống — bạn tự định nghĩa** |
| ⭐ **15** | ⭐ **Privileged EXEC** — dấu nhắc `#`, toàn quyền |

```
! Tạo level 5 chỉ cho xem — dành cho helpdesk
privilege exec level 5 show running-config
privilege exec level 5 show interfaces
privilege exec level 5 ping
enable algorithm-type scrypt secret level 5 MatKhauHelpdesk
!
username helpdesk privilege 5 algorithm-type scrypt secret MatKhau123
```

⭐ **Role-Based CLI Access (parser view)** — mịn hơn privilege level:
```
aaa new-model                             ! BẮT BUỘC có trước
enable view                               ! vào chế độ root view
!
parser view HELPDESK
 secret MatKhauView
 commands exec include show interfaces
 commands exec include show ip interface brief
 commands exec include ping
!
parser view MONITOR superview             ! superview = gộp nhiều view
 secret MatKhauSuper
 view HELPDESK
```
```
show parser view                          ! đang ở view nào
enable view HELPDESK                      ! chuyển sang view
```

> ⭐ **Thực tế:** ⭐ **hầu như không ai dùng privilege level tùy chỉnh nữa** —
> ⭐ **người ta dùng TACACS+ command authorization** (§3) vì nó quản tập trung.
> ⭐ **Nhưng đề vẫn hỏi khái niệm level 0/1/15.**

### 2.4 ⭐⭐ SSH — cấu hình chuẩn

```
! ─── ① Bốn thứ BẮT BUỘC để sinh được khóa RSA ───
hostname R1                               ! (1) không được là "Router"
ip domain-name cty.local                  ! (2) bắt buộc
crypto key generate rsa modulus 2048      ! (3) ≥ 2048 bit
username admin privilege 15 algorithm-type scrypt secret MatKhauRatDai   ! (4)

! ─── ② Ép SSH v2 và siết tham số ───
ip ssh version 2                          ! v1 có lỗ hổng — LUÔN ép v2
ip ssh time-out 60
ip ssh authentication-retries 3

! ─── ③ Khóa VTY lại ───
line vty 0 15
 transport input ssh                      ! CHỈ SSH — cấm telnet
 login local                              ! (hoặc: login authentication <method-list>)
 exec-timeout 5 0                         ! tự thoát sau 5 phút không gõ
 access-class ACL-MGMT in                 ! CHỈ cho phép IP quản trị
!
ip access-list standard ACL-MGMT
 permit 10.99.0.0 0.0.0.255
 deny   any log

! ─── ④ Chống dò mật khẩu ───
login block-for 120 attempts 3 within 60  ! sai 3 lần trong 60s → KHÓA 120s
login quiet-mode access-class ACL-MGMT    ! admin vẫn vào được trong lúc bị khóa
login on-failure log
login on-success log

! ─── ⑤ Banner — đây là vấn đề PHÁP LÝ ───
banner login ^
  CANH BAO: He thong rieng. Chi nguoi duoc uy quyen. Moi hoat dong bi ghi log.
^
```

> 🔴 ⭐⭐ **Banner là vấn đề pháp lý, không phải trang trí.**
> ⭐ **KHÔNG BAO GIỜ viết "Welcome"** — ⭐ ở nhiều nơi, chữ "chào mừng" có thể bị luật sư bên bị
> dùng để lập luận rằng ⭐ **hệ thống đã MỜI kẻ tấn công vào**. ⭐ **Phải là lời CẢNH BÁO.**

⭐ **Verify:**
```
show ip ssh                               ! version, timeout, retries
show ssh                                  ! phiên SSH đang mở
show crypto key mypubkey rsa              ! đã có khóa chưa, bao nhiêu bit
show login                                ! trạng thái login block-for
show users                                ! ai đang đăng nhập
```

### 2.5 ⭐ Checklist hardening — bảng dùng được ngoài đời

| # | Việc | Lệnh |
|:---:|---|---|
| 1 | ⭐ **Tắt dịch vụ không dùng** | `no ip http server` · `no ip http secure-server` *(hoặc siết bằng ACL)* |
| 2 | ⭐ Tắt dịch vụ cũ nguy hiểm | `no service tcp-small-servers` · `no service udp-small-servers` · `no ip finger` · `no service pad` |
| 3 | ⭐ Tắt source routing | `no ip source-route` |
| 4 | ⭐⭐ **Tắt CDP/LLDP trên port ra ngoài** | `no cdp enable` *(trên interface)* — ⭐ CDP tiết lộ model, IOS version, IP |
| 5 | ⭐ Tắt proxy-ARP nếu không cần | `no ip proxy-arp` |
| 6 | ⭐ Tắt ICMP redirect / unreachable trên port ngoài | `no ip redirects` · `no ip unreachables` |
| 7 | ⭐⭐ **Tắt AUX** | `line aux 0` → `no exec` |
| 8 | ⭐⭐ **Chỉ SSH, cấm Telnet** | `transport input ssh` |
| 9 | ⭐⭐ **exec-timeout trên MỌI line** | `exec-timeout 5 0` |
| 10 | ⭐ Chống dò mật khẩu | `login block-for ...` |
| 11 | ⭐⭐ **NTP + logging** | *(Module-06B + Module-11)* — ⭐ **log sai giờ = log vô dụng** |
| 12 | ⭐ Bảo vệ config | `secure boot-image` · `secure boot-config` *(Resilient Configuration)* |
| 13 | ⭐⭐ **Banner cảnh báo** | `banner login` |
| 14 | ⭐ Ép mật khẩu mạnh | `security passwords min-length` · `algorithm-type scrypt` |

---

## 📘 3. 🔴 ⭐⭐ AAA (blueprint 5.1.b — CONFIGURE) — trọng tâm số 1 của module

### 3.1 ⭐ Ba chữ A

| A | Câu hỏi nó trả lời | Ví dụ |
|---|---|---|
| ⭐⭐ **Authentication** (xác thực) | ⭐ **"Anh là AI?"** | Đúng username/password/chứng thư không |
| ⭐⭐ **Authorization** (phân quyền) | ⭐ **"Anh được LÀM GÌ?"** | Được vào enable mode? Được gõ lệnh `reload`? |
| ⭐ **Accounting** (ghi nhận) | ⭐ **"Anh ĐÃ LÀM GÌ?"** | Log lại từng lệnh đã gõ, thời gian phiên |

### 3.2 ⭐⭐ TACACS+ vs RADIUS — bảng ĐỀ HỎI NHIỀU NHẤT

| | ⭐⭐ **TACACS+** | ⭐⭐ **RADIUS** |
|---|---|---|
| ⭐ **Giao thức / port** | ⭐⭐ **TCP 49** | ⭐⭐ **UDP 1812** (auth) / **1813** (acct)<br>*(đời cũ: 1645/1646)* |
| ⭐⭐ **Mã hóa** | ⭐⭐ **TOÀN BỘ phần thân gói** | 🔴 ⭐⭐ **CHỈ mã hóa trường PASSWORD** — phần còn lại đi trần |
| ⭐⭐ **Tách 3 chữ A** | ⭐⭐ **TÁCH RIÊNG cả ba** | 🔴 ⭐ **GỘP Authentication + Authorization** |
| **Chuẩn** | ⭐ **Cisco độc quyền** | ⭐ **Chuẩn mở (RFC 2865/2866)** |
| ⭐⭐ **Command authorization** | ⭐⭐ **CÓ — cho phép/cấm TỪNG LỆNH** | 🔴 ⭐ **Không** (chỉ gán quyền thô) |
| ⭐⭐ **Hợp nhất với** | ⭐⭐ **Quản trị THIẾT BỊ** (ai được SSH vào router và gõ lệnh gì) | ⭐⭐ **Truy nhập MẠNG** (802.1X, wireless, VPN) |
| Đa giao thức | ✅ (IP, và cả non-IP đời cũ) | Chủ yếu IP |
| Sản phẩm Cisco | ⭐ **ISE**, ACS *(cũ)* | ⭐ **ISE**, FreeRADIUS, Windows NPS |

> 🔴 ⭐⭐ **Câu chốt phải thuộc — đề hỏi đi hỏi lại:**
> ⭐ **"TACACS+ để QUẢN TRỊ THIẾT BỊ. RADIUS để CHO NGƯỜI DÙNG VÀO MẠNG."**
> ⭐ **"TACACS+ mã hóa TẤT CẢ, TCP 49, tách cả 3 A, có command authorization."**
> ⭐ **"RADIUS chỉ mã hóa MẬT KHẨU, UDP 1812/1813, gộp authn+authz."**
>
> ⭐ **Mẹo nhớ port:** ⭐ **TACACS+ = TCP = 49** (cùng vần "T"). ⭐ **RADIUS = UDP = 1812/1813.**

### 3.3 ⭐⭐ Cấu hình AAA — mẫu đầy đủ

```
!═══════ ① BẬT AAA ═══════
! TẠO USER LOCAL TRƯỚC KHI GÕ DÒNG NÀY — xem cảnh báo §3.5
username admin privilege 15 algorithm-type scrypt secret MatKhauCuuHo2026
!
aaa new-model                             ! dòng bật toàn bộ hệ thống AAA

!═══════ ② KHAI BÁO SERVER ═══════
! ─── TACACS+ (cho quản trị thiết bị) ───
tacacs server ISE-TAC-1
 address ipv4 10.99.1.10
 key SecretTacacs2026
 timeout 3
!
aaa group server tacacs+ GRP-TAC
 server name ISE-TAC-1
 ip tacacs source-interface Loopback0     ! nguồn cố định — server dễ khai ACL

! ─── RADIUS (cho 802.1X / wireless) ───
radius server ISE-RAD-1
 address ipv4 10.99.1.10 auth-port 1812 acct-port 1813
 key SecretRadius2026
 timeout 3
 retransmit 2
 automate-tester username probe-user probe-on   ! tự dò server sống/chết
!
aaa group server radius GRP-RAD
 server name ISE-RAD-1
 ip radius source-interface Loopback0

!═══════ ③ METHOD LIST — phần quan trọng nhất ═══════
! ─── Authentication ───
aaa authentication login  default group GRP-TAC local
!                         ↑ tên list      ↑ thử TACACS+ trước   ↑ HỎNG thì dùng local
aaa authentication enable default group GRP-TAC enable
aaa authentication dot1x  default group GRP-RAD

! ─── Authorization ───
aaa authorization exec     default group GRP-TAC local if-authenticated
aaa authorization commands 15 default group GRP-TAC local
aaa authorization network  default group GRP-RAD        ! cho 802.1X (VLAN/dACL/SGT)
aaa authorization config-commands

! ─── Accounting ───
aaa accounting exec        default start-stop group GRP-TAC
aaa accounting commands 15 default start-stop group GRP-TAC
aaa accounting dot1x       default start-stop group GRP-RAD

!═══════ ④ ÁP LÊN LINE (nếu dùng named list) ═══════
line vty 0 15
 login authentication default             ! dùng list "default" thì có thể bỏ dòng này
 authorization exec default
 transport input ssh
```

### 3.4 ⭐⭐ Method list — hiểu cho đúng

```
   aaa authentication login  default  group GRP-TAC  local
   └──────┬──────────────┘   └──┬──┘  └──────┬────┘  └─┬─┘
       loại xác thực       tên list      PHƯƠNG PHÁP 1  PHƯƠNG PHÁP 2
                                         (thử trước)    (dự phòng)
```

| ⭐ Quy tắc | Chi tiết |
|---|---|
| ⭐⭐ **Thử lần lượt từ trái sang phải** | Hết phương pháp 1 mới sang 2 |
| 🔴 ⭐⭐ **CHỈ chuyển sang phương pháp sau khi phương pháp trước KHÔNG TRẢ LỜI** | ⭐⭐ **Server trả lời "SAI MẬT KHẨU" là ĐÃ TRẢ LỜI → DỪNG, KHÔNG fallback!**<br>⭐ Chỉ khi server **im lặng/chết** mới sang `local` |
| ⭐ **`default`** | ⭐ Áp cho **MỌI line** tự động |
| ⭐ **Named list** | Phải ⭐ **gán thủ công** lên line/interface mới có tác dụng |

⭐ **Các phương pháp hay dùng:**

| Phương pháp | Nghĩa |
|---|---|
| `group GRP-TAC` / `group tacacs+` | Hỏi nhóm server / tất cả server TACACS+ |
| ⭐ `local` | ⭐ **Dùng `username` trong config** *(phân biệt hoa-thường)* |
| `local-case` | Như trên nhưng bắt buộc đúng hoa-thường |
| ⭐ `enable` | Dùng `enable secret` |
| ⭐ `line` | Dùng mật khẩu đặt trên chính line đó |
| ⭐ `none` | 🔴 **Không xác thực gì cả** — ⭐ chỉ dùng cho console trong lab |
| ⭐ `if-authenticated` | ⭐ *(authorization)* — đã xác thực xong thì cho qua |

### 3.5 🔴 ⭐⭐ CẢNH BÁO: cách tự khóa mình ra khỏi thiết bị

> 🔴 ⭐⭐ **Đây là tai nạn phổ biến nhất khi triển khai AAA. Đọc kỹ.**

```
! KỊCH BẢN CHẾT NGƯỜI
R1(config)# aaa new-model
!  Ngay lập tức: mọi line chuyển sang dùng method list "default"
!  Mà bạn CHƯA tạo user local nào
!  → Lần đăng nhập sau: KHÔNG CÓ TÀI KHOẢN NÀO ĐỂ DÙNG
!  → MẤT THIẾT BỊ (phải password recovery tại chỗ)
```

| ⭐ Bốn quy tắc vàng khi triển khai AAA |
|---|
| ⭐⭐ **1. TẠO USER LOCAL TRƯỚC** khi gõ `aaa new-model` |
| ⭐⭐ **2. LUÔN có `local` ở cuối method list** — server chết vẫn vào được |
| ⭐⭐ **3. GIỮ MỘT PHIÊN SSH ĐANG MỞ** trong lúc cấu hình — nếu hỏng thì còn đường sửa |
| ⭐⭐ **4. TEST TRƯỚC bằng `test aaa`**, đừng logout rồi mới biết |

```
! Bảo vệ console riêng — nhiều nơi để console dùng local, không qua AAA server
aaa authentication login CONSOLE-LOCAL local
line con 0
 login authentication CONSOLE-LOCAL
```

### 3.6 ⭐ Verify & troubleshoot AAA

```
! TEST TRƯỚC KHI LOGOUT — lệnh cứu mạng
test aaa group GRP-TAC admin MatKhau legacy
test aaa group GRP-RAD admin MatKhau new-code

show aaa servers                          ! server sống hay chết + thống kê
show aaa sessions
show aaa method-lists all
show tacacs                               ! số gói gửi/nhận, lỗi
show radius statistics

debug aaa authentication                  ! ⚠️ chỉ trong lab
debug aaa authorization
debug tacacs
debug radius authentication
```

⭐ **Đọc `show aaa servers` — dòng cần nhìn:**
```
RADIUS: id 1, priority 1, host 10.99.1.10, auth-port 1812, acct-port 1813
     State: current UP, duration 3520s, previous duration 0s
     Dead: total time 0s, count 0                 ← count > 0 = server từng chết
     Authen: request 24, timeouts 0, failover 0, retransmission 0
             Response: accept 22, reject 2        ← reject = sai mật khẩu (server CÓ trả lời)
```

> 🔴 ⭐⭐ **Phân biệt hai loại "đăng nhập thất bại" — đây là chỗ đề gài:**
>
> | Quan sát | ⭐ Nghĩa | ⭐ Có fallback sang `local` không |
> |---|---|---|
> | ⭐ `reject` tăng | ⭐ **Server TRẢ LỜI: sai mật khẩu** | 🔴 ⭐⭐ **KHÔNG** — server đã trả lời rồi |
> | ⭐ `timeouts` tăng · `State: DEAD` | ⭐ **Server IM LẶNG / chết / sai key / firewall chặn** | ⭐⭐ **CÓ — chuyển sang `local`** |
>
> ⭐ **Sai shared key thì biểu hiện giống hệt "server chết"** — vì router không giải mã được câu trả lời.

---

## 📘 4. 🔴 ⭐⭐ ACL NÂNG CAO (blueprint 5.2.a — CONFIGURE)

> ⭐ ACL cơ bản đã học ở [Module-P0 §2.8](Module-P0-Nen-tang-Ready-for-ENCOR.md). ⭐ **Đây là phần NÂNG CAO.**

### 4.1 ⭐ Ôn nhanh 5 điều nền tảng

| # | Điều phải nhớ |
|:---:|---|
| 1 | ⭐⭐ **Xử lý TỪ TRÊN XUỐNG, KHỚP DÒNG NÀO DỪNG DÒNG ĐÓ** |
| 2 | ⭐⭐ **Cuối mỗi ACL luôn có `deny ip any any` NGẦM** — ⭐ không hiện trong config, ⭐ **không đếm, không log** |
| 3 | ⭐ **Wildcard mask là mặt NGƯỢC của subnet mask**: `0.0.0.255` ↔ /24 · `host X` = `X 0.0.0.0` · `any` = `0.0.0.0 255.255.255.255` |
| 4 | ⭐⭐ **Standard ACL** (chỉ khớp SOURCE) → ⭐ **đặt GẦN ĐÍCH**<br>⭐⭐ **Extended ACL** (khớp cả hai) → ⭐ **đặt GẦN NGUỒN** |
| 5 | ⭐ Dải số: **1–99 / 1300–1999** = standard · **100–199 / 2000–2699** = extended. ⭐ **Nhưng hãy dùng named ACL** |

⭐ **Vì sao standard đặt gần đích:** vì nó **chỉ biết source** → đặt gần nguồn sẽ ⭐ **chặn nhầm cả traffic
đi tới những nơi lẽ ra được phép.**

### 4.2 ⭐⭐ Named ACL & sequence number — sửa ACL mà không phải xóa hết

```
ip access-list extended ACL-DMZ-IN
 10 permit tcp any host 203.0.113.10 eq 443
 20 permit tcp any host 203.0.113.10 eq 80
 30 permit udp any host 203.0.113.11 eq 53
 40 deny   ip any any log                  ! deny TƯỜNG MINH để có bộ đếm + log
```

```
! CHÈN một dòng vào GIỮA — không cần gõ lại cả ACL
R1(config)# ip access-list extended ACL-DMZ-IN
R1(config-ext-nacl)# 15 permit tcp any host 203.0.113.10 eq 8443

! XÓA đúng một dòng
R1(config-ext-nacl)# no 30

! ĐÁNH SỐ LẠI cho gọn (bắt đầu 10, bước 10)
R1(config)# ip access-list resequence ACL-DMZ-IN 10 10
```

> 🔴 ⭐⭐ **Đây là lý do LUÔN dùng named ACL:** ⭐ với **numbered ACL**, gõ thêm một dòng là nó
> **luôn nối vào CUỐI** — ⭐ **mà cuối thì đã có `deny` rồi → dòng mới vô dụng.**
> ⭐ Muốn sửa numbered ACL kiểu cũ thì phải **xóa cả ACL rồi gõ lại** — 🔴 ⭐ **và trong khoảng thời gian
> đó interface không có ACL → hở toang.**

⭐ **Luôn để `deny ip any any log` TƯỜNG MINH ở cuối** — vì:
- ⭐ **Deny ngầm KHÔNG đếm** → bạn không biết ACL đang chặn bao nhiêu
- ⭐ **Deny ngầm KHÔNG log** → không điều tra được

### 4.3 ⭐ Các loại ACL nâng cao

#### ⭐ `established` — cho phép traffic TRẢ VỀ

```
ip access-list extended ACL-INTERNET-IN
 permit tcp any 10.1.0.0 0.0.255.255 established
 deny   ip any any log
```
⭐ **`established` khớp gói TCP có cờ ACK hoặc RST** → tức là ⭐ **gói TRẢ LỜI cho một phiên do bên trong khởi tạo.**
🔴 ⭐ **Nhược điểm: nó CHỈ nhìn cờ, không theo dõi trạng thái thật** → kẻ tấn công tự đặt cờ ACK vẫn lọt.
⭐ **Chỉ là "giả stateful". Muốn stateful thật thì dùng firewall (ZBFW/ASA/FTD).**

#### ⭐ Time-based ACL

```
time-range GIO-HANH-CHINH
 periodic weekdays 08:00 to 18:00
!
time-range BAO-TRI
 absolute start 00:00 1 January 2026 end 23:59 31 January 2026
!
ip access-list extended ACL-USER
 permit tcp 10.1.10.0 0.0.0.255 any eq 443 time-range GIO-HANH-CHINH
 deny   ip any any log
```
> 🔴 ⭐ **Time-based ACL phụ thuộc hoàn toàn vào ĐỒNG HỒ** → ⭐ **bắt buộc phải có NTP** *(Module-06B §3)*.
> ⭐ Kiểm tra bằng `show time-range` — xem nó đang `active` hay `inactive`.

#### ⭐ Reflexive ACL — stateful "nhà nghèo"

```
ip access-list extended ACL-OUT
 permit tcp 10.1.0.0 0.0.255.255 any reflect PHIEN-TCP
 permit udp 10.1.0.0 0.0.255.255 any reflect PHIEN-UDP
!
ip access-list extended ACL-IN
 evaluate PHIEN-TCP
 evaluate PHIEN-UDP
 deny ip any any log
!
interface GigabitEthernet0/0
 ip access-group ACL-OUT out
 ip access-group ACL-IN  in
```
⭐ **Tốt hơn `established`** vì nó **thực sự tạo entry tạm** cho từng phiên (và làm được với UDP/ICMP),
⭐ **nhưng vẫn kém xa firewall thật.**

#### ⭐ Object group — làm ACL đọc được

```
object-group network MANG-NOI-BO
 10.1.10.0 255.255.255.0
 10.1.20.0 255.255.255.0
!
object-group network SERVER-WEB
 host 203.0.113.10
 host 203.0.113.11
!
object-group service DICH-VU-WEB
 tcp eq 80
 tcp eq 443
!
ip access-list extended ACL-GON
 permit object-group DICH-VU-WEB object-group MANG-NOI-BO object-group SERVER-WEB
 deny   ip any any log
```
⭐ **Một dòng thay cho 12 dòng.** ⭐ Thêm subnet mới → ⭐ **chỉ sửa object-group, không đụng vào ACL.**

### 4.4 🔴 ⭐⭐ IPv6 ACL — BẪY LỚN NHẤT của mục 5.2.a

| | IPv4 ACL | ⭐ **IPv6 ACL** |
|---|---|---|
| Đặt tên | Numbered hoặc named | ⭐ **CHỈ named** |
| Áp lên interface | `ip access-group X in` | ⭐ **`ipv6 traffic-filter X in`** |
| Wildcard mask | ⭐ Có | ⭐ **KHÔNG — dùng prefix `/64`** |
| ⭐⭐ **Cuối ACL ngầm có gì** | ⭐ `deny ipv4 any any` | 🔴 ⭐⭐ **BA dòng ngầm** *(xem dưới)* |

```
   CUỐI MỖI IPv6 ACL, IOS TỰ THÊM BA DÒNG NGẦM THEO ĐÚNG THỨ TỰ NÀY:

      permit icmp any any nd-na       Neighbor Advertisement
      permit icmp any any nd-ns       Neighbor Solicitation
      deny   ipv6 any any
```

> 🔴 ⭐⭐ **BẪY:** ⭐ **NDP là "ARP của IPv6"** — chặn nó là ⭐ **toàn bộ IPv6 chết**.
> ⭐ IOS tự cho phép NDP đi qua, **nhưng chỉ khi bạn KHÔNG viết `deny` tường minh.**
>
> ```
> ipv6 access-list ACL-V6-SAI
>  permit tcp any 2001:db8:1::/64 eq 443
>  ⭐ deny ipv6 any any log            ! 🔴 DÒNG NÀY GIẾT NDP
> ! → Hai dòng permit nd-na/nd-ns NGẦM nằm SAU dòng deny này → không bao giờ tới lượt
> ! → Không phân giải được địa chỉ lớp 2 → IPv6 NGỪNG HOẠT ĐỘNG HOÀN TOÀN
> ```
> ```
> ipv6 access-list ACL-V6-DUNG
>  ⭐ permit icmp any any nd-na        ! ⭐ TỰ VIẾT LẠI TRƯỚC
>  ⭐ permit icmp any any nd-ns
>  permit tcp any 2001:db8:1::/64 eq 443
>  deny ipv6 any any log              ! ✅ giờ mới an toàn
> ```
> ⭐⭐ **Quy tắc: nếu viết `deny ipv6 any any` tường minh, PHẢI tự thêm hai dòng NDP lên TRƯỚC.**

### 4.5 ⭐⭐ PACL / VACL / RACL — ba loại ACL trên switch

| Loại | Áp ở đâu | Lọc traffic nào |
|---|---|---|
| ⭐ **PACL** (Port ACL) | ⭐ **Port L2 vật lý** (`ip access-group` trên switchport) | ⭐ Traffic **VÀO** port đó. ⭐ **Chỉ chiều inbound** |
| ⭐ **VACL** (VLAN map) | ⭐ **Cả VLAN** (`vlan filter`) | ⭐⭐ **Cả traffic BRIDGED trong cùng VLAN** — ⭐ điều RACL **không** làm được |
| ⭐ **RACL** (Router ACL) | ⭐ **SVI hoặc routed port** | ⭐ Traffic **ĐƯỢC ĐỊNH TUYẾN** (giữa các VLAN) |

```
   THỨ TỰ XỬ LÝ — chiều VÀO (ingress):
      PACL  →  VACL  →  RACL
   
   Chiều RA (egress):
      RACL  →  VACL  →  (không có PACL egress)
```

```
! VACL — chặn 2 máy trong CÙNG VLAN nói chuyện với nhau
ip access-list extended ACL-CHAN-NOI-BO
 permit ip host 10.1.10.50 host 10.1.10.51
!
vlan access-map VMAP-10 10
 match ip address ACL-CHAN-NOI-BO
 action drop
vlan access-map VMAP-10 20
 action forward                          ! BẮT BUỘC — nếu không, mọi thứ khác bị drop
!
vlan filter VMAP-10 vlan-list 10
```

> 🔴 ⭐⭐ **Hai bẫy VACL:**
> 1. ⭐⭐ **VACL kết thúc bằng `drop` ngầm** → ⭐ **phải luôn có một map cuối `action forward`**,
>    nếu không bạn **chặn sạch cả VLAN**.
> 2. ⭐⭐ **VACL là thứ DUY NHẤT lọc được traffic trong CÙNG một VLAN** —
>    ⭐ RACL không thấy traffic đó vì nó **không đi qua router**.

### 4.6 ⭐ uRPF — chống giả mạo địa chỉ nguồn

```
interface GigabitEthernet0/0
 ip verify unicast source reachable-via rx        ! STRICT mode
 !  ip verify unicast source reachable-via any      ! LOOSE mode
```

| Mode | Kiểm tra gì | ⭐ Dùng khi |
|---|---|---|
| ⭐ **Strict (`rx`)** | ⭐ **Có route về source KHÔNG, VÀ route đó có trỏ đúng interface gói vừa đến không?** | ⭐ Mạng **đối xứng** (một đường vào ra) — VD port access, chi nhánh 1 đường |
| ⭐ **Loose (`any`)** | ⭐ **Chỉ cần CÓ route về source** (bất kể interface nào) | ⭐ Mạng **bất đối xứng** / multihoming — VD router biên có nhiều ISP |

> 🔴 ⭐ **Bật strict mode ở nơi định tuyến bất đối xứng = tự drop traffic hợp lệ.**
> ⭐ **Không chắc thì dùng loose**, hoặc bật **strict chỉ ở port access hướng người dùng.**

⭐ **Infrastructure ACL (iACL):** ở router biên, ⭐ **chặn mọi traffic từ Internet đi TỚI dải địa chỉ
hạ tầng của bạn** (loopback, link giữa các router), ⭐ **chỉ cho phép traffic ĐI XUYÊN QUA.**
⭐ Đây là lớp bảo vệ trước khi CoPP phải ra tay.

### 4.7 ⭐ Verify ACL

```
show access-lists                         ! bộ đếm match từng dòng
show access-lists ACL-DMZ-IN
show ip access-lists
show ip interface Gi0/0 | include access list     ! ACL nào đang áp, chiều nào
show ipv6 access-list
show vlan access-map                      ! VACL
show vlan filter                          ! VACL áp lên VLAN nào
show time-range                           ! time-range đang active chưa
clear ip access-list counters ACL-DMZ-IN  ! reset bộ đếm trước khi test
show ip interface Gi0/0 | include verify  ! uRPF
show cef interface Gi0/0 internal | include RPF
```

> ⭐⭐ **Kỹ thuật troubleshoot ACL số 1:**
> ⭐ **`clear ip access-list counters` → tạo traffic → `show access-lists`.**
> ⭐ **Dòng nào có bộ đếm tăng chính là dòng đang quyết định số phận gói tin.**
> ⭐ Nếu **không dòng nào tăng** → gói **không tới interface đó** hoặc **áp sai chiều.**

---

## 📘 5. 🔴 ⭐⭐ CoPP (blueprint 5.2.b — CONFIGURE)

### 5.1 ⭐ Vấn đề CoPP giải quyết

> ⭐ Nhắc lại [Module-01 §2](Module-01-Packet-Forwarding-va-Kien-truc-Thiet-bi.md):
> ⭐ **Data plane** = ASIC/CEF, **cực nhanh**. ⭐ **Control plane** = CPU, **chậm hơn hàng nghìn lần**.

```
   KỊCH BẢN TẤN CÔNG (hoặc chỉ là một vòng lặp lỗi):

   Kẻ tấn công bắn 1 triệu gói/giây TỚI ĐỊA CHỈ CỦA ROUTER
   (ICMP, SSH, SNMP, hoặc gói TTL=1)
                    ↓
   Những gói này KHÔNG được ASIC xử lý — chúng bị "punt" LÊN CPU
                    ↓
   CPU 100%  →  OSPF/BGP hello không kịp gửi  →  HÀNG XÓM RỚT ADJACENCY
                  →  SSH không vào được để cứu  →  MẤT CẢ MẠNG
   
   Điều đáng sợ: DATA PLANE VẪN CHẠY TỐT. Chỉ "bộ não" bị đánh gục.
```

> ⭐⭐ **CoPP = một QoS policy áp lên chính "cửa vào CPU"**, để ⭐ **giới hạn tốc độ từng loại
> traffic được phép làm phiền control plane.**

### 5.2 ⭐⭐ Cấu hình CoPP bằng MQC

```
!═══════ ① ACL phân loại từng nhóm traffic ═══════
ip access-list extended ACL-CP-ROUTING
 permit tcp host 10.0.0.2 host 10.0.0.1 eq bgp
 permit tcp host 10.0.0.2 eq bgp host 10.0.0.1
 permit ospf any any
 permit eigrp any any
!
ip access-list extended ACL-CP-MANAGEMENT
 permit tcp 10.99.0.0 0.0.0.255 any eq 22        ! SSH CHỈ từ mạng quản trị
 permit udp 10.99.0.0 0.0.0.255 any eq snmp
 permit udp host 10.99.1.5 any eq ntp
!
ip access-list extended ACL-CP-ICMP
 permit icmp any any echo
 permit icmp any any echo-reply
 permit icmp any any ttl-exceeded
 permit icmp any any unreachable
!
ip access-list extended ACL-CP-UNDESIRABLE
 permit tcp any any eq telnet                    ! mình đã cấm telnet → ai gõ = đáng ngờ
 permit udp any any eq 1434

!═══════ ② CLASS-MAP ═══════
class-map match-all CM-CP-ROUTING
 match access-group name ACL-CP-ROUTING
class-map match-all CM-CP-MANAGEMENT
 match access-group name ACL-CP-MANAGEMENT
class-map match-all CM-CP-ICMP
 match access-group name ACL-CP-ICMP
class-map match-all CM-CP-UNDESIRABLE
 match access-group name ACL-CP-UNDESIRABLE

!═══════ ③ POLICY-MAP ═══════
policy-map PM-COPP
 class CM-CP-ROUTING
  police 500000 conform-action transmit exceed-action transmit   ! ĐỪNG BÓP ROUTING
 class CM-CP-MANAGEMENT
  police 200000 conform-action transmit exceed-action drop
 class CM-CP-ICMP
  police 50000  conform-action transmit exceed-action drop         ! giới hạn ping flood
 class CM-CP-UNDESIRABLE
  police 8000 conform-action drop exceed-action drop             ! vứt thẳng
 class class-default
  police 500000 conform-action transmit exceed-action transmit   ! BẮT ĐẦU: CHỈ ĐẾM

!═══════ ④ ÁP LÊN CONTROL PLANE ═══════
control-plane
 service-policy input PM-COPP
```

> 🔴 ⭐⭐ **QUY TẮC VÀNG CỦA CoPP — đề hỏi, và ngoài đời còn quan trọng hơn:**
>
> ⭐⭐ **BẮT ĐẦU với `exceed-action transmit` cho MỌI class (kể cả class-default).**
> ⭐ Chạy như vậy **vài ngày**, ⭐ **xem bộ đếm** để biết tốc độ THẬT của từng loại traffic,
> ⭐ **rồi mới siết xuống `drop`.**
>
> 🔴 ⭐⭐ **CoPP quá tay = bạn TỰ tấn công chính mình:** ⭐ bóp nhầm OSPF → **rớt neighbor** ·
> ⭐ bóp nhầm SSH → **không vào cứu được** · ⭐ bóp nhầm ARP → **mất kết nối lớp 2**.
>
> ⭐ **Và: LUÔN đặt `class-default` rộng rãi.** ⭐ Mọi thứ bạn quên phân loại đều rơi vào đó.

### 5.3 ⭐ CPPr — bản nâng cấp của CoPP

> ⭐ **CPPr (Control Plane Protection)** chia control plane thành ⭐ **BA cửa con** để siết mịn hơn:

| Sub-interface | Nhận traffic gì | Ví dụ |
|---|---|---|
| ⭐ **host** | ⭐ Traffic gửi **TỚI địa chỉ của chính router** | ⭐ SSH, SNMP, ICMP tới router, BGP/OSPF |
| ⭐ **transit** | ⭐ Traffic **đi XUYÊN QUA** nhưng bị đẩy lên CPU (software-switched) | Gói cần xử lý đặc biệt |
| ⭐ **cef-exception** | ⭐ Thứ **CEF không xử lý nổi**, phải punt | ⭐ **ARP**, gói **TTL=1**, gói có **IP options** |

```
control-plane host
 service-policy input PM-COPP-HOST
control-plane transit
 service-policy input PM-COPP-TRANSIT
control-plane cef-exception
 service-policy input PM-COPP-EXCEPTION
```
⭐ **CPPr còn có:** ⭐ **port-filtering** (vứt ngay gói tới port đóng) và ⭐ **queue-thresholding**
(giới hạn số gói xếp hàng cho mỗi giao thức).

> ⭐ **Cho đề thi:** ⭐ **nhớ tên 3 sub-interface và ⭐ đặc biệt là `cef-exception` chứa ARP/TTL-exceeded.**

### 5.4 ⭐ Verify CoPP

```
show policy-map control-plane                             ! lệnh chính
show policy-map control-plane input class CM-CP-ICMP
show policy-map control-plane input                       ! chi tiết mọi class
show processes cpu sorted | exclude 0.00                  ! CPU đang bận vì cái gì
show processes cpu history                                ! biểu đồ CPU theo thời gian
```

⭐ **Đọc output — nhìn đúng ba dòng:**
```
Control Plane
  Service-policy input: PM-COPP
    Class-map: CM-CP-ICMP (match-all)
      152340 packets, 9140400 bytes             ← có traffic
      police:  cir 50000 bps, bc 1562 bytes
        conformed 148120 packets  (trong hạn mức → cho qua)
        exceeded  4220 packets    ← ĐANG BỊ VỨT / hoặc vượt hạn mức
```

> 🔴 ⭐⭐ **`exceeded` tăng đều đặn có nghĩa gì?** ⭐ Hai khả năng, phải phân biệt:
> 1. ⭐ **Đang bị tấn công / có vòng lặp** → tốt, CoPP đang làm đúng việc
> 2. 🔴 ⭐ **Bạn đặt hạn mức quá thấp** → ⭐ **đang tự vứt traffic hợp lệ của chính mình**
>
> ⭐ **Cách phân biệt: xem traffic đó ĐẾN TỪ ĐÂU.** ⭐ Nếu từ mạng quản trị của chính mình → là (2).

---

## 📘 6. ⭐⭐ NETWORK ACCESS CONTROL — 802.1X / MAB / WebAuth (blueprint 5.5.e)

> ⭐ Blueprint xếp mục này vào **5.5 "Describe"**, ⭐ **nhưng 5.1.b (AAA) và 5.4 (wireless) kéo nó
> thành "configure" trên thực tế.** ⭐ **Học ở mức cấu hình được — nó cũng là nền của TrustSec (§8).**

### 6.1 ⭐⭐ Ba vai — phải thuộc

```
   ┌─────────────┐   EAPoL    ┌──────────────────┐   RADIUS   ┌──────────────────┐
   │ SUPPLICANT│◄────────────►│ AUTHENTICATOR │◄────────────►│ AUTH SERVER   │
   │  (client)   │   Layer 2     │ (switch / WLC)   │  UDP 1812    │  (ISE / RADIUS)  │
   │             │  CHƯA CÓ IP│                  │              │                  │
   └─────────────┘               └──────────────────┘              └──────────────────┘
```

| Vai | Là ai | ⭐ Làm gì |
|---|---|---|
| ⭐⭐ **Supplicant** | ⭐ Phần mềm **trên client** (Windows native, Cisco Secure Client, wpa_supplicant) | Trả lời thử thách xác thực |
| ⭐⭐ **Authenticator** | ⭐ **Switch** (có dây) hoặc **WLC/AP** (không dây) | ⭐⭐ **Giữ cổng đóng. Chuyển tiếp EAP ↔ RADIUS.** ⭐ **Nó KHÔNG tự quyết định** |
| ⭐⭐ **Authentication Server** | ⭐ **ISE / FreeRADIUS / NPS** | ⭐⭐ **NGƯỜI RA QUYẾT ĐỊNH.** Trả về `Access-Accept` kèm VLAN/dACL/SGT |

> 🔴 ⭐⭐ **Ba điểm đề hay gài:**
> 1. ⭐⭐ **EAPoL chạy ở LAYER 2** — ⭐ **client CHƯA CÓ IP khi xác thực.** ⭐ Đó là lý do 802.1X làm được
>    việc mà firewall không làm được: ⭐ **chặn ngay từ trước khi thiết bị có địa chỉ.**
> 2. ⭐⭐ **Authenticator KHÔNG quyết định** — nó chỉ là **người đưa thư**. ⭐ **Server quyết.**
> 3. ⭐ **EAPoL** giữa supplicant↔switch · ⭐ **RADIUS** giữa switch↔server. ⭐ **Hai giao thức khác nhau.**

### 6.2 ⭐ Luồng 802.1X

```
   ① Port lên → switch CHẶN mọi thứ trừ EAPoL (và CDP/STP/LLDP)
   ② Switch gửi EAP-Request/Identity   (hoặc client gửi EAPoL-Start trước)
   ③ Client gửi EAP-Response/Identity  ("tôi là user@cty.local")
   ④ Switch bọc vào RADIUS Access-Request → gửi ISE
   ⑤ ISE ↔ Client trao đổi EAP (qua switch làm trung gian) — dựng tunnel TLS, kiểm chứng thư/mật khẩu
   ⑥ ISE trả RADIUS Access-Accept + THUỘC TÍNH:
          · VLAN động (Tunnel-Private-Group-ID)
          · dACL (downloadable ACL)
          · SGT  (→ §8 TrustSec)
   ⑦ Switch gửi EAPoL-Success → MỞ CỔNG và áp các thuộc tính nhận được
   ⑧ Client mới bắt đầu DHCP → có IP → vào mạng
```

> ⭐⭐ **Bước ⑥ là lý do 802.1X mạnh:** ⭐ **cùng một cổng vật lý có thể cho ra kết quả khác nhau
> tùy AI đang cắm vào** — kế toán vào VLAN 20 + SGT `KeToan`, khách vào VLAN 99 + ACL hạn chế.
> ⭐ Nhắc lại [Module-07B §8.2](Module-07B-CAPWAP-WLC-FlexConnect-Roaming.md): ⭐ **đây chính là
> "1 SSID + gán VLAN động" thay vì tạo 8 SSID.**

### 6.3 ⭐⭐ MAB & WebAuth — hai phương án dự phòng

| | ⭐⭐ **MAB** (MAC Authentication Bypass) | ⭐ **WebAuth** |
|---|---|---|
| Dành cho | ⭐ **Thiết bị KHÔNG có supplicant**: máy in, camera, đầu đọc thẻ, IoT, điện thoại cũ | ⭐ **Người dùng là CON NGƯỜI** nhưng không có tài khoản 802.1X: khách |
| Cách hoạt động | ⭐ Switch lấy **MAC** của thiết bị, ⭐ **gửi MAC làm username VÀ password** cho RADIUS | ⭐ Client được IP tạm → mở trình duyệt → ⭐ **bị chuyển hướng** về portal → nhập thông tin |
| 🔴 Điểm yếu | 🔴 ⭐⭐ **MAC giả mạo được rất dễ** → ⭐ **phải dùng kèm profiling của ISE** | ⭐ Cần DHCP + DNS hoạt động trước |
| Thời điểm | ⭐ Sau khi 802.1X **hết giờ chờ** | ⭐ Sau khi 802.1X **và** MAB đều trượt |

> 🔴 ⭐⭐ **Thứ tự mặc định: 802.1X → MAB → WebAuth.**
> ⭐ **Vì sao đúng thứ tự đó:** ⭐ mạnh nhất trước, yếu nhất sau.
> ⭐ 802.1X phải **hết timeout** (mặc định `tx-period 30s × 3 lần = 90 giây`!) mới sang MAB →
> 🔴 ⭐ **máy in mất 90 giây mới lên mạng.** ⭐ **Cách sửa: `dot1x timeout tx-period 7`** → còn ~21 giây.

### 6.4 ⭐⭐ Host mode — bảng phải nhớ

| Host mode | Cho phép bao nhiêu MAC | ⭐ Dùng khi |
|---|---|---|
| ⭐ **single-host** | ⭐ **Đúng 1 MAC** | An toàn nhất, nhưng không dùng được với điện thoại IP |
| 🔴 ⭐ **multi-host** | ⭐ **MAC đầu tiên xác thực → TẤT CẢ MAC còn lại được vào FREE** | 🔴 ⭐⭐ **Rất kém an toàn.** Chỉ dùng khi sau port là AP/switch tin cậy |
| ⭐⭐ **multi-domain (MDA)** | ⭐⭐ **1 thiết bị VOICE + 1 thiết bị DATA** | ⭐⭐ **Phổ biến nhất ở văn phòng: điện thoại IP + PC cắm sau điện thoại** |
| ⭐ **multi-auth** | ⭐ **MỌI MAC đều phải xác thực RIÊNG** | ⭐ An toàn nhất khi sau port có hub / nhiều VM / switch nhỏ |

### 6.5 ⭐⭐ Cấu hình 802.1X trên switch

```
!═══════ ① AAA (nối tiếp §3) ═══════
aaa new-model
!
radius server ISE-1
 address ipv4 10.99.1.10 auth-port 1812 acct-port 1813
 key SecretRadius2026
 automate-tester username probe-user probe-on      ! tự dò server sống/chết
!
aaa group server radius GRP-RAD
 server name ISE-1
!
aaa authentication dot1x default group GRP-RAD
aaa authorization network default group GRP-RAD    ! BẮT BUỘC để nhận VLAN/dACL/SGT
aaa accounting dot1x default start-stop group GRP-RAD
!
radius-server attribute 6  on-for-login-auth
radius-server attribute 8  include-in-access-req   ! gửi IP client — cần cho dACL
radius-server attribute 25 access-request include
!
radius-server vsa send authentication              ! nhận thuộc tính riêng của Cisco
radius-server vsa send accounting
!
radius-server dead-criteria time 5 tries 3
radius-server deadtime 10

!═══════ ② BẬT 802.1X TOÀN CỤC — DÒNG HAY QUÊN NHẤT ═══════
dot1x system-auth-control

!═══════ ③ CẤU HÌNH PORT ═══════
interface GigabitEthernet1/0/10
 description Cong nguoi dung
 switchport mode access
 switchport access vlan 10
 switchport voice vlan 20
 !
 authentication host-mode multi-domain          ! điện thoại + PC
 authentication port-control auto               ! "auto" = BẬT 802.1X thật sự
 authentication order dot1x mab                 ! thử 802.1X trước, rồi MAB
 authentication priority dot1x mab
 authentication periodic
 authentication timer reauthenticate server
 authentication violation restrict
 !
 mab                                            ! bật MAB trên port
 dot1x pae authenticator                        ! switch đóng vai authenticator
 dot1x timeout tx-period 7                      ! giảm từ 30s → thiết bị MAB lên nhanh
 !
 spanning-tree portfast
 spanning-tree bpduguard enable
```

⭐ **Ba giá trị của `port-control`:**

| Giá trị | Nghĩa |
|---|---|
| ⭐⭐ **`auto`** | ⭐ **Bật 802.1X thật** — cổng đóng cho tới khi xác thực xong |
| ⭐ `force-authorized` | ⭐ **Mặc định** — cổng luôn mở, **không xác thực gì** |
| ⭐ `force-unauthorized` | Cổng **luôn đóng**, không ai vào được |

> 🔴 ⭐⭐ **Hai dòng hay quên nhất, và cả hai đều làm 802.1X "không chạy mà không báo lỗi":**
> 1. ⭐⭐ **`dot1x system-auth-control`** — thiếu nó thì ⭐ **cấu hình trên port vô nghĩa hoàn toàn**
> 2. ⭐⭐ **`aaa authorization network default group ...`** — thiếu nó thì ⭐ **xác thực THÀNH CÔNG
>    nhưng VLAN động / dACL / SGT KHÔNG được áp** → ⭐ client vào nhầm VLAN

### 6.6 ⭐⭐ Ba VLAN dự phòng — và chế độ triển khai

| Cơ chế | Kích hoạt khi | ⭐ Dùng để |
|---|---|---|
| ⭐ **Guest VLAN** | ⭐ Client **KHÔNG trả lời EAPoL** (không có supplicant) | ⭐ Cho khách vào vùng hạn chế |
| ⭐ **Auth-fail / Restricted VLAN** | ⭐ Client **CÓ trả lời nhưng xác thực TRƯỢT** | Vùng cách ly, chỉ cho vào trang hướng dẫn |
| ⭐⭐ **Critical VLAN / Inaccessible Auth Bypass** | 🔴 ⭐⭐ **RADIUS server CHẾT** | ⭐⭐ **Cứu cả công ty** — không có nó thì **server ISE sập = toàn bộ nhân viên mất mạng** |

```
interface GigabitEthernet1/0/10
 authentication event no-response action authorize vlan 99      ! Guest VLAN
 authentication event fail action authorize vlan 98             ! Auth-fail VLAN
 authentication event server dead action authorize vlan 10      ! Critical VLAN
 authentication event server dead action authorize voice
 authentication event server alive action reinitialize
```

> 🔴 ⭐⭐ **Critical VLAN là tính năng quan trọng nhất mà người mới hay bỏ qua.**
> ⭐ Không có nó: ⭐ **ISE bảo trì 10 phút = 2000 nhân viên không vào được mạng**, và
> ⭐ **bạn cũng không SSH vào switch được để sửa** (nếu switch cũng dùng ISE cho AAA).

#### ⭐⭐ Ba giai đoạn triển khai 802.1X — LÀM ĐÚNG THỨ TỰ NÀY

| Giai đoạn | Cấu hình | ⭐ Chuyện gì xảy ra |
|---|---|---|
| ⭐⭐ **1. Monitor Mode** *(Open mode)* | ⭐ `authentication open` | ⭐⭐ **Xác thực chạy và GHI LOG, nhưng KHÔNG chặn ai cả.** ⭐ Dùng để **tìm ra mọi thiết bị lạ** trong mạng trước |
| ⭐ **2. Low-Impact Mode** | `authentication open` + ⭐ **pre-auth ACL** | ⭐ Cho phép tối thiểu (DHCP, DNS, PXE) trước khi xác thực; xong thì mở rộng |
| ⭐ **3. Closed Mode** | ⭐ **Bỏ `authentication open`** | ⭐ **Đóng hoàn toàn** — không xác thực thì không có gì |

> 🔴 ⭐⭐ **KHÔNG BAO GIỜ bật thẳng Closed Mode trên mạng đang chạy.**
> ⭐ Bạn sẽ phát hiện ra hàng chục máy in, camera, máy chấm công, máy quét mã vạch mà
> ⭐ **không ai biết là chúng tồn tại** — và tất cả rớt mạng cùng lúc.
> ⭐ **Chạy Monitor Mode vài tuần trước đã.**

### 6.7 ⭐ Verify 802.1X

```
show authentication sessions                              ! (IOS cũ)
show access-session                                       ! (IOS-XE mới)
show access-session interface Gi1/0/10 details          ! LỆNH QUAN TRỌNG NHẤT
show dot1x all
show dot1x interface Gi1/0/10 details
show mab all
show aaa servers | include host|State
!
debug dot1x all                                             ! ⚠️ chỉ lab
debug radius authentication
```

⭐ **Đọc `show access-session interface ... details`:**
```
            Interface: GigabitEthernet1/0/10
          MAC Address: 0050.56aa.bb01
           IPv4 Address: 10.1.10.55
              Status: Authorized                ← ✅ đã xong
        Domain: DATA                            ← DATA hay VOICE (multi-domain)
      Oper host mode: multi-domain
           Current Policy: POLICY_Gi1/0/10
   Method status list:
         Method       State
       dot1x       Authc Success               ← 802.1X thành công
         mab          Not run                     ← không cần chạy tới MAB
   Server Policies:
         Vlan Group: Vlan: 20                   ← VLAN động ISE trả về
         SGT Value: 10                          ← SGT (→ §8)
         ACS ACL: xACSACLx-IP-EMPLOYEE-ACL      ← dACL
```

| ⭐ Trạng thái | Nghĩa |
|---|---|
| ⭐ `Authorized` | ✅ Xong, cổng mở |
| ⭐ `Unauthorized` | 🔴 Chưa qua — xem `Method status list` để biết hỏng ở đâu |
| ⭐ `Running` | Đang xác thực dở |
| ⭐ `Authc Failed` | ⭐ Server **trả lời TRƯỢT** → sai mật khẩu/chứng thư |
| ⭐ `No response` | ⭐ **Client không có supplicant** → sẽ rơi xuống MAB / Guest VLAN |

---

## 📘 7. 🔴 ⭐⭐ WIRELESS SECURITY (blueprint 5.4 — CONFIGURE)

> ⭐ Khái niệm đã học ở [Module-07B §8](Module-07B-CAPWAP-WLC-FlexConnect-Roaming.md).
> ⭐ **Ở đây là CẤU HÌNH — vì 5.4 nói "Configure and verify".**

### 7.1 ⭐ Ôn nhanh bảng thế hệ

| Thế hệ | Personal | Enterprise | Mã hóa | ⭐ PMF |
|---|---|---|---|---|
| WEP | Shared key | — | RC4 | ❌ |
| WPA | PSK | 802.1X | TKIP | ❌ |
| ⭐⭐ **WPA2** | ⭐ **PSK** | ⭐ **802.1X/EAP** | ⭐ **AES-CCMP** | Tùy chọn |
| ⭐ **WPA3** | ⭐⭐ **SAE** *(không phải PSK!)* | 802.1X | AES-GCMP/CCMP | ⭐⭐ **BẮT BUỘC** |
| ⭐ **OWE** (Enhanced Open) | Không mật khẩu | — | ⭐ **Có mã hóa** | Bắt buộc |

> 🔴 ⭐⭐ **Ba điểm về WPA3 hay ra đề:**
> 1. ⭐⭐ **WPA3-Personal dùng SAE, KHÔNG dùng PSK.** ⭐ SAE (*Simultaneous Authentication of Equals*,
>    còn gọi **Dragonfly**) ⭐ **chống được tấn công dò mật khẩu OFFLINE** — kẻ tấn công bắt được
>    handshake **cũng không brute-force ngoại tuyến được**.
> 2. ⭐⭐ **WPA3 BẮT BUỘC PMF (802.11w)** → 🔴 ⭐ **client cũ không hỗ trợ 802.11w sẽ KHÔNG join được.**
> 3. ⭐ **OWE = mở nhưng CÓ mã hóa** — dành cho Wi-Fi công cộng, ⭐ không cần mật khẩu mà vẫn không bị nghe lén.

### 7.2 ⭐ Cấu hình PSK / SAE (5.4.c) trên Catalyst 9800

```
! ═══ WPA2-Personal (PSK) ═══
wlan WLAN-PSK 1 CTY-PSK
 security wpa
 security wpa wpa2
 security wpa wpa2 ciphers aes
 security wpa akm psk
 security wpa akm psk set-key ascii 0 MatKhauRatDaiVaKho2026
 security pmf optional
 no shutdown

! ═══ WPA3-Personal (SAE) ═══
wlan WLAN-WPA3 2 CTY-WPA3
 security wpa wpa3
 security wpa wpa3 ciphers aes
 security wpa akm sae
 security wpa akm sae pwe h2e            ! Hash-to-Element (bản SAE mới hơn)
 security pmf mandatory                  ! WPA3 BẮT BUỘC PMF
 no shutdown

! ═══ Chế độ chuyển tiếp WPA2+WPA3 (cho client cũ vẫn vào được) ═══
wlan WLAN-MIXED 3 CTY-MIXED
 security wpa wpa2
 security wpa wpa3
 security wpa akm psk
 security wpa akm sae
 security pmf optional                   ! "optional" để client cũ không bị loại
 no shutdown
```

> 🔴 ⭐ **Bẫy triển khai:** đặt `pmf mandatory` cho một SSID đang có máy cũ dùng →
> ⭐ **những máy đó biến mất khỏi mạng ngay lập tức.** ⭐ Dùng **transition mode + `pmf optional`** trước.

### 7.3 ⭐⭐ Cấu hình EAP / 802.1X wireless (5.4.a)

```
! ═══ ① AAA trỏ tới ISE ═══
aaa new-model
!
radius server ISE-1
 address ipv4 10.99.1.10 auth-port 1812 acct-port 1813
 key SecretRadius2026
!
aaa group server radius GRP-RAD
 server name ISE-1
!
aaa authentication dot1x WLAN-DOT1X group GRP-RAD
aaa authorization network WLAN-AUTHZ group GRP-RAD
aaa accounting identity WLAN-ACCT start-stop group GRP-RAD

! ═══ ② WLAN dùng 802.1X ═══
wlan WLAN-CORP 4 CTY-CORP
 security wpa wpa2
 security wpa wpa2 ciphers aes
 security dot1x authentication-list WLAN-DOT1X     ! trỏ tới method list
 security ft                                          ! 802.11r (Module-07B §6.5)
 security pmf optional
 no shutdown

! ═══ ③ Policy Profile — nơi nhận VLAN/ACL từ ISE ═══
wireless profile policy POL-CORP
 vlan 20
 aaa-override                                       ! CHO PHÉP ISE ghi đè VLAN/ACL
 nac                                                ! bật Central Web Auth / posture
 accounting-list WLAN-ACCT
 no shutdown
```

> 🔴 ⭐⭐ **`aaa-override` là dòng hay quên nhất của wireless 802.1X.**
> ⭐ Thiếu nó: ⭐ **xác thực thành công nhưng client LUÔN vào VLAN tĩnh của Policy Profile**,
> ⭐ **thuộc tính ISE trả về bị BỎ QUA.** ⭐ Đây là bản song sinh của bẫy
> `aaa authorization network` bên switch (§6.5).

#### ⭐ Chọn loại EAP nào

| EAP type | Server cần | Client cần | ⭐ Nhận xét |
|---|---|---|---|
| ⭐⭐ **EAP-TLS** | ⭐ **Chứng thư** | ⭐⭐ **Chứng thư** | ⭐⭐ **An toàn nhất — không có mật khẩu để đánh cắp.** 🔴 Cần hạ tầng **PKI** + phân phối chứng thư → nặng |
| ⭐⭐ **PEAP-MSCHAPv2** | ⭐ **Chứng thư** | ⭐ **Username + password** | ⭐⭐ **Phổ biến nhất.** ⭐ Dựng tunnel TLS trước rồi mới gửi mật khẩu bên trong |
| **EAP-TTLS** | Chứng thư | Username/password | Giống PEAP, linh hoạt hơn về giao thức bên trong |
| **EAP-FAST** | (PAC) | PAC / username | ⭐ Của Cisco — dùng **PAC** thay chứng thư server |
| 🔴 **EAP-MD5** | — | — | 🔴 ⭐ **Không dùng cho Wi-Fi** — không sinh khóa mã hóa, không xác thực server |

> 🔴 ⭐⭐ **Bẫy đề kinh điển:** *"EAP-TLS và PEAP đều cần chứng thư ở cả hai bên"* → ⭐ **SAI.**
> ⭐⭐ **PEAP: CHỈ SERVER cần chứng thư.** ⭐⭐ **EAP-TLS: CẢ HAI đều cần.**
>
> 🔴 ⭐ **Và một điểm an ninh thật:** với PEAP, ⭐ **client PHẢI được cấu hình "validate server certificate"**.
> ⭐ Không bật → kẻ tấn công dựng AP giả + RADIUS giả → ⭐ **thu được hash mật khẩu MSCHAPv2 của nhân viên.**

### 7.4 ⭐ WebAuth (5.4.b)

| Kiểu | Trang đăng nhập nằm ở đâu | Ghi chú |
|---|---|---|
| ⭐ **LWA** (Local Web Auth) | ⭐ **Trên chính WLC** | Đơn giản, ít tính năng |
| ⭐⭐ **CWA** (Central Web Auth) | ⭐ **Trên ISE** | ⭐ Kèm được **posture, profiling, guest sponsor** |
| **External** | Web server riêng | Tùy biến giao diện tối đa |

```
! ═══ Pre-auth ACL — phải MỞ DNS và DHCP ═══
ip access-list extended ACL-PREAUTH
 permit udp any any eq domain            ! DNS — thiếu là KHÔNG có portal
 permit udp any any eq bootps
 permit udp any any eq bootpc
 permit tcp any host 10.99.1.10 eq 8443    ! cho phép tới portal ISE
 deny   ip any any

! ═══ Parameter map ═══
parameter-map type webauth WEBAUTH-KHACH
 type webauth
 redirect on-success https://cty.local/xin-chao
 banner text ^Mang danh cho khach^

! ═══ WLAN khách ═══
wlan WLAN-KHACH 5 CTY-KHACH
 no security wpa
 no security wpa akm dot1x
 no security wpa wpa2
 security web-auth
 security web-auth authentication-list WEB-AUTH-LIST
 security web-auth parameter-map WEBAUTH-KHACH
 no shutdown
```

> 🔴 ⭐⭐ **Lỗi WebAuth số 1: khách kết nối được, có IP, nhưng KHÔNG hiện trang đăng nhập.**
>
> | Nguyên nhân | ⭐ Cách sửa |
> |---|---|
> | ⭐⭐ **Pre-auth ACL chặn DNS (UDP 53)** | ⭐ **Mở UDP 53** — không phân giải được tên thì trình duyệt không mở nổi trang nào |
> | ⭐ Client dùng **DNS-over-HTTPS** | ⭐ Chặn DoH ở pre-auth ACL, hoặc hướng dẫn khách vào `http://` |
> | ⭐ **HSTS cache** trong trình duyệt | ⭐ Trang HTTPS đã lưu HSTS **không cho phép chuyển hướng** → bảo khách mở một trang **`http://`** bất kỳ |
> | ⭐ Chứng thư portal không hợp lệ | Khách thấy cảnh báo bảo mật rồi bỏ đi |

### 7.5 ⭐ Verify wireless security

```
show wlan summary
show wlan id 4                                    ! xem đủ cấu hình bảo mật của 1 WLAN
show wireless profile policy detailed POL-CORP      ! aaa-override bật chưa
show wireless client mac-address <MAC> detail     ! State, VLAN, SGT, ACL đang áp
show wireless client summary
show aaa servers
!
debug wireless mac <H.H.H> internal               ! RadioActive Trace (Module-07B §9.4)
test aaa group GRP-RAD user pass new-code
```

---

## 📘 8. ⭐⭐ TRUSTSEC & MACSEC (blueprint 5.5.d — Describe)

### 8.1 ⭐ Vấn đề TrustSec giải quyết

```
   CÁCH CŨ — ACL theo địa chỉ IP:

   permit ip 10.1.10.0 0.0.0.255 host 10.2.5.100      ! kế toán → server lương
   permit ip 10.1.11.0 0.0.0.255 host 10.2.5.100
   ... (200 dòng nữa)

   Vấn đề: CHÍNH SÁCH BỊ TRÓI VÀO ĐỊA CHỈ IP VÀ TOPOLOGY
   Đổi subnet  → viết lại ACL
   Thêm site   → viết lại ACL ở nhiều thiết bị
   Nhân viên chuyển tầng → sai VLAN → sai quyền
   ACL phình tới hàng nghìn dòng, không ai dám sửa
```

> ⭐⭐ **Ý tưởng TrustSec:** ⭐ **gán cho mỗi người/thiết bị một NHÃN (SGT) dựa trên DANH TÍNH,
> rồi viết chính sách theo NHÃN — hoàn toàn không nhắc tới địa chỉ IP.**
>
> ⭐ `Nhóm KeToan` → được nói với `Nhóm ServerLuong`
> ⭐ `Nhóm ThucTapSinh` → **cấm** nói với `Nhóm ServerLuong`
> ⭐ **Người đó ngồi ở tầng nào, IP bao nhiêu — KHÔNG QUAN TRỌNG.**

### 8.2 ⭐⭐ Ba pha của TrustSec — bảng phải thuộc

| Pha | ⭐ Làm gì | ⭐ Cách làm |
|:---:|---|---|
| ⭐⭐ **1. CLASSIFICATION**<br>*(gán nhãn)* | ⭐ Gán **SGT** cho endpoint | ⭐ **Động:** ISE gán khi **802.1X / MAB / WebAuth** thành công *(§6)*<br>⭐ **Tĩnh:** IP-to-SGT · VLAN-to-SGT · Subnet-to-SGT · Port-to-SGT |
| ⭐⭐ **2. PROPAGATION**<br>*(mang nhãn đi)* | ⭐ Đưa SGT từ nơi gán tới nơi thực thi | ⭐ **Inline tagging** — nhét SGT vào **trường Cisco Metadata (CMD)** của frame L2 *(⭐ cần phần cứng hỗ trợ)*<br>⭐ **SXP** (SGT Exchange Protocol, ⭐ **TCP 64999**) — cho thiết bị **không** inline tag được<br>⭐ **VXLAN** — mang SGT trong header *(⭐ SD-Access!)* |
| ⭐⭐ **3. ENFORCEMENT**<br>*(thực thi)* | ⭐ Cho phép / chặn | ⭐ **SGACL** trên switch/router · ⭐ **SG-Firewall** trên ASA/FTD |

> 🔴 ⭐⭐ **Ba điểm đề gài:**
> 1. ⭐⭐ **Enforcement xảy ra ở thiết bị EGRESS (lối ra)** — ⭐ vì chỉ ở đó mới biết **SGT của ĐÍCH**.
> 2. ⭐⭐ **SXP tồn tại vì nhiều thiết bị KHÔNG inline-tag được** — ⭐ nó "kể" ánh xạ IP↔SGT qua **TCP 64999**.
> 3. ⭐ **SGT được gán bởi ISE, KHÔNG phải bởi switch.** ⭐ Switch chỉ **nhận** trong `Access-Accept`.

⭐ **Ma trận SGACL trong ISE trông như thế này:**

| Nguồn ↓ / Đích → | `ServerLuong` | `ServerFile` | `Internet` |
|---|:---:|:---:|:---:|
| ⭐ **KeToan** | ✅ Permit | ✅ Permit | ✅ Permit |
| ⭐ **ThucTapSinh** | 🔴 **Deny** | ✅ Permit | ✅ Permit |
| ⭐ **Camera** | 🔴 Deny | 🔴 Deny | 🔴 Deny |
| ⭐ **Khach** | 🔴 Deny | 🔴 Deny | ✅ Permit |

⭐ **Thêm một phòng ban mới = thêm một dòng trong ma trận.** ⭐ **Không đụng vào ACL nào cả.**

```
! Vài lệnh nhận biết (không cần thuộc)
cts authorization list ISE-LIST
cts role-based enforcement                        ! bật thực thi SGACL
cts role-based sgt-map 10.1.10.0/24 sgt 10        ! gán tĩnh subnet → SGT
!
interface Gi1/0/1
 cts manual
  policy static sgt 100 trusted
!
cts sxp enable
cts sxp connection peer 10.99.1.10 password default mode local listener
!
show cts environment-data
show cts role-based sgt-map all
show cts role-based permissions
show cts sxp connections
```

### 8.3 ⭐ Nối với SD-Access

> ⭐⭐ Nhắc lại [Module-09 §7.1](Module-09-Architecture-va-QoS.md):
>
> | Tầng | Công nghệ | Học ở đâu |
> |---|---|---|
> | Control plane | **LISP** | Module-08 §7 |
> | Data plane | **VXLAN** | Module-08 §8 |
> | ⭐⭐ **Policy plane** | ⭐⭐ **TrustSec / SGT** | ⭐ **CHÍNH LÀ MỤC §8 NÀY** |
>
> ⭐ Và: ⭐ **VN = macro-segmentation (VRF)** · ⭐ **SGT = micro-segmentation trong cùng VN.**
> ⭐ Trong SD-Access, ⭐ **VXLAN mang CẢ VNI lẫn SGT** → propagation là "miễn phí", không cần SXP.

### 8.4 ⭐⭐ MACsec (IEEE 802.1AE)

```
   MACsec mã hóa Ở LỚP 2, TỪNG CHẶNG MỘT (hop-by-hop):

   [PC]══mã hóa══[SW1]──giải mã, xử lý, mã hóa lại──[SW2]══mã hóa══[Server]
        MỖI CHẶNG mã hóa riêng. Switch NHÌN THẤY gói ở giữa.

   So sánh IPsec (Module-08 §5) — mã hóa ĐẦU-CUỐI:
   [R1]════════════ mã hóa suốt chặng ════════════[R2]
        Router ở giữa KHÔNG đọc được gì.
```

| | ⭐⭐ **MACsec** | ⭐⭐ **IPsec** |
|---|---|---|
| ⭐ **Tầng** | ⭐⭐ **Layer 2** (802.1AE) | ⭐⭐ **Layer 3** |
| ⭐ **Phạm vi** | ⭐⭐ **Hop-by-hop** (từng liên kết) | ⭐⭐ **End-to-end** (xuyên mạng định tuyến) |
| Mã hóa cái gì | ⭐ **Cả frame Ethernet** (kể cả header L2, VLAN tag) | Gói IP |
| Tốc độ | ⭐⭐ **Line-rate, mã hóa bằng PHẦN CỨNG** | Phụ thuộc CPU/crypto engine |
| Quản lý khóa | ⭐ **MKA** (MACsec Key Agreement) | ⭐ **IKEv1/IKEv2** |
| ⭐ Dùng khi | ⭐ **Switch↔switch (uplink)** · **host↔switch (downlink)** | ⭐ **Site↔site qua Internet/WAN** |
| ⭐ Mang được SGT? | ⭐ **Có** — SGT nằm trong frame đã mã hóa | Không trực tiếp |

⭐ **Hai kiểu triển khai MACsec:**

| Kiểu | Quản lý khóa | ⭐ Dùng cho |
|---|---|---|
| ⭐ **Downlink** (host ↔ switch) | ⭐ **MKA lấy khóa từ phiên 802.1X** (MSK → CAK) | ⭐ Bảo vệ đoạn từ PC tới switch tầng access |
| ⭐ **Uplink** (switch ↔ switch) | ⭐ **MKA với pre-shared key (CKN/CAK)**, hoặc **SAP** *(Cisco, đời cũ)* | ⭐ Bảo vệ đường trục, đặc biệt khi **cáp đi qua khu vực không kiểm soát** |

```
! Cấu hình MACsec switch↔switch với pre-shared key
key chain KC-MACSEC macsec
 key 01
  cryptographic-algorithm aes-256-cmac
  key-string 0123456789ABCDEF...
!
mka policy MKA-POL
 macsec-cipher-suite gcm-aes-256
!
interface TenGigabitEthernet1/0/1
 macsec network-link
 mka policy MKA-POL
 mka pre-shared-key key-chain KC-MACSEC
!
show macsec summary
show macsec interface Te1/0/1
show mka sessions
```

> ⭐⭐ **Câu chốt cho đề:** ⭐ **"MACsec = L2, hop-by-hop, mã hóa cả frame, line-rate phần cứng, dùng MKA.
> IPsec = L3, end-to-end, xuyên mạng định tuyến, dùng IKE."**
> 🔴 ⭐ **Bẫy: "MACsec mã hóa end-to-end"** → **SAI.** ⭐ **Từng chặng một.**

---

## 📘 9. 🟡 THÀNH PHẦN THIẾT KẾ AN NINH MẠNG (blueprint 5.5.a/b/c — Describe)

> ⭐ Mục này ⭐ **chỉ cần "describe"** — ⭐ **học bảng, biết tên, hiểu vai trò. KHÔNG cấu hình.**

### 9.1 ⭐⭐ NGFW vs Firewall truyền thống vs UTM

| | **Stateful Firewall** *(truyền thống)* | **UTM** | ⭐⭐ **NGFW** (Next-Gen Firewall) |
|---|---|---|---|
| Lọc theo | ⭐ **5-tuple** (IP nguồn/đích, port, protocol) | 5-tuple + vài dịch vụ gộp | ⭐⭐ **5-tuple + ỨNG DỤNG + NGƯỜI DÙNG** |
| ⭐ Nhận diện ứng dụng | 🔴 ❌ — chỉ thấy "TCP 443" | Hạn chế | ⭐⭐ **CÓ** — phân biệt được "Facebook" với "Salesforce" **dù cùng TCP 443** |
| ⭐ Nhận diện người dùng | 🔴 ❌ — chỉ thấy IP | Hạn chế | ⭐⭐ **CÓ** — "user `nam.tran` được, `khach01` không" |
| ⭐ IPS tích hợp | ❌ | Có (rời rạc) | ⭐⭐ **CÓ, tích hợp sâu** |
| URL filtering / AMP | ❌ | Có | ⭐ **Có** |
| Giải mã TLS | ❌ | Hạn chế | ⭐ **Có** |
| Threat intelligence | ❌ | Ít | ⭐⭐ **Có — cập nhật liên tục (Talos)** |
| ⭐ Sản phẩm Cisco | ASA *(truyền thống)* | — | ⭐⭐ **Secure Firewall / Firepower (FTD)**, quản lý bằng **FMC** |

> ⭐⭐ **Câu định nghĩa NGFW cho đề:** ⭐ **"Firewall stateful + nhận diện ỨNG DỤNG + nhận diện NGƯỜI DÙNG
> + IPS tích hợp + threat intelligence."**
> ⭐ **Điểm mấu chốt: NGFW nhìn được BÊN TRONG cổng 443**, firewall cũ chỉ thấy "có traffic HTTPS".

### 9.2 ⭐⭐ IDS vs IPS

| | ⭐ **IDS** (Detection) | ⭐⭐ **IPS** (Prevention) |
|---|---|---|
| ⭐ **Vị trí** | ⭐⭐ **NGOÀI luồng** (out-of-band) — nhận bản sao qua **SPAN/TAP** | ⭐⭐ **TRONG luồng** (inline) — gói **đi xuyên qua nó** |
| ⭐ **Làm được gì** | ⭐ **Chỉ phát hiện + cảnh báo** | ⭐⭐ **Phát hiện + CHẶN NGAY** |
| Ảnh hưởng độ trễ | ⭐ **Không** | ⭐ Có (nhỏ) |
| 🔴 Rủi ro | ⭐ Gói xấu **đã tới đích rồi** mới báo | 🔴 ⭐⭐ **False positive = CHẶN NHẦM traffic hợp lệ** · ⭐ **thiết bị chết = ĐỨT MẠNG** *(cần fail-open/bypass)* |

> ⭐ **Mẹo nhớ:** ⭐ **IDS = camera an ninh** (thấy trộm, gọi báo — trộm vẫn vào được).
> ⭐ **IPS = cửa xoay có bảo vệ** (chặn được — nhưng chặn nhầm thì khách hàng cũng không vào được).

⭐ **Hai cách phát hiện:** ⭐ **Signature-based** (khớp mẫu đã biết — chính xác, ⭐ **mù với tấn công mới**) ·
⭐ **Anomaly/behavior-based** (học "bình thường" rồi báo cái lệch — ⭐ **bắt được zero-day, nhưng nhiều false positive**).

### 9.3 ⭐ Threat defense — hệ sinh thái Cisco

| Sản phẩm | ⭐ Làm gì |
|---|---|
| ⭐⭐ **Talos** | ⭐ **Đội tình báo mối đe dọa của Cisco** — nguồn cấp dữ liệu cho **tất cả** sản phẩm còn lại |
| ⭐⭐ **Secure Firewall / FTD** *(Firepower)* | ⭐ **NGFW + IPS**, quản lý bằng **FMC** (nhiều thiết bị) hoặc **FDM** (một thiết bị) |
| ⭐⭐ **Umbrella** | ⭐⭐ **An ninh ở tầng DNS** — ⭐ chặn tên miền độc hại **TRƯỚC KHI kết nối được tạo ra**. ⭐ Bảo vệ cả máy **ở ngoài văn phòng** |
| ⭐ **Secure Network Analytics** *(Stealthwatch)* | ⭐ Phân tích **NetFlow** để phát hiện bất thường · ⭐ **ETA** — phát hiện malware **trong traffic đã mã hóa mà KHÔNG cần giải mã** |
| ⭐ **Secure Endpoint** *(AMP for Endpoints)* | ⭐ **EDR** trên máy trạm — ⭐ **retrospective detection**: phát hiện file lành hôm qua hóa ra là mã độc hôm nay |
| ⭐ **Secure Email / Secure Web Appliance** *(ESA/WSA)* | Lọc email và web proxy |
| ⭐⭐ **ISE** | ⭐⭐ **NAC + policy + SGT** — ⭐ **trung tâm của cả §6 và §8** |
| ⭐ **Duo** | ⭐ **Xác thực đa yếu tố (MFA)** — trụ cột "workforce" của Zero Trust |
| ⭐ **Secure Client** *(AnyConnect)* | ⭐ VPN + supplicant 802.1X + posture — **tất cả trong một agent** |

### 9.4 ⭐ Endpoint security

| Thành phần | ⭐ Vai trò |
|---|---|
| ⭐ **Antivirus / EDR** | Chặn mã độc trên chính máy trạm |
| ⭐⭐ **Posture assessment** | ⭐⭐ **ISE kiểm tra máy TRƯỚC KHI cho vào mạng**: đã vá lỗi chưa · AV có bật không · ổ đĩa mã hóa chưa. ⭐ **Chưa đạt → đẩy vào VLAN cách ly để tự khắc phục (remediation)** |
| ⭐ **Host firewall** | Tường lửa trên máy |
| ⭐ **Disk encryption** | BitLocker / FileVault |
| ⭐ **MDM** | Quản lý thiết bị di động |
| ⭐ **DNS-layer (Umbrella)** | Bảo vệ cả khi máy **không ở trong mạng công ty** |

> ⭐⭐ **Posture assessment là điểm nối quan trọng:** ⭐ nó biến 802.1X từ *"anh là ai"* thành
> ⭐ ***"anh là ai VÀ máy của anh có đủ an toàn không"***.

### 9.5 ⭐ Zero Trust & Defense in Depth

| Khái niệm | ⭐ Nghĩa |
|---|---|
| ⭐⭐ **Zero Trust** | ⭐⭐ **"Không tin ai theo mặc định — kể cả bên trong mạng."** ⭐ Bỏ mô hình *"trong tường lửa là an toàn"*. ⭐ **Mọi truy cập đều phải xác thực và phân quyền lại** |
| ⭐ **3 trụ cột Zero Trust của Cisco** | ⭐ **Workforce** (Duo/MFA) · ⭐ **Workload** (Secure Workload/Tetration) · ⭐ **Workplace** (ISE + TrustSec) |
| ⭐ **Defense in Depth** | ⭐ **Nhiều lớp phòng thủ chồng nhau** — thủng một lớp vẫn còn lớp sau |
| ⭐ **Least privilege** | Chỉ cấp đúng quyền tối thiểu cần thiết |
| ⭐ **Microsegmentation** | ⭐ **Chính là SGT** *(§8)* — chia nhỏ tới mức từng nhóm người/thiết bị |

> ⭐ **Ba trụ cột kỹ thuật của Zero Trust trong ENCOR mà bạn ĐÃ học:**
> ⭐ **802.1X** (§6 — xác thực mọi thiết bị) + ⭐ **TrustSec/SGT** (§8 — phân quyền theo danh tính)
> + ⭐ **posture** (§9.4 — kiểm tra sức khỏe máy). ⭐ **Ba cái đó ghép lại chính là Zero Trust.**

---

## 📘 10. 🟡 REST API SECURITY (blueprint 5.3 — Describe)

> ⭐ Mục nhỏ nhưng ⭐ **chắc chắn có câu hỏi**, và nó là ⭐ **nền cho Module-12**.

### 10.1 ⭐⭐ Các cách xác thực API

| Cách | Hoạt động | ⭐ Nhận xét |
|---|---|---|
| ⭐ **Basic Auth** | ⭐ `username:password` **mã hóa Base64** trong header `Authorization` | 🔴 ⭐⭐ **Base64 KHÔNG PHẢI mã hóa — giải ngược trong 1 giây.** ⭐ **BẮT BUỘC đi kèm HTTPS** |
| ⭐ **API Key** | Một chuỗi bí mật trong header hoặc query string | ⭐ Đơn giản. 🔴 **Để trong URL là sai** (lọt vào log) |
| ⭐⭐ **Bearer Token / JWT** | ⭐ Đăng nhập một lần → nhận **token có hạn** → gắn vào header các lần sau | ⭐⭐ **Phổ biến nhất.** ⭐ Token hết hạn thì phải xin lại |
| ⭐ **OAuth 2.0** | ⭐ Ủy quyền cho bên thứ ba **mà không đưa mật khẩu** | Dùng khi tích hợp nhiều hệ thống |
| ⭐ **mTLS** | Cả client và server đều dùng chứng thư | An toàn nhất, triển khai nặng |

### 10.2 ⭐⭐ Luồng token của hai sản phẩm Cisco — đề hay hỏi

```
   DNA CENTER — Basic Auth đổi lấy token
   ① POST https://<dnac>/dna/system/api/v1/auth/token
      Header: Authorization: Basic <base64(user:pass)>
   ② Trả về: { "Token": "eyJhbGciOi..." }
   ③ Mọi lời gọi sau: Header  X-Auth-Token: eyJhbGciOi...
   Token hết hạn (thường ~1 giờ) → xin lại

   vMANAGE (SD-WAN) — session cookie
   ① POST https://<vmanage>/j_security_check   (form: j_username, j_password)
   ② Trả về cookie JSESSIONID
   ③ Với lệnh GHI: xin thêm X-XSRF-TOKEN từ /dataservice/client/token
```

> ⭐⭐ **Nhớ hai điểm:** ⭐ **DNAC = `X-Auth-Token`** · ⭐ **vManage = cookie `JSESSIONID` + `X-XSRF-TOKEN`.**

### 10.3 ⭐⭐ Mã trạng thái HTTP — 401 vs 403 là câu kinh điển

| Mã | Nghĩa | ⭐ Ghi chú |
|:---:|---|---|
| **200 OK** | Thành công | |
| **201 Created** | Đã tạo tài nguyên | Thường trả về sau POST |
| **204 No Content** | Thành công, không có nội dung | Thường sau DELETE |
| 🔴 ⭐⭐ **401 Unauthorized** | ⭐⭐ **CHƯA XÁC THỰC** *(hoặc token sai/hết hạn)* | ⭐ **"Tôi không biết anh là ai"** → ⭐ **xin token mới** |
| 🔴 ⭐⭐ **403 Forbidden** | ⭐⭐ **ĐÃ xác thực nhưng KHÔNG ĐỦ QUYỀN** | ⭐ **"Tôi biết anh là ai, nhưng anh không được phép"** → ⭐ **vấn đề RBAC, xin token mới VÔ ÍCH** |
| **404 Not Found** | Sai URL/endpoint | |
| **405 Method Not Allowed** | Sai verb (dùng GET nơi cần POST) | |
| ⭐ **429 Too Many Requests** | ⭐ **Vượt rate limit** | ⭐ Phải chờ (`Retry-After`) hoặc giảm tần suất gọi |
| **500 Internal Server Error** | Lỗi phía server | |

> 🔴 ⭐⭐ **401 vs 403 — đây là câu hỏi được ra nhiều nhất của mục 5.3.**
> ⭐ **401 = "anh CHƯA đăng nhập"** *(sửa: lấy token mới)*
> ⭐ **403 = "anh ĐÃ đăng nhập nhưng KHÔNG có quyền"** *(sửa: đổi quyền tài khoản — lấy token mới không giúp gì)*

### 10.4 ⭐ Checklist bảo mật REST API

| # | Việc | Vì sao |
|:---:|---|---|
| 1 | ⭐⭐ **LUÔN dùng HTTPS/TLS** | ⭐ Không có TLS thì token và Basic Auth **đi trần trên mạng** |
| 2 | ⭐ **Token có thời hạn + xoay khóa định kỳ** | Token bị lộ cũng chỉ hại trong thời gian ngắn |
| 3 | ⭐⭐ **KHÔNG hardcode credential trong script** | ⭐ Dùng **biến môi trường / vault**. 🔴 ⭐ **Push credential lên Git là tai nạn kinh điển** |
| 4 | ⭐ **RBAC / least privilege** | Tài khoản đọc-báo-cáo thì không cần quyền ghi cấu hình |
| 5 | ⭐ **Rate limiting** | Chống brute-force và chống chính script của bạn làm sập controller |
| 6 | ⭐ **Input validation** | Chống injection |
| 7 | ⭐ **Ghi log + audit** | Biết ai đã gọi API nào |
| 8 | ⭐ **Không để secret trong URL** | ⭐ URL bị ghi vào log của proxy, server, trình duyệt |
| 9 | ⭐ **Kiểm tra chứng thư server** | 🔴 ⭐ `verify=False` trong Python **là lỗ hổng MITM** — chỉ dùng trong lab |

---

## 📘 11. 🟡 BỔ TRỢ — Tính năng an ninh Layer 2

> ⚠️ ⭐ **Mục này KHÔNG có trong blueprint ENCOR v1.1** *(nó thuộc CCNA và ENARSI)*.
> ⭐ **Nhưng nó là kiến thức đi làm bắt buộc, và có thể xuất hiện gián tiếp.** ⭐ **Đọc 20 phút, không lab sâu.**

| Tính năng | ⭐ Chống tấn công gì | Lệnh chính |
|---|---|---|
| ⭐⭐ **DHCP Snooping** | ⭐⭐ **DHCP server giả** (rogue DHCP phát gateway giả để nghe lén) | `ip dhcp snooping` · `ip dhcp snooping vlan 10` · ⭐ `ip dhcp snooping trust` **trên port hướng DHCP server thật** |
| ⭐⭐ **DAI** (Dynamic ARP Inspection) | ⭐⭐ **ARP spoofing / MITM** | `ip arp inspection vlan 10` · ⭐ **dùng bảng binding của DHCP Snooping** |
| ⭐ **IP Source Guard** | ⭐ **Giả mạo IP nguồn** | `ip verify source` · ⭐ cũng dựa vào bảng binding |
| ⭐ **Port Security** | ⭐ **CAM table overflow** · cắm thiết bị lạ | `switchport port-security maximum 2` · `violation restrict\|protect\|shutdown` · `mac-address sticky` |
| ⭐ **Storm Control** | Bão broadcast/multicast | `storm-control broadcast level 1.00` |
| ⭐ **Private VLAN** | Cách ly host **trong cùng VLAN** | `private-vlan isolated \| community` |
| ⭐ **BPDU Guard / Root Guard** | ⭐ Switch lạ cướp root bridge *(Module-02)* | `spanning-tree bpduguard enable` |

> 🔴 ⭐⭐ **Thứ tự phụ thuộc phải nhớ:**
> ⭐⭐ **DHCP Snooping phải bật TRƯỚC** → nó xây **bảng binding (MAC ↔ IP ↔ port ↔ VLAN)** →
> ⭐ **DAI và IP Source Guard đều DÙNG bảng đó.**
> 🔴 ⭐ **Bật DAI mà chưa có DHCP Snooping = chặn sạch ARP = sập mạng.**
>
> ⭐ **Và:** với thiết bị đặt IP tĩnh (server, máy in), ⭐ **phải khai `ip source binding` thủ công**,
> nếu không DAI sẽ chặn chúng.

> 🔴 ⭐ **Nhắc lại từ Module-08 §12:** ⭐ **KHÔNG bật `port-security maximum 1` trên port nối host ảo hóa**
> — một sợi cáp mang MAC của hàng chục VM.

---

## 📖 12. HIỂU RÕ HƠN

### 12.1 AAA là "thẻ nhân viên, quyền mở cửa, và sổ ra vào"

- ⭐ **Authentication** = ⭐ **quẹt thẻ ở cổng** → "anh là ai?"
- ⭐ **Authorization** = ⭐ **thẻ đó mở được những cửa nào** → "anh vào phòng server được không?"
- ⭐ **Accounting** = ⭐ **sổ ghi ai vào phòng nào lúc mấy giờ**

⭐ **TACACS+ vs RADIUS trong ẩn dụ này:**
- ⭐⭐ **TACACS+ = hệ thống của TÒA NHÀ VĂN PHÒNG**: kiểm soát ⭐ **từng cánh cửa một** (từng lệnh CLI),
  và ⭐ **cả cuộc trao đổi ở quầy lễ tân đều được che kín** (mã hóa toàn bộ gói).
- ⭐⭐ **RADIUS = hệ thống của CỔNG SÂN VẬN ĐỘNG**: chỉ hỏi ⭐ **"anh có vé không"** rồi cho vào
  (gộp authn+authz), và ⭐ **chỉ che mỗi tấm vé** (chỉ mã hóa mật khẩu).

⭐ Vì thế: ⭐ **quản trị router = TACACS+** (cần soi từng lệnh) · ⭐ **cho nhân viên vào Wi-Fi = RADIUS**
(chỉ cần vào hay không vào).

### 12.2 Fallback: vì sao "sai mật khẩu" khác "server chết"

⭐ Bạn gọi điện cho phòng nhân sự hỏi *"anh A có phải nhân viên không?"*:

- ⭐ **Nhân sự bắt máy và nói "KHÔNG"** → ⭐ **bạn có câu trả lời rồi.**
  🔴 ⭐ **Gọi sang phòng khác hỏi lại là VÔ LÝ** → ⭐ **đây là `reject`, KHÔNG fallback.**
- ⭐ **Nhân sự KHÔNG BẮT MÁY** → ⭐ **bạn chưa có câu trả lời** →
  ⭐ **hợp lý khi tra danh sách dự phòng trong ngăn kéo** → ⭐ **đây là `timeout` → fallback sang `local`.**

⭐⭐ **Đó chính xác là cách method list hoạt động.** ⭐ Và vì thế ⭐ **sai shared key trông y hệt
"server chết"** — router **không giải mã nổi câu trả lời**, nên với nó thì nhân sự **coi như không bắt máy.**

### 12.3 CoPP: bảo vệ "bộ não", không phải "đôi chân"

⭐ Một con router giống ⭐ **vận động viên có đôi chân siêu nhanh (ASIC/data plane) và một bộ não
bình thường (CPU/control plane)**.

- ⭐ Đôi chân chạy hàng triệu gói/giây **không mệt** — vì đó là phần cứng chuyên dụng.
- 🔴 ⭐ **Nhưng nếu ai đó liên tục hỏi bộ não hàng triệu câu hỏi mỗi giây** (gói gửi **tới chính router**),
  ⭐ **bộ não quá tải** → ⭐ **quên gửi OSPF hello** → ⭐ **hàng xóm tưởng anh ta chết** → ⭐ **cả mạng hội tụ lại.**
- ⭐⭐ **Điều đáng sợ: đôi chân vẫn khỏe.** ⭐ `show interface` sạch, băng thông còn dư, ⭐ **mà mạng vẫn sập.**

⭐⭐ **CoPP = người thư ký đứng trước cửa phòng bộ não**, ⭐ **lọc và giới hạn xem mỗi giây được phép
hỏi bao nhiêu câu, loại nào.**

🔴 ⭐ **Và nếu bạn cho thư ký quá nghiêm khắc** → ⭐ **chính bạn cũng không gặp được bộ não** →
⭐ **đó là lý do phải bắt đầu bằng chế độ "chỉ ĐẾM, không chặn".**

### 12.4 802.1X là "bảo vệ ở cửa, KHÔNG phải người quyết định"

⭐ Switch giống ⭐ **anh bảo vệ đứng ở cửa**:
- ⭐ Anh ta ⭐ **giữ cửa đóng** cho tới khi có lệnh mở
- ⭐ Anh ta ⭐ **cầm giấy tờ của khách chạy vào hỏi giám đốc** (RADIUS/ISE)
- 🔴 ⭐⭐ **Anh ta KHÔNG tự quyết định gì cả**
- ⭐ Giám đốc trả lời: ⭐ **"cho vào, và đưa anh ta lên tầng 5, chỉ được vào phòng A và B"**
  → ⭐ **đó chính là `Access-Accept` kèm VLAN + dACL + SGT**

⭐⭐ **Và ba tình huống dự phòng cũng rất đời:**
- ⭐ **Khách không có giấy tờ gì** (không có supplicant) → ⭐ **cho vào phòng chờ** = **Guest VLAN**
- ⭐ **Giấy tờ sai** → ⭐ **phòng cách ly** = **Auth-fail VLAN**
- 🔴 ⭐⭐ **GIÁM ĐỐC ĐI VẮNG** (RADIUS chết) → ⭐⭐ **phải có quy định sẵn: "cứ cho nhân viên vào bình thường"**
  = ⭐⭐ **Critical VLAN.** ⭐ **Không có quy định này thì cả công ty đứng ngoài cửa.**

### 12.5 TrustSec: dán nhãn người, đừng đánh số ghế

- 🔴 ⭐ **ACL truyền thống = viết nội quy theo SỐ GHẾ**: *"ghế A1–A50 được vào phòng họp"*.
  ⭐ Ai đó đổi chỗ ngồi → ⭐ **phải viết lại toàn bộ nội quy.**
- ⭐⭐ **TrustSec = dán nhãn lên NGƯỜI**: *"ai đeo thẻ VÀNG thì được vào phòng họp"*.
  ⭐ **Người đó ngồi đâu cũng không quan trọng.**

⭐ Và ba pha rất tự nhiên:
⭐ **Classification** = phát thẻ ở quầy lễ tân (ISE gán SGT khi 802.1X) ·
⭐ **Propagation** = ⭐ **thẻ phải nhìn thấy được suốt đường đi** (inline tag / SXP / VXLAN) ·
⭐ **Enforcement** = ⭐ **bảo vệ ở CỬA PHÒNG ĐÍCH kiểm tra thẻ** (⭐ vì thế enforcement ở **egress**).

### 12.6 MACsec vs IPsec: xe bọc thép từng chặng vs vali khóa suốt hành trình

- ⭐ **MACsec = xe bọc thép chở tiền giữa hai ngân hàng liền kề.**
  ⭐ **Mỗi chặng một xe bọc thép riêng.** ⭐ Tới ngân hàng trung gian thì ⭐ **dỡ ra, đếm, rồi cho lên xe khác.**
  ⭐ **Ngân hàng trung gian NHÌN THẤY tiền.** ⭐ Đổi lại: **bọc thép rất nhanh và rẻ** (phần cứng).
- ⭐ **IPsec = vali khóa số, khóa từ nhà và chỉ mở ở đích.**
  ⭐ **Mọi trạm trung chuyển đều KHÔNG mở được.** ⭐ Đổi lại: chậm hơn, và ⭐ **trạm trung gian không
  làm gì được với nội dung** (không QoS theo ứng dụng, không kiểm tra an ninh).

⭐⭐ **Vì thế: MACsec cho đường trục trong nhà mình (cần tốc độ, và mình sở hữu mọi switch).
IPsec cho đường đi qua Internet (không tin ai ở giữa).**

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

---

## 💡 15. THỰC CHIẾN ĐI LÀM

| # | Tình huống thật | 🔴 Điều người mới làm sai | ⭐ Cách làm đúng |
|:---:|---|---|---|
| 1 | Triển khai AAA lên 200 switch | Push `aaa new-model` bằng script cho cả 200 con | 🔴 ⭐⭐ **Nếu sai một chi tiết = mất 200 thiết bị cùng lúc.** ⭐ **Làm 1 con trước, test `test aaa`, đợi 1 tuần, rồi mới nhân rộng.** ⭐ **Luôn có `local` fallback + user local trên MỌI thiết bị** |
| 2 | Sếp bảo "mã hóa hết mật khẩu trong config" | Bật `service password-encryption` rồi báo cáo xong | 🔴 ⭐⭐ **Type 7 giải ngược trong 1 giây.** ⭐ **Phải chuyển sang `algorithm-type scrypt` (type 9)** cho `enable secret` và mọi `username` |
| 3 | Bật CoPP theo bài mẫu trên mạng | Copy nguyên policy có `exceed-action drop` | 🔴 ⭐⭐ **Rớt OSPF/BGP ngay đêm đó.** ⭐ **Bắt đầu `exceed-action transmit`, đo vài ngày, rồi siết** |
| 4 | Bật 802.1X cho toàn công ty | Bật thẳng Closed Mode vào thứ Hai | 🔴 ⭐⭐ **Hàng chục máy in/camera/máy chấm công không ai biết sẽ rớt cùng lúc.** ⭐ **Monitor Mode vài tuần trước → lập danh sách → rồi mới siết** |
| 5 | ISE cần bảo trì 30 phút | Cứ tắt, nghĩ "chỉ 30 phút" | 🔴 ⭐⭐ **Không có Critical VLAN = 2000 người mất mạng.** ⭐ **Cấu hình `authentication event server dead action authorize vlan <data>` TRƯỚC** |
| 6 | Viết ACL cho DMZ | Không có dòng `deny ip any any log` cuối | ⭐ **Deny ngầm không đếm, không log** → ⭐ khi có sự cố bạn **mù hoàn toàn**. ⭐ **Luôn viết deny tường minh** |
| 7 | Áp ACL IPv6 lần đầu | Viết `deny ipv6 any any` ở cuối | 🔴 ⭐⭐ **Giết NDP → IPv6 chết sạch.** ⭐ **Thêm `permit icmp any any nd-na/nd-ns` lên TRƯỚC** |
| 8 | Sửa numbered ACL đang chạy | `no access-list 100` rồi gõ lại | 🔴 ⭐⭐ **Interface hở toang trong lúc gõ.** ⭐ **Dùng named ACL + sequence number** để sửa từng dòng |
| 9 | Bật DAI để chống ARP spoofing | Bật `ip arp inspection vlan 10` luôn | 🔴 ⭐⭐ **Chưa có DHCP Snooping = không có bảng binding = chặn SẠCH ARP.** ⭐ **DHCP Snooping trước, và khai `ip source binding` cho IP tĩnh** |
| 10 | Triển khai PEAP cho Wi-Fi công ty | Để client tự cấu hình | 🔴 ⭐⭐ **Không bật "validate server certificate" → AP giả + RADIUS giả thu được hash mật khẩu nhân viên.** ⭐ **Đẩy cấu hình bằng GPO/MDM, ghim chứng thư CA** |
| 11 | Bật WPA3 cho SSID chính | Đặt `pmf mandatory` ngay | 🔴 ⭐ **Máy cũ không hỗ trợ 802.11w biến mất khỏi mạng.** ⭐ **Dùng transition mode WPA2+WPA3 với `pmf optional`** trước |
| 12 | Khách kêu không thấy trang đăng nhập | Restart WLC | ⭐⭐ **Kiểm tra pre-auth ACL có mở UDP 53 (DNS) chưa** — ⭐ đây là nguyên nhân số 1 |
| 13 | Viết script gọi API DNAC | Hardcode username/password, `verify=False` | 🔴 ⭐⭐ **Credential lọt lên Git + lỗ hổng MITM.** ⭐ **Biến môi trường/vault + kiểm tra chứng thư** |
| 14 | Script API trả 403, viết lại code xin token | Nghĩ token hết hạn | ⭐⭐ **403 = ĐÃ xác thực nhưng KHÔNG có quyền** → ⭐ **xin token mới vô ích, phải sửa RBAC.** ⭐ **401 mới là "xin token lại"** |
| 15 | Cần cách ly camera khỏi mạng nhân viên | Viết ACL theo subnet | ⭐ ACL sẽ phình và **vỡ mỗi lần đổi subnet**. ⭐ **Dùng SGT (TrustSec)** — chính sách theo **danh tính**, không theo IP |
| 16 | Ai đó hỏi "MACsec hay IPsec?" | Chọn bừa | ⭐ **Đường trục trong nhà mình, cần line-rate → MACsec.** ⭐ **Qua Internet, không tin ai ở giữa → IPsec** |

> 🔴 ⭐⭐ **Bốn câu thần chú của module này:**
> 1. ⭐ **"Tạo user local TRƯỚC `aaa new-model`. Luôn có `local` cuối method list. Giữ phiên SSH thứ hai."**
> 2. ⭐ **"CoPP và 802.1X: ĐO trước, SIẾT sau."**
> 3. ⭐ **"Type 7 không phải bảo mật. Dùng type 9 (scrypt)."**
> 4. ⭐ **"401 = chưa đăng nhập. 403 = đăng nhập rồi nhưng không có quyền."**

---

## 🎓 16. BẪY TRONG ĐỀ ENCOR

| # | ⭐ Bẫy | ✅ Sự thật |
|:---:|---|---|
| 1 | "`service password-encryption` bảo vệ mật khẩu" | 🔴 ⭐⭐ **Chỉ tạo type 7 — GIẢI NGƯỢC trong 1 giây.** ⭐ Là "che mắt", không phải bảo mật |
| 2 | "`enable password` và `enable secret` như nhau" | 🔴 ⭐ **`enable secret` được HASH và LUÔN THẮNG.** ⭐ `enable password` chỉ type 0/7 |
| 3 | "Type 5 là an toàn nhất" | 🔴 ⭐ **Type 5 = MD5, đã yếu.** ⭐ **Type 8 (PBKDF2) và type 9 (scrypt) mới tốt** |
| 4 | "Privilege level mặc định của user EXEC là 0" | 🔴 ⭐ **Level 1.** ⭐ Level 0 chỉ có 5 lệnh (`disable/enable/exit/help/logout`) |
| 5 | "SSH tự chạy sau khi tạo user" | 🔴 ⭐ Cần **4 thứ**: hostname (≠Router) · `ip domain-name` · `crypto key generate rsa` · user local. ⭐ Rồi mới `transport input ssh` |
| 6 | 🔴 ⭐⭐ "TACACS+ dùng UDP" | 🔴 ⭐⭐ **TACACS+ = TCP 49.** ⭐ **RADIUS = UDP 1812/1813** |
| 7 | 🔴 ⭐⭐ "RADIUS mã hóa toàn bộ gói" | 🔴 ⭐⭐ **RADIUS chỉ mã hóa TRƯỜNG PASSWORD.** ⭐ **TACACS+ mã hóa TOÀN BỘ phần thân** |
| 8 | "RADIUS tách riêng cả 3 chữ A" | 🔴 ⭐⭐ **RADIUS GỘP authentication + authorization.** ⭐ **TACACS+ mới tách cả ba** |
| 9 | "RADIUS làm được command authorization" | 🔴 ⭐⭐ **Chỉ TACACS+** — đó là lý do quản trị thiết bị dùng TACACS+ |
| 10 | 🔴 ⭐⭐ "Sai mật khẩu thì router fallback sang `local`" | 🔴 ⭐⭐ **KHÔNG.** ⭐ Server **trả lời `reject` = ĐÃ trả lời → DỪNG**. ⭐ **Chỉ khi server IM LẶNG (timeout) mới fallback** |
| 11 | "`aaa new-model` không ảnh hưởng gì ngay" | 🔴 ⭐⭐ **Nó áp method list `default` lên MỌI line NGAY LẬP TỨC** → ⭐ **chưa có user local = tự khóa mình** |
| 12 | "Standard ACL nên đặt gần nguồn" | 🔴 ⭐⭐ **Standard → gần ĐÍCH** (nó chỉ khớp source). ⭐ **Extended → gần NGUỒN** |
| 13 | "Deny ngầm có thể xem bộ đếm" | 🔴 ⭐ **Deny ngầm KHÔNG đếm, KHÔNG log.** ⭐ Phải viết `deny ip any any log` tường minh |
| 14 | "Thêm dòng vào numbered ACL sẽ chèn đúng chỗ" | 🔴 ⭐ **Nó nối vào CUỐI — sau `deny` → vô dụng.** ⭐ **Dùng named ACL + sequence** |
| 15 | 🔴 ⭐⭐ "IPv6 ACL giống IPv4, chỉ đổi địa chỉ" | 🔴 ⭐⭐ **IPv6 ACL có BA dòng ngầm**: `permit icmp any any nd-na` · `nd-ns` · `deny ipv6 any any`. ⭐ **Viết `deny` tường minh = GIẾT NDP** |
| 16 | "IPv6 ACL dùng wildcard mask" | 🔴 ⭐ **Dùng prefix `/64`.** ⭐ Và **chỉ có named ACL**, áp bằng `ipv6 traffic-filter` |
| 17 | "RACL lọc được traffic trong cùng VLAN" | 🔴 ⭐⭐ **Không** — traffic đó không qua router. ⭐ **Phải dùng VACL** |
| 18 | "VACL kết thúc bằng permit ngầm" | 🔴 ⭐⭐ **Kết thúc bằng DROP ngầm** → ⭐ **luôn cần map cuối `action forward`** |
| 19 | "Thứ tự ingress là RACL → VACL → PACL" | 🔴 ⭐ **Ngược: PACL → VACL → RACL** |
| 20 | "uRPF strict luôn tốt hơn loose" | 🔴 ⭐ **Strict phá mạng có định tuyến BẤT ĐỐI XỨNG.** ⭐ Multihoming → dùng **loose** |
| 21 | "CoPP bảo vệ data plane" | 🔴 ⭐⭐ **CoPP bảo vệ CONTROL PLANE (CPU).** ⭐ Data plane do ASIC lo |
| 22 | "Nên đặt CoPP nghiêm ngặt ngay từ đầu" | 🔴 ⭐⭐ **Bắt đầu `exceed-action transmit` để ĐO.** ⭐ Siết ngay = tự đánh sập OSPF/SSH của mình |
| 23 | "CPPr có 2 sub-interface" | 🔴 ⭐ **BA: `host`, `transit`, `cef-exception`.** ⭐ **ARP và TTL-exceeded nằm ở `cef-exception`** |
| 24 | 🔴 ⭐⭐ "Switch quyết định cho client vào hay không" | 🔴 ⭐⭐ **Switch là AUTHENTICATOR — chỉ chuyển tiếp.** ⭐ **RADIUS/ISE mới quyết định** |
| 25 | "EAPoL chạy trên IP" | 🔴 ⭐⭐ **EAPoL là LAYER 2** — ⭐ client **chưa có IP** khi xác thực |
| 26 | "Thứ tự mặc định là MAB → 802.1X" | 🔴 ⭐ **802.1X → MAB → WebAuth** (mạnh nhất trước) |
| 27 | "multi-host an toàn vì mỗi MAC phải xác thực" | 🔴 ⭐⭐ **multi-host: MAC ĐẦU TIÊN xác thực, phần còn lại vào FREE.** ⭐ **multi-auth mới bắt mọi MAC xác thực** |
| 28 | "Điện thoại IP + PC dùng single-host" | 🔴 ⭐ **Dùng multi-domain (MDA)** — 1 voice + 1 data |
| 29 | "`authentication port-control auto` là mặc định" | 🔴 ⭐ **Mặc định là `force-authorized`** (cổng luôn mở). ⭐ **`auto` mới bật 802.1X thật** |
| 30 | "Chỉ cần cấu hình trên port là 802.1X chạy" | 🔴 ⭐⭐ **Thiếu `dot1x system-auth-control` toàn cục = KHÔNG CHẠY và KHÔNG BÁO LỖI** |
| 31 | "Guest VLAN dùng khi xác thực trượt" | 🔴 ⭐ **Guest VLAN = client KHÔNG TRẢ LỜI EAPoL.** ⭐ **Auth-fail VLAN mới là "trả lời nhưng trượt"** |
| 32 | "MAB an toàn vì dựa vào MAC" | 🔴 ⭐⭐ **MAC giả mạo cực dễ.** ⭐ Phải dùng kèm **profiling của ISE** |
| 33 | 🔴 ⭐ "PEAP cần chứng thư ở cả client và server" | 🔴 ⭐⭐ **PEAP: CHỈ SERVER.** ⭐ **EAP-TLS: CẢ HAI** |
| 34 | "WPA3-Personal dùng PSK" | 🔴 ⭐⭐ **WPA3-Personal dùng SAE** (chống dò mật khẩu offline) |
| 35 | "WPA3 PMF là tùy chọn" | 🔴 ⭐⭐ **WPA3 BẮT BUỘC PMF (802.11w)** |
| 36 | "OWE là mạng mở không mã hóa" | 🔴 ⭐ **OWE = mở (không mật khẩu) NHƯNG CÓ mã hóa** |
| 37 | 🔴 ⭐ "SGT do switch gán" | 🔴 ⭐⭐ **ISE gán** — switch nhận trong `Access-Accept` |
| 38 | "TrustSec enforcement ở ingress" | 🔴 ⭐⭐ **Ở EGRESS** — vì chỉ ở đó mới biết SGT của **ĐÍCH** |
| 39 | "SXP dùng để mã hóa SGT" | 🔴 ⭐ **SXP chỉ TRUYỀN ánh xạ IP↔SGT (TCP 64999)** cho thiết bị không inline-tag được |
| 40 | 🔴 ⭐⭐ "MACsec mã hóa end-to-end" | 🔴 ⭐⭐ **MACsec là L2, HOP-BY-HOP.** ⭐ **IPsec mới end-to-end (L3)** |
| 41 | "MACsec dùng IKE để trao khóa" | 🔴 ⭐ **MACsec dùng MKA.** ⭐ IPsec mới dùng IKE |
| 42 | "IDS chặn được tấn công" | 🔴 ⭐⭐ **IDS out-of-band, CHỈ cảnh báo.** ⭐ **IPS inline mới chặn được** |
| 43 | "NGFW chỉ là firewall nhanh hơn" | 🔴 ⭐⭐ **NGFW = stateful + nhận diện ỨNG DỤNG + NGƯỜI DÙNG + IPS tích hợp + threat intel** |
| 44 | 🔴 ⭐⭐ "401 và 403 đều là lỗi xác thực" | 🔴 ⭐⭐ **401 = CHƯA xác thực (xin token mới).** ⭐ **403 = ĐÃ xác thực nhưng KHÔNG có quyền (xin token vô ích)** |
| 45 | "Basic Auth đã mã hóa credential" | 🔴 ⭐⭐ **Base64 KHÔNG phải mã hóa** — giải ngược tức thì. ⭐ **Bắt buộc kèm HTTPS** |
| 46 | "DAI hoạt động độc lập" | 🔴 ⭐⭐ **DAI DÙNG bảng binding của DHCP Snooping.** ⭐ Chưa bật snooping = chặn sạch ARP |

---

## 🐛 17. GỠ LỖI NHANH

### 17.1 ⭐ Hộp lệnh vạn năng

```
═══ DEVICE ACCESS ═══
show run | include enable secret|username|service password
show ip ssh                          ! version phải là 2.0
show ssh                             ! phiên đang mở
show crypto key mypubkey rsa         ! đã sinh khóa chưa, bao nhiêu bit
show login                           ! trạng thái login block-for / quiet-mode
show users
show privilege                       ! đang ở level mấy
show parser view

═══ AAA ═══
test aaa group <GRP> <user> <pass> legacy       ! TEST TRƯỚC KHI LOGOUT
test aaa group <GRP> <user> <pass> new-code
show aaa servers                                ! UP/DEAD + accept/reject/timeout
show aaa sessions
show aaa method-lists all
show tacacs
show radius statistics
debug aaa authentication                           ! ⚠️ chỉ lab
debug tacacs / debug radius authentication

═══ ACL ═══
show access-lists <NAME>                        ! BỘ ĐẾM TỪNG DÒNG
show ip interface Gi0/0 | include access list      ! ACL nào, chiều nào
show ipv6 access-list
show vlan access-map  /  show vlan filter          ! VACL
show time-range
clear ip access-list counters <NAME>            ! reset trước khi test
show ip interface Gi0/0 | include verify           ! uRPF + số drop

═══ CoPP ═══
show policy-map control-plane                   ! lệnh chính
show policy-map control-plane input class <CM>
show processes cpu sorted | exclude 0.00        ! CPU bận vì cái gì
show processes cpu history

═══ 802.1X / NAC ═══
show dot1x | include Sysauthcontrol             ! KIỂM TRA ĐẦU TIÊN
show access-session interface Gi0/2 details    ! LỆNH QUAN TRỌNG NHẤT
show authentication sessions interface Gi0/2 details   ! (IOS cũ)
show dot1x all / show dot1x interface Gi0/2 details
show mab all
debug dot1x all                                    ! ⚠️ chỉ lab

═══ TRUSTSEC / MACSEC ═══
show cts environment-data
show cts role-based sgt-map all
show cts role-based permissions
show cts sxp connections
show macsec summary / show macsec interface <intf>
show mka sessions

═══ WIRELESS (C9800) ═══
show wlan id <n>
show wireless profile policy detailed <POL>        ! aaa-override bật chưa
show wireless client mac-address <MAC> detail
debug wireless mac <H.H.H> internal                ! RadioActive Trace

═══ L2 SECURITY ═══
show ip dhcp snooping / show ip dhcp snooping binding
show ip arp inspection statistics
show port-security interface <intf>
```

### 17.2 ⭐⭐ Bảng: triệu chứng → nguyên nhân → cách sửa

| 🔴 Triệu chứng | ⭐ Nguyên nhân | ✅ Cách sửa |
|---|---|---|
| 🔴 ⭐⭐ **Không SSH vào được sau khi bật AAA** | ⭐⭐ **Method list thiếu `local`**, hoặc **chưa tạo user local** trước `aaa new-model` | ⭐ Dùng phiên SSH đang mở (hoặc console) → thêm `local` vào cuối method list. ⭐ **Bài học: luôn giữ phiên thứ hai** |
| ⭐ **Sai mật khẩu nhưng KHÔNG fallback sang local** | ⭐⭐ **Server trả `reject` = ĐÃ trả lời** → đúng theo thiết kế, không fallback | ⭐ Không phải lỗi. ⭐ Nếu muốn kiểm chứng: `show aaa servers` → xem `reject` hay `timeouts` tăng |
| ⭐ **Server sống mà router vẫn báo DEAD** | ⭐⭐ **Sai shared key** · firewall chặn TCP 49 / UDP 1812 · sai source-interface | ⭐ **Sai key trông y hệt "server chết"** — router không giải mã nổi. ⭐ Kiểm tra key hai đầu + `ip tacacs source-interface` |
| ⭐ **Đăng nhập được nhưng chỉ vào user EXEC (`>`)** | ⭐ Thiếu `aaa authorization exec` · server không trả **privilege level 15** | ⭐ Thêm `aaa authorization exec default group <G> local if-authenticated` · kiểm tra shell profile trên ISE |
| ⭐⭐ **ACL "trông đúng" mà không chặn / không cho qua** | ⭐ Áp **sai chiều** (in/out) · sai interface · gói không tới đó · thứ tự dòng sai | ⭐⭐ **`clear ip access-list counters` → tạo traffic → `show access-lists`.** ⭐ **Không dòng nào tăng = gói không tới hoặc sai chiều** |
| ⭐ **Không biết ACL đang chặn bao nhiêu** | ⭐ Chỉ có **deny ngầm** (không đếm, không log) | ⭐ Thêm `deny ip any any log` **tường minh** ở cuối |
| ⭐ **Thêm dòng vào ACL mà không có tác dụng** | ⭐ Numbered ACL → dòng mới **nối vào CUỐI**, sau `deny` | ⭐ **Chuyển sang named ACL** + dùng sequence number để chèn |
| 🔴 ⭐⭐ **Áp ACL IPv6 xong là IPv6 chết hoàn toàn** | ⭐⭐ **Viết `deny ipv6 any any` tường minh → chặn NDP** | ⭐ Thêm `permit icmp any any nd-na` và `nd-ns` **lên TRƯỚC**. ⭐ Kiểm chứng: `show ipv6 neighbors` trống |
| 🔴 ⭐ **Áp VACL xong cả VLAN mất kết nối** | ⭐⭐ **VACL kết thúc bằng `drop` ngầm** | ⭐ Thêm map cuối `action forward` |
| ⭐ **Hai máy cùng VLAN vẫn nói chuyện được dù đã có ACL** | ⭐ Dùng **RACL** — traffic **không qua router** | ⭐ **Phải dùng VACL** |
| ⭐ **uRPF drop traffic hợp lệ** | ⭐ **Strict mode** trên mạng định tuyến **bất đối xứng** | ⭐ Đổi sang `reachable-via any` (loose) |
| 🔴 ⭐⭐ **Bật CoPP xong rớt OSPF/BGP neighbor** | ⭐⭐ **Hạn mức quá thấp** hoặc **quên phân loại routing protocol** | ⭐ Đổi mọi class về `exceed-action transmit`, đo lại. ⭐ **Class routing phải rộng rãi** |
| ⭐ **CoPP: `exceeded` tăng đều** | (a) đang bị tấn công · (b) ⭐ **bạn đặt hạn mức quá thấp** | ⭐ **Xem traffic ĐẾN TỪ ĐÂU.** Từ mạng quản trị của mình → là (b) |
| ⭐ **CPU 100% mà interface sạch** | ⭐ **Tấn công/vòng lặp vào CONTROL PLANE** | ⭐ `show processes cpu sorted` tìm process ngốn CPU → áp CoPP |
| 🔴 ⭐⭐ **802.1X cấu hình đủ mà "không có gì xảy ra"** | ⭐⭐ **Thiếu `dot1x system-auth-control` toàn cục** | ⭐⭐ **`show dot1x \| include Sysauthcontrol` — kiểm tra ĐẦU TIÊN** |
| ⭐⭐ **Xác thực thành công nhưng VLAN/dACL/SGT không áp** | ⭐⭐ Thiếu `aaa authorization network default group ...` *(switch)* hoặc thiếu ⭐ **`aaa-override`** *(WLC)* | ⭐ Thêm dòng tương ứng. ⭐ Đây là **cùng một lỗi ở hai nền tảng** |
| ⭐ **Máy in mất 90 giây mới lên mạng** | ⭐ 802.1X chờ hết timeout (30s × 3) mới sang MAB | ⭐ `dot1x timeout tx-period 7` → còn ~21s. Hoặc đảo `authentication order mab dot1x` cho port máy in |
| 🔴 ⭐⭐ **RADIUS chết → cả công ty mất mạng** | ⭐⭐ **Chưa cấu hình Critical VLAN** | ⭐ `authentication event server dead action authorize vlan <data>` + `... authorize voice` |
| ⭐ **Client vào nhầm Guest VLAN** | ⭐ Client **không có supplicant** hoặc supplicant chưa bật | ⭐ `show access-session ... details` → `dot1x: No response` xác nhận |
| ⭐ **Khách có IP nhưng không thấy portal** | ⭐⭐ **Pre-auth ACL chặn DNS (UDP 53)** · DoH · HSTS cache | ⭐ Mở UDP 53 + DHCP. ⭐ Bảo khách mở một trang **`http://`** |
| ⭐ **Bật WPA3 xong máy cũ mất SSID** | ⭐ **PMF mandatory** — client không hỗ trợ 802.11w | ⭐ Dùng **transition mode WPA2+WPA3** với `pmf optional` |
| ⭐ **SGT không tới được thiết bị enforcement** | ⭐ Thiết bị trung gian **không inline-tag được** | ⭐ Dùng **SXP** (TCP 64999) · `show cts sxp connections` |
| 🔴 ⭐ **Bật DAI xong VLAN chết** | ⭐⭐ **Chưa bật DHCP Snooping** → không có bảng binding | ⭐ Bật `ip dhcp snooping` trước · khai `ip source binding` cho IP tĩnh |
| ⭐ **API trả 401** | ⭐ **Chưa xác thực / token hết hạn / token sai** | ⭐ **Xin token mới** |
| ⭐ **API trả 403** | ⭐⭐ **ĐÃ xác thực nhưng tài khoản KHÔNG có quyền** | ⭐⭐ **Sửa RBAC** — ⭐ **xin token mới VÔ ÍCH** |
| ⭐ **API trả 429** | ⭐ Vượt rate limit | ⭐ Chờ theo `Retry-After`, giảm tần suất, gộp request |

### 17.3 ⭐ Quy trình chẩn đoán 802.1X — 6 bước

```
① show dot1x | include Sysauthcontrol
      → Disabled?  →  thiếu "dot1x system-auth-control". DỪNG, sửa cái này trước.

② show access-session interface <intf> details
      → CLIENT ĐANG DỪNG Ở ĐÂU?  (Unauthorized / Running / Authorized)

③ Xem "Method status list":
      · dot1x = No response      → client KHÔNG có supplicant → sẽ rơi xuống MAB/Guest
      · dot1x = Authc Failed     → server TRẢ LỜI TRƯỢT → sai mật khẩu/chứng thư
      · dot1x = Running mãi      → không tới được server

④ show aaa servers | include host|State
      → DEAD?  →  firewall / sai key / sai IP  →  và Critical VLAN đã cấu hình chưa?

⑤ Authorized rồi nhưng SAI VLAN/thiếu ACL?
      → thiếu "aaa authorization network default group ..."  (hoặc "aaa-override" trên WLC)

⑥ Vẫn không thông sau khi Authorized?
      → Không còn là vấn đề 802.1X. Xem VLAN, trunk, DHCP  (Module-07B §9)
```

---

## 📝 18. QUIZ TỰ KIỂM TRA

**1.** Phân biệt password type 5, 7, 9. `service password-encryption` tạo ra loại nào?
<details><summary>Đáp án</summary>

⭐ **Type 5** = MD5 có salt — 🟡 **đã yếu**.
🔴 ⭐⭐ **Type 7** = Vigenère — ⭐ **GIẢI NGƯỢC ĐƯỢC trong 1 giây. KHÔNG PHẢI bảo mật.**
⭐⭐ **Type 9** = scrypt — ⭐ **tốt nhất, nên dùng** *(type 8 = PBKDF2 cũng tốt)*.

⭐⭐ **`service password-encryption` CHỈ tạo ra type 7** → ⭐ **nó là "che mắt", không bảo vệ gì.**
⭐ Dùng đúng: `enable algorithm-type scrypt secret ...` và `username X algorithm-type scrypt secret ...`
</details>

**2.** Bốn thứ cần có để SSH hoạt động trên router?
<details><summary>Đáp án</summary>

⭐ **(1)** `hostname` khác mặc định · ⭐ **(2)** `ip domain-name` · ⭐ **(3)** `crypto key generate rsa modulus 2048`
· ⭐ **(4)** tài khoản (`username ... secret` hoặc AAA)

⭐ Rồi trên line: `transport input ssh` + `login local`.
⭐ Và ⭐ **`ip ssh version 2`** — v1 có lỗ hổng.
</details>

**3.** TACACS+ vs RADIUS: port, mã hóa, tách 3A, dùng cho việc gì?
<details><summary>Đáp án</summary>

| | ⭐ **TACACS+** | ⭐ **RADIUS** |
|---|---|---|
| Port | ⭐⭐ **TCP 49** | ⭐⭐ **UDP 1812/1813** |
| Mã hóa | ⭐⭐ **TOÀN BỘ phần thân gói** | 🔴 ⭐ **CHỈ trường password** |
| Tách 3A | ⭐⭐ **Tách cả ba** | 🔴 **Gộp authn+authz** |
| Command authorization | ⭐⭐ **Có** | ❌ Không |
| ⭐ Dùng cho | ⭐⭐ **Quản trị THIẾT BỊ** | ⭐⭐ **Cho người dùng vào MẠNG** (802.1X/Wi-Fi/VPN) |
</details>

**4.** `aaa authentication login default group GRP-TAC local`. Server trả lời "sai mật khẩu". Router có thử `local` không? Vì sao?
<details><summary>Đáp án</summary>

🔴 ⭐⭐ **KHÔNG.**

⭐ Method list ⭐ **chỉ chuyển sang phương pháp tiếp theo khi phương pháp trước KHÔNG TRẢ LỜI.**
⭐ Server trả `reject` = ⭐ **đã trả lời rồi** → ⭐ **dừng lại, từ chối đăng nhập.**

⭐ **Chỉ khi server IM LẶNG (timeout / DEAD)** mới fallback sang `local`.
⭐ Kiểm chứng: `show aaa servers` — xem ⭐ **`reject` tăng (đã trả lời)** hay ⭐ **`timeouts` tăng (im lặng)**.
</details>

**5.** Ba việc phải làm để không tự khóa mình khi triển khai AAA?
<details><summary>Đáp án</summary>

⭐⭐ **(1) TẠO USER LOCAL TRƯỚC khi gõ `aaa new-model`** — vì nó áp method list `default` lên mọi line **ngay lập tức**.
⭐⭐ **(2) LUÔN có `local` ở cuối method list** — server chết vẫn vào được.
⭐⭐ **(3) GIỮ MỘT PHIÊN SSH THỨ HAI đang mở** trong lúc cấu hình.

⭐ Cộng thêm: ⭐ **`test aaa group ...` TRƯỚC KHI logout**, và ⭐ tách method list riêng cho console.
</details>

**6.** Standard ACL đặt gần nguồn hay gần đích? Vì sao?
<details><summary>Đáp án</summary>

⭐⭐ **Standard ACL → đặt GẦN ĐÍCH.**

⭐ Vì standard ACL ⭐ **chỉ khớp địa chỉ NGUỒN** — nó không biết gói định đi đâu.
⭐ Đặt gần nguồn sẽ ⭐ **chặn nhầm cả traffic đi tới những đích lẽ ra được phép.**

⭐⭐ **Extended ACL → đặt GẦN NGUỒN**, vì nó khớp cả nguồn lẫn đích → ⭐ chặn sớm, tiết kiệm băng thông.
</details>

**7.** Vì sao luôn nên viết `deny ip any any log` tường minh ở cuối ACL?
<details><summary>Đáp án</summary>

⭐ Vì ⭐ **deny NGẦM không có bộ đếm và không ghi log.**

⭐ Có dòng tường minh thì bạn:
1. ⭐ **Thấy được ACL đang chặn bao nhiêu gói** (`show access-lists`)
2. ⭐ **Có log để điều tra** (`show logging`)

⭐ Không có nó → khi sự cố xảy ra bạn **mù hoàn toàn**, không biết ACL có phải thủ phạm không.
</details>

**8.** Bạn viết IPv6 ACL kết thúc bằng `deny ipv6 any any`. Chuyện gì xảy ra và vì sao?
<details><summary>Đáp án</summary>

🔴 ⭐⭐ **IPv6 chết hoàn toàn.**

⭐ Cuối mỗi IPv6 ACL, IOS tự thêm **BA dòng ngầm theo thứ tự:**
```
permit icmp any any nd-na       Neighbor Advertisement
permit icmp any any nd-ns       Neighbor Solicitation
deny   ipv6 any any
```
⭐ **NDP là "ARP của IPv6".** ⭐ Khi bạn viết `deny ipv6 any any` **tường minh**, hai dòng permit NDP ngầm
⭐ **nằm SAU nó → không bao giờ tới lượt** → ⭐ **không phân giải được địa chỉ lớp 2.**

✅ **Sửa:** tự thêm `permit icmp any any nd-na` và `nd-ns` ⭐ **lên TRƯỚC** dòng deny.
</details>

**9.** RACL, VACL, PACL — thứ tự xử lý ingress? Cái nào lọc được traffic trong cùng VLAN?
<details><summary>Đáp án</summary>

⭐⭐ **Ingress: PACL → VACL → RACL** *(egress: RACL → VACL)*

⭐⭐ **Chỉ VACL lọc được traffic BRIDGED trong cùng một VLAN** — vì traffic đó ⭐ **không đi qua router**,
nên RACL không bao giờ nhìn thấy.

🔴 ⭐ **Bẫy VACL: nó kết thúc bằng `drop` ngầm** → ⭐ **luôn phải có map cuối `action forward`**,
nếu không bạn chặn sạch cả VLAN.
</details>

**10.** CoPP bảo vệ cái gì? Vì sao phải bắt đầu với `exceed-action transmit`?
<details><summary>Đáp án</summary>

⭐⭐ **CoPP bảo vệ CONTROL PLANE (CPU/route processor)**, không phải data plane.

⭐ **Kịch bản:** kẻ tấn công bắn hàng triệu gói **TỚI địa chỉ của router** → gói bị **punt lên CPU** →
⭐ **CPU 100%** → ⭐ **OSPF/BGP hello không kịp gửi → rớt adjacency → sập mạng.**
⭐⭐ **Đáng sợ ở chỗ: data plane vẫn khỏe, `show interface` vẫn sạch.**

⭐⭐ **Vì sao bắt đầu `transmit`:** ⭐ bạn **chưa biết tốc độ THẬT** của từng loại traffic.
🔴 ⭐ **Đặt hạn mức quá thấp = tự đánh sập OSPF/SSH của chính mình.**
⭐ **Chạy chế độ "chỉ đếm" vài ngày → xem bộ đếm → rồi mới siết.** ⭐ Và **để `class-default` rộng rãi.**
</details>

**11.** Ba sub-interface của CPPr? ARP và TTL-exceeded rơi vào cái nào?
<details><summary>Đáp án</summary>

⭐ **`host`** — traffic gửi **tới địa chỉ của chính router** (SSH, SNMP, BGP/OSPF)
⭐ **`transit`** — traffic **đi xuyên qua** nhưng bị đẩy lên CPU (software-switched)
⭐⭐ **`cef-exception`** — thứ **CEF không xử lý nổi, phải punt**

⭐⭐ **ARP, gói TTL=1 (TTL-exceeded), và gói có IP options → `cef-exception`.**
</details>

**12.** Ba vai của 802.1X? Ai ra quyết định? EAPoL chạy ở tầng nào?
<details><summary>Đáp án</summary>

⭐⭐ **Supplicant** (phần mềm trên client) · ⭐⭐ **Authenticator** (switch/WLC) · ⭐⭐ **Authentication Server** (ISE/RADIUS)

🔴 ⭐⭐ **SERVER ra quyết định.** ⭐ Authenticator **chỉ giữ cổng đóng và làm người đưa thư** — nó **không tự quyết**.

⭐⭐ **EAPoL chạy ở LAYER 2** → ⭐ **client CHƯA CÓ IP khi xác thực.** ⭐ Đó là sức mạnh của 802.1X:
chặn ngay **trước khi** thiết bị có địa chỉ.
⭐ Giữa switch↔server là **RADIUS** (UDP 1812), không phải EAPoL.
</details>

**13.** Bốn host mode của 802.1X? Cái nào cho điện thoại IP + PC? Cái nào kém an toàn nhất?
<details><summary>Đáp án</summary>

⭐ **single-host** — đúng 1 MAC
🔴 ⭐ **multi-host** — ⭐ **MAC đầu tiên xác thực, TẤT CẢ còn lại vào FREE** → ⭐ **kém an toàn nhất**
⭐⭐ **multi-domain (MDA)** — ⭐ **1 voice + 1 data** → ⭐ **dùng cho điện thoại IP + PC**
⭐ **multi-auth** — ⭐ **mọi MAC đều phải xác thực riêng** → an toàn nhất
</details>

**14.** Guest VLAN, Auth-fail VLAN, Critical VLAN kích hoạt khi nào? Cái nào quan trọng nhất ngoài đời?
<details><summary>Đáp án</summary>

⭐ **Guest VLAN** — client ⭐ **KHÔNG TRẢ LỜI EAPoL** (không có supplicant)
⭐ **Auth-fail VLAN** — client ⭐ **CÓ trả lời nhưng xác thực TRƯỢT**
⭐⭐ **Critical VLAN** — 🔴 ⭐⭐ **RADIUS SERVER CHẾT**

⭐⭐ **Critical VLAN quan trọng nhất ngoài đời:** không có nó thì ⭐ **ISE bảo trì 10 phút = cả công ty
mất mạng**, và ⭐ **bạn cũng không SSH vào switch được để sửa** (nếu switch cũng dùng ISE cho AAA).
</details>

**15.** Hai dòng cấu hình hay quên nhất khiến 802.1X "không chạy mà không báo lỗi"?
<details><summary>Đáp án</summary>

⭐⭐ **(1) `dot1x system-auth-control`** *(toàn cục)* — thiếu nó thì ⭐ **cấu hình trên port hoàn toàn vô nghĩa**,
và ⭐ **không có thông báo lỗi nào.** ⭐ Kiểm tra: `show dot1x | include Sysauthcontrol`.

⭐⭐ **(2) `aaa authorization network default group <G>`** — thiếu nó thì ⭐ **xác thực THÀNH CÔNG
nhưng VLAN động / dACL / SGT KHÔNG được áp** → client vào nhầm VLAN.
⭐ **Trên WLC, lỗi tương đương là quên `aaa-override` trong Policy Profile.**
</details>

**16.** Ba giai đoạn triển khai 802.1X theo thứ tự? Vì sao không bật thẳng Closed Mode?
<details><summary>Đáp án</summary>

⭐⭐ **(1) Monitor Mode** (`authentication open`) — ⭐ **xác thực chạy và GHI LOG nhưng KHÔNG chặn ai**
→ ⭐ **(2) Low-Impact Mode** (open + pre-auth ACL) → ⭐ **(3) Closed Mode** (bỏ `authentication open`).

🔴 ⭐⭐ **Vì sao không bật thẳng Closed:** bạn sẽ phát hiện ra ⭐ **hàng chục máy in, camera, máy chấm công,
máy quét mã vạch mà không ai biết là chúng tồn tại** — ⭐ **và tất cả rớt mạng cùng lúc.**
⭐ **Monitor Mode vài tuần trước để lập danh sách đã.**
</details>

**17.** PEAP và EAP-TLS: bên nào cần chứng thư? Rủi ro an ninh của PEAP nếu cấu hình client sai?
<details><summary>Đáp án</summary>

⭐⭐ **PEAP: CHỈ SERVER cần chứng thư** (client dùng username/password bên trong tunnel TLS).
⭐⭐ **EAP-TLS: CẢ HAI đều cần chứng thư** → an toàn nhất nhưng cần hạ tầng **PKI**.

🔴 ⭐⭐ **Rủi ro PEAP:** nếu client ⭐ **không bật "validate server certificate"** →
⭐ kẻ tấn công dựng **AP giả + RADIUS giả** → ⭐ **thu được hash mật khẩu MSCHAPv2 của nhân viên.**
⭐ **Phải đẩy cấu hình bằng GPO/MDM và ghim chứng thư CA.**
</details>

**18.** WPA3-Personal dùng gì thay PSK? Tại sao bật WPA3 có thể làm máy cũ rớt mạng?
<details><summary>Đáp án</summary>

⭐⭐ **WPA3-Personal dùng SAE** (*Simultaneous Authentication of Equals*, còn gọi Dragonfly) —
⭐ **chống được tấn công dò mật khẩu OFFLINE**: bắt được handshake cũng không brute-force ngoại tuyến được.

🔴 ⭐⭐ **WPA3 BẮT BUỘC PMF (802.11w)** → ⭐ **client cũ không hỗ trợ 802.11w sẽ KHÔNG join được.**
⭐ **Cách xử lý: transition mode WPA2+WPA3 với `pmf optional`.**
</details>

**19.** Ba pha của TrustSec? Enforcement xảy ra ở ingress hay egress, và vì sao? SXP để làm gì?
<details><summary>Đáp án</summary>

⭐⭐ **(1) Classification** — gán SGT (⭐ **ISE gán** khi 802.1X/MAB/WebAuth, hoặc gán tĩnh IP/VLAN/port-to-SGT)
⭐⭐ **(2) Propagation** — mang SGT đi: ⭐ **inline tagging** (trường Cisco Metadata trong frame L2) ·
⭐ **SXP (TCP 64999)** · ⭐ **VXLAN** (SD-Access)
⭐⭐ **(3) Enforcement** — ⭐ **SGACL** trên switch/router, hoặc SG-Firewall

⭐⭐ **Enforcement ở EGRESS** — ⭐ **vì chỉ thiết bị lối ra mới biết SGT của ĐÍCH.**

⭐ **SXP tồn tại vì nhiều thiết bị KHÔNG inline-tag được** → nó "kể" ánh xạ **IP↔SGT** qua TCP 64999.
</details>

**20.** MACsec vs IPsec: tầng nào, phạm vi nào, quản lý khóa bằng gì?
<details><summary>Đáp án</summary>

| | ⭐⭐ **MACsec** | ⭐⭐ **IPsec** |
|---|---|---|
| Tầng | ⭐ **Layer 2** (802.1AE) | ⭐ **Layer 3** |
| Phạm vi | ⭐⭐ **HOP-BY-HOP** (từng liên kết) | ⭐⭐ **END-TO-END** |
| Mã hóa | ⭐ **Cả frame Ethernet** | Gói IP |
| Quản lý khóa | ⭐⭐ **MKA** | ⭐⭐ **IKEv1/IKEv2** |
| Tốc độ | ⭐ **Line-rate, phần cứng** | Phụ thuộc CPU/crypto engine |

🔴 ⭐ **Bẫy: "MACsec mã hóa end-to-end" → SAI.** ⭐ **Switch trung gian giải mã, xử lý, mã hóa lại.**
⭐ **Chọn:** đường trục trong nhà mình → **MACsec** · qua Internet → **IPsec**.
</details>

**21.** IDS vs IPS: vị trí, khả năng, rủi ro?
<details><summary>Đáp án</summary>

⭐ **IDS** — ⭐⭐ **out-of-band** (nhận bản sao qua SPAN/TAP) → ⭐ **chỉ phát hiện + cảnh báo**.
🔴 Gói xấu **đã tới đích rồi** mới báo. ⭐ Không thêm độ trễ.

⭐⭐ **IPS** — ⭐⭐ **inline** (gói đi xuyên qua) → ⭐ **phát hiện + CHẶN NGAY**.
🔴 ⭐ **Rủi ro: false positive = chặn nhầm traffic hợp lệ** · ⭐ **thiết bị chết = đứt mạng** (cần fail-open).

⭐ **Nhớ: IDS = camera an ninh · IPS = cửa xoay có bảo vệ.**
</details>

**22.** NGFW khác firewall stateful truyền thống ở những điểm nào?
<details><summary>Đáp án</summary>

⭐ **Firewall truyền thống:** chỉ lọc theo ⭐ **5-tuple** (IP nguồn/đích, port, protocol) → ⭐ nó chỉ thấy "TCP 443".

⭐⭐ **NGFW thêm:**
1. ⭐⭐ **Nhận diện ỨNG DỤNG** — phân biệt "Facebook" với "Salesforce" **dù cùng TCP 443**
2. ⭐⭐ **Nhận diện NGƯỜI DÙNG** — chính sách theo user, không theo IP
3. ⭐⭐ **IPS tích hợp**
4. ⭐ **URL filtering + AMP (chống malware)**
5. ⭐ **Giải mã TLS**
6. ⭐ **Threat intelligence** (Talos) cập nhật liên tục

⭐ **Cisco: Secure Firewall / Firepower (FTD)**, quản lý bằng **FMC**.
</details>

**23.** HTTP 401 vs 403 khác nhau thế nào? Gặp 403 thì xin token mới có giúp gì không?
<details><summary>Đáp án</summary>

⭐⭐ **401 Unauthorized = CHƯA XÁC THỰC** (hoặc token sai/hết hạn) → ⭐ *"Tôi không biết anh là ai"*
→ ⭐ **xin token mới SẼ giúp.**

⭐⭐ **403 Forbidden = ĐÃ xác thực nhưng KHÔNG ĐỦ QUYỀN** → ⭐ *"Tôi biết anh là ai, nhưng anh không được phép"*
→ 🔴 ⭐⭐ **Xin token mới VÔ ÍCH.** ⭐ **Phải sửa RBAC / quyền của tài khoản.**

⭐ *(Thêm: **429** = vượt rate limit → chờ theo `Retry-After`.)*
</details>

**24.** Basic Auth có an toàn không? Luồng lấy token của DNA Center?
<details><summary>Đáp án</summary>

🔴 ⭐⭐ **Basic Auth = `user:pass` mã hóa Base64 — Base64 KHÔNG PHẢI mã hóa**, giải ngược tức thì.
⭐ **Chỉ an toàn khi đi kèm HTTPS/TLS.**

⭐ **Luồng DNA Center:**
1. ⭐ `POST /dna/system/api/v1/auth/token` với header `Authorization: Basic <base64(user:pass)>`
2. ⭐ Trả về `{"Token": "eyJ..."}`
3. ⭐ Mọi lời gọi sau: header ⭐ **`X-Auth-Token: eyJ...`**
4. ⭐ Token hết hạn (~1 giờ) → xin lại

⭐ *(vManage khác: `POST /j_security_check` → cookie **JSESSIONID** + **X-XSRF-TOKEN** cho lệnh ghi.)*
</details>

**25.** Vì sao phải bật DHCP Snooping trước DAI? Thiết bị IP tĩnh thì sao?
<details><summary>Đáp án</summary>

⭐⭐ **DHCP Snooping xây bảng binding (MAC ↔ IP ↔ port ↔ VLAN)** khi quan sát quá trình DHCP.
⭐⭐ **DAI (và IP Source Guard) DÙNG chính bảng đó** để kiểm tra ARP có hợp lệ không.

🔴 ⭐⭐ **Bật DAI mà chưa có DHCP Snooping = không có bảng binding = chặn SẠCH ARP = sập VLAN.**

⭐ **Thiết bị đặt IP tĩnh** (server, máy in) ⭐ **không bao giờ xuất hiện trong bảng binding** →
⭐ **phải khai thủ công bằng `ip source binding <mac> vlan <n> <ip> interface <intf>`**, nếu không DAI sẽ chặn chúng.
</details>

---

## 📚 19. THUẬT NGỮ ANH–VIỆT

| English | Tiếng Việt / Giải thích |
|---|---|
| ⭐ **Line: console / VTY / AUX** | Cổng vật lý / ⭐ **truy nhập từ xa (rủi ro nhất)** / cổng phụ (⭐ **phải tắt**) |
| ⭐ **Password type 0/5/7/8/9** | Plaintext / MD5 / ⭐ **Vigenère — GIẢI NGƯỢC ĐƯỢC** / PBKDF2 / ⭐ **scrypt (tốt nhất)** |
| ⭐ **`service password-encryption`** | ⭐ Chỉ tạo **type 7** — che mắt, **không phải bảo mật** |
| ⭐ **Privilege level 0/1/15** | 5 lệnh / user EXEC (`>`) / ⭐ **privileged EXEC (`#`)** |
| ⭐ **Parser view / superview** | Role-Based CLI Access — gói lệnh theo vai trò |
| ⭐ **`login block-for` / quiet-mode** | Chống brute-force / khoảng thời gian khóa đăng nhập |
| ⭐ **Banner** | ⭐ **Lời CẢNH BÁO pháp lý** — 🔴 không bao giờ viết "Welcome" |
| ⭐⭐ **AAA** | Authentication (⭐ **anh là ai**) · Authorization (⭐ **được làm gì**) · Accounting (⭐ **đã làm gì**) |
| ⭐⭐ **TACACS+** | ⭐ **TCP 49** · ⭐ **mã hóa TOÀN BỘ** · ⭐ **tách cả 3A** · ⭐ **có command authorization** → ⭐ **quản trị THIẾT BỊ** |
| ⭐⭐ **RADIUS** | ⭐ **UDP 1812/1813** · 🔴 **chỉ mã hóa PASSWORD** · **gộp authn+authz** → ⭐ **cho vào MẠNG** |
| ⭐⭐ **Method list** | Danh sách phương pháp thử **lần lượt** — ⭐ **chỉ chuyển khi phương pháp trước KHÔNG TRẢ LỜI** |
| ⭐⭐ **Fallback `local`** | ⭐ Dùng `username` trong config khi server **im lặng** — ⭐ **bắt buộc phải có** |
| ⭐ **`reject` vs `timeout`** | ⭐ **Server trả lời "sai" (KHÔNG fallback)** vs ⭐ **server im lặng (CÓ fallback)** |
| ⭐ **`test aaa`** | ⭐ Kiểm tra AAA **trước khi logout** — lệnh cứu mạng |
| ⭐ **Standard / Extended ACL** | Chỉ khớp source (⭐ **đặt gần ĐÍCH**) / khớp cả hai (⭐ **đặt gần NGUỒN**) |
| ⭐ **Implicit deny** | ⭐ `deny ip any any` ngầm — ⭐ **KHÔNG đếm, KHÔNG log** |
| ⭐ **Sequence number** | Số dòng trong named ACL — ⭐ cho phép **chèn/xóa từng dòng** |
| ⭐ **`established`** | Khớp gói TCP có **ACK/RST** — ⭐ "giả stateful", chỉ nhìn cờ |
| ⭐ **Reflexive ACL** | Tạo entry tạm cho từng phiên — stateful "nhà nghèo" |
| ⭐ **Time-range** | ACL theo giờ — ⭐ **phụ thuộc NTP** |
| ⭐ **Object group** | Gom mạng/dịch vụ để ACL ngắn và dễ đọc |
| ⭐⭐ **NDP / nd-na / nd-ns** | ⭐ **"ARP của IPv6"** — ⭐ **viết `deny ipv6 any any` tường minh sẽ GIẾT nó** |
| ⭐ **`ipv6 traffic-filter`** | Lệnh áp IPv6 ACL lên interface *(không phải `ip access-group`)* |
| ⭐⭐ **PACL / VACL / RACL** | Port ACL / ⭐ **VLAN map (lọc được traffic TRONG cùng VLAN)** / Router ACL.<br>⭐ **Ingress: PACL → VACL → RACL** |
| ⭐ **uRPF strict / loose** | Có route **và đúng interface** / ⭐ **chỉ cần có route** (cho mạng bất đối xứng) |
| ⭐ **iACL** (Infrastructure ACL) | Chặn traffic Internet đi **TỚI** dải địa chỉ hạ tầng |
| ⭐⭐ **CoPP** | ⭐ **QoS policy bảo vệ CONTROL PLANE (CPU)** khỏi bị làm ngập |
| ⭐ **CPPr** | Bản mịn hơn — 3 sub-interface: ⭐ **`host` · `transit` · `cef-exception`** *(ARP, TTL-exceeded ở đây)* |
| ⭐ **Punt** | Gói bị **đẩy từ ASIC lên CPU** để xử lý |
| ⭐⭐ **Supplicant / Authenticator / Auth Server** | Client / ⭐ **switch-WLC (chỉ đưa thư)** / ⭐ **ISE-RADIUS (RA QUYẾT ĐỊNH)** |
| ⭐⭐ **EAPoL** | EAP over LAN — ⭐ **chạy ở LAYER 2, client CHƯA CÓ IP** |
| ⭐⭐ **MAB** | MAC Authentication Bypass — cho thiết bị **không có supplicant**. 🔴 **MAC giả mạo được** |
| ⭐ **WebAuth (LWA / CWA)** | Captive portal trên **WLC** / trên **ISE** |
| ⭐ **`dot1x system-auth-control`** | ⭐⭐ **Dòng BẬT 802.1X toàn cục — thiếu là không chạy và KHÔNG BÁO LỖI** |
| ⭐ **`port-control auto`** | ⭐ Bật 802.1X thật *(mặc định là `force-authorized` = luôn mở)* |
| ⭐⭐ **Host mode** | `single-host` · 🔴 **`multi-host` (kém an toàn)** · ⭐ **`multi-domain` (phone+PC)** · `multi-auth` |
| ⭐ **Guest / Auth-fail / Critical VLAN** | Không trả lời EAPoL / trả lời nhưng trượt / ⭐⭐ **RADIUS CHẾT** |
| ⭐⭐ **Monitor → Low-Impact → Closed Mode** | ⭐ **Ba giai đoạn triển khai 802.1X — KHÔNG bật thẳng Closed** |
| ⭐ **dACL** | Downloadable ACL — ACL do RADIUS đẩy xuống theo từng phiên |
| ⭐ **`aaa-override`** | ⭐⭐ Trên WLC: **cho phép ISE ghi đè VLAN/ACL** — hay quên |
| ⭐⭐ **WPA2 / WPA3 / SAE / OWE** | AES-CCMP / ⭐ **bắt buộc PMF** / ⭐ **thay PSK ở WPA3** / mở nhưng **có mã hóa** |
| ⭐ **PMF / 802.11w** | Bảo vệ frame quản lý — chống **deauth attack** |
| ⭐⭐ **EAP-TLS / PEAP** | ⭐ **Chứng thư CẢ HAI bên** / ⭐ **CHỈ server cần chứng thư** |
| ⭐⭐ **TrustSec / SGT** | Chính sách theo **danh tính**, không theo IP · **Scalable Group Tag** |
| ⭐ **3 pha TrustSec** | ⭐ **Classification (ISE gán)** → ⭐ **Propagation (inline tag / SXP / VXLAN)** → ⭐ **Enforcement (EGRESS)** |
| ⭐ **SXP** | SGT Exchange Protocol — ⭐ **TCP 64999**, cho thiết bị không inline-tag được |
| ⭐ **SGACL** | Ma trận "SGT nguồn × SGT đích → permit/deny" |
| ⭐⭐ **MACsec (802.1AE)** | ⭐ **L2, HOP-BY-HOP, mã hóa cả frame, line-rate phần cứng** |
| ⭐ **MKA** | MACsec Key Agreement — ⭐ quản lý khóa cho MACsec *(IPsec dùng IKE)* |
| ⭐⭐ **NGFW** | Stateful + ⭐ **nhận diện ỨNG DỤNG + NGƯỜI DÙNG** + IPS tích hợp + threat intel |
| ⭐⭐ **IDS / IPS** | ⭐ **Out-of-band, chỉ cảnh báo** / ⭐ **inline, CHẶN được** |
| ⭐ **Talos / FTD / FMC** | Đội tình báo mối đe dọa Cisco / NGFW+IPS / bộ quản lý tập trung |
| ⭐ **Umbrella** | ⭐ **An ninh tầng DNS** — chặn tên miền độc hại **trước khi** kết nối được tạo |
| ⭐ **Secure Network Analytics (Stealthwatch) / ETA** | Phân tích NetFlow · ⭐ **phát hiện malware trong traffic MÃ HÓA mà không giải mã** |
| ⭐ **Posture assessment** | ⭐ **ISE kiểm tra sức khỏe máy** (vá lỗi, AV) **trước khi** cho vào mạng |
| ⭐ **Zero Trust** | ⭐ **"Không tin ai theo mặc định."** 3 trụ cột Cisco: **Workforce · Workload · Workplace** |
| ⭐ **Defense in Depth / Least privilege / Microsegmentation** | Nhiều lớp / quyền tối thiểu / ⭐ **chính là SGT** |
| ⭐⭐ **401 / 403 / 429** | ⭐ **Chưa xác thực (xin token)** / ⭐ **đã xác thực nhưng KHÔNG có quyền (sửa RBAC)** / vượt rate limit |
| ⭐ **Basic Auth / Bearer token / OAuth 2.0 / mTLS** | ⭐ **Base64 — KHÔNG phải mã hóa** / token có hạn / ủy quyền bên thứ ba / chứng thư hai chiều |
| ⭐ **`X-Auth-Token` / `JSESSIONID`** | ⭐ **DNA Center** / ⭐ **vManage** |
| ⭐ **DHCP Snooping / DAI / IP Source Guard** | ⭐ **Xây bảng binding** / dùng bảng đó chống **ARP spoofing** / chống giả IP |

---

## 🎯 20. ĐÚC KẾT MODULE-10

**3 điều rút ra:**

1. 🔴 ⭐⭐ **Hai bảng của Domain 5.0 phải thuộc như bảng cửu chương — và cả hai đều xoay quanh AAA:**
   ⭐⭐ **TACACS+ = TCP 49, mã hóa TOÀN BỘ, tách cả 3A, có command authorization → quản trị THIẾT BỊ.**
   ⭐⭐ **RADIUS = UDP 1812/1813, chỉ mã hóa PASSWORD, gộp authn+authz → cho người dùng vào MẠNG.**
   Và ⭐⭐ **cơ chế fallback:** ⭐ **method list chỉ chuyển sang phương pháp sau khi phương pháp trước
   KHÔNG TRẢ LỜI** — ⭐ **`reject` (server trả lời "sai") KHÔNG fallback**, ⭐ **`timeout` (server im lặng) MỚI fallback.**
   🔴 ⭐ Từ đó ra **bốn quy tắc sống còn**: ⭐ **tạo user local TRƯỚC `aaa new-model` · luôn có `local`
   cuối method list · giữ phiên SSH thứ hai · `test aaa` trước khi logout.**

2. 🔴 ⭐⭐ **Ba tính năng "configure" đều có chung một bài học: ĐO TRƯỚC, SIẾT SAU.**
   ⭐ **CoPP** bảo vệ ⭐ **CONTROL PLANE (CPU)**, không phải data plane — 🔴 ⭐ **siết quá tay là tự đánh
   sập OSPF/SSH của mình**, nên ⭐ **bắt đầu bằng `exceed-action transmit` để đếm.**
   ⭐ **802.1X** phải đi ⭐ **Monitor → Low-Impact → Closed**, và ⭐⭐ **Critical VLAN là thứ cứu cả công ty
   khi ISE chết.** ⭐ **ACL** thì ⭐ **luôn viết `deny ... log` tường minh** (deny ngầm **không đếm, không log**),
   ⭐ **luôn dùng named ACL + sequence**, và 🔴 ⭐⭐ **nhớ bẫy IPv6: viết `deny ipv6 any any` tường minh
   sẽ GIẾT NDP** → phải tự thêm `permit icmp any any nd-na/nd-ns` lên trước.

3. ⭐⭐ **Phần "describe" tuy nhẹ nhưng có bốn cặp phân biệt chắc chắn bị hỏi:**
   ⭐ **802.1X: switch là AUTHENTICATOR (chỉ đưa thư), SERVER mới RA QUYẾT ĐỊNH** · EAPoL ở **Layer 2**,
   client **chưa có IP** · ⭐ **TrustSec 3 pha, enforcement ở EGRESS** (vì chỉ ở đó mới biết SGT của đích),
   ⭐ **SGT do ISE gán chứ không phải switch** · ⭐⭐ **MACsec = L2 HOP-BY-HOP dùng MKA vs
   IPsec = L3 END-TO-END dùng IKE** · ⭐⭐ **401 = chưa xác thực (xin token mới) vs 403 = đã xác thực
   nhưng KHÔNG có quyền (xin token vô ích).** ⭐ Cộng thêm: ⭐ **IDS out-of-band chỉ cảnh báo, IPS inline
   mới chặn được**, và ⭐ **NGFW = stateful + nhận diện ỨNG DỤNG + NGƯỜI DÙNG + IPS tích hợp.**

🧠 **Một câu để nhớ:** *⭐ **AAA là thẻ nhân viên** — ⭐ **TACACS+ soi từng cánh cửa (từng lệnh),
RADIUS chỉ hỏi có vé không**; và ⭐ **"nhân sự nói KHÔNG" khác hẳn "nhân sự không bắt máy"** —
⭐ **chỉ cái sau mới cho phép giở sổ dự phòng (`local`)**. ⭐ **CoPP là thư ký gác cửa phòng bộ não** —
⭐ **để thư ký quá nghiêm thì chính bạn cũng không gặp được sếp**. ⭐ **802.1X là anh bảo vệ giữ cửa,
nhưng giám đốc mới quyết** — ⭐ **và phải có quy định sẵn cho lúc giám đốc đi vắng (Critical VLAN)**.
Còn ⭐ **TrustSec là dán nhãn lên NGƯỜI thay vì đánh số GHẾ** — ⭐ **người đó ngồi đâu cũng không quan trọng.***

---

### ✅ TỰ CHẤM

**Phần A — Trả lời được bằng lời của mình:**

| # | Câu | ✅ |
|:---:|---|:---:|
| 1 | ⭐ Ba loại line (console/VTY/AUX) · ⭐ **vì sao phải tắt AUX** | ☐ |
| 2 | ⭐⭐ **Password type 0/5/7/8/9** — cái nào giải ngược được, cái nào nên dùng | ☐ |
| 3 | 🔴 ⭐⭐ **`service password-encryption` thực sự làm gì** | ☐ |
| 4 | ⭐ `enable secret` vs `enable password` — cái nào thắng | ☐ |
| 5 | ⭐ **Privilege level 0 / 1 / 15** · parser view là gì | ☐ |
| 6 | ⭐⭐ **Bốn thứ cần để SSH hoạt động** · vì sao ép version 2 | ☐ |
| 7 | ⭐ `login block-for` · `quiet-mode access-class` · `exec-timeout` · `access-class` | ☐ |
| 8 | ⭐ Vì sao banner phải là **CẢNH BÁO**, không phải "Welcome" | ☐ |
| 9 | ⭐ **Ba chữ A** — mỗi chữ trả lời câu hỏi gì | ☐ |
| 10 | 🔴 ⭐⭐ **TACACS+ vs RADIUS**: port, mã hóa, tách 3A, command authz, dùng cho gì | ☐ |
| 11 | ⭐⭐ **Method list hoạt động thế nào** — thử lần lượt theo quy tắc nào | ☐ |
| 12 | 🔴 ⭐⭐ **`reject` vs `timeout`** — cái nào cho fallback, vì sao | ☐ |
| 13 | ⭐ Vì sao **sai shared key trông giống hệt "server chết"** | ☐ |
| 14 | 🔴 ⭐⭐ **Bốn quy tắc để không tự khóa mình khi triển khai AAA** | ☐ |
| 15 | ⭐ `test aaa` dùng để làm gì, gõ khi nào | ☐ |
| 16 | ⭐⭐ **Standard đặt gần đâu, Extended đặt gần đâu, VÌ SAO** | ☐ |
| 17 | ⭐⭐ Vì sao **luôn viết `deny ip any any log` tường minh** | ☐ |
| 18 | ⭐ Vì sao **luôn dùng named ACL** thay numbered | ☐ |
| 19 | ⭐ `established` làm gì · điểm yếu của nó | ☐ |
| 20 | ⭐ Time-based ACL phụ thuộc vào gì · reflexive ACL · object group | ☐ |
| 21 | 🔴 ⭐⭐ **BA dòng ngầm cuối IPv6 ACL** · ⭐ **vì sao `deny ipv6 any any` tường minh giết NDP** | ☐ |
| 22 | ⭐ IPv6 ACL khác IPv4 ở 3 điểm nào (tên, wildcard, lệnh áp) | ☐ |
| 23 | ⭐⭐ **PACL / VACL / RACL** — thứ tự ingress · ⭐ **cái nào lọc được trong cùng VLAN** | ☐ |
| 24 | 🔴 ⭐ **VACL kết thúc bằng gì** — hệ quả nếu quên `action forward` | ☐ |
| 25 | ⭐ **uRPF strict vs loose** — khi nào dùng cái nào | ☐ |
| 26 | ⭐⭐ **CoPP bảo vệ cái gì** · ⭐ **vì sao data plane vẫn khỏe mà mạng vẫn sập** | ☐ |
| 27 | 🔴 ⭐⭐ **Vì sao phải bắt đầu CoPP với `exceed-action transmit`** | ☐ |
| 28 | ⭐ **Ba sub-interface CPPr** · ⭐ **ARP và TTL-exceeded ở cái nào** | ☐ |
| 29 | ⭐⭐ **Ba vai 802.1X** · ⭐ **ai ra quyết định** · ⭐ **EAPoL ở tầng nào** | ☐ |
| 30 | ⭐ **MAB** dùng cho gì · điểm yếu · **WebAuth** dùng cho ai | ☐ |
| 31 | ⭐ **Thứ tự mặc định 802.1X → MAB → WebAuth** — vì sao đúng thứ tự đó | ☐ |
| 32 | ⭐⭐ **Bốn host mode** — cái nào cho phone+PC, cái nào kém an toàn nhất | ☐ |
| 33 | ⭐ Ba giá trị `port-control` · ⭐ **cái nào là mặc định** | ☐ |
| 34 | 🔴 ⭐⭐ **Hai dòng hay quên khiến 802.1X "không chạy mà không báo lỗi"** | ☐ |
| 35 | ⭐⭐ **Guest / Auth-fail / Critical VLAN** — kích hoạt khi nào, cái nào quan trọng nhất | ☐ |
| 36 | ⭐⭐ **Ba giai đoạn triển khai 802.1X** · ⭐ **vì sao không bật thẳng Closed Mode** | ☐ |
| 37 | ⭐ **WPA2 / WPA3 / SAE / OWE** · ⭐ **vì sao bật WPA3 làm máy cũ rớt** | ☐ |
| 38 | 🔴 ⭐⭐ **PEAP vs EAP-TLS** — bên nào cần chứng thư · ⭐ **rủi ro nếu client không validate server cert** | ☐ |
| 39 | ⭐ **LWA vs CWA** · 🔴 ⭐ **vì sao pre-auth ACL PHẢI mở DNS** | ☐ |
| 40 | ⭐ **`aaa-override`** trên WLC làm gì — hệ quả nếu quên | ☐ |
| 41 | ⭐⭐ **Ba pha TrustSec** · ⭐ **enforcement ở ingress hay egress, VÌ SAO** | ☐ |
| 42 | ⭐ **SGT do ai gán** · **SXP** để làm gì, port nào | ☐ |
| 43 | 🔴 ⭐⭐ **MACsec vs IPsec** — tầng, phạm vi, quản lý khóa | ☐ |
| 44 | ⭐ Hai kiểu MACsec (downlink/uplink) — quản lý khóa khác nhau ra sao | ☐ |
| 45 | ⭐⭐ **NGFW khác firewall stateful ở những điểm nào** | ☐ |
| 46 | ⭐⭐ **IDS vs IPS** — vị trí, khả năng, rủi ro | ☐ |
| 47 | ⭐ Signature-based vs anomaly-based detection | ☐ |
| 48 | ⭐ Kể được vai trò của: **Talos · FTD/FMC · Umbrella · Stealthwatch · ISE · Duo** | ☐ |
| 49 | ⭐ **Posture assessment** làm gì · ⭐ **Zero Trust 3 trụ cột Cisco** | ☐ |
| 50 | 🔴 ⭐⭐ **401 vs 403** — cái nào xin token mới thì được, cái nào vô ích | ☐ |
| 51 | ⭐ **Basic Auth có an toàn không** · ⭐ **luồng token của DNAC và vManage** | ☐ |
| 52 | 🔴 ⭐ **Vì sao DHCP Snooping phải bật TRƯỚC DAI** · IP tĩnh thì làm sao | ☐ |

**Phần B — Lab:**

| # | Yêu cầu | ✅ |
|:---:|---|:---:|
| 1 | ⭐ **LAB A1**: thấy `enable password` **hiện nguyên văn**, rồi thành **type 7** | ☐ |
| 2 | 🔴 ⭐⭐ **Chép chuỗi type 7 và GIẢI NGƯỢC được nó bằng công cụ online** | ⭐⭐ ☐ |
| 3 | ⭐ **LAB A2**: chuyển sang **type 9 (scrypt)** — xác nhận số `9` sau `secret` | ⭐ ☐ |
| 4 | ⭐ **LAB A3**: SSH v2 chạy được, **telnet bị từ chối**, banner hiện ra | ☐ |
| 5 | ⭐ **LAB A4**: sai mật khẩu 3 lần → `show login` hiện **Quiet-Mode** | ⭐ ☐ |
| 6 | ⭐⭐ **LAB B2–B3**: bật AAA trỏ server chết → ⭐ **`show aaa servers` báo DEAD** | ⭐⭐ ☐ |
| 7 | 🔴 ⭐⭐ **LAB B3: SSH vào được nhờ FALLBACK sang `local`** | ⭐⭐ ☐ |
| 8 | 🔴 ⭐⭐ **LAB B4: bỏ `local` → TỰ KHÓA MÌNH → sửa bằng phiên SSH thứ hai** | ⭐⭐ ☐ |
| 9 | ⭐ Đọc được `show aaa servers` và phân biệt **`timeouts` vs `reject`** | ⭐ ☐ |
| 10 | ⭐ **LAB C1**: chèn dòng **vào GIỮA** named ACL bằng sequence number | ☐ |
| 11 | ⭐ Thử với **numbered ACL** → thấy dòng mới **nhảy xuống cuối** → hiểu vì sao dùng named | ☐ |
| 12 | ⭐⭐ **LAB C2**: `clear counters` → tạo traffic → ⭐ **chỉ ra dòng ACL đang quyết định** | ⭐⭐ ☐ |
| 13 | ⭐ **LAB C3**: `deny ... log` tường minh → thấy **bộ đếm VÀ log** | ☐ |
| 14 | 🔴 ⭐⭐ **LAB C4: áp `deny ipv6 any any` → IPv6 CHẾT · `show ipv6 neighbors` trống** | ⭐⭐ ☐ |
| 15 | ⭐⭐ **Sửa bằng cách thêm `nd-na`/`nd-ns` lên trước → IPv6 sống lại** | ⭐⭐ ☐ |
| 16 | 🚀 **LAB C5**: `established` — SYN từ ngoài bị chặn, gói trả về được phép | 🚀 ☐ |
| 17 | ⭐ **LAB D1–D2**: CoPP ở chế độ đếm → thấy `exceeded` cao mà `actions: transmit` | ⭐ ☐ |
| 18 | 🔴 ⭐⭐ **LAB D3: đổi sang `exceed-action drop` → ping mất gói nghiêm trọng** | ⭐⭐ ☐ |
| 19 | ⭐ **LAB D4**: `show processes cpu` khi bị ping flood | ☐ |
| 20 | 🚀 ⭐⭐ **LAB E1**: cấu hình 802.1X → `show access-session` báo **`Unauthorized`** | 🚀 ⭐⭐ ☐ |
| 21 | 🚀 ⭐⭐ **LAB E2**: thêm **Critical VLAN** → trạng thái đổi sang **Authorized / Critical_Auth** | 🚀 ⭐⭐ ☐ |
| 22 | 🚀 🔴 ⭐⭐ **LAB E3**: `no dot1x system-auth-control` → ⭐ **session biến mất, KHÔNG có lỗi** | 🚀 ⭐⭐ ☐ |
| 23 | 🚀 ⭐ **LAB F**: uRPF drop gói source giả · `show ip interface` đếm verification drops | 🚀 ☐ |
| 24 | 🚀 🔴 ⭐ **LAB G**: bỏ `action forward` của VACL → **cả VLAN chết** | 🚀 ⭐ ☐ |
| 25 | 🚀 ⭐ **LAB H**: DHCP Snooping → xem **bảng binding** → rồi mới bật DAI | 🚀 ☐ |
| 26 | 🚀 ⭐ **LAB I**: trên DevNet C9800, vẽ lại chuỗi bảo mật của 1 WLAN thật | 🚀 ☐ |
| 27 | ⭐ Ghi ít nhất **3 mục** vào `SO-TAY-LOI.md` từ module này | ☐ |

> ⭐ **Nếu chỉ có thời gian làm một nửa:** ưu tiên ⭐⭐ **mục 6–9 (LAB B — AAA fallback, LAB quan trọng
> nhất module)**, ⭐⭐ **mục 12, 14–15 (bộ đếm ACL + bẫy IPv6)**, ⭐⭐ **mục 17–18 (CoPP đo trước siết sau)**,
> và ⭐⭐ **mục 20–22 (802.1X + Critical VLAN)**.
> ⭐ Bỏ LAB G/H/I nếu bám tiến độ — ⭐ **nhưng mục 2 (giải ngược type 7) chỉ mất 2 phút và nhớ cả đời.**
>
> ⚠️ ⭐ **Chưa tick được ≥ 45/52 Phần A thì đọc lại §3, §4, §5, §6** —
> ⭐ **bốn mục đó là toàn bộ phần "configure" của Domain 5.0.**
>
> 🎉 ⭐ **Hết Module-10 = xong Domain 5.0 Security (20%).**
> ⭐ **Cộng dồn: Infrastructure 30% + Architecture 15% + Virtualization 10% + Security 20% = 75% nội dung đề.**
> ⭐ **Đây là mốc Tuần 16 của ROADMAP.**

---

## 🔗 21. TÀI LIỆU CHO MODULE NÀY

| Nguồn | Cụ thể |
|---|---|
| **Sách OCG 350-401** | Chương *Secure Network Access Control*, *Network Device Access Control and Infrastructure Security* |
| **Cisco doc** ⭐⭐ | ***Cisco Guide to Harden Cisco IOS Devices*** — ⭐⭐ **tài liệu gốc cho §2 và §5.** Search: `cisco guide harden ios devices` |
| **Cisco doc** ⭐⭐ | *Authentication, Authorization, and Accounting Configuration Guide* — ⭐ method list, fallback |
| **Cisco doc** ⭐⭐ | ***TACACS+ and RADIUS Comparison*** — ⭐ **bảng so sánh chính thống của §3.2** |
| **Cisco doc** ⭐ | *Configuring Secure Shell (SSH)* · *Improving Security on Cisco Routers* |
| **Cisco doc** ⭐⭐ | ***Control Plane Policing (CoPP) Implementation Best Practices*** — ⭐⭐ **giải thích rõ vì sao phải đo trước siết sau** |
| **Cisco doc** ⭐ | *Control Plane Protection (CPPr)* — ⭐ 3 sub-interface |
| **Cisco doc** ⭐⭐ | *IPv6 Access Control Lists* — ⭐⭐ **phần implicit permit cho NDP (§4.4)** |
| **Cisco doc** ⭐ | *Configuring Network Security with ACLs* — ⭐ PACL/VACL/RACL và thứ tự xử lý |
| **Cisco doc** ⭐ | *Understanding Unicast Reverse Path Forwarding (uRPF)* |
| **Cisco doc** ⭐⭐ | ***IEEE 802.1X Authentication Configuration Guide*** — ⭐ host mode, guest/critical VLAN |
| **Cisco doc** ⭐⭐ | ***Wired 802.1X Deployment Guide*** — ⭐⭐ **Monitor → Low-Impact → Closed Mode (§6.6)** |
| **Cisco doc** ⭐ | *Identity-Based Networking Services (IBNS) 2.0 Configuration Guide* |
| **Cisco doc** ⭐⭐ | ***Cisco TrustSec Configuration Guide*** — ⭐ 3 pha, SXP, SGACL |
| **Cisco doc** ⭐ | *MACsec and MKA Configuration Guide* — ⭐ downlink vs uplink |
| **Cisco doc** ⭐ | *Catalyst 9800 Security Configuration Guide* — ⭐ WPA3/SAE, EAP, WebAuth (§7) |
| **Cisco doc** ⭐ | *DHCP Snooping / Dynamic ARP Inspection Configuration* (§11) |
| **Cisco DevNet** ⭐⭐ | ⭐ `developer.cisco.com/docs/dna-center/` — ⭐ **luồng lấy token `X-Auth-Token` (§10.2)**<br>⭐ `developer.cisco.com/docs/sdwan/` — luồng `j_security_check` của vManage |
| **RFC 2865 / 2866** | RADIUS Authentication / Accounting |
| **RFC 8907** | TACACS+ |
| **RFC 3748 / 5216** | EAP / EAP-TLS |
| **IEEE 802.1X-2010 / 802.1AE** | Port-Based NAC / ⭐ **MACsec** |
| **OWASP** ⭐ | ⭐ **OWASP API Security Top 10** — ⭐ nền tảng cho §10, đọc rất đáng |
| **Video** ⭐ | CBT Nuggets ENCOR — module Security · **Keith Barker**: search `Keith Barker AAA TACACS`, `Keith Barker CoPP`, `Keith Barker 802.1X` |
| **Cisco Live** ⭐⭐ | ⭐ search `ciscolive.com/on-demand`: `BRKSEC-2690 ISE deployment`, `BRKSEC-3690 TrustSec`, `BRKCRS-2501 802.1X deployment`, `Control plane policing` |
| **NetworkLessons** ⭐ | *AAA*, *TACACS+ vs RADIUS*, *CoPP*, *802.1X*, *IPv6 ACL*, *DHCP Snooping*, *DAI* — nhiều bài free |
| **Công cụ** ⭐ | ⭐ **FreeRADIUS** (Linux) hoặc **Windows NPS** — nếu muốn lab 802.1X đầy đủ · **Wireshark** filter `eapol`, `radius`, `tacplus` |
| **Forum** | https://community.cisco.com — search: `aaa new-model locked out`, `tacacs fallback local not working`, `ipv6 acl breaks ndp`, `copp dropping ospf`, `dot1x system-auth-control`, `critical vlan radius dead`, `vacl action forward` |

---

**➡️ Tiếp theo:** Module-11 — Network Assurance
*(Syslog · SNMPv2c/v3 · NetFlow & Flexible NetFlow · SPAN/RSPAN/ERSPAN · IP SLA · DNA Center Assurance · debug an toàn — **Tuần 17**)*

> ⭐ **Module-11 là khối nhẹ nhất còn lại (10% đề) và rất dễ ăn điểm** — ⭐ chủ yếu là
> **cấu hình được + ĐỌC ĐƯỢC OUTPUT**.
>
> ⭐ **Và bạn đã có sẵn ba mối nối:** ⭐ **IP SLA + object tracking** đã học ở
> [Module-03](Module-03-IP-Routing-Nen-tang.md) và [Module-06A](Module-06A-FHRP-HSRP-VRRP-GLBP.md) ·
> ⭐ **NTP** ở [Module-06B](Module-06B-NAT-NTP-Multicast.md) là **nền của mọi log** ·
> ⭐ **DNA Center Assurance** là workflow thứ tư bạn đã gặp ở [Module-09 §7.8](Module-09-Architecture-va-QoS.md).
