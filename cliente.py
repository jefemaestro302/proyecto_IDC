import asyncio
import aiocoap
import threading


async def turn_led_on(protocol):
    uri= "coap://192.168.250.201/led/turnOn"
    request = aiocoap.Message(code=aiocoap.GET, uri=uri)
    response =  await   protocol.request(request).response
    print('Result: %s\nPayload: %s' % (response.code, response.payload.decode('utf-8')))

async def turn_led_off(protocol):
    uri=  "coap://192.168.250.201/led/turnOff"
    request = aiocoap.Message(code=aiocoap.GET, uri=uri)
    response =   await  protocol.request(request).response
    print('Result: %s\nPayload: %s' % (response.code, response.payload.decode('utf-8')))

async def get_heartbeat(protocol):
    while(True):
        uri = "coap://192.168.250.201/"
        request = aiocoap.Message(code=aiocoap.GET, uri=uri)
        response = await protocol.request(request).response
        print('Result: %s\nPayload: %s' % (response.code, response.payload.decode('utf-8')))
    
async def observe_heartbeat(protocol):
    uri = "coap://192.168.250.201/sensor/observe"
    request = aiocoap.Message(code=aiocoap.GET, uri=uri, observe=0)  # Observe=0 to start observing

    requester = protocol.request(request)
    try:
        async for response in requester.observation:
            print('Notification: %s\nPayload: %s' % (response.code, response.payload.decode('utf-8')))
    except Exception as e:
        print(f"Observation ended or failed: {e}")


async def main():
    # Crear un contexto de cliente
    protocol = await aiocoap.Context.create_client_context()

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
            break
        elif option == "5":
            break
        else:
            print("Opcion no valida")
    

   

if __name__ == "__main__":
    asyncio.run(main())


