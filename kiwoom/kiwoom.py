from PyQt5.QAxContainer import *
from PyQt5.QtCore import * #로그인 중에 핸들링이 값이 없다고 나오는것을 해결해주기 위한
class Kiwoom(QAxWidget):
    def __init__(self):

        super().__init__()

        print("Kiwoom 클래스 입니다.")

        ####### eventloop 모음
        self.login_event_loop = None
        ####################
        self.get_ocx_instance()
        self.event_slots()

        self.signal_login_commConnect()

    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)

    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect()")

        self.login_event_loop = QEventLoop() #로그인 중에 핸들링이 값이 없다고 나오는것을 해결해주기 위한
        self.login_event_loop.exec_() # 로그인이 완료 될때까지 다음 코드가 실행이 안되게 해주는 exec_()
                                        # 자동 로그인 방법은 코드로 하지 않고, KOAStudio에서 설정하는 방법으로
    def login_slot(self, errCode):
        print(errCode)

        self.login_event_loop.exit()





