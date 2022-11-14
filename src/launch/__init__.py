import os,sys
import xdg.DesktopEntry
import thefuzz #Just in case I want to make my own version later to remove the dependency on fzf
import subprocess,re
desktop_file_paths=[os.path.expanduser("~")+"/.local/share/applications","/usr/share/applications","/usr/local/share/applications"]
applications={}
def extractApplications():
    if sys.platform=='darwin':
        stack=list(os.scandir('/Applications'))
        visited={}
        while len(stack)>0:
            v=stack.pop()
            if v not in visited:
                #Visit
                visited[v]=True
                if v.name.endswith(".app"):
                    info=[]
                    info.append(' '.join(['open','-a',f'"{v.path}"']))
                    info.append(False)
                    applications[v.name[:-4]]=info
                    continue #No need to search deeper
                if not v.is_dir():
                    continue
                for w in os.scandir(v):
                    if w not in visited:
                        stack.append(w)  
        return      
    for path in desktop_file_paths:
        for file in os.listdir(path):
            if not file.endswith(".desktop"):
                continue
            desktop_file=xdg.DesktopEntry.DesktopEntry(path+'/'+file)
            info=[]
            if not desktop_file.getNoDisplay():
                info.append(desktop_file.getExec())
                info.append(info.append(desktop_file.getTerminal()))
                applications[desktop_file.getName()]=info
    

def matchApplications():
    fzf = subprocess.Popen(["fzf","-1","-e","-0","--prompt=Application: ","--query="+(sys.argv[1] if len(sys.argv)>1 else "")], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    selection=fzf.communicate(input='\n'.join(applications.keys()).encode())[0].decode().strip()
    if (fzf.returncode==1):
        print("No matching applications!")
        return
    if not selection:
        return
    else:
        info=applications[selection]
    f=subprocess.Popen(re.sub(" %.+?(?=( |$))", "",info[0]),shell=True,stdout=(subprocess.DEVNULL if not info[1] else None))
    if info[1]:
        f.wait()
    #subprocess.run(["fzf","--expect="+",".join(applications.keys())])
                    
def main():
    extractApplications()
    matchApplications()
