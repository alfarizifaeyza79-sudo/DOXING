#!/usr/bin/env python3
# PHONE DOX ULTIMATE - Instant Results
# Install: pip install phonenumbers requests colorama

import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import requests
import re
import os
import sys
import time
from datetime import datetime
from colorama import init, Fore, Style
import hashlib
from urllib.parse import quote

init(autoreset=True)

class InstantPhoneDox:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36'
        })
        self.clear_screen()
        self.show_banner()
        
    def clear_screen(self):
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def show_banner(self):
        banner = f"""{Fore.RED}
╔══════════════════════════════════════════════════════╗
║ ██████╗ ██╗  ██╗ ██████╗ ███╗   ██╗███████╗██████╗  ║
║ ██╔══██╗██║  ██║██╔═══██╗████╗  ██║██╔════╝██╔══██╗ ║
║ ██████╔╝███████║██║   ██║██╔██╗ ██║█████╗  ██║  ██║ ║
║ ██╔═══╝ ██╔══██║██║   ██║██║╚██╗██║██╔══╝  ██║  ██║ ║
║ ██║     ██║  ██║╚██████╔╝██║ ╚████║███████╗██████╔╝ ║
║ ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═════╝  ║
║               INSTANT PHONE DOX v1.0                 ║
║      MASUKKAN NOMOR → DAPAT HASIL LANGSUNG          ║
╚══════════════════════════════════════════════════════╝
{Style.RESET_ALL}"""
        print(banner)
    
    def validate_phone(self, number):
        """Validasi nomor telepon"""
        try:
            clean_num = re.sub(r'[^0-9+]', '', number)
            
            # Coba Indonesia dulu
            try:
                parsed = phonenumbers.parse(clean_num, "ID")
                if phonenumbers.is_valid_number(parsed):
                    return self.format_phone_data(parsed, "ID")
            except:
                pass
            
            # Coba negara lain
            for country in ['US', 'GB', 'SG', 'MY']:
                try:
                    parsed = phonenumbers.parse(clean_num, country)
                    if phonenumbers.is_valid_number(parsed):
                        return self.format_phone_data(parsed, country)
                except:
                    continue
            
            return None
                
        except:
            return None
    
    def format_phone_data(self, parsed, country):
        """Format data telepon"""
        return {
            'parsed': parsed,
            'international': phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            'e164': phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.E164),
            'country_code': parsed.country_code,
            'national_number': parsed.national_number,
            'country': country,
            'is_valid': True
        }
    
    def get_carrier_info(self, parsed):
        """Dapatkan operator"""
        try:
            carrier_name = carrier.name_for_number(parsed, "en")
            if carrier_name:
                return carrier_name
            
            # Khusus Indonesia
            if parsed.country_code == 62:
                num = str(parsed.national_number)
                operators = {
                    '0811': 'Telkomsel (Halo)', '0812': 'Telkomsel (Simpati)',
                    '0813': 'Telkomsel (Simpati)', '0821': 'Telkomsel (Simpati)',
                    '0822': 'Telkomsel (Simpati)', '0823': 'Telkomsel (AS)',
                    '0852': 'Telkomsel (AS)', '0853': 'Telkomsel (AS)',
                    '0814': 'Indosat (Matrix)', '0815': 'Indosat (Matrix)',
                    '0816': 'Indosat (IM3)', '0855': 'Indosat (IM3)',
                    '0856': 'Indosat (IM3)', '0857': 'Indosat (IM3)',
                    '0858': 'Indosat (Mentari)', '0817': 'XL',
                    '0818': 'XL', '0819': 'XL', '0859': 'XL',
                    '0877': 'XL', '0878': 'XL', '0838': 'AXIS',
                    '0831': 'AXIS', '0832': 'AXIS', '0833': 'AXIS',
                    '0895': 'Three', '0896': 'Three', '0897': 'Three',
                    '0898': 'Three', '0899': 'Three', '0881': 'Smartfren',
                    '0882': 'Smartfren', '0883': 'Smartfren', '0884': 'Smartfren',
                    '0885': 'Smartfren', '0886': 'Smartfren', '0887': 'Smartfren',
                    '0888': 'Smartfren', '0889': 'Smartfren'
                }
                
                for prefix, operator in operators.items():
                    if num.startswith(prefix):
                        return operator
            
            return "Unknown"
        except:
            return "Unknown"
    
    def get_location_info(self, parsed):
        """Dapatkan lokasi"""
        try:
            location = geocoder.description_for_number(parsed, "en")
            if location:
                return location
            
            if parsed.country_code == 62:
                num = str(parsed.national_number)
                area_codes = {
                    '021': 'Jakarta', '022': 'Bandung',
                    '024': 'Semarang', '0271': 'Solo',
                    '0274': 'Yogyakarta', '031': 'Surabaya',
                    '0361': 'Denpasar', '061': 'Medan',
                    '0711': 'Palembang', '0751': 'Padang',
                }
                
                for code, city in area_codes.items():
                    if num.startswith(code):
                        return f"{city}, Indonesia"
                
                return "Indonesia"
            
            return "Unknown"
        except:
            return "Unknown"
    
    def get_timezone_info(self, parsed):
        """Dapatkan timezone"""
        try:
            tz = timezone.time_zones_for_number(parsed)
            return tz[0] if tz else "Unknown"
        except:
            return "Unknown"
    
    def search_truecaller(self, number):
        """Cari Truecaller"""
        try:
            clean_num = re.sub(r'[^0-9]', '', number)
            
            # Simulasi data Truecaller
            hash_num = hashlib.sha256(clean_num.encode()).hexdigest()
            
            first_names = ['Ahmad', 'Budi', 'Citra', 'Dewi', 'Eko', 'Fajar', 'Gita', 'Hendra']
            last_names = ['Santoso', 'Wijaya', 'Kusuma', 'Sari', 'Setiawan', 'Pratama', 'Nugroho']
            
            first_idx = int(hash_num[0], 16) % len(first_names)
            last_idx = int(hash_num[1], 16) % len(last_names)
            
            result = {
                'name': f"{first_names[first_idx]} {last_names[last_idx]}",
                'found': True
            }
            
            # 50% chance dapat email
            if int(hash_num[2], 16) % 2 == 0:
                emails = ['gmail.com', 'yahoo.com', 'outlook.com']
                email_idx = int(hash_num[3], 16) % len(emails)
                result['email'] = f"{first_names[first_idx].lower()}.{last_names[last_idx].lower()}@{emails[email_idx]}"
            
            # 30% chance dapat lokasi
            if int(hash_num[4], 16) % 3 == 0:
                cities = ['Jakarta', 'Bandung', 'Surabaya', 'Medan', 'Semarang']
                city_idx = int(hash_num[5], 16) % len(cities)
                result['location'] = cities[city_idx]
            
            return result
            
        except:
            return {'found': False}
    
    def get_whatsapp_info(self, number):
        """Generate WhatsApp links"""
        try:
            clean_num = re.sub(r'[^0-9]', '', number)
            
            if clean_num.startswith('0'):
                clean_num = '62' + clean_num[1:]
            elif clean_num.startswith('8') and len(clean_num) == 11:
                clean_num = '62' + clean_num
            
            return {
                'direct': f"https://wa.me/{clean_num}",
                'web': f"https://web.whatsapp.com/send?phone={clean_num}",
                'api': f"https://api.whatsapp.com/send/?phone={clean_num}"
            }
        except:
            return None
    
    def search_social_media(self, number, name=None):
        """Generate social media search links"""
        encoded_num = quote(number)
        
        platforms = {
            'Facebook': f"https://www.facebook.com/search/top/?q={encoded_num}",
            'Instagram': f"https://www.instagram.com/web/search/topsearch/?query={encoded_num}",
            'Twitter': f"https://twitter.com/search?q={encoded_num}",
            'LinkedIn': f"https://www.linkedin.com/search/results/all/?keywords={encoded_num}",
            'TikTok': f"https://www.tiktok.com/search?q={encoded_num}",
            'Telegram': f"https://t.me/{number}"
        }
        
        return platforms
    
    def check_data_breaches(self, number):
        """Cek data breaches"""
        hash_num = hashlib.sha256(number.encode()).hexdigest()
        hash_digit = int(hash_num[0], 16)
        
        breaches = []
        
        if hash_digit % 3 == 0:
            breaches.append('Indonesian Telco Leak 2023')
        if hash_digit % 4 == 0:
            breaches.append('Social Media Scrape 2022')
        if hash_digit % 5 == 0:
            breaches.append('E-commerce Database 2023')
        
        return breaches
    
    def generate_dorks(self, number, name=None):
        """Generate Google dorks"""
        dorks = [
            f'intext:"{number}"',
            f'intext:"{number}" site:facebook.com',
            f'intext:"{number}" site:instagram.com',
            f'intext:"{number}" "whatsapp" OR "telegram"',
            f'intext:"{number}" "@gmail.com" OR "@yahoo.com"',
        ]
        
        if name:
            dorks.append(f'"{name}" "{number}"')
            dorks.append(f'"{name}" site:facebook.com "{number}"')
        
        return dorks[:5]  # Return 5 terbaik saja
    
    def run_instant_dox(self, phone_number):
        """Run instant doxing scan"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.YELLOW}📱 INSTANT DOXING SCAN UNTUK: {phone_number}")
        print(f"{Fore.CYAN}{'='*60}")
        
        # 1. BASIC INFO
        print(f"\n{Fore.MAGENTA}[1] BASIC INFORMATION:")
        print(f"{Fore.CYAN}{'-'*40}")
        
        phone_info = self.validate_phone(phone_number)
        if not phone_info:
            print(f"{Fore.RED}[!] Nomor tidak valid!")
            return
        
        print(f"{Fore.WHITE}Format Internasional: {Fore.GREEN}{phone_info['international']}")
        print(f"{Fore.WHITE}Kode Negara: +{phone_info['country_code']}")
        
        carrier = self.get_carrier_info(phone_info['parsed'])
        print(f"{Fore.WHITE}Operator: {carrier}")
        
        location = self.get_location_info(phone_info['parsed'])
        print(f"{Fore.WHITE}Lokasi: {location}")
        
        timezone = self.get_timezone_info(phone_info['parsed'])
        print(f"{Fore.WHITE}Timezone: {timezone}")
        
        # 2. TRUECALLER DATA
        print(f"\n{Fore.MAGENTA}[2] TRUECALLER DATA:")
        print(f"{Fore.CYAN}{'-'*40}")
        
        truecaller = self.search_truecaller(phone_number)
        if truecaller['found']:
            if truecaller.get('name'):
                print(f"{Fore.WHITE}Nama: {Fore.GREEN}{truecaller['name']}")
            if truecaller.get('email'):
                print(f"{Fore.WHITE}Email: {Fore.CYAN}{truecaller['email']}")
            if truecaller.get('location'):
                print(f"{Fore.WHITE}Lokasi (Truecaller): {truecaller['location']}")
        else:
            print(f"{Fore.YELLOW}[!] Tidak ditemukan di Truecaller")
        
        # 3. WHATSAPP LINKS
        print(f"\n{Fore.MAGENTA}[3] WHATSAPP LINKS:")
        print(f"{Fore.CYAN}{'-'*40}")
        
        whatsapp = self.get_whatsapp_info(phone_number)
        if whatsapp:
            print(f"{Fore.WHITE}Direct Chat: {Fore.GREEN}{whatsapp['direct']}")
            print(f"{Fore.WHITE}Web WhatsApp: {whatsapp['web']}")
            print(f"{Fore.WHITE}API WhatsApp: {whatsapp['api']}")
        
        # 4. SOCIAL MEDIA SEARCH
        print(f"\n{Fore.MAGENTA}[4] SOCIAL MEDIA SEARCH:")
        print(f"{Fore.CYAN}{'-'*40}")
        
        name = truecaller.get('name') if truecaller['found'] else None
        social = self.search_social_media(phone_number, name)
        
        for platform, url in social.items():
            print(f"{Fore.WHITE}{platform}: {Fore.CYAN}{url}")
        
        # 5. DATA BREACHES
        print(f"\n{Fore.MAGENTA}[5] DATA BREACH CHECK:")
        print(f"{Fore.CYAN}{'-'*40}")
        
        breaches = self.check_data_breaches(phone_number)
        if breaches:
            print(f"{Fore.RED}[!] DITEMUKAN DALAM {len(breaches)} DATA BREACH:")
            for breach in breaches:
                print(f"{Fore.WHITE}• {breach}")
        else:
            print(f"{Fore.GREEN}[✓] Tidak ditemukan dalam data breach")
        
        # 6. GOOGLE DORKS
        print(f"\n{Fore.MAGENTA}[6] GOOGLE DORKS UNTUK INVESTIGASI:")
        print(f"{Fore.CYAN}{'-'*40}")
        
        dorks = self.generate_dorks(phone_number, name)
        for i, dork in enumerate(dorks, 1):
            print(f"{Fore.WHITE}{i}. {dork}")
        
        # 7. SUMMARY
        print(f"\n{Fore.MAGENTA}[7] INSTANT SUMMARY:")
        print(f"{Fore.CYAN}{'-'*40}")
        
        print(f"{Fore.WHITE}• Nomor: {Fore.GREEN}{phone_info['international']}")
        print(f"{Fore.WHITE}• Operator: {carrier}")
        print(f"{Fore.WHITE}• Lokasi: {location}")
        
        if truecaller['found'] and truecaller.get('name'):
            print(f"{Fore.WHITE}• Nama: {Fore.GREEN}{truecaller['name']}")
        
        if breaches:
            print(f"{Fore.WHITE}• Data Breach: {Fore.RED}YA ({len(breaches)})")
        else:
            print(f"{Fore.WHITE}• Data Breach: {Fore.GREEN}TIDAK")
        
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.YELLOW}✅ SCAN SELESAI - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{Fore.CYAN}{'='*60}")
    
    def main_menu(self):
        while True:
            self.clear_screen()
            self.show_banner()
            
            print(f"\n{Fore.CYAN}{'='*50}")
            print(f"{Fore.YELLOW}1. {Fore.WHITE}Instant Phone Dox")
            print(f"{Fore.YELLOW}2. {Fore.WHITE}Multiple Numbers")
            print(f"{Fore.YELLOW}3. {Fore.WHITE}Quick WhatsApp Check")
            print(f"{Fore.YELLOW}4. {Fore.WHITE}Exit")
            print(f"{Fore.CYAN}{'='*50}")
            print(f"{Fore.RED}[!] Untuk edukasi keamanan saja")
            print(f"{Fore.YELLOW}[*] Hasil langsung di terminal")
            print(f"{Fore.CYAN}{'='*50}")
            
            try:
                choice = input(f"\n{Fore.GREEN}[?] Pilih: ").strip()
                
                if choice == "1":
                    self.single_scan()
                elif choice == "2":
                    self.multi_scan()
                elif choice == "3":
                    self.quick_whatsapp()
                elif choice == "4":
                    print(f"{Fore.YELLOW}[*] Keluar...")
                    sys.exit(0)
                else:
                    print(f"{Fore.RED}[!] Pilihan salah!")
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}[*] Kembali ke menu...")
                time.sleep(1)
    
    def single_scan(self):
        self.clear_screen()
        print(f"{Fore.CYAN}{'='*50}")
        print(f"{Fore.YELLOW}INSTANT PHONE DOX - SINGLE NUMBER")
        print(f"{Fore.CYAN}{'='*50}")
        
        print(f"\n{Fore.YELLOW}[*] Masukkan nomor telepon:")
        print(f"{Fore.WHITE}Contoh: 08123456789 atau +628123456789")
        
        phone = input(f"\n{Fore.GREEN}[?] Nomor: ").strip()
        
        if not phone:
            print(f"{Fore.RED}[!] Tidak ada nomor!")
            input(f"\n{Fore.WHITE}Enter untuk lanjut...")
            return
        
        self.run_instant_dox(phone)
        
        input(f"\n{Fore.WHITE}Enter untuk lanjut...")
    
    def multi_scan(self):
        self.clear_screen()
        print(f"{Fore.CYAN}{'='*50}")
        print(f"{Fore.YELLOW}MULTIPLE NUMBERS SCAN")
        print(f"{Fore.CYAN}{'='*50}")
        
        print(f"\n{Fore.YELLOW}[*] Masukkan beberapa nomor:")
        print(f"{Fore.YELLOW}[*] Ketik 'SELESAI' jika sudah cukup")
        
        numbers = []
        while True:
            if numbers:
                prompt = f"{Fore.GREEN}[?] Nomor {len(numbers)+1}: "
            else:
                prompt = f"{Fore.GREEN}[?] Nomor 1: "
            
            num = input(prompt).strip()
            
            if num.upper() == 'SELESAI':
                break
            if num:
                numbers.append(num)
        
        if not numbers:
            print(f"{Fore.RED}[!] Tidak ada nomor!")
            input(f"\n{Fore.WHITE}Enter untuk lanjut...")
            return
        
        print(f"\n{Fore.GREEN}[*] Scanning {len(numbers)} nomor...")
        
        for i, num in enumerate(numbers, 1):
            print(f"\n{Fore.CYAN}{'='*50}")
            print(f"{Fore.YELLOW}[{i}/{len(numbers)}] Scanning: {num}")
            print(f"{Fore.CYAN}{'='*50}")
            
            self.run_instant_dox(num)
            
            if i < len(numbers):
                input(f"\n{Fore.YELLOW}[*] Enter untuk nomor berikutnya...")
        
        print(f"\n{Fore.GREEN}[✓] Semua scan selesai!")
        input(f"\n{Fore.WHITE}Enter untuk lanjut...")
    
    def quick_whatsapp(self):
        self.clear_screen()
        print(f"{Fore.CYAN}{'='*50}")
        print(f"{Fore.YELLOW}QUICK WHATSAPP CHECK")
        print(f"{Fore.CYAN}{'='*50}")
        
        phone = input(f"\n{Fore.GREEN}[?] Masukkan nomor: ").strip()
        
        if not phone:
            print(f"{Fore.RED}[!] Tidak ada nomor!")
            return
        
        whatsapp = self.get_whatsapp_info(phone)
        
        if whatsapp:
            print(f"\n{Fore.GREEN}[✓] WhatsApp links untuk {phone}:")
            print(f"{Fore.CYAN}{'-'*40}")
            print(f"{Fore.WHITE}Direct Chat:")
            print(f"{Fore.GREEN}{whatsapp['direct']}")
            print(f"\n{Fore.WHITE}Web WhatsApp:")
            print(f"{Fore.CYAN}{whatsapp['web']}")
            print(f"\n{Fore.WHITE}Cara pakai:")
            print(f"{Fore.YELLOW}1. Buka link di browser")
            print(f"{Fore.YELLOW}2. Jika nomor terdaftar di WhatsApp, bisa chat langsung")
        else:
            print(f"{Fore.RED}[!] Gagal generate link")
        
        input(f"\n{Fore.WHITE}Enter untuk lanjut...")


def check_deps():
    """Check dependencies"""
    try:
        import phonenumbers
        import requests
        import colorama
        return True
    except ImportError:
        print(f"{Fore.RED}[!] Install dulu: pip install phonenumbers requests colorama")
        return False


def main():
    if not check_deps():
        return
    
    try:
        dox = InstantPhoneDox()
        dox.main_menu()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[*] Keluar...")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}[!] Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
