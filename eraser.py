import os
import sys
import shutil
import re
from datetime import datetime

work_dir, month, dir_list = None, None, None


def usage():
    print("\n>>>   Usage : python eraser.py path month except_dir")
    print(">>> Example : python eraser.py D:\TestDirectory 5 ABC,DEF")
    print("\nStart directory must be root directory")
    print("If you have 'except directory', make argument using ',' without any space")
    print("like dir1,dir2,dir3,...")
    sys.exit()


# argument parsing
def parse(arg):
    directory = arg[1]
    mon = arg[2]
    if len(arg) == 4:
        ex_dir = arg[3]
        d_list = ex_dir.split(',')
        lower_d_list = [i.lower() for i in d_list]
    else:
        lower_d_list = None

    return directory, mon, lower_d_list


# move to working directory
def change_dir(directory):
    if os.path.isdir(directory):
        os.chdir(directory)  # check directory is exist
        print("-"*10, "Moved directory to", directory)
    else:
        print("-"*10, "There is no '{0}' directory".format(directory))


# 네자리 숫자(연도) 이름의 디렉토리 리턴
def year_directory_check(a):
    regex = re.compile(r'\d\d\d\d')
    mo = regex.search(a)
    if mo:
        return mo.group()


# 두자리 숫자(월) 이름의 디렉토리 리턴
def month_directory_check(a):
    regex = re.compile(r'\d\d')
    mo = regex.search(a)
    if mo:
        return mo.group()


# make month directory path to string
def make_path(cur_dir, mon):
    if len(mon) < 2:
        mon = "0" + mon
        path = os.path.join(cur_dir, mon)
    else:
        path = os.path.join(cur_dir, mon)
    return path


# 연도별 디렉토리 제거
def year_remove(today_year, today_month, year_list, over):
    for year in year_list:
        if int(year) < today_year:
            year_path = os.path.join(work_dir, year)
            change_dir(year_path)

            directory_list = next(os.walk(year_path))[1]  # 현재 디렉토리의 서브 디렉토리 목록
            month_list = list(filter(month_directory_check, directory_list))
            for mon in month_list:
                path = make_path(year_path, mon)
                remove(path)
        elif int(year) == today_year:
            year_path = os.path.join(work_dir, str(year))
            change_dir(year_path)
            month_remove(today_month, year_path, over)


# 월별 디렉토리 제거
def month_remove(today_month, year_path, over):
    if over:  # 작년으로 넘어가서 삭제할 경우
        check_month = 12 - int(month) + today_month
    else:  # 올해 안에서 삭제할 경우
        check_month = today_month - int(month)
    directory_list = next(os.walk(year_path))[1]  # 현재 디렉토리의 서브 디렉토리 목록
    month_list = list(filter(month_directory_check, directory_list))  # 서브 디렉토리 중 두자리 숫자의 디렉토리만 필터링
    for mon in month_list:
        if int(mon) < check_month:
            path = make_path(year_path, mon)
            remove(path)


# remove directory
def remove(path):
    print("Remove directory:", path)  # 지우는 디렉토리는 월 단위 디렉토리
    temp_list = list()  # 임시로 저장할 디렉토리 리스트
    save_list = list()  # 저장해야할 디렉토리 리스트
    if os.path.isdir(path):
        if dir_list:
            temp_list, save_list = compare(path)
        shutil.rmtree(path)
        print("Removal Success\n")
    else:
        print("error: There is no '{0}' directory".format(path))
        sys.exit()

    if len(temp_list):
        make_folder(temp_list, save_list)
        print("Copy Success\n")


def compare(folder):
    temp_list = list()
    save_list = list()
    directory_list = next(os.walk(folder))[1]  # 월 폴더에 있는 디렉토리 리스트
    day_list = list(filter(month_directory_check, directory_list))  # 월 폴더에 있는 일 폴더 리스트
    for day in day_list:
        day_dir = make_path(folder, day)
        dir_list_in_day = next(os.walk(day_dir))[1]
        if len(dir_list_in_day):
            lower_dirs = [i.lower() for i in dir_list_in_day]
            for d in lower_dirs:
                if d in dir_list:
                    save_dir = os.path.join(day_dir, d)
                    temp = saving(day_dir, save_dir, d)
                    temp_list.append(temp)
                    save_list.append(day_dir)
    return temp_list, save_list


# save except directory to temporary folder
def saving(path, save_dir, d):
    temp = path.split('\\')  # current directory parsing
    temp_list = temp[len(temp)-2] + temp[len(temp)-1]
    temp_dir = os.path.join(work_dir, temp_list, d)
    shutil.copytree(save_dir, temp_dir)
    print("Save folder:", save_dir, "to:", temp_dir)
    return temp_dir


def make_folder(temp_list, save_list):
    length = len(temp_list)
    tmp_list = list()
    for temp in range(length):
        tar_list = temp_list[temp].split('\\')
        tar = tar_list[len(tar_list) - 1]
        target = os.path.join(save_list[temp], tar)  # 타겟 디렉토리 주소

        save_dir = save_list[temp].split('\\')
        mon = save_dir[len(save_dir)-2]
        mon_dir = os.path.join(os.getcwd(), str(mon))  # 저장된 월 주소
        day = save_dir[len(save_dir)-1]
        day_dir = os.path.join(os.getcwd(), str(mon), str(day))  # 저장된 일 주소

        if os.path.isdir(day_dir):
            pass
        elif os.path.isdir(mon_dir):
            os.mkdir(day_dir)
        else:
            os.mkdir(mon_dir)
            os.mkdir(day_dir)

        shutil.copytree(temp_list[temp], target)
        shutil.rmtree(temp_list[temp])
        print("Copy Success from", temp_list[temp], " to", save_list[temp])
        tmp = tar_list[len(tar_list) - 2]
        tmp_list.append(tmp)

    # 임시로 만들었던 디렉토리 제거
    tmp_set = set(tmp_list)
    tmp_list = list(tmp_set)
    for i in tmp_list:
        tmp_dir = os.path.join(work_dir, i)
        shutil.rmtree(tmp_dir)


def main():
    global work_dir, month, dir_list

    if len(sys.argv) < 3 or len(sys.argv) > 4:  # check argument length
        usage()
    else:  # argument parsing
        work_dir, month, dir_list = parse(sys.argv)
        print("\nWorking directory: {0}\nRemove month: {1}\n"
              "Except directory: {2}\n".format(work_dir, month, dir_list))

    print("-------- Current directory is", os.getcwd())
    change_dir(work_dir)  # move to working directory

    today_month = datetime.today().month
    today_year = datetime.today().year

    directory_list = next(os.walk(work_dir))[1]  # 현재 디렉토리의 서브 디렉토리 목록
    year_list = list(filter(year_directory_check, directory_list))  # 서브 디렉토리 중 네자리 숫자의 디렉토리만 필터링

    if today_month > int(month):  # 현재 월이 살려둬야 하는 월보다 클경우
        year_remove(today_year, today_month, year_list, 0)
    else:
        today_year -= 1
        year_remove(today_year, today_month, year_list, 1)

    print("Process is done")


if __name__ == "__main__":
    main()
