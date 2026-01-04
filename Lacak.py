#!/usr/bin/env python3
# SIMPLE PHONE LOCATOR - Kartu & Lokasi Langsung
# Install: pip install phonenumbers

import phonenumbers
from phonenumbers import carrier, geocoder
import re
import os
import sys
from colorama import init, Fore, Style

init(autoreset=True)

class SimplePhoneLocator:
    def __init__(self):
        self.clear_screen()
        self.show_banner()
    
    def clear_screen(self):
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def show_banner(self):
        banner = f"""{Fore.GREEN}
╔══════════════════════════════════╗
║   SIMPLE PHONE LOCATOR v1.0      ║
║   Kartu • Lokasi • Maps Link     ║
╚══════════════════════════════════╝
{Style.RESET_ALL}"""
        print(banner)
    
    def get_carrier(self, parsed):
        """Ambil operator kartu"""
        try:
            op = carrier.name_for_number(parsed, "en")
            if op:
                # Terjemahkan ke Indonesia
                translations = {
                    'Telkomsel': 'Telkomsel',
                    'XL': 'XL Axiata',
                    'Indosat': 'Indosat',
                    'Axis': 'AXIS',
                    'Three': '3 (Tri)',
                    'Smartfren': 'Smartfren',
                    'Maxis': 'Maxis (Malaysia)',
                    'Celcom': 'Celcom (Malaysia)',
                    'Digi': 'Digi (Malaysia)',
                    'U Mobile': 'U Mobile (Malaysia)',
                    'Singtel': 'Singtel (Singapore)',
                    'StarHub': 'StarHub (Singapore)',
                    'M1': 'M1 (Singapore)'
                }
                for eng, indo in translations.items():
                    if eng in op:
                        return indo
                return op
            return "Unknown"
        except:
            return "Unknown"
    
    def get_location(self, parsed):
        """Ambil lokasi dari nomor"""
        try:
            loc = geocoder.description_for_number(parsed, "en")
            if loc:
                # Sederhanakan lokasi
                if 'Indonesia' in loc:
                    return loc.replace('Indonesia', 'ID')
                elif 'Malaysia' in loc:
                    return loc.replace('Malaysia', 'MY')
                elif 'Singapore' in loc:
                    return loc.replace('Singapore', 'SG')
                return loc
            return "Unknown"
        except:
            return "Unknown"
    
    def generate_maps_link(self, location):
        """Generate Google Maps link dari lokasi"""
        if location == "Unknown":
            return None
        
        # Clean location
        clean_loc = re.sub(r'[^a-zA-Z0-9 ,]', '', location)
        
        # Google Maps URL
        maps_url = f"https://www.google.com/maps/search/?api=1&query={clean_loc.replace(' ', '+')}"
        return maps_url
    
    def process_number(self, phone):
        """Proses nomor telepon"""
        try:
            # Validasi nomor
            clean_num = re.sub(r'[^0-9+]', '', phone)
            
            # Coba parse
            parsed = None
            for country in ['ID', 'MY', 'SG', 'US', 'GB']:
                try:
                    parsed = phonenumbers.parse(clean_num, country)
                    if phonenumbers.is_valid_number(parsed):
                        break
                except:
                    continue
            
            if not parsed or not phonenumbers.is_valid_number(parsed):
                print(f"{Fore.RED}[!] Nomor tidak valid")
                return None
            
            # Format nomor
            intl_format = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            
            # Dapatkan info
            operator = self.get_carrier(parsed)
            location = self.get_location(parsed)
            maps_link = self.generate_maps_link(location)
            
            return {
                'number': intl_format,
                'operator': operator,
                'location': location,
                'maps_link': maps_link
            }
            
        except Exception as e:
            print(f"{Fore.RED}[!] Error: {e}")
            return None
    
    def show_result(self, result):
        """Tampilkan hasil sederhana"""
        print(f"\n{Fore.CYAN}{'='*40}")
        print(f"{Fore.YELLOW}HASIL PENCARIAN:")
        print(f"{Fore.CYAN}{'='*40}")
        
        print(f"{Fore.WHITE}📱 Nomor: {Fore.GREEN}{result['number']}")
        print(f"{Fore.WHITE}📶 Kartu: {result['operator']}")
        print(f"{Fore.WHITE}📍 Lokasi: {result['location']}")
        
        if result['maps_link']:
            print(f"{Fore.WHITE}🗺️ Maps: {Fore.BLUE}{result['maps_link']}")
            print(f"\n{Fore.YELLOW}[*] Copy link di atas ke browser")
        else:
            print(f"{Fore.YELLOW}[!] Maps link tidak tersedia")
        
        print(f"\n{Fore.CYAN}{'='*40}")
    
    def main_loop(self):
        """Loop utama"""
        while True:
            self.clear_screen()
            self.show_banner()
            
            print(f"\n{Fore.YELLOW}[*] Masukkan nomor telepon:")
            print(f"{Fore.WHITE}Contoh: 08123456789, +60123456789")
            
            phone = input(f"\n{Fore.GREEN}[?] Nomor: ").strip()
            
            if not phone:
                print(f"{Fore.RED}[!] Masukkan nomor!")
                input(f"\n{Fore.WHITE}Enter untuk lanjut...")
                continue
            
            if phone.lower() == 'exit':
                break
            
            # Proses nomor
            result = self.process_number(phone)
            
            if result:
                self.show_result(result)
            else:
                print(f"{Fore.RED}[!] Gagal memproses nomor")
            
            # Tanya lagi
            print(f"\n{Fore.YELLOW}[*] Cari nomor lain? (y/n)")
            lagi = input(f"{Fore.GREEN}[?] Pilihan: ").strip().lower()
            
            if lagi != 'y':
                print(f"{Fore.YELLOW}[*] Keluar...")
                break
    
    def quick_test(self):
        """Test cepat beberapa nomor"""
        test_numbers = [
            '+628123456789',    # Indonesia - Telkomsel
            '+60123456789',     # Malaysia - Maxis
            '+6591234567',      # Singapore - Singtel
            '+628156789012',    # Indonesia - Indosat
            '+60192345678',     # Malaysia - Celcom
        ]
        
        print(f"\n{Fore.YELLOW}[*] TEST CEPAT:")
        print(f"{Fore.CYAN}{'='*40}")
        
        for num in test_numbers:
            result = self.process_number(num)
            if result:
                print(f"\n{Fore.WHITE}📱 {result['number']}")
                print(f"   📶 {result['operator']}")
                print(f"   📍 {result['location']}")
                if result['maps_link']:
                    print(f"   🗺️ {result['maps_link'][:50]}...")
        
        print(f"\n{Fore.CYAN}{'='*40}")
        input(f"\n{Fore.WHITE}Enter untuk lanjut...")


def main():
    # Cek dependency
    try:
        import phonenumbers
    except ImportError:
        print(f"{Fore.RED}[!] Install: pip install phonenumbers")
        return
    
    try:
        locator = SimplePhoneLocator()
        
        # Menu sederhana
        print(f"\n{Fore.CYAN}{'='*30}")
        print(f"{Fore.YELLOW}1. {Fore.WHITE}Cari Lokasi Nomor")
        print(f"{Fore.YELLOW}2. {Fore.WHITE}Test Cepat")
        print(f"{Fore.YELLOW}3. {Fore.WHITE}Keluar")
        print(f"{Fore.CYAN}{'='*30}")
        
        choice = input(f"{Fore.GREEN}[?] Pilih: ").strip()
        
        if choice == "1":
            locator.main_loop()
        elif choice == "2":
            locator.quick_test()
            locator.main_loop()
        elif choice == "3":
            print(f"{Fore.YELLOW}[*] Keluar...")
        else:
            print(f"{Fore.RED}[!] Pilihan salah")
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[*] Keluar...")
    except Exception as e:
        print(f"{Fore.RED}[!] Error: {e}")


if __name__ == "__main__":
    main()
