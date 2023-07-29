from selenium import webdriver
from selenium.webdriver.common.by import By
from icmplib import ping
import time, datetime

def reset_gateway():
    driver = webdriver.Firefox()

    # log-in shit
    while True:
        try:
            driver.get("http://192.168.250.254/cgi-bin/restart.ha")
            pwd_field = driver.find_element(by=By.NAME, value="password")
        except:
            continue
        else:
            break
    pwd_field.send_keys("<............your password/att device access code................>")
    ctn = driver.find_element(by=By.NAME, value="Continue")
    ctn.click()

    rst_button = driver.find_element(by=By.NAME, value="Restart")
    ccl_button = driver.find_element(by=By.NAME, value="Cancel")
    rst_button.click()

    driver.quit()


def main():

    # import pdb; pdb.set_trace()
    while True:
        pres = ping("google.com", count=30, privileged=False,family=6)
        if pres.packet_loss >= 0.5:
            print("bad packet loss at", datetime.datetime.now())
            print(pres)
            reset_gateway()
            time.sleep(3600)

main()
