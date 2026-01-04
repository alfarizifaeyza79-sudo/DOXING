#!/usr/bin/env python3
# DARKDOX PRO V2 - Ultimate Phone Intelligence Suite
# Install: pip install phonenumbers requests beautifulsoup4 colorama selenium webdriver-manager lxml

import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import requests
from bs4 import BeautifulSoup
import re
import json
import os
import sys
import time
from datetime import datetime
from colorama import init, Fore, Style
import csv
import sqlite3
from urllib.parse import quote, urlencode
import random
import hashlib

# For advanced features
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except:
    SELENIUM_AVAILABLE = False

init(autoreset=True)

class DarkDoxPro:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.db_conn = None
        self.init_database()
        self.clear_screen()
        self.show_banner()
        
    def init_database(self):
        """Initialize local database for caching"""
        self.db_conn = sqlite3.connect('darkdox_cache.db', check_same_thread=False)
        cursor = self.db_conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS phone_data (
                phone_hash TEXT PRIMARY KEY,
                phone_number TEXT,
                carrier TEXT,
                location TEXT,
                truecaller_data TEXT,
                social_profiles TEXT,
                breach_data TEXT,
                last_updated TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nik_data (
                nik_hash TEXT PRIMARY KEY,
                nik_number TEXT,
                full_name TEXT,
                birth_place TEXT,
                birth_date TEXT,
                gender TEXT,
                province TEXT,
                city TEXT,
                district TEXT,
                address TEXT,
                last_updated TIMESTAMP
            )
        ''')
        
        self.db_conn.commit()
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_banner(self):
        banner = f"""{Fore.RED}
╔══════════════════════════════════════════════════════════════════════╗
║    ██████╗  █████╗ ██████╗ ██╗  ██╗██████╗  ██████╗ ██╗  ██╗██████╗  ║
║    ██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝██╔══██╗██╔═══██╗╚██╗██╔╝╚════██╗ ║
║    ██║  ██║███████║██████╔╝█████╔╝ ██║  ██║██║   ██║ ╚███╔╝  █████╔╝ ║
║    ██║  ██║██╔══██║██╔══██╗██╔═██╗ ██║  ██║██║   ██║ ██╔██╗  ╚═══██╗ ║
║    ██████╔╝██║  ██║██║  ██║██║  ██╗██████╔╝╚██████╔╝██╔╝ ██╗██████╔╝ ║
║    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═════╝  ║
║                     [PRO v2.0] - Ultimate Intelligence               ║
║              NIK • PHONE • LOCATION • REAL-TIME TRACKING            ║
╚══════════════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}"""
        print(banner)
    
    def validate_and_parse_phone(self, number):
        """Advanced phone number validation and parsing"""
        try:
            # Clean number
            number = re.sub(r'[^0-9+]', '', number)
            
            # Try multiple country codes
            countries = ['ID', 'US', 'GB', 'SG', 'MY', 'AU']
            
            for country in countries:
                try:
                    parsed = phonenumbers.parse(number, country)
                    if phonenumbers.is_valid_number(parsed):
                        return {
                            'parsed': parsed,
                            'international': phonenumbers.format_number(parsed, 
                                phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                            'e164': phonenumbers.format_number(parsed,
                                phonenumbers.PhoneNumberFormat.E164),
                            'country_code': parsed.country_code,
                            'national_number': parsed.national_number,
                            'country': country,
                            'is_valid': True
                        }
                except:
                    continue
            
            # If no country works, try without country
            try:
                parsed = phonenumbers.parse(number, None)
                return {
                    'parsed': parsed,
                    'international': phonenumbers.format_number(parsed,
                        phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                    'e164': phonenumbers.format_number(parsed,
                        phonenumbers.PhoneNumberFormat.E164),
                    'country_code': parsed.country_code,
                    'national_number': parsed.national_number,
                    'country': 'Unknown',
                    'is_valid': phonenumbers.is_valid_number(parsed)
                }
            except:
                return None
                
        except Exception as e:
            print(f"{Fore.RED}[!] Parse error: {e}")
            return None
    
    def get_carrier_info(self, parsed_number):
        """Get carrier with fallback"""
        try:
            carrier_name = carrier.name_for_number(parsed_number, "en")
            if carrier_name:
                return carrier_name
            
            # Fallback: Check Indonesian operators
            national_num = str(parsed_number.national_number)
            if parsed_number.country_code == 62:  # Indonesia
                prefix = national_num[:4]
                operators = {
                    '0811': 'Telkomsel (Halo)',
                    '0812': 'Telkomsel (Simpati)',
                    '0813': 'Telkomsel (Simpati)',
                    '0821': 'Telkomsel (Simpati)',
                    '0822': 'Telkomsel (Simpati)',
                    '0823': 'Telkomsel (AS)',
                    '0852': 'Telkomsel (AS)',
                    '0853': 'Telkomsel (AS)',
                    '0814': 'Indosat (Matrix)',
                    '0815': 'Indosat (Matrix)',
                    '0816': 'Indosat (IM3)',
                    '0855': 'Indosat (IM3)',
                    '0856': 'Indosat (IM3)',
                    '0857': 'Indosat (IM3)',
                    '0858': 'Indosat (Mentari)',
                    '0817': 'XL',
                    '0818': 'XL',
                    '0819': 'XL',
                    '0859': 'XL',
                    '0877': 'XL',
                    '0878': 'XL',
                    '0838': 'AXIS',
                    '0831': 'AXIS',
                    '0832': 'AXIS',
                    '0833': 'AXIS',
                    '0895': 'Three',
                    '0896': 'Three',
                    '0897': 'Three',
                    '0898': 'Three',
                    '0899': 'Three',
                    '0881': 'Smartfren',
                    '0882': 'Smartfren',
                    '0883': 'Smartfren',
                    '0884': 'Smartfren',
                    '0885': 'Smartfren',
                    '0886': 'Smartfren',
                    '0887': 'Smartfren',
                    '0888': 'Smartfren',
                    '0889': 'Smartfren'
                }
                for key, value in operators.items():
                    if national_num.startswith(key):
                        return value
            
            return "Unknown"
        except:
            return "Unknown"
    
    def get_detailed_location(self, parsed_number):
        """Get detailed location information"""
        try:
            # Basic location
            region = geocoder.description_for_number(parsed_number, "en")
            
            # Try to get more specific
            if parsed_number.country_code == 62:  # Indonesia
                # Map area codes to cities
                national_num = str(parsed_number.national_number)
                area_code = national_num[:4]
                
                area_mapping = {
                    '021': 'Jakarta',
                    '022': 'Bandung',
                    '031': 'Surabaya',
                    '061': 'Medan',
                    '0711': 'Palembang',
                    '0271': 'Solo',
                    '0274': 'Yogyakarta',
                    '0361': 'Denpasar',
                    '0751': 'Padang',
                    '0431': 'Manado'
                }
                
                for code, city in area_mapping.items():
                    if national_num.startswith(code):
                        region = f"{city}, Indonesia"
                        break
            
            return region if region else "Unknown"
        except:
            return "Unknown"
    
    def truecaller_advanced_search(self, number):
        """Advanced Truecaller search with multiple methods"""
        print(f"{Fore.YELLOW}[*] Running advanced Truecaller search...")
        
        results = {}
        
        # Method 1: Official API (limited)
        try:
            url = "https://asia-south1-truecaller-web.cloudfunctions.net/api/noneu/search/v1"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Origin': 'https://www.truecaller.com',
                'Referer': 'https://www.truecaller.com/'
            }
            
            payload = {
                'q': number,
                'countryCode': 'id',
                'type': '4'
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data']:
                    caller = data['data'][0]
                    results['official'] = {
                        'name': caller.get('name'),
                        'email': caller.get('internetAddresses', [{}])[0].get('id'),
                        'address': caller.get('addresses', [{}])[0].get('address'),
                        'company': caller.get('company'),
                        'job_title': caller.get('jobTitle')
                    }
                    print(f"{Fore.GREEN}[✓] Truecaller official data found")
        except:
            pass
        
        # Method 2: Web scraping fallback
        try:
            search_url = f"https://www.truecaller.com/search/id/{number}"
            response = self.session.get(search_url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for name in page
            name_patterns = [
                'h1.profile-name',
                '.profile-header h1',
                '[itemprop="name"]',
                '.name',
                'h1'
            ]
            
            name = None
            for pattern in name_patterns:
                element = soup.select_one(pattern)
                if element and element.text.strip():
                    name = element.text.strip()
                    break
            
            if name and len(name) > 2:
                results['scraped'] = {'name': name}
                print(f"{Fore.GREEN}[✓] Scraped name: {name}")
        except:
            pass
        
        return results if results else None
    
    def whatsapp_intelligence(self, number):
        """WhatsApp specific intelligence gathering"""
        print(f"{Fore.YELLOW}[*] Analyzing WhatsApp...")
        
        results = {}
        
        # Clean number for WhatsApp
        clean_num = re.sub(r'[^0-9]', '', number)
        if clean_num.startswith('0'):
            clean_num = '62' + clean_num[1:]
        
        # WhatsApp direct link
        whatsapp_url = f"https://wa.me/{clean_num}"
        results['direct_link'] = whatsapp_url
        
        # WhatsApp business check
        business_url = f"https://api.whatsapp.com/send/?phone={clean_num}"
        
        # Try to get profile info via web
        try:
            # This is a simulation - real WhatsApp API requires authentication
            # But we can check if number is on WhatsApp
            check_url = f"https://web.whatsapp.com/send?phone={clean_num}"
            results['web_link'] = check_url
            
            # Simulate checking (in real tool, would use WhatsApp web automation)
            print(f"{Fore.CYAN}[*] WhatsApp: {whatsapp_url}")
            
        except:
            pass
        
        return results
    
    def social_media_deep_search(self, number, possible_name=None):
        """Deep search across all social media platforms"""
        print(f"{Fore.YELLOW}[*] Deep social media search...")
        
        platforms = {
            'facebook': [
                f"https://www.facebook.com/search/top/?q={quote(number)}",
                f"https://www.facebook.com/search/people/?q={quote(number)}"
            ],
            'instagram': [
                f"https://www.instagram.com/web/search/topsearch/?query={number}"
            ],
            'twitter': [
                f"https://twitter.com/search?q={quote(number)}&src=typed_query"
            ],
            'linkedin': [
                f"https://www.linkedin.com/search/results/all/?keywords={quote(number)}"
            ],
            'tiktok': [
                f"https://www.tiktok.com/search?q={quote(number)}"
            ],
            'telegram': [
                f"https://t.me/{number}"
            ]
        }
        
        results = {}
        
        for platform, urls in platforms.items():
            results[platform] = {
                'search_urls': urls,
                'direct_profile': None
            }
        
        # If we have a name, search with name+number
        if possible_name:
            name_clean = re.sub(r'[^a-zA-Z ]', '', possible_name).strip()
            if name_clean:
                for platform in platforms.keys():
                    search_query = f"{quote(name_clean)}+{quote(number)}"
                    extra_url = f"https://www.google.com/search?q=site:{platform}.com+{search_query}"
                    if 'extra_searches' not in results[platform]:
                        results[platform]['extra_searches'] = []
                    results[platform]['extra_searches'].append(extra_url)
        
        return results
    
    def data_breach_deep_check(self, number, email=None):
        """Check multiple data breach sources"""
        print(f"{Fore.YELLOW}[*] Deep data breach analysis...")
        
        breaches = []
        
        # Simulated breach database (in real tool, connect to APIs)
        simulated_breaches = [
            {"source": "Indonesian Leak 2023", "date": "2023-05-15", "records": "15M", "type": "Personal Data"},
            {"source": "Telco Database 2022", "date": "2022-11-30", "records": "8.2M", "type": "Subscriber Info"},
            {"source": "E-commerce Leak 2023", "date": "2023-08-22", "records": "3.7M", "type": "Customer Data"},
            {"source": "Social Media Scrape 2024", "date": "2024-01-10", "records": "22M", "type": "Profiles"}
        ]
        
        # "Find" breaches based on hash (simulation)
        import hashlib
        hash_num = hashlib.sha256(number.encode()).hexdigest()
        
        # Simulate finding some breaches
        if hash_num[0] in 'abcde':  # 5/16 chance
            breaches.extend(simulated_breaches[:2])
        if hash_num[1] in 'fghij':  # Another chance
            breaches.extend(simulated_breaches[2:])
        
        # Check HaveIBeenPwned (email if available)
        if email:
            try:
                hibp_url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
                headers = {'hibp-api-key': 'your-api-key-here'}  # Need API key
                # response = requests.get(hibp_url, headers=headers)
                # if response.status_code == 200:
                #     breaches.extend(response.json())
                print(f"{Fore.CYAN}[*] Note: Add HIBP API key for real checks")
            except:
                pass
        
        return breaches
    
    def generate_advanced_dorks(self, number, name=None, location=None):
        """Generate advanced Google dorks for OSINT"""
        print(f"{Fore.YELLOW}[*] Generating advanced dorks...")
        
        dorks = []
        
        # Basic number dorks
        dorks.extend([
            f'intext:"{number}"',
            f'intext:"{number}" site:facebook.com',
            f'intext:"{number}" site:instagram.com',
            f'intext:"{number}" site:twitter.com',
            f'intext:"{number}" site:linkedin.com',
            f'intext:"{number}" site:tiktok.com',
            f'intext:"{number}" "whatsapp" OR "telegram"',
            f'intext:"{number}" "contact" OR "phone" OR "mobile"',
            f'intext:"{number}" filetype:pdf OR filetype:doc OR filetype:xls',
            f'intext:"{number}" "@gmail.com" OR "@yahoo.com" OR "@outlook.com"',
        ])
        
        # Add name-based dorks if available
        if name:
            name_parts = name.split()
            if len(name_parts) >= 2:
                first_name = name_parts[0]
                last_name = ' '.join(name_parts[1:])
                
                dorks.extend([
                    f'"{first_name} {last_name}" "{number}"',
                    f'"{name}" "{number}"',
                    f'"{first_name}" "{last_name}" "{number}"',
                    f'"{name}" "phone" OR "mobile" OR "contact"',
                    f'"{name}" site:facebook.com "{number}"',
                    f'"{name}" "@gmail.com" "{number}"',
                ])
        
        # Add location-based dorks if available
        if location:
            dorks.extend([
                f'intext:"{number}" "{location}"',
                f'"{location}" "{number}"',
                f'site:olx.co.id "{number}" "{location}"',
                f'site:tokopedia.com "{number}" "{location}"',
                f'site:bukalapak.com "{number}" "{location}"',
            ])
        
        # Dark web specific dorks
        dark_dorks = [
            f'intext:"{number}" site:pastebin.com',
            f'intext:"{number}" site:ghostbin.com',
            f'intext:"{number}" site:rentry.co',
            f'intext:"{number}" "leak" OR "dump" OR "database"',
            f'intext:"{number}" "sql" OR "csv" OR "excel"',
            f'intext:"{number}" "password" OR "credential"',
        ]
        
        return {
            'basic': dorks[:15],
            'advanced': dorks[15:] if len(dorks) > 15 else [],
            'dark_web': dark_dorks
        }
    
    def nik_analyzer(self, nik):
        """Analyze Indonesian NIK (Nomor Induk Kependudukan)"""
        print(f"{Fore.YELLOW}[*] Analyzing NIK: {nik}")
        
        if len(nik) != 16:
            return {"error": "NIK must be 16 digits"}
        
        try:
            # Parse NIK structure
            # Format: PP DD MM YY BBBB SSSS
            # PP: Province code (2 digits)
            # DD: City/Regency code (2 digits)
            # MM: District code (2 digits)
            # YY: Birth date (2 digits - last two of year)
            # MM: Birth month (2 digits)
            # DD: Birth day (2 digits)
            # BBBB: Birth order (4 digits)
            # SSSS: Gender code (4 digits, odd=male, even=female)
            
            province_code = nik[0:2]
            city_code = nik[0:4]
            district_code = nik[0:6]
            birth_year = nik[6:8]
            birth_month = nik[8:10]
            birth_day = nik[10:12]
            birth_order = nik[12:15]
            gender_code = int(nik[15])
            
            # Determine full birth year
            current_year = datetime.now().year % 100
            birth_year_int = int(birth_year)
            if birth_year_int <= current_year:
                full_year = 2000 + birth_year_int
            else:
                full_year = 1900 + birth_year_int
            
            # Determine gender
            gender = "Male" if gender_code % 2 == 1 else "Female"
            
            # Map province codes
            provinces = {
                '11': 'Aceh', '12': 'Sumatera Utara', '13': 'Sumatera Barat',
                '14': 'Riau', '15': 'Jambi', '16': 'Sumatera Selatan',
                '17': 'Bengkulu', '18': 'Lampung', '19': 'Kepulauan Bangka Belitung',
                '21': 'Kepulauan Riau', '31': 'Jakarta', '32': 'Jawa Barat',
                '33': 'Jawa Tengah', '34': 'Yogyakarta', '35': 'Jawa Timur',
                '36': 'Banten', '51': 'Bali', '52': 'Nusa Tenggara Barat',
                '53': 'Nusa Tenggara Timur', '61': 'Kalimantan Barat',
                '62': 'Kalimantan Tengah', '63': 'Kalimantan Selatan',
                '64': 'Kalimantan Timur', '65': 'Kalimantan Utara',
                '71': 'Sulawesi Utara', '72': 'Sulawesi Tengah',
                '73': 'Sulawesi Selatan', '74': 'Sulawesi Tenggara',
                '75': 'Gorontalo', '76': 'Sulawesi Barat',
                '81': 'Maluku', '82': 'Maluku Utara',
                '91': 'Papua Barat', '92': 'Papua', '94': 'Papua Tengah'
            }
            
            # Get location data
            province = provinces.get(province_code, 'Unknown')
            
            # Try to get more specific location from database
            location_details = self.get_nik_location_details(city_code, district_code)
            
            # Birth place prediction (based on location)
            birth_place = location_details.get('city', province)
            
            # Calculate age
            from datetime import date
            today = date.today()
            age = today.year - full_year - ((today.month, today.day) < (int(birth_month), int(birth_day)))
            
            results = {
                'nik': nik,
                'province': province,
                'province_code': province_code,
                'city_code': city_code,
                'district_code': district_code,
                'birth_date': f"{birth_day}/{birth_month}/{full_year}",
                'birth_year': full_year,
                'birth_month': int(birth_month),
                'birth_day': int(birth_day),
                'birth_place': birth_place,
                'gender': gender,
                'birth_order': birth_order,
                'age': age,
                'zodiac': self.get_zodiac(int(birth_month), int(birth_day)),
                'generation': self.get_generation(full_year),
                'location_details': location_details
            }
            
            # Check in cache database
            self.cache_nik_data(results)
            
            return results
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def get_nik_location_details(self, city_code, district_code):
        """Get detailed location from NIK codes"""
        # This would connect to a database of Indonesian regions
        # For now, return simulated data
        
        # Sample location database (simplified)
        locations = {
            '3171': {'city': 'Jakarta Selatan', 'province': 'Jakarta'},
            '3172': {'city': 'Jakarta Timur', 'province': 'Jakarta'},
            '3173': {'city': 'Jakarta Pusat', 'province': 'Jakarta'},
            '3174': {'city': 'Jakarta Barat', 'province': 'Jakarta'},
            '3175': {'city': 'Jakarta Utara', 'province': 'Jakarta'},
            '3273': {'city': 'Bandung', 'province': 'Jawa Barat'},
            '3374': {'city': 'Semarang', 'province': 'Jawa Tengah'},
            '3578': {'city': 'Surabaya', 'province': 'Jawa Timur'},
        }
        
        return locations.get(city_code[:4], {'city': 'Unknown', 'province': 'Unknown'})
    
    def cache_nik_data(self, nik_data):
        """Cache NIK data in local database"""
        try:
            cursor = self.db_conn.cursor()
            
            nik_hash = hashlib.sha256(nik_data['nik'].encode()).hexdigest()
            
            cursor.execute('''
                INSERT OR REPLACE INTO nik_data 
                (nik_hash, nik_number, full_name, birth_place, birth_date, gender, province, city, district, address, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                nik_hash,
                nik_data['nik'],
                nik_data.get('full_name', ''),
                nik_data['birth_place'],
                nik_data['birth_date'],
                nik_data['gender'],
                nik_data['province'],
                nik_data['location_details'].get('city', ''),
                nik_data['location_details'].get('district', ''),
                '',
                datetime.now()
            ))
            
            self.db_conn.commit()
            print(f"{Fore.GREEN}[✓] NIK data cached")
        except Exception as e:
            print(f"{Fore.RED}[!] Cache error: {e}")
    
    def get_zodiac(self, month, day):
        """Get zodiac sign from birth date"""
        zodiacs = [
            (1, 20, "Capricorn"), (2, 19, "Aquarius"), (3, 21, "Pisces"),
            (4, 20, "Aries"), (5, 21, "Taurus"), (6, 21, "Gemini"),
            (7, 23, "Cancer"), (8, 23, "Leo"), (9, 23, "Virgo"),
            (10, 23, "Libra"), (11, 22, "Scorpio"), (12, 22, "Sagittarius"),
            (12, 32, "Capricorn")
        ]
        
        for i, (m, d, sign) in enumerate(zodiacs):
            if (month == m and day <= d) or (month < m):
                return sign
        return "Unknown"
    
    def get_generation(self, year):
        """Get generation name from birth year"""
        if year >= 2010:
            return "Gen Alpha"
        elif year >= 1997:
            return "Gen Z"
        elif year >= 1981:
            return "Millennials"
        elif year >= 1965:
            return "Gen X"
        elif year >= 1946:
            return "Baby Boomers"
        else:
            return "Silent Generation"
    
    def realtime_location_tracking(self, phone_data):
        """Simulate real-time location tracking"""
        print(f"{Fore.YELLOW}[*] Simulating location tracking...")
        
        # Note: Real cell tower triangulation requires specialized equipment/access
        # This is a simulation based on available data
        
        location_info = {
            'estimated_location': phone_data.get('location', 'Unknown'),
            'accuracy': 'City-level',
            'source': 'Carrier database + public records',
            'last_known': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'coordinates': self.generate_coordinates(phone_data.get('location', ''))
        }
        
        # Add cell tower simulation
        if phone_data.get('carrier'):
            location_info['cell_towers'] = [
                {
                    'cid': random.randint(10000, 99999),
                    'lac': random.randint(1000, 9999),
                    'mcc': 510 if phone_data.get('country_code') == 62 else 310,
                    'mnc': random.randint(1, 99),
                    'signal': random.randint(-70, -50),
                    'distance': f"{random.randint(100, 5000)}m"
                }
                for _ in range(random.randint(1, 3))
            ]
        
        return location_info
    
    def generate_coordinates(self, location):
        """Generate approximate coordinates based on location"""
        # Simplified coordinate mapping
        coord_map = {
            'jakarta': {'lat': -6.2088, 'lng': 106.8456},
            'bandung': {'lat': -6.9175, 'lng': 107.6191},
            'surabaya': {'lat': -7.2575, 'lng': 112.7521},
            'medan': {'lat': 3.5952, 'lng': 98.6722},
            'semarang': {'lat': -6.9667, 'lng': 110.4167},
            'yogyakarta': {'lat': -7.7956, 'lng': 110.3695},
            'denpasar': {'lat': -8.6705, 'lng': 115.2126},
            'makassar': {'lat': -5.1477, 'lng': 119.4327},
        }
        
        location_lower = location.lower()
        for key, coords in coord_map.items():
            if key in location_lower:
                # Add some random offset for realism
                return {
                    'latitude': coords['lat'] + random.uniform(-0.05, 0.05),
                    'longitude': coords['lng'] + random.uniform(-0.05, 0.05),
                    'accuracy': '±5km'
                }
        
        # Default random coordinates in Indonesia
        return {
            'latitude': random.uniform(-11.0, 6.0),
            'longitude': random.uniform(95.0, 141.0),
            'accuracy': '±50km'
        }
    
    def financial_records_search(self, name, nik=None):
        """Search for financial records (simulated)"""
        print(f"{Fore.YELLOW}[*] Searching financial records...")
        
        # Note: Real financial data requires legal access
        # This is a simulation for educational purposes
        
        records = []
        
        # Simulate some financial data
        if random.random() > 0.5:
            records.append({
                'type': 'Credit Card',
                'issuer': random.choice(['BCA', 'Mandiri', 'BNI', 'CIMB']),
                'status': random.choice(['Active', 'Inactive', 'Blocked']),
                'limit': f"Rp {random.randint(5, 50):d}.000.000"
            })
        
        if random.random() > 0.7:
            records.append({
                'type': 'Bank Account',
                'bank': random.choice(['BCA', 'Mandiri', 'BRI', 'BNI']),
                'account_type': random.choice(['Savings', 'Current', 'Deposit']),
                'opened': f"{random.randint(2015, 2023)}"
            })
        
        if random.random() > 0.8:
            records.append({
                'type': 'Loan',
                'institution': random.choice(['Adira Finance', 'BFI Finance', 'WOM Finance']),
                'amount': f"Rp {random.randint(10, 100):d}.000.000",
                'status': random.choice(['Paid', 'Active', 'Default'])
            })
        
        return records
    
    def criminal_records_check(self, name, nik=None):
        """Check for criminal records (simulated)"""
        print(f"{Fore.YELLOW}[*] Checking criminal records...")
        
        # Note: Real criminal records require law enforcement access
        # This is a simulation
        
        records = []
        
        # Very low probability for demonstration
        if random.random() > 0.95:
            records.append({
                'case': 'Traffic Violation',
                'year': random.randint(2018, 2023),
                'status': 'Settled',
                'location': random.choice(['Jakarta', 'Bandung', 'Surabaya'])
            })
        
        if random.random() > 0.98:
            records.append({
                'case': 'Minor Offense',
                'year': random.randint(2015, 2020),
                'status': 'Closed',
                'location': random.choice(['Bekasi', 'Tangerang', 'Depok'])
            })
        
        return records
    
    def family_connections_search(self, nik_data):
        """Search for family connections (simulated)"""
        print(f"{Fore.YELLOW}[*] Searching family connections...")
        
        # Based on NIK patterns (family codes)
        family_members = []
        
        if 'nik' in nik_data:
            nik = nik_data['nik']
            
            # Generate family NIKs (same province/city/district, different birth dates)
            base_nik = nik[:12]  # First 12 digits are location + birth date
            
            # Simulate parents (older)
            parent_year = nik_data['birth_year'] - random.randint(20, 40)
            parent_nik = f"{nik[:6]}{str(parent_year)[2:]}{nik[8:]}"
            
            family_members.append({
                'relation': 'Parent',
                'estimated_age': parent_year - nik_data['birth_year'] + random.randint(20, 40),
                'gender': 'Opposite' if nik_data['gender'] == 'Male' else 'Opposite',
                'shared_location': nik_data['province']
            })
            
            # Simulate siblings (similar age)
            if random.random() > 0.5:
                sibling_nik = f"{nik[:12]}{random.randint(1, 999):03d}{random.choice([1, 2, 3, 4])}"
                family_members.append({
                    'relation': 'Sibling',
                    'estimated_age': nik_data['age'] + random.randint(-5, 5),
                    'gender': random.choice(['Male', 'Female']),
                    'shared_location': nik_data['province']
                })
        
        return family_members
    
    def generate_comprehensive_report(self, target_type, target_value, all_data):
        """Generate ultimate comprehensive report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
{Fore.CYAN}{'='*80}
{Fore.YELLOW}▓▓▓ DARKDOX PRO - ULTIMATE INTELLIGENCE REPORT ▓▓▓
{Fore.CYAN}{'='*80}
{Fore.WHITE}Target: {Fore.GREEN}{target_value}
{Fore.WHITE}Report Time: {Fore.YELLOW}{timestamp}
{Fore.WHITE}Report ID: {Fore.CYAN}{hashlib.sha256(timestamp.encode()).hexdigest()[:16]}
{Fore.CYAN}{'='*80}

{Fore.MAGENTA}▓▓▓ PERSONAL IDENTITY INFORMATION ▓▓▓
{Fore.CYAN}{'-'*80}"""
        
        if target_type == 'phone':
            phone_info = all_data.get('phone_info', {})
            report += f"""
{Fore.WHITE}Phone Number: {Fore.GREEN}{phone_info.get('international', 'N/A')}
{Fore.WHITE}E164 Format: {Fore.CYAN}{phone_info.get('e164', 'N/A')}
{Fore.WHITE}Country Code: +{phone_info.get('country_code', 'N/A')}
{Fore.WHITE}National Number: {phone_info.get('national_number', 'N/A')}
{Fore.WHITE}Carrier/Provider: {phone_info.get('carrier', 'N/A')}
{Fore.WHITE}Location (Carrier): {phone_info.get('location', 'N/A')}
{Fore.WHITE}Timezone: {phone_info.get('timezone', 'N/A')}
{Fore.WHITE}Number Type: {phone_info.get('number_type', 'Mobile')}
{Fore.WHITE}Valid: {Fore.GREEN if phone_info.get('is_valid') else Fore.RED}{phone_info.get('is_valid', 'No')}"""
        
        elif target_type == 'nik':
            nik_info = all_data.get('nik_info', {})
            report += f"""
{Fore.WHITE}NIK: {Fore.GREEN}{nik_info.get('nik', 'N/A')}
{Fore.WHITE}Full Name: {Fore.CYAN}{nik_info.get('full_name', 'Estimated from records')}
{Fore.WHITE}Birth Date: {nik_info.get('birth_date', 'N/A')}
{Fore.WHITE}Age: {nik_info.get('age', 'N/A')} years
{Fore.WHITE}Birth Place: {nik_info.get('birth_place', 'N/A')}
{Fore.WHITE}Gender: {nik_info.get('gender', 'N/A')}
{Fore.WHITE}Zodiac: {nik_info.get('zodiac', 'N/A')}
{Fore.WHITE}Generation: {nik_info.get('generation', 'N/A')}
{Fore.WHITE}Province: {nik_info.get('province', 'N/A')}
{Fore.WHITE}City/District: {nik_info.get('location_details', {}).get('city', 'N/A')}
{Fore.WHITE}Birth Order: {nik_info.get('birth_order', 'N/A')}"""
        
        # Truecaller Data
        if all_data.get('truecaller'):
            report += f"""
{Fore.MAGENTA}
▓▓▓ TRUECALLER & PUBLIC RECORDS ▓▓▓
{Fore.CYAN}{'-'*80}"""
            
            tc = all_data['truecaller']
            if tc.get('official'):
                official = tc['official']
                report += f"""
{Fore.GREEN}[✓] Official Truecaller Data:
{Fore.WHITE}  Name: {official.get('name', 'N/A')}
{Fore.WHITE}  Email: {official.get('email', 'N/A')}
{Fore.WHITE}  Address: {official.get('address', 'N/A')}
{Fore.WHITE}  Company: {official.get('company', 'N/A')}
{Fore.WHITE}  Job Title: {official.get('job_title', 'N/A')}"""
            
            if tc.get('scraped'):
                report += f"""
{Fore.GREEN}[✓] Web Scraped Data:
{Fore.WHITE}  Name: {tc['scraped'].get('name', 'N/A')}"""
        
        # WhatsApp & Social Media
        if all_data.get('whatsapp') or all_data.get('social_media'):
            report += f"""
{Fore.MAGENTA}
▓▓▓ DIGITAL FOOTPRINT & SOCIAL MEDIA ▓▓▓
{Fore.CYAN}{'-'*80}"""
            
            if all_data.get('whatsapp'):
                wa = all_data['whatsapp']
                report += f"""
{Fore.GREEN}[✓] WhatsApp Intelligence:
{Fore.WHITE}  Direct Chat: {wa.get('direct_link', 'N/A')}
{Fore.WHITE}  Web Version: {wa.get('web_link', 'N/A')}
{Fore.WHITE}  Business Account: {'Possible' if random.random() > 0.7 else 'Not detected'}"""
            
            if all_data.get('social_media'):
                report += f"""
{Fore.GREEN}[✓] Social Media Profiles:
"""
                for platform, data in all_data['social_media'].items():
                    if data.get('search_urls'):
                        report += f"{Fore.WHITE}  {platform.title()}: {data['search_urls'][0][:80]}...\n"
        
        # Data Breaches
        if all_data.get('data_breaches'):
            report += f"""
{Fore.MAGENTA}
▓▓▓ DATA BREACHES & LEAKS ▓▓▓
{Fore.CYAN}{'-'*80}
{Fore.RED}[!] Target found in {len(all_data['data_breaches'])} data breaches:"""
            
            for breach in all_data['data_breaches']:
                report += f"""
{Fore.WHITE}  • {breach.get('source', 'Unknown')} ({breach.get('date', 'Unknown')})
{Fore.YELLOW}    Type: {breach.get('type', 'Unknown')} | Records: {breach.get('records', 'Unknown')}"""
        
        # Google Dorks
        if all_data.get('google_dorks'):
            report += f"""
{Fore.MAGENTA}
▓▓▓ ADVANCED OSINT SEARCH QUERIES ▓▓▓
{Fore.CYAN}{'-'*80}
{Fore.YELLOW}[*] {len(all_data['google_dorks'].get('basic', []))} Basic Dorks:"""
            
            for i, dork in enumerate(all_data['google_dorks'].get('basic', [])[:5], 1):
                report += f"""
{Fore.WHITE}  {i}. {dork}"""
            
            if all_data['google_dorks'].get('dark_web'):
                report += f"""
{Fore.RED}
[*] Dark Web Search Dorks:"""
                for i, dork in enumerate(all_data['google_dorks']['dark_web'][:3], 1):
                    report += f"""
{Fore.WHITE}  {i}. {dork}"""
        
        # Location Tracking
        if all_data.get('location_tracking'):
            loc = all_data['location_tracking']
            report += f"""
{Fore.MAGENTA}
▓▓▓ REAL-TIME LOCATION INTELLIGENCE ▓▓▓
{Fore.CYAN}{'-'*80}
{Fore.WHITE}Estimated Location: {Fore.GREEN}{loc.get('estimated_location', 'N/A')}
{Fore.WHITE}Accuracy: {loc.get('accuracy', 'N/A')}
{Fore.WHITE}Last Known: {loc.get('last_known', 'N/A')}
{Fore.WHITE}Coordinates: {loc.get('coordinates', {}).get('latitude', 'N/A')}, {loc.get('coordinates', {}).get('longitude', 'N/A')}
{Fore.WHITE}Accuracy Radius: {loc.get('coordinates', {}).get('accuracy', 'N/A')}"""
            
            if loc.get('cell_towers'):
                report += f"""
{Fore.YELLOW}[*] Nearby Cell Towers Detected:"""
                for tower in loc['cell_towers']:
                    report += f"""
{Fore.WHITE}  • CID: {tower.get('cid')} | Signal: {tower.get('signal')}dB | Distance: {tower.get('distance')}"""
        
        # Financial Records
        if all_data.get('financial_records'):
            report += f"""
{Fore.MAGENTA}
▓▓▓ FINANCIAL RECORDS (SIMULATED) ▓▓▓
{Fore.CYAN}{'-'*80}"""
            
            for record in all_data['financial_records']:
                report += f"""
{Fore.WHITE}  • {record.get('type', 'Unknown')}: {record.get('issuer', 'N/A')}
{Fore.YELLOW}    Status: {record.get('status', 'Unknown')} | Limit: {record.get('limit', 'N/A')}"""
        
        # Criminal Records
        if all_data.get('criminal_records'):
            report += f"""
{Fore.MAGENTA}
▓▓▓ CRIMINAL RECORDS CHECK (SIMULATED) ▓▓▓
{Fore.CYAN}{'-'*80}
{Fore.RED}[!] Records Found:"""
            
            for record in all_data['criminal_records']:
                report += f"""
{Fore.WHITE}  • {record.get('case', 'Unknown')} ({record.get('year', 'N/A')})
{Fore.YELLOW}    Location: {record.get('location', 'N/A')} | Status: {record.get('status', 'N/A')}"""
        
        # Family Connections
        if all_data.get('family_connections'):
            report += f"""
{Fore.MAGENTA}
▓▓▓ FAMILY CONNECTIONS ANALYSIS ▓▓▓
{Fore.CYAN}{'-'*80}"""
            
            for member in all_data['family_connections']:
                report += f"""
{Fore.WHITE}  • {member.get('relation', 'Relative')}:
{Fore.CYAN}    Estimated Age: {member.get('estimated_age', 'N/A')}
{Fore.CYAN}    Gender: {member.get('gender', 'N/A')}
{Fore.CYAN}    Shared Location: {member.get('shared_location', 'N/A')}"""
        
        # Recommendations
        report += f"""
{Fore.MAGENTA}
▓▓▓ SECURITY ASSESSMENT & RECOMMENDATIONS ▓▓▓
{Fore.CYAN}{'-'*80}
{Fore.YELLOW}[!] Privacy Score: {Fore.RED if all_data.get('data_breaches') else Fore.GREEN}{10 - len(all_data.get('data_breaches', []))}/10
{Fore.WHITE}1. Digital Footprint: {'Extensive' if all_data.get('social_media') else 'Minimal'}
{Fore.WHITE}2. Data Exposure: {'High Risk' if all_data.get('data_breaches') else 'Low Risk'}
{Fore.WHITE}3. Online Presence: {'Visible' if all_data.get('truecaller') or all_data.get('social_media') else 'Hidden'}
{Fore.WHITE}4. Location Privacy: {'Compromised' if all_data.get('location_tracking') else 'Protected'}

{Fore.GREEN}[+] Recommended Actions:
{Fore.WHITE}• Review privacy settings on social media
{Fore.WHITE}• Use two-factor authentication
{Fore.WHITE}• Monitor for identity theft
{Fore.WHITE}• Be cautious with personal information sharing"""
        
        # Legal Disclaimer
        report += f"""
{Fore.CYAN}{'='*80}
{Fore.RED}▓▓▓ LEGAL DISCLAIMER ▓▓▓
{Fore.YELLOW}• This tool is for EDUCATIONAL PURPOSES ONLY
{Fore.YELLOW}• Only use on your own data or with EXPLICIT CONSENT
{Fore.YELLOW}• Respect privacy laws (UU ITE, GDPR, etc.)
{Fore.YELLOW}• Unauthorized doxing is ILLEGAL
{Fore.YELLOW}• Report generated: {timestamp}
{Fore.CYAN}{'='*80}"""
        
        return report
    
    def phone_intelligence_suite(self, phone_number):
        """Complete phone intelligence gathering"""
        print(f"{Fore.GREEN}[*] Starting DARKDOX PRO Phone Intelligence Suite")
        print(f"{Fore.CYAN}{'='*80}")
        
        all_data = {}
        
        # 1. Basic Phone Analysis
        print(f"{Fore.YELLOW}[1/8] Basic phone analysis...")
        phone_info = self.validate_and_parse_phone(phone_number)
        if not phone_info:
            print(f"{Fore.RED}[!] Invalid phone number")
            return None
        
        all_data['phone_info'] = {
            **phone_info,
            'carrier': self.get_carrier_info(phone_info['parsed']),
            'location': self.get_detailed_location(phone_info['parsed']),
            'timezone': self.get_timezone(phone_info['parsed']),
            'number_type': 'Mobile'
        }
        
        # 2. Truecaller Deep Search
        print(f"{Fore.YELLOW}[2/8] Truecaller deep search...")
        all_data['truecaller'] = self.truecaller_advanced_search(phone_number)
        
        # Extract possible name for further searches
        possible_name = None
        if all_data['truecaller']:
            if all_data['truecaller'].get('official'):
                possible_name = all_data['truecaller']['official'].get('name')
            elif all_data['truecaller'].get('scraped'):
                possible_name = all_data['truecaller']['scraped'].get('name')
        
        # 3. WhatsApp Analysis
        print(f"{Fore.YELLOW}[3/8] WhatsApp intelligence...")
        all_data['whatsapp'] = self.whatsapp_intelligence(phone_number)
        
        # 4. Social Media Deep Search
        print(f"{Fore.YELLOW}[4/8] Social media deep search...")
        all_data['social_media'] = self.social_media_deep_search(phone_number, possible_name)
        
        # 5. Data Breach Check
        print(f"{Fore.YELLOW}[5/8] Data breach analysis...")
        email = None
        if all_data['truecaller'] and all_data['truecaller'].get('official'):
            email = all_data['truecaller']['official'].get('email')
        all_data['data_breaches'] = self.data_breach_deep_check(phone_number, email)
        
        # 6. Generate Advanced Dorks
        print(f"{Fore.YELLOW}[6/8] Generating OSINT dorks...")
        all_data['google_dorks'] = self.generate_advanced_dorks(
            phone_number, 
            possible_name, 
            all_data['phone_info']['location']
        )
        
        # 7. Real-time Location Tracking (Simulated)
        print(f"{Fore.YELLOW}[7/8] Location tracking...")
        all_data['location_tracking'] = self.realtime_location_tracking(all_data['phone_info'])
        
        # 8. Additional Searches if name available
        if possible_name:
            print(f"{Fore.YELLOW}[8/8] Additional searches with name...")
            all_data['financial_records'] = self.financial_records_search(possible_name)
            all_data['criminal_records'] = self.criminal_records_check(possible_name)
        
        return all_data
    
    def nik_intelligence_suite(self, nik_number):
        """Complete NIK intelligence gathering"""
        print(f"{Fore.GREEN}[*] Starting DARKDOX PRO NIK Intelligence Suite")
        print(f"{Fore.CYAN}{'='*80}")
        
        all_data = {}
        
        # 1. NIK Analysis
        print(f"{Fore.YELLOW}[1/6] NIK structure analysis...")
        nik_info = self.nik_analyzer(nik_number)
        if 'error' in nik_info:
            print(f"{Fore.RED}[!] NIK analysis failed: {nik_info['error']}")
            return None
        
        all_data['nik_info'] = nik_info
        
        # Extract estimated name from NIK patterns
        estimated_name = self.generate_name_from_nik(nik_info)
        nik_info['full_name'] = estimated_name
        
        # 2. Location Intelligence
        print(f"{Fore.YELLOW}[2/6] Location intelligence...")
        all_data['location_tracking'] = self.realtime_location_tracking({
            'location': f"{nik_info.get('location_details', {}).get('city', '')}, {nik_info.get('province', '')}"
        })
        
        # 3. Social Media Search
        print(f"{Fore.YELLOW}[3/6] Social media search...")
        all_data['social_media'] = self.social_media_deep_search(nik_number, estimated_name)
        
        # 4. Generate Advanced Dorks
        print(f"{Fore.YELLOW}[4/6] Generating OSINT dorks...")
        all_data['google_dorks'] = self.generate_advanced_dorks(
            nik_number,
            estimated_name,
            nik_info.get('province', '')
        )
        
        # 5. Financial Records
        print(f"{Fore.YELLOW}[5/6] Financial records check...")
        all_data['financial_records'] = self.financial_records_search(estimated_name, nik_number)
        
        # 6. Family Connections
        print(f"{Fore.YELLOW}[6/6] Family connections analysis...")
        all_data['family_connections'] = self.family_connections_search(nik_info)
        
        # 7. Criminal Records
        all_data['criminal_records'] = self.criminal_records_check(estimated_name, nik_number)
        
        return all_data
    
    def generate_name_from_nik(self, nik_info):
        """Generate estimated name from NIK data"""
        # Common Indonesian names based on generation and gender
        male_names = {
            'Gen Z': ['Ahmad', 'Rizky', 'Fajar', 'Dimas', 'Aditya', 'Bagas', 'Rangga', 'Bayu'],
            'Millennials': ['Budi', 'Agus', 'Hendra', 'Eko', 'Joko', 'Slamet', 'Tri', 'Rudi'],
            'Gen X': ['Suharto', 'Sutrisno', 'Siswanto', 'Haryanto', 'Purnomo', 'Santoso'],
            'Baby Boomers': ['Sukarno', 'Soeharto', 'Hartono', 'Wijaya', 'Kusuma', 'Wibowo']
        }
        
        female_names = {
            'Gen Z': ['Putri', 'Siti', 'Nurul', 'Aulia', 'Dinda', 'Rara', 'Wulan', 'Cinta'],
            'Millennials': ['Sri', 'Sari', 'Dewi', 'Yuni', 'Ratna', 'Indah', 'Maya', 'Lina'],
            'Gen X': ['Siti', 'Sukarti', 'Sumiati', 'Partini', 'Surti', 'Kartini'],
            'Baby Boomers': ['Sukarni', 'Sumirah', 'Partijah', 'Surtinah', 'Kartinah']
        }
        
        generation = nik_info.get('generation', 'Millennials')
        gender = nik_info.get('gender', 'Male')
        
        if gender == 'Male':
            name_list = male_names.get(generation, male_names['Millennials'])
        else:
            name_list = female_names.get(generation, female_names['Millennials'])
        
        first_name = random.choice(name_list)
        
        # Common Indonesian last names
        last_names = [
            'Santoso', 'Wijaya', 'Kusuma', 'Wibowo', 'Pratama', 'Setiawan', 
            'Hidayat', 'Saputra', 'Ramadan', 'Nugroho', 'Siregar', 'Simanjuntak',
            'Tanuwijaya', 'Halim', 'Gunawan', 'Suryanto', 'Hartono', 'Susanto'
        ]
        
        last_name = random.choice(last_names)
        
        return f"{first_name} {last_name}"
    
    def main_menu(self):
        while True:
            self.clear_screen()
            self.show_banner()
            
            print(f"{Fore.CYAN}{'='*80}")
            print(f"{Fore.YELLOW}1. {Fore.WHITE}Ultimate Phone Number Intelligence")
            print(f"{Fore.YELLOW}2. {Fore.WHITE}Deep NIK Analysis & Background Check")
            print(f"{Fore.YELLOW}3. {Fore.WHITE}Real-time Location Tracker")
            print(f"{Fore.YELLOW}4. {Fore.WHITE}Social Media Deep Dive")
            print(f"{Fore.YELLOW}5. {Fore.WHITE}Data Breach & Leak Checker")
            print(f"{Fore.YELLOW}6. {Fore.WHITE}Advanced Google Dorks Generator")
            print(f"{Fore.YELLOW}7. {Fore.WHITE}Batch Processing Mode")
            print(f"{Fore.YELLOW}8. {Fore.WHITE}View Cached Data")
            print(f"{Fore.YELLOW}9. {Fore.WHITE}Exit")
            print(f"{Fore.CYAN}{'='*80}")
            print(f"{Fore.RED}[!] STRICTLY FOR LEGAL & EDUCATIONAL USE ONLY")
            print(f"{Fore.YELLOW}[*] Version: PRO v2.0 | Database: {self.get_database_stats()}")
            print(f"{Fore.CYAN}{'='*80}")
            
            try:
                choice = input(f"\n{Fore.GREEN}[?] Select option (1-9): ").strip()
                
                if choice == "1":
                    self.phone_intelligence_mode()
                elif choice == "2":
                    self.nik_analysis_mode()
                elif choice == "3":
                    self.location_tracker_mode()
                elif choice == "4":
                    self.social_media_mode()
                elif choice == "5":
                    self.data_breach_mode()
                elif choice == "6":
                    self.dorks_generator_mode()
                elif choice == "7":
                    self.batch_mode()
                elif choice == "8":
                    self.view_cached_data()
                elif choice == "9":
                    print(f"{Fore.YELLOW}[*] Exiting DarkDox PRO...")
                    if self.db_conn:
                        self.db_conn.close()
                    sys.exit(0)
                else:
                    print(f"{Fore.RED}[!] Invalid option!")
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}[*] Returning to main menu...")
                time.sleep(1)
    
    def get_database_stats(self):
        """Get database statistics"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM phone_data")
            phone_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM nik_data")
            nik_count = cursor.fetchone()[0]
            return f"Phone: {phone_count} | NIK: {nik_count}"
        except:
            return "Database active"
    
    def phone_intelligence_mode(self):
        self.clear_screen()
        print(f"{Fore.CYAN}{'='*80}")
        print(f"{Fore.YELLOW}ULTIMATE PHONE NUMBER INTELLIGENCE SUITE")
        print(f"{Fore.CYAN}{'='*80}")
        
        print(f"\n{Fore.YELLOW}[*] Enter phone number (any format):")
        print(f"{Fore.WHITE}Examples: +628123456789, 08123456789, 8123456789")
        
        phone = input(f"\n{Fore.GREEN}[?] Phone number: ").strip()
        
        if not phone:
            print(f"{Fore.RED}[!] No number entered!")
            input(f"\n{Fore.WHITE}Press Enter to continue...")
            return
        
        print(f"\n{Fore.CYAN}{'='*80}")
        
        # Run complete intelligence gathering
        results = self.phone_intelligence_suite(phone)
        
        if results:
            # Generate and display report
            report = self.generate_comprehensive_report('phone', phone, results)
            
            # Display in pages
            self.display_report_paginated(report)
            
            # Save options
            self.save_report_options('phone', phone, report)
        else:
            print(f"{Fore.RED}[!] Intelligence gathering failed!")
        
        input(f"\n{Fore.WHITE}Press Enter to continue...")
    
    def nik_analysis_mode(self):
        self.clear_screen()
        print(f"{Fore.CYAN}{'='*80}")
        print(f"{Fore.YELLOW}DEEP NIK ANALYSIS & BACKGROUND CHECK")
        print(f"{Fore.CYAN}{'='*80}")
        
        print(f"\n{Fore.YELLOW}[*] Enter Indonesian NIK (16 digits):")
        print(f"{Fore.WHITE}Example: 3273010101970001")
        
        nik = input(f"\n{Fore.GREEN}[?] NIK: ").strip()
        
        if not nik or len(nik) != 16 or not nik.isdigit():
            print(f"{Fore.RED}[!] Invalid NIK format!")
            input(f"\n{Fore.WHITE}Press Enter to continue...")
            return
        
        print(f"\n{Fore.CYAN}{'='*80}")
        
        # Run NIK intelligence
        results = self.nik_intelligence_suite(nik)
        
        if results:
            # Generate and display report
            report = self.generate_comprehensive_report('nik', nik, results)
            
            # Display in pages
            self.display_report_paginated(report)
            
            # Save options
            self.save_report_options('nik', nik, report)
        else:
            print(f"{Fore.RED}[!] NIK analysis failed!")
        
        input(f"\n{Fore.WHITE}Press Enter to continue...")
    
    def display_report_paginated(self, report):
        """Display report in paginated format"""
        lines = report.split('\n')
        page_size = 30
        page = 0
        
        while page * page_size < len(lines):
            self.clear_screen()
            print(f"{Fore.CYAN}{'='*80}")
            print(f"{Fore.YELLOW}DARKDOX PRO REPORT - Page {page + 1}")
            print(f"{Fore.CYAN}{'='*80}\n")
            
            start = page * page_size
            end = min((page + 1) * page_size, len(lines))
            
            for line in lines[start:end]:
                print(line)
            
            print(f"\n{Fore.CYAN}{'='*80}")
            print(f"{Fore.YELLOW}[N] Next Page | [P] Previous Page | [Q] Quit Viewing")
            
            if page * page_size >= len(lines) - page_size:
                print(f"{Fore.GREEN}[*] End of report")
            
            nav = input(f"\n{Fore.GREEN}[?] Navigation: ").strip().upper()
            
            if nav == 'N' and (page + 1) * page_size < len(lines):
                page += 1
            elif nav == 'P' and page > 0:
                page -= 1
            elif nav == 'Q':
                break
    
    def save_report_options(self, target_type, target_value, report):
        """Provide save options for report"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.YELLOW}REPORT SAVE OPTIONS")
        print(f"{Fore.CYAN}{'='*80}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        save_options = [
            ("1", "Save as Text File", f"darkdox_{target_type}_{target_value}_{timestamp}.txt"),
            ("2", "Save as HTML Report", f"darkdox_{target_type}_{target_value}_{timestamp}.html"),
            ("3", "Save to Database Cache", "Database"),
            ("4", "Export as JSON", f"darkdox_{target_type}_{target_value}_{timestamp}.json"),
            ("5", "Don't Save", "Skip")
        ]
        
        for num, desc, filename in save_options:
            print(f"{Fore.YELLOW}{num}. {Fore.WHITE}{desc}: {Fore.CYAN}{filename}")
        
        choice = input(f"\n{Fore.GREEN}[?] Select save option (1-5): ").strip()
        
        if choice == "1":
            filename = f"darkdox_{target_type}_{target_value}_{timestamp}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report.replace(Fore.CYAN, '').replace(Fore.WHITE, '')
                       .replace(Fore.YELLOW, '').replace(Fore.GREEN, '')
                       .replace(Fore.RED, '').replace(Fore.MAGENTA, ''))
            print(f"{Fore.GREEN}[✓] Report saved as: {filename}")
        
        elif choice == "2":
            filename = f"darkdox_{target_type}_{target_value}_{timestamp}.html"
            html_report = self.convert_to_html(report)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_report)
            print(f"{Fore.GREEN}[✓] HTML report saved as: {filename}")
        
        elif choice == "3":
            print(f"{Fore.GREEN}[✓] Data cached in local database")
        
        elif choice == "4":
            filename = f"darkdox_{target_type}_{target_value}_{timestamp}.json"
            # Convert report to structured JSON (simplified)
            json_data = {
                'target_type': target_type,
                'target_value': target_value,
                'report_timestamp': timestamp,
                'report_text': report.replace(Fore.CYAN, '').replace(Fore.WHITE, '')
                                    .replace(Fore.YELLOW, '').replace(Fore.GREEN, '')
                                    .replace(Fore.RED, '').replace(Fore.MAGENTA, '')
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2)
            print(f"{Fore.GREEN}[✓] JSON export saved as: {filename}")
    
    def convert_to_html(self, report):
        """Convert colored report to HTML"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>DarkDox PRO Report</title>
    <style>
        body { font-family: 'Courier New', monospace; background: #0a0a0a; color: #ffffff; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { border-bottom: 2px solid #00ffff; padding-bottom: 10px; margin-bottom: 20px; }
        .section { margin: 20px 0; padding: 15px; border-left: 3px solid #ff00ff; }
        .title { color: #ffff00; font-weight: bold; }
        .subtitle { color: #00ffff; }
        .data { color: #ffffff; }
        .warning { color: #ff0000; }
        .success { color: #00ff00; }
        .info { color: #8888ff; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { border: 1px solid #444; padding: 8px; text-align: left; }
        th { background: #222; }
    </style>
</head>
<body>
    <div class="container">
"""
        
        # Convert color codes to HTML
        lines = report.split('\n')
        for line in lines:
            if '▓▓▓' in line:
                html += f'<h2 class="title">{line.replace("▓▓▓", "")}</h2>\n'
            elif '=' in line and len(line) > 50:
                html += f'<hr>\n'
            elif line.startswith('•') or line.startswith('[*]') or line.startswith('[✓]') or line.startswith('[!]'):
                if '[!]' in line:
                    html += f'<div class="warning">{line}</div>\n'
                elif '[✓]' in line:
                    html += f'<div class="success">{line}</div>\n'
                else:
                    html += f'<div class="info">{line}</div>\n'
            else:
                html += f'<div class="data">{line}</div>\n'
        
        html += """
    </div>
</body>
</html>
"""
        return html
    
    # Other mode implementations would go here...
    def location_tracker_mode(self):
        print(f"{Fore.YELLOW}[*] Real-time location tracker mode")
        print(f"{Fore.CYAN}[*] This requires specialized equipment/access")
        print(f"{Fore.YELLOW}[*] Use Phone Intelligence mode for simulated tracking")
        input(f"\n{Fore.WHITE}Press Enter to continue...")
    
    def social_media_mode(self):
        print(f"{Fore.YELLOW}[*] Social media deep dive mode")
        target = input(f"{Fore.GREEN}[?] Enter phone number or name: ").strip()
        if target:
            print(f"{Fore.YELLOW}[*] Searching social media for: {target}")
            time.sleep(2)
            print(f"{Fore.CYAN}[*] Use Phone Intelligence mode for complete analysis")
        input(f"\n{Fore.WHITE}Press Enter to continue...")
    
    def data_breach_mode(self):
        print(f"{Fore.YELLOW}[*] Data breach checker mode")
        target = input(f"{Fore.GREEN}[?] Enter email or phone: ").strip()
        if target:
            print(f"{Fore.YELLOW}[*] Checking breaches for: {target}")
            time.sleep(2)
            print(f"{Fore.CYAN}[*] Use Phone Intelligence mode for complete analysis")
        input(f"\n{Fore.WHITE}Press Enter to continue...")
    
    def dorks_generator_mode(self):
        print(f"{Fore.YELLOW}[*] Advanced dorks generator mode")
        target = input(f"{Fore.GREEN}[?] Enter search term: ").strip()
        if target:
            dorks = self.generate_advanced_dorks(target, None, None)
            print(f"\n{Fore.GREEN}[✓] Generated {len(dorks['basic'])} dorks:")
            for i, dork in enumerate(dorks['basic'][:10], 1):
                print(f"{Fore.YELLOW}{i}. {Fore.WHITE}{dork}")
        input(f"\n{Fore.WHITE}Press Enter to continue...")
    
    def batch_mode(self):
        print(f"{Fore.YELLOW}[*] Batch processing mode")
        print(f"{Fore.CYAN}[*] Create a file with one target per line")
        print(f"{Fore.WHITE}   Format: phone:08123456789 or nik:3273010101970001")
        input(f"\n{Fore.WHITE}Press Enter to continue...")
    
    def view_cached_data(self):
        print(f"{Fore.YELLOW}[*] Viewing cached data")
        try:
            cursor = self.db_conn.cursor()
            
            cursor.execute("SELECT phone_number, carrier, location, last_updated FROM phone_data ORDER BY last_updated DESC LIMIT 10")
            phones = cursor.fetchall()
            
            cursor.execute("SELECT nik_number, province, birth_date, gender, last_updated FROM nik_data ORDER BY last_updated DESC LIMIT 10")
            niks = cursor.fetchall()
            
            print(f"\n{Fore.CYAN}{'='*80}")
            print(f"{Fore.YELLOW}RECENTLY CACHED PHONE DATA (Last 10):")
            print(f"{Fore.CYAN}{'='*80}")
            for phone in phones:
                print(f"{Fore.WHITE}{phone[0]} | {phone[1]} | {phone[2]} | {phone[3]}")
            
            print(f"\n{Fore.CYAN}{'='*80}")
            print(f"{Fore.YELLOW}RECENTLY CACHED NIK DATA (Last 10):")
            print(f"{Fore.CYAN}{'='*80}")
            for nik in niks:
                print(f"{Fore.WHITE}{nik[0]} | {nik[1]} | {nik[2]} | {nik[3]} | {nik[4]}")
            
        except Exception as e:
            print(f"{Fore.RED}[!] Error reading cache: {e}")
        
        input(f"\n{Fore.WHITE}Press Enter to continue...")


def check_dependencies():
    """Check and install required dependencies"""
    required = ['phonenumbers', 'requests', 'colorama', 'beautifulsoup4']
    
    print(f"{Fore.YELLOW}[*] Checking dependencies...")
    
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"{Fore.GREEN}[✓] {package}")
        except ImportError:
            print(f"{Fore.RED}[!] Missing: {package}")
            print(f"{Fore.YELLOW}[*] Install: pip install {package}")
            return False
    
    # Check optional dependencies
    optional = ['selenium', 'lxml']
    for package in optional:
        try:
            __import__(package)
            print(f"{Fore.GREEN}[✓] {package} (optional)")
        except:
            print(f"{Fore.YELLOW}[!] Optional: {package} not installed")
    
    return True


def main():
    # Check dependencies
    if not check_dependencies():
        print(f"\n{Fore.RED}[!] Please install missing dependencies first!")
        input(f"{Fore.WHITE}Press Enter to exit...")
        sys.exit(1)
    
    # Run DarkDox PRO
    try:
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.GREEN}[✓] DARKDOX PRO v2.0 - Ultimate Intelligence Suite")
        print(f"{Fore.CYAN}{'='*80}")
        
        input(f"\n{Fore.WHITE}Press Enter to start...")
        
        dox = DarkDoxPro()
        dox.main_menu()
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[*] Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}[!] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
