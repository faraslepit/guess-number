import socket
import threading
import random

STATE_WAITING = "WAITING"
STATE_PLAYING = "PLAYING"
STATE_GAME_OVER = "GAME_OVER"

HOST = '127.0.0.1'
PORT = 65432

games = {}
lock = threading.Lock()
server_running = True
server_socket = None

def console_input():
    global server_running
    while server_running:
        try:
            cmd = input("").strip().upper()
            if cmd == "STOP":
                print("\nОстановка сервера...")

                server_running = False
                break
        except:
            break

def handle_client(client_socket, address):
    with lock:
        games[client_socket] = {"state": STATE_WAITING, "secret": None, "attempts": 0}

    try:
        client_socket.send("Добро пожаловать! Введи START для начала игры.\n".encode('utf-8'))

        while True:
            if not server_running:
                break
            data = client_socket.recv(1024)
            if not data:
                break

            message = data.decode('utf-8').strip()
            if not message:
                continue

            print(f"[{address}] Получено: {message}")

            with lock:
                current_state = games[client_socket]["state"]
                secret_number = games[client_socket]["secret"]
                attempts = games[client_socket]["attempts"]

            if current_state == STATE_WAITING:
                if message.upper() == "START":
                    new_secret = random.randint(1, 100)
                    with lock:
                        games[client_socket]["state"] = STATE_PLAYING
                        games[client_socket]["secret"] = new_secret
                        games[client_socket]["attempts"] = 0
                    client_socket.send("Игра началась. Загадано число от 1 до 100.\n".encode('utf-8'))
                else:
                    client_socket.send("Введи команду START для начала игры.\n".encode('utf-8'))

            elif current_state == STATE_PLAYING:
                try:
                    guess = int(message)
                    with lock:
                        games[client_socket]["attempts"] += 1
                        attempts = games[client_socket]["attempts"]
                        secret_number = games[client_socket]["secret"]

                    if guess < secret_number:
                        client_socket.send("Маловато\n".encode('utf-8'))
                    elif guess > secret_number:
                        client_socket.send("Переборщил\n".encode('utf-8'))
                    else:
                        with lock:
                            games[client_socket]["state"] = STATE_GAME_OVER
                        client_socket.send(f"Красавчик! Ты угадал число за {attempts} попыток.\n".encode('utf-8'))
                        client_socket.send("Введи RESTART для новой игры или QUIT для выхода.\n".encode('utf-8'))
                except ValueError:
                    client_socket.send("ERROR: Введи число, а не текст.\n".encode('utf-8'))

            elif current_state == STATE_GAME_OVER:
                if message.upper() == "RESTART":
                    new_secret = random.randint(1, 100)
                    with lock:
                        games[client_socket]["state"] = STATE_PLAYING
                        games[client_socket]["secret"] = new_secret
                        games[client_socket]["attempts"] = 0
                    client_socket.send("Новая игра началась! Введи число от 1 до 100.\n".encode('utf-8'))
                elif message.upper() == "QUIT":
                    print(f"[{address}] Клиент завершил игру.")
                    break
                else:
                    client_socket.send("Игра окончена. Введи RESTART или QUIT.\n".encode('utf-8'))

    except Exception as e:
        print(f"Ошибка с клиентом {address}: {e}")
    finally:
        print(f"Клиент {address} отключился.")
        with lock:
            if client_socket in games:
                del games[client_socket]
        client_socket.close()

def start_server():
    global server_running, server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.settimeout(1.0)

    try:
        server_socket.bind((HOST, PORT))
        print(f"Сервер привязан к {HOST}:{PORT}")
        server_socket.listen(5)
        print("Введите STOP для остановки сервера\n")

        threading.Thread(target=console_input, daemon=True).start()

        while server_running:
            try:
                client_socket, address = server_socket.accept()
                print(f"Подключен клиент: {address}")
                thread = threading.Thread(target=handle_client, args=(client_socket, address))
                thread.daemon = True
                thread.start()
            except socket.timeout:
                continue
            except OSError:
                break

    except Exception as e:
        print(f"Ошибка сервера: {e}")
    finally:
        server_socket.close()
        print("Сервер остановлен.")

if __name__ == "__main__":
    start_server()
