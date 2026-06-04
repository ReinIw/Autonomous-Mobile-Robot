import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node

def generate_launch_description():
    # Mendapatkan path absolut ke folder kerjamu
    base_path = os.path.expanduser('~/amr_control')
    ekf_config_path = os.path.join(base_path, 'ekf.yaml')
    
    return LaunchDescription([
        # 1. Menyalakan Jembatan Teensy (Micro-ROS Agent)
        ExecuteProcess(
            cmd=['ros2', 'run', 'micro_ros_agent', 'micro_ros_agent', 'serial', '--dev', '/dev/ttyACM0', '-b', '115200'],
            output='screen'
        ),
        
        # 2. Menyalakan Kalkulator Odom Roda
        ExecuteProcess(
            cmd=['python3', os.path.join(base_path, 'odom_node.py')],
            output='screen'
        ),

        ExecuteProcess(
            cmd=['python3', os.path.join(base_path, 'velocityinvert.py')],
            output='screen'
        ),

        # 3. Menyalakan Penambal IMU (Paspor VIP EKF)
        ExecuteProcess(
            cmd=['python3', os.path.join(base_path, 'imu_fixer.py')],
            output='screen'
        ),
        
        
        # 4. Koreksi Fisik IMU (Ingat: Pitch 180 derajat / 3.14159 karena sensor tengkurap!)
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='imu_static_tf',
            arguments=[
                '--x', '0', '--y', '0', '--z', '0', 
                '--roll', '0', '--pitch', '0', '--yaw', '0', 
                '--frame-id', 'base_link', '--child-frame-id', 'imu_link'
            ]
        ),
        # 5. Menghidupkan Sang Hakim EKF
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node', 
            parameters=[ekf_config_path],
            output='screen'
        )

        
    ])