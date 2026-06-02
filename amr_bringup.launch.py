import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    # Mendapatkan direktori share dari masing-masing package
    ydlidar_pkg_dir = get_package_share_directory('ydlidar_ros2_driver')
    merger_pkg_dir = get_package_share_directory('ros2_laser_scan_merger')

    # Path ke file parameter default YDLidar jika dibutuhkan (untuk baudrate, sample rate, dll)
    ydlidar_params = os.path.join(ydlidar_pkg_dir, 'params', 'ydlidar.yaml')

    # 1. Node Lidar Depan (Front Lidar)
    front_lidar_node = Node(
        package='ydlidar_ros2_driver',
        executable='ydlidar_ros2_driver_node',
        name='ydlidar_front',
        parameters=[
            ydlidar_params,
            {
                'port': '/dev/ttyUSB1',
                'frame_id': 'laser_front_right',
            }
        ],
        # Sinkronisasi topik ke /front_scan sesuai params.yaml merger
        remappings=[
            ('scan', '/front_scan')
        ],
        output='screen'
    )

    # 2. Node Lidar Belakang (Rear Lidar)
    rear_lidar_node = Node(
        package='ydlidar_ros2_driver',
        executable='ydlidar_ros2_driver_node',
        name='ydlidar_rear',
        parameters=[
            ydlidar_params,
            {
                'port': '/dev/ttyUSB2',
                'frame_id': 'laser_rear_left',
            }
        ],
        # Sinkronisasi topik ke /rear_scan sesuai params.yaml merger
        remappings=[
            ('scan', '/rear_scan')
        ],
        output='screen'
    )

    # 3. Memanggil file launch merger bawaan
    # File ini otomatis menjalankan ros2_laser_scan_merger dan pointcloud_to_laserscan menggunakan params.yaml Anda
    merger_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(merger_pkg_dir, 'launch', 'merge_2_scan.launch.py')
        )
    )

    return LaunchDescription([
        front_lidar_node,
        rear_lidar_node,
        merger_launch
    ])