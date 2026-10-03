# 結果展示

https://github.com/user-attachments/assets/d6e1f5af-a816-40ea-b923-d982f28812f0

---

# 一、 硬體實體接線總結

### 1. 完整腳位接線對照總表

#### ① 系統電源分送（由 LOLIN D32 提供）
| 來源腳位 (LOLIN D32) | 連接目標 (830 孔麵包板) | 說明 |
| :--- | :--- | :--- |
| **`3V`** (3.3V 輸出) | 麵包板 **紅色 (+) 導軌** | 提供全電路純淨 3.3V 電源 |
| **`GND`** (接地) | 麵包板 **藍色 (-) 導軌** | 全電路共用地線 |

#### ② 發射端：紅色 LED 光源（GPIO 控制）
| 元件端子 | 連接目標 | 說明 |
| :--- | :--- | :--- |
| **220Ω 電阻** | 一端接 **LOLIN D32 `GPIO 18`**，另一端接 **LED 長腳 (陽極 +)** | 限制電流保護 LED |
| **LED 短腳 (陰極 -)** | 麵包板 **藍色 (-) 導軌 (GND)** | 形成迴路接地 |

#### ③ 接收端：光敏電阻分壓與 LM358P 比較器
| 元件名稱 | 接腳編號 / 端子 | 連接目標 | 說明 |
| :--- | :--- | :--- | :--- |
| **LM358P 運算放大器** | **Pin 8 (VCC)** | 麵包板 **紅色 (+) 導軌 (3.3V)** | 晶片供電 |
| | **Pin 4 (GND)** | 麵包板 **藍色 (-) 導軌 (GND)** | 晶片接地 |
| | **Pin 2 (IN1-)** | 10K 可變電阻 **Pin 2 (中間滑動腳)** | 遮光觸發門檻電壓輸入 |
| | **Pin 3 (IN1+)** | 麵包板 **第 15 行 (分壓節點)** | 光敏電阻即時訊號輸入 |
| | **Pin 1 (OUT1)** | LOLIN D32 **`GPIO 4`** | 輸出乾淨方波至中斷腳位 |
| **10K 可變電阻 (WH148)** | **Pin 1 (左腳)** | 麵包板 **紅色 (+) 導軌 (3.3V)** | 門檻電位上端 |
| | **Pin 3 (右腳)** | 麵包板 **藍色 (-) 導軌 (GND)** | 門檻電位下端 |
| **光敏電阻分壓節點** | 光敏電阻 腳 1 | 麵包板 **紅色 (+) 導軌 (3.3V)** | 感測光強 |
| *(麵包板第 15 行)* | 光敏電阻 腳 2 | 麵包板 **第 15 行** | 連接分壓點 |
| | 10kΩ 固定電阻 腳 1 | 麵包板 **第 15 行** | 連接分壓點 |
| | 10kΩ 固定電阻 腳 2 | 麵包板 **藍色 (-) 導軌 (GND)** | 下拉接地 |

#### ④ OLED 螢幕模組 (I2C 通訊)
| OLED 螢幕接腳 | 連接目標 | 說明 |
| :--- | :--- | :--- |
| **VCC** | 麵包板 **紅色 (+) 導軌 (3.3V)** | 螢幕供電 |
| **GND** | 麵包板 **藍色 (-) 導軌 (GND)** | 螢幕接地 |
| **SCL** | LOLIN D32 **`GPIO 22`** | I2C 時脈線 |
| **SDA** | LOLIN D32 **`GPIO 23`** | I2C 資料線 |

---

# 二、 MicroPython 完整程式碼

ESP32 內部 Flash 需包含以下三個檔案：

### 檔案 1：`ble_uart_repl.py` (底層 BLE 藍牙 REPL 串流驅動)
```python
# ble_uart_repl.py
import bluetooth
import io
import os
import time
import struct
from micropython import const

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_FLAG_READ = const(0x0002)
_FLAG_WRITE_NO_RESPONSE = const(0x0008)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (
    bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_READ | _FLAG_NOTIFY,
)
_UART_RX = (
    bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_WRITE | _FLAG_WRITE_NO_RESPONSE,
)
_UART_SERVICE = (
    _UART_UUID,
    (_UART_TX, _UART_RX),
)

class BLEUARTStream(io.IOBase):
    def __init__(self, ble, name="ESP32-SpeedTrap"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        
        try:
            self._ble.config(rxbuf=1024)
        except Exception:
            pass
            
        ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((_UART_SERVICE,))
        self._ble.gatts_set_buffer(self._handle_rx, 512, True)
        
        self._connections = set()
        self._rx_buf = bytearray()
        self._adv_payload = self._create_payload(name=name)
        self._resp_payload = self._create_payload(services=[_UART_UUID])
        self._advertise()

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
            self._rx_buf = bytearray()
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self._connections.discard(conn_handle)
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if value_handle == self._handle_rx:
                self._rx_buf.extend(self._ble.gatts_read(value_handle))

    def _create_payload(self, limited_disc=False, br_edr=False, name=None, services=None):
        payload = bytearray()
        def _append(adv_type, adv_data):
            nonlocal payload
            payload += struct.pack("BB", len(adv_data) + 1, adv_type) + adv_data
        _append(0x01, struct.pack("B", (0x01 if limited_disc else 0x02) + (0x18 if br_edr else 0x04)))
        if name:
            _append(0x09, name.encode("utf-8"))
        if services:
            for uuid in services:
                b = bytes(uuid)
                if len(b) == 2:
                    _append(0x03, b)
                elif len(b) == 16:
                    _append(0x07, b)
        return payload

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._adv_payload, resp_data=self._resp_payload)

    def readinto(self, buf):
        if not self._rx_buf:
            return None
        n = min(len(buf), len(self._rx_buf))
        buf[:n] = self._rx_buf[:n]
        self._rx_buf = self._rx_buf[n:]
        return n

    def write(self, buf):
        if not self._connections:
            return len(buf)
        for conn_handle in self._connections:
            for i in range(0, len(buf), 20):
                chunk = buf[i:i+20]
                for _ in range(10):
                    try:
                        self._ble.gatts_notify(conn_handle, self._handle_tx, chunk)
                        break
                    except OSError as err:
                        if err.args[0] == 12 or getattr(err, 'errno', 0) == 12:
                            time.sleep_ms(10)
                        else:
                            break
                    except Exception:
                        break
        return len(buf)

    def ioctl(self, op, arg):
        if op == 1: return 1 if len(self._rx_buf) > 0 else 0
        if op == 2: return 1 if len(self._connections) > 0 else 0
        return 0
```

---

### 檔案 2：`boot.py` (開機自動啟動 BLE REPL)
```python
# boot.py
import bluetooth
import os
from ble_uart_repl import BLEUARTStream

ble = bluetooth.BLE()
stream = BLEUARTStream(ble, name="LOLIN-SpeedTrap")
os.dupterm(stream)
```

---

### 檔案 3：`main.py` (測速應用核心庫)
```python
# main.py
import time
import framebuf
from machine import Pin, I2C

# ==================== 1. SSD1306 OLED 驅動 ====================
class SSD1306:
    def __init__(self, i2c, addr=0x3C, width=128, height=64):
        self.i2c = i2c
        self.addr = addr
        self.width = width
        self.height = height
        self.buffer = bytearray(self.width * self.height // 8)
        self.fb = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.init_display()

    def init_display(self):
        cmds = (0xAE, 0xD5, 0x80, 0xA8, 0x3F, 0xD3, 0x00, 0x40, 0x8D, 0x14,
                0x20, 0x00, 0xA1, 0xC8, 0xDA, 0x12, 0x81, 0xCF, 0xD9, 0xF1,
                0xDB, 0x40, 0xA4, 0xA6, 0xAF)
        for cmd in cmds:
            self.i2c.writeto(self.addr, bytearray([0x80, cmd]))
        self.clear()

    def clear(self):
        self.fb.fill(0)
        self.show()

    def show(self):
        self.i2c.writeto(self.addr, bytearray([0x80, 0x21, 0x80, 0, 0x80, 127, 0x80, 0x22, 0x80, 0, 0x80, 7]))
        self.i2c.writeto_mem(self.addr, 0x40, self.buffer)

    def text(self, msg, x, y):
        self.fb.text(msg, x, y, 1)

# ==================== 2. 硬體初始化 ====================
i2c = I2C(0, scl=Pin(22), sda=Pin(23), freq=400000)

try:
    oled = SSD1306(i2c, addr=0x3C)
    oled_ok = True
except Exception as e:
    oled_ok = False
    print(f"[警告] OLED 未連線: {e}")

def show_oled(l1="", l2="", l3="", l4=""):
    """在 OLED 螢幕繪製 4 行資訊"""
    if not oled_ok: return
    oled.fb.fill(0)
    oled.text(l1, 0, 2)
    oled.text(l2, 0, 18)
    oled.text(l3, 0, 34)
    oled.text(l4, 0, 50)
    oled.show()

# 發射端 LED 控制 (LOLIN D32: GPIO 18)
led_emitter = Pin(18, Pin.OUT, value=0)

def led_on():
    """手動開啟紅色 LED 發射端"""
    led_emitter.value(1)
    print("💡 發射端 LED 已手動開啟 (ON)")

def led_off():
    """手動關閉紅色 LED 發射端"""
    led_emitter.value(0)
    print(" 發射端 LED 已手動關閉 (OFF)")

# ==================== 3. 防抖動中斷狀態機 ====================
STATE_IDLE = 0
STATE_BLOCKED = 1
STATE_FINISHED = 2

state = STATE_IDLE
t_enter = 0
t_exit = 0

def gate_isr(pin):
    global state, t_enter, t_exit
    val = pin.value()
    now = time.ticks_us()
    
    # 車頭切入遮光 (下降沿)
    if val == 0 and state == STATE_IDLE:
        t_enter = now
        state = STATE_BLOCKED
        
    # 車尾離開透光 (上升沿)
    elif val == 1 and state == STATE_BLOCKED:
        if time.ticks_diff(now, t_enter) > 1000: # 濾除 < 1ms 雜訊
            t_exit = now
            state = STATE_FINISHED

# 光門中斷 (GPIO 4)
gate1 = Pin(4, Pin.IN, Pin.PULL_UP)
gate1.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=gate_isr)

# ==================== 4. 校準模式 ====================
def calibrate(duration_sec=10):
    """
    光門即時對齊與門檻監測模式
    """
    if led_emitter.value() == 0:
        print("⚠️ 提醒: 發射端 LED 目前為關閉狀態，若需要光源請先執行 led_on()")
        
    print(f"\n🔧 === 啟動光門監測模式 (持續 {duration_sec} 秒) ===")
    print("👉 請調整 LED 對準角度或旋轉可變電阻...")
    
    start_t = time.time()
    while time.time() - start_t < duration_sec:
        val = gate1.value()
        remain = duration_sec - int(time.time() - start_t)
        
        if val == 1:
            status_term = "🟢 [正常] 光束對準 (Logic 1)"
            status_oled = ">> BEAM OK! <<"
            detail_oled = "Status: UNBLOCKED"
        else:
            status_term = "🔴 [遮蔽/失準] 光束中斷 (Logic 0)"
            status_oled = "!! BLOCKED !!"
            detail_oled = "Status: BLOCKED"
            
        print(f"\r{status_term} | 倒數: {remain}s  ", end="")
        show_oled("=== CALIBRATION ===", status_oled, detail_oled, f"Time left: {remain}s")
        time.sleep_ms(100)
        
    print("\n✅ 監測結束！")
    show_oled("CALIBRATION DONE", "Ready for Race!", "Type in REPL:", "test_speed(8.0)")

# ==================== 5. 測速核心函式 ====================
def test_speed(car_len_cm=8.0, timeout_sec=15):
    """
    單光門測速流程
    :param car_len_cm: 小車長度 (公分，預設 8.0 cm)
    """
    global state, t_enter, t_exit
    
    if led_emitter.value() == 0:
        print("⚠️ 警告: 發射端 LED 尚未開啟！請先輸入 led_on() 開燈。")
        show_oled("SPEED TRAP", "LED is OFF!", "Type: led_on()", "in REPL")
        return
        
    show_oled("SPEED TRAP READY", f"Len: {car_len_cm} cm", ">> READY <<", "Pass Gate...")
    print(f"\n🚗 [測速儀就緒] 車長設定: {car_len_cm} cm")
    
    if gate1.value() == 0:
        print("⚠️ 警告: 光門正處於遮蔽狀態，請移開障礙物...")
        while gate1.value() == 0:
            time.sleep_ms(20)
            
    time.sleep_ms(50)
    state = STATE_IDLE
    t_enter = 0
    t_exit = 0
    
    print("🟢 光門就緒，請放車衝線！")
    
    start_wait = time.time()
    while state != STATE_FINISHED:
        if time.time() - start_wait > timeout_sec:
            print("⏱️ [逾時] 逾時未偵測到物體衝線。")
            show_oled("SPEED TRAP", "Timeout!", "No Object", "Try Again")
            return
        time.sleep_ms(5)
        
    dt_us = time.ticks_diff(t_exit, t_enter)
    dt_ms = dt_us / 1000.0
    speed_kmh = (car_len_cm / dt_us) * 36000.0
    speed_ms = (car_len_cm / 100.0) / (dt_us / 1000000.0)
    
    print("\n" + "="*35)
    print(f"🏁 衝線成功！")
    print(f"⏱️ 遮光時間: {dt_ms:.2f} ms [{dt_us} us]")
    print(f"🚀 衝線時速: {speed_kmh:.2f} km/h ({speed_ms:.2f} m/s)")
    print("="*35)
    
    show_oled("=== RESULT ===",
              f"SPD: {speed_kmh:.2f}km/h",
              f"     ({speed_ms:.2f}m/s)",
              f"Time:{dt_ms:.1f}ms")

# 開機歡迎畫面
show_oled("ESP32 SPEED TRAP", "Lolin D32 Ready", "1. led_on()", "2. test_speed()")
print("=== ESP32 LOLIN D32 測速系統已啟動 (手動 LED 模式) ===")
```

---

# 三、 操作

1. **通電與無線連線：**
   * LOLIN D32 插上 USB 線（接電腦或行動電源供電）。
   * 手機開啟瀏覽器至 `https://viper-ide.org` ➔ 點擊連線並選擇藍牙 **`LOLIN-SpeedTrap`**。
2. **開啟光源：**
   * 在終端機輸入：`led_on()` （左側紅色 LED 亮起）。
3. **賽道對準校準（可選）：**
   * 輸入：`calibrate(10)` ➔ 觀察 OLED 顯示 `>> BEAM OK! <<`。
4. **小車測速（可連續測速）：**
   * 輸入：`test_speed(8.0)` （可依小車長度調整公分數）。
   * 放車衝線 ➔ OLED 螢幕與手機終端機同步跳出時速（km/h 與 m/s）。
5. **關燈待機：**
   * 比賽結束輸入：`led_off()` 關閉 LED。  

---

# 四、 Racing Competition


https://github.com/user-attachments/assets/d15a34de-b5b8-4c0c-97b3-0d499e5ec0c4



https://github.com/user-attachments/assets/fd1b4cef-f2aa-43d7-957b-eb6b973fdf1c

