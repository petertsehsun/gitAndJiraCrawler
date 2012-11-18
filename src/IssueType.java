 
public class IssueType {
	public IssueType()
	{
		this.self = "";
		this.id = "";
		this.description = "";
		this.iconUrl = "";
		this.name = "";
		this.subtask = "";
	}
	private String self;
	public String getSelf() {
		return self;
	}
	public void setSelf(String self) {
		this.self = self;
	}
	public String getId() {
		return id;
	}
	public void setId(String id) {
		this.id = id;
	}
	public String getDescription() {
		return description;
	}
	public void setDescription(String description) {
		this.description = description;
	}
	public String getIconUrl() {
		return iconUrl;
	}
	public void setIconUrl(String iconUrl) {
		this.iconUrl = iconUrl;
	}
	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public String getSubtask() {
		return subtask;
	}
	public void setSubtask(String subtask) {
		this.subtask = subtask;
	}
	private String id;
	private String description;
	private String iconUrl;
	private String name;
	private String subtask;
	

}
