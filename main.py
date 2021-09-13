import requests
import json
import time
import getpass

class System:
    def __init__(self):
        self.URL_LOGIN_PAGE = "https://ecourse.ncyu.edu.tw/login/index.php"
        self.URL_SEARCH_PAGE = "https://ecourse.ncyu.edu.tw/lib/ajax/service.php?info=core_message_data_for_messagearea_search_users&sesskey="
        self.LIMITNUM = 100
        self.login_response = None
        self.session = None
        self.START_YEAR = 110
        self.STOP_YEAR = 110
        self.START_DEPTID = 29
        self.STOP_DEPTID = 30
        self.BREAK_TIME = 5

    def login(self, username: str, password: str):
        self.session = requests.session()


        data = {
            "username": username,
            "password": password
        }

        self.login_response = self.session.post(url = self.URL_LOGIN_PAGE, data = data)

    def getUserid(self):
        response = self.login_response.text
        index = response.find("userid")
        userid = response[index + 8 : index + 12]

        return userid

    def getSessionKey(self):
        response = self.login_response.text
        index = response.find("sesskey")
        sesskey = response[index + 10 : index + 20]

        return sesskey

    def getContacts(self, number: str):
        userid = self.getUserid()
        sesskey = self.getSessionKey()
        url_search = self.URL_SEARCH_PAGE + sesskey
        payload = [{
            "index": 0,
            "methodname": "core_message_data_for_messagearea_search_users",
            "args": {
                "userid": userid,
                "search": number,
                "limitnum": self.LIMITNUM
            }
        }]

        response = self.session.post(url = url_search, data = json.dumps(payload))
        result = response.json()

        return result[0]['data']['noncontacts']

    def record(self):
        total = {}
        for year in range(self.START_YEAR, self.STOP_YEAR + 1):
            file = {}
            for id in range(self.START_DEPTID, self.STOP_DEPTID + 1):
                deptId = '{:0>2}'.format(id)
                query = str(year) + deptId
                contacts = self.getContacts(query)

                if not contacts:
                    continue

                temp = {}
                for row in contacts:
                    userid = int(row['userid'])
                    index = row['fullname'].find(query)
                    number = int(row['fullname'][index : index + 8])
                    name = row['fullname'][index + 8:]
                    temp[ userid ] = {
                        number : name
                    }
                file[ id ] = temp

                # cool down
                for i in range(self.BREAK_TIME, 0, -1):
                    time.sleep(1)
                    print(f'Time break: {i}s')

                print(f'{query} is OK!')
            total[ year ] = file

        with open("contact.json", "w") as files:
            json.dump(total, files, ensure_ascii = False, indent=4)

system = System()
username = input("請輸入帳號：")
password = getpass.getpass("請輸入密碼：")
system.login(username, password)
system.record()
