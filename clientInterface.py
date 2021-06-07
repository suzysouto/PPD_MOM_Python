import string
from tkinter import *
import PIL.Image, PIL.ImageTk
import pika
import threading as thread
import time
from random import *

class InterfaceUser:
    def __init__(self):
        app = Tk()

        app.geometry('700x400')
        app.resizable(0, 0)

        self.controller = True

        app.title("Monitor de Sensores")
        lbl_title = Label(app, text="Monitor de Sensores", font=('Helvatical bold',40), fg="blue")
        lbl_title.pack(pady=15)

        lbl_menu = Label(app, text="Escolha um sensor para monitorar.", font=('Helvatical bold',18), fg="blue")
        lbl_menu.pack()
        self.app = app

        OptionList = ["Umidade", "Temperatura", "Velocidade"] 

        option_menu = StringVar(app)
        option_menu.set("")
        self.selection = OptionList[0]
        self.option_menu = option_menu

        opt = OptionMenu(app, option_menu, *OptionList)
        opt.config(width=10, font=('Helvetica', 10))
        opt.pack(pady=10)
        self.opt = opt 

        b1 = Button(app,  text='Confirmar escolha de sensor', command=self.my_show) 
        b1.pack()     

        str_out=StringVar(app)
        str_out.set("Sensor escolhido: ")
        self.str_out = str_out

        l2 = Label(app, textvariable=str_out, width=20, fg="blue", font=('Helvetica', 15))
        l2.pack(pady=15)                 

        app2 = Frame(app, width=700, height=200)
        self.app2 = app2
        l3 = Label(app2, text="Medição", width=15, fg="blue", font=('Helvetica', 15))
        l3.pack(side=LEFT, fill=BOTH, pady=15) 

        app3 = Frame(app, width=700, height=200)
        self.app3 = app3
        l4 = Label(app3, text="-", width=50, fg="blue", font=('Helvetica', 15))
        l4.pack(side=LEFT, fill=BOTH) 
        self.l4 = l4
        app3.pack()  
                   

    def start_app(self):
        self.app.mainloop() 

    def my_show(self): 
        self.controller = False
        recebida = self.option_menu.get()
        self.str_out.set(recebida)        
         
        threadReceber = thread.Thread(target=self.rabbit_jesus_receive, daemon=True)
        threadReceber.start()
        time.sleep(1)

        threadMandar = thread.Thread(target=self.rabbit_jesus_send, daemon=True)
        threadMandar.start()

        self.controller = True

    def rabbit_jesus_receive(self):
        connection = pika.BlockingConnection (pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.exchange_declare(exchange=self.option_menu.get(), exchange_type='fanout')

        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue

        channel.queue_bind(exchange=self.option_menu.get(), queue=queue_name)

        print(' [*] Waiting for logs. To exit press CTRL + C.')

        def callback(ch, method, properties, body):
            responseString = body.decode("utf-8")
            print ("[x] %r" % responseString)
            self.l4.config(text=responseString)

        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

        channel.start_consuming()

    def rabbit_jesus_send(self):
        connection = pika.BlockingConnection (pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.exchange_declare(exchange=self.option_menu.get(), exchange_type='fanout')

        
        while(self.controller):
            randnum = randint(0, 100) 
            message = str(randnum) + self.simbolo_sensor(self.option_menu.get())         
            channel.basic_publish(exchange=self.option_menu.get(), routing_key='', body=message)
            print("[x] Sent %r" % message)
            time.sleep(1)
        
        connection.close()
        print("CONEXÃO FECHADA!")
        #Quando mudar de conexão dá um connection.close()

    def simbolo_sensor(self, option_menu):
        if option_menu == "Umidade":
            return "%"
        elif option_menu == "Velocidade":
            return "m/s"
        return "ºC"


if __name__ == "__main__":
    interfaceUser = InterfaceUser()
    interfaceUser.start_app()