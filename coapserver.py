import network
import time
import machine
from machine import Pin
import socket
import coapy
import dht
import _thread

led = machine.Pin("LED", machine.Pin.OUT)
sensor = dht.DHT11(Pin(15))   #sensor

my_ssid = "POCO_F3"
my_password = "12345678"
SERVER_PORT = 5683  # default CoAP port


wlan = network.WLAN(network.STA_IF)  # create station interface
wlan.active(True)  # activate the interface
 # connect to an AP

def connectToWifi():
    print('Starting attempt to connecto to WiFi...')
    nets = wlan.scan()
    for net in nets:
        ssid = net[0].decode("utf-8")
        if ssid == my_ssid:
            print('Network found!')
            wlan.connect(ssid, my_password)
            while not wlan.isconnected():
                machine.idle()  # save power while waiting

            connectionResults = wlan.ifconfig()
            print('WLAN connection succeeded with IP: ', connectionResults[0])
            break

    return wlan.isconnected()

connectToWifi()


def turnOnLed(packet, senderIp, senderPort):
    print('Turn-on-led request received:', packet.toString(), ', from: ', senderIp, ":", senderPort)
    start_led()
    
    client.sendResponse(senderIp, senderPort, packet.messageid,
                      "Led encendido", coapy.COAP_RESPONSE_CODE.COAP_CONTENT,
                      coapy.COAP_CONTENT_FORMAT.COAP_NONE, packet.token)
    


def turnOffLed(packet, senderIp, senderPort):
    print('Turn-off-led request received:', packet.toString(), ', from: ', senderIp, ":", senderPort)
    stop_led()
    client.sendResponse(senderIp, senderPort, packet.messageid,
                      "Led apagado", coapy.COAP_RESPONSE_CODE.COAP_CONTENT,
                      coapy.COAP_CONTENT_FORMAT.COAP_NONE, packet.token)
    


def returnSensor(packet, senderIp, senderPort):
    print('Heartbeat received:', packet.toString(), ', from: ', senderIp, ":", senderPort)

    try:
        sensor.measure() 
        temperature = sensor.temperature()
        response = f'Temperature: {temperature} C'
    except Exception as e:
        response = f'Error al leer el sensor: {str(e)}'
     
    client.sendResponse(senderIp, senderPort, packet.messageid,
                      temperature, coapy.COAP_RESPONSE_CODE.COAP_SENSOR_HEARTBEAT,
                      coapy.COAP_CONTENT_FORMAT.COAP_NONE, packet.token)
    


def observeSensor(packet, senderIp, senderPort):
    global observers
    print('Observe request received:', packet.toString(), ', from: ', senderIp, ":", senderPort)
    observers.append((senderIp, senderPort))
    client.sendResponse(senderIp, senderPort, packet.messageid,
                      "Observing sensor", coapy.COAP_RESPONSE_CODE.COAP_CONTENT,
                      coapy.COAP_CONTENT_FORMAT.COAP_NONE, packet.token)
    


def notify_observers():
    global observers
    while True:
        time.sleep(10)  # Notify every 10 seconds
        try:
            sensor.measure()
            temperature = sensor.temperature()
            message = f'Temperature: {temperature} C'
        except Exception as e:
            message = f'Error: {str(e)}'
        
        for observer in observers:
            addr = (observer[0], observer[1])
            client.sendResponse(addr[0], addr[1], 0,
                                message, coapy.COAP_RESPONSE_CODE.COAP_CONTENT,
                                coapy.COAP_CONTENT_FORMAT.COAP_NONE)
        print("Notified observers")


def start_led():
    led.on()

def stop_led():
    led.off()
    
client = coapy.Coap()
# setup callback for incoming response to a request
client.addIncomingRequestCallback('led/turnOn', turnOnLed)
client.addIncomingRequestCallback('led/turnOff', turnOffLed)
client.addIncomingRequestCallback('sensor/return', returnSensor)


# Starting CoAP...
client.start()

# start the thread
_thread.start_new_thread(notify_observers, ())

while True:
    client.poll(600)

# stop CoAP
client.stop()
