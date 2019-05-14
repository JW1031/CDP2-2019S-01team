from flask import Flask
from flask_restful import Resource, Api
from flask_restful import reqparse

app = Flask(__name__)
api = Api(app)

class CreateUser(Resource):
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('email',type=str)
            parser.add_argument('user_name',type=str)
            parser.add_argument('password',type=str)
            args = parser.parse_args()
            
            _userEmail = args['email']
            _userName = args['user_name']
            _userpassword = args['password']
            
            return {'Email':_userEmail,'UserName':_userName, 'Password':_userpassword}
        except Exception as e:
            return {'error':str(e)}

api.add_resource(CreateUser,'/user')

if __name__=='__main__':
    app.run(host='155.230.28.128',port=18700,debug=True)