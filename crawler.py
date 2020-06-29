from time import sleep
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
import time
import csv

# 미니 프로젝트 
# written by 박재균

# 클래스 형태로 크롤러를 제작합니다.
# 각 기능별로 상세하게 메소드로 분리 후 역할에 맞게 작성합니다.

# 커뮤니티 사이트 <웃긴대학>에서 웃긴자료 게시판에 대한 크롤링 & 스크래핑!
# <웃긴대학>는 먼저 대기자료게시판에 자료가 올라오게 되고,
# 일정 추천수를 받으면 웃긴자료게시판으로 넘어가게 된다.

# 많은 사람들의 관심을 받아 웃긴자료게시판으로 넘어온 자료들의
# 제목, 댓글수, 작성자, 웃긴자료게시판으로의 등록날짜시각, 조회수, 추천수, 반댓수 등을 수집한다. 

# 단편성 크롤링이 아닌 페이지 내 이동 규칙을 적용해서 소스코드 작성을 부탁드립니다.
# 크롤링 결과는 본인이 원하는 파일 포멧(CSV, TXT, JSON)등으로 꼭 저장해 봅니다.
# ★예외 처리는 최소화★로 작성했습니다.
# 특히 ★마지막 페이지가 없는 경우★는 조건문으로 처리를 꼭 해주셔야 합니다.
class HumorUnivCrawler(object):

	# <웃긴대학> 커뮤니티 사이트의 경우, 파이썬 웹 크롤러로 DOM 에 접근하는 것을 허용하지 않는다.
	# 따라서, "브라우저를 통해 요청을 하는 것"처럼 보이도록 header 를 통해 약간의 속임이 필요하다.
	headers = {
		"User-Agent" : UserAgent().chrome,
	}
	
	# 초기화
	def __init__(self):
		# 웃긴대학의 웃긴자료게시판의 기본적인 URL 형태
		self.target_url = 'http://web.humoruniv.com/board/humor/list.html?table=pds&pg='
		# 웃긴자료게시판에는 일정 추천수를 넘긴 시점의 역순으로 게시글이 배치된다.
		# 크롤링 범위는 기본적으로 게시판의 1페이지부터 2, 3, ... 식으로 해서
		# 점점 더 과거의 자료(정확히는, 더 과거에 웃긴자료로 승격된 자료)로 거슬러 올라가는 형식을 취한다. 
		self.range = {'s_page': 0, 'e_page': 1}


	# 범위 지정
	# 인스턴스 변수로 초기화된 크롤링 범위와 다르게 설정할 경우
	def set_page_range(self, s_page, e_page):
		self.range['s_page'] = s_page - 1
		self.range['e_page'] = e_page - 1
	
	
	# 크롤링
	@staticmethod
	def crawling(self):
		# 수집 데이터 전체 저장
		post_list = []

		# 시작페이지 -> 끝 페이지
		for number in range(self.range['s_page'], self.range['e_page'] + 1):
			# 페이지 URL 완성
			URL = self.target_url + str(number)
			
			# 페이지 수 및 URL 확인
			print("="*10, number+1, "Page", "="*10)
			print("URL :", URL)
			
			# 실제 요청
			# Chrome 브라우저를 통해 요청을 보내는 것처럼 header 를 조작하였다.
			response = requests.get(URL, headers=HumorUnivCrawler.headers)
			# 한국어 출력을 위한 인코딩 설정
			response.encoding = "euc-kr"
			
			assert response.status_code == 200
			
			# 수신 데이터 확인(주석 해제 후 확인)
			# 수신 헤더 정보
			# print(response.headers)
			# 수신 인코딩 정보
			# print(response.encoding)
			# 수신 데이터 수신 OK
			# print(response.ok)
			# 수신 컨텐츠 정보
			# print(response.content)
			# 수신 텍스트
			# print(response.text)
			
			# bs4 선언 및 파싱
			soup = BeautifulSoup(response.text, 'html.parser')
			
			# 이 부분에서 본인이 원하는 내용을 파싱
			# 제목, 댓글수, 작성자, 웃긴자료게시판으로의 등록날짜시각, 조횟수, 추천수, 반댓수
			# 각 파싱데이터를 클릭하면 해당 글로 이동

			# 게시판 영역
			board_area = soup.select('#cnts_list_new > div:nth-child(1) > table:nth-child(3) > tr')
			# 게시판 한페이지에서 맨 마지막에 항상 빈 <tr> 태그가 존재하는데 이를 빼준다.
			board_area = board_area[:-1]

			# 각 부분 파싱
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
				# 조횟수
				cnt_visited = post.select('td:nth-child(5)')[0].text.strip()
				# 추천수
				cnt_loveit = post.select('td:nth-child(6) span')[0].text
				# 반댓수
				cnt_hateit = post.select('td:nth-child(7) font')[0].text

				# 각 정보추출 확인
				# print(title, cnt_reply, writer, date, time, cnt_visited, cnt_loveit, cnt_hateit)
				
				# 각 글의 정보 담기
				post_list.append([title, cnt_reply, writer, date+" "+time, cnt_visited, cnt_loveit, cnt_hateit])
		
		print(len(post_list))

		# CSV 파일 저장
		self.export_csv(post_list)
	
	# 파일 저장
	def export_csv(self, args):
		# CSV 파일 쓰기
		# 관리자 권한 확인(윈도우), 본인이 원하는 경로 및 파일명 지정
		# Mac 일 경우, encoding = 'utf-8' 로 할 것
		with open('./result_post.csv', 'w', newline='', encoding='utf-8') as f:
			# Writer 객체 생성 
			wt = csv.writer(f)
			wt.writerow(["글제목", "댓글수", "작성자명", "등록날짜시각", "조횟수", "추천수", "반댓수"])
			# Tuple to Csv
			for c in args:
				wt.writerow(c)
	
	# 시작
	def start(self):
		HumorUnivCrawler.crawling(self)


if __name__ == "__main__":
	# 클래스 생성
	crawler = HumorUnivCrawler()
	# 크롤링 페이지 범위 설정
	crawler.set_page_range(1, 20)
	# 크롤링 시작
	crawler.start()