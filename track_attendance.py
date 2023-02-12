from Kalman import KalmanAngle
import smbus			#import SMBus module of I2C
import time
import math
import threading
import firebase_admin
from firebase_admin import db

#some MPU6050 Registers and their Address
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47
DeviceAddress = 0x68   # MPU6050 device address

cred_obj = firebase_admin.credentials.Certificate('attendancetracker-5e615-firebase-adminsdk-gk4m6-ffc1325573.json')
default_app = firebase_admin.initialize_app(cred_obj, {
	'databaseURL':'https://attendancetracker-5e615-default-rtdb.europe-west1.firebasedatabase.app'
	})

db = db.reference("/places")

db_places = db.get()

class Sensor_angles_measure(threading.Thread):
	def __init__(self, id):
		super(Sensor_angles_measure, self).__init__()
		self.id = id #id of the bus
		self.key = [i for i in db_places if db_places[i]['idPlace']==id][0] #key of the database record associated to the bus
  
	def run(self):
		kalmanX = KalmanAngle()
		kalmanY = KalmanAngle()

		RestrictPitch = False	#Comment out to restrict roll to ±90deg instead - please read: http://www.freescale.com/files/sensors/doc/app_note/AN3461.pdf
		radToDeg = 57.2957786
		kalAngleX = 0
		kalAngleY = 0

		bus = smbus.SMBus(self.id) # possible values are 1, 3 or 4 (corresponding the bus IDs)
		MPU_Init(bus)
		time.sleep(1)

		#Read Accelerometer raw value
		accX = read_raw_data(ACCEL_XOUT_H, bus)
		accY = read_raw_data(ACCEL_YOUT_H, bus)
		accZ = read_raw_data(ACCEL_ZOUT_H, bus)

		if (RestrictPitch):
			roll = math.atan2(accY,accZ) * radToDeg
			pitch = math.atan(-accX/math.sqrt((accY**2)+(accZ**2))) * radToDeg
		else:
			roll = math.atan(accY/math.sqrt((accX**2)+(accZ**2))) * radToDeg
			pitch = math.atan2(-accX,accZ) * radToDeg
		print(roll)
		kalmanX.setAngle(roll)
		kalmanY.setAngle(pitch)
		gyroXAngle = roll;
		gyroYAngle = pitch;
		compAngleX = roll;
		compAngleY = pitch;

		timer = time.time()
		flag = 0
		while True:
			if(flag >100): #Problem with the connection
				print("There is a problem with the connection")
				flag=0
				continue
			try:
				#Read Accelerometer raw value
				accX = read_raw_data(ACCEL_XOUT_H, bus)
				accY = read_raw_data(ACCEL_YOUT_H, bus)
				accZ = read_raw_data(ACCEL_ZOUT_H, bus)

				#Read Gyroscope raw value
				gyroX = read_raw_data(GYRO_XOUT_H, bus)
				gyroY = read_raw_data(GYRO_YOUT_H, bus)
				gyroZ = read_raw_data(GYRO_ZOUT_H, bus)

				dt = time.time() - timer
				timer = time.time()

				if (RestrictPitch):
					roll = math.atan2(accY,accZ) * radToDeg
					pitch = math.atan(-accX/math.sqrt((accY**2)+(accZ**2))) * radToDeg
				else:
					roll = math.atan(accY/math.sqrt((accX**2)+(accZ**2))) * radToDeg
					pitch = math.atan2(-accX,accZ) * radToDeg

				gyroXRate = gyroX/131
				gyroYRate = gyroY/131

				if (RestrictPitch):

					if((roll < -90 and kalAngleX >90) or (roll > 90 and kalAngleX < -90)):
						kalmanX.setAngle(roll)
						complAngleX = roll
						kalAngleX   = roll
						gyroXAngle  = roll
					else:
						kalAngleX = kalmanX.getAngle(roll,gyroXRate,dt)

					if(abs(kalAngleX)>90):
						gyroYRate  = -gyroYRate
						kalAngleY  = kalmanY.getAngle(pitch,gyroYRate,dt)
				else:

					if((pitch < -90 and kalAngleY >90) or (pitch > 90 and kalAngleY < -90)):
						kalmanY.setAngle(pitch)
						complAngleY = pitch
						kalAngleY   = pitch
						gyroYAngle  = pitch
					else:
						kalAngleY = kalmanY.getAngle(pitch,gyroYRate,dt)

					if(abs(kalAngleY)>90):
						gyroXRate  = -gyroXRate
						kalAngleX = kalmanX.getAngle(roll,gyroXRate,dt)

				#angle = (rate of change of angle) * change in time
				gyroXAngle = gyroXRate * dt
				gyroYAngle = gyroYAngle * dt

				#compAngle = constant * (old_compAngle + angle_obtained_from_gyro) + constant * angle_obtained from accelerometer
				compAngleX = 0.93 * (compAngleX + gyroXRate * dt) + 0.07 * roll
				compAngleY = 0.93 * (compAngleY + gyroYRate * dt) + 0.07 * pitch

				if ((gyroXAngle < -180) or (gyroXAngle > 180)):
					gyroXAngle = kalAngleX
				if ((gyroYAngle < -180) or (gyroYAngle > 180)):
					gyroYAngle = kalAngleY

				##### Sending data here #####
				if (kalAngleY < -150 or (kalAngleY >= 150 and kalAngleY <= 180)):
					print(f"Place {self.id} occupée")
					db.child(self.key).update({'estOccupee': True})
				else :
					print(f"Place {self.id} non occupée")
					db.child(self.key).update({'estOccupee': False})
				time.sleep(0.5)

			except Exception as exc:
				flag += 1

#Read the gyro and acceleromater values from MPU6050
def MPU_Init(bus):
	#write to sample rate register
	bus.write_byte_data(DeviceAddress, SMPLRT_DIV, 7)

	#Write to power management register
	bus.write_byte_data(DeviceAddress, PWR_MGMT_1, 1)

	#Write to Configuration register
	#Setting DLPF (last three bit of 0X1A to 6 i.e '110' It removes the noise due to vibration.) https://ulrichbuschbaum.wordpress.com/2015/01/18/using-the-mpu6050s-dlpf/
	bus.write_byte_data(DeviceAddress, CONFIG, int('0000110',2))

	#Write to Gyro configuration register
	bus.write_byte_data(DeviceAddress, GYRO_CONFIG, 24)

	#Write to interrupt enable register
	bus.write_byte_data(DeviceAddress, INT_ENABLE, 1)


def read_raw_data(addr, bus):
	#Accelero and Gyro value are 16-bit
		high = bus.read_byte_data(DeviceAddress, addr)
		low = bus.read_byte_data(DeviceAddress, addr+1)

		#concatenate higher and lower value
		value = ((high << 8) | low)

		#to get signed value from mpu6050
		if(value > 32768):
				value = value - 65536
		return value
	

if __name__ == '__main__':

	# create separate processes for each sensor measurements
	measuring_process1 = Sensor_angles_measure(1)
	measuring_process3 = Sensor_angles_measure(3)
	measuring_process4 = Sensor_angles_measure(4)

	measuring_process1.start()

	measuring_process3.start()

	measuring_process4.start()