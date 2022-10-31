from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
api = Api(app)
CORS(app)

class Users(Resource):
    def get(self):
        #####################################################################################3
        #### Important -- This is the how the connection must be done for autograder to work
        ### But on your local machine, you may need to remove "host=..." line if this doesn't work
        #####################################################################################3
        conn = psycopg2.connect("host=127.0.0.1 dbname=socialnetwork user=vagrant password=vagrant")
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
        conn = psycopg2.connect("host=127.0.0.1 dbname=socialnetwork user=vagrant password=vagrant")
        cur = conn.cursor()
        cur.execute("select name from users where userid in (select userid2 from friends where userid1 = '" + userid + "') order by name;")
        friend_list = []
        for c in cur.fetchall():
            friend_list.append(c[0])
            
        cur.execute("select * from users where userid ='" + userid + "';")
        for c in cur.fetchall():
            ret = {"userid": c[0], "name": c[1], "birthdate": str(c[2]), "joined": str(c[3]), "friends": friend_list}
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
        conn = psycopg2.connect("host=127.0.0.1 dbname=socialnetwork user=vagrant password=vagrant")
        cur = conn.cursor()

        cur.execute("select EXISTS (select * from users where userid = '" + userid + "');")
        userid_already_present = cur.fetchone()[0]

        if userid_already_present:
            return "FAILURE -- Userid must be unique", 201
        else:
            # Add your code to insert the new tuple into the database
            cur.execute("INSERT INTO users (userid, name, birthdate, joined) VALUES ('{}', '{}', '{}', '{}')".format(userid, args.name, args.birthdate, args.joined))
            conn.commit()
            return "SUCCESS", 201

    # Delete the user with the specific user id from the database
    def delete(self, userid):
        # Add your code to check if the userid is present in the database
        conn = psycopg2.connect("host=127.0.0.1 dbname=socialnetwork user=vagrant password=vagrant")
        cur = conn.cursor()

        cur.execute("select EXISTS (select * from users where userid = '" + userid + "');")
        userid_present = cur.fetchone()[0]

        if userid_present:
            # Add your code to delete the user from all of the tables, including
            # friends, users, follows, status, members, likes, etc.
            cur.execute("DELETE FROM friends WHERE userid1 = '{}' or userid2 = '{}'".format(userid, userid))
            cur.execute("DELETE FROM follows WHERE userid1 = '{}' or userid2 = '{}'".format(userid, userid))
            cur.execute("DELETE FROM likes WHERE statusid in (select statusid from status where userid = '{}')".format(userid))
            cur.execute("DELETE FROM status WHERE userid = '{}'".format(userid))
            cur.execute("DELETE FROM members WHERE userid = '{}'".format(userid))
            cur.execute("DELETE FROM likes WHERE userid = '{}'".format(userid))
            cur.execute("DELETE FROM users WHERE userid = '{}'".format(userid))
            conn.commit()
            return "SUCCESS", 201
        else:
            return "FAILURE -- Unknown Userid", 404
      
api.add_resource(Users, "/users/")
api.add_resource(User, "/user/<string:userid>")

app.run(debug=True, host="0.0.0.0", port=5000)
