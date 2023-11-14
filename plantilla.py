# !/usr/bin/python3
# -*- coding: utf-8 -*-
import os.path as path
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox as mssg
import sqlite3
import platform #para determinar el OS
from datetime import datetime
import re
if platform.system() == 'Linux':
  from PIL import Image, ImageTk

class Inventario:
  def __init__(self, master=None):
    self.path = path.dirname(path.abspath(__file__))
    #self.path = r'X:/Users/ferna/Documents/UNal/Alumnos/2023_S2/ProyInventario'
    self.db_name = self.path + r'/Inventario.db'

    ''' Dimensiones de la pantalla'''
    ancho=830
    alto=630
    
    self.actualizaProveedor = False
    self.actualizaProducto = False
    self.elimina = False

    ''' Crea ventana principal '''
    self.win = tk.Tk() 
    self.win.geometry(f"{ancho}x{alto}")
    '''Detecta cual es el OS y retorna los codigos necesarios para
    abrir los iconos en Linux y Windows '''
    if platform.system() == "Windows":
      self.win.iconbitmap(self.path + r'/f2.ico')
    elif platform.system() == "Linux":
      ima = Image.open('nino-modified.png') # Esta foto esta para mostrarse solamente en sistemas linux
      pho = ImageTk.PhotoImage(ima)
      self.win.wm_iconphoto(True, pho)
      
    self.win.resizable(False, False)
    self.win.title("Manejo de Proveedores") 

    '''Se encarga de llamar la funcion de confirmacion cuando se intente cerrar la ventana'''
    self.win.protocol("WM_DELETE_WINDOW", self.cierre)  

    #Centra la pantalla
    self.centra(self.win,ancho,alto)
    
    # Contenedor de widgets   
    self.win = tk.LabelFrame(master)
    self.win.configure(background="#e0e0e0",font="{Arial} 12 {bold}", height=ancho,labelanchor="n",width=alto)
    self.tabs = ttk.Notebook(self.win)
    self.tabs.configure(height=590, width=799)

    #Frame de datos
    self.frm1 = ttk.Frame(self.tabs)
    self.frm1.configure(height=200, width=200)

    #Etiqueta IdNit del Proveedor
    self.lblIdNit = ttk.Label(self.frm1)
    self.lblIdNit.configure(text='Id/Nit', width=6)
    self.lblIdNit.place(anchor="nw", x=10, y=40)
    
    #Captura IdNit del Proveedor y sugiere proveedores existentes
    self.idNit = ttk.Combobox(self.frm1, postcommand = self.actualizarProveedores)
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
    self.cantidad.bind("<KeyRelease>", lambda event, widget = self.cantidad, largo = 10 : self.validaVarCharNum(event, widget, largo))

    #Etiqueta precio del Producto
    self.lblPrecio = ttk.Label(self.frm1)
    self.lblPrecio.configure(text='Precio $', width=8)
    self.lblPrecio.place(anchor="nw", x=170, y=170)

    #Captura el precio del Producto
    self.precio = ttk.Entry(self.frm1)
    self.precio.configure(width=15)
    self.precio.place(anchor="nw", x=220, y=170)
    self.precio.bind("<KeyRelease>", lambda event, widget = self.precio, largo = 15 : self.validaVarCharNumPre(event, widget, largo))

    #Etiqueta fecha de compra del Producto
    self.lblFecha = ttk.Label(self.frm1)
    self.lblFecha.configure(text='Fecha', width=6)
    self.lblFecha.place(anchor="nw", x=340, y=170)

    #Captura la fecha de compra del Producto
    self.fecha = ttk.Entry(self.frm1, foreground="gray")
    self.fecha.configure(width=11)
    self.fecha.place(anchor="nw", x=380, y=170)
    self.fecha.insert(0, "dd/mm/aaaa")
    self.fecha.bind("<KeyRelease>", lambda event, widget = self.fecha, largo = 10 : self.validaVarCharFe(event, widget, largo))
    self.fecha.bind("<FocusIn>", self.entradaDatos)
    self.fecha.bind("<FocusOut>", self.salidaDatos)

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
    ''' centra las ventanas en la pantalla '''
    x = win.winfo_screenwidth()//2 - ancho//2 
    y = win.winfo_screenheight()//2 - alto//2 
    win.geometry(f'{ancho}x{alto}+{x}+{y}') 
    win.deiconify() # Se usa para restaurar la ventana

 # Validaciones de longitud del los campos
  def validaVarChar(self, event, widget, largo):
    if len(widget.get()) > largo:
      mssg.showwarning('Error.',  f'La longitud máxima de la cadena es de {largo} caracteres.')
      widget.delete(largo, 'end')

  def validaVarCharNum(self, event, widget, largo):    
    if event.keysym not in ["BackSpace","Up","Down","Left","Right","0","1","2","3","4","5","6","7","8","9"]:
      text = widget.get()
      p = re.compile(r"([^\d])")
      widget.delete(0, "end")
      widget.insert(0,p.sub("",text))
    if len(widget.get()) > largo: 
      mssg.showwarning('Error.',  f'La longitud máxima de la cadena es de {largo} caracteres.')
      widget.delete(largo, 'end')      

  def validaVarCharNumPre(self, event, widget, largo):    
    if event.keysym not in ["BackSpace","Up","Down","Left","Right","0","1","2","3","4","5","6","7","8","9"]:
      text = widget.get()
      p = re.compile(r"([^\d])")
      p2  = re.compile(r"([^\d\.])")
      widget.delete(0, "end")
      if len(text.split(r".")) > 2:
        widget.insert(0,p.sub("",text))
      else:
        widget.insert(0,p2.sub("",text))
    if len(widget.get()) > largo: 
      mssg.showwarning('Error.',  f'La longitud máxima de la cadena es de {largo} caracteres.')
      widget.delete(largo, 'end')

  def validaVarCharFe(self, event, widget, largo):   
    p = re.compile(r"([^\d/])")
    oLen = len(widget.get())
    text = p.sub("", widget.get())
    uEntry = False
    if oLen != len(text): uEntry = True
    p2 = re.compile(r"(/)")     
    addSlash = False
    if event.keysym != "BackSpace":
      if len(text) == 1 and len(re.findall(p2,text)) == 0:
        if int(text) > 3: addSlash = True
      if len(text) == 2 and len(re.findall(p2,text)) == 0:
        addSlash = True
      elif len(text) == 3:
        addSlash = True
        terms = text.split("/")
        if len(terms) == 2:
          for term in terms:
            if term < "0" or term > "9":
              addSlash = False
          if addSlash == True:
            if int(terms[1]) < 2:
              addSlash = False
        else:
          addSlash = False
      elif len(text) == 4:
        addSlash = True
        terms = text.split("/")
        if len(terms) == 2:
          if len(terms[0]) > 2:
            addSlash = False
          if len(terms[1]) > 2:
            addSlash = False
          elif len(terms[1]) == 1:
            if int(terms[1]) < 2: addSlash = False 
        else:
          addSlash = False   
      elif len(text) == 5:        
        addSlash = True
        terms = text.split("/")
        if len(terms) == 2:
          if len(terms[0]) != 2:
            addSlash = False
          if len(terms[1]) != 2:
            addSlash = False
        else:
          addSlash = False    
    if addSlash == True:
      text = text + "/"
    if addSlash == True or uEntry == True:
      widget.delete(0, "end")
      widget.insert(0, text)
    terms = text.split("/")
    if len(terms) == 3:
      if len(terms[2]) > 4:
        widget.delete(len(text) - (len(terms[2]) - 4), "end")
    if len(widget.get()) > largo: #Antes habia un "event.char and" antes del len(widget.get), aparentemente "event.char" siempre tomaba el valor de False, seguramente borre algo impotante pero funciona
      mssg.showwarning('Error.',  f'La longitud máxima de la cadena es de {largo} caracteres.')
      widget.delete(largo, 'end')

  def validacionIngresoRegistro(self):
    '''Validador de un registro de producto'''
    idN = self.idNit.get()
    can = self.cantidad.get()
    cod = self.codigo.get()
    errorMessage = ''
    if cod == '':
      errorMessage += 'Para ingresar un producto, ingrese su codigo\n'
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
    if fe != "":  # Tenia and idN == "" pero es inecesario si no se llama la funcion al ingresar proveedor
      if not self.vFecha(fe):
        errorMessage = errorMessage + "La fecha ingresada no es correcta.\n"
    if len(errorMessage) > 0:
      mssg.showwarning("Error en los datos de entrada.",errorMessage)
      return False
    return True
  
# Función para validar fecha
  def vFecha(self, fecha):
    ''' Valida si la fecha ingresada es correcta de acuerdo al calendario gregoriano, 
    ademas revisa con que no sea una fecha futura.
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
      #Los siguientes if's revisan que la fecha no sea del futuro
      if ano > int(datetime.today().strftime('%Y')):
        return False
      elif mes > int(datetime.today().strftime('%m')):
        return False
      elif dia > int(datetime.today().strftime('%d')):
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
  def updateProvider(self, event = None):
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
  def updateProduct(self, event = None):
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
      self.cantidad.insert(0,r[4])
      self.precio.delete(0,"end")
      self.precio.insert(0,r[5])
      self.fecha.delete(0,"end")
      self.fecha.insert(0,r[6])

  #Rutina de limpieza de datos
  def limpiaCampos(self):
    ''' Limpia todos los campos de captura'''
    if self.actualizaProducto or self.actualizaProveedor or self.elimina: self.cancelar()
    self.idNit.delete(0,'end')
    self.razonSocial.delete(0,'end')
    self.ciudad.delete(0,'end')
    self.idNit.delete(0,'end')
    self.codigo.delete(0,'end')
    self.descripcion.delete(0,'end')
    self.unidad.delete(0,'end')
    self.cantidad.delete(0,'end')
    self.precio.delete(0,'end')
    self.fecha.delete(0,'end')
    self.salidaDatos(None) #Notaran que toma  un None como parametro, no tengo idea de como funciona, solo le di Tab al autocompletado,, supongo que es porque esta programaado como un evento

  #Funcion para colocar fecha automaticamente
  def Auto(self):
    self.fecha.delete(0, 'end')
    self.fecha.insert(-1, str(datetime.today().strftime('%d/%m/%Y')))
    self.fecha.config(foreground="black") #Esto es poqrue el campo de texto debe esta definido como default en gris para poner el placeholder, dd/mm/aaaa, tonces lo cambia

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
        #if row[7] == '': row[7] = 0
        self.treeProductos.insert('',0, text = row[0], values = [row[4],row[5],row[6],row[7],row[8],row[9]])

  #Funciones para gurdar o modificar datos en la base de datos.
  def insertarProveedor(self): 
    '''Inserta, o en su defecto, verifica que este proveedor ya se encuentre en la base de datos
       retorna verdadero si al finalizar el procedimiento existe un proveedor con dado idNit.
    '''
    self.change = False # Variable que indica si hubo algun cambio en la base de datos.
    idN = self.idNit.get()
    rs = self.razonSocial.get()
    c = self.ciudad.get()
    r = self.run_Query("select * from Proveedor where idNitProv = ?;", (idN,))
    if r.fetchone() == None:
      confirmacion = mssg.askokcancel("Agregar proveedor", "¿Desea agregar este nuevo proveedor?")
      if confirmacion:
        r = self.run_Query("insert into Proveedor(idNitProv, Razon_Social, Ciudad) values(?,?,?);",(idN, rs, c))
        if r.rowcount > 0:
          mssg.showinfo(None,"Proveedor agregado exitosamente.")
          self.change = True
          return True # El proveedor fue agregado
        mssg.showerror("Error", "Error en la operación de adición de registro.")
    else:
      return True # El proveedor ya existia.
    return False
  

  def insertarProducto(self):
    '''Rutina para ingresar el producto en pantalla.'''
    errorMessage = ""
    idN = self.idNit.get()
    rs = self.razonSocial.get()
    c = self.ciudad.get()
    cod = self.codigo.get()
    des = self.descripcion.get()
    u = self.unidad.get()
    can = self.cantidad.get()
    pre = self.precio.get()
    fe = self.fecha.get()
    
    #Validación cuando se introduce un proveedor:
    try:
      if idN != "":
        if not self.insertarProveedor():
          self.buscar()
          return False
      else:
          mssg.showerror("Error", "No es posible registrar sin un proveedor.")
          return False
      
      # Validacion cuando se ingresa un producto
      if not self.validacionIngresoRegistro():
        return False
      r = self.run_Query("select * from Inventario where Codigo = ? AND IdNit = ?;",(cod,idN))
      if r.fetchone() != None: # Ya existe uno, no se deben duplicar.
        mssg.showerror("Error", "No pueden existir productos duplicados (En codigo y proveedor)")
        self.buscar()
        return False
      r = self.run_Query("insert into Inventario(idNit, Codigo, Descripcion, Und, Cantidad, Precio, Fecha) "
                                + "values(?,?,?,?,?,?,?);",(idN, cod, des, u, can, pre ,fe))
      if r.rowcount > 0:
        mssg.showinfo(None,"Producto agregado exitosamente.")
        self.buscar()
        return True
      
      mssg.showerror("Un error inesperado ocurrio al insertar el registro")
      self.buscar()
      return False
      
    except Exception as e:
      mssg.showerror("Error en la base de datos.", f"Error {type(e)}: {e}")
      return False
  
  def editarProducto(self):
    '''Rutina para editar el producto en pantalla.'''
    idN = self.idNit.get()
    rs = self.razonSocial.get()
    c = self.ciudad.get()
    cod = self.codigo.get()
    des = self.descripcion.get()
    u = self.unidad.get()
    can = self.cantidad.get()
    pre = self.precio.get()
    fe = self.fecha.get()
    if not self.validacionIngresoRegistro():
      return False
    if mssg.askokcancel("Editar producto", "¿Esta seguro de querer cambiar los valores de este producto?"):
      r = self.run_Query("update Inventario set(Descripcion, Und, Cantidad, Precio, Fecha) = "
                                      + "(?,?,?,?,?) where Codigo = ? AND IdNit = ?;", (des, u, can, pre, fe, cod, idN))
      if r.rowcount <= 0:
        mssg.showerror("Hubo un error en la base de datos al editar el producto")
        return False
        
      mssg.showinfo(None, 'Producto editado correctamente.')
      return True
    return False
  def editarProveedor(self):
    '''Rutina para editar el proveedor ingresado en la pantalla'''
    idN = self.idNit.get()
    rs = self.razonSocial.get()
    c = self.ciudad.get()
    r = self.run_Query("select * from Proveedor where idNitProv = ?;", (idN,))
    if r.fetchone() == None:
      mssg.showerror("Error", "Al parecer, este proveedor no se encuentra en la base de datos")
      return False
    
    confirmacion = mssg.askokcancel("Editar proveedor", "¿Desea editar este proveedor?")
    if confirmacion:
      r = self.run_Query("update Proveedor set(Razon_Social, Ciudad) = (?,?) where idNitProv = ?;", (rs, c, idN))
      if r.rowcount > 0:
        mssg.showinfo(None,"Proveedor editado exitosamente.")
        return True # El proveedor fue editado
      else:
        mssg.showerror("Error", "Error en la operación de edicion de registro.")

    return False

  
  def habilitarCampos(self, proveedor = True, producto = True, botonesEdicion = True, botonGrabar = True):
    '''Rutina para cambiar el state de las entradas y botones de la interfaz
       Los campos en Falso se deshabilitaran, y los que estan en verdadero (por defecto) se habilitaran
    '''
    state = "enabled" if proveedor else "disabled"
    self.idNit.config(state = state)
    self.razonSocial.config(state = state)
    self.ciudad.config(state = state)

    state = "enabled" if producto else "disabled"
    self.codigo.config(state =  state)
    self.descripcion.config(state =  state)
    self.unidad.config(state =  state)
    self.cantidad.config(state =  state)
    self.precio.config(state =  state)
    self.fecha.config(state =  state)
    self.btnAuto.config(state = state)


    state = "enabled" if botonesEdicion else "disabled"

    self.btnBuscar.config(state = state)
    self.btnEditar.config(state = state)
    self.btnEliminar.config(state = state)

    state = "enabled" if botonGrabar else "disabled"
    self.btnGrabar.config(state = state)
    
  def grabar(self):
    '''Función para guardar datos en la base de datos. Si esta en edicion, hace lo correspondiente'''
    if self.actualizaProducto:
      if self.editarProducto():
        self.actualizaProducto = False
        self.habilitarCampos()
        self.buscar()
    elif self.actualizaProveedor:
      if self.editarProveedor():
        self.actualizaProveedor = False
        self.habilitarCampos()
        self.buscar()
    else:
      self.insertarProducto()
      #self.buscar()
  
  #Función para habilitar el modo de edición de registros.
  def editar(self):
    '''Función para habilitar el modo de edición de registros.'''
    if self.idNit.get() != '' and mssg.askyesno("Edicion de registro", "Desea editar el proveedor?"):
      self.actualizaProveedor = True
      self.habilitarCampos(botonesEdicion=False, producto=False)
      self.idNit.config(state = "disabled")
    else:
      mssg.showinfo("Edicion de producto.", "Seleccione el producto cuyos datos desea editar. Para cancelar haga click en el botón cancelar.")
      self.actualizaProducto = True
      self.habilitarCampos(producto=False, botonesEdicion=False, proveedor=False)
  
  #Función que carga datos del registro seleccionado del TreeRow para ser modificados en caso de modo de edición
  # o que borra los datos del registro del TreeRow seleccionado de la base de datos en caso de modo de eliminación.
  def selectTreeRow(self,x):
    '''Función que carga datos del registro seleccionado del TreeRow para ser modificados en caso de modo de edición
        o que borra los datos del registro del TreeRow seleccionado de la base de datos en caso de modo de eliminación.'''
    if self.actualizaProducto:
      row = self.treeProductos.focus()
      if row == '':
        return 
      data = self.treeProductos.item(row, "values")
      data0 = self.treeProductos.item(row, "text")
      self.actualizaProducto = False
      self.habilitarCampos(botonesEdicion=False)
  
      self.limpiaCampos()
      self.actualizaProducto = True
      self.idNit.insert(0,data0)
      self.codigo.insert(0,data[0])
      self.updateProduct(None)
      self.updateProvider(None)
      
      
      self.habilitarCampos(proveedor=False, botonesEdicion=False)
      self.codigo.config(state = "disabled")
      self.fecha.delete(0, 'end')
      self.fecha.config(foreground="black")
      self.fecha.insert(0,data[5])

    if self.elimina:
      row = self.treeProductos.focus()
      if row == '':
        return
      self.elimina = False
      self.habilitarCampos()

      idNit = self.treeProductos.item(row, "text")
      data = self.treeProductos.item(row, "values")
      try:
        if mssg.askyesno("Confirmar eliminación.", "¿Desea eliminar este producto de la base de datos?"):
          r = self.run_Query("delete from Inventario where IdNit = ? AND codigo = ?;", (idNit, data[0]))
          if r.rowcount > 0:
            mssg.showinfo("Eliminacion exitosa", "Este producto ha sido eliminado correctamente")
            self.buscar()
            self.lee_treeProductos()
          else:
            mssg.showinfo("No se ha podido eliminar el producto")
      except Exception as e:
        mssg.showerror("Error en la base de datos.", f"Error {type(e)}: {e}")
      

  #función para cancelar edición o eliminación de datos.
  def cancelar(self):  
    '''función para cancelar edición o eliminación de datos.''' 
    self.habilitarCampos()
    if self.actualizaProducto or self.actualizaProveedor:
      self.actualizaProducto = False
      self.actualizaProveedor = False
      mssg.showinfo("Edición de datos.", "Edición de datos cancelada.")
    if self.elimina:
      self.elimina = False
      mssg.showinfo("Eliminación de datos.", "Eliminación de datos cancelada.")

  #Función que habilita el modo de eliminación.
  def eliminar(self):
    '''Función que habilita el modo de eliminación.'''
    if self.idNit.get() != '' and mssg.askyesno("Eliminacion de proveedor", "¿Desea eliminar este proveedor y todos sus productos?") and mssg.askyesno("Eliminacion de proveedor", "¿Esta seguro?\nEsta accion no se puede deshacer."):
      '''Se quiere eliminar el proveedor y sus productos'''
      try:
        self.run_Query("delete from Inventario where IdNit = ?;", (self.idNit.get(), ))
        r = self.run_Query("delete from Proveedor where IdNitProv = ?;", (self.idNit.get(),))
        if r.rowcount > 0:
          mssg.showinfo("Eliminación exitosa.", "Este proveedor y todos sus productos fueron borrados exitosamente.")
          self.lee_treeProductos()
          self.limpiaCampos()
        else:
          mssg.showerror("Error al eliminar", "Parece ser que no has escogido un proveedor valido.")
      except Exception as e:
        mssg.showerror("Error en la base de datos.", f"Error {type(e)}: {e}")
    else:
      '''Se quiere eliminar solo un producto'''
      mssg.showinfo("Eliminación de datos.", "Seleccione el registro cuyos datos desea eliminar. Para cancelar haga click en el botón cancelar.")
      self.elimina = True
      self.habilitarCampos(botonesEdicion=False, producto=False, proveedor=False)
      self.btnGrabar.config(state = "disabled")

  #Rutina para cargar los datos en el árbol  
  def carga_Datos(self):
    self.idNit.insert(0,self.treeProductos.item(self.treeProductos.selection())['text'])
    self.idNit.configure(state = 'readonly')
    self.razonSocial.insert(0,self.treeProductos.item(self.treeProductos.selection())['values'][0])
    self.unidad.insert(0,self.treeProductos.item(self.treeProductos.selection())['values'][3])

  #Rutina para actualizar la lista de los proveedores con las coincidencias en la base de datos
  def actualizarProveedores(self):
    consulta = f"SELECT IdNitProv FROM Proveedor WHERE IdNitProv LIKE '%{self.idNit.get()}%'"
    resultados = self.run_Query(consulta)
    self.idNit['values'] = [row[0] for row in resultados]
      
  #Funcion que escribe automaticamente los "/" en la fecha    
  def autocompletadoFecha(self, event):
    Fe = self.fecha.get()
    if (len(Fe) == 2 or len(Fe) == 5): 
      Fe += "/"
      self.fecha.delete(0, 'end')  # Borra el contenido actual del Entry
      self.fecha.insert('end', Fe) # Y reescribe para evitar problemas
    self.validaVarChar(event, self.fecha, 10) #Como la fecha requiere mas validaciones, entonces inclui la del varchar en la de poner los "/"
    if (len(Fe) == 3 or len(Fe) == 6) and event.keysym == "BackSpace": #El event.keysym revisa si la tecla que se presiono fue el backspace, si lo fue borra el "/"  junto con la letra que se deseaba borrar
      Fe = Fe[:-1]
      self.fecha.delete(0, 'end')  
      self.fecha.insert('end', Fe)
    if (len(Fe) == 3 or len(Fe) == 6) and Fe[-1] != "/": #Revisa so hace falta un / en su respectiva posicion y corta el string para meterlo donde deberia
      Fe = Fe[:-1] + "/" + Fe[-1:]
      self.fecha.delete(0, 'end')  
      self.fecha.insert('end', Fe)
  
  #Funcion que borra el placeholder de la fecha cuando entra en focus
  def entradaDatos(self, event):
    if self.fecha.get() == "dd/mm/aaaa":
        self.fecha.delete(0, 'end')
        self.fecha.config(foreground="black")

  #Funcion que reescribe el placeholder de la fecha, si el campo de la fecha no esta en focus, revisa si esta vacio y vuelve a escribir el "Placeholder"
  def salidaDatos(self, event):
    if self.fecha.get() == "":
      self.fecha.insert(0, "dd/mm/aaaa")
      self.fecha.config(foreground="gray")

  def validacionTipoDato(self, event, widget):
    if widget == self.fecha:
      st = widget.get()
      if not (st[-1].isdigit):
        widget.delete(len(st)-1, 'end')

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
      self.treeProductos.insert('',0, text = row[0], values = [row[4],row[5],row[6],row[7],row[8],row[9]])

  def cierre(self):
    if mssg.askokcancel('¿Desea cerrar la aplicacion?', 'Todo progreso no guardado se perdera'):
      self.win.destroy() #Esta linea de codigo pues no es estrictamente necesaria pero primero borra todos los widgets de la ventana antes de cerrarla
      self.win.quit()

if __name__ == "__main__":
    app = Inventario()
    app.run()
