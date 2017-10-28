## ECE -- DCS Font Editor
''' Copyright (C) 2016 Rodger "Iambian" Weisman
    
    Permission is hereby granted, free of charge, to any person obtaining a
    copy of this software and associated documentation files (the "Software"),
    to deal in the Software without restriction, including without limitation
    the rights to use, copy, modify, merge, publish, distribute, sublicense,
    and/or sell copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included
    in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
    OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
    CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
    TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
    SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from PIL import Image,ImageTk,PngImagePlugin
import Tkinter as tk
import ttk
import tkFileDialog
import tkFont
import sys
import os
import re

np = os.path.normpath
def getfont(s):
  return np(os.getcwd()+"/img/"+s+".dcf")
def getimg(s):
  return np(os.getcwd()+"/img/"+s+".png")

BLK,WHI,PRP,PNK = (0,1,2,3)
_PALETTE = (  32,0,0,         255,255,255,    128,0,128,      255,0,255, )

_OFFSET = 0  # -- Starting character in font table. Usually 0 or 32.

DEFAULTTEXTNAME = '__default_text__'

# ---------------------------------------------------------------------------

class _xdat():
  def __init__(self,objname,text='',wh=(96,64),xy=(0,0)):
    self.n = objname
    self.t = text
    self.x,self.y,self.w,self.h = xy+wh
    self.mp = 0
    self.c = None   #fmt: [[ 0=eof;1=nocont;2=cont ,"TEXT STRING"],[...]]
    self.reset()
  def reset(self):
    self.curx = self.x
    self.cury = self.y
    self.cp = 0

  def newline(self):
    self.cury += 8
    self.curx = self.x
    
  def homeup(self):
    self.curx = self.x
    self.cury = self.y
      
  def parse(self,s=''):
    s = s if s else self.t
    self.t = re.sub('\n\n*','\n',s)
    a = []
    s = re.sub('>>*','>',s)  #removes all adjacent dupes of '>'
    s = re.sub('##*','#',s)  #same for '#'
    s = s.replace('\r','')
    sa = re.split('#|>',s)
    sb = re.findall('#|>',s)
    for s,d in map(None,sa,sb):
      a.append([_SPACINGTYPE[d],s.lstrip('\n')])
    self.c = a
    self.mp = len(a)
    
  def setpage(self,page):
    if not self.c:
      self.parse()
    if page >= self.mp:
      page = self.mp-1
    if page < 0:
      page = 0
    self.cp = page
    return page

# ---------------------------------------------------------------------------

class TextHives():
  def __init__(self,font_table_path=None):
    self.curtext = DEFAULTTEXTNAME
    self.d = { self.curtext: _xdat(self.curtext,"Test text object.") }
    if font_table_path:
      self.chars = self.openfont(font_table_path)
      self.reset()
  def reset(self):
    self.palette = list(_PALETTE)
    self.fontimgs = dict()
    self.curimg = None
    self.curobj = self.d[self.curtext]
    self.cachefont()
    
  def openfont(self,file):
    chardict = dict() #fmt: charcode:  [long_name,char_width,[long_datalist (5byte)]]
    ldatdict = dict() #fmt: long_name: [long_datalist (5byte)]
    datalist = list() #fmt: [ref_to_longname_if_exist,[raw_data (3byte)],[metaname,vshift,adetect]]
    with open(file) as f:
      for line in f:
        try:
          meta = line.split(';')[1].split(' ')
        except:
          meta = []
        line = re.split('\t| |,|\\\\',line.split(';')[0])
        lbl = ''
        dref = ''
        data = []
        for i,word in enumerate(line):
          if word == '':
            continue
          if word[0].isalnum() and i==0:
            lbl = ''.join(i for i in word if i.isalnum() or i=='_')
          elif word[0].isalnum() and len(data)==1:
            dref = ''.join(i for i in word if i.isalnum() or i=='_')
          elif word[0] == '$' or word[0].isdigit():
            if word[1] == '$':
              word = word[1:]
            data.append(int(word.replace('$','0x'),0))
        if data==[]:
          continue
        if lbl != '':
          ldatdict[lbl] = data
        else:
          if len(meta)>0 and meta[0]:
            s = ''.join(c for c in meta[0] if c.isalnum() or c=='_')
            if s:
              if s[0].isdigit():
                s = "NAME_"+s
              mname = s
            else:
              mname = "CHR_"+str(len(datalist))
          else:
            mname = "CHR_"+str(len(datalist))
          if len(meta)>1:
            mvofst = True if meta[1].isdigit() and meta[1]=='1' else False
          else:
            mvofst = None
          if len(meta)>2:
            madetect =  True if meta[2].isdigit() and meta[2]=='1' else False
          else:
            madetect = None
          tmp = [mname,mvofst,madetect]
          datalist.append([dref,data,tmp])
    for n,i in enumerate(datalist):
      t = []
      longname = i[0]
      if  longname == '':
        w = (i[1][0] >> 4) & 0x07
        if i[1][0]&0x80:i[2][1]=True
        t.append( (i[1][0] << 4) & 0xF0 )  #0
        t.append(  i[1][1] & 0xF0 )        #1
        t.append( (i[1][1] << 4) & 0xF0 )  #2
        t.append(  i[1][2] & 0xF0 )        #3
        t.append( (i[1][2] << 4) & 0xF0 )  #4
        longname = i[2][0]
      else:
        if i[1][0]&0:i[2][1]=True
        w = i[1][0] & 0x07
        t = ldatdict[longname]
      chardict[n+_OFFSET] = [longname,w,t,i[2][1],i[2][2]] 
    return chardict
    
  def savefont(self,filename):
    def _getnib(byte,n):
      return format(byte>>4&15 if n else byte&15,'1x')
    s_top = ''
    s_low = ''
    for i in sorted(self.chars):
      a = self.chars[i]
      if len(a)==3:
        a.extend([None,False])
      name,width,data,vshift,adetect = a
      vshift = 1 if vshift else 0
      adetect = 1 if adetect else 0
      if width>6:
        width=6
      if vshift:
        width|=8
      if data == [n&0xF0 for n in data]:
        s  = ' .db $'+_getnib(width,0)+_getnib(data[0],1)+','
        s += '$'+_getnib(data[1],1)+_getnib(data[2],1)+','
        s += '$'+_getnib(data[3],1)+_getnib(data[4],1)
        s += '\t\t\t\t;'+str(name)+' '+str(vshift)+' '+str(adetect)+'\n'
        s_top += s
      else:
        s  = ' .db $F'+_getnib(width,0)+' \\ .dw '+name+'\t;'
        s += str(name)+' '+str(vshift)+' '+str(adetect)+'\n'
        s_top += s
        s  = str(name)+'\t\t\t.db '
        s += ','.join('$'+format(i,'02x') for i in data)
        s += '\t;\n'
        s_low += s
    with open(filename,'w') as f:
      f.write(s_top)
      f.write(s_low)
    
    
  def cachefont(self):
    for i in self.chars:
      a = self.chars[i]
      w = a[1]
      r = []
      for bytes in a[2]:
        for n in range(w+1):
          bit = (bytes & 0x80) >> 7
          r.append(bit)
          bytes = bytes << 1
      img = Image.new("P",(w+1,5))
      img.putdata(r)
      img.putpalette(self.palette)
      self.fontimgs[i] = img
      
      
  def add(self,objname,*args):
    if objname in self.d:
      obj = self.d[objname]
      obj.reset()
      return obj
    obj = self.d[objname] = _xdat(objname,*args)
    return obj
    
  def get(self,objname=''):
    if not objname:
      objname = self.curtext
    if objname not in self.d:
      self.curtext = objname = DEFAULTTEXTNAME
    return self.d[objname]
  def set(self,objname):
    if objname not in self.d:
      objname = DEFAULTTEXTNAME
    self.curtext = objname
    return objname
    
  def listnames(self):
    return [k for k in self.d]

  def newline(self,name):
    obj = self.get(name)
    obj.curx = obj.x
    obj.cury += 8
    
  def makebox(self,objname='',s=None):
    obj = self.get(objname)
    if not s:
      s = obj.t
    obj.w = 0
    obj.h = 5
    for c in s:
      if c=='\n':
        obj.h += 8
      if ord(c)>31 and ord(c)<255:
        obj.w += self.chars[ord(c)][1]
    self._drawnewbox(obj)
  def puts(self,objname='',s=None):
    obj = self.get(objname)
    if not s:
      s = obj.t
    for c in s:
      w = self.putc(c,objname)
      obj.curx += w #Do NOT merge above.
  def putc(self,c,objname=''):
    obj = self.get(objname)
    if c=='\n':
      obj.newline()
    c = ord(c)
    if c>255 or c<32:
      return 0
    w = self.chars[c][1]
    if obj.curx+w > obj.w or obj.cury+5 > obj.h:
      return 0
    if not self.curimg or obj is not self.curobj:
      self._drawnewbox(obj)
      self.curobj = obj
    ay = obj.cury
    if len(self.chars[c])>4 and self.chars[c][3]:
      ay+=1
    self.curimg.paste(self.fontimgs[c],(obj.curx,ay))
    return w

  def _drawnewbox(self,obj):
    i = Image.new('P',(obj.w,obj.h),BLK)
    i.putpalette(self.palette)
    self.curimg = i
    
    
class Message(ttk.Frame):
  def __init__(self,parent,width=0,height=0,**kwargs):
    ttk.Frame.__init__(self,parent,width=width,height=height)
    self.w = width
    self.h = height
    self.txt = ttk.Label(self,**kwargs)
    self.txt.pack(expand=1,fill=tk.BOTH)

  def configure(self,**kwargs):
    self.txt.configure(**kwargs)
  def config(self,**kwargs):
    self.configure(**kwargs)

  def draw(self,msg):
    self.txt.configure(text=msg)    
    
# ---------------------------------------------------------------------------

class Application(tk.Frame):
  def __init__(self,parent):
    tk.Frame.__init__(self,parent)
    self.df = tkFont.nametofont("TkDefaultFont")
    self.df.config(size=8,family="Tahoma")
    root = self.root = self.parent = parent

    self.parent.title("Font Editor for DCS")
    self.parent.geometry('355x285')
    self.parent.resizable(False,False)
    
    self.tester = TextHives(getfont("_dcsfont"))
    self.tester.reset()
    self.tester.get().t = "THE QUICK BROWN FOX JUMPED\nOVER THE SLOW LAZY DOG.\nthe quick brown fox jumped\nover the slow lazy dog.\n0123456789\n<>?\";\':<>[]{}()\n\\|!@#$%^&*()_+-=~`"
    self.tester.get().w = 180
    self.tester.get().h = 80
    self.tester.get().x = 1
    self.tester.get().y = 1
    self.tester.get().reset()
    self.tester.puts()
    self.pixels = {}     # canvid: [x,y]
    self.curchar = 0x41  # Current character
    self.default_width_autodetect = True
    self.img = ImageTk.PhotoImage(self.tester.curimg.convert("RGBA").resize((360,160)))
    self._LF = ImageTk.PhotoImage(Image.open(getimg("P1_LF")).convert('RGBA'))
    self._RI = ImageTk.PhotoImage(Image.open(getimg("P2_RI")).convert('RGBA'))
    
    t = self.main = tk.Frame(self.root)
    t.pack(expand=1,fill=tk.BOTH)
    
    self.adetect = tk.IntVar(t)
    self.adetect.set(1 if self.getfobj()[4] else 0)
    self.adetect.trace('w',self._adetectchanged)
    self.vshift = tk.IntVar(t)
    self.vshift.set(1 if self.getfobj()[3] else 0)
    self.vshift.trace('w',self._vshiftchanged)
    
    
    c = self.canvas = tk.Canvas(t,width=144,height=120)
    c.place(x=5,y=28,width=144,height=120)
    c.bind("<Button-1>",self.gridclick)
    # Draw the line here to allow overlapping to cover up any inaccuracies
    c.create_rectangle(1,5*18-1,7*18,5*18+1,width=0,fill='red')
    self.pixels = {}
    for y in range(0,6):
      for x in range(0,7):
        cx,cy = x*18+1,y*18+1
        z = c.create_rectangle(cx,cy,cx+16,cy+16,width=0,fill='#FFF')
        self.pixels[z] = (x,y)
    self.pcanv = tk.Canvas(t,width=250,height=122)
    self.pcanv.place(x=5,y=155,width=250,height=122)
    self.pcanv_id = self.pcanv.create_image(2,2,image=self.img,anchor=tk.NW)
    
    self.msg0 = Message(t,144,15,justify=tk.CENTER,anchor=tk.CENTER)
    self.msg0.place(x=5,y=5,width=144,height=15)
    
    
    self.fr1 = tk.Frame(t,width=200,height=120)
    self.fr1.place(x=150,y=5,width=200,height=140)

    self.b1a = tk.Button(self.fr1)
    self.b1a.place(x=5,y=7,width=20,height=20)
    self.b1a.config(width=20,image=self._LF,command=lambda:self._changesp(-1))
    self.b1b = tk.Button(self.fr1)
    self.b1b.place(x=170,y=7,width=20,height=20)
    self.b1b.config(width=20,image=self._RI,command=lambda:self._changesp(1))
    self.cb1 = ttk.Combobox(self.fr1,height=26,width=140,state='readonly')
    self.cb1.place(x=30,y=5,height=26,width=140)
    self.cb1.bind("<<ComboboxSelected>>",self._cb1changed)
    self.ck1 = tk.Checkbutton(self.fr1,height=13,width=120,anchor=tk.W,variable=self.vshift,text='Move V-align',state=tk.DISABLED)
    self.ck1.place(x=70,y=58,width=120,height=13)
    self.msg2 = Message(self.fr1,43,18,anchor=tk.E,text="Width:")
    self.msg2.place(x=5,y=40,width=43,height=18)
    self.ent2 = tk.Entry(self.fr1,width=45,font="TkFixedFont")
    self.ent2.place(x=50,y=40,width=20,height=18)
    self.ent2.bind("<Return>",self._widthchanged)
    self.ck2 = tk.Checkbutton(self.fr1,height=13,width=120,anchor=tk.W,variable=self.adetect,text='Autodetect width')
    self.ck2.place(x=70,y=40,width=120,height=18)
    self.msg3 = Message(self.fr1,43,18,anchor=tk.E,text="Name:")
    self.msg3.place(x=0,y=80,width=43,height=18)
    self.ent3 = tk.Entry(self.fr1,width=135)
    self.ent3.place(x=50,y=80,width=135,height=18)
    self.ent3.bind("<Return>",self._charnamechanged)
    
    self.btn1 = tk.Button(self.fr1,width=90,height=23,text="Load font",command=self._import)
    self.btn1.place(x=5,y=105,width=90,height=23)
    self.btn2 = tk.Button(self.fr1,width=90,height=23,text="Save font",command=self._export)
    self.btn2.place(x=105,y=105,width=90,height=23)
    
    self.btnx = tk.Button(t,width=90,height=40,text="Start from\nScratch",command=self._nukeit)
    self.btnx.place(x=260,y=180,width=85,height=40)
    self.btn3 = tk.Button(t,width=90,height=23,text="Save Changes",state=tk.DISABLED)
    self.btn3.place(x=260,y=222,width=85,height=23)
    self.btn4 = tk.Button(t,width=90,height=23,text="Exit",command=self.root.destroy)
    self.btn4.place(x=260,y=250,width=85,height=23)
    

    self.drawdata()
    
    


  def _(*a):pass

  def drawdata(self,*a):
    c = self.canvas
    fobj = self.getfobj()
    yof = 1 if fobj[3] else 0
    adetect = fobj[4]
    rev_pixels = {v:k for k,v in self.pixels.items()}
    for x in range(7):
      id = rev_pixels[(x,0 if fobj[3] else 5)]
      c.itemconfig(id,fill='#F88')
    shortest = 8
    for y,bytes in enumerate(fobj[2]):
      trailing = 0
      width = fobj[1]
      for x in range(7):
        bit = (bytes&0x80)>>7
        id = rev_pixels[(x,y+yof)]
        if width>0 or adetect:
          c.itemconfig(id,fill='black' if bit else 'white')
        else:
          c.itemconfig(id,fill='#F88')
        bytes = bytes<<1
        trailing = 0 if bit else trailing+1
        width -= 1
      if trailing<shortest:
        shortest = trailing
    # Shortest = shortest trailing width. 8-shortest or something like that
    # is our autodetected witdth
    if fobj[4]:
      width = 8-shortest
    else:
      width = fobj[1]
    fobj[1] = width  ## FEEDBACK. This ought to go in controller but meh
    self.msg0.draw("Char "+str(self.curchar)+" (0x"+format(self.curchar,'02x')+")")
    tb = self.tester.chars
    # Don't change. _updateentry sorts again, which produces incorrect results
    self.cb1['values'] = [self._getchrstr(k) for k in sorted(tb)]
    self.cb1.set(self._getchrstr(self.curchar))
    self.vshift.set(1 if self.getfobj()[3] else 0) # Point of possible infinite recursion
    self.adetect.set(1 if self.getfobj()[4] else 0)
    self._updateentry(self.ent2,width)
    
    self.tester.curimg = None
    self.tester.get().homeup()
    self.tester.puts()
    self.img = ImageTk.PhotoImage(self.tester.curimg.convert("RGBA").resize((360,160)))
    self.pcanv.itemconfig(self.pcanv_id,image=self.img)
    self._updateentry(self.ent3,self.getfobj()[0])
    self.red_button_state = 0
    
    
  def getfobj(self):
    fobj = self.tester.chars[self.curchar]
    if len(fobj)==3:
      fobj.extend([False,False])  #vertical downshift (T/F), do explicit width (no detect) (T/F)
    if len(fobj)!=5:
      raise ValueError("Font table dictionary entry corrupt")
    return fobj

  def gridclick(self,e=None):
    c = self.canvas
    lst = c.find_overlapping(e.x,e.y,e.x+1,e.y+1)
    id = None
    for i in lst:
      if i in self.pixels:
        id = i
    if not id:
      return
    fobj = self.getfobj()
    yof = 1 if fobj[3] else 0
    x,y = self.pixels[id]
    y -= yof
    if not 0<=y<5:
      return
    if x>=fobj[1] and not fobj[4]:
      return
    fobj[2][y] = fobj[2][y] ^ (0x80>>x)
    self.tester.reset()  # Flush font cache and rebuild from new data
    self.drawdata()
    

  def _getchrstr(self,k):
    itm = self.tester.chars[k]
    return  str(k)+": "+(itm[0] if itm[0] else (chr(k) if k<128 and k>31 else str(k)))


  def _cb1changed(self,*a):
    s = self.cb1.get()
    r = int(re.findall("\A[0-9]*:",s)[0][:-1]) #All nums b4 colon, excl colon.
    self.curchar = r
    self.drawdata()
    
    
  def _changesp(self,step):
    i=0
    for i in range(257):
      self.curchar = (self.curchar+step)&255
      if self.curchar in self.tester.chars:
        break
      if i>256:
        raise IndexError("self.tester.chars is empty")
    self.drawdata()

  def _vshiftchanged(self,*a):
    r = self.vshift.get()
    self.getfobj()[3] = True if r else False
    self.drawdata()

  def _adetectchanged(self,*a):
    r = self.adetect.get()
    self.getfobj()[4] = True if r else False
    self.drawdata()
    
  def _charnamechanged(self,*a):
    self.getfobj()[0] = ''.join(c for c in self.ent3.get() if c.isalnum() or c=='_')
    self.drawdata()
    
  def _widthchanged(self,*a):
    fobj = self.getfobj()
    fobj[4]=False
    try:
      s = int(re.sub(r"\D",'',self.ent2.get())[0])  # Get only one character
      if s>7:
        s=7
    except:
      s = 0
    self._updateentry(self.ent2,s)
    fobj[1]=s
    mask = [0b00000000,
            0b10000000,
            0b11000000,
            0b11100000,
            0b11110000,
            0b11111000,
            0b11111100,
            0b11111110][s]
    for n,i in enumerate(fobj[2]):
      fobj[2][n] = i&mask
    self.tester.reset()  # Flush font cache and rebuild from new data
    self.drawdata()
    
  def _import(self):
    f = tkFileDialog.askopenfilename(
      parent=self.root,
      filetypes=[('DCS Font Source','*.dcf')],)
    if f:
      a = self.tester.chars
      try:
        self.tester.chars = self.tester.openfont(f)
        self.tester.reset()
        self.drawdata()
      except:
        print "Font open failed."
        self.tester.chars = a
    
  def _export(self):
    f = tkFileDialog.asksaveasfilename(
      parent=self.root,
      defaultextension='.dcf',
      filetypes=[('DCS Font Source','*.dcf')],
    )
    if f:

      self.tester.savefont(f)
    
  def _nukeit(self):
    if self.red_button_state<3:
      self.red_button_state += 1
      return
    a = {}
    for i in range(256):
      a[i] = ["CHR_"+str(i),4,[0,0,0,0,0],False,True]
    self.tester.chars = a
    self.tester.reset()
    self.drawdata()

  def _updateentry(self,tkobj,dat,vals=None):
    tkobj.config(state='normal')
    if isinstance(tkobj,ttk.Combobox):
      vals = sorted(vals)
      if dat not in vals and vals:
        dat=vals[0]
      tkobj.set(str(dat))
      tkobj['values'] = vals
      tkobj.config(state='readonly')
    else:
      tkobj.delete(0,tk.END)
      tkobj.insert(0,str(dat))

## ==========================================================================
if __name__ == '__main__': 
  print "Loading objects..."
  root = tk.Tk()
  app = Application(root)
  app.pack()
  app.update()
  print "Application loaded"
  app.mainloop()
