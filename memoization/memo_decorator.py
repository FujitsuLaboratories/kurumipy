import os
import re
import shutil
import threading
import fasteners
from .file_operation import get_hash, file_write, file_read, try_file_read
from .func_analyzer import get_load_globals, get_load_deref

# メモ化のキャッシュファイル置き場ディレクトリのパス
memo_dir = os.path.join(os.path.dirname(__file__), 'memocache')

def key_value_list_to_dict(l):
    d = dict()
    for i in l:
        h = 0
        if callable(i[1]):
            try:
                h = hash(i[1].__code__.co_code)
            except AttributeError:
                h = hash(i[1].__name__)
        else:
            h = hash(i[1])
        d[i[0]] = h
    return d

memo_dir_lock = threading.Lock()

class LockTemp: pass # ロック用の情報を一時保存するクラス

# メモ化用のデコレータ
def memo(function):
    # メモ化用のキャッシュを置くディレクトリがなければ作成
    if not os.path.isdir(memo_dir):
        with memo_dir_lock:
            if not os.path.isdir(memo_dir):
                os.makedirs(memo_dir)

    def _memo(*args, **kwargs):
        _memo.calls += 1
        # print(dir(function))
        # print(get_load_globals(function))

        # キャッシュのファイル名用に引数のデータのハッシュ値を取得
        cachefilename_hash = get_hash(*args)
        # キャッシュファイル関係のパス名生成
        qualified_name = function.__qualname__
        escaped_qname = re.sub(r'[<>]', '_', qualified_name)
        func_dir = os.path.join(memo_dir, escaped_qname)
        env_path = os.path.join(func_dir, 'env.pickle')
        cache_path = os.path.join(func_dir, 'cache-' + cachefilename_hash + '.pickle')
        lock_path = os.path.join(memo_dir, escaped_qname + '.-lock')

        func_env = {}
        # 関数のコードのバイトコードとコード中で使用している定数のタプルを取得
        func_env['bytecode'] = function.__code__.co_code
        func_env['consts'] = hash(function.__code__.co_consts)
        # 関数で使われているグローバル変数とレキシカル変数を取得
        func_env['globals'] = key_value_list_to_dict(get_load_globals(function))
        func_env['frees'] = key_value_list_to_dict(get_load_deref(function))

        threadid = str(threading.get_ident())
        recursion_cnt = 0
        if hasattr(_memo.lock_temp, threadid):
            recursion_cnt = getattr(_memo.lock_temp, threadid)

        def call_memoized_function():
            cache_result = None
            # envファイルがあればenvファイルに更新があるかチェックし、異なればenvファイル更新、該当関数内のenvとキャッシュファイルを全削除、キャッシュ新規作成
            is_file, env_result = try_file_read(env_path)
            if is_file:
                # envファイルと差異がなく、かつ、キャッシュファイルがあればキャッシュを読み込み
                if env_result == func_env:
                    if os.path.isfile(cache_path):
                        _memo.hits += 1
                        cache_result = file_read(cache_path)
                    # キャッシュファイルがなければ、該当関数を実行して、キャッシュを新規作成
                    else:
                        cache_result = function(*args, **kwargs)
                        file_write(cache_path, cache_result)
                # envファイルと差異があれば、該当関数内のenvとキャッシュファイルを全削除し、envファイルを新規作成、該当関数を実行して、キャッシュを新規作成
                else:
                    # 関数フォルダを削除
                    _memo.invalidates += 1
                    shutil.rmtree(func_dir)
                    os.makedirs(func_dir)
                    file_write(env_path, func_env)
                    cache_result = function(*args, **kwargs)
                    file_write(cache_path, cache_result)
            # envファイルがなければenvファイルとキャッシュを作成
            else:
                if not os.path.isdir(func_dir):
                    os.makedirs(func_dir)
                file_write(env_path, func_env)
                cache_result = function(*args, **kwargs)
                file_write(cache_path, cache_result)
            return cache_result

        if recursion_cnt == 0:
            with fasteners.InterProcessLock(lock_path):
                setattr(_memo.lock_temp, threadid, 1)
                try:
                    return call_memoized_function()
                finally:
                    delattr(_memo.lock_temp, threadid)
        else:
            recursion_cnt += 1
            setattr(_memo.lock_temp, threadid, recursion_cnt)
            try:
                return call_memoized_function()
            finally:
                recursion_cnt -= 1
                setattr(_memo.lock_temp, threadid, recursion_cnt)
    _memo.calls = 0
    _memo.hits = 0
    _memo.invalidates = 0
    _memo.lock_temp = LockTemp()

    return _memo
