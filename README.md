

# URDF FILE DESIGN ROBOT FROM SOLIDWORKS 2024
## So what inside this folder : 
1. urdf file
2. STL file 

## First you must set up by using and set up the ROS 2 workspace 



## Set up enviroment 
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc

## Run Rviz 
cd ~/Documents/urdf_file/urdf
ros2 launch amr_launch.py

## easiest way to Run 
ros2 launch /home/rein/Documents/urdf_file/urdf/amr_launch.py



## The important thing is you can see the urdf in folder urdf_file/urdf and you must run actually by using amr_launch.py with syntax 
**ros2 launch amr launch.py**



## Important message for the future development if you want to use your robot design and make it into urdf 
1. Pay attention to
_<mesh
          filename="file:///home/rein/Documents/urdf_file/meshes/base_link.stl"/>_
cause this filename .stl sometimes didn't read in rviz as .stl cause Solidworks maybe have different of sensitive case


## important installer 
1. I am using Solidworks 2024 but urdf exporter for 2021 still works you can install on 
https://github.com/ros/solidworks_urdf_exporter/releases

2. I am also using rviz
sudo apt install ros-humble-joint-state-publisher-gui -y
sudo apt install ros-humble-robot-state-publisher -y
sudo apt install ros-humble-rviz2 -y


## Must define 
1. in Solidworks you should define for the motion such as wheel to have coordinate and axis reference and like base is only coordinate just okay
2. Also you need to define the front and the back and must be consistent to define the direction.
3. After we open the Rviz we must to define 
4. must set up the ROS2 Workspace first to run the Rviz
5. Set up the global option ( fixed frame into your base link. stl ) add robot model then scroll down search for description topic change into robot_description 


<img width="1842" height="998" alt="image" src="https://github.com/user-attachments/assets/db8c7916-37db-4c3c-93a0-5a8825210f63" /># Autonomous-Mobile-Robot
