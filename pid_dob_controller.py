#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

class PidDobController(Node):
    def __init__(self):
        super().__init__('pid_dob_controller')

        # 1. Konfigurasi Publisher & Subscriber
        # Subscribe ke perintah target (dari keyboard/joystick)
        self.sub_target = self.create_subscription(Twist, 'cmd_vel_target', self.target_cb, 10)
        # Subscribe ke sensor Odom (kecepatan aktual dari Gazebo)
        self.sub_odom = self.create_subscription(Odometry, 'odom', self.odom_cb, 10)
        # Publish ke roda Gazebo
        self.pub_cmd = self.create_publisher(Twist, 'cmd_vel', 10)

        # 2. Parameter Waktu & Kecepatan
        self.dt = 0.05 # Loop berjalan setiap 0.05 detik (20 Hz)
        self.timer = self.create_timer(self.dt, self.control_loop)
        self.v_max = 1.11 # Batas maksimum 4 km/jam (dalam m/s)

        # 3. Variabel Memori (State)
        self.v_ref = 0.0   # Kecepatan Target (Linear)
        self.w_ref = 0.0   # Kecepatan Target (Angular/Belok)
        self.v_act = 0.0   # Kecepatan Aktual
        self.w_act = 0.0

        # 4. Parameter PID
        self.kp = 1.5
        self.ki = 0.5
        self.kd = 0.1
        self.err_sum = 0.0
        self.err_prev = 0.0

        # 5. Parameter DOB (Disturbance Observer)
        self.tau_nom = 0.2     # Konstanta waktu nominal (respons robot saat kosong)
        self.v_act_prev = 0.0
        self.u_prev = 0.0      # Sinyal kontrol sebelumnya
        self.d_est_filt = 0.0  # Estimasi gangguan (payload) yang sudah difilter
        self.alpha = 0.1       # Koefisien Low-Pass Filter (0 - 1)

        self.get_logger().info("PID + DOB Controller Aktif! Max Speed: 4 km/jam")

    def target_cb(self, msg):
        # Membatasi kecepatan target agar tidak melebihi 4 km/jam
        self.v_ref = max(min(msg.linear.x, self.v_max), -self.v_max)
        self.w_ref = msg.angular.z

    def odom_cb(self, msg):
        # Membaca kecepatan asli dari Gazebo
        self.v_act = msg.twist.twist.linear.x
        self.w_act = msg.twist.twist.angular.z

    def control_loop(self):
        # Jika tidak ada perintah jalan, reset semua dan hentikan robot
        if self.v_ref == 0.0 and self.w_ref == 0.0:
            self.err_sum = 0.0
            self.d_est_filt = 0.0
            self.u_prev = 0.0
            self.pub_cmd.publish(Twist())
            return

        # ========================================================
        # A. ALGORITMA DISTURBANCE OBSERVER (DOB)
        # ========================================================
        # 1. Hitung percepatan asli
        v_dot = (self.v_act - self.v_act_prev) / self.dt
        self.v_act_prev = self.v_act

        # 2. Model Nominal (Inverse Plant): Berapa tenaga yang SEHARUSNYA dibutuhkan?
        u_nom = (self.tau_nom * v_dot) + self.v_act

        # 3. Hitung Gangguan (Tenaga yg Dikeluarkan - Tenaga Teoritis)
        d_est = self.u_prev - u_nom

        # 4. Saring nilai gangguan agar tidak loncat-loncat (Low-Pass Filter)
        self.d_est_filt = (1.0 - self.alpha) * self.d_est_filt + (self.alpha * d_est)

    
        # ========================================================
        # B. ALGORITMA PID CONTROLLER
        # ========================================================
        error = self.v_ref - self.v_act
        self.err_sum += error * self.dt
        err_dot = (error - self.err_prev) / self.dt
        self.err_prev = error

        u_pid = (self.kp * error) + (self.ki * self.err_sum) + (self.kd * err_dot)


        # ========================================================
        # C. TOTAL SINYAL KONTROL
        # ========================================================
        # Sinyal Target + Kompensasi PID + Kompensasi Beban (DOB)
        u_total = self.v_ref + u_pid + self.d_est_filt

        # Batasi output maksimal agar mesin Gazebo tidak meledak (Maks kompensasi 2x v_max)
        u_total = max(min(u_total, self.v_max * 2.0), -self.v_max * 2.0)
        self.u_prev = u_total

        # ========================================================
        # D. KIRIM PERINTAH KE RODA GAZEBO
        # ========================================================
        cmd = Twist()
        cmd.linear.x = float(u_total)
        
        # Untuk belok (angular), kita gunakan P-Controller sederhana
        err_w = self.w_ref - self.w_act
        cmd.angular.z = float(self.w_ref + (1.0 * err_w))
        
        self.pub_cmd.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = PidDobController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()