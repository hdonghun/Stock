from PyQt5.QAxContainer import *
from PyQt5.QtCore import * #로그인 중에 핸들링이 값이 없다고 나오는것을 해결해주기 위한
from config.errorCode import * # errorCode파일을 가져오기
class Kiwoom(QAxWidget):
    def __init__(self):

        super().__init__()

        print("Kiwoom 클래스 입니다.")

        ####### eventloop 모음
        self.login_event_loop = None
        ####################

        ####### 변수 모음
        self.account_num = None
        ####################

        self.get_ocx_instance()
        self.event_slots()

        self.signal_login_commConnect()  # 여기까지 로그인
        self.get_account_info()          # 계좌 정보 실행

        self.detail_account_info()       # 계좌정보 가져오기
        #self.trdata_slot()               # 예수금 가져오기

    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)     # 로그인에 대한 이벤트 OnEventConnect
        self.OnReceiveTrData.connect(self.trdata_slot)   # 이벤트 걸기! #Tr 관련 요청에 대한 것은 self.trdate_slot으로 !!

    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect()")

        self.login_event_loop = QEventLoop() #로그인 중에 핸들링이 값이 없다고 나오는것을 해결해주기 위한
        self.login_event_loop.exec_() # 로그인이 완료 될때까지 다음 코드가 실행이 안되게 해주는 exec_()
                                        # 자동 로그인 방법은 코드로 하지 않고, KOAStudio에서 설정하는 방법으로
    def login_slot(self, errCode):
        print(errCode)
        print(errors(errCode))         #errorCode

        self.login_event_loop.exit()


    #내 정보 가져오기
    def get_account_info(self):
        account_list = self.dynamicCall("GetLoginInfo(String)","ACCNO")  # 계좌번호

        self.account_num = account_list.split(';')[0] #계좌번호를 self에 넣어 언제든지 사용할수 있게 만들어준다.
        print("나의 보유 계좌번호 %s " % self.account_num) #계좌번호 확인

    def detail_account_info(self):
        print("예수금을 요청하는 부분 : ")
    #TR 요청!
        # opw00001: 예수금상세현황요청
        self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num) #인적사항 기입
        self.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(String, String)", "조회구분", "2")
        # 무엇을 원하는지
        # ("내가 지은 요청이름", "TR번호", "preNext", "화면번호")
        self.dynamicCall("CommRqData(String, String, int, String)", "예수금상세현황요청", "opw00001", "0", "2000")

    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        '''
        Tr 요청을 받는 구역이다. 슬롯이다.
        :param sScrNo: 스크린번호
        :param sRQName: 내가 요청했을 때 지은 이름
        :param sTrCode: 요청 id, tr코드
        :param sRecordName: 사용 안함
        :param sPrevNext: 다음 페이지가 있는지
        :return:
        '''
        if sRQName == "예수금상세현황요청":
            deposit = self.dynamicCall("GetCommDate(String, String, int, String)", sTrCode, sRQName, 0, "예수금") #데이터를 요청해서 받으면, 그것들이 데이터루프에 걸려있고, 그것을 저장소에서 꺼내와서 사용한다?
            print("예수금 %s" % type(deposit))
            print("예수금 형변환 %s" % int(deposit))

            ok_deposit = self.dynamicCall("GetCommDate(String,String,int,String)", sTrCode, sRQName, 0, "출금가능금액") #데이터를 요청해서 받으면, 그것들이 데이터루프에 걸려있고, 그것을 저장소에서 꺼내와서 사용한다?
            print("출금가능금액 %s" % ok_deposit)
            print("출금가능금액 형변환 %s" % int(ok_deposit))

# Event Loop 란 : 데이터를 처리하는 동안, 다른 작업을 할 수 있게 만드는 거.
# Pyqt Evnet Loop : 데이터를 처리하는 동안, 다른 것들이 실해 되지 않게, block을 건다.

