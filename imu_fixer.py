import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu

class ImuFixerNode(Node):
    def __init__(self):
        super().__init__('imu_fixer_node')
        
        # 1. Mencegat (Subscribe) data mentah dari Teensy
        self.subscription = self.create_subscription(
            Imu,
            '/imu/data',
            self.imu_callback,
            10)
        
        # 2. Membuat jalur baru yang legal untuk disuapkan ke EKF
        self.publisher = self.create_publisher(Imu, '/imu/data_fixed', 10)
    def imu_callback(self, msg):
        # A. Tambahkan cap waktu PC Ubuntu saat ini (Syarat EKF 1)
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'imu_link'
        

        # B. Matriks Covariance / Error (Syarat EKF 2)
        cov_matrix = [
            0.001, 0.0,   0.0,
            0.0,   0.001, 0.0,
            0.0,   0.0,   0.001
        ]
        
        # C. Tempelkan matriks ke dalam pesan
        msg.orientation_covariance = cov_matrix
        msg.angular_velocity_covariance = cov_matrix
        msg.linear_acceleration_covariance = cov_matrix
        
        # D. Publikasikan ulang ke topik yang baru!
        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = ImuFixerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

