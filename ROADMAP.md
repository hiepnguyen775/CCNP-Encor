# ROADMAP — Lộ trình 20 tuần CCNP ENCOR 350-401

> Đây là **bản đồ**. In ra hoặc mở song song khi học. Mỗi tuần xong thì tự tick vào cột ✅.
>
> Giả định: **10 giờ/tuần** · trình độ khởi điểm *"biết VLAN/IP, mờ về OSPF/BGP/STP"* · lab EVE-NG trên VMware, PC 16 GB.

---

## 1. Bản đồ tổng — 20 tuần

| Tuần | Module | Chủ đề chính | Domain (blueprint) | LAB chính | RAM lab | ✅ |
|:---:|---|---|---|---|:---:|:---:|
| **0** | Module-00 | Dựng lab EVE-NG trên VMware | — | Ping thành công giữa 2 router trong EVE-NG | 2 GB | ☐ |
| **1** | Module-P0 | CLI Cisco · VLAN/Trunk · STP từ gốc | Nền tảng | 2 switch + trunk + inter-VLAN routing | 3 GB | ☐ |
| **2** | Module-P0 | Cách router chọn đường · static · OSPF single-area · NAT · ACL | Nền tảng | 3 router OSPF area 0 + NAT ra "Internet" + ACL | 3 GB | ☐ |
| **3** | Module-01 | Control/Data plane · Process→Fast→CEF · TCAM · MLS | Infrastructure + Architecture | Xem CEF/FIB/adjacency table, so sánh process vs CEF switching | 2 GB | ☐ |
| **4** | Module-02 | STP sâu · RSTP · PortFast/BPDU Guard/Root Guard/Loop Guard | Infrastructure 30% | 4 switch: ép root bridge, đo lại convergence RSTP vs STP | 4 GB | ☐ |
| **5** | Module-02 | MST · EtherChannel (LACP/PAgP/static) · load-balancing hash | Infrastructure 30% | MST 2 instance + Layer2/Layer3 EtherChannel | 4 GB | ☐ |
| **6** | Module-03 | Bảng định tuyến · AD · longest-prefix · static/floating static · redistribute · EIGRP (mức ENCOR) | Infrastructure 30% | Đọc `show ip route`, floating static failover, redistribute static→OSPF | 3 GB | ☐ |
| **7** | **Module-04A** | OSPF: neighbor state · DR/BDR · network type · LSA 1-2-3 | Infrastructure 30% | OSPF multi-area 3 router, đọc LSDB từng LSA type | 3 GB | ☐ |
| **8** | **Module-04B** | OSPF: LSA 4-5-7 · stub area · summarization · virtual-link · auth · OSPFv3 | Infrastructure 30% | Stub/NSSA + summarization + virtual-link + MD5/SHA auth | 4 GB | ☐ |
| **9** | **Module-05A** | BGP: AS · eBGP peering · các loại message · attribute cơ bản | Infrastructure 30% | eBGP 3 AS, advertise network, đọc `show bgp ipv4 unicast` | 4 GB | ☐ |
| **10** | **Module-05B** | BGP: **13 bước path selection** · LP/MED/AS-path/Weight · community | Infrastructure 30% | Ép chọn đường bằng Weight → LP → AS-path prepend → MED | 4 GB | ☐ |
| **11** | **Module-06A**<br>**Module-06B** | HSRP/VRRP/GLBP · object tracking · NAT/PAT nâng cao · NTP · Multicast | Infrastructure 30% | HSRP + object tracking failover · NAT dual-ISP route-map · NTP auth | 3 GB | ☐ |
| **12** | **Module-07A** | Wireless: RF (dBm/EIRP/RSSI/SNR) · band/channel/DFS · CCI vs ACI · 802.11 a→ax · AP mode · antenna | Infrastructure (wireless) | ⭐ **Không cần EVE-NG** — lab bằng chính laptop (`netsh wlan`) + WiFi analyzer + tính RF trên giấy | **0 GB** | ☐ |
| **13** | **Module-07B** | Split-MAC · CAPWAP · AP join & discovery · WLC selection · FlexConnect · roaming L2/L3 · ⭐ troubleshoot | Infrastructure (wireless) | ⭐ Lab-trên-giấy (join & chẩn đoán) + DevNet Sandbox Catalyst 9800 | **0 GB** | ☐ |
| **14** | **Module-08** | Hypervisor/vSwitch · **VRF-lite** · **GRE** · **IPsec / GRE over IPsec** · LISP · VXLAN | Virtualization **10%** | 2 VRF **trùng IP** · GRE + OSPF · ⭐ tái hiện **recursive routing** · GRE over IPsec (`QM_IDLE`, encaps/decaps) | **2 GB**<br>*(7 GB nếu cần CSR1000v cho crypto)* | ☐ |
| **15** | **Module-09** | 2-tier/3-tier · Spine-Leaf · HA (SSO/NSF/GR) · WLAN design · cloud · **SD-WAN** · **SD-Access** · **QoS** | Architecture **15%** | ⭐ Lab-trên-giấy (chọn design + điền bảng thành phần) · MQC/LLQ trên 2 router · DevNet DNAC & vManage | **1 GB** | ☐ |
| **16** | **Module-10** | Hardening & password type · **AAA TACACS+/RADIUS** · **ACL nâng cao** · **CoPP** · 802.1X/MAB/WebAuth · wireless security · TrustSec/MACsec · NGFW · REST API security | Security **20%** | ⭐ AAA fallback (server chết → `local`) · bẫy IPv6 ACL giết NDP · CoPP "đo trước siết sau" · 802.1X + Critical VLAN. ⭐ **Không cần RADIUS thật** | **1.8 GB** | ☐ |
| **17** | **Module-11** | Syslog · SNMPv2c/v3 · **Flexible NetFlow** · SPAN/RSPAN/ERSPAN · **IP SLA** · **debug an toàn** · DNAC Assurance | Assurance **10%**<br>⚠️ *(trừ 4.7 → M12)* | ⭐ **Không cần collector**: `show flow monitor cache` xem flow ngay trên router · bẫy "cổng SPAN câm" · IP SLA udp-jitter + Responder | **1.8 GB** | ☐ |
| **18** | Module-12 | JSON/XML/YAML · REST API · Python netmiko/requests · EEM | Automation 15% | Script Python đọc/đổi config qua RESTCONF trên DevNet Sandbox | 2 GB | ☐ |
| **19** | Module-12 | NETCONF/RESTCONF/YANG · Ansible network · DNAC & vManage API · CI/CD ý tưởng | Automation 15% | Ansible playbook backup config 4 router + NETCONF get-config | 3 GB | ☐ |
| **20** | Module-13 | **LAB CAPSTONE** · luyện đề · bẫy đề · chiến thuật phòng thi | Toàn bộ | [Capstone "Mạng công ty VLT"](Module-13-LAB-Capstone.md): 6 node · 13 Task · 100 điểm · 5 bài diễn tập sự cố | **3,5 GB** | ☐ |

**Tổng: 20 tuần ≈ 200 giờ.** Nếu học 15 h/tuần → ~14 tuần. Nếu 6 h/tuần → ~30 tuần. Đừng ép, đừng bỏ.

---

## 2. Blueprint → Module: bạn học cái gì để lấy điểm nào

| Domain blueprint | % đề | Module phụ trách | Mức độ đề hỏi |
|---|:---:|---|---|
| **1.0 Architecture** | 15% | Module-01 (một phần), **Module-09** | Chủ yếu **khái niệm** — vai trò từng thành phần, chọn design nào cho case nào. Ít cấu hình. |
| **2.0 Virtualization** | 10% | **Module-08** | VRF-lite & GRE/IPsec → **cấu hình được**. LISP/VXLAN → hiểu cơ chế + đọc output. |
| **3.0 Infrastructure** | **30%** | **Module-02 → 07B** | **Cấu hình + troubleshoot ở mức sâu.** Đây là chỗ ăn điểm/mất điểm nhiều nhất. |
| **4.0 Network Assurance** | 10% | **Module-11**<br>⚠️ + **Module-12** *(mục 4.7)* | Cấu hình được + **đọc output** là chính.<br>⚠️ Mục **4.7 NETCONF/RESTCONF** thuộc domain này nhưng dạy ở Module-12. |
| **5.0 Security** | 20% | **Module-10** | ACL/CoPP/AAA → cấu hình. 802.1X/TrustSec → hiểu flow + cấu hình cơ bản. |
| **6.0 Automation** | 15% | **Module-12** | **Đọc code/output** (JSON, XML, Python, YANG) nhiều hơn là viết code. |

### 🎯 Chiến lược điểm — đọc kỹ bảng này

| Ưu tiên | Domain | Lý do |
|:---:|---|---|
| 🔴 **Số 1** | Infrastructure (30%) + Security (20%) = **50% đề** | Học kỹ 2 khối này là đã nắm nửa đề. **Không được học nửa vời chỗ này.** |
| 🟠 **Số 2** | Automation (15%) | Bạn có lợi thế (đã làm Terraform/Ansible). Nhưng đề hỏi rất đặc thù Cisco — phải học đúng cách Cisco. |
| 🟡 **Số 3** | Architecture (15%) | Chỉ hỏi khái niệm → **học nhớ, không cần lab nhiều**. Tỷ lệ điểm/công sức tốt nhất. |
| 🟢 **Số 4** | Virtualization (10%) + Assurance (10%) | Ít câu, nhưng dễ ăn điểm nếu đã lab. |

> **Sai lầm điển hình của người tự học:** dành 6 tuần mê mẩn SD-WAN/SD-Access (rất "hot" nhưng đề chỉ hỏi khái niệm),
> rồi vào phòng thi tắc ở câu OSPF LSA type và BGP path selection. **Đừng làm vậy.**

---

## 3. Bảng KIẾN THỨC CHÍNH phải nắm — dùng để tự kiểm tra

Đây là bảng quan trọng nhất của repo. **Học xong mỗi module, quay lại đây tự hỏi mình.**
Nếu không trả lời được bằng lời của mình (không cần nhìn tài liệu) → chưa đạt.

### Module-01 — Packet Forwarding & Kiến trúc thiết bị

| Phải nắm | Tự hỏi |
|---|---|
| 3 plane của thiết bị mạng | Control / Data / Management plane khác nhau gì? Cái nào chạy OSPF? Cái nào forward gói? |
| Process → Fast → CEF switching | Vì sao CEF nhanh hơn process switching? FIB và adjacency table chứa gì? |
| TCAM / CAM | CAM dùng cho gì (L2)? TCAM dùng cho gì (ACL/QoS/L3)? |
| Multilayer switch | Switch L3 forward gói ra sao khác router truyền thống? |
| Cấu trúc thiết bị | Supervisor, line card, backplane, ASIC làm gì? |

### Module-02 — Layer 2

| Phải nắm | Tự hỏi |
|---|---|
| Bầu Root Bridge | 3 bước so sánh: Priority → MAC → (Port ID). Ép root bridge bằng lệnh gì? |
| Port role & state | Root/Designated/Blocking/Alternate/Backup. STP có 5 state, RSTP có 3 — kể ra được không? |
| STP vs RSTP vs MST | Convergence STP ~50s vs RSTP ~vài giây — **vì sao** nhanh hơn? MST giải quyết vấn đề gì của PVST+? |
| Các loại Guard | PortFast, BPDU Guard, BPDU Filter, Root Guard, Loop Guard — đặt ở port nào, chống gì? |
| EtherChannel | LACP vs PAgP vs static (`on`). Mode `active/passive/desirable/auto` — cặp nào bắt tay được? |
| Điều kiện bundle | 5 tham số phải giống nhau giữa các member port là gì? |
| Load-balancing hash | `src-dst-ip` vs `src-mac`… — vì sao 1 flow lớn không chia được qua 2 link? |

### Module-03 — IP Routing nền tảng

| Phải nắm | Tự hỏi |
|---|---|
| Thứ tự chọn route | **Longest prefix match → Administrative Distance → Metric**. Đúng thứ tự này không? |
| AD từng protocol | Connected 0, Static 1, eBGP 20, EIGRP 90, OSPF 110, RIP 120, iBGP 200 |
| Floating static | Cấu hình dự phòng bằng cách nào? Vì sao gọi là "floating"? |
| Redistribute | Seed metric là gì? Vì sao redistribute vào OSPF cần `subnets`? Nguy cơ routing loop? |
| Đọc `show ip route` | Ký hiệu O, O IA, O E1, O E2, B, D EX nghĩa là gì? |

### Module-04 — OSPF

| Phải nắm | Tự hỏi |
|---|---|
| 8 neighbor state | Luồng thường 7 bước: Down → Init → 2-Way → ExStart → Exchange → Loading → Full.<br>Cái thứ 8 là **Attempt** (chỉ NBMA). Kẹt ở ExStart thường do gì? (MTU) |
| Điều kiện lên neighbor | 5 điều kiện phải khớp: area ID, subnet, hello/dead timer, auth, stub flag, MTU |
| LSA type | 1 Router, 2 Network, 3 Summary, 4 ASBR-Summary, 5 External, 7 NSSA-External |
| DR/BDR | Bầu bằng gì? Trên network type nào có bầu, nào không? DR non-preemptive nghĩa là gì? |
| Network type | Broadcast, Point-to-Point, NBMA, P2M — timer & DR khác nhau ra sao? |
| Area type | Backbone, Standard, Stub, Totally Stub, NSSA — LSA nào bị chặn ở đâu? |
| Summarization | `area range` (ABR) vs `summary-address` (ASBR) — dùng cái nào khi nào? |
| Virtual-link | Giải quyết vấn đề gì? Cấu hình giữa 2 router nào? |
| Cost | Cost = reference-bw / interface-bw. Vì sao phải đổi `auto-cost reference-bandwidth`? |

### Module-05 — BGP

| Phải nắm | Tự hỏi |
|---|---|
| eBGP vs iBGP | AD khác nhau (20 vs 200), TTL, rule "iBGP không quảng bá route học từ iBGP" |
| Neighbor state | Idle → Connect → Active → OpenSent → OpenConfirm → Established. "Active" **không** phải trạng thái tốt |
| 13 bước path selection | Weight → LP → Locally originated → AS-path ngắn → Origin → MED → eBGP>iBGP → … |
| Attribute nào lan tới đâu | Weight (chỉ local, không quảng bá) · LP (trong AS) · AS-path & MED (qua eBGP) |
| Đổi hướng traffic | Muốn đổi **outbound** → dùng Weight/LP. Muốn ảnh hưởng **inbound** → AS-path prepend/MED |
| Community | `no-export`, `no-advertise`, `local-AS` khác nhau gì? |
| `next-hop-self` | Khi nào cần? Vì sao thiếu nó thì route "học được mà không dùng được"? |

### Module-06 — FHRP / NAT / IPv6 FHS

| Phải nắm | Tự hỏi |
|---|---|
| HSRP vs VRRP vs GLBP | Cisco-only? Virtual MAC? Ai load-balance được? Priority default? |
| HSRP state | Init → Learn → Listen → Speak → Standby → Active. Preempt default **tắt** — nhớ chỗ này |
| Object tracking | Vì sao HSRP cần track? Không track thì lỗi gì xảy ra? |
| NAT các loại | Static NAT, Dynamic NAT, PAT, NAT overload, NAT64/NPTv6 |
| `inside`/`outside` | Đặt sai chiều thì hỏng — quy tắc là gì? Thứ tự NAT và routing? |
| IPv6 FHS | RA Guard, DHCPv6 Guard, IPv6 Snooping — chống tấn công gì? |

### Module-07A — Wireless: RF, 802.11, AP mode & Antenna

| Phải nắm | Tự hỏi |
|---|---|
| Đơn vị RF | dBm, mW, dB, dBi — cái nào tuyệt đối, cái nào tương đối? Quy tắc 3 & 10? |
| EIRP | `EIRP = Tx − cable loss + antenna gain` — vì sao loss trừ mà gain cộng? |
| RSSI / Noise / SNR | `SNR = RSSI − noise`. Ngưỡng −67 dBm và SNR 25 dB. **RSSI mạnh mà kết nối vẫn tệ — vì sao?** |
| Band & channel | 2.4 GHz vì sao chỉ 1/6/11? 4 UNII band, band nào cần DFS? DFS gây ra hiện tượng lạ nào? |
| Channel bonding | 20→40→80→160 MHz: SNR và số channel thay đổi ra sao? |
| CCI vs ACI | Cái nào **làm chậm**, cái nào **làm hỏng**? Vì sao ACI tệ hơn? |
| CSMA/CA | Vì sao Wi-Fi là half-duplex chia sẻ? CCA, NAV, backoff, ACK. Hidden node & RTS/CTS? |
| 802.11 standard | a/b/g/n/ac/ax — band, tốc độ, điểm nhận dạng. **a là 5 GHz · ac CHỈ 5 GHz · ax có cả 2.4** |
| MIMO / MU-MIMO / OFDMA | Đọc `4x4:4`. MU-MIMO chia **không gian**, OFDMA chia **tần số** — chuẩn nào có cái nào? |
| Client join | Beacon/Probe → 802.11 Auth → Association → 4-way handshake → DHCP. "Associated" đã xong chưa? |
| BSS/BSSID/SSID/ESS | 1 AP dual-band phát 4 SSID = mấy BSSID? Hệ quả? |
| AP mode | Local, FlexConnect, Monitor, Sniffer, Rogue Detector, SE-Connect, Bridge, Flex+Bridge, Sensor. **Cái nào tắt radio?** |
| Antenna | Omni vs directional · patch/yagi/dish · gain ⟺ beamwidth · polarization |
| Capacity design | 6 cách tăng capacity. Vì sao "tăng công suất AP" là sai lầm phổ biến nhất? |

### Module-07B — CAPWAP, WLC, FlexConnect & Roaming

| Phải nắm | Tự hỏi |
|---|---|
| Split-MAC | Chức năng nào ở AP, chức năng nào ở WLC? **Nguyên tắc chia** là gì? |
| CAPWAP | Control **5246** (DTLS luôn bật) / Data **5247** (DTLS tùy chọn). Chạy ở tầng nào? |
| MTU | Triệu chứng nhận dạng lỗi MTU? Lệnh kiểm chứng? |
| AP join | 6 giai đoạn theo thứ tự. Vì sao sai giờ (NTP) làm AP không join được? |
| Discovery algorithms | 5 cách. Cách nào **chết** khi AP khác subnet với WLC? Chuỗi hex option 43? |
| WLC selection | Primary → Secondary → Tertiary → Master → **Least-loaded**. "Least-loaded" nghĩa chính xác? |
| AP HA | HA SSO vs N+1 — khác biệt quan trọng nhất là gì? |
| FlexConnect | 2 trục (switching/auth) → 4 tổ hợp. **Cái gì sống sót ở Standalone mode?** Vì sao bắt buộc trunk? |
| Roaming | Intra-controller · Inter-controller **L2** (MOVE, không tunnel) · **L3** (COPY + tunnel) |
| Anchor / Foreign | Cái nào là WLC gốc? Guest anchor dùng để làm gì? |
| Fast roaming | 802.11 **k** (chỉ đường) · **v** (gợi ý) · **r** (trao đổi key trước). OKC có phải chuẩn IEEE? |
| Sticky client | Tác hại (2) và cách trị (4)? |
| WLAN config (C9800) | Chuỗi WLAN Profile → Policy Profile → **Policy Tag** → AP. 3 lỗi cấu hình kinh điển? |
| Wireless security | WPA2 vs WPA3 · PSK vs SAE · Personal vs Enterprise · EAP-TLS vs PEAP · PMF |
| **Troubleshoot (3.3.e)** | **6 tầng**: RF → AP join → WLAN config → Auth → IP/DHCP → Upstream. "Client dừng ở State nào?" |

### Module-08 — Virtualization & Overlay

| Phải nắm | Tự hỏi |
|---|---|
| VRF-lite | Tách bảng route ra sao? Lệnh nào gán interface vào VRF? Ping trong VRF gõ thế nào? |
| **2 bẫy VRF** | Gán VRF vào interface có IP → chuyện gì? Vì sao `ping <ip>` không tới host trong VRF? |
| GRE | Tunnel source/destination, MTU overhead 24 byte, vì sao GRE không mã hóa? |
| **Recursive routing** | `%TUN-5-RECURDOWN` xảy ra khi nào? 2 cách sửa? Nguyên tắc vàng là gì? |
| **MTU/MSS** | "Ping OK nhưng web treo nửa chừng" → 2 lệnh nào? Vì sao `adjust-mss` quan trọng hơn? |
| IPsec | IKE phase 1 vs 2, transform-set, tunnel vs transport mode, GRE over IPsec |
| **Đọc trạng thái IPsec** | `QM_IDLE` vs `MM_NO_STATE`? `encaps` tăng mà `decaps` = 0 nghĩa gì? |
| **Vì sao phải ghép** | Vì sao IPsec thuần không chạy được OSPF? GRE over IPsec dùng mode nào? |
| LISP | Vai trò: ITR/ETR/xTR, MS/MR, ALT. Tách "who" (EID) khỏi "where" (RLOC) nghĩa là gì? |
| VXLAN | VNI 24-bit (16 triệu segment), VTEP, encap UDP 4789, vì sao cần cho DC |
| Hypervisor | Type 1 vs Type 2, vSwitch, VLAN trunk vào host ảo hóa |

### Module-09 — Architecture & QoS

| Phải nắm | Tự hỏi |
|---|---|
| 2-tier vs 3-tier | Collapsed core dùng khi nào? Khi nào cần tách core? |
| Spine-Leaf | Vì sao DC dùng spine-leaf thay 3-tier? East-West traffic là gì? |
| HA | SSO vs NSF vs GR khác nhau gì? vPC khác VSS/StackWise chỗ nào? |
| SD-Access | 5 thành phần: Control plane node (LISP), Border node, Edge node, WLC, DNA Center + ISE |
| Fabric = ? | Underlay vs Overlay. SD-Access dùng LISP (control) + VXLAN (data) + TrustSec (policy) |
| **Anycast gateway** | Cơ chế là gì? Nó thay thế cái gì? Vì sao SD-Access không cần HSRP? |
| **VN vs SGT** | Cái nào là VRF/macro, cái nào là micro? Fusion router giải quyết vấn đề gì? |
| **SD-Access wireless** | Control plane đi đường nào? **Data plane** đi đường nào? |
| SD-WAN | **vManage** (quản lý), **vSmart** (control/policy), **vBond** (orchestrate/NAT traversal), **vEdge/cEdge** (data) |
| **SD-WAN — 3 câu chốt** | Thành phần nào cần **IP public**? Ai chạy **OMP**? Traffic người dùng **có qua vSmart không**? |
| **TLOC & color** | TLOC gồm 3 thành phần nào? Private color khác public color chỗ nào? AAR dựa vào gì? |
| **SD-WAN vs SD-Access** | Phạm vi · controller · control plane · data plane — 4 điểm khác biệt |
| QoS model | Best Effort, IntServ, **DiffServ** (cái ENCOR hỏi) |
| Marking | CoS (L2, 3 bit), DSCP (L3, 6 bit), EF=46, AF41=34, CS6=48 |
| **Ngưỡng Voice** | **150 ms / 30 ms / 1 %** — latency, jitter, loss. Nhớ chưa? |
| **Công thức AF** | `AFxy = 8x + 2y` · `CSx = 8x`. Trong AFxy, **y cao** nghĩa là gì? |
| **Trust boundary** | Đặt ở đâu? Vì sao **không tin DSCP từ PC người dùng**? |
| Policing vs Shaping | Cái nào drop, cái nào buffer? Dùng ở inbound hay outbound? Use case của shaping? |
| Queue | LLQ, CBWFQ, WRED — cái nào cho voice? Vì sao CBWFQ **không đủ** cho voice? Priority queue tối đa %? |
| **WRED** | Chống hiện tượng gì? 2 điều **cấm kỵ** khi dùng WRED? |
| **Wireless QoS** | WMM có mấy access category? Vấn đề **CAPWAP** với QoS là gì? |

### Module-10 — Security

| Phải nắm | Tự hỏi |
|---|---|
| Hardening | Tắt gì (AUX, CDP ra ngoài, HTTP server), bật gì (SSH v2, `login block-for`, `exec-timeout`, banner cảnh báo) |
| **Password type** | 0/5/7/8/9 — cái nào **giải ngược được**? `service password-encryption` thực sự làm gì? |
| AAA | Authentication / Authorization / Accounting. **TACACS+ vs RADIUS**: port, TCP/UDP, mã hóa gì, tách A-A-A không? |
| **Method list & fallback** | **`reject` vs `timeout`** — cái nào cho fallback sang `local`? 4 quy tắc để không tự khóa mình? |
| ACL | Standard vs Extended, thứ tự xử lý, implicit deny, wildcard mask, đặt gần source hay dest? |
| **Bẫy IPv6 ACL** | Cuối IPv6 ACL có **mấy dòng ngầm**? Vì sao `deny ipv6 any any` tường minh **giết NDP**? |
| **PACL/VACL/RACL** | Thứ tự ingress? Cái nào lọc được traffic **trong cùng VLAN**? VACL kết thúc bằng gì? |
| CoPP | Bảo vệ plane nào? Vì sao cần? Cấu hình bằng MQC ra sao? Vì sao phải **"đo trước, siết sau"**? |
| **CPPr** | 3 sub-interface? **ARP và TTL-exceeded** rơi vào cái nào? |
| 802.1X | 3 vai: Supplicant / Authenticator / Auth Server. **Ai ra quyết định?** EAPoL ở tầng nào? |
| **Host mode & VLAN dự phòng** | 4 host mode — cái nào cho phone+PC? **Guest / Auth-fail / Critical VLAN** khác nhau gì? |
| **2 dòng hay quên** | Thiếu gì thì 802.1X "không chạy mà không báo lỗi"? Thiếu gì thì VLAN/SGT không được áp? |
| **Wireless security** | WPA2 vs WPA3 (SAE) vs OWE · **PEAP vs EAP-TLS bên nào cần chứng thư** · vì sao pre-auth ACL phải mở DNS |
| TrustSec | SGT là gì? **3 pha**? Enforcement ở ingress hay **egress**, vì sao? Inline tagging & SXP |
| MACsec | Mã hóa ở lớp nào? **Hop-by-hop hay end-to-end**? Dùng MKA hay IKE? Switch-to-switch vs host-to-switch |
| **NGFW / IDS-IPS** | NGFW khác firewall stateful ở đâu? **IDS out-of-band vs IPS inline** |
| **REST API security** | **401 vs 403** khác gì? Basic Auth có an toàn không? Token của DNAC gọi là gì? |

### Module-11 — Network Assurance

| Phải nắm | Tự hỏi |
|---|---|
| **NTP là nền tảng** | Vì sao sai giờ làm HỎNG cả syslog, NetFlow lẫn IP SLA one-way delay? |
| Syslog | 8 severity 0–7 (Emergency…Debug). **Số nhỏ hay lớn nghiêm trọng hơn?** Level 4 gửi lên server thì gửi những level nào? |
| **Bẫy %LINK vs %LINEPROTO** | Vì sao cùng sự kiện rút cáp lại sinh 2 dòng khác severity? Hệ quả khi đặt `logging trap 4`? |
| SNMP | v2c vs v3: v3 thêm gì? 3 security level của v3 (noAuthNoPriv/authNoPriv/authPriv) |
| **Port & Trap/Inform** | Agent nghe port nào, manager nghe port nào? **Trap khác Inform** chỗ nào? |
| NetFlow vs Flexible NetFlow | **7 field** định nghĩa flow truyền thống (đừng quên ToS + input interface). FNF cho phép làm gì thêm? |
| **4 thành phần FNF** | Record / Exporter / Monitor / Sampler. **`match` khác `collect`** thế nào? |
| **`cache timeout active`** | Mặc định bao nhiêu? Vì sao con số đó nguy hiểm? |
| SPAN family | SPAN (local) / RSPAN (qua VLAN) / **ERSPAN** (qua L3, dùng GRE) — chọn cái nào khi nào? |
| **Bẫy SPAN destination** | Cổng đích bị gì? Vì sao thiết bị cắm vào mất mạng dù cổng `up/up`? Oversubscription? |
| IPSLA | Đo gì? Cấu hình 1 operation icmp-echo cần mấy dòng? Dùng chung với object tracking ra sao? |
| **`ip sla schedule` & Responder** | Quên schedule thì sao? Operation nào **bắt buộc** cần Responder? `reachability` vs `state`? |
| Debug an toàn | Vì sao `debug all` là tự sát trên production? **Thủ phạm thật là gì?** `terminal monitor`, conditional debug |
| **Bẫy CEF khi debug** | Vì sao `debug ip packet` không thấy traffic đi xuyên qua router? |
| DNA Center Assurance | Health score, Network Time Travel, Path Trace, Client 360 |
| **NETCONF/RESTCONF (4.7)** | ⚠️ **Thuộc Domain 4.0 chứ không phải 6.0!** Port 830 vs 443 · cái nào có rollback? → học ở M12 |

### Module-12 — Automation

| Phải nắm | Tự hỏi |
|---|---|
| Đọc data format | JSON `{}`/`[]`, XML thẻ đóng-mở, YAML thụt đầu dòng. **Đề cho snippet, hỏi giá trị nào** |
| REST | Method GET/POST/PUT/PATCH/DELETE, status code 200/201/400/401/403/404/500, header, token auth |
| NETCONF vs RESTCONF | NETCONF: SSH port 830, XML, RPC. RESTCONF: HTTPS 443, JSON/XML, HTTP verb |
| YANG | Model là gì? Native vs OpenConfig vs IETF model |
| EEM | Applet: `event` + `action`. Ví dụ tự backup config khi có ai `write mem` |
| Python | Đọc được script netmiko/requests, biết `for`/`if`/dict/list, hiểu output script in ra gì |
| Ansible | Playbook/inventory/module, idempotent nghĩa gì, `ios_config` vs `ios_command` |
| Controller API | DNAC: xin token rồi mới gọi API. vManage: session cookie. Biết flow, không cần nhớ endpoint |

---

## 4. Mốc kiểm tra (Milestone) — cửa kiểm soát chất lượng

Không đạt milestone thì **không sang giai đoạn sau**. Đây là chỗ giữ bạn khỏi học nửa vời.

| Sau tuần | Milestone | Bài kiểm tra tự chấm |
|:---:|---|---|
| **2** | 🚪 **Ready for ENCOR** | Từ lab trắng, tự dựng: 2 switch + trunk + 2 VLAN + SVI + 2 router OSPF area 0 + NAT + ACL. **Không nhìn tài liệu.** Trong 60 phút. |
| **6** | 🚪 **L2 vững** | Dựng 4 switch, ép root bridge theo ý muốn, bật đủ 4 loại Guard đúng port, tạo 1 L2 + 1 L3 EtherChannel. Giải thích được vì sao mỗi port ở role đó. |
| **11** | 🚪 **Routing vững — mốc quan trọng nhất** | OSPF multi-area + stub + summarization, eBGP 3 AS ép được đường bằng 3 attribute khác nhau, HSRP failover có tracking. **Đạt được đây là bạn đã qua 30% đề.** |
| **15** | 🚪 **Kiến trúc & Overlay** | Vẽ lại từ đầu trên giấy: topology 3-tier, SD-Access 5 role, SD-WAN 4 thành phần, QoS flow classify→mark→queue. Dựng được VRF-lite + GRE over IPsec. |
| **19** | 🚪 **Sẵn sàng ôn thi** | Cấu hình được AAA + CoPP + Flexible NetFlow + ERSPAN + IPSLA. Viết được 1 script Python lấy interface qua RESTCONF. Chạy được 1 Ansible playbook backup config. |
| **20** | 🚪 **Sẵn sàng book exam** | **Boson ExSim-Max 350-401 đạt ≥ 85% ổn định qua 3 lần đề khác nhau.** Chưa đạt thì đừng đóng $400. |

---

## 5. Nếu bạn bị chậm tiến độ

Chuyện bình thường. Đây là cách xử lý — **theo thứ tự này**, đừng tự ý cắt bừa:

| Nếu | Cắt cái này | Tuyệt đối KHÔNG cắt |
|---|---|---|
| Chậm 2–4 tuần | Gộp Module-07 Wireless còn 1 tuần (chỉ học bảng + khái niệm, bỏ lab DevNet) | Module-02, 04, 05 (STP/OSPF/BGP) |
| Chậm 5–8 tuần | Rút Module-09 còn 3 ngày (đọc bảng + nhớ vai trò thành phần) | Module-10 Security (20% đề) |
| Chậm > 8 tuần | Rút Module-01, Module-08 xuống mức "đọc bảng + 1 lab duy nhất" | Milestone tuần 11 — **bắt buộc phải đạt** |
| Kiệt sức | **Nghỉ hẳn 1 tuần**, không đọc gì. Rồi quay lại từ bảng 📘 của module đang dở | Đừng bỏ ngang giữa module |

> **Quy tắc vàng:** thà đi 30 tuần và đỗ, hơn ép 12 tuần rồi bỏ ở tuần thứ 9.
> Người tự học rớt vì bỏ ngang nhiều hơn là vì thi không đủ điểm.

---

## 6. Ngân sách RAM lab — PC 16 GB của bạn

Bảng này quyết định lab nào dựng được. **Xem trước khi mở lab lớn.**

| Loại node | RAM khuyến nghị | Ghi chú |
|---|:---:|---|
| IOL / IOU (L2 hoặc L3) | **256 MB** | Nhẹ nhất. Ưu tiên cho topology ≥ 6 node |
| vIOS (router) | **512 MB** | Đủ cho hầu hết lab routing |
| vIOS-L2 (switch) | **768 MB** | Dùng cho lab STP/EtherChannel |
| CSR1000v | **3 GB** | Chỉ dùng khi cần feature mới (RESTCONF, NETCONF) |
| vWLC | 2 GB | Lab wireless — tuần 12–13, cân nhắc dùng DevNet thay |
| Cat9kv | ⛔ 18 GB | **Máy bạn không kham được.** Dùng DevNet Sandbox |
| Nexus 9000v | ⛔ 8 GB | Không nên. Đề ENCOR không bắt buộc NX-OS |

**Ngân sách thực tế:** VM EVE-NG cấp **12 GB** → dùng an toàn khoảng **10 GB** cho node.

| Kịch bản lab | Cấu hình | RAM | Kham được? |
|---|---|:---:|:---:|
| Lab routing thường | 4× vIOS | 2 GB | ✅ Rất thoải mái |
| Lab L2 (STP/MST) | 4× vIOS-L2 | 3 GB | ✅ Thoải mái |
| Lab hỗn hợp | 2× vIOS-L2 + 3× vIOS | 3 GB | ✅ Thoải mái |
| Lab capstone tuần 20 | 3× vIOS-L2 + 3× vIOS | 3.8 GB | ✅ OK |
| Lab RESTCONF | 1× CSR1000v + 1× Linux host | 3.5 GB | ✅ OK |
| Lab wireless | 1× vWLC + 2× vIOS-L2 | 3.5 GB | ⚠️ Chạy được nhưng vWLC hay kén image |
| Lab SD-WAN on-prem | vManage+vSmart+vBond+2 vEdge | ⛔ 20+ GB | ❌ Dùng DevNet Sandbox |

💡 **Mẹo tiết kiệm RAM:** trong EVE-NG chỉ **Start** những node đang cần, không start cả lab.
Node đã Stop không ăn RAM.

---

## 7. Chi phí dự kiến

| Mục | Chi phí | Bắt buộc? |
|---|---|:---:|
| EVE-NG Community | **$0** | ✅ Đã chốt |
| VMware Workstation | $0 (bản Player/Pro cho dùng cá nhân) | ✅ Bạn đã có |
| Sách OCG (ENCOR 350-401 Official Cert Guide) | ~$50 | ✅ **Nên có** — repo này bổ trợ, không thay sách |
| Cisco DevNet Sandbox | **$0** | ✅ Đã chốt |
| Boson ExSim-Max 350-401 | ~$100 | ✅ **Rất nên** — đề sát nhất, dùng để quyết định book thi |
| Video (CBT Nuggets / INE / Kevin Wallace) | $50–$60/tháng | ⭕ Tùy — dùng khi lý thuyết bí |
| Phí thi 350-401 | ~$400 | ✅ Nếu muốn cert |
| **Tối thiểu để đỗ** | **≈ $550** | (sách + Boson + phí thi) |

---

## 8. Tuần này bạn làm gì

| Bước | Việc | File |
|:---:|---|---|
| 1 | Đọc hết README (nhất là §5 Cách dùng repo) | [README.md](README.md) |
| 2 | **Dựng lab EVE-NG** — đừng đọc lý thuyết trước khi có lab | [Module-00](Module-00-Setup-Lab-EVE-NG.md) |
| 3 | Đặt hàng sách OCG 350-401 (giao mất vài ngày, đặt sớm) | [Tai-lieu-tham-khao.md](Tai-lieu-tham-khao.md) |
| 4 | Tạo file `SO-TAY-LOI.md` rỗng trong repo này | — |
| 5 | Chốt lịch cố định 5 buổi/tuần vào calendar. **Lịch cố định quan trọng hơn động lực.** | — |
