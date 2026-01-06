import aiohttp
import json
import random
import string
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

try:
    from transliterate import translit
    TRANSLITERATE_AVAILABLE = True
except ImportError:
    TRANSLITERATE_AVAILABLE = False

def _simple_transliterate_uk_to_lat(text: str) -> str:
    """Проста транслітерація української на латиницю (fallback)"""
    uk_to_lat = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g', 'д': 'd', 'е': 'e', 'є': 'ie',
        'ж': 'zh', 'з': 'z', 'и': 'y', 'і': 'i', 'ї': 'i', 'й': 'i', 'к': 'k', 'л': 'l',
        'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ь': '', 'ю': 'iu',
        'я': 'ia', 'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'H', 'Ґ': 'G', 'Д': 'D', 'Е': 'E',
        'Є': 'Ie', 'Ж': 'Zh', 'З': 'Z', 'И': 'Y', 'І': 'I', 'Ї': 'I', 'Й': 'I', 'К': 'K',
        'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T',
        'У': 'U', 'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch', 'Ю': 'Iu',
        'Я': 'Ia'
    }
    result = ''
    for char in text:
        result += uk_to_lat.get(char, char)
    return result

class GraphService:
    # Base URL for Microsoft Graph API
    # Can be overridden for sovereign clouds (e.g., Government Cloud: graph.microsoft.us)
    BASE_URL = "https://graph.microsoft.com/v1.0"
    
    def __init__(self, config):
        self.client_id = config.APP_ID
        self.client_secret = config.APP_PASSWORD
        self.tenant_id = config.TENANT_ID
        # Якщо запускаємо локально без тенанта, використовуємо common (хоча краще мати ID)
        if not self.tenant_id:
            self.tenant_id = "common"
        
        # Allow custom BASE_URL for sovereign clouds
        self.base_url = getattr(config, 'GRAPH_API_BASE_URL', None) or self.BASE_URL
        
        # SKU ID ліцензії для призначення новим користувачам
        # Microsoft 365 Business Basic: f30db892-07e9-47e9-837c-80727f46fd3d
        self.default_license_sku_id = getattr(config, 'DEFAULT_LICENSE_SKU_ID', None) or ""
        if self.default_license_sku_id:
            print(f"📋 Використовується ліцензія за замовчуванням: {self.default_license_sku_id}")
        else:
            print(f"⚠️ DEFAULT_LICENSE_SKU_ID не налаштовано - ліцензії не будуть призначатися автоматично")
            print(f"   Додайте в .env.local.user: DEFAULT_LICENSE_SKU_ID=f30db892-07e9-47e9-837c-80727f46fd3d") 

    async def _get_access_token(self, session: aiohttp.ClientSession) -> str:
        """Отримує токен доступу (Application Permissions)"""
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials"
        }
        
        async with session.post(url, data=payload) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("access_token")
            else:
                text = await response.text()
                raise Exception(f"Auth Error: {text}")

    def generate_password(self) -> str:
        """Генерує складний пароль"""
        chars = string.ascii_letters + string.digits + "!@#$%"
        return ''.join(random.choice(chars) for _ in range(12)) + "Aa1!"

    async def create_user(self, data: dict) -> Dict[str, Any]:
        """Асинхронне створення користувача"""
        
        async with aiohttp.ClientSession() as session:
            try:
                # 1. Авторизація
                token = await self._get_access_token(session)
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                # --- ВИПРАВЛЕННЯ ТУТ ---
                # Ми прибираємо складний запит і просто пишемо твій реальний домен.
                # Це 100% спрацює.
                domain = "Markivskyi.onmicrosoft.com" 
                # -----------------------

                # 3. Підготовка даних
                nickname = data.get('emailNickname', 'user').replace(" ", "").lower()
                
                # Формуємо правильний UPN: user@Markivskyi.onmicrosoft.com
                upn = f"{nickname}@{domain}"
                password = self.generate_password()

                user_payload = {
                    "accountEnabled": True,
                    "displayName": f"{data.get('firstName')} {data.get('lastName')}",
                    "mailNickname": nickname,
                    "userPrincipalName": upn,
                    "passwordProfile": {
                        "forceChangePasswordNextSignIn": True,
                        "password": password
                    },
                    "jobTitle": data.get('jobTitle'),
                    "department": data.get('department'),
                    "usageLocation": "US"
                }

                # 4. Створення користувача
                create_url = "https://graph.microsoft.com/v1.0/users"
                async with session.post(create_url, headers=headers, json=user_payload) as response:
                    if response.status == 201:
                        user_data = await response.json()
                        user_id = user_data.get('id')
                        
                        if not user_id:
                            return {"success": False, "error": "Користувач створений, але не вдалося отримати user_id"}
                        
                        print(f"✅ Користувач створено: {user_id} ({upn})")
                        
                        result = {
                            "success": True,
                            "email": upn,
                            "password": password,
                            "user_id": user_id
                        }
                        
                        # 5. Виводимо всі доступні ліцензії для діагностики
                        print(f"\n📋 === СПИСОК ВСІХ ЛІЦЕНЗІЙ В ОРГАНІЗАЦІЇ ===")
                        all_licenses_info = await self.get_all_licenses()
                        if all_licenses_info.get("success"):
                            all_skus = all_licenses_info.get("licenses", [])
                            print(f"Знайдено {len(all_skus)} типів ліцензій:\n")
                            for sku in all_skus:
                                sku_id = sku.get('skuId', 'N/A')
                                sku_part_number = sku.get('skuPartNumber', 'N/A')
                                prepaid = sku.get('prepaidUnits', {})
                                enabled = prepaid.get('enabled', 0)
                                consumed = sku.get('consumedUnits', 0)
                                available = enabled - consumed
                                
                                status = "✅ ДОСТУПНО" if available > 0 else "❌ НЕМАЄ"
                                print(f"  {status} | {sku_part_number}")
                                print(f"         SKU ID: {sku_id}")
                                print(f"         Доступно: {available} з {enabled} (використано: {consumed})")
                                print()
                        else:
                            print(f"⚠️ Не вдалося отримати список ліцензій: {all_licenses_info.get('error')}")
                        print(f"📋 === КІНЕЦЬ СПИСКУ ЛІЦЕНЗІЙ ===\n")
                        
                        # 6. Призначаємо ліцензію, якщо вказано
                        license_sku_id = self.default_license_sku_id
                        if license_sku_id and license_sku_id.strip():
                            print(f"📋 Перевіряю доступність ліцензії {license_sku_id}...")
                            
                            # Спочатку перевіряємо, чи є доступні ліцензії
                            licenses_check = await self.get_available_licenses()
                            if licenses_check.get("success"):
                                available_licenses = licenses_check.get("licenses", [])
                                # Перевіряємо, чи є наша ліцензія в списку доступних
                                license_found = any(sku.get('skuId') == license_sku_id for sku in available_licenses)
                                
                                if not license_found:
                                    # Перевіряємо всі ліцензії (навіть якщо немає доступних)
                                    all_licenses = await self.get_all_licenses()
                                    if all_licenses.get("success"):
                                        all_skus = all_licenses.get("licenses", [])
                                        license_exists = any(sku.get('skuId') == license_sku_id for sku in all_skus)
                                        
                                        if not license_exists:
                                            error_msg = f"Ліцензія з SKU ID '{license_sku_id}' не знайдена в організації"
                                            print(f"❌ {error_msg}")
                                            result["license_assigned"] = False
                                            result["license_error"] = error_msg
                                        else:
                                            error_msg = f"Ліцензія '{license_sku_id}' існує, але немає доступних ліцензій"
                                            print(f"⚠️ {error_msg}")
                                            result["license_assigned"] = False
                                            result["license_error"] = error_msg
                                    else:
                                        # Не вдалося перевірити ліцензії, але спробуємо призначити
                                        print(f"⚠️ Не вдалося перевірити ліцензії, спробую призначити...")
                                        license_result = await self.assign_license_to_user(user_id, license_sku_id)
                                        
                                        if license_result.get("success"):
                                            result["license_assigned"] = True
                                            result["license_info"] = license_result.get("user", {})
                                        else:
                                            result["license_assigned"] = False
                                            result["license_error"] = license_result.get("error", "Невідома помилка")
                                else:
                                    # Ліцензія доступна, призначаємо
                                    print(f"✅ Ліцензія доступна, призначаю...")
                                    license_result = await self.assign_license_to_user(user_id, license_sku_id)
                                    
                                    if license_result.get("success"):
                                        result["license_assigned"] = True
                                        result["license_info"] = license_result.get("user", {})
                                        print(f"✅ Ліцензію успішно призначено користувачу")
                                    else:
                                        result["license_assigned"] = False
                                        result["license_error"] = license_result.get("error", "Невідома помилка")
                                        print(f"⚠️ Користувач створений, але ліцензію не вдалося призначити: {result['license_error']}")
                            else:
                                # Не вдалося перевірити ліцензії, але спробуємо призначити
                                print(f"⚠️ Не вдалося перевірити ліцензії: {licenses_check.get('error')}, спробую призначити...")
                                license_result = await self.assign_license_to_user(user_id, license_sku_id)
                                
                                if license_result.get("success"):
                                    result["license_assigned"] = True
                                    result["license_info"] = license_result.get("user", {})
                                else:
                                    result["license_assigned"] = False
                                    result["license_error"] = license_result.get("error", "Невідома помилка")
                        else:
                            print(f"⚠️ DEFAULT_LICENSE_SKU_ID не налаштовано, ліцензію не призначено")
                            result["license_assigned"] = False
                        
                        return result
                    else:
                        error_body = await response.json()
                        error_msg = error_body.get('error', {}).get('message', await response.text())
                        return {"success": False, "error": error_msg}

            except Exception as e:
                return {"success": False, "error": str(e)}

    async def get_available_licenses(self) -> Dict[str, Any]:
        """Отримує список доступних ліцензій в організації"""
        async with aiohttp.ClientSession() as session:
            try:
                token = await self._get_access_token(session)
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                # Отримуємо всі доступні ліцензії
                licenses_url = "https://graph.microsoft.com/v1.0/subscribedSkus"
                
                async with session.get(licenses_url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        skus = data.get('value', [])
                        
                        # Фільтруємо тільки ті, що мають доступні ліцензії
                        available_skus = [
                            sku for sku in skus 
                            if sku.get('consumedUnits', 0) < sku.get('prepaidUnits', {}).get('enabled', 0)
                        ]
                        
                        return {"success": True, "licenses": available_skus}
                    else:
                        error_body = await response.json()
                        error_msg = error_body.get('error', {}).get('message', await response.text())
                        return {"success": False, "error": error_msg}
                        
            except Exception as e:
                return {"success": False, "error": str(e)}

    async def get_all_licenses(self) -> Dict[str, Any]:
        """Отримує всі ліцензії в організації (включно з тими, що не мають доступних)"""
        async with aiohttp.ClientSession() as session:
            try:
                token = await self._get_access_token(session)
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                licenses_url = "https://graph.microsoft.com/v1.0/subscribedSkus"
                
                async with session.get(licenses_url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        skus = data.get('value', [])
                        return {"success": True, "licenses": skus}
                    else:
                        error_body = await response.json()
                        error_msg = error_body.get('error', {}).get('message', await response.text())
                        return {"success": False, "error": error_msg}
                        
            except Exception as e:
                return {"success": False, "error": str(e)}

    async def assign_license_to_user(self, user_id: str, sku_id: str) -> Dict[str, Any]:
        """Призначає ліцензію користувачу"""
        async with aiohttp.ClientSession() as session:
            try:
                token = await self._get_access_token(session)
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                # Призначаємо ліцензію користувачу
                assign_url = f"https://graph.microsoft.com/v1.0/users/{user_id}/assignLicense"
                
                request_body = {
                    "addLicenses": [
                        {
                            "skuId": sku_id
                        }
                    ],
                    "removeLicenses": []
                }
                
                print(f"📋 Призначаю ліцензію {sku_id} користувачу {user_id}")
                print(f"   Request body: {json.dumps(request_body, indent=2)}")
                
                async with session.post(assign_url, headers=headers, json=request_body) as response:
                    response_text = await response.text()
                    
                    if response.status == 200:
                        user_data = await response.json()
                        print(f"✅ Ліцензію успішно призначено")
                        return {"success": True, "user": user_data}
                    else:
                        print(f"❌ HTTP {response.status} при призначенні ліцензії")
                        print(f"   Response: {response_text}")
                        
                        try:
                            error_body = json.loads(response_text)
                            error_obj = error_body.get('error', {})
                            error_msg = error_obj.get('message', 'Unknown error')
                            error_code = error_obj.get('code', 'Unknown')
                            error_details = error_obj.get('details', [])
                            
                            # Формуємо детальне повідомлення про помилку
                            full_error = f"{error_code}: {error_msg}"
                            if error_details:
                                details_text = "; ".join([d.get('message', str(d)) for d in error_details])
                                full_error += f" ({details_text})"
                            
                            print(f"❌ Помилка призначення ліцензії: {full_error}")
                            return {"success": False, "error": full_error}
                        except json.JSONDecodeError:
                            # Якщо не вдалося розпарсити JSON
                            print(f"❌ Не вдалося розпарсити помилку: {response_text[:500]}")
                            return {"success": False, "error": f"HTTP {response.status}: {response_text[:200]}"}
                        
            except Exception as e:
                import traceback
                print(f"❌ Exception при призначенні ліцензії: {e}")
                print(traceback.format_exc())
                return {"success": False, "error": str(e)}

    def _transliterate_uk_to_en(self, text: str) -> str:
        """Транслітерує український текст на англійську з виправленнями для Azure AD"""
        try:
            if TRANSLITERATE_AVAILABLE:
                transliterated = translit(text, 'uk', reversed=True)
            else:
                transliterated = _simple_transliterate_uk_to_lat(text)
        except Exception as e:
            print(f"⚠️ Помилка транслітерації: {e}")
            transliterated = _simple_transliterate_uk_to_lat(text)
        
        # Виправлення для Azure AD форматів
        # Прибираємо апострофи та виправляємо загальні варіанти
        transliterated = transliterated.replace("'", "")  # Прибираємо апострофи (Markivs'kyj -> Markivskyj)
        transliterated = transliterated.replace("yj", "yi")  # Виправляємо закінчення (Markivskyj -> Markivskyi)
        transliterated = transliterated.replace("ij", "iy")  # Виправляємо "ij" -> "iy" (Andrij -> Andriy)
        transliterated = transliterated.replace("yy", "y")  # Виправляємо подвійні "y"
        
        return transliterated
    
    def _is_ukrainian_text(self, text: str) -> bool:
        """Перевіряє, чи текст містить українські літери"""
        ukrainian_chars = 'абвгґдеєжзиіїйклмнопрстуфхцчшщьюяАБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ'
        return any(char in ukrainian_chars for char in text)
    
    async def search_users(self, search_term: str, limit: int = 10) -> Dict[str, Any]:
        """Шукає користувачів по імені або прізвищу з підтримкою транслітерації"""
        async with aiohttp.ClientSession() as session:
            try:
                token = await self._get_access_token(session)
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                all_users = []
                search_terms = [search_term]
                
                # Якщо текст українською - додаємо транслітерований варіант
                if self._is_ukrainian_text(search_term):
                    transliterated = self._transliterate_uk_to_en(search_term)
                    if transliterated != search_term:
                        search_terms.append(transliterated)
                        print(f"🔄 Транслітерація: '{search_term}' -> '{transliterated}'")
                
                # Розбиваємо повне ім'я на частини (ім'я + прізвище)
                name_parts = []
                for term in search_terms:
                    parts = term.strip().split()
                    if len(parts) >= 2:
                        # Якщо є кілька слів, додаємо окремі частини
                        name_parts.extend(parts)
                    name_parts.append(term)  # Також шукаємо по всьому імені
                
                # Додаємо транслітерацію для окремих частин
                for part in name_parts[:]:
                    if self._is_ukrainian_text(part):
                        transliterated_part = self._transliterate_uk_to_en(part)
                        if transliterated_part != part:
                            name_parts.append(transliterated_part)
                
                # Унікальні терміни для пошуку
                all_search_terms = list(set(search_terms + name_parts))
                
                # Додаємо варіанти з виправленнями для Azure AD
                additional_variants = []
                for term in all_search_terms[:]:
                    # Додаємо варіанти без апострофів
                    if "'" in term:
                        additional_variants.append(term.replace("'", ""))
                    # Додаємо варіанти з "yi" замість "yj"
                    if "yj" in term.lower() or "Yj" in term:
                        additional_variants.append(term.replace("yj", "yi").replace("Yj", "Yi"))
                    # Додаємо варіанти з "iy" замість "ij"
                    if "ij" in term.lower() or "Ij" in term:
                        additional_variants.append(term.replace("ij", "iy").replace("Ij", "Iy"))
                    # Додаємо варіанти з "y" замість "ij" (Andrij -> Andriy)
                    if term.endswith("ij") or term.endswith("Ij"):
                        additional_variants.append(term[:-2] + "iy" if term.endswith("ij") else term[:-2] + "Iy")
                
                all_search_terms.extend(additional_variants)
                all_search_terms = list(set(all_search_terms))  # Унікальні
                
                print(f"🔍 Пошук користувачів по термінам: {all_search_terms}")
                
                # Спочатку спробуємо $search (більш потужний пошук)
                search_supported = True
                for term in all_search_terms[:3]:  # Обмежуємо кількість запитів
                    if not term.strip() or not search_supported:
                        continue
                    
                    try:
                        # Використовуємо $search для кращого пошуку
                        # Формат: $search="displayName:term OR mail:term"
                        search_query = f'"{term}"'
                        search_url = (
                            f"https://graph.microsoft.com/v1.0/users?"
                            f"$search={search_query}"
                            f"&$top={limit}"
                            f"&$select=id,displayName,mail,userPrincipalName,givenName,surname"
                        )
                        
                        headers_with_search = headers.copy()
                        headers_with_search["ConsistencyLevel"] = "eventual"
                        
                        print(f"🔍 Спробую $search для '{term}'")
                        async with session.get(search_url, headers=headers_with_search) as response:
                            if response.status == 200:
                                data = await response.json()
                                users = data.get('value', [])
                                
                                # Додаємо користувачів, уникаючи дублікатів
                                existing_ids = {u.get('id') for u in all_users}
                                for user in users:
                                    if user.get('id') not in existing_ids:
                                        all_users.append(user)
                                        existing_ids.add(user.get('id'))
                                
                                if users:
                                    print(f"✅ Знайдено {len(users)} користувачів через $search для '{term}'")
                            elif response.status == 501:
                                # $search не підтримується
                                print(f"⚠️ $search не підтримується (501), використовую $filter")
                                search_supported = False
                                break
                            else:
                                try:
                                    error_body = await response.json()
                                    error_msg = error_body.get('error', {}).get('message', 'Unknown error')
                                    error_code = error_body.get('error', {}).get('code', 'Unknown')
                                    print(f"⚠️ Помилка $search для '{term}': {error_code} - {error_msg}")
                                    if error_code == "Request_UnsupportedQuery":
                                        search_supported = False
                                        break
                                except:
                                    pass
                    except Exception as e:
                        print(f"⚠️ Помилка $search запиту для '{term}': {e}")
                        search_supported = False
                
                # Якщо $search не дав результатів або не підтримується, використовуємо $filter
                if len(all_users) == 0:
                    print(f"🔄 Використовую $filter для пошуку...")
                    for term in all_search_terms:
                        if not term.strip():
                            continue
                        
                        # Екрануємо спеціальні символи для OData запиту
                        escaped_term = term.replace("'", "''").replace('"', '""')
                        
                        # Пошук користувачів через Graph API з $filter
                        # Використовуємо тільки startswith (contains не підтримується)
                        search_url = (
                            f"https://graph.microsoft.com/v1.0/users?"
                            f"$filter=startswith(displayName,'{escaped_term}') or "
                            f"startswith(surname,'{escaped_term}') or "
                            f"startswith(givenName,'{escaped_term}') or "
                            f"startswith(mail,'{escaped_term}') or "
                            f"startswith(userPrincipalName,'{escaped_term}')"
                            f"&$top={limit}"
                            f"&$select=id,displayName,mail,userPrincipalName,givenName,surname"
                        )
                        
                        # Також спробуємо з нижнім регістром
                        term_lower = term.lower()
                        if term_lower != term:
                            escaped_term_lower = term_lower.replace("'", "''").replace('"', '""')
                            search_url_lower = (
                                f"https://graph.microsoft.com/v1.0/users?"
                                f"$filter=startswith(displayName,'{escaped_term_lower}') or "
                                f"startswith(surname,'{escaped_term_lower}') or "
                                f"startswith(givenName,'{escaped_term_lower}') or "
                                f"startswith(mail,'{escaped_term_lower}') or "
                                f"startswith(userPrincipalName,'{escaped_term_lower}')"
                                f"&$top={limit}"
                                f"&$select=id,displayName,mail,userPrincipalName,givenName,surname"
                            )
                            
                            try:
                                async with session.get(search_url_lower, headers=headers) as response:
                                    if response.status == 200:
                                        data = await response.json()
                                        users = data.get('value', [])
                                        
                                        existing_ids = {u.get('id') for u in all_users}
                                        for user in users:
                                            if user.get('id') not in existing_ids:
                                                all_users.append(user)
                                                existing_ids.add(user.get('id'))
                            except Exception as e:
                                print(f"⚠️ Помилка запиту з нижнім регістром для '{term_lower}': {e}")
                        
                        try:
                            print(f"🔍 Запит пошуку для '{term}'")
                            async with session.get(search_url, headers=headers) as response:
                                if response.status == 200:
                                    try:
                                        data = await response.json()
                                        users = data.get('value', [])
                                        
                                        print(f"📊 Отримано {len(users)} користувачів для '{term}'")
                                        
                                        # Додаємо користувачів, уникаючи дублікатів
                                        existing_ids = {u.get('id') for u in all_users}
                                        for user in users:
                                            if user.get('id') not in existing_ids:
                                                all_users.append(user)
                                                existing_ids.add(user.get('id'))
                                                print(f"   ✓ {user.get('displayName')} ({user.get('mail', user.get('userPrincipalName'))})")
                                        
                                        if users:
                                            print(f"✅ Знайдено {len(users)} користувачів через $filter для '{term}'")
                                    except json.JSONDecodeError as e:
                                        response_text = await response.text()
                                        print(f"❌ Помилка парсингу JSON: {e}")
                                        print(f"   Response: {response_text[:500]}")
                                elif response.status != 200:
                                    # Логуємо помилку детально
                                    try:
                                        error_body = await response.json()
                                        error_msg = error_body.get('error', {}).get('message', 'Unknown error')
                                        error_code = error_body.get('error', {}).get('code', 'Unknown')
                                        print(f"❌ HTTP {response.status} для '{term}': {error_code} - {error_msg}")
                                    except:
                                        response_text = await response.text()
                                        print(f"❌ HTTP {response.status} для '{term}'")
                                        print(f"   Response: {response_text[:500]}")
                        except Exception as e:
                            import traceback
                            print(f"❌ Exception для '{term}': {e}")
                            print(traceback.format_exc())
                            continue
                
                # Обмежуємо кількість результатів
                all_users = all_users[:limit]
                
                print(f"✅ Знайдено {len(all_users)} користувачів")
                
                if all_users:
                    return {"success": True, "users": all_users}
                else:
                    return {"success": False, "error": f"Користувача '{search_term}' не знайдено"}
                        
            except Exception as e:
                print(f"❌ Помилка search_users: {e}")
                return {"success": False, "error": str(e)}
    
    async def search_users_by_first_letter(self, search_term: str, limit: int = 20) -> Dict[str, Any]:
        """Шукає користувачів по першій букві прізвища (fallback метод)"""
        async with aiohttp.ClientSession() as session:
            try:
                token = await self._get_access_token(session)
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                # Визначаємо першу букву прізвища
                # Беремо останнє слово (прізвище) або весь термін якщо одне слово
                parts = search_term.strip().split()
                if len(parts) > 1:
                    last_name = parts[-1]  # Останнє слово - прізвище
                else:
                    last_name = search_term
                
                # Транслітеруємо якщо потрібно
                if self._is_ukrainian_text(last_name):
                    last_name = self._transliterate_uk_to_en(last_name)
                
                if not last_name:
                    return {"success": False, "error": "Не вдалося визначити прізвище"}
                
                first_letter = last_name[0].upper()
                print(f"🔍 Fallback пошук по першій букві прізвища: '{first_letter}'")
                
                # Шукаємо користувачів, чиє прізвище починається з цієї літери
                search_url = (
                    f"https://graph.microsoft.com/v1.0/users?"
                    f"$filter=startswith(surname,'{first_letter}') or startswith(surname,'{first_letter.lower()}')"
                    f"&$top={limit}"
                    f"&$orderby=displayName"
                    f"&$select=id,displayName,mail,userPrincipalName,givenName,surname"
                )
                
                async with session.get(search_url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        users = data.get('value', [])
                        print(f"📊 Знайдено {len(users)} користувачів з прізвищем на '{first_letter}'")
                        return {"success": True, "users": users, "search_type": "first_letter"}
                    else:
                        try:
                            error_body = await response.json()
                            error_msg = error_body.get('error', {}).get('message', 'Unknown error')
                            return {"success": False, "error": error_msg}
                        except:
                            return {"success": False, "error": f"HTTP {response.status}"}
                            
            except Exception as e:
                print(f"❌ Помилка search_users_by_first_letter: {e}")
                return {"success": False, "error": str(e)}

    async def execute_custom_query(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        use_consistency_level: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a custom Graph API query.
        
        This method allows other services to execute custom OData queries
        without needing to know about token management or session handling.
        
        Args:
            endpoint: Graph API endpoint (e.g., "users" or "users?$filter=...")
                     Will be prefixed with BASE_URL automatically
            params: Optional query parameters as dict (will be converted to URL params)
            use_consistency_level: If True, adds ConsistencyLevel: eventual header
                                  Required for complex $filter queries with OR across fields
                                  
        Returns:
            Dict with:
            - success: bool
            - data: Dict - response data (if success=True)
            - error: str - error message (if success=False)
        """
        async with aiohttp.ClientSession() as session:
            try:
                token = await self._get_access_token(session)
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                # Add ConsistencyLevel header for complex queries
                if use_consistency_level:
                    headers["ConsistencyLevel"] = "eventual"
                
                # Build URL
                if endpoint.startswith("http"):
                    # Full URL provided (backward compatibility)
                    url = endpoint
                else:
                    # Endpoint only - prefix with base URL
                    url = f"{self.base_url}/{endpoint.lstrip('/')}"
                
                # Add query parameters if provided
                if params:
                    import urllib.parse
                    query_string = urllib.parse.urlencode(params)
                    separator = "&" if "?" in url else "?"
                    url = f"{url}{separator}{query_string}"
                
                # Add $count=true for ConsistencyLevel queries
                if use_consistency_level and "$count" not in url:
                    separator = "&" if "?" in url else "?"
                    url = f"{url}{separator}$count=true"
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {"success": True, "data": data}
                    else:
                        try:
                            error_body = await response.json()
                            error_msg = error_body.get('error', {}).get('message', f'HTTP {response.status}')
                        except:
                            error_msg = f"HTTP {response.status}"
                        return {"success": False, "error": error_msg}
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    async def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        """Отримує інформацію про користувача по ID"""
        async with aiohttp.ClientSession() as session:
            try:
                token = await self._get_access_token(session)
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                url = f"https://graph.microsoft.com/v1.0/users/{user_id}?$select=id,displayName,mail,userPrincipalName,givenName,surname"
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        user = await response.json()
                        return {"success": True, "user": user}
                    else:
                        error_body = await response.json()
                        error_msg = error_body.get('error', {}).get('message', await response.text())
                        return {"success": False, "error": error_msg}
                        
            except Exception as e:
                return {"success": False, "error": str(e)}

    async def get_calendar_availability(self, user_id: str, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Перевіряє зайнятість календаря користувача"""
        async with aiohttp.ClientSession() as session:
            try:
                token = await self._get_access_token(session)
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                # Використовуємо конкретний user ID замість /me/
                availability_url = f"https://graph.microsoft.com/v1.0/users/{user_id}/calendar/getSchedule"
                
                # Підготовка тіла запиту
                request_body = {
                    "schedules": [user_id],
                    "startTime": {
                        "dateTime": start_time.isoformat(),
                        "timeZone": "UTC"
                    },
                    "endTime": {
                        "dateTime": end_time.isoformat(),
                        "timeZone": "UTC"
                    },
                    "availabilityViewInterval": 30  # 30 хвилин інтервали
                }
                
                async with session.post(availability_url, headers=headers, json=request_body) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {"success": True, "schedules": data.get('value', [])}
                    else:
                        error_body = await response.json()
                        error_msg = error_body.get('error', {}).get('message', await response.text())
                        return {"success": False, "error": error_msg}
                        
            except Exception as e:
                return {"success": False, "error": str(e)}

    async def find_free_slots(self, organizer_id: str, user_emails: List[str], start_date: datetime, end_date: datetime, duration_minutes: int = 30) -> Dict[str, Any]:
        """Знаходить вільні слоти для зустрічі"""
        async with aiohttp.ClientSession() as session:
            try:
                token = await self._get_access_token(session)
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                # Використовуємо findMeetingTimes з конкретним organizer_id
                find_meeting_url = f"https://graph.microsoft.com/v1.0/users/{organizer_id}/findMeetingTimes"
                
                # Форматуємо дати правильно для API
                start_iso = start_date.isoformat() + "Z" if not start_date.tzinfo else start_date.isoformat()
                end_iso = end_date.isoformat() + "Z" if not end_date.tzinfo else end_date.isoformat()
                
                request_body = {
                    "attendees": [{"emailAddress": {"address": email}} for email in user_emails],
                    "timeConstraint": {
                        "timeslots": [{
                            "start": {
                                "dateTime": start_iso,
                                "timeZone": "UTC"
                            },
                            "end": {
                                "dateTime": end_iso,
                                "timeZone": "UTC"
                            }
                        }]
                    },
                    "meetingDuration": f"PT{duration_minutes}M",
                    "maxCandidates": 5
                }
                
                print(f"🔍 Пошук вільних слотів:")
                print(f"   Organizer: {organizer_id}")
                print(f"   Attendees: {user_emails}")
                print(f"   Start: {start_iso}")
                print(f"   End: {end_iso}")
                print(f"   Duration: {duration_minutes} min")
                
                async with session.post(find_meeting_url, headers=headers, json=request_body) as response:
                    if response.status == 200:
                        data = await response.json()
                        meeting_time_suggestions = data.get('meetingTimeSuggestions', [])
                        print(f"✅ Знайдено {len(meeting_time_suggestions)} запропонованих слотів")
                        return {"success": True, "suggestions": meeting_time_suggestions}
                    else:
                        try:
                            error_body = await response.json()
                            error_msg = error_body.get('error', {}).get('message', 'Unknown error')
                            error_code = error_body.get('error', {}).get('code', 'Unknown')
                            print(f"❌ Помилка findMeetingTimes: {response.status}")
                            print(f"   Code: {error_code}")
                            print(f"   Message: {error_msg}")
                            return {"success": False, "error": f"{error_code}: {error_msg}"}
                        except:
                            response_text = await response.text()
                            print(f"❌ Помилка findMeetingTimes: {response.status}")
                            print(f"   Response: {response_text}")
                            return {"success": False, "error": f"HTTP {response.status}: {response_text}"}
                        
            except Exception as e:
                import traceback
                print(f"❌ Exception in find_free_slots: {e}")
                print(traceback.format_exc())
                return {"success": False, "error": str(e)}

    async def create_meeting(self, organizer_id: str, attendees: List[str], subject: str, start_time: datetime, end_time: datetime, body: str = "", agenda: str = None) -> Dict[str, Any]:
        """Створює зустріч в календарі"""
        async with aiohttp.ClientSession() as session:
            try:
                token = await self._get_access_token(session)
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                # Створюємо подію в календарі організатора
                create_event_url = f"https://graph.microsoft.com/v1.0/users/{organizer_id}/calendar/events"
                
                # Формуємо body події з агендою якщо вона є
                if agenda:
                    # Якщо є агенда, додаємо її в body
                    agenda_html = f"<h3>Агенда:</h3><p>{agenda.replace(chr(10), '<br>')}</p>"
                    content = f"<p>Meeting scheduled by HR Onboarding Assistant</p>{agenda_html}"
                elif body:
                    content = body
                else:
                    content = "<p>Meeting scheduled by HR Onboarding Assistant</p>"
                
                event_body = {
                    "subject": subject,
                    "body": {
                        "contentType": "HTML",
                        "content": content
                    },
                    "start": {
                        "dateTime": start_time.isoformat(),
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": end_time.isoformat(),
                        "timeZone": "UTC"
                    },
                    "attendees": [
                        {"emailAddress": {"address": attendee}, "type": "required"}
                        for attendee in attendees
                    ],
                    "isOnlineMeeting": True,
                    "onlineMeetingProvider": "teamsForBusiness"
                }
                
                async with session.post(create_event_url, headers=headers, json=event_body) as response:
                    if response.status == 201:
                        event = await response.json()
                        return {"success": True, "event": event}
                    else:
                        error_body = await response.json()
                        error_msg = error_body.get('error', {}).get('message', await response.text())
                        return {"success": False, "error": error_msg}
                        
            except Exception as e:
                return {"success": False, "error": str(e)}

    async def search_groups(self, search_term: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search for Azure AD groups by name.
        
        Args:
            search_term: Group name to search for
            limit: Maximum number of results
            
        Returns:
            Dict with success status and groups list
        """
        async with aiohttp.ClientSession() as session:
            try:
                token = await self._get_access_token(session)
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                # Search groups by displayName
                url = f"{self.base_url}/groups"
                params = {
                    "$filter": f"startswith(displayName,'{search_term}') or startswith(mail,'{search_term}')",
                    "$top": str(limit),
                    "$select": "id,displayName,mail,groupTypes,mailEnabled,securityEnabled"
                }
                
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        groups = data.get('value', [])
                        return {"success": True, "groups": groups}
                    else:
                        error_body = await response.json()
                        error_msg = error_body.get('error', {}).get('message', f'HTTP {response.status}')
                        return {"success": False, "error": error_msg}
            except Exception as e:
                return {"success": False, "error": str(e)}

    async def get_group_members(self, group_id: str) -> Dict[str, Any]:
        """
        Get all members of an Azure AD group.
        
        Args:
            group_id: Group ID (object ID)
            
        Returns:
            Dict with success status and members list (users only)
        """
        async with aiohttp.ClientSession() as session:
            try:
                token = await self._get_access_token(session)
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                # Get group members (users only, not nested groups)
                url = f"{self.base_url}/groups/{group_id}/members/microsoft.graph.user"
                params = {
                    "$select": "id,displayName,mail,userPrincipalName,givenName,surname"
                }
                
                all_members = []
                while url:
                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            members = data.get('value', [])
                            all_members.extend(members)
                            
                            # Check for next page
                            url = data.get('@odata.nextLink')
                            params = None  # NextLink already has params
                        else:
                            error_body = await response.json()
                            error_msg = error_body.get('error', {}).get('message', f'HTTP {response.status}')
                            return {"success": False, "error": error_msg}
                
                return {"success": True, "members": all_members}
            except Exception as e:
                return {"success": False, "error": str(e)}

    async def get_user_timezone(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's timezone from their mailbox settings.
        
        Args:
            user_id: User ID (AAD Object ID or userPrincipalName)
            
        Returns:
            Dict with success status and timezone (e.g., "Europe/Kiev")
        """
        async with aiohttp.ClientSession() as session:
            try:
                token = await self._get_access_token(session)
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                # Get mailbox settings (timezone)
                url = f"{self.base_url}/users/{user_id}/mailboxSettings"
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        settings = await response.json()
                        timezone = settings.get('timeZone', 'UTC')
                        return {"success": True, "timezone": timezone}
                    else:
                        # Fallback to UTC if cannot get timezone
                        return {"success": True, "timezone": "UTC"}
            except Exception as e:
                # Fallback to UTC on error
                return {"success": True, "timezone": "UTC"}

    async def get_calendar_events(
        self, 
        user_id: str, 
        start_time: datetime, 
        end_time: datetime,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Get calendar events for a user with details.
        
        Args:
            user_id: User ID (AAD Object ID or userPrincipalName)
            start_time: Start of time range
            end_time: End of time range
            include_details: Whether to include subject and other details (for Free/Busy vs Detailed view)
            
        Returns:
            Dict with success status and events list
        """
        async with aiohttp.ClientSession() as session:
            try:
                token = await self._get_access_token(session)
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                # Build query parameters
                start_iso = start_time.isoformat() + "Z" if not start_time.tzinfo else start_time.isoformat()
                end_iso = end_time.isoformat() + "Z" if not end_time.tzinfo else end_time.isoformat()
                
                # Select fields based on detail level
                if include_details:
                    select_fields = "id,subject,start,end,isAllDay,sensitivity,showAs,isCancelled,bodyPreview,location"
                else:
                    # Free/Busy only
                    select_fields = "id,start,end,showAs"
                
                url = f"{self.base_url}/users/{user_id}/calendar/calendarView"
                params = {
                    "startDateTime": start_iso,
                    "endDateTime": end_iso,
                    "$select": select_fields,
                    "$orderby": "start/dateTime",
                    "$top": "100"  # Limit to 100 events per day
                }
                
                all_events = []
                while url:
                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            events = data.get('value', [])
                            all_events.extend(events)
                            
                            # Check for next page
                            url = data.get('@odata.nextLink')
                            params = None  # NextLink already has params
                        else:
                            error_body = await response.json()
                            error_msg = error_body.get('error', {}).get('message', f'HTTP {response.status}')
                            return {"success": False, "error": error_msg}
                
                return {"success": True, "events": all_events}
            except Exception as e:
                return {"success": False, "error": str(e)}

