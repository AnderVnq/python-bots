from flask import request
import traceback
import requests
import socket
import json


class BugLogger:

    def __init__(self):
        pass

    def get_client_ip(self):

        try:
            ip_address = None
            local_ip = None
            public_ip = self.get_public_ip()
            
            hostname = socket.gethostname()
            ip_addresses = socket.gethostbyname_ex(hostname)[2]
            for ip in ip_addresses:
                if ip != "127.0.0.1" and ":" not in ip:
                    local_ip = ip
                    break
            
            ip_address = f"IP Publica: {public_ip} , IP Local: {local_ip}"
            return ip_address
        except Exception as e:
            return None          

    def get_request_url(self):
        return request.url

    def get_http_method(self):
        return request.method


    def get_user_agent(self):
        return request.headers.get("User-Agent")
    
    def get_public_ip(self):
        try:
            response = requests.get("https://api.ipify.org?format=json")
            response.raise_for_status()
            public_ip = response.json()["ip"]
            return public_ip
        except requests.RequestException as e:
            
            return None

    def bug_logs_data(self, e, severity="ERROR"):
        try:
            # Intentamos convertir el código de error, si está disponible
            error_code = int(e.args[0]) if e.args and str(e.args[0]).isdigit() else 0
        except (IndexError, ValueError) as error:
            # Si no podemos acceder a e.args[0] o convertirlo a entero, asignamos 0
            error_code = 0

        log_row = {
            "event_type": e.__class__.__name__,
            "log_description": str(e),
            "ip_address": self.get_client_ip(),
            "severity": severity,
            "module": f"{e.__traceback__.tb_frame.f_code.co_filename} {e.__traceback__.tb_lineno}",
            "request_url": self.get_request_url(),
            "http_method": self.get_http_method(),
            "user_agent": self.get_user_agent(),
            "error_code": error_code,
            "stack_trace": ''.join(traceback.format_exception(type(e), e, e.__traceback__)),
            "session_id": None
        }

        log_list = [log_row]

        return json.dumps(log_list)

