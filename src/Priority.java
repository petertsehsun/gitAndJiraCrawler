
public class Priority {
	private String self;
	public String getSelf() {
		return self;
	}
	public void setSelf(String self) {
		this.self = self;
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
	public String getId() {
		return id;
	}
	public void setId(String id) {
		this.id = id;
	}
	private String iconUrl;
	private String name;
	private String id;
	public Priority()
	{
		this.self = "";
		this.iconUrl = "";
		this.name = "";
		this.id = "";
	}
}
