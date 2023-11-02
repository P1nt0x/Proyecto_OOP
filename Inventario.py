# !/usr/bin/python3
# -*- coding: utf-8 -*-
import os.path as path
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox as mssg
import sqlite3
import platform #para determinar el OS
from datetime import datetime
if platform.system() == "Linux":  
  from PIL import Image, ImageTk

class Inventario:  
  def __init__(self, master=None):
    self.path = path.dirname(path.abspath(__file__))
    #self.path = r'X:/Users/ferna/Documents/UNal/Alumnos/2023_S2/ProyInventario'
    self.db_name = self.path + r'/Inventario.db'
    ancho=830;alto=630 # Dimensiones de la pantalla
    self.actualiza = False
    self.elimina = False
    self.proveedores = [] 

    # Crea ventana principal
    self.win = tk.Tk() 
    self.win.geometry(f"{ancho}x{alto}")
    # Esto detecta cual es el OS y retorna los codigos necesarios para abrir los iconos en Linux y Windows. se probo en Arch Linux x86
    if platform.system() == "Windows":
      self.win.iconbitmap(self.path + r'/f2.ico')
    elif platform.system() == "Linux":
      ima = Image.open('nino-modified.png') #Esta foto esta para mostrarse solamente en sistemas linux
      pho = ImageTk.PhotoImage(ima)
      self.win.wm_iconphoto(True, pho)
    self.win.resizable(False, False)
    self.win.title("Manejo de Proveedores") 
    #self.win.after(0,self.limpiaCampos)

    #Centra la pantalla
    self.centra(self.win,ancho,alto)
    
    # Contenedor de widgets   
    self.win = tk.LabelFrame(master)
    self.win.configure(background="#e0e0e0",font="{Arial} 12 {bold}",
    height=ancho,labelanchor="n",width=alto)
    self.tabs = ttk.Notebook(self.win)
    self.tabs.configure(height=590, width=799)

    #Frame de datos
    self.frm1 = ttk.Frame(self.tabs)
    self.frm1.configure(height=200, width=200)

    #Etiqueta IdNit del Proveedor
    self.lblIdNit = ttk.Label(self.frm1)
    self.lblIdNit.configure(text='Id/Nit', width=6)
    self.lblIdNit.place(anchor="nw", x=10, y=40)

    #Captura IdNit del Proveedor
    #self.idNit = ttk.Entry(self.frm1)
    #self.idNit.configure(takefocus=True)
    #self.idNit.place(anchor="nw", x=50, y=40)
    #self.idNit.bind("<KeyRelease>", self.validaIdNit, add="+")
    #self.idNit.bind("<KeyRelease>", self.updateProvider, add="+")
    #self.idNit.bind("<BackSpace>", lambda _:self.idNit.delete(len(self.idNit.get())),'end')
    

    self.actualizarProveedores()
    self.idNit = ttk.Combobox(self.frm1, values=self.proveedores)
    self.idNit.place(anchor="nw", x=50, y=40)
    self.idNit.configure(takefocus=True)
    self.idNit.bind("<<ComboboxSelected>>", self.buscar)
    self.idNit.bind("<<ComboboxSelected>>", self.updateProvider, add = "+")
    self.idNit.bind("<KeyRelease>", lambda event, widget = self.idNit, largo = 15 : self.validaVarChar(event, widget, largo), add="+")
    self.idNit.bind("<KeyRelease>", self.updateProvider, add="+")

    #Etiqueta razón social del Proveedor
    self.lblRazonSocial = ttk.Label(self.frm1)
    self.lblRazonSocial.configure(text='Razon social', width=12)
    self.lblRazonSocial.place(anchor="nw", x=218, y=40)

    #Captura razón social del Proveedor
    self.razonSocial = ttk.Entry(self.frm1)
    self.razonSocial.configure(width=36)
    self.razonSocial.place(anchor="nw", x=295, y=40)
    self.razonSocial.bind("<KeyRelease>", lambda event, widget=self.razonSocial, largo=50 : self.validaVarChar(event, widget, largo))

    #Etiqueta ciudad del Proveedor
    self.lblCiudad = ttk.Label(self.frm1)
    self.lblCiudad.configure(text='Ciudad', width=7)
    self.lblCiudad.place(anchor="nw", x=580, y=40)

    #Captura ciudad del Proveedor
    self.ciudad = ttk.Entry(self.frm1)
    self.ciudad.configure(width=20)
    self.ciudad.place(anchor="nw", x=630, y=40)
    self.ciudad.bind("<KeyRelease>", lambda event, widget = self.ciudad, largo = 50 : self.validaVarChar(event, widget, largo))
    #Separador
    self.separador1 = ttk.Separator(self.frm1)
    self.separador1.configure(orient="horizontal")
    self.separador1.place(anchor="nw", width=800, x=0, y=79)

    #Etiqueta Código del Producto
    self.lblCodigo = ttk.Label(self.frm1)
    self.lblCodigo.configure(text='Código', width=7)
    self.lblCodigo.place(anchor="nw", x=10, y=120)

    #Captura el código del Producto
    self.codigo = ttk.Entry(self.frm1)
    self.codigo.place(anchor="nw", x=60, y=120)
    self.codigo.bind("<KeyRelease>", lambda event, widget = self.codigo, largo = 15 : self.validaVarChar(event, widget, largo), add="+")
    self.codigo.bind("<KeyRelease>", self.updateProduct, add="+")

    #Etiqueta descripción del Producto
    self.lblDescripcion = ttk.Label(self.frm1)
    self.lblDescripcion.configure(text='Descripción', width=11)
    self.lblDescripcion.place(anchor="nw", x=220, y=120)

    #Captura la descripción del Producto
    self.descripcion = ttk.Entry(self.frm1)
    self.descripcion.configure(width=36)
    self.descripcion.place(anchor="nw", x=290, y=120) # 100
    self.descripcion.bind("<KeyRelease>", lambda event, widget = self.descripcion, largo = 100 : self.validaVarChar(event, widget, largo))

    #Etiqueta unidad o medida del Producto
    self.lblUnd = ttk.Label(self.frm1)
    self.lblUnd.configure(text='Unidad', width=7)
    self.lblUnd.place(anchor="nw", x=580, y=120)

    #Captura la unidad o medida del Producto
    self.unidad = ttk.Entry(self.frm1)
    self.unidad.configure(width=10)
    self.unidad.place(anchor="nw", x=630, y=120)
    self.unidad.bind("<KeyRelease>", lambda event, widget = self.unidad, largo = 10 : self.validaVarChar(event, widget, largo))
    self.unidad.delete(0, 'end')

    #Etiqueta cantidad del Producto
    self.lblCantidad = ttk.Label(self.frm1)
    self.lblCantidad.configure(text='Cantidad', width=8)
    self.lblCantidad.place(anchor="nw", x=10, y=170)

    #Captura la cantidad del Producto
    self.cantidad = ttk.Entry(self.frm1)
    self.cantidad.configure(width=12)
    self.cantidad.place(anchor="nw", x=70, y=170)

    #Etiqueta precio del Producto
    self.lblPrecio = ttk.Label(self.frm1)
    self.lblPrecio.configure(text='Precio $', width=8)
    self.lblPrecio.place(anchor="nw", x=170, y=170)

    #Captura el precio del Producto
    self.precio = ttk.Entry(self.frm1)
    self.precio.configure(width=15)
    self.precio.place(anchor="nw", x=220, y=170)

    #Etiqueta fecha de compra del Producto
    self.lblFecha = ttk.Label(self.frm1)
    self.lblFecha.configure(text='Fecha', width=6)
    self.lblFecha.place(anchor="nw", x=340, y=170)

    #Captura la fecha de compra del Producto
    self.fecha = ttk.Entry(self.frm1)
    self.fecha.configure(width=11)
    self.fecha.place(anchor="nw", x=380, y=170)

    #Estilo para configurar el tamaño del boton "Auto"
    TextoPequenno = ttk.Style()
    TextoPequenno.configure("TextoPequenno.TButton", font=("Arial", 7)) 

    #Boton para poner fecha automaticamente
    self.btnAuto = ttk.Button(self.frm1)
    self.btnAuto.configure(text='Auto', command= self.Auto, style="TextoPequenno.TButton")
    self.btnAuto.place(anchor="nw", height=22,width=37, x=470, y=170)

    #Separador
    self.separador2 = ttk.Separator(self.frm1)
    self.separador2.configure(orient="horizontal")
    self.separador2.place(anchor="nw", width=800, x=0, y=220)

    #tablaTreeView
    self.style=ttk.Style()
    self.style.configure("estilo.Treeview", highlightthickness=0, bd=0, background="#e0e0e0", font=('Calibri Light',10))
    self.style.configure("estilo.Treeview.Heading", background='Azure', font=('Calibri Light', 10,'bold')) 
    self.style.layout("estilo.Treeview", [('estilo.Treeview.treearea', {'sticky': 'nswe'})])
    
    #Árbol para mosrtar los datos de la B.D.
    self.treeProductos = ttk.Treeview(self.frm1, style="estilo.Treeview")
    self.treeProductos.bind("<ButtonRelease-1>", self.selectTreeRow)
    self.treeProductos.configure(selectmode="extended")

    # Etiquetas de las columnas para el TreeView
    self.treeProductos["columns"]=("Codigo","Descripcion","Und","Cantidad","Precio","Fecha")
    # Características de las columnas del árbol
    self.treeProductos.column ("#0",          anchor="w",stretch=True,width=3)
    self.treeProductos.column ("Codigo",      anchor="w",stretch=True,width=3)
    self.treeProductos.column ("Descripcion", anchor="w",stretch=True,width=150)
    self.treeProductos.column ("Und",         anchor="w",stretch=True,width=3)
    self.treeProductos.column ("Cantidad",    anchor="w",stretch=True,width=3)
    self.treeProductos.column ("Precio",      anchor="w",stretch=True,width=8)
    self.treeProductos.column ("Fecha",       anchor="w",stretch=True,width=3)

    # Etiquetas de columnas con los nombres que se mostrarán por cada columna
    self.treeProductos.heading("#0",          anchor="center", text='ID / Nit')
    self.treeProductos.heading("Codigo",      anchor="center", text='Código')
    self.treeProductos.heading("Descripcion", anchor="center", text='Descripción')
    self.treeProductos.heading("Und",         anchor="center", text='Unidad')
    self.treeProductos.heading("Cantidad",    anchor="center", text='Cantidad')
    self.treeProductos.heading("Precio",      anchor="center", text='Precio')
    self.treeProductos.heading("Fecha",       anchor="center", text='Fecha')

    #Carga los datos en treeProductos
    self.lee_treeProductos() 
    self.treeProductos.place(anchor="nw", height=300, width=790, x=2, y=230)

    #Scrollbar en el eje Y de treeProductos
    self.scrollbary=ttk.Scrollbar(self.treeProductos, orient='vertical', command=self.treeProductos.yview)
    self.treeProductos.configure(yscroll=self.scrollbary.set)
    self.scrollbary.place(x=772, y=25, height=275)

    # Título de la pestaña Ingreso de Datos
    self.frm1.pack(side="top")
    self.tabs.add(self.frm1, compound="center", text='Ingreso de datos')
    self.tabs.pack(side="top")

    #Frame 2 para contener los botones
    self.frm2 = ttk.Frame(self.win)
    self.frm2.configure(height=100, width=800)

    #Botón para Buscar un Proveedor
    self.btnBuscar = ttk.Button(self.frm2)
    self.btnBuscar.configure(text='Buscar', command = self.buscar)
    self.btnBuscar.place(anchor="nw", width=70, x=200, y=10)

    #Botón para Guardar los datos
    self.btnGrabar = ttk.Button(self.frm2)
    self.btnGrabar.configure(text='Grabar', command = self.grabar)
    self.btnGrabar.place(anchor="nw", width=70, x=275, y=10)

    #Botón para Editar los datos
    self.btnEditar = ttk.Button(self.frm2)
    self.btnEditar.configure(text='Editar', command = self.editar)
    self.btnEditar.place(anchor="nw", width=70, x=350, y=10)

    #Botón para Elimnar datos
    self.btnEliminar = ttk.Button(self.frm2)
    self.btnEliminar.configure(text='Eliminar', command = self.eliminar)
    self.btnEliminar.place(anchor="nw", width=70, x=425, y=10)

    #Botón para cancelar una operación
    self.btnCancelar = ttk.Button(self.frm2)
    self.btnCancelar.configure(text='Cancelar', width=80,command = self.limpiaCampos)
    self.btnCancelar.place(anchor="nw", width=70, x=500, y=10)

    #Ubicación del Frame 2
    self.frm2.place(anchor="nw", height=40, relwidth=1, y=565)
    self.win.pack(anchor="center", side="top")

    # widget Principal del sistema
    self.mainwindow = self.win
    
  #Fución de manejo de eventos del sistema
  def run(self):
      self.mainwindow.mainloop()
  
  ''' ......... Métodos utilitarios del sistema .............'''
  #Rutina de centrado de pantalla
  def centra(self,win,ancho,alto): 
      """ centra las ventanas en la pantalla """ 
      x = win.winfo_screenwidth()//2 - ancho//2 
      y = win.winfo_screenheight()//2 - alto//2 
      win.geometry(f'{ancho}x{alto}+{x}+{y}') 
      win.deiconify() # Se usa para restaurar la ventana

 # Validaciones del sistema
  def validaVarChar(self, event, widget, largo):
    if event.char and len(widget.get()) > largo:
      mssg.showwarning('Error.',  f'La longitud máxima de la cadena es de {largo} caracteres.')
      widget.delete(largo, "end")
  
# Función para validar fecha
  def vFecha(self, fecha):
    ''' Valida si la fecha ingresada es correcta de acuerdo al calendario gregoriano.
    Retorna True si esta es válida o False en cualquier otro caso. '''
    diasMes = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}  #Dias por mes
    cSlashes = 0    #Cantidad de slashes en la entrada
    f = ""
    for l in fecha:
      if l == "-":
        f = f + "/"
      else: f = f + l
    for l in f:
        if l == "/": cSlashes += 1  #Conteo de slashes en la entrada
    if cSlashes != 2:
      return False
    else:   
        dia, mes, ano = (x for x in f.split("/")) #Asignación de cada dato de la entrada a una variable diferente
        try:    #Validación de datos correctos
            dia = int(dia)
            mes = int(mes)
        except:
            return False
        try:
            ano = int(ano)  #valida si el año se puede convertir directamente a entero
            if ano <= 1900 or ano > 3000: 
                return False     
        except: #Se ejecuta si el año ingresado no se puede convertir directamente
            return False
        if mes > 12 or mes < 1 or dia < 1 or mes != 2 and diasMes[mes] < dia:   #Valida si los números ingresados en la fecha son válidos excepto para febrero
            return False
        if mes == 2:    #Valida si el mes es febrero
            if ano > 0 and ano%4 == 0 or ano < 0 and (ano + 1)%4 == 0:  #Valida si el año es bisiesto
                if dia > 29:
                    return False
                if ano%100 == 0 and ano%400 != 0:   #Valida si es año bisiesto no válido en el calendario gregoriano
                    if dia > diasMes[mes]: return False
            else:
                if dia > diasMes[mes]:  #Valida si el mes no es febrero
                    return False
        return True
  #Función que actualiza los campos relativos al proveedor
  # en caso de digitar un NIT existente en su respectivo campo.
  def updateProvider(self, event):
    '''Función que actualiza los campos relativos al proveedor
    en caso de digitar un NIT existente en su respectivo campo.'''
    try:
      r = self.run_Query("Select * from Proveedor where IdNitProv = ?;", (self.idNit.get(),))
    except Exception as e:
      mssg.showerror("Error en la base de datos.", f"Error {type(e)}: {e}")
    r = r.fetchone()
    if r != None:
      self.razonSocial.delete(0,"end")
      self.razonSocial.insert(0,r[1])
      self.ciudad.delete(0,"end")
      self.ciudad.insert(0,r[2])

  #Función que actualiza los campos relativos al producto y a su proveedor
  # en caso de digitar un código de producto existente en su respectivo campo.
  def updateProduct(self, event):
    '''Función que actualiza los campos relativos al producto y a su proveedor
    en caso de digitar un código de producto existente en su respectivo campo.'''
    r = self.run_Query("Select * from Inventario where Codigo = ?;", (self.codigo.get(),))
    r = r.fetchone()
    if r != None:
      self.idNit.delete(0,"end")
      self.idNit.insert(0,r[0])
      self.updateProvider("")
      self.descripcion.delete(0,"end")
      self.descripcion.insert(0,r[2])
      self.unidad.delete(0,"end")
      self.unidad.insert(0,r[3])
      self.cantidad.delete(0,"end")
      self.cantidad.insert(0,int(r[4]))
      self.precio.delete(0,"end")
      self.precio.insert(0,r[5])
      self.fecha.delete(0,"end")
      self.fecha.insert(0,r[6])

  #Rutina de limpieza de datos
  def limpiaCamposProductos(self):
    self.codigo.delete(0,'end')
    self.descripcion.delete(0,'end')
    self.unidad.delete(0,'end')
    self.cantidad.delete(0,'end')
    self.precio.delete(0,'end')
    self.fecha.delete(0,'end')

  def limpiaCampos(self):
      ''' Limpia todos los campos de captura'''
      if self.actualiza or self.elimina: self.cancelar()
      self.idNit.delete(0,'end')
      self.razonSocial.delete(0,'end')
      self.ciudad.delete(0,'end')
      self.limpiaCamposProductos()

  #Funcion para colocar fecha automaticamente
  def Auto(self):
    if self.Auto:
      self.Auto = True
      self.fecha.delete(0, 'end')
      self.fecha.insert(-1, str(datetime.today().strftime('%d/%m/%Y')))

  #Función para buscar los productos de un proveedor
  def buscar(self, event = None):
    '''Función para buscar los productos de un proveedor'''
    idN = self.idNit.get()
    if idN == "":
      mssg.showinfo("Nit de proveedor.", "Ingrese un NIT de proveedor para buscar sus productos.")
    else:
      try:
        r = self.run_Query("SELECT * from Proveedor INNER JOIN Inventario WHERE idNitProv = ? and idNitProv = idNit;",(idN,))
      except Exception as e:
        mssg.showerror("Error en la base de datos.", f"Error {type(e)}: {e}")
      tabla_TreeView = self.treeProductos.get_children()
      for linea in tabla_TreeView:
          self.treeProductos.delete(linea) # Límpia la filas del TreeView        
      # Insertando los datos de la BD en treeProductos de la pantalla
      row = None
      for row in r:
        self.treeProductos.insert('',0, text = row[0], values = [row[4],row[5],row[6],(row[7]),row[8],row[9]])

  #Función para gurdar o modificar datos en la base de datos.
  def grabar(self):
    '''Función para gurdar o modificar datos en la base de datos.'''
    if self.actualiza:
      self.actualiza = False      
      self.idNit.config(state = "enabled")
      self.razonSocial.config(state = "enabled")
      self.ciudad.config(state = "enabled")
      self.codigo.config(state = "enabled")
      self.btnBuscar.config(state = "enabled")
      self.btnEditar.config(state = "enabled")
      self.btnEliminar.config(state = "enabled")
    errorMessage = ""
    idN = self.idNit.get()
    rs = self.razonSocial.get()
    c = self.ciudad.get()
    cod = self.codigo.get()
    des = self.descripcion.get()
    u = self.unidad.get()
    can = self.cantidad.get()
    if can != "":
      try:        
        if int(can) < 1: errorMessage = errorMessage + "La cantidad ingresada no es correcta.\n"
      except:
        errorMessage = errorMessage + "La cantidad ingresada no es correcta.\n"
    pre = self.precio.get()
    if pre != "":
      try:
        if float(pre) <= 0: errorMessage = errorMessage + "El precio ingresado no es correcto.\n"
      except:
        errorMessage = errorMessage + "El precio ingresado no es correcto.\n"
    fe = self.fecha.get()
    if fe != "":
      if not(self.vFecha(fe)):
        errorMessage = errorMessage + "La fecha ingresada no es correcta.\n"
    if len(errorMessage) > 0:
      mssg.showwarning("Error en los datos de entrada.",errorMessage)
      return
    #Validación cuando se introduce únicamente un proveedor pero no un producto.
    try:
      if idN != "" and cod == "":
        r = self.run_Query("select * from Proveedor where idNitProv = ?;", (idN,))
        if r.fetchone() == None:
          r = self.run_Query("insert into Proveedor(idNitProv, Razon_Social, Ciudad) values(?,?,?);",(idN, rs, c))
          if r.rowcount > 0:
            mssg.showinfo(None,"Proveedor agregado exitosamente.")
          else:
            mssg.showerror("Error en la operación de adición de registro.")
        else:
          r = mssg.askokcancel("Confirmar modificación","Desea modificar el proveedor " + idN + "?")
          if r:
            r = self.run_Query("update Proveedor set (Razon_Social, Ciudad) = (?,?) where idNitProv = ?;", (rs, c ,idN))
            if r.rowcount > 0:
              mssg.showinfo(None,"Proveedor modificado exitosamente.")
            else:
              mssg.showerror("Error en la operación de modificación de registro.")
      #Validación cuando se introduce un producto.
      if cod != "":
        r = self.run_Query("select * from Inventario where Codigo = ?;",(cod,))
        if r.fetchone() == None:        
          if idN != "":
            #Validación cuando se introduce un producto y un proveedor nuevos
            r = self.run_Query("select * from Proveedor where idNitProv = ?;",(idN,))
            if r.fetchone() == None:
              r = self.run_Query("insert into Proveedor(idNitProv, Razon_Social, Ciudad) values(?,?,?);",(idN, rs, c))
              if r.rowcount > 0:
                r = self.run_Query("insert into Inventario(idNit, Codigo, Descripcion, Und, Cantidad, Precio, Fecha) "
                                  + "values(?,?,?,?,?,?,?);",(idN, cod, des, u, can, pre ,fe))
                if r.rowcount > 0:
                  mssg.showinfo(None,"Proveedor y producto agregados exitosamente.")
                else:
                  mssg.showerror("Error en la operación de adición de registros.")
              else:
                mssg.showerror("Error en la operación de adición de registro.")
            else:
              #Validación cuando el proveedor ya existe
              r = self.run_Query("insert into Inventario(idNit, Codigo, Descripcion, Und, Cantidad, Precio, Fecha) "
                                  + "values(?,?,?,?,?,?,?);", (idN, cod, des, u, can, pre, fe))
              if r.rowcount > 0:
                mssg.showinfo(None,"Producto agregado exitosamente a este proveedor.")
              else:
                mssg.showerror("Error en la operación de adición de registro.")
          else:
            #Validación en caso de que no haya ingresado NIT de proveedor
            mssg.showwarning("Operación inconsistente.","No se puede tener un producto que no esté referenciado a un proveedor.")
        #Validación si el producto ya existe
        else:
          #Validación si ingresó un Nit de proveedor
          if idN != "":
            r = self.run_Query("select * from Proveedor where idNitProv = ?;",(idN,))
            mprov = False
            row = r.fetchone()
            if row != None:
              if rs != row[1] or c != row[2]:
                mprov = True
              r = self.run_Query("select * from Inventario where Codigo = ?;", (cod,))
              row = r.fetchone()
              mprod = False
              if idN != row[0] or des != row[2] or u != row[3] or float(can) != row[4] or float(pre) != row[5] or fe != row[6]:
                mprod = True
              cprov = False
              if idN != row[0]: cprov = True
              #Validación si existe un producto idéntico
              if (not mprod )and (not mprov):
                mssg.showerror(None, "Ya existe un producto idéntico a este")
              #Validación si hay que modificar proveedor y producto
              if (mprod and mprov):
                if cprov:
                  msg = "¿Desea asociar este producto a este proveedor y simultáneamente modificar los datos de estos dos?"
                else:
                  msg = "¿Desea modificar los datos del producto y del proveedor simultaneamente?"
                if mssg.askokcancel("Confirmar modificación.", msg):
                  r = self.run_Query("update Inventario set(IdNit, Descripcion, Und, Cantidad, Precio, Fecha) = "
                                      + "(?,?,?,?,?,?) where Codigo = ?;", (idN, des, u, can, pre, fe, cod))
                  if r.rowcount > 0:
                    r = self.run_Query("update Proveedor set(Razon_Social, Ciudad) = (?,?) where idNitProv = ?;", (rs, c, idN))
                    if r.rowcount > 0:
                      mssg.showinfo(None,"Información modificada exitosamente.")
                    else:
                      mssg.showerror("Error en la operación de modificación de registro.")
                  else:
                    mssg.showerror("Error en la operación de modificación de registro.") 
              #Validación de si solamente hay que modificar producto:
              elif mprod:
                if mssg.askokcancel("Confirmar modificación.","¿Desea modificar este producto?"):
                  r = self.run_Query("update Inventario set(IdNit, Descripcion, Und, Cantidad, Precio, Fecha) = "
                                      + "(?,?,?,?,?,?) where Codigo = ?;", (idN, des, u, can, pre, fe, cod))
                  if r.rowcount > 0:
                    mssg.showinfo(None,"Producto modificado exitosamente.")
              #Validación se si solamente hay que modificar proveedor
              elif mprov:
                if mssg.askokcancel("Confirmar modificación.","¿Desea modificar este Proveedor?"):
                  r = self.run_Query("update Proveedor set(Razon_Social, Ciudad) = (?,?) where idNitProv = ?;", (rs, c, idN))
                  if r.rowcount > 0:
                    mssg.showinfo(None,"Información modificada exitosamente.")
            else:
              mssg.showwarning("Repita")
          else:
            #Validación en caso de que no haya ingresado NIT de proveedor
            mssg.showwarning("Operación inconsistente.","No se puede tener un producto que no esté referenciado a un proveedor.")
    except Exception as e:
      mssg.showerror("Error en la base de datos.", f"Error {type(e)}: {e}")
    self.buscar()
  
  #Función para habilitar el modo de edición de registros.
  def editar(self):
    '''Función para habilitar el modo de edición de registros.'''
    self.actualiza = True
    mssg.showinfo("Edición de datos.", "Seleccione el registro cuyos datos desea editar. Para cancelar haga click en el botón cancelar.")
    self.idNit.config(state = "disabled")
    self.razonSocial.config(state = "disabled")
    self.ciudad.config(state = "disabled")
    self.codigo.config(state = "disabled")
    self.descripcion.config(state = "disabled")
    self.unidad.config(state = "disabled")
    self.cantidad.config(state = "disabled")
    self.precio.config(state = "disabled")
    self.fecha.config(state = "disabled")
    self.btnBuscar.config(state = "disabled")
    self.btnGrabar.config(state = "disabled")
    self.btnEditar.config(state = "disabled")
    self.btnEliminar.config(state = "disabled")
  
  #Función que carga datos del registro seleccionado del TreeRow para ser modificados en caso de modo de edición
  # o que borra los datos del registro del TreeRow seleccionado de la base de datos en caso de modo de eliminación.
  def selectTreeRow(self,x):
    '''Función que carga datos del registro seleccionado del TreeRow para ser modificados en caso de modo de edición
        o que borra los datos del registro del TreeRow seleccionado de la base de datos en caso de modo de eliminación.'''
    if self.actualiza:
      row = self.treeProductos.focus()
      if row == '':
        return 
      data = self.treeProductos.item(row, "values")
      data0 = self.treeProductos.item(row, "text")
      self.actualiza = False
      self.idNit.config(state = "enabled")
      self.codigo.config(state = "enabled")
      self.descripcion.config(state = "enabled")
      self.unidad.config(state = "enabled")
      self.cantidad.config(state = "enabled")
      self.precio.config(state = "enabled")
      self.fecha.config(state = "enabled")
      self.btnGrabar.config(state = "enabled")
      self.limpiaCampos()
      self.actualiza = True
      self.idNit.insert(0,data0)
      self.idNit.config(state = "disabled")
      self.codigo.insert(0,data[0])
      self.codigo.config(state = "disabled")
      self.descripcion.insert(0,data[1])
      self.unidad.insert(0,data[2])
      self.cantidad.insert(0,data[3])
      self.precio.insert(0,data[4])
      self.fecha.insert(0,data[5])
    if self.elimina:
      row = self.treeProductos.focus()
      if row == '':
        return
      self.elimina = False
      self.idNit.config(state = "enabled")
      self.razonSocial.config(state = "enabled")
      self.ciudad.config(state = "enabled")
      self.codigo.config(state = "enabled")
      self.descripcion.config(state = "enabled")
      self.unidad.config(state = "enabled")
      self.cantidad.config(state = "enabled")
      self.precio.config(state = "enabled")
      self.fecha.config(state = "enabled")
      self.btnBuscar.config(state = "enabled")
      self.btnGrabar.config(state = "enabled")
      self.btnEditar.config(state = "enabled")
      self.btnEliminar.config(state = "enabled")
      data0 = self.treeProductos.item(row, "text")
      data = self.treeProductos.item(row, "values")
      try:
        if mssg.askyesno("Confirmar eliminación.", "¿Desea eliminar este producto de la base de datos?"):
          r = self.run_Query("delete from Inventario where codigo = ?;", (data[0],))
          if r.rowcount > 0:
            if mssg.askyesno("Confirmar eliminacion.", "¿Desea eliminar también este proveedor y todos sus productos?"):
              self.run_Query("delete from Inventario where IdNit = ?;", (data0,))
              r = self.run_Query("delete from Proveedor where IdNitProv = ?;", (data0,))
              if r.rowcount > 0:
                mssg.showinfo("Eliminación exitosa.", "Este proveedor y todos sus productos fueron borrados exitosamente.")
                self.actualizarProveedores()
                self.lee_treeProductos()
            else:
              self.buscar()
        else:
          if mssg.askyesno("Confirmar eliminacion.", "¿Desea eliminar este proveedor y todos sus productos?"):
            self.run_Query("delete from Inventario where IdNit = ?;", (data0,))
            r = self.run_Query("delete from Proveedor where IdNitProv = ?;", (data0,))
            if r.rowcount > 0:
              mssg.showinfo("Eliminación exitosa.", "Este proveedor y todos sus productos fueron borrados exitosamente.")
              self.actualizarProveedores()
              self.lee_treeProductos()
      except Exception as e:
        mssg.showerror("Error en la base de datos.", f"Error {type(e)}: {e}")
      

  #función para cancelar edición o eliminación de datos.
  def cancelar(self):  
    '''función para cancelar edición o eliminación de datos.'''  
    self.idNit.config(state = "enabled")
    self.razonSocial.config(state = "enabled")
    self.ciudad.config(state = "enabled")
    self.codigo.config(state = "enabled")
    self.descripcion.config(state = "enabled")
    self.unidad.config(state = "enabled")
    self.cantidad.config(state = "enabled")
    self.precio.config(state = "enabled")
    self.fecha.config(state = "enabled")
    self.btnBuscar.config(state = "enabled")
    self.btnGrabar.config(state = "enabled")
    self.btnEditar.config(state = "enabled")
    self.btnEliminar.config(state = "enabled")
    self.btnAuto.config(state = "enabled")
    if self.actualiza:
      self.actualiza = False
      mssg.showinfo("Edición de datos.", "Edición de datos cancelada.")
    if self.elimina:
      self.elimina = False
      mssg.showinfo("Eliminación de datos.", "Eliminación de datos cancelada.")

  #Función que habilita el modo de eliminación.
  def eliminar(self):
    '''Función que habilita el modo de eliminación.'''
    self.elimina = True
    mssg.showinfo("Eliminación de datos.", "Seleccione el registro cuyos datos desea eliminar. Para cancelar haga click en el botón cancelar.")
    self.idNit.config(state = "disabled")
    self.razonSocial.config(state = "disabled")
    self.ciudad.config(state = "disabled")
    self.codigo.config(state = "disabled")
    self.descripcion.config(state = "disabled")
    self.unidad.config(state = "disabled")
    self.cantidad.config(state = "disabled")
    self.precio.config(state = "disabled")
    self.fecha.config(state = "disabled")
    self.btnBuscar.config(state = "disabled")
    self.btnGrabar.config(state = "disabled")
    self.btnEditar.config(state = "disabled")
    self.btnEliminar.config(state = "disabled")
    self.btnAuto.config(state = "disabled")

  #Rutina para cargar los datos en el árbol  
  def carga_Datos(self):
    self.idNit.insert(0,self.treeProductos.item(self.treeProductos.selection())['text'])
    self.idNit.configure(state = 'readonly')
    self.razonSocial.insert(0,self.treeProductos.item(self.treeProductos.selection())['values'][0])
    self.unidad.insert(0,self.treeProductos.item(self.treeProductos.selection())['values'][3])

  #Rutina para actualizar la lista de los proveedores
  def actualizarProveedores(self):
    db_rows = self.run_Query("Select IdNitProv from Proveedor")
    self.proveedores.clear()
    for row in db_rows:
      self.proveedores.append(row[0])


  # Operaciones con la base de datos
  def run_Query(self, query, parametros = ()):
    ''' Función para ejecutar los Querys a la base de datos '''
    with sqlite3.connect(self.db_name) as conn:
        cursor = conn.cursor()
        result = cursor.execute(query, parametros)
        conn.commit()
    return result

  #función que carga todos los productos de la base de datos en el TreeRow
  def lee_treeProductos(self):
    ''' Carga los datos y Limpia la Tabla tablaTreeView '''
    tabla_TreeView = self.treeProductos.get_children()
    for linea in tabla_TreeView:
        self.treeProductos.delete(linea) # Límpia la filas del TreeView
    
    # Seleccionando los datos de la BD
    query = '''SELECT * from Proveedor INNER JOIN Inventario WHERE idNitProv = idNit ORDER BY idNitProv'''
    try:
      db_rows = self.run_Query(query) # db_rows contine la vista del query
    except Exception as e:
      mssg.showerror("Error en la base de datos.", f"Error {type(e)}: {e}")
      
    # Insertando los datos de la BD en treeProductos de la pantalla
    row = None
    for row in db_rows:
      self.treeProductos.insert('',0, text = row[0], values = [row[4],row[5],row[6],(row[7]),row[8],row[9]])

    ''' Al final del for row queda con la última tupla
        y se usan para cargar las variables de captura
    
    if row != None:
      self.idNit.delete(0,"end")
      self.idNit.insert(0,row[0])
      self.razonSocial.delete(0,"end")
      self.razonSocial.insert(0,row[1])
      self.ciudad.delete(0,"end")
      self.ciudad.insert(0,row[2])
      self.codigo.delete(0,"end")
      self.codigo.insert(0,row[4])
      self.descripcion.delete(0,"end")
      self.descripcion.insert(0,row[5])
      self.unidad.delete(0,"end")
      self.unidad.insert(0,row[6])
      self.cantidad.delete(0,"end")
      self.cantidad.insert(0,int(row[7]))
      self.precio.delete(0,"end")
      self.precio.insert(0,row[8])
      self.fecha.delete(0,"end")
      self.fecha.insert(0,row[9])  
      '''

if __name__ == "__main__":
    app = Inventario()
    app.run()
