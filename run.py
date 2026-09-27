"""
วิธีรัน:
    python run.py

เปิดจากเครื่องอื่นในวง LAN เดียวกัน:
    ดู IP ของเครื่องนี้ด้วย: ipconfig (Windows) หรือ ip a (Linux)
    แล้วเปิด http://<IP>:8000 จากเครื่องอื่น
"""
import socket
import uvicorn

if __name__ == "__main__":
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        local_ip = "ไม่พบ IP"

    print("\n" + "=" * 50)
    print("🖊️  ตู้เครื่องเขียนอัตโนมัติ  v2.0")
    print("=" * 50)
    print(f"   localhost      : http://localhost:8000")
    print(f"   IP เครื่องนี้  : http://{local_ip}:8000")
    print(f"   Admin Panel    : http://localhost:8000/admin")
    print("=" * 50)
    print("   กด Ctrl+C เพื่อหยุด\n")

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
