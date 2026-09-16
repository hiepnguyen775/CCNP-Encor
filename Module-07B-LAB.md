# LAB 07B — Tuần 13: AP join · Roaming · Chẩn đoán WLAN

> 📘 **Lý thuyết:** [Module-07B](Module-07B-CAPWAP-WLC-FlexConnect-Roaming.md) —
> đọc **Phần 1** và **Phần 2 mục §3.3 (CAPWAP), §3.4–3.6 (AP join), §3.9 (troubleshoot)** trước khi làm.
>
> ⏱️ **Thời gian:** ~3 giờ · 💾 **RAM: 0 GB** · 🧰 **Cần:** giấy bút + laptop + (tùy chọn) DevNet Sandbox

---

## ⭐ Module học bằng ĐẦU, không phải bằng tay

PC 16 GB **không dựng nổi** WLC + AP thật. Nhưng đề cũng **không bắt bạn cấu hình** —
nó cho tình huống và bắt bạn **chỉ ra nguyên nhân**. Lab này luyện đúng kỹ năng đó.

| LAB | Nội dung | Cần gì | Bắt buộc? |
|---|---|---|:---:|
| **A** | ⭐⭐ **AP sẽ join WLC nào?** — 6 tình huống | Giấy bút | ⭐⭐ **Có** |
| **B** | ⭐⭐ **12 tình huống chẩn đoán** | Giấy bút | ⭐⭐ **Có** |
| **C** | Nhìn WLC thật | DevNet Sandbox | Nên |
| **D** | Quan sát roaming thật | Laptop Windows | Nên |

> ⭐ **LAB A và B là dạng câu hỏi CHÍNH XÁC của blueprint 3.3.c và 3.3.e.**
> Làm hai lab này trên giấy có giá trị hơn nhiều so với cố dựng một WLC ảo.

---

## ⚠️ Đọc trước khi bắt đầu

| Điều cần biết | Chi tiết |
|---|---|
| **Viết đáp án TRƯỚC khi mở gợi ý** | Đây mới là luyện tập. Đọc thẳng đáp án thì vô ích |
| **LAB B: ghi đủ 3 thứ mỗi tình huống** | (a) tầng nào trong 6 tầng · (b) lệnh gõ đầu tiên · (c) nguyên nhân khả dĩ nhất |
| **DevNet Sandbox là môi trường DÙNG CHUNG** | ⭐ Chỉ **XEM**, đừng đổi cấu hình |
| **Lấy tài khoản từ chính trang sandbox** | Cisco đổi định kỳ — đừng chép từ nguồn khác |

---

## 🧪 11. LAB 07B

| LAB | Cần gì | Thời gian | Bắt buộc? |
|---|---|:---:|:---:|
| **A** — Lab trên giấy: AP sẽ join WLC nào | Bút + giấy | 30 phút | ⭐⭐ **Bắt buộc** |
| **B** — Lab chẩn đoán: 12 tình huống | Bút + giấy | 40 phút | ⭐⭐ **Bắt buộc** |
| **C** — DevNet Sandbox C9800 | Trình duyệt + tài khoản Cisco | 60 phút | ⭐ Rất nên |
| **D** — Quan sát roaming thật | Laptop Windows | 20 phút | ⭐ Nên |

---

### LAB A — ⭐⭐ AP sẽ join WLC nào? (30 phút, trên giấy)

> ⭐ **Đây chính xác là dạng câu hỏi của blueprint 3.3.c.** Làm hết 6 tình huống.

**Tình huống 1.** AP mới hoàn toàn (chưa từng join ai), nằm **cùng subnet** với WLC-A. Không có DHCP option 43, không có DNS record. Chuyện gì xảy ra?

<details><summary>⭐ Đáp án</summary>

⭐ **AP join được WLC-A** — nhờ ⭐ **broadcast discovery trên subnet local** (§3.5, cách 5).
⭐ Đây là lý do "cắm AP cùng VLAN với WLC thì tự chạy".
</details>

**Tình huống 2.** Như trên nhưng AP ở **VLAN 100**, WLC ở **VLAN 10** (có route thông giữa hai VLAN, ping được). Không có option 43, không DNS. Chuyện gì xảy ra?

<details><summary>⭐ Đáp án</summary>

🔴 ⭐ **AP KHÔNG join được**, dù **ping được WLC**.
⭐ Vì broadcast discovery **không đi qua router**, và AP không có nguồn thông tin nào khác.
⭐ **Cách sửa:** ⭐ **DHCP option 43**, hoặc **DNS `CISCO-CAPWAP-CONTROLLER.<domain>`**, hoặc cấu hình tĩnh qua console.

⭐ **Bài học:** *"Ping được ≠ join được."* Đây là câu đề rất hay hỏi.
</details>

**Tình huống 3.** AP đã cấu hình: Primary = WLC-A, Secondary = WLC-B. Cả hai đều **online và còn chỗ**. Discovery nhận được response từ **WLC-A, WLC-B và WLC-C**. AP join ai?

<details><summary>⭐ Đáp án</summary>

⭐ **WLC-A** — vì nó là **Primary**, bước ① của quá trình selection (§3.6).
⭐ Tải trọng hiện tại của các WLC **không quan trọng** khi Primary còn khả dụng.
</details>

**Tình huống 4.** AP **không có** primary/secondary/tertiary. Không có WLC nào là master. Discovery nhận response từ:
- WLC-A: sức chứa 500 AP, đang có **480**
- WLC-B: sức chứa 150 AP, đang có **60**
- WLC-C: sức chứa 6000 AP, đang có **5900**

AP join ai?

<details><summary>⭐ Đáp án</summary>

⭐ Tính **dung lượng dư** (excess capacity):
- WLC-A: 500 − 480 = **20**
- ⭐ **WLC-B: 150 − 60 = 90** ← **nhiều nhất**
- WLC-C: 6000 − 5900 = **100** ← ⭐ **thật ra đây mới là nhiều nhất!**

⭐ **Đáp án: WLC-C** (dư 100).

🔴 ⭐ **Bẫy kép ở câu này:** (a) không phải "WLC ít AP nhất" (đó là WLC-B với 60 AP);
(b) không phải "WLC ít tải nhất theo %" (WLC-B đang 40%, WLC-C đang 98%).
⭐ **Là WLC có SỐ CHỖ TRỐNG TUYỆT ĐỐI lớn nhất.**
</details>

**Tình huống 5.** AP đã từng join WLC-A (thuộc mobility group "HQ" cùng WLC-B và WLC-C). Hôm nay WLC-A **tắt để bảo trì**. AP reboot. Chuyện gì xảy ra?

<details><summary>⭐ Đáp án</summary>

⭐ AP nhớ trong **NVRAM** không chỉ WLC-A mà cả ⭐ **danh sách thành viên mobility group** mà WLC-A đã cung cấp.
→ ⭐ AP gửi discovery tới **WLC-B và WLC-C** → join một trong hai (theo thứ tự selection §3.6).

⭐ **Đây là lý do mobility group giúp cả roaming lẫn khả năng phục hồi khi join.**
</details>

**Tình huống 6.** AP có IP, ping được WLC, firewall đã mở UDP 5246/5247. `show ap join stats detailed` cho thấy hỏng ở giai đoạn **DTLS**. Nguyên nhân khả dĩ nhất?

<details><summary>⭐ Đáp án</summary>

⭐⭐ **Sai thời gian hệ thống** trên WLC (hoặc AP).
⭐ DTLS xác thực bằng **chứng thư số**; chứng thư có ngày hiệu lực và ngày hết hạn.
⭐ Đồng hồ sai → chứng thư bị coi là **"chưa có hiệu lực"** hoặc **"đã hết hạn"** → bắt tay thất bại.

⭐ **Sửa:** cấu hình **NTP** cho WLC (⭐ **Module-06B §3** — bạn đã học rồi!) và kiểm tra `show clock`.

⭐ *(Nguyên nhân khả dĩ khác: chứng thư MIC của AP hết hạn — gặp với AP rất cũ; hoặc AP nằm trong danh sách chặn.)*
</details>

---

### LAB B — ⭐⭐ 12 tình huống chẩn đoán (40 phút, trên giấy)

> ⭐ **Cách làm:** với mỗi tình huống, ⭐ **viết ra (a) tầng nào trong 6 tầng §9.1, (b) lệnh bạn gõ đầu tiên, (c) nguyên nhân khả dĩ nhất.**
> ⭐ Viết trước khi mở đáp án — đây mới là luyện tập.

| # | Tình huống |
|:---:|---|
| 1 | AP hiện `Registered` trên WLC, đèn xanh, nhưng **không client nào thấy SSID** |
| 2 | Client gõ đúng mật khẩu nhưng bị **đá ra ngay lập tức** |
| 3 | Client **Authenticated** nhưng **không nhận được IP** |
| 4 | AP ở chi nhánh: client có IP nhưng **sai subnet** |
| 5 | Khách kết nối SSID mở, có IP, nhưng **không hiện trang đăng nhập** |
| 6 | Người dùng đi từ tầng 2 sang tầng 3 thì **cuộc gọi rớt**, dữ liệu vẫn chạy |
| 7 | Chỉ **máy quét mã vạch** không thấy SSID, laptop và điện thoại đều thấy |
| 8 | AP mới lắp: có IP, **ping được WLC**, nhưng không join |
| 9 | Tất cả AP chi nhánh **rớt cùng lúc** lúc 2 giờ sáng, tự khôi phục lúc 2:05 |
| 10 | Client kết nối được, nhưng **tải file lớn thì treo**; ping và web nhỏ vẫn OK |
| 11 | Bật 802.11r xong, **5 laptop cũ không join được** |
| 12 | Vạch sóng đầy, SNR 28 dB, nhưng **mạng vẫn rất chậm** vào giờ họp |

<details><summary>⭐ Đáp án LAB B</summary>

| # | Tầng | ⭐ Lệnh đầu tiên | ⭐ Nguyên nhân khả dĩ nhất |
|:---:|:---:|---|---|
| 1 | ③ | ⭐ `show ap tag summary` | ⭐⭐ **Chưa gán Policy Tag cho AP**, hoặc tag không chứa WLAN nào. *(Xem §10.3 — hai chuỗi độc lập)* |
| 2 | ④ | `show wireless client mac-address <mac> detail` | ⭐ Sai PSK · hoặc ⭐ **PMF Required** mà client không hỗ trợ 802.11w |
| 3 | ⑤ | ⭐ `show interface trunk` (trên **switch**) + `show ip dhcp binding` | ⭐⭐ **VLAN sai trong Policy Profile**, hoặc **VLAN chưa được phép qua trunk**, hoặc DHCP scope cạn/thiếu `ip helper-address` |
| 4 | ⑤ | `show wireless profile flex …` + `show interface trunk` | ⭐⭐ **VLAN mapping trong Flex Profile sai** hoặc **native VLAN của trunk sai** |
| 5 | ④/⑤ | Kiểm tra ACL pre-auth | ⭐ **ACL pre-auth chặn DNS (UDP 53)** → trình duyệt không mở được trang nào → không có redirect |
| 6 | ④ | `show wireless client … mobility history` · `show wireless mobility summary` | ⭐ **Roam quá chậm** (chưa bật 11r/OKC) · hoặc **roam L3 giữa 2 WLC mà mobility peer Down** → đổi IP |
| 7 | ①/③ | `netsh wlan show networks` từ laptop cạnh đó | ⭐ **Client capabilities**: chỉ hỗ trợ **2.4 GHz** · hoặc AP đang ở **channel DFS** · hoặc **data rate thấp đã bị tắt** |
| 8 | ② | ⭐ `show ap join stats detailed <mac>` | ⭐ Firewall chặn **UDP 5246/5247** · hoặc ⭐ **sai giờ → DTLS hỏng** · hoặc ⭐ **MTU** *(ping được vì gói ping nhỏ)* |
| 9 | ② | `show ap uptime` + log WAN | ⭐ **Đứt WAN → AP vào Standalone mode.** Nếu là **central switching** → client rớt hết (§5.3). Xem thêm: cửa sổ bảo trì / backup job làm nghẽn WAN |
| 10 | ② | ⭐ `ping <WLC> df-bit size 1500` | ⭐⭐ **MTU** trên đường AP↔WLC (§3.3) — gói nhỏ qua, gói lớn drop. ⭐ **Dấu hiệu kinh điển** |
| 11 | ③/④ | `show wlan id <n>` | ⭐ Client cũ **không hỗ trợ FT** → dùng **FT adaptive** hoặc ⭐ **tách WLAN riêng cho voice** |
| 12 | ① | ⭐ `show ap auto-rf dot11 5ghz` (channel utilization) | ⭐ **Không phải vấn đề tín hiệu** — là **CAPACITY**: quá nhiều client/CCI trên cùng cell. ⭐ Xem Module-07A §4.2 (thêm AP, giảm công suất, 20/40 MHz, bớt SSID) |

⭐ **Điểm chung của 12 câu:** ⭐ **chỉ có câu 12 là vấn đề RF thuần túy.** Đa số ca "Wi-Fi hỏng"
thực ra là **cấu hình, VLAN, hoặc mạng có dây** — ⭐ **đây là bài học lớn nhất của mục 3.3.e.**
</details>

---

### LAB C — ⭐ DevNet Sandbox Catalyst 9800 (60 phút)

| Bước | Làm |
|:---:|---|
| 1 | `developer.cisco.com/site/sandbox/` → đăng nhập tài khoản Cisco (miễn phí) |
| 2 | Tìm sandbox **Catalyst 9800** — ⭐ ưu tiên loại **Always-On** (không cần đặt lịch/VPN) |
| 3 | ⚠️ ⭐ **Lấy URL + tài khoản từ chính trang sandbox** — Cisco đổi định kỳ, đừng chép ở nguồn khác |
| 4 | Đăng nhập **GUI** (và **SSH** nếu sandbox cho phép) |

⭐ **Bảng việc cần làm — mỗi dòng là một khái niệm bạn vừa học:**

| # | Tìm cái gì | Ở đâu (GUI) | Lệnh CLI tương đương | Liên hệ mục |
|:---:|---|---|---|:---:|
| 1 | ⭐ Danh sách AP, mode, channel, Tx power | Monitoring → Wireless → AP Statistics | `show ap summary` | 07A §5 |
| 2 | ⭐⭐ **AP đang dùng tag nào** | Configuration → Wireless → Access Points → *(chọn AP)* | ⭐ `show ap tag summary` | §7.1 |
| 3 | ⭐ Danh sách WLAN + trạng thái enable | Configuration → Tags & Profiles → WLANs | `show wlan summary` | §7 |
| 4 | ⭐ Policy Profile: **VLAN** và central/local switching | Configuration → Tags & Profiles → Policy | `show wireless profile policy summary` | §7.1 |
| 5 | ⭐⭐ **Policy Tag map WLAN nào với Policy nào** | Configuration → Tags & Profiles → Tags → Policy | `show wireless tag policy detailed <tag>` | §7.1 |
| 6 | ⭐ Site Tag — có bật FlexConnect (`no local-site`) không | Tags → Site | `show wireless tag site detailed <tag>` | §5.4 |
| 7 | ⭐ Client đang kết nối: **RSSI, SNR, State, VLAN** | Monitoring → Wireless → Clients | ⭐ `show wireless client mac-address <mac> detail` | §9.2 |
| 8 | ⭐ Mobility peer Up/Down | Configuration → Wireless → Mobility | ⭐ `show wireless mobility summary` | §6.3 |
| 9 | ⭐ Thiết lập RRM: DCA, TPC, channel list | Configuration → Radio Configurations → RRM | `show ap auto-rf dot11 5ghz` | 07A §2.7 |
| 10 | ⭐ Cấu hình bảo mật của một WLAN (WPA2/3, PSK/802.1X, PMF, FT) | WLANs → *(chọn)* → Security | `show wlan id <n>` | §8 |

> ⚠️ ⭐ **Sandbox always-on là môi trường DÙNG CHUNG.**
> ⭐ **Chỉ XEM, đừng đổi cấu hình** (trừ khi trang sandbox nói rõ được phép).
> Mục tiêu là **nhìn thấy các khái niệm nằm ở đâu**, không phải để cấu hình.

✅ **Checkpoint LAB C — trả lời được 4 câu này là đạt:**
1. ⭐ Vẽ lại (trên giấy) chuỗi **WLAN Profile → Policy Profile → Policy Tag → AP** của **một** SSID có thật trong sandbox
2. ⭐ Chỉ ra **một AP** và nói nó đang chạy **Local mode hay FlexConnect** — dựa vào đâu?
3. ⭐ Nếu muốn đổi VLAN của một SSID, bạn sửa ở **Policy Profile** hay **WLAN Profile**? Vì sao?
4. ⭐ Tìm được **một client** và đọc được **State / RSSI / SNR / VLAN** của nó

---

### LAB D — ⭐ Quan sát roaming thật bằng laptop (20 phút)

| Bước | Làm |
|:---:|---|
| 1 | Ở văn phòng/nơi có **nhiều AP cùng SSID**. Kết nối Wi-Fi |
| 2 | Ghi lại **BSSID** hiện tại: `netsh wlan show interfaces \| findstr BSSID` |
| 3 | ⭐ **Đi bộ** sang khu vực khác, chờ 30 giây, ghi lại BSSID |
| 4 | Lặp lại 3–4 lần ở các vị trí khác nhau |
| 5 | Chạy `netsh wlan show wlanreport`, mở file HTML, xem bảng **Wireless Sessions** |

✅ **Checkpoint:**

| # | Cần quan sát được | Ý nghĩa |
|:---:|---|---|
| 1 | ⭐ **BSSID thay đổi nhưng SSID giữ nguyên** | ⭐ Đó là **roaming trong một ESS** |
| 2 | ⭐ **IP có đổi không?** (`ipconfig`) | ⭐ Không đổi → **roam L2** (hoặc L3 có mobility tunnel hoạt động đúng) |
| 3 | ⭐ Trong `wlanreport`, có lần nào **rớt hẳn rồi kết nối lại** không? | ⭐ Rớt hẳn = **roam thất bại** — thiếu overlap hoặc client sticky |
| 4 | ⭐ Thử **đứng yên giữa 2 AP** rồi xem BSSID có nhảy qua lại không | ⭐ Nhảy liên tục = **"ping-pong roaming"** — cell overlap quá nhiều |
| 5 | ⭐ Đi thật xa AP cũ rồi mới quay lại xem BSSID — nó có đổi **muộn** không? | ⭐ Đổi muộn = **sticky client** (§6.6) |
