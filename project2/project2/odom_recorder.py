import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from nav_msgs.msg import Odometry
from std_msgs.msg import Empty
import math
import time


class OdomRecorder(Node): 
    def __init__(self):
        super().__init__('odom_recorder')

        #subscriber for joystick
        self.subscription = self.create_subscription(
            Joy,
            'joy',
            self.joystick_callback,
            10)
        self.subscription
        
        #subscriber for odometry
        self.subscription = self.create_subscription(Odometry, 'odom', self.odom_callback, 10)
        self.subscription
        
        #publisher to reset odometry
        self.pub_reset = self.create_publisher(Empty, '/commands/reset_odometry', 10)
        
        #timer to record odometry
        self.timer = self.create_timer(0.1, self.timer_callback)
        
        self.record = False
        self.prev_button_state = 0 #this variable is needed to tell how many times the joystick button was pressed
        
        #current orientation via odometry
        self.x_pos = 0.0
        self.y_pos = 0.0
        self.angular_pos = 0.0
        
        #keeping track of previously recorded coordinates to calculate distance
        self.x_pos_prev = 0.0
        self.y_pos_prev = 0.0

        #intialize storge for breadcrumbs -sharon
        self.breadcrumb_list = []
        self.record = False
        self.prev_button_state = 0 #this variable is needed to tell how many times the joystick button was pressed
        
    #start/stop recording odometry when "X" pressed on joystick
    def joystick_callback(self, msg):
        if msg.buttons[2] == 1 and self.prev_button_state == 0: 

            # idea code -sharon
            if not self.record:
                self.record = True
                self.pub_reset.publish(Empty())
                self.breadcrumb_list = [(0.0, 0.0)] #reset breadcrumb list
                
            time.sleep(2) #allow enough time for odom reset before recording
        
            self.record = not self.record
            self.prev_button_state = 1
            print(self.record)
            
            #stand in for writing current odometry to file
            self.x_pos = 0.0
            self.y_pos = 0.0
            self.x_pos_prev = 0.0
            self.y_pos_prev = 0.0
            print("-> ", self.x_pos, ", ", self.y_pos)
            
            
        elif msg.buttons[2] == 0:
            self.prev_button_state = 0
            
    def odom_callback(self, msg):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        z = msg.pose.pose.orientation.z
        w = msg.pose.pose.orientation.w
        siny_cosp = 2 * w * z
        cosy_cosp = 1 - 2 * z * z
        yaw = math.atan2(siny_cosp, cosy_cosp)
        degree = yaw * 180 / math.pi
        #print ('x: %f y: %f Orientation: %f' % (x, y, degree))
        self.x_pos = x
        self.y_pos = y
        self.angular_pos = degree
            
    def timer_callback(self):
        #distance from last recorded position to current position
        dist = math.sqrt((self.y_pos_prev - self.y_pos)**2 + (self.x_pos_prev - self.x_pos)**2)
        
        #if recording and distance from last recorded position is at least 10cm, record current position
        if self.record and dist >= 0.1:
            #stand in for writing current odometry to file
            print("-> ", self.x_pos, ", ", self.y_pos)
            self.x_pos_prev = self.x_pos
            self.y_pos_prev = self.y_pos


def main(args=None):
    rclpy.init(args=args)
    aNode = OdomRecorder()
    try:
        rclpy.spin(aNode)
        
    except KeyboardInterrupt:
        pass
    finally:
        aNode.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        
if __name__== '__main__':
    main()
