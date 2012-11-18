
public class Resolution {
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
	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	private String id;
	private String description;
	private String name;
	public Resolution()
	{
		this.self = "";
		this.id = "";
		this.description = "";
		this.name = "";
	}

}
