# LAB 11 — Tuần 17: Syslog · SNMP · NetFlow · SPAN · IP SLA

> 📘 **Lý thuyết:** [Module-11](Module-11-Network-Assurance.md) —
> đọc **Phần 1** và **Phần 2 mục §3 (thời gian), §4 (syslog), §6 (NetFlow), §8 (IP SLA)** trước khi làm.
>
> ⏱️ **Thời gian:** ~4 giờ · 💾 **RAM:** 1.8 GB · 🧰 **Cần:** EVE-NG + 2× vIOS + 1× vIOS-L2

---

## ⭐ Gần như không cần server ngoài

Điểm mạnh của Module-11: **mọi công cụ giám sát đều có bộ đệm ngay trên thiết bị**.

| Nội dung | Cần server? | Cách lab |
|---|:---:|---|
| ⭐⭐ **Syslog** | ❌ | `logging buffered` → `show logging` |
| SNMP | ⚠️ | Cấu hình + `show snmp user/group/host` |
| ⭐⭐ **Flexible NetFlow** | ❌ | ⭐⭐ **`show flow monitor <FM> cache` — xem TOÀN BỘ flow ngay trên router** |
| ⭐⭐ **SPAN** | ❌ | Cấu hình + tái hiện bẫy "cổng câm" |
| ⭐⭐ **IP SLA** | ❌ | Lab đầy đủ, kể cả `udp-jitter` với Responder |
| ⭐⭐ **Debug an toàn** | ❌ | Lab đầy đủ |

---

## ⚠️ Đọc trước khi bắt đầu

| Điều cần biết | Chi tiết |
|---|---|
| 🔴 ⭐⭐ **Đặt giờ TRƯỚC mọi thứ** | Lab không có NTP thì `clock set` **cả hai router**. Sai giờ là mọi số liệu thành rác |
| 🔴 ⭐⭐ **Trước khi debug: `no logging console`** | Console **đồng bộ và chậm** — đây mới là thứ làm treo router, không phải lệnh debug |
| ⭐⭐ **Học thuộc `u all`** | Lệnh cứu hộ. Biết nó **trước khi** bật bất kỳ debug nào |
| 🔴 **Bẫy "cổng câm" ở LAB D** | Cổng SPAN destination làm thiết bị cắm vào **mất mạng dù vẫn `up/up`** |
| **Lỗi > 15 phút** | Ghi vào [`SO-TAY-LOI.md`](SO-TAY-LOI.md) |

---

## 🧪 13. LAB 11

### 13.1 Topology — dùng lại đúng Module-10

```
        ┌──────────┐              ┌──────────┐              ┌──────────┐
        │    R1    │──Gi0/0───────│   SW1    │───────Gi0/1──│    R2    │
        │ 10.0.0.1 │              │ vIOS-L2  │              │ 10.0.0.2 │
        │ Lo0 1.1.1.1             │  VLAN 10 │              │ Lo0 2.2.2.2
        └──────────┘              └──────────┘              └──────────┘
```

| LAB | Nội dung | Cần server? | Thời gian | Bắt buộc? |
|---|---|:---:|:---:|:---:|
| **A** | Syslog — severity & lọc | ❌ | 30 phút | ⭐⭐ |
| **B** | SNMPv2c + v3 | ⚠️ | 20 phút | ⭐ |
| **C** | ⭐ **Flexible NetFlow** | ❌ | 40 phút | ⭐⭐ |
| **D** | SPAN + bẫy "cổng câm" | ❌ | 25 phút | ⭐⭐ |
| **E** | IP SLA + track + udp-jitter | ❌ | 40 phút | ⭐⭐ |

⭐ **Cấu hình nền — làm trước (§2!):**
```
!═══ CẢ R1 VÀ R2 ═══
clock timezone ICT 7 0
clock set 14:00:00 10 Sep 2026            ! lab không có NTP thì set tay CẢ HAI
service timestamps log datetime msec localtime show-timezone
service timestamps debug datetime msec localtime show-timezone
service sequence-numbers
```

---

### LAB A — ⭐⭐ Syslog: severity và cơ chế lọc (30 phút)

**Bước A1 — Bật buffer, tắt spam console:**
```
!═══ R1 ═══
logging buffered 64000 debugging
logging console warnings                  ! chỉ 0–4 ra console
logging monitor debugging
clear logging
```

**Bước A2 — ⭐⭐ Sinh sự kiện và quan sát HAI severity khác nhau:**
```
R1(config)# interface Loopback99
R1(config-if)# ip address 99.99.99.99 255.255.255.255
R1(config-if)# shutdown
R1(config-if)# no shutdown
R1(config-if)# exit
R1# show logging | include Loopback99
```
```
000045: Sep 10 14:05:12.334 ICT: %LINK-3-UPDOWN: Interface Loopback99,
           changed state to administratively down
000046: Sep 10 14:05:12.335 ICT: %LINEPROTO-5-UPDOWN: Line protocol on
           Interface Loopback99, changed state to down
000047: Sep 10 14:05:20.112 ICT: %LINK-3-UPDOWN: Interface Loopback99,
           changed state to up
000048: Sep 10 14:05:20.113 ICT: %LINEPROTO-5-UPDOWN: Line protocol on
           Interface Loopback99, changed state to up
```

✅ **Checkpoint A2 — ⭐ mổ xẻ một dòng, chỉ ra 5 phần:**

| Phần | Giá trị trong ví dụ |
|---|---|
| ⭐ Sequence | `000045` *(nhờ `service sequence-numbers`)* |
| ⭐ Timestamp | `Sep 10 14:05:12.334 ICT` *(nhờ `service timestamps ... msec localtime show-timezone`)* |
| ⭐ Facility | `%LINK` hoặc `%LINEPROTO` |
| ⭐⭐ **Severity** | ⭐ **`3` (Error)** vs ⭐ **`5` (Notification)** |
| ⭐ Mnemonic | `UPDOWN` |

> 💡 ⭐⭐ **Đây là bẫy §3.5 hiện ra bằng dữ liệu thật:** ⭐ **cùng một hành động `shut/no shut`
> sinh ra CẢ severity 3 LẪN severity 5.**

**Bước A3 — 🔴 ⭐⭐ Chứng minh `logging trap` lọc như thế nào:**
```
R1(config)# logging host 10.0.0.2               ! R2 đóng vai "syslog server" (không cần chạy gì)
R1(config)# logging trap 4                    ! chỉ gửi 0–4
R1# show logging | include Trap logging
```
```
    Trap logging: level warnings, 12 message lines logged
        Logging to 10.0.0.2 (udp port 514, audit disabled, link up),
              12 message lines logged, 0 message lines dropped
```
✅ **Checkpoint A3 — ⭐ so sánh hai con số:**
```
R1# show logging | include Buffer logging|Trap logging
    Buffer logging: level debugging, 312 messages logged     ← nhận HẾT (0–7)
    Trap logging:   level warnings,  12 message lines logged ← chỉ gửi 0–4
```
> 💡 ⭐⭐ **Chênh lệch 312 vs 12 chính là bằng chứng của cơ chế lọc.**
> ⭐ **Buffer nhận mức 7 nên có mọi thứ. Trap chỉ mức 4 nên bỏ qua toàn bộ `%LINEPROTO-5`, `%SYS-5`, `%SEC-6`.**

**Bước A4 — ⭐ Đổi ngưỡng và xác nhận:**
```
R1(config)# logging trap 6                    ! informational
R1(config)# interface Loopback99
R1(config-if)# shutdown
R1(config-if)# no shutdown
R1# show logging | include Trap logging
```
✅ ⭐ **Số message gửi đi tăng nhanh hơn hẳn** — ⭐ **vì giờ `%LINEPROTO-5` cũng được gửi.**

> 💡 ⭐ **Ghi vào `SO-TAY-LOI.md`:** ⭐ *"`logging trap N` = gửi mức 0 đến N. Số NHỎ = nghiêm trọng HƠN.
> Đặt trap 4 sẽ thấy interface down (`%LINK-3`) mà KHÔNG thấy nó up lại (`%LINEPROTO-5`)."*

---

### LAB B — ⭐ SNMPv2c và v3 (20 phút)

```
!═══ R1 — v2c (khóa bằng ACL) ═══
ip access-list standard ACL-SNMP
 permit 10.0.0.2
 deny   any log
!
snmp-server community CTY-Read-0nly RO ACL-SNMP
snmp-server location "LAB - EVE-NG"
snmp-server contact "hocvien@lab.local"
snmp-server host 10.0.0.2 version 2c CTY-Read-0nly
snmp-server enable traps snmp linkdown linkup

!═══ R1 — v3 (thứ tự VIEW → GROUP → USER) ═══
snmp-server view VIEW-ALL iso included
snmp-server group GRP-MONITOR v3 priv read VIEW-ALL access ACL-SNMP
snmp-server user netops GRP-MONITOR v3 auth sha AuthPass2026 priv aes 128 PrivPass2026
snmp-server host 10.0.0.2 version 3 priv netops
```

✅ **Checkpoint B — đọc và xác nhận mức bảo mật:**
```
R1# show snmp user
User name: netops
Engine ID: 800000090300...
storage-type: nonvolatile        active
Authentication Protocol: SHA           ← có xác thực
Privacy Protocol: AES128               ← CÓ mã hóa → đây là authPriv ✅
Group-name: GRP-MONITOR

R1# show snmp group
groupname: GRP-MONITOR      security model: v3 priv
readview : VIEW-ALL           writeview: <no writeview>
row status: active     access-list: ACL-SNMP

R1# show snmp host
Notification host: 10.0.0.2   udp-port: 162   type: trap
user: netops   security model: v3 priv
```

> 💡 ⭐ **Thử bỏ phần `priv` khi tạo user** (`... v3 auth sha AuthPass2026`) rồi `show snmp user` →
> ⭐ **`Privacy Protocol: None`** → ⭐ **đó là mức `authNoPriv`, dữ liệu KHÔNG được mã hóa.**
>
> ⚠️ ⭐ Muốn `snmpwalk` thật thì cần một máy Linux. ⭐ **Không có cũng không sao** — đề hỏi
> **v2c vs v3, ba security level, trap vs inform, port 161/162** — ⭐ tất cả đều verify được ở trên.

---

### LAB C — ⭐⭐ FLEXIBLE NETFLOW (40 phút) — **LAB hay nhất module**

> ⭐⭐ **Không cần collector.** ⭐ Bạn sẽ xem toàn bộ bảng flow ngay trên router.

**Bước C1 — Cấu hình đủ 4 thành phần:**
```
!═══ R1 ═══
!─── ① RECORD ───
flow record FR-LAB
 match ipv4 source address
 match ipv4 destination address
 match ipv4 protocol
 match transport source-port
 match transport destination-port
 collect counter bytes
 collect counter packets
 collect interface output
 collect timestamp sys-uptime first
 collect timestamp sys-uptime last
!
!─── ② EXPORTER (trỏ vào R2 — không cần R2 chạy gì) ───
flow exporter FE-LAB
 destination 10.0.0.2
 source Loopback0
 transport udp 2055
 export-protocol netflow-v9
!
!─── ③ MONITOR ───
flow monitor FM-LAB
 record FR-LAB
 exporter FE-LAB
 cache timeout active 60
 cache timeout inactive 15
!
!─── ④ ÁP LÊN INTERFACE ───
interface GigabitEthernet0/0
 ip flow monitor FM-LAB input
 ip flow monitor FM-LAB output
```

**Bước C2 — Sinh nhiều loại traffic khác nhau:**
```
R1# ping 10.0.0.2 repeat 50
R1# ping 10.0.0.2 repeat 30 size 1400
R1# telnet 10.0.0.2 80
R1# telnet 10.0.0.2 443
R2# ping 1.1.1.1 repeat 40 source Loopback0
```

✅ **Checkpoint C2 — ⭐⭐ xem bảng flow NGAY TRÊN ROUTER:**
```
R1# show flow monitor FM-LAB cache format table
```
```
IPV4 SRC ADDR  IPV4 DST ADDR  TRNS SRC PORT  TRNS DST PORT  IP PROT  bytes  pkts
=============  =============  =============  =============  =======  ========  ======
10.0.0.1       10.0.0.2                   0              0        1      5000      50
10.0.0.1       10.0.0.2                   0              0        1     42000      30
2.2.2.2        1.1.1.1                    0              0        1      4000      40
10.0.0.1       10.0.0.2               31421             80        6       120       2
10.0.0.1       10.0.0.2               31422            443        6       120       2
```

> 💡 ⭐⭐ **Bạn vừa nhìn thấy "ai nói chuyện với ai, bao nhiêu byte" mà KHÔNG cần bất kỳ server nào.**
> ⭐ **Đây chính là điều NetFlow làm trong mạng thật, chỉ khác là ở đó có collector vẽ biểu đồ.**

✅ **Checkpoint C3 — ⭐⭐ chứng minh `match` tạo ra flow như thế nào:**

⭐ Đếm số flow hiện tại:
```
R1# show flow monitor FM-LAB cache | include Current
  Current entries: 5
```
⭐ Giờ **bỏ bớt một key field** và xem số flow thay đổi:
```
R1(config)# flow record FR-LAB
R1(config-flow-record)# no match transport source-port
R1# clear flow monitor FM-LAB cache
R1# ping 10.0.0.2 repeat 20
R1# telnet 10.0.0.2 80
R1# telnet 10.0.0.2 443
R1# show flow monitor FM-LAB cache | include Current
```
> 💡 ⭐⭐ **Số flow GIẢM** — vì giờ các kết nối có source port khác nhau **bị gộp thành một flow.**
> ⭐ **Bạn vừa tự chứng minh: `match` = KEY = định nghĩa flow.**
> ⭐ **Thêm match = nhiều flow hơn = cache đầy nhanh hơn.**

✅ **Checkpoint C4 — kiểm tra sức khỏe cache và exporter:**
```
R1# show flow monitor FM-LAB statistics
  Current entries: 3
  High Watermark:   12
  Flows added:      48
  Flows aged:      45
    - Active timeout   (60 secs)   6
    - Inactive timeout (15 secs)   39
    - Emergency aged             0        ← PHẢI là 0
!
R1# show flow exporter FE-LAB statistics
  Packets sent: 24
  Client: Flow Monitor FM-LAB
    Exporting flows to 10.0.0.2 (2055)
```
> 💡 ⭐ **`Emergency aged > 0`** = ⭐ **cache đầy, số liệu không tin được** → tăng `cache entries`
> hoặc giảm số `match`.

**Bước C5 — ⭐ Quan sát `cache timeout active`:**
```
R1(config)# flow monitor FM-LAB
R1(config-flow-monitor)# cache timeout active 1800      ! về mặc định 30 phút
```
⭐ Tạo một flow dài (`ping 10.0.0.2 repeat 10000`) rồi xem `show flow exporter ... statistics` —
⭐ **`Packets sent` gần như không tăng**, vì flow **chưa bị đẩy đi.**
> 💡 🔴 ⭐⭐ **Đây là lý do phải đặt `cache timeout active 60` trong thực tế** — ⭐ **nếu không,
> collector không thấy gì trong 30 phút và bạn tưởng mạng đang rảnh.**

---

### LAB D — ⭐⭐ SPAN và bẫy "cổng câm" (25 phút)

```
!═══ SW1 ═══
monitor session 1 source interface GigabitEthernet0/0 both
monitor session 1 destination interface GigabitEthernet0/3
```
```
SW1# show monitor session 1
Session 1
---------
Type              : Local Session
Source Ports      :
    Both        : Gi0/0
Destination Ports : Gi0/3
    Encapsulation : Native
```

✅ **Checkpoint D1 — 🔴 ⭐⭐ tái hiện bẫy "cổng đích thành câm":**

⭐ **Trước khi cấu hình SPAN**, cắm R2 vào `Gi0/3` và xác nhận ping được.
⭐ **Sau khi cấu hình SPAN với destination = `Gi0/3`:**
```
R2# ping 10.0.0.1
.....                                  ← MẤT MẠNG HOÀN TOÀN
```
```
SW1# show interface Gi0/3 | include line protocol
GigabitEthernet0/3 is up, line protocol is up       ← VẪN BÁO UP/UP!
```
> 💡 🔴 ⭐⭐ **Đây là bài học đắt nhất của LAB D:** ⭐ **cổng vẫn `up/up`, đèn vẫn sáng,
> `show interface` hoàn toàn sạch — nhưng thiết bị cắm vào đó MẤT MẠNG.**
> ⭐ **Vì SPAN destination đã bị trưng dụng: không chuyển traffic thường, không STP, không học MAC.**
>
> ⭐ **Ghi vào `SO-TAY-LOI.md`:** ⭐ *"Trước khi đặt SPAN destination, LUÔN kiểm tra cổng đó có ai đang dùng không."*

✅ **Checkpoint D2 — ⭐ SPAN theo VLAN và các biến thể:**
```
SW1(config)# no monitor session 1
SW1(config)# monitor session 1 source vlan 10 rx
SW1(config)# monitor session 1 destination interface Gi0/3 encapsulation replicate
SW1# show monitor session 1 detail | include VLANs|Encapsulation
```
> 💡 ⭐ **`encapsulation replicate`** giữ nguyên **tag 802.1Q, CDP, STP BPDU** trong bản sao —
> ⭐ **cần thiết khi bạn phân tích chính vấn đề VLAN/STP.**

✅ **Checkpoint D3 — ⭐ RSPAN (nếu có 2 switch):**
```
! TRÊN CẢ HAI SWITCH:
vlan 999
 name RSPAN
 remote-span
!
! Switch nguồn:
monitor session 1 source interface Gi0/0 both
monitor session 1 destination remote vlan 999
!
! Switch đích:
monitor session 2 source remote vlan 999
monitor session 2 destination interface Gi0/3
```
> 💡 🔴 ⭐ **Thử BỎ `remote-span` trên một switch** → ⭐ **RSPAN ngừng hoạt động**,
> ⭐ và VLAN 999 trở thành VLAN thường → traffic sao chép **flood lung tung.**

---

### LAB E — ⭐⭐ IP SLA: đo và failover (40 phút)

**Bước E1 — icmp-echo + track (ôn Module-03/06A):**
```
!═══ R1 ═══
ip sla 10
 icmp-echo 10.0.0.2 source-interface GigabitEthernet0/0
 frequency 5
 timeout 500
 threshold 200
 tag "R2-health"
ip sla schedule 10 life forever start-time now
!
track 1 ip sla 10 reachability
 delay down 10 up 30
```

✅ **Checkpoint E1:**
```
R1# show ip sla statistics 10
IPSLA operation id: 10
    Latest RTT: 4 milliseconds
    Latest operation return code: OK
    Number of successes: 24
    Number of failures: 0

R1# show track 1
Track 1
  IP SLA 10 reachability
  Reachability is Up                 ← ✅
    3 changes, last change 00:02:14
```

**Bước E2 — 🔴 ⭐⭐ Tái hiện lỗi "quên `ip sla schedule`":**
```
R1(config)# ip sla 11
R1(config-ip-sla)# icmp-echo 10.0.0.2
R1(config-ip-sla)# exit
!  CỐ Ý KHÔNG gõ "ip sla schedule 11 ..."
R1# show ip sla statistics 11
```
```
IPSLA operation id: 11
	Operation has not been scheduled
```
> 💡 🔴 ⭐⭐ **Đây là lỗi số 1 với IP SLA.** ⭐ Operation nằm đầy đủ trong config,
> ⭐ **`show run` trông hoàn toàn đúng — nhưng nó KHÔNG BAO GIỜ CHẠY.**

**Bước E3 — ⭐⭐ Test failover thật:**
```
R1(config)# ip route 2.2.2.2 255.255.255.255 10.0.0.2 track 1
R1# show ip route 2.2.2.2 | include via
   * 10.0.0.2                          ← route CÓ trong bảng
```
⭐ **Giờ "cắt" đường** — shutdown interface phía R2:
```
R2(config)# interface Gi0/0
R2(config-if)# shutdown
```
⭐ Chờ ~15 giây rồi xem trên R1:
```
R1# show track 1
  Reachability is Down               ← track đã phát hiện
R1# show ip route 2.2.2.2
   % Network not in table              ← ROUTE ĐÃ TỰ BỊ GỠ
R1# show ip sla statistics 10 | include return code|failures
    Latest operation return code: Timeout
    Number of failures: 3
```
> 💡 ⭐⭐ **Bạn vừa thấy chuỗi hoàn chỉnh: IP SLA phát hiện → track đổi trạng thái → route bị gỡ.**
> ⭐ Đây chính là cơ chế **floating static failover** ở [Module-03](Module-03-IP-Routing-Nen-tang.md),
> giờ bạn nhìn được **từng mắt xích**.

⭐ **Bật lại `no shutdown` và xác nhận route quay về** *(chờ 30s vì `delay up 30`)*.

**Bước E4 — ⭐⭐ udp-jitter với Responder (phần hay nhất LAB E):**
```
!═══ TRÊN R2 (đầu đích) ═══
ip sla responder

!═══ TRÊN R1 (đầu nguồn) ═══
ip sla 20
 udp-jitter 10.0.0.2 5000 codec g711alaw
 frequency 30
 tos 184                              ! DSCP EF (Module-09!)
 tag "VoIP-quality"
ip sla schedule 20 life forever start-time now
```
⭐ Chờ ~2 phút rồi xem:
```
R1# show ip sla statistics 20
```
```
    Number of RTT: 1000     RTT Min/Avg/Max: 2/4/18 milliseconds
    Latency one-way SD: Min/Avg/Max: 1/2/9
    Latency one-way DS: Min/Avg/Max: 1/2/8
    Source to Destination Jitter Min/Avg/Max: 0/1/6
    Destination to Source Jitter Min/Avg/Max: 0/1/5
    Packet Loss SD: 0    Packet Loss DS: 0
    MOS score: 4.39
```
✅ **Checkpoint E4 — ⭐ đối chiếu với ngưỡng VoIP ([Module-09 §8.1](Module-09-Architecture-va-QoS.md)):**

| Chỉ số | Ngưỡng | Đo được | Đạt? |
|---|---|---|:---:|
| One-way latency | ≤ 150 ms | 2 ms | ✅ |
| Jitter | ≤ 30 ms | 1 ms | ✅ |
| Loss | ≤ 1 % | 0 % | ✅ |
| MOS | > 4.0 | 4.39 | ✅ |

> 💡 ⭐⭐ **Bạn vừa tạo ra một báo cáo chất lượng VoIP thật.** ⭐ Trong công việc, đây chính là
> **bằng chứng bạn gửi cho nhà mạng** khi họ nói *"đường của chúng tôi vẫn tốt"*.

✅ **Checkpoint E5 — ⭐ chứng minh vai trò của Responder:**
```
R2(config)# no ip sla responder
R1# clear ip sla statistics 20
```
⭐ Chờ 1 phút:
```
R1# show ip sla statistics 20 | include return code
    Latest operation return code: Timeout
```
> 💡 ⭐⭐ **`udp-jitter` KHÔNG chạy được nếu thiếu Responder.** ⭐ So sánh với `ip sla 10` (icmp-echo)
> vẫn chạy bình thường — ⭐ **đó là khác biệt "cần Responder" vs "không cần".**

---

## 🚀 14. LAB NÂNG CAO

### 14.1 🚀 ⭐⭐ LAB F — Conditional debug an toàn (25 phút)

> ⭐ **Kỹ năng thật sự của mục 4.1.** ⭐ Làm đúng quy trình 5 bước §8.2.

```
!═══ ① CHUẨN BỊ AN TOÀN — làm TRƯỚC khi bật debug ═══
R1(config)# no logging console
R1(config)# logging buffered 128000 debugging
R1# clear logging
R1# show processes cpu sorted | exclude 0.00      ! CPU đang bao nhiêu?

!═══ ② ACL LỌC — chỉ quan tâm traffic giữa 2 địa chỉ ═══
R1(config)# access-list 199 permit icmp host 10.0.0.1 host 10.0.0.2
R1(config)# access-list 199 permit icmp host 10.0.0.2 host 10.0.0.1   ! NHỚ CHIỀU VỀ

!═══ ③ BẬT DEBUG CÓ ĐIỀU KIỆN ═══
R1# debug ip packet 199 detail
R1# show debugging
   Generic IP:
     IP packet debugging is on for access list 199

!═══ ④ TÁI HIỆN — CHỈ VÀI GIÂY ═══
R1# ping 10.0.0.2 repeat 3
R1# undebug all                    ! TẮT NGAY

!═══ ⑤ ĐỌC TỪ BUFFER — thoải mái ═══
R1# show logging | include IP: s=
```

✅ **Checkpoint F1:**
```
IP: s=10.0.0.1 (local), d=10.0.0.2 (GigabitEthernet0/0), len 100, sending
IP: s=10.0.0.2 (GigabitEthernet0/0), d=10.0.0.1 (GigabitEthernet0/0), len 100, rcvd 3
```

✅ **Checkpoint F2 — 🔴 ⭐⭐ tái hiện bẫy CEF (§8.3):**
```
! Ping XUYÊN QUA router (không phải tới router) — traffic này do CEF xử lý
R2# ping 1.1.1.1 source 2.2.2.2 repeat 5
R1# show logging | include IP: s=2.2.2.2
   (TRỐNG — hoặc rất ít dòng)
```
> 💡 🔴 ⭐⭐ **`debug ip packet` CHỈ thấy gói được PROCESS-SWITCHED.**
> ⭐ Traffic đi xuyên qua router được **CEF (fast path)** xử lý → ⭐ **KHÔNG hiện trong debug.**
> ⭐ Traffic **tới chính router** (ping tới IP của nó) thì bị punt lên CPU → **có hiện.**
>
> ⭐ *(Nhắc lại [Module-01 §3](Module-01-Packet-Forwarding-va-Kien-truc-Thiet-bi.md) và
> [Module-10 §5.1](Module-10-Security.md) — cùng một cơ chế "punt".)*
>
> 🔴 ⭐ **Đừng bao giờ gõ `no ip cef` trên production để "nhìn thấy hết"** — bạn vừa tắt hardware forwarding.

✅ **Checkpoint F3 — ⭐ `debug condition`:**
```
R1# debug condition interface GigabitEthernet0/0
R1# debug ip packet detail
R1# show debug condition
   Condition 1: interface Gi0/0 (1 flags triggered)
R1# undebug all
R1# no debug condition all
```

✅ **Checkpoint F4 — 🔴 ⭐ hiểu vì sao console nguy hiểm (làm CẨN THẬN):**
```
R1(config)# logging console debugging       ! bật lại console ở mức 7
R1# debug ip packet
R1# ping 10.0.0.2 repeat 100 size 1400
   → quan sát console bị TRÀN, router phản hồi CHẬM HẲN
R1# u all                                    ! tắt ngay
R1(config)# no logging console               ! trả về an toàn
```
> 💡 🔴 ⭐⭐ **Đó mới chỉ là `debug ip packet` với 100 gói.** ⭐ Hình dung `debug all`
> trên router production có 10.000 gói/giây. ⭐ **Đây là lý do quy trình §8.2 tồn tại.**

### 14.2 🚀 ⭐ LAB G — Tìm MTU bằng extended ping (10 phút)

> ⭐ Nối trực tiếp với [Module-08 §4.4](Module-08-Virtualization-va-Overlay.md).

```
R1# ping 10.0.0.2 df-bit size 1500
!!!!!                                    OK (Ethernet MTU 1500)

R1# ping 10.0.0.2 df-bit size 1501
.....                                  ← vượt MTU

! CHẾ ĐỘ SWEEP — router tự tìm ngưỡng
R1# ping
Protocol [ip]: 
Target IP address: 10.0.0.2
Repeat count [5]: 1
Datagram size [100]: 
Timeout in seconds [2]: 1
Extended commands [n]: y
Source address or interface: 
Type of service [0]: 
Set DF bit in IP header? [no]: y
Validate reply data? [no]: 
Data pattern [0xABCD]: 
Loose, Strict, Record, Timestamp, Verbose[none]: 
Sweep range of sizes [n]: y
Sweep min size [36]: 1480
Sweep max size [18024]: 1520
Sweep interval [1]: 4
```
✅ **Checkpoint G:** ⭐ **Output cho thấy chính xác kích thước nào bắt đầu FAIL.**
⭐ Nếu bạn dựng GRE tunnel từ Module-08 và ping qua nó → ⭐ **ngưỡng sẽ là 1476 (1500 − 24).**

### 14.3 🚀 ⭐ LAB H — Ghép mọi thứ: chẩn đoán một sự cố giả lập (20 phút)

> ⭐ **Bài tập tổng hợp.** ⭐ Nhờ ai đó (hoặc chính bạn, rồi quên đi vài ngày) tạo MỘT lỗi trong
> danh sách dưới, ⭐ **rồi dùng đúng công cụ để tìm ra.**

| # | Lỗi được gieo | ⭐ Công cụ nên dùng |
|:---:|---|---|
| 1 | `shutdown` một interface | ⭐ `show logging \| include LINK-3` |
| 2 | Áp ACL chặn ICMP | ⭐ `show access-lists` (bộ đếm) + `debug ip packet <acl>` |
| 3 | Đổi `cache timeout active` thành 1800 | ⭐ `show flow exporter ... statistics` → `Packets sent` không tăng |
| 4 | Xóa `ip sla schedule` | ⭐ `show ip sla statistics` → **"has not been scheduled"** |
| 5 | Đặt `logging trap 2` | ⭐ `show logging \| include Trap logging` → mức quá thấp |
| 6 | Cấu hình SPAN destination lên cổng đang dùng | ⭐ Thiết bị mất mạng dù cổng `up/up` → `show monitor session all` |
| 7 | Sai `snmp-server user` (thiếu `priv`) | ⭐ `show snmp user` → `Privacy Protocol: None` |
| 8 | Chỉnh lệch đồng hồ R1 so với R2 30 giây | ⭐ `show clock` hai đầu → one-way delay của IP SLA sai bét |

> 💡 ⭐⭐ **Bài tập này mô phỏng đúng công việc thật:** ⭐ **bạn không biết trước lỗi ở đâu,
> phải chọn đúng giác quan để tìm.** ⭐ Ghi lại **mất bao lâu** để tìm ra mỗi lỗi.

### 14.4 🚀 ⭐ LAB I — DNA Center Assurance trên DevNet Sandbox (30 phút)

| Bước | Làm |
|:---:|---|
| 1 | `developer.cisco.com/site/sandbox/` → sandbox **DNA Center** (⭐ Always-On) |
| 2 | ⚠️ ⭐ Lấy URL + tài khoản **từ chính trang sandbox** |

⭐ **Bảng việc — chỉ XEM:**

| # | Tìm gì | ⭐ Liên hệ |
|:---:|---|:---:|
| 1 | ⭐ **Assurance → Health** — điểm health của thiết bị và client | §9.2 |
| 2 | ⭐⭐ **Client 360** — chọn một client, xem toàn bộ hành trình của nó | §9.2 |
| 3 | ⭐⭐ **Path Trace** — chạy thử giữa hai IP, xem đường đi hop-by-hop | §9.2 |
| 4 | ⭐ **Issues** — danh sách vấn đề + gợi ý khắc phục | §9.2 |
| 5 | ⭐ Tìm thanh **thời gian** (Network Time Travel) — tua về quá khứ | §9.2 |

✅ **Checkpoint I:** ⭐ chạy được **một Path Trace** và trả lời: ⭐ *"gói đi qua mấy hop, có ACL nào
trên đường không?"* — ⭐ **đây chính là thứ mà `traceroute` KHÔNG cho bạn biết.**
