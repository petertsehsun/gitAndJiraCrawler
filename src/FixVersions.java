import java.util.List;

import com.google.gson.JsonArray;



public class FixVersions {
	public FixVersions()
	{
		this.self = "";
		this.id = "";
		this.description = "";
		this.name = "";
		this.archived = "";
		this.released = "";
		this.releaseDate = "";
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
	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public String getArchived() {
		return archived;
	}
	public void setArchived(String archived) {
		this.archived = archived;
	}
	public String getReleased() {
		return released;
	}
	public void setReleased(String released) {
		this.released = released;
	}
	public String getReleasedDate() {
		return releaseDate;
	}
	public void setReleasedDate(String releasedDate) {
		this.releaseDate = releasedDate;
	}
	private String id;
	private String description;
	private String name;
	private String archived;
	private String released;
	private String releaseDate;
	
}
