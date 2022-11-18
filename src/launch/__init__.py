import os,sys
import xdg.DesktopEntry
import subprocess,re,shutil
desktop_file_paths=[os.path.expanduser("~")+"/.local/share/applications","/usr/share/applications","/usr/local/share/applications"]
applications={}
def extractApplications():
    if sys.platform=='darwin':
        stack=list(os.scandir('/Applications'))+list(os.scandir('/System/Applications'))
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
    
class NoAppFound(Exception):
    pass
def matchApplications():
    initial_input=sys.argv[1] if len(sys.argv)>1 else ""
    if 0:
        fzf = subprocess.Popen(["fzf","-1","-e","-0","--prompt=Application: ","--query="+initial_input], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        selection=fzf.communicate(input='\n'.join(applications.keys()).encode())[0].decode().strip()
        if (fzf.returncode==1):
            raise NoAppFound
    else:
        import pzp
        try:
            print(applications.keys())
            pzp.pzp(applications.keys(),input=initial_input,lazy=True,handle_actions=None)
        except pzp.exceptions.AbortAction:
            return None
        except pzp.exceptions.AcceptAction as action:
            if action.action=='accept':
                return action.selected_item
            else:
                if not action.selected_item:
                    raise NoAppFound
                else:
                    return action.selected_item
    return selection
def runApplication():
    try:
        selection=matchApplications()
    except NoAppFound:
        print("No matching applications!")
        return
    if not selection:
        return
    info=applications[selection]
    f=subprocess.Popen(re.sub(" %.+?(?=( |$))", "",info[0]),shell=True,stdout=(subprocess.DEVNULL if not info[1] else None),stderr=subprocess.DEVNULL)
    if info[1]:
       f.wait() 
                     
def main():
    extractApplications()
    runApplication()
