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

