"""Restore Kindle to normal mode (re-enable touch and UI)."""

import paramiko
from kindle_card.config import load


def main():
    config = load()
    kc = config.get("kindle", {})

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        connect_kwargs = {
            "hostname": kc.get("host", "192.168.1.100"),
            "port": kc.get("port", 22),
            "username": kc.get("user", "root"),
            "timeout": 10,
        }
        key_path = kc.get("key_path", "")
        if key_path:
            connect_kwargs["key_filename"] = key_path
        else:
            connect_kwargs["look_for_keys"] = True

        client.connect(**connect_kwargs)

        # Re-enable touchscreen
        client.exec_command("chmod 666 /dev/input/event1 2>/dev/null", timeout=5)

        # Restart framework
        client.exec_command(
            "/etc/upstart/framework &",
            timeout=5,
        )

        print("Kindle restored to normal mode.")
        print("Touch enabled, framework restarting.")
    except Exception as e:
        print(f"Restore failed: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
