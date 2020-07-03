import csv
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup


class HumorUnivCrawler(object):
    BASE_URL = 'http://web.humoruniv.com/board/humor/list.html?table=pds&pg='

    def __init__(self):
        self.range = {'s_page': 0, 'e_page': 1}
        self.headers = {'User-Agent': UserAgent().chrome}

    def set_page_range(self, s_page, e_page):
        """
        데이를 수집할 페이지의 범위를 설정합니다.

        s_page: 시작 페이지
        e_page: 종료 페이지
        인스턴스 변수로 초기화된 크롤링 범위와 다르게 설정할 경우 전달 받은 인자로 페이지 범위를 재설정합니다.
        """
        self.range['s_page'] = s_page - 1
        self.range['e_page'] = e_page - 1

    def crawling(self):
        """ 데이터를 수집할 페이지를 페이지 단위로 순회하며 데이터를 수집합니다. """
        post_list = []

        # 수집 페이지를 페이지 단위 순회
        for number in range(self.range['s_page'], self.range['e_page'] + 1):
            target_url = self.BASE_URL + str(number)

            # 페이지 수 및 URL 확인
            print(f'========== {number + 1} ==========')
            print(f'URL :{self.BASE_URL}')

            # 파이썬 크롤러를 허용하지 않으므로 가상 UserAgent 적용
            response = requests.get(target_url, headers=self.headers)
            response.encoding = "euc-kr"

            assert response.status_code == 200

            soup = BeautifulSoup(response.text, 'html.parser')

            # 게시판 영역 설정
            board_area = soup.select('#cnts_list_new > div:nth-child(1) > table:nth-child(3) > tr')
            board_area = board_area[:-1]  # 게시판 한페이지에서 맨 마지막에 항상 빈 <tr> 태그가 존재하는데 이를 빼준다.

            # 게시판 영역별 파싱
            for post in board_area:
                # 글제목 및 댓글수
                title_area = post.select('td:nth-child(2) a')[0].contents
                title = title_area[0].strip()
                cnt_reply = title_area[1].text.strip().replace("[", "").replace("]", "")

                # 작성자명
                writer = post.select('.hu_nick_txt')[0].text

                # 웃긴자료게시판으로의 등록날짜 및 시간
                datetime_area = post.select('td:nth-child(4) span')
                date = datetime_area[0].text
                time = datetime_area[1].text

                # 조회수, 추천수, 반댓수
                cnt_visited = post.select('td:nth-child(5)')[0].text.strip()
                cnt_loveit = post.select('td:nth-child(6) span')[0].text
                cnt_hateit = post.select('td:nth-child(7) font')[0].text

                # 각 글의 정보 담기
                post_list.append([
                    title, cnt_reply, writer, f'{date} {time}', cnt_visited, cnt_loveit, cnt_hateit
                ])

        # 전체 게시물 수 확인
        print(len(post_list))

        self.export_csv(post_list)

    @staticmethod
    def export_csv(args):
        """
        전달받은 게시물 목록을 순회하며 csv 형식의 파일을 작성하고 저장합니다.

        :param args: 전체 게시물 목록
        """
        with open('./result_post.csv', 'w', newline='', encoding='euc-kr') as f:
            wt = csv.writer(f)
            wt.writerow(['글제목', '댓글수', '작성자명', '등록날짜시각', '조횟수', '추천수', '반댓수'])
            for c in args:
                try:
                    wt.writerow(c)
                except:
                    print(c)  # 간혹 EUC-KR 인코딩에 에러가 나는 경우가 있음

    def start(self):
        """ 데이터 수집을 시작합니다. """
        HumorUnivCrawler.crawling(self)


if __name__ == '__main__':
    crawler = HumorUnivCrawler()
    crawler.set_page_range(1, 20)
    crawler.start()
