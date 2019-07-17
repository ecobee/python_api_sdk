from tokens import FileTokens
import pandas as pd
import unittest
from mock import MagicMock, patch
import os

stub_id = "123456789012"
stub_acc = "a"
stub_ref = "b"
stub_user_id = "abcdefg"

user_test_csv = "ebapi_user.csv"
tstat_test_csv = "ebapi_tstat.cvs"


class TestFileTokens(unittest.TestCase):



    def tearDown(self):
        clear_env_vars()
        delete_test_csvs()
       
    def test_no_env_vars_init(self):
        with self.assertRaisesRegex(EnvironmentError,
                                     FileTokens.missing_env_vars):
            FileTokens()

    def test_single_env_var_init(self):
        os.environ[FileTokens.user_ev] = "not a real path"
        missing_ev = FileTokens.tstat_ev
        err_msg = FileTokens.missing_env_var.format(missing_ev)
        with self.assertRaisesRegex(EnvironmentError, err_msg):
            FileTokens()

    def test_missing_single_file(self):
        load_evs()
        with open(user_test_csv, 'w'):
            pass
        expected = "Data Corrupted ebapi_tstat.cvs Missing."
        with self.assertRaisesRegex(EnvironmentError, expected):
            FileTokens()

    def test_no_files(self):
        load_evs()
        file_tokens = FileTokens()
        self.dfs_empty(file_tokens)
        self.assertTrue(csvs_exist())

    def test_both_file(self):
        file_tokens = populated_setup()

    def test_insert_tstat(self):
        load_evs()
        file_tokens = FileTokens()
        file_tokens.insert(stub_user_id, stub_id, stub_acc, stub_ref)
        self.has_test_row(file_tokens)
    
    
    def test_insert_saved(self):
        load_evs()
        file_tokens = FileTokens()
        file_tokens.insert(stub_user_id, stub_id, stub_acc, stub_ref)
        del file_tokens
        file_tokens_reopened = FileTokens()
        self.has_test_row(file_tokens_reopened)

    def test_insert_overrite_user(self):
        file_tokens = populated_setup()
        with self.assertRaisesRegex(RuntimeError, "Attempt to overwrite user.*"):
            file_tokens.insert(stub_user_id, stub_id, stub_acc, stub_ref)
        
    def test_insert_tstat(self):
        file_tokens = populated_setup()
        new_tstat = "100000000000"
        file_tokens.insert_tstat(stub_user_id, new_tstat)
        self.assertEqual(file_tokens.tstat.loc[new_tstat, "user_id"], stub_user_id)

    def test_delete_tstat(self):
        file_tokens = populated_setup()
        file_tokens.delete(stub_id)
        self.dfs_empty(file_tokens)
    
    def test_delete_tstat_saves(self):
        file_tokens = populated_setup()
        file_tokens.delete(stub_id)
        del file_tokens
        file_tokens = FileTokens()
        self.dfs_empty(file_tokens)

    def test_delete_tstat_dne(self):
        load_evs()
        file_tokens = FileTokens()
        err_msg = file_tokens.unknown_tstat.format(stub_id)
        with self.assertRaisesRegex(KeyError, err_msg):
            file_tokens.delete(stub_id)
    
    @patch('.tokens.refresh_token')
    def mock_refresh_token(ref):
        print("mock refresh_tokens")
        new_ref = ref + "b"
        new_acc = len(new_ref) * "b"
        return acc, ref
                  
    def test_refresh(self):
        file_tokens = populated_setup()
        file_tokens.refresh()

    def has_test_row(self, file_tokens):
        self.assertEqual(file_tokens.user.loc[stub_user_id, "access_token"], stub_acc)
        self.assertEqual(file_tokens.user.loc[stub_user_id, "refresh_token"], stub_ref)
        self.assertEqual(file_tokens.tstat.loc[stub_id, "user_id"], stub_user_id)


    def test_get_access_token(self):
        file_tokens = populated_setup()
        acc = file_tokens.get_access_token(stub_id)
        self.assertEqual(acc, stub_acc)

    def test_get_access_token_dne(self):
        load_evs()
        file_tokens = FileTokens()
        err_msg = file_tokens.unknown_tstat.format(stub_id)
        with self.assertRaisesRegex(KeyError, err_msg):
            file_tokens.get_access_token(stub_id)

    def dfs_empty(self, file_tokens):
        empty_user = gen_empty_user_df()
        empty_tstat = gen_empty_tstat_df()
        self.assertTrue(file_tokens.user.equals(empty_user))
        self.assertTrue(file_tokens.tstat.equals(empty_tstat))
    
        
def delete_test_csvs():
    for fname in [user_test_csv, tstat_test_csv]:
        if os.path.exists(fname):
            os.remove(fname)


def populated_setup():
    load_evs()
    save_populated_test_files()
    return FileTokens()


def save_populated_test_files():
    gen_populated_user().to_csv(user_test_csv)
    gen_populated_tstat().to_csv(tstat_test_csv)
    

def gen_populated_user():
    df_user = gen_empty_user_df()
    df_user.loc[stub_user_id] = [stub_acc, stub_ref]
    return df_user


def gen_populated_tstat():
    df_tstat = gen_empty_tstat_df()
    df_tstat.loc[stub_id] = [stub_user_id]
    return df_tstat


def gen_empty_user_df():
    df = pd.DataFrame(columns=FileTokens.user_cols)
    return df.set_index("user_id")
    
    
def gen_empty_tstat_df():
    df = pd.DataFrame(columns=FileTokens.tstat_cols)
    return df.set_index("tstat_id")


def csvs_exist():
    for fname in [user_test_csv, tstat_test_csv]:
        if not os.path.exists(fname):
            return False
    return True


def clear_env_vars():
    for ev in [FileTokens.user_ev, FileTokens.tstat_ev]:
        try:
            del os.environ[ev]
        except KeyError:
            pass


def load_evs():
    os.environ[FileTokens.user_ev] = user_test_csv
    os.environ[FileTokens.tstat_ev] = tstat_test_csv

