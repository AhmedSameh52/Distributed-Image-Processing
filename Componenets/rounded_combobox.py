
class RoundedCombobox(ttk.Combobox):
  def __init__(self, root, options, radius=10, **kwargs):
    self.canvas = Canvas(root, width=self.master.winfo_reqwidth()+radius*2, height=self.master.winfo_reqheight()+radius*2, highlightthickness=0)
    self.canvas.pack(fill='both', expand=True)

    self.combobox = ttk.Combobox(self.canvas, **kwargs, values=options)
    self.combobox.pack(fill='both', expand=True)

    self.canvas.bind('<Button-1>', self.on_click)
    self.canvas.itemconfig(self.canvas.create_oval(radius, radius, self.canvas.winfo_width()-radius-1, self.canvas.winfo_height()-radius-1), fill='white')

  def on_click(self, event):
    self.combobox.invoke(self.current())