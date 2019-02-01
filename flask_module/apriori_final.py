import pandas as pd
import random
from db.database_handlers import *

table_name = 'parts'

class Apriori:
    def __init__(self):
        #self.user_value = userValue
        self.part_list = []
        self.parts = []
        self.user_list = []
        self.apriori_list = []
        self.apriori_list2 = []
        self.userNumber = -1
        self.newPart = []
        self.user_ids = []

    def import_videos(self):
        parts = db.select_all_from_table_dic('parts')
        partList = [] #video bilgi kayıt listesi
        video_list = [] #video'arın index ve part indexlerini beraber tutan liste
        part_id = []  #video part listesi
        video_id = [] #video index listesi
        category = [] #video kategorisi listesi
        part_url = [] #video partlarının url'leri listesi
        for i in range(len(parts)):
            part_id.append(int(parts[i]['part_id']))
            video_id.append(int(parts[i]['video_id']))
            category.append(parts[i]['category'])
            part_url.append(parts[i]['part_url'])
            partList.append([video_id[i], part_id[i], category[i], part_url[i]])
        self.part_list = partList
        self.parts = part_id

    def import_users(self) :
        users = db.select_all_from_table_dic('user')
        user_id_list = []
        for i in range(len(users)) :
            user_id_list.append(users[i]['user_id'])
        self.user_ids = user_id_list

    def import_watched_parts(self) :
        watched_parts = db.select_all_from_table_dic('watched_parts')
        wpList = []
        for j in range(len(watched_parts)) :
            wpList.append([int(watched_parts[j]['user_id']),int(watched_parts[j]['part_id'])])
        temp = []
        for x in range(len(self.user_ids)) :
            temp.append([self.user_ids[x]])
            for y in range(len(wpList)) :
                if self.user_ids[x] == wpList[y][0] :
                    if wpList[y][1] not in temp[x] :
                        temp[x].append(wpList[y][1])
        self.user_list = temp

    def export_to_watched_table(self):
        watched_db = Watched_Parts_db_Handler()
        for i in range(len(self.user_list)) :
            user_id = self.user_list[i][0]
            for j in range(1,len(self.user_list[i])) :
                part_id = self.user_list[i][j]
                watched_db.insert_to_db(user_id, part_id)

    def generate_random_user_list(self) : # öneri için istediğimiz sayıda user'lara ait izleme geçmişi üretimi
        watchedList = []
        userVideoNumber = random.randint(10,20) # her user'ın listesi için izlenen video sayısı, en fazla 20 video tutuluyor.
        for i in range(len(self.user_ids)) :
            watchedList.append([0]*(userVideoNumber+1)) #+1;user_id'yi de eklemek için
            watchedList[i][0] = self.user_ids[i]
            for j in range(1,(userVideoNumber+1)) :
                a = self.parts[random.randint(0,(len(self.parts)-1))]
                if a not in watchedList[i] :
                    watchedList[i][j] = a
                else :
                    a = self.parts[random.randint(0,(len(self.parts)-1))]
                    watchedList[i][j] = a
            userVideoNumber = random.randint(10,20) # her user için izlenen video sayısı
        self.user_list = watchedList

    def new_part(self, user_id, part_id) : #Programı denemek için userNumber ve newPart_id'nin belirlendiği bir metot. JS'e geçince kaldırılacak.
        self.userNumber = int(user_id)
        self.newPart = int(part_id)

    def export_new_part_to_watched_parts(self) :
        watched_db = Watched_Parts_db_Handler()
        watched_db.insert_to_db(self.userNumber, self.newPart) #Yeni part'ın user no ile watched_parts tablosuna eklenmesi

    def apriori_for_new_video(self):
        print(self.newPart,"videosu için :\n")
        print(self.newPart," videosunu izleyenlerin izlediği diğer videolar için:\n")
        matched = 0 #izlenen video, user no'larda yer alıyor mu almıyor mu saptamak için.
        jCounter = 0 #Yeni videoyu izlemiş olan user sayısını saymak için
        jList = [] #unique olacak liste (newPartın yanında neler izlenmiş toplamda, o listeyi tutuyor)
        jTempList = [] #unique olmayacak liste (önerilecek herbir videonun kaç tane user no'da yer aldığını saptayabilmek ve rate'ini bulmak için)
        jCountList = [] #önerilecek videoların countlarının tutulduğu liste
        recommendation_list = [] #öneri listesi
        watched_list = []
        for u in self.user_list :
            if u[0] != self.userNumber :
                watched_list.append(u)
        for j in watched_list :
            for k in j :
                if self.newPart == k :
                    jCounter+=1
                    for a in range(1,len(j)) :
                        jTempList.append(j[a])
                        if j[a] not in jList : #unique bir liste olmalı. Aynı video listede birden fazla yer almamalı.
                            jList.append(j[a]) #kullanıcının izlediği video ile beraber izlenen videoların bir listede tutulması
                        if self.newPart in jTempList :
                            jTempList.remove(self.newPart) #Girilen videonun listeden çıkarılması
                    jList.remove(self.newPart) #kullanıcının zaten izlemiş olduğu (girilen video) videonun çıkarılması
                    matched =1
                    tempList = []
                    if len(j) > 1 : #farklı video keşfi için transactiondaki video sayısı birden fazla olmalı
                        for a in range(1,len(j)) :
                            if j[a] != k :
                                print("User no :" ,j[0]," Potansiyel önerilecek video : ",j[a])
                    else :
                        print("Aynı videonun izlendiği user no'da başka video izlenmemiş.")
        if len(jList) != 0 :
            print("\n",self.newPart,"videosunun yanında izlenen diğer videolar : ",jList)
            for o in range(len(jList)) :
                x = jList[o]
                jCountList.append([jList[o],jTempList.count(x)])
            print("\nVe bulunma sayıları : ",jCountList)
            totalCount=0
            for c in range(len(jCountList)) :
                totalCount += jCountList[c][1]
            for r in range(len(jList)) :
                rate = float(100*(jCountList[r][1]/totalCount))
                recommendation_list.append([jList[r],rate])
            recommendation_list.sort(key=lambda x:x[1], reverse=True)
            print("\n")
            for s in range(len(recommendation_list)) :
                print(s+1,".öneri : ",recommendation_list[s][0]," yüzde : %" , round(recommendation_list[s][1],2))
        print(jCounter,"tane user listesinde video bulundu.")
        if matched == 0 :
            print("User listelerinde yer almadığından öneri yapılamadı.\n")

        self.apriori_list = recommendation_list

        newPartCategory = ""
        recommendation_list2 = [] #kategori tabanlı apriori öneri listesi
        for x in range(len(self.part_list)) :
            if self.newPart == self.part_list[x][1] :
                newPartCategory = self.part_list[x][2]
        for p in range(len(self.apriori_list)) :
            for l in range(len(self.part_list)) :
                if self.apriori_list[p][0] == self.part_list[l][1] :
                    if self.part_list[l][2] == newPartCategory :
                        recommendation_list2.append(self.apriori_list[p])
        self.apriori_list2 = recommendation_list2

        self.export_new_part_to_watched_parts()
        return self.apriori_list,self.apriori_list2

    def apriori_calculate(self):
        matched = 0 #izlenen video, user no'larda yer alıyor mu almıyor mu saptamak için.
        jCounter = 0 #Yeni videoyu izlemiş olan user sayısını saymak için
        jList = [] #unique olacak liste (newPartın yanında neler izlenmiş toplamda, o listeyi tutuyor)
        jTempList = [] #unique olmayacak liste (önerilecek herbir videonun kaç tane user no'da yer aldığını saptayabilmek ve rate'ini bulmak için)
        jCountList = [] #önerilecek videoların countlarının tutulduğu liste
        recommendation_list = [] #öneri listesi
        watched_list = []
        for u in self.user_list :
            if u[0] != self.userNumber :
                watched_list.append(u)
        for j in watched_list :
            # Finding other matched users who watched current vid.
            for k in j :
                if self.newPart == k :
                    jCounter+=1
                    for a in range(1,len(j)) :
                        jTempList.append(j[a])
                        if j[a] not in jList : #unique bir liste olmalı. Aynı video listede birden fazla yer almamalı.
                            jList.append(j[a]) #kullanıcının izlediği video ile beraber izlenen videoların bir listede tutulması
                        if self.newPart in jTempList :
                            jTempList.remove(self.newPart) #Girilen videonun listeden çıkarılması
                    jList.remove(self.newPart) #kullanıcının zaten izlemiş olduğu (girilen video) videonun çıkarılması
                    matched =1
                    tempList = []
        if len(jList) != 0 :
            for o in range(len(jList)) :
                x = jList[o]
                jCountList.append([jList[o],jTempList.count(x)])
            totalCount=0
            for c in range(len(jCountList)) :
                totalCount += jCountList[c][1]
            for r in range(len(jList)) :
                rate = float(100*(jCountList[r][1]/totalCount))
                recommendation_list.append([jList[r],rate])
            recommendation_list.sort(key=lambda x:x[1], reverse=True)

        self.apriori_list = recommendation_list

        newPartCategory = ""
        recommendation_list2 = [] #kategori tabanlı apriori öneri listesi
        for x in range(len(self.part_list)) :
            if self.newPart == self.part_list[x][1] :
                newPartCategory = self.part_list[x][2]
        for p in range(len(self.apriori_list)) :
            for l in range(len(self.part_list)) :
                if self.apriori_list[p][0] == self.part_list[l][1] :
                    if self.part_list[l][2] == newPartCategory :
                        recommendation_list2.append(self.apriori_list[p])
        self.apriori_list2 = recommendation_list2


a = Apriori()

def run_apriori_for(user_id, part_id):
    a.import_videos()
    a.import_users()
    a.import_watched_parts()
    a.new_part(user_id,part_id)
    a.apriori_calculate()

def return_recommendation_part_id_lists(user_id, part_id):
    run_apriori_for(user_id, part_id)
    dic = {}
    dic['general_apriori'] = [i[0] for i in a.apriori_list]
    dic['category_apriori'] = [i[0] for i in a.apriori_list2]
    return dic
