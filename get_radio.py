import asyncio
from bleak import BleakScanner
import subprocess
import datetime
import os  # ファイルの存在確認
import getpass  # パスワード入力


async def main():
    password = getpass.getpass()
    # ファイルの存在確認
    file_name = save_file_init()
    for i in range(30):
        print(i, "start")
        # BLE
        ble_devices = await get_ble_devices()
        save_ble_data(i, ble_devices, file_name)
        # WIFI
        wifi_devices = get_wifi_devices(password)
        save_wifi_data(i, wifi_devices, file_name)
        print(i, "end")


async def get_ble_devices():
    devices = await BleakScanner.discover()
    return devices


def get_wifi_devices(password):
    command = "echo {} | sudo -S /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -s".format(
        password
    )
    output = subprocess.check_output(command, shell=True)
    return output.decode("utf-8")


def time_init():
    dt_now = datetime.datetime.now()
    mouth = dt_now.month
    day = dt_now.day
    time = dt_now.strftime("%H:%M:%S")
    time = time.replace(":", "-")
    return (mouth, day, time)


def save_file_init():
    # ファイルの存在確認
    files = ["data"]
    for f in files:
        if not os.path.exists(f):
            os.makedirs(f)
    # ble  name: mouth_date_time.csv
    # wifi name: mouth_date_time.csv
    mouth, day, time = time_init()
    file_name = f"data/{mouth}_{day}_{time}.csv"
    # 管理者権限なしでファイルを作成
    with open(file_name, "w") as f:
        f.write("gets,rssi,address\n")
    return file_name


def save_ble_data(i, ble_devices, file_name):
    # csv として保存
    # rssi address
    with open(file_name, "a") as f:
        for d in ble_devices:
            # rssi が 3桁以上の場合
            if d.rssi > 0:
                continue
            f.write(f"{i},{d.rssi},{d.address}\n")


def save_wifi_data(i, wifi_devices, file_name):
    wifi_devices = wifi_devices.split("\n")

    for count, device in enumerate(wifi_devices, start=1):
        if count == 1:  # Skip the first line
            continue

        # Split the device string into parts
        parts = device.split()

        # Get the Mac and RSSI
        if len(parts) < 2:
            continue
        mac = parts[1]
        rssi = parts[2]

        err = False
        count = 1
        # rssi が-から始まらない場合
        while rssi[0] != "-":
            count += 1
            mac += " " + rssi
            rssi = parts[count]
            if rssi[0] == "-":
                break
            if count > 5:
                err = True
                break

        if err:
            continue

        # Save the Mac and RSSI to a file
        with open(file_name, "a") as f:
            f.write(f"{i},{rssi},{mac}\n")


asyncio.run(main())
