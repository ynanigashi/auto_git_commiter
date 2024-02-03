import os
import configparser
import subprocess
import datetime

def main():
    # 設定ファイルの読み込み
    config = load_config()
    target_dir = config['DEFAULT']['target_dir']
    
    # ディレクトリの移動
    os.chdir(target_dir)
    
    # git statusコマンドを実行
    result = subprocess.run(["git", "status"], capture_output=True, text=True)
    result_stdout = result.stdout
    
    # 対象ファイルを取得
    modified_files = get_modified_today_file(result_stdout)
    added_files = get_added_file_with_today_str(result_stdout)
    if len(modified_files) == 0 and len(added_files) == 0:
        return 0

    # git addコマンドを実行
    commit_files = modified_files + added_files
    print(commit_files)
    for file in commit_files:
        subprocess.run(["git", "add", file])

    # commit commentの作成
    comment = generate_commit_comment(modified_files, added_files)
    print(comment)

    # git commitコマンドを実行
    subprocess.run(["git", "commit", "-m", comment])
    
    # git pushコマンドを実行
    result = subprocess.run(["git", "push"], capture_output=True, text=True)
    print(result.stdout)


def load_config():
    # 設定ファイルの読み込み
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    return config

def get_modified_today_file(result):
    # git statusの結果から、本日更新されたファイルを取得
    lines = result.splitlines()
    today = datetime.date.today()
    files = []
    for line in lines:
        if 'modified:' in line:
            modified_file = line.split(':')[1].strip()
            modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(modified_file))
            if modified_time.date() == today:
                files.append(modified_file)
    return files

def get_added_file_with_today_str(result):
    # git statusの結果から、本日の名前が付いたファイルを取得
    lines = result.splitlines()
    today = datetime.datetime.today().strftime('%Y%m%d')
    files = []
    # check untracked files line
    Untracked_files_line = 0
    for i in range(len(lines)):
        if 'Untracked files:' in lines[i]:
            Untracked_files_line = i
            break
    
    # Untracked files:以下の行からファイル名を取得
    for line in lines[Untracked_files_line:]:
       
        if today in line:
            file = line.strip()
            files.append(file)
                
    return files


def generate_commit_comment(modified_files, added_files):
    # コミットコメントを生成
    comment = ''
    if len(modified_files) > 0:
        comment += 'Modified file: ' + ', '.join(modified_files)
    if len(added_files) > 0:
        if len(modified_files) > 0:
            comment += '; '
        comment += generate_solved_str(added_files)
    return comment


def generate_solved_str(added_files):
    # コミットコメントに追加する解いた問題の文字列を生成
    solved_str = 'solved: '
    solved_problems = {}
    for file in added_files:
        file_name = file.split('/')[-1]
        contest_name = file_name.split('_')[0]
        problem = file_name.split('_')[1]
        contest_number = problem.split('-')[0]
        problem = problem.split('-')[1]

        if contest_name not in solved_problems:
            solved_problems[contest_name] = {contest_number: [problem]}
        elif contest_number not in solved_problems[contest_name]:
            solved_problems[contest_name][contest_number] = [problem]
        else:
            solved_problems[contest_name][contest_number].append(problem)

    for contest in solved_problems:
        for contest_number in solved_problems[contest]:
            solved_str += contest + contest_number + ' '
            solved_str += ', '.join(solved_problems[contest][contest_number])
            solved_str += '; '

    return solved_str


if __name__ == "__main__":
    main()