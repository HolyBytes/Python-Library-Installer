#!/usr/bin/env python3
import os
import platform
import subprocess
import sys
import socket
import psutil
import getpass
import time
from datetime import datetime
import threading

# Warna untuk terminal (compatible dengan semua terminal)
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    PURPLE = '\033[35m'
    WHITE = '\033[37m'
    GRAY = '\033[90m'

# ASCII Art untuk header
ASCII_ART = f"""{Colors.GREEN}
╔══════════════════════════════════════════════════════════════════════════════╗
║  ██████╗ ██╗   ██╗████████╗██╗  ██╗ ██████╗ ███╗   ██╗                      ║
║  ██╔══██╗╚██╗ ██╔╝╚══██╔══╝██║  ██║██╔═══██╗████╗  ██║                      ║
║  ██████╔╝ ╚████╔╝    ██║   ███████║██║   ██║██╔██╗ ██║                      ║
║  ██╔═══╝   ╚██╔╝     ██║   ██╔══██║██║   ██║██║╚██╗██║                      ║
║  ██║        ██║      ██║   ██║  ██║╚██████╔╝██║ ╚████║                      ║
║  ╚═╝        ╚═╝      ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝                      ║
║                                                                              ║
║     ██╗     ██╗██████╗ ██████╗  █████╗ ██████╗ ██╗   ██╗                    ║
║     ██║     ██║██╔══██╗██╔══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝                    ║
║     ██║     ██║██████╔╝██████╔╝███████║██████╔╝ ╚████╔╝                     ║
║     ██║     ██║██╔══██╗██╔══██╗██╔══██║██╔══██╗  ╚██╔╝                      ║
║     ███████╗██║██████╔╝██║  ██║██║  ██║██║  ██║   ██║                       ║
║     ╚══════╝╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝                       ║
║                                                                              ║
║              ██╗███╗   ██╗███████╗████████╗ █████╗ ██╗     ██╗              ║
║              ██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██║     ██║              ║
║              ██║██╔██╗ ██║███████╗   ██║   ███████║██║     ██║              ║
║              ██║██║╚██╗██║╚════██║   ██║   ██╔══██║██║     ██║              ║
║              ██║██║ ╚████║███████║   ██║   ██║  ██║███████╗███████╗         ║
║              ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝         ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.ENDC}"""

# Daftar library berdasarkan kategori
LIBRARIES = {
    "🧮 Data Science & Analisis Data": [
        "pandas", "numpy", "scipy", "statsmodels", "scikit-learn",
        "seaborn", "matplotlib", "plotly", "bokeh", "xlrd",
        "openpyxl", "pyjanitor", "patsy", "pyarrow", "dask"
    ],
    "🤖 Machine Learning & AI": [
        "tensorflow", "keras", "torch", "xgboost", "lightgbm",
        "catboost", "fastai", "transformers", "flair", "mlflow",
        "optuna", "skorch", "gym", "stable-baselines3", "deepspeed"
    ],
    "🧠 NLP (Natural Language Processing)": [
        "nltk", "spacy", "gensim", "textblob", "sumy",
        "pytextrank", "polyglot", "yake", "sentence-transformers"
    ],
    "🌐 Web Development": [
        "flask", "django", "fastapi", "tornado", "bottle",
        "starlette", "sanic", "hug", "aiohttp", "jinja2"
    ],
    "🕸️ Web Scraping & Crawling": [
        "requests", "beautifulsoup4", "lxml", "scrapy", "selenium",
        "playwright", "httpx", "mechanicalsoup", "pyquery", "robobrowser"
    ],
    "🗃️ Database & ORM": [
        "sqlalchemy", "psycopg2", "pymysql", "mongoengine", "pymongo",
        "ponyorm", "peewee", "tinydb", "redis", "ormar"
    ],
    "📦 Packaging & Dependency": [
        "pip", "setuptools", "poetry", "pipenv", "virtualenv", 
        "wheel", "twine", "hatch", "build", "pipx"
    ],
    "⚙️ DevOps, Testing & Automation": [
        "pytest", "unittest", "nose2", "tox", "fabric",
        "invoke", "ansible", "docker", "pre-commit", "coverage"
    ],
    "🧰 Utility, Tools & Misc": [
        "tqdm", "rich", "loguru", "typer", "click",
        "pydantic", "arrow", "faker", "schedule", "pathlib"
    ],
    "🔐 Security & Cryptography": [
        "cryptography", "pycrypto", "hashlib", "ssl", "paramiko",
        "bcrypt", "passlib", "keyring", "cryptodome", "jwcrypto"
    ]
}

class SystemInfo:
    def __init__(self):
        self.username = getpass.getuser()
        self.hostname = socket.gethostname()
        self.os_name = self.get_os_info()
        self.cpu_info = self.get_cpu_info()
        self.memory_info = self.get_memory_info()
        self.network_info = self.get_network_info()
        
    def get_os_info(self):
        try:
            system = platform.system()
            release = platform.release()
            version = platform.version()
            
            if system == "Linux":
                # Cek apakah di Android (Termux)
                if "android" in platform.platform().lower() or os.path.exists("/system/build.prop"):
                    try:
                        with open("/system/build.prop", "r") as f:
                            content = f.read()
                            if "ro.build.version.release" in content:
                                for line in content.split('\n'):
                                    if line.startswith("ro.build.version.release"):
                                        android_version = line.split('=')[1]
                                        return f"Android {android_version}"
                    except:
                        pass
                    return "Android (Termux)"
                return f"Linux {release}"
            elif system == "Windows":
                return f"Windows {release}"
            elif system == "Darwin":
                return f"macOS {release}"
            else:
                return f"{system} {release}"
        except:
            return "Unknown OS"
    
    def get_cpu_info(self):
        try:
            return platform.processor() or "Unknown CPU"
        except:
            return "Unknown CPU"
    
    def get_memory_info(self):
        try:
            memory = psutil.virtual_memory()
            total_gb = round(memory.total / (1024**3), 2)
            used_gb = round(memory.used / (1024**3), 2)
            available_gb = round(memory.available / (1024**3), 2)
            return {
                'total': total_gb,
                'used': used_gb,
                'available': available_gb,
                'percent': memory.percent
            }
        except:
            return {'total': 0, 'used': 0, 'available': 0, 'percent': 0}
    
    def get_network_info(self):
        try:
            # Dapatkan IP address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
            s.close()
            
            # Deteksi jenis koneksi
            network_type = "Unknown"
            try:
                interfaces = psutil.net_if_stats()
                for interface_name, interface_info in interfaces.items():
                    if interface_info.isup:
                        if "wlan" in interface_name.lower() or "wifi" in interface_name.lower():
                            network_type = "📶 WiFi"
                            break
                        elif "eth" in interface_name.lower() or "lan" in interface_name.lower():
                            network_type = "🔌 Ethernet"
                            break
                        elif "ppp" in interface_name.lower() or "cellular" in interface_name.lower():
                            network_type = "📱 Mobile Data"
                            break
                if network_type == "Unknown":
                    network_type = "🌐 Network"
            except:
                network_type = "🌐 Network"
                
            return {'ip': ip_address, 'type': network_type}
        except:
            return {'ip': 'Disconnected', 'type': '❌ No Connection'}

def clear_screen():
    """Membersihkan layar terminal dengan kompatibilitas penuh"""
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # Unix/Linux/macOS/Android
        os.system('clear')

def loading_animation():
    """Animasi loading yang menarik"""
    chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    for i in range(30):
        sys.stdout.write(f"\r{Colors.CYAN}[{chars[i % len(chars)]}] Initializing system... {Colors.ENDC}")
        sys.stdout.flush()
        time.sleep(0.1)
    print()

def typing_effect(text, delay=0.03):
    """Efek mengetik untuk teks"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def print_system_info(sys_info):
    """Menampilkan informasi sistem dengan styling menarik"""
    print(f"{Colors.BOLD}{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}║                              SYSTEM INFORMATION                             ║{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}╠══════════════════════════════════════════════════════════════════════════════╣{Colors.ENDC}")
    
    info_items = [
        (f"👤 User", sys_info.username),
        (f"🖥️  Hostname", sys_info.hostname),
        (f"💻 Operating System", sys_info.os_name),
        (f"🔧 CPU", sys_info.cpu_info),
        (f"🧠 RAM Total", f"{sys_info.memory_info['total']} GB"),
        (f"📊 RAM Used", f"{sys_info.memory_info['used']} GB ({sys_info.memory_info['percent']:.1f}%)"),
        (f"💾 RAM Available", f"{sys_info.memory_info['available']} GB"),
        (f"🌐 IP Address", sys_info.network_info['ip']),
        (f"📡 Network Type", sys_info.network_info['type'])
    ]
    
    for label, value in info_items:
        print(f"{Colors.CYAN}║{Colors.ENDC} {Colors.YELLOW}{label:<20}{Colors.ENDC}: {Colors.WHITE}{value:<50}{Colors.CYAN}║{Colors.ENDC}")
    
    print(f"{Colors.BOLD}{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.ENDC}")

def print_developer_info():
    """Menampilkan informasi developer"""
    print(f"\n{Colors.BOLD}{Colors.PURPLE}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.PURPLE}║                              DEVELOPER INFORMATION                          ║{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.PURPLE}╠══════════════════════════════════════════════════════════════════════════════╣{Colors.ENDC}")
    print(f"{Colors.PURPLE}║{Colors.ENDC} {Colors.YELLOW}👨‍💻 Developer{Colors.ENDC}        : {Colors.WHITE}ADE PRATAMA{Colors.PURPLE}                                        ║{Colors.ENDC}")
    print(f"{Colors.PURPLE}║{Colors.ENDC} {Colors.YELLOW}🐙 GitHub{Colors.ENDC}           : {Colors.WHITE}https://github.com/HolyBytes{Colors.PURPLE}                      ║{Colors.ENDC}")
    print(f"{Colors.PURPLE}║{Colors.ENDC} {Colors.YELLOW}💰 Donasi{Colors.ENDC}           : {Colors.WHITE}https://saweria.co/HolyBytes{Colors.PURPLE}                      ║{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.PURPLE}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.ENDC}")

def get_pip_command():
    """Mendapatkan perintah pip yang sesuai dengan error handling yang lebih baik"""
    pip_commands = [
        [sys.executable, "-m", "pip"],
        ["pip3"],
        ["pip"],
        ["python", "-m", "pip"],
        ["python3", "-m", "pip"]
    ]
    
    for cmd in pip_commands:
        try:
            subprocess.check_call(cmd + ["--version"], 
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL)
            return cmd
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    return None

def install_libraries(libraries):
    """Menginstal library Python dengan progress bar yang menarik"""
    pip_command = get_pip_command()
    if not pip_command:
        print(f"{Colors.RED}❌ Error: Pip tidak ditemukan. Pastikan pip terinstal dengan benar.{Colors.ENDC}")
        return False
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}🚀 Memulai instalasi library...{Colors.ENDC}")
    print(f"{Colors.GRAY}{'='*80}{Colors.ENDC}")
    
    success_count = 0
    total_count = len(libraries)
    
    for i, lib in enumerate(libraries, 1):
        progress = f"({i}/{total_count})"
        print(f"{Colors.CYAN}📦 {progress} Installing {lib}...{Colors.ENDC}", end=' ', flush=True)
        
        try:
            subprocess.check_call(pip_command + ["install", "--upgrade", lib], 
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL)
            print(f"{Colors.GREEN}✅ SUCCESS{Colors.ENDC}")
            success_count += 1
        except subprocess.CalledProcessError:
            print(f"{Colors.RED}❌ FAILED{Colors.ENDC}")
    
    print(f"{Colors.GRAY}{'='*80}{Colors.ENDC}")
    print(f"{Colors.GREEN}✨ Instalasi selesai! {success_count}/{total_count} library berhasil diinstal.{Colors.ENDC}")
    
    if success_count < total_count:
        print(f"{Colors.YELLOW}⚠️  {total_count - success_count} library gagal diinstal. Periksa koneksi internet dan dependensi.{Colors.ENDC}")
    
    return True

def show_menu(sys_info):
    """Menampilkan menu pilihan dengan styling menarik"""
    while True:
        clear_screen()
        print(ASCII_ART)
        print_system_info(sys_info)
        print_developer_info()
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.GREEN}║                           PILIH KATEGORI LIBRARY                             ║{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.GREEN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.ENDC}")
        
        # Tampilkan kategori dengan styling
        categories = list(LIBRARIES.keys())
        for i, category in enumerate(categories, 1):
            print(f"{Colors.BLUE}[{i:2d}]{Colors.ENDC} {Colors.WHITE}{category}{Colors.ENDC}")
        
        print(f"\n{Colors.YELLOW}[99]{Colors.ENDC} {Colors.WHITE}🚀 Install Semua Library{Colors.ENDC}")
        print(f"{Colors.RED}[ 0]{Colors.ENDC} {Colors.WHITE}❌ Keluar{Colors.ENDC}")
        
        try:
            choice = input(f"\n{Colors.BOLD}{Colors.CYAN}┌─[{sys_info.username}@{sys_info.hostname}]─[~/python-installer]")
            choice = input(f"{Colors.CYAN}└─$ {Colors.ENDC}").strip()
            
            if choice == "0":
                print(f"\n{Colors.YELLOW}👋 Terima kasih telah menggunakan Python Library Installer!{Colors.ENDC}")
                typing_effect(f"{Colors.GREEN}Sampai jumpa lagi...{Colors.ENDC}")
                time.sleep(1)
                clear_screen()
                sys.exit(0)
                
            elif choice == "99":
                print(f"\n{Colors.BOLD}{Colors.RED}⚠️  PERINGATAN: Anda akan menginstal SEMUA library!{Colors.ENDC}")
                confirm = input(f"{Colors.YELLOW}Apakah Anda yakin? (y/N): {Colors.ENDC}").lower()
                if confirm in ['y', 'yes']:
                    all_libs = []
                    for libs in LIBRARIES.values():
                        all_libs.extend(libs)
                    if install_libraries(all_libs):
                        input(f"\n{Colors.GREEN}✨ Tekan Enter untuk kembali ke menu...{Colors.ENDC}")
                        
            elif choice.isdigit() and 1 <= int(choice) <= len(categories):
                selected_category = categories[int(choice)-1]
                print(f"\n{Colors.GREEN}📦 Installing {selected_category}...{Colors.ENDC}")
                if install_libraries(LIBRARIES[selected_category]):
                    input(f"\n{Colors.GREEN}✨ Tekan Enter untuk kembali ke menu...{Colors.ENDC}")
                    
            else:
                print(f"{Colors.RED}❌ Pilihan tidak valid! Mohon masukkan angka yang benar.{Colors.ENDC}")
                time.sleep(2)
                
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}👋 Program dihentikan oleh pengguna.{Colors.ENDC}")
            time.sleep(1)
            clear_screen()
            sys.exit(0)
        except Exception as e:
            print(f"{Colors.RED}❌ Terjadi kesalahan: {str(e)}{Colors.ENDC}")
            time.sleep(2)

def main():
    """Fungsi utama program"""
    try:
        # Cek versi Python
        if sys.version_info[0] < 3:
            print(f"{Colors.RED}❌ Tool ini membutuhkan Python 3 atau yang lebih baru.{Colors.ENDC}")
            sys.exit(1)
        
        # Cek dan install psutil jika belum ada
        try:
            import psutil
        except ImportError:
            print(f"{Colors.YELLOW}📦 Installing required dependency: psutil{Colors.ENDC}")
            pip_cmd = get_pip_command()
            if pip_cmd:
                subprocess.check_call(pip_cmd + ["install", "psutil"], 
                                    stdout=subprocess.DEVNULL, 
                                    stderr=subprocess.DEVNULL)
                import psutil
            else:
                print(f"{Colors.RED}❌ Cannot install required dependencies.{Colors.ENDC}")
                sys.exit(1)
        
        clear_screen()
        
        # Loading animation
        print(f"{Colors.BOLD}{Colors.GREEN}Python Library Installer - Advanced Version{Colors.ENDC}")
        loading_animation()
        
        # Inisialisasi system info
        print(f"{Colors.CYAN}🔍 Collecting system information...{Colors.ENDC}")
        sys_info = SystemInfo()
        
        # Welcome message
        clear_screen()
        print(f"{Colors.BOLD}{Colors.GREEN}🎉 SELAMAT DATANG, {sys_info.username.upper()}! 🎉{Colors.ENDC}")
        typing_effect(f"{Colors.CYAN}Sistem berhasil diinisialisasi pada {sys_info.os_name}{Colors.ENDC}")
        time.sleep(2)
        
        # Mulai program utama
        show_menu(sys_info)
        
    except Exception as e:
        print(f"{Colors.RED}❌ Fatal Error: {str(e)}{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
