# Step using Gazebo

## First to start gazebo-ing you need to make workspace first 


### make folder you can cd first and then make the folder to define where the folder is make 
mkdir -p ~/AMR_ws/src

### you can copy from urdf file that you make before into this workspace 
cp -r ~/Documents/urdf_file ~/AMR_ws/src/amr_robot

### access this folder after you make 
cd ~/AMR_ws

### start compile 
colcon build

### ATTENTION : YOU MAY SEE ERROR THIS CAUSE BY C MAKE FILES IN URDF FILE BEFORE CAUSE THIS IS ROS 1 VERSION YOU NEED TO CHANGE TO ROS 2 by using this 2 step 
cat > ~/AMR_ws/src/amr_robot/CMakeLists.txt << 'EOF'
cmake_minimum_required(VERSION 3.8)
project(amr_robot)

find_package(ament_cmake REQUIRED)

install(DIRECTORY urdf meshes launch config
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
EOF

cat > ~/AMR_ws/src/amr_robot/package.xml << 'EOF'
<?xml version="1.0"?>
<package format="3">
  <name>amr_robot</name>
  <version>0.0.1</version>
  <description>AMR Robot URDF Package</description>
  <maintainer email="rein@email.com">rein</maintainer>
  <license>MIT</license>

  <buildtool_depend>ament_cmake</buildtool_depend>
  <exec_depend>robot_state_publisher</exec_depend>
  <exec_depend>joint_state_publisher_gui</exec_depend>
  <exec_depend>rviz2</exec_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
EOF


### Retry to build the package 
cd ~/AMR_ws
colcon build
source install/setup.bash



### Make Launch file for robot display Rviz
cat > ~/AMR_ws/src/amr_robot/launch/display.launch.py << 'EOF'
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg = get_package_share_directory('amr_robot')
    urdf_file = os.path.join(pkg, 'urdf', 'Assembly_Autonomous Mobile Robot v2.urdf')
    with open(urdf_file, 'r') as f:
        robot_desc = f.read()
    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_desc}]
        ),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
        ),
        Node(
            package='rviz2',
            executable='rviz2',
        )
    ])
EOF


### Try to Run
cd ~/AMR_ws
ros2 launch amr_robot display.launch.py
