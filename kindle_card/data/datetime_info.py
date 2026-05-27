from datetime import datetime

WEEKDAYS = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]


def fetch() -> dict:
    now = datetime.now()
    return {
        "time": now.strftime("%H:%M"),
        "date": now.strftime("%Y年%m月%d日"),
        "weekday": WEEKDAYS[now.weekday()],
    }
