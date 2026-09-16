# LAB CAPSTONE — Dự án "Mạng công ty VLT"

> 📘 **Lý thuyết:** [Module-13](Module-13-On-thi-va-Chien-thuat-Phong-thi.md)
>
> ⏱️ **Thời gian:** 12–16 giờ *(chia 3–4 buổi)* · 💾 **RAM:** ~3,5 GB · 🧰 **EVE-NG — 6 node**
>
> 🔴 **Đây KHÔNG phải bài tập theo chương.** Đây là **một dự án hoàn chỉnh**, đề bài viết
> theo **yêu cầu nghiệp vụ** giống hồ sơ thầu ngoài đời — **không nói cho bạn dùng lệnh gì.**

---

## 📋 BỐI CẢNH DỰ ÁN

> Công ty **VLT** có **trụ sở (HQ)** và **một chi nhánh (BRANCH)**.
> Bạn là kỹ sư mạng được giao **triển khai toàn bộ hạ tầng từ con số 0** và **bàn giao có nghiệm thu**.
>
> **Khách hàng đưa ra 13 yêu cầu.** Mỗi yêu cầu có **tiêu chí nghiệm thu rõ ràng** —
> đạt hay không đạt, không có "gần đúng".

### Yêu cầu tổng thể của khách hàng

| # | Khách hàng nói | Dịch sang ngôn ngữ kỹ thuật |
|:---:|---|---|
| 1 | *"Nhân viên phòng nào chỉ thấy mạng phòng đó"* | VLAN + phân tách L2 |
| 2 | *"Đứt một sợi cáp giữa 2 switch thì không được rớt mạng"* | EtherChannel + STP |
| 3 | *"Hỏng một router thì nhân viên không được biết"* | FHRP có tracking |
| 4 | *"Chi nhánh phải nói chuyện được với trụ sở"* | Định tuyến động |
| 5 | *"Chúng tôi thuê 2 nhà mạng, đứt cái này phải tự sang cái kia"* | BGP dual-homed + IP SLA |
| 6 | *"Máy nội bộ phải ra được Internet"* | NAT |
| 7 | *"Chỉ phòng IT được đăng nhập thiết bị"* | AAA + ACL quản trị |
| 8 | *"Có sự cố thì phải biết lúc mấy giờ, ai làm gì"* | NTP + Syslog |
| 9 | *"Tôi muốn biết ai đang ăn hết băng thông"* | NetFlow |
| 10 | *"Ban đêm không có ai trực, thiết bị phải tự xử lý"* | EEM |

---

## 🗺️ SƠ ĐỒ HỆ THỐNG

```
                        ┌──────────────────────┐
                        │        ISP           │  AS 65100
                        │   Lo0: 8.8.8.8/32    │  (mô phỏng Internet)
                        └───┬──────────────┬───┘
                 203.0.113.0/30      198.51.100.0/30
                            │              │
                       Gi0/0│              │Gi0/0
                    ┌───────┴────┐   ┌─────┴──────┐
                    │   EDGE1    │   │   EDGE2    │   AS 65001
                    │ Lo0 1.1.1.1│───│ Lo0 2.2.2.2│
                    └──┬──────┬──┘Gi0/2  ┬────────┘
                       │      │ 10.1.0.0/30
              Gi0/3    │      │Gi0/1     │Gi0/1
         10.1.1.0/30   │      │ trunk    │ trunk
                       │      │          │
              ┌────────┴──┐   │          │
              │  BRANCH   │   │          │
              │Lo0 3.3.3.3│   │          │
              │LAN 10.2.10│   │          │
              └───────────┘   │          │
                              │          │
                        ┌─────┴───┐  ┌───┴─────┐
                        │   SW1   │══│   SW2   │  Po1 (Gi0/2+Gi0/3)
                        │ STP root│  │         │
                        └────┬────┘  └────┬────┘
                          Gi0/1        Gi0/1
                         VLAN 10      VLAN 20
                         (PC1)        (PC2)
```

### Bảng nối dây

| Từ | Cổng | Đến | Cổng | Mạng |
|---|---|---|---|---|
| ISP | Gi0/0 | EDGE1 | Gi0/0 | 203.0.113.0/30 |
| ISP | Gi0/1 | EDGE2 | Gi0/0 | 198.51.100.0/30 |
| EDGE1 | Gi0/2 | EDGE2 | Gi0/2 | 10.1.0.0/30 |
| EDGE1 | Gi0/3 | BRANCH | Gi0/0 | 10.1.1.0/30 |
| EDGE1 | Gi0/1 | SW1 | Gi0/0 | trunk |
| EDGE2 | Gi0/1 | SW2 | Gi0/0 | trunk |
| SW1 | Gi0/2, Gi0/3 | SW2 | Gi0/2, Gi0/3 | **Po1** |
| SW1 | Gi0/1 | PC1 | — | access VLAN 10 |
| SW2 | Gi0/1 | PC2 | — | access VLAN 20 |

### Bảng địa chỉ

| Thiết bị | Cổng | IP | Ghi chú |
|---|---|---|---|
| **ISP** | Lo0 | 8.8.8.8/32 | đích để test Internet |
| | Gi0/0 | 203.0.113.2/30 | |
| | Gi0/1 | 198.51.100.2/30 | |
| **EDGE1** | Lo0 | 1.1.1.1/32 | Router-ID |
| | Gi0/0 | 203.0.113.1/30 | outside |
| | Gi0/2 | 10.1.0.1/30 | tới EDGE2 |
| | Gi0/3 | 10.1.1.1/30 | tới BRANCH |
| | Gi0/1.10 | 10.1.10.2/24 | VLAN 10 |
| | Gi0/1.20 | 10.1.20.2/24 | VLAN 20 |
| | Gi0/1.99 | 10.1.99.2/24 | VLAN 99 quản lý |
| **EDGE2** | Lo0 | 2.2.2.2/32 | Router-ID |
| | Gi0/0 | 198.51.100.1/30 | outside |
| | Gi0/2 | 10.1.0.2/30 | tới EDGE1 |
| | Gi0/1.10 | 10.1.10.3/24 | VLAN 10 |
| | Gi0/1.20 | 10.1.20.3/24 | VLAN 20 |
| | Gi0/1.99 | 10.1.99.3/24 | VLAN 99 |
| **HSRP VIP** | VLAN 10/20/99 | 10.1.X.1 | 🔴 cổng mặc định của PC |
| **SW1** | SVI 99 | 10.1.99.11/24 | quản lý |
| **SW2** | SVI 99 | 10.1.99.12/24 | quản lý |
| **BRANCH** | Lo0 | 3.3.3.3/32 | Router-ID |
| | Gi0/0 | 10.1.1.2/30 | tới EDGE1 |
| | Gi0/1 | 10.2.10.1/24 | LAN chi nhánh |

---

## ⚖️ LUẬT CHƠI — đọc trước khi bắt đầu

| Luật | Chi tiết |
|---|---|
| 🔴 **Làm đúng thứ tự Task 1 → 13** | Task sau phụ thuộc Task trước, y như dự án thật |
| 🔴 **KHÔNG mở đáp án trước khi tự làm** | Mở sớm là bạn tự lấy mất giá trị của bài |
| **Mỗi Task có điểm** | Tổng **100 điểm**. Nghiệm thu đạt từ **80 điểm** |
| **Tiêu chí nghiệm thu là tuyệt đối** | Đạt hoặc không đạt — không có "gần đúng" |
| **Được tra tài liệu** | 🔴 **Nhưng chỉ tra tài liệu của repo này**, không tìm sẵn config trên mạng |
| **Ghi lại thời gian** | Tổng thời gian bạn làm — dùng để đánh giá ở §nghiệm thu |
| **Lỗi > 20 phút** | Ghi vào [`SO-TAY-LOI.md`](SO-TAY-LOI.md), tạm bỏ qua, quay lại sau |

### Bảng điểm

| Giai đoạn | Task | Điểm | Domain |
|---|:---:|:---:|---|
| **1. Nền tảng** | 1–3 | 21 | 3.0 · 5.0 |
| **2. Định tuyến** | 4–6 | 32 | 3.0 |
| **3. Dịch vụ** | 7–8 | 14 | 3.0 |
| **4. Bảo mật** | 9–10 | 13 | 5.0 |
| **5. Giám sát & tự động** | 11–13 | 20 | 4.0 · 6.0 |
| | | **100** | |

---

# 🏗️ GIAI ĐOẠN 1 — NỀN TẢNG

---

## 🎯 TASK 1 — Bàn giao thiết bị và truy cập quản trị (7 điểm)

> **ĐỀ BÀI**
>
> Sáu thiết bị vừa được lắp đặt, đang ở cấu hình trắng. Khách hàng yêu cầu:
>
> 1. Mỗi thiết bị phải có **tên đúng như sơ đồ**.
> 2. Kỹ sư phải **đăng nhập từ xa được**, nhưng 🔴 **tuyệt đối không dùng Telnet**.
> 3. Mật khẩu **không được lưu dạng đọc được** trong file cấu hình.
> 4. Phiên đăng nhập **tự ngắt sau 10 phút** không hoạt động.
> 5. Thiết bị phải hiện **cảnh báo pháp lý** trước khi cho đăng nhập.
> 6. 🔴 **Toàn hệ thống phải cùng một mốc thời gian**, lấy từ EDGE1.

**Tiêu chí nghiệm thu:**

| # | Phải đạt | Kiểm bằng |
|:---:|---|---|
| 1.1 | Hostname đúng trên cả 6 node | `show running-config \| include hostname` |
| 1.2 | 🔴 SSH vào được, **Telnet BỊ TỪ CHỐI** | `telnet <ip>` phải thất bại · `ssh` phải thành công |
| 1.3 | Không thấy mật khẩu dạng chữ thường trong config | `show run \| include password\|secret` |
| 1.4 | Phiên tự ngắt | `show run \| section line vty` |
| 1.5 | Banner hiện trước khi hỏi mật khẩu | Thử đăng nhập |
| 1.6 | 🔴 Đồng hồ khớp nhau trên mọi thiết bị | `show clock` trên từng node |

> 📘 **Kiến thức dùng:** [Module-10 §3](Module-10-Security.md) *(SSH, AAA)* ·
> [Module-06B §3](Module-06B-NAT-NTP-Multicast.md) *(NTP)*

<details><summary>💡 Gợi ý nếu bí (mở cái này trước đáp án)</summary>

- Sinh khoá RSA cần **hostname** và **domain-name** đặt trước — thiếu một trong hai là không sinh được.
- Muốn Telnet bị từ chối thì phải **giới hạn giao thức vào** của `line vty`, không phải chỉ bật SSH.
- Mật khẩu "không đọc được" nghĩa là dùng **hàm băm**, không phải mã hoá đảo ngược được.
- NTP: EDGE1 làm **máy chủ**, các node còn lại làm **máy khách**. Nhớ `ntp master` ở đâu đó.
</details>

<details><summary>✅ ĐÁP ÁN TASK 1</summary>

**Trên MỌI thiết bị** *(đổi hostname cho đúng từng con)*:

```
hostname EDGE1
!
ip domain-name vlt.local
crypto key generate rsa modulus 2048
!
username admin privilege 15 algorithm-type scrypt secret MatKhauRatDaiCuaVLT
!
aaa new-model
aaa authentication login default local
aaa authorization exec default local
!
service password-encryption
!
banner login ^
*************************************************************
*  HE THONG CUA CONG TY VLT - CHI DANH CHO NGUOI CO QUYEN   *
*  Moi truy cap deu duoc ghi log va giam sat.               *
*************************************************************
^
!
line vty 0 4
 transport input ssh          ! ← DONG NAY moi la thu tu choi Telnet
 exec-timeout 10 0
 login local
!
ip ssh version 2
ip ssh time-out 60
ip ssh authentication-retries 3
```

**Chỉ trên EDGE1** *(làm máy chủ thời gian)*:

```
clock timezone ICT 7
ntp master 3
```

**Trên 5 node còn lại:**

```
clock timezone ICT 7
ntp server 10.1.99.2          ! hoac IP EDGE1 ma node do voi toi duoc
```

> 🔴 **Ba chỗ hay sai ở Task 1:**
> 1. Chỉ gõ `ip ssh version 2` mà **quên `transport input ssh`** → Telnet vẫn vào được → **trượt 1.2**.
> 2. Dùng `password` thay vì `secret` → `service password-encryption` chỉ dùng **type 7 đảo ngược được** → **trượt 1.3**.
> 3. Cấu hình `ntp server` trỏ tới IP mà node đó **chưa định tuyến tới được** → làm Task 1 xong mới thấy
>  đồng hồ không đồng bộ. 🔴 **Bình thường — NTP sẽ hội tụ sau Task 5.** Quay lại kiểm 1.6 sau.
</details>

**Điểm:** ☐ 1.1 *(1đ)* ☐ 1.2 *(2đ)* ☐ 1.3 *(1đ)* ☐ 1.4 *(1đ)* ☐ 1.5 *(1đ)* ☐ 1.6 *(1đ)*

---

## 🎯 TASK 2 — Phân tách phòng ban và gộp đường trục (7 điểm)

> **ĐỀ BÀI**
>
> Khách hàng nói: *"Phòng Kế toán và phòng Kỹ thuật **không được thấy nhau ở tầng mạng**.
> Ngoài ra chúng tôi có một mạng riêng để quản trị thiết bị, nhân viên thường **không được vào**."*
>
> Và: *"Giữa hai switch tôi đã kéo **2 sợi cáp**. Tôi muốn **dùng cả hai cùng lúc**,
> chứ không phải một sợi chạy một sợi nằm chơi. **Đứt một sợi thì không được rớt mạng.**"*
>
> | VLAN | Tên | Dùng cho |
> |:---:|---|---|
> | 10 | `KE-TOAN` | PC1 |
> | 20 | `KY-THUAT` | PC2 |
> | 99 | `QUAN-LY` | SVI của switch |
>
> 🔴 **Ràng buộc:** đường trục giữa 2 switch phải là **một đường luận lý duy nhất** dưới mắt STP,
> và phải thương lượng bằng **giao thức chuẩn mở** *(không dùng giao thức riêng của Cisco)*.

**Tiêu chí nghiệm thu:**

| # | Phải đạt | Kiểm bằng |
|:---:|---|---|
| 2.1 | Ba VLAN tồn tại, **đúng tên** trên cả 2 switch | `show vlan brief` |
| 2.2 | Cổng PC là **access**, đúng VLAN | `show interfaces Gi0/1 switchport` |
| 2.3 | Trunk lên EDGE hoạt động, cho qua đủ 3 VLAN | `show interfaces trunk` |
| 2.4 | 🔴 EtherChannel trạng thái **`SU`**, giao thức **LACP** | `show etherchannel summary` |
| 2.5 | 🔴 Cả **2 cổng đều `(P)`** | `show etherchannel summary` |
| 2.6 | Rút 1 sợi → **ping không mất quá 1 gói** | Rút cáp trong EVE-NG khi đang ping |

> 📘 **Kiến thức dùng:** [Module-02 §3.5](Module-02-Layer2-STP-RSTP-MST-EtherChannel.md)

<details><summary>💡 Gợi ý nếu bí</summary>

- "Giao thức chuẩn mở" cho EtherChannel = **LACP** *(PAgP mới là của Cisco)*.
- LACP có 2 chế độ: một chế độ **chủ động hỏi**, một chế độ **chỉ trả lời**.
  🔴 **Hai đầu cùng để chế độ "chỉ trả lời" thì bó KHÔNG BAO GIỜ lên.**
- Tham số gộp đặt trên **interface vật lý**; tham số chung đặt trên **Port-channel**.
- 🔴 **Hai cổng thành viên phải giống hệt nhau** về speed/duplex/mode/VLAN.
</details>

<details><summary>✅ ĐÁP ÁN TASK 2</summary>

**Trên SW1 và SW2:**

```
vlan 10
 name KE-TOAN
vlan 20
 name KY-THUAT
vlan 99
 name QUAN-LY
!
interface range GigabitEthernet0/2 - 3
 switchport trunk encapsulation dot1q
 switchport mode trunk
 channel-protocol lacp
 channel-group 1 mode active
 no shutdown
!
interface Port-channel1
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk allowed vlan 10,20,99
!
interface GigabitEthernet0/0
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk allowed vlan 10,20,99
 no shutdown
!
interface Vlan99
 ip address 10.1.99.11 255.255.255.0
 no shutdown
!
ip default-gateway 10.1.99.1
```

*(SW2 dùng `10.1.99.12`)*

**Cổng nối PC — SW1 dùng VLAN 10, SW2 dùng VLAN 20:**

```
interface GigabitEthernet0/1
 switchport mode access
 switchport access vlan 10
 no shutdown
```

**Kiểm chứng đúng:**

```
SW1# show etherchannel summary
Group  Port-channel  Protocol    Ports
------+-------------+-----------+---------------------------
1      Po1(SU)        LACP        Gi0/2(P)   Gi0/3(P)
```

> 🔴 **Đọc ký hiệu — chỗ mất điểm nhiều nhất:**
>
> | Ký hiệu | Nghĩa |
> |:---:|---|
> | **`(P)`** | ✅ Đang **trong bó** — đúng |
> | **`(I)`** | 🔴 **Individual** — cổng chạy **độc lập**, bó KHÔNG hình thành. **Nguy hiểm nhất vì mạng vẫn thông** nên bạn tưởng đã xong |
> | **`(s)`** | Suspended — bị treo, thường do lệch tham số |
> | **`(D)`** | Down |
>
> 🔴 **Thấy `(I)` là trượt 2.4 và 2.5** — dù ping vẫn chạy bình thường.
>
> **Nguyên nhân `(I)` hay gặp nhất:** một đầu để `mode active`, đầu kia để `mode passive`
> thì **vẫn lên**; nhưng **cả hai cùng `passive`** thì không ai mở lời → `(I)`.
</details>

**Điểm:** ☐ 2.1 *(1đ)* ☐ 2.2 *(1đ)* ☐ 2.3 *(1đ)* ☐ 2.4 *(2đ)* ☐ 2.5 *(1đ)* ☐ 2.6 *(1đ)*

---

## 🎯 TASK 3 — Chống vòng lặp và chống thiết bị lạ (7 điểm)

> **ĐỀ BÀI**
>
> Khách hàng kể: *"Lần trước có nhân viên tự cắm một cái switch mini mua ngoài chợ vào ổ mạng,
> **cả công ty mất mạng nửa buổi sáng**. Tôi không muốn chuyện đó lặp lại."*
>
> Yêu cầu:
> 1. 🔴 **SW1 phải là gốc của cây STP** cho mọi VLAN — không để thiết bị tự bầu.
> 2. **SW2 là gốc dự phòng** — SW1 chết thì SW2 lên thay.
> 3. 🔴 Nếu ai cắm switch lạ vào **cổng nối PC** → **cổng đó phải tự tắt ngay**.
> 4. Cổng nối PC phải **lên mạng tức thì**, không bắt nhân viên chờ 30 giây.
> 5. 🔴 Mỗi cổng PC **chỉ cho tối đa 2 địa chỉ MAC**; vượt quá thì **tắt cổng**.

**Tiêu chí nghiệm thu:**

| # | Phải đạt | Kiểm bằng |
|:---:|---|---|
| 3.1 | 🔴 SW1 là root cho **tất cả** VLAN | `show spanning-tree root` |
| 3.2 | SW2 là root thứ hai | So priority 2 switch |
| 3.3 | Cổng PC lên `FWD` gần như tức thì | `show spanning-tree interface Gi0/1` |
| 3.4 | 🔴 Cổng PC có bảo vệ chống switch lạ | `show spanning-tree interface Gi0/1 detail` |
| 3.5 | 🔴 Port-security: **tối đa 2 MAC**, vi phạm → **shutdown** | `show port-security interface Gi0/1` |
| 3.6 | Gây vi phạm thử → cổng vào `err-disabled` | Tự thử |

> 📘 **Kiến thức dùng:** [Module-02 §3.1, §3.4](Module-02-Layer2-STP-RSTP-MST-EtherChannel.md) ·
> [Module-10](Module-10-Security.md)

<details><summary>💡 Gợi ý nếu bí</summary>

- Ép root: có lệnh làm hộ bạn. 🔴 **Priority chỉ nhận bội số của 4096.**
- 🔴 **Phân biệt hai loại bảo vệ — đề rất thích hỏi:**
  - Loại chặn **mọi BPDU đi vào cổng lẽ ra không có BPDU** → dùng ở **cổng PC**.
  - Loại chỉ chặn **BPDU tốt hơn root hiện tại** → dùng ở **cổng trunk**.

  Đề nói "cắm vào **cổng nối PC**" → chọn loại nào?
- "Lên mạng tức thì" và "chống switch lạ" là **hai lệnh khác nhau**, luôn đi cùng nhau.
</details>

<details><summary>✅ ĐÁP ÁN TASK 3</summary>

**SW1 — root chính:**

```
spanning-tree mode rapid-pvst
spanning-tree vlan 10,20,99 root primary
```

**SW2 — root dự phòng:**

```
spanning-tree mode rapid-pvst
spanning-tree vlan 10,20,99 root secondary
```

**Cổng nối PC — cả 2 switch:**

```
interface GigabitEthernet0/1
 spanning-tree portfast
 spanning-tree bpduguard enable
 !
 switchport port-security
 switchport port-security maximum 2
 switchport port-security violation shutdown
 switchport port-security mac-address sticky
```

**Kiểm chứng root:**

```
SW1# show spanning-tree root
                                        Root    Hello Max Fwd
Vlan            Root ID                 Cost    Time  Age Dly
--------------- -------------------- --------- ----- --- ---
VLAN0010        24586 0c1f.xxxx.xxxx        0    2    20  15
                  ↑                         ↑
        24576 + 10 (so VLAN)      cost 0 = CHINH NO la root
```

> 🔴 **Bẫy lớn nhất Task 3 — BPDU Guard hay Root Guard?**
>
> | | **BPDU Guard** | **Root Guard** |
> |---|---|---|
> | Đặt ở | 🔴 **Cổng access nối PC** | **Cổng trunk nối switch khác** |
> | Kích hoạt khi | 🔴 **Nhận BẤT KỲ BPDU nào** | Nhận BPDU **tốt hơn** root hiện tại |
> | Phản ứng | 🔴 **Tắt cổng — `err-disabled`** | Chặn cổng — `root-inconsistent` |
> | Phục hồi | Bật lại tay *(hoặc `errdisable recovery`)* | 🔴 **Tự phục hồi** khi BPDU xấu ngừng |
>
> 🔴 **Đề nói "cổng nối PC" → đáp án là BPDU Guard.**
> Root Guard ở đây cũng chặn được, nhưng **sai ý đồ thiết kế**: cổng PC thì
> **không được có BPDU nào cả**, chứ không phải "chỉ cấm BPDU tốt hơn".

**Nghiệm thu 3.6 — tự gây vi phạm:**

```
SW1# show port-security interface GigabitEthernet0/1
Port Security              : Enabled
Port Status                : Secure-shutdown        ← sau khi vi pham
Violation Mode             : Shutdown
Maximum MAC Addresses      : 2
Security Violation Count   : 1

SW1# show interfaces Gi0/1 | include line protocol
GigabitEthernet0/1 is down, line protocol is down (err-disabled)

! Bat lai:
SW1(config-if)# shutdown
SW1(config-if)# no shutdown
```
</details>

**Điểm:** ☐ 3.1 *(2đ)* ☐ 3.2 *(1đ)* ☐ 3.3 *(1đ)* ☐ 3.4 *(1đ)* ☐ 3.5 *(1đ)* ☐ 3.6 *(1đ)*

---

# 🧭 GIAI ĐOẠN 2 — ĐỊNH TUYẾN

---

## 🎯 TASK 4 — Cổng mặc định không bao giờ chết (12 điểm)

> **ĐỀ BÀI**
>
> Khách hàng: *"Tôi trả tiền cho **hai** con router ở trụ sở. Tôi muốn: **hỏng một con thì
> nhân viên không hề hay biết** — không phải đổi cấu hình máy tính, không phải gọi IT."*
>
> Bổ sung: *"Bình thường tôi muốn **EDGE1 gánh việc**, EDGE2 nằm chờ.
> Nhưng 🔴 **nếu đường ra Internet của EDGE1 chết** thì EDGE2 phải lên gánh — chứ không phải
> để traffic đi vào EDGE1 rồi mắc kẹt ở đó."*
>
> Và: *"Khi EDGE1 sống lại, **nó phải tự lấy lại việc**, tôi không muốn phải can thiệp tay."*
>
> 🔴 **Ràng buộc:** dùng **giao thức dự phòng cổng chuẩn mở** *(không dùng giao thức riêng Cisco)*.

**Tiêu chí nghiệm thu:**

| # | Phải đạt | Kiểm bằng |
|:---:|---|---|
| 4.1 | Sub-interface đúng IP cho 3 VLAN trên cả 2 EDGE | `show ip interface brief` |
| 4.2 | 🔴 PC ping được VIP `10.1.X.1` | `ping` từ PC |
| 4.3 | 🔴 EDGE1 là **Master**, EDGE2 là **Backup** cả 3 VLAN | `show vrrp brief` |
| 4.4 | Tắt EDGE1 → PC **vẫn ping ra được** | Ping liên tục rồi `shutdown` EDGE1 |
| 4.5 | 🔴 **Shut cổng WAN EDGE1 → quyền chuyển sang EDGE2** | `shutdown` Gi0/0 của EDGE1 |
| 4.6 | 🔴 Bật lại → **EDGE1 tự lấy lại quyền** | `no shutdown` rồi xem lại |

> 📘 **Kiến thức dùng:** [Module-06A](Module-06A-FHRP-HSRP-VRRP-GLBP.md) *(FHRP + tracking)* ·
> [Module-03 §2.4](Module-03-IP-Routing-Nen-tang.md) *(IP SLA + track)*

<details><summary>💡 Gợi ý nếu bí</summary>

- "Chuẩn mở" → 🔴 **VRRP** *(HSRP và GLBP đều là của Cisco)*.
- 🔴 **VRRP bật preempt SẴN theo mặc định** — khác HSRP *(mặc định TẮT)*.
  Yêu cầu "tự lấy lại việc" vì thế **không cần gõ thêm gì** với VRRP.
- Yêu cầu "đường ra Internet chết thì nhường quyền" = **tracking**.
  🔴 **Chỉ track cổng là CHƯA đủ** — cổng có thể vẫn `up` mà nhà mạng đã chết bên trong.
  Muốn chắc thì phải **đo thật bằng cách ping một đích ngoài Internet**.
- 🔴 Giá trị track phải **đủ lớn để kéo priority xuống DƯỚI đối thủ**, nếu không nhường quyền
  sẽ không xảy ra dù track đã Down.
</details>

<details><summary>✅ ĐÁP ÁN TASK 4</summary>

**EDGE1 — sub-interface + VRRP:**

```
interface GigabitEthernet0/1
 no ip address
 no shutdown
!
interface GigabitEthernet0/1.10
 encapsulation dot1Q 10
 ip address 10.1.10.2 255.255.255.0
 vrrp 10 ip 10.1.10.1
 vrrp 10 priority 120
 vrrp 10 track 1 decrement 40
!
interface GigabitEthernet0/1.20
 encapsulation dot1Q 20
 ip address 10.1.20.2 255.255.255.0
 vrrp 20 ip 10.1.20.1
 vrrp 20 priority 120
 vrrp 20 track 1 decrement 40
!
interface GigabitEthernet0/1.99
 encapsulation dot1Q 99
 ip address 10.1.99.2 255.255.255.0
 vrrp 99 ip 10.1.99.1
 vrrp 99 priority 120
 vrrp 99 track 1 decrement 40
```

> 🔴 **KHẮC PHỤC THỨ TỰ — đọc trước khi cấu hình IP SLA:**
> IP SLA dưới đây ping `8.8.8.8`, nhưng **đường ra Internet mãi Task 6 (BGP) mới có**.
> Nếu làm đúng thứ tự, ở thời điểm này **track sẽ Down ngay từ đầu** — không phải bạn sai.
>
> **Hai cách xử lý, chọn một:**
> - Ⓐ Thêm **default route tạm** để test ngay:
>   `ip route 0.0.0.0 0.0.0.0 203.0.113.2` trên EDGE1 và `198.51.100.2` trên EDGE2.
>   ⚠️ **Nhớ XOÁ hai dòng này sau khi xong Task 6**, nếu không chúng sẽ
>   **đè lên default route học từ BGP** *(static AD 1 < eBGP AD 20)* và phá hỏng Task 6.
> - Ⓑ Cấu hình đủ bây giờ, nhưng **hoãn nghiệm thu 4.5 lại cho đến sau Task 6**.
>
> ⭐ **Đây không phải lỗi đề bài — dự án thật luôn có những phụ thuộc chéo kiểu này.**
> **Biết nhận ra và xử lý chúng mới là kỹ năng đáng học.**

**EDGE1 — đo đường Internet THẬT bằng IP SLA:**

```
ip sla 1
 icmp-echo 8.8.8.8 source-interface GigabitEthernet0/0
 frequency 5
 timeout 2000
ip sla schedule 1 life forever start-time now
!
track 1 ip sla 1 reachability
 delay down 3 up 5
```

**EDGE2 — giống hệt nhưng priority thấp hơn, không cần track:**

```
interface GigabitEthernet0/1.10
 encapsulation dot1Q 10
 ip address 10.1.10.3 255.255.255.0
 vrrp 10 ip 10.1.10.1
 vrrp 10 priority 100
```

*(tương tự cho .20 và .99)*

**Kiểm chứng:**

```
EDGE1# show vrrp brief
Interface      Grp Pri Time  Own Pre State   Master addr     Group addr
Gi0/1.10        10 120 3531       Y  Master  10.1.10.2       10.1.10.1
                    ↑                 ↑
              priority 120     Pre = Y → preempt BAT SAN
```

**Thử nghiệm 4.5 — shut cổng WAN của EDGE1:**

```
EDGE1(config)# interface GigabitEthernet0/0
EDGE1(config-if)# shutdown

! Sau ~15 giay (delay down 3 + hoi tu):
EDGE1# show track 1
Track 1
  IP SLA 1 reachability
  Reachability is Down           ← IP SLA khong ping duoc 8.8.8.8 nua

EDGE1# show vrrp brief
Gi0/1.10        10  80 ...        N  Backup  10.1.10.3    10.1.10.1
                    ↑                  ↑
          120 - 40 = 80        da nhuong quyen cho EDGE2 ✅
```

> 🔴 **Ba chỗ quyết định đúng/sai của Task 4:**
>
> 1. 🔴 **Track phải kéo priority xuống DƯỚI đối thủ.**
>  `120 − 40 = 80 < 100` ✅. Nếu bạn đặt `decrement 10` → `110 > 100` →
>  **track Down nhưng KHÔNG nhường quyền** → trượt 4.5.
>
> 2. 🔴 **Phải có `source-interface` trong `icmp-echo`.**
>  Về cú pháp nó là **tuỳ chọn** — nhưng ở đây thiếu nó thì SLA ping theo bảng route,
>  đi vòng qua EDGE2 và **vẫn báo OK dù cổng WAN của EDGE1 đã chết** →
>  **track không bao giờ Down** → trượt 4.5.
>
> 3. 🔴 **VRRP preempt bật sẵn**, nên yêu cầu 4.6 tự đạt.
>  Nếu bạn chọn **HSRP** thì **phải gõ thêm `standby 10 preempt`** — thiếu là trượt 4.6.
>  Đây chính là khác biệt HSRP/VRRP mà đề ENCOR rất hay hỏi.
</details>

**Điểm:** ☐ 4.1 *(2đ)* ☐ 4.2 *(2đ)* ☐ 4.3 *(2đ)* ☐ 4.4 *(2đ)* ☐ 4.5 *(3đ)* ☐ 4.6 *(1đ)*

---

## 🎯 TASK 5 — Định tuyến nội bộ giữa trụ sở và chi nhánh (10 điểm)

> **ĐỀ BÀI**
>
> Khách hàng: *"Chi nhánh phải nói chuyện được với trụ sở. Nhưng tôi có ba lo ngại:*
>
> 1. *Router chi nhánh là **con rẻ tiền, RAM ít**. Nó **chỉ có một đường duy nhất** về trụ sở,
>  nên **đừng bắt nó nhớ chi tiết toàn bộ mạng công ty** — cho nó biết đường ra là đủ.*
> 2. *Sau này tôi mở thêm chi nhánh. **Bảng định tuyến ở trụ sở không được phình ra**
>  mỗi lần tôi mở thêm một mạng con ở chi nhánh.*
> 3. *Tôi không muốn ai cắm một con router lạ vào là **tự động tham gia định tuyến** được."*
>
> **Quy hoạch vùng:** trụ sở = **vùng 0** · chi nhánh = **vùng 1** · EDGE1 là **cầu nối hai vùng**.
> Chi nhánh sẽ mở rộng trong dải **10.2.0.0/16**.

**Tiêu chí nghiệm thu:**

| # | Phải đạt | Kiểm bằng |
|:---:|---|---|
| 5.1 | Neighbor OSPF **FULL** giữa EDGE1–EDGE2 và EDGE1–BRANCH | `show ip ospf neighbor` |
| 5.2 | BRANCH ping được **mọi VLAN** của trụ sở | `ping 10.1.10.1` từ BRANCH |
| 5.3 | 🔴 Bảng route của BRANCH **gọn** — không có chi tiết từng mạng trụ sở | `show ip route` trên BRANCH |
| 5.4 | 🔴 Trụ sở chỉ thấy **một dòng `10.2.0.0/16`**, không thấy từng /24 | `show ip route ospf` trên EDGE2 |
| 5.5 | 🔴 Xác thực OSPF bật — router không có khoá **không lên neighbor** | `show ip ospf interface` |
| 5.6 | Router-ID đúng loopback đã quy hoạch | `show ip ospf` |

> 📘 **Kiến thức dùng:** [Module-04A](Module-04A-OSPF-Nen-tang-va-LSDB.md) ·
> [Module-04B](Module-04B-OSPF-Area-Summarization-OSPFv3.md) *(area type + summarization)*

<details><summary>💡 Gợi ý nếu bí</summary>

- Lo ngại 1 = **loại vùng đặc biệt**. Chi nhánh **chỉ có một đường ra** → dùng loại vùng
  **chặn nhiều nhất** và thay mọi thứ bằng **một default route**.
  🔴 **Lưu ý: cấu hình ở ABR và ở router trong vùng KHÁC NHAU một từ khoá.**
- Lo ngại 2 = **tóm tắt tuyến**. 🔴 **Tóm tắt giữa các vùng làm ở ABR bằng lệnh khác**
  với tóm tắt tuyến ngoại (redistribute).
- Lo ngại 3 = **xác thực**. Chọn loại băm mạnh, đừng dùng plaintext.
- 🔴 Router-ID nên **đặt tay**, đừng để nó tự chọn — tự chọn sẽ đổi khi loopback thay đổi.
</details>

<details><summary>✅ ĐÁP ÁN TASK 5</summary>

**EDGE1 (ABR — nối cả hai vùng):**

```
interface Loopback0
 ip address 1.1.1.1 255.255.255.255
!
router ospf 1
 router-id 1.1.1.1
 !
 ! Vung 0 - tru so
 network 10.1.0.0 0.0.0.3 area 0
 network 10.1.10.0 0.0.0.255 area 0
 network 10.1.20.0 0.0.0.255 area 0
 network 10.1.99.0 0.0.0.255 area 0
 network 1.1.1.1 0.0.0.0 area 0
 !
 ! Vung 1 - chi nhanh
 network 10.1.1.0 0.0.0.3 area 1
 !
 ! Lo ngai 1: chi nhanh chi nhan DEFAULT ROUTE
 area 1 stub no-summary                    ! ← "no-summary" CHI dat o ABR
 !
 ! Lo ngai 2: gom mang chi nhanh thanh MOT dong
 area 1 range 10.2.0.0 255.255.0.0
 !
 passive-interface default
 no passive-interface GigabitEthernet0/2
 no passive-interface GigabitEthernet0/3
```

**EDGE2:**

```
interface Loopback0
 ip address 2.2.2.2 255.255.255.255
!
router ospf 1
 router-id 2.2.2.2
 network 10.1.0.0 0.0.0.3 area 0
 network 10.1.10.0 0.0.0.255 area 0
 network 10.1.20.0 0.0.0.255 area 0
 network 10.1.99.0 0.0.0.255 area 0
 network 2.2.2.2 0.0.0.0 area 0
 passive-interface default
 no passive-interface GigabitEthernet0/2
```

**BRANCH:**

```
interface Loopback0
 ip address 3.3.3.3 255.255.255.255
!
router ospf 1
 router-id 3.3.3.3
 network 10.1.1.0 0.0.0.3 area 1
 network 10.2.10.0 0.0.0.255 area 1
 network 3.3.3.3 0.0.0.0 area 1
 !
 area 1 stub                               ! ← KHONG co "no-summary" o day
 !
 passive-interface default
 no passive-interface GigabitEthernet0/0
```

**Xác thực — trên cả 3 router, ở interface nối nhau:**

```
interface GigabitEthernet0/2
 ip ospf authentication message-digest
 ip ospf message-digest-key 1 md5 KhoaOspfCuaVLT
```

*(EDGE1 làm cả Gi0/2 và Gi0/3; BRANCH làm Gi0/0)*

**Kiểm chứng 5.3 — bảng route BRANCH phải GỌN:**

```
BRANCH# show ip route ospf
      10.0.0.0/8 is variably subnetted
O*IA  0.0.0.0/0 [110/2] via 10.1.1.1, 00:05:12, GigabitEthernet0/0
       ↑
   CHI CO MOT DONG DEFAULT - dung y do "router re tien, RAM it" ✅
```

**Kiểm chứng 5.4 — trụ sở chỉ thấy một dòng tóm tắt:**

```
EDGE2# show ip route ospf
O IA  10.2.0.0/16 [110/3] via 10.1.0.1, 00:04:01, GigabitEthernet0/2
       ↑
   MOT dong thay vi tung /24 ✅
```

> 🔴 **Bốn chỗ quyết định đúng/sai Task 5:**
>
> 1. 🔴 **`no-summary` CHỈ gõ ở ABR (EDGE1).** Gõ nhầm ở BRANCH là sai cú pháp/vô nghĩa.
>  - `area 1 stub` → chặn tuyến **ngoại** (LSA 5), vẫn nhận LSA 3 liên vùng.
>  - `area 1 stub no-summary` *(totally stubby)* → 🔴 **chặn cả LSA 3**, thay bằng **một default**.
>  - Đề nói *"chỉ có một đường ra, cho nó biết đường ra là đủ"* → **totally stubby**.
>
> 2. 🔴 **Mọi router trong cùng một vùng stub PHẢI cùng khai `stub`.**
>  Thiếu ở một con → **cờ E-bit lệch → neighbor KHÔNG lên** *(điều kiện số 8 ở Module-04A)*.
>
> 3. 🔴 **`area 1 range` gom tuyến LIÊN VÙNG và chỉ chạy ở ABR.**
>  Đừng nhầm với `summary-address` — cái đó dành cho tuyến **redistribute vào** *(ASBR)*.
>
> 4. 🔴 **`passive-interface default` rồi mở lại đúng cổng cần chạy OSPF.**
>  Đây là thói quen bảo mật: mặc định **không quảng bá ra đâu cả**, chỉ mở nơi thật sự cần.
>  Quên mở lại cổng nối neighbor → **neighbor không bao giờ lên** *(điều kiện số 3)*.
</details>

**Điểm:** ☐ 5.1 *(2đ)* ☐ 5.2 *(1đ)* ☐ 5.3 *(2đ)* ☐ 5.4 *(2đ)* ☐ 5.5 *(2đ)* ☐ 5.6 *(1đ)*

---

## 🎯 TASK 6 — Đấu nối hai nhà mạng và điều hướng traffic (10 điểm)

> **ĐỀ BÀI**
>
> Khách hàng: *"Công ty tôi có **số hiệu mạng riêng AS 65001** và được cấp dải công cộng
> **192.0.2.0/24**. Tôi đấu **hai đường** lên nhà mạng AS 65100.*
>
> *Yêu cầu của tôi:*
> 1. *🔴 **Traffic ĐI RA Internet phải ưu tiên đường EDGE1.** EDGE2 chỉ dùng khi EDGE1 chết.*
> 2. *🔴 **Traffic TỪ Internet VÀO cũng phải ưu tiên đường EDGE1.** Tôi biết cái này khó hơn.*
> 3. *Router của tôi **không đủ RAM ôm cả bảng định tuyến Internet**. 🔴 **Chỉ nhận đường mặc định.***
> 4. *Hai con EDGE phải **trao đổi thông tin với nhau**, đừng để mỗi con hiểu một kiểu.*
> 5. *Phiên BGP giữa hai con EDGE **không được chết** chỉ vì đứt một sợi cáp giữa chúng.*

**Tiêu chí nghiệm thu:**

| # | Phải đạt | Kiểm bằng |
|:---:|---|---|
| 6.1 | eBGP lên `Established` ở **cả hai** EDGE | `show ip bgp summary` |
| 6.2 | 🔴 iBGP EDGE1–EDGE2 `Established`, **peer bằng loopback** | `show ip bgp neighbors` |
| 6.3 | `192.0.2.0/24` xuất hiện trên ISP từ **cả hai** đường | `show ip bgp` trên ISP |
| 6.4 | 🔴 Bảng BGP trên EDGE chỉ có **default route**, không có bảng đầy | `show ip bgp \| count` |
| 6.5 | 🔴 EDGE2 chọn đường ra **qua EDGE1** *(local preference)* | `show ip bgp 0.0.0.0` trên EDGE2 |
| 6.6 | 🔴 ISP chọn đường vào **qua EDGE1** *(AS-path ngắn hơn)* | `show ip bgp 192.0.2.0` trên ISP |

> 📘 **Kiến thức dùng:** [Module-05A](Module-05A-BGP-Nen-tang-va-eBGP-Peering.md) ·
> [Module-05B](Module-05B-BGP-Path-Selection-va-Filtering.md) *(13 bước chọn đường)*

<details><summary>💡 Gợi ý nếu bí</summary>

- Yêu cầu 5 *("không chết vì đứt một sợi")* = 🔴 **peer bằng địa chỉ loopback**, không phải IP cổng vật lý.
  Loopback không bao giờ down, và OSPF ở Task 5 đã lo đường tới nó.
  🔴 **Peer bằng loopback thì phải khai thêm HAI thứ** — một cái nói "tôi gửi đi từ đâu",
  một cái sửa vấn đề next-hop của iBGP.
- Yêu cầu 1 *(traffic ĐI RA)* = thuộc tính **ảnh hưởng quyết định của CHÍNH MÌNH**,
  chỉ trao đổi **trong nội bộ AS**. 🔴 **Giá trị CAO hơn thì thắng.**
- Yêu cầu 2 *(traffic ĐI VÀO)* = bạn **không ra lệnh được cho nhà mạng**.
  Cách duy nhất là **làm cho đường kia trông XẤU hơn** trong mắt họ →
  🔴 **kéo dài AS-path của EDGE2** *(prepend)*.
- Yêu cầu 3 = **lọc tuyến nhận vào** bằng prefix-list, chỉ cho `0.0.0.0/0` qua.
</details>

<details><summary>✅ ĐÁP ÁN TASK 6</summary>

**EDGE1:**

```
router bgp 65001
 bgp router-id 1.1.1.1
 bgp log-neighbor-changes
 !
 ! eBGP toi nha mang
 neighbor 203.0.113.2 remote-as 65100
 neighbor 203.0.113.2 description ISP-duong-CHINH
 !
 ! iBGP toi EDGE2 - PEER BANG LOOPBACK
 neighbor 2.2.2.2 remote-as 65001
 neighbor 2.2.2.2 update-source Loopback0     ! toi gui di TU loopback
 !
 address-family ipv4
  network 192.0.2.0 mask 255.255.255.0
  !
  neighbor 203.0.113.2 activate
  neighbor 203.0.113.2 prefix-list CHI-NHAN-DEFAULT in
  neighbor 203.0.113.2 route-map DAT-LOCALPREF-CAO in
  !
  neighbor 2.2.2.2 activate
  neighbor 2.2.2.2 next-hop-self               ! BAT BUOC voi iBGP
 exit-address-family
!
! Chi nhan duong mac dinh - yeu cau 3
ip prefix-list CHI-NHAN-DEFAULT seq 5 permit 0.0.0.0/0
!
! Duong ra uu tien EDGE1 - yeu cau 1
route-map DAT-LOCALPREF-CAO permit 10
 set local-preference 200
!
! De co 192.0.2.0/24 trong bang route (neu chua co interface nao dung)
ip route 192.0.2.0 255.255.255.0 Null0
```

**EDGE2:**

```
router bgp 65001
 bgp router-id 2.2.2.2
 !
 neighbor 198.51.100.2 remote-as 65100
 neighbor 198.51.100.2 description ISP-duong-DU-PHONG
 !
 neighbor 1.1.1.1 remote-as 65001
 neighbor 1.1.1.1 update-source Loopback0
 !
 address-family ipv4
  network 192.0.2.0 mask 255.255.255.0
  !
  neighbor 198.51.100.2 activate
  neighbor 198.51.100.2 prefix-list CHI-NHAN-DEFAULT in
  neighbor 198.51.100.2 route-map KEO-DAI-ASPATH out    ! yeu cau 2
  !
  neighbor 1.1.1.1 activate
  neighbor 1.1.1.1 next-hop-self
 exit-address-family
!
ip prefix-list CHI-NHAN-DEFAULT seq 5 permit 0.0.0.0/0
!
! Lam duong EDGE2 trong XAU hon trong mat nha mang - yeu cau 2
route-map KEO-DAI-ASPATH permit 10
 set as-path prepend 65001 65001 65001
!
ip route 192.0.2.0 255.255.255.0 Null0
```

**ISP** *(để bạn dựng được lab)*:

```
router bgp 65100
 bgp router-id 8.8.8.8
 neighbor 203.0.113.1 remote-as 65001
 neighbor 198.51.100.1 remote-as 65001
 !
 address-family ipv4
  neighbor 203.0.113.1 activate
  neighbor 203.0.113.1 default-originate
  neighbor 198.51.100.1 activate
  neighbor 198.51.100.1 default-originate
  network 8.8.8.8 mask 255.255.255.255
 exit-address-family
!
interface Loopback0
 ip address 8.8.8.8 255.255.255.255
```

**Kiểm chứng 6.5 — traffic ĐI RA ưu tiên EDGE1:**

```
EDGE2# show ip bgp 0.0.0.0
BGP routing table entry for 0.0.0.0/0
  Refresh Epoch 1
  65100
    198.51.100.2 from 198.51.100.2 (8.8.8.8)
      Origin IGP, localpref 100, valid, external
  Local
    1.1.1.1 (metric 2) from 1.1.1.1 (1.1.1.1)
      Origin IGP, localpref 200, valid, internal, best     ← ✅ THANG
                             ↑
                  200 > 100 nen duong qua EDGE1 duoc chon
```

**Kiểm chứng 6.6 — traffic ĐI VÀO ưu tiên EDGE1:**

```
ISP# show ip bgp 192.0.2.0
BGP routing table entry for 192.0.2.0/24
  65001                                             ← qua EDGE1: 1 chang
    203.0.113.1 from 203.0.113.1 (1.1.1.1)
      Origin IGP, valid, external, best             ← ✅ THANG
  65001 65001 65001 65001                           ← qua EDGE2: 4 chang
    198.51.100.1 from 198.51.100.1 (2.2.2.2)
      Origin IGP, valid, external
```

> 🔴 **Bốn chỗ quyết định đúng/sai Task 6:**
>
> 1. 🔴 **`next-hop-self` là BẮT BUỘC với iBGP.** Thiếu nó, EDGE2 nhận được default route
>  nhưng next-hop là **IP của ISP (203.0.113.2)** — một địa chỉ EDGE2 **không có đường tới** →
>  tuyến bị đánh dấu **không hợp lệ**, không vào bảng route. 🔴 **Đây là lỗi iBGP kinh điển nhất.**
>
> 2. 🔴 **Peer bằng loopback thì PHẢI có `update-source Loopback0`.**
>  Thiếu nó, gói BGP đi ra mang IP cổng vật lý, đầu kia **không nhận ra** → phiên không lên.
>
> 3. 🔴 **Local Preference đi RA, AS-path prepend đi VÀO** — đừng lẫn.
>  - **LocalPref** chỉ sống **trong AS của bạn** → chỉ ảnh hưởng **đường ra**.
>  - Muốn ảnh hưởng **đường vào**, bạn phải tác động vào thứ **nhà mạng nhìn thấy** →
>  làm AS-path **dài ra** cho xấu đi.
>  - 🔴 **Nhớ: LocalPref CAO thì thắng, AS-path NGẮN thì thắng** — ngược chiều nhau.
>
> 4. 🔴 **`set as-path prepend` phải áp chiều `out`**, không phải `in`.
>  Áp `in` là bạn tự làm xấu đường trong bảng của chính mình — vô nghĩa với yêu cầu.
</details>

**Điểm:** ☐ 6.1 *(1đ)* ☐ 6.2 *(2đ)* ☐ 6.3 *(1đ)* ☐ 6.4 *(2đ)* ☐ 6.5 *(2đ)* ☐ 6.6 *(2đ)*

---

# 🔧 GIAI ĐOẠN 3 — DỊCH VỤ

---

## 🎯 TASK 7 — Ra Internet và mở cổng cho máy chủ (8 điểm)

> **ĐỀ BÀI**
>
> Khách hàng: *"Bây giờ cho nhân viên ra Internet được.*
> 1. *Tôi có dải công cộng **192.0.2.0/24** nhưng **muốn dùng tiết kiệm** —
>  🔴 **hàng trăm máy nội bộ phải chung nhau vài địa chỉ công cộng**.*
> 2. *🔴 **Chỉ VLAN 10 và VLAN 20 được ra Internet.** VLAN 99 là mạng quản trị,
>  **tuyệt đối không cho ra ngoài**.*
> 3. *Tôi có **máy chủ web nội bộ ở 10.1.20.50**. **Khách từ Internet phải vào được**
>  qua địa chỉ **192.0.2.80**, cổng 80."*

**Tiêu chí nghiệm thu:**

| # | Phải đạt | Kiểm bằng |
|:---:|---|---|
| 7.1 | PC ở VLAN 10 ping được `8.8.8.8` | `ping` từ PC1 |
| 7.2 | PC ở VLAN 20 ping được `8.8.8.8` | `ping` từ PC2 |
| 7.3 | 🔴 Thiết bị ở **VLAN 99 KHÔNG ra được** | `ping 8.8.8.8` từ SW1 → **phải hỏng** |
| 7.4 | 🔴 Bảng NAT cho thấy **nhiều máy chung một IP công cộng** | `show ip nat translations` |
| 7.5 | 🔴 Có bản dịch **tĩnh** cho máy chủ web | `show ip nat translations` |
| 7.6 | Từ ISP vào được `192.0.2.80` cổng 80 | `telnet 192.0.2.80 80` từ ISP |

> 📘 **Kiến thức dùng:** [Module-06B §2](Module-06B-NAT-NTP-Multicast.md) ·
> [Module-10 §4](Module-10-Security.md) *(ACL)*

<details><summary>💡 Gợi ý nếu bí</summary>

- "Nhiều máy chung vài địa chỉ" = 🔴 **PAT** — phân biệt nhau bằng **số cổng**.
- 🔴 **Danh sách "ai được NAT" quyết định luôn yêu cầu 2.** Chỉ cần **không cho VLAN 99 vào ACL**
  là nó tự động không ra được — không cần viết ACL chặn riêng.
- 🔴 **Phải khai rõ cổng nào `inside`, cổng nào `outside`.** Quên là NAT **không chạy
  mà không báo lỗi gì cả**.
- Máy chủ cho Internet vào = **NAT tĩnh**; chỉ mở một cổng thì dùng dạng `static tcp`.
</details>

<details><summary>✅ ĐÁP ÁN TASK 7</summary>

**EDGE1** *(EDGE2 làm tương tự, đổi pool cho khỏi trùng)*:

```
! ═══ ① Khai vai tro cong - QUEN LA NAT KHONG CHAY ═══
interface GigabitEthernet0/0
 ip nat outside
!
interface GigabitEthernet0/1.10
 ip nat inside
interface GigabitEthernet0/1.20
 ip nat inside
!
! ⚠️ Gi0/1.99 KHONG khai "ip nat inside"
!    -> VLAN 99 khong ra Internet duoc. Dung yeu cau 2.
!
! ═══ ② Ai duoc phep NAT ═══
ip access-list standard ACL-DUOC-NAT
 permit 10.1.10.0 0.0.0.255
 permit 10.1.20.0 0.0.0.255
 deny   any
!
! ═══ ③ PAT ═══
ip nat pool POOL-CONG-CONG 192.0.2.10 192.0.2.20 netmask 255.255.255.0
ip nat inside source list ACL-DUOC-NAT pool POOL-CONG-CONG overload
!
! ═══ ④ NAT tinh cho may chu web ═══
ip nat inside source static tcp 10.1.20.50 80 192.0.2.80 80
```

**Kiểm chứng 7.4:**

```
EDGE1# show ip nat translations
Pro  Inside global      Inside local     Outside local   Outside global
tcp  192.0.2.10:1024    10.1.10.50:1150  8.8.8.8:80      8.8.8.8:80
tcp  192.0.2.10:1025    10.1.10.51:1150  8.8.8.8:80      8.8.8.8:80
tcp  192.0.2.10:1026    10.1.20.60:2100  8.8.8.8:80      8.8.8.8:80
        ↑                     ↑
  CUNG mot IP cong cong   BA may noi bo khac nhau
  khac nhau o SO CONG     -> dung la PAT

tcp  192.0.2.80:80       10.1.20.50:80    ---             ---
        ↑  ban dich TINH cho may chu web
```

> 🔴 **Ba chỗ quyết định đúng/sai Task 7:**
>
> 1. 🔴 **Thiếu `overload` → thành NAT một-đổi-một.** Pool 11 địa chỉ thì
>  **máy thứ 12 trở đi không ra được Internet** — lỗi chỉ lộ khi đông người dùng.
>
> 2. 🔴 **Quên `ip nat inside` / `ip nat outside`.** NAT **im lặng không làm gì**,
>  `show ip nat translations` rỗng, không có thông báo lỗi nào.
>  🔴 **Luôn kiểm cái này ĐẦU TIÊN khi NAT không chạy.**
>
> 3. 🔴 **ACL của NAT là "ai ĐƯỢC dịch", không phải "ai bị cấm".**
>  Không cần viết ACL chặn VLAN 99 — chỉ cần **không cho nó vào danh sách**.
>
> ⚠️ **Lưu ý thiết kế thật:** môi trường dual-homed mà **cả hai EDGE cùng NAT** sẽ có vấn đề
> khi đường về đi vào con khác. Ngoài đời xử lý bằng **chỉ một con NAT tại một thời điểm**
> *(gắn với trạng thái VRRP)* hoặc **tường lửa có đồng bộ phiên**.
> Lab này đơn giản hoá để tập trung vào cú pháp NAT.
</details>

**Điểm:** ☐ 7.1 *(1đ)* ☐ 7.2 *(1đ)* ☐ 7.3 *(2đ)* ☐ 7.4 *(2đ)* ☐ 7.5 *(1đ)* ☐ 7.6 *(1đ)*

---

## 🎯 TASK 8 — Cấp địa chỉ tự động (6 điểm)

> **ĐỀ BÀI**
>
> Khách hàng: *"Tôi **không muốn IT đi gõ IP cho từng máy**. Máy cắm vào là **tự có mạng**.*
>
> *Nhưng: 🔴 **máy in ở VLAN 10 phải LUÔN giữ đúng 10.1.10.200**, vì phần mềm kế toán trỏ cứng
> vào đó. Và 🔴 **đừng cấp trùng vào dải tôi đã dùng cho thiết bị mạng** (`.1` đến `.20`)."*

**Tiêu chí nghiệm thu:**

| # | Phải đạt | Kiểm bằng |
|:---:|---|---|
| 8.1 | PC VLAN 10 tự nhận IP đúng dải | `show ip dhcp binding` |
| 8.2 | PC VLAN 20 tự nhận IP đúng dải | như trên |
| 8.3 | 🔴 Không máy nào nhận `.1` đến `.20` | `show ip dhcp binding` |
| 8.4 | 🔴 Máy in luôn nhận đúng `10.1.10.200` | `show ip dhcp binding` |
| 8.5 | 🔴 Cổng mặc định PC nhận được là **VIP** `10.1.X.1` | `ipconfig` trên PC |
| 8.6 | PC nhận được DNS | như trên |

> 📘 **Kiến thức dùng:** [Module-P0](Module-P0-Nen-tang-Ready-for-ENCOR.md) ·
> [Module-06B](Module-06B-NAT-NTP-Multicast.md)

<details><summary>💡 Gợi ý nếu bí</summary>

- "Không cấp trùng dải thiết bị mạng" = lệnh **loại trừ** ở mức **toàn cục**,
  🔴 gõ **trước khi** tạo pool.
- "Máy in luôn giữ đúng địa chỉ" = **gán cố định theo định danh máy**.
  🔴 Với thiết bị Ethernet, định danh thường là `01` + địa chỉ MAC.
- 🔴 **Cổng mặc định phải trỏ VIP của VRRP**, không phải IP thật của EDGE1.
</details>

<details><summary>✅ ĐÁP ÁN TASK 8</summary>

**Trên EDGE1:**

```
! ═══ Loai tru TRUOC khi tao pool ═══
ip dhcp excluded-address 10.1.10.1 10.1.10.20
ip dhcp excluded-address 10.1.20.1 10.1.20.20
!
ip dhcp pool VLAN10-KE-TOAN
 network 10.1.10.0 255.255.255.0
 default-router 10.1.10.1              ! ← VIP cua VRRP, KHONG phai .2
 dns-server 8.8.8.8
 domain-name vlt.local
 lease 7
!
ip dhcp pool VLAN20-KY-THUAT
 network 10.1.20.0 255.255.255.0
 default-router 10.1.20.1
 dns-server 8.8.8.8
 lease 7
!
! ═══ May in - dia chi co dinh ═══
ip dhcp pool MAY-IN-KE-TOAN
 host 10.1.10.200 255.255.255.0
 client-identifier 0100.5079.6668.01   ! 01 + MAC may in
 default-router 10.1.10.1
 dns-server 8.8.8.8
```

**Kiểm chứng:**

```
EDGE1# show ip dhcp binding
IP address     Client-ID/Hardware address  Lease expiration   Type
10.1.10.21     0100.5079.6668.aa           Sep 17 2026 10:00  Automatic
10.1.10.200    0100.5079.6668.01           Infinite           Manual
     ↑                                                          ↑
 bat dau .21 vi .1-.20 da loai tru                    gan tay = co dinh
```

> 🔴 **Hai chỗ quyết định đúng/sai Task 8:**
>
> 1. 🔴 **`default-router` PHẢI là VIP `10.1.10.1`.**
>  Trỏ `10.1.10.2` (IP thật EDGE1) thì khi EDGE1 chết **PC mất mạng** —
>  tức là bạn vừa **phá hỏng toàn bộ Task 4** mà không hề biết.
>  **Đây đúng kiểu lỗi ngoài đời: làm đúng từng phần nhưng ghép lại thì sai.**
>
> 2. 🔴 **`ip dhcp excluded-address` là lệnh TOÀN CỤC**, không nằm trong pool.
>  Gõ trong pool là sai cú pháp.
</details>

**Điểm:** ☐ 8.1 *(1đ)* ☐ 8.2 *(1đ)* ☐ 8.3 *(1đ)* ☐ 8.4 *(1đ)* ☐ 8.5 *(1đ)* ☐ 8.6 *(1đ)*

---

# 🔒 GIAI ĐOẠN 4 — BẢO MẬT

---

## 🎯 TASK 9 — Siết quyền truy cập thiết bị (7 điểm)

> **ĐỀ BÀI**
>
> Khách hàng: *"Tôi vừa bị kiểm toán an ninh và họ chấm **trượt**. Họ yêu cầu:*
> 1. *🔴 **Chỉ máy trong mạng quản trị (VLAN 99) được đăng nhập thiết bị.**
>  Máy nhân viên thường **không được chạm tới**.*
> 2. *🔴 Ai **thử sai mật khẩu 3 lần** thì **bị chặn một lúc** — chống dò mật khẩu.*
> 3. *Tôi muốn biết **ai đăng nhập, lúc nào, gõ lệnh gì**.*
> 4. *Nhân viên trực ca đêm **chỉ được xem, không được sửa**."*
>
> 🔴 **Cẩn thận:** làm sai yêu cầu 1 là bạn **tự khoá mình ra khỏi thiết bị**.
> **Giữ sẵn một phiên console đang mở.**

**Tiêu chí nghiệm thu:**

| # | Phải đạt | Kiểm bằng |
|:---:|---|---|
| 9.1 | 🔴 SSH từ VLAN 99 **thành công** | `ssh` từ SW1 |
| 9.2 | 🔴 SSH từ VLAN 10 **bị từ chối** | `ssh` từ PC1 → phải hỏng |
| 9.3 | Sai mật khẩu 3 lần → bị chặn | Thử sai liên tục |
| 9.4 | `show login` cho thấy cơ chế đang bật | `show login` |
| 9.5 | Có ghi nhật ký lệnh đã gõ | `show run \| include aaa account` |
| 9.6 | Tài khoản "chỉ xem" **không vào được config mode** | Đăng nhập thử |

> 📘 **Kiến thức dùng:** [Module-10 §3, §4](Module-10-Security.md)

<details><summary>💡 Gợi ý nếu bí</summary>

- Yêu cầu 1 = ACL áp vào `line vty` — 🔴 **dùng từ khoá riêng của vty, không phải lệnh áp lên interface.**
- 🔴 **Luôn `permit` mạng quản trị TRƯỚC**, và test bằng **một phiên SSH khác đang mở**
  trước khi đóng phiên hiện tại.
- Yêu cầu 2 có lệnh chuyên dụng dạng "chặn X giây nếu sai Y lần trong Z giây".
- Yêu cầu 4 = **mức đặc quyền**: 15 là toàn quyền, 1 là chỉ xem.
</details>

<details><summary>✅ ĐÁP ÁN TASK 9</summary>

**Trên mọi thiết bị:**

```
! ═══ ① Chi VLAN 99 duoc dang nhap ═══
ip access-list standard ACL-QUAN-TRI
 permit 10.1.99.0 0.0.0.255
 deny   any log
!
line vty 0 4
 access-class ACL-QUAN-TRI in       ! ← "access-class", KHONG phai "ip access-group"
 transport input ssh
 exec-timeout 10 0
 login local
!
! ═══ ② Chong do mat khau ═══
login block-for 120 attempts 3 within 60
login quiet-mode access-class ACL-QUAN-TRI
login on-failure log
login on-success log
!
! ═══ ③ Ghi nhat ky ai lam gi ═══
aaa accounting exec default start-stop group tacacs+
aaa accounting commands 15 default start-stop group tacacs+
!
! ═══ ④ Tai khoan chi xem ═══
username truc-dem privilege 1  algorithm-type scrypt secret MatKhauTrucDem
username admin    privilege 15 algorithm-type scrypt secret MatKhauRatDaiCuaVLT
```

**Kiểm chứng:**

```
EDGE1# show login
  Router enabled to watch for login Attacks.
  If more than 3 login failures occur in 60 seconds or less,
  logins will be disabled for 120 seconds.
  Router presently in Normal-Mode.

EDGE1# show access-lists ACL-QUAN-TRI
Standard IP access list ACL-QUAN-TRI
    10 permit 10.1.99.0, wildcard bits 0.0.0.255 (12 matches)
    20 deny   any log (3 matches)         ← 3 lan bi chan tu VLAN khac
```

> 🔴 **Ba chỗ quyết định đúng/sai Task 9:**
>
> 1. 🔴 **Trên `line vty` phải dùng `access-class`, KHÔNG phải `ip access-group`.**
>  Đây là chỗ người mới nhầm nhiều nhất vì `ip access-group` là lệnh quen ở interface.
>
> 2. 🔴 **`login quiet-mode access-class` là thứ cứu bạn.**
>  Khi thiết bị vào "chế độ im lặng" sau khi bị dò mật khẩu, nó chặn **TẤT CẢ** — kể cả bạn.
>  Dòng này chừa ra mạng quản trị.
>  🔴 **Thiếu nó, kẻ tấn công có thể CỐ TÌNH sai mật khẩu để khoá luôn quản trị viên.**
>
> 3. ⚠️ **Lab không có server TACACS+**, nên `aaa accounting` chỉ cấu hình cho đúng hình thức.
>  Ngoài đời thiếu server mà không có phương án dự phòng thì thiết bị sẽ **treo khi
>  server không trả lời** — xem [Module-10](Module-10-Security.md) phần dự phòng AAA.
</details>

**Điểm:** ☐ 9.1 *(1đ)* ☐ 9.2 *(2đ)* ☐ 9.3 *(1đ)* ☐ 9.4 *(1đ)* ☐ 9.5 *(1đ)* ☐ 9.6 *(1đ)*

---

## 🎯 TASK 10 — Bảo vệ bộ não của router (6 điểm)

> **ĐỀ BÀI**
>
> Khách hàng: *"Tuần trước **CPU của EDGE1 lên 100%** và cả công ty chậm như rùa.
> Kỹ sư cũ bảo có ai đó **ping dồn dập vào router**.*
>
> *Tôi muốn: **dù ai bắn bao nhiêu gói vào router, bộ não của nó vẫn phải sống**
> để còn chạy định tuyến."*
>
> 🔴 **Ràng buộc:** *"Nhưng **tuyệt đối đừng bóp nhầm giao thức định tuyến** —
> làm sập OSPF/BGP thì còn tệ hơn."*

**Tiêu chí nghiệm thu:**

| # | Phải đạt | Kiểm bằng |
|:---:|---|---|
| 10.1 | Có phân loại lưu lượng lên CPU | `show policy-map control-plane` |
| 10.2 | 🔴 ICMP **bị giới hạn tốc độ** | `show policy-map control-plane` |
| 10.3 | 🔴 Định tuyến **CHỈ ĐẾM, KHÔNG bóp** | xem `exceed-action` |
| 10.4 | Chính sách **đã áp vào control-plane** | `show run \| section control-plane` |
| 10.5 | 🔴 Sau khi áp, OSPF/BGP **vẫn sống** | `show ip ospf nei` · `show ip bgp sum` |
| 10.6 | Ping dồn dập → số gói **drop** tăng | `show policy-map control-plane` |

> 📘 **Kiến thức dùng:** [Module-10 §7](Module-10-Security.md) *(CoPP)*

<details><summary>💡 Gợi ý nếu bí</summary>

- Cấu trúc luôn **ba tầng**: phân loại *(class-map)* → hành động *(policy-map)* → áp *(service-policy)*.
- 🔴 **Nơi áp KHÔNG phải interface** mà là một chỗ đặc biệt đại diện cho CPU.
- 🔴 **Nguyên tắc vàng làm CoPP lần đầu: bắt đầu bằng CHỈ ĐẾM, chưa bóp gì.**
  Đề nói *"đừng bóp nhầm định tuyến"* chính là ý này.
- Lệnh `police` có hai vế: khi **trong ngưỡng** *(conform)* và khi **vượt ngưỡng** *(exceed)*.
</details>

<details><summary>✅ ĐÁP ÁN TASK 10</summary>

**Trên EDGE1 và EDGE2:**

```
! ═══ ① PHAN LOAI ═══
ip access-list extended ACL-COPP-ROUTING
 permit ospf any any
 permit tcp any any eq bgp
 permit tcp any eq bgp any
!
ip access-list extended ACL-COPP-QUAN-TRI
 permit tcp 10.1.99.0 0.0.0.255 any eq 22
!
ip access-list extended ACL-COPP-ICMP
 permit icmp any any
!
class-map match-all CM-ROUTING
 match access-group name ACL-COPP-ROUTING
class-map match-all CM-QUAN-TRI
 match access-group name ACL-COPP-QUAN-TRI
class-map match-all CM-ICMP
 match access-group name ACL-COPP-ICMP
!
! ═══ ② HANH DONG ═══
policy-map PM-COPP
 class CM-ROUTING
  police 500000 conform-action transmit exceed-action transmit
!                                              ↑ CHI DEM - KHONG bao gio bop
 class CM-QUAN-TRI
  police 200000 conform-action transmit exceed-action transmit
 class CM-ICMP
  police 50000 conform-action transmit exceed-action drop
!                                              ↑ ICMP thi BOP
 class class-default
  police 100000 conform-action transmit exceed-action transmit
!
! ═══ ③ AP VAO CPU ═══
control-plane
 service-policy input PM-COPP
```

**Kiểm chứng 10.6 — ping dồn dập từ ISP rồi xem:**

```
EDGE1# show policy-map control-plane
 Control Plane

  Class-map: CM-ICMP (match-all)
    18452 packets, 1845200 bytes
    police:
      conformed 2310 packets; action: transmit
      exceeded 16142 packets; action: drop          ← dang bao ve CPU
                    ↑ so goi bi vut tang len

  Class-map: CM-ROUTING (match-all)
    4210 packets, 421000 bytes
    police:
      conformed 4210 packets; action: transmit
      exceeded 0 packets; action: transmit          ← KHONG bao gio bop
```

> 🔴 **Ba chỗ quyết định đúng/sai Task 10:**
>
> 1. 🔴 **Áp vào `control-plane`, KHÔNG phải vào interface.**
>  Áp nhầm vào interface là bạn đang bóp traffic **đi XUYÊN QUA** router,
>  không phải traffic **đi LÊN CPU** — sai hoàn toàn mục đích,
>  và còn làm chậm mạng người dùng.
>
> 2. 🔴 **Lớp định tuyến phải để `exceed-action transmit` (chỉ đếm).**
>  Đặt `drop` ở đây là tự tay làm **rớt neighbor OSPF/BGP** lúc mạng bận —
>  đúng cái khách hàng dặn tránh. **Trượt cả 10.3 lẫn 10.5.**
>
> 3. 🔴 **Luôn có `class-default`.** Thiếu nó thì mọi thứ chưa phân loại
>  đi lên CPU **không giới hạn** — thủng lỗ lớn nhất của CoPP.
>
> ⚠️ **Nguyên tắc triển khai thật:** lần đầu làm CoPP trên hệ thống đang chạy,
> **đặt TẤT CẢ các lớp ở `transmit/transmit` (chỉ đếm)**, chạy 1–2 tuần, xem số liệu thật,
> rồi mới siết từng lớp. **Siết ngay bằng số đoán là cách nhanh nhất để tự gây sự cố.**
</details>

**Điểm:** ☐ 10.1 *(1đ)* ☐ 10.2 *(1đ)* ☐ 10.3 *(2đ)* ☐ 10.4 *(1đ)* ☐ 10.5 *(1đ)* ☐ 10.6 *(1đ)*

---

# 📡 GIAI ĐOẠN 5 — GIÁM SÁT & TỰ ĐỘNG HOÁ

---

## 🎯 TASK 11 — Nhật ký tập trung (6 điểm)

> **ĐỀ BÀI**
>
> Khách hàng: *"Lần trước mạng sập lúc 2 giờ sáng. Sáng ra tôi hỏi *'lúc đó chuyện gì xảy ra?'*
> thì **không ai trả lời được** — log nằm rải rác trên từng thiết bị, mà router khởi động lại
> là **mất sạch**.*
>
> *Tôi muốn:*
> 1. *🔴 **Log của MỌI thiết bị gửi hết về một máy chủ** ở `10.1.99.100`.*
> 2. *🔴 **Mỗi dòng log phải có ngày giờ CHÍNH XÁC ĐẾN MILI GIÂY**, và phải là **giờ chuẩn**,
>  để tôi ghép được sự kiện giữa các thiết bị.*
> 3. *Chỉ gửi những thứ **đáng quan tâm** — đừng làm ngập máy chủ bằng log vặt.*
> 4. *Nhưng trên chính thiết bị vẫn **giữ lại log chi tiết hơn** để soi khi cần."*

**Tiêu chí nghiệm thu:**

| # | Phải đạt | Kiểm bằng |
|:---:|---|---|
| 11.1 | Có khai máy chủ syslog | `show logging` |
| 11.2 | 🔴 Dòng log có **ngày giờ + mili giây** | `show logging` — xem dòng thật |
| 11.3 | 🔴 Đồng hồ **đồng bộ NTP**, không phải giờ tự đặt | `show ntp status` |
| 11.4 | 🔴 Mức gửi đi **chặt hơn** mức lưu tại chỗ | `show logging` |
| 11.5 | Bộ đệm nội bộ đủ lớn | `show logging` |
| 11.6 | Gây một sự kiện → thấy nó trong log | `shutdown` một cổng rồi xem |

> 📘 **Kiến thức dùng:** [Module-11 §3, §4](Module-11-Network-Assurance.md) *(NTP + Syslog)*

<details><summary>💡 Gợi ý nếu bí</summary>

- 🔴 **Mốc thời gian là điều kiện TIÊN QUYẾT của cả module giám sát.**
  Log không có giờ đúng thì **vô giá trị** — bạn không ghép được sự kiện giữa 6 thiết bị.
- Mặc định IOS chỉ đóng dấu `uptime` *(vd `00:04:12`)*, **không phải ngày giờ thật**.
  Phải đổi sang dạng ngày giờ và **thêm mili giây**.
- 🔴 **Mức severity: số càng NHỎ càng nghiêm trọng** *(0 = emergency, 7 = debug)*.
  "Gửi đi chặt hơn, giữ tại chỗ rộng hơn" nghĩa là **số ở `logging trap` NHỎ hơn số ở `logging buffered`**.
</details>

<details><summary>✅ ĐÁP ÁN TASK 11</summary>

**Trên mọi thiết bị:**

```
! ═══ ① Dong dau thoi gian - LAM DAU TIEN ═══
service timestamps log datetime msec localtime show-timezone
service timestamps debug datetime msec localtime show-timezone
!
clock timezone ICT 7
ntp server 10.1.99.2                  ! EDGE1 lam NTP master (Task 1)
!
! ═══ ② Gui ve may chu tap trung ═══
logging host 10.1.99.100
logging trap warnings                 ! muc 4 - CHI gui thu dang quan tam
logging source-interface Vlan99        ! hoac Gi0/1.99 tren router
!
! ═══ ③ Giu chi tiet hon tai cho ═══
logging buffered 64000 informational  ! muc 6 - rong hon muc gui di
!
no logging console                    ! tranh log do ra console lam nghen
```

**Kiểm chứng 11.2 và 11.4:**

```
EDGE1# show logging
Trap logging: level warnings, 142 message lines logged
                     ↑ muc 4
Buffer logging:  level informational, 891 messages logged
                       ↑ muc 6 - RONG HON ✅

Log Buffer (64000 bytes):
Sep 16 2026 14:22:31.482 ICT: %LINK-3-UPDOWN: Interface Gi0/1, changed state to down
     ↑ ngay gio day du        ↑ mili giay    ↑ mui gio ✅
```

> 🔴 **Ba chỗ quyết định đúng/sai Task 11:**
>
> 1. 🔴 **Không có `service timestamps ... datetime msec` thì log chỉ có `uptime`.**
>  Hai thiết bị khởi động lệch nhau 3 ngày sẽ cho hai mốc uptime **không thể ghép được**.
>  **Đây là lý do yêu cầu 2 của khách hàng tồn tại.**
>
> 2. 🔴 **NTP phải chạy THẬT, không chỉ `clock set`.**
>  Đặt giờ tay thì mỗi thiết bị trôi một kiểu, vài ngày là lệch nhau vài giây —
>  đủ để bạn đọc sai thứ tự nhân quả của một sự cố.
>  Kiểm bằng `show ntp status` phải thấy **`Clock is synchronized`**.
>
> 3. 🔴 **`logging trap` (gửi đi) phải CHẶT hơn `logging buffered` (giữ tại chỗ).**
>  Đặt `logging trap debugging` là bạn **tự làm ngập máy chủ syslog** và
>  làm nghẽn đường mạng quản trị. **Nhớ: số nhỏ = chặt.**
</details>

**Điểm:** ☐ 11.1 *(1đ)* ☐ 11.2 *(2đ)* ☐ 11.3 *(1đ)* ☐ 11.4 *(1đ)* ☐ 11.5 *(0,5đ)* ☐ 11.6 *(0,5đ)*

---

## 🎯 TASK 12 — Nhìn thấy ai đang dùng băng thông (7 điểm)

> **ĐỀ BÀI**
>
> Khách hàng: *"Cứ đến 3 giờ chiều là mạng chậm. Tôi hỏi thì ai cũng bảo 'không phải em'.*
>
> 1. *🔴 **Tôi muốn biết CHÍNH XÁC máy nào, nói chuyện với đâu, bao nhiêu byte.**
>  Không phải đồ thị tổng, mà là **danh sách từng luồng**.*
> 2. *Và khi có sự cố lạ, **kỹ sư phải sao chép được toàn bộ gói tin của một cổng**
>  sang một máy có Wireshark để mổ xẻ."*

**Tiêu chí nghiệm thu:**

| # | Phải đạt | Kiểm bằng |
|:---:|---|---|
| 12.1 | Có **flow record** khai đủ khoá nhận dạng luồng | `show flow record` |
| 12.2 | Có **flow exporter** trỏ về máy thu thập | `show flow exporter` |
| 12.3 | Có **flow monitor** ghép record + exporter | `show flow monitor` |
| 12.4 | 🔴 Monitor **đã áp lên interface** | `show run \| include flow monitor` |
| 12.5 | 🔴 Sinh traffic → **cache có dữ liệu thật** | `show flow monitor FM-IPV4 cache` |
| 12.6 | SPAN sao chép được cổng sang cổng giám sát | `show monitor session 1` |

> 📘 **Kiến thức dùng:** [Module-11 §6, §7](Module-11-Network-Assurance.md) *(NetFlow · SPAN)*

<details><summary>💡 Gợi ý nếu bí</summary>

- 🔴 **Flexible NetFlow có BỐN thành phần**, phải đủ cả bốn mới chạy:
  **record** *(ghi gì)* → **exporter** *(gửi đi đâu)* → **monitor** *(ghép hai cái trên)* →
  **áp lên interface** *(chỗ người mới hay quên nhất)*.
- 🔴 **Phân biệt `match` và `collect`:**
  `match` = **khoá** định nghĩa thế nào là một luồng riêng biệt.
  `collect` = **số liệu** đếm thêm cho luồng đó.
  Đặt nhầm `collect` chỗ `match` là gộp nhầm các luồng khác nhau làm một.
- SPAN: cổng đích sẽ **"câm"** — chỉ đổ traffic sao chép ra, không dùng để nối mạng bình thường.
</details>

<details><summary>✅ ĐÁP ÁN TASK 12</summary>

**NetFlow trên EDGE1:**

```
! ═══ ① RECORD - ghi gi ═══
flow record FR-IPV4
 match ipv4 source address
 match ipv4 destination address
 match ipv4 protocol
 match transport source-port
 match transport destination-port
 match ipv4 tos
 collect counter bytes
 collect counter packets
 collect interface output
 collect timestamp sys-uptime first
 collect timestamp sys-uptime last
!
! ═══ ② EXPORTER - gui di dau ═══
flow exporter FE-COLLECTOR
 destination 10.1.99.100
 source GigabitEthernet0/1.99      ! router dùng sub-interface, KHÔNG có Vlan99
 transport udp 2055
 template data timeout 60
!
! ═══ ③ MONITOR - ghep lai ═══
flow monitor FM-IPV4
 record FR-IPV4
 exporter FE-COLLECTOR
 cache timeout active 60
 cache timeout inactive 15
!
! ═══ ④ AP LEN INTERFACE - CHO HAY QUEN NHAT ═══
interface GigabitEthernet0/1.10
 ip flow monitor FM-IPV4 input
 ip flow monitor FM-IPV4 output
```

**SPAN trên SW1:**

```
monitor session 1 source interface GigabitEthernet0/1 both
monitor session 1 destination interface GigabitEthernet0/3 encapsulation replicate
```

**Kiểm chứng 12.5 — sinh traffic rồi xem cache:**

```
EDGE1# show flow monitor FM-IPV4 cache
IPV4 SRC ADDR  IPV4 DST ADDR  TRNS SRC  TRNS DST  PROT  bytes  pkts
=============  =============  ========  ========  ====  =====  ====
10.1.10.50     8.8.8.8            1150        80     6  48210   322
10.1.10.51     93.184.216.34      1044       443     6 128940   890
10.1.20.60     8.8.8.8            2100        80     6   9120    61
                                                          ↑
                        DAY la thu khach hang muon: tung luong, ai an bao nhieu
```

> 🔴 **Ba chỗ quyết định đúng/sai Task 12:**
>
> 1. 🔴 **Quên áp `ip flow monitor` lên interface.**
>  Ba thành phần đầu cấu hình đẹp đẽ, `show flow monitor` hiện đầy đủ,
>  nhưng **cache LUÔN RỖNG** vì chưa có cổng nào đẩy dữ liệu vào.
>  🔴 **Đây là lỗi số 1 của Flexible NetFlow.**
>
> 2. 🔴 **Thiếu `match` quan trọng → gộp nhầm luồng.**
>  Nếu không `match transport source-port`, mọi phiên từ cùng một máy tới cùng một đích
>  bị gộp thành **một dòng duy nhất** — mất đúng cái chi tiết mà khách hàng cần.
>
> 3. 🔴 **Cổng đích của SPAN trở thành "câm".**
>  Chọn nhầm một cổng đang có người dùng làm cổng đích là **bạn vừa cắt mạng của họ**.
>  Luôn dùng một cổng trống.
>
> ⚠️ **Lab này không có máy thu thập NetFlow thật**, nên `show flow exporter statistics`
> sẽ báo gửi thất bại — **bình thường**. Nghiệm thu dựa vào **cache có dữ liệu** (12.5).
</details>

**Điểm:** ☐ 12.1 *(1đ)* ☐ 12.2 *(1đ)* ☐ 12.3 *(1đ)* ☐ 12.4 *(2đ)* ☐ 12.5 *(1đ)* ☐ 12.6 *(1đ)*

---

## 🎯 TASK 13 — Thiết bị tự xử lý lúc 3 giờ sáng (7 điểm)

> **ĐỀ BÀI**
>
> Khách hàng: *"Ban đêm **không có ai trực**. Tôi muốn thiết bị **tự lo** ba việc:*
>
> 1. *🔴 Khi **đường ISP chính chết**, nó phải **tự ghi lại hiện trạng ngay lúc đó** —
>  vì sáng hôm sau mạng đã tự lên lại thì **không còn dấu vết gì để điều tra**.*
> 2. *🔴 Mỗi khi có người **lưu cấu hình**, tự **sao lưu ra file** — để còn biết
>  trước đó cấu hình thế nào.*
> 3. *Khi có **cổng bị tắt do vi phạm bảo mật** (Task 3), tự ghi một dòng cảnh báo rõ ràng."*

**Tiêu chí nghiệm thu:**

| # | Phải đạt | Kiểm bằng |
|:---:|---|---|
| 13.1 | 3 applet đã đăng ký | `show event manager policy registered` |
| 13.2 | 🔴 Shut cổng WAN EDGE1 → applet **tự chạy** | `shutdown` Gi0/0 rồi xem log |
| 13.3 | 🔴 `write memory` → **file backup xuất hiện** | `dir flash:` |
| 13.4 | Gây err-disable → applet cảnh báo chạy | Vi phạm port-security |
| 13.5 | 🔴 Các `action` chạy **đúng thứ tự** | Đọc thứ tự dòng log |
| 13.6 | `show event manager statistics policy` có số đếm | như trên |

> 📘 **Kiến thức dùng:** [Module-12 §8](Module-12-Automation-va-Programmability.md) *(EEM)*

<details><summary>💡 Gợi ý nếu bí</summary>

- 🔴 **Nhãn `action` sắp theo CHUỖI, không theo SỐ** — `action 10` chạy **trước** `action 2`.
  Luôn viết `1.0`, `2.0`, `3.0`.
- 🔴 **Phiên CLI của EEM bắt đầu ở chế độ user EXEC** → phải `enable` trước lệnh privileged.
- Việc 1 có hai cách bắt sự kiện: bắt **dòng syslog** khi cổng down,
  hoặc bắt **trạng thái `track`** đã tạo ở Task 4. Cách thứ hai đúng ý đồ hơn.
- Muốn test nhanh mà không phải chờ sự kiện thật → tạm đổi sang `event none` rồi
  `event manager run <tên>`.
</details>

<details><summary>✅ ĐÁP ÁN TASK 13</summary>

**Trên EDGE1:**

```
! ═══ ① Duong ISP chet -> chup lai hien trang ═══
event manager applet ISP-CHET
 event track 1 state down
 action 1.0 syslog msg "EEM: DUONG ISP1 DA CHET - dang chup hien trang"
 action 2.0 cli command "enable"
 action 3.0 cli command "show ip interface brief | redirect flash:suco-int.txt"
 action 4.0 cli command "show ip bgp summary | append flash:suco-int.txt"
 action 5.0 cli command "show vrrp brief | append flash:suco-int.txt"
 action 6.0 syslog msg "EEM: da luu hien trang ra flash:suco-int.txt"
!
! ═══ ② Tu sao luu khi co nguoi ghi config ═══
event manager applet BACKUP-KHI-LUU
 event cli pattern "write mem.*" sync no skip no
 action 1.0 syslog msg "EEM: co nguoi vua luu config"
 action 2.0 cli command "enable"
 action 3.0 cli command "show running-config | redirect flash:backup-config.txt"
 action 4.0 syslog msg "EEM: da sao luu ra flash:backup-config.txt"
!
! ═══ ③ Canh bao khi co cong bi tat do vi pham ═══
event manager applet CANH-BAO-ERRDISABLE
 event syslog pattern "err-disable"
 action 1.0 syslog msg "EEM: CANH BAO - co cong vua bi tat do vi pham bao mat"
 action 2.0 cli command "enable"
 action 3.0 cli command "show interfaces status err-disabled"
```

*(Applet ③ nên đặt trên **SW1 và SW2**, vì port-security nằm ở đó)*

**Kiểm chứng 13.2 — shut cổng WAN của EDGE1:**

```
EDGE1(config)# interface GigabitEthernet0/0
EDGE1(config-if)# shutdown

! Sau ~15 giay (track co delay down 3):
%TRACK-6-STATE: 1 ip sla 1 reachability Up -> Down
%HA_EM-6-LOG: ISP-CHET: EEM: DUONG ISP1 DA CHET - dang chup hien trang
%HA_EM-6-LOG: ISP-CHET: EEM: da luu hien trang ra flash:suco-int.txt

EDGE1# dir flash:
    -rw-        1842   Sep 16 2026 03:14:22   suco-int.txt     ← co that
```

> 🔴 **Ba chỗ quyết định đúng/sai Task 13:**
>
> 1. 🔴 **`event track 1 state down` đúng ý đồ hơn `event syslog`.**
>  Cổng có thể vẫn `up` mà nhà mạng đã chết bên trong — lúc đó **không có dòng syslog nào**
>  về link down cả, nên applet bắt syslog sẽ **không bao giờ chạy**.
>  Còn `track` gắn với **IP SLA ping thật** nên nó bắt được cả trường hợp đó.
>  🔴 **Đây chính là chỗ Task 4 và Task 13 nối vào nhau.**
>
> 2. 🔴 **`redirect` ghi đè, `append` ghi nối.**
>  Dùng `redirect` cho **cả 3 lệnh** thì file cuối chỉ còn kết quả của lệnh cuối —
>  mất hai lệnh đầu. Đúng phải là **lệnh đầu `redirect`, các lệnh sau `append`**.
>
> 3. 🔴 **Thiếu `action 2.0 cli command "enable"`** thì các lệnh `show` phía sau
>  **thất bại im lặng**, file sinh ra rỗng — và bạn tưởng applet đã chạy đúng vì
>  dòng syslog đầu tiên vẫn hiện ra.
</details>

**Điểm:** ☐ 13.1 *(1đ)* ☐ 13.2 *(2đ)* ☐ 13.3 *(1đ)* ☐ 13.4 *(1đ)* ☐ 13.5 *(1đ)* ☐ 13.6 *(1đ)*

---

# 🏁 NGHIỆM THU CUỐI — BÀN GIAO DỰ ÁN

> 🔴 **Đây mới là phần quan trọng nhất.**
>
> 13 Task ở trên kiểm tra **từng phần riêng lẻ**. Phần này kiểm tra thứ khác hẳn:
> 🔴 **hệ thống GHÉP LẠI có chạy không.**
>
> ⭐ **Ngoài đời, lỗi đắt nhất không phải "cấu hình sai một lệnh" —
> mà là "mỗi phần đều đúng, nhưng ghép lại thì hỏng".**
> Task 8 đã cho bạn nếm thử điều đó *(DHCP trỏ nhầm cổng mặc định làm hỏng Task 4)*.

---

## A. Kiểm tra thông suốt — 6 đường phải chạy

> Chạy lần lượt, **ghi kết quả vào bảng**. Tất cả phải ✅ mới sang phần B.

| # | Từ | Tới | Kỳ vọng | ☐ |
|:---:|---|---|---|:---:|
| A1 | PC1 (VLAN 10) | `10.1.10.1` *(VIP)* | Thông | ☐ |
| A2 | PC1 (VLAN 10) | PC2 (VLAN 20) | Thông *(định tuyến liên VLAN)* | ☐ |
| A3 | PC1 | `10.2.10.1` *(LAN chi nhánh)* | Thông | ☐ |
| A4 | PC1 | `8.8.8.8` *(Internet)* | Thông *(qua NAT)* | ☐ |
| A5 | BRANCH | `10.1.99.11` *(SVI của SW1)* | Thông | ☐ |
| A6 | SW1 (VLAN 99) | `8.8.8.8` | 🔴 **PHẢI HỎNG** *(Task 7 yêu cầu 2)* | ☐ |

> 🔴 **A6 hỏng mới là ĐÚNG.** Nếu nó thông thì bạn đã để lọt VLAN quản trị ra Internet —
> **trượt yêu cầu bảo mật của khách hàng.**

---

## B. Diễn tập sự cố — 5 kịch bản

> 🔴 **Đây là thứ phân biệt một hệ thống "cấu hình xong" với một hệ thống "dùng được".**
>
> **Cách làm:** mở một cửa sổ **ping liên tục** từ PC1 tới `8.8.8.8`, rồi gây sự cố,
> **đếm số gói mất**.

### Diễn tập 1 — Đứt một sợi trong EtherChannel

| | |
|---|---|
| **Làm gì** | Trong EVE-NG, xoá liên kết `SW1 Gi0/2 ↔ SW2 Gi0/2` |
| 🔴 **Kỳ vọng** | **Mất tối đa 1 gói.** `Po1` còn `(SU)` với 1 cổng `(P)` |
| **Kiểm** | `show etherchannel summary` |
| **Nếu hỏng** | Bó chưa lên đúng — quay lại **Task 2**, xem có `(I)` không |
| **Đạt?** | ☐ |

### Diễn tập 2 — Chết hẳn một router biên

| | |
|---|---|
| **Làm gì** | Tắt hẳn node **EDGE1** trong EVE-NG |
| 🔴 **Kỳ vọng** | **Mất < 10 gói**, rồi ping thông lại qua EDGE2 |
| **Kiểm** | `show vrrp brief` trên EDGE2 → phải thành **Master** |
| **Nếu hỏng** | Kiểm **Task 4** *(VRRP)* và **Task 8** *(cổng mặc định có trỏ VIP không?)* |
| **Đạt?** | ☐ |

### 🔴 Diễn tập 3 — Đường Internet chết nhưng router vẫn sống *(khó nhất)*

| | |
|---|---|
| **Làm gì** | `shutdown` cổng `Gi0/0` của **EDGE1** *(router vẫn chạy, chỉ đường ra chết)* |
| 🔴 **Kỳ vọng** | Sau ~15 giây: VRRP **nhường quyền cho EDGE2**, ping thông lại |
| **Kiểm** | `show track 1` → `Down` · `show vrrp brief` → EDGE1 thành `Backup` |
| **Nếu hỏng** | 🔴 **Đây là bài lộ ra 2 lỗi kinh điển:**<br>① thiếu `source-interface` trong IP SLA → track không bao giờ Down<br>② `decrement` quá nhỏ, không kéo priority xuống dưới đối thủ |
| **Đạt?** | ☐ |

> ⭐ **Vì sao Diễn tập 3 khó hơn Diễn tập 2:**
> 🔴 **Router chết thì VRRP tự phát hiện — dễ.**
> 🔴 **Router SỐNG mà đường ra chết thì VRRP KHÔNG biết gì cả** — nó vẫn thấy mình khoẻ,
> vẫn làm Master, và **hút toàn bộ traffic vào một cái hố đen.**
> ⭐ **Đó chính là lý do tồn tại của IP SLA + tracking.**

### Diễn tập 4 — Nhân viên cắm switch lạ

| | |
|---|---|
| **Làm gì** | Nối thêm một switch vào cổng `Gi0/1` của SW1 |
| 🔴 **Kỳ vọng** | Cổng vào `err-disabled` **ngay lập tức** |
| **Kiểm** | `show interfaces status err-disabled` · và **applet EEM Task 13 phải ghi log** |
| **Nếu hỏng** | Chưa bật BPDU Guard — quay lại **Task 3** |
| **Đạt?** | ☐ |

### Diễn tập 5 — Đứt liên kết giữa hai router biên

| | |
|---|---|
| **Làm gì** | Xoá liên kết `EDGE1 Gi0/2 ↔ EDGE2 Gi0/2` |
| 🔴 **Kỳ vọng** | 🔴 **Phiên iBGP KHÔNG được chết** — vì peer bằng loopback, OSPF còn đường vòng |
| **Kiểm** | `show ip bgp summary` → vẫn `Established` |
| **Nếu hỏng** | Bạn đã peer bằng **IP cổng vật lý** thay vì loopback — quay lại **Task 6** |
| **Đạt?** | ☐ |

> 🔴 **Lưu ý về Diễn tập 5:** trong sơ đồ này, đứt `EDGE1–EDGE2` thì đường vòng duy nhất
> là **qua các VLAN** *(cả hai EDGE đều có chân trên VLAN 10/20/99)*.
> ⭐ Nếu OSPF của bạn có quảng bá các mạng VLAN thì iBGP sống sót được.
> **Đây là ví dụ rất thật về việc "dự phòng" chỉ có giá trị khi TOÀN BỘ đường đi còn nguyên.**

---

## C. Bảng điểm tổng

| Task | Nội dung | Điểm tối đa | Bạn đạt |
|:---:|---|:---:|:---:|
| 1 | Truy cập quản trị + NTP | 7 | ___ |
| 2 | VLAN + EtherChannel | 7 | ___ |
| 3 | STP + bảo vệ cổng | 7 | ___ |
| 4 | 🔴 FHRP + tracking | 12 | ___ |
| 5 | OSPF nhiều vùng | 10 | ___ |
| 6 | 🔴 BGP + điều hướng | 10 | ___ |
| 7 | NAT | 8 | ___ |
| 8 | DHCP | 6 | ___ |
| 9 | Siết truy cập | 7 | ___ |
| 10 | CoPP | 6 | ___ |
| 11 | Syslog + NTP | 6 | ___ |
| 12 | NetFlow + SPAN | 7 | ___ |
| 13 | EEM | 7 | ___ |
| **A** | Thông suốt *(6 đường)* | — | ☐ đủ 6 |
| **B** | 🔴 **Diễn tập sự cố** *(5 kịch bản)* | — | ☐ đủ 5 |
| | **TỔNG** | **100** | ___ |

## D. Đánh giá

| Điểm | Kết luận | Việc tiếp theo |
|:---:|---|---|
| **90–100** | ✅ **Sẵn sàng thi.** Bạn đã làm được thứ mà nhiều người đi làm 2 năm chưa làm trọn | Sang phần luyện đề *(Module-13 §5)* |
| **80–89** | ✅ **Đạt nghiệm thu.** Còn vài chỗ lỏng | Xem lại đúng các Task bị mất điểm, **làm lại riêng Task đó** |
| **65–79** | ⚠️ **Chưa đạt.** Hiểu nguyên lý nhưng chưa chắc tay | 🔴 **Làm lại toàn bộ từ Task 1, không nhìn đáp án.** Lần hai sẽ nhanh hơn nhiều |
| **< 65** | 🔴 **Quay lại module lý thuyết** | Xem bảng dưới để biết quay lại đâu |

### Mất điểm ở đâu thì quay lại module nào

| Mất điểm nhiều ở | Quay lại |
|---|---|
| Task 2, 3 | [Module-02](Module-02-Layer2-STP-RSTP-MST-EtherChannel.md) |
| 🔴 **Task 4** | [Module-06A](Module-06A-FHRP-HSRP-VRRP-GLBP.md) + [Module-03 §2.4](Module-03-IP-Routing-Nen-tang.md) |
| Task 5 | [Module-04A](Module-04A-OSPF-Nen-tang-va-LSDB.md) + [Module-04B](Module-04B-OSPF-Area-Summarization-OSPFv3.md) |
| 🔴 **Task 6** | [Module-05A](Module-05A-BGP-Nen-tang-va-eBGP-Peering.md) + [Module-05B](Module-05B-BGP-Path-Selection-va-Filtering.md) |
| Task 7, 8 | [Module-06B](Module-06B-NAT-NTP-Multicast.md) |
| Task 9, 10 | [Module-10](Module-10-Security.md) |
| Task 11, 12 | [Module-11](Module-11-Network-Assurance.md) |
| Task 13 | [Module-12 §8](Module-12-Automation-va-Programmability.md) |
| **Diễn tập B thất bại** | 🔴 **Không phải lỗi một module** — đó là lỗi **ghép nối**. Đọc lại phần E |

## E. 🔴 Nếu bạn làm đúng từng Task nhưng trượt phần Diễn tập

> ⭐ **Đây là bài học đắt giá nhất của cả capstone, và là thứ tách người biết cấu hình
> khỏi người làm được hệ thống.**

| Triệu chứng | Nguyên nhân ghép nối | Bài học |
|---|---|---|
| Tắt EDGE1 thì PC mất mạng, dù VRRP đúng | 🔴 **DHCP cấp cổng mặc định là IP thật, không phải VIP** | Task 8 âm thầm phá Task 4 |
| Shut WAN EDGE1 mà VRRP không nhường | 🔴 **IP SLA thiếu `source-interface`** → ping vòng qua EDGE2 → track luôn Up | Đo sai chỗ thì cơ chế dự phòng vô dụng |
| iBGP chết khi đứt link giữa 2 EDGE | 🔴 **Peer bằng IP vật lý** thay vì loopback | Dự phòng chỉ có giá trị khi *toàn bộ* đường đi còn dự phòng |
| EDGE2 nhận default route nhưng không dùng được | 🔴 **Thiếu `next-hop-self`** trên iBGP | Tuyến "có trong bảng BGP" ≠ "dùng được" |
| Bật CoPP xong OSPF rớt | 🔴 **Bóp nhầm lớp định tuyến** | Bảo vệ mà làm sập thứ cần bảo vệ |
| NAT cấu hình đúng mà không ra Internet | 🔴 **Quên `ip nat inside/outside`** | Lỗi im lặng nguy hiểm hơn lỗi báo đỏ |

> 🔴 **Rút ra:**  **mỗi khi bạn thêm một cấu hình mới, hãy tự hỏi:
> "cái này có phá thứ gì tôi đã làm trước đó không?"**
> Đó là câu hỏi mà người làm dự án thật hỏi liên tục, và người mới thì không bao giờ hỏi.

## F. Hồ sơ bàn giao — làm nốt cho giống thật

> ⭐ Dự án thật **không kết thúc khi cấu hình xong**, mà khi **bàn giao được cho người khác vận hành**.
> ⭐ Làm nốt 4 việc này — vừa là thói quen nghề nghiệp, vừa giúp bạn ôn lại lần cuối:

| ☐ | Việc | Vì sao |
|:---:|---|---|
| ☐ | **Xuất `show running-config` của cả 6 node ra file** | Hồ sơ gốc để so sánh về sau |
| ☐ | **Vẽ lại sơ đồ bằng tay**, ghi đủ IP · VLAN · AS · area | 🔴 **Vẽ được mới là hiểu.** Chép lại không tính |
| ☐ | **Viết 1 trang: hệ thống này dự phòng ở những điểm nào** | Buộc bạn nói ra thiết kế bằng lời của mình |
| ☐ | **Liệt kê 3 điểm YẾU còn lại của thiết kế này** | Xem gợi ý bên dưới |

<details><summary>💡 Gợi ý — ba điểm yếu của chính thiết kế này</summary>

⭐ **Một kỹ sư giỏi biết hệ thống mình vừa xây còn hở chỗ nào.** Ba chỗ rõ nhất:

1. 🔴 **Cả hai EDGE cùng NAT.** Phiên đi ra bằng EDGE1 mà đường về vào EDGE2 thì **đứt**.
   Ngoài đời xử lý bằng cách gắn NAT vào **trạng thái VRRP** *(chỉ Master mới NAT)*,
   hoặc dùng **tường lửa có đồng bộ phiên**.

2. 🔴 **Chi nhánh chỉ có MỘT đường về trụ sở.** Đứt cáp đó là chi nhánh mất mạng hoàn toàn.
   Thiết kế thật cần **đường dự phòng** *(4G/LTE, hoặc VPN qua Internet — xem
   [Module-08](Module-08-Virtualization-va-Overlay.md) về GRE over IPsec)*.

3. 🔴 **Không có mã hoá trên đường WAN.** Traffic giữa trụ sở và chi nhánh đi **trần**.
   Thiết kế thật phải bọc **IPsec**.

⭐ **Thêm một điểm nữa nếu bạn nhìn ra:** máy chủ syslog và NetFlow ở `10.1.99.100`
là **một điểm chết đơn lẻ** — mất nó là mất toàn bộ khả năng điều tra sự cố.
</details>

---

> 🎓 **Hoàn thành capstone = bạn đã dựng một hệ thống chạm vào CẢ SÁU domain của ENCOR
> trong MỘT bài, và kiểm chứng nó bằng diễn tập sự cố như nghiệm thu thật.**
>
> ⭐ **Tiếp theo:** [Module-13 §5 — luyện đề và chiến thuật phòng thi](Module-13-On-thi-va-Chien-thuat-Phong-thi.md).
