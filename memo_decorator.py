import os
import shutil
import file_operation as fo
import func_analyzer

# メモ化のキャッシュファイル置き場ディレクトリのパス
memo_dir = "memocache/"

# メモ化用のデコレータ
def memo(function):
    def _memo(*args,**kwargs):

        # print(dir(function))
        print(func_analyzer.get_load_globals(function))

        # キャッシュのファイル名用に引数のデータのハッシュ値を取得
        cachefilename_hash = fo.get_hash(*args)
        # キャッシュファイル関係のパス名生成
        func_dir = memo_dir + function.__name__ + '/'
        env_path = func_dir + 'env.pickle'
        cache_path = func_dir + 'cache-' + cachefilename_hash + '.pickle'
        # メモ化用のキャッシュを置くディレクトリがなければ作成
        if not os.path.isdir(memo_dir):
            os.makedirs(memo_dir)

        func_env = {}
        # 関数のコードのバイトコードとコード中で使用している定数のタプルを取得
        func_env['bytecode'] = function.__code__.co_code
        func_env['consts'] = function.__code__.co_consts
        # 関数で使われているグローバル変数とレキシカル変数を取得
        func_env['globals'] = func_analyzer.get_load_globals(function)
        func_env['frees'] = func_analyzer.get_load_deref(function)

        cache_result = ''
        # envファイルがあればenvファイルに更新があるかチェックし、異なればenvファイル更新、該当関数内のenvとキャッシュファイルを全削除、キャッシュ新規作成
        if os.path.isfile(env_path):
            env_result = fo.file_read(env_path)
            # envファイルと差異がなく、かつ、キャッシュファイルがあればキャッシュを読み込み
            if(env_result == func_env):
                if os.path.isfile(cache_path):
                    cache_result = fo.file_read(cache_path)
                # キャッシュファイルがなければ、該当関数を実行して、キャッシュを新規作成
                else:
                    cache_result = function(*args,**kwargs)
                    fo.file_write(cache_path, cache_result)
            # envファイルと差異があれば、該当関数内のenvとキャッシュファイルを全削除し、envファイルを新規作成、該当関数を実行して、キャッシュを新規作成
            else:
                # 関数フォルダを削除
                shutil.rmtree(func_dir)
                os.makedirs(func_dir)
                fo.file_write(env_path, func_env)
                cache_result = function(*args,**kwargs)
                fo.file_write(cache_path, cache_result)
        # envファイルがなければenvファイルとキャッシュを作成
        else:
            if not os.path.isdir(func_dir):
                os.makedirs(func_dir)
            fo.file_write(env_path, func_env)
            cache_result = function(*args,**kwargs)
            fo.file_write(cache_path, cache_result)
        return cache_result
    return _memo
