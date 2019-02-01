import pandas as pd
from abc import ABCMeta, abstractmethod
from os.path import join, isfile
from db.connection import *

video_csv_path = "./csv"
parts_csv_path = "./csv"
db = Database_Connection()

class db_Handler(object):
    __metaclass__ = ABCMeta
    def __init__(self, table_name):
        self.table_name = table_name
        self.csv_tuples = []

    def insert_csv_tuples_to_db(self):
        if len(self.csv_tuples)!=0:
            for tuple in self.csv_tuples:
                db.execute_query(db.create_insert_query(self.table_name, tuple))
            db.commit()

    def clear_table_from_db(self):
        db.truncate_table(self.table_name)

    def select_all_from_db(self):
        return db.select_all_from_table(self.table_name)

    def select_all_from_db_dic(self):
        return db.select_all_from_table_dic(self.table_name)

    @abstractmethod
    def select_from_db(self, dic):
        db.execute_query(db.create_select_query(self.table_name, dic))
        return db.fetchall()

    @abstractmethod
    def select_from_db_dic(self, dic):
        db.execute_query_dic(db.create_select_query(self.table_name, dic))
        return db.fetchall_dic()


    @abstractmethod
    def import_from_csv(self): pass
    @abstractmethod
    def select_from_db(self): pass
    @abstractmethod
    def insert_to_db(self, dic):
        db.execute_query(db.create_insert_query(self.table_name, dic))
        db.commit()


class Video_db_Handler(db_Handler):
    def __init__(self):
        super().__init__("video")

    def import_from_csv(self):
        fname = join(video_csv_path, "videos.csv")
        if isfile(fname):
            video_list = []
            df = pd.read_csv(fname)
            columns = df.columns
            if columns[0]=="id" and columns[1]=="name" and columns[2]=="thumbnail_url":
                for row in df.index:
                    id = str(df.loc[row, columns[0]])
                    name = str(df.loc[row, columns[1]])
                    thumbnail_url = str(df.loc[row, columns[2]])
                    url = str(df.loc[row, columns[4]])
                    embedded_link = str(df.loc[row, columns[5]])
                    temp_tuple = {
                        "video_id":id,
                        "name":name,
                        "url":url,
                        "embedded_link":embedded_link,
                        "thumbnail_url":thumbnail_url
                    }
                    video_list.append(temp_tuple)
                self.csv_tuples = video_list

    def select_from_db(self, id):
        dic = {'video_id':id}
        return super(Video_db_Handler, self).select_from_db(dic)

    def select_from_db_dic(self, id):
        dic = {'video_id':id}
        return super(Video_db_Handler, self).select_from_db_dic(dic)


class Parts_db_Handler(db_Handler):
    def __init__(self):
        super().__init__("parts")

    def import_from_csv(self):
        fname = join(video_csv_path, "parts.csv")
        if isfile(fname):
            part_list = []
            df = pd.read_csv(fname)
            columns = df.columns
            if columns[0]=="video_id" and columns[1]=="part_id" and columns[2]=="category":
                for row in df.index:
                    video_id = df.loc[row, columns[0]]
                    part_id = df.loc[row, columns[1]]
                    category = df.loc[row, columns[2]]
                    keywords = df.loc[row, columns[3]]
                    keywords = str([i[1:-1] for i in keywords[1:-1].split(', ')])[1:-1].replace(' ','').replace("'","")
                    part_url = df.loc[row, columns[4]]
                    time =  [df.loc[row, columns[5]][1:-1].split(', ')[0][1:-1], df.loc[row, columns[5]][1:-1].split(', ')[1][1:-1]]
                    text = df.loc[row, columns[6]]
                    temp_tuple = {
                        "video_id":video_id,
                        "part_id":part_id,
                        "category":category,
                        "keywords":keywords,
                        "part_url":part_url,
                        "time":time,
                        "text":text
                    }
                    part_list.append(temp_tuple)
                self.csv_tuples = part_list

    def select_from_db(self, id):
        dic = {'part_id':id}
        return super(Parts_db_Handler, self).select_from_db(dic)

    def select_from_db_dic(self, id):
        dic = {'part_id':id}
        return super(Parts_db_Handler, self).select_from_db_dic(dic)

    def select_parts_by_video_id_dic(self, video_id):
        db.execute_query_dic("SELECT * FROM parts WHERE video_id=%s" % (str(video_id)))
        return db.fetchall_dic()


class Watched_Parts_db_Handler(db_Handler):
    def __init__(self):
        super().__init__("watched_parts")

    def insert_to_db(self, user_id, part_id):
        dic = {
            "user_id":user_id,
            "part_id":part_id
        }
        super(Watched_Parts_db_Handler, self).insert_to_db(dic)

    def select_from_db(self, id, part_id):
        dic = {'user_id':id, 'part_id':part_id}
        return super(Watched_Parts_db_Handler, self).select_from_db(dic)

    def select_from_db_dic(self, id):
        dic = {'user_id':id}
        return super(Watched_Parts_db_Handler, self).select_from_db_dic(dic)


class User_db_Handler(db_Handler):
    def __init__(self):
        super().__init__("user")

    def insert_to_db(self, username, password):
        dic = {
            "user_name":username,
            "password":password
        }
        super(User_db_Handler, self).insert_to_db(dic)

    def select_from_db(self, user_name):
        dic = {'user_name':user_name}
        return super(User_db_Handler, self).select_from_db(dic)

    def select_from_db_dic(self, user_name):
        dic = {'user_name':user_name}
        return super(User_db_Handler, self).select_from_db_dic(dic)
