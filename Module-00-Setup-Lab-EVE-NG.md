# Module-00 — Dựng lab EVE-NG trên VMware Workstation

> 🧭 **Lộ trình:** `[Bạn đang ở đây] Module-00` → Module-P0 → Module-01 …
> **Tuần 0** · Không thuộc blueprint đề thi, nhưng **không có lab thì không đỗ ENCOR**.
>
> ⚠️ Module này dùng **khuôn giản lược** (setup, không phải kiến thức thi): Chuẩn bị → Lý thuyết ngắn →
> Hướng dẫn step-by-step → Gỡ lỗi → Checklist → Đúc kết.

---

## ✅ 1. Chuẩn bị trước khi bắt đầu

| Cần có | Yêu cầu | Kiểm tra thế nào |
|---|---|---|
| PC | **16 GB RAM** (bạn đã có), CPU hỗ trợ VT-x/AMD-V | Task Manager → Performance → CPU → dòng *Virtualization: Enabled* |
| Ổ đĩa trống | **≥ 100 GB** | EVE-NG OVA thin-provision nhưng sẽ phình khi thêm image |
| VMware Workstation | Bản 16 trở lên (bạn đã có) | Help → About |
| Kết nối Internet | Để tải OVA (~4 GB) và cập nhật EVE-NG | — |
| Công cụ phụ | **WinSCP** hoặc **FileZilla** (copy image qua SFTP), **PuTTY** | Tải free |
| Image Cisco | Xem §5 — cách hợp pháp để có image | — |

**Thời lượng thực tế:** 3–5 giờ cho lần đầu (kể cả thời gian tải OVA). Đừng làm gấp.

---

## 📘 2. Lý thuyết ngắn — bạn đang dựng cái gì?

### 2.1 Kiến trúc 3 tầng lồng nhau

```
┌──────────────────────────────────────────────────────────┐
│  Windows 11 (PC 16 GB) — HOST                            │
│  ┌────────────────────────────────────────────────────┐  │
│  │  VMware Workstation                                │  │
│  │  ┌──────────────────────────────────────────────┐  │  │
│  │  │  VM "EVE-NG" (Ubuntu) — cấp 12 GB RAM        │  │  │
│  │  │  ┌────────┐ ┌────────┐ ┌────────┐            │  │  │
│  │  │  │ R1     │ │ R2     │ │ SW1    │  ← node    │  │  │
│  │  │  │ vIOS   │ │ vIOS   │ │ vIOS-L2│    KVM/QEMU│  │  │
│  │  │  │ 512 MB │ │ 512 MB │ │ 768 MB │            │  │  │
│  │  │  └────────┘ └────────┘ └────────┘            │  │  │
│  │  └──────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

**Vì sao phải hiểu chỗ này:** router trong lab là **máy ảo bên trong một máy ảo**.
Đây gọi là **nested virtualization** (ảo hóa lồng). Nếu VMware không cho phép EVE-NG dùng
CPU virtualization, thì EVE-NG không tạo được node → node không boot. **Đây là lỗi số 1 của người mới.**

### 2.2 Các thành phần EVE-NG

| Thành phần | Là gì | Bạn tương tác ra sao |
|---|---|---|
| **EVE-NG VM** | Ubuntu Server + KVM/QEMU + web app | SSH vào (root) khi cần copy image |
| **Web UI** | Giao diện kéo-thả tạo topology | Trình duyệt → `http://<IP-eve>` |
| **Node** | 1 thiết bị mạng ảo (router/switch) | Click phải → Start, double-click → console |
| **Image** | File hệ điều hành thiết bị (`.qcow2`, `.bin`) | Copy vào `/opt/unetlab/addons/…` |
| **Lab (.unl)** | 1 file chứa topology + config | Tạo trong web UI, lưu trên EVE-NG |
| **Cloud (pnet)** | Cầu nối lab ↔ mạng thật | Kéo object *Network → Cloud0* vào lab |

### 2.3 Ba loại mạng bạn sẽ gặp

| Tên trong EVE-NG | Nghĩa | Dùng khi nào |
|---|---|---|
| **Cloud0** (pnet0) | Nối ra card mạng quản lý của EVE-NG → ra LAN/Internet thật | Cho router lab ra Internet, hoặc để Python/Ansible từ Windows nói chuyện với node |
| **Cloud1–9** (pnet1–9) | Nối ra card mạng phụ (phải thêm NIC vào VM EVE-NG) | Lab nâng cao, ít dùng |
| **Bridge** (net) | Switch ảo trong lab, chỉ nối các node với nhau | ⭐ Dùng nhiều nhất: nối nhiều node vào 1 segment |

> 💡 **Nối 2 node point-to-point** thì cứ kéo dây trực tiếp từ interface node A sang node B — EVE-NG
> tự tạo bridge ẩn. Chỉ khi cần ≥3 node cùng segment mới cần object *Bridge*.

---

## 🛠️ 3. HƯỚNG DẪN STEP-BY-STEP — dựng EVE-NG

### Bước 1 — Tải EVE-NG Community OVA

1. Mở https://www.eve-ng.net → menu **Download** → **Community Edition**
2. Chọn bản **OVA** (không phải ISO). File tên dạng `EVE-Community-VM-*.ova`, ~4 GB
3. Đồng thời tải luôn:
   - **EVE-NG Cookbook** (PDF, ở mục Documentation) — tài liệu chính thức, giữ để tra
   - **Windows Client Side Pack** (mục Download) — cài để click node là mở PuTTY luôn

✅ **Checkpoint:** bạn có 1 file `.ova` khoảng 4 GB.

---

### Bước 2 — ⚠️ Xử lý Hyper-V trên Windows 11 (BƯỚC HAY BỊ BỎ QUA NHẤT)

Windows 11 mặc định bật một số tính năng bảo mật dựa trên Hyper-V. Khi đó **VMware phải chạy
"trên lưng" Hyper-V**, và nested virtualization thường không hoạt động → node EVE-NG không boot.

**Kiểm tra trước:** mở PowerShell **as Administrator**:

```powershell
# Xem Hyper-V/VBS có đang bật không
Get-CimInstance -ClassName Win32_ComputerSystem | Select-Object HypervisorPresent
systeminfo | Select-String "Hyper-V"
```

- `HypervisorPresent : False` → 🎉 Tốt, bỏ qua bước này, sang Bước 3
- `HypervisorPresent : True` → cần tắt, làm tiếp bên dưới

**Cách tắt** (chạy PowerShell as Administrator):

```powershell
# 1. Tắt các Windows feature liên quan
Disable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All -NoRestart
Disable-WindowsOptionalFeature -Online -FeatureName HypervisorPlatform -NoRestart
Disable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -NoRestart
Disable-WindowsOptionalFeature -Online -FeatureName Windows-Defender-ApplicationGuard -NoRestart

# 2. Tắt hypervisor lúc boot
bcdedit /set hypervisorlaunchtype off
```

Rồi tắt bằng GUI:
- **Windows Security → Device security → Core isolation → Memory integrity → Off**
- **Settings → System → Recovery** → khởi động lại máy

**Sau khi reboot, kiểm tra lại:**
```powershell
Get-CimInstance -ClassName Win32_ComputerSystem | Select-Object HypervisorPresent
# Mong đợi: False
```

> ⚠️ **Đánh đổi phải biết:** tắt Memory Integrity làm **giảm mức bảo vệ của Windows**.
> Và **WSL2, Docker Desktop, Windows Sandbox, Android Emulator sẽ không chạy được** khi Hyper-V tắt.
> Đây là đánh đổi hai chiều — bạn bật lại lúc nào cũng được bằng:
> ```powershell
> bcdedit /set hypervisorlaunchtype auto
> ```
> rồi reboot. Nếu bạn cần WSL2 thường xuyên, cân nhắc để nguyên Hyper-V rồi thử EVE-NG trước —
> một số phiên bản VMware Workstation mới vẫn chạy được nested virt trên Hyper-V, chỉ **chậm hơn**.
> Nếu node boot được thì khỏi phải tắt gì.

✅ **Checkpoint:** `HypervisorPresent : False` (hoặc bạn chấp nhận thử với Hyper-V còn bật).

---

### Bước 3 — Import OVA vào VMware Workstation

1. VMware Workstation → **File → Open…** → chọn file `.ova`
2. Đặt tên VM: `EVE-NG` · chọn thư mục lưu (ổ còn ≥100 GB, **ưu tiên SSD**)
3. Nhấn **Import**
4. Nếu hiện cảnh báo *"The import failed because … did not pass OVF specification conformance"*
   → nhấn **Retry**. Đây là cảnh báo bình thường, không phải lỗi.

✅ **Checkpoint:** VM `EVE-NG` xuất hiện trong danh sách VMware, **chưa bật**.

---

### Bước 4 — ⚠️ Cấu hình VM TRƯỚC KHI BẬT (bước quyết định)

Click VM `EVE-NG` → **Edit virtual machine settings**:

| Tab | Cấu hình cho PC 16 GB | Vì sao |
|---|---|---|
| **Memory** | **12288 MB (12 GB)** | Để lại 4 GB cho Windows. Cấp ít hơn 8 GB thì lab sẽ rất chật |
| **Processors** → Number of processors | **1** | |
| **Processors** → Cores per processor | **4** (hoặc = số core vật lý – 2) | Node cần CPU để boot; 2 core thường quá chậm |
| **Processors** → ⭐ **Virtualize Intel VT-x/EPT or AMD-V/RVI** | ✅ **PHẢI TICK** | **Đây là ô quan trọng nhất của cả module này.** Không tick → node không bao giờ boot |
| **Processors** → Virtualize IOMMU | Không cần tick | |
| **Hard Disk** | Để nguyên (mặc định thường ~100 GB thin) | Phình dần khi thêm image |
| **Network Adapter** | **Bridged** + tick *Replicate physical network connection state* | Để EVE-NG có IP cùng dải LAN nhà bạn → truy cập web UI dễ, node ra Internet được |
| **Display** | Bỏ tick *Accelerate 3D graphics* | Không cần, đỡ tốn |

> 💡 **Bridged vs NAT:** Bridged cho EVE-NG một IP thật trong LAN nhà bạn (VD `192.168.1.50`) —
> dễ nhất để mở web UI và để script Python trên Windows nói chuyện với node lab.
> Nếu mạng nhà bạn chặn hoặc Wi-Fi không cho bridge, dùng **NAT** rồi truy cập qua IP NAT của VMware.

✅ **Checkpoint:** ô *Virtualize Intel VT-x/EPT* đã tick, RAM 12 GB, 4 core, network Bridged.

---

### Bước 5 — Boot lần đầu & wizard cấu hình

1. **Power on this virtual machine**
2. Chờ boot (1–3 phút). Đến màn hình login:
   ```
   eve-ng login: root
   Password: eve
   ```
   > Mật khẩu mặc định là `eve`, gõ sẽ **không hiện gì cả** — bình thường, cứ gõ rồi Enter.

3. Wizard tự chạy, trả lời lần lượt:

| Câu hỏi | Nhập gì | Ghi chú |
|---|---|---|
| `Enter root password` (2 lần) | Mật khẩu mới của bạn | **Ghi lại ngay.** Mất là phải làm lại từ đầu |
| `Hostname` | `eve-ng` | Để mặc định cũng được |
| `DNS domain name` | `lab.local` | Không quan trọng |
| `Network configuration` | Chọn **static** | ⭐ Nên static — DHCP đổi IP là bạn mất web UI |
| `Static IPv4 address` | VD `192.168.1.50` | Chọn IP **ngoài dải DHCP** của router nhà bạn |
| `Netmask` | `255.255.255.0` | Theo LAN nhà bạn |
| `Default gateway` | VD `192.168.1.1` | IP router nhà bạn |
| `Primary DNS` | `8.8.8.8` | |
| `Secondary DNS` | `1.1.1.1` | |
| `NTP server` | Để trống → Enter | Hoặc `pool.ntp.org` |
| `How is your VM connected to internet` | **direct connection** | Chọn proxy chỉ khi mạng bạn qua proxy |

4. EVE-NG **tự reboot**. Chờ boot lại.

5. Sau khi boot, đăng nhập lại và kiểm tra:

```bash
ip -br a          # xem IP đã đúng chưa
ping -c 3 8.8.8.8 # xem ra Internet được chưa
free -h           # xem RAM VM nhận đủ 12 GB chưa
```

**Output mẫu bạn sẽ thấy:**
```
root@eve-ng:~# ip -br a
lo               UNKNOWN        127.0.0.1/8
pnet0            UP             192.168.1.50/24
eth0             UP

root@eve-ng:~# free -h
               total        used        free      shared  buff/cache   available
Mem:            11Gi       800Mi        10Gi        1.0Mi       500Mi        10Gi
```

> 💡 Chú ý: IP nằm trên interface **`pnet0`**, không phải `eth0`. `pnet0` là bridge mà EVE-NG tạo ra
> để nối lab với mạng ngoài. Đây là thiết kế bình thường của EVE-NG.

✅ **Checkpoint:** `ip -br a` cho thấy `pnet0` có IP bạn đặt · `ping 8.8.8.8` thành công · `free -h` báo ~11–12 Gi.

---

### Bước 6 — Cập nhật EVE-NG & vào Web UI

**Cập nhật (nên làm ngay, sửa nhiều bug):**
```bash
apt update
apt upgrade -y
reboot
```

**Vào Web UI:**
1. Trên Windows, mở trình duyệt → `http://192.168.1.50` (IP bạn vừa đặt)
2. Đăng nhập:
   - Username: **`admin`**
   - Password: **`eve`**
   - HTML5 console: chọn **Html5** trong dropdown nếu chưa cài Windows Client Pack

**Đổi mật khẩu web ngay:** góc trên phải → **Management** → **User management** → sửa `admin`.

✅ **Checkpoint:** thấy được giao diện EVE-NG với thanh trạng thái **CPU / RAM / Disk** ở góc trên.

---

### Bước 7 — Cài Windows Client Side Pack (nên làm)

Không cài thì vẫn dùng được (qua HTML5 console trong browser), nhưng cài rồi thì tiện hơn nhiều.

1. Chạy file `EVE-NG-Win-Client-Pack.exe` đã tải ở Bước 1 → Next hết
2. Trong Web UI EVE-NG: góc trên phải → chọn console type = **Native console**
3. Từ đó double-click node sẽ mở **PuTTY** trực tiếp

| Console type | Ưu | Nhược |
|---|---|---|
| **Html5** | Không cần cài gì, dùng được từ máy khác | Copy-paste config dài hay bị lỗi ký tự |
| **Native (PuTTY)** | ⭐ Copy-paste tốt, log ra file được, nhiều tab | Phải cài client pack trên Windows |

> 💡 Với ENCOR bạn sẽ paste rất nhiều block config → **dùng Native/PuTTY.**
> Trong PuTTY nhớ bật **Session → Logging → All session output** để lưu lại output làm bằng chứng học tập.

✅ **Checkpoint:** double-click node mở được PuTTY (sau khi đã có node ở Bước 9).

---

## 📦 4. Ngân sách RAM — luật bạn phải nhớ

VM EVE-NG có 12 GB. Ubuntu ăn ~1–1.5 GB → **còn ~10 GB cho node**.

| Loại node | RAM khuyến nghị | Chạy tối đa được bao nhiêu con |
|---|:---:|:---:|
| IOL / IOU (nhẹ nhất) | 256 MB | ~30 con |
| **vIOS** (router) | **512 MB** | ~18 con |
| **vIOS-L2** (switch) | **768 MB** | ~12 con |
| CSR1000v | 3 GB | 3 con |
| vWLC | 2 GB | 4 con |
| Cat9kv | ⛔ 18 GB | **0 — không kham được** |
| Nexus 9000v | ⛔ 8 GB | 1 con, và máy sẽ lết |

**3 quy tắc RAM:**
1. **Chỉ Start node đang cần.** Node ở trạng thái Stop không ăn RAM. Lab 8 node nhưng chỉ cần 3 → start 3.
2. **Xem thanh RAM ở góc trên Web UI** trước khi start thêm node. Quá 85% là sắp treo.
3. **vIOS thay cho CSR1000v** ở mọi lab routing thường. Chỉ dùng CSR1000v khi cần RESTCONF/NETCONF (Module-12).

**Lệnh kiểm tra trên EVE-NG:**
```bash
free -h                              # RAM tổng
ps aux | grep qemu | wc -l           # số node đang chạy
```

---

## 💾 5. Đưa image vào EVE-NG

### 5.1 Lấy image ở đâu — nói thẳng

Image Cisco (IOS-XE, vIOS…) là **phần mềm có bản quyền**. Repo này không cung cấp và không chỉ nguồn lậu.
Ba đường hợp pháp:

| Cách | Chi phí | Phù hợp |
|---|---|---|
| **CCO account có service contract** → tải từ https://software.cisco.com | $0 nếu công ty bạn có contract | ⭐ **Thử cách này trước** — hỏi bên mua sắm/vendor của công ty bạn |
| **Cisco CML Personal** (~$199/năm) — kèm sẵn image hợp pháp | $199/năm | Nếu bạn muốn khỏi lo chuyện image. CML cũng chạy OVA trên VMware |
| **DevNet Sandbox + Packet Tracer** | $0 | ⭐ **Plan B luôn dùng được.** Thiết bị Cisco thật online, không cần image |

> 💡 **Lời khuyên thật:** bạn làm DevOps ở doanh nghiệp có hạ tầng mạng — rất có thể công ty đã có
> CCO account với contract. Hỏi thử. Đó là cách vừa hợp pháp vừa miễn phí.
>
> Và nếu tạm thời chưa có image: **vẫn học được tuần 1–2 bằng Packet Tracer**. Đừng để chuyện image
> chặn bạn khởi động. Cứ học đi, image lo sau.

### 5.2 Nơi đặt image trong EVE-NG

| Loại image | Thư mục | File đĩa đặt tên |
|---|---|---|
| QEMU (vIOS, vIOS-L2, CSR1000v, vWLC…) | `/opt/unetlab/addons/qemu/<tên-thư-mục>/` | `virtioa.qcow2` (hoặc `hda.qcow2` tùy image) |
| IOL / IOU | `/opt/unetlab/addons/iol/bin/` | file `.bin` + file license `iourc` |
| Dynamips (router cũ) | `/opt/unetlab/addons/dynamips/` | file `.image` |

**Tên thư mục PHẢI theo đúng quy ước của EVE-NG**, nếu không Web UI sẽ không thấy image. Ví dụ:

| Image | Tên thư mục |
|---|---|
| Cisco IOSv (router) | `vios-adventerprisek9-m.<version>` |
| Cisco IOSvL2 (switch) | `viosl2-adventerprisek9-m.<version>` |
| CSR1000v | `csr1000vng-universalk9.<version>` |
| Cisco vWLC | `vwlc-<version>` |

> ⚠️ **Quy ước tên thay đổi theo phiên bản EVE-NG.** Trước khi copy, mở
> **EVE-NG Documentation → "How to add images"** (https://www.eve-ng.net/index.php/documentation/)
> và đối chiếu đúng bảng tên của bản EVE-NG bạn đang chạy. Sai 1 ký tự là image không hiện.

### 5.3 Các bước copy image

1. Trên Windows mở **WinSCP** → protocol **SFTP** → host `192.168.1.50`, user `root`, password bạn đặt
2. Vào `/opt/unetlab/addons/qemu/`
3. Tạo thư mục đúng tên, VD `vios-adventerprisek9-m.157-3.M3`
4. Copy file đĩa vào, đặt tên `virtioa.qcow2`
5. **Nếu image bạn có là `.vmdk` hoặc `.bin`** → phải convert. SSH vào EVE-NG:
   ```bash
   cd /opt/unetlab/addons/qemu/vios-adventerprisek9-m.157-3.M3/
   qemu-img convert -f vmdk -O qcow2 <file-goc>.vmdk virtioa.qcow2
   rm <file-goc>.vmdk        # xóa file gốc cho đỡ tốn đĩa
   ```
6. ⭐ **Bước không được quên** — sửa quyền:
   ```bash
   /opt/unetlab/wrappers/unl_wrapper -a fixpermissions
   ```
7. Kiểm tra Web UI đã thấy image:
   ```bash
   ls -la /opt/unetlab/addons/qemu/
   ```
   Rồi trong Web UI: tạo lab mới → Add node → dropdown template phải hiện tên image
   **không còn màu xám**.

✅ **Checkpoint:** trong Web UI, template image bạn thêm hiển thị bình thường (không xám mờ).

---

## 🧪 6. LAB 0 — Lab đầu tiên: 2 router ping được nhau

Mục tiêu: xác nhận toàn bộ chuỗi *VMware → EVE-NG → node → console → forwarding* đều hoạt động.

### 6.1 Topology

```
        10.0.0.0/30
   R1 ────────────── R2
  Gi0/0            Gi0/0
 .1                    .2
```

| Thiết bị | Image | Interface | IP | RAM |
|---|---|---|---|:---:|
| R1 | vIOS | Gi0/0 | 10.0.0.1/30 | 512 MB |
| R2 | vIOS | Gi0/0 | 10.0.0.2/30 | 512 MB |

**Tổng RAM: 1 GB** — nhẹ, chạy được ngay cả khi Windows đang mở nhiều tab.

### 6.2 Các bước

**Bước 1 — Tạo lab**
1. Web UI → **Add new lab**
2. Name: `LAB-00-First-Lab` · Author: tên bạn · Description: `Kiem tra lab hoat dong`
3. **Save**

**Bước 2 — Thêm node**
1. Click phải vào vùng trắng → **Node**
2. Template: chọn image vIOS của bạn
3. Number of nodes: `2` · Name/prefix: `R` · RAM: `512` · Ethernets: `4`
4. **Save**

✅ Bạn thấy 2 icon router `R1`, `R2` trên canvas.

**Bước 3 — Nối dây**
1. Đưa chuột lên `R1` → xuất hiện icon ổ cắm 🔌 → **giữ chuột và kéo** sang `R2`
2. Hộp thoại hiện ra: chọn `R1 Gi0/0` ↔ `R2 Gi0/0` → **Save**

✅ Có 1 đường nối giữa R1 và R2.

**Bước 4 — Start node**
- Click phải vùng trắng → **More actions → Start all nodes**
- Icon router chuyển từ **xám → xanh** (mất 1–3 phút)

⚠️ Nếu icon **không chuyển xanh** hoặc chuyển xanh rồi tắt → xem §7 Gỡ lỗi, lỗi #1.

**Bước 5 — Vào console cấu hình R1**

Double-click icon `R1` → mở PuTTY. Nhấn **Enter** vài lần.

> ⚠️ vIOS boot mất 1–3 phút. Nếu console trống, cứ chờ và nhấn Enter. Đừng vội kết luận là lỗi.

Khi thấy prompt, có thể nó hỏi:
```
Would you like to enter the initial configuration dialog? [yes/no]: no
```
→ trả lời **`no`** rồi Enter.

Paste block sau (đây là **config đầy đủ**, copy được cả khối):

```
enable
configure terminal
!
hostname R1
no ip domain lookup
!
interface GigabitEthernet0/0
 description ---> To R2
 ip address 10.0.0.1 255.255.255.252
 no shutdown
!
line con 0
 exec-timeout 0 0
 logging synchronous
!
end
write memory
```

**Bước 6 — Cấu hình R2** (double-click `R2`)

```
enable
configure terminal
!
hostname R2
no ip domain lookup
!
interface GigabitEthernet0/0
 description ---> To R1
 ip address 10.0.0.2 255.255.255.252
 no shutdown
!
line con 0
 exec-timeout 0 0
 logging synchronous
!
end
write memory
```

**Bước 7 — Kiểm tra**

Trên R1:
```
R1# show ip interface brief
```
**Output mẫu:**
```
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0         10.0.0.1        YES manual up                    up
GigabitEthernet0/1         unassigned      YES unset  administratively down down
GigabitEthernet0/2         unassigned      YES unset  administratively down down
GigabitEthernet0/3         unassigned      YES unset  administratively down down
```

```
R1# ping 10.0.0.2
```
**Output mẫu:**
```
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 10.0.0.2, timeout is 2 seconds:
.!!!!
Success rate is 80 percent (4/5), round-trip min/avg/max = 1/3/8 ms
```

> 💡 **Gói đầu tiên bị mất (dấu `.`) là bình thường** — đó là lúc R1 gửi ARP để học MAC của R2.
> Ping lại lần 2 sẽ được `!!!!!` (100%). Chi tiết này đề ENCOR có hỏi.

### 6.3 ✅ Checkpoint LAB-00

| Kiểm tra | Mong đợi |
|---|---|
| `show ip interface brief` trên R1 | Gi0/0 = `10.0.0.1`, Status `up`, Protocol `up` |
| `ping 10.0.0.2` từ R1 | Success rate 80–100% |
| `ping 10.0.0.1` từ R2 | Success rate 100% (lần 2) |
| `show version` | Hiện version IOS, không báo lỗi license chặn |
| Thanh RAM trên Web UI | < 30% |

### 6.4 ⚠️ Nếu không ping được — kiểm tra theo thứ tự này

| # | Kiểm tra | Lệnh | Nếu sai thì |
|:---:|---|---|---|
| 1 | Interface có `up/up`? | `show ip int brief` | Thiếu `no shutdown` → vào interface gõ `no shutdown` |
| 2 | IP có đúng subnet? | `show run int Gi0/0` | `/30` chỉ có 2 host: `.1` và `.2`. Đặt `.1` và `.3` là sai subnet |
| 3 | Dây có nối đúng interface? | Xem canvas Web UI | Nối Gi0/0 ↔ Gi0/1 vẫn ping được, nhưng phải cấu hình IP trên interface **đúng** |
| 4 | ARP đã học chưa? | `show arp` | Trống → ping lại lần 2 |
| 5 | Có ACL nào chặn? | `show ip int Gi0/0 \| include access list` | Lab mới thì không có. Nếu có thì bạn paste sai |

### 6.5 🧪 Thử nghiệm — làm để hiểu sâu

Sau khi lab chạy đúng, **cố ý phá nó** rồi tự sửa. Đây là cách học nhanh nhất:

| Thử nghiệm | Gõ gì | Quan sát gì | Bài học |
|---|---|---|---|
| Tắt 1 đầu link | Trên R1: `int Gi0/0` → `shutdown` | `show ip int br` trên **R2** cũng thành `down` | Link ảo trong EVE-NG mô phỏng đúng như dây thật |
| Đặt sai subnet | Trên R2: đổi IP thành `10.0.0.5/30` | Ping fail hoàn toàn | `/30` chỉ chứa `.1`–`.2`; `.5` thuộc subnet khác |
| Đổi mask lệch | R1 `/30`, R2 `/24` | Ping có thể một chiều được, một chiều không | Mask lệch là lỗi kinh điển, đề ENCOR hay gài |
| Xem gói thật | Click phải link → **Capture** | Wireshark mở, thấy ICMP + ARP | ⭐ Đây là siêu năng lực của bạn suốt 20 tuần tới |

---

## 📸 7. Bước cuối — Snapshot (làm ngay, đừng bỏ)

Sau khi EVE-NG chạy được + đã thêm image xong:

1. **Shutdown EVE-NG cho gọn** (SSH vào: `shutdown -h now`)
2. VMware → click VM `EVE-NG` → **VM → Snapshot → Take Snapshot**
3. Đặt tên: `EVE-NG-clean-co-image` · Description: ghi ngày + đã có image gì

**Vì sao quan trọng:** trong 20 tuần bạn sẽ có lúc gõ sai gì đó làm EVE-NG lỗi. Có snapshot thì
5 phút là quay lại được. Không có thì mất cả buổi tối làm lại từ đầu.

> 💡 Chụp thêm snapshot mỗi khi thêm image mới hoặc trước khi `apt upgrade`. Snapshot ăn đĩa,
> nhớ xóa snapshot cũ khi không cần.

---

## 🐛 8. Gỡ lỗi nhanh — bảng lỗi EVE-NG thường gặp

### 8.1 Lệnh debug vạn năng

```bash
# Trên EVE-NG (SSH root)
free -h                                    # còn RAM không
df -h                                      # còn đĩa không (đầy đĩa là node không start)
ip -br a                                   # IP quản lý còn đúng không
systemctl status apache2                   # web UI có chạy không
ps aux | grep qemu                         # node nào đang chạy
ls -la /opt/unetlab/addons/qemu/           # image đã đặt đúng chỗ chưa
/opt/unetlab/wrappers/unl_wrapper -a fixpermissions   # sửa quyền — thuốc chữa nhiều bệnh
tail -50 /opt/unetlab/data/Logs/unl_wrapper.txt       # log khi node không start
```

### 8.2 Bảng triệu chứng → nguyên nhân → cách sửa

| # | Triệu chứng | Nguyên nhân thường gặp | Cách sửa |
|:---:|---|---|---|
| **1** | ⭐ Node **không start**, icon xám hoài, hoặc xanh rồi tắt ngay | **Chưa tick *Virtualize Intel VT-x/EPT*** trong VMware. Hoặc Hyper-V đang chiếm CPU virtualization | Shutdown VM → Settings → Processors → tick VT-x/EPT. Nếu vẫn lỗi → làm Bước 2 (tắt Hyper-V) |
| 2 | Node start được nhưng máy **lết như rùa** | Cấp quá ít core, hoặc host đang swap | Tăng core VM lên 4. Giảm số node đang start. Đóng Chrome trên Windows |
| 3 | **Console trống trơn**, gõ không phản hồi | vIOS boot chưa xong (1–3 phút) | Chờ + nhấn Enter. Nếu >5 phút → node thiếu RAM, tăng RAM node |
| 4 | Image **hiện màu xám** trong dropdown Add node | Tên thư mục sai quy ước, hoặc chưa `fixpermissions` | Đối chiếu tên với EVE-NG doc + chạy `unl_wrapper -a fixpermissions` |
| 5 | **Không mở được Web UI** | IP EVE-NG đổi (DHCP), hoặc apache chết | SSH vào: `ip -br a` xem IP thật · `systemctl restart apache2` |
| 6 | Node **không ra được Internet** dù đã nối Cloud0 | VM EVE-NG đang ở NAT thay vì Bridged; hoặc node chưa có default route | Đổi VMware network sang Bridged · Trên node: `ip route 0.0.0.0 0.0.0.0 <gw>` |
| 7 | `write memory` báo lỗi / config mất sau reboot node | Đĩa EVE-NG đầy | `df -h` → dọn `/opt/unetlab/tmp/` bằng: Web UI → Lab → *Wipe all nodes* các lab cũ |
| 8 | Kéo dây **không hiện hộp chọn interface** | Node đang chạy — EVE-NG không cho nối dây khi node đã start | Stop node → nối dây → start lại |
| 9 | **PuTTY không mở** khi double-click node | Chưa cài Windows Client Pack, hoặc console type đang là Html5 | Cài client pack · đổi console type sang Native |
| 10 | Copy-paste config **bị mất ký tự** | Html5 console + block quá dài | Dùng PuTTY. Hoặc paste từng đoạn ngắn |
| 11 | Lab mở lên **mất hết config** | Node bị *Wipe* (wipe = reset về mặc định) | Đừng dùng "Wipe" khi chỉ muốn tắt. Dùng **Stop**. Wipe là để reset lab về trắng |
| 12 | Sau `apt upgrade` EVE-NG **không boot** | Update lỗi | Restore snapshot (§7). Đây là lý do phải có snapshot |

### 8.3 Phân biệt Stop / Wipe — chỗ người mới hay mất công

| Hành động | Làm gì | Config còn không? | Dùng khi nào |
|---|---|:---:|---|
| **Stop** | Tắt node như tắt điện | ✅ Còn (nếu đã `write memory`) | ⭐ Bình thường dùng cái này |
| **Wipe** | Xóa toàn bộ trạng thái, node về image gốc | ❌ **Mất hết** | Khi muốn làm lại lab từ trắng |
| **Export CFG** | Lưu config node vào lab file | — | ⭐ Làm trước khi đóng lab, để lần sau mở lên còn config |

> ⚠️ **Thói quen phải tập:** trước khi đóng lab → click phải vùng trắng → **More actions → Export all CFGs**.
> Không làm bước này thì lần sau mở lab có thể mất config dù đã `write memory`.

---

## ✅ 9. CHECKLIST — "Lab của tôi đã sẵn sàng học ENCOR"

Tick hết bảng này mới sang Module-P0.

| # | Mục | ✅ |
|:---:|---|:---:|
| 1 | VMware: ô *Virtualize Intel VT-x/EPT* đã tick | ☐ |
| 2 | VM EVE-NG: 12 GB RAM, 4 core, network Bridged | ☐ |
| 3 | `HypervisorPresent : False` (hoặc đã xác nhận node boot được dù Hyper-V bật) | ☐ |
| 4 | EVE-NG có IP tĩnh trên `pnet0`, ping ra `8.8.8.8` được | ☐ |
| 5 | Đã `apt update && apt upgrade` | ☐ |
| 6 | Mở được Web UI, **đã đổi mật khẩu `admin`** | ☐ |
| 7 | Đã cài Windows Client Pack, double-click node mở PuTTY | ☐ |
| 8 | Có ít nhất **1 image router** (vIOS hoặc CSR1000v) hiện không xám | ☐ |
| 9 | Có ít nhất **1 image switch** (vIOS-L2) — cần cho Module-02 | ☐ |
| 10 | **LAB-00 chạy được: R1 ping R2 thành công** | ☐ |
| 11 | Đã thử **Capture** trên link, Wireshark mở được | ☐ |
| 12 | Đã tạo **snapshot** `EVE-NG-clean-co-image` trong VMware | ☐ |
| 13 | Đã tạo file `SO-TAY-LOI.md` và ghi vào đó lỗi đầu tiên bạn gặp | ☐ |

> ⚠️ **Chưa có image switch (mục 9)?** Vẫn học được Module-P0 tuần 1 bằng **Packet Tracer** (free).
> Đừng để chờ image làm bạn mất đà. Song song đó đi hỏi CCO account của công ty.

---

## 📚 10. Thuật ngữ Anh–Việt

| Tiếng Anh | Tiếng Việt | Ghi chú |
|---|---|---|
| Nested virtualization | Ảo hóa lồng | Máy ảo trong máy ảo — nền của EVE-NG |
| Hypervisor | Trình ảo hóa | VMware = Type 2, ESXi/Hyper-V = Type 1 |
| Bridged network | Mạng cầu nối | VM có IP cùng dải LAN thật |
| NAT network | Mạng dịch địa chỉ | VM ẩn sau IP của host |
| Node | Nút / thiết bị ảo | 1 router/switch trong lab |
| Template | Khuôn image | Loại thiết bị bạn chọn khi Add node |
| Topology | Sơ đồ mạng | Cách các node nối với nhau |
| Snapshot | Ảnh chụp trạng thái | Điểm phục hồi của VM |
| Wipe | Xóa sạch trạng thái | Reset node về image gốc — **mất config** |
| Console | Cửa sổ điều khiển | Nơi bạn gõ lệnh vào node |
| Capture | Bắt gói | Nghe traffic trên 1 link bằng Wireshark |
| Thin provision | Cấp phát mỏng | Đĩa ảo chỉ tốn chỗ theo dữ liệu thật |

---

## 🎯 11. Đúc kết Module-00

**3 điều rút ra:**

1. **Ô tick *Virtualize Intel VT-x/EPT* là điểm chết của 90% người mới.** Node không boot thì kiểm tra
   ô này trước mọi thứ khác. Kế đó là Hyper-V trên Windows 11.
2. **RAM là tài nguyên hiếm, không phải image.** PC 16 GB dùng vIOS/vIOS-L2 thay CSR1000v là đủ cho
   ~85% nội dung ENCOR. Chỉ start node đang cần.
3. **Snapshot + Export CFG là hai thói quen cứu bạn.** Snapshot cứu VM, Export CFG cứu config lab.
   Tập ngay từ tuần 0.

🧠 **Một câu để nhớ:** *Lab không chạy thì kiến thức không vào. Đầu tư 5 giờ ở Module-00 tiết kiệm
cho bạn 50 giờ vật vã ở 19 tuần sau.*

**✅ Tự chấm — trả lời được hết chưa?**

| Câu | ✅ |
|---|:---:|
| Vì sao EVE-NG cần nested virtualization? | ☐ |
| IP quản lý của EVE-NG nằm trên interface nào, vì sao không phải `eth0`? | ☐ |
| PC 16 GB thì start được tối đa mấy con vIOS-L2? | ☐ |
| Khác nhau giữa **Stop** và **Wipe** node? | ☐ |
| Lệnh nào sửa quyền sau khi copy image? | ☐ |
| Tôi tự dựng lại được LAB-00 từ lab trắng trong 10 phút? | ☐ |

---

**➡️ Tiếp theo:** [Module-P0 — Nền tảng Ready-for-ENCOR](Module-P0-Nen-tang-Ready-for-ENCOR.md)
