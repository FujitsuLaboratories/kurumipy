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

class ReentrantInterprocessLock():
    def __init__(self, lock_path):
        self.lock_path = lock_path
        self.interprocess_lock = fasteners.InterProcessLock(lock_path)
        self.condition = threading.Condition()
        self.thread_id = 0
        self.recursion_count = 0

    def __enter__(self):
        ident = threading.get_ident()
        while True:
            with self.condition:
                if self.thread_id != 0 and self.thread_id != ident:
                    self.condition.wait()
                else:
                    if self.thread_id == ident:
                        self.recursion_count += 1
                    else:
                        self.thread_id = ident
                        self.recursion_count = 1
                        self.interprocess_lock.__enter__()
                    return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self.condition:
            self.recursion_count -= 1
            if self.recursion_count == 0:
                self.thread_id = 0
                self.condition.notify_all()
                return self.interprocess_lock.__exit__(exc_type, exc_val, exc_tb)
            else:
                return False

# メモ化用のデコレータ
def memo(function):
    # メモ化用のキャッシュを置くディレクトリがなければ作成
    if not os.path.isdir(memo_dir):
        with memo_dir_lock:
            if not os.path.isdir(memo_dir):
                os.makedirs(memo_dir)

    # キャッシュファイル関係のパス名生成
    qualified_name = function.__qualname__
    escaped_qname = re.sub(r'[<>]', '_', qualified_name)
    func_dir = os.path.join(memo_dir, escaped_qname)
    env_path = os.path.join(func_dir, 'env.pickle')
    lock_path = os.path.join(memo_dir, escaped_qname + '.-lock')

    def _memo(*args, **kwargs):
        _memo.calls += 1
        # print(dir(function))
        # print(get_load_globals(function))

        # キャッシュのファイル名用に引数のデータのハッシュ値を取得
        cachefilename_hash = get_hash(*args)
        cache_path = os.path.join(func_dir, 'cache-' + cachefilename_hash + '.pickle')

        func_env = {}
        # 関数のコードのバイトコードとコード中で使用している定数のタプルを取得
        func_env['bytecode'] = function.__code__.co_code
        func_env['consts'] = hash(function.__code__.co_consts)
        # 関数で使われているグローバル変数とレキシカル変数を取得
        func_env['globals'] = key_value_list_to_dict(get_load_globals(function))
        func_env['frees'] = key_value_list_to_dict(get_load_deref(function))

        with _memo.lock:
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
    _memo.calls = 0
    _memo.hits = 0
    _memo.invalidates = 0
    _memo.lock = ReentrantInterprocessLock(lock_path)

    return _memo
