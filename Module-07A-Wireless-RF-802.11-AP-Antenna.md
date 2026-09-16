# Module-07A — Wireless: RF, 802.11, AP mode & Antenna

> 🧭 **Lộ trình:** [Module-06B](Module-06B-NAT-NTP-Multicast.md) → `[Bạn đang ở đây] Module-07A` → Module-07B (CAPWAP · WLC · FlexConnect · Roaming)
>
> 📊 **Blueprint — Domain 3.3 Wireless (thuộc Infrastructure 30%):**
> · **3.3.a — Describe Layer 1 concepts, such as RF power, RSSI, SNR, interference, noise, band and channels, and wireless client devices capabilities**
> · **3.3.b — Describe AP modes and antenna types**
>
> 📊 Chạm thêm: **1.2.c — Client density** (WLAN design) · phần còn lại của 1.2 nằm ở Module-09
>
> ⏱️ **Tuần 12** · 8–10 giờ

---

# 📌 TÓM TẮT — đọc 10 phút là nắm khung

## Module này trả lời một câu hỏi duy nhất

> **"Sóng Wi-Fi là thứ vô hình — làm sao biết nó MẠNH hay YẾU, SẠCH hay NHIỄU,
> và vì sao vạch đầy mà mạng vẫn chậm?"**

## Sự thật nền tảng — hiểu cái này là hiểu 70% wireless

```
   ⭐⭐ Wi-Fi là HALF-DUPLEX và là môi trường CHIA SẺ

   Trên MỘT channel, trong MỘT vùng nghe được nhau
   → chỉ MỘT thiết bị được phát tại một thời điểm.

   AP và TẤT CẢ client CHIA NHAU thời gian phát.

   ┌───────────────────────────────────────────────┐
   │  Ethernet switch  = mỗi người một đường dây   │
   │  Wi-Fi            = một phòng họp không chủ tọa│
   │                     càng đông càng ít lượt nói│
   └───────────────────────────────────────────────┘

   ⭐ Mọi giới hạn của Wi-Fi đều bắt nguồn từ đây.
```

## Ba công thức phải tính được bằng đầu

```
   ①  QUY TẮC 3 & 10          0 dBm = 1 mW
                              +3 dB = ×2      −3 dB = ÷2
                              +10 dB = ×10    −10 dB = ÷10
       → 20 dBm = 100 mW · 30 dBm = 1 W

   ②  EIRP = Tx power − cable loss + antenna gain
                          ^^^ TRỪ        ^^^ CỘNG

   ③  SNR = RSSI − Noise floor        (ra dB, không phải dBm)
```

## 7 ý phải nhớ

| # | Ý | Một câu |
|:---:|---|---|
| 1 | ⭐⭐ **RSSI mạnh ≠ kết nối tốt** | Phải nhìn **SNR**. RSSI −55 mà noise −65 → SNR chỉ 10 dB = **tệ** |
| 2 | **Ba ngưỡng thiết kế** | RSSI ≥ **−67 dBm** · SNR ≥ **25 dB** · cell overlap **15–20%** |
| 3 | ⭐⭐ **2.4 GHz chỉ có 3 channel** | **1, 6, 11**. Vì channel cách nhau 5 MHz nhưng rộng 20–22 MHz |
| 4 | ⭐⭐ **CCI làm CHẬM, ACI làm HỎNG** | Cùng channel → nhường nhau (chậm) · chồng lấn một phần → **gói vỡ** |
| 5 | **Channel rộng gấp đôi** | **SNR −3 dB** và **mất một nửa số channel**. Doanh nghiệp dùng **20/40 MHz** |
| 6 | ⭐ **802.11: a là 5 GHz · ac CHỈ 5 GHz · ax có cả 2.4** | Ba bẫy đề hay gài nhất |
| 7 | ⭐⭐ **MU-MIMO vs OFDMA** | MU-MIMO chia **không gian** · OFDMA chia **tần số** *(chỉ 802.11ax)* |

## Bảng lệnh cốt lõi

| Lệnh | Cho biết gì |
|---|---|
| `netsh wlan show interfaces` | SSID/BSSID/channel/chuẩn/signal **hiện tại** |
| ⭐ `netsh wlan show networks mode=bssid` | **Mọi AP xung quanh** + channel + band |
| `netsh wlan show drivers` | Card của bạn hỗ trợ chuẩn gì, có PMF không |
| `netsh wlan show wlanreport` | Báo cáo HTML — **lịch sử roam & rớt** |
| *(trên WLC)* `show ap summary` | AP nào up, mode gì, channel nào |
| *(trên WLC)* `show ap auto-rf dot11 5ghz` | Noise, interference, load — dữ liệu RRM |

> ⭐ **Đổi `Signal %` của Windows sang dBm:** `dBm ≈ (% ÷ 2) − 100`
> → 80% ≈ −60 dBm · 34% ≈ −83 dBm (đã rất yếu)

## 🗺️ Bố cục module

| Phần | Tên | Thời gian |
|:---:|---|:---:|
| **1** | 🧠 **CÁI ĐÓ LÀ GÌ** — 5 ví von cho thứ vô hình | 45 phút |
| **2** | ⚙️ **NÓ CHẠY THẾ NÀO** — RF, 802.11, AP mode, antenna | 5 giờ |
| **3** | 🧪 **NHÌN THẤY NÓ** — [LAB 07A](Module-07A-LAB.md), ⭐ **RAM 0 GB** | 3 giờ |
| **4** | 🏗️ **TOPO & KIẾN TRÚC** — coverage vs capacity | 45 phút |
| **📎** | **PHỤ LỤC** — 🔴 không đọc lần đầu | — |

> ⭐ **Toàn bộ Domain 3.3 dùng từ "Describe"** (trừ mục troubleshoot ở Module-07B).
> Nghĩa là ⭐ **đề KHÔNG bắt bạn cấu hình WLC**. Học **bảng**, đừng sa đà cấu hình.
>
> 🎉 **Và đây là module duy nhất lab được mà không cần EVE-NG** — bạn dùng chính
> laptop và Wi-Fi quanh mình.

---

## ⭐ 0. Phạm vi — đọc trước, tiết kiệm cho bạn cả tuần

### 0.1 Điều quan trọng nhất về khối Wireless

> 🔴 ⭐⭐ **Toàn bộ Domain 3.3 dùng từ "Describe", trừ đúng một mục cuối (3.3.e "Troubleshoot").**
> Nghĩa là: ⭐ **đề KHÔNG bắt bạn cấu hình WLC từ đầu.** Đề hỏi *"cái này là gì"*, *"dùng khi nào"*,
> *"nhìn output/màn hình này thì client hỏng ở đâu"*.

| Nếu bạn định… | Thì… |
|---|---|
| Mua AP + WLC thật về lab | ❌ **Không cần.** Tốn tiền, và đề không hỏi tới mức đó |
| Dựng vWLC trong EVE-NG cho đủ bộ | ⚠️ Chạy được nhưng **kén image, hay treo**, và bạn vẫn **không có AP thật để join** |
| Học thuộc mọi lệnh `config wlan …` của AireOS | ❌ **Lãng phí.** AireOS đang bị thay bằng IOS-XE C9800 |
| Học kỹ **bảng** + **đọc được màn hình/output** | ✅ ⭐ **Đúng chiến lược.** Đây là cách ăn điểm khối wireless |

⭐ **Wireless là khối có tỉ lệ điểm/công sức tốt thứ hai của ENCOR** (sau Architecture) —
**với điều kiện** bạn học đúng: học bảng, không sa đà cấu hình.

### 0.2 Bảng phạm vi chi tiết

| Chủ đề | Blueprint | Mức cần đạt | Thời gian |
|---|---|---|---|
| ⭐⭐ **Đơn vị RF** (dBm, mW, dB, dBi, EIRP) | 3.3.a | ⭐ **Tính được bằng đầu** (quy tắc 3 & 10) | 1.5 giờ |
| ⭐⭐ **RSSI · SNR · noise floor** | 3.3.a | ⭐ **Nhớ ngưỡng thực tế** + đọc được số | 1 giờ |
| ⭐⭐ **Band & channel** (2.4 / 5 / 6 GHz, DFS) | 3.3.a | ⭐ **1-6-11**, UNII band, vì sao 5 GHz tốt hơn | 1.5 giờ |
| ⭐ **Interference vs Noise · CCI vs ACI** | 3.3.a | Phân biệt chính xác 4 khái niệm này | 45 phút |
| ⭐ **CSMA/CA · hidden node** | 3.3.a | Hiểu vì sao Wi-Fi là *half-duplex chia sẻ* | 45 phút |
| ⭐⭐ **802.11 a/b/g/n/ac/ax** | 3.3.a | ⭐ **Bảng band–tốc độ–MIMO–tính năng mới** | 1.5 giờ |
| ⭐ **MIMO · MU-MIMO · OFDMA** | 3.3.a | Phân biệt được 3 cái này (đề hay gài) | 45 phút |
| ⭐ **Client capabilities & density** | 3.3.a + 1.2.c | Hiểu vì sao thiết kế theo *capacity* chứ không theo *coverage* | 30 phút |
| ⭐⭐ **AP modes** (9 mode) | 3.3.b | ⭐ **Học thuộc bảng — đề hỏi trực tiếp** | 1 giờ |
| ⭐⭐ **Antenna types** | 3.3.b | ⭐ **Bảng loại–gain–beamwidth–dùng khi nào** | 45 phút |
| CAPWAP · WLC · FlexConnect · Roaming | 3.3.c, 3.3.d | ➡️ **Module-07B** (Tuần 13) | — |
| Wireless security (WPA2/3, EAP, PSK) | 5.4 | ➡️ **Module-07B §7** (giới thiệu) + **Module-10** (sâu) | — |
| Wireless deployment model & location services | 1.2.a, 1.2.b | ➡️ **Module-09** (Architecture) | — |

---

## ✅ 1. Chuẩn bị

| Cần có | Chi tiết |
|---|---|
| **Kiến thức trước** | Module-P0 §2.1 (VLAN/trunk) · Module-01 §2 (3 plane — sẽ dùng lại khi nói split-MAC ở 07B) |
| **Lab** | ⭐ **Không cần EVE-NG cho module này.** Bạn sẽ lab bằng: (1) **chính laptop Wi-Fi của bạn**, (2) app WiFi analyzer trên điện thoại, (3) DevNet Sandbox (tùy chọn) |
| **RAM** | **0 GB** 🎉 — module duy nhất không tốn RAM lab |
| **Cần chuẩn bị** | Một laptop có Wi-Fi (Windows là tiện nhất) · điện thoại Android để cài WiFi analyzer · máy tính bỏ túi hoặc app calculator |
| **Thời lượng** | 5h lý thuyết · 3h lab · 1h quiz |

> 💡 **Tin tốt:** đây là module bạn có thể học ở quán cà phê, trên xe, không cần bật EVE-NG.
> ⭐ **Tin xấu:** đúng vì thế mà nhiều người học chay rồi tưởng mình hiểu. **Vẫn phải làm LAB §9** —
> nó dùng chính Wi-Fi quanh bạn, mất 30 phút, và biến lý thuyết RF thành thứ nhìn thấy được.

---

## 🧠 PHẦN 1 — CÁI ĐÓ LÀ GÌ

> **Đọc phần này TRƯỚC, đọc một mạch.** Không lệnh, không bảng tra.
>
> RF là thứ **vô hình** — bạn không thấy sóng, không thấy nhiễu, không thấy vì sao mạng chậm.
> Năm ví von dưới đây là cách duy nhất để "nhìn" được nó trước khi vào công thức.
>
> **Tự kiểm tra:** đọc xong mỗi mục, gấp tài liệu lại, nói lại trong 3 câu.

### 2.1 Wi-Fi là cuộc họp trong một phòng, không phải điện thoại

Ethernet switch full-duplex = mỗi người có **một đường dây riêng**, nói bao nhiêu tùy thích.

⭐ **Wi-Fi = một phòng họp không có chủ tọa.** Mọi người nghe chung một không khí:
- Muốn nói → **phải nghe xem có ai đang nói không** (CCA)
- Hai người cùng mở miệng → **cả hai đều bị lấp** (collision) → phải nói lại
- Nói xong → **phải chờ người kia gật đầu** (ACK) mới coi là đã truyền đạt
- ⭐ **Càng đông người trong phòng, mỗi người càng ít lượt nói** — dù mỗi người nói rất nhanh

⭐ **Từ đó suy ra mọi thứ:**
- **Thêm AP cùng channel** = kê thêm bàn trong **cùng một phòng** → vẫn phải nhường nhau (**CCI**)
- **Thêm AP khác channel** = ⭐ **mở thêm phòng họp** → đây mới là cách tăng dung lượng thật
- **Client cũ chậm** = một người nói **rất chậm và dài dòng** → cả phòng phải ngồi chờ (⭐ lý do tắt low data rate)
- ⭐ **OFDMA** = cho phép **nhiều người nói cùng lúc mỗi người một chủ đề nhỏ**, thay vì lần lượt

### 2.2 dB là "gấp mấy lần", dBm là "bao nhiêu"

Nhầm dB/dBm là nhầm kiểu **"tăng 50%"** với **"bằng 50"**.
- ⭐ **dBm** trả lời *"to bằng nào?"* → **20 dBm = 100 mW**. Đây là một **con số**.
- ⭐ **dB** trả lời *"gấp/kém mấy lần?"* → **+3 dB = gấp đôi**. Đây là một **tỉ lệ**.
- ⭐ Nên: "antenna 6 **dBi**" = *gom sóng lại gấp 4 lần theo hướng chính* — nó là **tỉ lệ**, không phải công suất.
- ⭐ Và: cộng/trừ trong công thức EIRP hoạt động được **vì thang log biến phép nhân thành phép cộng.**

### 2.3 Antenna không tạo năng lượng — nó nắn hình

Tưởng tượng một quả bóng bay chứa lượng khí cố định:
- ⭐ **Omni** = bóng tròn → tỏa đều mọi hướng, không đi xa
- ⭐ **Gain cao** = ⭐ **bóp dẹt quả bóng** → nó **dài ra theo một hướng**, nhưng **mỏng đi ở hướng khác**
- ⭐ **Lượng khí (năng lượng) không đổi.** Chỉ có hình dạng đổi.

🔴 ⭐ Vì thế: đổi sang antenna gain cao mà **không tính lại hướng lắp** → có chỗ xa hơn nhưng
⭐ **xuất hiện vùng chết ngay dưới AP**.

### 2.4 RSSI là "nghe to cỡ nào", SNR là "nghe rõ cỡ nào"

- ⭐ **RSSI** = người ta nói **to** cỡ nào.
- ⭐ **Noise floor** = trong phòng **ồn** cỡ nào.
- ⭐ **SNR** = ⭐ **bạn có nghe RÕ không** = to hơn tiếng ồn bao nhiêu.

⭐ Ai đó hét rất to (RSSI −50) trong quán bar cực ồn (noise −60) → **bạn vẫn không nghe rõ** (SNR 10 dB).
Người nói vừa phải (RSSI −65) trong thư viện im lặng (noise −95) → ⭐ **nghe rất rõ** (SNR 30 dB).
🔴 ⭐ **Đây là lý do "đầy vạch sóng mà mạng vẫn chậm".**

### 2.5 CCI là chờ, ACI là vỡ

- ⭐ **CCI (cùng channel)**: hai người nói **cùng ngôn ngữ** → nghe được nhau → **lịch sự nhường nhau**.
  Chậm, nhưng **mọi câu đều tới nơi nguyên vẹn**.
- 🔴 ⭐ **ACI (channel chồng lấn)**: hai người nói **hai ngôn ngữ khác nhau, cùng lúc** →
  không ai nhường ai, và **cả hai câu đều bị nhiễu thành vô nghĩa** → phải nói lại từ đầu.

⭐ **Vì thế 1-6-11 luôn thắng "channel 3 cho lạ".**


---

## ⚙️ PHẦN 2 — NÓ CHẠY THẾ NÀO

> | Phần 1 (ví von) | → | Phần 2 (cơ chế) |
> |---|:---:|---|
> | §2.1 cuộc họp trong một phòng | → | **§3.8 CSMA/CA** · **§3.6 band & channel** |
> | §2.2 dB là "gấp mấy lần" | → | **§3.2 Đơn vị công suất** ⭐⭐ |
> | §2.3 antenna nắn hình | → | **§3.3 EIRP** · **§7 Antenna** |
> | §2.4 nghe to vs nghe rõ | → | **§3.4 RSSI · Noise · SNR** ⭐⭐ |
> | §2.5 CCI là chờ, ACI là vỡ | → | **§3.7 Interference vs Noise** |
>
> ⚠️ **Toàn bộ Domain 3.3 dùng từ "Describe"** — trừ mục troubleshoot ở Module-07B.
> ⭐ **Học BẢNG, đừng sa đà cấu hình WLC.** Đây là khối có tỉ lệ điểm/công sức tốt.

---

## 📘 3. LAYER 1 — RF (RADIO FREQUENCY)

### 3.1 Sóng RF — bốn thuộc tính, chỉ cần nhớ đúng chừng này

| Thuộc tính | Là gì | Đơn vị | Ảnh hưởng gì trong Wi-Fi |
|---|---|---|---|
| ⭐ **Frequency** (tần số) | Số chu kỳ trong 1 giây | Hz / MHz / GHz | ⭐ Quyết định **band** và **channel**. Tần số cao → đi gần hơn, xuyên vật cản kém hơn |
| **Wavelength** (bước sóng) | Độ dài 1 chu kỳ | cm / m | Quyết định **kích thước antenna**. 2.4 GHz ≈ 12.5 cm · 5 GHz ≈ 6 cm |
| ⭐ **Amplitude** (biên độ) | "Độ lớn" của sóng | ⭐ **dBm / mW** | ⭐ Chính là **công suất phát**. Toàn bộ §2.2–2.4 nói về cái này |
| **Phase** (pha) | Vị trí trong chu kỳ | độ (°) | 2 sóng lệch pha gặp nhau → **multipath**, có thể triệt tiêu nhau |

⭐ **Công thức duy nhất cần nhớ:** `bước sóng = 300 / tần số(MHz)` (kết quả ra **mét**)
→ 2400 MHz → 300/2400 = 0.125 m = **12.5 cm** · 5000 MHz → **6 cm**

> ⭐ **Hệ quả thực tế của bước sóng:** antenna hiệu quả nhất khi dài bằng **½ hoặc ¼ bước sóng**.
> Đó là lý do antenna 2.4 GHz dài hơn antenna 5 GHz, và vì sao AP dual-band có 2 bộ antenna khác nhau bên trong.

---

### 3.2 ⭐⭐ Đơn vị công suất — phần PHẢI tính được bằng đầu

Đây là mục bị hỏi nhiều nhất của 3.3.a. Đừng học thuộc bảng số — **học 2 quy tắc**.

#### Bốn đơn vị, phân biệt tuyệt đối vs tương đối

| Đơn vị | Loại | Nghĩa | Ví dụ |
|---|---|---|---|
| ⭐ **mW** (milliwatt) | 🔵 **Tuyệt đối** | Công suất thật | AP phát `100 mW` |
| ⭐⭐ **dBm** | 🔵 **Tuyệt đối** | Công suất so với **1 mW**, thang log | `20 dBm` = 100 mW |
| ⭐⭐ **dB** (decibel) | 🟠 **Tương đối** | **Chênh lệch / thay đổi**, không phải công suất | "cáp mất `2 dB`" |
| ⭐ **dBi** | 🟠 **Tương đối** | **Gain của antenna** so với antenna isotropic lý tưởng | antenna `6 dBi` |
| **dBd** | 🟠 Tương đối | Gain so với antenna **dipole** | ⭐ `0 dBd = 2.14 dBi` |

> 🔴 ⭐⭐ **Bẫy đề kinh điển:** *"Tăng công suất lên 3 dBm"* — **câu này sai về mặt kỹ thuật.**
> Thay đổi thì dùng **dB**. Giá trị tuyệt đối mới dùng **dBm**.
> ⭐ Nhớ: **"m" = mốc = so với 1 mW"** → có "m" là số tuyệt đối. Không có "m" là số chênh lệch.

#### ⭐⭐ QUY TẮC 3 VÀ 10 — học cái này, bỏ máy tính đi

```
   ┌────────────────────────────────────────────────┐
   │   MỐC GỐC:   0 dBm  =  1 mW                    │
   ├────────────────────────────────────────────────┤
   │   + 3 dB   →   CÔNG SUẤT  × 2                  │
   │   − 3 dB   →   CÔNG SUẤT  ÷ 2                  │
   │   +10 dB   →   CÔNG SUẤT  × 10                 │
   │   −10 dB   →   CÔNG SUẤT  ÷ 10                 │
   └────────────────────────────────────────────────┘
```

⭐ **Cách dùng:** đi từ 0 dBm (=1 mW), cộng dồn các bước +3 và +10 cho tới khi ra số cần tìm.

**Ví dụ 1 — 20 dBm bằng bao nhiêu mW?**
```
0 dBm  = 1 mW
+10 dB → 10 dBm = 10 mW        (×10)
+10 dB → 20 dBm = 100 mW       (×10)
                    Đáp án: 100 mW
```

**Ví dụ 2 — 26 dBm bằng bao nhiêu mW?**
```
0 dBm  = 1 mW
+10 → 10 dBm = 10 mW
+10 → 20 dBm = 100 mW
+3  → 23 dBm = 200 mW
+3  → 26 dBm = 400 mW          Đáp án: 400 mW
```

**Ví dụ 3 — 50 mW là bao nhiêu dBm?** (đi ngược)
```
100 mW = 20 dBm
÷2 → 50 mW = 20 − 3 = 17 dBm   Đáp án: 17 dBm
```

#### Bảng tra nhanh — nhớ được 5 dòng in đậm là đủ thi

| dBm | mW | Ghi chú |
|:---:|:---:|---|
| **0** | **1 mW** | ⭐ **Mốc gốc — phải nhớ** |
| 3 | 2 mW | |
| 6 | 4 mW | |
| **10** | **10 mW** | ⭐ Mức công suất thấp nhất AP thường dùng |
| 13 | 20 mW | |
| 17 | 50 mW | ⭐ Mức phổ biến cho AP mật độ cao |
| **20** | **100 mW** | ⭐ **Giới hạn phổ biến cho 2.4 GHz indoor nhiều nước** |
| 23 | 200 mW | |
| 26 | 400 mW | |
| **30** | **1000 mW = 1 W** | ⭐ **Phải nhớ** — giới hạn EIRP nhiều regulatory domain |
| **-30** | 0.001 mW | ⭐ RSSI cực mạnh (đứng sát AP) |
| **-70** | 0.0000001 mW | ⭐ RSSI ngưỡng "dùng được" |

> ⭐ **Vì sao RSSI là số âm?** Vì tín hiệu tới máy client rất nhỏ — nhỏ hơn 1 mW rất nhiều.
> Nhỏ hơn 1 mW → dBm âm. **Số âm càng gần 0 = càng mạnh.** `-40` **mạnh hơn** `-70`.

---

### 3.3 ⭐⭐ EIRP — công thức phải thuộc

> ⭐⭐ **EIRP (Effective Isotropic Radiated Power)** = công suất **thực sự phát ra không trung**,
> tính ở điểm ra khỏi antenna. Đây là con số mà **cơ quan quản lý tần số giới hạn**, không phải công suất máy.

```
   ┌──────────────────────────────────────────────────────────────┐
   │   EIRP (dBm) = Tx Power (dBm) − Cable Loss (dB) + Antenna Gain (dBi)  │
   └──────────────────────────────────────────────────────────────┘

        [ Radio AP ]───── cáp ─────[ Antenna ]  ~~~~~~>  không trung
         Tx = 17 dBm      −2 dB      +6 dBi           EIRP = 21 dBm
```

⭐ **Ba thành phần, ba dấu — nhớ bằng logic chứ đừng học vẹt:**

| Thành phần | Dấu | Vì sao |
|---|:---:|---|
| **Tx Power** (công suất radio) | (gốc) | Điểm xuất phát |
| **Cable / connector loss** | ⭐ **trừ** | Cáp và đầu nối **hao** năng lượng |
| **Antenna gain** | ⭐ **cộng** | Antenna **không tạo thêm** năng lượng — nó **gom lại theo hướng** → theo hướng đó thấy mạnh hơn |

> 🔴 ⭐ **Hiểu đúng "antenna gain":** antenna **không khuếch đại**. Nó **nắn hình** vùng phủ.
> Giống bóp đầu vòi nước: nước không nhiều hơn, nhưng **tia bắn xa hơn** vì hẹp lại.
> ⭐ **Hệ quả: gain càng cao → beamwidth càng hẹp → vùng phủ càng "kén hướng".**

**Bài tập mẫu — làm được 3 câu này là xong mục EIRP:**

<details>
<summary>① AP phát 50 mW, cáp mất 3 dB, antenna 9 dBi. EIRP = ?</summary>

```
50 mW  = 17 dBm   (vì 100 mW = 20 dBm, ÷2 → −3 dB)
EIRP = 17 − 3 + 9 = 23 dBm  =  200 mW
```
⭐ **Đáp án: 23 dBm (200 mW)**
</details>

<details>
<summary>② Quy định cho phép EIRP tối đa 30 dBm. Antenna 12 dBi, cáp mất 2 dB. Tx Power tối đa được đặt là bao nhiêu?</summary>

```
30 = Tx − 2 + 12   →   Tx = 30 + 2 − 12 = 20 dBm  =  100 mW
```
⭐ **Đáp án: 20 dBm (100 mW).** Đặt cao hơn là **vi phạm quy định tần số**.
⭐ Đây chính là lý do WLC bắt bạn khai báo **regulatory domain** và **loại antenna** —
để nó tự chặn không cho đặt Tx quá cao.
</details>

<details>
<summary>③ Đổi antenna từ 3 dBi sang 9 dBi, giữ nguyên mọi thứ khác. EIRP thay đổi thế nào, và vùng phủ thay đổi thế nào?</summary>

```
EIRP tăng 6 dB  →  công suất phát ra tăng ×4  (+3 = ×2, +3 nữa = ×4)
```
⭐ **Nhưng vùng phủ KHÔNG "to gấp 4".** Antenna 9 dBi có **beamwidth hẹp hơn** →
đi **xa hơn theo hướng chính**, nhưng **hụt ở hai bên và bên dưới**.
🔴 ⭐ **Bẫy thực tế:** thay antenna gain cao lên trần nhà thấp → **ngay dưới AP lại yếu đi**
(hiện tượng "vùng chết dưới chân AP").
</details>

---

### 3.4 ⭐⭐ RSSI, Noise floor, SNR — ba số bạn sẽ nhìn mỗi ngày

| Chỉ số | Là gì | Đơn vị | Ai đo |
|---|---|---|---|
| ⭐⭐ **RSSI** (Received Signal Strength Indicator) | Độ mạnh tín hiệu **nhận được** | **dBm** (số âm) | ⭐ Cả AP đo client, và client đo AP — **hai chiều có thể khác nhau!** |
| ⭐ **Noise floor** | Mức "ồn nền" của môi trường (mọi năng lượng RF không phải tín hiệu Wi-Fi bạn cần) | **dBm** (số âm) | AP báo cáo lên WLC |
| ⭐⭐ **SNR** (Signal-to-Noise Ratio) | ⭐ **RSSI − Noise floor** | ⭐ **dB** (số dương, vì là *chênh lệch*) | Tính ra từ 2 số trên |

```
    SNR (dB)  =  RSSI (dBm)  −  Noise floor (dBm)

   Ví dụ:   RSSI = −65 dBm ,  Noise = −92 dBm
            SNR  = −65 − (−92) = 27 dB     → tốt
```

#### ⭐ Bảng ngưỡng thực tế — nhớ 3 mốc in đậm

| RSSI | Chất lượng | Dùng được cho |
|---|---|---|
| −30 → −50 dBm | 🟢 Xuất sắc | Mọi thứ (thường là đang đứng ngay cạnh AP) |
| −50 → −60 dBm | 🟢 Rất tốt | Mọi thứ, kể cả tốc độ cao nhất |
| **−67 dBm** | 🟡 ⭐ **NGƯỠNG THIẾT KẾ CHUẨN** | ⭐ **Voice / Video / roaming mượt.** Thiết kế WLAN nhắm ≥ −67 dBm ở **mọi điểm** |
| −70 dBm | 🟡 Đủ | Data thường, duyệt web. Voice bắt đầu rớt |
| **−80 dBm** | 🟠 ⭐ **Ranh giới** | Kết nối được nhưng tốc độ rất thấp, hay rớt |
| −90 dBm trở xuống | 🔴 Không dùng được | Gần bằng noise floor → SNR ≈ 0 |

| SNR | Chất lượng |
|---|---|
| **≥ 25 dB** | 🟢 ⭐ **Mục tiêu thiết kế.** Đạt được tốc độ cao (MCS cao) |
| 20 – 25 dB | 🟢 ⭐ **Tối thiểu cho Voice** |
| 15 – 20 dB | 🟡 Data ổn, tốc độ trung bình |
| 10 – 15 dB | 🟠 Chậm, hay retry |
| **< 10 dB** | 🔴 ⭐ **Hỏng.** Nhiều lỗi CRC, retransmit liên tục |

> 🔴 ⭐⭐ **Bài học quan trọng nhất mục này:** ⭐ **RSSI mạnh KHÔNG đảm bảo kết nối tốt.**
> Nếu noise floor cũng cao thì SNR vẫn thấp.
> **Ví dụ:** RSSI `−55 dBm` (rất mạnh!) nhưng noise floor `−65 dBm` (rất ồn) → SNR = **10 dB** → 🔴 **tệ**.
> ⭐ **Luôn nhìn SNR, đừng chỉ nhìn vạch sóng.** Đây là câu hỏi rất hay gặp trong đề.

> ⭐ **Noise floor bình thường là bao nhiêu?** Khoảng **−90 đến −95 dBm**.
> Nếu WLC báo noise floor **−80 dBm** → có nguồn nhiễu mạnh gần đó, phải đi tìm (xem §2.7).

---

### 3.5 Điều gì xảy ra với sóng trên đường đi

| Hiện tượng | Nghĩa | Ví dụ đời thật |
|---|---|---|
| ⭐ **Absorption** (hấp thụ) | Vật liệu **nuốt** năng lượng, đổi thành nhiệt | ⭐ **Tường gạch, bê tông, và đặc biệt là NƯỚC** — cơ thể người là túi nước → phòng đông người hút sóng rất mạnh |
| ⭐ **Reflection** (phản xạ) | Sóng dội lại từ bề mặt lớn, nhẵn | Tường kim loại, tủ hồ sơ, thang máy, kính |
| **Refraction** (khúc xạ) | Sóng **bẻ hướng** khi qua môi trường khác mật độ | Qua tường kính dày, qua lớp không khí khác nhiệt độ |
| **Diffraction** (nhiễu xạ) | Sóng **vòng qua** mép vật cản | Vòng qua góc tường → có sóng yếu ở hành lang bên kia |
| **Scattering** (tán xạ) | Sóng tán ra nhiều hướng khi gặp bề mặt gồ ghề / bụi | Trần nhà thô, lưới thép, mưa |
| ⭐⭐ **Multipath** | Cùng 1 tín hiệu tới nơi qua **nhiều đường** → **lệch pha** | ⭐ Hai bản sao lệch pha 180° → **triệt tiêu nhau** → "vùng chết" dù RSSI trên giấy phải tốt |
| **Free Space Path Loss (FSPL)** | Sóng yếu đi theo **bình phương khoảng cách**, ngay cả khi không có vật cản | ⭐ Gấp đôi khoảng cách → mất thêm **6 dB** |

> ⭐ **Multipath — mặt tốt và mặt xấu:**
> · 🔴 Với **802.11a/b/g** (1 antenna): multipath là **kẻ thù**, gây triệt tiêu tín hiệu.
> · 🟢 Với **802.11n trở đi** (MIMO): multipath thành **tài nguyên** — MIMO dùng nhiều antenna để
> **tách các bản sao ra** và ghép lại (MRC), thậm chí gửi **dữ liệu khác nhau** trên từng đường.
> ⭐ **Đây là ý tưởng cốt lõi của MIMO** — xem §3.2.

⭐ **Bảng suy hao thực tế qua vật cản** (số gần đúng, dùng để ước lượng khi khảo sát):

| Vật cản | Suy hao |
|---|:---:|
| Vách thạch cao (drywall) | ~3 dB |
| Cửa gỗ | ~3–4 dB |
| Tường gạch | ~6–8 dB |
| Tường bê tông | ~10–15 dB |
| Kính thường | ~2–3 dB |
| ⭐ Kính low-E / kính phản quang | ⭐ **~25–30 dB** (gần như chặn hẳn — bẫy khi khảo sát tòa nhà mới) |
| Sàn bê tông giữa 2 tầng | ~15–20 dB |
| ⭐ Thang máy / tủ kim loại | ⭐ **~30 dB+** (coi như tường chắn) |
| ⭐ Đám đông người | ⭐ **~3–5 dB** — lý do hội trường phải thiết kế theo *capacity* |

---

### 3.6 ⭐⭐ Band & Channel

#### Bức tranh tổng — ba band Wi-Fi

| Band | Dải tần | Số channel 20 MHz | Ưu | Nhược |
|---|---|:---:|---|---|
| ⭐ **2.4 GHz** | 2.400 – 2.4835 GHz (ISM) | ⭐ **Chỉ 3** không chồng lấn | Đi xa hơn, xuyên vật cản tốt hơn, mọi thiết bị đều hỗ trợ | 🔴 ⭐ **Quá ít channel** · rất đông · nhiễu từ Bluetooth, lò vi sóng, camera |
| ⭐⭐ **5 GHz** | 5.150 – 5.850 GHz (UNII) | ⭐ **~25** (tùy quốc gia) | ⭐ **Nhiều channel** · ít nhiễu · băng thông rộng hơn | Đi gần hơn, xuyên tường kém hơn |
| **6 GHz** (Wi-Fi 6E / 7) | 5.925 – 7.125 GHz | ⭐ Tới **59** | ⭐ Cực rộng, **sạch** (chỉ thiết bị mới được vào) | Chỉ client Wi-Fi 6E trở lên · phủ gần nhất · chưa mở ở mọi nước |

#### ⭐⭐ 2.4 GHz — vì sao là 1, 6, 11

```
  Channel:   1    2    3    4    5    6    7    8    9   10   11
  Center:  2412 2417 2422 2427 2432 2437 2442 2447 2452 2457 2462 (MHz)
             └─ cách nhau chỉ 5 MHz ─┘

  Nhưng MỖI channel rộng ~20–22 MHz:

   ch1  ├──────────────┤
   ch6            ├──────────────┤
   ch11                     ├──────────────┤
        Cách nhau 25 MHz  →  KHÔNG chồng lấn

   ch1  ├──────────────┤
   ch3        ├──────────────┤      CHỒNG LẤN → phá nhau
```

> 🔴 ⭐⭐ **Chỉ có 3 channel không chồng lấn ở 2.4 GHz: 1, 6, 11.**
> (Ở một số nước có ch 12–13 → có thể dùng 1, 5, 9, 13. Nhưng **đề Cisco luôn hỏi 1-6-11**.)

🔴 ⭐ **Sai lầm phổ biến nhất khi tự chỉnh router ở nhà:** đặt channel 3 hoặc 9 "cho tránh hàng xóm".
Kết quả **tệ hơn** — xem §2.7 (ACI tệ hơn CCI).

#### ⭐ 5 GHz — các UNII band và DFS

| UNII band | Dải tần | Channel (20 MHz) | ⭐ DFS? | Ghi chú |
|---|---|---|:---:|---|
| **UNII-1** | 5.150 – 5.250 GHz | 36, 40, 44, 48 | ❌ Không | ⭐ **An toàn nhất** — dùng đầu tiên |
| **UNII-2A** | 5.250 – 5.350 GHz | 52, 56, 60, 64 | ⭐ **Có** | Phải né radar |
| **UNII-2C** (2 Extended) | 5.470 – 5.725 GHz | 100 – 144 | ⭐ **Có** | ⭐ Nhiều channel nhất |
| **UNII-3** | 5.725 – 5.850 GHz | 149, 153, 157, 161, 165 | ❌ Không | ⭐ An toàn, hay dùng cho bridge ngoài trời |

> ⭐⭐ **DFS (Dynamic Frequency Selection)** — bắt buộc ở UNII-2A và UNII-2C, vì các dải này
> **dùng chung với radar** (radar thời tiết, radar quân sự, radar sân bay).
>
> **AP phải làm 2 việc:**
> 1. ⭐ **CAC (Channel Availability Check)** — nghe **60 giây** trước khi phát trên channel DFS
> 2. ⭐ **Nếu phát hiện radar khi đang chạy → PHẢI rời channel trong 10 giây** và không quay lại 30 phút
> 3. 🔴 ⭐ **Ngoại lệ TDWR** — channel **120 / 124 / 128** nằm cạnh **radar thời tiết sân bay**,
>    nên CAC kéo dài **600 giây (10 phút)**, không phải 60 s. AP im lặng 10 phút là **bình thường**, không phải hỏng.

| 🔴 ⭐ Triệu chứng gặp thật với DFS | Giải thích |
|---|---|
| AP đột nhiên đổi channel, **toàn bộ client rớt vài giây** | AP phát hiện radar (thật hoặc giả) → buộc phải nhảy channel |
| AP mất tới **60 giây** mới lên sóng sau khi reboot | Đang chạy CAC trên channel DFS |
| Client cũ / thiết bị IoT **không thấy SSID** dù AP đang phát | ⭐ **Nhiều client rẻ không hỗ trợ channel DFS** — đây là bẫy hay gặp |

⭐ **TPC (Transmit Power Control)** đi kèm DFS trong nhiều regulatory domain — buộc AP giảm công suất khi có thể.

#### ⭐ Channel bonding (độ rộng channel)

| Độ rộng | Số channel 20 MHz gộp | Tốc độ | ⭐ Ảnh hưởng lên SNR | Số channel còn lại ở 5 GHz |
|:---:|:---:|---|---|:---:|
| **20 MHz** | 1 | Cơ bản | Chuẩn | ~25 |
| **40 MHz** | 2 | ~×2 | ⭐ **−3 dB SNR** | ~12 |
| **80 MHz** | 4 | ~×4 | ⭐ **−6 dB SNR** | ~6 |
| **160 MHz** | 8 | ~×8 | ⭐ **−9 dB SNR** | ⭐ **Chỉ 2** |

> 🔴 ⭐⭐ **Đánh đổi cốt lõi — đề rất hay hỏi:**
> **Channel rộng gấp đôi → nhận thêm gấp đôi noise → SNR giảm 3 dB → vùng phủ nhỏ lại
> VÀ số channel dùng được giảm một nửa.**
>
> ⭐ **Nguyên tắc thực tế:**
> · Văn phòng mật độ cao / nhiều AP → ⭐ **20 hoặc 40 MHz**
> · Nhà riêng, ít AP, ít nhiễu → 80 MHz OK
> · ⭐ **160 MHz trong doanh nghiệp = gần như luôn sai** (chỉ còn 2 channel → CCI khủng khiếp)
> · ⭐ **2.4 GHz: LUÔN dùng 20 MHz.** Bonding ở 2.4 GHz nghĩa là chiếm mất 2/3 số channel của cả band.

---

### 3.7 ⭐⭐ Interference vs Noise · CCI vs ACI — 4 khái niệm hay bị lẫn

| Khái niệm | Nguồn | Wi-Fi có "hiểu" nó không? | Hậu quả |
|---|---|---|---|
| ⭐⭐ **CCI** — Co-Channel Interference<br>*(đúng hơn: Co-Channel **Contention**)* | AP/client khác **cùng channel** | ✅ **Có** — nghe được, nên **nhường nhau** | ⭐ **Không hỏng gói, nhưng phải CHỜ** → giảm throughput. Chia airtime |
| 🔴 ⭐⭐ **ACI** — Adjacent Channel Interference | AP/client ở channel **chồng lấn một phần** (VD ch1 và ch3) | ❌ **Không** — nghe thấy năng lượng nhưng không giải mã được | 🔴 ⭐ **Gói bị HỎNG → CRC error → retransmit.** **TỆ HƠN CCI NHIỀU** |
| ⭐ **Non-Wi-Fi Interference** | Lò vi sóng, Bluetooth, camera analog, điện thoại không dây, đèn huỳnh quang hỏng, thiết bị y tế | ❌ Không | Gói hỏng, noise floor tăng vọt |
| ⭐ **Noise** (noise floor) | Nền năng lượng RF tổng hợp của môi trường | ❌ Không | ⭐ Kéo **SNR** xuống → phải hạ tốc độ |

> 🔴 ⭐⭐ **Câu chốt phải nhớ:** ⭐ **CCI làm CHẬM. ACI làm HỎNG.**
> Vì thế **thà nhiều AP chung channel 1 (CCI) còn hơn để một AP ở channel 3 (ACI)**.
> Đây chính là lý do quy tắc **1-6-11** tồn tại — nó **chấp nhận CCI để loại bỏ hoàn toàn ACI**.

⭐ **Cách Cisco xử lý tự động:**

| Tính năng | Làm gì |
|---|---|
| ⭐ **RRM** (Radio Resource Management) | Bộ não tự động: tự chọn channel + công suất cho từng AP |
| ⭐ **DCA** (Dynamic Channel Assignment) | Thành phần của RRM — **chọn channel** tránh CCI/ACI |
| ⭐ **TPC** (Transmit Power Control) | Thành phần của RRM — **chỉnh công suất**, tránh cell quá to |
| ⭐ **CleanAir** | Chip chuyên dụng trên AP Cisco — **nhận diện nguồn nhiễu non-Wi-Fi** ("đây là lò vi sóng", "đây là camera") |
| **EDRRM / ED-RRM** | Event-Driven RRM — thấy nhiễu nặng thì **đổi channel ngay**, không chờ chu kỳ DCA |
| **Coverage Hole Detection** | Phát hiện chỗ client RSSI quá thấp → tăng công suất AP gần đó |

---

### 3.8 ⭐ CSMA/CA — vì sao Wi-Fi không bao giờ nhanh như con số quảng cáo

> 🔴 ⭐⭐ **Sự thật nền tảng nhất về Wi-Fi:** ⭐ **Wi-Fi là HALF-DUPLEX và là môi trường CHIA SẺ.**
> Tại một thời điểm, **trên một channel, trong một vùng nghe được nhau — chỉ MỘT thiết bị được phát.**
> AP và tất cả client **chia nhau** thời gian phát. Ethernet switch full-duplex thì không thế.

**CSMA/CA** = *Carrier Sense Multiple Access with Collision **Avoidance*** — **tránh** đụng độ, chứ không **phát hiện** như Ethernet cũ (CSMA/CD).

⭐ **Vì sao không "phát hiện" được như Ethernet?** Vì radio **không thể vừa phát vừa nghe** trên cùng tần số —
tín hiệu của chính nó át hết. Không nghe được thì không biết mình có đụng ai không → **phải tránh trước**.

```
  Muốn phát 1 frame:
  1. Nghe kênh (Clear Channel Assessment - CCA)
        ├─ Có ai đang phát? → CHỜ
        └─ Rảnh? → tiếp
  2. Chờ hết DIFS (khoảng lặng bắt buộc)
  3. Chờ thêm một số ngẫu nhiên (random backoff)   ← chống 2 máy cùng nhảy vào
  4. Phát frame
  5. CHỜ ACK. Không có ACK trong SIFS → coi như MẤT → phát lại (retry)
```

| Thuật ngữ | Nghĩa |
|---|---|
| ⭐ **CCA** (Clear Channel Assessment) | Hành động "nghe xem kênh có rảnh không" |
| **DIFS / SIFS / PIFS** | Các khoảng lặng bắt buộc. ⭐ **SIFS ngắn nhất** → ACK được ưu tiên chen lên trước |
| ⭐ **NAV** (Network Allocation Vector) | Bộ đếm "kênh sẽ bận thêm bao lâu" — đọc từ trường Duration trong frame người khác. ⭐ *Virtual carrier sense* |
| ⭐ **Random backoff** | Số ngẫu nhiên phải đếm lùi trước khi phát — chống việc mọi máy cùng phát khi kênh vừa rảnh |
| ⭐ **ACK** | ⭐ **Mọi frame unicast 802.11 đều phải được ACK.** Đây là lý do overhead Wi-Fi rất lớn |

> 🔴 ⭐ **Hệ quả phải nhớ cho đề:** ⭐ **Throughput thực tế của Wi-Fi chỉ khoảng 50–60% data rate.**
> "Wi-Fi 6 tốc độ 1.2 Gbps" → thực tế được ~600–700 Mbps, và **chia cho tất cả client trên channel đó**.

#### ⭐ Hidden Node — và RTS/CTS

```
        A  ────── nghe được ──────  AP  ────── nghe được ──────  B
        │                                                        │
        └──────────  A và B KHÔNG nghe thấy nhau  ────────────┘

   → A nghe kênh: "rảnh" (không nghe được B) → phát
   → B nghe kênh: "rảnh" (không nghe được A) → phát
   → Hai gói ĐỤNG NHAU tại AP → cả hai hỏng → cả hai retry → vòng lặp tệ hơn
```

| Vấn đề | Tên | Cách xử lý |
|---|---|---|
| ⭐ 2 client không nghe được nhau nhưng cùng nghe được AP | ⭐ **Hidden node** | ⭐ **RTS/CTS**: xin phép AP trước (RTS), AP phát CTS cho **cả vùng** nghe → mọi người đặt NAV và im lặng |
| Client nghe thấy AP khác nên tưởng bận, dù thật ra không ảnh hưởng | **Exposed node** | Hiếm gặp trong thiết kế Wi-Fi doanh nghiệp |

⭐ **RTS/CTS tốn thêm 2 frame mỗi lần gửi** → chỉ bật khi thật cần (thường cấu hình bằng **RTS threshold**:
chỉ frame lớn hơn ngưỡng mới dùng RTS/CTS).

---

## 📘 4. CHUẨN 802.11

### 4.1 ⭐⭐ Bảng chuẩn — học thuộc bảng này

| Chuẩn | Tên Wi-Fi | Năm | ⭐ Band | Điều chế | Max data rate (lý thuyết) | ⭐ Điểm nhận dạng |
|---|:---:|:---:|:---:|---|---|---|
| 802.11 | — | 1997 | 2.4 | FHSS/DSSS | 2 Mbps | Chuẩn gốc, tuyệt chủng |
| **802.11b** | — | 1999 | ⭐ **2.4** | DSSS / CCK | **11 Mbps** | ⭐ **Chậm nhất còn gặp** — bật nó lên là **kéo cả cell chậm theo** |
| **802.11a** | — | 1999 | ⭐ **5 chỉ** | OFDM | **54 Mbps** | ⭐ 5 GHz **trước cả** 802.11g. Không tương thích b/g |
| **802.11g** | — | 2003 | ⭐ **2.4** | OFDM | **54 Mbps** | ⭐ Tương thích ngược 802.11b |
| **802.11n** | ⭐ **Wi-Fi 4** | 2009 | ⭐ **2.4 + 5** | OFDM, 64-QAM | **600 Mbps** (4 SS, 40 MHz) | ⭐⭐ **Đưa MIMO vào Wi-Fi** · 40 MHz · frame aggregation |
| **802.11ac** | ⭐ **Wi-Fi 5** | 2013 | 🔴 ⭐ **CHỈ 5 GHz** | OFDM, ⭐ **256-QAM** | ⭐ **~6.9 Gbps** (8 SS, 160 MHz) | ⭐⭐ **Wave 2 thêm MU-MIMO (chỉ chiều xuống)** · 80/160 MHz |
| **802.11ax** | ⭐ **Wi-Fi 6**<br>(6 GHz = **Wi-Fi 6E**) | 2019 | ⭐ **2.4 + 5 (+6)** | ⭐ **OFDMA**, 1024-QAM | ⭐ **~9.6 Gbps** | ⭐⭐ **OFDMA · BSS Coloring · TWT · MU-MIMO 2 chiều** |
| 802.11be | Wi-Fi 7 | 2024 | 2.4+5+6 | 4096-QAM | ~46 Gbps | 320 MHz · MLO. ⭐ **Ngoài blueprint** — chỉ cần biết tên |

> 🔴 ⭐⭐ **Ba dòng đề hay gài nhất:**
> 1. ⭐ **802.11a là 5 GHz** (không phải 2.4) — dễ nhầm vì "a" đứng trước "b".
> 2. ⭐ **802.11ac CHỈ có 5 GHz.** Router "AC1200" vẫn phát 2.4 GHz — nhưng phần 2.4 đó là **802.11n**, không phải ac.
> 3. ⭐ **802.11ax quay lại hỗ trợ CẢ 2.4 GHz** — nó là chuẩn đầu tiên sau n làm việc trên cả hai band.

#### ⭐ Amendment "chữ cái nhỏ" — bảng phải biết

| Amendment | Làm gì | Thuộc mục nào |
|---|---|---|
| ⭐ **802.11k** | **Neighbor report** — AP nói cho client biết "các AP hàng xóm ở channel nào" → client roam nhanh, không phải quét mù | ➡️ Roaming (07B) |
| ⭐ **802.11v** | **BSS Transition Management** — WLC **gợi ý** client nên chuyển sang AP nào | ➡️ Roaming (07B) |
| ⭐⭐ **802.11r** | **Fast Transition (FT)** — bỏ qua bước xác thực đầy đủ khi roam → ⭐ **roam < 50 ms, cần cho Voice** | ➡️ Roaming (07B) |
| ⭐ **802.11w** | **Protected Management Frames (PMF)** — ký số frame quản lý → ⭐ chống **deauth attack**. Bắt buộc với **WPA3** | ➡️ Security (07B/M10) |
| **802.11e** | QoS trong Wi-Fi (tiền thân của **WMM**) | ➡️ QoS (M09) |
| **802.11i** | Bảo mật — nền của **WPA2** | ➡️ Security (07B/M10) |
| **802.11h** | ⭐ **DFS + TPC** — cho phép dùng 5 GHz an toàn với radar | §2.6 |
| **802.11d** | Regulatory domain — AP quảng bá "đây là nước nào" | §2.6 |

⭐ **Mẹo nhớ 3 chữ hay lẫn nhất:** **K** = **K**now your neighbors (biết hàng xóm) ·
**V** = ad**V**ise (khuyên nên đi đâu) · **R** = **R**oam fast (chuyển nhanh).
⭐ **Thứ tự dùng: k tìm → v khuyên → r chuyển nhanh.**

---

### 4.2 ⭐⭐ MIMO, Spatial Stream, MU-MIMO, Beamforming — phân biệt cho đúng

| Kỹ thuật | Là gì | Có từ chuẩn |
|---|---|---|
| ⭐ **MIMO** (Multiple In Multiple Out) | Nhiều antenna phát **và** nhiều antenna thu | 802.11n |
| ⭐⭐ **Spatial Multiplexing** | ⭐ Gửi **các luồng dữ liệu KHÁC NHAU** cùng lúc, cùng channel, qua các đường multipath khác nhau. ⭐ **Đây là cái làm tốc độ tăng** | 802.11n |
| **MRC** (Maximal Ratio Combining) | Bên thu **ghép nhiều bản sao** yếu thành một tín hiệu tốt | 802.11n |
| **TxBF** (Transmit Beamforming) | Chỉnh **pha** giữa các antenna để sóng **cộng hưởng đúng tại vị trí client** | 802.11n (chuẩn hóa ở ac) |
| ⭐⭐ **MU-MIMO** (Multi-User MIMO) | ⭐ Phục vụ **NHIỀU CLIENT CÙNG LÚC** bằng các spatial stream khác nhau | ⭐ **802.11ac Wave 2 (chỉ downlink)** → ⭐ **802.11ax (cả 2 chiều)** |
| ⭐⭐ **OFDMA** | ⭐ Chia **một** channel thành nhiều **RU** (Resource Unit) nhỏ, mỗi client một mảnh, **cùng lúc** | ⭐ **802.11ax** |

#### ⭐ Cách đọc ký hiệu MIMO: `4x4:4`

```
   4 x 4 : 4
   │   │   └── số SPATIAL STREAM (số luồng dữ liệu song song)  ← cái quyết định tốc độ
   │   └────── số antenna THU (Receive)
   └────────── số antenna PHÁT (Transmit)
```

> 🔴 ⭐ **Bẫy đề:** ⭐ **Số spatial stream thực dùng = MIN(số SS của AP, số SS của client).**
> AP `4x4:4` gặp điện thoại `1x1:1` → ⭐ **chỉ được 1 spatial stream.**
> Mua AP xịn **không** làm điện thoại nhanh hơn theo cách này — hầu hết điện thoại chỉ 1–2 SS.

#### 🔴 ⭐⭐ MU-MIMO vs OFDMA — đề CỰC hay hỏi phân biệt

| | ⭐ **MU-MIMO** | ⭐ **OFDMA** |
|---|---|---|
| **Chia cái gì?** | ⭐ Chia **KHÔNG GIAN** (spatial stream) | ⭐ Chia **TẦN SỐ** (channel thành các RU nhỏ) |
| **Chuẩn** | 802.11ac Wave 2 (DL) → 802.11ax (DL+UL) | ⭐ **Chỉ 802.11ax** |
| **Hợp với** | ⭐ **Ít client, gói LỚN** (tải file, video) | ⭐ **NHIỀU client, gói NHỎ** (IoT, chat, web, voice) |
| **Giới hạn** | Số client đồng thời ≤ số spatial stream AP | Tới 9 RU nhỏ nhất trên channel 20 MHz |
| **Analogy** | ⭐ **Nhiều làn xe riêng biệt** trên cùng con đường | ⭐ **Một xe tải chở hàng của nhiều người**, mỗi người một ngăn |

> ⭐ **Câu chốt:** ⭐ **OFDMA là tính năng quan trọng nhất của Wi-Fi 6** — vì mạng doanh nghiệp
> thực tế đầy **gói nhỏ**, mà mỗi gói nhỏ trước đây vẫn chiếm **trọn** channel trong một lượt.

---

### 4.3 ⭐ Tính năng riêng của 802.11ax (Wi-Fi 6)

| Tính năng | Giải quyết vấn đề gì |
|---|---|
| ⭐⭐ **OFDMA** | Gói nhỏ chiếm trọn channel → chia RU cho nhiều client cùng lúc |
| ⭐⭐ **BSS Coloring** | ⭐ Gán "màu" (6 bit) cho mỗi BSS. Nghe thấy frame **khác màu** → biết là AP khác → **được phép phát đè** thay vì phải chờ. ⭐ **Giảm tác hại của CCI** |
| ⭐ **TWT** (Target Wake Time) | AP hẹn giờ "lúc X hãy tỉnh dậy" → ⭐ **IoT/cảm biến ngủ lâu, pin bền hơn nhiều** |
| **1024-QAM** | Nhồi nhiều bit hơn mỗi symbol → nhanh hơn ~25% (⭐ nhưng **cần SNR rất cao**) |
| **MU-MIMO uplink** | ac chỉ có downlink; ax thêm chiều lên |
| **Longer OFDM symbol** | Symbol dài 4× → chống multipath tốt hơn → ⭐ hoạt động tốt hơn **ngoài trời** |
| **BSS/Spatial Reuse** | Chỉnh ngưỡng CCA linh hoạt để tái sử dụng không gian |

> ⭐ **Cách nhớ mục tiêu của Wi-Fi 6:** nó **không phải để 1 người tải nhanh hơn**, mà để
> ⭐ **200 người trong hội trường cùng dùng được**. Đây là **hiệu suất môi trường đông**, không phải tốc độ đỉnh.

---

### 4.4 ⭐ Data rate, MCS, và cái bẫy "mandatory rate"

| Khái niệm | Nghĩa |
|---|---|
| **Data rate** | Tốc độ **truyền bit trên không trung** (≠ throughput người dùng thấy) |
| ⭐ **MCS** (Modulation and Coding Scheme) | Bảng đánh số các tổ hợp (điều chế + coding + số SS + channel width). ⭐ **MCS cao = nhanh nhưng cần SNR cao hơn** |
| ⭐ **Dynamic Rate Shifting / Rate Adaptation** | Client **tự hạ tốc độ** khi tín hiệu yếu đi, tự tăng khi tốt lên |
| ⭐ **Mandatory (Required) rate** | Tốc độ mà ⭐ **client BẮT BUỘC hỗ trợ mới được join**. ⭐ Beacon và các frame quản lý gửi ở tốc độ mandatory **thấp nhất** |
| **Supported rate** | Tốc độ được phép dùng nhưng không bắt buộc |
| **Disabled rate** | Tốc độ bị tắt hẳn |

> 🔴 ⭐⭐ **Bẫy quan trọng — "tắt low data rate":**
> Nếu để bật rate 1 Mbps (802.11b):
> · ⭐ **Beacon phát ở 1 Mbps** → mỗi beacon chiếm airtime lâu gấp ~54 lần so với phát ở 54 Mbps
> · ⭐ Client ở rất xa vẫn bám được cell → **kéo dài cell** và **chiếm airtime lâu** cho mỗi gói
> · 🔴 ⭐ **Một client chậm làm chậm CẢ CELL** — vì airtime bị nó chiếm
>
> ⭐ **Thực tế chuẩn:** tắt các rate 1, 2, 5.5, 11 Mbps (802.11b) ở band 2.4 GHz;
> đặt mandatory rate thấp nhất khoảng **12 hoặc 24 Mbps**.
> ⭐ **Đây là một trong những chỉnh sửa hiệu quả nhất, tốn ít công nhất** trong tối ưu WLAN.

---

### 4.5 ⭐ Frame 802.11 — ba loại và quá trình client kết nối

| Loại frame | Ví dụ | Dùng để |
|---|---|---|
| ⭐ **Management** | ⭐ **Beacon**, Probe Request/Response, Authentication, Association Request/Response, Reassociation, Deauthentication, Disassociation, Action | Thiết lập & duy trì quan hệ AP–client |
| ⭐ **Control** | **RTS, CTS, ACK**, Block ACK, PS-Poll | Điều phối truy nhập môi trường |
| **Data** | Data, QoS Data, Null Function | Chở dữ liệu thật |

#### ⭐⭐ Quá trình client join — 4 bước, đề hay hỏi thứ tự

```
   ① DISCOVERY  ─ Client tìm AP
      ├─ Passive scanning : nghe BEACON (AP phát ~10 lần/giây)
      └─ Active scanning  : client gửi PROBE REQUEST → AP trả PROBE RESPONSE
                               (SSID ẩn → phải dùng active scanning)

   ② 802.11 AUTHENTICATION  ─ Chỉ là thủ tục "chào hỏi", KHÔNG phải bảo mật thật
      └─ Open System (gần như luôn dùng)  |  Shared Key (WEP, tuyệt chủng)

   ③ ASSOCIATION  ─ Client xin gia nhập BSS
      └─ AP cấp AID (Association ID)  → giờ client "thuộc về" AP này

   ④ SECURITY  ─ Bảo mật thật xảy ra Ở ĐÂY
      ├─ WPA2/3-Personal : 4-way handshake với PSK
      └─ WPA2/3-Enterprise: 802.1X/EAP với RADIUS  → rồi 4-way handshake
                                                    ↓
   ⑤ (nếu có) DHCP → client có IP → MỚI thật sự dùng được mạng
```

> 🔴 ⭐⭐ **Bẫy đề kinh điển:** *"Client hiện Associated nhưng không vào được mạng"*.
> ⭐ **Associated ≠ Authenticated ≠ có IP.** Bước ② "Authentication" trong 802.11 **không phải**
> xác thực mật khẩu — mật khẩu được kiểm ở bước ④. ⭐ **Câu này cực hay ra.**

⭐ **Vài trường quan trọng trong Beacon** (đề có thể cho xem Wireshark):
SSID · Supported rates · Channel (DS Parameter Set) · ⭐ **BSSID = MAC của radio AP** ·
Beacon interval (mặc định ~102.4 ms) · TIM · Capability info · RSN IE (thông tin bảo mật WPA2/3) · Country (802.11d).

| Thuật ngữ vùng phủ | Nghĩa |
|---|---|
| ⭐ **BSS** (Basic Service Set) | Một AP + các client của nó |
| ⭐ **BSSID** | ⭐ **MAC của radio AP** — mỗi SSID trên mỗi band có **BSSID riêng** |
| ⭐ **SSID** | **Tên** mạng (chuỗi ký tự người đọc được) |
| ⭐ **ESS** (Extended Service Set) | ⭐ **Nhiều AP dùng CHUNG một SSID** → cho phép **roaming** |
| **IBSS / Ad-hoc** | Client nối trực tiếp, không có AP |
| **BSA** | Vùng phủ vật lý của một BSS ("cell") |
| **DS** (Distribution System) | Hạ tầng nối các AP với nhau (thường là mạng có dây) |

> ⭐ **Một AP dual-band phát 3 SSID → có bao nhiêu BSSID?** ⭐ **6** (3 SSID × 2 radio).
> 🔴 ⭐ **Hệ quả thực tế:** mỗi BSSID phát beacon riêng → ⭐ **càng nhiều SSID càng tốn airtime**.
> ⭐ **Nguyên tắc vàng: tối đa 3–4 SSID.** Cần nhiều mạng hơn → dùng **1 SSID + 802.1X gán VLAN động** (Module-10).

---

## 📘 5. ⭐ CLIENT CAPABILITIES & THIẾT KẾ THEO MẬT ĐỘ

*(blueprint 3.3.a "wireless client devices capabilities" + 1.2.c "client density")*

### 5.1 Vì sao phải quan tâm năng lực client

> 🔴 ⭐⭐ **Nguyên tắc số 1 của thiết kế WLAN:** ⭐ **Client là bên yếu, và client quyết định.**
> · ⭐ **Client quyết định khi nào roam** — không phải AP, không phải WLC (WLC chỉ *gợi ý* qua 802.11v)
> · ⭐ **Client quyết định dùng band nào** (AP chỉ *hướng* được qua Band Select)
> · ⭐ **Tốc độ bị giới hạn bởi bên yếu hơn** — thường là client

| Năng lực client cần biết | Ảnh hưởng |
|---|---|
| ⭐ **Số spatial stream** (1x1, 2x2…) | ⭐ Giới hạn trần tốc độ. Điện thoại thường **1–2 SS**, laptop 2–3 SS |
| ⭐ **Dual-band hay chỉ 2.4** | ⭐ Nhiều IoT/máy quét/máy in **chỉ có 2.4 GHz** → không thể ép hết sang 5 GHz |
| ⭐ **Có hỗ trợ DFS channel không** | ⭐ Client rẻ **không thấy** SSID trên channel DFS |
| ⭐ **Hỗ trợ 802.11r/k/v?** | Quyết định roaming có mượt không |
| **Hỗ trợ WPA3 / PMF?** | Bật WPA3-only có thể **loại** thiết bị cũ |
| **Công suất phát của client** | ⭐ Client thường phát **yếu hơn AP** → gây **mất cân bằng** (xem dưới) |

> 🔴 ⭐⭐ **Vấn đề mất cân bằng công suất (asymmetric power) — bẫy thiết kế kinh điển:**
> AP phát 20 dBm, điện thoại phát 12 dBm.
> → ⭐ **Client "nghe" AP rất rõ (vạch đầy) nhưng AP KHÔNG nghe rõ client** → upload hỏng, hay rớt.
> ⭐ **Cách sửa: HẠ công suất AP xuống gần mức client (thường 11–14 dBm indoor).**
> 🔴 ⭐ **Tăng công suất AP là phản xạ sai lầm phổ biến nhất khi "sóng yếu".**

### 5.2 ⭐ Coverage design vs Capacity design

| | **Thiết kế theo COVERAGE** | ⭐ **Thiết kế theo CAPACITY** |
|---|---|---|
| Câu hỏi chính | "Có sóng khắp nơi chưa?" | ⭐ "Bao nhiêu người dùng cùng lúc, cần bao nhiêu Mbps mỗi người?" |
| Cách làm | Ít AP, công suất cao, cell to | ⭐ **Nhiều AP, công suất THẤP, cell NHỎ** |
| Hợp với | Kho hàng, bãi xe, hành lang | ⭐ **Văn phòng, lớp học, hội trường, sân vận động** |
| Kết quả nếu chọn sai | 🔴 Có sóng đầy vạch nhưng **mạng rất chậm** khi đông người | — |

⭐ **Các cần gạt để tăng capacity** (nhớ đủ 6 cái là ăn trọn câu hỏi loại này):

| # | Cách | Vì sao có tác dụng |
|:---:|---|---|
| 1 | ⭐ **Giảm công suất, thêm AP** (cell nhỏ hơn) | Ít client mỗi cell → mỗi client được nhiều airtime hơn |
| 2 | ⭐ **Tắt low data rate (1/2/5.5/11 Mbps)** | Bỏ client "chậm" ăn airtime · cell tự nhỏ lại |
| 3 | ⭐ **Dùng 20 hoặc 40 MHz, KHÔNG dùng 80/160** | Giữ lại nhiều channel → giảm CCI |
| 4 | ⭐ **Band Select / ưu tiên 5 GHz** | Đẩy client dual-band sang band nhiều channel hơn |
| 5 | ⭐ **Giảm số SSID xuống 3–4** | Bớt beacon → trả airtime lại cho dữ liệu |
| 6 | ⭐ **Airtime Fairness** | Không cho một client chậm chiếm airtime quá lâu |
| 7 | **RX-SOP** (Receiver Start of Packet threshold) | Đặt ngưỡng "yếu quá thì bỏ qua" → cell nhỏ và sạch hơn |

---

## 📘 6. ⭐⭐ AP MODES — bảng phải học thuộc (blueprint 3.3.b)

> ⭐ Đây là mục **đề hỏi trực tiếp nhất** trong cả module. Học kỹ bảng này.

| AP Mode | Phục vụ client? | Radio làm gì | ⭐ Dùng khi nào |
|---|:---:|---|---|
| ⭐⭐ **Local** | ✅ Có | Phục vụ client + ⭐ **rời channel quét ~50 ms mỗi 16 giây** (off-channel scanning) để phát hiện rogue/nhiễu | ⭐ **Mặc định.** Dùng cho hầu hết AP trong tòa nhà |
| ⭐⭐ **FlexConnect**<br>*(tên cũ: H-REAP)* | ✅ Có | Như Local, nhưng ⭐ **có thể switch traffic TẠI CHỖ** (local switching) và ⭐ **sống sót khi mất WAN tới WLC** | ⭐ **Chi nhánh / remote site** — WLC ở trung tâm, không muốn traffic chạy vòng về HQ. ➡️ Chi tiết ở **07B** |
| ⭐⭐ **Monitor** | ❌ **Không** | ⭐ **Chỉ THU, không phát.** Quét toàn thời gian mọi channel | ⭐ Chuyên **wIPS / phát hiện rogue / định vị (location)**. AP "hy sinh" để làm cảm biến |
| ⭐ **Sniffer** | ❌ Không | ⭐ **Bắt toàn bộ frame 802.11** trên 1 channel rồi **đóng gói gửi tới máy phân tích** (Wireshark / OmniPeek) | ⭐ **Troubleshoot sâu tầng RF** — khi cần xem chính xác frame trên không trung |
| ⭐ **Rogue Detector** | ❌ Không | 🔴 ⭐ **RADIO TẮT HẲN.** Cắm vào **trunk có dây**, nghe **ARP** để so MAC rogue trên không trung với MAC trên dây | ⭐ Xác định rogue có **thực sự cắm vào mạng có dây của mình** không. *(Đã bỏ trên nhiều nền tảng IOS-XE mới)* |
| ⭐ **SE-Connect**<br>*(Spectrum Expert Connect)* | ❌ Không | ⭐ **Phân tích phổ chuyên sâu** (CleanAir), stream dữ liệu phổ về Cisco Spectrum Expert / Chanalyzer | ⭐ **Săn nguồn nhiễu non-Wi-Fi** — "lò vi sóng nằm ở đâu" |
| ⭐ **Bridge / Mesh** | ✅ (nếu bật) | Nối **AP–AP qua không trung**. ⭐ **RAP** (Root AP, có dây) ↔ ⭐ **MAP** (Mesh AP, không dây) | ⭐ Nối 2 tòa nhà · phủ bãi xe / ngoài trời nơi **không kéo được cáp** |
| **Flex + Bridge** | ✅ Có | ⭐ Mesh **+** FlexConnect (local switching) | Mesh ở chi nhánh xa, muốn traffic switch tại chỗ |
| **Sensor** | ❌ Không | ⭐ AP đóng vai **client giả**, tự kết nối & test dịch vụ (DHCP, DNS, RADIUS, ping…) | ⭐ **DNA Center Assurance** — chủ động phát hiện lỗi trước khi user than phiền |

#### 🔴 ⭐⭐ Ba cặp cực dễ nhầm — đề gài đúng chỗ này

| Cặp | Khác nhau ở đâu |
|---|---|
| ⭐⭐ **Monitor** vs ⭐ **Sniffer** | ⭐ **Monitor**: quét **mọi channel**, mục đích **an ninh** (rogue/wIPS/location), tự xử lý.<br>⭐ **Sniffer**: đứng yên **một channel**, ⭐ **gửi frame thô đi cho người phân tích** — mục đích **troubleshoot** |
| ⭐⭐ **Monitor** vs ⭐ **Rogue Detector** | ⭐ **Monitor**: ⭐ **radio BẬT**, nghe **trên không trung**.<br>⭐ **Rogue Detector**: 🔴 ⭐ **radio TẮT**, nghe **trên DÂY** (ARP qua trunk) |
| ⭐ **Local** vs ⭐ **Monitor** | ⭐ **Local**: phục vụ client, chỉ **tranh thủ** quét 50 ms/16 s.<br>⭐ **Monitor**: **không** phục vụ client, quét **100% thời gian** |

> ⭐ **Mẹo nhớ:** ⭐ **"Sniffer thì đưa cho người khác ngửi"** (gửi capture đi) ·
> ⭐ **"Rogue Detector đi dò dưới ĐẤT (dây), Monitor canh trên TRỜI (sóng)"**.

⭐ **Ngoài ra còn 2 khái niệm hay đi kèm:**

| | Nghĩa |
|---|---|
| ⭐ **Lightweight AP** (LAP / CAPWAP AP) | ⭐ AP "nhẹ dạ" — **phải có WLC** mới hoạt động. Mọi mode ở trên đều nói về loại này |
| ⭐ **Autonomous AP** | ⭐ AP **độc lập**, tự có toàn bộ cấu hình, **không cần WLC**. Quản lý từng cái một → không mở rộng được |
| **Embedded Wireless Controller (EWC)** | ⭐ WLC **chạy ngay trên một AP** trong nhóm — cho site nhỏ, không cần mua WLC riêng |

---

## 📘 7. ⭐⭐ ANTENNA (blueprint 3.3.b)

### 7.1 Hai họ antenna

```
   ═══ OMNIDIRECTIONAL ═══              ═══ DIRECTIONAL ═══

        nhìn từ trên:                        nhìn từ trên:
           ╭───────╮                              ╱▔▔▔╲
          │    ●    │  (360°)                    │  ●  │→→→→  (hẹp)
           ╰───────╯                              ╲___╱

        nhìn từ bên (hình BÁNH RÁN):
           ~~~~●~~~~                    Gom hết năng lượng
              ⚠️                            về MỘT hướng
       Ngay DƯỚI antenna là YẾU
```

| | ⭐ **Omnidirectional** | ⭐ **Directional** |
|---|---|---|
| Hình phủ | ⭐ **Hình bánh rán (donut)** quanh trục antenna | ⭐ **Chùm tia** về một hướng |
| Gain | Thấp: **2 – 6 dBi** | Cao: **6 – 30 dBi** |
| Beamwidth | 360° ngang | Hẹp — càng gain cao càng hẹp |
| ⭐ Dùng khi | ⭐ **Phủ trong nhà**, AP gắn **trần**, phủ đều quanh mình | ⭐ **Bắn xa theo một hướng**: hành lang, kho hàng dài, nối 2 tòa nhà |

### 7.2 ⭐ Bảng các loại antenna — học thuộc

| Loại | Họ | Gain điển hình | Beamwidth | ⭐ Dùng cho |
|---|---|:---:|:---:|---|
| ⭐ **Dipole** ("rubber duck") | Omni | 2 – 5 dBi | 360° ngang | ⭐ AP để bàn, phủ chung phòng nhỏ |
| ⭐ **Omni gắn trần / integrated** | Omni | 3 – 6 dBi | 360° ngang | ⭐ **Loại phổ biến nhất trong văn phòng** |
| ⭐ **Patch / Panel** | Directional | 6 – 14 dBi | ~60 – 90° | ⭐ **Gắn TƯỜNG** phủ vào trong phòng · lối đi kho hàng · khán đài |
| ⭐ **Yagi** | Directional | 10 – 14 dBi | ~30 – 50° | ⭐ Nối **điểm-điểm khoảng cách trung bình** (vài trăm m) |
| ⭐ **Parabolic dish** | Directional | ⭐ **20 – 30 dBi** | ⭐ **< 10° (rất hẹp)** | ⭐ **Bridge ngoài trời khoảng cách XA** (vài km). Phải ngắm rất chính xác |
| **Sector** | Directional | 10 – 17 dBi | 60 – 120° | Chia vùng ngoài trời / sân vận động thành các múi |
| ⭐ **Omni "high-gain" cho trần cao** | Omni dẹt | 6 – 10 dBi | 360° nhưng **mỏng theo chiều dọc** | ⭐ Kho hàng trần **cao**: ép sóng xuống sàn thay vì tỏa lên trần |

> 🔴 ⭐⭐ **Quy luật vàng của antenna — đề hay hỏi dưới dạng tình huống:**
> ⭐ **Gain cao ⟺ beamwidth hẹp.** Không có antenna vừa gain cao vừa phủ rộng.
>
> ⭐ **Ba tình huống mẫu:**
> · *"Cần phủ đều một phòng họp"* → ⭐ **omni gain thấp, gắn trần giữa phòng**
> · *"Cần bắn dọc một hành lang / dãy kệ kho dài"* → ⭐ **patch hoặc yagi**
> · *"Cần nối 2 tòa nhà cách 3 km"* → ⭐ **parabolic dish hai đầu, cùng polarization, có tầm nhìn thẳng**

### 7.3 ⭐ Ba khái niệm phụ nhưng hay ra đề

| Khái niệm | Nghĩa | Vì sao quan trọng |
|---|---|---|
| ⭐ **Radiation pattern** | Biểu đồ vùng phủ, gồm ⭐ **Azimuth (H-plane, nhìn từ trên)** và ⭐ **Elevation (E-plane, nhìn từ bên)** | ⭐ **Phải xem cả HAI.** Nhiều người chỉ xem hình nhìn từ trên rồi ngạc nhiên vì tầng dưới không có sóng |
| ⭐ **Beamwidth** | Góc giữa 2 điểm mà công suất giảm **3 dB** so với hướng chính | Xác định "vùng dùng được" thật sự của antenna |
| ⭐ **Polarization** | Hướng dao động của sóng: **dọc (vertical)** hay **ngang (horizontal)** | 🔴 ⭐ **Hai đầu bridge lệch polarization → mất 20+ dB.** Lỗi kinh điển khi lắp link ngoài trời. ⭐ Wi-Fi indoor thường **vertical** |

> ⭐ **Cắm antenna cũng có bẫy:** AP có nhiều cổng antenna (A/B/C…). ⭐ **Phải cắm đủ và đúng chuỗi** —
> cắm thiếu antenna trên AP MIMO → **mất spatial stream** → tốc độ tụt, và AP có thể báo lỗi.
> ⭐ Với AP dual-band có antenna riêng cho từng band: **cắm nhầm band = phủ sai hoàn toàn**.

## 🧪 PHẦN 3 — NHÌN THẤY NÓ

> ### 👉 **[LAB 07A — Tuần 12: RF thật, bằng thiết bị bạn đang có](Module-07A-LAB.md)**

> ⭐ **Module duy nhất không cần EVE-NG.** Bạn lab bằng chính laptop và Wi-Fi quanh mình.

| LAB | Nội dung | Cần gì | Bắt buộc? |
|---|---|---|:---:|
| **A** | Tính RF trên giấy (8 bài) | Bút + giấy | ⭐⭐ **Có** |
| **B** | Soi Wi-Fi thật bằng `netsh wlan` | Laptop Windows | ⭐⭐ **Có** |
| **C** | Bản đồ channel quanh nhà | Điện thoại Android | ⭐ Nên |
| **D** | Lịch sử roam (`wlanreport`) | Laptop Windows | Nên |
| **E** | 🚀 Nhìn WLC thật | DevNet Sandbox | Tùy chọn |

> ⚠️ **Wireless là khối bạn KHÔNG thể lab bằng EVE-NG** (PC 16 GB không dựng nổi WLC + AP).
> Nhưng bạn **có sẵn một mạng Wi-Fi thật** ngay quanh mình — và nó đủ để chứng minh
> mọi khái niệm RF của Phần 2.
>
> Ở **LAB B bước 4**, bạn sẽ tự tay chứng minh ba thứ mà đề chỉ hỏi bằng chữ:
> **rate shifting** (tín hiệu yếu → tốc độ tự giảm) · **suy hao qua tường** ·
> và ⭐ **cơ thể người hút sóng** — lý do phòng họp đông người phải thiết kế theo *capacity*.

---

## 🏗️ PHẦN 4 — TOPO & KIẾN TRÚC

> Bạn vừa học vật lý sóng. Phần này trả lời: **đặt AP thế nào cho một tòa nhà thật?**

### 4.1 Bản đồ: hai cách thiết kế, hai kết quả khác hẳn

```
   ❌ THIẾT KẾ THEO "COVERAGE"  (sai cho văn phòng)

   ┌────────────────────────────────────────────┐
   │                                            │
   │                  ((( AP )))                │   1 AP công suất MAX
   │              cell rất to                   │   → "có sóng khắp nơi"
   │                                            │   → nhưng 80 người CHIA NHAU
   │   [PC][PC][PC][PC][PC][PC][PC][PC][PC]     │     một kênh duy nhất
   └────────────────────────────────────────────┘   🔴 Vạch đầy, mạng chậm


   ✅ THIẾT KẾ THEO "CAPACITY"  (đúng cho văn phòng)

   ┌────────────────────────────────────────────┐
   │   ((AP))        ((AP))        ((AP))       │   Nhiều AP, công suất THẤP
   │    ch 1          ch 6          ch 11       │   → cell NHỎ
   │  [PC][PC]      [PC][PC]      [PC][PC]      │   → mỗi nhóm một kênh riêng
   └────────────────────────────────────────────┘   ⭐ Mỗi người nhiều airtime hơn
```

### 4.2 Sáu quyết định thiết kế — và sai thì hỏng thế nào

| # | Quyết định | 🔴 Sai thì hỏng thế nào |
|:---:|---|---|
| ① | ⭐⭐ **Sóng yếu thì THÊM AP, đừng tăng công suất** | Tăng Tx → **mất cân bằng với client** (client chỉ phát ~12 dBm) → **upload hỏng, hay rớt** · cell to ra → CCI nặng hơn |
| ② | **2.4 GHz chỉ dùng channel 1, 6, 11** | Dùng channel 3 hay 9 → **ACI** (gói bị **hỏng**), tệ hơn CCI (chỉ **chờ**) |
| ③ | **Dùng 20 hoặc 40 MHz, không dùng 80/160** | 160 MHz → chỉ còn **2 channel** ở 5 GHz, và **SNR giảm 9 dB** |
| ④ | **Tắt data rate thấp (1/2/5.5/11 Mbps)** | Để bật → client chậm **chiếm airtime rất lâu** → làm chậm **cả cell** |
| ⑤ | **Tối đa 3–4 SSID** | Mỗi SSID × mỗi band = một BSSID phát beacon riêng → 8 SSID = **80 beacon/giây** ăn airtime |
| ⑥ | **Thiết kế RSSI ≥ −67 dBm ở MỌI điểm** | Dưới ngưỡng này → roaming không mượt, voice rớt |

### 4.3 Ba sự thật mà chỉ người đi làm mới biết

| Sự thật | Giải thích |
|---|---|
| ⭐⭐ **RSSI mạnh KHÔNG đảm bảo kết nối tốt** | RSSI `−55` (rất mạnh) + noise floor `−65` (rất ồn) = **SNR chỉ 10 dB** = tệ. ⭐ **Luôn nhìn SNR, đừng nhìn vạch sóng** |
| ⭐⭐ **Mất cân bằng công suất AP–client** | AP phát 20 dBm, điện thoại phát 12 dBm → client **nghe AP rõ** nhưng **AP không nghe rõ client** → upload hỏng. ⭐ **Cách sửa là HẠ công suất AP**, không phải tăng |
| ⭐ **Antenna gain cao ⟺ beamwidth HẸP** | Antenna **không tạo thêm năng lượng** — nó **nắn hình**. Đổi sang antenna gain cao trên trần thấp → **xuất hiện vùng chết ngay dưới AP** |

### 4.4 Những thứ này sẽ lớn lên thành gì

| Bạn vừa học | Sẽ thành | Ở module |
|---|---|---|
| RSSI, SNR, cell overlap | Điều kiện để **roaming** mượt (≥ −67 dBm, overlap 15–20%) | **Module-07B §6** |
| AP mode (9 loại) | FlexConnect · Fabric AP của SD-Access | **Module-07B · Module-09** |
| Client density, capacity | Thiết kế WLAN (1.2.a/b/c) · location services | **Module-09 §4** |
| CSMA/CA, airtime | **WMM / QoS không dây** — 4 access category | **Module-09 §8.7** |

### 4.5 Vẽ lại để nhớ

> **Bài tập 15 phút, trên giấy.**
>
> 1. Vẽ một tầng văn phòng 40m × 20m, đặt AP theo kiểu **capacity**
> 2. Gán channel 2.4 GHz cho từng AP (chỉ dùng 1, 6, 11) sao cho **không AP kề nhau nào trùng**
> 3. Trả lời: *"Người dùng kêu sóng yếu ở góc phòng. Sếp bảo tăng công suất AP lên max. Giải thích trong 3 câu vì sao đó là ý tồi."*

<details>
<summary>Đáp án câu 3</summary>

1. ⭐ **Mất cân bằng công suất:** client chỉ phát ~12 dBm. AP hét 23 dBm thì client
   **nghe rõ AP nhưng AP không nghe rõ client** → upload hỏng, hay rớt kết nối.
2. ⭐ **Cell to ra → CCI nặng hơn:** nhiều client hơn phải chia nhau cùng airtime,
   và cell chồng lấn AP hàng xóm.
3. ⭐ **Client bám dai (sticky):** giữ AP cũ lâu hơn thay vì roam sang AP gần → tốc độ tệ khi di chuyển.

⭐ **Giải pháp đúng: thêm AP, giảm công suất, cell nhỏ lại.**

</details>

---

## 💡 4.6 Thực chiến đi làm

> ⭐ Phần này **không có trong đề** nhưng là lý do bạn học wireless. Đọc 15 phút.

| # | Tình huống thật | ⭐ Điều người mới làm sai | ⭐ Cách làm đúng |
|:---:|---|---|---|
| 1 | *"Sóng yếu quá, tăng công suất AP lên đi"* | 🔴 Tăng Tx power lên max | ⭐ **Ngược lại: thường phải GIẢM.** Tăng Tx làm mất cân bằng với client (§4.1) và làm cell to ra → **CCI nặng hơn**. Thiếu sóng thì **thêm AP**, không phải hét to hơn |
| 2 | *"Wi-Fi chậm mà vạch vẫn đầy"* | Đổ lỗi cho ISP | ⭐ Xem **SNR** và **số client/AP**, không xem RSSI. Vạch đầy + SNR thấp = **nhiễu**; vạch đầy + SNR tốt + vẫn chậm = **quá tải airtime** |
| 3 | Công ty muốn 8 SSID (mỗi phòng ban 1 cái) | Tạo đủ 8 | 🔴 ⭐ **Từ chối.** 8 SSID × 2 band = 16 BSSID beacon → ăn hết airtime. ⭐ Dùng **1–2 SSID + 802.1X gán VLAN động** (Module-10) |
| 4 | Kho hàng trần cao 12 m, sóng dưới sàn yếu | Gắn omni thường lên trần | ⭐ Dùng ⭐ **omni high-gain dẹt** hoặc **patch hướng xuống** — ép năng lượng xuống sàn (§6.2) |
| 5 | Máy quét mã vạch / máy in cũ không thấy SSID | Nghĩ thiết bị hỏng | ⭐ Kiểm tra: (a) thiết bị **chỉ có 2.4 GHz**? (b) AP đang ở **channel DFS**? (c) đã **tắt rate thấp** mà thiết bị chỉ hỗ trợ 11 Mbps? |
| 6 | Bật Wi-Fi cho phòng họp 100 người | Đặt 1 AP xịn ở giữa | 🔴 ⭐ Sai. ⭐ **Nhiều AP công suất thấp** + 20/40 MHz + tắt rate thấp (§4.2). Một AP = **một phòng họp cho 100 người nói lần lượt** |
| 7 | Link bridge 2 tòa nhà mới lắp, tín hiệu tệ | Đổi antenna to hơn | ⭐ Kiểm tra trước: ⭐ **polarization có khớp không** · có **line-of-sight** không · **ngắm đúng hướng** chưa (dish beamwidth < 10°!) |
| 8 | Người dùng đi từ phòng này sang phòng kia thì cuộc gọi rớt | Nghĩ do AP yếu | ⭐ Vấn đề **roaming** — cần **RSSI ≥ −67 dBm ở mọi điểm**, có vùng chồng lấn giữa các cell, và bật **802.11r/k/v**. ➡️ **Module-07B** |
| 9 | AP tự đổi channel lúc nửa đêm, user báo rớt mạng | Nghĩ AP lỗi | ⭐ **DFS** phát hiện radar (§2.6), hoặc **DCA** chạy chu kỳ. Xem log WLC. Nếu bị liên tục → **loại channel DFS ra khỏi DCA list** |
| 10 | Lắp AP mới, tốc độ thấp hơn AP cũ | Nghi AP lỗi | ⭐ Đếm lại **số antenna đã cắm** (§6.3) và kiểm tra ⭐ **cắm đúng band chưa** · kiểm tra PoE có đủ công suất không (AP Wi-Fi 6 thường cần **PoE+ / 802.3at**) |

> 🔴 ⭐⭐ **Ba câu thần chú của người làm wireless:**
> 1. ⭐ **"Sóng yếu thì thêm AP, đừng tăng công suất."**
> 2. ⭐ **"Nhìn SNR, đừng nhìn vạch."**
> 3. ⭐ **"Ít SSID, nhiều channel, cell nhỏ."**

---

# 📎 PHỤ LỤC — TRA CỨU

> 🔴 **KHÔNG đọc phần này ở lần học đầu tiên.**
>
> | Khi nào | Mở mục nào |
> |---|---|
> | Đang lab mà lỗi | **Gỡ lỗi nhanh** (§11) — ⭐ quy trình chẩn đoán RF 5 bước |
> | Quên lệnh | **Hộp lệnh** (§11.1) |
> | Tuần 20, ôn thi | **Bẫy đề** (§10) + **Quiz** (§12) |
> | Gặp từ lạ | **Thuật ngữ** (§13) |
> | Tự chấm | **Đúc kết** (§14) |

---

## 🎓 10. BẪY TRONG ĐỀ ENCOR

| # | ⭐ Bẫy | ✅ Sự thật |
|:---:|---|---|
| 1 | "802.11a chạy ở 2.4 GHz" | 🔴 ⭐ **SAI. 802.11a là 5 GHz.** Chữ cái không theo thứ tự tần số |
| 2 | "802.11ac hỗ trợ cả 2.4 và 5 GHz" | 🔴 ⭐ **SAI. ac CHỈ 5 GHz.** Phần 2.4 của router "AC…" là **802.11n** |
| 3 | "802.11ax chỉ ở 6 GHz" | 🔴 **SAI.** ax chạy ⭐ **2.4 + 5**, và **6 GHz khi là Wi-Fi 6E** |
| 4 | "2.4 GHz có 11 channel nên dùng được 11" | 🔴 ⭐ **Chỉ 3 không chồng lấn: 1, 6, 11** |
| 5 | "Tăng công suất AP lên 3 dBm" | 🔴 ⭐ Thay đổi thì dùng **dB**, không phải **dBm** |
| 6 | "EIRP = Tx + cable loss + antenna gain" | 🔴 ⭐ **Cable loss phải TRỪ:** `EIRP = Tx − loss + gain` |
| 7 | "SNR đơn vị là dBm" | 🔴 ⭐ **SNR là dB** (hiệu của hai dBm → ra dB) |
| 8 | "RSSI −80 mạnh hơn −60" | 🔴 ⭐ **SAI. Số âm càng GẦN 0 càng mạnh.** −60 mạnh hơn −80 |
| 9 | "ACI nhẹ hơn CCI vì chỉ chồng một phần" | 🔴 ⭐⭐ **NGƯỢC LẠI. ACI tệ hơn** — gói bị **hỏng**, không chỉ **chờ** |
| 10 | "Dùng 160 MHz để mạng doanh nghiệp nhanh hơn" | 🔴 ⭐ Còn **2 channel** → CCI khủng khiếp, SNR −9 dB. ⭐ Doanh nghiệp dùng **20/40** |
| 11 | "MU-MIMO và OFDMA là một" | 🔴 ⭐⭐ **MU-MIMO chia KHÔNG GIAN, OFDMA chia TẦN SỐ.** OFDMA **chỉ có ở 802.11ax** |
| 12 | "MU-MIMO có từ 802.11n" | 🔴 ⭐ **802.11ac Wave 2** (downlink) · ⭐ **802.11ax** thêm uplink |
| 13 | "AP 4x4:4 làm điện thoại nhanh gấp 4" | 🔴 ⭐ **SS thực = MIN(AP, client).** Điện thoại 1–2 SS thì chỉ được 1–2 |
| 14 | "Rogue Detector quét trên sóng" | 🔴 ⭐⭐ **Radio TẮT.** Nó nghe **ARP trên dây** qua trunk |
| 15 | "Monitor mode và Sniffer mode giống nhau" | 🔴 ⭐ **Monitor** = quét mọi channel, cho **an ninh**. ⭐ **Sniffer** = một channel, **gửi capture** cho máy phân tích |
| 16 | "Local mode AP chỉ phục vụ client, không quét" | 🔴 ⭐ **Có quét** — off-channel **~50 ms mỗi 16 giây** |
| 17 | "Antenna gain cao thì phủ rộng hơn" | 🔴 ⭐⭐ **Gain cao ⟺ beamwidth HẸP.** Xa hơn nhưng **hẹp hơn** |
| 18 | "0 dBd = 0 dBi" | 🔴 ⭐ **0 dBd = 2.14 dBi** |
| 19 | "Client Associated là đã vào được mạng" | 🔴 ⭐⭐ **Associated ≠ đã xác thực ≠ có IP.** Còn 4-way handshake và DHCP |
| 20 | "802.11 Authentication là xác thực mật khẩu" | 🔴 ⭐ **Không.** Đó chỉ là thủ tục chào hỏi. Mật khẩu kiểm ở **4-way handshake / 802.1X** |
| 21 | "SSID và BSSID giống nhau" | 🔴 ⭐ **SSID = tên. BSSID = MAC của radio AP.** 1 SSID có thể có **rất nhiều** BSSID (= ESS) |
| 22 | "WLC quyết định client roam khi nào" | 🔴 ⭐⭐ **CLIENT quyết định.** WLC chỉ **gợi ý** (802.11v) |
| 23 | "DFS chỉ là tính năng tùy chọn" | 🔴 ⭐ **Bắt buộc** ở UNII-2A và UNII-2C. Có radar → **rời channel trong 10 giây** |
| 24 | "Tắt low data rate làm mạng chậm đi" | 🔴 ⭐ **Ngược lại** — nó **giải phóng airtime** và thu nhỏ cell |
| 25 | "Wi-Fi là full-duplex như switch" | 🔴 ⭐⭐ **Half-duplex, môi trường chia sẻ.** Đây là gốc của mọi giới hạn Wi-Fi |
| 26 | "Nhiều SSID thì linh hoạt hơn, không hại gì" | 🔴 ⭐ Mỗi BSSID **phát beacon riêng** → tốn airtime. ⭐ **Tối đa 3–4 SSID** |
| 27 | "BSS Coloring làm tăng tốc độ" | 🔴 ⭐ Nó **giảm tác hại của CCI** (cho phép phát đè khi khác màu), không tăng tốc độ đỉnh |

---

## 🐛 11. GỠ LỖI NHANH — tầng RF

### 11.1 ⭐ Hộp lệnh / công cụ vạn năng

```
═══ TRÊN MÁY WINDOWS (client) ═══
netsh wlan show interfaces                    ! SSID/BSSID/channel/rate/signal hiện tại
netsh wlan show networks mode=bssid           ! Mọi AP xung quanh + channel + band
netsh wlan show drivers                       ! Card này hỗ trợ chuẩn gì, có PMF không
netsh wlan show wlanreport                    ! Báo cáo HTML — lịch sử roam & rớt

═══ TRÊN MACOS ═══
! Giữ Option + click icon Wi-Fi → xem RSSI, noise, channel ngay
/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I

═══ TRÊN LINUX ═══
iw dev wlan0 link          ! kết nối hiện tại + signal
iw dev wlan0 scan | grep -E "SSID|signal|freq"
iwconfig                   ! (cũ) link quality, signal level

═══ TRÊN WLC (Catalyst 9800 / IOS-XE) — sẽ dùng nhiều ở 07B ═══
show ap summary                               ! danh sách AP + mode + channel
show ap dot11 5ghz summary                    ! channel, Tx power từng AP
show wireless client summary                  ! danh sách client
show wireless client mac-address <MAC> detail ! RSSI, SNR, data rate của 1 client
show ap auto-rf dot11 5ghz                    ! thông tin RRM: noise, interference, channel
```

### 11.2 ⭐⭐ Bảng: triệu chứng → nguyên nhân → cách sửa

| 🔴 Triệu chứng | ⭐ Nguyên nhân thường gặp | ✅ Cách kiểm chứng / sửa |
|---|---|---|
| ⭐ **Vạch đầy nhưng mạng chậm** | (a) SNR thấp do nhiễu · (b) quá nhiều client trên cell · (c) CCI | ⭐ Xem **SNR** (không xem RSSI) · đếm client/AP · xem noise floor. Noise > −85 → đi tìm nguồn nhiễu (CleanAir / SE-Connect) |
| ⭐ **Download nhanh, upload tệ, hay rớt** | 🔴 ⭐ **Mất cân bằng công suất** — AP hét to, client nói nhỏ | ⭐ **Giảm Tx power AP** xuống 11–14 dBm indoor |
| ⭐ **Sóng yếu ở một góc phòng** | Vật cản (kính low-E, thang máy, tủ kim loại) hoặc multipath | ⭐ Đo bằng LAB B tại chỗ · thêm AP · đổi vị trí, **đừng tăng công suất** |
| ⭐ **Client rớt khi đi lại** | Thiếu vùng chồng lấn giữa các cell · client "sticky" · thiếu 802.11r/k/v | ⭐ Thiết kế **RSSI ≥ −67 dBm ở mọi điểm** · bật 11r/k/v → **Module-07B** |
| ⭐ **Thiết bị cũ không thấy SSID** | (a) chỉ hỗ trợ 2.4 GHz · (b) AP ở **channel DFS** · (c) đã tắt data rate mà nó cần · (d) bật **WPA3-only** | ⭐ Kiểm tra từng cái theo thứ tự này |
| ⭐ **AP tự đổi channel, user rớt vài giây** | ⭐ **DFS** phát hiện radar · hoặc **DCA/ED-RRM** chạy | ⭐ Xem log WLC. Bị liên tục → **loại channel DFS** khỏi DCA list |
| ⭐ **AP mất tới 60 s mới lên sóng sau reboot** (🔴 tới **10 phút** nếu là channel **120/124/128**) | ⭐ **CAC** trên channel DFS — TDWR cần 600 s (bình thường!) | Không phải lỗi. Muốn nhanh → dùng UNII-1/UNII-3 |
| ⭐ **Noise floor cao bất thường (> −85 dBm)** | Nguồn nhiễu non-Wi-Fi: lò vi sóng, camera analog, điện thoại DECT, đèn hỏng, thiết bị y tế | ⭐ Bật **CleanAir** · đặt 1 AP sang **SE-Connect mode** để định vị nguồn nhiễu |
| ⭐ **Nhiều CRC error / retry rate cao** | 🔴 ⭐ **ACI** (channel chồng lấn) hoặc **hidden node** | ⭐ Kiểm tra channel plan có đúng **1-6-11** không · cân nhắc **RTS/CTS** |
| ⭐ **Tốc độ thấp dù đứng gần AP** | (a) client ít spatial stream · (b) thiếu antenna trên AP · (c) channel width nhỏ · (d) MCS bị hạ do SNR | ⭐ `netsh wlan show drivers` xem năng lực client · kiểm tra antenna đã cắm đủ chưa |
| ⭐ **AP không lên nguồn / reboot liên tục** | ⭐ **PoE không đủ công suất** (AP Wi-Fi 6 cần 802.3at/PoE+, có loại cần 802.3bt) | Kiểm tra ngân sách PoE trên switch (`show power inline`) |
| ⭐ **Chỉ 2.4 GHz hoạt động, 5 GHz không thấy** | Client không hỗ trợ · AP tắt radio 5 GHz · channel DFS · regulatory domain sai | ⭐ `netsh wlan show networks mode=bssid` xem AP có phát 5 GHz không |

### 11.3 ⭐ Quy trình chẩn đoán RF — 5 bước

```
① CLIENT hay MẠNG?
   → Thử 1 client khác cùng chỗ. Chỉ 1 máy lỗi → vấn đề ở client (driver/năng lực/nguồn)

② TÍN HIỆU có đủ không?     → RSSI ≥ −67 dBm?
   → Không đủ  → vấn đề COVERAGE: thêm AP / đổi vị trí / đổi antenna

③ TÍN HIỆU có SẠCH không?   → SNR ≥ 20–25 dB? Noise floor ≤ −85 dBm?
   → Không sạch → vấn đề NHIỄU: CleanAir / SE-Connect / đổi channel

④ KÊNH có ĐÔNG không?       → Bao nhiêu BSSID cùng channel? Channel utilization %?
   → Đông      → vấn đề CAPACITY: thêm AP + giảm công suất + tắt rate thấp + bớt SSID

⑤ HAI CHIỀU có CÂN không?   → Client nghe AP tốt mà AP nghe client kém?
   → Lệch      → GIẢM Tx power của AP
```

> ⭐ **Nhớ đúng thứ tự này** — nó ngăn bạn khỏi sai lầm số 1: nhảy ngay vào "tăng công suất".

---

## 📝 12. QUIZ TỰ KIỂM TRA

**1.** AP phát 17 dBm, cáp mất 3 dB, antenna 10 dBi. EIRP bằng bao nhiêu dBm và mW?
<details><summary>Đáp án</summary>

`EIRP = 17 − 3 + 10 = ` ⭐ **24 dBm**.
Đổi: 20 dBm=100 mW → +3=23 dBm=200 mW → +1 dB ≈ ×1.25 → ⭐ **≈250 mW**.
</details>

**2.** RSSI = −58 dBm, noise floor = −72 dBm. SNR là bao nhiêu? Kết nối này tốt hay xấu? Vì sao?
<details><summary>Đáp án</summary>

`SNR = −58 − (−72) = ` ⭐ **14 dB**.
🔴 ⭐ **Xấu**, mặc dù RSSI **rất mạnh**. Vì ⭐ **noise floor −72 dBm là cao bất thường**
(bình thường −90 đến −95) → có **nguồn nhiễu mạnh** ở gần.
⭐ **Đây là bài học cốt lõi: RSSI mạnh không có nghĩa là kết nối tốt.**
</details>

**3.** Vì sao 2.4 GHz chỉ có 3 channel không chồng lấn, dù có tới 11–13 channel?
<details><summary>Đáp án</summary>

⭐ Channel cách nhau chỉ **5 MHz**, nhưng mỗi channel **rộng 20–22 MHz**.
→ Cần cách nhau **ít nhất 5 số channel** mới không chồng → ⭐ **1, 6, 11**.
</details>

**4.** CCI và ACI — cái nào tệ hơn, và vì sao?
<details><summary>Đáp án</summary>

🔴 ⭐⭐ **ACI tệ hơn.**
· ⭐ **CCI** (cùng channel): các thiết bị **nghe hiểu nhau** → **nhường nhau** (CSMA/CA) → chỉ **chậm**, gói vẫn nguyên.
· ⭐ **ACI** (chồng lấn một phần): **không giải mã được nhau** → phát đè → ⭐ **gói HỎNG** → CRC error → retransmit.
⭐ Vì thế 1-6-11 **chấp nhận CCI để loại bỏ ACI**.
</details>

**5.** Kể tên 4 AP mode **không phục vụ client** và mỗi cái dùng để làm gì.
<details><summary>Đáp án</summary>

| Mode | Dùng để |
|---|---|
| ⭐ **Monitor** | Quét mọi channel toàn thời gian — rogue detection, wIPS, location |
| ⭐ **Sniffer** | Bắt frame 802.11 trên **một** channel, **gửi tới máy phân tích** (Wireshark) |
| ⭐ **Rogue Detector** | 🔴 ⭐ **Radio TẮT** — nghe **ARP trên dây** qua trunk để đối chiếu MAC rogue |
| ⭐ **SE-Connect** | Phân tích **phổ** (CleanAir) — tìm nguồn nhiễu non-Wi-Fi |

*(Sensor mode cũng không phục vụ client — nó đóng vai client giả để test dịch vụ cho DNA Center Assurance.)*
</details>

**6.** Phân biệt MU-MIMO và OFDMA.
<details><summary>Đáp án</summary>

| | MU-MIMO | OFDMA |
|---|---|---|
| Chia gì | ⭐ **Không gian** (spatial stream) | ⭐ **Tần số** (Resource Unit) |
| Chuẩn | 802.11ac Wave 2 (DL) → 802.11ax (DL+UL) | ⭐ **Chỉ 802.11ax** |
| Hợp với | Ít client, gói **lớn** | ⭐ Nhiều client, gói **nhỏ** |

⭐ Analogy: MU-MIMO = **nhiều làn xe riêng**; OFDMA = **một xe tải nhiều ngăn**.
</details>

**7.** Một AP dual-band phát 4 SSID. Có bao nhiêu BSSID? Điều đó ảnh hưởng gì?
<details><summary>Đáp án</summary>

⭐ **8 BSSID** (4 SSID × 2 radio).
⭐ Mỗi BSSID **phát beacon riêng** (~10 lần/giây) → 🔴 **80 beacon/giây chỉ để quảng bá tên mạng**,
ăn mất airtime lẽ ra dành cho dữ liệu.
⭐ **Nguyên tắc: tối đa 3–4 SSID.** Cần phân tách nhiều hơn → **1 SSID + 802.1X gán VLAN động**.
</details>

**8.** Client kết nối vào WLAN. Sắp xếp đúng thứ tự: Association · 4-way handshake · Probe/Beacon · 802.11 Authentication · DHCP.
<details><summary>Đáp án</summary>

⭐ **Probe/Beacon (discovery) → 802.11 Authentication → Association → 4-way handshake (security) → DHCP**

🔴 ⭐ **Bẫy:** bước "802.11 Authentication" **không** kiểm mật khẩu — nó chỉ là thủ tục chào hỏi (Open System).
⭐ Mật khẩu được kiểm ở **4-way handshake** (PSK) hoặc **802.1X/EAP** (Enterprise), tức là **SAU** khi Associated.
</details>

**9.** Vì sao dùng channel 160 MHz trong văn phòng thường là quyết định sai?
<details><summary>Đáp án</summary>

Ba lý do:
1. ⭐ **Chỉ còn 2 channel 160 MHz** ở 5 GHz → các AP buộc phải trùng channel → 🔴 **CCI nặng**
2. ⭐ **SNR giảm 9 dB** so với 20 MHz (mỗi lần gấp đôi độ rộng = −3 dB) → **vùng phủ nhỏ lại**
3. ⭐ Phần lớn channel 160 MHz **nằm trong dải DFS** → nguy cơ radar buộc đổi channel + client cũ không thấy

⭐ Văn phòng nên dùng **20 hoặc 40 MHz**.
</details>

**10.** Người dùng báo "vạch sóng đầy nhưng mạng rất chậm". Bạn kiểm tra theo thứ tự nào?
<details><summary>Đáp án</summary>

⭐ Theo quy trình 5 bước §11.3:
1. **Client hay mạng?** — thử máy khác cùng chỗ
2. **RSSI** ≥ −67? (ở đây có vẻ đủ)
3. ⭐ **SNR** ≥ 20–25 dB? **Noise floor** ≤ −85? → nếu noise cao → **nhiễu** → CleanAir/SE-Connect
4. ⭐ **Channel utilization / số client trên cell** → nếu cao → **capacity**: thêm AP, giảm công suất, tắt rate thấp, bớt SSID
5. ⭐ **Cân bằng hai chiều** — upload tệ hơn download → **giảm Tx power AP**

🔴 ⭐ **Điều KHÔNG được làm đầu tiên: tăng công suất AP.**
</details>

**11.** Antenna nào cho: (a) phòng họp vuông, AP gắn trần giữa phòng; (b) hành lang dài 80 m; (c) nối 2 tòa nhà cách 4 km?
<details><summary>Đáp án</summary>

| Tình huống | Antenna | Vì sao |
|---|---|---|
| (a) Phòng họp, gắn trần | ⭐ **Omni gain thấp (3–6 dBi)** | Cần phủ **đều 360°** quanh AP |
| (b) Hành lang dài | ⭐ **Patch hoặc Yagi** (directional) | Cần **bắn dọc** một hướng, không phí năng lượng vào tường hai bên |
| (c) Bridge 4 km | ⭐ **Parabolic dish 20–30 dBi hai đầu** | Cần gain rất cao. ⚠️ Phải **line-of-sight**, **ngắm chính xác** (beamwidth < 10°), **cùng polarization** |
</details>

**12.** `netsh wlan show interfaces` cho `Signal: 62%`. Ước tính RSSI theo dBm. Đủ cho cuộc gọi thoại không?
<details><summary>Đáp án</summary>

⭐ `dBm ≈ (62/2) − 100 = 31 − 100 = ` ⭐ **−69 dBm**.
⭐ **Chưa đạt** ngưỡng thiết kế Voice là ⭐ **−67 dBm**. Gọi được nhưng dễ rớt khi di chuyển.
⭐ Muốn chắc chắn còn phải xem **SNR ≥ 20–25 dB** nữa.
</details>

**13.** Vì sao "tắt data rate thấp" lại **tăng** hiệu năng WLAN?
<details><summary>Đáp án</summary>

⭐ Ba lý do:
1. ⭐ **Beacon và frame quản lý được phát ở mandatory rate thấp nhất.** Ở 1 Mbps, một beacon chiếm airtime lâu hơn ~54 lần so với 54 Mbps
2. ⭐ **Client ở xa không bám cell được nữa** → **cell tự nhỏ lại** → bớt CCI, và client đó bị đẩy sang AP gần hơn
3. 🔴 ⭐ **Một client chậm chiếm airtime rất lâu cho mỗi gói** → làm chậm **cả cell** (Wi-Fi là môi trường chia sẻ)
</details>

**14.** DFS là gì, áp dụng ở đâu, và gây ra 2 hiện tượng lạ nào trong vận hành?
<details><summary>Đáp án</summary>

⭐ **DFS (Dynamic Frequency Selection)** — bắt buộc ở ⭐ **UNII-2A (52–64)** và ⭐ **UNII-2C (100–144)** vì
dải này **dùng chung với radar**.

⭐ AP phải: (1) ⭐ **CAC — nghe 60 giây** trước khi phát (🔴 **channel 120/124/128 — TDWR: 600 giây**) · (2) ⭐ **phát hiện radar → rời channel trong 10 giây**, không quay lại 30 phút.

⭐ Hai hiện tượng lạ trong vận hành:
1. ⭐ AP **mất tới 60 giây mới lên sóng** sau reboot (đang chạy CAC)
2. ⭐ AP **đột ngột đổi channel, client rớt vài giây** (phát hiện radar)
*(Thứ ba, hay gặp: ⭐ **client rẻ/IoT không hỗ trợ DFS → không thấy SSID**)*
</details>

**15.** Client nói "Wi-Fi yếu", sếp bảo "tăng công suất AP lên max". Giải thích trong 3 câu vì sao đó là ý tồi.
<details><summary>Đáp án</summary>

1. ⭐ **Mất cân bằng công suất:** client chỉ phát ~12 dBm. AP hét 23 dBm thì client **nghe rõ AP nhưng AP không nghe rõ client** → upload hỏng, hay rớt.
2. ⭐ **Cell to ra → CCI nặng hơn:** nhiều client hơn phải chia sẻ cùng airtime, và cell chồng lấn AP hàng xóm.
3. ⭐ **Client bám dai (sticky):** client giữ AP cũ lâu hơn thay vì roam sang AP gần → tốc độ tệ khi di chuyển.

⭐ **Giải pháp đúng: thêm AP, giảm công suất, cell nhỏ lại.**
</details>

---

## 📚 13. THUẬT NGỮ ANH–VIỆT

| English | Tiếng Việt / Giải thích |
|---|---|
| **RF** (Radio Frequency) | Tần số vô tuyến |
| **Amplitude / Frequency / Phase / Wavelength** | Biên độ / Tần số / Pha / Bước sóng |
| ⭐ **dBm** | Công suất **tuyệt đối** so với 1 mW |
| ⭐ **dB** | **Chênh lệch** công suất (tương đối) |
| ⭐ **dBi / dBd** | Gain antenna so với isotropic / dipole. ⭐ `0 dBd = 2.14 dBi` |
| ⭐ **EIRP** | Công suất bức xạ hiệu dụng = `Tx − loss + gain` |
| ⭐ **RSSI** | Độ mạnh tín hiệu thu (dBm, số âm) |
| ⭐ **Noise floor** | Mức ồn nền của môi trường (dBm) |
| ⭐ **SNR** | Tỉ số tín hiệu trên nhiễu = `RSSI − noise` (dB) |
| **Attenuation / Absorption** | Suy hao / Hấp thụ |
| **Reflection / Refraction / Diffraction / Scattering** | Phản xạ / Khúc xạ / Nhiễu xạ / Tán xạ |
| ⭐ **Multipath** | Đa đường — cùng tín hiệu tới qua nhiều đường |
| **FSPL** (Free Space Path Loss) | Suy hao không gian tự do |
| ⭐ **ISM / UNII band** | Các dải tần miễn cấp phép (2.4 GHz / 5 GHz) |
| ⭐ **Channel bonding** | Gộp channel để tăng độ rộng (40/80/160 MHz) |
| ⭐ **DFS / TPC** | Tự né radar / Điều khiển công suất phát |
| ⭐ **CAC** (Channel Availability Check) | Nghe 60 s trước khi dùng channel DFS |
| ⭐ **CCI / ACI** | Nhiễu **cùng** channel (chờ nhau) / nhiễu channel **kề** (hỏng gói) |
| ⭐ **CSMA/CA** | Nghe trước khi nói, **tránh** đụng độ |
| ⭐ **CCA** | Đánh giá kênh có rảnh không |
| ⭐ **NAV** | Bộ đếm "kênh còn bận bao lâu" (carrier sense ảo) |
| **DIFS / SIFS** | Các khoảng lặng bắt buộc giữa các frame |
| ⭐ **Hidden node** | Hai client không nghe được nhau → đụng độ tại AP |
| ⭐ **RTS/CTS** | Xin phép / cho phép phát — chống hidden node |
| ⭐ **MIMO** | Nhiều antenna phát và thu |
| ⭐ **Spatial stream (SS)** | Luồng dữ liệu song song. ⭐ `4x4:4` = 4 phát, 4 thu, 4 luồng |
| ⭐ **MU-MIMO** | Phục vụ nhiều client cùng lúc bằng **không gian** |
| ⭐ **OFDMA** | Chia channel thành **RU** cho nhiều client (802.11ax) |
| **Beamforming (TxBF)** | Nắn chùm sóng về phía client |
| **MRC** | Ghép nhiều bản sao tín hiệu ở bên thu |
| ⭐ **MCS** | Bảng tổ hợp điều chế + coding → quyết định data rate |
| ⭐ **Rate shifting** | Tự hạ/tăng tốc độ theo chất lượng tín hiệu |
| ⭐ **Mandatory / Supported rate** | Tốc độ **bắt buộc** hỗ trợ mới join / được phép dùng |
| ⭐ **BSS / BSSID / SSID / ESS** | Một AP+client / MAC radio AP / Tên mạng / Nhiều AP chung SSID |
| ⭐ **Beacon / Probe** | Frame AP quảng bá / Frame client đi tìm |
| ⭐ **Association / AID** | Gia nhập BSS / Số hiệu client được cấp |
| ⭐ **4-way handshake** | Trao đổi khóa mã hóa sau khi xác thực |
| ⭐ **AP mode: Local / FlexConnect / Monitor / Sniffer / Rogue Detector / SE-Connect / Bridge / Sensor** | Xem bảng §5 |
| ⭐ **Lightweight AP / Autonomous AP** | AP cần WLC / AP độc lập |
| ⭐ **Omni / Directional** | Antenna tỏa đều / hướng |
| ⭐ **Patch / Yagi / Parabolic dish / Sector** | Các loại antenna hướng, xem §6.2 |
| ⭐ **Beamwidth** | Góc phủ hữu ích (mốc −3 dB) |
| ⭐ **Polarization** | Hướng dao động sóng (dọc / ngang) |
| ⭐ **Radiation pattern (Azimuth / Elevation)** | Biểu đồ vùng phủ nhìn từ trên / từ bên |
| ⭐ **RRM / DCA / TPC / CleanAir** | Tự động quản lý tài nguyên RF của Cisco |
| ⭐ **Airtime fairness / RX-SOP** | Chia đều thời gian phát / Ngưỡng bỏ qua tín hiệu quá yếu |
| ⭐ **Band Select** | Đẩy client dual-band sang 5 GHz |
| **Coverage vs Capacity design** | Thiết kế theo vùng phủ vs theo dung lượng |

---

## 🎯 14. ĐÚC KẾT MODULE-07A

**3 điều rút ra:**

1. 🔴 ⭐⭐ **Ba con số RF, và mối quan hệ giữa chúng, là toàn bộ Layer 1:**
   ⭐ **`EIRP = Tx − cable loss + antenna gain`** (nhớ dấu **trừ** ở cable) ·
   ⭐ **`SNR = RSSI − noise floor`** (ra **dB**, không phải dBm) ·
   ⭐ **quy tắc 3 & 10** (`+3 dB = ×2`, `+10 dB = ×10`, mốc `0 dBm = 1 mW`).
   ⭐ Và bài học lớn nhất: ⭐ **RSSI mạnh không có nghĩa là kết nối tốt — phải nhìn SNR.**

2. 🔴 ⭐⭐ **Wi-Fi là môi trường CHIA SẺ, HALF-DUPLEX — mọi giới hạn đều bắt nguồn từ đây:**
   ⭐ 2.4 GHz chỉ có **3 channel** (1-6-11) · ⭐ **CCI làm CHẬM, ACI làm HỎNG** (nên 1-6-11 luôn thắng) ·
   ⭐ channel rộng gấp đôi = **SNR −3 dB và mất một nửa số channel** · ⭐ mỗi SSID thêm vào là thêm beacon
   ăn airtime. ⭐ Vì thế nguyên tắc thiết kế là ⭐ **thêm AP – giảm công suất – cell nhỏ**,
   🔴 **không bao giờ là "tăng công suất lên"**.

3. ⭐⭐ **Hai bảng phải học thuộc vì đề hỏi trực tiếp:** ⭐ **9 AP mode** (nhớ 3 cặp dễ nhầm:
   Monitor↔Sniffer, Monitor↔Rogue Detector, Local↔Monitor — ⭐ **Rogue Detector là cái duy nhất TẮT radio,
   nghe trên DÂY**) và ⭐ **bảng antenna** (⭐ **gain cao ⟺ beamwidth hẹp**, antenna **nắn hình** chứ
   không tạo thêm năng lượng). Cộng thêm ⭐ **bảng chuẩn 802.11** với 3 bẫy: **a là 5 GHz · ac CHỈ 5 GHz ·
   ax có cả 2.4**.

🧠 **Một câu để nhớ:** *Wi-Fi là **một phòng họp không chủ tọa** — ai cũng phải nghe trước khi nói,
nói xong phải chờ gật đầu, và ⭐ **càng đông thì mỗi người càng ít lượt**. Muốn phục vụ nhiều người hơn,
bạn ⭐ **mở thêm phòng** (thêm AP, thêm channel, cell nhỏ) chứ ⭐ **không bắt mọi người hét to hơn**
(tăng công suất). Còn antenna chỉ là ⭐ **cái loa định hướng** — nó không tạo thêm tiếng, nó chỉ chọn
hướng để dồn tiếng vào.*

---

### ✅ TỰ CHẤM

**Phần A — Trả lời được bằng lời của mình:**

| # | Câu | ✅ |
|:---:|---|:---:|
| 1 | ⭐⭐ Quy tắc 3 & 10. Đổi 26 dBm ↔ mW **không dùng máy tính** | ☐ |
| 2 | ⭐ Phân biệt **dBm / dB / dBi / dBd**. `0 dBd = ? dBi` | ☐ |
| 3 | ⭐⭐ Công thức **EIRP** — và vì sao cable loss **trừ** còn antenna gain **cộng** | ☐ |
| 4 | ⭐⭐ Công thức **SNR**, đơn vị, và **3 ngưỡng** RSSI/SNR quan trọng | ☐ |
| 5 | 🔴 ⭐ Vì sao **RSSI mạnh mà kết nối vẫn tệ** — cho ví dụ bằng số | ☐ |
| 6 | ⭐ 6 hiện tượng sóng gặp trên đường (absorption…multipath) | ☐ |
| 7 | ⭐ Multipath: khi nào là **kẻ thù**, khi nào là **tài nguyên** | ☐ |
| 8 | ⭐⭐ Vì sao 2.4 GHz chỉ có **1-6-11** | ☐ |
| 9 | ⭐ 4 UNII band, band nào cần **DFS** | ☐ |
| 10 | ⭐⭐ DFS làm gì? **CAC 60 s** và **rời channel 10 s** | ☐ |
| 11 | ⭐⭐ Channel rộng gấp đôi → SNR và số channel thay đổi thế nào | ☐ |
| 12 | 🔴 ⭐⭐ **CCI vs ACI** — cái nào tệ hơn, **vì sao** | ☐ |
| 13 | ⭐ **Interference vs Noise** khác nhau gì | ☐ |
| 14 | ⭐ RRM · DCA · TPC · CleanAir — mỗi cái làm gì | ☐ |
| 15 | ⭐⭐ Vì sao Wi-Fi là **half-duplex chia sẻ**? Vì sao dùng CA chứ không CD? | ☐ |
| 16 | ⭐ CCA · NAV · random backoff · ACK | ☐ |
| 17 | ⭐ **Hidden node** là gì? RTS/CTS giải quyết ra sao? | ☐ |
| 18 | ⭐⭐ Bảng **802.11 a/b/g/n/ac/ax**: band, tốc độ, điểm nhận dạng | ☐ |
| 19 | 🔴 ⭐ Ba bẫy: **a là 5 GHz · ac CHỈ 5 GHz · ax có cả 2.4** | ☐ |
| 20 | ⭐ **802.11 k / v / r / w** mỗi cái làm gì | ☐ |
| 21 | ⭐ Đọc `4x4:4`. ⭐ Số SS thực dùng = ? | ☐ |
| 22 | ⭐⭐ **MU-MIMO vs OFDMA** — chia gì, chuẩn nào, hợp với gì | ☐ |
| 23 | ⭐ 4 tính năng chính của Wi-Fi 6 · **BSS Coloring** làm gì | ☐ |
| 24 | ⭐⭐ Vì sao **tắt low data rate** lại làm mạng nhanh hơn | ☐ |
| 25 | ⭐⭐ **4 bước client join** — và vì sao "Associated" chưa phải xong | ☐ |
| 26 | ⭐ **BSS · BSSID · SSID · ESS** — 1 AP dual-band 4 SSID = mấy BSSID? | ☐ |
| 27 | ⭐⭐ **9 AP mode** — kể tên + mục đích | ☐ |
| 28 | 🔴 ⭐⭐ **Monitor vs Sniffer vs Rogue Detector** — 3 khác biệt then chốt | ☐ |
| 29 | ⭐ **Lightweight vs Autonomous AP** · EWC là gì | ☐ |
| 30 | ⭐⭐ Bảng antenna: loại · gain · beamwidth · dùng khi nào | ☐ |
| 31 | ⭐⭐ Vì sao **gain cao ⟺ beamwidth hẹp**? Antenna có "tạo năng lượng" không? | ☐ |
| 32 | ⭐ **Polarization** — hậu quả khi 2 đầu bridge lệch nhau | ☐ |
| 33 | ⭐ **Coverage design vs Capacity design** + **6 cách tăng capacity** | ☐ |
| 34 | 🔴 ⭐⭐ **Mất cân bằng công suất AP–client**: triệu chứng và cách sửa | ☐ |
| 35 | ⭐ **Quy trình chẩn đoán RF 5 bước** (§11.3) | ☐ |

**Phần B — Lab:**

| # | Yêu cầu | ✅ |
|:---:|---|:---:|
| 1 | ⭐⭐ **LAB A**: làm đúng ≥ 7/8 câu, **không dùng máy tính** | ⭐⭐ ☐ |
| 2 | ⭐ Riêng câu 5 & 6 của LAB A — giải thích được **vì sao RSSI mạnh mà vẫn tệ** | ⭐ ☐ |
| 3 | ⭐ **LAB B Bước 1**: đọc được SSID/BSSID/channel/band/chuẩn của mạng mình | ☐ |
| 4 | ⭐ Đổi được `Signal %` sang **dBm** ước lượng | ☐ |
| 5 | ⭐ Nói được channel hiện tại **có phải DFS** không | ☐ |
| 6 | ⭐⭐ **LAB B Bước 2**: quét và **lập bảng thống kê 7 dòng** các AP xung quanh | ⭐⭐ ☐ |
| 7 | 🔴 ⭐ Tìm được ít nhất **1 AP 2.4 GHz KHÔNG ở 1/6/11** → giải thích nó gây **ACI** | ⭐ ☐ |
| 8 | ⭐ Tìm được **1 SSID có nhiều BSSID** → nhận ra đó là **ESS** | ☐ |
| 9 | ⭐ **LAB B Bước 3**: card Wi-Fi của bạn hỗ trợ `802.11ax`? `802.11w`? | ☐ |
| 10 | ⭐⭐ **LAB B Bước 4**: đo RSSI ở **4 vị trí** và ghi lại data rate | ⭐⭐ ☐ |
| 11 | ⭐⭐ Quan sát được **data rate tự giảm khi RSSI giảm** (rate shifting) | ⭐⭐ ☐ |
| 12 | ⭐ Quan sát được **1 bức tường** làm tụt bao nhiêu | ☐ |
| 13 | 🔴 ⭐ Quan sát được **thân người che laptop** làm tín hiệu tụt (absorption) | ⭐ ☐ |
| 14 | ⭐ **LAB C**: chụp được biểu đồ channel 2.4 GHz và 5 GHz, so sánh độ chật | ☐ |
| 15 | ⭐ Chỉ ra được AP nào đang chiếm **80 MHz** ở 5 GHz | ☐ |
| 16 | ⭐ Tự chọn được channel cho AP của mình và **giải thích lý do** | ☐ |
| 17 | ⭐ **LAB D**: tạo được `wlanreport` và tìm được **1 lần BSSID đổi** = roaming | ☐ |
| 18 | 🚀 **LAB E**: đăng nhập được DevNet Sandbox C9800 | 🚀 ☐ |
| 19 | 🚀 Tìm được màn hình hiển thị **RSSI/SNR** của client trên WLC thật | 🚀 ☐ |
| 20 | 🚀 Tìm được **AP mode** và **channel/Tx power** trên WLC thật | 🚀 ☐ |

> ⭐ **Nếu chỉ có thời gian làm một nửa:** ưu tiên **mục 1–2** (LAB A — dạng tính toán duy nhất của đề),
> **mục 6–7** (quét AP xung quanh, thấy tận mắt vấn đề 1-6-11), và **mục 10–13** (đo RSSI thật, thấy rate shifting).
> Bỏ LAB E nếu đang bám tiến độ — sẽ làm ở **Module-07B**.
>
> ⚠️ **Chưa tick được ≥ 30/35 ở Phần A thì chưa nên sang 07B.**
> ⭐ 07B (CAPWAP/WLC/roaming) **xây trực tiếp** trên các khái niệm RSSI, SNR, BSSID, ESS, AP mode ở đây.

---

## 🔗 15. TÀI LIỆU CHO MODULE NÀY

| Nguồn | Cụ thể |
|---|---|
| **Sách OCG 350-401** | Chương *Wireless Signals and Modulation* và *Wireless Infrastructure* — ⭐ đọc song song với module này |
| **Sách chuyên sâu** ⭐⭐ | ***CWNA Certified Wireless Network Administrator Study Guide*** (David Coleman & David Westcott) — ⭐ **cuốn hay nhất về RF cho người mới**. Không bắt buộc, nhưng nếu bạn muốn theo wireless nghiêm túc thì đây là cuốn đầu tiên |
| **Cisco doc** ⭐⭐ | ***Cisco Wireless Controller Configuration Guide*** (bản C9800 / IOS-XE) — chương *Radio Resource Management* |
| **Cisco doc** ⭐⭐ | ***Cisco 802.11ac / Wi-Fi 6 (802.11ax) White Paper*** — ⭐ giải thích OFDMA, BSS Coloring, TWT bằng hình rất dễ hiểu |
| **Cisco doc** ⭐ | *Antenna Product Selection Guide* — ⭐ **có biểu đồ radiation pattern thật của từng model**. Search: `cisco aironet antenna selection guide` |
| **Cisco doc** ⭐ | *Channel Deployment Issues for 2.4-GHz 802.11 WLANs* — ⭐ tài liệu gốc giải thích vì sao 1-6-11 |
| **Cisco doc** ⭐ | *Dynamic Frequency Selection and IEEE 802.11h* · *CleanAir Deployment Guide* |
| **Cisco doc** ⭐ | *Lightweight AP Modes* — ⭐ bảng AP mode chính thống (§5) |
| **Cisco Validated Design** ⭐⭐ | ***Campus Wireless LAN Design Guide*** — ⭐ chứa số liệu thiết kế thật: ngưỡng −67 dBm, SNR 25 dB, cell overlap |
| **Cisco DevNet** ⭐ | `developer.cisco.com/site/sandbox/` — tìm sandbox **Catalyst 9800** (⭐ LAB E) |
| **Công cụ** ⭐ | **WiFiAnalyzer (VREM)** — Android, open source · **Ekahau/NetSpot** (bản trial) cho khảo sát · **Wireshark** |
| **Video** ⭐ | CBT Nuggets ENCOR — module Wireless · **Keith Barker**: search `Keith Barker wireless RF fundamentals` · **Rowell Dionicio / Clear To Send** podcast (chuyên wireless) |
| **Blog** ⭐⭐ | **mrncciew.com** (⭐ tuyệt vời cho CWNA/wireless, có phân tích frame 802.11 từng byte) · **badfi.com** · **wifinigel.blogspot.com** |
| **NetworkLessons** | Loạt bài *Wireless Fundamentals*, *802.11 Frame Types*, *MIMO*, *Antenna* — nhiều bài free |
| **Forum** | https://community.cisco.com → mục **Wireless - Mobility**. Search: `low snr high rssi`, `dfs radar detected ap changed channel`, `clients not seeing ssid dfs channel`, `disable low data rates 2.4ghz` |

---

**➡️ Tiếp theo:** [Module-07B — CAPWAP, WLC, FlexConnect & Roaming](Module-07B-CAPWAP-WLC-FlexConnect-Roaming.md)
*(Split-MAC · quá trình AP discover & join WLC · WLC deployment model · FlexConnect · L2/L3 roaming · WLAN config & troubleshoot — **Tuần 13**)*

> ⭐ **07B là nửa "hạ tầng" của khối wireless** — và chứa mục **3.3.e "Troubleshoot"**, mục **duy nhất
> trong Domain 3.3 không phải "Describe"**. Chuẩn bị tinh thần học kỹ phần đó.
