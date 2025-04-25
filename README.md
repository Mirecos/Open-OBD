# **OPEN-OBD**

## **Installation**

Open-OBD doesn't have a lot of requirements. First of all, make sure to install [**Python**](https://www.python.org/downloads/). Then, you have two options:
- Installing an **ELM-327 OBD II emulator** to simulate a car connection from your computer
- Plug your device with an **OBD II cable** and run the app

### **ELM-327 Emulator (for Development Environment)**

In order to make the app work without plugging into a real car, you can install an **ELM-327** to simulate an OBD II connection. The way to go is the [**ELM-327 Python library**](https://github.com/Ircama/ELM327-emulator).

For **Windows installation**: You'll need to install *com0com* software and create a port pair (e.g., 'COM5' to 'COM6'). Then, you'll connect to one of the ports from the emulator, and the other with the Python app.

Once done, you can install the emulator:

```
$ pip install git+https://github.com/ircama/ELM327-emulator
$ python -m elm -p ${YOUR_SPECIFIED_COM_PORT}
```

### **Python App Installation**

To download and run the code (*only if Python is already installed*):
```
$ git clone https://github.com/Mirecos/Open-OBD/
$ python -m venv venv
$ ./venv/Scripts/activate
$ pip install -r requirements.txt
$ python main.py
```