import requests
import datetime
import os
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

load_dotenv(".env")

# 時間をHH:mm:ss形式に変換する関数を定義します
def format_duration(duration, symbol=False):
  seconds = duration // 1000
  minutes, seconds = divmod(seconds, 60)
  hours, minutes = divmod(minutes, 60)
  return f'{"+" if symbol and duration > 0 else ""}{int(hours):d}:{int(minutes):02d}:{int(seconds):02d}'

def get_api_records(params):
  data = []
  page = 1
  while True:
    params['page'] = page
    response = requests.get(toggl_api_endpoint, auth=(api_key, 'api_token'), params=params)
    page_data = response.json()
    data.extend(page_data['data'])
    if not page_data['data']:
      break
    page += 1
  return data, sum([entry['dur'] for entry in data])

# 各プロジェクトの作業時間の割合と、先週の作業時間との差を計算します
def calculation_project_ratios(projects_data):
  project_work_time_ratios_and_differences = []
  for project_id, work_time in projects_data:
    work_time_ratio = work_time["dur"] / total_work_time
    params['project_ids'] = project_id  # プロジェクトIDを指定します
    response = requests.get(toggl_api_endpoint, auth=(api_key, 'api_token'), params=params)
    data = response.json()
    last_week_project_work_time = data["total_grand"]
    work_time_project_difference = work_time["dur"] - (0 if last_week_project_work_time is None else last_week_project_work_time)
    project_work_time_ratios_and_differences.append((project_id, work_time["dur"], work_time_ratio, work_time_project_difference, work_time["name"]))
  return project_work_time_ratios_and_differences

# Toggl APIのエンドポイントとAPIキーを設定します
toggl_api_endpoint = "https://api.track.toggl.com/reports/api/v2/details"
toggl_projects_endpoint = "https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/projects"  # バージョン9を使用します
api_key = os.getenv("TOGGL_APIKEY")

# 先週の土曜日と今週の金曜日の日付を取得します
today = datetime.date.today()
last_saturday = today - datetime.timedelta(days=today.weekday() + 2)
this_friday = last_saturday + datetime.timedelta(days=6)

# リクエストパラメータを設定します
params = {
  'user_agent': 'api_test',
  'workspace_id': os.getenv("TOGGL_WORKSPACEID"),  # ワークスペースIDを指定します
  'since': last_saturday.isoformat(),
  'until': this_friday.isoformat()
}

# Toggl APIからデータを取得します
week_data, total_work_time = get_api_records(params)

# 先週の土曜日から先週の金曜日までの間との総作業時間の差を計算します
# ここでは、先週の作業時間を取得するために同じAPIリクエストを再度行い、日付範囲を変更します
params['since'] = (last_saturday - relativedelta(weeks=1)).isoformat()
params['until'] = (this_friday - relativedelta(weeks=1)).isoformat()
last_week_data, last_week_work_time = get_api_records(params=params)
work_time_difference = total_work_time - last_week_work_time

# 1の7分の1の値を計算します
one_seventh_work_time = total_work_time / 7

# 3の前週との差を計算します
# ここでは、先週の作業時間の7分の1を計算します
last_week_one_seventh_work_time = last_week_work_time / 7
one_seventh_work_time_difference = one_seventh_work_time - last_week_one_seventh_work_time

# プロジェクト単位で実行した作業時間が多いもの上位三件の作業時間、および、作業時間の割合を計算します
# また、先週の土曜日から先週の金曜日までのそのプロジェクトの作業時間との差を計算します
# ここでは、プロジェクトごとの作業時間を計算し、上位3つのプロジェクトを取得します
project_work_times = {}
for entry in week_data:
  if entry["project"] != "雑務":
    project_id = entry['pid']  # プロジェクトIDを使用します
    if project_id not in project_work_times:
      project_work_times[project_id] = {"name": entry["project"], "dur": 0}
    project_work_times[project_id]["dur"] += entry['dur']
top_projects = sorted(project_work_times.items(), key=lambda x: x[1]["dur"], reverse=True)[:3]
worst_projects = sorted(project_work_times.items(), key=lambda x: x[1]["dur"], reverse=False)[:3]

project_work_time_ratios_and_differences = calculation_project_ratios(top_projects)
under_project_work_time_ratios_and_differences = calculation_project_ratios(worst_projects)

# 結果を出力します
print(f"{last_saturday:%Y年%m月%d日}から{this_friday:%Y年%m月%d日}までのレポート")
print('ワークスペースの総作業時間:', f"{format_duration(total_work_time)}({format_duration(work_time_difference, True)})")
print('平均:', f"{format_duration(one_seventh_work_time)}({format_duration(one_seventh_work_time_difference, True)})")
for caption, projects in [["上位", project_work_time_ratios_and_differences], ["下位", under_project_work_time_ratios_and_differences]]:
  print(f'{caption}三件:')
  for project_id, work_time, work_time_ratio, work_time_project_difference, project_name in projects:
    print(f"{project_name}: {format_duration(work_time)}({format_duration(work_time_project_difference, True)})  {work_time_ratio:.2%}") 
