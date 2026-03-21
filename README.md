# Dictionary of ROS 2 node 

## Robot_state_publisher : to open urdf Files 
Node(
    package='robot_state_publisher',
    executable='robot_state_publisher',
    parameters=[{'robot_description': robot_desc}]
)


## joint_state_publisher_gui : moving the joint robot by using slider 
Node(
    package='joint_state_publisher_gui',
    executable='joint_state_publisher_gui',
),


## RVIz2 : to visualize the 3d of the Robot 
Node(
    package='rviz2',
    executable='rviz2',
)
