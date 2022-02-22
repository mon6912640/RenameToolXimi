import re
import shutil
import sys
from pathlib import Path

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMainWindow, QApplication

from gui.main import *
from monkey_event import *

EVENT_LOG = 'event_log'


def show_log(pstr):
    EventCenterSync.send_event(EVENT_LOG, pstr)


def run(spath, tpath):
    path_source = Path(spath)
    path_target = Path(tpath)

    list_files = sorted(path_source.rglob('**/*'))
    run_flag = False
    for v in list_files:
        if v.is_dir():
            if re.match(r'd\d+', v.stem):  # 匹配d+数字的文件夹
                path_result = path_target.joinpath(v.parent.stem).joinpath(v.stem)
                # print(v.stem, v.parent.stem, path_result)
                png_results = []
                list_dir = list(v.glob('stand'))
                if len(list_dir) > 0:
                    mydir = list_dir[0]
                    list_pngs = sorted(mydir.glob('*.png'))
                    if len(list_pngs) > 0:
                        png_results += list_pngs

                list_dir = list(v.glob('run'))
                if len(list_dir) > 0:
                    mydir = list_dir[0]
                    list_pngs = sorted(mydir.glob('*.png'))
                    if len(list_pngs) > 0:
                        png_results += list_pngs

                list_dir = list(v.glob('attack'))
                if len(list_dir) > 0:
                    mydir = list_dir[0]
                    list_pngs = sorted(mydir.glob('*.png'))
                    if len(list_pngs) > 0:
                        png_results += list_pngs
                # print(png_results)

                if len(png_results) > 0:
                    for i in range(len(png_results)):
                        run_flag = True
                        if not path_result.exists():
                            path_result.mkdir(parents=True, exist_ok=True)
                        png_target = path_result.joinpath(str(i + 1) + '.png')
                        shutil.copy(str(png_results[i]), png_target)

    if run_flag:
        return True
    else:
        return False


class MyMainWin(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(MyMainWin, self).__init__()
        self.setupUi(self)
        self.setAcceptDrops(True)
        self.areaShow.setOpenLinks(False)
        self.areaShow.setOpenExternalLinks(False)

        self.areaShow.anchorClicked.connect(self.on_anchor_clicked)

        EventCenterSync.add_event(EVENT_LOG, self.handle_show_log)

    def on_anchor_clicked(self, url: QUrl):
        QDesktopServices.openUrl(url)

    def dragEnterEvent(self, event: QDragEnterEvent):
        mime_data: QMimeData = event.mimeData()
        if mime_data.hasFormat('text/uri-list'):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        pass

    def dropEvent(self, event: QDropEvent):
        mime_data: QMimeData = event.mimeData()
        files: List[QUrl] = mime_data.urls()
        for url in files:
            path_source = Path(url.toLocalFile())
            if not path_source.exists():
                continue
            if path_source.is_dir():
                # print(path_source.parent)
                self.show_log('来源：' + str(path_source))
                ptarget = path_source.parent.joinpath('copy_rename')
                if run(path_source, ptarget):
                    self.show_log('......转换成功')
                    if ptarget.is_absolute():
                        file_url = ptarget.as_uri()
                    else:
                        file_url = str(ptarget)
                    self.show_log('......生成路径：' + '<a href="{0}">{1}</a>'.format(file_url, str(ptarget)))
                else:
                    self.show_log('<font color="#ff0000">......没有可转换的文件</font>')

    def handle_show_log(self, event: EventVo):
        # print('handle_show_log == '+event.type)
        self.show_log(event.data)

    def show_log(self, p_str: str):
        self.areaShow.append(p_str.encode('utf-8').decode('utf-8'))


if __name__ == '__main__':
    # # source = 'C:\\Users\\Administrator\\Desktop\\test'
    # # target = 'C:\\Users\\Administrator\\Desktop\\test1'
    # run(source, target)
    app = QApplication(sys.argv)

    main_win = MyMainWin()
    main_win.show()
    main_win.setWindowTitle('动作帧重命名工具')

    sys.exit(app.exec_())
