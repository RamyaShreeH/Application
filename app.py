from flask import Flask, jsonify, request
from flask_mongoengine import MongoEngine
import datetime

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    'db':'Application',
    'host':'localhost',
    'port': 27017
}

db = MongoEngine()
db.init_app(app)

class Comment(db.EmbeddedDocument):
    _id = db.IntField(primary_key = True)
    description = db.StringField()
    
class application(db.Document):
    id = db.IntField(primary_key=True)
    name = db.StringField()
    isDeleted = db.StringField()
    #comment1 = db.EmbeddedDocumentField(Comment)
    #comment2 = db.EmbeddedDocumentField(Comment)
    #comment = db.EmbeddedDocumentField(Comment)
    comment = db.ListField(db.EmbeddedDocumentField(Comment))

    creation_time = db.DateTimeField(default = datetime.datetime.now)
    modified_time = db.DateTimeField()
    deleted_time = db.DateTimeField()

class action(db.Document):
    id = db.SequenceField(primary_key=True)
    action = db.StringField()
    application_id = db.IntField()
    creation_time = db.DateTimeField()
    modified_time = db.DateTimeField()
    deleted_time = db.DateTimeField()

@app.route('/applications', methods=["POST"])
def add_application():
    #data = request.get_json()
    data = request.json
    # l = len(data['comment'])
    # print("length:",l)
    commentList = []
    for i in range(0,len(data['comment'])):
        _id = data['comment'][i]['_id']
        description = data['comment'][i]['description']
        comment = Comment(_id = _id, description = description)
        print("Comment",comment)
        commentList.append(comment)

    print("CommentList:", commentList)
    _id1 = data['comment'][0]['_id']
    description1 = data['comment'][0]['description']
    
    _id2 = data['comment'][1]['_id']
    description2 = data['comment'][1]['description']

    '''_id = data['comment'][0]['_id']
    description = data['comment'][0]['description']
    comment = Comment(_id = _id, description = description)'''
 
    applications = application(id = data.get('id'), name = data.get('name'), isDeleted = 'False', comment=[Comment(_id = _id1, description = description1), Comment(_id = _id2, description = description2)]).save()
    #applications = application(id = data.get('id'), name = data.get('name'), isDeleted = 'False', comment=[for items in commentList:]).save()

    application_id = data.get('id')
    #applications = application( id = data.get('id'), name = data.get('name'), isDeleted = 'False',comment = comment).save()
    print('adding action for application create')
    action(application_id = application_id, action = "Added the application", creation_time = datetime.datetime.now).save()
    return  jsonify(applications), 201

@app.route('/applications', methods = ['GET'])
def  get_applications():
    '''applications = application.objects()
    return  jsonify(applications), 200'''

    page = int(request.args.get('page'))
    limit = int(request.args.get('limit',2))
    offset = (page - 1) * limit
    list = application.objects.skip(offset).limit(limit)
    return  jsonify(list), 200


@app.route('/application/<id>', methods = ['GET'])
def get_one_application(id):
    print("Id:",id)
    one_application = application.objects(id=id).first_or_404()
    return jsonify(one_application), 200


@app.route('/application/<id>', methods=['PUT'])
def update_application(id):
    json = request.json
    name = json['name']
    application_id = id
    one_application = application.objects.get_or_404(id=id)
    one_application.update(name = name, modified_time = datetime.datetime.now)
    action(application_id = application_id, action = "Updated the application", modified_time = datetime.datetime.now).save()
    return jsonify({"message":"Updated successfully."}), 200


@app.route('/application/<id>', methods=['DELETE'])
def delete_application(id):
    application_id = id
    one_application = application.objects.get_or_404(id=id)
    one_application.update(isDeleted = 'True', deleted_time = datetime.datetime.now)
    action(application_id = application_id, action = "Deleted the application", deleted_time = datetime.datetime.now).save()
    return jsonify({"message":"Deleted successfully."}), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({"message":"Not Found!."}),404

if __name__ =='__main__': 
    app.run(debug = True)