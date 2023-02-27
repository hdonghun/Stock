from PyQt5.QAxContainer import *
from PyQt5.QtCore import * #로그인 중에 핸들링이 값이 없다고 나오는것을 해결해주기 위한
from config.errorCode import * # errorCode파일을 가져오기
class Kiwoom(QAxWidget):
    def __init__(self):

        super().__init__()

        print("Kiwoom 클래스 입니다.")

        ####### eventloop 모음
        self.login_event_loop = None
        self.detail_account_info_event_loop = None
        self.detail_account_info_event_loop_2 = None
        self.detail_account_info_event_loop_2 = QEventLoop()

        # Event Loop 란 : 데이터를 처리하는 동안, 다른 작업을 할 수 있게 만드는 거.
        # Pyqt Evnet Loop : 데이터를 처리하는 동안, 다른 것들이 실해 되지 않게, block을 건다.
        ####################

        ####### 변수 모음
        self.account_num = None
        ####################

        ####### 계좌관련 변수
        self.use_money = 0
        self.use_money_percent = 0.5
        ####################

        ####### 변수 모음
        self.account_stock_dict = {}
        ####################


        self.get_ocx_instance()
        self.event_slots()

        self.signal_login_commConnect()  # 여기까지 로그인
        self.get_account_info()          # 계좌 정보 실행
        self.detail_account_info()       # 예수금 가져오는거
        self.detail_account_mystock()    # 계좌평가 잔고 내역 요청

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

        self.detail_account_info_event_loop = QEventLoop()
        self.detail_account_info_event_loop.exec_()

    def detail_account_mystock(self, sPrevNext="0"):
        print("계좌평가 잔고내역 요청하기 연속조회 %s" sPrevNext)
        self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num)  # 인적사항 기입
        self.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(String, String)", "조회구분", "2")
        self.dynamicCall("CommRqData(String, String, int, String)", "계좌평가잔고내역요청", "opw00018", sPrevNext, "2000")

        self.detail_account_info_event_loop_2.exec_()

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
            self.use_money = int(deposit) * self.use_money_percent
            self.use_money = self.use_money / 4

            ok_deposit = self.dynamicCall("GetCommDate(String,String,int,String)", sTrCode, sRQName, 0, "출금가능금액") #데이터를 요청해서 받으면, 그것들이 데이터루프에 걸려있고, 그것을 저장소에서 꺼내와서 사용한다?
            print("출금가능금액 %s" % ok_deposit)
            print("출금가능금액 형변환 %s" % int(ok_deposit))

            #이벤트 루프 끊기
            self.detail_account_info_event_loop.exit()
            # 위의 작업이 끝난뒤에 다른 작업들이 시작된다.

        if sRQName == "계좌평가잔고내역요청":

            total_buy_money = self.dynamicCall("GetCommDate(String, String, int, String)", sTrCode, sRQName, 0, "총매입금액")
            total_buy_money_result = int(total_buy_money)

            print("총매입금액 %s" % total_buy_money_result)

            total_profit_loss_rate = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "총수익률(%)")
            total_profit_rate_result = float(total_profit_loss_rate)

            print("총수익률(%%) : %s" % total_profit_loss_rate_result)

            # GetRepeaetCnt == 멀티데이터 조회 용도, 키움Open Api에 TR목록에서 확인가능 , 총 20종목 조회가능 , 그 다음 페이지 20종목
            rows = self.dynamicCall("GetRepeaetCnt(QString, QSting", sTrCode,sRQName)
            cnt = 0
            for i in range(rows): #가져올 데이터들 만들어주기
                code = self.dynamicCall("GetCommData(QString, QString, int, QString", sTrCode, sRQName, i, "종목번호")
                code = code.strip()[1:]

                code_nm = self.dynamicCall("GetCommDate(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString", sTrCode, sRQName, i, "보유수량")
                buy_price = self.dynamicCall("GetCommData(QString, QString, int, QString", sTrCode, sRQName, i, "매입가")
                learn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString", sTrCode, sRQName, i, "수익률(%)")
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString", sTrCode, sRQName, i, "현재가")
                total_chegual_price = self.dynamicCall("GetCommData(QString, QString, int, QString", sTrCode, sRQName, i, "매입금액")
                possible_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString", sTrCode, sRQName, i, "매매가능수량")

                # 딕셔너리에 아래서 가공한 데이터들을 저장하기
                if code in self.account_stock_dict:
                    pass
                else:
                    self.account_stock_dict.update({code:{}})

                # 가져오는 데이터들 보기좋게, 깔끔하게 가져오기 위해서
                code_nm = code_nm.strip()
                stock_quantity = int(stock_quantity.strip())
                buy_price = int(buy_price.strip())
                learn_rate = float(learn_rate.strip())
                current_price = int(current_price.strip())
                total_chegual_price = int(total_chegual_price.strip())
                possible_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매매가능수량")

                self.account_stock_dict[code].update({"종목명":code_nm})
                self.account_stock_dict[code].update({"종목명":stock_quantity})
                self.account_stock_dict[code].update({"종목명":buy_price})
                self.account_stock_dict[code].update({"종목명":learn_rate})
                self.account_stock_dict[code].update({"종목명":current_price})
                self.account_stock_dict[code].update({"종목명":total_chegual_price})
                self.account_stock_dict[code].update({"종목명":possible_quantity})

                cnt += 1

            print("계좌에 가지고 있는 종목 %s" % self.account_stock_dict)
            print("계좌에 보유종목 카운트 %s" % cnt)

            # 종목의 수가 20개가 넘어가면 sPrevNext가 "2"로 표시된다.
            # 종목 20개당 페이지 수 의 표시 > sPrevNext
            if sPrevNext == "2":
                self.detail_account_mystock(sPrevNext="2")
            else:
                self.detail_account_info_event_loop_2.exit()



