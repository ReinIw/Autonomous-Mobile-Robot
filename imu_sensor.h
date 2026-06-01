#ifndef IMU_SENSOR_H
#define IMU_SENSOR_H

#include <Arduino.h>
#include <sensor_msgs/msg/imu.h>

// Deklarasi fungsi
void imu_init();
void imu_read_data(sensor_msgs__msg__Imu *msg);

#endif