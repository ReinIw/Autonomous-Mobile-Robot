#include "imu_sensor.h"
#include <Wire.h>
#include <Adafruit_BNO08x.h>

// Objek sensor BNO08x
Adafruit_BNO08x bno08x;
sh2_SensorValue_t sensorValue;

void imu_init() {
  Wire.begin();
  pinMode(13, OUTPUT); // LED indikator Teensy
  
  // Mencoba inisialisasi BNO08x via I2C
  while (!bno08x.begin_I2C(0x4B)) {
    // Jika gagal, LED berkedip cepat
    digitalWrite(13, HIGH);
    delay(100);
    digitalWrite(13, LOW);
    delay(100);
  }
  
  // Jika sukses terdeteksi, LED akan menyala solid
  digitalWrite(13, HIGH);

  // --- MENGAKTIFKAN REPORT DATA (50Hz = 20000 microsecond) ---
  // SLAM membutuhkan Quaternion (Rotation Vector), Gyro, dan Linear Accel
  bno08x.enableReport(SH2_GAME_ROTATION_VECTOR, 20000); 
  bno08x.enableReport(SH2_GYROSCOPE_CALIBRATED, 20000); 
  bno08x.enableReport(SH2_LINEAR_ACCELERATION, 20000); 
}

void imu_read_data(sensor_msgs__msg__Imu *msg) {
  // Set Frame ID untuk integrasi TF Tree ROS 2
  msg->header.frame_id.data = (char *)"imu_link";
  msg->header.frame_id.size = strlen(msg->header.frame_id.data);
  msg->header.frame_id.capacity = msg->header.frame_id.size + 1;

  // Jika sensor mengalami reset (misal karena lonjakan arus), aktifkan ulang reportnya
  if (bno08x.wasReset()) {
    bno08x.enableReport(SH2_GAME_ROTATION_VECTOR, 20000);
    bno08x.enableReport(SH2_GYROSCOPE_CALIBRATED, 20000);
    bno08x.enableReport(SH2_LINEAR_ACCELERATION, 20000);
  }

  // BNO08x menumpuk data di buffer. Kita loop hingga data paling mutakhir.
  while (bno08x.getSensorEvent(&sensorValue)) {
    switch (sensorValue.sensorId) {
      
      case SH2_GAME_ROTATION_VECTOR:
        msg->orientation.x = sensorValue.un.gameRotationVector.i;
        msg->orientation.y = sensorValue.un.gameRotationVector.j;
        msg->orientation.z = sensorValue.un.gameRotationVector.k;
        msg->orientation.w = sensorValue.un.gameRotationVector.real;
        break;
        
      case SH2_GYROSCOPE_CALIBRATED:
        msg->angular_velocity.x = sensorValue.un.gyroscope.x;
        msg->angular_velocity.y = sensorValue.un.gyroscope.y;
        msg->angular_velocity.z = sensorValue.un.gyroscope.z;
        break;
        
      case SH2_LINEAR_ACCELERATION:
        msg->linear_acceleration.x = sensorValue.un.linearAcceleration.x;
        msg->linear_acceleration.y = sensorValue.un.linearAcceleration.y;
        msg->linear_acceleration.z = sensorValue.un.linearAcceleration.z;
        break;
    }
  }
}
