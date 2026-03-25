# This document to help run command 

## Run Gazebo 

```
cd ~/AMR_ws 
colcon build 
source install/setup.bash
ros2 launch amr_robot gazebo.launch.py

```


## Run PId and DOB 
```
cd ~/AMR_ws 
colcon build 
source install/setup.bash
ros2 run amr_robot pid_dob_controller.py
```
## Run Linear Velocity 
```
source install/setup.bash
ros2 topic pub -r 10 /cmd_vel_target geometry_msgs/msg/Twist "{linear: {x: 0.3, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"

```

## to stop 
```

ros2 topic pub --once /cmd_vel_target geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```
## Run Plot Juggler 
```
ros2 run plotjuggler plotjuggler
```
