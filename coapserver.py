import network
import time
import machine
from machine import Pin
import socket
import coapy


led = machine.Pin("LED", machine.Pin.OUT)

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
    client.sendResponse(senderIp, senderPort, packet.messageid,
                      None, coapy.COAP_RESPONSE_CODE.COAP_SENSOR_HEARTBEAT,
                      coapy.COAP_CONTENT_FORMAT.COAP_NONE, packet.token)

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

# wait for incoming request


while True:
    client.poll(600)

# stop CoAP
client.stop()