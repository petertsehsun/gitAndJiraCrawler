GS = -cp
CLASSPATH = -classpath
JC = javac
JDFLAGS = ../google-gson-2.2.2-release/google-gson-2.2.2/gson-2.2.2.jar:../mysql-connector-java-5.1.22/mysql-connector-java-5.1.22-bin.jar
.SUFFIXES: .java .class
.java.class:
	$(JC) $*.java $(GS) .:$(JDFLAGS)

CLASSES = \
        Resolution.java \
        Project.java \
        Priority.java \
        IssueType.java \
	FixVersions.java \
	Comment.java \
	Assignee.java \
	Fields.java \
	Data.java \
	Jira_main.java \

default: classes

classes: $(CLASSES:.java=.class)

clean:
	$(RM) *.class
