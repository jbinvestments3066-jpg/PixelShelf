using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;

// One coordinator owns the playback order even when the form is hidden.
sealed class Playback : IDisposable {
    readonly List<Scene> library;
    List<Scene> sequence = new List<Scene>();
    Process player;
    bool repeat, queueRun;
    int index;
    public bool Busy {get;private set;}
    public string Error {get;private set;}
    public Scene Current {get;private set;}
    public string Position {get {return queueRun && Current!=null ? (index+1)+"/"+sequence.Count : "";}}
    public Playback(List<Scene> library) {this.library=library;}

    async Task Release() {
        // The outgoing process must finish stop_game before another bind.
        sequence.Clear();
        foreach(var scene in library) if(!scene.Released()) scene.Stop();
        var timeout=Stopwatch.StartNew();
        while((player!=null && !player.HasExited) || library.Exists(s=>!s.Released())) {
            if(timeout.ElapsedMilliseconds>12000) throw new IOException("OLED player did not stop.");
            // A player might have been in startup when the first stop was sent.
            if(Current!=null && !Current.Released()) Current.Stop();
            await Task.Delay(80);
        }
        if(player!=null) {player.Dispose();player=null;}
        Current=null;
    }
    public async Task Start(List<Scene> items, bool loop, bool playlist) {
        if(Busy || items.Count==0)return;
        Busy=true;Error=null;
        try {
            await Release();
            sequence=new List<Scene>(items); repeat=loop; queueRun=playlist; index=0;
            StartCurrent();
        } catch(Exception ex) {Error=ex.Message; sequence.Clear();}
        finally {Busy=false;}
    }
    public async Task Stop() {
        if(Busy)return;
        Busy=true;Error=null;
        try {await Release();} catch(Exception ex){Error=ex.Message;}
        finally {Busy=false;}
    }
    void StartCurrent() {
        var scene=sequence[index];
        string args="-NoProfile -ExecutionPolicy Bypass -File \""+scene.Player+"\" -ReportStop -SceneId "+scene.Id;
        if(queueRun || !repeat)args+=" -DurationSeconds "+scene.Seconds;
        var info=new ProcessStartInfo(Path.Combine(Environment.SystemDirectory,"WindowsPowerShell","v1.0","powershell.exe"),args);
        info.UseShellExecute=false;info.CreateNoWindow=true;
        player=Process.Start(info); Current=scene;
    }
    public void Update() {
        if(Busy || player==null || !player.HasExited)return;
        int code=player.ExitCode;
        player.Dispose();player=null;Current=null;
        // Exit 2 is the player's explicit external stop signal.
        if(code!=0 || !queueRun || sequence.Count==0) {
            if(code!=0 && code!=2)Error="Player failed. Check SteelSeries GG.";
            sequence.Clear();return;
        }
        index++;
        if(index==sequence.Count) {if(!repeat){sequence.Clear();return;} index=0;}
        try {StartCurrent();} catch(Exception ex){Error=ex.Message;sequence.Clear();}
    }
    public void Dispose() {
        if(Current!=null)Current.Stop();
        if(player!=null)player.Dispose();
    }
}
