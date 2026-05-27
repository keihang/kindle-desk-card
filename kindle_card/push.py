import paramiko
from io import BytesIO
from PIL import Image


FRAMEBUFFER_WIDTH = 1088
FRAMEBUFFER_HEIGHT = 1448


def push_to_kindle(img: Image.Image, config: dict):
    """Push image to Kindle via SSH and write to framebuffer."""
    kc = config.get("kindle", {})
    host = kc.get("host", "192.168.1.100")
    port = kc.get("port", 22)
    user = kc.get("user", "root")
    key_path = kc.get("key_path", "")
    fbink = kc.get("fbink_path", "/mnt/us/koreader/fbink")
    waveform = config.get("display", {}).get("waveform", "GC16")

    # Convert image to framebuffer format: 1088x1448 8-bit grayscale
    fb_img = img.resize((FRAMEBUFFER_WIDTH, FRAMEBUFFER_HEIGHT), Image.LANCZOS)
    fb_img = fb_img.convert("L")
    raw_data = fb_img.tobytes()

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        connect_kwargs = {"hostname": host, "port": port, "username": user, "timeout": 10}
        if key_path:
            connect_kwargs["key_filename"] = key_path
        else:
            connect_kwargs["look_for_keys"] = True

        client.connect(**connect_kwargs)

        # Kill Kindle status bar to prevent overlay
        client.exec_command(
            "kill $(pidof JunoStatusBarDriver) $(pidof pillowd) 2>/dev/null",
            timeout=5,
        )

        # Upload raw framebuffer data via SFTP
        sftp = client.open_sftp()
        remote_path = "/tmp/card.raw"
        with sftp.open(remote_path, "wb") as f:
            f.write(raw_data)
        sftp.close()

        # Write to framebuffer and refresh
        size = len(raw_data)
        cmd = (
            f"dd if={remote_path} of=/dev/fb0 bs={size} count=1 2>/dev/null && "
            f"{fbink} -s -W {waveform} -f"
        )
        stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
        exit_code = stdout.channel.recv_exit_status()
        if exit_code != 0:
            err = stderr.read().decode().strip()
            print(f"Push error (exit {exit_code}): {err}")

    except Exception as e:
        print(f"Push failed: {e}")
    finally:
        client.close()
