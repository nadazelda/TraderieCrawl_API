import os
import undetected_chromedriver as uc # 특정 local의 설치파일로 할경우
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import tempfile

class ChromeDriver:
    # 최대한 컴퓨팅 자원을 아끼기 위한 옵션 설정
    def __init__(self)->None:
      self._options = self._getTestChromeOptions()
      # Docker에서 수동설치하기때문에 경로지정하는 방식으로 변경
      #self._service = Service(executable_path=ChromeDriverManager().install())
      print(" ✅ 수동 설치된 경로")
      self._service = Service(executable_path="/usr/bin/chromedriver")  # ✅ 수동 설치된 경로

      self._driver = webdriver.Chrome(service=self._service, options=self._options)
      self._driver.set_page_load_timeout(60)


    def _getTestChromeOptions(self):
      print('_getTestChromeOptions')
      options = Options()
      user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
      options.add_argument('user-agent=' + user_agent)
      options.add_argument("lang=ko_KR")
      # ✅ 고유한 유저 디렉토리 생성
      print( "✅ 고유한 유저 디렉토리 생성")
      user_data_dir = tempfile.mkdtemp()
      options.add_argument(f'--user-data-dir={user_data_dir}')


      options.add_argument('--headless')  # GUI 없이 실행
      options.add_argument('--no-sandbox')  # 보안 모드 비활성화
      options.add_argument('--disable-dev-shm-usage')  # 공유 메모리 문제 해결
      options.add_argument('--remote-debugging-port=9222')  # 디버깅 포트 설정
      options.add_argument('--disable-gpu')  # GPU 비활성화
      options.add_argument('--disable-software-rasterizer')  # 소프트웨어 렌더링 비활성화

        # Chrome 드라이버 경로 설정
       # Chrome이 설치된 경로를 명시해야 합니다.
      options.binary_location = "/usr/bin/google-chrome"  # 서버에서 크롬 바이너리 경로를 지정

      return options

    # 단순히 해당 페이지 접속
    def get(self, url):
        self._driver.get(url)
    def __del__(self):
        try:
            self.quit()
        except:
            pass
        
    # selectors에 대해 모두 로딩 될 때까지 대기
    def waitAllByCssSelector(self, *selectors,  timeout=10):
        try:
            for selector in selectors:
                WebDriverWait(self._driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
        except Exception as e:
            print(f"❌ waitAllByCssSelector 실패: {selectors} - {e}")
            raise

    # selectors에 대해 하나라도 로딩 될 때까지 대기
    def waitAnyByCssSelector(self, *selectors, timeout=10):
        try:
            WebDriverWait(self._driver, timeout).until(
                EC.any_of(*[
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    for selector in selectors
                ])
            )
        except Exception as e:
            print(f"❌ waitAnyByCssSelector 실패: {selectors} - {e}")
            raise

    # 제곧내
    def waitClassName(self, className, timeout=10):
        try:
            WebDriverWait(self._driver, timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, className))
            )
        except Exception as e:
            print(f"❌ waitClassName 실패: {className} - {e}")
            raise

    def findElementByCssSelector(self, selector):
        try:
            return self._driver.find_element(By.CSS_SELECTOR, selector)
        except Exception as e:
            print(f"❌ findElementByCssSelector 실패: {selector} - {e}")
            raise
        #return self._driver.find_element(By.CSS_SELECTOR, selector)

    def findElementsByCssSelector(self, selector):
        try:
            return self._driver.find_elements(By.CSS_SELECTOR, selector)
        except Exception as e:
            print(f"❌ findElementsByCssSelector 실패: {selector} - {e}")
            raise
        

    def findElementsByClassName(self, className):
        try:
            return self._driver.find_elements(By.CLASS_NAME, className)
        except Exception as e:
            print(f"❌ findElementsByClassName 실패: {className} - {e}")
            raise
        

    # 크롬 드라이버 종료 (굳이 할 필요가 있을까?)
    def quit(self):
        try:
            self._driver.quit()
        except Exception as e:
            print(f"❗ 드라이버 종료 실패: {e}")
