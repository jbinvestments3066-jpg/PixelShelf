using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Threading;
using System.Threading.Tasks;
using System.Text.RegularExpressions;
using System.Windows.Forms;
using System.Xml.Linq;

[assembly: AssemblyTitle("Pixel Shelf")]
[assembly: AssemblyProduct("Pixel Shelf")]
[assembly: AssemblyDescription("Pixel animation library and player for SteelSeries GameSense OLED displays")]
[assembly: AssemblyVersion("1.0.0.0")]
[assembly: AssemblyFileVersion("1.0.0.0")]

sealed class Scene {
    public string Title, Player, Signal, Category, Id, Film;
    public int Fps, Seconds;
    public override string ToString() { return Title; }
    public bool IsPlaying() {
        EventWaitHandle handle;
        if (!EventWaitHandle.TryOpenExisting(Signal, out handle)) return false;
        using(handle) return !handle.WaitOne(0);
    }
    public void Stop() {
        EventWaitHandle handle;
        if (EventWaitHandle.TryOpenExisting(Signal, out handle)) using(handle) handle.Set();
    }
    public bool Released() {
        EventWaitHandle handle;
        if (!EventWaitHandle.TryOpenExisting(Signal,out handle)) return true;
        handle.Dispose(); return false;
    }
}

sealed class Shelf : Form {
    const int FrameBytes = 832;
    static readonly Color Ink = Color.FromArgb(34,32,47), Paper = Color.FromArgb(252,238,209);
    static readonly Color Peach = Color.FromArgb(255,163,117), Violet = Color.FromArgb(196,177,221);
    static readonly Color ScreenInk = Color.FromArgb(40,46,64), Light = Color.FromArgb(244,224,180);
    readonly List<Scene> scenes = new List<Scene>();
    readonly ListBox list = new ListBox();
    readonly ComboBox category = new ComboBox();
    readonly TextBox search = new TextBox();
    byte[] selectedFrames;
    readonly Label status = new Label();
    readonly Button action=new Button(), stop=new Button(), libraryTab=new Button(), queueTab=new Button();
    readonly Button editQueue=new Button(), up=new Button(), down=new Button();
    readonly ComboBox mode=new ComboBox();
    readonly Label caption=new Label(), findLabel=new Label();
    readonly ToolTip tips=new ToolTip();
    readonly List<Scene> playlist=new List<Scene>();
    readonly Playback playback;
    bool inQueue;
    readonly string stateFile=Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),"PixelShelf","playlist.xml");
    readonly PictureBox preview = new PictureBox();
    readonly Bitmap bitmap = new Bitmap(128,52,PixelFormat.Format32bppArgb);
    readonly int[] pixels = new int[128*52];
    readonly Stopwatch clock = Stopwatch.StartNew();
    readonly NotifyIcon tray = new NotifyIcon();
    readonly System.Windows.Forms.Timer timer = new System.Windows.Forms.Timer();
    readonly EventWaitHandle open;
    bool chordDown, exiting;
    long nextStatus;
    int drawn = -1;
    string error = "";

    [DllImport("user32.dll")] static extern short GetAsyncKeyState(int key);
    [DllImport("user32.dll")] static extern short VkKeyScanEx(char ch,IntPtr layout);
    [DllImport("user32.dll")] static extern IntPtr GetKeyboardLayout(uint thread);
    [DllImport("user32.dll")] static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr window,IntPtr unused);
    [DllImport("user32.dll")] static extern bool SetForegroundWindow(IntPtr window);
    [DllImport("user32.dll")] internal static extern bool SetProcessDPIAware();
    static bool Down(int key) { return (GetAsyncKeyState(key) & 0x8000)!=0; }
    bool Chord() {
        if (!Down((int)Keys.F10)) return false;
        if (Down((int)Keys.Divide)) return true;
        IntPtr layout=GetKeyboardLayout(GetWindowThreadProcessId(GetForegroundWindow(),IntPtr.Zero));
        short slash=VkKeyScanEx('/',layout);
        if (slash==-1) return Down(0xBF);
        return Down(slash & 255) && ((slash & 256)==0 || Down(16))
            && ((slash & 512)==0 || Down(17)) && ((slash & 1024)==0 || Down(18));
    }
    static string Asset(string name) {
        if (String.IsNullOrEmpty(name) || !Regex.IsMatch(name, @"^(films/)?[A-Za-z0-9_.-]+$") || name.Contains(".."))
            throw new InvalidDataException("Invalid catalog filename.");
        return Path.Combine(AppDomain.CurrentDomain.BaseDirectory,name);
    }
    public Shelf(EventWaitHandle openSignal) {
        open=openSignal;
        foreach (var item in XDocument.Load(Asset("Shelf.xml")).Root.Elements("scene")) {
            var scene=new Scene {Title=(string)item.Attribute("title"), Fps=(int)item.Attribute("fps"),
                Film=Asset((string)item.Attribute("frames")), Id=(string)item.Attribute("id"),
                Category=(string)item.Attribute("category"), Seconds=(int)item.Attribute("seconds"),
                Player=Asset((string)item.Attribute("player")), Signal=(string)item.Attribute("stopEvent")};
            if(!Regex.IsMatch(scene.Id,@"^[a-z][a-z0-9_]*$") || new FileInfo(scene.Film).Length!=(long)scene.Seconds*scene.Fps*FrameBytes || scene.Fps<1 || scene.Fps>60 || !File.Exists(scene.Player))
                throw new InvalidDataException("Invalid scene: "+scene.Title);
            scenes.Add(scene);
        }
        if(scenes.Count==0) throw new InvalidDataException("The shelf is empty.");
        playback=new Playback(scenes);
        Text="Pixel Shelf"; BackColor=Paper; ClientSize=new Size(302,283);
        FormBorderStyle=FormBorderStyle.FixedSingle; MaximizeBox=false; MinimizeBox=false; ShowInTaskbar=true;
        StartPosition=FormStartPosition.CenterScreen; KeyPreview=true; DoubleBuffered=true;
        Font=new Font("Consolas",9f);
        preview.SetBounds(14,36,128,52);
        preview.Paint+=delegate(object sender,PaintEventArgs e){ e.Graphics.DrawImageUnscaled(bitmap,0,0); };
        caption.SetBounds(152,34,141,35); caption.ForeColor=Ink;caption.Font=new Font(Font,FontStyle.Bold);
        status.SetBounds(152,70,142,20);status.ForeColor=Ink;status.AutoEllipsis=true;
        ButtonStyle(libraryTab,"Library",11,97,78,24,delegate{SetView(false);});
        ButtonStyle(queueTab,"Playlist",92,97,100,24,delegate{SetView(true);});
        ButtonStyle(editQueue,"+ Queue",196,97,95,24,delegate{EditQueue();});
        category.SetBounds(11,126,163,23); category.DropDownStyle=ComboBoxStyle.DropDownList;
        category.AccessibleName="Category";category.BackColor=Paper;category.ForeColor=Ink;
        category.Items.Add("All categories");
        foreach(var scene in scenes) if(!category.Items.Contains(scene.Category)) category.Items.Add(scene.Category);
        category.SelectedIndex=0;
        findLabel.Text="Find";findLabel.ForeColor=Ink;findLabel.SetBounds(179,129,34,19);
        search.SetBounds(211,127,80,21);search.AccessibleName="Find animation";search.BackColor=Paper;
        search.ForeColor=Ink;search.BorderStyle=BorderStyle.FixedSingle;
        ButtonStyle(up,"Move up",11,126,135,23,delegate{MoveItem(-1);});
        ButtonStyle(down,"Move down",151,126,140,23,delegate{MoveItem(1);});
        list.SetBounds(11,153,280,84);list.IntegralHeight=false;list.BorderStyle=BorderStyle.None;
        list.DrawMode=DrawMode.OwnerDrawFixed;list.ItemHeight=21;list.BackColor=Paper;
        list.AccessibleName="Animations";list.DrawItem+=DrawRow;
        list.SelectedIndexChanged+=delegate{LoadPreview();};
        category.SelectedIndexChanged+=delegate{if(!inQueue)Filter();};
        search.TextChanged+=delegate{if(!inQueue)Filter();};
        list.DoubleClick+=delegate{Play();};
        ButtonStyle(action,"Play",11,249,86,25,delegate{Play();});
        ButtonStyle(stop,"Stop",102,249,76,25,async delegate{await playback.Stop();RefreshStatus();});
        mode.SetBounds(184,250,107,25);mode.DropDownStyle=ComboBoxStyle.DropDownList;
        mode.AccessibleName="Playback mode";mode.Items.AddRange(new object[]{"Loop","Play once"});mode.SelectedIndex=0;
        tips.SetToolTip(mode,"Library: one animation. Playlist: the entire queue.");
        LoadState();mode.SelectedIndexChanged+=delegate{SaveState();};
        Controls.AddRange(new Control[]{preview,caption,status,libraryTab,queueTab,editQueue,category,findLabel,search,up,down,list,action,stop,mode});
        SetView(false);
        KeyDown+=delegate(object s,KeyEventArgs e) {
            if(e.KeyCode==Keys.Escape) { Hide(); e.SuppressKeyPress=true; }
            if(e.KeyCode==Keys.Enter && list.Focused) { Play(); e.SuppressKeyPress=true; }
        };
        Icon=MakeIcon(); tray.Icon=Icon; tray.Text="Pixel Shelf  |  / + F10";
        var menu=new ContextMenuStrip(); menu.Items.Add("Open Pixel Shelf",null,delegate {Reveal();});
        menu.Items.Add("Quit Pixel Shelf",null,delegate {exiting=true; Close(); Application.ExitThread();});
        tray.ContextMenuStrip=menu; tray.DoubleClick+=delegate { Reveal(); }; tray.Visible=true;
        FormClosing+=delegate(object s,FormClosingEventArgs e) {
            if(!exiting && e.CloseReason==CloseReason.UserClosing) { e.Cancel=true; Hide(); }
        };
        timer.Interval=25; timer.Tick+=delegate { TickShelf(); }; timer.Start();
    }
    [DllImport("user32.dll")] static extern bool DestroyIcon(IntPtr icon);
    static Icon MakeIcon() {
        using(var tile=new Bitmap(16,16)) using(var g=Graphics.FromImage(tile)) {
            g.Clear(Color.Transparent);
            using(var dark=new SolidBrush(Ink)) using(var orange=new SolidBrush(Peach)) using(var pale=new SolidBrush(Paper)) {
                g.FillRectangle(dark,1,2,14,12); g.FillRectangle(orange,3,4,10,6);
                g.FillRectangle(dark,5,5,2,2); g.FillRectangle(dark,9,5,2,2);
                g.FillRectangle(pale,5,11,6,1);
            }
            IntPtr h=tile.GetHicon(); try { return (Icon)Icon.FromHandle(h).Clone(); } finally {DestroyIcon(h);}
        }
    }
    protected override void OnPaint(PaintEventArgs e) {
        base.OnPaint(e); var g=e.Graphics;
        // A hand-lettered 5x5 masthead. Each hex digit pair is one scanline.
        string[] letters={"1e111e1010","1f0404041f","11110a0a11","1f101c101f","101010101f","",
            "0f100e011e","11111f1111","1f101c101f","101010101f","1f101c1010"};
        using(var dark=new SolidBrush(Ink)) using(var shade=new SolidBrush(Violet)) {
            int x=16;
            foreach(string letter in letters) {
                for(int r=0;r<letter.Length/2;r++) {
                    int bits=Convert.ToInt32(letter.Substring(r*2,2),16);
                    for(int c=0;c<5;c++) if((bits & (16>>c))!=0) g.FillRectangle(dark,x+c*3,9+r*3,3,3);
                }
                x+=letter==""?7:18;
            }
            g.FillRectangle(shade,14,36,132,56); g.FillRectangle(dark,12,34,132,56);
            g.FillRectangle(dark,11,241,280,2);
        }
        TextRenderer.DrawText(g,"/ + F10",Font,new Rectangle(211,6,80,20),Ink,
            TextFormatFlags.Right|TextFormatFlags.VerticalCenter);
    }
    void DrawRow(object sender,DrawItemEventArgs e) {
        if(e.Index<0 || e.Index>=list.Items.Count)return;
        bool sel=(e.State & DrawItemState.Selected)!=0;
        using(var b=new SolidBrush(sel?Violet:Paper)) e.Graphics.FillRectangle(b,e.Bounds);
        var scene=(Scene)list.Items[e.Index]; int x=e.Bounds.X,y=e.Bounds.Y;
        if(sel) using(var b=new SolidBrush(Ink)) for(int i=0;i<3;i++) e.Graphics.FillRectangle(b,x+6+i*2,y+8+i*2,2,10-i*4);
        TextRenderer.DrawText(e.Graphics,scene.Title,Font,new Rectangle(x+21,y,e.Bounds.Width-72,21),Ink,
            TextFormatFlags.Left|TextFormatFlags.VerticalCenter|TextFormatFlags.EndEllipsis);
        var duration=TimeSpan.FromSeconds(scene.Seconds);
        TextRenderer.DrawText(e.Graphics,duration.ToString(@"m\:ss"),Font,new Rectangle(e.Bounds.Right-51,y,45,21),Ink,TextFormatFlags.Right|TextFormatFlags.VerticalCenter);
    }
    void ButtonStyle(Button b,string text,int x,int y,int width,int height,EventHandler click) {
        b.SetBounds(x,y,width,height);b.Text=text;b.ForeColor=Ink;b.BackColor=Paper;b.FlatStyle=FlatStyle.Flat;
        b.FlatAppearance.BorderColor=Ink;b.FlatAppearance.BorderSize=1;b.Cursor=Cursors.Hand;b.Click+=click;
    }
    void LoadState() {
        if(!File.Exists(stateFile))return;
        try {
            var root=XDocument.Load(stateFile).Root;
            foreach(var entry in root.Elements("item")) {
                var scene=scenes.Find(s=>s.Id==(string)entry.Attribute("id"));if(scene!=null)playlist.Add(scene);
            }
            mode.SelectedIndex=(string)root.Attribute("mode")=="once"?1:0;
        } catch(Exception ex){error="Playlist could not load";tips.SetToolTip(queueTab,ex.Message);}
    }
    void SaveState() {
        try {
            Directory.CreateDirectory(Path.GetDirectoryName(stateFile));
            var root=new XElement("playlist", new XAttribute("mode",mode.SelectedIndex==1?"once":"loop"));
            foreach(var scene in playlist) root.Add(new XElement("item",new XAttribute("id",scene.Id)));
            string temp=stateFile+".tmp";new XDocument(root).Save(temp);
            if(File.Exists(stateFile)) File.Replace(temp,stateFile,null); else File.Move(temp,stateFile);
        } catch(Exception ex){ MessageBox.Show(this,ex.Message,"Saving playlist"); }
    }
    void SetView(bool queue) {
        inQueue=queue;libraryTab.BackColor=queue?Paper:Violet;queueTab.BackColor=queue?Violet:Paper;
        editQueue.Text=queue?"Remove":"+ Queue";
        category.Visible=search.Visible=findLabel.Visible=!queue;up.Visible=down.Visible=queue;
        Filter();
    }
    void Filter(int index=-1) {
        var before=list.SelectedItem;
        list.BeginUpdate();
        try {
            list.Items.Clear();
            foreach(var scene in (inQueue?playlist:scenes)) if(inQueue ||
                ((category.SelectedIndex<=0 || scene.Category==(string)category.SelectedItem)
                && scene.Title.IndexOf(search.Text.Trim(),StringComparison.OrdinalIgnoreCase)>=0)) list.Items.Add(scene);
            if(index>=0 && list.Items.Count>0)list.SelectedIndex=Math.Min(index,list.Items.Count-1);
            else if(before!=null && list.Items.Contains(before)) list.SelectedItem=before;
            else if(list.Items.Count>0) list.SelectedIndex=0;
        } finally {list.EndUpdate();}
        if(list.SelectedItem==null) LoadPreview();
        RefreshStatus();
    }
    void EditQueue() {
        if(list.SelectedIndex<0)return;
        int index=list.SelectedIndex;
        if(inQueue)playlist.RemoveAt(index);else playlist.Add((Scene)list.SelectedItem);
        SaveState(); if(inQueue)Filter(index);else RefreshStatus();
    }
    void MoveItem(int delta) {
        int i=list.SelectedIndex,j=i+delta;if(!inQueue || i<0 || j<0 || j>=playlist.Count)return;
        var scene=playlist[i];playlist.RemoveAt(i);playlist.Insert(j,scene);SaveState();Filter(j);
    }
    void LoadPreview() {
        var scene=list.SelectedItem as Scene;
        selectedFrames=null; drawn=-1; error=""; clock.Restart(); nextStatus=0;
        if(scene!=null) {
            try {selectedFrames=File.ReadAllBytes(scene.Film);}
            catch(IOException) {error="Preview unavailable";}
        }
        caption.Text=scene==null?(inQueue?"Playlist is empty":"No matches"):scene.Title;
        if(selectedFrames==null) {
            using(var g=Graphics.FromImage(bitmap)) g.Clear(ScreenInk);
            preview.Invalidate(); status.Text=scene==null?"No matches":error; action.Enabled=false;
        }
    }
    public void Reveal() {
        if(!Visible) Show();
        Activate(); SetForegroundWindow(Handle); list.Focus(); nextStatus=0;
    }
    async void Play() {
        if(playback.Busy || selectedFrames==null)return;
        var items=inQueue?new List<Scene>(playlist):new List<Scene>{(Scene)list.SelectedItem};
        await playback.Start(items,mode.SelectedIndex==0,inQueue);
        RefreshStatus();
    }
    void RefreshStatus() {
        var scene=list.SelectedItem as Scene;
        bool ready=scene!=null && selectedFrames!=null;
        queueTab.Text="Playlist ("+playlist.Count+")";
        editQueue.Enabled=ready;up.Enabled=inQueue && list.SelectedIndex>0;
        down.Enabled=inQueue && list.SelectedIndex>=0 && list.SelectedIndex<playlist.Count-1;
        action.Enabled=!playback.Busy && ready;action.BackColor=Peach;
        stop.Enabled=!playback.Busy && (playback.Current!=null || scenes.Exists(s=>s.IsPlaying()));
        string info=playback.Busy?"Switching...":playback.Error!=null?playback.Error:
            playback.Current!=null?(playback.Position==""?"On station":"Playing "+playback.Position):
            scene!=null && scene.IsPlaying()?"On station":inQueue?"Playlist":list.Items.Count+" on shelf";
        status.Text=info;
        tips.SetToolTip(status,playback.Current!=null?playback.Current.Title:info);
        tips.SetToolTip(action,inQueue?"Play the playlist from the beginning":"Play the selected animation");
    }
    void TickShelf() {
        if(open.WaitOne(0)) Reveal();
        bool chord=Chord();
        if(chord && !chordDown) { if(Visible) Hide(); else Reveal(); }
        chordDown=chord;
        playback.Update();
        if(!Visible)return;
        var scene=(Scene)list.SelectedItem;
        long ms=clock.ElapsedMilliseconds;
        if(ms>=nextStatus) {RefreshStatus(); nextStatus=ms+300;}
        if(selectedFrames==null)return;
        int frame=(int)((ms*scene.Fps/1000)%(selectedFrames.Length/FrameBytes));
        if(frame==drawn)return;
        int start=frame*FrameBytes, light=Light.ToArgb(), dark=ScreenInk.ToArgb();
        for(int i=0;i<pixels.Length;i++) pixels[i]=(selectedFrames[start+i/8] & (128>>(i%8)))!=0?light:dark;
        var data=bitmap.LockBits(new Rectangle(0,0,128,52),ImageLockMode.WriteOnly,PixelFormat.Format32bppArgb);
        try { Marshal.Copy(pixels,0,data.Scan0,pixels.Length); } finally { bitmap.UnlockBits(data); }
        drawn=frame; preview.Invalidate();
    }
    protected override void Dispose(bool disposing) {
        if(disposing) {timer.Dispose();playback.Dispose();tips.Dispose();tray.Visible=false;tray.Dispose();bitmap.Dispose();}
        base.Dispose(disposing);
    }
    [STAThread] static void Main(string[] args) {
        bool hidden=Array.IndexOf(args,"--hidden")>=0;
        bool first;
        using(var open=new EventWaitHandle(false,EventResetMode.AutoReset,@"Local\AbiPixelShelfOpen",out first)) {
            if(!first) {if(!hidden)open.Set();return;}
            SetProcessDPIAware(); Application.EnableVisualStyles();
            try { using(var shelf=new Shelf(open)) {
                if(!hidden) shelf.Reveal();
                Application.Run();
            }} catch(Exception ex) { MessageBox.Show(ex.Message,"Pixel Shelf"); }
        }
    }
}
