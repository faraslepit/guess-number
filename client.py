import socket
import threading
import sys

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 65432


def receive_messages(sock):
    buffer = ""
    try:
        while True:
            data = sock.recv(1024)

            if not data:
                print("\nСервер принудительно разорвал соединение.")
                break

            buffer += data.decode('utf-8')

            while '\n' in buffer:
                parts = buffer.split('\n', 1)
                line = parts[0]
                buffer = parts[1]

                print(f"{line}")

    except ConnectionResetError:
        print("\nСервер принудительно разорвал соединение.")
    except Exception as e:
        print(f"\nОшибка: {e}")
    finally:
        sock.close()
        sys.exit(0)


def connect_to_server(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((host, port))
    except ConnectionRefusedError:
        print(f"Ошибка: Не удалось подключиться к {host}:{port}")
        print("Проверьте, запущен ли сервер.")
        return None
    except Exception as e:
        print(f"Ошибка подключения: {e}")
        return None

    return sock


def main():
    host = SERVER_HOST
    port = SERVER_PORT

    sock = connect_to_server(host, port)
    if sock is None:
        return

    recv_thread = threading.Thread(target=receive_messages, args=(sock,), daemon=True)
    recv_thread.start()

    try:
        while True:
            user_input = input("> ")

            if not user_input.strip():
                continue

            if user_input.strip().upper() == 'QUIT':
                print("Отключение от сервера...")
                break

            sock.sendall((user_input + '\n').encode('utf-8'))

    except KeyboardInterrupt:
        print("\nПрервано пользователем.")
    finally:
        sock.close()
        print("Соединение закрыто.")


if __name__ == "__main__":
    main()
