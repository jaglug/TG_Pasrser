from selenium import webdriver
import time
import gc
import asyncio
import os
import csv
import socket
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.options import Options as ChromeOptions



############### БЛОК ОБЪЯВЛЕНИЯ ФУНКЦИЙ ######################################

# Функция для проверки доступности порта
def is_port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

# Функция для поиска следующего доступного порта
def get_next_available_port(start_port=9210):
    port = start_port
    while not is_port_available(port):
        port += 1
    return port

#Функция получения id последнего сообщения
def get_latest_message_id(driver):
    # Получаем все сообщения и находим сообщение с максимальным data-message-id
    messages = driver.find_elements(By.CSS_SELECTOR, 'div.message-list-item')
    if not messages:
        return None
    latest_message = max(messages, key=lambda m: int(m.get_attribute('data-message-id')))
    return int(latest_message.get_attribute('data-message-id'))

#Получение данных сообщения
def get_message_info(message, chat_name):
    # Извлечение данных из сообщения
    try:
        positive_group_id = str(abs(int(group_id)))[3:]
        try:
            peer_id = message.find_element(By.CSS_SELECTOR, 'div.Avatar').get_attribute('data-peer-id')
        except:
            pass

        try:
            name = message.find_element(By.CSS_SELECTOR, 'span.message-title-name').text
        except:
            pass

        try:
            msg = message.find_element(By.CSS_SELECTOR, 'div.text-content').text
        except:
            pass

        try:
            message_id = message.get_attribute('data-message-id')
        except:
            pass
        try:

            return f'ID пользователя: {peer_id},Ник пользователя: {name},Сообщение: {msg},Переслано из: {chat_name},Ссылка на сообщение: https://t.me/c/{positive_group_id}/{message_id};'
        except:
            pass   
    except:
        print(f"Ошибка при извлечении данных сообщения:")
        return None
    
# def get_message_info_2(message, chat_name):
#     # Извлечение данных из сообщения
#     try:
#         peer_id = message.find_element(By.CSS_SELECTOR, 'div.colored-name.name.floating-part').get_attribute('data-peer-id')
#         msg = message.find_element(By.CSS_SELECTOR, 'div[class="message spoilers-container"]').text
#         message_id = message.get_attribute('data-mid')
#         name = message.find_element(By.CSS_SELECTOR, 'span.peer-title').text
#         return f'ID пользователя: {peer_id},Ник пользователя: {name},Сообщение: {msg},Переслано из: {chat_name},Ссылка на сообщение: https://t.me/c/{group_id}/{message_id};'
#     except:
#         print(f"Ошибка при извлечении данных сообщения:")
#         return None

#Загрузка данных в csv файл
def append_message_to_csv_file(message_info, file_path='C:\\Projects\\Telegram_ML\\messages.csv'):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    with open(file_path, 'a', newline='', encoding='utf-8') as file:
        file.write(f"{message_info}\n")

def scroll_to_message(driver, message_id):
    try:
        message = driver.find_element(By.CSS_SELECTOR, f'div.message-list-item[data-message-id="{message_id}"]')
        driver.execute_script("arguments[0].scrollIntoView();", message)
        print(f"Прокручено к сообщению с ID {message_id}")
    except Exception as e:
        print(f"Ошибка при прокрутке к сообщению с ID {message_id}: {e}")

############### КОНЕЦ БЛОКА ОБЪЯВЛЕНИЯ ФУНКЦИЙ ######################################


# capabilities = DesiredCapabilities.CHROME.copy()
# capabilities['version'] = 'latest'
# capabilities['enableVNC'] = True
# capabilities['enableVideo'] = False

selenoid_url = "http://localhost:4444/wd/hub"

useragent = UserAgent()
#useragent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
options = webdriver.ChromeOptions()
options.add_argument(f"user-agent=useragent={useragent.random}")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--headless")
options.add_argument("--disable-javascript")
options.add_argument("--disable-features=PermissionsPolicy")
options.add_argument("--disable-features=SensorExtraClasses")
options.set_capability("pageLoadStrategy", "eager")
#options.set_capability("browserVersion", "127.0")
# remote_debugging_port = get_next_available_port()
# options.add_argument(f"--remote-debugging-port={remote_debugging_port}")

# driver = webdriver.Chrome(options=options)

driver = webdriver.Remote(
    command_executor=selenoid_url,
    options=options
)


driver.get('https://web.telegram.org/')


#Нажатие кнопки вход по номеру телефона, 2 варианта
time.sleep(5)
try:
        log_by_phone = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//button[contains(@class, "Button") and contains(text(), "Log in by phone Number")]'))
        )
        log_by_phone.click()
        print('Вход по номеру телефона')

except:
    print('НЕПРАВИЛЬНАЯ ВЕРСИЯ TELEGRAM ПОПРОБУЙТЕ СНОВА')
    driver.quit()
    driver.close()

time.sleep(3)


#Здесь в зависимости от поля для ввода номера 2 разных варианта


############# Первый вариант ###################
try:
    login = WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[aria-label="Your phone number"]'))
    )
    number=input('Введите номер телефона:')
    login.send_keys(number)
    print('ввели логин')
    time.sleep(5)
    try:
        button_next = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button[type="submit"].Button.default.primary.has-ripple'))
            )
        button_next.click()
        print('нажал на кнопку next')
    except:
        print('Ошибка на этапе ввода номера телефона')
    try:
        invalid_number = WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[aria-label="Invalid phone number."]'))
    )
        print('Неправильный формат номера, попробуйте снова')
        driver.quit()
        driver.close()
    except:
        pass
    try:
        input_field = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, 'sign-in-code'))
        )
        print('поле найдено')
        input_code = input("Введите код для входа: ") 
        input_field.send_keys(input_code) 
        print("Текст успешно вставлен в поле ввода")
    except:
        print('Ошибка на этапе ввода кода')
    time.sleep(3)
    try:
        # Ожидание загрузки элемента и вставка текста
        input_password_field = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, 'sign-in-password'))
        )
        input_password = input("Введите пароль: ")  # Ввод пароля через input
        input_password_field.send_keys(input_password)  # Вставка текста
        print("Пароль успешно вставлен в поле ввода")
    except:
        print('Ошибка на этапе двухфакторки')
    time.sleep(3)

    try:
        button_next = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button[type="submit"].Button.default.primary.has-ripple'))
            )
        button_next.click()
        print('нажал на кнопку next')
    
    except:
        print('Ошибка на этапе подтвержения поля двухфакторки')
    time.sleep(3)
    try:
        time.sleep(5)
        group_id = input("Введите id группы: ")  # Ввод ID группы через input
        # Ожидание загрузки элемента ссылки и поиск по href
        link = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f'a.ListItem-button[href*="#{group_id}"]'))
        )
        link.click()
        print('ссылка нажата')
    except:
        print('Ошибка на этапе поиска чата по ID')
    time.sleep(3)
    try:
        chat_name_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.ChatInfo h3.fullName'))
        )
        chat_name = chat_name_element.text.strip()
    except Exception as e:
        print(f"Ошибка при получении названия чата: {e}")
        chat_name = "Unknown Chat"
    time.sleep(3)

    #Процесс парсинга    
    try:
        # Начальное получение самого последнего сообщения
        latest_message_id = get_latest_message_id(driver)
        if latest_message_id is not None:
            print(f"Самое последнее сообщение ID: {latest_message_id}")
        else:
            latest_message_id = 0

        while True:
            try:
                # Проверка наличия кнопки для прокрутки чата вниз
                try:
                    button = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'button.Button.cxwA6gDO.default.secondary.round[aria-label="Go to bottom"]'))
                    )
                    button.click()
                    print("Кнопка успешно нажата")
                except:
                    print('Нет кнопки')
                    pass  # Если кнопка не найдена, продолжаем дальше

                # Ожидание 5 секунд перед проверкой новых сообщений
                time.sleep(5)

                # Поиск новых сообщений
                messages = driver.find_elements(By.CSS_SELECTOR, 'div.message-list-item')
                if messages:
                    print('Найдены новые сообщения:\n\n')
                else:
                    print('Не найдено новых сообщений')

                for message in messages:
                    try:
                        message_id = int(message.get_attribute('data-message-id'))
                        print(f'Обнаружено сообщение с ID: {message_id}')

                        if message_id > latest_message_id:
                            print(f'Новое сообщение с ID {message_id} больше последнего ID {latest_message_id}')
                            info = get_message_info(message, chat_name)
                            if info:
                                append_message_to_csv_file(info)
                                print(info)
                            latest_message_id = message_id
                        else:
                            print(f'Сообщение с ID {message_id} уже обработано')
                    except Exception as e:
                        print(f"Ошибка при обработке сообщения: {e}")

                # Прокрутка к сообщению, которое находится на 5 сообщений выше последнего обработанного
                target_message_id = max(latest_message_id - 5, 0)
                scroll_to_message(driver, target_message_id)

                # Ожидание 10 секунд перед повторной проверкой
                time.sleep(10)
            except Exception as e:
                print(f"Ошибка: {e}")

    except Exception as e:
        print(f"Ошибка: {e}")
except Exception as e:
    print(f"Ошибка: {e}")
# ############# второй вариант #################
# except:
#     try:
#         try:
#             login = WebDriverWait(driver, 3).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, 'div[inputmode="decimal"].input-field-input'))
#             )
#             number=input('Введите номер телефона:')
#             login.send_keys(number)
#             print('ввели логин')
#         except:
#             print('не удалось найти поле для ввода')
#         time.sleep(3)

#     #Кнопка next после ввода номера
#         try:    
#             button_next = WebDriverWait(driver, 3).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, 'button[class="btn-primary btn-color-primary rp"]'))
#             )
#             button_next.click()
#             print('нажал на кнопку next')
#         except:
#             print('не удалось найти кнопку next')
#         try:
#             invalid_number = WebDriverWait(driver, 3).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="input-field-input error"]'))
#         )
#             print('Ошибка сессии, попробуйте снова')
#             driver.quit()
#             driver.close()
#         except:
#             pass
#     #Поле подтвеждения кода
#         try:
#             input_field = WebDriverWait(driver, 3).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, 'input[class="input-field-input is-empty"]'))
#             )
#             print('поле найдено')
#             input_code = input("Введите код для входа: ") 
#             input_field.send_keys(input_code) 
#             print("Текст успешно вставлен в поле ввода")
#         except:
#             print('Не найдено поля для ввода кода')

#         time.sleep(3)

#     #Ввод пароля двухфактортки

#         try:
#             input_password_field = WebDriverWait(driver, 5).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="notsearch_password"]'))
#             )
#             if input_password_field:
#                 print('не найдено поля ввода пароля')
#             input_password = input("Введите пароль: ")  # Ввод пароля через input
#             input_password_field.send_keys(input_password)  # Вставка текста
#             print("Пароль успешно вставлен в поле ввода")

#         except:
#             print(f"Не найдено поле для ввода пароля")
#         time.sleep(3)

#     #Нажатие next в меню двухфакторки
#         try:
#             button_next = WebDriverWait(driver, 3).until(
#                 EC.presence_of_element_located((By.XPATH, '//button[contains(@class, "btn-primary btn-color-primary rp")]//div[contains(@class, "c-ripple")]')))
#             button_next.click()
#             print('нажал на кнопку next')
#         except:
#             print('не удалось найти кнопку next')

#     #Нажатие по ссылке группы
#         try:
#             time.sleep(5)
#             group_id = input("Введите id группы: ")  # Ввод ID группы через input
#             group_id = '-'+group_id[4:] if group_id.startswith('-100') else group_id
#             # Ожидание загрузки элемента ссылки и поиск по href
#             link = WebDriverWait(driver, 3).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, f'a.row.no-wrap.row-with-padding.row-clickable.hover-effect.rp.chatlist-chat.chatlist-chat-bigger.row-big[href*="{group_id}"]'))
#             )
#             link.click()
#             print('ссылка нажата')
#         except Exception as e:
#             print(f"Ошибка: {e}")
#         time.sleep(3)
#     #Получение названия чата
#         try:
#             chat_name_element = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, 'div.user-title span.peer-title'))
#             )
#             chat_name = chat_name_element.text.strip()
#         except Exception as e:
#             print(f"Ошибка при получении названия чата: {e}")
#             chat_name = "Unknown Chat"

#         time.sleep(3)
        
#     #Процесс парсинга
#         try:
#             # Начальное получение самого последнего сообщения
#             latest_message_id = get_latest_message_id(driver)
#             if latest_message_id is not None:
#                 print(f"Самое последнее сообщение ID: {latest_message_id}")
#             else:
#                 latest_message_id = 0

#             while True:
#                 try:
#                     # Проверка наличия кнопки для прокрутки чата вниз
#                     try:
#                         button = WebDriverWait(driver, 5).until(
#                             EC.presence_of_element_located((By.CSS_SELECTOR, 'button[class="btn-circle btn-corner z-depth-1 bubbles-corner-button chat-secondary-button bubbles-go-down rp"]'))
#                         )
#                         button.click()
#                         print("Кнопка успешно нажата")
#                     except:
#                         pass  # Если кнопка не найдена, продолжаем дальше

#                     # Ожидание 5 секунд перед проверкой новых сообщений
#                     time.sleep(5)

#                     # Поиск новых сообщений
#                     messages = driver.find_elements(By.CSS_SELECTOR, 'div[data-mid]')
#                     for message in messages:
#                         message_id = int(message.get_attribute('data-mid'))
#                         if message_id > latest_message_id:
#                             info = get_message_info_2(message, chat_name)
#                             if info:
#                                 append_message_to_csv_file(info)
#                                 print(info)
#                             latest_message_id = message_id

#                 except Exception as e:
#                     print(f"Ошибка: {e}")
            
#         except Exception as e:
#             print(f"Ошибка: {e}")
#     except Exception as e:
#         print(f"Ошибка: {e}")

