import xml.etree.ElementTree as elemTree
import base64
from bs4 import BeautifulSoup

XML_PATH = '/Users/dongyeon/Desktop/test.xml'
TEMPLATE_HTML_PATH = 'template.html'

tree = elemTree.parse(XML_PATH)
root = tree.getroot()


def base64_decode(data):
    """
    base64 decode
    """

    return base64.b64decode(data).decode('utf-8')


def get_template_html():
    """
    결과를 작성하는 HTML에 사용되는 템플릿 HTML 데이터를 읽어 반환
    """

    with open(TEMPLATE_HTML_PATH, 'r') as f:
        content = ''.join(f.readlines())

    return content


def parse_xml(xml_tree):
    """
    xml 파일에서 결과 HTML 작성에 필요한 정보를 파싱
    """

    info_rows = []

    for item in xml_tree.findall('./item'):

        row = {}

        # base64로 처리된 부분을 디코딩
        for base64_item in item.findall('./*[@base64="true"]'):
            base64_data = base64_item.text
            base64_item.text = base64_decode(base64_data)

        host = item.find('./host').text or ""
        row['ip'] = item.find('./host').attrib.get('ip', '') or ""
        row['port'] = item.find('./port').text or ""
        row['url'] = item.find('./url').text or ""
        row['path'] = item.find('./path').text or ""
        row['method'] = item.find('./method').text or ""
        row['status'] = item.find('./status').text or ""
        row['responselength'] = item.find('./responselength').text or ""
        row['mimetype'] = item.find('./mimetype').text or ""
        row['extension'] = item.find('./extension').text or ""
        row['time'] = item.find('./time').text or ""
        row['request'] = item.find('./request').text or ""
        row['response'] = item.find('./response').text or ""

        # host 설정
        if host:
            if row['port'] == '80':
                row['host'] = f'http://{host}'
            elif row['port'] == '443':
                row['host'] = f'https://{host}'
            else:
                row['host'] = f'http://{host}:{row["port"]}'

        info_rows.append(row)

    return info_rows


def set_result_html(xml_data):
    """
    xml 파일에서 추출한 데이터를 사용하여 결과 HTML를 만듦
    """

    # 템플릿의 html 설정을 위해 객체를 가져온다.
    soup = BeautifulSoup(get_template_html(), "html.parser")
    info_in_table = soup.html.body.table.tbody

    # Table의 Index 목록
    index_td = soup.html.body.table.tbody.tr.find_all('td')
    index_list = [td.text for td in index_td]

    # 1번 Row부터 설정
    for idx, item in enumerate(xml_data, start=1):

        # 각 Item의 기본적인 정보(request, reasponse 제외)를 저장하는 부분
        basic_info = soup.new_tag('tr')
        basic_info.attrs['onclick'] = 'show_detail(this)'
        basic_info.attrs['id'] = f'row-{idx}'

        for index in index_list:
            temp = soup.new_tag("td")
            temp.string = item.get(index)
            basic_info.append(temp)

        basic_info.append(soup.new_tag("td"))

        # [각 Item의 request 정보를 저장하는 부분]
        request_info = soup.new_tag("tr")
        request_info.attrs['class'] = 'request'

        # request 정보가 작성되는 div tag를 감싸는 td tag
        temp_td = soup.new_tag("td")
        temp_td.attrs['class'] = 'hide'
        temp_td.attrs['colspan'] = '100%'
        temp_td.attrs['id'] = f'row-{idx}-request'

        # request 정보가 작성되는 div tag
        temp_div = soup.new_tag("div")
        temp_div.string = item.get('request')

        # td tag에 div tag 추가
        temp_td.append(temp_div)

        # request 정보 추가
        request_info.append(temp_td)

        # [각 Item의 response 정보를 저장하는 부분]
        response_info = soup.new_tag("tr")
        response_info.attrs['class'] = 'response'

        # request 정보가 작성되는 div tag를 감싸는 td tag
        temp_td = soup.new_tag("td")
        temp_td.attrs['class'] = 'hide'
        temp_td.attrs['colspan'] = '100%'
        temp_td.attrs['id'] = f'row-{idx}-response'

        # request 정보가 작성되는 div tag
        temp_div = soup.new_tag("div")
        temp_div.string = item.get('response')

        # td tag에 div tag 추가
        temp_td.append(temp_div)

        # request 정보 추가
        response_info.append(temp_td)

        # 하나의 ITEM에 대한 정보 추가
        info_in_table.append(basic_info)
        info_in_table.append(request_info)
        info_in_table.append(response_info)

    return soup


# xml에서 Item에 대한 정보를 얻는다.
xml_data = parse_xml(tree)

# 결과가 작성된 html 코드 내용을 가져온다.
result = set_result_html(xml_data)

# 결과를 html 파일로 저장한다.
with open("result.html", "w") as file:
    file.write(str(result))
