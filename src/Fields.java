import java.util.List;


public class Fields {
	public String summary;
	public IssueType issuetype;
	public Resolution resolution;
	public List<FixVersions> fixVersions;
	public Project project;
	public Priority priority;
	public String description;
	public Comment comment;
	public String created;
	public String updated;
	public String resolved;
	public Assignee assignee;
	public Fields()
	{
		this.assignee = new Assignee();
		resolved = "";
		updated="";
		created="";
		this.comment = new Comment();
		this.description = "";
		this.priority = new Priority();
		//this.fixVersions = new List<FixVersions>();
		
		this.resolution = new Resolution();
		this.issuetype = new IssueType();
		this.summary = "";
	}
	public Resolution getResolution() {
		return resolution;
	}

	public void setResolution(Resolution resolution) {
		this.resolution = resolution;
	}

	public IssueType getIssuetype() {
		return issuetype;
	}

	public void setIssuetype(IssueType issuetype) {
		this.issuetype = issuetype;
	}

	public String getSummary() {
		return summary;
	}

	public void setSummary(String summary) {
		this.summary = summary;
	}

}
