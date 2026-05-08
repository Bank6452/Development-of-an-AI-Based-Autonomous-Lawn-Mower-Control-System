# STM32 Bluepill Pinout Report (Mower Project)

เอกสารสรุปการใช้งานขา (Pin Assignment) ทั้งหมดของหุ่นยนต์ตัดหญ้า ณ ปัจจุบัน

## 🔴 ขาที่ถูกใช้งานแล้ว (DO NOT USE)

| หมวดหมู่ | ขา (Pin) | หน้าที่ (Function) | หมายเหตุ |
| :--- | :--- | :--- | :--- |
| **Encoders** | PA0, PA1 | Encoder ล้อซ้าย | ใช้ Interrupt (CHANGE) |
| | PA4, PA5 | Encoder ล้อขวา | ใช้ Interrupt (CHANGE) |
| **Motors** | PB4, PB5 | คุมมอเตอร์ตีนตะขาบ | ใช้ไลบรารี Servo (PWM) |
| **Engine** | PB3 | คุมคันเร่งเครื่องยนต์ | ใช้ไลบรารี Servo (PWM) |
| | PB15 | รีเลย์สตาร์ท/ดับเครื่อง | ใช้ไลบรารี Servo (PWM) |
| **IMU** | PB6, PB7 | BNO055 (I2C1) | SCL (PB6), SDA (PB7) |
| **Serial** | PA9, PA10 | เชื่อมต่อกับ Raspberry Pi | UART1 (TX: PA9, RX: PA10) |
| **UI/Control** | PB14 | สวิตช์สลับโหมด | Input Pull-up |
| | PC14 | ไฟแสดงสถานะโหมด | Output (LED) |
| | PC13 | ไฟบนบอร์ด | Built-in LED |

---

## 🟢 ขาที่ยังว่าง (FREE PINS)

| ขา (Pin) | ฟังก์ชันที่รองรับ (Peripherals) | คำแนะนำในการใช้งาน |
| :--- | :--- | :--- |
| **PB8, PB9** | **I2C2** (SCL/SDA) | **แนะนำที่สุด** สำหรับติดเซนเซอร์ I2C เพิ่ม (เช่น จอ OLED, เซนเซอร์ระยะทาง) |
| **PA2, PA3** | UART2 (TX/RX), ADC | ใช้ต่อเซนเซอร์ที่ส่งข้อมูล Serial หรือ Analog |
| **PB0, PB1** | **ADC** (Analog In), PWM | เหมาะสำหรับเซนเซอร์ Analog เช่น วัดแรงดันแบตเตอรี่ |
| **PB10, PB11** | UART3, I2C2 | ขาสำรองสำหรับ Serial หรือ I2C |
| **PA6, PA7** | PWM, ADC | ใช้คุม Servo เพิ่มเติม หรืออ่านค่า Analog |
| **PB12, PB13** | SPI2, UART3 | ใช้ต่อโมดูลที่ใช้ SPI เช่น NRF24L01 หรือ SD Card |

---

## ⚠️ ข้อควรระวัง
1. **PA11, PA12**: ถ้ามีการใช้พอร์ต USB บนบอร์ด Bluepill สองขานี้จะถูกจอง (D-/D+) แนะนำให้ใช้เป็นทางเลือกสุดท้าย
2. **PB2 (BOOT1)**: ขานี้มักจะถูกต่อลง Ground หรือดึงขึ้นผ่าน Jumper ไม่แนะนำให้ใช้เป็น IO ทั่วไป
3. **5V Tolerance**: ขาส่วนใหญ่ของ Bluepill รับ 5V ได้ แต่ **PA0-PA7 ไม่ได้รับ 5V (3.3V Only)** โปรดระวังเวลาต่อเซนเซอร์ 5V เข้าขา Analog
