#!flask/bin/python
from app import app
import config
from app import wx
from app import views  # 初始化views用，不可删除


# app.run(debug=config.DEBUG, host='0.0.0.0', port='9790')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.S_PORT, debug=config.DEBUG)
