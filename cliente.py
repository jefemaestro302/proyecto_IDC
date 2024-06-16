import asyncio
import aiocoap
import threading
import sys
import socket
import signal

UDP_IP = "192.168.58.154"

CODIGO_HEARTBEAT = 0x43






def parse_coap_message(data):
    version_type_token = data[0]
    code = data[1]
    message_id = data[2:4]  
    token = data[4:4 + (version_type_token & 0x0F)]
    payload = data[4 + (version_type_token & 0x0F):]

    return code, payload



def udp_listener(udp_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, udp_port))

    print("UDP server up and listening")
    try:
        while True:
            data, addr = sock.recvfrom(1024)
            print("received message:", data)
            code, payload = parse_coap_message(data)
            print("code: ", code)
            print("payload: ", payload)
            if code == CODIGO_HEARTBEAT:
                print("Observation received")
                print("payload: ", payload.decode('utf-8'))
                #start observation
                #start_observation()
            else:
                print("Request")
                #handle request
                #handle_request()
    except KeyboardInterrupt:
        print("\nExiting due to Ctrl-C")
    finally:
        sock.close()






async def turn_led_on(protocol):
    uri= "coap://192.168.58.201/led/turnOn"
    request = aiocoap.Message(code=aiocoap.GET, uri=uri)
    response =  await   protocol.request(request).response
    print('Result: %s\nPayload: %s' % (response.code, response.payload.decode('utf-8')))

async def turn_led_off(protocol):
    uri=  "coap://192.168.58.201/led/turnOff"
    request = aiocoap.Message(code=aiocoap.GET, uri=uri)
    response =   await  protocol.request(request).response
    print('Result: %s\nPayload: %s' % (response.code, response.payload.decode('utf-8')))

async def get_heartbeat(protocol):
    while(True):
        uri = "coap://192.168.58.201/sensor/return"
        request = aiocoap.Message(code=aiocoap.GET, uri=uri)
        response = await protocol.request(request).response
        print('Result: %s\nPayload: %s' % (response.code, response.payload.decode('utf-8')))
    
async def observe_sensor_heartbeat(protocol):
    uri = "coap://192.168.58.201/sensor/observe"
    request = aiocoap.Message(code=aiocoap.GET, uri=uri, observe=0)  # Observe=0 to start observing
    response = await protocol.request(request).response
    port = int(response.payload.decode('utf-8'))
    return port
    #abrir socket udp que se quede escuchando





async def main():

    
    # Crear un contexto de cliente
    protocol = await aiocoap.Context.create_client_context()
    #port = await get_client_port(protocol)
    #udp_listener_thread = threading.Thread(target=udp_listener, args=(port,))
    #udp_listener_thread.daemon = True
    #udp_listener_thread.start()

    async def signal_handler(sig, frame):
        print("\nExiting due to Ctrl-C")
        if udp_listener_thread:
            udp_listener_thread.join()

    # Cerrar el contexto de cliente CoAP
        await protocol.shutdown()

        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    print("seleccione recurso a acceder")
    print("1. Encender led")
    print("2. Apagar led")
    print("3. Recibir heartbeat del sensor ")
    print("4. Observar sensor")
    print("5. Salir")

    while True: 
        option = input("Ingrese una opcion: ")
        if option == "1":
            await turn_led_on(protocol)
        elif option == "2":
            await turn_led_off(protocol)
        elif option == "3":
            await get_heartbeat(protocol)

        elif option == "4":
            port = await observe_sensor_heartbeat(protocol)
            port = port + 1
            print("port: ", port)
            udp_listener_thread = threading.Thread(target=udp_listener, args=(port,))
            udp_listener_thread.daemon = True
            udp_listener_thread.start()


        elif option == "5":
            break
        else:
            print("Opcion no valida")


    
   

if __name__ == "__main__":
    asyncio.run(main())


