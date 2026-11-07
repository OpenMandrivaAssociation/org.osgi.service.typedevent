Name:		org.osgi.service.typedevent
Version:	1.0.0
Release:	1
Summary:	OSGi Typed Event API
Group:		Development/Java
License:	ASL 2.0
URL:		https://docs.osgi.org/
Source0:	https://repo1.maven.org/maven2/org/osgi/org.osgi.service.typedevent/%{version}/org.osgi.service.typedevent-%{version}-sources.jar
Source1:	https://raw.githubusercontent.com/osgi/osgi/r8-cmpn-final/LICENSE#/org.osgi.service.typedevent-%{version}-LICENSE

BuildArch:	noarch
BuildRequires:	python
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildRequires:	mvn(org.osgi:osgi.annotation)
BuildRequires:	mvn(org.osgi:org.osgi.service.component.annotations)
BuildRequires:	mvn(org.osgi:org.osgi.namespace.implementation)
BuildRequires:	mvn(org.osgi:org.osgi.util.pushstream)
BuildSystem:	maven
BuildOption(install):	--file-name %{name}

%description
OSGi Typed Event 1.0. Event monitoring returns
org.osgi.util.pushstream.PushStream from the packaged Push Stream
1.1.0 API. RequireTypedEvent is a class-retention requirement
annotation. The implementation namespace constant is inlined.
Component property types and versioning annotations are compile-time
only. The package version is 1.0. This build targets Java 8.

%prep
%setup -q -c -T
# The builders' rpmuncompress passes a sources jar to tar.
python - %{SOURCE0} <<'PY'
import sys
import zipfile
zipfile.ZipFile(sys.argv[1]).extractall(".")
PY
rm -rf META-INF
cp -p %{SOURCE1} LICENSE
mkdir -p src/main/java
mv org src/main/java/
python - <<'PY'
from pathlib import Path

root = Path("src/main/java/org/osgi/service/typedevent")
names = sorted(str(path.relative_to(root)) for path in root.rglob("*.java"))
expect = [
    "TopicPermission.java",
    "TypedEventBus.java",
    "TypedEventConstants.java",
    "TypedEventHandler.java",
    "UnhandledEventHandler.java",
    "UntypedEventHandler.java",
    "annotations/RequireTypedEvent.java",
    "annotations/package-info.java",
    "monitor/MonitorEvent.java",
    "monitor/TypedEventMonitor.java",
    "monitor/package-info.java",
    "package-info.java",
    "propertytypes/EventFilter.java",
    "propertytypes/EventTopics.java",
    "propertytypes/EventType.java",
    "propertytypes/package-info.java",
]
if names != expect:
    raise SystemExit("java files " + " ".join(names))
if list(Path(".").rglob("packageinfo")):
    raise SystemExit("unexpected packageinfo")
if "Apache License" not in Path("LICENSE").read_text(encoding="utf-8"):
    raise SystemExit("LICENSE is not the Apache license")
if list(Path(".").rglob("*.jar")) or list(Path(".").rglob("*.class")):
    raise SystemExit("prebuilt binary remains")
for pom in Path(".").rglob("pom.xml"):
    pom.unlink()

Path("pom.xml").write_text("""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.osgi</groupId>
  <artifactId>org.osgi.service.typedevent</artifactId>
  <version>%{version}</version>
  <packaging>jar</packaging>
  <name>org.osgi:org.osgi.service.typedevent</name>
  <description>OSGi Typed Event.</description>
  <url>https://docs.osgi.org/</url>
  <licenses>
    <license>
      <name>Apache-2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.release>8</maven.compiler.release>
  </properties>
  <dependencies>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>org.osgi.util.pushstream</artifactId>
      <version>1.1.0</version>
    </dependency>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>osgi.annotation</artifactId>
      <version>8.1.0</version>
      <scope>provided</scope>
    </dependency>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>org.osgi.service.component.annotations</artifactId>
      <version>1.5.1</version>
      <scope>provided</scope>
    </dependency>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>org.osgi.namespace.implementation</artifactId>
      <version>1.0.0</version>
      <scope>provided</scope>
    </dependency>
  </dependencies>
  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.12.1</version>
        <configuration>
          <release>8</release>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-jar-plugin</artifactId>
        <version>3.3.0</version>
      </plugin>
    </plugins>
  </build>
</project>
""", encoding="utf-8")
pom = Path("pom.xml").read_text(encoding="utf-8")
for needle in (
    "<artifactId>org.osgi.service.typedevent</artifactId>",
    "<artifactId>org.osgi.util.pushstream</artifactId>",
    "<version>1.1.0</version>",
    "<artifactId>osgi.annotation</artifactId>",
    "<version>8.1.0</version>",
    "<artifactId>org.osgi.service.component.annotations</artifactId>",
    "<version>1.5.1</version>",
    "<artifactId>org.osgi.namespace.implementation</artifactId>",
    "<version>1.0.0</version>",
    "<scope>provided</scope>",
    "<version>%{version}</version>",
    "<release>8</release>",
):
    if needle not in pom:
        raise SystemExit("pom missing " + needle)
for needle in (
    "junit",
    "SNAPSHOT",
    "<source>",
    "<target>",
    "<parent>",
    "felix",
    "maven-bundle-plugin",
    "<artifactId>org.osgi.util.function</artifactId>",
    "<artifactId>org.osgi.util.promise</artifactId>",
    "<version>1.0.1</version>",
):
    if needle in pom:
        raise SystemExit("pom still contains " + needle)
PY

%build -a
java --module-path target/org.osgi.service.typedevent-%{version}.jar --describe-module org.osgi.service.typedevent > module-describe.txt
grep -q '^org.osgi.service.typedevent' module-describe.txt || { cat module-describe.txt; exit 1; }
grep -q ' automatic$' module-describe.txt || { cat module-describe.txt; exit 1; }
python - <<'PY'
import zipfile
from pathlib import Path
jar = Path("target/org.osgi.service.typedevent-%{version}.jar")
with zipfile.ZipFile(jar) as zf:
    names = set(zf.namelist())
need = (
    "org/osgi/service/typedevent/package-info.class",
    "org/osgi/service/typedevent/annotations/package-info.class",
    "org/osgi/service/typedevent/monitor/package-info.class",
    "org/osgi/service/typedevent/propertytypes/package-info.class",
)
for name in need:
    if name not in names:
        raise SystemExit("missing " + name)
if any(name.endswith("packageinfo") for name in names):
    raise SystemExit("unexpected packageinfo")
PY

%files -f .mfiles
%doc LICENSE
