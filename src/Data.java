


public class Data {
	private String id;
	private String key;
	private Fields fields;
	
    public Fields getFields() {
		return fields;
	}

	public void setFields(Fields fields) {
		this.fields = fields;
	}

	public String getID() { return id; }

    public void setID(String id) { this.id = id; }

    public String getkey() { return key; }

    public void setkey(String key) { this.key = key; }

    public String toString() {
	// key; issuetype; resolution
	
        //return String.format("%s; %s; %s", key, fields.issuetype.getName(), fields.resolution.getName());
	//return String.format("%s; %s; %s", key, (fields.issuetype!=null?fields.issuetype.getName():""), (fields.resolution!=null?fields.resolution.getName():""));
	return String.format("%s; %s; %s; %s", key, (fields.issuetype!=null?fields.issuetype.getName():""), (fields.resolution!=null?fields.resolution.getName():""), (fields.priority!=null?fields.priority.getName():""));
    }

}
