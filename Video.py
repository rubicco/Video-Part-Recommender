# https://img.youtube.com/vi/2Lpc4GSJ9_M/0.jpg

from contextlib import redirect_stdout
from os.path import join, isfile
import re
# Imports the Google Cloud client library
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
import six
import pandas as pd

from keyword_extractor import *

videos_input_file = "./videos.in"
classification_lengths = [500,750,980]
baseX = 980
url_prefix = "https://www.youtube.com/embed/"
# url_prefix = "https://www.youtube.com/watch?v="
srt_output_path = "./output/text/srt"
merged_result_output_path_csv = "./output/csv/merged"
classification_output_path_csv = "./output/csv/classification"
part_output_path_csv = "./output/csv/part"
db_output_path_csv = "./output/csv/db"


def append_text(text, t):
    if(len(text)!=0):
        text = text + ' ' + t
    else:
        text = t
    return text

class Video_Database:
    def __init__(self):
        self.video_list = []
        self.all_parts = []

    def add_video(self, name, srt_name, url, embedded_link, classification_lengths=[980]):
        self.video_list.append(Video(name, srt_name, url, embedded_link, classification_lengths))

    def get_video(self, id):
        for video in self.video_list:
            if video.get_id() == str(id):
                return video
        return None

    def calculate_all(self):
        for video in self.video_list:
            video.full_calculate()

    def calculate_only_parts(self):
        for video in self.video_list:
            video.create_parts(baseX)

    def import_all(self):
        for video in self.video_list:
            video.import_all()

    def import__all_except_parts(self):
        for video in self.video_list:
            video.import_classificition_list()
            video.import_merge_list()

    def import_all_parts(self):
        f = "parts.csv"
        fname = join(db_output_path_csv, f)
        if isfile(fname):
            part_list = []
            temp_part_id_counter = ""
            video_id = ""
            df = pd.read_csv(fname)
            columns = df.columns
            if columns[0]=="video_id" and columns[1]=="part_id" and columns[2]=="category":
                print("(all parts) %s importing..." %(f))
                for row in df.index:
                    video_id = str(df.loc[row, columns[0]])
                    part_id = str(df.loc[row, columns[1]])
                    temp_part_id_counter = part_id
                    category = df.loc[row, columns[2]]
                    keywords = df.loc[row, columns[3]]
                    part_url = df.loc[row, columns[4]]
                    part_list.append(Part_Tuple(video_id, part_url, keywords, category, part_id))
            self.all_parts = part_list.copy()
            Part_Tuple.set_id_counter(temp_part_id_counter)
            print("(all parts) %s imported." %(f))
        else:
            print("%s cannot found. Import failed!" % (fname))
        print("-"*30)

    def export_all(self):
        print("-"*80)
        self.export_videos()
        self.export_all_parts()
        for video in self.video_list:
            video.export_all()
        print("-"*80)

    def export_videos(self):
        f = "videos.csv"
        fname = join(db_output_path_csv, f)
        fullCsv = []
        print("videos.csv exporting...")
        for video in self.video_list:
            csvRow = video.to_csvRow()
            fullCsv.append(csvRow)
        dataframe = pd.DataFrame(fullCsv)
        dataframe.to_csv(fname, header=["id", "name", "thumbnail_url","srt_name", "url", "embedded_link", "classification_lengths"], index=False)
        print("videos.csv exported.")
        print("-"*30)

    def export_all_parts(self):
        f = "parts.csv"
        fname = join(db_output_path_csv, f)
        fullCsv = []
        print("parts.csv exporting...")
        for video in self.video_list:
            video.export_parts()
            fullCsv.extend(video.parts.to_csvRows_all_parts())
        dataframe = pd.DataFrame(fullCsv)
        dataframe.to_csv(fname, header=["video_id","part_id","category","keywords","part_url","time","text"], index=False)
        print("parts.csv exported.")
        print("-"*30)

    def get_parts_of_video(self, video_id):
        part_list=[]
        for part in self.all_parts:
            if part.get_video_id() == str(video_id):
                part_list.append(part)
        return part_list

    def get_videos_from_file(self, fname=videos_input_file):
        video_lines = []
        with open(fname,'r') as file:
            video_lines = file.readlines()
        print("-"*50)
        for line in video_lines:
            if(line[0]=='#'):
                continue
            else:
                objs = line.split(';;')
                v_name = objs[0].strip()
                srt_name = objs[1].strip()
                url_hash = objs[2].strip()
                emb_link = objs[3].strip()
                self.add_video(v_name, srt_name, url_hash, emb_link, classification_lengths)
                print("imported: %s"%(v_name))
        print("-"*50)

class Video:
    # static variables:
    id_counter = "1000"
    # vars : id, name, srt_name, url, embedded_link, subs, scenes, parts, classification_event
    # functions:
    def __init__(self, name, srt_name, url, embedded_link, classification_lengths=[980]):
        self.id = self.create_id()
        self.name = name
        self.srt_name = srt_name
        self.url = url
        self.thumbnail_url = "https://img.youtube.com/vi/" + url + "/0.jpg"
        self.embedded_link = embedded_link
        self.subs = Subtitle(srt_name)
        self.scenes = self.create_scenes()
        self.classification_lengths = classification_lengths
        self.classification_list = []
        self.merge_list= []
        for length in classification_lengths:
            self.classification_list.append(Video_Classification(self.id, length))
            self.merge_list.append(Merged_Results(self.id, length))
        self.parts = Parts(self.id, self.url)

    def create_id(self):
        id = Video.id_counter
        Video.id_counter = str(int(Video.id_counter)+1)
        return id

    def get_id(self):
        return self.id

    def full_calculate(self):
        self.classify_all_list_from_subs()
        self.merge_all_list()
        self.create_parts(baseX)

    def print_subtitles(self):
        self.subs.print_subs()

    def write_file_subtitles(self, fname=""):
        if fname=="":
            fname=self.srt_name+".out"
        fpath = join(srt_output_path,fname)
        with open(fpath,'w') as file:
            with redirect_stdout(file):
                self.print_subtitles()

    def print_full_text(self):
        print(self.subs.get_full_text())

    def create_scenes(self):
        return self.subs.join_sentences()

    def create_parts(self, baseX):
        if baseX in self.classification_lengths:
            self.parts.create_part_list((self.get_merge_list_X(baseX)).get_source_scenes(), (self.get_merge_list_X(baseX)).get_result_scenes())
        else:
            print("Cannot find desired length.")

    def get_classification_list_X(self, length):
        for i in self.classification_list:
            if i.text_size == length:
                return i

    def get_merge_list_X(self, length):
        for i in self.merge_list:
            if i.text_size == length:
                return i

    def classify_all_list_from_scenes(self):
        for i in self.classification_list:
            i.classify(self.scenes)

    def classify_all_list_from_subs(self):
        for i in self.classification_list:
            i.classify(self.subs.get_subtitiles())

    def merge_all_list(self):
        for i in self.merge_list:
            i.merge(self.get_classification_list_X(i.text_size).get_source_scenes(), self.get_classification_list_X(i.text_size).get_result_scenes())

    def export_merge_list(self):
        for i in self.merge_list:
            i.export_merged_results()

    def export_classification_list(self):
        for i in self.classification_list:
            i.export_classification()

    def export_parts(self):
        self.parts.export_parts()

    def export_all(self):
        print("-"*30)
        self.export_merge_list()
        self.export_classification_list()
        self.export_parts()

    def import_merge_list(self):
        for i in self.merge_list:
            i.import_merged_results()

    def import_classificition_list(self):
        for i in self.classification_list:
            i.import_classification()

    def import_parts(self):
        self.parts.import_parts()

    def import_all(self):
        print("-"*30)
        self.import_classificition_list()
        self.import_merge_list()
        self.import_parts()

    def to_csvRow(self):
        return [self.id, self.name, self.thumbnail_url, self.srt_name, self.url, self.embedded_link, self.classification_lengths]

class Subtitle:
    srt_path = "./subtitles/"
    def __init__(self, srt_name):
        self.subtitles = self.import_from_srt(srt_name)

    def import_from_srt(self, srt_name):
        lines = []
        subtitles = []
        srtCount = 1
        srtLines = []
        srtTime = 0
        fpath = Subtitle.srt_path + srt_name
        with open(fpath, 'r') as file:
            lines = file.readlines()

        for i in lines:
            line = i.strip()
            if(line==""):
                continue
            if line=='1' or line==str(srtCount):
                if(srtCount-1!=0):
                    subtitles.append(Subtitle_Tuple(srtCount-1,srtTime,srtLines))
                    srtLines=[]
                srtCount+=1
                continue
            fontCount = line.count('</font>')
            regex_pattern = self.find_regex(fontCount)
            matches=re.findall(regex_pattern, line)
            if "-->" in line:
                srtTime = line.split(" --> ")
            elif not matches.__len__()==0:
                for s in matches:
                    if type(s) is tuple:
                        for el in s:
                            if not el == '':
                                srtLines.append(el.strip())
                    elif not s == '':
                        srtLines.append(s.strip())
        subtitles.append(Subtitle_Tuple(srtCount-1,srtTime,srtLines))
        return subtitles

    def find_regex(self, fontCount):
        return "(.*)<.*>(.*)<\/.*>" * fontCount + "(.*)"

    def print_subs(self):
        for tuple in self.subtitles:
            tuple.print_tuple()

    def get_subtitiles(self):
        return self.subtitles

    def get_full_text(self):
        ftext = ""
        for tuple in self.subtitles:
            ftext = append_text(ftext, tuple.get_merged_text())
        return ftext

    def get_text_from_range(self, start_no, end_no):
        # srt'de start_no 'dan end_no'ya kadar textleri merge edip geri dondurur.
        text = ""
        rangeArray = [x for x in range(start_no, end_no+1)]
        for tuple in self.subtitles:
            if rangeArray==[]:
                break
            if tuple.no in rangeArray:
                text = append_text(text, tuple.get_merged_text())
                rangeArray.remove(tuple.no)
        return text

    def join_sentences(self):
        temp = []
        scenes = []
        temp_sentences = []
        sentence = ""
        found = 0
        for tuple in self.subtitles:
            #sentence creation:
            tuple_textlist = tuple.get_textlist()
            for str in tuple_textlist:
                if str[-1]!='.':
                    sentence = append_text(sentence, str)
                elif str[-1]=='.':
                    sentence = append_text(sentence, str)
                    temp_sentences.append(sentence)
                    sentence = ""
                    # sentence found.
            temp.append(tuple)
            if tuple_textlist!=[] and tuple_textlist[-1][-1] == '.':
                # create new srt sequention
                sub_seq = []
                new_time = Time_Scale.merge_times(temp[0].time, temp[-1].time)
                new_sentences = temp_sentences.copy()
                for t in temp:
                    sub_seq.append(t.no)
                scenes.append(Scene_Tuple(sub_seq,new_time,new_sentences))
                temp_sentences = []
                temp = []
        return scenes

class Subtitle_Tuple:
    def __init__(self, no, time, texts):
        self.no = no
        self.time = Time_Scale(time)
        self.texts = Subtitle_Text(texts)

    def get_sentence_list(self):
        return self.texts.get_list()

    def print_tuple(self):
        print(self.no)
        print(self.time.to_string())
        print(self.texts.to_string())

    def get_merged_text(self):
        return self.texts.join_all()

    def get_textlist(self):
        return self.texts.get_list()

    def get_time(self):
        return self.time

class Subtitle_Text:
    def __init__(self, text_list):
        self.text_list =  text_list

    def to_string(self):
        return self.join_all()

    def join_all(self):
        text = ""
        if len(self.text_list)>1:
            for t in self.text_list:
                text = append_text(text, t)
        else:
            text = self.text_list[0]
        return text

    def get_list(self):
        return self.text_list

class Scene_Tuple:
    def __init__(self, no_list, time, texts):
        self.no_list = no_list
        self.time = Time_Scale(time)
        self.texts = Subtitle_Text(texts)

    def get_sentence_list(self):
        return self.texts.get_list()

    def get_merged_text(self):
        return self.texts.join_all()

    def get_no_list(self):
        return self.no_list

    def get_time(self):
        return self.time

    def get_time_csvRow(self):
        return self.time.to_csvRow()

class Time_Scale:
    def __init__(self, time):
        self.start = time[0]
        self.end = time[1]

    def to_string(self):
        return self.start+" - "+self.end

    def convert_second(self):
        s_hour, s_min, s_sec = self.start.split(':')
        e_hour, e_min, e_sec = self.end.split(':')
        start_sec = int(s_hour)*3600 + int(s_min)*60 + int(s_sec.split(',')[0])
        end_sec = int(e_hour)*3600 + int(e_min)*60 + int(e_sec.split(',')[0])
        return [start_sec, end_sec]

    def to_csvRow(self):
        return [self.start, self.end]

    @staticmethod
    def merge_times(time1, time2):
        return [time1.start, time2.end]

class Video_Classification:
    def __init__(self, video_id, text_size):
        self.video_id = video_id
        self.text_size = text_size
        self.source_scenes = []
        self.result_scenes = []

    def classify(self, scenes):
        print("%s_%d classifying..." % (self.video_id,self.text_size))
        if type(scenes[0]) is Scene_Tuple:
            self.source_scenes = self.getXchar(scenes)
            self.result_scenes = self.classify_lines(self.source_scenes)
            print("%s_%d classified" % (self.video_id,self.text_size))
            print("-"*30)
        elif type(scenes[0]) is Subtitle_Tuple:
            self.source_scenes = self.getXchar_from_subs(scenes)
            self.result_scenes = self.classify_lines(self.source_scenes)
            print("%s_%d classified" % (self.video_id,self.text_size))
            print("-"*30)

    def getXchar(self, scenes):
        listOfLines = []
        limit=self.text_size
        tempNo = []
        tempTime= []
        start_time = ""
        end_time = ""
        lineX = ""
        for tuple in scenes:
            currLine = ""
            for sentence in tuple.get_sentence_list():
                currLine = append_text(currLine, sentence)
            if len(lineX)+len(currLine)<=limit:
                # suan bulunulan satir eklenince limiti asmiyorsa suanki satiri ekle
                if len(lineX)==0:
                    # ilk cumlesi ise start time i ekle
                    start_time = tuple.time.start
                end_time = tuple.time.end
                tempNo.extend(tuple.no_list)
                lineX=append_text(lineX, currLine)
            else:
                listOfLines.append(Scene_Tuple(tempNo, [start_time, end_time],[lineX]))
                tempNo = []
                tempNo.extend(tuple.no_list)
                start_time = tuple.time.start
                lineX=currLine
        return listOfLines

    def getXchar_from_subs(self, subs):
        listOfLines = []
        limit=self.text_size
        tempNo = []
        tempTime= []
        start_time = ""
        end_time = ""
        lineX = ""
        for tuple in subs:
            currLine = ""
            for sentence in tuple.get_sentence_list():
                currLine = append_text(currLine, sentence)
            if len(lineX) + len(currLine) <= limit:
                if len(lineX) == 0:
                    start_time = tuple.time.start
                end_time = tuple.time.end
                tempNo.append(tuple.no)
                lineX=append_text(lineX, currLine)
            else:
                listOfLines.append(Scene_Tuple(tempNo, [start_time, end_time], [lineX]))
                tempNo = []
                tempNo.append(tuple.no)
                start_time = tuple.time.start
                lineX = currLine
        return listOfLines

    def classify_lines(self, scenes):
        counter = 0
        listOfClassification = []
        for tuple in scenes:
            cat_list = []
            text = tuple.get_merged_text()
            cat = Video_Classification.classify_text(text)
            for c in cat:
                cat_list.append([c.name, c.confidence])
            listOfClassification.append([counter,cat_list])
            counter += 1
        return listOfClassification

    def get_source_scenes(self):
        return self.source_scenes

    def get_result_scenes(self):
        return self.result_scenes

    def export_classification(self):
        f = self.video_id + '_' + str(self.text_size) + ".csv"
        print("(classification) %s exporting..." % (f))
        fname = join(classification_output_path_csv,f)
        fullCsv = []
        for line in self.result_scenes:
            csvRow = []
            index = line[0]
            tuple = self.source_scenes[index]
            csvRow.append(self.video_id)
            csvRow.append(index)
            csvRow.append(tuple.get_no_list())
            csvRow.append(tuple.get_time_csvRow())
            csvRow.append(line[1])
            csvRow.append(tuple.get_merged_text())
            fullCsv.append(csvRow)
        dataframe = pd.DataFrame(fullCsv)
        dataframe.to_csv(fname, header=["video_id","index","no_list","time","categories","part"], index=False)
        print("(classification) %s exported." % (f))
        print("-"*30)

    def import_classification(self):
        f = self.video_id + '_' + str(self.text_size) + ".csv"
        fname = join(classification_output_path_csv,f)
        if isfile(fname):
            resultList = []
            contentList = []
            df = pd.read_csv(fname)
            columns = df.columns
            if columns[0]=="video_id" and columns[1]=="index" and columns[2]=="no_list":
                print("(classification) %s importing..."%(f))
                for row in df.index:
                    index = df.loc[row, columns[1]]
                    no_list = [int(i) for i in df.loc[row,columns[2]][1:-1].split(', ')]
                    time = [df.loc[row, columns[3]][1:-1].split(', ')[0][1:-1], df.loc[row, columns[3]][1:-1].split(', ')[1][1:-1]]
                    cats = re.findall(r'\[(.*?)\]',  df.loc[row,columns[4]][1:-1])
                    categories = [[x.split(', ')[0][1:-1], float(x.split(', ')[1])] for x in cats]
                    part = df.loc[row,columns[5]][:]
                    resultList.append([index,categories])
                    contentList.append(Scene_Tuple(no_list,time,[part]))
            self.source_scenes = contentList.copy()
            self.result_scenes = resultList.copy()
            print("(classification) %s imported."%(f))
        else:
            print("%s cannot found. Import failed!" % (fname))
        print("-"*30)

    @staticmethod
    def classify_text(text):
        """Classifies content categories of the provided text."""
        client = language.LanguageServiceClient()

        if isinstance(text, six.binary_type):
            text = text.decode('utf-8')

        document = types.Document(
            content=text.encode('utf-8'),
            type=enums.Document.Type.PLAIN_TEXT)

        categories = client.classify_text(document).categories
        return categories

class Merged_Results:
    def __init__(self, video_id, text_size):
        self.video_id = video_id
        self.text_size = text_size
        self.result_scenes = []
        self.source_scenes = []

    def merge(self, source, result):
        self.result_scenes = Merge_Handler.merge_result(result)
        self.source_scenes = Merge_Handler.merge_parts(source, self.result_scenes)
        for i in range(len(self.result_scenes)):
            self.result_scenes[i][0]=i

    def get_source_scenes(self):
        return self.source_scenes

    def get_result_scenes(self):
        return self.result_scenes

    def export_merged_results(self):
        f = self.video_id + '_' + str(self.text_size) + ".csv"
        print("(merged_results) %s exporting..."%(f))
        fname = join(merged_result_output_path_csv,f)
        fullCsv = []
        for line in self.result_scenes:
            csvRow = []
            index = line[0]
            tuple = self.source_scenes[index]
            csvRow.append(self.video_id)
            csvRow.append(index)
            csvRow.append(tuple.get_no_list())
            csvRow.append(tuple.get_time_csvRow())
            csvRow.append(line[1])
            csvRow.append(tuple.get_merged_text())
            fullCsv.append(csvRow)
        dataframe = pd.DataFrame(fullCsv)
        dataframe.to_csv(fname, header=["video_id","index","no_list","time","categories","part"], index=False)
        print("(merged_results) %s exported."%(f))
        print("-"*30)

    def import_merged_results(self):
        f = self.video_id + '_' + str(self.text_size) + ".csv"
        fname = join(merged_result_output_path_csv,f)
        if isfile(fname):
            resultList = []
            contentList = []
            df = pd.read_csv(fname)
            columns = df.columns
            if columns[0]=="video_id" and columns[1]=="index" and columns[2]=="no_list":
                print("(merged_results) %s importing..."%(f))
                for row in df.index:
                    index = df.loc[row, columns[1]]
                    no_list = [int(i) for i in df.loc[row,columns[2]][1:-1].split(', ')]
                    time = [df.loc[row, columns[3]][1:-1].split(', ')[0][1:-1], df.loc[row, columns[3]][1:-1].split(', ')[1][1:-1]]
                    cotegory = df.loc[row, columns[4]]
                    part = df.loc[row,columns[5]][:]
                    resultList.append([index,cotegory])
                    contentList.append(Scene_Tuple(no_list,time,[part]))
            self.source_scenes = contentList.copy()
            self.result_scenes = resultList.copy()
            print("(merged_results) %s imported."%(f))
        else:
            print("%s cannot found. Import failed!" % (fname))
        print("-"*30)

class Merge_Handler:
    @staticmethod
    def merge_parts(parts, new_results):
        new_parts = []
        for res in new_results:
            temp_indexes = []
            temp_no_list = []
            temp_time = []
            temp_text = ""
            temp_indexes = res[0]
            temp_time = Time_Scale.merge_times(parts[temp_indexes[0]].time, parts[temp_indexes[-1]].time)
            for i in temp_indexes:
                temp_text = append_text(temp_text, parts[i].get_merged_text())
                temp_no_list.extend(parts[i].get_no_list())
            new_parts.append(Scene_Tuple(temp_no_list, temp_time, [temp_text]))
        return new_parts

    @staticmethod
    def merge_result(results):
        new_results = []
        temp_index=[]
        for i in range(len(results)):
            if not i == len(results)-1:
                cat1 = results[i][1]
                cat2 = results[i+1][1]
                if cat1==[]:
                    temp_index.append(results[i][0])
                    if not cat2==[]:
                        # no-class'lari birlestirir. istemiyorsan if'i kaldir.
                        new_results.append([temp_index,""])
                        temp_index=[]
                elif cat2==[]:
                    temp_index.append(results[i][0])
                    new_results.append([temp_index, results[i][1][0][0].split('/')[1]])
                    temp_index=[]
                else:
                    if cat1[0][0].split('/')[1] == cat2[0][0].split('/')[1]:
                        temp_index.append(results[i][0])
                    else:
                        temp_index.append(results[i][0])
                        new_results.append([temp_index, results[i][1][0][0].split('/')[1]])
                        temp_index=[]
        return new_results

    @staticmethod
    def merge_source_result(source, result):
        # merged_list dondurur ve bunu export edebilir.
        merged_list = []
        for i in range(len(result)):
            cat = result[i][1]
            tuple = source[i]
            merged_list.append(tuple.get_no_list(), tuple.get_time(), cat, tuple.get_merged_text())
        return merged_list

class Parts:
    def __init__(self, video_id, video_url):
        self.video_id = video_id
        self.video_url = video_url
        self.part_list = []
        # gelen result'daki her tuple icin source'dan text

    def create_part_list(self, source_scenes, result_scenes):
        for tuple in result_scenes:
            source_tuple = source_scenes[tuple[0]]
            time = [source_tuple.get_time().start,source_tuple.get_time().end]
            start, end =  source_tuple.get_time().convert_second()
            part_url = self.video_url
            # part_url = self.video_url + '?start=' + str(start) + '&end=' + str(end)
            kwords = Parts.kword_operations(source_tuple.get_merged_text())
            keywords = Parts.get_X_keyword(kwords)
            category = tuple[1]
            part_text = source_tuple.get_merged_text()
            self.part_list.append(Part_Tuple(self.video_id, part_url, keywords, category, time, part_text))

    def get_part_list(self):
        return self.part_list

    def to_csvRows_all_parts(self):
        all_rows = []
        for part in self.part_list:
            all_rows.append(part.to_csvRow())
        return all_rows

    def export_parts(self):
        f = self.video_id + '_parts' + ".csv"
        print("(parts) %s exporting..."%(f))
        fname = join(part_output_path_csv, f)
        fullCsv = []
        for tuple in self.part_list:
            csvRow = tuple.to_csvRow()
            fullCsv.append(csvRow)
        dataframe = pd.DataFrame(fullCsv)
        dataframe.to_csv(fname, header=["video_id","part_id","category","keywords","part_url","time","text"], index=False)
        print("(parts) %s exported."%(f))
        print("-"*30)

    def import_parts(self):
        f = self.video_id + '_parts' + ".csv"
        fname = join(part_output_path_csv, f)
        if isfile(fname):
            part_list = []
            temp_part_id_counter = ""
            video_id = ""
            df = pd.read_csv(fname)
            columns = df.columns
            if columns[0]=="video_id" and columns[1]=="part_id" and columns[2]=="category":
                print("(parts) %s importing..."%(f))
                for row in df.index:
                    video_id = str(df.loc[row, columns[0]])
                    part_id = str(df.loc[row, columns[1]])
                    temp_part_id_counter = part_id
                    category = df.loc[row, columns[2]]
                    keywords = df.loc[row, columns[3]]
                    part_url = df.loc[row, columns[4]]
                    time =  [df.loc[row, columns[5]][1:-1].split(', ')[0][1:-1], df.loc[row, columns[5]][1:-1].split(', ')[1][1:-1]]
                    text = df.loc[row, columns[6]]
                    part_list.append(Part_Tuple(video_id, part_url, keywords, category, part_id, time, text))
            self.part_list = part_list.copy()
            self.video_id = video_id
            Part_Tuple.set_id_counter(temp_part_id_counter)
            print("(parts) %s imported."%(f))
        else:
            print("%s cannot found. Import failed!" % (fname))
        print("-"*30)

    @staticmethod
    def get_X_keyword(kwlist):
        return [x[0] for x in kwlist[:Part_Tuple.keyword_capacity]]

    @staticmethod
    def kword_operations(text):
        kwords = list(set(keyword_extract(text)))
        counted_result = [[x, count_kword(text,x)] for x in kwords]
        counted_result.sort(key=lambda x: x[1], reverse=True)
        return counted_result

class Part_Tuple:
    id_counter = "100000"
    keyword_capacity = 5
    # TODO: text ile keywords degistir.
    def __init__(self, video_id, url, keywords, category, time, part_text,part_id=-1):
        if part_id==-1:
            self.id = self.create_id()
        else:
            self.id = part_id
        print(self.id)
        self.video_id = video_id
        self.part_url = url
        self.keywords = keywords
        self.category = category
        self.time = Time_Scale(time)
        self.part_text = part_text

    def create_id(self):
        id = Part_Tuple.id_counter
        Part_Tuple.id_counter = str(int(Part_Tuple.id_counter)+1)
        return id

    def get_video_id(self):
        return self.video_id

    def to_csvRow(self):
        return [self.video_id, self.id, self.category, self.keywords, self.part_url, self.time.to_csvRow(), self.part_text]

    @staticmethod
    def set_id_counter(id):
        Part_Tuple.id_counter = id
