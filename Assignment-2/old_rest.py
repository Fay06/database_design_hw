from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
api = Api(app)
CORS(app)

class Users(Resource):
    def get(self):
        conn = psycopg2.connect("dbname=socialnetwork user=vagrant")
        cur = conn.cursor()

        cur.execute("select * from users;")
        d = {"tuples": []}
        for c in cur.fetchall():
            t_to_d = {"userid": c[0], "name": c[1], "birthdate": str(c[2]), "joined": str(c[3])}
            d["tuples"].append(t_to_d)
        return d,200

class User(Resource):
    # Return all the info about a specific user, including its friends as an array
    # FORMAT: {"userid": "user0", "name": "...", "birthdate": "...", "joined": "...", "friends": ["friendname1", "friendname2", ...]}
    def get(self, userid):
        # Add your code to construct "ret" using the format shown below
        # Friend names must be sorted in alphabetically increasing order
        # Birthdate should be of the format: "2007-02-04" (this is what Python str() will give you)
        conn = psycopg2.connect("dbname=socialnetwork user=vagrant")
        cur = conn.cursor()
        
        cur.execute("select name from users where userid in (select userid2 from friends where userid1 = '" + userid + "') order by name;")
        friend_list = []
        for c in cur.fetchall():
            friends.append(c[0])
            
        cur.execute("select * from users where userid ='" + userid + "';")
        ret = {"userid": cur.fetchone()[0], "name": cur.fetchone()[1], "birthdate": str(cur.fetchone()[2]), "joined": str(cur.fetchone()[3]), "friends": friend_list}
        
        return ret, 200

    # Add a new user into the database, using the information that's part of the POST request
    # We have provided the code to parse the POST payload
    # If the "userid" is already present in the database, a FAILURE message should be returned
    def post(self, userid):
        parser = reqparse.RequestParser()
        parser.add_argument("name")
        parser.add_argument("birthdate")
        parser.add_argument("joined")
        args = parser.parse_args()
        print(args)

        # Add your code to check if the userid is already present in the database
        conn = psycopg2.connect("dbname=socialnetwork user=vagrant")
        cur = conn.cursor()

        cur.execute("select EXISTS (select * from users where userid = '" + userid + "');")
        userid_already_present = cur.fetchone()[0]

        if userid_already_present:
            return "FAILURE -- Userid must be unique", 201
        else:
            # Add your code to insert the new tuple into the database
            cur.execute("INSERT INTO users (userid, name, birthate, joined) VALUES ('{}', '{}', '{}', '{}')".format(userid, args.name, args.birthdate, args.joined))
            conn.commit()
            return "SUCCESS", 201

    # Delete the user with the specific user id from the database
    def delete(self, userid):
        # Add your code to check if the userid is present in the database
        conn = psycopg2.connect("dbname=socialnetwork user=vagrant")
        cur = conn.cursor()

        cur.execute("select EXISTS (select * from users where userid = '" + userid + "');")
        userid_present = cur.fetchone()[0]

        if not userid_present:
            # Add your code to delete the user from all of the tables, including
            # friends, users, follows, status_updates, members
            cur.execute("DELETE FROM users where userid = '" + userid + "');")
            conn.commit()
            return "SUCCESS", 201
        else:
            return "FAILURE -- Unknown Userid", 404
      
api.add_resource(Users, "/users/")
api.add_resource(User, "/user/<string:userid>")

app.run(debug=True, host="0.0.0.0", port=5000)
