from db.database_handlers import *

class SearchEngine:
    def __init__(self):
        self.video_counts = []
        self.part_counts = []

    def search_in_text(self, wanted, text):
        wanted_keywords = wanted.split(' ')
        splited_text = text.split(' ')
        count = 0
        for t in splited_text:
            for wk in wanted_keywords:
                if not (wk == 'of' or wk == 'and' or wk == 'but' or wk == 'or' or wk == 'nor' or wk == 'so' or wk == 'for' or wk == 'yet'):
                    if(wk == t):
                        count += 1
        return count

    def search_in_keywords(self, wanted, keyword_list):
        wanted_keywords = wanted.split(' ')
        count = 0
        for keyword in keyword_list:
            for wk in wanted_keywords:
                if not (wk == 'of' or wk == 'and' or wk == 'but' or wk == 'or' or wk == 'nor' or wk == 'so' or wk == 'for' or wk == 'yet'):
                    if(wk == keyword):
                        count += 1
        return count

    def select_video_most_related(self, wanted):
        self.calculate_video_counts(wanted)
        self.video_counts = sorted(self.video_counts, key=lambda x: x[1], reverse=True)

    def select_part_most_related(self, wanted):
        self.calculate_part_counts(wanted)
        self.part_counts = sorted(self.part_counts, key=lambda x: x[2], reverse=True)

    def parts_of_video(self, video_id, parts):
        parts_of_curr_video = []
        for part in parts:
            if part['video_id'] == video_id:
                parts_of_curr_video.append(part)
        return parts_of_curr_video

    def calculate_video_counts(self, wanted):
        parts = db.select_all_from_table_dic('parts')
        videos = db.select_all_from_table_dic('video')
        video_ids = []
        for video in videos:
            video_ids.append(video['video_id'])
        videoCounts = []
        video_count = 0
        curr_video_index = 0
        parts_of_curr_video = []
        for video in video_ids:
            parts_of_curr_video = self.parts_of_video(str(video), parts)
            for part in parts_of_curr_video:
                video_count += self.search_in_text(wanted, part['text'])
            videoCounts.append([video, video_count])
            video_count = 0
        self.video_counts = videoCounts
        return videoCounts

    def calculate_part_counts(self, wanted):
        parts = db.select_all_from_table_dic('parts')
        videos = db.select_all_from_table_dic('video')
        partCounts = []
        for part in parts:
            partCounts.append([part['video_id'], part['part_id'], self.search_in_text(wanted, part['text'])])
        self.part_counts = partCounts
        return partCounts
