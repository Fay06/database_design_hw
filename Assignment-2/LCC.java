import java.sql.*;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Set;

public class LCC 
{
	public static void executeLCC() {
		
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
        String query = "select * from friends order by userid1 asc;";
		HashMap<String, ArrayList<String>> friend_map = new HashMap<>();
        try {
            stmt = connection.createStatement();
            ResultSet rs = stmt.executeQuery(query);
            while (rs.next()) {
                String userid1 = rs.getString("userid1");
				String userid2 = rs.getString("userid2");
                if(friend_map.containsKey(userid1)){
					friend_map.get(userid1).add(userid2);
				} else {
					ArrayList<String> arr = new ArrayList<>();
					arr.add(userid2);
					friend_map.put(userid1, arr);
				}
            }
			stmt.executeUpdate("ALTER table users ADD lcc real;");
			stmt.executeUpdate("UPDATE users SET lcc = 0.0;");
			
			for (String key : friend_map.keySet()) {
				int n = 0;
				int k = friend_map.get(key).size();
				for (int i = 0; i < k - 1; i++) {
					String friend1 = friend_map.get(key).get(i);
					for (int j = i + 1; j < k; j++) {
						String friend2 = friend_map.get(key).get(j);
						if(friend_map.get(friend1).contains(friend2)) {
							n++;
						}
					}
				}
				
				double lcc = (2.0 * n)/(k * (k - 1));
				
				stmt.executeUpdate("UPDATE users SET lcc = '" + lcc + "'where userid = '" + key + "';");
			}
			stmt.executeUpdate("select * from users order by userid asc;");
            stmt.close();
        } catch (SQLException e ) {
            System.out.println(e);
        }
	}

	public static void main(String[] argv) {
        executeLCC();
	}
}
