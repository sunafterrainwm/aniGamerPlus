#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/5 20:23
# @Author  : Miyouzi
# @File    : Config.py
# @Software: PyCharm

import os, json, re, sys, requests, time
from ColorPrint import err_print

working_dir = os.path.dirname(os.path.realpath(__file__))
# working_dir = os.path.dirname(sys.executable)  # 使用 pyinstaller 编译时，打开此项
config_path = os.path.join(working_dir, 'config.json')
sn_list_path = os.path.join(working_dir, 'sn_list.txt')
cookies_path = os.path.join(working_dir, 'cookie.txt')
aniGamerPlus_version = 'v8.1'
latest_config_version = 3.1


def __init_settings():
    if os.path.exists(config_path):
        os.remove(config_path)
    settings = {'bangumi_dir': '',
                'check_frequency': 5,
                'download_resolution': '1080',
                'default_download_mode': 'latest',  # 仅下载最新一集，另一个模式是 'all' 下载所有及日后更新
                'multi-thread': 3,  # 最大并发下载数
                'multi_upload': 3,
                'segment_download_mode': True,  # 由 aniGamerPlus 下载分段, False 为 ffmpeg 下载
                'multi_downloading_segment': 2,  # 在上面配置为 True 时有效, 每个视频并发下载分段数
                'add_bangumi_name_to_video_filename': True,
                'add_resolution_to_video_filename': True,  # 是否在文件名中添加清晰度说明
                'customized_video_filename_prefix': '【動畫瘋】',  # 用户自定前缀
                'customized_video_filename_suffix': '',  # 用户自定后缀
                'use_proxy': False,
                'proxies': {  # 代理功能
                    1: 'socks5://127.0.0.1:1080',
                    2: 'http://user:passwd@example.com:1000'
                },
                'upload_to_server': False,
                'ftp': {  # 将文件上传至远程服务器
                    'server': '',
                    'port': '',
                    'user': '',
                    'pwd': '',
                    'tls': True,
                    'cwd': '',  # 文件存放目录, 登陆后首先进入的目录
                    'show_error_detail': False,
                    'max_retry_num': 15
                },
                'check_latest_version': True,  # 是否检查新版本
                'read_sn_list_when_checking_update': True,
                'read_config_when_checking_update': True,
                'config_version': latest_config_version
                }
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)


def __update_settings(old_settings):  # 升级配置文件
    new_settings = old_settings.copy()
    if 'check_latest_version' not in new_settings.keys():  # v2.0 新增检查更新开关
        new_settings['check_latest_version'] = True

    if 'tls' not in new_settings['ftp'].keys():  # v2.0 新增 FTP over TLS 开关
        new_settings['ftp']['tls'] = True

    if 'upload_to_server' not in new_settings.keys():  # v2.0 新增上传开关
        new_settings['upload_to_server'] = False

    if 'use_proxy' not in new_settings.keys():  # v2.0 新增代理开关
        new_settings['use_proxy'] = False

    if 'show_error_detail' not in new_settings['ftp'].keys():  # v2.0 新增显示FTP传输错误开关
        new_settings['ftp']['show_error_detail'] = False

    if 'max_retry_num' not in new_settings['ftp'].keys():  # v2.0 新增显示FTP重传尝试数
        new_settings['ftp']['max_retry_num'] = 10

    if 'read_sn_list_when_checking_update' not in new_settings.keys():  # v2.0 新增开关: 每次检查更新时读取sn_list
        new_settings['read_sn_list_when_checking_update'] = True

    if 'multi_upload' not in new_settings.keys():  # v2.0 新增最大并行上传任务数
        new_settings['multi_upload'] = 3

    if 'read_config_when_checking_update' not in new_settings.keys():  # v2.0 新增开关: 每次检查更新时读取config.json
        new_settings['read_config_when_checking_update'] = True

    if 'add_bangumi_name_to_video_filename' not in new_settings.keys():  # v3.0 新增开关, 文件名可以单纯用剧集命名
        new_settings['add_bangumi_name_to_video_filename'] = True

    if 'proxies' not in new_settings.keys():  # v3.0 新增代理功能
        new_settings['proxies'] = {1: '', 2: ''}

    if 'proxy' in new_settings.keys():  # v3.0 去掉旧的代理配置
        new_settings.pop('proxy')

    if 'segment_download_mode' not in new_settings.keys():  # v3.1 新增分段下载模式开关
        new_settings['segment_download_mode'] = True

    if 'multi_downloading_segment' not in new_settings.keys():  # v3.1 新增分段下载模式下每个视频并发下载分段数
        new_settings['multi_downloading_segment'] = 2

    new_settings['config_version'] = latest_config_version
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(new_settings, f, ensure_ascii=False, indent=4)
    err_print('配置文件從 v'+str(old_settings['config_version'])+' 升級到 v'+str(latest_config_version)+' 你的有效配置不會丟失!', True)


def __read_settings_file():
    with open(config_path, 'r', encoding='utf-8') as f:
        # 转义win路径
        return json.loads(re.sub(r'\\', '\\\\\\\\', f.read()))


def read_settings():
    if not os.path.exists(config_path):
        __init_settings()

    settings = __read_settings_file()

    if settings['config_version'] < latest_config_version:
        __update_settings(settings)  # 升级旧版配置
        settings = __read_settings_file()  # 重新载入

    if settings['ftp']['port']:
        settings['ftp']['port'] = int(settings['ftp']['port'])
    # 防呆
    settings['check_frequency'] = int(settings['check_frequency'])
    settings['download_resolution'] = str(settings['download_resolution'])
    settings['multi-thread'] = int(settings['multi-thread'])
    if not re.match(r'^(all|latest|largest-sn)$', settings['default_download_mode']):
        settings['default_download_mode'] = 'latest'  # 如果输入非法模式, 将重置为 latest 模式
    # 如果用户自定了番剧目录且存在
    if settings['bangumi_dir'] and os.path.exists(settings['bangumi_dir']):
        # 番剧路径规范化
        settings['bangumi_dir'] = os.path.abspath(settings['bangumi_dir'])
    else:
        # 如果用户没有有自定番剧目录或目录不存在，则保存在本地 bangumi 目录
        settings['bangumi_dir'] = os.path.join(working_dir, 'bangumi')
    settings['working_dir'] = working_dir
    settings['aniGamerPlus_version'] = aniGamerPlus_version
    # 修正 proxies 字典, 使 key 为 int, 方便用于链式代理
    new_proxies = {}
    use_gost = False
    for key, value in settings['proxies'].items():
        if value:
            if not (re.match(r'^http://', value.lower()) or re.match(r'^https://', value.lower())):
                #  如果出现非 http 也非 https 的协议
                use_gost = True
            new_proxies[int(key)]=value
    if len(new_proxies.keys()) > 1:  # 如果代理配置大于 1 , 即使用链式代理, 则同样需要 gost
        use_gost = True
    settings['proxies'] = new_proxies
    settings['use_gost'] = use_gost
    if not new_proxies:
        settings['use_proxy'] = False

    return settings


def read_sn_list():
    settings = read_settings()
    if not os.path.exists(sn_list_path):
        return {}
    with open(sn_list_path, 'r', encoding='utf-8') as f:
        sn_dict = {}
        bangumi_tag = ''
        for i in f.readlines():
            if re.match(r'^@.+', i):  # 读取番剧分类
                bangumi_tag = i[1:-1]
                continue
            elif re.match(r'^@ *', i):
                bangumi_tag = ''
                continue
            i = re.sub(r'#.+\n', '', i).strip()
            i = re.sub(r' +', ' ', i)  # 去除多余空格
            a = i.split(" ")
            if not a[0]:  # 跳过纯注释行
                continue
            if re.match(r'^\d+$', a[0]):
                if len(a) > 1:  # 如果有特別指定下载模式
                    if re.match(r'^(all|latest|largest-sn)$', a[1]):  # 仅认可合法的模式
                        sn_dict[int(a[0])] = {'mode': a[1]}
                    else:
                        sn_dict[int(a[0])] = {'mode': settings['default_download_mode']}  # 非法模式一律替换成默认模式
                else:  # 没有指定下载模式则使用默认设定
                    sn_dict[int(a[0])] = {'mode': settings['default_download_mode']}
                sn_dict[int(a[0])]['tag'] = bangumi_tag
        return sn_dict


def read_cookie():
    old_cookie_path = cookies_path.replace('cookie.txt', 'cookies.txt')
    if os.path.exists(old_cookie_path):
        os.rename(old_cookie_path, cookies_path)
    # 用户可以将cookie保存在程序所在目录下，保存为 cookies.txt ，UTF-8 编码
    if os.path.exists(cookies_path):
        with open(cookies_path, 'r', encoding='utf-8') as f:
            cookies = f.readline()
            cookies = dict([l.split("=", 1) for l in cookies.split("; ")])
            cookies.pop('ckBH_lastBoard', 404)
            return cookies
    else:
        return {}


def renew_cookies(new_cookie):
    new_cookie_str = ''
    for key, value in new_cookie.items():
        new_cookie_str = new_cookie_str + key + '=' + value + '; '
    new_cookie_str = new_cookie_str[0:-2]
    # print(new_cookie_str)
    try_counter = 0
    while True:
        try:
            with open(cookies_path, 'w', encoding='utf-8') as f:
                f.write(new_cookie_str)
            break
        except:
            if try_counter > 3:
                err_print('新cookie保存失敗!')
                break
            time.sleep(2)
            try_counter = try_counter + 1


def read_latest_version_on_github():
    req = 'https://api.github.com/repos/miyouzi/aniGamerPlus/releases/latest'
    session = requests.session()
    remote_version = {}
    try:
        latest_releases_info = session.get(req, timeout=3).json()
        remote_version['tag_name'] = latest_releases_info['tag_name']
        remote_version['body'] = latest_releases_info['body']  # 更新内容
    except:
        remote_version['tag_name'] = aniGamerPlus_version  # 拉取github版本号失败
        remote_version['body'] = ''
    return remote_version


if __name__ == '__main__':
    pass