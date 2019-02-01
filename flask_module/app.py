from flask import Flask, render_template, request
import json
from search import *
from apriori_final import *
from db.database_handlers import *

video_db = Video_db_Handler()
parts_db = Parts_db_Handler()
watched_parts_db = Watched_Parts_db_Handler()
user_db = User_db_Handler()

app = Flask(__name__)
app.debug = True

@app.route('/signInUser', methods=['POST','GET'])
def signUpUser():
    user =  request.form['user_name']
    password = request.form['password']
    selected = user_db.select_from_db_dic(user)
    if not selected == [] and password==selected[0]['password']:
        return json.dumps({'status':'OK', 'user_id':selected[0]['user_id']})
    else:
        return json.dumps({'status':'KO'})

@app.route('/getDataFromPartIds', methods=['POST','GET'])
def getDataFromPartIds():
    parts = request.form.getlist('parts[]')
    res = []
    for id in parts:
        dic = {}
        part_id = str(id);
        curr_part_data = parts_db.select_from_db_dic(part_id)[0]
        curr_video_data = video_db.select_from_db_dic(curr_part_data['video_id'])[0]
        thumbnail_url = curr_video_data['thumbnail_url']
        title = curr_video_data['name']
        start_time = curr_part_data['start_time']
        end_time = curr_part_data['end_time']
        category = curr_part_data['category']
        url = curr_video_data['url']
        dic["part_id"] = part_id
        dic["thumbnail_url"] = thumbnail_url
        dic["title"] = title
        dic["start_time"] = start_time
        dic["end_time"] = end_time
        dic["category"] = category
        dic["url"] = url
        res.append(dic)
    return json.dumps({'parts_data':res})

@app.route('/getVideoParts', methods=['POST','GET'])
def getVideoPartsFromPartId():
    part_id = str(request.form['part_id'])
    curr_part_data = parts_db.select_from_db_dic(part_id)[0]
    curr_video_data = video_db.select_from_db_dic(curr_part_data['video_id'])[0]
    video_id = curr_part_data['video_id']
    parts = parts_db.select_parts_by_video_id_dic(video_id)
    parts.sort(key=lambda x: x['part_id'])
    for p in parts:
        p["thumbnail_url"] = curr_video_data['thumbnail_url']
        p["title"] = curr_video_data['name']
        p["url"] = curr_video_data['url']
    return json.dumps({'status':'OK', 'parts':parts})

@app.route('/getAprioriLists', methods=['POST','GET'])
def getAprioriLists():
    user_name = request.form['user_name']
    part_id = request.form['part_id']
    a = return_recommendation_part_id_lists(user_name, part_id)
    return json.dumps(a)
    # return return_recommendation_part_id_lists(user_name, part_id)

@app.route('/search')
def searching():
    return render_template('search.html')

@app.route('/searchingText', methods=['POST','GET'])
def searchingText():
    wanted = request.form['search']
    se = SearchEngine()
    se.select_part_most_related(wanted)
    parts = []
    for count in se.part_counts:
        if count[2]!=0:
            p = parts_db.select_from_db_dic(int(count[1]))
            part_id = p[0]['part_id']
            parts.append(part_id)
    return json.dumps({'status':'OK', 'parts':parts})

@app.route('/')
def signing():
    return render_template('index.html')

@app.route('/video')
def loadVideoPage():
    return render_template('video.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
