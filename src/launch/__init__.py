import os,sys
import xdg.DesktopEntry
import thefuzz #Just in case I want to make my own version later to remove the dependency on fzf
import subprocess,re
desktop_file_paths=[os.path.expanduser("~")+"/.local/share/applications","/usr/share/applications","/usr/local/share/applications"]
applications={}
def extractApplications():
    for path in desktop_file_paths:
        for file in os.listdir(path):
            if not file.endswith(".desktop"):
                continue
            desktop_file=xdg.DesktopEntry.DesktopEntry(path+'/'+file)
            if not desktop_file.getNoDisplay():
                applications[desktop_file.getName()]=desktop_file.getExec()
    

def matchApplications():
    fzf = subprocess.Popen(["fzf","-1","--query="+(sys.argv[1] if len(sys.argv)>1 else "")], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    selection=fzf.communicate(input='\n'.join(applications.keys()).encode())[0].decode().strip()
    if not selection:
        return
    subprocess.Popen(re.sub(" %.+?(?=( |$))", "",applications[selection]),shell=True)
    #subprocess.run(["fzf","--expect="+",".join(applications.keys())])
                    
def main():
    extractApplications()
    matchApplications()
