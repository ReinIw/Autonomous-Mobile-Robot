# Setup Gazebo 

## Install Gazebo 
sudo apt install gazebo
sudo apt install ros-humble-gazebo-ros-pkgs -y
sudo apt install ros-humble-gazebo-ros2-control -y
sudo apt install ros-humble-diff-drive-controller -y
sudo apt install ros-humble-joint-state-broadcaster -y

sudo apt install ros-humble-nav2-bringup -y
sudo apt install ros-humble-slam-toolbox -y

## if you found failed fetched while installation use this command 
sudo apt update --fix-missing
sudo apt upgrade -y

## to recheck if all installed well 
echo "=== GAZEBO ===" && gazebo --version && \
echo "=== DIFF DRIVE ===" && ros2 pkg list | grep diff && \
echo "=== JOINT STATE ===" && ros2 pkg list | grep joint_state && \
echo "=== NAV2 ===" && ros2 pkg list | grep nav2 | head -5 && \
echo "=== SLAM ===" && ros2 pkg list | grep slam

## Install Teleop Keyboard 
sudo apt install ros-humble-teleop-twist-keyboard -y

## Add plugin you can add before </robot> just search in urdf files 
<gazebo>
  <plugin name="differential_drive_controller" 
          filename="libgazebo_ros_diff_drive.so">
    <ros>
      <namespace>/</namespace>
    </ros>
    <left_joint>left_wheel_joint</left_joint>
    <right_joint>right_wheel_joint</right_joint>
    <wheel_separation>0.45</wheel_separation>
    <wheel_diameter>0.123</wheel_diameter>
    <max_wheel_torque>20</max_wheel_torque>
    <max_wheel_acceleration>1.0</max_wheel_acceleration>
    <publish_odom>true</publish_odom>
    <publish_odom_tf>true</publish_odom_tf>
    <publish_wheel_tf>true</publish_wheel_tf>
    <odometry_frame>odom</odometry_frame>
    <robot_base_frame>base_footprint</robot_base_frame>
  </plugin>
</gazebo>


<gazebo>
  <plugin name="gazebo_ros_joint_state_publisher"
          filename="libgazebo_ros_joint_state_publisher.so">
    <ros>
      <namespace>/</namespace>
    </ros>
    <joint_name>left_wheel_joint</joint_name>
    <joint_name>right_wheel_joint</joint_name>
  </plugin>
</gazebo>


<gazebo reference="lidar1_link">
  <sensor type="ray" name="lidar1">
    <pose>0 0 0 0 0 0</pose>
    <visualize>true</visualize>
    <update_rate>10</update_rate>
    <ray>
      <scan>
        <horizontal>
          <samples>360</samples>
          <resolution>1</resolution>
          <min_angle>-3.14159</min_angle>
          <max_angle>3.14159</max_angle>
        </horizontal>
      </scan>
      <range>
        <min>0.1</min>
        <max>10.0</max>
        <resolution>0.01</resolution>
      </range>
    </ray>
    <plugin name="lidar1_controller"
            filename="libgazebo_ros_ray_sensor.so">
      <ros>
        <remapping>~/out:=scan1</remapping>
      </ros>
      <output_type>sensor_msgs/LaserScan</output_type>
    </plugin>
  </sensor>
</gazebo>

<gazebo reference="lidar2_link">
  <sensor type="ray" name="lidar2">
    <pose>0 0 0 0 0 0</pose>
    <visualize>true</visualize>
    <update_rate>10</update_rate>
    <ray>
      <scan>
        <horizontal>
          <samples>360</samples>
          <resolution>1</resolution>
          <min_angle>-3.14159</min_angle>
          <max_angle>3.14159</max_angle>
        </horizontal>
      </scan>
      <range>
        <min>0.1</min>
        <max>10.0</max>
        <resolution>0.01</resolution>
      </range>
    </ray>
    <plugin name="lidar2_controller"
            filename="libgazebo_ros_ray_sensor.so">
      <ros>
        <remapping>~/out:=scan2</remapping>
      </ros>
      <output_type>sensor_msgs/LaserScan</output_type>
    </plugin>
  </sensor>
</gazebo>


