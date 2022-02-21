import argparse
import re
import shutil
import sys
from pathlib import Path


def run(spath, tpath):
    path_source = Path(spath)
    path_target = Path(tpath)

    list_files = sorted(path_source.rglob('**/*'))
    run_flag = False
    for v in list_files:
        if v.is_dir():
            if re.match('d\d+', v.stem):  # 匹配d+数字的文件夹
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

                for i in range(len(png_results)):
                    run_flag = True
                    if not path_result.exists():
                        path_result.mkdir(parents=True, exist_ok=True)
                    png_target = path_result.joinpath(str(i + 1) + '.png')
                    shutil.copy(str(png_results[i]), png_target)
    if run_flag:
        print('成功运行')
    else:
        print('没有可转换的文件')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='帮助信息')
    parser.add_argument('--source', type=str, default='', help='源路径')
    parser.add_argument('--output', type=str, default='', help='输出路径')
    args = parser.parse_args()

    source = args.source
    target = args.output

    path_app = Path(sys.argv[0]).parent
    print(path_app)

    if not source:
        source = path_app

    if not source:
        print('无指定源路径，程序结束')
        sys.exit()

    if not target:
        target = Path(source).joinpath('copy')

    # source = 'C:\\Users\\Administrator\\Desktop\\test'
    # target = 'C:\\Users\\Administrator\\Desktop\\test1'
    run(source, target)
