import mysql.connector

def check_key_list_in_dic(keylist, dic):
    for i in keylist:
        if not check_dic_key(i,dic):
            return False
    return True

def check_dic_key(key, dic):
    if key in dic.keys():
        return True
    else:
        return False

class Database_Connection:
    def __init__(self):
        config = {
          'user': 'root',
          'password': 'zanzirik8',
          'host': '127.0.0.1',
          'database': 'thesis2',
          'raise_on_warnings': True,
        }
        self.conn = mysql.connector.connect(**config)
        self.cursor_dic = self.conn.cursor(dictionary=True)
        self.cursor = self.conn.cursor()
        query = "SELECT table_name FROM information_schema.tables where table_schema='thesis2'"
        self.execute_query(query)
        self.table_names = [i[0] for i in self.fetchall()]

    def execute_query(self,query):
        self.cursor.execute(query)

    def fetchall(self):
        return self.cursor.fetchall()

    def execute_query_dic(self, query):
        self.cursor_dic.execute(query)

    def fetchall_dic(self):
        return self.cursor_dic.fetchall()

    def commit(self):
        try:
            self.conn.commit()
        except:
            self.conn.rollback()

    def create_insert_query(self, table_name, dic):
        if table_name in self.table_names:
            if table_name == "video":
                if check_key_list_in_dic(["video_id", "name", "url", "thumbnail_url", "embedded_link"], dic):
                    return "INSERT INTO video VALUES(%s,'%s','%s','%s','%s')" % (str(dic[('video_id')]), str(dic[('name')]), str(dic[('url')]), str(dic[('thumbnail_url')]), str(dic[('embedded_link')]))
            elif table_name == "parts":
                if check_key_list_in_dic(["part_id", "video_id", "category", "part_url", "time", "text"], dic):
                    start_time = dic['time'][0]
                    end_time = dic['time'][1]
                    text = str(dic[('text')]).replace("'", "\\'").replace('"', '\\"')
                    return "INSERT INTO parts VALUES(%s, %s,'%s','%s','%s', '%s', '%s','%s')" % (str(dic[('part_id')]), str(dic[('video_id')]), str(dic[('category')]), str(dic[('part_url')]), str(dic[('keywords')]), str(start_time), str(end_time), text)
            elif table_name == "user":
                if check_key_list_in_dic(["user_id", "username", "password"], dic):
                    return "INSERT INTO user VALUES(%s,'%s','%s')" % (str(dic[('user_id')]),str(dic[('username')]),str(dic[('password')]))
            elif table_name == "watched_parts":
                if check_key_list_in_dic(["user_id", "part_id"], dic):
                    return "INSERT INTO watched_parts VALUES(%s,%s)" % (str(dic[('user_id')]),str(dic[('part_id')]))
        else:
            return None

    def create_select_query(self, table_name, dic):
        if table_name in self.table_names:
            if table_name == "video":
                if check_key_list_in_dic(["video_id"], dic):
                    return "SELECT * FROM video WHERE video_id=%s" % (str(dic[("video_id")]))
            elif table_name == "parts":
                if check_key_list_in_dic(["part_id"], dic):
                    return "SELECT * FROM parts WHERE part_id=%s" % (str(dic[("part_id")]))
            elif table_name == "user":
                if check_key_list_in_dic(["user_name"], dic):
                    return "SELECT * FROM user WHERE user_name='%s'" % (str(dic["user_name"]))
            elif table_name == "watched_parts":
                if check_key_list_in_dic(["user_name", "part_id"], dic):
                    return "SELECT * FROM user WHERE user_name='%s' AND part_id=%s" % (str(dic[("user_name")]), str(dic[("part_id")]))
        else:
            return None

    def create_delete_query(self, table_name, dic):
        if table_name in self.table_names:
            if table_name == "video":
                if check_key_list_in_dic(["video_id"], dic):
                    return "DELETE FROM video WHERE video_id=%s" % (str(dic[("video_id")]))
            elif table_name == "parts":
                if check_key_list_in_dic(["part_id"], dic):
                    return "DELETE FROM parts WHERE part_id=%s" % (str(dic[("part_id")]))
            elif table_name == "user":
                if check_key_list_in_dic(["user_id"], dic):
                    return "DELETE FROM user WHERE user_id=%s" % (str(dic[("user_id")]))
            elif table_name == "watched_parts":
                if check_key_list_in_dic(["user_id", "part_id"], dic):
                    return "DELETE FROM user WHERE user_id=%s AND part_id=%s" % (str(dic[("user_id")]), str(dic[("part_id")]))
        else:
            return None

    def truncate_table(self, table_name):
        if table_name in self.table_names:
            self.execute_query("TRUNCATE %s"%table_name)
            self.commit()
        else:
            return False

    def truncate_all_tables(self):
        for table in self.table_names:
            self.truncate_table(table)

    def select_all_from_table(self, table_name):
        if table_name in self.table_names:
            self.execute_query("SELECT * FROM %s" %(table_name))
            return self.fetchall()
        else:
            return None

    def select_all_from_table_dic(self, table_name):
        if table_name in self.table_names:
            self.execute_query_dic("SELECT * FROM %s" %(table_name))
            return self.fetchall_dic()
        else:
            return None
