import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
//import java.sql.DriverManager;
//import java.sql.ResultSet;
//import java.sql.SQLException;
//import java.sql.Statement;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
//import com.mysql.jdbc.Connection;




public class Jira_main {

	/**
	 * @param args
	 * @throws IOException 
	 * @throws SQLException 
	 */
	public static void main(String[] args) throws IOException{
		// TODO Auto-generated method stub
		if (args.length != 1)
		{
			System.out.println("you need an input!");
			return ;
		}
//		System.out.println(args[0]);
		String json = "";
		try{
				
				json = httpGet("https://issues.apache.org/jira/rest/api/latest/issue/"+args[0]);
		}
		catch(IOException e)
		{
			System.out.println(e.getMessage());
			return;
		}
		

		// Now do the magic.
		Data data = new Gson().fromJson(json, Data.class);
				

		
		////here store in DB
		//storeinDB(data);
		//
		System.out.println(data);
//		System.out.println("End");

	}
	public static String makeSqlStatement(String keyid, String bugResolution
			, String issue_type,String priority
			, String numberofComments
			, String descriptionSize
			, String created
			, String updated
			, String resolved
			, String assigneeName
			
			//,String jsonStructure
			)
	{
		return "INSERT INTO _jira (keyid, bug_resolution , issue_type" +
				",priority" +
				",number_comments" +
				",description_size" +
				",date_created" +
				",date_updated" +
				",date_resolved" +
				",assignee_name" +
				
				//", json_structure" +
				")" +
				" VALUES('" + keyid +
				"','" + bugResolution + 
				"','" + issue_type +
				"','" + priority +
				"','" + numberofComments +
				"','" + descriptionSize +
				"','" + created +
				"','" + updated +
				"','" + resolved +
				"','" + assigneeName +
				//"','" + jsonStructure +
				"')";
	}
	/*public static void storeinDB(Data data)
	{
        try {
       	 
			Class.forName("com.mysql.jdbc.Driver");
 
		} catch (ClassNotFoundException e) {
 
			System.out.println("Something has happened with the sql connection");
			e.printStackTrace();
			return;
 
		}
		Connection connection = null;
		 
		try {
			connection = (Connection) DriverManager
					.getConnection("jdbc:mysql://localhost:3306/jira",
							"root", "");
			Statement select = connection.createStatement();
		    //ResultSet rs = select.executeQuery("SELECT * FROM _jira");
			String sql_statement = makeSqlStatement(data.getkey()
					, data.getFields().resolution.getName()
					, data.getFields().issuetype.getName()
					, data.getFields().priority.getName()
					, data.getFields().comment.getTotal() 
					, Integer.toString(data.getFields().description.length())
					, data.getFields().created
					, data.getFields().updated
					, data.getFields().resolved
					, (data.getFields().assignee!= null ? data.getFields().assignee.getName() : "")
					
				//	,json
					);
			select.executeUpdate(sql_statement);
		    //while( rs.next() )
		     //    System.out.println( rs.getString("key") ) ;
		      // Close the result set, statement and the connection
		     
		    //rs.close() ;
     	    select.close() ;
		    connection.close() ;

 
		} catch (SQLException e) {
			System.out.println(e.getMessage());
			return;
		}
	}*/
	public static String httpGet(String urlStr) throws IOException {
		  URL url = new URL(urlStr);
		  HttpURLConnection conn =
		      (HttpURLConnection) url.openConnection();

		  if (conn.getResponseCode() != 200) {
			  String msg = conn.getResponseMessage();
			  conn.disconnect();
			  throw new IOException(msg);
		  }

		  // Buffer the result into a string
		  BufferedReader rd = new BufferedReader(
		      new InputStreamReader(conn.getInputStream()));
		  StringBuilder sb = new StringBuilder();
		  String line;
		  while ((line = rd.readLine()) != null) {
		    sb.append(line);
		  }
		  rd.close();
		  conn.disconnect();
		  return sb.toString();
		}

}

