import tkinter as tk

def pantalla_principal():
    # Funciones para los botones
    def asign_tasks():
        return 1

    def view_tasks():
        return 2

    def exit_tasks():
        ventana.destroy()
        return 0

    # Crear una ventana
    ventana = tk.Tk()
    ventana.title("Gestor de tareas")

    # Crear botones
    boton1 = tk.Button(ventana, text="Crear Tarea", command=asign_tasks)
    boton2 = tk.Button(ventana, text="Ver Tareas", command=view_tasks)
    boton3 = tk.Button(ventana, text="Salir", command=exit_tasks)

    # Organizar los elementos en la ventana
    boton1.pack()
    boton2.pack()
    boton3.pack()

    # Iniciar el bucle principal de la interfaz gráfica
    ventana.mainloop()
