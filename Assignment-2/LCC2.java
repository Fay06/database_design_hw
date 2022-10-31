import java.sql.*;
import java.util.HashMap;
import java.util.LinkedList;

public class LCC2 
{
	public static void executeLCC() {
		/************* 
		 * Add you code to compute LCC for each node, and write it back into the database.
		 ************/
		System.out.println("-------- PostgreSQL " + "JDBC Connection Testing ------------");
        try {
            Class.forName("org.postgresql.Driver");
        } catch (ClassNotFoundException e) {
            System.out.println("Where is your PostgreSQL JDBC Driver? " + "Include in your library path!");
            e.printStackTrace();
            return;
        }

        System.out.println("PostgreSQL JDBC Driver Registered!");
        Connection connection = null;
        try {
            connection = DriverManager.getConnection("jdbc:postgresql://localhost:5432/socialnetwork","vagrant", "vagrant");
        } catch (SQLException e) {
            System.out.println("Connection Failed! Check output console");
            e.printStackTrace();
            return;
        }

        if (connection != null) {
            System.out.println("You made it, take control your database now!");
        } else {
            System.out.println("Failed to make connection!");
            return;
        }

        Statement stmt = null;
        String query = "select * from friends;";
		HashMap<String, LinkedList<String>> database = new HashMap<>();
        try {
            stmt = connection.createStatement();
            ResultSet rs = stmt.executeQuery(query);
			// recording the data
            while (rs.next()) {
                String userid1 = rs.getString("userid1");
                String userid2 = rs.getString("userid2");
				if(database.containsKey(userid1)) {
					database.get(userid1).add(userid2);
				}else {
					LinkedList<String> friendList = new LinkedList<>();
					friendList.add(userid2);
					database.put(userid1, friendList);
				}
            }
			
			// add column lcc and make the default value to be 0.0
      		// stmt.executeUpdate("alter table users add column lcc real");
			stmt.executeUpdate("update users set lcc = 0.0");

			// calculate llc
			for(String key : database.keySet()) {
				LinkedList<String> friends = database.get(key);
				int k = friends.size();
				int n = 0;
				// calculate n
				for(int i = 0; i < k - 1; i++) {
					String curFriend = friends.get(i);
					for(int j = i + 1; j < k; j++) {
						String compFriend = friends.get(j);
						if(database.get(curFriend).contains(compFriend)) {
							n++;							
						}
					}
				}
				double lcc = (2.0 * n) / (k * (k - 1));

				//System.out.println("userid: " + key + "  lcc: " + lcc + "  n: " + n + "  k: " + k);

				String update = "update users set lcc = " + lcc + "where userid = '" + key + "'";
      			stmt.executeUpdate(update);

			}

			// commit the change
			// connection.commit();

			// close statements
			stmt.close();
        } catch (SQLException e ) {
            System.out.println(e);
        }
	}

	public static void main(String[] argv) {
        executeLCC();


		Connection connection = null;
        try {
            connection = DriverManager.getConnection("jdbc:postgresql://localhost:5432/socialnetwork","vagrant", "vagrant");
        } catch (SQLException e) {
            System.out.println("Connection Failed! Check output console");
            e.printStackTrace();
            return;
        }

        if (connection != null) {
            System.out.println("You made it, take control your database now!");
        } else {
            System.out.println("Failed to make connection!");
            return;
        }

        Statement stmt = null;
        String query = "select * from users;";
        try {
            stmt = connection.createStatement();
            ResultSet rs = stmt.executeQuery(query);
            while (rs.next()) {
                String name = rs.getString("userid");
				String lcc = rs.getString("lcc");
                System.out.println(name + "\t" + lcc);
            }
            stmt.close();
        } catch (SQLException e ) {
            System.out.println(e);
        }
	}
}
