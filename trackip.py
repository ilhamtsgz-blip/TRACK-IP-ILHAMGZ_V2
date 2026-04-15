import requests
import json
import os
import time
from datetime import datetime

# ========== KONFIGURASI ==========
TOKEN_FILE = "token_config.json"
TARGET_IP = ""
BOT_TOKEN = ""
CHAT_ID = ""

# ========== FUNGSI ==========
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_config():
    global BOT_TOKEN, CHAT_ID
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            data = json.load(f)
            BOT_TOKEN = data.get('bot_token', '')
            CHAT_ID = data.get('chat_id', '')

def save_config():
    with open(TOKEN_FILE, 'w') as f:
        json.dump({'bot_token': BOT_TOKEN, 'chat_id': CHAT_ID}, f)

def get_ip_info(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,zip,lat,lon,isp,org,as,query", timeout=10)
        data = response.json()
        if data['status'] == 'success':
            return data
        else:
            return None
    except:
        return None

def send_to_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        return "⚠️ Token/ID belum di set!"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
    try:
        r = requests.post(url, data=payload, timeout=10)
        return "✅ Terkirim!" if r.status_code == 200 else f"❌ Gagal: {r.text}"
    except:
        return "❌ Error koneksi"

def broadcast_to_all(message, user_ids_file="users.txt"):
    if not BOT_TOKEN:
        return "⚠️ Token bot belum di set!"
    if not os.path.exists(user_ids_file):
        return "⚠️ File users.txt tidak ditemukan!"
    with open(user_ids_file, 'r') as f:
        users = [line.strip() for line in f if line.strip()]
    success = 0
    for uid in users:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        try:
            r = requests.post(url, data={'chat_id': uid, 'text': message}, timeout=5)
            if r.status_code == 200:
                success += 1
        except:
            pass
    return f"✅ Broadcast selesai! Terkirim ke {success}/{len(users)} user"

def track_and_send(ip):
    info = get_ip_info(ip)
    if not info:
        msg = f"❌ Gagal melacak IP: {ip}"
    else:
        msg = f"""🎯 <b>HASIL PELACAKAN IP</b> 🎯
🔹 <b>IP:</b> {info['query']}
🌍 <b>Negara:</b> {info['country']}
🏙️ <b>Region/Kota:</b> {info['regionName']} - {info['city']}
📮 <b>Kode Pos:</b> {info['zip']}
📍 <b>Koordinat:</b> {info['lat']}, {info['lon']}
📡 <b>ISP:</b> {info['isp']}
🏢 <b>Organisasi:</b> {info['org']}
🔗 <b>AS:</b> {info['as']}
⏰ <b>Waktu:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    print(msg)
    result = send_to_telegram(msg)
    print(result)

def menu():
    global BOT_TOKEN, CHAT_ID, TARGET_IP
    load_config()
    while True:
        clear_screen()
        print("""
╔════════════════════════════════════╗
║   🔥 SHADOW IP TRACKER + BROADCAST 🔥
╠════════════════════════════════════╣
║ 1. Set Bot Token & Chat ID         ║
║ 2. Track IP & Kirim ke Telegram    ║
║ 3. Track IP (tanpa kirim)          ║
║ 4. Broadcast pesan ke semua user   ║
║ 5. Tambah user ID ke daftar        ║
║ 6. Lihat konfigurasi saat ini      ║
║ 7. Keluar                          ║
╚════════════════════════════════════╝
        """)
        print(f"📌 Token: {BOT_TOKEN[:10]}... | Chat ID: {CHAT_ID}")
        pilih = input(">> Pilih menu: ")

        if pilih == '1':
            BOT_TOKEN = input("Masukkan Bot Token: ")
            CHAT_ID = input("Masukkan Chat ID: ")
            save_config()
            print("✅ Tersimpan!")
            time.sleep(1)

        elif pilih == '2':
            ip = input("Masukkan IP target: ")
            track_and_send(ip)
            input("\nTekan Enter...")

        elif pilih == '3':
            ip = input("Masukkan IP target: ")
            info = get_ip_info(ip)
            if info:
                print(json.dumps(info, indent=2))
            else:
                print("❌ Gagal")
            input("\nTekan Enter...")

        elif pilih == '4':
            pesan = input("Masukkan pesan broadcast: ")
            hasil = broadcast_to_all(pesan)
            print(hasil)
            input("\nTekan Enter...")

        elif pilih == '5':
            uid = input("Masukkan User ID Telegram: ")
            with open("users.txt", "a") as f:
                f.write(uid + "\n")
            print("✅ User ditambahkan!")
            time.sleep(1)

        elif pilih == '6':
            print(f"Token: {BOT_TOKEN}")
            print(f"Chat ID: {CHAT_ID}")
            input("\nTekan Enter...")

        elif pilih == '7':
            print("Keluar...")
            break

if __name__ == "__main__":
    menu()