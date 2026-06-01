#include <Arduino.h>
#include <micro_ros_platformio.h>
#include <rcl/rcl.h>
#include <rcl/error_handling.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>

// Pesan ROS 2
#include <geometry_msgs/msg/twist.h>
#include <std_msgs/msg/float32_multi_array.h>
#include <sensor_msgs/msg/imu.h>

// Library Eksternal
#include <ModbusMaster.h>
#include "imu_sensor.h"

// --- KONFIGURASI HARDWARE MOTOR (ZLAC) ---
#define MODBUS_SERIAL Serial1 
#define SLAVE_ADDR 1
ModbusMaster driver;

const uint16_t OPR_MODE_REG = 0x200D;
const uint16_t CTRL_REG     = 0x200E;
const uint16_t CMD_RPM_REG  = 0x2088;
const uint16_t FB_POS_REG   = 0x20A7; 

// --- VARIABEL ROS 2 ---
rcl_subscription_t sub_cmd_vel;
rcl_publisher_t pub_encoder;
rcl_publisher_t pub_imu;      // Publisher untuk IMU

geometry_msgs__msg__Twist msg_cmd_vel;
std_msgs__msg__Float32MultiArray msg_encoder;
sensor_msgs__msg__Imu msg_imu; // Wadah data IMU
float encoder_data_array[2]; 

rclc_executor_t executor;
rclc_support_t support;
rcl_allocator_t allocator;
rcl_node_t node;

#define RCCHECK(fn) { rcl_ret_t temp_rc = fn; if((temp_rc != RCL_RET_OK)){error_loop();}}
#define RCSOFTCHECK(fn) { rcl_ret_t temp_rc = fn; if((temp_rc != RCL_RET_OK)){}}

// --- STATE KENDALI & WAKTU ---
int16_t target_left_cmd = 0;
int16_t target_right_cmd = 0;

unsigned long last_imu_publish = 0;
unsigned long last_modbus_write = 0;
unsigned long last_modbus_read = 0;

// ==========================================
// ERROR LOOP
// ==========================================
void error_loop() {
  while(1) {
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
    delay(500);
  }
}

// ==========================================
// CALLBACK: PERINTAH WASD (CMD_VEL)
// ==========================================
void twist_callback(const void * msgin) {
  const geometry_msgs__msg__Twist * twist_msg = (const geometry_msgs__msg__Twist *)msgin;
  
  float linear_x = twist_msg->linear.x;
  float angular_z = twist_msg->angular.z;

  float linear_to_rpm = 9.4;   
  float angular_to_rpm = 7.0;  
  float max_safe_rpm = 25.0; 

  float left_rpm  = (linear_x * linear_to_rpm) - (angular_z * angular_to_rpm);
  float right_rpm = (linear_x * linear_to_rpm) + (angular_z * angular_to_rpm);

  left_rpm = constrain(left_rpm, -max_safe_rpm, max_safe_rpm);
  right_rpm = constrain(right_rpm, -max_safe_rpm, max_safe_rpm);

  target_left_cmd = (int16_t)(left_rpm * 10);
  target_right_cmd = (int16_t)(-right_rpm * 10); 
}

// ==========================================
// SETUP
// ==========================================
void setup() {
  // 1. Jeda santai untuk colok USB dan buka terminal
  delay(5000); 

  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);

  // 2. Inisialisasi IMU BNO08x (I2C)
  imu_init();

  // 3. Binding micro-ROS
  set_microros_serial_transports(Serial);
  
  // 4. Ping agen ke PC (Cari Koneksi)
  while (rmw_uros_ping_agent(1000, 1) != RMW_RET_OK) {
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
    delay(100);
  }
  digitalWrite(LED_BUILTIN, LOW); 
  
  // 5. Inisialisasi ROS 2 Core
  allocator = rcl_get_default_allocator();
  RCCHECK(rclc_support_init(&support, 0, NULL, &allocator));
  RCCHECK(rclc_node_init_default(&node, "teensy_amr_core", "", &support));
  
  // 6. Inisialisasi Topik ROS 2
  RCCHECK(rclc_subscription_init_default(
    &sub_cmd_vel, &node, ROSIDL_GET_MSG_TYPE_SUPPORT(geometry_msgs, msg, Twist), "/cmd_vel"));
    
  RCCHECK(rclc_publisher_init_default(
    &pub_encoder, &node, ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Float32MultiArray), "/wheel_travel"));

  RCCHECK(rclc_publisher_init_default(
    &pub_imu, &node, ROSIDL_GET_MSG_TYPE_SUPPORT(sensor_msgs, msg, Imu), "/imu/data"));

  msg_encoder.data.capacity = 2;
  msg_encoder.data.size = 2;
  msg_encoder.data.data = encoder_data_array;
    
  // Executor (Handle = 1 karena hanya ada 1 subscriber cmd_vel)
  RCCHECK(rclc_executor_init(&executor, &support.context, 1, &allocator));
  RCCHECK(rclc_executor_add_subscription(&executor, &sub_cmd_vel, &msg_cmd_vel, &twist_callback, ON_NEW_DATA));

  // 7. Inisialisasi Modbus Motor
  MODBUS_SERIAL.begin(115200);
  driver.begin(SLAVE_ADDR, MODBUS_SERIAL);
  
  driver.writeSingleRegister(OPR_MODE_REG, 3); 
  delay(50);
  driver.writeSingleRegister(CTRL_REG, 8);     
  
  // Sukses Semua
  digitalWrite(LED_BUILTIN, HIGH); 
}

// ==========================================
// LOOP (PENJADWALAN PARALEL TUGAS)
// ==========================================
void loop() {
  // Mengecek apakah ada perintah WASD masuk
  rclc_executor_spin_some(&executor, RCL_MS_TO_NS(2)); 
  
  unsigned long now = millis();

  // --- TUGAS 1: BACA & PUBLISH IMU (Tiap 20ms / 50Hz) ---
  if (now - last_imu_publish >= 20) {
    imu_read_data(&msg_imu);
    rcl_publish(&pub_imu, &msg_imu, NULL);
    last_imu_publish = now;
  }

  // --- TUGAS 2: KIRIM PERINTAH KE MOTOR (Tiap 100ms) ---
  if (now - last_modbus_write >= 100) {
    driver.setTransmitBuffer(0, target_left_cmd);
    driver.setTransmitBuffer(1, target_right_cmd);
    driver.writeMultipleRegisters(CMD_RPM_REG, 2);
    last_modbus_write = now;
  }
  
  // --- TUGAS 3: BACA & PUBLISH ENCODER (Tiap 100ms, Offset 50ms dari Tugas 2) ---
  else if (now - last_modbus_read >= 100 && (now - last_modbus_write) > 50) {
    uint8_t result = driver.readHoldingRegisters(FB_POS_REG, 4);
    
    if (result == driver.ku8MBSuccess) {
      uint16_t l_hi = driver.getResponseBuffer(0);
      uint16_t l_lo = driver.getResponseBuffer(1);
      uint16_t r_hi = driver.getResponseBuffer(2);
      uint16_t r_lo = driver.getResponseBuffer(3);

      int32_t l_pulse = (int32_t)(((uint32_t)l_hi << 16) | (uint32_t)l_lo);
      int32_t r_pulse = (int32_t)(((uint32_t)r_hi << 16) | (uint32_t)r_lo);

      float l_travel = ((float)l_pulse / 16385.0) * 1.6558 ;
      float r_travel = ((float)r_pulse / 16385.0) * 1.6558;

      msg_encoder.data.data[0] = l_travel;
      msg_encoder.data.data[1] = -r_travel; 

      rcl_publish(&pub_encoder, &msg_encoder, NULL);
    }
    last_modbus_read = now;
  }
}