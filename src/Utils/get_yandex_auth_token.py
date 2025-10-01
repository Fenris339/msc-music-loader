from selenium import webdriver
import time


def get_token():
    drivers = [
        lambda: webdriver.Chrome(),
        lambda: webdriver.Firefox(),
        lambda: webdriver.Edge(),
        lambda: webdriver.Safari()
    ]

    driver = None
    for driver_func in drivers:
        try:
            driver = driver_func()
            print(f"Успешно запущен {driver.name}")
            break
        except:
            continue

    if not driver:
        print("Не удалось запустить ни один браузер")
        return None

    try:
        driver.get("https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d")

        print("Авторизуйтесь в браузере...")
        print("Ожидание получения токена (максимум 5 минут)...")

        start_time = time.time()
        while time.time() - start_time < 300:  # 5 минут
            if "access_token=" in driver.current_url:
                url = driver.current_url
                token = url.split("access_token=")[1].split("&")[0]
                print("Токен получен!")
                return token
            time.sleep(1)

        raise Exception("Таймаут: не удалось получить токен")

    finally:
        driver.quit()