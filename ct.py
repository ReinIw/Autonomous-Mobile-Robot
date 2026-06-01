#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32MultiArray
import time
import numpy as np
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

# ==========================================================
# 1. CLASS DRIVER ZLAC8015D (Definisi Register & Modbus)
# ==========================================================
class ZlacDriver:
    def __init__(self, port="/dev/ttyUSB0"):
        self._port = port
        self.client = ModbusClient(method='rtu', port=self._port, baudrate=115200, timeout=0.1)
        self.client.connect()
        self.ID = 1

        # Register Address
        self.CONTROL_REG = 0x200E
        self.OPR_MODE = 0x200D
        self.L_CMD_RPM = 0x2088
        self.R_CMD_RPM = 0x2089
        self.L_FB_POS_HI = 0x20A7
        self.L_FB_POS_LO = 0x20A8
        self.R_FB_POS_HI = 0x20A9
        self.R_FB_POS_LO = 0x20AA

        # Control CMDs
        self.DOWN_TIME = 0x07
        self.ENABLE = 0x08

        # Odometry (Roda 8 inch)
        self.travel_in_one_rev = 0.655
        self.cpr = 16385
        self.R_Wheel = 0.105 # meter

    def modbus_fail_read_handler(self, ADDR, WORD):
        read_success = False
        reg = [None]*WORD
        retry_count = 0
        while not read_success and retry_count < 3:
            result = self.client.read_holding_registers(ADDR, WORD, unit=self.ID)
            try:
                for i in range(WORD):
                    reg[i] = result.registers[i]
                read_success = True
            except AttributeError:
                retry_count += 1
                time.sleep(0.01)
        return reg if read_success else [0]*WORD

    def set_mode(self, MODE):
        self.client.write_register(self.OPR_MODE, MODE, unit=self.ID)

    def enable_motor(self):
        self.client.write_register(self.CONTROL_REG, self.ENABLE, unit=self.ID)

    def disable_motor(self):
        self.client.write_register(self.CONTROL_REG, self.DOWN_TIME, unit=self.ID)

    def int16Dec_to_int16Hex(self, int16):
        lo_byte = (int16 & 0x00FF)
        hi_byte = (int16 & 0xFF00) >> 8
        return (hi_byte << 8) | lo_byte

    def set_rpm(self, L_rpm, R_rpm):
        # Constrain RPM
        L_rpm = max(-3000, min(L_rpm, 3000))
        R_rpm = max(-3000, min(R_rpm, 3000))

        # ZLAC menerima format RPM x 10
        left_bytes = self.int16Dec_to_int16Hex(int(L_rpm * 10))
        right_bytes = self.int16Dec_to_int16Hex(int(R_rpm * 10))

        self.client.write_registers(self.L_CMD_RPM, [left_bytes, right_bytes], unit=self.ID)

    def get_wheels_travelled(self):
        registers = self.modbus_fail_read_handler(self.L_FB_POS_HI, 4)
        if not registers or None in registers:
            return 0.0, 0.0
            
        l_pul_hi = registers[0]
        l_pul_lo = registers[1]
        r_pul_hi = registers[2]
        r_pul_lo = registers[3]

        l_pulse = np.int32(((l_pul_hi & 0xFFFF) << 16) | (l_pul_lo & 0xFFFF))
        r_pulse = np.int32(((r_pul_hi & 0xFFFF) << 16) | (r_pul_lo & 0xFFFF))
        
        l_travelled = (float(l_pulse)/self.cpr) * self.travel_in_one_rev 
        r_travelled = (float(r_pulse)/self.cpr) * self.travel_in_one_rev 

        return l_travelled, r_travelled

# ==========================================================
# 2. ROS 2 NODE (Menerima Perintah & Membaca Encoder)
# ==========================================================
class AmrBaseNode(Node):
    def __init__(self):
        super().__init__('amr_base_node')
        
        self.port = '/dev/ttyUSB0' 
        
        # 1. Inisialisasi Hardware
        try:
            self.motors = ZlacDriver(port=self.port)
            self.motors.disable_motor()
            time.sleep(0.5)
            self.motors.set_mode(3) # Mode Velocity
            self.motors.enable_motor()
            self.get_logger().info(f"[OK] ZLAC8015D Terhubung di {self.port}")
        except Exception as e:
            self.get_logger().error(f"[FATAL] Gagal terhubung ke ZLAC: {e}")
            raise SystemExit

        # 2. Parameter Kinematika
        self.linear_to_rpm = 9.4
        self.angular_to_rpm = 7.0
        self.max_safe_rpm = 25.0
        
        self.target_left_rpm = 0.0
        self.target_right_rpm = 0.0
        self.last_cmd_time = time.time()

        # 3. Setup ROS 2 Subs/Pubs & Timer
        self.sub_cmd_vel = self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_cb, 10)
        self.pub_wheel_travel = self.create_publisher(Float32MultiArray, '/wheel_travel', 10)
        self.timer = self.create_timer(0.05, self.control_loop) # Loop 20Hz
        
        self.get_logger().info("🔥 AMR Base Node Aktif: Mengontrol Motor & Membaca Encoder!")

    def cmd_vel_cb(self, msg):
        left_rpm = (msg.linear.x * self.linear_to_rpm) - (msg.angular.z * self.angular_to_rpm)
        right_rpm = (msg.linear.x * self.linear_to_rpm) + (msg.angular.z * self.angular_to_rpm)
        
        self.target_left_rpm = max(-self.max_safe_rpm, min(left_rpm, self.max_safe_rpm))
        self.target_right_rpm = max(-self.max_safe_rpm, min(right_rpm, self.max_safe_rpm))
        self.last_cmd_time = time.time()

    def control_loop(self):
        # 1. Dead-Man's Switch
        if time.time() - self.last_cmd_time > 0.5:
            self.target_left_rpm = 0.0
            self.target_right_rpm = 0.0

        # 2. Kirim RPM (Roda kanan dibalik agar geraknya searah)
        try:
            self.motors.set_rpm(self.target_left_rpm, -self.target_right_rpm)
        except Exception as e:
            self.get_logger().warn(f"Gagal mengirim RPM: {e}")

        # 3. Baca Encoder & Publish Jarak
        try:
            l_travel, r_travel = self.motors.get_wheels_travelled()
            r_travel = -r_travel # Balikkan nilai jarak roda kanan
            
            msg = Float32MultiArray()
            msg.data = [float(l_travel), float(r_travel)]
            self.pub_wheel_travel.publish(msg)
        except Exception as e:
            self.get_logger().warn(f"Gagal membaca encoder: {e}")

    def shutdown_hook(self):
        self.get_logger().info("Mematikan motor...")
        try:
            self.motors.set_rpm(0, 0)
            time.sleep(0.1)
            self.motors.disable_motor()
        except:
            pass

def main(args=None):
    rclpy.init(args=args)
    node = AmrBaseNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.shutdown_hook()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()