# Autonomous-Mobile-Robot for EKF ( Encoder and IMU FUSION ) 

### amr_launch.py
to start the teensy reminder you will see the established system notification if you are didnt get just plug and unplug the teensy 


### imu_fixer.py 
to make the imu can be inputted to the ekf.yaml 


### ekf.yaml 
to get the fusion process between ecnoder and Imu 

### cmd.inverter 
_notes if you want to go nav2 use this node to access rpm CAUSE THE ZLAC8015D GOT INVERTED WHEN TURN RIGHT OR LEFT_
to invert the right and left turn between left and right wheel 


### safe_teleop.py 
to run the wasd control from your keyboard 

### odom_node.py 
to calculate the odometri so that the encoder result can be input to the EKF.yaml 

### ct.py 
if you want tested just to move robot using rs/ttl - ttl/usb you can use this !!!


##
