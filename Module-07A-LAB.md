# LAB 07A — Tuần 12: RF thật, bằng đúng thiết bị bạn đang có

> 📘 **Lý thuyết:** [Module-07A](Module-07A-Wireless-RF-802.11-AP-Antenna.md) —
> đọc **Phần 1** và **Phần 2 mục §3.2 (dBm), §3.3 (EIRP), §3.4 (RSSI/SNR), §3.6 (band & channel)** trước khi làm.
>
> ⏱️ **Thời gian:** ~3 giờ · 💾 **RAM: 0 GB** 🎉 · 🧰 **Cần:** laptop Wi-Fi + điện thoại Android

---

## ⭐ Module duy nhất KHÔNG cần EVE-NG

Bạn sẽ lab bằng **chính Wi-Fi quanh bạn** — không dựng máy ảo, không tốn RAM,
làm được ở quán cà phê.

| # | Câu hỏi | LAB |
|:---:|---|:---:|
| 1 | Đổi dBm ↔ mW **bằng đầu**, không máy tính — làm được không? | A |
| 2 | EIRP tính thế nào, và vì sao cable loss **trừ** mà antenna gain **cộng**? | A |
| 3 | Vạch sóng đầy mà mạng vẫn chậm — nhìn số nào mới biết? | A, B |
| 4 | Wi-Fi quanh bạn đang dùng channel nào? Có ai gây nhiễu không? | B, C |
| 5 | Một bức tường làm tín hiệu tụt bao nhiêu? Thân người thì sao? | B |
| 6 | Laptop của bạn hỗ trợ chuẩn gì — và điều đó giới hạn gì? | B |

> ⭐ **LAB A và B là bắt buộc.** Chúng biến lý thuyết RF trừu tượng thành thứ
> **nhìn thấy được**, và chỉ mất 45 phút.

---

## ⚠️ Đọc trước khi bắt đầu

| Điều cần biết | Chi tiết |
|---|---|
| **LAB A làm trên giấy** | 8 bài tính. ⭐ **Không dùng máy tính** — chỉ dùng quy tắc 3 & 10 |
| **LAB B cần Windows** | Dùng `netsh wlan`. macOS/Linux có lệnh tương đương — xem §11.1 của lý thuyết |
| **LAB C cần Android** | iPhone **không làm được** (iOS chặn API quét Wi-Fi). Không có Android thì bỏ qua |
| **Số của bạn sẽ khác** | Đây là Wi-Fi thật quanh bạn — mỗi người một kết quả. Đó là điểm hay của lab này |
| **Lỗi > 15 phút** | Ghi vào [`SO-TAY-LOI.md`](SO-TAY-LOI.md) |

---

## 🧪 8. LAB 07A — RF thật, bằng đúng thiết bị bạn đang có

> ⭐ **Module này không cần EVE-NG.** Nhưng  **bắt buộc phải làm LAB A và LAB B** —
> chúng biến lý thuyết RF thành thứ **nhìn thấy được**, mất tổng cộng ~45 phút.

### 8.1 Bảng tổng LAB

| LAB | Cần gì | Thời gian | Bắt buộc? |
|---|---|:---:|:---:|
| **A** — Tính RF trên giấy | Bút + giấy | 20 phút | ⭐ **Bắt buộc** |
| **B** — Soi Wi-Fi bằng Windows CLI | Laptop Windows có Wi-Fi | 30 phút | ⭐ **Bắt buộc** |
| **C** — Bản đồ channel quanh nhà | Điện thoại Android + app | 20 phút | ⭐ Rất nên |
| **D** — Wi-Fi report & lịch sử roam | Laptop Windows | 15 phút | Nên |
| **E** — Nhìn WLC thật trên DevNet Sandbox | Trình duyệt + tài khoản DevNet | 30 phút | Tùy chọn (làm ở 07B cũng được) |

---

### LAB A — ⭐ Tính RF trên giấy (20 phút)

> ⭐ **Làm hết 8 câu, KHÔNG dùng máy tính.** Chỉ dùng quy tắc 3 & 10.
> Đây chính là dạng câu tính toán duy nhất mà ENCOR hỏi ở khối wireless.

| # | Đề |
|:---:|---|
| 1 | 40 mW = ? dBm |
| 2 | 23 dBm = ? mW |
| 3 | AP: Tx 20 dBm, cáp mất 4 dB, antenna 8 dBi → EIRP = ? dBm = ? mW |
| 4 | Quy định EIRP tối đa 36 dBm. Antenna 21 dBi, cáp 3 dB → Tx tối đa = ? |
| 5 | RSSI −72 dBm, noise floor −94 dBm → SNR = ? Có đủ cho Voice không? |
| 6 | RSSI −52 dBm, noise floor −68 dBm → SNR = ? Nhận xét? |
| 7 | Đổi channel 20 MHz → 80 MHz, mọi thứ khác giữ nguyên. SNR thay đổi ra sao? |
| 8 | Antenna đổi từ 4 dBi → 13 dBi. EIRP tăng bao nhiêu dB? Công suất phát ra gấp mấy lần? |

<details>
<summary>⭐ Đáp án LAB A</summary>

| # | Lời giải | Đáp án |
|:---:|---|---|
| 1 | 100 mW=20 dBm → ÷2 = 50 mW=17 dBm → ÷2 = 25 mW=14. 40 không tròn theo 3/10 — ⭐ ước lượng: 40 mW nằm giữa 25 (14 dBm) và 50 (17 dBm), gần 50 hơn → **≈16 dBm** | **≈16 dBm** *(chính xác 16.02)* |
| 2 | 0→10 dBm=10 mW→20 dBm=100 mW→+3=23 dBm=200 mW | **200 mW** |
| 3 | 20 − 4 + 8 = 24 dBm. 24 = 20(100mW) +3(200) +1… ⭐ dễ hơn: 21 dBm=125 mW, 24=21+3 → **250 mW** | **24 dBm ≈ 250 mW** |
| 4 | 36 = Tx − 3 + 21 → Tx = 36 + 3 − 21 = **18 dBm** | **18 dBm (≈63 mW)** |
| 5 | −72 − (−94) = **22 dB** →  đạt tối thiểu cho Voice (≥20) nhưng **RSSI −72 đã dưới ngưỡng −67** → 🔴 **chưa đạt chuẩn Voice** | **22 dB — không đạt vì RSSI yếu** |
| 6 | −52 − (−68) = **16 dB**.  RSSI rất mạnh nhưng **noise floor cao bất thường (−68)** → SNR chỉ 16 → 🔴 **có nguồn nhiễu mạnh, phải đi tìm** | **16 dB — vạch đầy nhưng mạng tệ** |
| 7 | 20→40 = −3 dB, 40→80 = −3 dB nữa → ⭐ **SNR giảm 6 dB** | **−6 dB** |
| 8 | +9 dB. +3=×2, +3=×4, +3=×8 → ⭐ **gấp 8 lần** | **+9 dB, ×8** |

⭐ **Câu 5 và 6 là hai câu quan trọng nhất** — chúng dạy bạn rằng phải nhìn **cả RSSI lẫn SNR**.
</details>

---

### LAB B — ⭐ Soi Wi-Fi thật bằng Windows CLI (30 phút)

> ⭐ Không cần cài gì. Mở **PowerShell** hoặc **CMD** trên laptop đang bật Wi-Fi.

#### Bước 1 — Xem kết nối hiện tại

```
netsh wlan show interfaces
```

**Output mẫu (rút gọn):**
```
    Name                   : Wi-Fi
    SSID                   : CTY-CORP
    BSSID                  : a4:53:0e:11:22:30      <-- MAC radio của AP
    Network type           : Infrastructure
    Radio type             : 802.11ax               <-- chuẩn đang dùng
    Authentication         : WPA2-Enterprise        <-- 802.1X (Module-10)
    Cipher                 : CCMP
    Channel                : 44                     <-- 5 GHz, UNII-1, không DFS
    Receive rate (Mbps)    : 573
    Transmit rate (Mbps)   : 573
    Signal                 : 82%                    <-- Windows cho %, không cho dBm
```

✅ **Checkpoint 1 — trả lời được 5 câu này về chính mạng của bạn:**

| # | Câu hỏi | Cách tra |
|:---:|---|---|
| 1 | Bạn đang ở band nào? | ⭐ Channel ≤ 14 → 2.4 GHz · 36–165 → 5 GHz |
| 2 | Channel của bạn có phải DFS không? | ⭐ 52–64 và 100–144 → **có DFS** |
| 3 | Chuẩn 802.11 nào? | dòng `Radio type` |
| 4 | ⭐ **Signal % ≈ bao nhiêu dBm?** | **dBm ≈ (% ÷ 2) − 100** → 82% ≈ **−59 dBm** |
| 5 | Data rate hiện tại có gần tốc độ tối đa của chuẩn đó không? | So với bảng §3.1 |

> ⭐ **Công thức đổi % → dBm của Windows:** `dBm ≈ (quality/2) − 100`
> → 100% = −50 dBm · 80% = −60 dBm · ⭐ **34% ≈ −83 dBm (đã rất yếu)** · 0% = −100 dBm

#### Bước 2 — ⭐ Quét toàn bộ AP xung quanh (đây là phần hay nhất)

```
netsh wlan show networks mode=bssid
```

**Output mẫu (một mục):**
```
SSID 3 : NHA-HANG-XOM
    Network type            : Infrastructure
    Authentication          : WPA2-Personal
    BSSID 1                 : 3c:84:6a:aa:bb:c0
         Signal             : 45%
         Radio type         : 802.11n
         Band               : 2.4 GHz
         Channel            : 3            <-- KHÔNG PHẢI 1/6/11 → gây ACI!
    BSSID 2                 : 3c:84:6a:aa:bb:c1
         Signal             : 38%
         Radio type         : 802.11ac
         Band               : 5 GHz
         Channel            : 149
```

✅ **Checkpoint 2 — làm bảng thống kê này bằng tay** (đây là bài tập chính của LAB B):

| Việc cần làm | Ghi kết quả |
|---|---|
| ⭐ Đếm tổng số **BSSID** thấy được | ____ |
| ⭐ Đếm số BSSID ở **2.4 GHz** vs **5 GHz** | 2.4: ____ / 5: ____ |
| 🔴  Liệt kê các AP 2.4 GHz **KHÔNG ở channel 1/6/11** | ____ |
| ⭐ Channel 2.4 GHz nào **đông nhất**? | ____ |
| ⭐ Có AP nào ở channel **DFS (52–64, 100–144)** không? | ____ |
| ⭐ Có SSID nào xuất hiện với **nhiều BSSID** không? (→ đó là **ESS**, nhiều AP hoặc nhiều band) | ____ |
| ⭐ Chuẩn cũ nhất bạn thấy (`802.11g`? `802.11n`?) | ____ |

> ⭐ **Kết luận bạn PHẢI tự rút ra:** đếm xem có bao nhiêu AP 2.4 GHz quanh bạn.
> ⭐ **Chỉ có 3 channel để chia.** Nếu bạn thấy 15 BSSID ở 2.4 GHz → trung bình **5 AP/channel** →
> ⭐ **đây chính là lý do 2.4 GHz luôn chậm**, và vì sao doanh nghiệp ưu tiên 5 GHz.

#### Bước 3 — Xem card Wi-Fi của bạn hỗ trợ gì (client capabilities)

```
netsh wlan show drivers
```
**Tìm 3 dòng:**
```
    Radio types supported     : 802.11a 802.11b 802.11g 802.11n 802.11ac 802.11ax
    802.11w Management Frame Protection supported : Yes    <-- PMF → WPA3 được
    Number of supported ... (tùy driver)
```

✅ **Checkpoint 3:** máy bạn có hỗ trợ `802.11ax` không? Có `802.11w` (PMF) không?
⭐ **Nếu không có 802.11w → máy bạn không dùng được WPA3.** Đây chính là "client capabilities" mà blueprint nói.

#### Bước 4 — ⭐ Chứng minh RSSI thay đổi theo khoảng cách và vật cản

| Bước | Làm | Ghi lại `Signal %` + `Receive rate` |
|:---:|---|---|
| 1 | Đứng **cạnh AP/router** | ____% · ____ Mbps |
| 2 | Sang **phòng bên cạnh** (qua 1 tường) | ____% · ____ Mbps |
| 3 | Ra **xa nhất còn kết nối** | ____% · ____ Mbps |
| 4 | ⭐ Đứng nguyên chỗ (3), **lấy thân người che laptop khỏi hướng AP** | ____% · ____ Mbps |

Lệnh dùng ở mỗi bước:
```
netsh wlan show interfaces | findstr /C:"Signal" /C:"Receive rate" /C:"Channel"
```

✅ **Checkpoint 4 — ⭐ Ba điều phải quan sát được:**
1. ⭐ **RSSI giảm → data rate TỰ ĐỘNG giảm theo** → đó chính là **Dynamic Rate Shifting** (§3.4)
2. ⭐ **Chỉ một bức tường** đã làm tụt vài chục % — đúng bảng suy hao §2.5
3. 🔴  **Bước 4: cơ thể người (túi nước) làm tín hiệu tụt rõ rệt** → đây là **absorption**,
   và là lý do phòng họp đông người phải thiết kế theo **capacity** (§4.2)

💡 **Vì sao quan trọng:** bạn vừa **tự tay chứng minh** 3 khái niệm mà đề sẽ hỏi bằng chữ.

---

### LAB C — ⭐ Bản đồ channel quanh nhà (20 phút, điện thoại Android)

> ⚠️ **iPhone không làm được** (iOS chặn API quét Wi-Fi). Dùng Android, hoặc bỏ qua LAB này và dùng LAB B thay thế.

| Bước | Làm |
|:---:|---|
| 1 | Cài app **WiFiAnalyzer** (open source, của VREM) trên Google Play |
| 2 | Mở tab **Channel graph** cho band **2.4 GHz** |
| 3 | ⭐ Chụp màn hình. Đếm xem có bao nhiêu "quả đồi" chồng lên nhau |
| 4 | Chuyển sang band **5 GHz**, chụp lại |
| 5 | Mở tab **Channel rating** → app gợi ý channel tốt nhất |

✅ **Checkpoint — nhìn hai ảnh và trả lời:**

| # | Câu | Điều bạn phải thấy |
|:---:|---|---|
| 1 | Band nào **chật hơn** rõ rệt? | ⭐ Chắc chắn là 2.4 GHz |
| 2 | Có AP nào nằm **giữa** 1-6-11 không? | ⭐ Nếu có → nó đang gây **ACI** cho cả hai bên |
| 3 | Ở 5 GHz, có AP nào chiếm **80 MHz** (quả đồi rất rộng) không? | ⭐ Một AP 80 MHz "ăn" 4 channel |
| 4 | ⭐ Nếu bạn là admin ở đây, bạn chọn channel nào cho AP của mình? Vì sao? | Câu trả lời phải là **1, 6, hoặc 11** — chọn cái ít chồng lấn nhất, **KHÔNG chọn channel lẻ** |

---

### LAB D — Wi-Fi report của Windows: xem lịch sử roam (15 phút)

```
netsh wlan show wlanreport
```
→ File HTML sinh ra tại:
`C:\ProgramData\Microsoft\Windows\WlanReport\wlan-report-latest.html`

Mở bằng trình duyệt. ⭐ **Ba thứ đáng xem:**

| Mục trong report | Ý nghĩa |
|---|---|
| ⭐ **Biểu đồ session** (đường thời gian trên cùng) | Mỗi lần kết nối/rớt.  **Đường đứt nhiều = mạng không ổn định** |
| ⭐ **Bảng "Wireless Sessions"** → cột **BSSID** | **BSSID đổi = bạn đã ROAM sang AP khác.** Đây là roaming thật, nhìn thấy được |
| **Disconnect Reason** | Lý do rớt: do người dùng, do AP deauth, do mất tín hiệu |

✅ **Checkpoint:** tìm được ít nhất **một lần BSSID thay đổi trong khi SSID giữ nguyên** →
⭐ **đó chính là roaming trong một ESS** (§3.5). Nếu chưa có, cầm laptop đi vòng quanh nhà/công ty rồi chạy lại lệnh.

---

### LAB E — 🚀 Nhìn WLC thật trên DevNet Sandbox (tùy chọn, 30 phút)

> ⭐ **Đây là Plan B thay cho việc mua WLC.** Cisco cho dùng **miễn phí**.

| Bước | Làm |
|:---:|---|
| 1 | Vào `developer.cisco.com/site/sandbox/` → đăng nhập bằng tài khoản Cisco (miễn phí) |
| 2 | Tìm sandbox có tên chứa **"Catalyst 9800"** hoặc **"Wireless"** |
| 3 | ⭐ Ưu tiên loại **Always-On** (không cần đặt lịch, không cần VPN) |
| 4 | Đọc trang sandbox để lấy **URL + tài khoản hiện hành** — ⚠️ ⭐ **Cisco đổi thông tin này định kỳ, luôn lấy từ trang sandbox, đừng chép ở đâu khác** |
| 5 | Đăng nhập GUI → xem **Monitoring → Wireless → Clients** và **Configuration → Radio Configurations** |

⭐ **Ba màn hình đáng xem nhất ở LAB E (để chuẩn bị cho 07B):**

| Màn hình | Bạn sẽ thấy |
|---|---|
| **Monitoring → AP Statistics** | ⭐ Channel, Tx power, **AP mode** (§5) của từng AP |
| **Monitoring → Clients** | ⭐ **RSSI, SNR** thật của từng client (§2.4) |
| **Configuration → Radio Configurations → RRM** | ⭐ DCA, TPC, coverage hole (§2.7) |

> ⭐ **Chưa cần cấu hình gì ở LAB này.** Mục tiêu chỉ là **nhìn thấy các con số bạn vừa học**
> nằm ở đâu trên một WLC thật. Cấu hình sẽ làm ở **Module-07B**.
